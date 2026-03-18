---
name: release-orchestrator
description: End-to-end release pipeline automation with pre-flight checks, test orchestration, semantic versioning, changelog generation, and deployment readiness validation
license: MIT + Commons Clause
metadata:
  version: 2.0.0
  author: borghei
  category: engineering-team
  domain: release-engineering
  updated: 2026-03-18
  python-tools: preflight_checker.py, changelog_generator.py, version_bumper.py, release_readiness_scorer.py
  tech-stack: python, git, semver, conventional-commits, ci-cd
---

# Release Orchestrator Skill

**Category:** Engineering Team
**Domain:** Release Engineering
**Author:** borghei
**Version:** 2.0.0
**Last Updated:** March 2026

## Overview

The Release Orchestrator is the most comprehensive release automation skill available for AI coding assistants. It provides six composable workflows that cover every stage of the software release lifecycle, from pre-flight validation through deployment readiness assessment. Each workflow operates independently or chains together into a full release pipeline.

Unlike single-pass release scripts, this skill treats releases as a multi-phase quality gate process. Every phase produces a scored assessment, and the final deployment readiness score aggregates all signals into a clear GO / CONDITIONAL / NO-GO decision.

## Keywords

release-automation, semantic-versioning, changelog-generation, pre-flight-checks, deployment-readiness, conventional-commits, rollback-strategy, feature-flags, ci-cd-pipeline, release-engineering, version-management, test-orchestration, code-quality-gate, hotfix-workflow, canary-deployment

## Quick Start

```bash
# 1. Run pre-flight checks before any release work
python scripts/preflight_checker.py --repo /path/to/repo --base main

# 2. Generate changelog from conventional commits
python scripts/changelog_generator.py --repo /path/to/repo --from v1.2.0 --to HEAD

# 3. Auto-detect and bump version
python scripts/version_bumper.py --repo /path/to/repo --dry-run

# 4. Score release readiness
python scripts/release_readiness_scorer.py --input assets/sample_release_data.json
```

## Core Workflows

### Workflow 1: Pre-Flight Validation

Pre-flight validation ensures the repository is in a clean, safe, and mergeable state before any release work begins. This catches problems that would otherwise surface late in the pipeline.

**Steps:**

1. **Branch Sync Check** - Verify local branch is up to date with the remote base branch. Detect divergence and report commits behind/ahead.
2. **Merge Conflict Detection** - Dry-run merge against the base branch to identify conflicts without modifying the working tree.
3. **Uncommitted Changes Scan** - Fail if the working tree has staged or unstaged changes that would be lost during release.
4. **Secret Scanning** - Pattern-match for API keys, tokens, passwords, private keys, and connection strings across all staged files. Covers AWS, GCP, GitHub, Stripe, Slack, JWT, and generic patterns.
5. **Gitignore Validation** - Confirm that `.env`, credential files, and key directories are covered by `.gitignore`.
6. **Conventional Commit Validation** - Parse recent commits and flag any that do not follow the `type(scope): description` format.
7. **Dependency Audit** - Check for known lock file inconsistencies (package-lock.json vs package.json, poetry.lock vs pyproject.toml).

**Tool:** `preflight_checker.py`

```bash
python scripts/preflight_checker.py --repo . --base main --verbose
```

**Output:** Pass/fail checklist with details for each check. Exit code 0 on all-pass, 1 on any failure.

---

### Workflow 2: Test Orchestration

Test orchestration discovers, executes, and analyzes test suites. This is a concrete, executable workflow — not a wish list.

**Step 1 — Test Discovery:** Auto-detect the project's test framework by scanning for config files:

```bash
# Python: look for pytest.ini, setup.cfg [tool:pytest], pyproject.toml [tool.pytest]
ls pytest.ini setup.cfg pyproject.toml conftest.py 2>/dev/null

# JavaScript: look for jest.config.*, vitest.config.*, .mocharc.*
ls jest.config.* vitest.config.* .mocharc.* 2>/dev/null

# Go: test files are *_test.go (built-in)
find . -name "*_test.go" | head -5

# Rust: look for #[test] in src/ or tests/ directory
ls tests/ 2>/dev/null; grep -rl "#\[test\]" src/ 2>/dev/null | head -5
```

