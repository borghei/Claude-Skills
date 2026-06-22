---
name: handoff
description: >
  This skill should be used when the user asks to "write a handoff", "hand this
  off", "package this work for someone else", "summarize where we are so another
  person/agent can continue", or "create a context doc before I switch off this task".
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: workflow
  domain: collaboration
  updated: 2026-06-22
  python-tools: handoff_context.py
  tags: [handoff, delegation, context, continuity, onboarding, async]
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

## Use when

- **Switching off a task** — you started something and someone else (or future-you) will finish it.
- **Delegating to an agent** — handing a scoped task to a sub-agent or teammate who lacks your conversation history.
- **End of a session/shift** — async teams where the next person picks up cold.
- **Escalating** — passing a blocked item up or sideways with full context on what was tried.

## Clarify First

Before writing the handoff, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Receiver** — a teammate, a fresh AI agent, or future-you (sets how much background to spell out vs assume)
- [ ] **The goal + done-state** — what "finished" looks like for this work (anchors the Next Steps section)
- [ ] **Current state** — what is done, in-progress, and untouched right now (the heart of the handoff)
- [ ] **Constraints & landmines** — deadlines, decisions already made, paths already tried and abandoned (prevents the receiver repeating dead ends)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the handoff.

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

## Anti-patterns

- **Narrating history instead of state.** The receiver needs "where we are," not a chronological diary. Lead with current state.
- **Vague next steps.** "Continue the integration" is not actionable. "Wire `auth.py:42` to the new token endpoint; expect a 200 with a JWT" is.
- **Omitting abandoned paths.** If you don't say "we tried X, it failed because Y," the receiver wastes hours rediscovering it.
- **Dumping the whole conversation.** A handoff is a curated package, not a transcript. Summarize and link.
- **No single starting action.** Always end with the one thing to do first.

## Scope & Limitations

**In Scope:** Producing a structured, self-contained handoff document for in-progress work in any domain; capturing objective repo state via the helper script; making open work actionable for the receiver.

**Out of Scope:** Project status reporting to stakeholders (`project-management/execution/status-update-generator/`); incident post-mortems (`project-management/execution/post-mortem/`); onboarding a new hire to a whole role (`hr-operations/`, `project-management/career/pm-onboarding/`). A handoff is about one body of in-flight work, not a person's full ramp-up.

## References

- `assets/handoff_template.md` — fill-in-the-blanks handoff document.
- `scripts/handoff_context.py` — captures git branch, recent commits, and changed/untracked files as a seed block.
