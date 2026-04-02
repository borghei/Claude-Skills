---
title: Quick Start
---

# Quick Start: Your First Skill in 5 Minutes

This guide walks you through using a Claude Skill from clone to first result.

## Step 1: Clone the Repository

```bash
git clone https://github.com/borghei/Claude-Skills.git
cd Claude-Skills
```

## Step 2: Pick a Skill

Browse the catalog and pick something relevant to your work.

| If you want to... | Try this skill |
|---|---|
| Review code quality | `engineering/code-reviewer` |
| Optimize your CLAUDE.md | `engineering/claude-code-mastery` |
| Analyze campaign ROI | `marketing/campaign-analytics` |
| Run a compliance audit | `ra-qm-team/soc2-compliance-expert` |
| Score features with RICE | `product-team/product-manager-toolkit` |

## Step 3: Run a Tool

Every skill includes Python CLI tools in its `scripts/` folder. Run one directly:

```bash
python engineering/code-reviewer/scripts/code_quality_analyzer.py /path/to/your/project
```

Output looks like:

```
Code Quality Report
  Overall Score: 78/100
  Files Analyzed: 42
  Issues: 3 critical, 7 warnings
  Top Issue: Missing error handling in api/routes.py:142
```

## Step 4: Use the SKILL.md with Your AI Assistant

=== "Claude Code"

    Reference the skill in your `CLAUDE.md`:
    ```markdown
    ## Skills
    - See engineering/code-reviewer/SKILL.md for code review workflows
    ```

    Or invoke directly:
    ```
    > Review this PR using engineering/code-reviewer/SKILL.md guidelines
    ```

=== "Cursor"

    Add to `.cursorrules`:
    ```
    When reviewing code, follow the frameworks in engineering/code-reviewer/SKILL.md
    ```

=== "Copilot"

    Reference in `.github/copilot-instructions.md`:
    ```markdown
    For code reviews, apply engineering/code-reviewer/SKILL.md standards
    ```

## Step 5: Explore Agents (Optional)

Agents combine multiple skills into specialized personas. Try one:

```
> /agents/cs-tech-lead Review the architecture of this project
```

The agent selects relevant skills, runs tools, and produces structured analysis.

## What's Next

- Browse the full [Skill Catalog](../skills/index.md) to find skills for your domain
- Read [Authoring Guide](../guides/authoring.md) to create custom skills
- Check [Starter Bundles](../guides/bundles.md) for pre-selected skill sets by role
