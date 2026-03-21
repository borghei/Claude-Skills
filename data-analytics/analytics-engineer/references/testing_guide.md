# Testing & CI/CD Guide

Ensuring data pipeline integrity requires rigorous coverage at all execution vectors.

## 1. Generic Tests

Generic tests are globally scalable validations declared within `.yml` schema files.

- **Unique**: Apply to all primary keys to ensure the grain of the model is respected.
- **Not_null**: Apply to all primary keys and critical business fields (e.g. `amount`).
- **Accepted_values**: Use to validate enum-type fields (e.g., ensuring `order_status` can only equal `pending`, `shipped`, `cancelled`).
- **Relationships**: Apply to all foreign keys to validate referential integrity against parent dimension tables.

*Implementation Example:*
```yaml
models:
  - name: fct_orders
    columns:
      - name: order_id
        tests:
          - unique
          - not_null
      - name: customer_id
        tests:
          - relationships:
              to: ref('dim_customers')
              field: customer_id
      - name: status
        tests:
          - accepted_values:
              values: ['placed', 'shipped', 'completed']
```

## 2. Testing Sources First

Do not wait until the transformation is complete to discover bad data. Apply tests directly to the raw sources inside the `_sources.yml` configurations. Isolating upstream drops reduces debug turnaround.

## 3. Singular Tests

When business logic requires complex checks that generic `.yml` blocks can't accommodate, write explicit Singular Tests.
- Store these as `.sql` files within the `tests/` directory.
- The test file should `SELECT` the failing condition. If the query returns `0` rows, the test passes.

*Example:* `tests/assert_positive_amount.sql`
```sql
-- Ensure that the revenue amount is never negative
SELECT
    order_id,
    revenue_amount
FROM {{ ref('fct_orders') }}
WHERE revenue_amount < 0
```

## 4. Continuous Integration (CI/CD)

### Pull Request Workflows
Never merge directly into `main`. The Git workflow should mandate PRs, and the CI environment must automatically run building and testing.

### Slim CI
Running a full `dbt build` against thousands of models on every PR commits is too slow and expensive.
- **Rule**: Utilize Slim CI workflows comparing state against production.
- **Command**: `dbt build --select state:modified+`
- **Result**: Instructs the environment to only build and test models whose code changed in the PR branch, along with any downstream models that depend on them.
