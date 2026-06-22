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
  updated: 2026-06-17
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

Before producing the review, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Which output** — lint report, design scorecard, or breaking-change detection (selects `api_linter.py`, `api_scorecard.py`, or `breaking_change_detector.py`)
- [ ] **Spec file(s)** — the OpenAPI/Swagger JSON, or the two versions to diff (the input the tools parse)
- [ ] **Quality bar / CI gate** — minimum grade or fail-on-breaking (sets `--min-grade` / `--exit-on-breaking` and how strict the verdict is)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `api_linter.py` | Lint an OpenAPI/Swagger JSON spec for REST conventions and best practices | `python scripts/api_linter.py openapi.json --format json` |
| `breaking_change_detector.py` | Detect breaking changes between two spec versions (with migration guides) | `python scripts/breaking_change_detector.py v1.json v2.json --exit-on-breaking` |
| `api_scorecard.py` | Score API design quality across 5 weighted dimensions (A–F grades) | `python scripts/api_scorecard.py openapi.json --min-grade B` |

## References

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
