---
name: issue-triage
description: >
  Move engineering issues and external PRs through a triage state machine and
  write agent-ready briefs. Use when clearing a triage queue, deciding if a
  report is real or wanted, or handing an issue to a coding agent.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-11-08
  python-tools: triage_state_validator.py, agent_brief_linter.py
  tech-stack: issue-tracking, github, gitlab, linear, jira, ai-agents
  tags:
    - triage
    - issue-tracking
    - agent-brief
    - pull-requests
    - labels
---

# Issue Triage

Triage decides, for each inbound issue or external pull request, what it is, whether it is real, whether the project wants it, and who makes the next move. The agent runs it as a state machine — `new → needs-info → reproduced → accepted / duplicate / out-of-scope → ready-for-agent / ready-for-human` — so every item has one owner of its next step and shortcuts become visible. A PR is an issue with code attached: same states, read against the diff.

## When to Use

- A backlog of unlabelled or `needs-info` issues needs clearing
- Deciding whether a bug report holds up or a feature request is wanted
- An external PR arrives and needs a verdict before review time is spent
- An accepted issue is about to go to a coding agent and needs a brief

## Clarify First

The tracker conventions and who decides shape every label change. Settle the inputs below before producing anything. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Label scheme and tracker:** state may be labels or native statuses; mapping wrongly creates two sources of truth. Default: `type:`/`state:`/`priority:` labels.
- **Out-of-scope register location:** without it, the prior-rejection check cannot run and old debates restart.
- **Who confirms decisions:** the agent recommends; a maintainer approves state changes unless they said to apply them directly.

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

Audit a triage export against the state machine (exit 1 = violations):

```bash
python3 project-management/execution/issue-triage/scripts/triage_state_validator.py \
  --input project-management/execution/issue-triage/assets/sample_triage_history_clean.json --today 2026-11-08
# assets/sample_triage_history.json is the flawed export: exits 1 with 10 errors
```

Lint briefs before an item moves to `ready-for-*` (exit 1 = not hand-off ready):

```bash
python3 project-management/execution/issue-triage/scripts/agent_brief_linter.py \
  --input project-management/execution/issue-triage/assets/sample_agent_brief_clean.md --format json
```

A clean export prints:

```text
Triage state validation: PASS  (5 items, as of 2026-11-08)
```

## Tools Overview

| Tool | Input | Checks |
|---|---|---|
| `triage_state_validator.py` | Issues with labels + transitions; register | Illegal moves, label invariants, unreproduced bugs, missing briefs, unlinked duplicates, unregistered rejections, stale needs-info |
| `agent_brief_linter.py` | Briefs, JSON or markdown | Missing sections, paths/line numbers, vague or compound criteria, procedural wording, no verification command |

### Exit code contract [PROVEN]

| Code | Meaning |
|---|---|
| 0 | No error findings (warnings allowed) |
| 1 | Gate failed: at least one error finding — the flawed samples exit 1 by design |
| 2 | Input missing, unreadable, or not the expected shape |

## Workflow

1. **Show the queue.** Unlabelled, then `state:new`, then overdue `needs-info`, oldest first; tag `[issue]` or `[PR]`.
2. **Gather context.** Read the thread and earlier triage notes; never re-ask an answered question.
3. **Run the evidence checks** [PROVEN]. Search by concept for an existing implementation and say where you looked; check the out-of-scope register for a prior rejection. Details: `references/evidence-and-out-of-scope.md`.
4. **Verify the claim.** Reproduce a bug from the reporter's steps; check out a PR and run its tests. No bug reaches `accepted` without `reproduced`.
5. **Recommend, then apply.** Post type, state and reasoning; the maintainer confirms. Flag conflicting labels instead of fixing them silently.
6. **Write the outcome note** from `assets/triage_notes_template.md`: needs-info, duplicate, out-of-scope (plus register entry) or already-implemented.
7. **Write the brief** [RECOMMENDED] for `ready-for-agent` from `assets/agent_brief_template.md`: behaviour not steps, no file paths, testable criteria, an out-of-scope fence, a verification command. `ready-for-human` adds why it cannot be delegated.
8. **Quality gate.** Run `agent_brief_linter.py` on every brief and `triage_state_validator.py` on the weekly export; validate to zero errors before the state changes.

| Signal in the export | Diagnosis |
|---|---|
| `needs-info` keeps growing | Questions too vague to answer |
| `accepted` keeps growing | Briefs not being written |
| Many `ready-for-agent`, few `resolved` | Briefs too loose; tighten criteria |

## Anti-Patterns

### Accepting Unreproduced Bugs
**Mistake:** A plausible bug goes from `new` to `accepted` and then to an agent.
**Why it happens:** The report sounds credible and reproducing feels slow.
**Instead:** Reproduce first; the reproduction note becomes the brief's "current behavior". If you cannot, use `needs-info` or record why you accept without it.

### The Reporter's Text as the Brief
**Mistake:** An item is labelled `ready-for-agent` with only the original report.
**Why it happens:** Labelling is one click; a brief takes ten minutes.
**Instead:** No `ready-for-*` state without a brief that passes the linter.

### "Please Provide More Info"
**Mistake:** Parking an item with a generic request.
**Why it happens:** The triager has not worked out what is actually missing.
**Instead:** State what is established, then ask one or two questions that decide the next state.

### Rejections Without Memory
**Mistake:** Closing a feature request with "not planned" and nothing else.
**Why it happens:** The decision feels obvious today.
**Instead:** Add the issue to an out-of-scope register entry with a durable reason. Keep already-implemented items out of it.

### Judging the Code Before the Change
**Mistake:** Reviewing an external PR line by line before deciding the project wants it.
**Why it happens:** The diff is concrete; scope feels abstract.
**Instead:** Accept or reject the change first; then verify or brief the diff.

## Files

| File | Purpose |
|---|---|
| `scripts/*.py` | The two gates above |
| `assets/sample_triage_history*.json` | Flawed (exit 1) and `_clean` (exit 0) exports |
| `assets/sample_agent_briefs.json`, `sample_agent_brief_clean.md` | Flawed (exit 1) and clean (exit 0) briefs |
| `assets/*_template.md` | Agent brief, triage notes, register entry, label scheme |

## Reference Documentation

- `references/state-machine-and-labels.md` — states, legal transitions, PR readings, stale policy, tracker mapping, validator rules. Read when setting up triage or reading a failing validation.
- `references/agent-briefs.md` — brief principles, ready-for-human reasons, PR briefs, worked example, linter rules. Read before writing a brief.
- `references/evidence-and-out-of-scope.md` — redundancy and prior-rejection checks, reproduction, needs-info questions, duplicates, the register. Read when deciding whether an item is real and wanted.

## Scope & Limitations

**In Scope:** the triage state machine for issues and external PRs, labels, evidence checks, needs-info notes, the out-of-scope register, and briefs.

**Out of Scope:** customer feedback from support or sales into the backlog (`project-management/execution/customer-feedback-triage/`); which work agents may take and review capacity (`project-management/execution/agents-in-the-team/`); prioritising accepted work (`project-management/execution/prioritization-frameworks/`); incident response (`project-management/execution/post-mortem/`).

**Important Caveats:**
- Both tools read exported JSON or markdown; neither calls a tracker API or changes labels.
- The brief linter catches structure and wording, not wrong intent. A person reads every brief before the state changes.
- Path and vague-word detection are regex heuristics; expect occasional false positives.
