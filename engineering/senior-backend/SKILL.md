---
name: senior-backend
description: >
  Builds and reviews Node.js REST APIs on PostgreSQL: OpenAPI-to-route scaffolding, schema and
  index analysis with migrations, HTTP load tests with a CI gate. Use when designing endpoints,
  fixing slow queries, or load-testing an API.
license: MIT + Commons Clause
metadata:
  version: 1.2.0
  author: borghei
  category: engineering
  domain: backend
  updated: 2026-11-08
  tags: [api-design, microservices, databases, caching, queues]
---
# Senior Backend Engineer

Scaffold and review backend services: API design and OpenAPI-driven code generation for Express/Fastify/Koa, PostgreSQL schema analysis and migration generation, HTTP load testing, and production security hardening. Outputs ready-to-run route handlers, Zod validators, TypeScript types, migrations with rollbacks, and load-test reports.

## Core Capabilities

- **API scaffolding** — generate route handlers, validation middleware, TypeScript types, and OpenAPI specs across Express, Fastify, and Koa.
- **Database optimization** — schema analysis, missing-index detection, N+1 risk detection, and migration generation with paired rollback scripts.
- **Load testing** — configurable concurrency with latency percentiles (P50/P90/P95/P99), throughput, error rates, and endpoint comparison.
- **Security hardening** — JWT config, rate limiting, input validation (Zod), and security headers (helmet) for production readiness.
- **Standardized contracts** — consistent `data`/`error`/`meta` response envelope and HTTP status conventions.

## When to Use

- Designing a new API or refactoring existing endpoints.
- Slow queries or database performance needs improvement.
- Preparing an API for production or after a security review.
- Building regression/load-test baselines for backend endpoints.

## Clarify First

Before scaffolding, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Framework:** Express / Fastify / Koa (`--framework`; changes the generated route handlers, validators, and types).
- **API contract source:** the OpenAPI spec or endpoint list to scaffold from (the input the scaffolder reads).
- **Database intent:** the schema file and whether you want analysis vs migration generation (drives `database_migration_tool.py`).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Tools Overview

| Tool | Purpose | Command |
|------|---------|---------|
| `api_scaffolder.py` | Route handlers, Zod validators and TS types from an OpenAPI spec (JSON, or block-style YAML; flow-style YAML needs PyYAML) | `python3 scripts/api_scaffolder.py openapi.json --framework express --output src/routes/` |
| `database_migration_tool.py` | PostgreSQL schema analysis, index suggestions, migrations with rollbacks | `python3 scripts/database_migration_tool.py schema.sql --analyze` |
| `api_load_tester.py` | HTTP load test with latency percentiles, throughput and comparison; `--min-success` turns it into a CI gate | `python3 scripts/api_load_tester.py https://staging.example.com/health --concurrency 20 --duration 30 --min-success 99` |

**Exit codes:** 0 done; 1 `api_load_tester.py` success rate below `--min-success`; 2 unusable input (unreadable spec, unsupported YAML, bad arguments). Without `--min-success` the load tester reports failures but exits 0, so set it in CI.

## Quick Start

```bash
# from engineering/senior-backend/; write generated code outside the repo
python3 scripts/database_migration_tool.py assets/sample_schema.sql --analyze    # flags the unindexed orders.user_id
python3 scripts/api_scaffolder.py assets/sample_openapi.json --framework express --output "$(mktemp -d)"
```

Run load tests only against systems you own or are allowed to test, and never against production without agreement: the tester sends real traffic.

## Reference Documentation

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/tools-reference.md](references/tools-reference.md)** — full usage examples, flag tables, and sample output for the scaffolder, migration tool, and load tester, plus quick-start and common commands. Read when running any tool.
- **[references/workflows-and-patterns.md](references/workflows-and-patterns.md)** — the API-design, database-optimization, and security-hardening workflows, common response/index patterns, the troubleshooting table, and the success-criteria bar. Read when designing or hardening a service.
- **[references/api_design_patterns.md](references/api_design_patterns.md)** — REST vs GraphQL, versioning, error handling, pagination. Read when designing new APIs.
- **[references/database_optimization_guide.md](references/database_optimization_guide.md)** — indexing strategies, query optimization, N+1 solutions. Read when fixing slow queries.
- **[references/backend_security_practices.md](references/backend_security_practices.md)** — OWASP Top 10, auth patterns, input validation. Read when hardening security.

## Anti-Patterns

**Mistake:** Adding an index for every slow query.
**Why it matters:** Each index slows writes and costs memory; overlapping indexes are common after a few rounds.
**Instead:** Read the query plan (`EXPLAIN ANALYZE`), add the index that the plan needs, and drop ones that are never used.

**Mistake:** Shipping a migration without a tested rollback.
**Why it matters:** A failed deploy then needs a manual fix under pressure, and data changes may not reverse cleanly.
**Instead:** Generate the rollback with the migration, run both on a copy of production data, and use expand-then-contract for breaking changes.

**Mistake:** Reading a load test that "finished" as a pass.
**Why it matters:** A run where most requests failed still prints latency numbers.
**Instead:** Check the success rate first, and gate CI with `--min-success`.

## Files

| File | Purpose |
|------|---------|
| `scripts/api_scaffolder.py`, `scripts/database_migration_tool.py`, `scripts/api_load_tester.py` | CLIs (stdlib; PyYAML optional for flow-style YAML) |
| `assets/sample_openapi.json` | Orders API with list and create operations |
| `assets/sample_schema.sql` | Two tables with an unindexed foreign key |

## Scope & Limitations

**What this skill covers:**
- REST API design, scaffolding, and OpenAPI-driven code generation for Express, Fastify, and Koa
- PostgreSQL schema analysis, index optimization, migration generation with rollback support
- HTTP load testing with latency percentile analysis, throughput measurement, and endpoint comparison
- Backend security patterns including JWT configuration, rate limiting, input validation, and security headers

**What this skill does NOT cover:**
- Frontend development, UI components, or client-side state management -- see `senior-frontend`
- Infrastructure provisioning, container orchestration, or CI/CD pipeline setup -- see `senior-devops`
- GraphQL schema design, resolvers, or subscriptions -- see `senior-fullstack`
- Application performance monitoring (APM), distributed tracing, or log aggregation -- see `senior-secops`
