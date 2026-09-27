# Claude Code Mastery Workflows

Read this for the step-by-step playbooks: optimizing a CLAUDE.md, authoring a new skill, creating a subagent, configuring hooks, and managing the context budget.

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
2. **Create the agent file** at `.claude/agents/agent-name.md` (YAML frontmatter + markdown body as the system prompt):
   ```markdown
   ---
   name: security-reviewer
   description: Reviews code for security vulnerabilities. Use proactively after code changes.
   tools: Read, Glob, Grep, Bash
   model: sonnet
   ---

   You are a security reviewer. Use Bash only for read-only git commands.
   For every change:
   1. Check for hardcoded secrets
   2. Identify injection vulnerabilities
   3. Verify auth patterns
   4. Flag insecure dependencies
   Output a structured report with severity levels.
   ```
   The body after the closing `---` is the system prompt. `allowed-tools` and `custom-instructions` are not agent keys and are silently ignored.
3. **Set tool access** -- `tools` takes tool names only: read-only (`Read, Glob, Grep`), read+commands (`+ Bash`), or write-capable (`+ Edit, Write`). Omit `tools` to inherit everything. To limit which commands Bash may run, use `permissions.deny` rules in `.claude/settings.json`; `Bash(npm test *)` in `tools` does not narrow Bash.
4. **Invoke** -- "Use the security-reviewer subagent to review the last 3 commits", or `@"security-reviewer (agent)"` from the `@` typeahead. Claude also delegates on its own when a request matches the `description`.
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
