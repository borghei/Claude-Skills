---
name: session-retro
description: >
  Review a coding-agent session and turn its failures and waste into ranked fixes to
  the agent's environment. Use when a session went slow or wrong, after a messy
  agent run, or to tune CLAUDE.md or AGENTS.md.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: workflow
  domain: agent-operations
  updated: 2026-11-08
  python-tools: session_log_analyzer.py, action_item_linter.py
  tags: [retrospective, agent-session, claude-md, agents-md, tool-calls, developer-experience]
---

# Session Retro

A retrospective on one coding-agent session, aimed at the agent's **environment** rather
than at the people or the model. Every wasted call in a session has a cause outside the
model that someone can edit: a file nobody pointed to, a test command written nowhere, a
lint rule that does not exist, a safe command missing from the allowlist, a skill whose
description never matched. This skill reads the transcript, counts where the session
leaked time, and produces a short ranked list of changes, each naming the file to edit.

The output is not "the agent should be more careful". It is "add `Tests: make test` to
`AGENTS.md`" or "wire `ruff check` into the pre-commit hook", with the call numbers that
justify it.

## When to Use

- **After a session that went slow or wrong** — many retries, a late-found bug, a wrong turn that cost twenty calls.
- **After a session the user had to rescue** — the user pasted information, overrode a decision, or approved the same command repeatedly.
- **When tuning steering files** — `CLAUDE.md`, `AGENTS.md`, `GEMINI.md` or Cursor rules have grown and nobody knows which lines still earn their place.
- **Before repeating a task type** — the same kind of change is coming again and the last run was expensive.

**Not this skill:** a team sprint retrospective (`sprint-retrospective` in project management), an incident post-mortem, or a code review of the session's output.

## Clarify First

What shapes the result most is which session is reviewed and what it was supposed to
achieve. Settle the inputs below before analysing. When one is missing or vague and would
change the result, ask about it; when it wouldn't, use a sensible default and say which
one you used.

- **Which session:** a transcript path or session id. Default to the current session; the analyzer needs the log, and memory of a session is far less reliable than its record.
- **The task the session was given:** the waste only makes sense against the goal. Twenty reads before an edit is waste on a one-line fix and normal on an investigation.
- **Skills that should have fired:** they become `--expected-skills`, and without them the skill-miss category cannot be checked.
- **What the user is allowed to change:** a contributor may be able to edit `CLAUDE.md` but not CI or global settings, which moves fixes to a different rung.

Ask about the two or three inputs that matter most for this request, not the whole list.
If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

```bash
# 1. Count where the session leaked: retries, re-reads, failures, friction
python3 scripts/session_log_analyzer.py --input assets/sample_session.jsonl --expected-skills tdd

# 2. Lint the drafted action list before handing it over
python3 scripts/action_item_linter.py --input assets/sample_action_items.json
```

Both sample runs exit 1 on purpose: the sample session is full of waste, and two of the
six sample action items are deliberately malformed so you can see each rule fire.

## Workflow

1. **Locate the transcript.** Use the session the user named, or the current one. Claude Code keeps logs at `~/.claude/projects/<project-slug>/<session-id>.jsonl`; other agents vary (see `references/transcript-sources.md`). Without a log, rebuild the call list by hand in the normalized format.
2. **Run the analyzer.** `session_log_analyzer.py --input <log> --expected-skills <list>`. It reports findings by category with call numbers as evidence. Treat each finding as a lead, not a verdict.
3. **Confirm every lead against the transcript.** Open the cited calls. Drop findings that were legitimate work: a failing test in a test-first loop, a re-read after compaction, long reading on an investigation task. The detector table in `references/finding-categories.md` lists what to check for each.
4. **Read for what the analyzer cannot count.** Moments where the user corrected the agent, where the agent asked a question the repo should have answered, where it followed a stale instruction, or where it found a bug late. These are often the most valuable findings.
5. **Read the environment before proposing anything.** Open the steering files, the check commands (`Makefile`, `package.json` scripts, pre-commit config, CI workflow) and the settings file. A check that exists but is unwired is a different fix from a check that does not exist.
6. **Turn each confirmed finding into one change on the highest possible rung.** Deterministic check first, then a better tool, then an environment change, then the standards doc the reviewer reads, then a directory-level pointer, and only then a line in the root steering file. The ladder is in `references/fix-placement-and-steering-style.md`.
7. **Rank and cut.** Score by severity, recurrence and fix effort. Keep at most seven items; park the rest with the trigger that would promote them.
8. **Validate the list.** Run `action_item_linter.py` over it. Every item needs a category, an imperative change, a target file, evidence and a severity. Fix all errors; treat warnings as review prompts.
9. **Present, then apply only what the user approves.** Show the ranked list from `assets/retro_template.md`. The agent edits files only after approval, because steering files and CI are shared with other people and other agents.
10. **Name the verification.** For each shipped item, state what the next comparable session should show if the fix worked.

