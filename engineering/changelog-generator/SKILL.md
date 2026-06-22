---
name: changelog-generator
description: >
  Generate changelogs and release notes from Conventional Commits with semver bump detection,
  Keep a Changelog formatting, and monorepo scopes. Use when preparing releases, enforcing
  commit standards, or automating release notes.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: release-management
  tier: POWERFUL
  updated: 2026-06-17
  frameworks: conventional-commits, keep-a-changelog, semantic-versioning
---
# Changelog Generator

Generate consistent, auditable changelogs and release notes from Conventional Commits. Parses commit messages, detects semantic version bumps (major/minor/patch), renders Keep a Changelog sections, supports monorepo scoped changelogs, integrates with CI for automated release notes, and enforces commit format with linting. Separates commit parsing, bump logic, and rendering so teams can automate releases without losing editorial control.

## Keywords

changelog, release notes, conventional commits, semantic versioning, semver, Keep a Changelog, commit linting, release automation, monorepo changelog

## Core Capabilities

- **Commit parsing** — parse Conventional Commit messages into structured data (type, scope, description, body, footer); detect breaking changes from `!` and `BREAKING CHANGE:`.
- **Semantic version detection** — map commit types to bump levels (breaking→major, feat→minor, others→patch); support pre-release versions.
- **Changelog rendering** — Keep a Changelog, GitHub release notes, plain markdown, and JSON output grouped by type.
- **Quality enforcement** — commit message linter for CI and pre-commit hooks, strict mode, scope validation, breaking-change documentation requirements.

## When to Use

- Before publishing a release tag
- During CI to generate release notes automatically
- In PR checks to enforce commit message standards
- In monorepos where package changelogs need scoped filtering
- When converting raw git history into user-facing notes
- As a pre-release checklist step

## Clarify First

Before generating the changelog, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Commit range** — since which tag or commit (defines what history is included)
- [ ] **Output format** — Keep a Changelog, GitHub release notes, plain markdown, or JSON (sets `changelog_formatter.py --format`)
- [ ] **Version & scope** — the release version, and in a monorepo which package scope to filter (sets `--version` and scoped filtering)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `commit_parser.py` | Parse `git log` (with `---COMMIT_END---` delimiters) into structured changelog entries | `git log --pretty=format:'%H%n%s%n%b%n---COMMIT_END---' --no-merges \| python scripts/commit_parser.py --json` |
| `breaking_change_detector.py` | Scan commit messages/diffs for breaking-change indicators | `python scripts/breaking_change_detector.py -f gitlog.txt --severity high` |
| `changelog_formatter.py` | Format parsed commits into Keep a Changelog or GitHub markdown | `python scripts/changelog_formatter.py -f parsed.json --version 1.4.0 --format keepachangelog` |

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/commit-format-and-rendering.md](references/commit-format-and-rendering.md)** — the Conventional Commit grammar, type→section/semver mapping table, breaking-change rules, and the Keep a Changelog and GitHub Release Notes output formats. Read when defining commit standards or output style.
- **[references/generation-and-linting.md](references/generation-and-linting.md)** — the 4-step parse→bump→render workflow with Python code, the pre-commit hook and CI commitlint config, monorepo scoped-changelog strategy, and the release-workflow integration diagram. Read when building the pipeline or enforcing format.
- **[references/quality-and-troubleshooting.md](references/quality-and-troubleshooting.md)** — the pre-publish quality checklist, common pitfalls, best practices, troubleshooting table, and success criteria. Read before publishing a changelog or when diagnosing an issue.

## Scope & Limitations

**This skill covers:**
- Parsing Conventional Commit messages into structured data for changelog generation
- Determining semantic version bumps (major/minor/patch) from commit history
- Rendering changelogs in Keep a Changelog, GitHub Release Notes, plain markdown, and JSON formats
- Enforcing commit message standards via pre-commit hooks and CI linting

**This skill does NOT cover:**
- Actual release publishing or deployment pipeline execution — see `engineering/ci-cd-pipeline-design`
- Git tag management, branch strategies, or merge workflows — see `engineering/git-workflow-automation`
- Writing or improving commit messages themselves — see `standards/git/git-workflow-standards.md`
- Coordinated multi-package versioning with tools like Changesets or Lerna — referenced in monorepo strategy but not implemented here

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `engineering/ci-cd-pipeline-design` | Changelog generation runs as a CI stage before release publishing | Parsed commits and rendered changelog feed into the release pipeline as artifacts |
| `engineering/git-workflow-automation` | Commit linting hooks enforce format before commits reach the changelog generator | Pre-commit validation ensures only parseable commits enter the git history |
| `engineering/code-review-automation` | PR checks verify commit messages conform to Conventional Commits before merge | Linting results gate PR approval, preventing unparseable commits from reaching main |
| `engineering/api-versioning-strategy` | Breaking change detection aligns API version bumps with changelog major releases | `BREAKING CHANGE` commits trigger both changelog entries and API version increments |
| `project-management/release-management` | Release planning uses generated changelogs for stakeholder communication | Rendered release notes flow into release checklists and stakeholder announcements |
| `standards/git/git-workflow-standards.md` | Commit format standards define the grammar this skill parses | Standard definitions are the source of truth for the commit regex pattern |
