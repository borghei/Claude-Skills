---
name: database-schema-designer
description: >
  Design a new relational schema from product requirements: tables, ORM models, RLS,
  indexes, migrations and an ERD. Use when modelling a new feature, adding multi-tenancy
  or soft deletes, or writing Drizzle/Prisma/Alembic schemas.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: data-architecture
  tier: POWERFUL
  updated: 2026-11-08
  frameworks: drizzle, prisma, alembic, typeorm
  tags:
    - schema-design
    - normalization
    - erd
    - row-level-security
    - postgresql
---
# Database Schema Designer

The agent turns product requirements into a normalized relational schema with the cross-cutting columns, constraints, Row-Level Security, indexes, migrations and generated types the application needs, for PostgreSQL, MySQL or SQLite with Drizzle, Prisma, TypeORM or Alembic.

## Core Capabilities

- **Schema design from requirements** — extract entities/relationships from natural language, apply 1NF–3NF normalization, add timestamps/soft-delete/audit/versioning, generate complete DDL.
- **Migration planning** — forward and rollback migrations, zero-downtime patterns for large tables, column additions/type changes/backfills across Drizzle, Prisma, TypeORM, Alembic, and raw SQL.
- **Index strategy** — composite, partial, covering, and GIN/GiST indexes mapped to query patterns; bloat detection and maintenance.
- **Type generation** — TypeScript interfaces + Zod schemas and Python dataclasses + Pydantic models from the DB schema (enums as string unions).
- **Security** — Row-Level Security for multi-tenant isolation, column-level PII encryption, audit logging with before/after JSON snapshots.

## When to Use

- Designing tables for a new feature
- Checking a schema you are designing for missing indexes and conventions (for deep analysis of an existing schema and index tuning, use `engineering/database-designer`)
- Adding multi-tenancy to a single-tenant schema
- Planning a breaking schema migration
- Generating ERD documentation for a service

## Clarify First

Before designing the schema, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Requirements or existing DDL:** the entities/relationships in natural language, or the schema to review (the source the design is derived from).
- **Engine & ORM:** PostgreSQL/MySQL/SQLite and Drizzle/Prisma/TypeORM/Alembic (sets the migration and type-generation output format).
- **Cross-cutting needs:** multi-tenancy/RLS, soft deletes, audit trails, or temporal data (determines which patterns and policies are generated).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Workflow

1. **Model.** List the entities, their relationships and cardinalities from the requirements; normalize to 3NF, then denormalize only where a read path needs it and say why.
2. **Add the cross-cutting columns** each table needs: `id`, `created_at`, `updated_at`, and where required `deleted_at`, `organization_id`, `version`.
   - Primary keys: UUIDv7 (time-ordered, so B-tree inserts stay local) stored in the native `uuid` type, or CUID2 where IDs are generated in the app. PostgreSQL 18+ can generate UUIDv7 with `uuidv7()`. Use integer identity keys only for internal tables whose IDs never leave the database.
3. **Write the DDL or ORM schema**, with a foreign-key index on every FK column, partial indexes for soft-deleted tables, and RLS policies for multi-tenant tables (see `references/schema-design-and-security.md`).
4. **Validate** with `schema_validator.py` and fix every error; then render the ERD with `erd_generator.py` and check that it matches the requirements.
5. **Migrate.** For a change to an existing schema, diff the two DDL versions with `migration_diffr.py`, review the forward and rollback SQL, and use the zero-downtime patterns in `references/indexes-and-migrations.md` for large tables.

## Quick Start

```bash
python3 scripts/schema_validator.py assets/sample_schema_v1.sql               # warnings only (exit 0)
python3 scripts/schema_validator.py assets/sample_schema_v2.sql               # new table without FK indexes (exit 1)
python3 scripts/migration_diffr.py assets/sample_schema_v1.sql assets/sample_schema_v2.sql   # forward + rollback SQL
python3 scripts/erd_generator.py assets/sample_schema_v2.sql                  # Mermaid ERD
```

