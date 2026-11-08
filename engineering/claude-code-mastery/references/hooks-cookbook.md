# Hooks Cookbook

Practical hook recipes for automating code quality, security enforcement, workflow
optimization, and developer experience with Claude Code.

---

## Table of Contents

- [Hook Architecture](#hook-architecture)
- [Lifecycle Events](#lifecycle-events)
- [Hook Types](#hook-types)
- [Environment Variables](#environment-variables)
- [Recipes: Code Quality](#recipes-code-quality)
- [Recipes: Security](#recipes-security)
- [Recipes: Workflow](#recipes-workflow)
- [Recipes: Notifications](#recipes-notifications)
- [Recipes: Context Management](#recipes-context-management)
- [Recipes: Logging and Audit](#recipes-logging-and-audit)
- [Recipes: Advanced Patterns](#recipes-advanced-patterns)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Hook Architecture

Hooks are configured in `.claude/settings.json` (project-level, committed) or
`~/.claude/settings.json` (user-level, global). Project-level hooks apply to
everyone working on the project. User-level hooks apply to all projects.

```json
{
  "hooks": {
    "EventName": [
      {
        "matcher": "ToolNameRegex",
        "hooks": [
          {
            "type": "command",
            "command": "your-shell-command"
          }
        ]
      }
    ]
  }
}
```

---

## Lifecycle Events

| Event | Fires When | Blocking | Use For |
|-------|-----------|----------|---------|
| `PreToolUse` | Before a tool executes | Yes (exit 2 blocks) | Validation, protection |
| `PostToolUse` | After a tool completes | No | Formatting, logging |
| `Notification` | Claude sends a notification | No | Desktop alerts |
| `Stop` | Claude finishes a response | No | Session logging, cleanup |
| `SessionStart` | Session begins or compact occurs | No | Context injection |
| `SubagentStart` | A subagent is launched | No | Setup, logging |
| `SubagentStop` | A subagent finishes | No | Cleanup, logging |

**Blocking behavior:** Only `PreToolUse` hooks can prevent an action. If the
hook script exits with code 2, the tool call is blocked and stderr is shown to the model; exit 1
is a non-blocking error and the call goes ahead. All other events are
informational -- the hook runs but cannot stop the action.

---

## Hook Input: JSON on stdin

Tool arguments are not in environment variables. Each event arrives as JSON on stdin with
`session_id`, `transcript_path`, `cwd`, `permission_mode`, `hook_event_name`, `tool_name` and
`tool_input` (`.file_path` for Write/Edit, `.command` for Bash); the only documented env var is
`CLAUDE_PROJECT_DIR`. Every example below reads stdin once (`IN=$(cat)`) and pulls fields with
`jq`. In a script under `.claude/hooks/`:

```bash
#!/bin/bash
IN=$(cat)                                              # read the event once
TOOL=$(jq -r '.tool_name // empty' <<<"$IN")
F=$(jq -r '.tool_input.file_path // empty' <<<"$IN")   # Write / Edit
CMD=$(jq -r '.tool_input.command // empty' <<<"$IN")   # Bash
SID=$(jq -r '.session_id // empty' <<<"$IN")
```

An unset variable makes a guard silently allow everything: test each blocking hook once.

## Hook Types

### Command Hooks

Run a shell command. Fast, deterministic, no LLM cost.

```json
{
  "type": "command",
  "command": "IN=$(cat); F=$(jq -r '.tool_input.file_path // empty' <<<\"$IN\"); prettier --write \"$F\" 2>/dev/null || true"
}
```

### Prompt Hooks

Send a single-turn prompt to a fast model (Haiku by default). Useful for
content evaluation that requires judgment.

```json
{
  "type": "prompt",
  "prompt": "Check if this change introduces security issues. Output WARNING if yes, nothing if no.",
  "model": "haiku"
}
```

### Agent Hooks

Launch a multi-turn agent with tool access. Most powerful but slowest and
most expensive. Use sparingly.

```json
{
  "type": "agent",
  "prompt": "Review the changed file for security vulnerabilities and report findings.",
  "model": "sonnet",
  "tools": ["Read", "Grep"]
}
```

## Recipes: Code Quality

### Recipe 1: Auto-Format Python with Black

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "IN=$(cat); F=$(jq -r '.tool_input.file_path // empty' <<<\"$IN\"); if [[ \"$F\" == *.py ]]; then python3 -m black --quiet \"$F\" 2>/dev/null; fi"
          }
        ]
      }
    ]
  }
}
```

### Recipe 2: Auto-Format JavaScript/TypeScript with Prettier

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "IN=$(cat); F=$(jq -r '.tool_input.file_path // empty' <<<\"$IN\"); if [[ \"$F\" =~ \\.(js|jsx|ts|tsx|css|json|md)$ ]]; then npx prettier --write \"$F\" 2>/dev/null || true; fi"
          }
        ]
      }
    ]
  }
}
```

### Recipe 3: Run ESLint Auto-Fix

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "IN=$(cat); F=$(jq -r '.tool_input.file_path // empty' <<<\"$IN\"); if [[ \"$F\" =~ \\.(ts|tsx|js|jsx)$ ]]; then npx eslint --fix \"$F\" 2>/dev/null || true; fi"
          }
        ]
      }
    ]
  }
}
```

### Recipe 4: Type-Check After TypeScript Edits

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "IN=$(cat); F=$(jq -r '.tool_input.file_path // empty' <<<\"$IN\"); if [[ \"$F\" =~ \\.tsx?$ ]]; then npx tsc --noEmit --pretty 2>&1 | head -20 || true; fi"
          }
        ]
      }
    ]
  }
}
```

