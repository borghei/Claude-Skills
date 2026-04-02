---
name: devops-workflow-engineer
description: >
  Use when designing GitHub Actions workflows, creating CI/CD pipelines,
  planning multi-environment deployments, optimizing pipeline cost and
  execution time, or implementing deployment strategies (blue-green, canary,
  rolling). Generates production-ready workflow YAML, analyzes existing
  pipelines for optimization, and creates deployment plans.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: devops
  updated: 2026-04-02
  tags: [github-actions, ci-cd, deployment, workflows]
  python-tools: workflow_generator.py, pipeline_analyzer.py, deployment_planner.py
  tech-stack: python, github-actions, yaml, ci-cd
---
# DevOps Workflow Engineer

The agent generates GitHub Actions workflow YAML, analyzes existing pipelines for optimization opportunities, and creates deployment plans with strategy selection, health checks, and rollback procedures.

---

## Quick Start

```bash
# Generate a CI workflow
python scripts/workflow_generator.py --type ci --language python --test-framework pytest

# Analyze existing pipelines for optimization
python scripts/pipeline_analyzer.py .github/workflows/ --format json

# Plan a deployment strategy
python scripts/deployment_planner.py --type webapp --environments dev,staging,prod --strategy canary
```

## Tools Overview

| Tool | Input | Output |
|------|-------|--------|
| `workflow_generator.py` | Workflow type + language | GitHub Actions YAML (ci, cd, release, security-scan, docs-check) |
| `pipeline_analyzer.py` | Workflow file or directory | Optimization findings, cost estimates, severity ratings |
| `deployment_planner.py` | Project type + environments | Deployment plan with strategy, health checks, rollback |

All tools support `--format json` and `--output` for file writing.

---

## Workflow 1: CI Pipeline Design

The agent generates pipelines following fail-fast ordering:

1. **Lint and format** (~30s) -- cheapest gate first
2. **Unit tests** (~2-5m) -- matrix across versions
3. **Build verification** (~3-8m)
4. **Integration tests** (~5-15m, parallel with build)
5. **Security scanning** (~2-5m)

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: make lint

  test:
    needs: lint
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']
    steps:
      - uses: actions/setup-python@v5
        with: { python-version: "${{ matrix.python-version }}", cache: pip }
      - run: pip install -r requirements.txt
      - run: pytest --junitxml=results.xml

  security:
    needs: lint
    steps:
      - run: pip-audit -r requirements.txt
```

**CI targets:**

| Metric | Target | Fix |
|--------|--------|-----|
| Total CI time | < 10 min | Parallelize, add caching |
| Lint step | < 1 min | Use pre-commit locally |
| Unit tests | < 5 min | Split suites, use matrix |
| Flaky rate | < 1% | Quarantine flaky tests |
| Cache hit rate | > 80% | Review cache keys |

---

## Workflow 2: CD Pipeline and Multi-Environment Deployment

```bash
python scripts/deployment_planner.py --type webapp --environments dev,staging,prod --format json
```

**Environment promotion flow:**
```
Build -> Dev (auto) -> Staging (auto) -> Production (manual approval)
                                              |
                                        Canary (10%) -> Full rollout
```

| Aspect | Dev | Staging | Production |
|--------|-----|---------|------------|
| Trigger | Every push | Merge to main | Manual approval |
| Replicas | 1 | 2 | 3+ (auto-scaled) |
| Secrets | Repository | Environment | Vault/OIDC |
| Monitoring | Basic logs | Full observability | Full + alerting |

**Key CD rules:**
- Build once, deploy the same artifact everywhere
- Tag artifacts with commit SHA for traceability
- Use environment protection rules for production gates
- Maintain rollback capability at every stage

---

## Workflow 3: Pipeline Optimization

```bash
python scripts/pipeline_analyzer.py .github/workflows/ --format json -o report.json
```

The agent checks for:

1. **Missing caching** -- dependencies reinstalled every run
2. **No timeouts** -- stuck jobs burn budget
3. **Sequential chains** that could parallelize
4. **Deprecated actions** with newer versions available
5. **Security issues** -- secrets in logs, missing permissions scoping
6. **Cost inefficiency** -- oversized runners, no path filtering

**Optimization techniques:**

**Path-based filtering** -- skip CI for docs-only changes:
```yaml
on:
  push:
    paths: ['src/**', 'tests/**', 'requirements*.txt']
    paths-ignore: ['docs/**', '*.md']
