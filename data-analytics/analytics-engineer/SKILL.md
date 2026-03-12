---
name: analytics-engineer
description: >
  Expert analytics engineering covering data modeling, dbt development, data
  transformation, and semantic layer management. Use when building dbt models,
  designing star schemas, writing staging or mart SQL, configuring data tests,
  defining semantic-layer metrics, or optimizing warehouse query performance.
version: 1.0.0
author: borghei
category: data-analytics
tags: [analytics-engineering, dbt, data-modeling, transformation, semantic-layer]
---

# Analytics Engineer

The agent operates as a senior analytics engineer, building scalable dbt transformation layers, designing dimensional models, writing tested SQL, and managing semantic-layer metric definitions.

## Workflow

1. **Understand the data request** -- Identify the business question, required grain, and downstream consumers (dashboard, notebook, reverse-ETL). Confirm source tables exist and check freshness.
2. **Design the dimensional model** -- Choose star or snowflake schema. Map source entities to dimension and fact tables at the correct grain. Document grain, primary keys, and foreign keys.
3. **Build staging models** -- One `stg_` model per source table. Rename columns, cast types, filter soft-deletes, and add metadata columns. Validate: `dbt build --select stg_*`.
4. **Build intermediate models** -- Encapsulate reusable business logic in `int_` models (e.g., `int_orders_enriched`). Keep each CTE single-purpose.
5. **Build mart models** -- Create `dim_` and `fct_` models for consumption. Configure materialization (view for staging, incremental for large facts, table for small marts).
6. **Add tests and documentation** -- Every primary key gets `unique` + `not_null`. Foreign keys get `relationships`. Add `accepted_values` for enums. Write model descriptions in YAML.
7. **Define semantic-layer metrics** -- Register metrics (sum, average, count_distinct) with time grains and dimension slices so BI consumers get a single source of truth.
8. **Validate end-to-end** -- Run `dbt build`, confirm test pass rate = 100%, check row counts against source, and verify dashboard numbers match.

## dbt Project Structure

```
analytics/
  dbt_project.yml
  models/
    staging/          # stg_<source>__<table>.sql  (one per source table)
    intermediate/     # int_<entity>_<verb>.sql     (reusable logic)
    marts/
      core/           # dim_*.sql, fct_*.sql        (consumption-ready)
      marketing/
      finance/
  macros/             # Reusable Jinja helpers
  tests/              # Custom generic + singular tests
  seeds/              # Static CSV lookups
  snapshots/          # SCD Type 2 captures
```

## Concrete Example: Customer Dimension

**Staging model** (`models/staging/crm/stg_crm__customers.sql`):
```sql
WITH source AS (
    SELECT * FROM {{ source('crm', 'customers') }}
),

renamed AS (
    SELECT
        id                          AS customer_id,
        TRIM(LOWER(name))           AS customer_name,
        TRIM(LOWER(email))          AS email,
        created_at::timestamp       AS created_at,
        updated_at::timestamp       AS updated_at,
        is_active::boolean          AS is_active,
        _fivetran_synced            AS _loaded_at
    FROM source
    WHERE _fivetran_deleted = false
)

SELECT * FROM renamed
```

**Mart model** (`models/marts/core/dim_customer.sql`):
```sql
WITH customers AS (
    SELECT * FROM {{ ref('stg_crm__customers') }}
),

customer_orders AS (
    SELECT
        customer_id,
        MIN(order_date)  AS first_order_date,
        MAX(order_date)  AS most_recent_order_date,
        COUNT(*)         AS lifetime_orders,
        SUM(order_amount) AS lifetime_value
    FROM {{ ref('stg_orders__orders') }}
    GROUP BY customer_id
),

final AS (
    SELECT
        c.customer_id,
        c.customer_name,
        c.email,
        c.created_at,
        co.first_order_date,
        co.most_recent_order_date,
        co.lifetime_orders,
        co.lifetime_value,
        CASE
            WHEN co.lifetime_value >= 10000 THEN 'platinum'
            WHEN co.lifetime_value >= 5000  THEN 'gold'
            WHEN co.lifetime_value >= 1000  THEN 'silver'
            ELSE 'bronze'
        END AS customer_tier
    FROM customers c
    LEFT JOIN customer_orders co
        ON c.customer_id = co.customer_id
)

SELECT * FROM final
```

