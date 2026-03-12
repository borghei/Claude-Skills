# Analytics Engineer -- Extended Reference

## Source Configuration

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
            tests: [unique, not_null]
          - name: email
            tests: [unique]
```

## Custom Generic Tests

```sql
-- tests/assert_positive_amount.sql
{% test positive_amount(model, column_name) %}
SELECT {{ column_name }}
FROM {{ model }}
WHERE {{ column_name }} < 0
{% endtest %}

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

## Additional Macros

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

-- macros/pivot_values.sql
{% macro pivot_values(column_name, values, alias_prefix='') %}
    {% for value in values %}
        SUM(CASE WHEN {{ column_name }} = '{{ value }}' THEN 1 ELSE 0 END)
            AS {{ alias_prefix }}{{ value | lower | replace(' ', '_') }}
        {% if not loop.last %},{% endif %}
    {% endfor %}
{% endmacro %}
```

## Exposures

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
```

## GitHub Actions CI/CD Pipeline

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
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install dbt-snowflake
      - run: dbt deps
      - run: dbt compile --target ci
      - run: dbt test --target ci

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: dbt run --target prod
      - run: dbt test --target prod
```

## Query Optimization: Pre-aggregate Pattern

```sql
-- Before: expensive window function on full table
SELECT order_id, customer_id, order_date,
    SUM(amount) OVER (PARTITION BY customer_id ORDER BY order_date) AS running_total
FROM orders;

-- After: pre-aggregate then join
WITH daily_totals AS (
    SELECT customer_id, order_date, SUM(amount) AS daily_amount
    FROM orders
    GROUP BY customer_id, order_date
),
running_totals AS (
    SELECT customer_id, order_date,
        SUM(daily_amount) OVER (PARTITION BY customer_id ORDER BY order_date) AS running_total
    FROM daily_totals
)
SELECT o.order_id, o.customer_id, o.order_date, rt.running_total
FROM orders o
JOIN running_totals rt
    ON o.customer_id = rt.customer_id AND o.order_date = rt.order_date;
```

## Model Documentation Template

```yaml
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