```

**Concurrency cancellation** -- cancel superseded runs:
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

**Dependency caching:**
```yaml
- uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-deps-${{ hashFiles('**/requirements.txt') }}
```

---

## Deployment Strategies

**Decision tree:**
```
Zero-downtime required?
  No  -> Rolling deployment
  Yes -> Need instant rollback?
    No  -> Rolling with health checks
    Yes -> Budget for 2x infrastructure?
      Yes -> Blue-green
      No  -> Canary
```

**Canary traffic split schedule:**

| Phase | % | Duration | Gate |
|-------|---|----------|------|
| 1 | 5% | 15 min | Error rate < 0.1% |
| 2 | 25% | 30 min | P99 latency < 200ms |
| 3 | 50% | 60 min | Business metrics stable |
| 4 | 100% | -- | Full promotion |

---

## GitHub Actions Patterns

**Reusable workflows** -- define once, call everywhere:
```yaml
# .github/workflows/reusable-deploy.yml
on:
  workflow_call:
    inputs:
      environment: { required: true, type: string }
      image_tag: { required: true, type: string }
    secrets:
      DEPLOY_KEY: { required: true }
```

**OIDC authentication** -- no long-lived credentials:
```yaml
permissions:
  id-token: write
  contents: read
steps:
  - uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: arn:aws:iam::123456789:role/github-actions
      aws-region: us-east-1
```

**Secrets hierarchy:** Organization > Repository > Environment. Never echo secrets; use `add-mask` for dynamic values. Prefer OIDC for cloud auth.

---

## Runner Cost Optimization

| Runner | vCPU | RAM | Cost/min | Best For |
|--------|------|-----|----------|----------|
| 2-core | 2 | 7 GB | $0.008 | Standard tasks |
| 4-core | 4 | 16 GB | $0.016 | Build-heavy |
| 8-core | 8 | 32 GB | $0.032 | Large compilations |
| 16-core | 16 | 64 GB | $0.064 | Parallel test suites |

**Monthly estimate:** `(runs/day) x (avg min/run) x 30 x (cost/min)`
Example: 50 pushes/day x 8 min x 30 = 12,000 min x $0.008 = **$96/month**.

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Monolithic workflow | 45-min single workflow | Split into parallel jobs |
| No caching | Reinstall deps every run | Cache dependencies and builds |
| Secrets in logs | Leaked credentials | `add-mask`, avoid `echo` |
| No timeout | Stuck jobs burn budget | `timeout-minutes` on every job |
| Full matrix every push | 30-min matrix on every commit | Full nightly; reduced on push |
| No rollback plan | Stuck with broken deploy | Automate rollback in CD pipeline |

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Workflow never triggers | Wrong `on:` config or branch name mismatch | Verify triggers match branching strategy |
| Cache miss every run | Volatile cache key (timestamp) | Use `hashFiles()` on lock files |
| Matrix fails on one OS only | Platform-specific paths or deps | Use `shell: bash`; install OS deps per matrix entry |
| Secret not available | Wrong environment scope | Ensure job declares correct `environment:` |
| Health check fails after deploy | App not started before check | Add retry loop with backoff |
| Concurrency cancels needed runs | Overly broad group key | Scope to `workflow-ref`; separate groups for deploy |

---

## References

| Guide | Path |
|-------|------|
| GitHub Actions Patterns | `references/github-actions-patterns.md` |
| Deployment Strategies | `references/deployment-strategies.md` |
| Agentic Workflows Guide | `references/agentic-workflows-guide.md` |

---

## Integration Points

| Skill | Integration |
|-------|-------------|
| `release-orchestrator` | Release workflows align with versioning and changelog |
| `senior-devops` | Deployment strategies complement infra automation |
| `senior-secops` | Security scanning steps feed SecOps dashboards |
| `senior-qa` | CI quality gates map to QA acceptance criteria |
| `incident-commander` | Rollback procedures connect to incident playbooks |

---

**Last Updated:** April 2026
**Version:** 1.1.0
