---
name: analytics-engineer
description: Expert analytics engineering covering data modeling, dbt development, data transformation, and semantic layer management.
version: 1.0.0
author: Claude Skills
category: data-analytics
tags: [analytics-engineering, dbt, data-modeling, transformation, semantic-layer]
---

# Analytics Engineer

Expert-level analytics engineering for scalable data transformation.

## Core Competencies

- Data modeling
- dbt development
- SQL transformation
- Semantic layer design
- Data testing
- Documentation
- Performance optimization
- Pipeline orchestration

## Analytics Engineering Stack

### Modern Data Stack

```
SOURCES → INGESTION → WAREHOUSE → TRANSFORMATION → SEMANTIC → BI
   │          │           │             │             │        │
   ▼          ▼           ▼             ▼             ▼        ▼
 APIs      Fivetran   Snowflake        dbt         Looker   Tableau
 DBs       Airbyte    BigQuery       Dataform     Transform  PBI
 Files     Stitch     Redshift       Spark SQL    dbt ML    Metabase
```

### Project Structure (dbt)

```
analytics/
├── dbt_project.yml
├── profiles.yml
├── models/
│   ├── staging/           # Raw → Cleaned
│   │   ├── stg_*.sql
│   │   └── _stg_*.yml
│   ├── intermediate/      # Business logic
│   │   ├── int_*.sql
│   │   └── _int_*.yml
│   └── marts/             # Final models
│       ├── core/
│       │   ├── dim_*.sql
│       │   └── fct_*.sql
│       ├── marketing/
│       └── finance/
├── macros/
├── tests/
├── seeds/
├── snapshots/
└── analyses/
```

## Data Modeling

### Dimensional Modeling

**Star Schema:**
```
                    ┌──────────────┐
                    │  dim_date    │
                    └──────┬───────┘
                           │
┌──────────────┐    ┌──────┴───────┐    ┌──────────────┐
│ dim_customer │────│  fct_orders  │────│ dim_product  │
└──────────────┘    └──────┬───────┘    └──────────────┘
                           │
                    ┌──────┴───────┐
                    │  dim_store   │
                    └──────────────┘
```

**Dimension Table Pattern:**
```sql
-- models/marts/core/dim_customer.sql

WITH customers AS (
    SELECT * FROM {{ ref('stg_crm__customers') }}
),

addresses AS (
    SELECT * FROM {{ ref('stg_crm__addresses') }}
),

customer_orders AS (
    SELECT
        customer_id,
        MIN(order_date) AS first_order_date,
        MAX(order_date) AS most_recent_order_date,
        COUNT(*) AS lifetime_orders,
        SUM(order_amount) AS lifetime_value
    FROM {{ ref('stg_orders__orders') }}
    GROUP BY customer_id
),

final AS (
    SELECT
        customers.customer_id,
        customers.customer_name,
        customers.email,
        customers.created_at,
        addresses.city,
        addresses.state,
        addresses.country,
        customer_orders.first_order_date,
        customer_orders.most_recent_order_date,
        customer_orders.lifetime_orders,
        customer_orders.lifetime_value,
        CASE
            WHEN customer_orders.lifetime_value >= 10000 THEN 'platinum'
            WHEN customer_orders.lifetime_value >= 5000 THEN 'gold'
            WHEN customer_orders.lifetime_value >= 1000 THEN 'silver'
            ELSE 'bronze'
        END AS customer_tier
    FROM customers
    LEFT JOIN addresses
        ON customers.address_id = addresses.address_id
    LEFT JOIN customer_orders
        ON customers.customer_id = customer_orders.customer_id
)

SELECT * FROM final
```

**Fact Table Pattern:**
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
        orders.order_id,
        orders.order_date,
        orders.customer_id,
        order_items.product_id,
        orders.store_id,
        order_items.quantity,
        order_items.unit_price,
        order_items.quantity * order_items.unit_price AS line_total,
        orders.discount_amount,
        orders.tax_amount,
        orders.shipping_amount,
        orders.total_amount
    FROM orders
    INNER JOIN order_items
        ON orders.order_id = order_items.order_id
)

SELECT * FROM final
```

### Staging Layer

```sql
-- models/staging/crm/stg_crm__customers.sql

WITH source AS (
    SELECT * FROM {{ source('crm', 'customers') }}
),

