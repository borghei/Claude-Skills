---
name: changelog-generator
description: Generate changelogs and release notes from Conventional Commits. Covers commit parsing, semantic version bump detection, Keep a Changelog formatting, monorepo scoped changelogs, CI integration, and commit message linting. Use when preparing releases, enforcing commit standards, or automating release notes.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  category: engineering
  domain: release-management
  tier: POWERFUL
  updated: 2026-03-09
  frameworks: conventional-commits, keep-a-changelog, semantic-versioning
---

# Changelog Generator

**Tier:** POWERFUL
**Category:** Engineering / Release Management
**Maintainer:** Claude Skills Team

## Overview

Generate consistent, auditable changelogs and release notes from Conventional Commits. Parses commit messages, detects semantic version bumps (major/minor/patch), renders Keep a Changelog sections, supports monorepo scoped changelogs, integrates with CI for automated release notes, and enforces commit format with linting. Separates commit parsing, bump logic, and rendering so teams can automate releases without losing editorial control.

## Keywords

changelog, release notes, conventional commits, semantic versioning, semver, Keep a Changelog, commit linting, release automation, monorepo changelog

## Core Capabilities

### 1. Commit Parsing
- Parse Conventional Commit messages into structured data
- Extract type, scope, description, body, and footer
- Detect breaking changes from `!` suffix and `BREAKING CHANGE:` footer
- Handle multi-line commit bodies and co-author trailers

### 2. Semantic Version Detection
- Map commit types to version bump levels
- Breaking changes trigger major bumps
- `feat` triggers minor bumps
- All other types trigger patch bumps
- Support for pre-release versions (alpha, beta, rc)

### 3. Changelog Rendering
- Keep a Changelog format with semantic sections
- GitHub release notes format
- Plain markdown for documentation
- JSON output for automation pipelines
- Grouped by type with user-readable descriptions

### 4. Quality Enforcement
- Commit message linter for CI and pre-commit hooks
- Strict mode that blocks non-conforming commits
- Scope validation against allowed values
- Breaking change documentation requirements

## When to Use

- Before publishing a release tag
- During CI to generate release notes automatically
- In PR checks to enforce commit message standards
- In monorepos where package changelogs need scoped filtering
- When converting raw git history into user-facing notes
- As a pre-release checklist step

## Conventional Commit Format

```
<type>(<scope>)<!>: <description>

[optional body]

[optional footer(s)]
```

### Type to Section Mapping

| Commit Type | Changelog Section | SemVer Bump | User-Facing? |
|-------------|------------------|-------------|-------------|
| `feat` | Added | minor | Yes |
| `fix` | Fixed | patch | Yes |
| `perf` | Performance | patch | Yes |
| `security` | Security | patch | Yes |
| `deprecated` | Deprecated | minor | Yes |
| `remove` | Removed | major | Yes |
| `refactor` | Changed | patch | Sometimes |
| `docs` | — | patch | No |
| `test` | — | — | No |
| `build` | — | — | No |
| `ci` | — | — | No |
| `chore` | — | — | No |

### Breaking Change Rules

Breaking changes always trigger a **major** version bump regardless of type:

```
feat(api)!: remove deprecated v1 endpoints

BREAKING CHANGE: The /api/v1/* endpoints have been removed.
Migrate to /api/v2/* before upgrading. See migration guide at docs/v2-migration.md.
```

## Changelog Rendering

### Keep a Changelog Format

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] - 2026-03-09

