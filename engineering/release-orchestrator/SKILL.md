---
name: release-orchestrator
description: >
  Use when running pre-release validation, generating changelogs, bumping
  semantic versions, scoring deployment readiness, or orchestrating end-to-end
  release pipelines. Provides pre-flight checks, secret scanning, conventional
  commit parsing, and GO/CONDITIONAL/NO-GO gating.
license: MIT + Commons Clause
metadata:
  version: 2.1.0
  author: borghei
  category: engineering
  domain: release-engineering
  updated: 2026-04-02
  tags: [release-pipeline, versioning, pre-flight, readiness]
  python-tools: preflight_checker.py, changelog_generator.py, version_bumper.py, release_readiness_scorer.py
  tech-stack: python, git, semver, conventional-commits, ci-cd
---
# Release Orchestrator

The agent runs pre-flight validation, generates changelogs from conventional commits, auto-bumps semantic versions, and scores deployment readiness with a GO/CONDITIONAL/NO-GO decision.

---

## Quick Start

```bash
# Pre-flight: branch sync, secrets, conflicts, commits, deps
python scripts/preflight_checker.py --repo . --base main --verbose

# Changelog from conventional commits
python scripts/changelog_generator.py --repo . --from v1.2.0 --to HEAD

# Auto-detect version bump from commit history
python scripts/version_bumper.py --repo . --dry-run

# Score deployment readiness (7 categories, weighted)
python scripts/release_readiness_scorer.py --input release_data.json --json
```

## Tools Overview

| Tool | Input | Output |
|------|-------|--------|
| `preflight_checker.py` | Repo path + base branch | Pass/fail on 7 checks (sync, conflicts, secrets, commits, deps) |
| `changelog_generator.py` | Git repo + ref range | Keep a Changelog markdown with commit grouping |
| `version_bumper.py` | Repo path | Next semver from commit analysis; updates version files |
| `release_readiness_scorer.py` | Release data JSON | Score 0-100, GO/CONDITIONAL/NO-GO decision |

All tools support `--json` for machine output. Exit code 0 = pass, 1 = fail (CI-friendly).

---

## Workflow 1: Pre-Flight Validation

```bash
python scripts/preflight_checker.py --repo . --base main --json
```

The agent runs seven automated checks:

1. **Branch sync** -- local branch up to date with remote base
2. **Merge conflicts** -- dry-run merge to detect conflicts
3. **Uncommitted changes** -- fail if working tree is dirty
4. **Secret scanning** -- pattern-match for API keys, tokens, passwords (AWS, GCP, GitHub, Stripe, JWT)
5. **Gitignore validation** -- `.env`, credential files covered
6. **Conventional commits** -- recent commits follow `type(scope): description`
7. **Dependency audit** -- lock file consistency (package-lock.json, poetry.lock, etc.)

**Validation checkpoint:** All 7 checks pass. Exit code 0.

---

## Workflow 2: Version Management and Changelog

**Step 1 -- Auto-detect version bump.**

```bash
python scripts/version_bumper.py --repo . --dry-run --json
```

| Commit Type | Bump | Example |
|---|---|---|
| `fix:` | PATCH (0.0.x) | `fix(auth): handle expired tokens` |
| `feat:` | MINOR (0.x.0) | `feat(api): add pagination` |
| `feat!:` or `BREAKING CHANGE` | MAJOR (x.0.0) | `feat!: redesign auth flow` |
| `docs:`, `chore:`, `test:` | No bump | `docs: update README` |

Reads from: `package.json`, `pyproject.toml`, `setup.py`, `setup.cfg`, `Cargo.toml`, `VERSION` file.
Pre-release support: `--pre alpha|beta|rc` produces `1.3.0-rc.1`.

**Step 2 -- Generate changelog.**

```bash
python scripts/changelog_generator.py --repo . --from latest --to HEAD --output CHANGELOG.md --full
```

Groups commits by type (Added, Changed, Fixed, Security, Breaking Changes) with hashes and `@author` attribution.

**Step 3 -- Apply version bump.**

```bash
python scripts/version_bumper.py --repo .  # writes to all discovered version files
```

**Validation checkpoint:** `--dry-run` shows expected version. Changelog covers 100% of commits.

---

## Workflow 3: Deployment Readiness

```bash
python scripts/release_readiness_scorer.py --input release_data.json --json
```

The agent scores across 7 weighted categories:

| Category | Weight | Measures |
|----------|--------|----------|
| Tests | 25% | Pass rate, coverage, flaky count |
| Code Quality | 20% | Lint errors, type errors, complexity, duplication |
| Documentation | 15% | README, API docs, changelog, migration guide |
| Security | 15% | No secrets, no critical CVEs, SAST clean |
| Breaking Changes | 10% | Documented, migration path, deprecation notices |
| Dependencies | 10% | Lock files consistent, no yanked packages |
| Rollback Plan | 5% | Procedure documented, DB migration reversible, feature flags |

