---
name: handoff
description: >
  Package in-progress work into a self-contained context doc or a background agent's
  prompt. Use when handing work off, switching off a task, or delegating to a fresh or
  background agent.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: workflow
  domain: collaboration
  updated: 2026-11-08
  python-tools: handoff_context.py
  tags: [handoff, delegation, context, continuity, background-agent, async]
---
# Handoff

## Overview

A handoff is a self-contained context package that lets a different person — or a
fresh AI agent — pick up in-progress work without re-deriving everything. Most
delegation fails not because the next person lacks skill, but because the *context*
in the originator's head never got written down: what's done, what's half-done, why
a path was abandoned, and what to do next. This skill produces a structured handoff
document that captures exactly that, so the receiver can be productive on their first
action instead of their tenth.

Use it across any domain in this library — engineering work, a PM initiative, a
compliance audit, a draft document — wherever work outlives a single working session.

## When to Use

- **Switching off a task** — you started something and someone else (or future-you) will finish it.
- **Delegating to an agent** — handing a scoped task to a sub-agent or teammate who lacks your conversation history.
- **End of a session/shift** — async teams where the next person picks up cold.
- **Escalating** — passing a blocked item up or sideways with full context on what was tried.
- **Handing off to a background agent** — the work should keep going in a separate session while you do something else (see the background-agent workflow below).

## Clarify First

Before writing the handoff, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Receiver:** a teammate, a fresh AI agent, or future-you (sets how much background to spell out vs assume).
- **The goal + done-state:** what "finished" looks like for this work (anchors the Next Steps section).
- **Current state:** what is done, in-progress, and untouched right now (the heart of the handoff).
- **Mode:** a person or interactive agent reads the doc and can ask questions; a background agent gets the doc as its whole prompt and cannot. Background mode needs stop conditions and a report-back target.
- **Constraints & landmines:** deadlines, decisions already made, paths already tried and abandoned (prevents the receiver repeating dead ends).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

```bash
# Gather objective state (git branch, recent commits, changed/untracked files) to seed the handoff
python scripts/handoff_context.py --repo . --format markdown
```

1. Run `handoff_context.py` to capture the objective state (git status, recent commits, changed files).
2. Fill the handoff template (`assets/handoff_template.md`) — lead with goal + current state, not history.
3. Make every open item **actionable**: a verb, a file/location, and the expected outcome.
4. List abandoned approaches and *why* — this is the highest-value, most-often-omitted section.
5. End with the single recommended next action so the receiver has zero ambiguity about step 1.

## Background-Agent Workflow [RECOMMENDED]

Use when the work should continue unattended in its own session. The doc becomes the
background agent's whole prompt, so it must stand alone. Full guidance, launch options per
platform and safety notes: [references/background-agent-handoff.md](references/background-agent-handoff.md).

1. Write the doc from the template, including the three background sections: **Stop and report when**, **Report back**, **Suggested skills**.
2. Point at the spec, tickets, branch and commits; do not paste diffs or long excerpts.
3. Redact keys, tokens, passwords and personal data; name where a secret lives instead.
4. Save the doc outside the working tree (OS temp or a scratch folder).
5. Validate with `handoff_context.py --check`; fix every problem it lists.
6. After the user confirms, launch a named background session with the doc as its prompt, from the same directory.

```bash
python scripts/handoff_context.py --check assets/sample_background_handoff.md --name "Exporter dry-run"
claude --bg --name "Exporter dry-run" -- "$(cat /tmp/handoff.md)"   # flags vary by version: check --help
```

## The handoff structure

| Section | What it answers | Keep it to |
|---------|-----------------|-----------|
| **Goal & done-state** | Where are we headed and how do we know we're done? | 2-3 sentences |
| **Current state** | What's done / in-progress / untouched right now? | A checklist |
| **Next steps** | What should the receiver do, in order? | Ranked, actionable |
| **Decisions made** | What's already settled (don't relitigate)? | Bullets + one-line why |
| **Abandoned paths** | What was tried and ruled out, and why? | Bullets + reason |
| **Open questions / risks** | What's unresolved or could bite? | Bullets, flag owner |
| **Key locations** | Files, branches, dashboards, tickets, people | Links/paths |
| **Stop and report when** *(background)* | When must the agent stop instead of improvising? | Bullets |
| **Report back** *(background)* | Where does the result go, and what must it contain? | One line |
| **Suggested skills** *(background)* | Which skills cover which step? | Skill — step |

## Anti-patterns

- **Narrating history instead of state.** The receiver needs "where we are," not a chronological diary. Lead with current state.
- **Vague next steps.** "Continue the integration" is not actionable. "Wire `auth.py:42` to the new token endpoint; expect a 200 with a JWT" is.
- **Omitting abandoned paths.** If you don't say "we tried X, it failed because Y," the receiver wastes hours rediscovering it.
- **Dumping the whole conversation.** A handoff is a curated package, not a transcript. Summarize and link.
- **No single starting action.** Always end with the one thing to do first.

### The Open-Ended Background Prompt
**Mistake:** Launching a background agent with "continue where we left off" plus a summary, and no stop conditions or report target.
**Why it happens:** It works in an interactive session, where the receiver can ask.
**Instead:** Spell out when to stop and where to report. An unattended agent with no stop rule improvises past the point where a person would have asked, and its result lands nowhere anyone looks.

### Secrets in the Prompt
**Mistake:** Pasting a connection string or token into the handoff "so the agent has everything".
**Why it happens:** It is the fastest way to unblock the receiver.
**Instead:** Name where the secret lives and let the receiver read it there. `--check` flags common key formats, but redaction is the author's job.

### The Pasted Diff
**Mistake:** Including the full diff or whole files in the handoff.
**Why it happens:** It feels more complete than a pointer.
**Instead:** Reference the branch and commits. The receiver reads current files; a pasted copy is stale the moment anything changes.

## Tools Overview

`scripts/handoff_context.py` has two modes. Default: print the branch, recent commits and
changed files as a seed block (`--format markdown|json`). With `--check FILE`: validate a
handoff doc for background use and print launch commands; exit 0 ready, 1 not ready, 2
unreadable file. It never launches anything itself.

## Scope & Limitations

**In Scope:** Producing a structured, self-contained handoff document for in-progress work in any domain; capturing objective repo state via the helper script; making open work actionable for the receiver; preparing, checking and launching a handoff as the prompt of a background agent session.

**Out of Scope:** Project status reporting to stakeholders (`project-management/execution/status-update-generator/`); incident post-mortems (`project-management/execution/post-mortem/`); onboarding a new hire to a whole role (`hr-operations/`, `project-management/career/pm-onboarding/`). A handoff is about one body of in-flight work, not a person's full ramp-up.

## Files

| File | Purpose |
|------|---------|
| `scripts/handoff_context.py` | Seed block from git state; `--check` validates a background-mode handoff |
| `assets/handoff_template.md` | Fill-in handoff document, with the three background-mode sections at the end |
| `assets/sample_background_handoff.md` | Complete background-mode handoff that passes `--check` |

## Reference Documentation

- `references/background-agent-handoff.md` — what a background prompt needs, launch commands per platform, quoting, permissions, and how to check on the run.
- `assets/handoff_template.md` — fill-in-the-blanks handoff document.
- `scripts/handoff_context.py` — captures git branch, recent commits, and changed/untracked files as a seed block.