## Finding Categories

Eight categories, each matching a value the linter accepts: `navigation`, `missing-check`,
`standards`, `steering-file`, `tool-economy`, `permission-friction`, `skill-miss`,
`information-access`. Signals, causes and the usual target file for each are in
`references/finding-categories.md`.

## Tools Overview

| Tool | Purpose | Exit codes |
|------|---------|-----------|
| `scripts/session_log_analyzer.py` | Detect retries, re-reads, failed commands, empty searches, permission blocks, oversized outputs, slow orientation and missed skills in a JSONL log | 0 clean, 1 finding at or above `--fail-on` (default medium), 2 unreadable input |
| `scripts/action_item_linter.py` | Require category, imperative change, target file, evidence and severity per item; flag advice wording, long steering edits and mechanical rules routed to prose | 0 clean, 1 errors (or warnings with `--strict`), 2 unreadable input |

```bash
# Real session, JSON for further processing, only fail on high-severity findings
python3 scripts/session_log_analyzer.py \
  --input ~/.claude/projects/<project-slug>/<session-id>.jsonl \
  --expected-skills tdd,code-reviewer --fail-on high --format json

# Lint the filled-in template directly (it reads the action-item table)
python3 scripts/action_item_linter.py --input retro.md --strict
```

## Decision Rules

### [PROVEN] Fix the environment, not the transcript
A finding that ends in "the agent should have…" is unfinished. Ask what file, if it had
said something different, would have prevented the cost. If no file edit would have
helped, the finding is about the model and does not belong in the action list.

### [PROVEN] Prefer a check over a sentence
A rule with a fixed shape (banned import, required flag, file location) becomes a lint
rule, hook or test. A sentence in `CLAUDE.md` is followed most of the time and costs
tokens on every turn; a check is followed every time and costs nothing until it fires.

### [RECOMMENDED] Put review rules where the reviewer reads them
The implementing agent carries the heaviest context load. Standards that a reviewer can
apply to a diff belong in the standards document, not in the always-loaded steering file.

### [RECOMMENDED] Deletion counts as a fix
Check which steering lines did nothing this session, or misled the agent. Removing a
stale line is cheaper and often more effective than adding a new one.

### [EXPERIMENTAL] Orientation budget of 25 calls
The analyzer flags more than 25 calls before the first edit. The number is a starting
point from implementation-style tasks; raise it for investigation tasks with
`--orientation-budget`. Risk: on a large unfamiliar repo the default fires on healthy
exploration, so confirm before acting.

## Anti-Patterns

### Advice Dressed as an Action
**Mistake:** Action items like "be more careful with test commands" or "remember to use the TDD skill".
**Why it happens:** It is the natural way to describe a mistake, and it feels like a lesson learned.
**Instead:** Name the file and the edit: "Add `Tests: make test` to `AGENTS.md`." The linter flags advice wording and missing targets for this reason.

### The Steering File Landfill
**Mistake:** Every retro appends three paragraphs to `CLAUDE.md`, until it is longer than the code it describes.
**Why it happens:** Adding a line feels safe; removing one feels risky, so nothing is ever pruned.
**Instead:** Climb the placement ladder first. When a steering line is the right fix, keep it to one imperative line or a pointer, and look for a line to delete in the same retro.

