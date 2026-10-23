---
name: snowflake-development
description: >
  This skill should be used when the user asks to "optimize Snowflake queries",
  "analyze Snowflake SQL performance", "size Snowflake warehouses",
  "review Snowflake data models", or "troubleshoot Snowflake cost issues".
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: data-warehouse
  updated: 2026-04-02
  tags: [snowflake, sql, data-warehouse, query-optimization, warehouse-sizing]
---

# Snowflake Development

> **Category:** Engineering
> **Domain:** Data Warehouse

## Overview

The **Snowflake Development** skill provides tools for analyzing and optimizing Snowflake SQL queries, recommending warehouse sizing, and enforcing Snowflake-specific best practices. Helps data engineers reduce costs and improve query performance.

## Clarify First

Before analyzing or sizing, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Action:** analyze / optimize / warehouse-sizing (`--action`; selects the workflow).
- **SQL file or query:** the specific query(ies) to optimize (`--file`; the subject of the analysis).
- **Workload type & data volume:** ETL / BI / ad-hoc and the GB scale (`--workload`/`--data-volume`; drives the warehouse recommendation).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

```bash
# Analyze a Snowflake SQL file for optimization opportunities
python scripts/snowflake_query_helper.py --file queries.sql --action analyze

# Get warehouse sizing recommendations
python scripts/snowflake_query_helper.py --action warehouse-sizing --workload "etl" --data-volume "500GB"

# Optimize a specific query
python scripts/snowflake_query_helper.py --file slow_query.sql --action optimize
```

## Tools Overview

| Tool | Purpose | Key Flags |
|------|---------|-----------|
| `snowflake_query_helper.py` | Analyze, optimize Snowflake SQL and recommend warehouse sizes | `--file`, `--action`, `--workload`, `--data-volume` |

## Workflows

### Query Performance Optimization
1. Collect slow queries from query history
2. Run analyzer to identify optimization opportunities
3. Apply recommended changes
4. Compare before/after execution plans

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
- Cost figures assume 8 hours a day at $2 per credit. Credit prices depend on edition, region and contract, and Snowflake features and pricing change over time.

## Reference Documentation

- [Snowflake Best Practices](references/snowflake-best-practices.md) - Query patterns, warehouse management, cost optimization

## Common Patterns

### Cost Reduction
- Right-size warehouses (don't use XL for small queries)
- Set auto-suspend to 60 seconds for ad-hoc warehouses
- Use materialized views for frequently accessed aggregations
- Partition large tables with clustering keys
- Avoid SELECT * in production queries
