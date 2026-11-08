---
name: api-test-suite-builder
description: >
  Generates API test skeletons from an OpenAPI spec, measures which endpoints tests really assert
  on, and checks response samples against the spec. Use when adding API tests, auditing API test
  coverage, or catching contract drift.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: api-testing
  tier: POWERFUL
  updated: 2026-11-08
  frameworks: vitest, pytest, supertest, httpx, k6, pact
  tags:
    - api-testing
    - contract-testing
    - load-testing
    - k6
    - openapi
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

Before generating the suite, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Target framework:** Vitest+Supertest, Pytest+httpx, or k6 (determines the emitted test-file format via `--framework`).
- **Spec or routes source:** an OpenAPI spec or the source files to scan (the input the generator parses).
- **Test scope:** auth, input validation, contract, load, or the full matrix (which test categories get generated).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start Workflow

The scripts read OpenAPI 3.x / Swagger 2.0 **JSON** specs. Auth, validation, Pact and k6 patterns
for the parts the scripts do not generate are in the references.

```bash
# 1. Generate skeletons (pytest+httpx or vitest+supertest) into a scratch dir, then move what you keep
python scripts/test_generator.py assets/sample_openapi.json --framework vitest --output /tmp/api-tests

# 2. Measure coverage: endpoints called by a test, and endpoints whose tests assert on the body
python scripts/coverage_analyzer.py assets/sample_openapi.json assets/sample_tests --threshold 50 --show-covered
python scripts/coverage_analyzer.py assets/sample_openapi.json /tmp/api-tests --threshold 95   # exit 1: skeletons only

# 3. Validate recorded responses against the spec's response schemas
python scripts/contract_validator.py assets/sample_openapi.json assets/sample_responses          # exit 0
python scripts/contract_validator.py assets/sample_openapi.json assets/sample_responses_flawed   # exit 1, 3 violations
```

**Tools overview.**
- `test_generator.py` writes one file per tag: 401 tests for secured operations, 422 tests per required field and wrong type, a success test that expects the spec's own 2xx code (201 for create, 204 for delete) on a URL with path parameters filled in, and a skipped placeholder for each declared error code. Every success test carries a TODO to assert on the body; a skeleton proves the route answers, not that it is right.
- `coverage_analyzer.py` pairs each HTTP call with its own method and path, matches `{param}` segments, and ignores skipped tests. It reports two numbers: endpoints called, and endpoints with a body or header assertion. `--threshold` gates on the second, so a suite of status-only skeletons cannot pass a 95% gate.
- `contract_validator.py` matches each sample by filename (`GET_users_200.json`) or a `_meta` block (`{"method", "path", "status"}`) and reports missing required fields, wrong types and disallowed properties; `--strict` also rejects extra properties where the schema does not forbid them.

All three accept `--json`.

**Exit codes.** `0` sound (or files generated); `1` coverage below `--threshold` or a sample violates its contract; `2` missing or unreadable spec, directory or sample set, invalid JSON, or a file that is not an OpenAPI spec.

**Done when:**
1. Every TODO in the generated files is replaced by a real assertion or deleted.
2. The suite runs green against a local or mocked server, and red when you break the handler on purpose.
3. `coverage_analyzer.py --threshold` passes at the bar your team agreed (asserted coverage, not call coverage).
4. Each auth and validation rule in the spec has a negative test, and `contract_validator.py` passes on fresh recorded responses.

## Anti-Patterns

### Status-code-only tests
**Mistake:** Every test asserts `status == 200` and nothing about the body.
**Why it happens:** Generated skeletons look finished, and status checks are easy to write.
**Instead:** Assert the fields the spec promises (ids, types, error messages). `coverage_analyzer.py` counts only these tests toward the gate.

### Testing the happy path only
**Mistake:** No test sends a missing field, a wrong type or an expired token.
**Why it happens:** Negative cases need fixtures and feel like extra work.
**Instead:** Start from the generated 401 and 422 cases and add one negative test per validation rule and per role boundary.

### Contract checks on hand-made samples
**Mistake:** Validating response samples someone typed, which match the spec by construction.
**Why it happens:** Recording real traffic takes setup.
**Instead:** Record responses from a running build (staging or a local server) and validate those. Drift only shows up in real output.

## Files

- `scripts/test_generator.py`, `scripts/coverage_analyzer.py`, `scripts/contract_validator.py` — the three CLIs above.
- `assets/sample_openapi.json` — four-operation Users API; `assets/sample_tests/` — a small hand-written suite (75% called, 50% asserted).
- `assets/sample_responses/` (valid) and `assets/sample_responses_flawed/` (three contract violations).
- `references/` — route detection per framework, test matrices, Pact and k6 scripts, workflow and quality bar.

## Reference Documentation

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/route-detection-and-matrices.md](references/route-detection-and-matrices.md)** — per-framework route-detection shell commands and the full auth / input-validation / pagination test matrices with worked TypeScript examples. Read when scanning a codebase or writing the core test cases.
- **[references/contract-and-load-testing.md](references/contract-and-load-testing.md)** — complete Pact consumer-driven contract test and k6 load-test scripts, plus the commands to run load tests locally, against staging, and in the cloud. Read when adding contract or performance tests.
- **[references/workflow-and-quality.md](references/workflow-and-quality.md)** — the 9-step generation workflow, reusable test-helper patterns (auth, authed request, factories), common pitfalls, best practices, a troubleshooting table, and the success-criteria bar. Read before generating a suite and before shipping it.

## Scope & Limitations

**This skill covers:**
- Generating test skeletons from OpenAPI JSON specs; route-detection recipes for Node.js, Python and Go codebases without a spec
- Authentication, authorization, input validation, pagination, and error-path test generation
- Consumer-driven contract testing with Pact and schema snapshot validation
- Load and performance testing patterns with k6 (reference scripts, not generated)

**This skill does NOT cover:**
- GraphQL API testing (see `engineering/api-design-reviewer` for schema review patterns)
- End-to-end browser testing or UI interaction testing (see `engineering/playwright-pro`)
- Database migration testing or schema validation (see `engineering/database-schema-designer`)
- Security penetration testing beyond input sanitization checks (see `engineering/skill-security-auditor`)

## See Also

- `engineering/api-design-reviewer` — review the spec before generating tests from it.
- `engineering/ci-cd-pipeline-builder` — run the suite and the coverage gate where your team gates merges.
- `engineering/playwright-pro` — browser-level tests for the frontend that calls these APIs.
- `engineering/performance-profiler` — follow up on endpoints that miss k6 thresholds.
