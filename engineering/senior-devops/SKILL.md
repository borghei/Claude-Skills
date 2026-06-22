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

Before generating pipelines or infra, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **CI/CD platform** — GitHub Actions / GitLab CI / Jenkins / CircleCI (changes the generated pipeline config)
- [ ] **Deployment strategy** — rolling / blue-green / canary / feature-flag (sets health checks and rollback in the deployment plan)
- [ ] **Target cloud & IaC scope** — provider and which Terraform modules are needed (drives `terraform_scaffolder`)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `pipeline_generator.py` | Analyze a project and generate a CI/CD pipeline config (GitHub Actions, GitLab CI, Jenkins, CircleCI) | `python scripts/pipeline_generator.py <project-path> --json` |
| `terraform_scaffolder.py` | Scaffold a Terraform module structure with state config | `python scripts/terraform_scaffolder.py <target-path> --json` |
| `deployment_manager.py` | Produce a deployment plan with health checks and rollback | `python scripts/deployment_manager.py <target-path> --json` |

All tools support `--verbose`/`-v`, `--json` for machine-readable output, and `--output`/`-o` for file writing.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/devops-workflows-and-operations.md](references/devops-workflows-and-operations.md)** — the three end-to-end workflows (containerize & deploy, Terraform IaC, CI/CD design) with worked Dockerfile/YAML/HCL examples, the deployment-strategy selection matrix and canary ladder, monitoring essentials (Four Golden Signals, SLO targets), anti-patterns, and the troubleshooting table. Read when executing any workflow or diagnosing an incident.
- **[references/cicd_pipeline_guide.md](references/cicd_pipeline_guide.md)** — pipeline patterns, platform comparisons, optimization.
- **[references/infrastructure_as_code.md](references/infrastructure_as_code.md)** — Terraform patterns, module design, state management.
- **[references/deployment_strategies.md](references/deployment_strategies.md)** — strategy details, rollback procedures, traffic management.
- **[references/kubernetes_patterns.md](references/kubernetes_patterns.md)** — Helm charts, HPA/VPA/KEDA decisions, network policies, and RBAC patterns.
- **[references/cloud_platform_guide.md](references/cloud_platform_guide.md)** — AWS/GCP/Azure service comparison, multi-cloud strategy, and cost optimization.

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
