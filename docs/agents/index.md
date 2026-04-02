---
title: Agents
---

# Agents

Claude Skills includes **25 role-based agents** and **7 personas** that combine multiple skills into specialized AI experts. Agents select the right skills, run relevant tools, and produce structured analysis.

## Two Types of Agents

### Task Agents (cs-* prefix)

Task agents are domain specialists. Each one focuses on a specific function like code review, security auditing, or compliance assessment. They follow structured workflows and produce actionable reports.

**19 task agents** across 5 domains.

[:octicons-arrow-right-24: View all task agents](task-agents.md)

### Personas

Personas are cross-functional roles that combine skills from multiple domains. A "Startup CTO" persona draws from engineering, product, and c-level skills simultaneously.

**7 personas** for common professional roles.

[:octicons-arrow-right-24: View all personas](personas.md)

### Subagents (Claude Code only)

**6 built-in subagents** in `.claude/agents/` run autonomously within Claude Code:

| Subagent | Purpose |
|---|---|
| `code-reviewer` | Autonomous PR review with security and quality checks |
| `security-auditor` | Security vulnerability scanning |
| `qa-engineer` | Test generation and quality assurance |
| `doc-generator` | Documentation generation from code |
| `changelog-manager` | Changelog updates from git history |
| `git-workflow` | Branch management and PR creation |

```
> /agents/code-reviewer Review the last 3 commits for security issues
```

## How Agents Work

1. You invoke an agent with a task description
2. The agent selects relevant skills from its domain
3. It runs Python tools for automated analysis
4. It applies knowledge from reference guides
5. It produces a structured report or recommendation

!!! tip "Agents are optional"
    You can always use skills directly without agents. Agents are a convenience layer for common multi-skill workflows.
