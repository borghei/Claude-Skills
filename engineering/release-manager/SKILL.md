---
name: release-manager
description: >
  Turns conventional-commit logs into a changelog and SemVer bump, and scores a
  release plan for readiness, rollback and comms. Use when you have commit text or
  a plan JSON to turn into release notes, a version or a go/no-go.
license: MIT + Commons Clause
metadata:
  version: 1.2.0
  author: borghei
  category: engineering
  domain: devops
  tier: POWERFUL
  updated: 2026-11-08
  tags:
    - release-management
    - semver
    - changelog
    - release-readiness
    - versioning
---
# Release Manager

The agent turns a commit range into release notes and the right version number, and a release plan into a readiness verdict with a rollback runbook and stakeholder messages. The tools work on text you give them (piped `git log` output or JSON), so they run anywhere, including outside the repo.

**Pick this or `engineering/release-orchestrator`:** this skill works offline on commit text and a plan file (notes, version, readiness, rollback, comms). `release-orchestrator` runs against a live checkout: preflight checks, secret scan, tagging and a GO/NO-GO score from repo state.

## When to Use

- Preparing a release: generate the changelog and determine the next version.
- Validating a release candidate: score readiness and surface blockers from a plan JSON.
- Shipping a hotfix: pre-release versioning, a rollback runbook and a comms plan.
- Auditing commit hygiene: see which commits are not conventional and get dropped or miscategorised.

## Clarify First

Before preparing the release, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Last release tag / commit range:** defines the changelog window and the basis for the bump.
- **Release type:** standard / hotfix / pre-release (alpha, beta, rc), which selects the workflow and versioning track.
- **Target ecosystem:** npm / Python / Rust / Git / Docker, which decides the bump commands emitted.

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Workflow

1. Collect commits for the range: `git log --oneline <last-tag>..HEAD` (or default `git log` for bodies and `BREAKING CHANGE:` footers, which the oneline format cannot carry).
2. Run `version_bumper.py` and `changelog_generator.py` on the same input. Read stderr: a `skipped N line(s)` warning means some lines were not commits and were left out.
3. Validation checkpoint: verify that the result matches the commits: every `!` or `BREAKING CHANGE` commit is under Breaking Changes and the bump is MAJOR; every `feat` is under Added; every `fix` under Fixed.
4. For a release candidate, fill a plan JSON (shape: `assets/sample_release_plan.json`) and run `release_planner.py` with `--include-rollback --include-communication`. Pass `--as-of` (or `as_of` in the plan) when the report must be reproducible.
5. Done when: the changelog and bump agree with step 3, the planner reports no blocking issues (or each blocker has an owner), and the rollback runbook names real commands for this system rather than the generated defaults.

## Quick Start

```bash
# from engineering/release-manager/
python3 changelog_generator.py --input assets/sample_git_log.txt --version 2.0.0 --date 2026-01-01 --summary
python3 version_bumper.py --input assets/sample_git_log.txt --current-version 1.2.3 --analysis
```

```bash
python3 release_planner.py --input assets/sample_release_plan.json --include-checklist --include-rollback
python3 changelog_generator.py --input assets/sample_git_log_full.txt --format json
```

The oneline sample has two `!` commits, so the bump is 1.2.3 -> 2.0.0. The plan sample reports BLOCKED (72.2%) with three named blockers.

## Tools Overview

| Tool | Purpose | Example |
|------|---------|---------|
| `changelog_generator.py` | Keep-a-Changelog Markdown/JSON from `git log` (oneline or full) or a JSON commit array | `git log --oneline v1.0.0..HEAD \| python3 changelog_generator.py --version 1.1.0 --format both` |
| `version_bumper.py` | MAJOR/MINOR/PATCH from commit types, pre-release tracks, bump commands | `git log --oneline v1.0.0..HEAD \| python3 version_bumper.py --current-version 1.0.0 --analysis` |
| `release_planner.py` | Readiness score, blockers, checklist, rollback runbook, comms plan | `python3 release_planner.py --input plan.json --include-checklist --include-rollback` |

**Exit codes (all three):** 0 = output produced (a BLOCKED plan is still exit 0: read the Status line); 2 = unusable input (missing or unreadable file, bad JSON, no commits found, bad `--as-of`). Full flag tables are in the tool reference.

## Anti-Patterns

**Mistake:** Feeding `git log --oneline` and trusting it caught every breaking change.
**Why it matters:** `BREAKING CHANGE:` lives in the commit footer, which oneline output drops, so only `!` commits are seen and the bump comes out MINOR.
**Instead:** Use default `git log` output when the team writes footers, or confirm there are none.

**Mistake:** Ignoring the `skipped N line(s)` warning.
**Why it matters:** Skipped lines are commits the tools never saw: missing changelog entries and a possibly wrong bump.
**Instead:** Fix the input (merge headers, wrapped lines, non-hex hashes) and rerun until the warning is gone.

**Mistake:** Shipping the generated rollback runbook unchanged.
**Why it matters:** The default steps and time estimates are generic; in an incident they send people to commands that do not exist.
**Instead:** Supply `rollback_steps` in the plan with this system's real commands and timings.

## Reference Documentation

Load the reference that matches the task:

- **[references/workflows-and-tool-reference.md](references/workflows-and-tool-reference.md)**: the three workflows with checkpoints, version-bump rules, rollback triggers, troubleshooting, success criteria and the full CLI flag reference. Read when running a release or looking up a flag.
- **[references/conventional-commits-guide.md](references/conventional-commits-guide.md)**: commit format, types and footers. Read when fixing commit hygiene.
- **[references/hotfix-procedures.md](references/hotfix-procedures.md)**: severity classes (P0 to P3) and hotfix procedures. Read when shipping an emergency fix.
- **[references/release-workflow-comparison.md](references/release-workflow-comparison.md)**: Git Flow vs GitHub Flow vs trunk-based. Read when choosing a branching model.

## Files

| File | Purpose |
|------|---------|
| `changelog_generator.py`, `version_bumper.py`, `release_planner.py` | The three CLIs (stdlib only, at the skill root) |
| `assets/sample_git_log.txt` | 30 oneline commits including two `!` breaking changes |
| `assets/sample_git_log_full.txt` | 10 full-format commits with bodies and a `BREAKING CHANGE:` footer |
| `assets/sample_commits.json` | The same history as a JSON commit array (`--input-format json`) |
| `assets/sample_release_plan.json` | Plan with features, gates and a pinned `as_of`; reports BLOCKED |
| `expected_outputs/` | Example outputs for comparison |

## Scope & Limitations

**Covers:** parsing conventional commits into Markdown/JSON changelogs; SemVer bumps with pre-release tracks; readiness scoring across features, gates, approvals and timeline; rollback runbooks, checklists and comms plans from a plan JSON.

**Does not cover:**
- Pipeline execution or deployment (see `engineering/ci-cd-pipeline-builder`).
- Live monitoring and alerting during a rollout (see `engineering/observability-designer`).
- Code review (see `engineering/code-reviewer`).
- Infrastructure provisioning (see `engineering/terraform-patterns`).
- Repo-state checks, secret scanning and tagging (see `engineering/release-orchestrator`).
