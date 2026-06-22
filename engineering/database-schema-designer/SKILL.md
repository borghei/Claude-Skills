---
name: database-schema-designer
description: >
  Design relational schemas from requirements with normalization, migrations, ERDs, RLS
  policies, and indexes for PostgreSQL, MySQL, and SQLite. Use when designing new features,
  reviewing schemas, or adding multi-tenancy.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: data-architecture
  tier: POWERFUL
  updated: 2026-06-17
  frameworks: drizzle, prisma, alembic, typeorm
---
# Database Schema Designer

Design normalized relational database schemas from requirements and generate migrations, TypeScript/Python types, seed data, Row-Level Security policies, index strategies, and ERD diagrams. Handles multi-tenancy, soft deletes, audit trails, optimistic locking, polymorphic associations, and temporal data patterns. Supports PostgreSQL, MySQL, and SQLite with Drizzle, Prisma, TypeORM, and Alembic.

## Keywords

database schema, schema design, normalization, migration, ERD, row-level security, indexing, multi-tenancy, soft deletes, audit trail, Drizzle, Prisma, PostgreSQL

## Core Capabilities

- **Schema design from requirements** — extract entities/relationships from natural language, apply 1NF–3NF normalization, add timestamps/soft-delete/audit/versioning, generate complete DDL.
- **Migration planning** — forward and rollback migrations, zero-downtime patterns for large tables, column additions/type changes/backfills across Drizzle, Prisma, TypeORM, Alembic, and raw SQL.
- **Index strategy** — composite, partial, covering, and GIN/GiST indexes mapped to query patterns; bloat detection and maintenance.
- **Type generation** — TypeScript interfaces + Zod schemas and Python dataclasses + Pydantic models from the DB schema (enums as string unions).
- **Security** — Row-Level Security for multi-tenant isolation, column-level PII encryption, audit logging with before/after JSON snapshots.

## When to Use

- Designing tables for a new feature
- Reviewing an existing schema for normalization or performance issues
- Adding multi-tenancy to a single-tenant schema
- Planning a breaking schema migration
- Generating ERD documentation for a service

## Clarify First

Before designing the schema, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Requirements or existing DDL** — the entities/relationships in natural language, or the schema to review (the source the design is derived from)
- [ ] **Engine & ORM** — PostgreSQL/MySQL/SQLite and Drizzle/Prisma/TypeORM/Alembic (sets the migration and type-generation output format)
- [ ] **Cross-cutting needs** — multi-tenancy/RLS, soft deletes, audit trails, or temporal data (determines which patterns and policies are generated)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `erd_generator.py` | Parse SQL DDL and generate a Mermaid ER diagram | `python scripts/erd_generator.py schema.sql -o erd.mmd` |
| `migration_diffr.py` | Diff two SQL schemas into migration ALTER statements (with rollback) | `python scripts/migration_diffr.py old.sql new.sql` |
| `schema_validator.py` | Validate DDL for normalization violations, missing indexes, naming | `python scripts/schema_validator.py schema.sql --strict` |

## References

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

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `migration-architect` | Hands off generated DDL and migration files for sequencing across services | Schema Designer produces migrations, Migration Architect orchestrates cross-service rollout order |
| `api-design-reviewer` | Schema entities map directly to API resource models and endpoint structure | Schema entities and relationships feed into REST/GraphQL resource definitions and validation rules |
| `senior-backend` | Generated types and ORM schemas plug into repository and service layers | TypeScript interfaces and Pydantic models from schema become the backend's data access contracts |
| `performance-profiler` | Index strategy recommendations are validated against real query execution plans | Schema Designer proposes indexes, Performance Profiler confirms effectiveness with `EXPLAIN ANALYZE` data |
| `senior-secops` | RLS policies and column encryption align with security compliance requirements | Security requirements flow in, RLS policies and encryption specifications flow out for audit verification |
| `observability-designer` | Audit log schema provides the foundation for operational dashboards and alerting | Audit log table structure feeds into observability pipelines for change tracking and anomaly detection |
