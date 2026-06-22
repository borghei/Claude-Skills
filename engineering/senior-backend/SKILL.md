---
name: senior-backend
description: >
  Backend development with Node.js/Express/Fastify and PostgreSQL. Use when designing REST or
  GraphQL APIs, optimizing database queries, implementing authentication, building
  microservices, handling migrations, or reviewing backend code.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: backend
  updated: 2026-06-17
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

Before scaffolding, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Framework** — Express / Fastify / Koa (`--framework`; changes the generated route handlers, validators, and types)
- [ ] **API contract source** — the OpenAPI spec or endpoint list to scaffold from (the input the scaffolder reads)
- [ ] **Database intent** — the schema file and whether you want analysis vs migration generation (drives `database_migration_tool.py`)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `api_scaffolder.py` | Generate route handlers, Zod validators, and TS types from an OpenAPI spec | `python scripts/api_scaffolder.py openapi.yaml --framework express --output src/routes/` |
| `database_migration_tool.py` | Analyze schemas, suggest indexes, and generate migrations with rollbacks | `python scripts/database_migration_tool.py schema.sql --analyze` |
| `api_load_tester.py` | HTTP load test with latency percentiles, throughput, and comparison | `python scripts/api_load_tester.py https://api.example.com/users --concurrency 50 --duration 30` |

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/tools-reference.md](references/tools-reference.md)** — full usage examples, flag tables, and sample output for the scaffolder, migration tool, and load tester, plus quick-start and common commands. Read when running any tool.
- **[references/workflows-and-patterns.md](references/workflows-and-patterns.md)** — the API-design, database-optimization, and security-hardening workflows, common response/index patterns, the troubleshooting table, and the success-criteria bar. Read when designing or hardening a service.
- **[references/api_design_patterns.md](references/api_design_patterns.md)** — REST vs GraphQL, versioning, error handling, pagination. Read when designing new APIs.
- **[references/database_optimization_guide.md](references/database_optimization_guide.md)** — indexing strategies, query optimization, N+1 solutions. Read when fixing slow queries.
- **[references/backend_security_practices.md](references/backend_security_practices.md)** — OWASP Top 10, auth patterns, input validation. Read when hardening security.

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

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `senior-fullstack` | API routes generated here feed into fullstack project scaffolding | OpenAPI spec &rarr; fullstack scaffolder consumes as API contract |
| `senior-devops` | Migration scripts output here are consumed by CI/CD deployment pipelines | `migrations/` directory &rarr; deployment workflow applies and verifies |
| `senior-security` | Load test results and security hardening output feed into security review | Load test JSON &rarr; security audit validates rate limiting and error handling |
| `senior-qa` | Generated route handlers and validators provide test surface for QA automation | Route files + Zod schemas &rarr; QA generates integration test suites |
| `senior-frontend` | TypeScript types generated by the scaffolder are shared with frontend consumers | `types.ts` &rarr; frontend imports API types for type-safe client code |
| `code-reviewer` | Schema analysis issues and migration diffs feed into code review checklists | Analysis report &rarr; reviewer validates index coverage and naming conventions |
