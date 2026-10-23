---
name: senior-devops
description: >
  DevOps for CI/CD, containers, Kubernetes, and Terraform. Use when building pipelines,
  containerizing apps, managing clusters, provisioning cloud infra, deploying with blue-
  green/canary, or handling infrastructure incidents.
license: MIT + Commons Clause
metadata:
  version: 2.2.0
  author: borghei
  category: engineering
  domain: infrastructure
  updated: 2026-06-17
  tags: [docker, kubernetes, terraform, ci-cd, monitoring]
  python-tools: pipeline_generator.py, terraform_scaffolder.py, deployment_manager.py
  tech-stack: python, docker, kubernetes, terraform, prometheus
---
# Senior DevOps Engineer

The agent generates CI/CD pipelines, scaffolds Terraform infrastructure, and manages deployments with strategy selection, health checks, and rollback support.

## Core Capabilities

- **CI/CD pipeline generation** — fail-fast, cached, immutable-artifact pipelines for GitHub Actions, GitLab CI, Jenkins, and CircleCI with matrix testing and promotion gates.
- **Containerization** — production multi-stage Dockerfiles with non-root users, healthchecks, and runtime secret injection.
- **Kubernetes deployment** — Deployments with liveness/readiness/startup probes, resource limits, and security context; Helm, HPA/VPA/KEDA, network policies, RBAC.
- **Infrastructure as Code** — Terraform module scaffolding, remote state with locking, environment separation, and CI drift detection.
- **Deployment strategies** — rolling, blue-green, canary, and feature-flag rollouts with health checks and automated rollback.
- **Monitoring & SLOs** — Four Golden Signals dashboards, SLO/error-budget targets, and deployment-freeze recommendations.

## When to Use

- Building or optimizing a CI/CD pipeline.
- Containerizing an app or deploying to Kubernetes.
- Provisioning cloud infrastructure with Terraform.
- Choosing and executing a deployment strategy (blue-green/canary).
- Handling an infrastructure incident or rollback.

## Clarify First

Before generating pipelines or infra, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **CI/CD platform:** GitHub Actions / GitLab CI / Jenkins / CircleCI (changes the generated pipeline config).
- **Deployment strategy:** rolling / blue-green / canary / feature-flag (sets health checks and rollback in the deployment plan).
- **Target cloud & IaC scope:** provider and which Terraform modules are needed (drives `terraform_scaffolder`).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Tools

All three are Python standard library only, read local files, make no network calls and never run other programs. Each prints readable text by default and JSON with `--json`, and exits 1 with a one-line `error:` message on bad input.

| Tool | Purpose | Command |
|------|---------|---------|
| `pipeline_generator.py` | Detect the stack (Node with npm/yarn/pnpm, Python with pip/uv/poetry, Go, Rust, Maven, Gradle, Dockerfile) and generate a CI config with cached install, lint, test, build and optional Docker build | `python scripts/pipeline_generator.py <project-path> --json` |
| `terraform_scaffolder.py` | Scaffold a Terraform module, per-environment root modules with remote state and locking, tfvars and a README | `python scripts/terraform_scaffolder.py <target-path> --json` |
| `deployment_manager.py` | Read a JSON deployment spec and plan the release: strategy with reasons, steps, probe thresholds, rollback triggers and runbook | `python scripts/deployment_manager.py <spec.json> --json` |

**Flags.**
- `pipeline_generator.py`: `--platform github-actions|gitlab-ci|circleci|jenkins` (default `github-actions`), `--no-docker`, `--output/-o PATH` (relative to the project; refuses to overwrite without `--force`), `--verbose/-v`. Without `--output` it only prints. Version files are honoured only for Node 18 to 26 and Python 3.8 to 3.14 (otherwise Node 22 or Python 3.12, with a warning). GitHub Actions are pinned to major-version tags by design; pin to commit SHAs for high-assurance repositories (see `references/cicd_pipeline_guide.md`).
- `terraform_scaffolder.py`: `--provider aws|gcp|azure` (S3 + DynamoDB, GCS or azurerm backend), `--name` (default `app`), `--envs` (default `dev,staging,prod`), `--force`, `--dry-run`, `--verbose/-v`. Refuses to write if any target `.tf` or `.tfvars` file exists, unless `--force`; an existing `README.md` or `.gitignore` is always kept, never overwritten. Names must be lowercase with single inner hyphens (`orders-api`). Azure scaffolds include the `subscription_id` that azurerm 4.x requires, keep the environment suffix in the 24-character storage account name, and limit environments to 12 characters without hyphens. The generated README notes that `dev` sets `force_destroy = true` and that bucket names must be globally unique.
- `deployment_manager.py`: `--strategy rolling|blue-green|canary` to override the choice, `--example` to print a sample spec, `--output/-o PATH` to save the JSON plan, `--verbose/-v` to include the resolved spec. It only plans; it executes nothing. `service` must be a Kubernetes name and `version` an image tag, because both appear in the runbook commands.

**Sample inputs** in `assets/`: `sample-node-app/` and `sample-python-app/` (tiny projects), and `deploy-canary.json`, `deploy-blue-green.json`, `deploy-rolling.json` (one spec per strategy).

**Example output.**

