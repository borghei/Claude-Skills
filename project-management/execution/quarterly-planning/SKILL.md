---
name: quarterly-planning
description: >
  Run the full quarterly planning cycle -- pre-quarter homework, kickoff,
  weekly Wodtke rhythm, mid-quarter check-in, and close retro -- using Radical
  Focus, Cagan strategy, and the Reforge cycle around your OKRs.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-06-15
  tech-stack: quarterly-planning, okrs, product-strategy, radical-focus
---
# Quarterly Planning Expert

## Overview

Quarterly planning is the operating cadence that turns annual strategy into quarterly outcomes. Done well, it produces aligned OKRs, a roadmap that delivers them, a capacity plan that respects reality, and a tracking ritual that catches drift before it compounds. Done poorly, it produces OKR theater -- a slide deck of objectives that nobody references after week two.

This skill is the **above-OKR-writing** companion to `execution/brainstorm-okrs/`. Where `brainstorm-okrs/` covers how to write good OKRs, this skill covers the full quarterly cycle around them: pre-quarter homework, kickoff agenda, mid-quarter check-in, close-of-quarter retro, and the weekly/biweekly tracking cadence. The framework synthesizes four sources: Wodtke's *Radical Focus* (Monday-commit / Friday-celebrate rhythm, one OKR per quarter), Reforge's product strategy cycle, Cagan's quarterly product strategy, and the RAD ritual (Reflect-Align-Decide) used inside each meeting.

## Core Capabilities

- **Pre-quarter homework** -- strategy review, outcome candidate list, capacity assessment, and the 1-page kickoff brief
- **Kickoff facilitation** -- the 2-3hr RAD agenda that commits OKRs, roadmap, and capacity
- **Weekly Wodtke rhythm** -- Monday Commit, Friday Celebrate, biweekly KR confidence review
- **Mid-quarter check-in** -- carry / kill / pivot / escalate decisions at week 6
- **Close retro** -- 0.0-1.0 OKR scoring, learning extraction, and next-cycle seeding

## Clarify First

Before running a phase, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Which phase** — pre-quarter/kickoff vs mid-quarter check-in vs close retro (selects the agenda and artifacts produced)
- [ ] **Position in the 13-week cycle** — what week you're in (the carry/kill/pivot check belongs at ~week 6, the retro at week 13)
- [ ] **Existing OKRs & strategy** — the committed Objective and the annual strategy it serves (the kickoff commits OKRs; every Objective must trace to a vision pillar)
- [ ] **Real team capacity** — honest capacity after PTO/on-call (a stretch slate dressed as commitments is the #1 cadence failure)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## The Quarterly Cycle

```
Week -3   -1     0       1-5    6      7-12    13
  | Pre-quarter | Kickoff |  Mid-quarter  | Close
  |  homework   | (start) |   check-in    | retro
  +--Reforge/Cagan--+-- Wodtke weekly Mon/Fri rhythm --+
```

- **Pre-quarter (weeks -3 to -1):** run the homework and kickoff to commit OKRs and roadmap.
- **Mid-quarter (~week 6):** run the check-in to course-correct.
- **Close (week 13):** run the retro to extract learning before the next cycle.

## When to Use

- **Pre-quarter (2-3 weeks before start).** Run the homework and kickoff to commit OKRs and roadmap.
- **Mid-quarter (~week 6 of 13).** Run the mid-quarter check-in to course-correct.
- **Close-of-quarter (last week).** Run the close retro to extract learning before next planning cycle.
- **New PM joining mid-quarter.** Understand where the team is in the cycle and what is expected when.
- **Failing OKR cadence.** Team has OKRs but no one references them by week 4 -- reset the ritual.

## References

Load the reference that matches the task -- keep this file lean and pull detail on demand:

- **[references/cycle-playbook.md](references/cycle-playbook.md)** -- the full operational playbook: pre-quarter homework + kickoff brief template, kickoff / mid-quarter / close agendas, the weekly Wodtke rhythm scripts, anti-patterns, artifacts-produced map, troubleshooting, and success criteria. Read this when running any phase of the cycle.
- **[references/quarterly-planning-guide.md](references/quarterly-planning-guide.md)** -- the framework theory (Wodtke Radical Focus, Cagan product strategy, Reforge cycle, RAD ritual) with a worked Reconcile Q3 example. Read this when you need the reasoning behind the rituals.
- **[references/red-flags.md](references/red-flags.md)** -- 11 quarterly-planning anti-patterns (OKR theater, capacity in story points, stretch goals as committed slate) with symptoms and fixes. Read this when reviewing a quarter's plan or diagnosing a failing cadence.

Templates live in `assets/`: `kickoff_agenda_template.md`, `mid_quarter_check_in_template.md`, `close_retro_template.md`, `quarterly_review_deck_outline.md`.

## Scope & Limitations

**In scope:** pre-quarter homework (strategy, outcomes, capacity); kickoff agenda; weekly Wodtke rhythm; biweekly KR confidence review; mid-quarter check-in; close retro; carry/kill/pivot framework; quarterly review deck outline.

**Out of scope:** writing individual OKRs (`execution/brainstorm-okrs/`); roadmap construction (`execution/outcome-roadmap/`); sprint-level planning (`scrum-master/`); multi-quarter / annual strategy (`c-level-advisor/`); performance management (`career/`); portfolio management (`program-manager/`).

**Caveats:** the cycle is the system -- skipping one ritual (especially the close retro) degrades the next quarter; OKRs are a tool for focus, not control (Wodtke argues one Objective per team per quarter); the skill assumes a 13-week quarter; it works best where the company has shared OKR practice.

## Integration Points

| Integration | Direction | What Flows |
|-------------|-----------|------------|
| `execution/brainstorm-okrs/` | Bidirectional | Quarterly cycle uses OKRs; OKR drafting is a kickoff sub-skill |
| `execution/outcome-roadmap/` | Bidirectional | Quarterly OKRs become Now-horizon roadmap; roadmap themes inform candidate outcomes |
| `execution/north-star-metric/` | Receives from | NSM is the long-term metric; quarterly KRs are short-term moves on it |
| `execution/product-vision/` | Receives from | Every Objective must trace to a vision pillar |
| `execution/dependency-map/` | Receives from | Pre-quarter dependency mapping prevents week-6 surprises |
| `execution/status-update-generator/` | Feeds into | Weekly Wodtke rhythm produces input for exec status updates |
| `execution/cycle-time-analyzer/` | Receives from | Flow metrics inform capacity assessment |
| `discovery/customer-interview-script/` | Receives from | Recent customer signal feeds the strategy review |
| `discovery/jtbd-workshop/` | Receives from | Top desired outcomes seed the outcome candidate list |
| `scrum-master/` | Feeds into | Quarterly OKRs cascade into sprint capacity planning |
| `senior-pm/` | Feeds into | Quarterly artifacts inform portfolio-level reporting |
| `career/pm-onboarding/` | Complementary | New PMs use this skill in their 30-60-90 plan to ramp on team cadence |
