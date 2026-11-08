---
name: ci-cd-pipeline-builder
description: >
  Generates GitHub Actions or GitLab CI pipelines from a repo's stack, lints pipelines for
  security and reliability gaps, and finds missing caches. Use when bootstrapping CI, reviewing a
  workflow, adding deploy gates, or speeding up builds.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: devops
  tier: POWERFUL
  updated: 2026-11-08
  frameworks: github-actions, gitlab-ci, circleci, buildkite
  tags:
    - ci-cd
    - github-actions
    - gitlab-ci
    - circleci
    - pipelines
---
# CI/CD Pipeline Builder

The agent generates CI/CD pipelines from detected project stack signals (lockfiles, then manifests), lints existing pipelines, and finds missing caches. The scripts emit GitHub Actions and GitLab CI; CircleCI and Buildkite are covered by the reference templates and guidance only.

## Core Capabilities

- **Stack detection** — infer language/runtime, package manager, build/test/lint commands, framework, and infrastructure (Docker, K8s, Terraform) from lockfiles and manifests.
- **Pipeline generation** — lint/test/build/deploy stages with correct dependencies, caching, matrix builds, artifact passing, and conditional execution.
- **Deployment strategies** — blue-green, canary, rolling updates, recreate, feature-flag integration, and manual approval gates.
- **Security integration** — SAST (CodeQL, Semgrep, Snyk), dependency and container scanning (Trivy, Grype), secret scanning, and SBOM generation.
- **Optimization** — caching matched to package manager, path filtering, concurrency control, and fail-fast matrices.

## When to Use

- Bootstrapping CI/CD for a new repository
- Migrating between CI platforms
- Optimizing slow or flaky pipelines
- Adding deployment stages to an existing CI-only pipeline
- Implementing security scanning in the pipeline
- Setting up multi-environment deployment (staging, production)

## Clarify First

Before generating the pipeline, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Target platform:** GitHub Actions, GitLab CI, CircleCI, or Buildkite (sets the YAML dialect `pipeline_generator.py` emits via `--platform`).
- **Project stack:** language/runtime, package manager, and whether Docker/K8s/Terraform are present (drives stack detection, caching, and which stages are generated).
- **Deployment strategy & gates:** blue-green, canary, rolling, or CI-only, plus any manual approval gates (determines the deploy stages and conditions).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start Workflow

```bash
# 1. See what the generator detects (lockfile first, then package.json / pyproject.toml / Cargo.toml ...)
python scripts/pipeline_generator.py assets/sample_node_project --detect-only

# 2. Generate a workflow; triggers default to the repo's default branch (read from .git), else main
python scripts/pipeline_generator.py assets/sample_node_project --branches main > /tmp/ci.yml
python scripts/pipeline_generator.py . --platform gitlab --deploy

# 3. Lint and check caching on any pipeline file or directory
python scripts/pipeline_linter.py assets/sample_workflows/flawed-ci.yml    # 5 errors, exit 1
python scripts/pipeline_linter.py /tmp/ci.yml                              # clean, exit 0
python scripts/cache_optimizer.py assets/sample_workflows/flawed-ci.yml    # missing npm cache, exit 1
```

## Tools Overview

| Tool | Purpose | Key flags |
|------|---------|-----------|
| `pipeline_generator.py` | Lint, test, build (and with `--deploy` staging/production) jobs for Node, Python and Go; generic fallback otherwise | `--platform github\|gitlab`, `--branches a,b`, `--deploy`, `--detect-only`, `--json` |
| `pipeline_linter.py` | Hardcoded secrets, actions on a retired Node runtime (checkout/setup-node < v5, setup-python/upload-artifact < v6, download-artifact < v7, cache < v5, setup-go < v6, setup-java < v5), actions on `@main`, missing timeouts, concurrency, permissions, retention, ungated production deploys | `--dir`, `--severity`, `--json` |
| `cache_optimizer.py` | Missing or weak dependency caches per package manager, with time savings | `--dir`, `--severity`, `--json` |

Generated jobs use the latest majors as of 2026-11 (checkout v7, setup-node v7, setup-python v7, upload-artifact v7, download-artifact v8, cache v6, setup-go v7) and Node 24; GitHub removed the Node 20 action runtime from hosted runners on 2026-09-23, so older majors fail. For supply-chain hardening, pin third-party actions to a full commit SHA with the tag in a comment; the linter flags only mutable branch refs.

