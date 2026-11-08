---
name: claude-code-mastery
description: >
  Optimizes CLAUDE.md files, scaffolds skills and subagents, wires hooks and measures context
  budget for Claude Code. Use when writing or trimming a CLAUDE.md, creating a skill, subagent
  or hook, or auditing token usage.
license: MIT
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: development-tools
  updated: 2026-11-08
  tags: [claude-code, skill-authoring, subagents, hooks]
---
# Claude Code Mastery

Expert skill for Claude Code CLI -- CLAUDE.md optimization, skill authoring, subagent creation, hooks automation, and context engineering.

## Core Capabilities

- **CLAUDE.md optimization** — audit, restructure, compress, and hierarchize config files for token efficiency.
- **Skill authoring** — scaffold and write discoverable skill packages with correct layout and frontmatter.
- **Subagent creation** — write `.claude/agents/<name>.md` files with a `tools` allowlist and a Markdown-body system prompt.
- **Hooks automation** — wire `PreToolUse`/`PostToolUse`/`Stop` lifecycle scripts via `.claude/settings.json`.
- **Context engineering** — measure and manage the context-window token budget across a codebase.

## When to Use

- Authoring, structuring, or optimizing a CLAUDE.md file for any project.
- Scaffolding a new skill package or creating a Claude Code subagent.
- Configuring hooks for automated quality, security, or workflow steps.
- Auditing and reducing context-window consumption.

## Clarify First

Before scaffolding or optimizing, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Which task:** scaffold a new skill, optimize a CLAUDE.md, create a subagent, or analyze context budget (selects `skill_scaffolder.py` vs `claudemd_optimizer.py` vs `context_analyzer.py`).
- **Target identity:** for a new skill: its name, domain, and one-line description; for optimization: the file or project path (the inputs the scripts require).
- **Token budget:** the target ceiling (sets `--token-limit` and what counts as over-budget).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Workflow

```bash
# Score a CLAUDE.md for structure, token cost and redundancy (default budget 6000 tokens)
python scripts/claudemd_optimizer.py CLAUDE.md --token-limit 4000

# Estimate how much of the context window a project's files would take, by category
python scripts/context_analyzer.py . --max-depth 4 --context-window 200000

# Scaffold a skill package into an existing parent directory
python scripts/skill_scaffolder.py my-skill -d engineering -o /tmp --description "Scores API specs for breaking changes"
```

All three accept `--json`. Full flags and output fields: [references/tool-reference.md](references/tool-reference.md).

- `claudemd_optimizer.py` reports a 0–100 score, the token estimate against `--token-limit`, duplicated or vague sections, and concrete cuts.
- `context_analyzer.py` defaults to a 200K window as a conservative floor. Pass the real window of the model you run, or the percentages will overstate the pressure.
- `skill_scaffolder.py` creates `<-o DIR>/<skill-name>/` with `SKILL.md`, `scripts/`, `references/` and `assets/`. `-o` (`--output`) is the parent directory, which must already exist; it defaults to the current directory, so pass `-o` to keep the scaffold out of the repo you are standing in. If the description has no "Use when" clause it appends a placeholder so you fill in the triggers before shipping.

**Exit codes (all three):** `0` report or scaffold written; `2` missing file or path, output directory that does not exist, or a skill folder that already exists. They are advisory, not gates: an over-budget CLAUDE.md still exits 0.

**Done when:** the CLAUDE.md fits its budget and every line is something the model could not infer from the code; a new skill's description says what it does and when to use it in under 240 characters; a hook has been triggered once on purpose and blocked or passed as intended.

## Anti-Patterns

### CLAUDE.md as a wiki
**Mistake:** Pasting architecture essays, full style guides and onboarding notes into CLAUDE.md.
**Why it happens:** It is the one file the agent always reads, so everything lands there.
**Instead:** Keep commands, conventions and traps the code does not reveal; link to longer docs and let the agent read them when needed. Every line costs tokens on every turn.

### Hooks that fail open
**Mistake:** A PreToolUse guard that exits 1 on a violation and assumes the tool call was blocked.
**Why it happens:** Exit 1 means "error" in most CLIs.
**Instead:** A PreToolUse hook blocks only on exit 2 (stderr goes back to the model). Test the hook against a real violating command before relying on it. See [references/hooks-cookbook.md](references/hooks-cookbook.md).

### Subagents with every tool
**Mistake:** A review subagent with no `tools` allowlist, so it can edit files and run shell commands.
**Why it happens:** Omitting `tools` is the shortest working file.
**Instead:** Give each subagent the smallest tool list its job needs; a reviewer gets read and search tools only.

## Files

- `scripts/claudemd_optimizer.py`, `scripts/context_analyzer.py`, `scripts/skill_scaffolder.py` — the three CLIs above.
- `assets/skill-template.md`, `assets/agent-template.md` — starting files for a skill and a subagent.
- `references/` — playbooks, quick reference, tool reference, skill authoring, subagent patterns, hooks cookbook.

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

## See Also

- [context-engine](../context-engine/SKILL.md) — compression and prioritisation once you know the budget.
- [doc-drift-detector](../doc-drift-detector/SKILL.md) — find where CLAUDE.md no longer matches the code.
- [code-reviewer](../code-reviewer/SKILL.md) — review logic for a code-review subagent.
- [senior-prompt-engineer](../senior-prompt-engineer/SKILL.md) — wording for skill descriptions and agent prompts.
