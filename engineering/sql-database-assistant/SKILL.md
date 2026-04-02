---
name: sql-database-assistant
description: >
  This skill should be used when the user asks to "optimize SQL queries",
  "explore database schemas", "generate migration SQL", "analyze query
  performance", or "document database structure".
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: databases
  updated: 2026-04-02
  tags: [sql, database, optimization, migration, schema]
---
# SQL Database Assistant

> **Category:** Engineering
> **Domain:** Database Development & Optimization

## Overview

The **SQL Database Assistant** skill provides tools for analyzing SQL query performance, exploring database schemas from DDL files, and generating migration SQL from schema differences. It helps teams write efficient queries, maintain clean schemas, and manage database evolution safely.

## Quick Start

```bash
# Analyze a SQL query for performance issues
python scripts/query_optimizer.py --file slow_query.sql

# Analyze inline SQL
python scripts/query_optimizer.py --query "SELECT * FROM users WHERE name LIKE '%john%'"

# Explore schema from DDL file
python scripts/schema_explorer.py --file schema.sql

# Generate migration from schema diff
python scripts/migration_generator.py --from old_schema.sql --to new_schema.sql

# JSON output
python scripts/query_optimizer.py --file query.sql --format json
```

## Tools Overview

### query_optimizer.py

Analyzes SQL queries for performance issues and optimization opportunities.

| Feature | Description |
|---------|-------------|
| SELECT * detection | Flags queries selecting all columns |
| Missing index hints | Identifies WHERE/JOIN columns likely needing indexes |
| N+1 detection | Flags correlated subquery patterns |
| Full table scan | Detects queries without WHERE clauses on large tables |
| JOIN analysis | Checks join conditions and types |
| LIKE optimization | Flags leading wildcard LIKE patterns |

### schema_explorer.py

Generates documentation from SQL DDL (CREATE TABLE) files.

| Feature | Description |
|---------|-------------|
| Table catalog | Lists all tables with column counts |
| Column details | Documents types, nullability, defaults |
| Index listing | Catalogs indexes and their columns |
| Relationship mapping | Identifies foreign key relationships |
| Markdown output | Generates schema documentation |

### migration_generator.py

Generates migration SQL by comparing two schema DDL files.

| Feature | Description |
|---------|-------------|
| Column additions | ALTER TABLE ADD COLUMN for new columns |
| Column removals | ALTER TABLE DROP COLUMN for removed columns |
| Type changes | ALTER TABLE ALTER COLUMN for type modifications |
| New tables | CREATE TABLE for entirely new tables |
| Dropped tables | DROP TABLE for removed tables |
| Index changes | CREATE/DROP INDEX for index differences |

## Workflows

### Query Optimization Workflow

1. **Identify slow queries** - Collect queries from slow query log
2. **Analyze** - Run query_optimizer.py on each query
3. **Review findings** - Prioritize by estimated impact
4. **Optimize** - Apply suggested improvements
5. **Verify** - Re-analyze to confirm optimization

### Schema Documentation Workflow

1. **Export DDL** - Dump schema from database
2. **Explore** - Run schema_explorer.py to generate docs
3. **Review** - Check relationships and data types
4. **Publish** - Include in project documentation

### Migration Workflow

1. **Capture current** - Export current schema DDL
2. **Define target** - Write desired schema DDL
3. **Generate migration** - Run migration_generator.py
4. **Review SQL** - Check generated migration for safety
5. **Test** - Apply to staging database first
6. **Deploy** - Apply to production with rollback plan

### CI Integration

```bash
# Lint SQL queries
python scripts/query_optimizer.py --file queries/ --format json --strict

# Generate schema docs
python scripts/schema_explorer.py --file schema.sql --format markdown > SCHEMA.md
```

## Reference Documentation

- [SQL Optimization](references/sql-optimization.md) - Index strategies, query patterns, anti-patterns

## Common Patterns Quick Reference

### Query Anti-Patterns
| Pattern | Issue | Fix |
|---------|-------|-----|
| `SELECT *` | Fetches unnecessary data | List specific columns |
| `LIKE '%term%'` | Cannot use index | Use full-text search |
| Correlated subquery | N+1 query pattern | Rewrite as JOIN |
| No WHERE clause | Full table scan | Add filtering conditions |
| `OR` in WHERE | Poor index usage | Use UNION or IN |
| Functions on indexed columns | Prevents index use | Apply to value side |

### Index Guidelines
| Query Pattern | Index Type |
|--------------|------------|
| `WHERE col = value` | B-tree on col |
| `WHERE col1 = v AND col2 = v` | Composite (col1, col2) |
| `ORDER BY col` | B-tree on col |
| `WHERE col LIKE 'prefix%'` | B-tree on col |
| `WHERE col IN (...)` | B-tree on col |
| Full-text search | Full-text index |

### Migration Safety
- Always generate rollback SQL alongside forward migration
- Test migrations against a copy of production data
- Add columns as nullable first, then backfill, then add constraints
- Never rename columns directly; add new, migrate data, drop old