**Step 2 — Test Execution:** Run with coverage enabled:

```bash
# Python (pytest)
python -m pytest --cov=src --cov-report=json:coverage.json --cov-report=term -v

# JavaScript (jest)
npx jest --coverage --coverageReporters=json-summary --verbose

# Go
go test -coverprofile=coverage.out -v ./...

# Rust
cargo test --verbose 2>&1; cargo tarpaulin --out json
```

**Step 3 — Coverage Analysis:** Parse coverage output and compute delta vs main:

```bash
# Get main branch coverage (if saved)
git stash && git checkout main && python -m pytest --cov=src --cov-report=json:coverage_main.json -q
git checkout - && git stash pop

# Compare: current vs main
python -c "
import json
with open('coverage.json') as f: curr = json.load(f)['totals']['percent_covered']
with open('coverage_main.json') as f: main = json.load(f)['totals']['percent_covered']
delta = curr - main
print(f'Coverage: {curr:.1f}% (delta: {delta:+.1f}%)')
if delta < -2: exit(1)  # Block if coverage dropped >2%
"
```

**Step 4 — Flaky Test Detection:** Re-run failing tests 3x. If intermittent, mark as flaky:

```bash
# Collect failing tests from initial run
FAILING=$(python -m pytest --tb=no -q 2>&1 | grep FAILED | awk '{print $1}')

# Re-run each failing test 3 times
for test in $FAILING; do
  PASS=0; for i in 1 2 3; do python -m pytest "$test" -q && PASS=$((PASS+1)); done
  if [ $PASS -gt 0 ] && [ $PASS -lt 3 ]; then echo "FLAKY: $test"; fi
done
```

**Step 5 — Coverage Gate:** Block release if coverage drops >2% from main branch. Warn if coverage is below 80%.

**Integration:** Feed test results JSON into the readiness scorer for the Tests category (25% weight).

---

### Workflow 3: Code Quality Gate

The code quality gate runs concrete checks using standard tooling. Each check is independently executable.

**Check 1 — Linting:**

```bash
# Python
ruff check . --output-format=json > lint_results.json 2>/dev/null || \
  python -m pylint src/ --output-format=json > lint_results.json

# JavaScript/TypeScript
npx eslint . --format json -o lint_results.json

# Go
golangci-lint run --out-format json > lint_results.json

# Rust
cargo clippy --message-format=json > lint_results.json
```

**Check 2 — Type Checking:**

```bash
# TypeScript
npx tsc --noEmit 2>&1 | tail -1  # "Found 0 errors" = pass

# Python
mypy src/ --ignore-missing-imports 2>&1 | tail -1

# Go (built into compiler)
go vet ./...
```

**Check 3 — Cyclomatic Complexity:** Flag functions exceeding threshold (default 15):

```bash
# Python (radon)
radon cc src/ -s -n C  # Show functions with complexity >= C grade

# JavaScript (eslint rule)
npx eslint . --rule '{"complexity": ["error", 15]}'
```

**Check 4 — Dead Code Detection:**

```bash
# Python
vulture src/ --min-confidence 80

# JavaScript
npx ts-prune  # Detect unused exports

# Go
staticcheck ./...  # Includes unused code detection
```

**Check 5 — Dependency Vulnerability Scan:**

```bash
# JavaScript
npm audit --json | python -c "import json,sys; d=json.load(sys.stdin); print(f'{d.get(\"metadata\",{}).get(\"vulnerabilities\",{}).get(\"total\",0)} vulnerabilities')"

# Python
pip-audit --format=json

# Rust
cargo audit --json
```

**Check 6 — Code Duplication:** Detect copy-paste blocks (configurable token threshold):

```bash
# JavaScript/TypeScript
npx jscpd src/ --min-tokens 50 --reporters json

# Python
python -m pylint src/ --disable=all --enable=duplicate-code
```

**Gate Logic:** Score each check 0-100. Aggregate with equal weights. Block release if aggregate < 70 or any single check scores < 40.

---

### End-to-End Release Pipeline

Chain all 6 workflows into a single automated pipeline — this is how `/ship` works:

