# dbt Style Guide & Conventions

Consistent project structure and SQL style are critical for maintaining large-scale dbt architectures.

## 1. Project Layering

The dbt project must follow a strict three-layer architecture:

### Staging (`models/staging/`)
- Forms a strict 1:1 relationship with source tables.
- **Purpose**: Renaming columns, casting data types, standardizing booleans, and applying `trim/lower` logic.
- **Constraints**: 
  - Strictly NO JOINs or aggregations allowed!
  - Must use the `source('schema', 'table')` macro.
- **Materialization**: `view`
- **Naming Prefix**: `stg_<source_name>__<table_name>.sql`

### Intermediate (`models/intermediate/`)
- Encapsulates complex transformational logic.
- **Purpose**: Consolidating multi-source data, joining lookup tables, and executing window functions.
- **Materialization**: `ephemeral` (compiled inside downstream CTEs) or `view` if referenced multiple times.
- **Naming Prefix**: `int_<entity_name>_<verb>.sql` (e.g., `int_users_enriched.sql`)

### Marts (`models/marts/`)
- The business-facing dimensional and fact models.
- **Purpose**: Serving clean, optimized data to BI tools.
- **Materialization**: `table` (or `incremental` for massive fact tables).
- **Naming Prefix**: `dim_<entity>.sql` or `fct_<event>.sql`

---

## 2. SQL Formatting and Syntax

### No Implicit Columns
- NEVER use `SELECT *` against source or ref tables in Production models (outside of simple staging passthroughs).
- The terminal `SELECT * FROM final` CTE pattern is acceptable as it references an explicitly projected CTE.
- **Why**: Implicit lists break dbt data contracts during schema drift and inflate network/memory payloads. **Always project columns explicitly in CTEs.**

### CTE Structure
- All models must use Common Table Expressions (CTEs), ending with a final `SELECT * FROM final` block.
- **Why**: Separating logic into modular CTE blocks allows for isolation and step-by-step debugging.

**Example Standard Model:**
```sql
WITH customers AS (
    SELECT * FROM {{ ref('stg_salesforce__customers') }}
),
orders AS (
    SELECT * FROM {{ ref('stg_stripe__orders') }}
),
customer_orders AS (
    SELECT
        customer_id,
        MIN(order_date) AS first_order_date,
        SUM(amount) AS lifetime_value
    FROM orders
    GROUP BY customer_id
),
final AS (
    SELECT
        c.customer_id,
        c.customer_name,
        co.first_order_date,
        co.lifetime_value
    FROM customers AS c
    LEFT JOIN customer_orders AS co
        ON c.customer_id = co.customer_id
)

SELECT * FROM final;
```

### Jinja and Macros
- Store reusable logic (e.g., converting cents to dollars, generating schema names) inside the `macros/` folder.
- Use `target.name` conditionals to limit data queried in `dev` environments to save operational costs.
