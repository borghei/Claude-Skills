# CI/CD Workflows

12 ready-to-use GitHub Actions workflow templates in [`templates/workflows/`](../templates/workflows/). Copy to your project's `.github/workflows/` directory to activate.

---

## Quick Setup

```bash
# Copy all workflows
mkdir -p .github/workflows
cp templates/workflows/*.yml .github/workflows/

# Or copy individual workflows
cp templates/workflows/ci-quality-gate.yml .github/workflows/
```

---

## Workflow Reference

| Workflow | Triggers On | What It Does |
|----------|------------|--------------|
| `ci-quality-gate.yml` | PR | YAML lint, Python syntax check, security audit |
| `qa-validation.yml` | PR with `*.py` changes | Flake8 lint, Bandit security scan, CLI standards check |
| `skill-validation.yml` | PR touching skills | Package structure validation, tier classification |
| `documentation-check.yml` | PR with `*.md` changes | YAML frontmatter validation, link checking, skill inventory |
| `changelog-enforcer.yml` | PR to main/dev | Ensures CHANGELOG.md is updated when code changes |
| `release-drafter.yml` | Push to main | Auto-generates release notes with full repo stats |
| `skill-auto-update.yml` | Daily + manual | Detects changed skills, generates update manifest |
| `claude-code-review.yml` | PR | AI-powered code review via Claude |
| `claude.yml` | @claude mentions | Interactive Claude Code in issues/PRs |
| `pr-issue-auto-close.yml` | PR merged | Auto-close linked issues on merge |
| `smart-sync.yml` | Issue label/state changes | Bidirectional issue/project board sync |
| `sync-codex-skills.yml` | SKILL.md changes | Codex compatibility sync |

---

## Workflow Details

### ci-quality-gate.yml

Runs on every pull request. Validates Python syntax, runs linting, and performs a security audit.

```
Example output:
  [ok] Python Syntax Check     -- 180/180 scripts compiled successfully
  [ok] Flake8 Lint             -- 0 errors (E9, F63, F7, F82)
  [ok] Bandit Security Scan    -- 0 high-severity issues
  [ok] CLI Standards           -- 180/180 scripts have argparse + --help
```

**Required secrets:** None

### qa-validation.yml

Triggers on PRs that include changes to `*.py` files. Runs Flake8 for linting, Bandit for security scanning, and checks CLI standards (argparse, --help).

**Required secrets:** None

### skill-validation.yml

Triggers on PRs that touch skill packages. Validates package structure and classifies skills into quality tiers.

```
Example output:
  [ok] senior-fullstack         -- SKILL.md (342 lines), 3 scripts, 2 refs, 1 asset -> Tier 1
  [ok] claude-code-mastery      -- SKILL.md (488 lines), 3 scripts, 3 refs, 2 assets -> Tier 1
  [!!] senior-cloud-architect   -- SKILL.md (89 lines), 0 scripts -> Tier 3 (needs upgrade)
```

**Required secrets:** None

### documentation-check.yml

Triggers on PRs with markdown changes. Validates YAML frontmatter in SKILL.md files, checks internal links, and counts skills.

**Required secrets:** None

### changelog-enforcer.yml

Triggers on PRs targeting main or dev. Warns when CHANGELOG.md is not updated alongside code changes. Suggests a changelog entry based on the changed files.

**Required secrets:** None

### release-drafter.yml

Triggers on push to main. Auto-generates release notes with repository stats, latest skills, and installation instructions.

**Required secrets:** `GITHUB_TOKEN` (automatically available)

### skill-auto-update.yml

Runs daily and on manual trigger. Detects changed skills since last run and generates an update manifest for downstream consumers.

**Required secrets:** None

### claude-code-review.yml

Triggers on pull requests. Runs an AI-powered code review using Claude Code, posting inline comments on the PR.

**Required secrets:** `ANTHROPIC_API_KEY`

### claude.yml

Triggers when @claude is mentioned in issues or PR comments. Enables interactive Claude Code conversations directly in GitHub.

**Required secrets:** `ANTHROPIC_API_KEY`

### pr-issue-auto-close.yml

Triggers when a PR is merged. Automatically closes any issues linked in the PR body (e.g., "Closes #123").

**Required secrets:** `GITHUB_TOKEN` (automatically available)

### smart-sync.yml

Triggers on issue label or state changes. Provides bidirectional sync between issues and project boards.

**Required secrets:** `GITHUB_TOKEN` (automatically available), project board configured

### sync-codex-skills.yml

Triggers when SKILL.md files change. Syncs skills to the `.codex/` directory for OpenAI Codex compatibility.

**Required secrets:** None

---

## Customization

### Modifying Triggers

Each workflow file has an `on:` section you can customize:

```yaml
on:
  pull_request:
    branches: [main, dev]        # Change target branches
    paths: ['engineering/**']     # Limit to specific paths
  push:
    branches: [main]
```

### Adding Required Secrets

For workflows that need API keys, add them in your repository settings:

1. Go to **Settings > Secrets and variables > Actions**
2. Click **New repository secret**
3. Add the required secret (e.g., `ANTHROPIC_API_KEY`)

### Disabling a Workflow

Either delete the workflow file from `.github/workflows/` or add a condition:

```yaml
jobs:
  build:
    if: false  # Temporarily disabled
```

See [`templates/workflows/README.md`](../templates/workflows/README.md) and [`templates/workflows/SETUP_GUIDE.md`](../templates/workflows/SETUP_GUIDE.md) for additional setup instructions.