```
$ python scripts/pipeline_generator.py assets/sample-node-app
Detected: node 22 (npm), Docker: yes
Stages: install, lint, test, build, docker

# .github/workflows/ci.yml
name: CI
on:
  push:
    branches:
      - main
  pull_request: {}
permissions:
  contents: read
...
```

```
$ python scripts/terraform_scaffolder.py ./infra --provider aws --name orders-api --envs dev,prod
Created 18 files (aws, s3 backend, envs: dev, prod)
infra/
  .gitignore
  README.md
  environments/
    dev/
      backend.tf
      main.tf
...
```

```
$ python scripts/deployment_manager.py assets/deploy-canary.json
Deployment plan: checkout-api 2.3.1 -> 2.4.0  [canary]
  Why: User-facing, medium risk, 400 rps: enough traffic to judge a small slice before exposing everyone.

Steps:
  1. deploy canary: Start checkout-api:2.4.0 next to the stable version with 0% traffic; wait for readiness.
  2. shift 5% [traffic 5%] [bake 10 min]: Route 5% to 2.4.0; compare canary against stable on the rollback triggers for 10 min.
...
Automatic rollback when any of these holds:
  - error rate (5xx / total) > 0.8% (2 consecutive 1-min windows)
  - p99 latency > 330 ms (3 consecutive 1-min windows)
...
```

`deploy-blue-green.json` picks blue-green (high risk, 1-minute rollback tolerance, capacity can double) and `deploy-rolling.json` picks rolling (low risk, internal worker).

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/devops-workflows-and-operations.md](references/devops-workflows-and-operations.md)** — the three end-to-end workflows (containerize & deploy, Terraform IaC, CI/CD design) with worked Dockerfile/YAML/HCL examples, the deployment-strategy selection matrix and canary ladder, monitoring essentials (Four Golden Signals, SLO targets), anti-patterns, and the troubleshooting table. Read when executing any workflow or diagnosing an incident.
- **[references/cicd_pipeline_guide.md](references/cicd_pipeline_guide.md)** — stage order, lockfile installs and cache keys per stack, platform differences, least-privilege and pinning defaults, review checklist. Read with `pipeline_generator.py` output.
- **[references/infrastructure_as_code.md](references/infrastructure_as_code.md)** — module and environment layout, version pinning, remote state and locking per backend, variable validation, plan/apply workflow and drift detection. Read with `terraform_scaffolder.py` output.
- **[references/deployment_strategies.md](references/deployment_strategies.md)** — the strategy selection rules, canary ladder and bake-time formula, probe settings, rollback triggers, runbooks and expand/contract migrations. Read with `deployment_manager.py` output.
- **[references/kubernetes_patterns.md](references/kubernetes_patterns.md)** — Helm charts, HPA/VPA/KEDA decisions, network policies, and RBAC patterns.
- **[references/cloud_platform_guide.md](references/cloud_platform_guide.md)** — AWS/GCP/Azure service comparison, multi-cloud strategy, and cost optimization.

## Scope & Limitations

**In Scope:**
- Generating a starter CI pipeline from a project's files, scaffolding a Terraform module with environments and remote state, and planning a rolling, blue-green or canary release from a spec (the three scripts).
- Guidance and worked examples for containerizing and deploying an application, Terraform infrastructure as code and CI/CD pipeline design, in `references/devops-workflows-and-operations.md`.
- Deployment strategy selection (rolling, blue-green, canary, feature flags), monitoring essentials (Four Golden Signals, SLO targets), anti-patterns and troubleshooting.
- Kubernetes patterns (Helm structure, HPA, VPA and KEDA, network policies, RBAC, container security) in `references/kubernetes_patterns.md`.
- Cloud service comparison, cost optimization, alerting rules and incident runbook templates in `references/cloud_platform_guide.md`.

**Out of Scope:**
- Linting existing pipelines, cache tuning and deploy-stage generation (see `engineering/ci-cd-pipeline-builder/`).
- Static review of Terraform modules and security rules (see `engineering/terraform-patterns/`) and of Helm charts (see `engineering/helm-chart-builder/`).
- Running an incident (see `engineering/incident-commander/`) and designing observability (see `engineering/observability-designer/`).
- Applying anything to a cloud account or cluster. The skill has no cloud, cluster or CI access.

**Important Caveats:**
- `pipeline_generator.py` reads only the project root and generates for the first stack it finds; a monorepo needs one run per package. It stops at the Docker build and does not push images or deploy.
- `terraform_scaffolder.py` writes placeholder state bucket names (`CHANGE-ME`) and one starter storage resource; replace both before `terraform init`.
- `deployment_manager.py` plans from the numbers in the spec. Rollback thresholds are only as good as the `baseline` and `slo` supplied.
- Cloud services, CI platform syntax and Kubernetes APIs change often, so examples need checking against current provider documentation before use.

## Integration Points

| Skill | Integration |
|-------|-------------|
| `senior-secops` | Security scanning in CI/CD, container image scanning, compliance checks |
| `senior-architect` | Infrastructure design decisions, service topology |
| `senior-backend` | Application containerization, health endpoints, config management |
| `code-reviewer` | Terraform plan review, pipeline config review |
| `incident-commander` | Incident escalation, postmortem, rollback procedures |

---

**Last Updated:** June 2026
**Version:** 2.2.0
