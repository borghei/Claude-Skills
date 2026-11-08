---
name: snowflake-development
description: >
  Review Snowflake SQL for pruning and join problems, size warehouses and cut credit spend.
  Use when a Snowflake query is slow or expensive, or when sizing or reviewing warehouses.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: data-warehouse
  updated: 2026-11-08
  tags: [snowflake, sql, data-warehouse, query-optimization, warehouse-sizing]
---

# Snowflake Development

> **Category:** Engineering
> **Domain:** Data Warehouse

## Overview

The **Snowflake Development** skill provides tools for analyzing and optimizing Snowflake SQL queries, recommending warehouse sizing, and enforcing Snowflake-specific best practices. Helps data engineers reduce costs and improve query performance.

## When to Use

- A Snowflake query is slow or a warehouse bill jumped and you need the likely causes.
- Sizing a new warehouse for an ETL, BI, ad-hoc, data-science or ingest workload.
- Reviewing SQL or a data model before it goes into a scheduled pipeline.

For other databases use `sql-database-assistant`; for pipeline orchestration use `senior-data-engineer`.

## Clarify First

Before analyzing or sizing, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Action:** analyze / optimize / warehouse-sizing (`--action`; selects the workflow).
- **SQL file or query:** the specific query(ies) to optimize (`--file`; the subject of the analysis).
- **Workload type & data volume:** ETL / BI / ad-hoc and the GB scale (`--workload`/`--data-volume`; drives the warehouse recommendation).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

```bash
# Analyze a Snowflake SQL file for optimization opportunities (bundled sample: 4 issues)
python scripts/snowflake_query_helper.py --file assets/sample_queries.sql --action analyze

# Get warehouse sizing recommendations, costed at your hours and contract credit price
python scripts/snowflake_query_helper.py --action warehouse-sizing --workload "etl" --data-volume "500GB" --hours 4 --credit-price 3

# Optimize a specific query
python scripts/snowflake_query_helper.py --file slow_query.sql --action optimize
```

## Tools Overview

| Tool | Purpose | Key Flags |
|------|---------|-----------|
| `snowflake_query_helper.py` | Analyze, optimize Snowflake SQL and recommend warehouse sizes | `--file`/`--sql`, `--action analyze/optimize/warehouse-sizing`, `--workload`, `--data-volume`, `--hours`, `--credit-price`, `--format human/json` |

Exit codes: `0` ok (analysis found no critical issue); `1` a critical issue was found;
`2` bad input (missing file, no SQL given).

## Workflows

### Query Performance Optimization
1. Collect the expensive queries with real numbers (needs access to the `SNOWFLAKE.ACCOUNT_USAGE` share; it lags by up to about 45 minutes):
   ```sql
   SELECT query_id, warehouse_name, total_elapsed_time / 1000 AS seconds,
          bytes_scanned, partitions_scanned, partitions_total, query_text
   FROM snowflake.account_usage.query_history
   WHERE start_time >= DATEADD(day, -7, CURRENT_TIMESTAMP())
     AND execution_status = 'SUCCESS'
   ORDER BY total_elapsed_time DESC
   LIMIT 20;
   ```
2. Run the analyzer on those query texts for pattern-level fixes (SELECT *, functions on filter columns, always-true joins).
3. For each query, open the Query Profile: the real evidence is partitions scanned vs total, spilling to local/remote storage, and the most expensive operator. Prefer it over the script whenever they disagree.
4. Apply the change and verify against the same metrics before/after; done when elapsed time or bytes scanned fell on the same input.

### Warehouse Right-Sizing
1. Identify workload type (ETL, BI, ad-hoc, etc.)
2. Run warehouse-sizing with data volume
3. Review recommendations
4. Implement multi-cluster settings if applicable

## Scope & Limitations

**In Scope:**
- Rule-based review of Snowflake SQL from a file or `--sql` text with `snowflake_query_helper.py --action analyze` or `optimize`, with a complexity score and a suggested warehouse size per query.
- Warehouse sizing for five workload types (etl, bi, ad-hoc, data-science, ingest) from a data volume, with credits per hour, an estimated daily cost and a `CREATE WAREHOUSE` statement.
- Query, warehouse, cost and data modeling practices in `references/snowflake-best-practices.md`.

**Out of Scope:**
- Connecting to Snowflake, reading query history or query profiles, or running any statement.
- SQL work for other databases (see `engineering/sql-database-assistant/`).
- Building and orchestrating data pipelines (see `engineering/senior-data-engineer/`).
- Access control, governance and data sharing setup.

**Important Caveats:**
- Analysis matches patterns in SQL text. It does not see execution plans, table sizes or clustering, so it misses issues that only show at run time.
- Sizing comes from a fixed table of data volume and concurrency limits. It is a starting point to adjust with observed query performance.
- Cost figures default to 8 hours a day at $2 per credit; pass `--hours` and `--credit-price` for your contract. Credit prices depend on edition, region and contract, and Snowflake features and pricing change over time.

## Reference Documentation

- [Snowflake Best Practices](references/snowflake-best-practices.md) - Query patterns, warehouse management, cost optimization

## Common Patterns

### Cost Reduction
- Right-size warehouses (don't use XL for small queries)
- Set auto-suspend to 60 seconds for ad-hoc warehouses
- Use materialized views for frequently accessed aggregations
- Let Snowflake's automatic micro-partitioning do its job; add a clustering key only to very large tables (multi-terabyte) whose frequent filters scan most partitions (`partitions_scanned` close to `partitions_total`), and check `SYSTEM$CLUSTERING_INFORMATION` first, since automatic reclustering costs credits
- Avoid SELECT * in production queries

## Anti-Patterns

### Sizing Up to Fix a Slow Query
**Mistake:** Moving a slow query to a larger warehouse without reading its profile.
**Why it happens:** It is one setting and often helps a little.
**Instead:** Check the Query Profile first. Poor pruning or a bad join is not fixed by more compute; spilling to remote storage is the case where a larger size usually pays for itself.

### Clustering Every Large Table
**Mistake:** Adding clustering keys as routine "partitioning".
**Why it happens:** Other warehouses need explicit partitioning.
**Instead:** Snowflake micro-partitions automatically. Cluster only when a frequent filter on a very large table scans most partitions, and watch the reclustering credits.

### Warehouses That Never Sleep
**Mistake:** Leaving `AUTO_SUSPEND` at hours or disabled on ad-hoc and BI warehouses.
**Why it happens:** Users dislike the resume delay.
**Instead:** Suspend after 60-300 seconds; resume takes seconds while idle compute bills every second it runs.

## Files

| File | Purpose |
|------|---------|
| `scripts/snowflake_query_helper.py` | SQL pattern analysis and warehouse sizing |
| `assets/sample_queries.sql` | Two queries with deliberate problems |
| `references/snowflake-best-practices.md` | Query, warehouse, cost and modelling practices |
