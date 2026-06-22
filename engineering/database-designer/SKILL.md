---
name: database-designer
description: >
  Database design with schema analysis, index optimization, and migration generation for
  PostgreSQL, MySQL, MongoDB, and DynamoDB. Use when designing schemas, optimizing queries,
  planning migrations, or analyzing database performance.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: databases
  tier: POWERFUL
  updated: 2026-06-17
---
# Database Designer

The agent analyzes SQL schemas for normalization compliance, recommends optimal indexes based on query patterns, and generates safe migration scripts with rollback procedures. It produces Mermaid ERDs, detects redundant indexes, and implements zero-downtime expand-contract migration patterns for PostgreSQL and MySQL.

## Core Capabilities

- **Schema analysis** — detect normalization violations (1NF-BCNF), missing constraints, naming issues, and data-type problems from DDL or JSON.
- **ERD generation** — produce valid Mermaid entity-relationship diagrams from declared relationships.
- **Index optimization** — recommend indexes from query patterns, order composite columns by selectivity, detect redundant/overlapping indexes, and find covering-index opportunities.
- **Migration generation** — forward + rollback SQL between schema versions, with validation queries.
- **Zero-downtime migrations** — expand-contract pattern with safe backfill for tables with 10M+ rows.
- **Database selection guidance** — match workload requirements to PostgreSQL, MySQL, MongoDB, or DynamoDB.

## When to Use

- Designing or reviewing a new schema for normalization and constraints.
- Optimizing queries by recommending or pruning indexes.
- Planning a safe (optionally zero-downtime) migration between schema versions.
- Analyzing database performance and relationship structure (ERD).
- Choosing the right database technology for a workload.

## Clarify First

Before designing or migrating, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Task** — schema analysis/ERD, index optimization, or migration generation (selects `schema_analyzer.py` vs `index_optimizer.py` vs `migration_generator.py`)
- [ ] **Engine** — PostgreSQL, MySQL, MongoDB, or DynamoDB (drives the DDL dialect and selection guidance)
- [ ] **Schema input & query patterns** — the DDL/JSON schema and the queries to optimize for (the input the tools analyze; index recommendations depend on the query patterns)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/workflows-and-tools.md](references/workflows-and-tools.md)** — the Quick Start, three core workflows (analyze/optimize, safe migration, index optimization), and the full CLI reference (flags, usage, output formats) for `schema_analyzer.py`, `index_optimizer.py`, and `migration_generator.py`. Read when running the tools end-to-end.
- **[references/patterns-and-troubleshooting.md](references/patterns-and-troubleshooting.md)** — index-type selection table, anti-patterns, the troubleshooting table for tool output, and the success-criteria quality bar. Read when picking an index type, avoiding mistakes, debugging output, or checking your work.
- **[references/database_selection_decision_tree.md](references/database_selection_decision_tree.md)** — systematic database-technology selection based on requirements, data patterns, and operational constraints. Read when choosing between SQL and NoSQL engines.
- **[references/index_strategy_patterns.md](references/index_strategy_patterns.md)** — proven patterns for index design, optimization strategies, and pitfalls to avoid. Read when designing an indexing strategy in depth.
- **[references/normalization_guide.md](references/normalization_guide.md)** — normal forms (1NF-BCNF), decomposition to eliminate anomalies, and integrity trade-offs. Read when normalizing or deliberately denormalizing a schema.

## Scope & Limitations

**Covers:**
- Schema design analysis for SQL databases (PostgreSQL, MySQL) including normalization, constraints, naming, and data types
- Index optimization with selectivity estimation, composite index ordering, covering indexes, and redundancy detection
- Migration generation with forward/rollback scripts, zero-downtime patterns, and validation queries
- ERD generation in Mermaid format from DDL or JSON schema definitions

**Does NOT cover:**
- Runtime query performance monitoring or live database profiling (see `performance-profiler` skill)
- NoSQL-specific schema design for MongoDB, DynamoDB, or Cassandra (conceptual guidance only in the reference sections)
- Database administration tasks such as backup/restore, replication setup, or user/role management
- Application-level ORM configuration, connection pool tuning, or driver-specific optimizations (see `database-schema-designer` for ORM-adjacent patterns)

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `migration-architect` | Migration strategy and execution planning for large-scale schema changes | Database Designer generates migration SQL; Migration Architect orchestrates multi-service deployment order and rollback coordination |
| `database-schema-designer` | Complementary schema design with focus on application-layer patterns | Database Designer provides normalization analysis; Schema Designer applies ORM mapping and application modeling conventions |
| `performance-profiler` | Runtime validation of index and schema optimization recommendations | Database Designer outputs recommended indexes; Performance Profiler measures actual query plan improvements via EXPLAIN ANALYZE |
| `api-design-reviewer` | Alignment between database schema and API resource contracts | Database Designer defines table structures; API Design Reviewer validates that endpoint schemas match underlying data models |
| `ci-cd-pipeline-builder` | Automated migration execution in deployment pipelines | Database Designer generates migration scripts; CI/CD Pipeline Builder integrates them into deployment stages with validation gates |
| `observability-designer` | Database performance monitoring and alerting post-optimization | Database Designer identifies query patterns; Observability Designer configures slow query alerts and index usage dashboards |