### Recipe 5: Run Ruff Linter on Python Files

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "IN=$(cat); F=$(jq -r '.tool_input.file_path // empty' <<<\"$IN\"); if [[ \"$F\" == *.py ]]; then ruff check --fix \"$F\" 2>/dev/null && ruff format \"$F\" 2>/dev/null; fi"
          }
        ]
      }
    ]
  }
}
```

### Recipe 6: Validate JSON After Edits

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "IN=$(cat); F=$(jq -r '.tool_input.file_path // empty' <<<\"$IN\"); if [[ \"$F\" == *.json ]]; then python3 -c \"import json; json.load(open('$F'))\" 2>&1 || echo 'WARNING: Invalid JSON in $F' >&2; fi"
          }
        ]
      }
    ]
  }
}
```

---

## Recipes: Security

### Recipe 7: Protect Sensitive Files

Block modifications to files containing secrets or credentials.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "IN=$(cat); F=$(jq -r '.tool_input.file_path // empty' <<<\"$IN\"); if echo \"$F\" | grep -qiE '(\\.env$|\\.env\\.|credentials|secrets?|private.key|id_rsa)'; then echo 'BLOCKED: Cannot modify sensitive files' >&2; exit 2; fi"
          }
        ]
      }
    ]
  }
}
```

### Recipe 8: Block Dangerous Bash Commands

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "IN=$(cat); CMD=$(jq -r '.tool_input.command // empty' <<<\"$IN\"); if echo \"$CMD\" | grep -qE '(rm -rf /|rm -rf \\*|DROP TABLE|DROP DATABASE|--force push|git push.*(--force|-f)|> /dev/sd|mkfs\\.|dd if=)'; then echo 'BLOCKED: Potentially destructive command' >&2; exit 2; fi"
          }
        ]
      }
    ]
  }
}
```

### Recipe 9: Block Production Environment Access

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "IN=$(cat); CMD=$(jq -r '.tool_input.command // empty' <<<\"$IN\"); if echo \"$CMD\" | grep -qiE '(production|prod\\.|prod-|PROD_|--prod)'; then echo 'BLOCKED: Production commands not allowed in development' >&2; exit 2; fi"
          }
        ]
      }
    ]
  }
}
```

### Recipe 10: Prevent Editing Generated/Vendored Files

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "IN=$(cat); F=$(jq -r '.tool_input.file_path // empty' <<<\"$IN\"); if echo \"$F\" | grep -qE '(generated|dist/|build/|\\.min\\.|vendor/|node_modules/)'; then echo 'BLOCKED: Cannot edit generated or vendored files' >&2; exit 2; fi"
          }
        ]
      }
    ]
  }
}
```

### Recipe 11: AI-Powered Security Review (Prompt Hook)

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Check if this file change introduces security vulnerabilities (injection, XSS, hardcoded secrets, insecure crypto). If yes, output a brief WARNING with the issue. If clean, output nothing.",
            "model": "haiku"
          }
        ]
      }
    ]
  }
}
```

---

## Recipes: Workflow

### Recipe 12: Enforce Conventional Commits

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "IN=$(cat); CMD=$(jq -r '.tool_input.command // empty' <<<\"$IN\"); if echo \"$CMD\" | grep -q 'git commit'; then if ! echo \"$CMD\" | grep -qE '(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\\(|:)'; then echo 'BLOCKED: Commit must use conventional commits (feat|fix|docs|...)' >&2; exit 2; fi; fi"
          }
        ]
      }
    ]
  }
}
```

