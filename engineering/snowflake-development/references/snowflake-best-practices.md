# Snowflake Best Practices

## Query Optimization

### SELECT Best Practices
- **Never use SELECT * in production** - specify exact columns needed
- **Filter early** - push WHERE clauses as close to the source as possible
- **Use LIMIT during development** - avoid scanning full tables during testing
- **Avoid correlated subqueries** - rewrite as JOINs or CTEs
- **Use QUALIFY instead of subqueries** for window function filtering

### JOIN Optimization
- **Smaller table on the right** in joins (Snowflake optimizes right-to-left)
- **Filter before joining** - reduce row counts before the join operation
- **Avoid cartesian products** - always specify join conditions
- **Use NATURAL JOIN cautiously** - explicit conditions are safer
- **Consider LATERAL joins** for semi-structured data

### Common Table Expressions (CTEs)
- Use CTEs for readability, but be aware they execute for each reference
- For reused CTEs, consider temporary tables or materialized CTEs
- Recursive CTEs have a 100-iteration default limit

### Semi-Structured Data
- Use VARIANT type for JSON/Avro/Parquet/ORC data
- Access nested fields with `:` notation: `data:field::STRING`
- Use FLATTEN for array operations
- Create materialized views over semi-structured queries for performance

## Warehouse Management

### Sizing Guide

| Size | Credits/hr | Nodes | Good For |
|------|-----------|-------|----------|
| X-Small | 1 | 1 | Simple queries, small data, development |
| Small | 2 | 2 | Light BI queries, small ETL jobs |
| Medium | 4 | 4 | Standard BI workloads, medium ETL |
| Large | 8 | 8 | Complex queries, large ETL pipelines |
| X-Large | 16 | 16 | Heavy analytics, large-scale transformations |
| 2X-Large | 32 | 32 | Extremely complex queries, massive data volumes |

### Auto-Suspend Settings
- **Ad-hoc queries**: 60 seconds (minimize idle costs)
- **BI dashboards**: 300 seconds (balance between cost and responsiveness)
- **ETL pipelines**: 0 seconds (suspend immediately after completion)
- **Always-on services**: Never auto-suspend (if constant query flow)

### Multi-Cluster Warehouses
- Enable for BI workloads with variable concurrency
- Set min clusters to 1, max based on peak concurrent users
- Economy scaling policy for cost-sensitive workloads
- Standard scaling policy for performance-sensitive workloads

## Cost Optimization

### Top Cost Drivers
1. **Warehouse compute** (largest cost typically 60-80%)
2. **Storage** (compressed, relatively cheap)
3. **Data transfer** (egress charges, cross-region)
4. **Serverless features** (Snowpipe, auto-clustering, etc.)

### Cost Reduction Strategies
- Right-size warehouses (monitor credit usage vs. query volume)
- Set resource monitors with quotas and alerts
- Use warehouse auto-suspend aggressively
- Schedule ETL during off-peak hours if using reserved capacity
- Avoid unnecessary cloning of large databases
- Drop unused tables and databases
- Use transient tables for staging data (no Time Travel/Fail-Safe costs)

## Anti-Patterns

### Query Anti-Patterns
- `SELECT *` in production queries
- `ORDER BY` without `LIMIT`
- Using `UNION` when `UNION ALL` would work (forces deduplication)
- Joining on non-clustering key columns for large tables
- String functions in WHERE clauses on large tables
- Using `NOT IN` with NULLable columns (use `NOT EXISTS` instead)

### Warehouse Anti-Patterns
- One warehouse for all workloads (prevents optimization)
- X-Large warehouse for simple queries
- Long auto-suspend timeouts for infrequent use
- No resource monitors (unbounded spending)

### Data Modeling Anti-Patterns
- Overly normalized schemas (Snowflake prefers denormalized/star schemas)
- Missing clustering keys on large tables
- Not using Time Travel for data recovery
- Storing staging data in permanent tables (use transient)
