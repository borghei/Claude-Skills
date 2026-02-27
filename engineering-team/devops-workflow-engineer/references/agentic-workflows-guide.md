# GitHub Agentic Workflows Guide

Reference for GitHub's agentic workflow system (2026): markdown-based AI automation definitions, safe-outputs, tool permissions, continuous automation categories, and setup with the gh-aw CLI.

---

## Table of Contents

- [Overview](#overview)
- [What Are Agentic Workflows?](#what-are-agentic-workflows)
- [Markdown-Based Workflow Format](#markdown-based-workflow-format)
- [Frontmatter Schema](#frontmatter-schema)
- [Safe-Outputs Concept](#safe-outputs-concept)
- [Tool Permissions](#tool-permissions)
- [Six Continuous Automation Categories](#six-continuous-automation-categories)
- [Setup with gh-aw CLI](#setup-with-gh-aw-cli)
- [Examples](#examples)
- [Integration with Traditional GitHub Actions](#integration-with-traditional-github-actions)
- [Best Practices](#best-practices)
- [Limitations and Considerations](#limitations-and-considerations)

---

## Overview

GitHub agentic workflows are a new automation layer that enables AI-driven tasks within GitHub repositories. Unlike traditional GitHub Actions (which use YAML-based declarative definitions), agentic workflows are defined in **markdown files** with YAML frontmatter, written in natural language, and executed by an AI agent with access to repository tools.

Agentic workflows complement, rather than replace, GitHub Actions. They are best suited for tasks that benefit from AI reasoning: code review, documentation generation, triage, and security analysis.

---

## What Are Agentic Workflows?

Agentic workflows are:

- **Markdown files** stored in `.github/agents/` within a repository.
- **Triggered by GitHub events** (pull_request, push, issues, schedule, etc.).
- **Executed by an AI agent** that reads the markdown instructions and uses declared tools.
- **Permission-scoped** to limit what the agent can access.
- **Safe by default** -- outputs are labeled as AI-generated and require human review.

### Key Differences from GitHub Actions

| Aspect | GitHub Actions | Agentic Workflows |
|--------|---------------|-------------------|
| Definition format | YAML | Markdown + YAML frontmatter |
| Execution model | Declarative steps | AI-driven reasoning |
| Logic | Explicit conditionals | Natural language instructions |
| Tool access | Shell commands, actions | Declared tool permissions |
| Output control | Direct write | Safe-outputs (labeled, auditable) |
| Best for | Deterministic automation | Reasoning-heavy tasks |

---

## Markdown-Based Workflow Format

Agentic workflows are stored as markdown files in `.github/agents/`:

```
.github/
  agents/
    code-review.md
    triage-issues.md
    update-docs.md
    security-scan.md
```

### Structure

Each file has two parts:

1. **YAML frontmatter** -- Metadata, triggers, tools, and permissions.
2. **Markdown body** -- Natural language instructions for the AI agent.

### Minimal Example

```markdown
---
name: code-review-agent
description: Reviews pull requests for quality, security, and conventions
triggers:
  - pull_request
tools:
  - code-search
  - file-read
  - comment-create
permissions:
  contents: read
  pull-requests: write
safe-outputs: true
---

# Code Review Agent

Review every pull request for:

1. Security vulnerabilities and credential leaks
2. Performance regressions
3. Test coverage gaps
4. Adherence to project coding conventions

## Process

- Read the pull request diff and understand the context
- Search the codebase for related files that might be affected
- Post inline comments for specific issues found
- Post a summary comment with an overall assessment
```

---

## Frontmatter Schema

The YAML frontmatter defines the workflow's identity, triggers, capabilities, and constraints.

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Unique identifier for the workflow (kebab-case) |
| `description` | string | What the workflow does (for UI display) |
| `triggers` | list | GitHub events that activate this workflow |

### Optional Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `tools` | list | [] | Tools the agent can access |
| `permissions` | map | {} | GitHub token permissions |
| `safe-outputs` | boolean | true | Label outputs as AI-generated |
| `model` | string | (platform default) | AI model to use |
| `max-iterations` | integer | 10 | Max reasoning loops |
| `timeout-minutes` | integer | 15 | Execution timeout |
| `concurrency` | map | {} | Concurrency group settings |

### Triggers

Agentic workflows support the same event triggers as GitHub Actions:

```yaml
triggers:
  - pull_request           # Fires on PR open, sync, reopen
  - push                   # Fires on push to branches
  - issues                 # Fires on issue open, edit, label
  - issue_comment          # Fires on new comments
  - schedule               # Cron-based scheduling
  - workflow_dispatch      # Manual trigger
  - release                # Fires on release events
```

### Trigger with Filters

```yaml
triggers:
  - type: pull_request
    branches: [main, release/*]
    paths: ['src/**', 'tests/**']
  - type: schedule
    cron: '0 9 * * 1'     # Mondays at 9 AM UTC
```

---

## Safe-Outputs Concept

The `safe-outputs: true` flag (enabled by default) ensures that everything the agent produces is:

1. **Labeled as AI-generated** -- Comments, commits, and issues include an AI attribution badge.
2. **Not auto-merged** -- PR changes created by the agent require human approval.
3. **Not auto-deployed** -- Deployment triggers are suppressed for agent-created artifacts.
4. **Fully auditable** -- Every action is logged with the agent's reasoning chain.

### Why Safe-Outputs Matters

- Prevents AI hallucinations from reaching production unreviewed.
- Maintains human accountability for all deployed changes.
- Provides an audit trail for compliance.
- Builds trust incrementally as teams gain confidence in AI outputs.

### Disabling Safe-Outputs

For low-risk automation (like labeling or triage), you can disable safe-outputs:

```yaml
safe-outputs: false   # Outputs are applied directly without AI labeling
```

**Use with caution.** Only disable for:
- Read-only operations (search, analysis)
- Low-risk write operations (adding labels, assigning reviewers)
- Internal tooling where all outputs are reviewed by other processes

---

## Tool Permissions

Agentic workflows declare which tools the agent can use. Each tool maps to a specific capability and required permission.

### Available Tools

| Tool | Capability | Required Permission |
|------|-----------|-------------------|
| `code-search` | Search repository code and file names | `contents: read` |
| `file-read` | Read file contents | `contents: read` |
| `file-write` | Create or modify files | `contents: write` |
| `comment-create` | Post comments on PRs and issues | `pull-requests: write` or `issues: write` |
| `issue-create` | Create new issues | `issues: write` |
| `issue-update` | Update issue labels, assignees, state | `issues: write` |
| `pr-review` | Submit PR reviews (approve, request changes) | `pull-requests: write` |
| `workflow-trigger` | Trigger other workflows | `actions: write` |
| `web-search` | Search the web for documentation | (no permission needed) |
| `run-command` | Execute shell commands in sandbox | `contents: write` |

### Permission Scoping

Follow the principle of least privilege:

```yaml
# Good: minimal permissions
permissions:
  contents: read
  pull-requests: write

# Avoid: overly broad
permissions:
  contents: write     # Only needed if the agent creates/modifies files
  actions: write      # Only needed if the agent triggers workflows
```

### Tool + Permission Matrix

```yaml
# Read-only agent (code review)
tools: [code-search, file-read, comment-create]
permissions:
  contents: read
  pull-requests: write

# Write agent (auto-fix)
tools: [code-search, file-read, file-write, comment-create]
permissions:
  contents: write
  pull-requests: write

# Triage agent (issue management)
tools: [issue-update, comment-create]
permissions:
  issues: write
```

---

## Six Continuous Automation Categories

GitHub organizes agentic workflows into six categories of continuous automation:

### 1. Code Quality

Automated code review, style enforcement, and quality checks.

**Triggers:** `pull_request`
**Tools:** `code-search`, `file-read`, `comment-create`, `pr-review`
**Examples:**
- Review PRs for security vulnerabilities
- Check adherence to coding conventions
- Identify performance anti-patterns
- Suggest refactoring opportunities

### 2. Documentation

Automated documentation generation, updates, and verification.

**Triggers:** `push` (to main), `pull_request`
**Tools:** `code-search`, `file-read`, `file-write`, `comment-create`
**Examples:**
- Generate changelog entries from PR titles
- Update API documentation when endpoints change
- Verify README accuracy
- Generate code documentation

### 3. Security

Automated security scanning, vulnerability detection, and remediation.

**Triggers:** `push`, `schedule`, `pull_request`
**Tools:** `code-search`, `file-read`, `comment-create`, `issue-create`
**Examples:**
- Scan for hardcoded secrets
- Detect dependency vulnerabilities
- Review infrastructure-as-code for misconfigurations
- Generate security advisories

### 4. Release Management

Automated versioning, release notes, and publishing.

**Triggers:** `release`, `workflow_dispatch`, `push` (tags)
**Tools:** `code-search`, `file-read`, `file-write`, `comment-create`
**Examples:**
- Draft release notes from merged PRs
- Bump version numbers
- Validate release checklists
- Generate migration guides

### 5. Issue Triage

Automated issue labeling, assignment, and prioritization.

**Triggers:** `issues`, `issue_comment`
**Tools:** `issue-update`, `comment-create`, `code-search`
**Examples:**
- Label issues by type (bug, feature, question)
- Assign issues to relevant team members
- Detect duplicate issues
- Prioritize based on severity

### 6. Maintenance

Automated dependency updates, cleanup, and housekeeping.

**Triggers:** `schedule`
**Tools:** `code-search`, `file-read`, `file-write`, `issue-create`
**Examples:**
- Check for outdated dependencies
- Clean up stale branches
- Archive old issues
- Verify CI configuration health

---

## Setup with gh-aw CLI

The `gh-aw` CLI extension manages agentic workflows from the command line.

### Installation

```bash
# Install the gh-aw extension
gh extension install github/gh-aw
```

### Commands

```bash
# List all agentic workflows in the repository
gh aw list

# Create a new agentic workflow from a template
gh aw create --name code-review --category code-quality

# Validate workflow files
gh aw validate

# Run a workflow manually (for testing)
gh aw run code-review --event pull_request --pr 42

# View workflow execution logs
gh aw logs code-review --run 12345

# Disable a workflow
gh aw disable code-review

# Enable a workflow
gh aw enable code-review
```

### Creating from Templates

```bash
# List available templates
gh aw templates

# Create from template
gh aw create --template security-scanner
gh aw create --template pr-reviewer
gh aw create --template issue-triager
gh aw create --template doc-generator
gh aw create --template release-drafter
gh aw create --template dependency-checker
```

### Validation

```bash
# Validate all workflow files
gh aw validate

# Output:
# .github/agents/code-review.md     [VALID]
# .github/agents/triage-issues.md   [VALID]
# .github/agents/update-docs.md     [WARNING] Missing description
# .github/agents/security-scan.md   [ERROR] Invalid tool: 'deploy-trigger'
```

---

## Examples

### Example 1: PR Code Reviewer

```markdown
---
name: pr-code-reviewer
description: Reviews pull requests for quality, security, and best practices
triggers:
  - pull_request
tools:
  - code-search
  - file-read
  - comment-create
  - pr-review
permissions:
  contents: read
  pull-requests: write
safe-outputs: true
timeout-minutes: 10
---

# PR Code Reviewer

## Instructions

Review the pull request thoroughly:

1. Read the complete diff to understand what changed
2. Search for related files that might be affected by the changes
3. Check for security issues: SQL injection, XSS, credential exposure
4. Check for performance issues: N+1 queries, unbounded loops, large allocations
5. Verify test coverage: new code should have corresponding tests
6. Check code style: consistent with project conventions

## Output

Post inline comments for specific issues with severity labels:
- [CRITICAL] Security vulnerabilities or data loss risks
- [WARNING] Performance issues or potential bugs
- [SUGGESTION] Style improvements or refactoring opportunities

Post a summary comment with:
- Overall assessment (approve, request changes, or comment)
- Risk level (low/medium/high)
- List of findings grouped by severity
```

### Example 2: Issue Triager

```markdown
---
name: issue-triager
description: Automatically labels and assigns new issues
triggers:
  - issues
tools:
  - code-search
  - issue-update
  - comment-create
permissions:
  issues: write
  contents: read
safe-outputs: false
---

# Issue Triager

When a new issue is created:

1. Read the issue title and body
2. Classify the issue type: bug, feature-request, question, documentation
3. Determine the affected component by searching the codebase for related files
4. Apply appropriate labels
5. If the issue is a bug, add priority label based on severity
6. Post a welcome comment acknowledging the issue and explaining next steps
```

### Example 3: Documentation Updater

```markdown
---
name: doc-updater
description: Updates documentation when code changes
triggers:
  - type: push
    branches: [main]
    paths: ['src/api/**']
tools:
  - code-search
  - file-read
  - file-write
  - comment-create
permissions:
  contents: write
  pull-requests: write
safe-outputs: true
---

# Documentation Updater

When API code changes are pushed to main:

1. Identify which API endpoints were modified
2. Read the current documentation in docs/api/
3. Compare code with documentation to find discrepancies
4. Create a PR with documentation updates
5. Include a summary of what changed and why

## Rules

- Only update documentation that is directly affected by code changes
- Preserve existing documentation style and formatting
- Add examples for new endpoints
- Mark deprecated endpoints clearly
```

---

## Integration with Traditional GitHub Actions

Agentic workflows coexist with GitHub Actions. Common integration patterns:

### Pattern 1: Agent Triggered by Action

```yaml
# .github/workflows/on-pr.yml
on:
  pull_request:
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - run: make lint
  # The agentic workflow in .github/agents/code-review.md
  # fires on the same pull_request event independently
```

### Pattern 2: Agent Triggers an Action

```markdown
---
tools:
  - workflow-trigger
permissions:
  actions: write
---

If the review finds critical security issues, trigger the
security-alert workflow to notify the security team.
```

### Pattern 3: Action Passes Context to Agent

GitHub Actions can create comments or artifacts that agentic workflows read as context for more informed analysis.

---

## Best Practices

1. **Start with safe-outputs enabled.** Disable only after building trust with a specific workflow.
2. **Scope permissions minimally.** Give each workflow only the tools and permissions it needs.
3. **Write clear, structured instructions.** Use numbered steps and explicit criteria.
4. **Test with `gh aw run` before enabling triggers.** Validate behavior on real PRs/issues.
5. **Set reasonable timeouts.** Default 15 minutes is good for most tasks; reduce for simple triage.
6. **Monitor execution logs.** Review `gh aw logs` regularly to catch unexpected behavior.
7. **Version your workflows.** Track changes to `.github/agents/` in version control like any other config.
8. **Combine with Actions for deterministic gates.** Use Actions for build/test/deploy; use agents for review/triage/documentation.
9. **Keep instructions focused.** One workflow per task. Do not create a single workflow that tries to do everything.
10. **Document the expected behavior.** Include a "## Rules" section in the markdown to set explicit boundaries.

---

## Limitations and Considerations

- **Non-deterministic:** Agentic workflows may produce different outputs for the same input. Use safe-outputs and human review.
- **Token costs:** Each execution consumes AI model tokens. Monitor usage for cost control.
- **Rate limits:** Frequent triggers (every push, every comment) can hit rate limits. Use path filters and concurrency groups.
- **Not a replacement for Actions:** Deterministic tasks (build, test, deploy) should remain in GitHub Actions.
- **Model availability:** Execution depends on AI model availability. Plan for occasional delays or failures.
- **Repository access:** Agentic workflows can only access the repository they are defined in (no cross-repo access by default).
