# Handing Off to a Background Agent

A normal handoff is read by someone who can ask questions. A background handoff is not
read so much as executed: the document becomes the entire prompt of a new agent session
that runs unattended while the current session moves on. Everything the receiver needs to
start, finish, stop safely and report has to be in the document or reachable from it.

## When to use it

- The remaining work is well defined and does not need decisions from the user along the way.
- It would block the current session for a long time (a test-heavy loop, a broad mechanical change, research reading).
- The current session's context is crowded, and a clean start would do the work better.

Do not use it when the next step needs a judgement call only the user can make, when it
touches production or shared infrastructure, or when the work involves a migration or other
change that the project gates on human approval. Hand those to a person.

## What the document needs beyond a normal handoff

| Section | Why it matters unattended | Good example |
|---------|---------------------------|--------------|
| **Goal & done-state** | The agent has no other way to know when to stop | "Done when `make test` passes and a draft PR is open" |
| **Start here** | Removes the first-action guess | "Write the failing test in `tests/x/test_y.py` first" |
| **Stop and report when** | Replaces the questions it cannot ask | "Stop if any test outside `tests/exporter/` fails" |
| **Report back** | Without it the result lands where nobody looks | "Draft PR with a three-line summary; nothing else" |
| **Suggested skills** | The agent starts cold and may not know which skills fit | "`tdd-guide` for steps 1–2; `code-reviewer` before the PR" |
| **Decisions / abandoned paths** | Stops it relitigating or retrying dead ends | "Bare `pytest` fails on import; use `make test`" |

Keep it short. Point at artifacts that already exist — the spec, the tickets, the branch,
specific commits — rather than restating them. The receiver can open files; a pasted copy
is stale the moment something changes and costs prompt space for nothing.

## Redaction

The prompt may be stored in session logs, shown in a job list, or sent to a remote service.
Before launching:

- Remove API keys, tokens, passwords, connection strings and private keys. Write where the
  secret lives (`.env`, the team vault) and let the agent read it there if it is allowed to.
- Remove personal data that the task does not need.
- `handoff_context.py --check` flags common key formats and `password=`-style assignments.
  It cannot catch everything; redaction stays the author's responsibility.

## Where to save the document

Outside the working tree, so it is never committed by accident: the OS temp directory
(`$TMPDIR` on macOS, `/tmp` on Linux, `%TEMP%` on Windows) or a scratch folder ignored by git.
Name it after the task: `handoff-exporter-dry-run.md`.

## Launching

Run from the same working directory as the current session so paths in the doc resolve.
Give the session a descriptive name so it is recognisable in the job list. Read the file
through `"$(cat file)"` or stdin: either way the shell does not interpret backticks or `$`
inside the document.

| Platform | Command shape | Notes |
|----------|---------------|-------|
| Claude Code, background session | `claude --bg --name "<name>" -- "$(cat <file>)"` | Available in recent versions; confirm with `claude --help`. Manage running sessions with the CLI's agent/session commands. |
| Claude Code, headless | `nohup claude -p < <file> > run.log 2>&1 &` | Print mode runs non-interactively; tool permissions come from settings, since nobody can approve prompts. |
| Codex CLI | `codex exec "$(cat <file>)"` | Non-interactive execution; check `codex exec --help` for sandbox and approval flags. |
| Others | The tool's non-interactive or background mode | Look for "headless", "exec", "print" or "background" in its help. |

Flags change between versions. Check the CLI's help before relying on any row above.

## Permissions

A background session cannot ask for approval, so whatever it needs must already be allowed,
and whatever it must not do must already be denied. Check the permission settings that apply
to the directory before launching. Do not widen them for the run; if the task needs a
permission the project does not grant, the task is not ready for background mode.

## Checking on the run

- Note the session name and where the report will land.
- Look at the result where the doc said it would be (the draft PR, the file). Review it as
  you would any change: the background agent's confidence is not evidence.
- If it stopped on a stop condition, that is the system working. Read its report, make the
  decision it could not make, and hand off again or finish by hand.
