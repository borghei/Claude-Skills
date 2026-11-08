# Finding Categories

Eight categories cover almost everything that goes wrong in a coding-agent session and
can be fixed in the environment. Each entry lists what it looks like in a transcript,
what usually causes it, and where the fix belongs. The category names match the values
`action_item_linter.py` accepts.

The question behind every category is the same: **what would a fresh agent, starting
this exact task tomorrow, need to find in its environment so that this cost disappears?**
A finding that cannot be answered with a file edit is not a retro finding; it is a note
about the model.

---

## 1. navigation

**Transcript signals**
- Runs of empty `Grep`/`Glob` results, often with spelling variants of one identifier (`dry_run`, `dryRun`, `dry-run`).
- `ls` walks down a tree one directory at a time.
- The same file read two or more times with no edit in between.
- Many calls (the analyzer's default is 25) before the first edit.

**Usual causes**
- The entry point for a kind of change is not where the name suggests (flags defined in a `build_parser()` three files away from `cli.py`).
- A hidden coupling: changing A requires changing B, and nothing in A mentions B.
- Generated code or vendored copies that look like the real source.

**Where the fix goes**
- One line in `CLAUDE.md` / `AGENTS.md` that maps a task type to its entry point: "CLI flags: `src/exporter/main.py` `build_parser()`."
- A comment at the top of file A that names file B when they must change together.
- A per-directory `CLAUDE.md`/`AGENTS.md` when one area carries most of the confusion, so the root file stays short.
- Exclude generated and vendored directories from search (`.ignore`, `.rgignore`) so they stop surfacing as decoys.

---

## 2. missing-check

**Transcript signals**
- A mistake that a linter, type checker, test or hook would have caught, found late or by the user.
- Several failed shell commands while the agent guesses the right test or build invocation.
- "Done" reported, then a failure discovered on the next command.

**Usual causes**
- The check exists but is not wired anywhere the agent runs it (a `lint` script nobody calls, a hook not installed).
- The check command needs setup that is written nowhere (`PYTHONPATH=src`, a virtualenv, a service running).
- No guardrail at all: no pre-commit hook and no CI job runs lint, types or tests.

**Where the fix goes**
- First look for an existing check that is unwired or broken; fixing it beats adding a new one.
- A deterministic gate — a lint rule, a pre-commit hook, a `make check` target — is the strongest fix. It works whether or not the agent remembers anything.
- When the gate is a command the agent must run, one line in the steering file naming the exact command: "Tests: `make test` (bare `pytest` fails on import)."

---

## 3. standards

**Transcript signals**
- The reviewer (human or agent) caught a style or design problem the implementer kept making.
- The agent asked, or guessed, which of two conventions the repo uses.
- Two parts of the change follow different conventions.

**Usual causes**
- The convention lives in people's heads or in old review comments.
- The standards file contradicts itself or the code.

**Where the fix goes**
- Classify first. A **mechanical** rule (banned API, import shape, file location, naming pattern) becomes a check — see category 2. Writing it as prose is the weaker fix.
- A **judgement** rule (consistency with surrounding code, when to extract a helper) goes in the standards document the reviewer reads, such as `CODING_STANDARDS.md` or `CONTRIBUTING.md`.
- Remove or correct a rule that the code base openly ignores; a standard nobody follows teaches the agent that standards are optional.

---

## 4. steering-file

**Transcript signals**
- The agent followed an instruction in `CLAUDE.md`/`AGENTS.md` that no longer matches the repo.
- The steering file is long, and the instruction that mattered was buried.
- Two steering files (global and project, or root and subdirectory) disagree.

**Usual causes**
- Sediment: lines added after past incidents and never pruned.
- Content that belongs elsewhere: full standards, long procedures, command output.
- Restating what the environment already says (`package.json` scripts, `--help`).

**Where the fix goes**
- Delete stale or contradicted lines. Deletion is a legitimate retro action and often the highest-value one.
- Move procedures into a skill or a doc and leave a one-line pointer.
- Move review-time rules into the standards file; the implementer has the least context to spare.
- See `fix-placement-and-steering-style.md` for the line-writing rules.

---

## 5. tool-economy

**Transcript signals**
- Identical calls repeated after a failure with nothing changed in between.
- Outputs over the analyzer's size threshold (`git log -p`, full test logs, whole JSON dumps).
- Reading a whole large file to find one function.
- A custom CLI or MCP tool whose output is mostly noise.

**Usual causes**
- No narrower command is documented, so the agent reaches for the broadest one.
- A tool lacks a filter, limit, or summary mode.
- The failure message did not say what to change, so the agent tried the same thing again.

**Where the fix goes**
- Add a summary or `--format json` mode to an in-repo tool, or a wrapper script that prints only what matters.
- Improve the failure message of an in-repo script so it names the fix ("run `make deps` first").
- A steering line naming the narrow form: "History of one file: `git log --oneline -20 -- <path>`."

---

## 6. permission-friction

**Transcript signals**
- Calls denied by the permission system or a hook, then retried unchanged.
- The user approving the same safe read-only command over and over.
- The agent abandoning a correct approach because a command was blocked.

**Usual causes**
- Safe read-only commands are not on the allowlist.
- A dangerous command (`rm -rf`) is the only documented way to do a routine thing.
- A hook blocks something without saying what the approved alternative is.

**Where the fix goes**
- Allowlist safe read-only commands in the agent's settings file (for Claude Code, `.claude/settings.json`).
- Give the routine task a safe named entry point (`make clean`) and allowlist that instead of loosening the dangerous command.
- Make every blocking hook print the approved alternative.

Never "fix" friction by allowing a destructive or production-touching command. That trades a slow session for an unsafe one.

---

## 7. skill-miss

**Transcript signals**
- The task matched a skill's purpose, but the skill was never invoked (pass it to the analyzer with `--expected-skills`).
- The agent re-derived a procedure a skill already encodes.
- The wrong skill fired because two descriptions overlap.

**Usual causes**
- The skill's description does not contain the words a user or agent actually uses for the task.
- The skill is user-invoked only, and nobody invoked it.
- Two skills compete for the same trigger words.

**Where the fix goes**
- Rewrite the skill's `description:` so its first words are the trigger the task used.
- Add a one-line pointer in the steering file: "Before adding a CLI flag, use the `tdd` skill."
- For a user-invoked skill, the fix is a habit or a slash command, not a description change. Say so explicitly.

---

## 8. information-access

**Transcript signals**
- The agent guessed at runtime behaviour it could not observe (server logs, browser console, a third-party API's actual response).
- The user had to paste information the agent could have fetched.
- Work stalled waiting on a fact that lives in another system.

**Usual causes**
- Logs go to a terminal the agent cannot read.
- No read-only credential or tool for a service the work depends on.

**Where the fix goes**
- Tee dev-server output to a file the agent can read, and add the path to the steering file.
- Add a read-only integration (CLI, MCP server) scoped to the data needed.
- Document where the fact lives when access cannot be granted.

---

## Mapping analyzer detectors to categories

| Detector in `session_log_analyzer.py` | Category | Confirm before acting |
|---------------------------------------|----------|----------------------|
| empty searches | navigation | Were the searches looking for something that exists? |
| re-reads of unchanged files | navigation | Was the re-read after compaction or a long gap? That is legitimate. |
| calls before first edit | navigation | Was this an investigation task where reading is the work? |
| failed shell commands | missing-check | Was the failure the expected red step of test-first work? That is healthy. |
| identical retries | tool-economy | Was the retry waiting on something external (network, a build)? |
| oversized outputs | tool-economy | Was the whole output actually needed? |
| permission blocks | permission-friction | Was the block correct? If so, the fix is the alternative, not the allowlist. |
| expected skills not invoked | skill-miss | Was the skill really applicable to this task? |

Every detector is a prompt for judgement, not a verdict. A retro that turns each detector
hit into an action item without this confirmation produces churn.