```bash
#!/bin/bash
set -e

REPO="."
BASE="main"
echo "=== RELEASE PIPELINE START ==="

# Phase 1: Pre-Flight
echo "--- Phase 1: Pre-Flight Validation ---"
python scripts/preflight_checker.py --repo "$REPO" --base "$BASE" --json > /tmp/preflight.json
PREFLIGHT_PASS=$(python -c "import json; print(json.load(open('/tmp/preflight.json'))['all_passed'])")
if [ "$PREFLIGHT_PASS" != "True" ]; then
  echo "BLOCKED: Pre-flight checks failed. Fix issues before release."
  exit 1
fi

# Phase 2: Test Orchestration (project-specific — example for Python)
echo "--- Phase 2: Test Orchestration ---"
python -m pytest --cov=src --cov-report=json:coverage.json -v
# Coverage gate: fail if below 70%
python -c "import json; c=json.load(open('coverage.json'))['totals']['percent_covered']; exit(0 if c>=70 else 1)"

# Phase 3: Code Quality (project-specific)
echo "--- Phase 3: Code Quality Gate ---"
ruff check . || echo "WARN: Lint issues found"

# Phase 4: Version Bump
echo "--- Phase 4: Version Management ---"
python scripts/version_bumper.py --repo "$REPO" --dry-run --json > /tmp/version.json
echo "Next version: $(python -c "import json; print(json.load(open('/tmp/version.json')).get('next_version','unknown'))")"

# Phase 5: Changelog
echo "--- Phase 5: Changelog Generation ---"
python scripts/changelog_generator.py --repo "$REPO" --from latest --to HEAD

# Phase 6: Readiness Assessment
echo "--- Phase 6: Deployment Readiness ---"
python scripts/release_readiness_scorer.py --input release_data.json --json > /tmp/readiness.json
DECISION=$(python -c "import json; print(json.load(open('/tmp/readiness.json'))['decision'])")
echo "Decision: $DECISION"

if [ "$DECISION" = "NO_GO" ]; then
  echo "BLOCKED: Readiness score too low. Address blockers."
  exit 1
fi

echo "=== RELEASE PIPELINE COMPLETE: $DECISION ==="
```

**Non-interactive by default.** The pipeline runs end-to-end without prompts unless: test failures occur, pre-flight checks fail, or readiness score is NO-GO.

---

### State Persistence

Save release data for trend tracking across versions:

```bash
# Save readiness score after each release
python scripts/release_readiness_scorer.py --input data.json --history .release-history/

# View trends: scores improve or degrade over releases
ls .release-history/  # v1.2.0.json, v1.3.0.json, v1.4.0.json
```

**Storage:** `.release-history/{version}.json` — readiness score, category breakdown, blockers, timestamp, commit range.

---

### Workflow 4: Semantic Version Management

Automatically determine the next version number from the commit history using the Conventional Commits specification.

**Rules:**

| Commit Type | Version Bump | Example |
|---|---|---|
| `fix:` | PATCH (0.0.x) | `fix(auth): handle expired tokens` |
| `feat:` | MINOR (0.x.0) | `feat(api): add pagination support` |
| `feat!:` or `BREAKING CHANGE` | MAJOR (x.0.0) | `feat!: redesign auth flow` |
| `docs:`, `chore:`, `test:`, `ci:` | No bump | `docs: update README` |

**Pre-release Support:**

```bash
# Alpha release
python scripts/version_bumper.py --repo . --pre alpha

# Beta release
python scripts/version_bumper.py --repo . --pre beta

# Release candidate
python scripts/version_bumper.py --repo . --pre rc
```

**Version Sources:** Reads and writes to `package.json`, `pyproject.toml`, `setup.py`, `setup.cfg`, `Cargo.toml`, and standalone `VERSION` files.

**Tool:** `version_bumper.py`

---

### Workflow 5: Changelog and Release Notes

Generate structured, human-readable changelogs from commit history using the Keep a Changelog format.

**Features:**

- Groups commits by type: Added, Changed, Deprecated, Removed, Fixed, Security
- Highlights breaking changes in a dedicated section
- Includes commit hashes and author attribution
- Supports tag-to-tag, date range, and HEAD-based ranges
- Outputs Markdown ready for GitHub Releases

**Tool:** `changelog_generator.py`

