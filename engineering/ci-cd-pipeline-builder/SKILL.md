---
name: ci-cd-pipeline-builder
description: >
  Design and generate CI/CD pipelines from project stack signals across GitHub Actions, GitLab
  CI, CircleCI, and Buildkite. Use when bootstrapping CI, migrating pipelines, adding
  deployment gates, or optimizing build times.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: devops
  tier: POWERFUL
  updated: 2026-06-17
  frameworks: github-actions, gitlab-ci, circleci, buildkite
---
# CI/CD Pipeline Builder

Generate production-grade CI/CD pipelines from detected project stack signals. Analyzes lockfiles, manifests, and scripts to produce optimized pipelines with proper caching, matrix strategies, security scanning, and deployment gates. Supports GitHub Actions, GitLab CI, CircleCI, and Buildkite with deployment strategies including blue-green, canary, and rolling updates.

**Keywords:** CI/CD, GitHub Actions, GitLab CI, pipeline, deployment, caching, matrix builds, blue-green deployment, canary deployment, security scanning, SAST, container builds, environment gates

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

Before generating the pipeline, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Target platform** — GitHub Actions, GitLab CI, CircleCI, or Buildkite (sets the YAML dialect `pipeline_generator.py` emits via `--platform`)
- [ ] **Project stack** — language/runtime, package manager, and whether Docker/K8s/Terraform are present (drives stack detection, caching, and which stages are generated)
- [ ] **Deployment strategy & gates** — blue-green, canary, rolling, or CI-only, plus any manual approval gates (determines the deploy stages and conditions)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `pipeline_generator.py` | Generate pipeline YAML from project stack detection | `python scripts/pipeline_generator.py . --platform github --deploy` |
| `cache_optimizer.py` | Analyze pipeline configs and suggest caching improvements | `python scripts/cache_optimizer.py --dir . --severity high` |
| `pipeline_linter.py` | Lint pipeline YAML for common issues | `python scripts/pipeline_linter.py --dir . --severity warning` |

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/pipeline-templates.md](references/pipeline-templates.md)** — stack-detection heuristics, full GitHub Actions templates (Node.js/pnpm/Next.js and Python/uv/FastAPI), the GitLab CI equivalent, the caching strategy reference table, pipeline optimization techniques, and the deployment-strategy decision framework. Read when generating a pipeline or choosing a deployment strategy.
- **[references/quality-and-operations.md](references/quality-and-operations.md)** — pre-merge validation checklist, common pitfalls, best practices, troubleshooting table, and success criteria. Read before merging a generated pipeline or when one misbehaves.

## Scope & Limitations

**This skill covers:**
- Generating CI/CD pipelines for GitHub Actions, GitLab CI, CircleCI, and Buildkite
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
