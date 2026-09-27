# Claude Code Quick Reference

Read this for the at-a-glance tables (slash commands, permission modes, CLAUDE.md loading order, MCP servers), plus troubleshooting and success criteria.

## Slash Commands

| Command | Description |
|---------|-------------|
| `/compact` | Summarize conversation to free context |
| `/clear` | Clear conversation history |
| `/model` | Switch model mid-session |
| `/agents` | Since v2.1.198 prints a reminder; create subagents by editing `.claude/agents/<name>.md` or asking Claude |
| `/permissions` | View and modify tool permissions |
| `/cost` | Show token usage and cost |
| `/doctor` | Diagnose configuration issues |
| `/init` | Generate CLAUDE.md for current project |

## Permission Modes

| Mode | Behavior | Best For |
|------|----------|----------|
| Default | Asks permission for writes | Normal development |
| Allowlist | Auto-approves listed tools | Repetitive workflows |
| Yolo | Auto-approves everything | Trusted automation |

```json
{ "permissions": { "allow": ["Read", "Glob", "Grep", "Bash(npm test*)"],
                    "deny": ["Bash(rm -rf*)", "Bash(git push*)"] } }
```

## CLAUDE.md Loading Order

1. `~/.claude/CLAUDE.md` -- user global, always loaded
2. `/project/CLAUDE.md` -- project root, always loaded
3. `/project/.claude/CLAUDE.md` -- project config, always loaded
4. `/project/subdir/CLAUDE.md` -- subdirectory, loaded when files accessed

## MCP Servers

| Server | Purpose |
|--------|---------|
| `server-filesystem` | File access beyond project |
| `server-github` | GitHub API (issues, PRs) |
| `server-postgres` | Database queries |
| `server-memory` | Persistent key-value store |
| `server-brave-search` | Web search |
| `server-puppeteer` | Browser automation |

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| CLAUDE.md changes not picked up | Claude loads CLAUDE.md at session start | Start a new conversation or use `/clear` to reload configuration |
| Skill not triggering on expected prompts | Description field in YAML frontmatter missing trigger phrases | Add quoted user phrases to the `description` field (e.g., `"optimize queries"`, `"profile memory"`) |
| Context window exhausted mid-task | Root CLAUDE.md too large or too many files read | Run `context_analyzer.py` to audit token usage, then move domain content to child CLAUDE.md files |
| Hook not firing after tool use | Matcher in `.claude/settings.json` does not match the tool name | Verify the `matcher` regex matches the exact tool name (e.g., `Edit\|Write`, not `edit\|write`) |
| Subagent exceeds scope and edits unrelated files | `tools` is missing (inherits every tool), too permissive, or written as `allowed-tools` (ignored for agents) | Set `tools: Read, Glob, Grep` and add write tools only when necessary |
| Scaffolder fails with "Directory already exists" | Target skill directory already present on disk | Remove or rename the existing directory, or choose a different skill name |
| Optimizer reports low score despite good structure | Token count exceeds the default 6000 limit | Pass `--token-limit` matching your actual budget (e.g., `--token-limit 10000`) |

## Success Criteria

- CLAUDE.md optimizer score of 80+ on all project CLAUDE.md files
- Root CLAUDE.md stays under 4000 tokens (verified by `claudemd_optimizer.py --token-limit 4000`)
- Auto-loaded configuration (all CLAUDE.md files combined) consumes less than 10% of the context window
- Every new skill scaffolded passes the optimizer with zero "critical" missing sections
- Subagents stay within their declared `tools` scope during testing
- Hooks execute in under 500ms to avoid perceptible delay on tool use
- Context analyzer shows 50%+ of the context window available for source code and reasoning
