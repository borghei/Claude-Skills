---
name: sql-database-assistant
description: >
  Review SQL queries for index and scan problems, document schemas from DDL, and generate
  migrations with rollback and destructive-change flags. Use when tuning a query, documenting
  a schema, or diffing two schemas.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: databases
  updated: 2026-11-08
  tags: [sql, database, optimization, migration, schema]
---
# SQL Database Assistant

> **Category:** Engineering
> **Domain:** Database Development & Optimization

## Overview

The **SQL Database Assistant** skill provides tools for analyzing SQL query performance, exploring database schemas from DDL files, and generating migration SQL from schema differences. It helps teams write efficient queries, maintain clean schemas, and manage database evolution safely.

## When to Use

- A query is slow and you want the likely text-level causes before reading its plan.
- You need schema documentation (tables, columns, keys) from DDL.
- You have a current and a target schema and need the migration SQL and its rollback.

## Clarify First

Before analyzing or generating, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Task:** query optimization / schema documentation / migration generation (selects the script).
- **SQL input:** the query, the DDL file, or the from/to schema pair to operate on (the script's actual input).
- **Target database / dialect:** Postgres / MySQL / etc. The scripts have no dialect option and always emit PostgreSQL-style migration SQL, so for another database, adapt the generated statements by hand and note which ones changed.

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

```bash
# Review a file of queries (bundled sample: 8 findings; --strict exits 1 on any finding)
python scripts/query_optimizer.py --file examples/queries.sql --strict

# Review one inline query
python scripts/query_optimizer.py --query "SELECT * FROM users WHERE name LIKE '%john%'"

# Document a schema
python scripts/schema_explorer.py --file examples/schema.sql --format markdown

# Diff two schemas: additive change exits 0, drops exit 1 until reviewed
python scripts/migration_generator.py --from examples/schema.sql --to examples/schema_additive.sql
python scripts/migration_generator.py --from examples/schema.sql --to examples/schema_v2.sql
```

## Tools Overview

| Tool | What it checks or produces | Key flags |
|------|---------------------------|-----------|
| `query_optimizer.py` | `SELECT *`, leading-wildcard `LIKE`, missing `WHERE`, correlated subqueries, join and `OR` patterns, `DISTINCT`, unbounded `ORDER BY`, `= NULL`; comments are ignored | `--file` or `--query`, `--format text/json`, `--strict` |
| `schema_explorer.py` | Table catalog, columns with types/nullability/defaults, indexes, foreign keys | `--file`, `--format text/json/markdown` |
| `migration_generator.py` | UP and commented DOWN SQL for added/dropped tables and columns and type changes, with a destructive-change banner | `--from`, `--to`, `--format`, `--allow-destructive` |

Exit codes: `0` ok; `1` `query_optimizer.py --strict` found something, or
`migration_generator.py` produced destructive steps (drops or type changes) without
`--allow-destructive`; `2` bad input (file not found). Index changes are not diffed.

The optimizer reads query text only. For a real diagnosis ask for the plan
(`EXPLAIN (ANALYZE, BUFFERS)` in PostgreSQL, `EXPLAIN ANALYZE` in MySQL 8) and trust it over
the script when they disagree: look for sequential scans on large tables, row-estimate
errors and sorts or hashes spilling to disk.

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
3. **Generate migration** - Run migration_generator.py; exit 1 means it drops or retypes something
4. **Review SQL** - For every `[DESTRUCTIVE]` step, decide how the data is preserved (backup, copy column, expand-and-contract) before passing `--allow-destructive`
5. **Test** - Apply UP, then the DOWN script, then UP again on a copy of production data
6. **Deploy** - Done when UP and DOWN both ran cleanly on the copy, data in kept columns is unchanged, and the backup of dropped data is verified

### CI Integration

```bash
# Lint SQL queries (--file takes one file, so loop over the directory)
for f in queries/*.sql; do
  python scripts/query_optimizer.py --file "$f" --format json --strict || exit 1
done

# Generate schema docs
python scripts/schema_explorer.py --file schema.sql --format markdown > SCHEMA.md
```

## Scope & Limitations

**In Scope:**
- Static review of a SQL query from a file or string with `query_optimizer.py`: `SELECT *`, likely index candidates, correlated subqueries, missing `WHERE`, join checks and leading-wildcard `LIKE`, with `--strict` for CI.
- Schema documentation from DDL with `schema_explorer.py`: tables, columns, indexes and foreign keys, in text, JSON or Markdown.
- Migration SQL from two DDL files with `migration_generator.py`, with up steps and commented rollback steps.
- Index strategies, query patterns and anti-patterns in `references/sql-optimization.md`.

**Out of Scope:**
- Connecting to a database, running `EXPLAIN` or applying migrations.
- Data modeling and schema design (see `engineering/database-designer/`).
- Zero-downtime migration planning for large systems (see `engineering/migration-architect/`).
- Snowflake-specific tuning (see `engineering/snowflake-development/`).

**Important Caveats:**
- All three tools parse SQL text with patterns. Index advice does not use real table sizes, statistics or query plans.
- The scripts have no dialect option. Generated migrations use PostgreSQL-style syntax such as `ALTER COLUMN ... TYPE` and need adapting for other databases.
- A renamed column is generated as a drop and an add, and rollback steps restore structure, not data. Generated migrations need review and a test on a copy of the database before production.
- `--file` takes a single file, not a directory.

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

## Anti-Patterns

### Trusting DOWN to Restore Data
**Mistake:** Running a migration that drops a column because "there is a rollback script".
**Why it happens:** The DOWN section looks like an undo button.
**Instead:** DOWN recreates the column empty. Copy or back up the data first, and prefer expand-and-contract (add new, backfill, switch reads, drop later).

### Adding Indexes From Text Alone
**Mistake:** Creating every index the optimizer suggests.
**Why it happens:** Each suggestion looks cheap.
**Instead:** Indexes cost writes and storage. Confirm with the query plan and the column's selectivity, and check for an existing composite index that already covers it.

### Renames as Drop and Add
**Mistake:** Applying a generated drop-plus-add for what is really a renamed column.
**Why it happens:** A schema diff cannot tell a rename from a replacement.
**Instead:** Replace the pair with `ALTER TABLE ... RENAME COLUMN` (or a staged copy for zero downtime) before running it.

## Files

| File | Purpose |
|------|---------|
| `scripts/query_optimizer.py` | Static SQL query review |
| `scripts/schema_explorer.py` | Schema documentation from DDL |
| `scripts/migration_generator.py` | Schema diff to UP/DOWN migration with destructive flags |
| `examples/queries.sql` | Queries with deliberate anti-patterns |
| `examples/schema.sql` | Six-table e-commerce schema |
| `examples/schema_additive.sql`, `schema_v2.sql` | Target schemas: additive (exit 0) and destructive (exit 1) |
| `references/sql-optimization.md` | Index strategies, query patterns, anti-patterns |