renamed AS (
    SELECT
        -- Primary key
        id AS customer_id,

        -- Strings
        TRIM(LOWER(name)) AS customer_name,
        TRIM(LOWER(email)) AS email,

        -- Dates
        created_at::timestamp AS created_at,
        updated_at::timestamp AS updated_at,

        -- Booleans
        is_active::boolean AS is_active,

        -- Metadata
        _fivetran_synced AS _loaded_at

    FROM source
    WHERE _fivetran_deleted = false
)

SELECT * FROM renamed
```

### Source Configuration

```yaml
# models/staging/crm/_crm__sources.yml

version: 2

sources:
  - name: crm
    description: Customer relationship management system
    database: raw
    schema: crm
    loader: fivetran
    loaded_at_field: _fivetran_synced

    freshness:
      warn_after: {count: 12, period: hour}
      error_after: {count: 24, period: hour}

    tables:
      - name: customers
        description: Customer master data
        columns:
          - name: id
            description: Primary key
            tests:
              - unique
              - not_null
          - name: email
            tests:
              - unique
```

## Data Testing

### Test Types

```yaml
# models/marts/core/_core__models.yml

version: 2

models:
  - name: dim_customer
    description: Customer dimension table

    columns:
      - name: customer_id
        description: Primary key
        tests:
          - unique
          - not_null

      - name: email
        tests:
          - unique
          - not_null

      - name: customer_tier
        tests:
          - accepted_values:
              values: ['platinum', 'gold', 'silver', 'bronze']

      - name: lifetime_value
        tests:
          - dbt_utils.expression_is_true:
              expression: ">= 0"

  - name: fct_orders
    description: Order fact table

    tests:
      - dbt_utils.unique_combination_of_columns:
          combination_of_columns:
            - order_id
            - product_id

    columns:
      - name: customer_id
        tests:
          - relationships:
              to: ref('dim_customer')
              field: customer_id
```

### Custom Tests

```sql
-- tests/assert_positive_amounts.sql

{% test positive_amount(model, column_name) %}

SELECT
    {{ column_name }}
FROM {{ model }}
WHERE {{ column_name }} < 0

{% endtest %}
```

```sql
-- tests/generic/assert_row_count_equal.sql

{% test row_count_equal(model, compare_model) %}

WITH source_count AS (
    SELECT COUNT(*) AS cnt FROM {{ model }}
),
compare_count AS (
    SELECT COUNT(*) AS cnt FROM {{ ref(compare_model) }}
)

SELECT *
FROM source_count
CROSS JOIN compare_count
WHERE source_count.cnt != compare_count.cnt

{% endtest %}
```

## Macros and DRY Patterns

### Common Macros

```sql
-- macros/generate_schema_name.sql

