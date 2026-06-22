---
name: release-manager
description: >
  Automates release management with changelog generation, semantic versioning,
  and release readiness checks. Use when preparing releases, generating
  changelogs, bumping versions, or validating release candidates.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: devops
  tier: POWERFUL
  updated: 2026-06-17
---
# Release Manager

The agent automates release management by parsing conventional commits into structured changelogs, determining semantic version bumps, and assessing release readiness with checklists, rollback runbooks, and stakeholder communication plans.

## Core Capabilities

- **Changelog generation** — parse conventional commits since the last tag into Keep-a-Changelog Markdown/JSON, grouped by type with breaking-change highlights and issue links.
- **Semantic version bumping** — determine MAJOR/MINOR/PATCH from commit types, support pre-release tracks (alpha → beta → rc), emit bump commands for npm, Python, Rust, Git, Docker.
- **Release readiness** — score a release plan across features, quality gates, approvals, and timelines; surface blocking issues.
- **Rollback & comms** — generate rollback runbooks with triggers and time estimates, plus stakeholder communication plans with timed message templates.
- **Workflows** — changelog+bump, readiness assessment, and expedited hotfix releases, each with validation checkpoints.

## When to Use

- Preparing a release — generate the changelog and determine the next version.
- Validating a release candidate — assess readiness and surface blockers.
- Shipping a hotfix — expedited fix, pre-release versioning, tested rollback.
- Auditing commit hygiene — confirm conventional commits drive clean changelogs.

## Clarify First

Before preparing the release, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Last release tag / commit range** — defines the changelog window and the basis for the version-bump decision
- [ ] **Release type** — standard / hotfix / pre-release (alpha→beta→rc) (selects the workflow and versioning track)
- [ ] **Target ecosystem** — npm / Python / Rust / Git / Docker (determines which bump commands are emitted)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `changelog_generator.py` | Generate Keep-a-Changelog from conventional commits | `git log --oneline v1.0.0..HEAD \| python changelog_generator.py --version 1.1.0 --format both` |
| `version_bumper.py` | Determine SemVer bump + emit bump commands | `git log --oneline v1.0.0..HEAD \| python version_bumper.py --current-version 1.0.0 --analysis` |
| `release_planner.py` | Assess release readiness, checklist, rollback, comms | `python release_planner.py --input release-plan.json --include-checklist --include-rollback` |

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/workflows-and-tool-reference.md](references/workflows-and-tool-reference.md)** — quick start, the 3 core workflows with checkpoints, version-bump rules, rollback triggers, anti-patterns, troubleshooting table, success criteria, and the full CLI flag reference for all three scripts. Read when running a release or looking up a flag.
- **[references/conventional-commits-guide.md](references/conventional-commits-guide.md)** — conventional-commit format, types, and footer conventions. Read when fixing commit hygiene so changelog/version tooling works.
- **[references/hotfix-procedures.md](references/hotfix-procedures.md)** — severity classification (P0–P3), hotfix procedures, and best practices across workflows. Read when shipping an emergency fix.
- **[references/release-workflow-comparison.md](references/release-workflow-comparison.md)** — Git Flow vs GitHub Flow vs Trunk-based, with structure, branch types, and trade-offs. Read when choosing or aligning a branching model.

## Scope & Limitations

**This skill covers:**
- Parsing conventional commits and generating structured changelogs in Markdown and JSON formats
- Determining semantic version bumps (major/minor/patch) with pre-release support (alpha, beta, rc)
- Assessing release readiness across features, quality gates, approvals, and timelines
- Generating rollback runbooks, communication plans, and release checklists from structured input

**This skill does NOT cover:**
- Actual CI/CD pipeline execution or deployment automation (see `engineering/ci-cd-pipeline-generator`)
- Live monitoring, alerting, or incident response during deployments (see `engineering/monitoring-alerting-setup`)
- Code review processes or pull request management (see `engineering/code-review-automation`)
- Infrastructure provisioning, container orchestration, or environment management (see `engineering/infrastructure-as-code`)

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `engineering/ci-cd-pipeline-generator` | Embed changelog generation and version bumping as pipeline stages | Git log output flows into `changelog_generator.py`; version bump output feeds pipeline tagging steps |
| `engineering/code-review-automation` | Validate that PR commits follow conventional commit format before merge | Commit messages validated upstream ensure clean input for changelog generation |
| `engineering/monitoring-alerting-setup` | Define rollback triggers based on monitoring thresholds from the rollback runbook | Rollback trigger thresholds (error rate >2x, latency >50%) feed into alert rule configuration |
| `engineering/api-design-reviewer` | Breaking API changes flagged by the reviewer map to MAJOR version bumps | API review findings populate `breaking_changes` arrays in the release plan JSON |
| `engineering/infrastructure-as-code` | Deployment steps in the rollback runbook reference infrastructure rollback commands | Rollback runbook `command` fields contain infrastructure-specific commands (kubectl, DNS, load balancer) |
| `project-management/release-planning` | Release plan JSON structure aligns with PM release tracking artifacts | PM feature lists and approval statuses feed directly into `release_planner.py` input format |
