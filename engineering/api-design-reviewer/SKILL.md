---
name: api-design-reviewer
description: >
  Review REST API designs for quality, consistency, and breaking changes. Lints OpenAPI specs,
  generates scorecards, and detects breaking changes between versions. Use when designing
  APIs, reviewing contracts, or managing API versioning.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: api-design
  tier: POWERFUL
  updated: 2026-11-08
  tags:
    - api-design
    - rest
    - openapi
    - breaking-changes
    - linting
---
# API Design Reviewer

Comprehensive analysis and review of REST API designs against conventions, best practices, and industry standards. Helps engineering teams build consistent, maintainable, well-designed APIs through automated linting, breaking-change detection, and design scorecards.

## Core Capabilities

- **API linting & convention analysis** — resource naming (kebab-case URLs, camelCase fields), HTTP method usage, URL structure, status-code compliance, error-format consistency, and documentation coverage.
- **Breaking change detection** — endpoint removal, response-shape changes, field removal/rename, type changes, new required fields, and status-code changes between two spec versions, with migration guides.
- **API design scoring** — weighted scorecard across Consistency (30%), Documentation (20%), Security (20%), Usability (15%), and Performance (15%), with letter grades A–F and recommendations.

## When to Use

- Designing a new REST API or reviewing an API contract.
- Validating an OpenAPI/Swagger spec against REST conventions.
- Managing API versioning and detecting breaking changes between releases.
- Gating deployments on API design quality in CI.

## Clarify First

Before producing the review, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Which output:** lint report, design scorecard, or breaking-change detection (selects `api_linter.py`, `api_scorecard.py`, or `breaking_change_detector.py`).
- **Spec file(s):** the OpenAPI/Swagger JSON, or the two versions to diff (the input the tools parse).
- **Quality bar / CI gate:** minimum grade or fail-on-breaking (sets `--min-grade` / `--exit-on-breaking` and how strict the verdict is).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start Workflow

```bash
# 1. Lint conventions (naming, methods, status codes, error format, docs coverage)
python scripts/api_linter.py assets/sample_openapi_v1.json                 # 93/100, 0 errors, exit 0

# 2. Diff two versions for breaking changes, with migration notes
python scripts/breaking_change_detector.py assets/sample_openapi_v1.json assets/sample_openapi_v2.json --exit-on-breaking
#    -> 3 breaking (DELETE removed, User.id integer->string, new required field), exit 1

# 3. Score overall design maturity across five weighted dimensions
python scripts/api_scorecard.py assets/sample_openapi_v1.json --min-grade C   # F (51/100), exit 1
```

## Tools Overview

| Tool | Measures | Gate with it? |
|------|----------|---------------|
| `api_linter.py` | Convention violations; starts at 100 and subtracts per issue, so a small clean spec scores high | Yes: exit 1 on any error-level issue. Use on every PR. |
| `breaking_change_detector.py` | Removed endpoints/methods, type changes, new required fields, status-code changes between two versions | Yes: `--exit-on-breaking` on every PR that touches the spec. |
| `api_scorecard.py` | Design maturity: documentation depth, examples, security coverage, pagination, error guidance; absent features cost points | As a ratchet: set `--min-grade` to today's grade so it cannot drop, and review the recommendations at release time. |

The linter and the scorecard disagree by design. On the sample spec the linter gives 93/100 (few
violations) while the scorecard gives F (missing descriptions, examples, error schemas, rate-limit
docs). Report both and say which question each answers: "does it break our rules?" versus "is it
a complete, well-documented API?".

All three take `--format text|json` and `--output FILE`.

**Exit codes.** `0` pass; `1` linter errors found, breaking changes found (with
`--exit-on-breaking`) or grade below `--min-grade`; `2` missing or unreadable spec, invalid JSON,
or a spec the tool cannot analyse.

