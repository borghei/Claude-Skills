---
name: backlog-refinement
description: >
  Backlog refinement playbook covering INVEST quality, vertical story splitting,
  Definition of Ready, and Definition of Done -- with a Python scorer that grades
  each story against INVEST and emits a ready/not-ready verdict.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-06-15
  python-tools: refinement_scorer.py
  tech-stack: invest, story-splitting, definition-of-ready, definition-of-done
---
# Backlog Refinement Expert

## Overview

Refinement is the most under-invested ritual in agile teams. Stories arrive at sprint planning oversized, ambiguous, or strategically disconnected, and the team spends planning meetings doing what should have happened the week before. This skill is the refinement playbook: grade stories against INVEST, split them vertically (so each slice ships value end-to-end), and keep a working Definition of Ready and Definition of Done that prevent half-baked work from entering or leaving a sprint.

The skill includes a Python scorer (`refinement_scorer.py`) that grades each story in a JSON backlog against the six INVEST criteria and outputs a readiness score (0-6) per story. Stories scoring 5-6 are sprint-ready; 3-4 need targeted refinement; below 3 go back to discovery.

This complements `wwas/` (Why-What-Acceptance format) and `job-stories/` (JTBD format). Either format produces stories; this skill grades them and gets them sprint-ready.

## Core Capabilities

- **INVEST grading** — score each story across Independent, Negotiable, Valuable, Estimable, Small, Testable (0-6) and triage by score.
- **Vertical story splitting** — the 9 Lawrence recipes + SPIDR taxonomy; avoid horizontal (layer/team/sprint) splits.
- **Definition of Ready / Done** — input and output quality gates with enforceable templates.
- **Refinement session structure** — cadence, candidate volume, triage routing into discovery or planning.

## When to Use

- **Weekly refinement session** -- grade next-sprint candidates against INVEST and split anything too large.
- **Backlog hygiene sweep** -- re-grade the top 30 items and retire what no longer connects to strategy.
- **Sprint planning input** -- confirm all candidates pass DoR before planning.
- **New team onboarding** -- establish a shared definition of "ready" and "done."
- **Velocity diagnosis** -- erratic sprint completion usually traces to refinement quality.

**When NOT to use:** pure technical task lists with no user-facing outcome (use a simpler checklist); ad-hoc bug triage (different lifecycle); unscoped work (send to `discovery/` first).

## Clarify First

Before grading the backlog, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **The stories** — the actual backlog items in the user's words, with their acceptance criteria (drives every INVEST score and which slicing recipe applies)
- [ ] **Team's Definition of Ready** — what "ready" means for THIS team (DoR must be team-authored to be enforced; sets the promote/refine/return gate)
- [ ] **Sprint size / "small enough" bar** — sprint length and rough capacity (sets how far a story must be split before it counts as Small)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Quick Start

```bash
python scripts/refinement_scorer.py --input backlog.json --format markdown   # grade a backlog
python scripts/refinement_scorer.py --demo --format markdown                 # inspect demo + output
```

Triage by score: **5-6** promote to Refined, **3-4** discuss and fix the failing criteria, **0-2** send back to discovery.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/refinement-playbook.md](references/refinement-playbook.md)** — full INVEST table, the 9 splitting recipes + SPIDR, DoR/DoD templates and anti-patterns, the step-by-step workflow, the `refinement_scorer.py` reference (flags, input JSON, scoring rubric), troubleshooting, and success criteria. Read when running a refinement session or wiring the scorer.
- **[references/invest-and-splitting-guide.md](references/invest-and-splitting-guide.md)** — deep dive on INVEST (Wake), the 9 Lawrence patterns, SPIDR (Cohn), and worked horizontal-vs-vertical split examples. Read when a story is hard to split or a slice feels wrong.
- **[references/red-flags.md](references/red-flags.md)** — concrete examples of how refinement output goes wrong, why it's bad, and how to fix it. Read when reviewing a refined backlog or diagnosing recurring quality issues.
- **assets/refinement_checklist.md** — ready-to-use DoR and DoD checklists plus a refinement session agenda. Use during a live session.

## Scope & Limitations

**In Scope:** INVEST grading of individual stories; vertical splitting (9 Lawrence patterns + SPIDR); DoR/DoD templates and enforcement; refinement session structure and cadence; the Python scorer.

**Out of Scope:** authoring stories from scratch (`wwas/`, `job-stories/`); prioritization/sequencing (`prioritization-frameworks/`); sprint planning/capacity/velocity (`../scrum-master/`); discovery and problem framing (`discovery/`); estimation techniques (`agile-coach/`).

**Caveats:** INVEST is a heuristic — a 6/6 story can still be the wrong story (pair with `prioritization-frameworks/` and `discovery/identify-assumptions/`). DoR/DoD must be team-authored to be enforced. The scorer grades structural form, not strategic substance.

## Integration Points

| Integration | Direction | Description |
|-------------|-----------|-------------|
| `execution/wwas/` | Receives from | WWAS-format stories enter refinement to be graded and split |
| `execution/job-stories/` | Receives from | Job stories enter refinement to be graded and split |
| `execution/prioritization-frameworks/` | Pairs with | Prioritization sets the sequence; refinement makes the top N executable |
| `discovery/identify-assumptions/` | Sends to | Stories scoring 0-2 are sent back for assumption mapping |
| `discovery/brainstorm-experiments/` | Sends to | Stories with unvalidated assumptions become experiment candidates |
| `../scrum-master/` | Feeds into | Refined stories feed sprint planning; refinement quality drives velocity stability |
| `execution/status-update-generator/` | Indirect | DoD compliance feeds the "what's done this week" section of status updates |
| `../jira-expert/` | Pairs with | Refined stories become Jira tickets with structured fields and DoR/DoD checklists |
