---
name: devops-workflow-engineer
description: >
  Generate and optimize GitHub Actions CI/CD workflows. Use when designing workflows, planning
  multi-environment deployments, optimizing pipeline cost and runtime, or implementing blue-
  green, canary, or rolling deployment strategies.
license: MIT + Commons Clause
metadata:
  version: 1.2.0
  author: borghei
  category: engineering
  domain: devops
  updated: 2026-06-17
  tags: [github-actions, ci-cd, deployment, workflows]
  python-tools: workflow_generator.py, pipeline_analyzer.py, deployment_planner.py
  tech-stack: python, github-actions, yaml, ci-cd
---
# DevOps Workflow Engineer

Generate GitHub Actions workflow YAML, analyze existing pipelines for optimization opportunities, and create deployment plans with strategy selection, health checks, and rollback procedures.

## Core Capabilities

- **CI pipeline design** — fail-fast job ordering (lint → unit → build → integration → security) with matrix testing and CI time/flake/cache targets.
- **CD & multi-environment** — dev/staging/prod promotion flows, build-once-deploy-everywhere, environment protection rules, and rollback at every stage.
- **Pipeline optimization** — detect missing caching, missing timeouts, serial chains, deprecated actions, leaked secrets, and oversized runners; apply path filtering and concurrency cancellation.
- **Deployment strategies** — choose blue-green, canary, or rolling via decision tree; canary traffic-split schedule with promotion gates.
- **GitHub Actions patterns** — reusable workflows, OIDC auth, secrets hierarchy, and runner cost estimation.

## When to Use

- Designing a new CI or CD workflow from scratch.
- Planning a multi-environment (dev/staging/prod) deployment.
- Optimizing an existing pipeline's cost or runtime.
- Implementing a blue-green, canary, or rolling deployment strategy.

## Clarify First

Before generating the workflow, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Workflow type** — CI, CD, release, or security-scan (sets `workflow_generator.py --type`)
- [ ] **Stack** — language and test framework (e.g. python/pytest) (drives the generated YAML steps via `--language`/`--test-framework`)
- [ ] **Deployment strategy & environments** — blue-green, canary, or rolling, and which of dev/staging/prod (drives the `deployment_planner.py` plan)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `workflow_generator.py` | Generate GitHub Actions YAML (ci, cd, release, security-scan, docs-check) | `python scripts/workflow_generator.py --type ci --language python --test-framework pytest` |
| `pipeline_analyzer.py` | Analyze workflows for optimization findings, cost estimates, severity ratings | `python scripts/pipeline_analyzer.py .github/workflows/ --format json` |
| `deployment_planner.py` | Generate a deployment plan with strategy, health checks, rollback | `python scripts/deployment_planner.py --type webapp --environments dev,staging,prod --strategy canary` |

All tools support `--format json` and `--output`/`-o` for file writing.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/workflows-and-optimization.md](references/workflows-and-optimization.md)** — the CI / CD / optimization workflows with full YAML, deployment-strategy decision tree and canary schedule, GitHub Actions patterns, runner cost table, anti-patterns, and troubleshooting. Read when building or tuning a pipeline.
- **[references/github-actions-patterns.md](references/github-actions-patterns.md)** — deep GitHub Actions pattern library. Read when authoring advanced workflow YAML.
- **[references/deployment-strategies.md](references/deployment-strategies.md)** — deep deployment strategy guide (blue-green, canary, rolling). Read when planning a release rollout.
- **[references/agentic-workflows-guide.md](references/agentic-workflows-guide.md)** — agentic/automated workflow patterns. Read when wiring up AI-driven or autonomous pipeline steps.

## Integration Points

| Skill | Integration |
|-------|-------------|
| `release-orchestrator` | Release workflows align with versioning and changelog |
| `senior-devops` | Deployment strategies complement infra automation |
| `senior-secops` | Security scanning steps feed SecOps dashboards |
| `senior-qa` | CI quality gates map to QA acceptance criteria |
| `incident-commander` | Rollback procedures connect to incident playbooks |