### Recipe 13: Auto-Stage Written Files

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "IN=$(cat); F=$(jq -r '.tool_input.file_path // empty' <<<\"$IN\"); git add \"$F\" 2>/dev/null || true"
          }
        ]
      }
    ]
  }
}
```

### Recipe 14: Remind About Barrel Exports

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "IN=$(cat); F=$(jq -r '.tool_input.file_path // empty' <<<\"$IN\"); if [[ \"$F\" =~ \\.(ts|tsx)$ ]] && [[ ! \"$F\" =~ index\\.ts ]]; then DIR=$(dirname \"$F\"); if [ -f \"$DIR/index.ts\" ]; then echo \"Note: Consider updating $DIR/index.ts with the new export\" >&2; fi; fi"
          }
        ]
      }
    ]
  }
}
```

### Recipe 15: Run Related Tests After Edits

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "IN=$(cat); F=$(jq -r '.tool_input.file_path // empty' <<<\"$IN\"); if [[ \"$F\" =~ \\.py$ ]] && [[ ! \"$F\" =~ test_ ]]; then TESTFILE=$(echo \"$F\" | sed 's/\\(.*\\)\\/\\(.*\\)\\.py/\\1\\/test_\\2.py/'); if [ -f \"$TESTFILE\" ]; then python3 -m pytest \"$TESTFILE\" -x -q 2>&1 | tail -5; fi; fi"
          }
        ]
      }
    ]
  }
}
```

### Recipe 16: Restrict Bash to Read-Only Commands

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "IN=$(cat); CMD=$(jq -r '.tool_input.command // empty' <<<\"$IN\"); if echo \"$CMD\" | grep -qE '^(rm |mv |cp |chmod|chown|kill|pkill|mkdir|touch|tee |>|>>)'; then echo 'BLOCKED: Only read commands allowed in this mode' >&2; exit 2; fi"
          }
        ]
      }
    ]
  }
}
```

---

## Recipes: Notifications

### Recipe 17: macOS Desktop Notification on Task Complete

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"Claude Code finished\" with title \"Claude Code\" sound name \"Glass\"' 2>/dev/null || true"
          }
        ]
      }
    ]
  }
}
```

### Recipe 18: Linux Desktop Notification

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "notify-send --app-name='Claude Code' 'Task Complete' 'Claude Code finished its response' 2>/dev/null || true"
          }
        ]
      }
    ]
  }
}
```

### Recipe 19: Play Sound on Completion

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "afplay /System/Library/Sounds/Glass.aiff 2>/dev/null || paplay /usr/share/sounds/freedesktop/stereo/complete.oga 2>/dev/null || true"
          }
        ]
      }
    ]
  }
}
```

---

## Recipes: Context Management

### Recipe 20: Inject Context on Session Start

Re-inject critical context after compaction or at session start.

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "echo \"Project: MyApp v2.1 | Stack: Next.js 14, PostgreSQL, Redis | Testing: Jest + Playwright | Deploy: Vercel + AWS\""
          }
        ]
      }
    ]
  }
}
```

### Recipe 21: Load Session Notes on Start

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "if [ -f .claude/session-notes.md ]; then echo '--- Session Notes ---'; cat .claude/session-notes.md; echo '---'; fi"
          }
        ]
      }
    ]
  }
}
```

### Recipe 22: Inject Git Branch Context

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "BRANCH=$(git branch --show-current 2>/dev/null); if [ -n \"$BRANCH\" ]; then echo \"Current branch: $BRANCH\"; BEHIND=$(git rev-list --count HEAD..origin/$BRANCH 2>/dev/null || echo 0); if [ \"$BEHIND\" -gt 0 ]; then echo \"WARNING: Branch is $BEHIND commits behind remote\"; fi; fi"
          }
        ]
      }
    ]
  }
}
```

---

## Recipes: Logging and Audit

### Recipe 23: Log All Tool Usage

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "IN=$(cat); F=$(jq -r '.tool_input.file_path // empty' <<<\"$IN\"); CMD=$(jq -r '.tool_input.command // empty' <<<\"$IN\"); TOOL=$(jq -r '.tool_name // empty' <<<\"$IN\"); echo \"$(date -Iseconds) | $TOOL | ${F:-${CMD:-n/a}}\" >> .claude/tool-usage.log 2>/dev/null || true"
          }
        ]
      }
    ]
  }
}
```

### Recipe 24: Log Session Duration

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "IN=$(cat); SID=$(jq -r '.session_id // empty' <<<\"$IN\"); echo \"SESSION_START $(date -Iseconds) $SID\" >> .claude/sessions.log 2>/dev/null || true"
          }
        ]
      }
    ],
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "IN=$(cat); SID=$(jq -r '.session_id // empty' <<<\"$IN\"); echo \"SESSION_STOP $(date -Iseconds) $SID\" >> .claude/sessions.log 2>/dev/null || true"
          }
        ]
      }
    ]
  }
}
```

