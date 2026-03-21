# SQL Query Optimization Patterns

This guide outlines antipatterns that cripple data warehouse performance and details the strategies required to remediate them.

## 1. Eliminate Spaghetti Queries

- **The Antipattern**: Writing a monolithic, multi-thousand-line `SELECT` statement attempting to aggregate, filter, and join a dozen tables at once to fulfill an entire reporting requirement.
- **The Issue**: Massive queries confuse the warehouse optimizer. The engine often allocates incorrect memory logic, resulting in unintentional Cartesian products (cross-joins) that spin compute resources into infinity.
- **The Fix**: Adopt a **Divide and Conquer** methodology. Break complex operations down into distinct sequential dbt Intermediate models (`int_` layer) or distinct, linearly progressive Common Table Expressions (CTEs) representing granular steps.

## 2. Eliminate EAV and Jaywalking Joins

- **Jaywalking**: Storing comma-separated delimited IDs inside a single column and using `JOIN ON a LIKE '%' || b || '%'` to connect them.
- **EAV (Entity-Attribute-Value)**: Storing schema-less data in three vertical columns (`entity_id`, `attribute_name`, `value`).
- **The Issue**: Both patterns completely bypass the relational database indexing structures, forcing horizontal table scans that are mathematically exponential.
- **The Fix**: Abstract many-to-many elements into an explicit explicit Intersection Table natively supporting primary-to-foreign key bridging.

## 3. Ambiguous Aggregations

- **The Antipattern**: Selecting raw columns alongside aggregate measures without explicitly grouping them, or adding extraneous descriptive fields to a `GROUP BY` clause just to pass syntax.
- **The Issue**: It results in pseudo-random value selection for the non-grouped rows or inadvertently alters the grain of the calculation, resulting in duplicated or dropped financial measures.
- **The Fix**: Follow the single-value rule. Only group on the absolute core dimension keys. For descriptive descriptors, wrap them in deterministic functions like `MAX()`, or calculate the core aggregates in a nested CTE and `JOIN` the descriptors afterward.

## 4. Unoptimized Randomization

- **The Antipattern**: `SELECT * FROM massive_table ORDER BY RAND() LIMIT 10`
- **The Issue**: The database must assign a random floating-point integer to *every single row in the millions-row facts table*, execute a global sort on the entire table in memory, select the first 10, and discard the rest.
- **The Fix**: Avoid `RAND()`. Instead use windowing sequencing operations:

```sql
-- More optimal approach for sampling:
WITH CTE AS (
  SELECT *, ROW_NUMBER() OVER(ORDER BY event_timestamp) AS rn
  FROM massive_table
)
SELECT * FROM CTE WHERE rn % 100 = 0; -- takes 1% roughly
```

## 5. Incremental Processing

For facts exceeding ten million records, daily rebuilds consume massive resources.
Configure fact models as `materialized='incremental'` inside the configuration block.
- Read only the last 1-3 days of data utilizing the `{% if is_incremental() %}` Jinja macro condition.
- Update matching records utilizing `unique_key`.