**Test configuration** (`models/marts/core/_core__models.yml`):
```yaml
version: 2
models:
  - name: dim_customer
    description: Customer dimension with lifetime order metrics and tier classification.
    columns:
      - name: customer_id
        tests: [unique, not_null]
      - name: email
        tests: [unique, not_null]
      - name: customer_tier
        tests:
          - accepted_values:
              values: ['platinum', 'gold', 'silver', 'bronze']
      - name: lifetime_value
        tests:
          - dbt_utils.expression_is_true:
              expression: ">= 0"
```

## Incremental Fact Table Pattern

```sql
-- models/marts/core/fct_orders.sql
{{
    config(
        materialized='incremental',
        unique_key='order_id',
        partition_by={'field': 'order_date', 'data_type': 'date'},
        cluster_by=['customer_id', 'product_id']
    )
}}

WITH orders AS (
    SELECT * FROM {{ ref('stg_orders__orders') }}
    {% if is_incremental() %}
    WHERE order_date >= (SELECT MAX(order_date) FROM {{ this }})
    {% endif %}
),

order_items AS (
    SELECT * FROM {{ ref('stg_orders__order_items') }}
),

final AS (
    SELECT
        o.order_id,
        o.order_date,
        o.customer_id,
        oi.product_id,
        o.store_id,
        oi.quantity,
        oi.unit_price,
        oi.quantity * oi.unit_price AS line_total,
        o.discount_amount,
        o.tax_amount,
        o.total_amount
    FROM orders o
    INNER JOIN order_items oi ON o.order_id = oi.order_id
)

SELECT * FROM final
```

## Materialization Strategy

| Layer | Materialization | Rationale |
|-------|----------------|-----------|
| Staging | View | Thin wrappers; no storage cost |
| Intermediate | Ephemeral / View | Business logic; referenced multiple times |
| Marts (small) | Table | Query performance for BI tools |
| Marts (large) | Incremental | Efficient appends for large fact tables |

## Semantic-Layer Metric Definition

```yaml
# models/marts/core/_core__metrics.yml
metrics:
  - name: revenue
    label: Total Revenue
    model: ref('fct_orders')
    calculation_method: sum
    expression: total_amount
    timestamp: order_date
    time_grains: [day, week, month, quarter, year]
    dimensions: [customer_tier, product_category, store_region]
    filters:
      - field: is_cancelled
        operator: '='
        value: 'false'

  - name: average_order_value
    label: Average Order Value
    model: ref('fct_orders')
    calculation_method: average
    expression: total_amount
    timestamp: order_date
    time_grains: [day, week, month]
```

## Useful Macros

```sql
-- macros/cents_to_dollars.sql
{% macro cents_to_dollars(column_name) %}
    ({{ column_name }} / 100.0)::decimal(18,2)
{% endmacro %}

-- macros/get_incremental_filter.sql
{% macro get_incremental_filter(column_name, lookback_days=3) %}
    {% if is_incremental() %}
        WHERE {{ column_name }} >= (
            SELECT DATEADD(day, -{{ lookback_days }}, MAX({{ column_name }}))
            FROM {{ this }}
        )
    {% endif %}
{% endmacro %}
```

## CI/CD: Slim CI for Pull Requests

```bash
# Only run modified models and their downstream dependents
dbt run  --select state:modified+ --defer --state ./target-base
dbt test --select state:modified+ --defer --state ./target-base
```

For full CI/CD pipeline configuration, see `REFERENCE.md`.

## Reference Materials

- `REFERENCE.md` -- Extended patterns: source config, custom tests, CI/CD workflows, exposures, documentation templates
- `references/modeling_patterns.md` -- Data modeling best practices
- `references/dbt_style_guide.md` -- SQL and dbt conventions
- `references/testing_guide.md` -- Testing strategies
- `references/optimization.md` -- Performance tuning

## Scripts

```bash
python scripts/impact_analyzer.py --model dim_customer
python scripts/schema_diff.py --source prod --target dev
python scripts/doc_generator.py --format markdown
python scripts/quality_scorer.py --model fct_orders
```
