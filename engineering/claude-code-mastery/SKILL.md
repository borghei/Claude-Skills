---
name: claude-code-mastery
description: 
license: MIT
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: development-tools
  updated: 2026-03-31
  tags: [claude-code, skill-authoring, subagents, hooks]
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

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| CLAUDE.md changes not picked up | Claude loads CLAUDE.md at session start | Start a new conversation or use `/clear` to reload configuration |
| Skill not triggering on expected prompts | Description field in YAML frontmatter missing trigger phrases | Add quoted user phrases to the `description` field (e.g., `"optimize queries"`, `"profile memory"`) |
| Context window exhausted mid-task | Root CLAUDE.md too large or too many files read | Run `context_analyzer.py` to audit token usage, then move domain content to child CLAUDE.md files |
| Hook not firing after tool use | Matcher in `.claude/settings.json` does not match the tool name | Verify the `matcher` regex matches the exact tool name (e.g., `Edit\|Write`, not `edit\|write`) |
| Subagent exceeds scope and edits unrelated files | `allowed-tools` list is too permissive | Restrict to read-only tools (`Read, Glob, Grep`) and add write tools only when necessary |
| Scaffolder fails with "Directory already exists" | Target skill directory already present on disk | Remove or rename the existing directory, or choose a different skill name |
| Optimizer reports low score despite good structure | Token count exceeds the default 6000 limit | Pass `--token-limit` matching your actual budget (e.g., `--token-limit 10000`) |

## Success Criteria

- CLAUDE.md optimizer score of 80+ on all project CLAUDE.md files
- Root CLAUDE.md stays under 4000 tokens (verified by `claudemd_optimizer.py --token-limit 4000`)
- Auto-loaded configuration (all CLAUDE.md files combined) consumes less than 10% of the context window
- Every new skill scaffolded passes the optimizer with zero "critical" missing sections
- Subagents stay within their declared `allowed-tools` scope during testing
- Hooks execute in under 500ms to avoid perceptible delay on tool use
- Context analyzer shows 50%+ of the context window available for source code and reasoning

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

## Tool Reference

### 1. Skill Scaffolder (`scripts/skill_scaffolder.py`)

**Purpose:** Generate a complete skill package directory with SKILL.md template, starter Python script, reference document, and proper YAML frontmatter.

**Usage:**

```bash
python scripts/skill_scaffolder.py <skill_name> [options]
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `skill_name` | positional | Yes | -- | Name for the skill in kebab-case (e.g., `my-new-skill`) |
| `--domain, -d` | string | No | `engineering` | Domain category. Options: `engineering`, `marketing`, `product`, `project-management`, `c-level`, `ra-qm`, `business-growth`, `finance`, `standards`, `development-tools` |
| `--description` | string | No | auto-generated | Brief description for YAML frontmatter, optimized for auto-discovery |
| `--version` | string | No | `1.0.0` | Semantic version for metadata |
| `--license` | string | No | `MIT` | License type for frontmatter |
| `--category` | string | No | same as domain | Skill category for metadata |
| `--output, -o` | string | No | `.` (current dir) | Parent directory for the skill folder |
| `--json` | flag | No | off | Output results in JSON format |

**Example:**

```bash
python scripts/skill_scaffolder.py api-analyzer -d engineering --description "API analysis and optimization" --json
```

**Output Formats:**

- **Human-readable (default):** Prints skill name, domain, version, location, directory tree, and next-steps checklist.
- **JSON (`--json`):** Returns `{ success, path, name, domain, version, directories_created, files_created }`.

---

### 2. CLAUDE.md Optimizer (`scripts/claudemd_optimizer.py`)

**Purpose:** Analyze a CLAUDE.md file for structure completeness, token efficiency, redundancy, and verbosity. Produces a scored report with prioritized optimization recommendations.

**Usage:**

```bash
python scripts/claudemd_optimizer.py <file_path> [options]
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file_path` | positional | Yes | -- | Path to the CLAUDE.md file to analyze |
| `--token-limit` | integer | No | `6000` | Maximum recommended token count for the file |
| `--json` | flag | No | off | Output results in JSON format |

**Example:**

```bash
python scripts/claudemd_optimizer.py path/to/CLAUDE.md --token-limit 4000
```

**Output Formats:**

- **Human-readable (default):** Displays score (0-100), file metrics (lines, words, tokens), section breakdown with per-section token estimates, section completeness checklist (critical/high/medium), redundancy issues, and prioritized recommendations (HIGH/MEDIUM/LOW).
- **JSON (`--json`):** Returns `{ success, file, metrics, sections, completeness, redundancies, recommendations, score }`.

---

### 3. Context Analyzer (`scripts/context_analyzer.py`)

**Purpose:** Scan a project directory to estimate how much of Claude Code's context window is consumed by CLAUDE.md files, skill definitions, source code, and configuration. Produces a token budget breakdown with reduction recommendations.

**Usage:**

```bash
python scripts/context_analyzer.py <project_path> [options]
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `project_path` | positional | Yes | -- | Path to the project directory to analyze |
| `--max-depth` | integer | No | `5` | Maximum directory traversal depth |
| `--context-window` | integer | No | `200000` | Total context window size in tokens |
| `--json` | flag | No | off | Output results in JSON format |

**Example:**

```bash
python scripts/context_analyzer.py /path/to/project --max-depth 3 --context-window 200000 --json
```

**Output Formats:**

- **Human-readable (default):** Displays project summary (files scanned, total tokens, auto-loaded tokens), context budget breakdown with visual bar chart, per-category breakdown (Claude Configuration, Skill Definitions, Reference Documents, Source Code, Config & Build, Documentation) with largest files listed, top 20 largest files, and prioritized recommendations.
- **JSON (`--json`):** Returns `{ success, project_path, context_window, summary, categories, budget, largest_files, recommendations }`.
