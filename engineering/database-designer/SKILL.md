---
name: database-designer
description: >
  Analyse an existing SQL schema for normalization and constraint gaps, recommend indexes
  from query patterns, and generate forward/rollback migrations. Use when reviewing DDL,
  tuning indexes, or diffing two schema versions.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: databases
  tier: POWERFUL
  updated: 2026-11-08
  tags:
    - database
    - schema-design
    - indexing
    - migrations
    - postgresql
    - mongodb
---
# Database Designer

The agent analyses an existing relational schema for normalization, constraint, naming and type problems, recommends indexes for the queries that actually run, and generates forward and rollback migrations between two schema versions. To design a new schema from product requirements (ERDs, RLS, ORM models), use `engineering/database-schema-designer` instead.

## When to Use

- Reviewing a schema (DDL or JSON) before or after a change.
- Choosing or pruning indexes for a known set of queries.
- Turning a schema diff into a migration with rollback and validation queries, optionally zero-downtime (expand-contract).
- Choosing between database engines for a workload (reference only).

## Clarify First

Before designing or migrating, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Task:** schema analysis/ERD, index optimization, or migration generation (selects `schema_analyzer.py` vs `index_optimizer.py` vs `migration_generator.py`).
- **Engine:** PostgreSQL or MySQL (drives the DDL dialect; for choosing an engine, see the selection reference).
- **Schema input & query patterns:** the DDL/JSON schema and the queries to optimize for (the input the tools analyze; index recommendations depend on the query patterns).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Workflow

1. **Analyse** the current schema with `schema_analyzer.py` (DDL or JSON). Read the findings as candidates: the transitive-dependency check matches column-name prefixes (`user_id`, `user_email`) and can flag unrelated columns, so confirm each before proposing a split.
2. **Index** with `index_optimizer.py`, which needs the schema as JSON plus the query patterns (`assets/sample_query_patterns.json` shows the shape). Columns already covered by a primary key, a unique constraint or an existing index prefix are not recommended again. Validate each recommendation with `EXPLAIN` on real data before creating it.
3. **Migrate** with `migration_generator.py --current old.json --target new.json`. Review every HIGH-risk step (drops, type changes) and use `--zero-downtime` for large or busy tables. Run the migration on a copy, then run the rollback, before it goes near production.
4. **Verify** that the analyzer's high-severity count went down and the generated rollback restores the original schema.

## Quick Start

```bash
python3 scripts/schema_analyzer.py --input assets/sample_schema.sql --output-format text      # 11 tables, 14 FKs
python3 scripts/schema_analyzer.py --input assets/sample_schema.sql --erd-only               # Mermaid ERD
python3 scripts/index_optimizer.py --schema assets/sample_schema.json --queries assets/sample_query_patterns.json --analyze-existing
python3 scripts/migration_generator.py --current assets/sample_schema.json --target assets/sample_schema_target.json --format sql
```

## Tools Overview

| Tool | What it does | Key flags |
|------|--------------|-----------|
| `scripts/schema_analyzer.py` | Parse DDL (`CREATE TABLE`, inline and table-level `REFERENCES`, `CREATE INDEX`) or JSON; report 1NF-BCNF smells, missing PK/FK/NOT NULL/CHECK, VARCHAR(255) defaults, naming; Mermaid ERD | `--input`, `--output-format json|text`, `--generate-erd`, `--erd-only`, `--output` |
| `scripts/index_optimizer.py` | Recommend single, composite and covering indexes from query patterns; order composite columns by selectivity; flag redundant and overlapping indexes | `--schema`, `--queries`, `--analyze-existing`, `--min-priority 1-4`, `--format json|text` |
| `scripts/migration_generator.py` | Diff two JSON schemas into ordered steps with forward and rollback SQL, risk level and validation queries | `--current`, `--target`, `--format json|text|sql`, `--zero-downtime`, `--include-validations`, `--validate-only` |

Exit codes: 0 report produced, 2 bad input (missing file, invalid JSON, no tables found).

## Anti-Patterns

**Mistake:** Creating every index the optimizer suggests.
**Why it happens:** Each recommendation looks reasonable on its own.
**Instead:** Indexes cost write throughput and storage. Create the ones that serve frequent or slow queries, confirm with `EXPLAIN`, and drop the redundant ones `--analyze-existing` finds.

**Mistake:** Running a generated `DROP COLUMN` or type change directly on a large production table.
**Why it happens:** The SQL is ready to paste.
**Instead:** Use expand-contract (`--zero-downtime`): add, backfill, switch reads, then drop in a later release. Rehearse the rollback first.

**Mistake:** Normalising everything the analyzer flags.
**Why it happens:** Normal forms look like correctness.
**Instead:** Denormalised columns can be deliberate (snapshots of a price at order time, read models). Keep them when they are intentional and say why.

## Files

- `scripts/schema_analyzer.py`, `scripts/index_optimizer.py`, `scripts/migration_generator.py` — the tools above.
- `assets/sample_schema.sql` (DDL, 11 tables), `assets/sample_schema.json` (same schema as JSON), `assets/sample_schema_target.json` (adds `users.phone` and an index, drops `products.brand`), `assets/sample_query_patterns.json`.
- `expected_outputs/` — reference outputs; `README.md` — longer walkthrough.

## Reference Documentation

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/workflows-and-tools.md](references/workflows-and-tools.md)** — the Quick Start, three core workflows (analyze/optimize, safe migration, index optimization), and the full CLI reference (flags, usage, output formats) for `schema_analyzer.py`, `index_optimizer.py`, and `migration_generator.py`. Read when running the tools end-to-end.
- **[references/patterns-and-troubleshooting.md](references/patterns-and-troubleshooting.md)** — index-type selection table, anti-patterns, the troubleshooting table for tool output, and the success-criteria quality bar. Read when picking an index type, avoiding mistakes, debugging output, or checking your work.
- **[references/database_selection_decision_tree.md](references/database_selection_decision_tree.md)** — systematic database-technology selection based on requirements, data patterns, and operational constraints. Read when choosing between SQL and NoSQL engines.
- **[references/index_strategy_patterns.md](references/index_strategy_patterns.md)** — proven patterns for index design, optimization strategies, and pitfalls to avoid. Read when designing an indexing strategy in depth.
- **[references/normalization_guide.md](references/normalization_guide.md)** — normal forms (1NF-BCNF), decomposition to eliminate anomalies, and integrity trade-offs. Read when normalizing or deliberately denormalizing a schema.

## Scope & Limitations

Covers PostgreSQL and MySQL schemas: analysis, indexing and migrations. MongoDB, DynamoDB and other NoSQL stores get only the selection guidance in the references. Does not cover live query profiling (`engineering/performance-profiler`), multi-service migration rollout (`engineering/migration-architect`), or database administration (backups, replication, roles).