## Tools Overview

| Tool | What it does | Key flags | Exit codes |
|------|--------------|-----------|------------|
| `scripts/schema_validator.py <file.sql>` | Missing PK, sequential PK, FK without index, nullable FK, missing timestamps, soft deletes without a partial index, tables with no index, naming | `--json`, `--strict` (warnings fail too) | 0 clean, 1 errors (or warnings with `--strict`), 2 bad input |
| `scripts/migration_diffr.py <old.sql> <new.sql>` | Added/removed tables and columns, type and nullability changes, index changes, with rollback | `--json`, `--no-rollback`, `-o <file>` | 0 no differences, 1 differences found, 2 bad input |
| `scripts/erd_generator.py <file.sql>` | Mermaid `erDiagram` with PK/FK markers and a table summary | `-o <file.mmd>`, `--json` | 0, 2 bad input |

## Anti-Patterns

**Mistake:** Exposing sequential integer IDs in URLs and APIs.
**Why it happens:** `SERIAL` is the default in most tutorials.
**Instead:** Use UUIDv7 or CUID2 for anything that leaves the database; sequential IDs leak volume and invite enumeration.

**Mistake:** Multi-tenant tables that rely on the application to filter by tenant.
**Why it happens:** A `WHERE organization_id = ?` in the repository layer feels sufficient.
**Instead:** Add RLS policies keyed on the tenant column so a missed filter returns nothing instead of another tenant's rows.

**Mistake:** Foreign keys without an index.
**Why it happens:** PostgreSQL does not create one automatically.
**Instead:** Index every FK column; joins and cascading deletes scan the child table otherwise. `schema_validator.py` reports each one.

## Files

- `scripts/schema_validator.py`, `scripts/migration_diffr.py`, `scripts/erd_generator.py` — the tools above.
- `assets/sample_schema_v1.sql` and `assets/sample_schema_v2.sql` — two versions of a small multi-tenant schema (v2 adds soft deletes, due dates and a comments table without FK indexes).

## Reference Documentation

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/schema-design-and-security.md](references/schema-design-and-security.md)** — the 4-step requirements-to-schema process, the full Drizzle ORM schema example, cross-cutting concerns, and PostgreSQL Row-Level Security policies. Read when designing a new schema or adding multi-tenancy.
- **[references/indexes-and-migrations.md](references/indexes-and-migrations.md)** — the index-type decision framework, index anti-patterns, zero-downtime migration patterns (add NOT NULL column, rename column), and Mermaid ERD generation. Read when choosing indexes or planning a safe migration.
- **[references/best-practices-and-troubleshooting.md](references/best-practices-and-troubleshooting.md)** — common pitfalls, best practices, the troubleshooting table, and the success-criteria bar. Read before shipping a schema or when diagnosing a problem.

## Scope & Limitations

**This skill covers:**
- Relational schema design for PostgreSQL, MySQL, and SQLite including normalization through 3NF
- Migration generation and zero-downtime migration planning for Drizzle, Prisma, TypeORM, and Alembic
- Row-Level Security policies, index strategy, and type generation (TypeScript and Python)
- Cross-cutting patterns: multi-tenancy, soft deletes, audit trails, optimistic locking, and temporal data

**This skill does NOT cover:**
- NoSQL or document database design (MongoDB, DynamoDB, Cassandra) — see `senior-data-engineer` for broader data store guidance
- Query optimization and execution plan analysis beyond index recommendations — see `performance-profiler` for runtime profiling
- Database infrastructure provisioning, replication, or failover configuration — see `senior-cloud-architect` for cloud database setup
- Application-layer ORM patterns, connection pooling, or caching strategies — see `senior-backend` for backend architecture decisions

Related skills: `engineering/database-designer` (analysis and index tuning of existing schemas), `engineering/migration-architect` (cross-service rollout), `engineering/api-design-reviewer` (API resources from the schema).
