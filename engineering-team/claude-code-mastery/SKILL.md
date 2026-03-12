---
name: claude-code-mastery
description: >-
  Use when the user asks to "optimize CLAUDE.md", "create a new skill",
  "write a custom agent", "configure hooks", "manage context window",
  "set up MCP servers", "scaffold a skill package", "analyze token budget",
  "create subagents", "configure permissions", "set up worktrees", or
  "integrate Claude Code with editors". Covers Claude Code CLI mastery,
  skill authoring, context engineering, hooks automation, subagent creation,
  and development workflow optimization.
license: MIT
metadata:
  version: 1.0.0
  category: engineering
  domain: development-tools
---

# Claude Code Mastery

Expert skill for Claude Code CLI -- CLAUDE.md optimization, skill authoring,
subagent creation, hooks automation, and context engineering.

## Keywords

claude-code, claude-cli, CLAUDE.md, skill-authoring, subagents, hooks,
context-window, token-budget, MCP-servers, worktrees, permission-modes,
prompt-engineering, context-engineering, slash-commands

---

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

---

## Tools

### Skill Scaffolder

Generates a skill directory with SKILL.md template, scripts/, references/,
assets/ directories, and YAML frontmatter.

```bash
python scripts/skill_scaffolder.py my-skill --domain engineering --description "Does X"
```

| Parameter | Description |
|-----------|-------------|
| `skill_name` | Name for the skill (kebab-case) |
| `--domain, -d` | Domain category |
| `--description` | Brief description for frontmatter |
| `--version` | Semantic version (default: 1.0.0) |
| `--license` | License type (default: MIT) |
| `--output, -o` | Parent directory for skill folder |
| `--json` | Output as JSON |

### CLAUDE.md Optimizer

Analyzes a CLAUDE.md file and produces optimization recommendations.

```bash
python scripts/claudemd_optimizer.py CLAUDE.md --token-limit 4000 --json
```

**Output includes:** line count, token estimate, section completeness,
redundancy detection, missing sections, scored recommendations.

### Context Analyzer

Scans a project to estimate context window consumption by file category.

```bash
python scripts/context_analyzer.py /path/to/project --max-depth 4 --json
```

**Output includes:** token estimates per category, percentage of context
consumed, largest files, budget breakdown, reduction recommendations.

---

## Workflow 1: Optimize a CLAUDE.md

1. **Audit** -- Run `python scripts/claudemd_optimizer.py CLAUDE.md` and capture the score.
2. **Structure** -- Reorganize into these sections:
   ```markdown
   ## Project Purpose         -- What the project is
   ## Architecture Overview   -- Directory structure, key patterns
   ## Development Environment -- Build, test, setup commands
   ## Key Principles          -- 3-7 non-obvious rules
   ## Anti-Patterns to Avoid  -- Things that look right but are wrong
   ## Git Workflow            -- Branch strategy, commit conventions
   ```
3. **Compress** -- Convert paragraphs to bullets (saves ~30% tokens). Use code blocks for commands. Remove generic advice Claude already knows.
4. **Hierarchize** -- Move domain details to child CLAUDE.md files:
   ```
   project/
   ├── CLAUDE.md              # Global: purpose, architecture, principles
   ├── frontend/CLAUDE.md     # Frontend-specific: React patterns, styling
   ├── backend/CLAUDE.md      # Backend-specific: API patterns, DB conventions
   └── .claude/CLAUDE.md      # User-specific overrides (gitignored)
   ```
5. **Validate** -- Run `python scripts/claudemd_optimizer.py CLAUDE.md --token-limit 4000` and confirm score improved.

## Workflow 2: Author a New Skill

1. **Scaffold** -- `python scripts/skill_scaffolder.py my-skill -d engineering --description "..."`
2. **Write SKILL.md** in this order:
   - YAML frontmatter (name, description with trigger phrases, license, metadata)
   - Title and one-line summary
   - Quick Start (3-5 copy-pasteable commands)
   - Tools (each script with usage and parameters table)
   - Workflows (numbered step-by-step sequences)
   - Reference links
3. **Optimize the description** for auto-discovery:
   ```yaml
   description: >-
     This skill should be used when the user asks to "analyze performance",
     "optimize queries", "profile memory", or "benchmark endpoints".
     Use for performance engineering and capacity planning.
   ```
4. **Build Python tools** -- standard library only, argparse CLI, `--json` flag, module docstring, error handling.
5. **Verify** -- Confirm the skill triggers on expected prompts and tools run without errors.

## Workflow 3: Create a Subagent

