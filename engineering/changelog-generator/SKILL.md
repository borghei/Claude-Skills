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
  updated: 2026-11-08
  frameworks: conventional-commits, keep-a-changelog, semantic-versioning
  tags:
    - changelog
    - release-notes
    - conventional-commits
    - semver
    - monorepo
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

Before generating the changelog, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Commit range:** since which tag or commit (defines what history is included).
- **Output format:** Keep a Changelog, GitHub release notes, plain markdown, or JSON (sets `changelog_formatter.py --format`).
- **Version & scope:** the release version, and in a monorepo which package scope to filter (sets `--version` and scoped filtering).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start Workflow

The parser reads `git log` text with `---COMMIT_END---` after each commit and writes JSON; the
formatter reads that JSON (never raw `git log`). Pipe one into the other:

```bash
# Real history: everything since the last tag
git log v1.3.2..HEAD --pretty=format:'%H%n%s%n%b%n---COMMIT_END---' --no-merges \
  | python scripts/commit_parser.py --json \
  | python scripts/changelog_formatter.py --auto-version 1.3.2 --repo-url https://github.com/org/repo

# Bundled sample (7 commits: one breaking feat, feat, fix, perf, docs, chore, one non-conventional)
python scripts/commit_parser.py -f assets/sample_commit_log.txt --json \
  | python scripts/changelog_formatter.py --version 2.0.0 --date 2026-11-01
python scripts/breaking_change_detector.py -f assets/sample_commit_log.txt --severity high
```

## Tools Overview

| Tool | Purpose | Key flags |
|------|---------|-----------|
| `commit_parser.py` | Conventional Commit parser: type, scope, breaking marker, footers; skips non-conventional subjects and counts them | `-f FILE` or stdin, `--json`, `--scope api,ui`, `--types feat,fix`, `--user-facing` |
| `changelog_formatter.py` | Keep a Changelog or GitHub release notes, BREAKING first; computes the next version from commit types | `--version` or `--auto-version BASE`, `--date` (default today), `--format keepachangelog\|github`, `--repo-url`, `--unreleased` |
| `breaking_change_detector.py` | Confirmed (`!`, `BREAKING CHANGE:`) and suspected (keyword, optional diff) breaking changes | `-f FILE`, `--diff-file`, `--severity`, `--confirmed-only`, `--json` |

**Exit codes (all three):** `0` output written; `2` missing or unreadable file, no input on stdin,
or (formatter) input that is not `commit_parser.py --json` output. None of them gate on content:
read the "Skipped (invalid)" count and the breaking-change report.

**Done when:**
1. Every commit in the range is either in the changelog or deliberately skipped (docs, chore, non-conventional).
2. Each breaking change has a migration note a user can follow, not just the commit subject.
3. The version bump matches the highest-impact change (breaking means major).
4. Someone who did not write the code can read the entries and understand the user impact.

## Anti-Patterns

### Commit log as changelog
**Mistake:** Publishing every commit subject, including chores, merges and "fix typo".
**Why it happens:** It is the zero-effort output.
**Instead:** Use `--user-facing` or the formatter's sections, and rewrite entries in terms of what users notice.

### Silent breaking changes
**Mistake:** A breaking API change ships as a minor release because the commit lacked `!` or a `BREAKING CHANGE:` footer.
**Why it happens:** The author did not think of it as breaking.
**Instead:** Run `breaking_change_detector.py` and review its suspected list before choosing the version.

### Ignoring skipped commits
**Mistake:** Not looking at the parser's "Skipped (invalid)" count, so non-conventional commits vanish from the notes.
**Why it happens:** The output looks complete.
**Instead:** Review skipped commits each release and add a commit-lint hook so the count trends to zero.

## Files

- `scripts/commit_parser.py`, `scripts/changelog_formatter.py`, `scripts/breaking_change_detector.py` — the three CLIs above.
- `assets/sample_commit_log.txt` — seven-commit sample in the delimiter format.
- `references/` — commit grammar and rendering, generation and linting, quality checklist.

## Reference Documentation

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
- Actual release publishing or deployment pipeline execution — see `engineering/ci-cd-pipeline-builder`
- Git tag management, branch strategies, or merge workflows — see `standards/git/git-workflow-standards.md`
- Writing or improving commit messages themselves — see `standards/git/git-workflow-standards.md`
- Coordinated multi-package versioning with tools like Changesets or Lerna — referenced in monorepo strategy but not implemented here

## See Also

- `engineering/ci-cd-pipeline-builder` — run the parse and format steps in the release pipeline.
- `engineering/pr-description-writer` — user-facing summaries at PR time that feed good changelog entries.
- `standards/git/git-workflow-standards.md` — the commit format this skill parses.