```bash
# Generate changelog between two tags
python scripts/changelog_generator.py --repo . --from v1.2.0 --to v1.3.0

# Generate changelog since last tag
python scripts/changelog_generator.py --repo . --from latest --to HEAD

# Generate with date range
python scripts/changelog_generator.py --repo . --since 2026-01-01 --until 2026-03-18
```

**Output Format:**

```markdown
## [1.3.0] - 2026-03-18

### Added
- feat(api): add rate limiting middleware (a1b2c3d) - @borghei

### Fixed
- fix(auth): handle token refresh race condition (d4e5f6a) - @borghei

### Breaking Changes
- feat!: require API key for all endpoints (b7c8d9e) - @borghei
```

---

### Workflow 6: Deployment Readiness Assessment

The final gate before shipping. Aggregates signals from all previous workflows into a single readiness score with a clear GO / CONDITIONAL / NO-GO decision.

**Tool:** `release_readiness_scorer.py`

```bash
python scripts/release_readiness_scorer.py --input release_data.json
```

**Decision Thresholds:**

| Score | Decision | Action |
|---|---|---|
| 80-100 | GO | Proceed with deployment |
| 60-79 | CONDITIONAL | Proceed with mitigations documented |
| 0-59 | NO-GO | Address blockers before release |

---

## Python Tools

### preflight_checker.py

Pre-flight validation for release readiness. Checks branch sync, merge conflicts, secrets, gitignore, uncommitted changes, conventional commits, and dependency lock files.

```bash
python scripts/preflight_checker.py --repo /path/to/repo --base main [--verbose]
```

### changelog_generator.py

Generates Keep a Changelog formatted release notes from conventional commits. Supports tag ranges, date ranges, and contributor attribution.

```bash
python scripts/changelog_generator.py --repo /path/to/repo --from v1.0.0 --to HEAD [--output CHANGELOG.md]
```

### version_bumper.py

Semantic version management with auto-detection from conventional commits. Reads and updates version across multiple file formats.

```bash
python scripts/version_bumper.py --repo /path/to/repo [--bump major|minor|patch] [--pre alpha|beta|rc] [--dry-run]
```

### release_readiness_scorer.py

Computes a weighted readiness score (0-100) from release checklist data. Provides category breakdowns, recommendations, and trend tracking.

```bash
python scripts/release_readiness_scorer.py --input release_data.json [--history releases_history.json]
```

---

## Release Readiness Score

The readiness score is a weighted composite of seven categories:

| Category | Weight | What It Measures |
|---|---|---|
| **Tests** | 25% | Test pass rate, coverage percentage, flaky test count |
| **Code Quality** | 20% | Lint errors, type errors, complexity violations, duplication |
| **Documentation** | 15% | README updated, API docs current, changelog generated, migration guide present |
| **Security** | 15% | No secrets in code, dependencies free of critical CVEs, SAST clean |
| **Breaking Changes** | 10% | Breaking changes documented, migration path provided, deprecation notices |
| **Dependencies** | 10% | Lock files consistent, no yanked packages, major upgrades reviewed |
| **Rollback Plan** | 5% | Rollback procedure documented, database migration reversible, feature flags in place |

**Scoring per Category:**

Each category scores 0-100 based on its sub-checks. The overall score is the weighted average. Individual category scores below 40 trigger a mandatory blocker regardless of the overall score.

**Example Output:**

```
Release Readiness Report
========================
Overall Score: 82/100 - GO

Category Breakdown:
  Tests:             88/100 (25%) -> 22.0
  Code Quality:      85/100 (20%) -> 17.0
  Documentation:     73/100 (15%) -> 11.0
  Security:          90/100 (15%) -> 13.5
  Breaking Changes:  70/100 (10%) ->  7.0
  Dependencies:      80/100 (10%) ->  8.0
  Rollback Plan:     75/100  (5%) ->  3.8

Recommendations:
  - Documentation: Update API changelog for new endpoints
  - Breaking Changes: Add migration guide for auth flow change
```

---

## Release Types

### Hotfix Release

For critical production issues. Branches from the latest release tag, applies minimal fix, bumps PATCH.

```bash
git checkout -b hotfix/v1.2.1 v1.2.0
# Apply fix
python scripts/version_bumper.py --repo . --bump patch
python scripts/changelog_generator.py --repo . --from v1.2.0 --to HEAD
```