1. **Define scope** -- One narrow responsibility per agent.
2. **Create agent YAML** at `.claude/agents/agent-name.yaml`:
   ```yaml
   name: security-reviewer
   description: Reviews code for security vulnerabilities
   model: claude-sonnet-4-20250514
   allowed-tools:
     - Read
     - Glob
     - Grep
     - Bash(git diff*)
   custom-instructions: |
     For every change:
     1. Check for hardcoded secrets
     2. Identify injection vulnerabilities
     3. Verify auth patterns
     4. Flag insecure dependencies
     Output a structured report with severity levels.
   ```
3. **Set tool access** -- read-only (`Read, Glob, Grep`), read+commands (`+ Bash(npm test*)`), or write-capable (`+ Edit, Write`).
4. **Invoke** -- `/agents/security-reviewer Review the last 3 commits`
5. **Validate** -- Confirm the agent stays within scope and produces structured output.

## Workflow 4: Configure Hooks

Hooks run custom scripts at lifecycle events without user approval.

| Hook | Fires When | Blocking |
|------|-----------|----------|
| `PreToolUse` | Before tool executes | Yes (exit 1 blocks) |
| `PostToolUse` | After tool completes | No |
| `Notification` | Claude sends notification | No |
| `Stop` | Claude finishes turn | No |

1. **Add hook config** to `.claude/settings.json`:
   ```json
   {
     "hooks": {
       "PostToolUse": [
         {
           "matcher": "Edit|Write",
           "hooks": [{ "type": "command", "command": "prettier --write \"$CLAUDE_FILE_PATH\" 2>/dev/null || true" }]
         }
       ],
       "PreToolUse": [
         {
           "matcher": "Bash",
           "hooks": [{ "type": "command", "command": "bash .claude/hooks/validate.sh" }]
         }
       ]
     }
   }
   ```
2. **Test** -- Trigger the relevant tool and confirm the hook fires.
3. **Iterate** -- Add matchers for additional tools as needed.

## Workflow 5: Manage Context Budget

1. **Audit** -- `python scripts/context_analyzer.py /path/to/project`
2. **Apply budget targets:**
   | Category | Budget | Purpose |
   |----------|--------|---------|
   | System prompt + CLAUDE.md | 5-10% | Project configuration |
   | Skill definitions | 5-15% | Active skill content |
   | Source code (read files) | 30-50% | Files Claude reads |
   | Conversation history | 20-30% | Messages and responses |
   | Working memory | 10-20% | Reasoning space |
3. **Reduce overhead** -- Keep root CLAUDE.md under 4000 tokens. Use hierarchical loading. Avoid reading entire large files. Use `/compact` after completing subtasks.
4. **Validate** -- Re-run context analyzer and confirm overhead dropped.

---

## Quick Reference

### Slash Commands

| Command | Description |
|---------|-------------|
| `/compact` | Summarize conversation to free context |
| `/clear` | Clear conversation history |
| `/model` | Switch model mid-session |
| `/agents` | List and invoke custom agents |
| `/permissions` | View and modify tool permissions |
| `/cost` | Show token usage and cost |
| `/doctor` | Diagnose configuration issues |
| `/init` | Generate CLAUDE.md for current project |

### Permission Modes

| Mode | Behavior | Best For |
|------|----------|----------|
| Default | Asks permission for writes | Normal development |
| Allowlist | Auto-approves listed tools | Repetitive workflows |
| Yolo | Auto-approves everything | Trusted automation |

```json
{ "permissions": { "allow": ["Read", "Glob", "Grep", "Bash(npm test*)"],
                    "deny": ["Bash(rm -rf*)", "Bash(git push*)"] } }
```

### CLAUDE.md Loading Order

1. `~/.claude/CLAUDE.md` -- user global, always loaded
2. `/project/CLAUDE.md` -- project root, always loaded
3. `/project/.claude/CLAUDE.md` -- project config, always loaded
4. `/project/subdir/CLAUDE.md` -- subdirectory, loaded when files accessed

### MCP Servers

| Server | Purpose |
|--------|---------|
| `server-filesystem` | File access beyond project |
| `server-github` | GitHub API (issues, PRs) |
| `server-postgres` | Database queries |
| `server-memory` | Persistent key-value store |
| `server-brave-search` | Web search |
| `server-puppeteer` | Browser automation |

---

## Reference Documentation

| Document | Path |
|----------|------|
| Skill Authoring Guide | [references/skill-authoring-guide.md](references/skill-authoring-guide.md) |
| Subagent Patterns | [references/subagent-patterns.md](references/subagent-patterns.md) |
| Hooks Cookbook | [references/hooks-cookbook.md](references/hooks-cookbook.md) |
| Skill Template | [assets/skill-template.md](assets/skill-template.md) |
| Agent Template | [assets/agent-template.md](assets/agent-template.md) |
