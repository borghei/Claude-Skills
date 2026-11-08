---
name: release-orchestrator
description: >
  Gates a release from a live git checkout: preflight checks, secret scan, tag-based SemVer
  bump, changelog and GO/NO-GO score. Use when cutting a release from a repo (offline notes
  and plans from text: release-manager).
license: MIT + Commons Clause
metadata:
  version: 2.3.0
  author: borghei
  category: engineering
  domain: release-engineering
  updated: 2026-11-08
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

Before orchestrating the release, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Base branch & ref range:** what HEAD is compared against (drives pre-flight branch-sync and the changelog `--from`/`--to`).
- **Release type:** hotfix / patch / minor / major / pre-release (sets the branch pattern and bump rule).
- **Gate strictness:** block on CONDITIONAL (60-79) or only on NO-GO (<60) (decides whether the pipeline halts).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `preflight_checker.py` | Run 7 pre-release checks (sync, conflicts, secrets, commits, deps) | `python scripts/preflight_checker.py --repo . --base main --json` |
| `changelog_generator.py` | Generate Keep a Changelog markdown from a ref range | `python scripts/changelog_generator.py --repo . --from v1.2.0 --to HEAD --output CHANGELOG.md` |
| `version_bumper.py` | Auto-detect next semver from commits; write version files | `python scripts/version_bumper.py --repo . --dry-run --json` |
| `release_readiness_scorer.py` | Score readiness 0-100 with GO/CONDITIONAL/NO-GO decision | `python scripts/release_readiness_scorer.py --input release_data.json --json` |

All tools support `--json` for machine output. Exit code 0 = pass, 1 = fail (CI-friendly).

## Reference Documentation

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/release-workflows-and-operations.md](references/release-workflows-and-operations.md)** — quick-start commands, the three core workflows (pre-flight, version/changelog, readiness) with their checkpoint tables, the end-to-end pipeline script, release-type matrix, CI/CD integration YAML, anti-patterns, and the troubleshooting table. Read when running or chaining any workflow.
- **[references/release_engineering_guide.md](references/release_engineering_guide.md)** — release strategies (rolling, blue-green, canary) and release engineering practice. Read when choosing a deployment strategy.
- **[references/rollback_strategies.md](references/rollback_strategies.md)** — database migration rollbacks, reversible-migration rules, and rollback playbooks. Read when planning the rollback portion of a release.
- **[references/ci_cd_best_practices.md](references/ci_cd_best_practices.md)** — pipeline design patterns (stage-gate, fan-out/fan-in) and CI/CD best practices. Read when designing the surrounding pipeline.

## Anti-Patterns

**Mistake:** Tagging a release from a dirty or unpushed working tree.
**Why it matters:** The tag then points at code nobody reviewed, and the build cannot be reproduced.
**Instead:** Let the preflight checker fail the release until the tree is clean and in sync with the remote.

**Mistake:** Overriding a NO-GO score because the date is fixed.
**Why it matters:** The checks that fail (tests, secrets, missing changelog) are the ones that cause rollbacks.
**Instead:** Fix the failing input or record an explicit, named exception with a rollback plan.

**Mistake:** Hand-editing the version in one file.
**Why it matters:** Manifests, in-app constants and docs drift apart, and users see two versions.
**Instead:** Bump with `version_bumper.py` from the commit history, then grep for the old version.

## Files

| File | Purpose |
|------|---------|
| `scripts/preflight_checker.py` | Repo-state checks (clean tree, branch, remote sync, tests, secrets) |
| `scripts/version_bumper.py` | SemVer bump from conventional commits since the last tag |
| `scripts/changelog_generator.py` | Changelog from a git range |
| `scripts/release_readiness_scorer.py` | Weighted GO/NO-GO score from release data |
| `assets/sample_release_data.json` | Release data for the scorer (89/100, GO) |

## Scope & Limitations

**This skill covers:** pre-flight validation, semantic version bumping, changelog generation, deployment-readiness scoring, and gating releases with GO/NO-GO decisions for git + conventional-commits projects.

**This skill does NOT cover:** the actual deploy/orchestration execution (handled by `senior-devops` / `devops-workflow-engineer`), test authoring (`senior-qa`), or deep security scanning beyond secret pattern-matching (`senior-secops`).

**Pick this or `engineering/release-manager`:** this skill works against a live checkout (preflight checks, secret scan, tag-based bumps, GO/NO-GO). `release-manager` works offline on commit text and a release-plan file (notes, version, readiness, rollback runbook, comms plan).