**Decision thresholds:**

| Score | Decision | Action |
|---|---|---|
| 80-100 | **GO** | Proceed with deployment |
| 60-79 | **CONDITIONAL** | Proceed with mitigations documented |
| 0-59 | **NO-GO** | Address blockers first |

Any single category below 40 triggers a mandatory blocker regardless of overall score.

**Validation checkpoint:** Score >= 80 (GO). Zero category blockers.

---

## End-to-End Release Pipeline

Chain all workflows into a single automated pipeline:

```bash
#!/bin/bash
set -e

# Phase 1: Pre-flight
python scripts/preflight_checker.py --repo . --base main --json > /tmp/preflight.json

# Phase 2: Tests (project-specific)
python -m pytest --cov=src --cov-report=json:coverage.json -v

# Phase 3: Version bump (dry-run)
python scripts/version_bumper.py --repo . --dry-run --json > /tmp/version.json

# Phase 4: Changelog
python scripts/changelog_generator.py --repo . --from latest --to HEAD

# Phase 5: Readiness assessment
python scripts/release_readiness_scorer.py --input release_data.json --json > /tmp/readiness.json
DECISION=$(python -c "import json; print(json.load(open('/tmp/readiness.json'))['decision'])")
echo "Decision: $DECISION"
```

Non-interactive by default. Blocks on: pre-flight failure, test failure, or NO-GO readiness.

---

## Release Types

| Type | Branch Pattern | Bump | Notes |
|------|---------------|------|-------|
| **Hotfix** | `hotfix/v1.2.1` from tag | PATCH | Minimal fix, branches from release tag |
| **Patch** | Standard flow | PATCH | Accumulated bug fixes |
| **Minor** | Standard flow | MINOR | New features, backward compatible |
| **Major** | Standard flow | MAJOR | Breaking changes, needs migration docs |
| **Pre-release** | Standard flow | `--pre alpha\|beta\|rc` | `1.3.0-alpha.1` for testing |

---

## CI/CD Integration

```yaml
- name: Pre-flight Check
  run: python scripts/preflight_checker.py --repo . --base main --json > preflight.json

- name: Version Bump
  run: python scripts/version_bumper.py --repo . --dry-run --json > version.json

- name: Changelog
  run: python scripts/changelog_generator.py --repo . --from latest --to HEAD --output CHANGELOG.md

- name: Readiness Score
  run: python scripts/release_readiness_scorer.py --input release_data.json
```

Git hook: `python scripts/preflight_checker.py --repo . --base main` in `.git/hooks/pre-push`.

---

## Anti-Patterns

1. **Skipping pre-flight** -- secrets ship to production. Always run pre-flight before any release work.
2. **Manual version bumping** -- leads to inconsistencies. Let commit history drive the version.
3. **No rollback plan** -- every release needs documented rollback (git revert, feature flags, or DB migration down).
4. **Ignoring single-category blockers** -- a 95 overall score with 35 Security = NO-GO.
5. **Changelog after release** -- generate before tagging so reviewers can validate.

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Pre-flight "HEAD is detached" | CI checked out specific commit | Check out a named branch first |
| Changelog "No commits found" | `--from` ref does not exist | Verify tag with `git tag -l`; use `--since` date range |
| Version bumper cannot parse version | Non-semver format (e.g., `1.0`) | Use `MAJOR.MINOR.PATCH` in all manifest files |
| Readiness scorer exits 1 despite high score | Single category below 40-point blocker | Check BLOCKERS section; fix failing category |
| Secret scan false positives on test fixtures | Pattern matches example tokens | Lines with "example"/"placeholder" are skipped; move fixtures to non-tracked dir |

---

## References

| Guide | Path |
|-------|------|
| Release Engineering Guide | `references/release_engineering_guide.md` |
| Rollback Strategies | `references/rollback_strategies.md` |
| CI/CD Best Practices | `references/ci_cd_best_practices.md` |

---

## Integration Points

| Skill | Integration |
|-------|-------------|
| `senior-devops` | Pipeline stages consume pre-flight and readiness JSON as gates |
| `senior-qa` | Test results feed Tests category (25% weight) |
| `senior-secops` | Secret scan and CVE counts feed Security category (15%) |
| `code-reviewer` | Code quality metrics feed Code Quality category (20%) |
| `devops-workflow-engineer` | Workflow YAML calls tools as pipeline steps |

---

**Last Updated:** April 2026
**Version:** 2.1.0