{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- set default_schema = target.schema -%}
    {%- if custom_schema_name is none -%}
        {{ default_schema }}
    {%- else -%}
        {{ default_schema }}_{{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
```

```sql
-- macros/cents_to_dollars.sql

{% macro cents_to_dollars(column_name) %}
    ({{ column_name }} / 100.0)::decimal(18,2)
{% endmacro %}
```

```sql
-- macros/pivot_values.sql

{% macro pivot_values(column_name, values, alias_prefix='') %}
    {% for value in values %}
        SUM(CASE WHEN {{ column_name }} = '{{ value }}' THEN 1 ELSE 0 END)
            AS {{ alias_prefix }}{{ value | lower | replace(' ', '_') }}
        {% if not loop.last %},{% endif %}
    {% endfor %}
{% endmacro %}
```

### Incremental Patterns

```sql
-- macros/incremental_filter.sql

{% macro get_incremental_filter(column_name, lookback_days=3) %}
    {% if is_incremental() %}
        WHERE {{ column_name }} >= (
            SELECT DATEADD(day, -{{ lookback_days }}, MAX({{ column_name }}))
            FROM {{ this }}
        )
    {% endif %}
{% endmacro %}
```

## Semantic Layer

### Metric Definitions

```yaml
# models/marts/core/_core__metrics.yml

version: 2

metrics:
  - name: revenue
    label: Total Revenue
    model: ref('fct_orders')
    description: Sum of all order amounts

    calculation_method: sum
    expression: total_amount

    timestamp: order_date
    time_grains: [day, week, month, quarter, year]

    dimensions:
      - customer_tier
      - product_category
      - store_region

    filters:
      - field: is_cancelled
        operator: '='
        value: 'false'

  - name: average_order_value
    label: Average Order Value
    model: ref('fct_orders')
    description: Average order amount

    calculation_method: average
    expression: total_amount

    timestamp: order_date
    time_grains: [day, week, month]

  - name: customer_count
    label: Customer Count
    model: ref('dim_customer')

    calculation_method: count_distinct
    expression: customer_id
```

### Exposures

```yaml
# models/exposures.yml

version: 2

exposures:
  - name: executive_dashboard
    type: dashboard
    maturity: high
    url: https://tableau.company.com/views/executive
    description: Executive KPI dashboard

    depends_on:
      - ref('fct_orders')
      - ref('dim_customer')
      - ref('dim_product')

    owner:
      name: Analytics Team
      email: analytics@company.com

  - name: marketing_report
    type: notebook
    maturity: medium
    url: https://databricks.company.com/notebooks/marketing

    depends_on:
      - ref('fct_marketing_events')
      - ref('dim_campaign')

    owner:
      name: Marketing Analytics
      email: marketing-analytics@company.com
```

## Performance Optimization

### Materialization Strategy

| Layer | Materialization | Reason |
|-------|-----------------|--------|
| Staging | View | Raw data, no aggregation |
| Intermediate | Ephemeral/View | Business logic, referenced multiple times |
| Marts (small) | Table | Final models, query performance |
| Marts (large) | Incremental | Large fact tables, efficiency |

### Query Optimization

```sql
-- Before: Expensive window function on full table
SELECT
    order_id,
    customer_id,
    order_date,
    SUM(amount) OVER (
        PARTITION BY customer_id
        ORDER BY order_date
    ) AS running_total
FROM orders;

-- After: Pre-aggregate then join
WITH daily_totals AS (
    SELECT
        customer_id,
        order_date,
        SUM(amount) AS daily_amount
    FROM orders
    GROUP BY customer_id, order_date
),

running_totals AS (
    SELECT
        customer_id,
        order_date,
        SUM(daily_amount) OVER (
            PARTITION BY customer_id
            ORDER BY order_date
        ) AS running_total
    FROM daily_totals
)

SELECT
    o.order_id,
    o.customer_id,
    o.order_date,
    rt.running_total
FROM orders o
JOIN running_totals rt
    ON o.customer_id = rt.customer_id
    AND o.order_date = rt.order_date;
```

### Clustering and Partitioning

```sql
{{
    config(
        materialized='incremental',
        unique_key='event_id',
        partition_by={
            'field': 'event_date',
            'data_type': 'date',
            'granularity': 'day'
        },
        cluster_by=['user_id', 'event_type']
    )
}}
```

## CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/dbt.yml

name: dbt CI/CD

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: pip install dbt-snowflake

      - name: dbt deps
        run: dbt deps

      - name: dbt compile
        run: dbt compile --target ci

      - name: dbt test
        run: dbt test --target ci

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: dbt run
        run: dbt run --target prod

      - name: dbt test
        run: dbt test --target prod
```

### Slim CI

```bash
# Only run modified models and downstream
dbt run --select state:modified+ --defer --state ./target-base
dbt test --select state:modified+ --defer --state ./target-base
```

## Documentation

### Model Documentation

```yaml
# models/marts/core/_core__models.yml

version: 2

models:
  - name: fct_orders
    description: |
      Order fact table containing one row per order line item.

      ## Business Logic
      - Orders with status 'cancelled' are excluded
      - Amounts are in USD
      - Tax is calculated at time of order

      ## Usage
      ```sql
      SELECT * FROM {{ ref('fct_orders') }}
      WHERE order_date >= '2024-01-01'
      ```

      ## Dependencies
      - stg_orders__orders
      - stg_orders__order_items
```

### Generate Docs

```bash
# Generate and serve documentation
dbt docs generate
dbt docs serve --port 8080
```

## Reference Materials

- `references/modeling_patterns.md` - Data modeling best practices
- `references/dbt_style_guide.md` - SQL and dbt conventions
- `references/testing_guide.md` - Testing strategies
- `references/optimization.md` - Performance tuning

## Scripts

```bash
# Model impact analyzer
python scripts/impact_analyzer.py --model dim_customer

# Schema change detector
python scripts/schema_diff.py --source prod --target dev

# Documentation generator
python scripts/doc_generator.py --format markdown

# Data quality scorer
python scripts/quality_scorer.py --model fct_orders
```