### Added
- User can now export projects as CSV ([#234](https://github.com/org/repo/pull/234))
- Dark mode support for dashboard ([#228](https://github.com/org/repo/pull/228))

### Fixed
- Pagination returning duplicate items on page boundaries ([#231](https://github.com/org/repo/pull/231))
- Login form not showing validation errors on mobile ([#229](https://github.com/org/repo/pull/229))

### Performance
- Reduced dashboard load time by 40% with query optimization ([#232](https://github.com/org/repo/pull/232))

### Security
- Updated jsonwebtoken to 9.0.2 to fix CVE-2024-XXXX ([#233](https://github.com/org/repo/pull/233))

## [1.3.2] - 2026-02-28

### Fixed
- API rate limiter not resetting after window expiry ([#227](https://github.com/org/repo/pull/227))

[1.4.0]: https://github.com/org/repo/compare/v1.3.2...v1.4.0
[1.3.2]: https://github.com/org/repo/compare/v1.3.1...v1.3.2
```

### GitHub Release Notes Format

```markdown
## What's New

- **CSV Export**: Users can now export project data as CSV files (#234)
- **Dark Mode**: Dashboard fully supports dark mode (#228)

## Bug Fixes

- Fixed pagination returning duplicate items on page boundaries (#231)
- Fixed login form validation on mobile devices (#229)

## Performance

- Dashboard load time reduced by 40% through query optimization (#232)

## Security

- Updated jsonwebtoken to patch CVE-2024-XXXX (#233)

**Full Changelog**: https://github.com/org/repo/compare/v1.3.2...v1.4.0
```

## Generation Workflow

### Step 1: Collect Commits

```bash
# Get commits between two tags
git log v1.3.2..HEAD --pretty=format:'%H %s' --no-merges

# Get commits with full body (for breaking change detection)
git log v1.3.2..HEAD --pretty=format:'%H%n%s%n%b%n---COMMIT_END---' --no-merges
```

### Step 2: Parse and Classify

```python
import re
from dataclasses import dataclass
from typing import Optional

@dataclass
class ParsedCommit:
    hash: str
    type: str
    scope: Optional[str]
    description: str
    body: Optional[str]
    breaking: bool
    breaking_description: Optional[str]

COMMIT_PATTERN = re.compile(
    r'^(?P<type>feat|fix|perf|refactor|docs|test|build|ci|chore|security|deprecated|remove)'
    r'(?:\((?P<scope>[^)]+)\))?'
    r'(?P<breaking>!)?'
    r':\s*(?P<description>.+)$'
)

def parse_commit(hash: str, message: str) -> Optional[ParsedCommit]:
    lines = message.strip().split('\n')
    subject = lines[0]
    body = '\n'.join(lines[1:]).strip() if len(lines) > 1 else None

    match = COMMIT_PATTERN.match(subject)
    if not match:
        return None  # Non-conventional commit

    breaking = bool(match.group('breaking'))
    breaking_desc = None

    if body and 'BREAKING CHANGE:' in body:
        breaking = True
        bc_match = re.search(r'BREAKING CHANGE:\s*(.+)', body, re.DOTALL)
        if bc_match:
            breaking_desc = bc_match.group(1).strip()

    return ParsedCommit(
        hash=hash,
        type=match.group('type'),
        scope=match.group('scope'),
        description=match.group('description'),
        body=body,
        breaking=breaking,
        breaking_description=breaking_desc,
    )
```

### Step 3: Determine Version Bump

```python
def determine_bump(commits: list[ParsedCommit]) -> str:
    """Determine semver bump from parsed commits."""
    if any(c.breaking for c in commits):
        return 'major'
    if any(c.type == 'feat' for c in commits):
        return 'minor'
    if any(c.type in ('fix', 'perf', 'security', 'refactor') for c in commits):
        return 'patch'
    return 'none'

def bump_version(current: str, bump: str) -> str:
    """Apply bump to a semver string."""
    major, minor, patch = map(int, current.lstrip('v').split('.'))
    if bump == 'major':
        return f"{major + 1}.0.0"
    elif bump == 'minor':
        return f"{major}.{minor + 1}.0"
    elif bump == 'patch':
        return f"{major}.{minor}.{patch + 1}"
    return current
```

### Step 4: Render Changelog

```python
SECTION_MAP = {
    'feat': 'Added',
    'fix': 'Fixed',
    'perf': 'Performance',
    'security': 'Security',
    'deprecated': 'Deprecated',
    'remove': 'Removed',
    'refactor': 'Changed',
}

def render_changelog(version: str, date: str, commits: list[ParsedCommit], repo_url: str) -> str:
    sections: dict[str, list[str]] = {}

    # Breaking changes get their own section
    breaking = [c for c in commits if c.breaking]
    if breaking:
        sections['BREAKING CHANGES'] = []
        for c in breaking:
            desc = c.breaking_description or c.description
            scope = f"**{c.scope}**: " if c.scope else ""
            sections['BREAKING CHANGES'].append(f"- {scope}{desc}")

    # Group remaining by section
    for commit in commits:
        section = SECTION_MAP.get(commit.type)
        if not section:
            continue
        if section not in sections:
            sections[section] = []
        scope = f"**{commit.scope}**: " if commit.scope else ""
        link = f"([{commit.hash[:7]}]({repo_url}/commit/{commit.hash}))"
        sections[section].append(f"- {scope}{commit.description} {link}")

    # Render
    lines = [f"## [{version}] - {date}", ""]
    for section_name in ['BREAKING CHANGES', 'Added', 'Changed', 'Deprecated', 'Removed', 'Fixed', 'Performance', 'Security']:
        if section_name in sections:
            lines.append(f"### {section_name}")
            lines.extend(sections[section_name])
            lines.append("")

    return '\n'.join(lines)
```

## Commit Linting

### Pre-Commit Hook

```bash
#!/bin/bash
# .git/hooks/commit-msg
# Validates commit message follows Conventional Commit format

COMMIT_MSG_FILE=$1
COMMIT_MSG=$(cat "$COMMIT_MSG_FILE")
FIRST_LINE=$(head -1 "$COMMIT_MSG_FILE")

PATTERN='^(feat|fix|perf|refactor|docs|test|build|ci|chore|security|deprecated|remove)(\([a-z0-9-]+\))?!?:\s.{1,72}$'

if ! echo "$FIRST_LINE" | grep -qE "$PATTERN"; then
  echo "ERROR: Commit message does not follow Conventional Commits format."
  echo ""
  echo "Expected: <type>(<scope>): <description>"
  echo "Example:  feat(auth): add OAuth2 login flow"
  echo ""
  echo "Valid types: feat, fix, perf, refactor, docs, test, build, ci, chore, security"
  echo ""
  echo "Your message: $FIRST_LINE"
  exit 1
fi

# Check description length
DESC_LENGTH=$(echo "$FIRST_LINE" | sed 's/^[^:]*: //' | wc -c)
if [ "$DESC_LENGTH" -gt 72 ]; then
  echo "ERROR: Commit description exceeds 72 characters ($DESC_LENGTH chars)."
  exit 1
fi
```

### CI Linting

```yaml
# .github/workflows/lint-commits.yml
name: Lint Commits
on:
  pull_request:

jobs:
  commitlint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm install -g @commitlint/cli @commitlint/config-conventional
      - run: |
          npx commitlint --from ${{ github.event.pull_request.base.sha }} \
                          --to ${{ github.event.pull_request.head.sha }}
```

## Monorepo Strategy

### Scoped Changelogs

In a monorepo, each package maintains its own changelog filtered by scope:

```bash
# Get commits scoped to a specific package
git log v1.3.0..HEAD --pretty=format:'%H %s' --no-merges | \
  grep -E '^\w+ (feat|fix|perf|refactor)\(ui\):'

# Example output:
# abc1234 feat(ui): add date picker component
# def5678 fix(ui): button alignment on mobile
```

### Per-Package Changelog Location

```
packages/
  ui/
    CHANGELOG.md        ← @repo/ui changes only
    package.json
  api/
    CHANGELOG.md        ← @repo/api changes only
    package.json
CHANGELOG.md            ← infrastructure / cross-cutting changes
```

## Release Workflow Integration

```
PR merges to main
      │
      v
CI detects new commits since last tag
      │
      v
Parse commits → determine bump → generate changelog
      │
      v
Create draft GitHub Release with generated notes
      │
      v
Human reviews and edits release notes
      │
      v
Publish release → triggers deployment pipeline
```

## Output Quality Checklist

Before publishing generated changelog:

1. Each bullet is user-meaningful, not implementation noise
2. Breaking changes include migration instructions
3. Security fixes are in their own section (not mixed with bug fixes)
4. Duplicate bullets across sections are removed
5. Scope prefixes are consistent and meaningful
6. Empty sections are omitted
7. Links to PRs/commits are correct

## Common Pitfalls

- **Merge commit messages polluting the changelog** — exclude merge commits with `--no-merges`
- **Vague commit messages** — "fix stuff" cannot become a useful release note; enforce linting
- **Missing migration guidance for breaking changes** — require `BREAKING CHANGE:` footer with instructions
- **Docs/chore commits in user-facing changelog** — filter to only user-facing types
- **Overwriting historical entries** — always prepend new entries, never modify existing ones
- **Manual version bumps in monorepos** — use Changesets for coordinated versioning

## Best Practices

1. **Enforce conventional commits in CI** — block merges with non-conforming messages
2. **Scope commits in monorepos** — `feat(ui):` not just `feat:` for package-specific changes
3. **Review generated changelog before publishing** — automation gets you 90%, human editing adds polish
4. **Tag releases after changelog is finalized** — changelog is part of the release, not an afterthought
5. **Keep an [Unreleased] section** — for manual curation between releases
6. **Link to PRs, not commits** — PRs have context and discussion that commits lack
7. **Separate internal and external changelogs** — users do not need to know about CI config changes

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Changelog is empty after generation | All commits use non-user-facing types (`docs`, `chore`, `ci`, `test`) | Ensure feature and fix commits use `feat:` or `fix:` types; review type-to-section mapping |
| Version bump detected as `none` | No commits match bump-triggering types | Verify commits follow Conventional Commit format; check regex pattern matches your type list |
| Breaking changes missing from output | `BREAKING CHANGE:` footer has wrong casing or whitespace | Use exact string `BREAKING CHANGE:` (uppercase, with colon and space) in commit footer |
| Monorepo changelog includes unrelated packages | Scope filter not applied or scope names inconsistent | Standardize scope names across teams; filter commits with `grep -E 'type\(your-scope\):'` |
| Merge commits polluting release notes | `--no-merges` flag omitted from `git log` | Always pass `--no-merges` when collecting commits for changelog generation |
| Commit linter rejects valid messages | Regex pattern missing a valid type or scope contains uppercase | Update the `PATTERN` regex to include all custom types; enforce lowercase scopes |
| Duplicate entries across changelog sections | A breaking change commit also matches its original type section | Deduplicate by checking if a commit already appears in BREAKING CHANGES before adding to type section |

## Success Criteria

- **Commit parse rate above 95%** — fewer than 5% of commits in a release range fail to parse as valid Conventional Commits
- **Zero manual version bump errors** — semantic version is always determined automatically from commit types, never hand-edited
- **Changelog generation under 10 seconds** — full parse-classify-render cycle completes in under 10 seconds for repositories with up to 500 commits per release
- **100% of breaking changes documented** — every commit with `!` suffix or `BREAKING CHANGE:` footer appears in the BREAKING CHANGES section with migration guidance
- **Release notes review time under 15 minutes** — generated changelog requires minimal human editing before publication
- **Commit lint failure rate below 2%** — after team onboarding, fewer than 2% of commits are rejected by the pre-commit hook or CI linter
- **Monorepo scope accuracy at 100%** — scoped changelogs contain only commits relevant to their package with no cross-contamination

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
