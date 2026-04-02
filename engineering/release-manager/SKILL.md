---
name: release-manager
description: >
  Automates release management with changelog generation, semantic versioning,
  and release readiness checks. Use when preparing releases, generating
  changelogs, bumping versions, or validating release candidates.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: devops
  tier: POWERFUL
  updated: 2026-03-31
---
# Release Manager

The agent automates release management by parsing conventional commits into structured changelogs, determining semantic version bumps, and assessing release readiness with checklists, rollback runbooks, and stakeholder communication plans.

## Quick Start

```bash
# Generate changelog from conventional commits
git log --oneline v1.0.0..HEAD | python changelog_generator.py --version 1.1.0 --format both

# Determine version bump from commit history
git log --oneline v1.0.0..HEAD | python version_bumper.py --current-version 1.0.0 --analysis

# Assess release readiness
python release_planner.py --input release-plan.json --include-checklist --include-rollback
```

---

## Core Workflows

### Workflow 1: Generate Changelog and Version Bump

1. Collect commits since last tag: `git log --oneline v1.0.0..HEAD`
2. Pipe to `changelog_generator.py` to produce a Keep-a-Changelog-format CHANGELOG
3. Pipe to `version_bumper.py` to determine MAJOR/MINOR/PATCH bump from commit types
4. Review changelog grouping (Added, Fixed, Changed, Breaking Changes)
5. **Validation checkpoint:** All `feat` commits appear under Added; all `fix` under Fixed; breaking changes highlighted

```bash
git log --oneline v1.2.0..HEAD | python changelog_generator.py \
  --version 1.3.0 --date 2026-03-21 --base-url https://github.com/org/repo --summary
```

### Workflow 2: Assess Release Readiness

1. Prepare release plan JSON with features, quality gates, stakeholders, and target date
2. Run `release_planner.py` with checklist, communication, and rollback flags
3. Review blocking issues and readiness score
4. Address blockers (missing approvals, failed gates, overdue items)
5. **Validation checkpoint:** Readiness score >80%; zero blocking issues; rollback runbook generated with time estimates

```bash
python release_planner.py --input release-plan.json \
  --output-format json --include-checklist --include-communication --include-rollback
```

### Workflow 3: Hotfix Release

1. Create hotfix branch from last stable tag
2. Apply minimal fix and run `version_bumper.py` with `--prerelease rc`
3. Generate changelog entry for the fix
4. Assess readiness with expedited checklist
5. **Validation checkpoint:** Fix addresses root cause only; rollback procedure tested; stakeholders notified

---

## Version Bump Rules

| Commit Type | Bump | Example |
|-------------|------|---------|
| `BREAKING CHANGE` or `!` suffix | MAJOR | `feat!: remove deprecated API` |
| `feat` | MINOR | `feat(auth): add OAuth2` |
| `fix`, `perf`, `security` | PATCH | `fix(api): resolve race condition` |
| `docs`, `test`, `chore`, `ci` | None | `docs: update README` |

Pre-release progression: `alpha.N` -> `beta.1` -> `rc.1` -> stable release.

---

## Rollback Triggers

- **Error rate:** >2x baseline within 30 minutes
- **Latency:** >50% P95 increase
- **Feature failures:** Core functionality broken
- **Security incident:** Vulnerability exploited
- **Data corruption:** Database integrity compromised

---

## Anti-Patterns

- **Monolithic releases** -- large, infrequent releases with high blast radius; prefer small, frequent releases
- **Manual deployments** -- error-prone and inconsistent; automate every step that can be automated
- **No rollback plan** -- every release must have a tested rollback procedure before going live
- **Skipping quality gates** -- deploying without test coverage, security scan, or dependency audit
- **Last-minute changes** -- code freeze exists for a reason; changes after freeze need explicit approval
- **Non-conventional commits** -- free-form commit messages break changelog generation and version bumping
- **Environment drift** -- staging must mirror production; drift causes false confidence in testing

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Changelog generator produces empty output | Non-conventional commit messages that don't match the `type(scope): description` pattern | Ensure all commits follow conventional commit format; non-matching messages default to `chore` type which is excluded from user-facing changelogs |
| Version bumper recommends `none` despite meaningful commits | Commits use types in the ignore list (`test`, `ci`, `build`, `chore`, `docs`, `style`) | Use `feat` for new features and `fix` for bug fixes; override with `--custom-rules` to map additional types to bump levels |
| Release planner reports `blocked` status unexpectedly | Missing required approvals (`pm_approved`, `qa_approved`) on features or failed required quality gates | Review the `blocking_issues` array in the assessment output; ensure all features have the necessary approval flags set to `true` in the input JSON |
| Pre-release version not incrementing correctly | Existing pre-release type does not match the requested `--prerelease` type, causing a reset to `.1` | When promoting from alpha to beta or beta to rc, the counter resets to 1 by design; to stay on the same track, pass the same pre-release type |
| Git log parsing misses commits | Input uses full `git log` format but lines are not properly indented with 4 spaces | Use `git log --oneline` for the simplest input format, or ensure the full format output preserves the standard 4-space commit message indent |
| Readiness score seems too low | Quality gates default to `pending` status when not explicitly set, and pending gates score zero points | Provide explicit `quality_gates` with accurate `status` values in the release plan JSON, or complete the gates before running assessment |
| Rollback time estimate is inaccurate | Default rollback steps use generic time estimates that don't reflect your infrastructure | Supply custom `rollback_steps` in the release plan JSON with `estimated_time` values that match your actual deployment environment |

