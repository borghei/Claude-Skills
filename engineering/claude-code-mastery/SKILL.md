---
name: claude-code-mastery
description: 
license: MIT
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: development-tools
  updated: 2026-06-17
  tags: [claude-code, skill-authoring, subagents, hooks]
---
# Claude Code Mastery

Expert skill for Claude Code CLI -- CLAUDE.md optimization, skill authoring, subagent creation, hooks automation, and context engineering.

**Keywords:** claude-code, claude-cli, CLAUDE.md, skill-authoring, subagents, hooks, context-window, token-budget, MCP-servers, worktrees, permission-modes, prompt-engineering, context-engineering, slash-commands

## Core Capabilities

- **CLAUDE.md optimization** — audit, restructure, compress, and hierarchize config files for token efficiency.
- **Skill authoring** — scaffold and write discoverable skill packages with correct layout and frontmatter.
- **Subagent creation** — define scoped agents with `allowed-tools` and structured custom instructions.
- **Hooks automation** — wire `PreToolUse`/`PostToolUse`/`Stop` lifecycle scripts via `.claude/settings.json`.
- **Context engineering** — measure and manage the context-window token budget across a codebase.

## When to Use

- Authoring, structuring, or optimizing a CLAUDE.md file for any project.
- Scaffolding a new skill package or creating a Claude Code subagent.
- Configuring hooks for automated quality, security, or workflow steps.
- Auditing and reducing context-window consumption.

## Clarify First

Before scaffolding or optimizing, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Which task** — scaffold a new skill, optimize a CLAUDE.md, create a subagent, or analyze context budget (selects `skill_scaffolder.py` vs `claudemd_optimizer.py` vs `context_analyzer.py`)
- [ ] **Target identity** — for a new skill: its name, domain, and one-line description; for optimization: the file or project path (the inputs the scripts require)
- [ ] **Token budget** — the target ceiling (sets `--token-limit` and what counts as over-budget)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Quick Start

```bash
# Scaffold a new skill package
python scripts/skill_scaffolder.py my-new-skill --domain engineering --description "Brief description"

# Analyze and optimize an existing CLAUDE.md
python scripts/claudemd_optimizer.py path/to/CLAUDE.md

# Estimate context window usage across a project
python scripts/context_analyzer.py /path/to/project

# All tools support JSON output
python scripts/claudemd_optimizer.py CLAUDE.md --json
```

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `skill_scaffolder.py` | Scaffold a new skill package with correct structure + frontmatter | `python scripts/skill_scaffolder.py my-skill -d engineering --description "Does X"` |
| `claudemd_optimizer.py` | Score a CLAUDE.md for structure, tokens, and redundancy with recommendations | `python scripts/claudemd_optimizer.py CLAUDE.md --token-limit 4000` |
| `context_analyzer.py` | Estimate context-window consumption by file category with a budget breakdown | `python scripts/context_analyzer.py /path/to/project --max-depth 4` |

All tools support `--json`. See **[references/tool-reference.md](references/tool-reference.md)** for full parameter tables and output formats.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/workflows.md](references/workflows.md)** — the five numbered playbooks: optimize a CLAUDE.md, author a skill, create a subagent, configure hooks, and manage the context budget. Read when executing any of those tasks step-by-step.
- **[references/quick-reference.md](references/quick-reference.md)** — slash commands, permission modes, CLAUDE.md loading order, MCP servers, the troubleshooting table, and success criteria. Read for at-a-glance lookups or when debugging configuration.
- **[references/tool-reference.md](references/tool-reference.md)** — full parameter tables and output formats for the three Python tools. Read when scripting the tools or interpreting their JSON output.
- **[references/skill-authoring-guide.md](references/skill-authoring-guide.md)** — comprehensive reference for writing effective skills, from YAML frontmatter to structure. Read when authoring a skill in depth.
- **[references/subagent-patterns.md](references/subagent-patterns.md)** — guide to creating and using subagents for parallel work and scoped tasks. Read when designing a subagent.
- **[references/hooks-cookbook.md](references/hooks-cookbook.md)** — practical hook recipes for code quality, security enforcement, and workflow automation. Read when building hooks.

**Templates:** [assets/skill-template.md](assets/skill-template.md), [assets/agent-template.md](assets/agent-template.md)

## Scope & Limitations

**This skill covers:**
- Authoring, structuring, and optimizing CLAUDE.md files for any project
- Scaffolding new skill packages with correct directory layout and frontmatter
- Creating and configuring Claude Code subagents with scoped tool access
- Analyzing and managing context window token budgets across a codebase

**This skill does NOT cover:**
- Writing application source code or implementing business logic (see [senior-fullstack](../senior-fullstack/SKILL.md), [senior-backend](../senior-backend/SKILL.md))
- MCP server development or custom transport protocols (see [mcp-server-builder](../../engineering/mcp-server-builder/SKILL.md))
- Advanced prompt engineering techniques for LLM applications (see [senior-prompt-engineer](../senior-prompt-engineer/SKILL.md))
- CI/CD pipeline configuration or deployment automation (see [senior-devops](../senior-devops/SKILL.md), [ci-cd-pipeline-builder](../../engineering/ci-cd-pipeline-builder/SKILL.md))

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| [senior-architect](../senior-architect/SKILL.md) | Architecture decisions inform CLAUDE.md structure sections | Architecture diagrams and patterns feed into the Architecture Overview section of CLAUDE.md |
| [code-reviewer](../code-reviewer/SKILL.md) | Subagent creation for automated code review | Claude Code Mastery creates the agent YAML; Code Reviewer provides the review logic |
| [senior-prompt-engineer](../senior-prompt-engineer/SKILL.md) | Prompt optimization for skill descriptions and agent instructions | Prompt engineering techniques improve YAML frontmatter trigger phrases and agent `custom-instructions` |
| [doc-drift-detector](../doc-drift-detector/SKILL.md) | Detects when CLAUDE.md drifts out of sync with the codebase | Context Analyzer output feeds drift detection; drift findings trigger CLAUDE.md optimization |
| [context-engine](../../engineering/context-engine/SKILL.md) | Advanced context management strategies | Context Analyzer provides token budgets; Context Engine applies compression and prioritization |
| [senior-secops](../senior-secops/SKILL.md) | Security hooks and permission mode configuration | SecOps policies define which tools to deny; Claude Code Mastery configures the permission allowlists |
