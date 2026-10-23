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

Before generating the workflow, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Workflow type:** CI, CD, release, or security-scan (sets `workflow_generator.py --type`).
- **Stack:** language and test framework (e.g. python/pytest) (drives the generated YAML steps via `--language`/`--test-framework`).
- **Deployment strategy & environments:** blue-green, canary, or rolling, and which of dev/staging/prod (drives the `deployment_planner.py` plan).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

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

## Scope & Limitations

**In Scope:**
- Generating GitHub Actions YAML with `workflow_generator.py` for CI, CD, release, security-scan and docs-check workflows in Python, Node, Go or Rust, with CD targets for Kubernetes, Docker Compose, AWS ECS or static hosting
- Analyzing existing workflow files with `pipeline_analyzer.py` for missing caching and timeouts, serial job chains, deprecated actions, possible leaked secrets and oversized runners, with severity ratings and cost estimates
- Deployment plans from `deployment_planner.py` for blue-green, canary or rolling releases, with health checks and rollback steps per environment
- Patterns for reusable workflows, OIDC authentication, secrets hierarchy and multi-environment promotion from the references

**Out of Scope:**
- CI systems other than GitHub Actions, such as GitLab CI, CircleCI and Buildkite (see `engineering/ci-cd-pipeline-builder/`)
- Provisioning infrastructure (see `engineering/terraform-patterns/` and `engineering/senior-devops/`)
- Versioning, changelogs and release coordination (see `engineering/release-orchestrator/`)
- Helm chart authoring and review (see `engineering/helm-chart-builder/`)
- Running deployments or watching live rollouts; the tools produce files and plans only

**Important Caveats:**
- Generated workflows are templates. Secrets, environment names, deploy commands and action versions need review before the workflow runs.
- The analyzer parses YAML with a minimal built-in parser and pattern checks. Complex anchors, expressions and reusable-workflow calls can be misread, and it does not run the workflow.
- Runner cost estimates use a fixed per-minute table for GitHub-hosted runners. GitHub pricing and runner images change, so treat the numbers as rough.
- Action versions and deprecations go stale quickly. Check pinned actions against their current releases.

## Integration Points

| Skill | Integration |
|-------|-------------|
| `release-orchestrator` | Release workflows align with versioning and changelog |
| `senior-devops` | Deployment strategies complement infra automation |
| `senior-secops` | Security scanning steps feed SecOps dashboards |
| `senior-qa` | CI quality gates map to QA acceptance criteria |
| `incident-commander` | Rollback procedures connect to incident playbooks |
