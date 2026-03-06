# Sample GitHub Workflows

12 ready-to-use GitHub Actions workflows for managing your AI skills repository. Copy the ones you need into your project's `.github/workflows/` directory.

## Quick Start

```bash
# Copy all workflows to your project
mkdir -p .github/workflows
cp templates/workflows/*.yml .github/workflows/

# Or copy individual workflows
cp templates/workflows/ci-quality-gate.yml .github/workflows/
cp templates/workflows/skill-validation.yml .github/workflows/
```

## Available Workflows

### Quality & Validation

| Workflow | Triggers On | What It Does |
|----------|------------|--------------|
| `ci-quality-gate.yml` | PR | YAML lint, Python syntax check, security audit, markdown link checks |
| `qa-validation.yml` | PR/push with `*.py` changes | Flake8, bandit security, CLI standards |
| `skill-validation.yml` | PR touching skills | Package structure validation, tier classification |
| `documentation-check.yml` | PR with `*.md` changes | YAML frontmatter validation, link checking, skill inventory |

### Release & Deployment

| Workflow | Triggers On | What It Does |
|----------|------------|--------------|
| `changelog-enforcer.yml` | PR to main/dev | Ensures CHANGELOG.md is updated when code changes |
| `release-drafter.yml` | Push to main | Auto-generates release notes with repo stats |
| `skill-auto-update.yml` | Daily + manual | Detects changed skills, generates update manifest and skills index |

### Code Review & Automation

| Workflow | Triggers On | What It Does |
|----------|------------|--------------|
| `claude-code-review.yml` | PR | AI-powered code review via Claude Code |
| `claude.yml` | @claude mentions | Interactive Claude Code in issues/PRs |
| `pr-issue-auto-close.yml` | PR merged | Auto-close linked issues, update project board |

### Synchronization

| Workflow | Triggers On | What It Does |
|----------|------------|--------------|
| `smart-sync.yml` | Issue label/state changes | Bidirectional issue ↔ GitHub Project board sync |
| `sync-codex-skills.yml` | SKILL.md changes | Sync skills to .codex/ directory via symlinks |

## Setup

Most workflows work out of the box. Some require secrets:

| Workflow | Required Secret | Purpose |
|----------|----------------|---------|
| `claude-code-review.yml` | `CLAUDE_CODE_OAUTH_TOKEN` | Claude Code API access |
| `claude.yml` | `CLAUDE_CODE_OAUTH_TOKEN` | Claude Code API access |
| `smart-sync.yml` | `PROJECTS_TOKEN` | GitHub Project board access |

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for detailed configuration instructions.

## Kill Switch

All workflows check a `WORKFLOW_KILLSWITCH` file for emergency disable:

```bash
# Disable all workflows
echo "STATUS: DISABLED" > .github/WORKFLOW_KILLSWITCH

# Re-enable
echo "STATUS: ENABLED" > .github/WORKFLOW_KILLSWITCH
```

Copy the [WORKFLOW_KILLSWITCH](WORKFLOW_KILLSWITCH) file to your `.github/` directory to enable this feature.

## Customization

These workflows are designed as starting points. Common customizations:

- **Change triggers** — adjust `on:` sections for your branching strategy
- **Add/remove checks** — modify job steps to match your stack
- **Update schedules** — change cron expressions in `skill-auto-update.yml`
- **Adjust permissions** — tighten `permissions:` blocks for your security requirements
