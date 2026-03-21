# Data Modeling Patterns

This guide formalizes the dimensional data modeling conventions expected within the analytics engineering workflow.

## 1. Dimensional Architectures

### The Star Schema
The **Star Schema** is the universally preferred architecture for analytics. It relies on a single **Fact Table** surrounded by highly denormalized **Dimension Tables**.
- **Performance**: Minimizes complex multi-table joins.
- **Understandability**: Business users can natively grok the "nouns" (dimensions) and "verbs" (facts) of the business.
- **Rule**: Never use a Snowflake schema unless explicitly required by a BI tool limitation. A dimension table should contain all attributes required to slice the fact table, regardless of normalization redundancy.

### One Big Table (OBT)
- **Warning**: Do not use OBT approaches. While columnar databases handle them well, they force disparate business processes into monolithic structures, resulting in extreme matrix sparsity and complex workarounds.

---

## 2. Dimension Tables

Dimensions (the "who, what, where, when") provide the text attributes used to filter and group fact data.

### Surrogate Keys
- **Rule**: Every dimension table MUST have a meaningless, auto-incrementing integer (or hashed integer) as its primary key.
- **Why**: Protects the warehouse from upstream source system changes (e.g., if a natural key is recycled) and enables Slowly Changing Dimension (SCD) capabilities.
- **Implementation**: Use `dbt_utils.generate_surrogate_key(['natural_key'])`.

### Hierarchies
- Do not normalize hierarchies. The `Dim_Product` table should contain `Category`, `Sub_Category`, `Brand`, and `SKU` directly on the single row.

### Slowly Changing Dimensions (SCDs)
- **SCD Type 1 (Overwrite)**: Use when history is irrelevant. Edits overwrite the old data.
- **SCD Type 2 (Versioning)**: Required for compliance and historical accuracy. Create a new row when an attribute changes. Requires `is_active` boolean, `effective_date`, and `expiration_date` columns.
- *For implementing SCD Type 2 in dbt, utilize the `snapshots` feature rather than manual logic.*

---

## 3. Fact Tables

Fact tables capture the measurable, quantitative metrics of a business event.

### Target Atomic Grain
- Define the lowest possible granularity. The fact table should represent the most atomic level of an event (e.g., `one row per order line item`, not `one row per order`).

### Additive Facts Only
- **Rule**: Store fully additive measures (e.g., `dollars_sold`, `quantity_ordered`).
- **Rule**: Non-additive measures (e.g., `gross_margin_percentage`, `conversion_rate`) must NOT be stored in the database. Instead, store the additive components (`revenue`, `cost`) and perform the ratio division dynamically in the BI tool.

### Degenerate Dimensions
- **Rule**: For extremely high-cardinality values with no descriptive attributes (e.g., `transaction_id`, `invoice_number`), store them directly on the fact table. Do not create a dimension table just to hold an ID.

### No NULL Foreign Keys
- **Rule**: A fact table must *never* contain a `NULL` foreign key. Inner joins drop records with `NULL` keys, silently obliterating revenue metrics.
- **Fix**: Direct `NULL` foreign keys to an established placeholder dimension row (e.g., ID `-1` mapped to "Unknown" or "N/A").
