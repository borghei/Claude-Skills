---
name: quarterly-planning
description: >
  Run the meetings around a quarter's OKRs: homework and kickoff, weekly
  check-ins, the week-6 carry/kill/pivot review and the close retro. Use when
  running any phase of that cadence; writing the OKRs is brainstorm-okrs.
license: MIT + Commons Clause
metadata:
  version: 1.0.2
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-11-08
  tech-stack: quarterly-planning, okrs, product-strategy, radical-focus
  tags:
    - quarterly-planning
    - okrs
    - radical-focus
    - planning-cycle
---
# Quarterly Planning Expert

## Overview

Quarterly planning is the operating cadence that turns annual strategy into quarterly outcomes. Done well, it produces aligned OKRs, a roadmap that delivers them, a capacity plan that respects reality, and a tracking ritual that catches drift before it compounds. Done poorly, it produces OKR theater -- a slide deck of objectives that nobody references after week two.

This skill is the **above-OKR-writing** companion to `execution/brainstorm-okrs/`. Where `brainstorm-okrs/` covers how to write good OKRs, this skill covers the full quarterly cycle around them: pre-quarter homework, kickoff agenda, mid-quarter check-in, close-of-quarter retro, and the weekly/biweekly tracking cadence. Each meeting uses a Reflect-Align-Decide agenda; the theory behind the rhythm is in `references/quarterly-planning-guide.md`.

## Core Capabilities

- **Pre-quarter homework** -- strategy review, outcome candidate list, capacity assessment, and the 1-page kickoff brief
- **Kickoff facilitation** -- the 2-3hr RAD agenda that commits OKRs, roadmap, and capacity
- **Weekly Wodtke rhythm** -- Monday Commit, Friday Celebrate, biweekly KR confidence review
- **Mid-quarter check-in** -- carry / kill / pivot / escalate decisions at week 6
- **Close retro** -- 0.0-1.0 OKR scoring, learning extraction, and next-cycle seeding

## Clarify First

Before running a phase, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Which phase:** pre-quarter/kickoff vs mid-quarter check-in vs close retro (selects the agenda and artifacts produced).
- **Position in the 13-week cycle:** what week you're in (the carry/kill/pivot check belongs at ~week 6, the retro at week 13).
- **Existing OKRs & strategy:** the committed Objective and the annual strategy it serves (the kickoff commits OKRs; every Objective must trace to a vision pillar).
- **Real team capacity:** honest capacity after PTO/on-call (a stretch slate dressed as commitments is the #1 cadence failure).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Workflow

Pick the phase from where the team is in the 13-week cycle, then run that phase's agenda from `references/cycle-playbook.md`.

| Phase | When | Output | Done when |
|---|---|---|---|
| Pre-quarter homework | Weeks -3 to -1 | 1-page kickoff brief: strategy recap, outcome candidates, real capacity | Every candidate Objective traces to a strategy pillar; capacity is in hours after PTO and on-call |
| Kickoff | Week 0 | Committed OKRs, roadmap slice, capacity plan | Commitments fit capacity; stretch is labelled as stretch |
| Weekly rhythm | Weeks 1-12 | Monday commitments, Friday wins, KR confidence every two weeks | Confidence is recorded for every KR, not just the green ones |
| Mid-quarter check-in | About week 6 | Carry / kill / pivot / escalate per KR | Each KR has a decision and an owner; anything rebaselined says why |
| Close retro | Week 13 | KR scores (0.0-1.0), lessons, seeds for next quarter | Each miss has a cause, and next quarter's homework starts from it |

Week 6 is the default for the check-in [RECOMMENDED] because it leaves enough quarter to act on a kill or pivot; move it earlier for six-week cycles.

## When to Use

- **Any phase of the quarter** listed in the Workflow table.
- **New PM joining mid-quarter.** Understand where the team is in the cycle and what is expected when.
- **Failing OKR cadence.** Team has OKRs but no one references them by week 4 -- reset the ritual.

## Anti-Patterns

### Key results that are activities
**Mistake:** "KR: launch the new pricing page by June 1." The KR is a deliverable.
**Why it happens:** Deliverables are easy to plan and score, and shipping feels like success.
**Instead:** Rewrite each KR as a measurable change, for example "free-to-paid conversion >= 4.5% by June 30", and treat the deliverable as the bet behind it. A KR built on ship, launch, build or complete with no downstream metric needs a rewrite.

### Dependencies found mid-quarter
**Mistake:** In week 6, Team A discovers it needs an API that Team B never put in its slate.
**Why it happens:** Each team plans its own slate, and the cross-team check feels like extra overhead.
**Instead:** Before kickoff, have every team list its initiatives and dependencies. Run a reconciliation session in week 0, and cut scope where the other team can't commit. No documented week-0 session means mid-quarter surprises.

### A mid-quarter check-in with no authority to rebaseline
**Mistake:** The week-6 check-in finds KR2 off-track, and the answer is "push harder".
**Why it happens:** Descoping feels like admitting failure, so nobody is given the authority.
**Instead:** Bring carry, kill, pivot and escalate options to the check-in, such as descope the KR, borrow capacity, or drop another KR. Record the decision and who signed off. A check-in with no rebaseline decisions was a status meeting.

Eight more, each with a bad and a good example: `references/red-flags.md`.

## References

Load the reference that matches the task -- keep this file lean and pull detail on demand:

- **[references/cycle-playbook.md](references/cycle-playbook.md)** -- the full operational playbook: pre-quarter homework + kickoff brief template, kickoff / mid-quarter / close agendas, the weekly Wodtke rhythm scripts, anti-patterns, artifacts-produced map, troubleshooting, and success criteria. Read this when running any phase of the cycle.
- **[references/quarterly-planning-guide.md](references/quarterly-planning-guide.md)** -- the framework theory (Wodtke Radical Focus, Cagan product strategy, strategy cycle, RAD ritual) with a worked Reconcile Q3 example. Read this when you need the reasoning behind the rituals.
- **[references/red-flags.md](references/red-flags.md)** -- 11 quarterly-planning anti-patterns (OKR theater, capacity in story points, stretch goals as committed slate) with symptoms and fixes. Read this when reviewing a quarter's plan or diagnosing a failing cadence.


## Files

| File | Purpose |
|---|---|
| `assets/kickoff_agenda_template.md` | Kickoff agenda |
| `assets/mid_quarter_check_in_template.md` | Week-6 check-in |
| `assets/close_retro_template.md` | Close retro |
| `assets/quarterly_review_deck_outline.md` | Quarterly review deck outline |
| `examples/northwind-q4-planning-cycle.md` | Worked cycle |

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
