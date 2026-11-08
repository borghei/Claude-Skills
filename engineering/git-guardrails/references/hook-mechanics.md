# Hook Mechanics: Claude Code PreToolUse and Plain Git Hooks

How the two enforcement layers actually work, where each one is blind, and how
to install, test and debug them without breaking an existing setup.

## Layer 1: Claude Code PreToolUse hook

### The contract

1. Before Claude Code runs a tool, it looks up `hooks.PreToolUse` in every
   settings file in scope and selects entries whose `matcher` matches the tool
   name. `"Bash"` matches only the Bash tool.
2. It runs each matching `command` with the tool call as JSON on **stdin**:

   ```json
   {
     "session_id": "abc123",
     "hook_event_name": "PreToolUse",
     "cwd": "/home/dev/project",
     "tool_name": "Bash",
     "tool_input": {"command": "git reset --hard", "description": "Discard changes"}
   }
   ```

3. It reads the exit code:

   | Exit | Meaning | What the agent sees |
   |------|---------|---------------------|
   | `0` | allow | nothing; the command runs |
   | `2` | **block** | the hook's stderr is fed back to the model; the command never runs |
   | any other | non-blocking error | stderr is shown to the user; **the command still runs** |

The third row is the trap. A hook that crashes with a Python traceback exits 1,
and exit 1 does **not** block. That is why the bundled hook never raises: every
parse failure resolves to a decision, and blocking is only ever exit 2. Some
older write-ups claim exit 1 blocks; test it with the tester rather than trust it.

A hook may alternatively print a JSON object with a `permissionDecision` of
`deny` and exit 0. The exit-2 form is used here because it is simpler, works in
every Claude Code version that supports hooks, and is trivially testable from a
shell.

### Settings layering

| File | Scope | Committed? | Use for |
|------|-------|------------|---------|
| `~/.claude/settings.json` | every project for this user | no | personal safety net on all repos |
| `<project>/.claude/settings.json` | this project, every contributor | yes | team-wide guardrails |
| `<project>/.claude/settings.local.json` | this project, this user | no (gitignore it) | local experiments |
| managed / enterprise policy | org-wide | admin-controlled | non-negotiable rules |

Hooks from all levels **run together**; a project file cannot remove a user-level
hook. That makes user scope the right home for a personal guardrail and project
scope the right home for a team one. [RECOMMENDED] Install at project scope and
commit it, so every contributor's agent gets the same rules and the corpus test
can run in CI.

### Command path

Use `$CLAUDE_PROJECT_DIR` for project hooks so the hook resolves no matter which
subdirectory the agent has `cd`-ed into:

```json
{"type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/git_guardrails_hook.py\"", "timeout": 10}
```

Quote the variable: project paths with spaces are common on macOS. The timeout
keeps a hung `git symbolic-ref` (network filesystem, huge repo) from stalling
every Bash call.

### What the agent sees on a block

```
BLOCKED by git-guardrails [reset-hard]: reset --hard discards uncommitted work with no undo.
  command: git reset --hard
  Do not retry or work around this. If the operation is really intended, explain why and ask the user to run it in their own terminal.
```

The last line matters. Without an instruction, models tend to try the next
closest command (`git checkout -- .`, then `rm -rf`, then `git stash && git stash
drop`). Telling the model to stop and hand the decision to the human is what
turns a block into a conversation instead of an arms race.

### Escape hatches

- **For one command:** the human runs it in their own terminal. This is the
  intended path; destructive git should be a human decision.
- **For a session:** `export GIT_GUARDRAILS_DISABLE=1` *before* starting Claude
  Code. The variable is read from the hook's own environment, so an agent
  writing `GIT_GUARDRAILS_DISABLE=1 git push -f` gains nothing: that assignment
  only applies to the git process, which never starts.
- **For one rule:** add its id to `disabled_rules` in `.claude/git-guardrails.json`.

## Layer 2: plain git hooks

Git has client hooks for some, not all, destructive operations:

| Operation | Git hook available? | Bundled |
|-----------|---------------------|---------|
| Force push, remote delete, push to protected | `pre-push` (sees every ref update with old/new SHA) | yes |
| Rebase of a protected branch | `pre-rebase` | yes |
| `reset --hard`, `clean -f`, `checkout .`, `branch -D` | **none** | n/a |
| History rewrite with filter-repo | none (it bypasses hooks) | n/a |

So the git hooks complement, not replace, the Claude Code hook. Their advantage
is coverage of anything that calls git: release scripts, IDE buttons, other AI
tools, and humans. Their weakness is `git push --no-verify`, which skips them by
design, and the fact that `.git/hooks` is not versioned. Teams that want them on
every clone should set `core.hooksPath` to a committed directory.

Force detection in `pre-push` is exact rather than flag-based: for each ref it
checks whether the remote's current SHA is an ancestor of the new SHA. If the
remote SHA is not present locally (someone else pushed and you have not fetched),
the hook refuses pushes to protected branches and asks for a fetch, because it
cannot prove the update is a fast-forward.

Configure protected branches per repo:

```bash
git config --add guardrails.protected main
git config --add guardrails.protected 'release/*'
git config guardrails.blockDirectPush true   # also refuse direct pushes to them
```

## Layer 0: the server

Neither client layer replaces server-side branch protection (required reviews,
no force push, no deletion on `main`). Client hooks stop mistakes early and
explain them; server rules are the only ones a client cannot skip. [PROVEN]
Configure both.

## Install safety rules (what the installer guarantees)

1. **Merge, never overwrite.** The installer appends its own PreToolUse entry.
   Existing entries, matchers, other events and every other settings key are
   left byte-for-byte equal in meaning.
2. **Idempotent.** If any entry already runs `git_guardrails_hook.py`, the
   settings file is not rewritten.
3. **Refuse on doubt.** Invalid JSON, a non-object `hooks`, or a non-list
   `PreToolUse` stops the run with exit 2 and no writes.
4. **Backups.** The previous settings are copied to `settings.json.bak` before
   the atomic replace (write to `.tmp`, then rename).
5. **No hook clobbering.** A different `git_guardrails_hook.py` (older version)
   or a foreign `pre-push` is reported as a conflict and left alone, exit 1.

To chain with an existing `pre-push`, call ours from yours and propagate its
exit code; git passes the ref list on stdin, so capture it once and feed both:

```bash
refs="$(cat)"
printf '%s\n' "$refs" | .git/hooks/pre-push.guardrails "$@" || exit 1
printf '%s\n' "$refs" | .git/hooks/pre-push.original "$@"
```

## Debugging

1. Run the hook by hand with `--check`: prints the decision as JSON and exits
   0 or 2.
2. Pipe a payload: `echo '{"tool_name":"Bash","tool_input":{"command":"git reset --hard"}}' | python3 .claude/hooks/git_guardrails_hook.py; echo $?`
3. In Claude Code, `/hooks` lists the hooks actually loaded; if yours is missing,
   check that the settings file is valid JSON and that you restarted the session.
4. A hook that blocks a harmless command: add the command to the corpus as an
   `allow` case first, then fix the rule, then re-run the tester. The corpus is
   the regression suite.