**Exit codes.** `pipeline_linter.py`: `0` no errors, `1` at least one error-level finding. `cache_optimizer.py`: `0` no high-severity suggestion, `1` at least one. Both exit `2` when no file is given or found. `pipeline_generator.py`: `0` generated, `2` the project directory does not exist.

**Done when:**
1. The linter reports no errors on the final pipeline, and the cache optimizer no high items.
2. The pipeline ran once on a branch and failed when a test was broken on purpose (no `|| true` on lint or test steps).
3. Production deploys sit behind an environment with required reviewers or a protected branch condition.
4. Secrets come from the platform's secret store, never from the YAML.

## Anti-Patterns

### Steps that cannot fail
**Mistake:** `npm test || true` or `continue-on-error: true` on lint and test steps.
**Why it happens:** A flaky check blocks a release, and silencing it is the quick fix.
**Instead:** Fix or quarantine the flaky test explicitly. A gate that always passes is worse than none, because it looks like coverage.

### Ungated production deploys
**Mistake:** Any push to the default branch deploys straight to production.
**Why it happens:** It is the shortest path to continuous delivery.
**Instead:** Deploy through an environment with protection rules, or a manual approval job, after staging succeeds.

### Stale or mutable action refs
**Mistake:** `actions/checkout@v2` or `some-org/action@main`.
**Why it happens:** Workflows get copied from old examples.
**Instead:** Use at least the first Node 24 major (the linter errors below it) and pin third-party actions to a SHA.

## Files

- `scripts/pipeline_generator.py`, `scripts/pipeline_linter.py`, `scripts/cache_optimizer.py` — the three CLIs above.
- `assets/sample_node_project/` — package.json-only project (no lockfile) for the generator; `assets/sample_workflows/flawed-ci.yml` — workflow with five lint errors.
- `references/` — pipeline templates per stack and platform, quality and operations checklist.

## Reference Documentation

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/pipeline-templates.md](references/pipeline-templates.md)** — stack-detection heuristics, full GitHub Actions templates (Node.js/pnpm/Next.js and Python/uv/FastAPI), the GitLab CI equivalent, the caching strategy reference table, pipeline optimization techniques, and the deployment-strategy decision framework. Read when generating a pipeline or choosing a deployment strategy.
- **[references/quality-and-operations.md](references/quality-and-operations.md)** — pre-merge validation checklist, common pitfalls, best practices, troubleshooting table, and success criteria. Read before merging a generated pipeline or when one misbehaves.

## Scope & Limitations

**This skill covers:**
- Generating CI/CD pipelines for GitHub Actions and GitLab CI (scripts); CircleCI and Buildkite patterns (references)
- Stack detection from lockfiles, manifests, Dockerfiles, and infrastructure-as-code definitions
- Deployment strategy selection (blue-green, canary, rolling, recreate) with decision framework
- Pipeline optimization including caching, matrix builds, path filtering, and concurrency control

**This skill does NOT cover:**
- Runtime infrastructure provisioning or cloud resource management (see `engineering/saas-scaffolder`)
- Application-level security hardening beyond CI-integrated scanning (see `engineering/skill-security-auditor`)
- Monitoring, alerting, and observability configuration after deployment (see `engineering/observability-designer`)
- Database migration orchestration during deployments (see `engineering/migration-architect`)

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `engineering/dependency-auditor` | Feeds vulnerability scan results into pipeline security gates | Auditor findings trigger pipeline failure or warning annotations |
| `engineering/release-manager` | Coordinates versioning and changelog with deploy stages | Release tags drive conditional deployment job execution |
| `engineering/observability-designer` | Post-deploy health checks and alerting complement pipeline gates | Pipeline triggers smoke tests; observability confirms deployment health |
| `engineering/env-secrets-manager` | Manages secrets referenced by pipeline environment variables | Secret rotation policies feed into pipeline secret store configuration |
| `engineering/migration-architect` | Database migrations run as a pre-deploy step in the pipeline | Migration status gates the application deployment job |
| `engineering/runbook-generator` | Generates rollback runbooks aligned with deployment strategy | Pipeline failure triggers link to the relevant rollback runbook |