**Done when:**
1. The linter reports no errors and every warning is fixed or accepted with a reason.
2. The breaking-change diff against the last released spec is empty, or each breaking change has a version bump and a migration note.
3. The scorecard grade did not drop, and its top recommendation is either done or ticketed.

## Anti-Patterns

### Gating on the wrong score
**Mistake:** Blocking merges on a scorecard grade of B for an API that has never had examples or long descriptions.
**Why it happens:** One number per PR looks tidy.
**Instead:** Gate on linter errors and breaking changes; use the scorecard as a ratchet so it only improves.

### Verbs in paths
**Mistake:** `/getUsers`, `/createOrder`, `/users/delete/{id}`.
**Why it happens:** RPC habits carry over into REST.
**Instead:** Nouns for resources and HTTP methods for actions (`GET /users`, `POST /orders`, `DELETE /users/{id}`). The linter flags these.

### Breaking changes in a minor release
**Mistake:** Changing a field type or adding a required request field without a version bump.
**Why it happens:** The change looks small from the server side.
**Instead:** Run the detector against the last released spec in CI; a breaking change needs a new version or a compatibility shim.

## Files

- `scripts/api_linter.py`, `scripts/breaking_change_detector.py`, `scripts/api_scorecard.py` — the three CLIs above.
- `assets/sample_openapi_v1.json` (Users API) and `assets/sample_openapi_v2.json` (same API with three breaking changes and a verb path).
- `references/` — REST design patterns, rules, anti-patterns, tooling and CI integration.

## Reference Documentation

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/rest-design-patterns.md](references/rest-design-patterns.md)** — REST naming/method/URL principles, versioning strategies, pagination patterns, error formats and status codes, auth/RBAC patterns, rate limiting, HATEOAS, idempotency, backward-compatibility rules, OpenAPI validation, performance, and security best practices. Read when designing or reviewing endpoints.
- **[references/tooling-ci-and-troubleshooting.md](references/tooling-ci-and-troubleshooting.md)** — the three tools' features, CI/CD and pre-commit integration, best-practices and anti-pattern checklists, troubleshooting table, success criteria, and full CLI flag references. Read when wiring tools into pipelines or debugging.
- **[references/rest_design_rules.md](references/rest_design_rules.md)** — detailed REST design rules reference (resources vs actions, HTTP method semantics with worked examples). Read for an in-depth rules catalog.
- **[references/api_antipatterns.md](references/api_antipatterns.md)** — common API anti-patterns (verb-based URLs / RPC trap and more) with bad/good examples and recommended fixes. Read when auditing an existing API for design smells.

## Scope & Limitations

**This skill covers:**
- Linting OpenAPI 3.x and Swagger 2.0 JSON specifications against REST conventions
- Detecting breaking, potentially-breaking, and non-breaking changes between two spec versions
- Scoring API design quality across consistency, documentation, security, usability, and performance
- Generating actionable migration guides when breaking changes are found

**This skill does NOT cover:**
- Runtime API testing, load testing, or contract testing (see `api-test-suite-builder`)
- GraphQL, gRPC, or WebSocket API design review
- Auto-generation of OpenAPI specs from code or server stubs
- Authentication flow implementation or OAuth server configuration (see `senior-security` in engineering/)

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `engineering/api-test-suite-builder` | Generate test cases from linter findings | Linter issues feed into test plan priorities for endpoint validation |
| `engineering/changelog-generator` | Document breaking changes in release notes | Breaking change detector output provides structured change data for changelogs |
| `engineering/ci-cd-pipeline-builder` | Gate deployments on API quality | Scorecard grade and linter exit codes integrate as pipeline quality gates |
| `engineering/senior-backend` | Review API implementation against design | Scorecard recommendations guide backend refactoring decisions |
| `engineering/code-reviewer` | Enrich PR reviews with API analysis | Linter and breaking change reports attach to PR review comments |
| `engineering/release-manager` | Validate version bumps match change severity | Breaking change detector severity levels inform semver version decisions |