### Detector Worship
**Mistake:** Turning every analyzer hit into an action item without opening the cited calls.
**Why it happens:** The report looks authoritative and the call numbers make it feel checked.
**Instead:** Confirm each lead in the transcript. A failing test in a red-green loop is the workflow working; a re-read after compaction is necessary. Drop those and say so.

### The Fifteen-Item Retro
**Mistake:** Listing every possible improvement, ranked by nothing.
**Why it happens:** Completeness feels like rigour.
**Instead:** Rank by severity, recurrence and effort, ship at most seven, and park the rest with a promotion trigger. Three landed fixes beat fifteen proposed ones.

### Loosening Safety to Remove Friction
**Mistake:** Allowlisting a destructive command because the agent kept asking for it.
**Why it happens:** Permission prompts are the most visible friction in a session.
**Instead:** Give the routine task a safe, named entry point (`make clean`) and allowlist that. Leave destructive and production-touching commands gated.

## Verification Checklist

Before presenting the retro, verify that:

- [ ] Every finding was confirmed against the cited calls, and false positives were dropped with a reason.
- [ ] The environment was read before proposing changes (steering files, check commands, settings).
- [ ] Each item names one target file and sits on the highest rung that can carry it.
- [ ] `action_item_linter.py` passes with zero errors.
- [ ] The list has at most seven items, ranked high to low, with a parked list for the rest.
- [ ] Each shipped item has a verification the next session can show.
- [ ] No raw transcript excerpts with secrets or personal data appear in the output.

## Files

| File | Purpose |
|------|---------|
| `scripts/session_log_analyzer.py` | Transcript analyzer: retries, re-reads, failures, empty searches, permission blocks, oversized outputs, orientation cost, missed skills |
| `scripts/action_item_linter.py` | Action-list linter for JSON or the template's markdown table |
| `references/finding-categories.md` | The eight categories: transcript signals, causes, where the fix goes, and how to confirm each detector |
| `references/fix-placement-and-steering-style.md` | Placement ladder, ranking formula, steering-line style with rewrites, platform file map, verification |
| `references/transcript-sources.md` | Where session logs live, the two accepted formats, call-number evidence, safe handling |
| `assets/sample_session.jsonl` | Synthetic 22-call Claude Code session with typical waste, for the analyzer |
| `assets/sample_action_items.json` | Sample action list: four good items and two deliberately flawed ones |
| `assets/retro_template.md` | Retro document template with the action-item table the linter reads |

## Reference Documentation

- **[references/finding-categories.md](references/finding-categories.md)** — read when classifying a finding or deciding whether a detector hit is real.
- **[references/fix-placement-and-steering-style.md](references/fix-placement-and-steering-style.md)** — read when choosing where a fix goes or writing a steering-file line.
- **[references/transcript-sources.md](references/transcript-sources.md)** — read when locating a session log or converting one from another agent.

## Scope & Limitations

**In Scope:**
- One coding-agent session (or a few sessions on the same task type) reviewed for environment fixes.
- Deterministic transcript analysis of Claude Code JSONL logs and a normalized format any agent's log can be converted to.
- Ranked, evidenced action items covering navigation, checks, standards, steering files, tool economy, permissions, skill triggering and information access.
- Linting the action list before it is shared.

**Out of Scope:**
- Team sprint retrospectives and delivery metrics (`sprint-retrospective`).
- Incident post-mortems for production failures (`post-mortem`).
- Reviewing the code the session produced (`code-reviewer`).
- Judging model quality or comparing models.

**Important Caveats:**
- Detectors are heuristics over call sequences. They do not understand intent, so every finding needs confirmation in the transcript.
- Log formats change between agent versions. If the analyzer reports zero calls on a real log, convert it to the normalized format.
- The analyzer reads tool inputs and outputs, which can include secrets. It prints only counts and call numbers, but the transcript itself must be handled as sensitive.
- Applying fixes edits shared files (steering files, CI, settings). The skill proposes; the user approves.