---

## Recipes: Advanced Patterns

### Recipe 25: Combine Multiple Hooks on One Event

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "IN=$(cat); F=$(jq -r '.tool_input.file_path // empty' <<<\"$IN\"); if [[ \"$F\" == *.py ]]; then python3 -m black --quiet \"$F\" 2>/dev/null; fi"
          },
          {
            "type": "command",
            "command": "IN=$(cat); F=$(jq -r '.tool_input.file_path // empty' <<<\"$IN\"); if [[ \"$F\" == *.py ]]; then ruff check --fix \"$F\" 2>/dev/null; fi"
          },
          {
            "type": "command",
            "command": "IN=$(cat); F=$(jq -r '.tool_input.file_path // empty' <<<\"$IN\"); echo \"$(date -Iseconds) | FORMAT | $F\" >> .claude/tool-usage.log 2>/dev/null || true"
          }
        ]
      }
    ]
  }
}
```

### Recipe 26: Conditional Hook with External Script

Create a reusable hook script for complex logic:

**`.claude/hooks/validate-edit.sh`:**
```bash
#!/bin/bash
# Validate file edits with multiple checks

FILE=$(jq -r '.tool_input.file_path // empty')   # hook input arrives as JSON on stdin

# Check 1: Not a lock file
if [[ "$FILE" =~ (lock|\.lock)$ ]]; then
    echo "BLOCKED: Cannot edit lock files" >&2
    exit 2
fi

# Check 2: Not in node_modules
if [[ "$FILE" =~ node_modules/ ]]; then
    echo "BLOCKED: Cannot edit node_modules" >&2
    exit 2
fi

# Check 3: File size limit (prevent editing huge files)
if [ -f "$FILE" ]; then
    SIZE=$(wc -c < "$FILE")
    if [ "$SIZE" -gt 100000 ]; then
        echo "WARNING: File is $(( SIZE / 1024 ))KB - consider editing specific sections" >&2
    fi
fi

exit 0
```

**`.claude/settings.json`:**
```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/validate-edit.sh"
          }
        ]
      }
    ]
  }
}
```

---

## Best Practices

1. **Always fail safe** -- Use `2>/dev/null || true` for non-critical hooks.
   A failing PostToolUse hook should not break the workflow.

2. **Keep hooks fast** -- Command hooks should complete in under 2 seconds.
   Slow hooks degrade the interactive experience.

3. **Use exit codes correctly** -- Exit 2 in PreToolUse blocks the action (stderr is fed back to Claude); exit 1 is a non-blocking error and the tool still runs.
   Exit 0 (or any code) in PostToolUse is informational only.

4. **Write messages to stderr** -- Hook output on stderr is shown to the user.
   Output on stdout may be captured differently.

5. **Test in local settings first** -- Use `.claude/settings.local.json` for
   personal hooks. Only commit to `.claude/settings.json` when proven stable.

6. **Use prompt hooks sparingly** -- They add latency (1-3 seconds) and cost
   money. Reserve them for security-critical checks.

7. **Log for debugging** -- Add a logging hook during development and remove
   it when everything works.

8. **Document your hooks** -- Add a comment (as a separate echo to /dev/null)
   or maintain a README explaining what each hook does.

9. **Keep matchers specific** -- `"Edit|Write"` is better than `""` (which
   matches everything). Specific matchers reduce unnecessary hook executions.

10. **Combine related hooks** -- Use the hooks array to run multiple commands
    on the same event/matcher rather than creating separate entries.

---

## Troubleshooting

### Hook Not Firing

- Verify the event name is spelled correctly (case-sensitive)
- Check that the matcher regex matches the tool name
- Ensure the settings file is valid JSON (`python3 -c "import json; json.load(open('.claude/settings.json'))"`)
- Check that the command exists and is executable

### Hook Blocking Unexpectedly

- Log the raw input to see what the hook receives: `IN=$(cat); echo "DEBUG: $IN" >&2`
- Check that your grep patterns are not too broad
- Verify that exit codes are correct (exit 0 = allow, exit 2 = block)

### Hook Running Too Slowly

- Profile the command: `time your-command`
- Use `|| true` to skip slow operations that fail
- Move complex logic to a compiled script
- Consider if the hook can run asynchronously (PostToolUse only)

### Hook Errors in Logs

- Check stderr output: hooks log errors to the Claude Code console
- Verify file paths are properly quoted (spaces in paths)
- Ensure external tools (prettier, eslint, black) are installed

---

**Last Updated:** February 2026