## Success Criteria

- **Changelog accuracy**: 100% of conventional commits are correctly categorized (feat to Added, fix to Fixed, etc.) with zero miscategorized entries
- **Version bump correctness**: Recommended version matches SemVer rules in all cases -- breaking changes produce MAJOR, features produce MINOR, fixes produce PATCH
- **Readiness assessment coverage**: All blocking issues (missing approvals, failed quality gates, overdue timelines) are surfaced with zero false negatives
- **Release cycle time reduction**: Teams using the planner reduce release preparation time by 40% or more compared to manual checklist tracking
- **Rollback preparedness**: Every release assessed by the planner has a complete, actionable rollback runbook with time estimates and verification steps
- **Stakeholder communication**: Communication plans cover all identified stakeholders with appropriate timing (T-48h external, T-24h internal, T+1h post-deploy)
- **Tool integration time**: New teams can configure and run all three scripts against their repository within 30 minutes of initial setup

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

## Tool Reference

### changelog_generator.py

**Purpose:** Parses git log output in conventional commit format and generates structured changelogs. Groups commits by type (Added, Fixed, Changed, etc.), extracts scope and issue references, and highlights breaking changes.

**Usage:**
```bash
git log --oneline v1.0.0..HEAD | python changelog_generator.py
python changelog_generator.py --input commits.txt --version 2.0.0 --format json
cat commits.json | python changelog_generator.py --input-format json --summary
```

**Flags/Parameters:**

| Flag | Short | Type | Default | Description |
|------|-------|------|---------|-------------|
| `--input` | `-i` | string | stdin | Input file path; reads from stdin if omitted |
| `--format` | `-f` | choice | `markdown` | Output format: `markdown`, `json`, or `both` |
| `--version` | `-v` | string | `Unreleased` | Version label for the changelog section header |
| `--date` | `-d` | string | today | Release date in YYYY-MM-DD format |
| `--base-url` | `-u` | string | empty | Base repository URL for commit links (e.g., `https://github.com/org/repo`) |
| `--input-format` | | choice | `git-log` | Input format: `git-log` (oneline or full) or `json` (array of commit objects) |
| `--output` | `-o` | string | stdout | Output file path; prints to stdout if omitted |
| `--summary` | `-s` | flag | false | Append release summary statistics (total commits, by type, breaking changes, issue references) |

**Example:**
```bash
git log --oneline v1.2.0..HEAD | python changelog_generator.py \
  --version 1.3.0 \
  --date 2026-03-21 \
  --base-url https://github.com/myorg/myapp \
  --format both \
  --summary
```

**Output Formats:**
- **markdown**: Keep a Changelog format with sections for Breaking Changes, Added, Changed, Deprecated, Removed, Fixed, Security. Commits grouped by scope within each section.
- **json**: Structured object with `version`, `date`, `summary` (counts by type, by author, scopes, issue references), and `categories` (arrays of commit objects per category).
- **both**: Markdown changelog followed by JSON output, each with a heading separator.

---

### version_bumper.py

**Purpose:** Analyzes conventional commits since the last tag to determine the correct semantic version bump (major/minor/patch). Supports pre-release versions (alpha, beta, rc) and generates version bump commands for npm, Python, Rust, Git, and Docker.

