---
name: claude-code-mastery
description: >-
  This skill should be used when the user asks to "optimize CLAUDE.md",
  "create a new skill", "write a custom agent", "configure hooks",
  "manage context window", "set up MCP servers", "scaffold a skill package",
  "analyze token budget", "create subagents", "configure permissions",
  "set up worktrees", or "integrate Claude Code with editors".
  Use for Claude Code CLI mastery, skill authoring, context engineering,
  hooks automation, subagent creation, and development workflow optimization.
license: MIT
metadata:
  version: 1.0.0
  category: engineering
  domain: development-tools
---

# Claude Code Mastery

Expert-level skill for mastering Claude Code CLI -- from CLAUDE.md optimization and
skill authoring to subagent creation, hooks automation, and context engineering.

## Keywords

claude-code, claude-cli, CLAUDE.md, skill-authoring, subagents, hooks,
context-window, token-budget, MCP-servers, worktrees, permission-modes,
prompt-engineering, context-engineering, progressive-disclosure, slash-commands

---

## Table of Contents

- [Quick Start](#quick-start)
- [Tools Overview](#tools-overview)
- [Core Workflows](#core-workflows)
- [Advanced Techniques](#advanced-techniques)
- [Best Practices](#best-practices)
- [Editor and Agent Integration](#editor-and-agent-integration)
- [Reference Documentation](#reference-documentation)
- [Quick Reference Tables](#quick-reference-tables)

---

## Quick Start

```bash
# Scaffold a new skill package with proper structure
python scripts/skill_scaffolder.py my-new-skill --domain engineering --description "Brief description"

# Analyze and optimize an existing CLAUDE.md
python scripts/claudemd_optimizer.py path/to/CLAUDE.md

# Estimate context window usage across a project
python scripts/context_analyzer.py /path/to/project

# All tools support JSON output
python scripts/claudemd_optimizer.py CLAUDE.md --json
python scripts/context_analyzer.py . --json --max-depth 3
```

---

## Tools Overview

### 1. Skill Scaffolder

Generates a complete skill directory with SKILL.md template, scripts/, references/,
assets/ directories, and properly formatted YAML frontmatter.

```bash
python scripts/skill_scaffolder.py my-skill --domain engineering --description "Does X"
python scripts/skill_scaffolder.py my-skill -d marketing --description "Campaign tools" --json
python scripts/skill_scaffolder.py my-skill -d product --description "User research" -o /path/
```

| Parameter | Description |
|-----------|-------------|
| `skill_name` | Name for the skill (kebab-case recommended) |
| `--domain, -d` | Domain category (engineering, marketing, product, etc.) |
| `--description` | Brief description for YAML frontmatter |
| `--version` | Semantic version (default: 1.0.0) |
| `--license` | License type (default: MIT) |
| `--category` | Skill category for metadata |
| `--output, -o` | Parent directory for skill folder |
| `--json` | Output results as JSON |

### 2. CLAUDE.md Optimizer

Analyzes a CLAUDE.md file and produces actionable optimization recommendations.

```bash
python scripts/claudemd_optimizer.py CLAUDE.md
python scripts/claudemd_optimizer.py CLAUDE.md --token-limit 4000 --json
```

| Parameter | Description |
|-----------|-------------|
| `file_path` | Path to the CLAUDE.md file to analyze |
| `--token-limit` | Maximum recommended token count (default: 6000) |
| `--json` | Output results as JSON |

**Report includes:** line count, token estimate, section completeness, redundancy
detection, missing sections, hierarchical loading suggestions, scored recommendations.

### 3. Context Analyzer

Scans a project to estimate context window consumption by file category.

```bash
python scripts/context_analyzer.py .
python scripts/context_analyzer.py /path/to/project --max-depth 4 --json
python scripts/context_analyzer.py . --context-window 200000
```

| Parameter | Description |
|-----------|-------------|
| `project_path` | Path to the project directory |
| `--max-depth` | Maximum directory traversal depth (default: 5) |
| `--context-window` | Total context window size in tokens (default: 200000) |
| `--json` | Output results as JSON |

**Report includes:** token estimates per category, percentage of context consumed,
largest files, budget breakdown, reduction recommendations.

---

## Core Workflows

### Workflow 1: CLAUDE.md Optimization

**Step 1: Audit** -- `python scripts/claudemd_optimizer.py CLAUDE.md`

**Step 2: Follow the recommended structure:**

```markdown
# CLAUDE.md
## Project Purpose         -- What the project is, who it serves
## Architecture Overview   -- Directory structure, key patterns
## Development Environment -- Build commands, test commands, setup
## Key Principles          -- 3-7 non-obvious rules Claude must follow
## Anti-Patterns to Avoid  -- Things that look reasonable but are wrong
## Git Workflow            -- Branch strategy, commit conventions
```

**Step 3: Apply token-saving patterns:**
- Bullet points over paragraphs (30% fewer tokens)
- Code blocks for commands (prevents misinterpretation)
- Remove generic advice Claude already knows
- Move domain details to child CLAUDE.md files

**Step 4: Set up hierarchical loading:**

```
project/
├── CLAUDE.md              # Global: purpose, architecture, principles
├── frontend/CLAUDE.md     # Frontend-specific: React patterns, styling
├── backend/CLAUDE.md      # Backend-specific: API patterns, DB conventions
└── .claude/CLAUDE.md      # User-specific overrides (gitignored)
```

**Step 5: Validate** -- `python scripts/claudemd_optimizer.py CLAUDE.md --token-limit 4000`

### Workflow 2: Skill Authoring

**Step 1: Scaffold** -- `python scripts/skill_scaffolder.py my-skill -d engineering --description "..."`

**Step 2: Write the SKILL.md** following this order:
1. YAML frontmatter (name, description with trigger phrases, license, metadata)
2. Title and one-line summary
3. Table of contents
4. Quick Start (3-5 copy-pasteable commands)
5. Tools Overview (each script with usage, parameters table)
6. Workflows (step-by-step sequences combining tools and knowledge)
7. Reference Documentation (links to references/)
8. Quick Reference (tables, cheat sheets)

**Step 3: Optimize the description for auto-discovery:**

```yaml
description: >-
  This skill should be used when the user asks to "analyze performance",
  "optimize queries", "profile memory", or "benchmark endpoints".
  Use for performance engineering and capacity planning.
```

**Step 4: Build Python tools** -- standard library only, argparse, --json flag,
module docstring, error handling. See [references/skill-authoring-guide.md](references/skill-authoring-guide.md).

### Workflow 3: Subagent Creation

**Step 1:** Define a narrow scope (one thing done well).

**Step 2:** Create `.claude/agents/agent-name.yaml`:

```yaml
---
name: security-reviewer
description: Reviews code for security vulnerabilities and compliance
model: claude-sonnet-4-20250514
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash(git diff*)
custom-instructions: |
  You are a security-focused code reviewer. For every change:
  1. Check for hardcoded secrets
  2. Identify injection vulnerabilities
  3. Verify auth patterns
  4. Flag insecure dependencies
  Output a structured report with severity levels.
---
```

**Step 3: Configure tool access** -- read-only (`Read, Glob, Grep`), read+commands
(`+ Bash(npm test*)`), or write-capable (`+ Edit, Write`).

**Step 4: Invoke** -- `/agents/security-reviewer Review the last 3 commits`

See [references/subagent-patterns.md](references/subagent-patterns.md) for delegation
patterns, memory persistence, and production recipes.

### Workflow 4: Hooks Setup

Hooks run custom scripts at lifecycle events without user approval.

| Hook | Fires When | Blocking |
|------|-----------|----------|
| `PreToolUse` | Before tool executes | Yes (exit 1 blocks) |
| `PostToolUse` | After tool completes | No |
| `Notification` | Claude sends notification | No |
| `Stop` | Claude finishes turn | No |
| `SessionStart` | Session/compact begins | No |

**Configure in `.claude/settings.json`:**

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

See [references/hooks-cookbook.md](references/hooks-cookbook.md) for 25+ ready-to-use recipes.

### Workflow 5: Context Management

**Step 1: Audit** -- `python scripts/context_analyzer.py /path/to/project`

**Step 2: Apply the context budget framework:**

| Category | Budget | Purpose |
|----------|--------|---------|
| System prompt + CLAUDE.md | 5-10% | Project configuration |
| Skill definitions | 5-15% | Active skill content |
| Source code (read files) | 30-50% | Files Claude reads |
| Conversation history | 20-30% | Messages and responses |
| Working memory | 10-20% | Reasoning space |

**Step 3: Reduce overhead:**
- Keep root CLAUDE.md under 4000 tokens
- Use hierarchical loading (child CLAUDE.md files load on demand)
- Avoid reading entire large files -- use line ranges
- Use `/compact` proactively after completing subtasks
- Start new sessions for unrelated tasks

### Workflow 6: Prompt Engineering for Claude Code

**Be specific about scope:**
```
# Weak: Fix the bug in the login flow
# Strong: Fix the auth bug in src/auth/login.ts where expired refresh tokens
# cause a 500 error. Catch TokenExpiredError in the try/catch on line 45.
```

**Specify output format:**
```
Create .claude/settings.json with hooks that:
1. Auto-format TypeScript with prettier after Edit/Write
2. Block Bash commands containing "rm -rf"
3. Log all tool uses to /tmp/claude-session.log
```

**Use checkpoints for multi-step work:**
```
Implement the dashboard. After each step, wait for confirmation:
1. Create route at src/app/dashboard/page.tsx
2. Build DashboardLayout component
3. Add API endpoint at src/app/api/dashboard/route.ts
4. Write tests in __tests__/dashboard.test.tsx
```

**Leverage Claude Code's strengths:** point it at existing code, ask it to follow
established patterns, give it test cases, let it search before changing.

---

## Advanced Techniques

### Worktrees for Parallel Work

```
/worktree feature/new-api    # Creates isolated working copy
```

Useful for exploring alternatives, parallel tasks, and risky refactors.

```bash
git worktree add .claude/worktrees/feature-api feature/new-api
git worktree list
git worktree remove .claude/worktrees/feature-api
```

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

### MCP Server Integration

Configure in `.claude/settings.json` under `mcpServers`:

| Server | Purpose |
|--------|---------|
| `server-filesystem` | File access beyond project |
| `server-github` | GitHub API (issues, PRs) |
| `server-postgres` | Database queries |
| `server-memory` | Persistent key-value store |
| `server-brave-search` | Web search |
| `server-puppeteer` | Browser automation |

### Memory and Session Management

- **CLAUDE.md** -- Project-level memory, loads every session
- **Session handoff** -- Ask Claude to write `.claude/session-notes.md`
- **MCP memory server** -- Structured persistent memory across sessions
- **`/compact`** -- Summarize conversation to free context

---

## Best Practices

### Progressive Disclosure

1. **Root CLAUDE.md** -- Project-wide rules only (under 200 lines)
2. **Domain CLAUDE.md files** -- `frontend/CLAUDE.md`, `backend/CLAUDE.md`
3. **Skill files** -- Loaded when relevant skills trigger
4. **Reference files** -- Deep knowledge loaded on explicit request

**Rule:** If Claude does not need it for every task, move it out of root CLAUDE.md.

### Token Budget Management

- 1 token is approximately 3.5 characters for Claude models
- A 200-line CLAUDE.md is roughly 2000-3000 tokens

```
200K context window:
├── System prompt:     ~3K tokens (fixed)
├── CLAUDE.md tree:    ~5K tokens (target)
├── Active skills:     ~10K tokens (on demand)
├── Source files:      ~80K tokens (the work)
├── Conversation:      ~70K tokens (grows)
└── Headroom:          ~32K tokens (reasoning)
```

### Context Engineering

**Include:** non-obvious conventions, technology versions, test/deploy commands,
architecture decisions and rationale.

**Exclude:** generic programming advice, language syntax Claude knows, verbose
paragraphs replaceable by bullets, historical information irrelevant to current work.

**Test:** Ask Claude to do a common task. If it makes preventable mistakes, update
CLAUDE.md. If it succeeds without reading a section, that section may be unnecessary.

---

## Editor and Agent Integration

### Claude Code with VS Code / Cursor

- VS Code: Claude Code in terminal + Copilot for inline completions
- Cursor: Cursor Tab/Cmd+K for inline edits, Claude Code for multi-file work
- Exclude `.claude/` from VS Code search: `"search.exclude": {".claude": true}`

### Claude Code vs Codex CLI

| Feature | Claude Code | Codex CLI |
|---------|-------------|-----------|
| Context awareness | CLAUDE.md hierarchy | Single prompt |
| Tool ecosystem | MCP servers | Function calling |
| Permission model | Granular allowlists | Sandbox only |
| Session memory | Conversation + compact | Stateless |
| Subagents | Built-in agent system | Not available |

### Programmatic Invocation

```bash
echo "Explain this project" | claude --print
claude --print "Run tests and summarize failures"
claude --model claude-sonnet-4-20250514 --print "Quick review of last commit"
```

---

## Reference Documentation

| Document | Path | Description |
|----------|------|-------------|
| Skill Authoring Guide | [references/skill-authoring-guide.md](references/skill-authoring-guide.md) | Complete skill writing reference |
| Subagent Patterns | [references/subagent-patterns.md](references/subagent-patterns.md) | Agent creation, delegation, recipes |
| Hooks Cookbook | [references/hooks-cookbook.md](references/hooks-cookbook.md) | 25+ practical hook recipes |

## Templates

| Template | Path | Description |
|----------|------|-------------|
| Skill Template | [assets/skill-template.md](assets/skill-template.md) | Ready-to-use SKILL.md template |
| Agent Template | [assets/agent-template.md](assets/agent-template.md) | Ready-to-use subagent definition |

---

## Quick Reference Tables

### Slash Commands

| Command | Description |
|---------|-------------|
| `/help` | Show available commands |
| `/compact` | Summarize conversation to free context |
| `/clear` | Clear conversation history |
| `/model` | Switch model mid-session |
| `/agents` | List and invoke custom agents |
| `/permissions` | View and modify tool permissions |
| `/config` | Open settings |
| `/cost` | Show token usage and cost |
| `/doctor` | Diagnose configuration issues |
| `/init` | Generate CLAUDE.md for current project |

### CLAUDE.md Loading Order

1. `~/.claude/CLAUDE.md` -- user global, always loaded
2. `/project/CLAUDE.md` -- project root, always loaded
3. `/project/.claude/CLAUDE.md` -- project config, always loaded
4. `/project/subdir/CLAUDE.md` -- subdirectory, loaded when files accessed

### Settings.json Structure

```json
{
  "permissions": { "allow": ["Tool(pattern*)"], "deny": ["Tool(pattern*)"] },
  "hooks": {
    "PreToolUse": [{ "matcher": "regex", "hooks": [{ "type": "command", "command": "script" }] }],
    "PostToolUse": [{ "matcher": "regex", "hooks": [{ "type": "command", "command": "script" }] }]
  },
  "mcpServers": { "name": { "command": "cmd", "args": [], "env": {} } }
}
```

---

**Last Updated:** February 2026
**Version:** 1.0.0
**Tools:** 3 Python CLI tools
**References:** 3 deep-dive guides
**Templates:** 2 ready-to-use templates
