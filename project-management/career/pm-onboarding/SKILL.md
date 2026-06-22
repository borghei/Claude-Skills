---
name: pm-onboarding
description: >
  30-60-90 day plan for a new PM joining a company or team, grounded in Michael
  Watkins' First 90 Days framework and the STARS situational diagnosis. Includes
  week-by-week plan, stakeholder map, 1:1 question bank, and first-PRD template.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: pm-career
  updated: 2026-06-15
  tech-stack: pm-onboarding, 30-60-90, first-90-days, stars-framework
---
# PM Onboarding Expert

## Overview

A new PM's first 90 days are disproportionately important. Trust earned in the first quarter compounds; missteps in the first quarter haunt for the next year. This skill is a structured 30-60-90 day plan that helps a new PM diagnose the situation, build relationships, identify early wins, and arrive at the end of the quarter with credibility and a clear point of view.

The skill draws on Michael Watkins' *The First 90 Days*, the STARS situational diagnosis (Start-up / Turnaround / Accelerated growth / Realignment / Sustaining success), and the public PM onboarding patterns popularized by senior product leaders.

### The arc in brief

- **Days 1-30 (Learn):** build context; no major decisions, no big PRDs. End with a 1-page "What I'm learning" memo (STARS diagnosis + top-3 going well + top-3 risks).
- **Days 31-60 (Plan):** form a point of view; interview customers yourself; identify 1-2 early wins; align manager + stakeholders. End with a first PRD/strategy memo and draft 6-month roadmap.
- **Days 61-90 (Deliver):** ship the early win; set the operating cadence; write the 90-day retro memo.

Diagnose the STARS situation first — a Sustaining-success area rewards 60+ days of listening; a Turnaround needs decisive action within 30. Misreading the situation is the most common new-PM mistake.

### When to Use

- **New job at a new company** -- use the full 90-day plan from week 1.
- **Internal transfer to a new team** -- compress to 60 days but keep the structure.
- **New scope within the same team** -- use the 30-day learning sprint only.
- **Returning from extended leave (3+ months)** -- use a modified 30-day plan to re-orient.

### When NOT to Use

- First week of a routine role (no major scope change) -- this is overkill.
- Interim leadership (acting role <60 days) -- run a stability-focused playbook instead.

## Clarify First

Before building the onboarding plan, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **STARS situation** — Start-up, Turnaround, Accelerated-growth, Realignment, or Sustaining-success (sets the listen-vs-act balance; misreading it is the top new-PM mistake)
- [ ] **Transition type** — new company, internal transfer, new scope, or return from leave (chooses full-90 vs compressed-60 vs 30-day plan)
- [ ] **Manager's 90-day expectations** — what "success" means to them (anchors early-win selection and the whole arc)
- [ ] **Scope and key partners** — what the PM owns and who the critical stakeholders are (drives the stakeholder tiers and first-PRD)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## References

Load the reference that matches the task; keep this file lean and pull detail on demand.

- **[references/30-60-90-plan-and-tactics.md](references/30-60-90-plan-and-tactics.md)** — full STARS diagnostic table and diagnosis questions, the week-by-week 30-60-90 plan with outputs, the early-wins playbook, onboarding stakeholder tiers, the first-PRD rules, the run-the-quarter workflow, troubleshooting, and success criteria. Read this when actually building or running the plan.
- **[references/first-90-days-playbook.md](references/first-90-days-playbook.md)** — Watkins-grounded deep dive: the transition trap, STARS in depth, securing early wins, the five-conversations framework, remote/hybrid onboarding, and the 90-day retro memo structure. Read for the underlying theory.
- **[references/red-flags.md](references/red-flags.md)** — bad-vs-good examples of early-tenure decisions. Scan after producing a 30-60-90 plan, stakeholder map, or onboarding artifact.
- `assets/30_60_90_plan.md` — editable 30-60-90 plan template.
- `assets/stakeholder_map.md` — onboarding stakeholder map template.
- `assets/onboarding_1on1_questions.md` — question bank for the first 30 days of 1:1s.
- `assets/first_prd_template.md` — tighter PRD template for new-PM constraints.

External: Watkins, M. *The First 90 Days* (HBR Press, 2013); Bock, L. *Work Rules!* (onboarding at scale).

## Scope & Limitations

**In Scope:** 30-60-90 day plan for new PM roles; STARS situational diagnosis; onboarding stakeholder mapping; first-quarter 1:1 question banks; first-PRD template; early-win identification and execution.

**Out of Scope:** Job-search or offer-evaluation prep (use `personal-productivity/`); compensation negotiation; long-term career planning beyond 90 days (`pm-career-ladder/`); onboarding for non-PM roles.

**Caveats:** The 90-day plan is a planning artifact, not a contract — adjust as you learn. Calibrate "early wins" to the company's pace (a startup's 90-day win may be an enterprise's 180-day win). Your manager's expectations matter most: align in week 1, do not surprise them in week 6.

## Integration Points

| Integration | Direction | What Flows |
|-------------|-----------|------------|
| `pm-1on1s/` | Feeds into | The 1:1 question banks here are designed for first-90-day conversations; ongoing 1:1s use the broader skill |
| `pm-career-ladder/` | Feeds into | End-of-90-day retro becomes the baseline self-score on the ladder |
| `pm-interview-prep/` | Receives from | Pre-offer "Can you do the job?" stories often map to early wins delivered in past 90-day windows |
| `senior-pm/stakeholder-mapper/` | Reuses | The stakeholder mapping technique scales beyond onboarding into steady-state |
| `execution/create-prd/` | Feeds into | First-PRD template is a tighter version of the full PRD skill |
| `discovery/interview-synthesis/` | Reuses | Customer interviews in week 5 use the same synthesis discipline as steady-state discovery |
