---
name: api-test-suite-builder
description: >
  Generate API test suites from route definitions across frameworks: auth, input validation,
  contract, k6 load testing, mocking, and OpenAPI-driven generation. Use when adding new APIs,
  auditing test coverage, or building regression suites.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: api-testing
  tier: POWERFUL
  updated: 2026-06-17
  frameworks: vitest, pytest, supertest, httpx, k6, pact
---
# API Test Suite Builder

Scan API route definitions across frameworks (Next.js App Router, Express, FastAPI, Django REST, Go net/http), analyze request/response schemas, and generate comprehensive test suites covering authentication, authorization, input validation, error handling, pagination, file uploads, rate limiting, contract testing, and load testing. Outputs ready-to-run test files for Vitest+Supertest (Node), Pytest+httpx (Python), or k6 (load testing).

## Core Capabilities

- **Route detection & analysis** — scan source files to extract endpoints, parse request/response schemas, detect auth middleware and authorization rules across Node, Python, and Go frameworks.
- **Test matrix generation** — auth (valid/invalid/expired tokens, wrong roles), input validation (missing/wrong-type/boundary/injection), error paths (400/401/403/404/409/422/429/500), pagination, file uploads, and rate limiting.
- **Contract testing** — OpenAPI-to-test generation, Pact consumer-driven contracts, schema snapshot testing for breaking-change detection.
- **Load testing** — k6 scripts with ramp-up patterns and SLA thresholds, latency percentile tracking (P50/P95/P99), concurrent user simulation.

## When to Use

- New API added — generate a test scaffold before implementation (TDD).
- Legacy API with no tests — scan and generate baseline coverage.
- Pre-release — ensure all routes have at least smoke tests.
- API contract change — detect and test breaking changes.
- Security audit — generate adversarial input tests.
- Performance validation — create load-test baselines.

## Clarify First

Before generating the suite, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Target framework** — Vitest+Supertest, Pytest+httpx, or k6 (determines the emitted test-file format via `--framework`)
- [ ] **Spec or routes source** — an OpenAPI spec or the source files to scan (the input the generator parses)
- [ ] **Test scope** — auth, input validation, contract, load, or the full matrix (which test categories get generated)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `test_generator.py` | Generate API test skeletons from an OpenAPI/Swagger spec | `python scripts/test_generator.py spec.json --framework vitest --output tests/` |
| `coverage_analyzer.py` | Compare spec endpoints vs existing test files to find gaps | `python scripts/coverage_analyzer.py spec.json tests/ --threshold 95` |
| `contract_validator.py` | Validate response samples against OpenAPI schema contracts | `python scripts/contract_validator.py spec.json samples/ --strict` |

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/route-detection-and-matrices.md](references/route-detection-and-matrices.md)** — per-framework route-detection shell commands and the full auth / input-validation / pagination test matrices with worked TypeScript examples. Read when scanning a codebase or writing the core test cases.
- **[references/contract-and-load-testing.md](references/contract-and-load-testing.md)** — complete Pact consumer-driven contract test and k6 load-test scripts, plus the commands to run load tests locally, against staging, and in the cloud. Read when adding contract or performance tests.
- **[references/workflow-and-quality.md](references/workflow-and-quality.md)** — the 9-step generation workflow, reusable test-helper patterns (auth, authed request, factories), common pitfalls, best practices, a troubleshooting table, and the success-criteria bar. Read before generating a suite and before shipping it.

## Scope & Limitations

**This skill covers:**
- Generating test suites from route definitions for REST APIs across Node.js, Python, and Go frameworks
- Authentication, authorization, input validation, pagination, and error-path test generation
- Consumer-driven contract testing with Pact and schema snapshot validation
- Load and performance testing script generation with k6 and Artillery

**This skill does NOT cover:**
- GraphQL API testing (see `engineering/api-design-reviewer` for schema review patterns)
- End-to-end browser testing or UI interaction testing (see `engineering/playwright-pro`)
- Database migration testing or schema validation (see `engineering/database-schema-designer`)
- Security penetration testing beyond input sanitization checks (see `engineering/skill-security-auditor`)

## Integration Points

| Skill | Integration | Data Flow |
|-------|------------|-----------|
| `engineering/api-design-reviewer` | Validate API design before generating tests | Design review output defines the endpoint contracts that this skill generates tests for |
| `engineering/ci-cd-pipeline-builder` | Embed generated tests into CI/CD pipelines | Generated test files and k6 scripts are added as pipeline stages with pass/fail gates |
| `engineering/playwright-pro` | Complement API tests with E2E browser tests | API test suite validates backend behavior; Playwright tests validate the frontend consuming those APIs |
| `engineering/database-schema-designer` | Align test fixtures with database schema | Schema definitions inform factory functions and seed data used in generated test helpers |
| `engineering/observability-designer` | Monitor test-covered endpoints in production | Load test thresholds (P95, P99) feed into alerting rules for the same endpoints in production dashboards |
| `engineering/performance-profiler` | Investigate endpoints that fail load test thresholds | k6 results identify slow endpoints; the profiler skill traces root causes at the code level |
