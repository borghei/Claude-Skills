---
name: release-orchestrator
description: >
  Orchestrate end-to-end release pipelines. Use when running pre-release validation,
  generating changelogs, bumping semantic versions, scoring deployment readiness, or gating
  releases with secret scanning and GO/NO-GO checks.
license: MIT + Commons Clause
metadata:
  version: 2.2.0
  author: borghei
  category: engineering
  domain: release-engineering
  updated: 2026-06-17
  tags: [release-pipeline, versioning, pre-flight, readiness]
  python-tools: preflight_checker.py, changelog_generator.py, version_bumper.py, release_readiness_scorer.py
  tech-stack: python, git, semver, conventional-commits, ci-cd
---
# Release Orchestrator

The agent runs pre-flight validation, generates changelogs from conventional commits, auto-bumps semantic versions, and scores deployment readiness with a GO/CONDITIONAL/NO-GO decision.

## Core Capabilities

- **Pre-flight validation** — 7 automated checks: branch sync, merge conflicts, dirty tree, secret scanning (AWS/GCP/GitHub/Stripe/JWT), gitignore coverage, conventional commits, dependency lock consistency.
- **Version management** — auto-detect semver bump (PATCH/MINOR/MAJOR) from commit history across `package.json`, `pyproject.toml`, `Cargo.toml`, etc.; pre-release tags (`--pre alpha|beta|rc`).
- **Changelog generation** — Keep a Changelog markdown grouped by type (Added/Changed/Fixed/Security/Breaking) with hashes and `@author` attribution.
- **Deployment readiness** — weighted score across 7 categories (Tests, Code Quality, Docs, Security, Breaking Changes, Dependencies, Rollback) → GO (80+) / CONDITIONAL (60-79) / NO-GO (<60), with single-category blocker at <40.
- **End-to-end pipeline** — chain all tools non-interactively; blocks on pre-flight failure, test failure, or NO-GO. CI/CD steps and pre-push git hook provided.
- **Release types** — hotfix, patch, minor, major, and pre-release flows with branch patterns and bump rules.

## When to Use

- Running pre-release validation or gating a release with secret scanning and GO/NO-GO checks.
- Generating a changelog from conventional commits before tagging.
- Auto-bumping a semantic version from commit history.
- Scoring deployment readiness across tests, quality, security, and rollback.
- Wiring release validation into a CI/CD pipeline or pre-push hook.

## Clarify First

Before orchestrating the release, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Base branch & ref range** — what HEAD is compared against (drives pre-flight branch-sync and the changelog `--from`/`--to`)
- [ ] **Release type** — hotfix / patch / minor / major / pre-release (sets the branch pattern and bump rule)
- [ ] **Gate strictness** — block on CONDITIONAL (60-79) or only on NO-GO (<60) (decides whether the pipeline halts)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `preflight_checker.py` | Run 7 pre-release checks (sync, conflicts, secrets, commits, deps) | `python scripts/preflight_checker.py --repo . --base main --json` |
| `changelog_generator.py` | Generate Keep a Changelog markdown from a ref range | `python scripts/changelog_generator.py --repo . --from v1.2.0 --to HEAD --output CHANGELOG.md` |
| `version_bumper.py` | Auto-detect next semver from commits; write version files | `python scripts/version_bumper.py --repo . --dry-run --json` |
| `release_readiness_scorer.py` | Score readiness 0-100 with GO/CONDITIONAL/NO-GO decision | `python scripts/release_readiness_scorer.py --input release_data.json --json` |

All tools support `--json` for machine output. Exit code 0 = pass, 1 = fail (CI-friendly).

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/release-workflows-and-operations.md](references/release-workflows-and-operations.md)** — quick-start commands, the three core workflows (pre-flight, version/changelog, readiness) with their checkpoint tables, the end-to-end pipeline script, release-type matrix, CI/CD integration YAML, anti-patterns, and the troubleshooting table. Read when running or chaining any workflow.
- **[references/release_engineering_guide.md](references/release_engineering_guide.md)** — release strategies (rolling, blue-green, canary) and release engineering practice. Read when choosing a deployment strategy.
- **[references/rollback_strategies.md](references/rollback_strategies.md)** — database migration rollbacks, reversible-migration rules, and rollback playbooks. Read when planning the rollback portion of a release.
- **[references/ci_cd_best_practices.md](references/ci_cd_best_practices.md)** — pipeline design patterns (stage-gate, fan-out/fan-in) and CI/CD best practices. Read when designing the surrounding pipeline.

## Scope & Limitations

**This skill covers:** pre-flight validation, semantic version bumping, changelog generation, deployment-readiness scoring, and gating releases with GO/NO-GO decisions for git + conventional-commits projects.

**This skill does NOT cover:** the actual deploy/orchestration execution (handled by `senior-devops` / `devops-workflow-engineer`), test authoring (`senior-qa`), or deep security scanning beyond secret pattern-matching (`senior-secops`).

## Integration Points

| Skill | Integration |
|-------|-------------|
| `senior-devops` | Pipeline stages consume pre-flight and readiness JSON as gates |
| `senior-qa` | Test results feed Tests category (25% weight) |
| `senior-secops` | Secret scan and CVE counts feed Security category (15%) |
| `code-reviewer` | Code quality metrics feed Code Quality category (20%) |
| `devops-workflow-engineer` | Workflow YAML calls tools as pipeline steps |