**Usage:**
```bash
git log --oneline v1.2.0..HEAD | python version_bumper.py --current-version 1.2.0
python version_bumper.py -c 2.0.0-beta.3 -i commits.json --input-format json --prerelease rc
git log --oneline v1.0.0..HEAD | python version_bumper.py -c 1.0.0 -f json --analysis --include-commands
```

**Flags/Parameters:**

| Flag | Short | Type | Default | Description |
|------|-------|------|---------|-------------|
| `--current-version` | `-c` | string | **required** | Current version (e.g., `1.2.3`, `v1.2.3`, `1.0.0-beta.2`) |
| `--input` | `-i` | string | stdin | Input file with commits; reads from stdin if omitted |
| `--input-format` | | choice | `git-log` | Input format: `git-log` (oneline) or `json` (array of commit objects) |
| `--prerelease` | `-p` | choice | none | Generate pre-release version: `alpha`, `beta`, or `rc` |
| `--output-format` | `-f` | choice | `text` | Output format: `text`, `json`, or `commands` |
| `--output` | `-o` | string | stdout | Output file path; prints to stdout if omitted |
| `--include-commands` | | flag | false | Include version bump commands for npm, Python, Rust, Git, and Docker |
| `--include-files` | | flag | false | Include file update snippets for package.json, pyproject.toml, setup.py, Cargo.toml, __init__.py |
| `--custom-rules` | | string | none | JSON string mapping commit types to bump levels (e.g., `'{"perf": "minor"}'`) |
| `--ignore-types` | | string | `test,ci,build,chore,docs,style` | Comma-separated list of commit types to ignore for bump determination |
| `--analysis` | `-a` | flag | false | Include detailed commit analysis (breaking changes list, features list, fixes list, ignored list) |

**Example:**
```bash
git log --oneline v2.1.0..HEAD | python version_bumper.py \
  --current-version 2.1.0 \
  --output-format json \
  --analysis \
  --include-commands \
  --include-files
```

**Output Formats:**
- **text**: Human-readable summary with current version, recommended version, bump type, and optional analysis/commands.
- **json**: Structured object with `current_version`, `recommended_version`, `bump_type`, and optional `analysis`, `commands`, and `file_updates` fields.
- **commands**: Shell-ready version bump commands organized by platform (npm, Python, Rust, Git, Docker).

---

### release_planner.py

**Purpose:** Takes a release plan JSON (features, quality gates, stakeholders, target date) and assesses release readiness. Generates a readiness report with scoring, a release checklist, a stakeholder communication plan with message templates, and a rollback runbook.

**Usage:**
```bash
python release_planner.py --input release-plan.json
python release_planner.py -i plan.json -f json --include-checklist --include-rollback
python release_planner.py -i plan.json -f markdown --include-checklist --include-communication --include-rollback
```

**Flags/Parameters:**

| Flag | Short | Type | Default | Description |
|------|-------|------|---------|-------------|
| `--input` | `-i` | string | **required** | Path to release plan JSON file |
| `--output-format` | `-f` | choice | `text` | Output format: `json`, `markdown`, or `text` |
| `--output` | `-o` | string | stdout | Output file path; prints to stdout if omitted |
| `--include-checklist` | | flag | false | Include the full release checklist (pre-release validation, quality gates, approvals, documentation, deployment) |
| `--include-communication` | | flag | false | Include stakeholder communication plan with timeline and message templates |
| `--include-rollback` | | flag | false | Include rollback runbook with step-by-step procedures, triggers, and verification checks |
| `--min-coverage` | | float | `80.0` | Minimum test coverage threshold percentage for quality gate validation |

**Example:**
```bash
python release_planner.py \
  --input release-plan.json \
  --output-format json \
  --output readiness-report.json \
  --include-checklist \
  --include-communication \
  --include-rollback \
  --min-coverage 85.0
```

**Input JSON Structure:**
The input file expects a JSON object with keys: `release_name`, `version`, `target_date` (ISO format), `features` (array of feature objects with `id`, `title`, `type`, `status`, `risk_level`, approvals, etc.), `quality_gates` (optional array), `stakeholders` (optional array), and `rollback_steps` (optional array). When `quality_gates` or `rollback_steps` are omitted, sensible defaults are generated automatically.

**Output Formats:**
- **text**: Plain text report with status, readiness score, blocking issues, warnings, recommendations, feature summary, and quality gate summary.
- **markdown**: Formatted Markdown report with headings, status icons, and structured feature/checklist sections.
- **json**: Complete structured object with `assessment`, `checklist`, `communication_plan`, and `rollback_runbook` fields (null when not requested).