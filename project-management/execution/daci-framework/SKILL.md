---
name: daci-framework
description: >
  DACI decision facilitation framework (Driver, Approver, Contributor, Informed)
  for clarifying decision ownership, reducing decision thrash, role assignment,
  and governance design across product teams.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-06-15
  tech-stack: daci, decision-framework, governance
---
# DACI Decision Framework

## Overview

Clarify decision ownership and reduce decision thrash using the DACI framework (Driver, Approver, Contributor, Informed). Unlike RACI which focuses on task responsibility, DACI is purpose-built for product decisions -- who drives the decision to closure, who has veto power, who provides input, and who needs to know.

The four roles in brief: **Driver** (exactly one, drives to closure), **Approver** (1-2 max, holds veto), **Contributor** (input without veto), **Informed** (notified, not consulted). Build a chart by mapping current state, finding pain points, designing target state, and rolling out a 30/60/90 transition. See the playbook reference for role rules, the 7-step build sequence, and health metrics.

## When to Use

- **New team formation** -- A new cross-functional group needs clear decision-making roles.
- **Decision thrash** -- Decisions stall because nobody knows who has authority.
- **Scaling teams** -- Growth creates ambiguity about who owns which decisions.
- **Post-incident** -- A failed launch or missed deadline reveals unclear ownership.
- **Reorg transitions** -- Role changes create governance gaps.

### When NOT to Use

- Task assignment or project execution (use RACI instead).
- Individual contributor work allocation (use sprint planning).
- Truly one-person decisions (no governance overhead needed).

## Clarify First

Before building the DACI chart, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **The specific decisions to map** — the 3-5 high-impact decisions, not "everything" (each becomes a chart row; mapping too much at once is the top failure mode)
- [ ] **Candidate people and their real authority** — who can actually approve or veto (drives the Driver and Approver assignments; without genuine authority the chart is fiction)
- [ ] **Current pain points** — where decisions stall or thrash today (drives the current→target-state gap and the 30/60/90 transition plan)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## References

- **[references/playbook.md](references/playbook.md)** — read this when building or running a DACI chart: role definitions and rules, the 7-step build sequence (working group → roles → decisions → current-state map → pain points → target-state → transition plan), governance health metrics, troubleshooting, and success criteria.
- **[references/red-flags.md](references/red-flags.md)** — read this before publishing a chart or running a decision under it: common ways a DACI chart goes wrong with bad/good examples anchored to the role rules.

## Scope & Limitations

**In Scope:** DACI chart creation, current-state mapping, target-state design, transition planning, governance health metrics, pain point identification, decision ownership clarity.

**Out of Scope:** Task assignment (use RACI), project execution tracking (use sprint planning), individual performance management, organizational design beyond decision governance.

**Important Caveats:** DACI works best when leadership commits to respecting the framework. Without executive buy-in, Drivers may lack the authority to actually drive decisions. Start with 3-5 high-impact decisions rather than trying to map everything at once.

## Integration Points

| Integration | Direction | What Flows |
|---|---|---|
| `create-prd/` | Feeds into | DACI decisions inform PRD Contacts section and decision log |
| `identify-assumptions/` | Complements | Surfaces assumptions about who has authority |
| `brainstorm-okrs/` | Complements | OKR ownership aligns with DACI decision ownership |
| `summarize-meeting/` | Feeds into | Meeting summaries capture DACI decision outcomes |
| `senior-pm/` | Complements | Portfolio-level DACI for cross-project decisions |

## Further Reading

- Productside DACI guidance for product teams
- Inspired by the DACI framework used at Intuit and other product-led organizations