### Patch Release

Accumulated bug fixes. No new features, no breaking changes. Bumps PATCH.

```bash
python scripts/version_bumper.py --repo . --bump patch
```

### Minor Release

New features with backward compatibility. May include bug fixes. Bumps MINOR.

```bash
python scripts/version_bumper.py --repo . --bump minor
```

### Major Release

Breaking changes present. Requires migration documentation. Bumps MAJOR.

```bash
python scripts/version_bumper.py --repo . --bump major
```

### Pre-release

Alpha, beta, or release candidate builds for testing before stable release.

```bash
python scripts/version_bumper.py --repo . --bump minor --pre alpha
# Produces: 1.3.0-alpha.1

python scripts/version_bumper.py --repo . --bump minor --pre rc
# Produces: 1.3.0-rc.1
```

---

## Integration Points

### CI/CD Pipeline Integration

Each tool outputs structured data suitable for pipeline consumption:

- **Exit codes:** 0 = success, 1 = failure (for gate logic)
- **JSON output:** All tools support `--json` flag for machine-readable output
- **Environment variables:** Tools read `CI`, `GITHUB_ACTIONS`, `GITLAB_CI` for environment-aware behavior

### GitHub Actions Example

```yaml
- name: Pre-flight Check
  run: python scripts/preflight_checker.py --repo . --base main --json > preflight.json

- name: Version Bump
  run: python scripts/version_bumper.py --repo . --dry-run --json > version.json

- name: Generate Changelog
  run: python scripts/changelog_generator.py --repo . --from latest --to HEAD --output CHANGELOG.md

- name: Readiness Score
  run: |
    python scripts/release_readiness_scorer.py --input release_data.json
    if [ $? -ne 0 ]; then echo "Release blocked"; exit 1; fi
```

### Git Hook Integration

Add pre-push validation:

```bash
# .git/hooks/pre-push
python scripts/preflight_checker.py --repo . --base main
```

### Slack / Teams Notifications

Readiness scorer outputs a summary suitable for messaging:

```bash
python scripts/release_readiness_scorer.py --input data.json --format summary
# Output: "Release v1.3.0 scored 82/100 (GO) - 1 recommendation"
```

---

## Rollback Strategies

Every release must have a documented rollback plan. The skill supports four rollback patterns:

### 1. Git Revert Rollback

Safest for code-only changes. Creates a new commit that undoes the release.

```bash
git revert --no-edit HEAD~3..HEAD
git push origin main
```

### 2. Feature Flag Rollback

Instant rollback by disabling the flag. No deployment required.

```bash
# Toggle flag in configuration
feature_flags:
  new_auth_flow: false
```

### 3. Blue-Green Rollback

Switch traffic back to the previous environment. Requires infrastructure support.

### 4. Database Migration Rollback

Reverse migrations must be tested before release. Include `down()` migrations for every `up()`.

See `references/rollback_strategies.md` for comprehensive rollback guidance.

---

## Feature Flag Management

Feature flags enable progressive rollouts and instant rollbacks. The release orchestrator integrates with feature flag workflows:

**Flag Lifecycle:**
1. **Development** - Flag created, default OFF
2. **Testing** - Flag ON in staging environments
3. **Canary** - Flag ON for 1-5% of production traffic
4. **Rollout** - Gradual increase to 100%
5. **Cleanup** - Flag removed, code paths consolidated

**Release Integration:**
- Pre-flight checks verify all new features have corresponding flags
- Readiness scorer includes flag coverage in the Rollback Plan category
- Changelog generator annotates features with their flag status

**Best Practices:**
- Never release a major feature without a flag
- Set flag expiration dates to prevent permanent flags
- Log flag evaluations for debugging
- Test both flag states in CI

---

## References

- `references/release_engineering_guide.md` - Release strategies, semver deep dive, conventional commits
- `references/rollback_strategies.md` - Database, feature flag, git, and infrastructure rollbacks
- `references/ci_cd_best_practices.md` - Pipeline design, caching, artifact management

## Assets

- `assets/release_checklist_template.md` - Copy-paste release checklist for your team
- `assets/sample_release_data.json` - Sample input for `release_readiness_scorer.py`
