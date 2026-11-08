---
name: daci-framework
description: >
  Assign Driver, Approver, Contributor and Informed roles for the decisions
  that keep stalling, then roll the chart out. Use when decisions thrash,
  ownership is unclear after a reorg, or a new team needs decision rights.
license: MIT + Commons Clause
metadata:
  version: 1.0.2
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-11-08
  tech-stack: daci, decision-framework, governance
  tags:
    - daci
    - decision-making
    - roles
    - governance
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

Before building the DACI chart, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **The specific decisions to map:** the 3-5 high-impact decisions, not "everything" (each becomes a chart row; mapping too much at once is the top failure mode).
- **Candidate people and their real authority:** who can actually approve or veto (drives the Driver and Approver assignments; without genuine authority the chart is fiction).
- **Current pain points:** where decisions stall or thrash today (drives the current→target-state gap and the 30/60/90 transition plan).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Workflow

1. **Pick 3-5 decisions** that stall or recur, not every decision the team makes.
2. **Map the current state** per decision: who actually decides today, who blocks late, where it stalls.
3. **Assign roles** [RECOMMENDED] per decision: exactly one Driver (one person drives to closure), one or two Approvers who hold real authority, at most 3-4 Contributors with expertise to add, everyone else Informed. Anyone who can stop the decision is a Contributor or Approver, never Informed.
4. **Agree the chart** with the Approvers named in it; a chart they have not accepted is fiction.
5. **Roll out** with a 30/60/90 plan and record each decision (option chosen, Approver, rationale, vetoes with reasons).

**Verify** before publishing: every row has one D and one or two A; no row has more than 5 C; every A has the authority in practice; the last few vetoes have written reasons. Build steps, health metrics and troubleshooting: `references/playbook.md`.

## Anti-Patterns

### Informed roles that object late
**Mistake:** Marketing is marked Informed on the launch date, objects three days before launch, and the date slips two weeks.
**Why it happens:** Teams mark a role Informed to keep meetings small, without asking whether that role can block the decision.
**Instead:** Make anyone who can stop the decision a Contributor or Approver from the start. Once the decision locks, a late objection goes to the Approver as an escalation.

### Everyone marked Contributor
**Mistake:** Most cells in the chart are C, so everyone expects to be consulted on everything.
**Why it happens:** Assigning C avoids hard conversations about who is left out.
**Instead:** Per decision, assign one D, one or two A, and at most 3-4 C. Give C only to roles with real expertise to add, and mark the rest I or leave them blank. More than 5 C cells on a row is a flag.

### Vetoes with no written reason
**Mistake:** The Driver proposes option A and the Approver says "No" with no follow-up. Two months later the same debate returns.
**Why it happens:** A veto feels like the end of the matter, so writing it up seems optional.
**Instead:** Ask Approvers to give every veto a written rationale and say what a counter-proposal would need to address. Keep these as decision records, and check the last 5 vetoes for them.

Nine more, each with a bad and a good example: `references/red-flags.md`.

## References

- **[references/playbook.md](references/playbook.md)** — read this when building or running a DACI chart: role definitions and rules, the 7-step build sequence (working group → roles → decisions → current-state map → pain points → target-state → transition plan), governance health metrics, troubleshooting, and success criteria.
- **[references/red-flags.md](references/red-flags.md)** — read this before publishing a chart or running a decision under it: common ways a DACI chart goes wrong with bad/good examples anchored to the role rules.

## Files

| File | Purpose |
|---|---|
| `references/playbook.md` | Role rules, 7-step build, health metrics |
| `references/red-flags.md` | Bad/good charts with fixes |
| `examples/choosing-payment-processor.md` | Worked DACI for one decision |

## Scope & Limitations

**In Scope:** DACI chart creation, current-state mapping, target-state design, transition planning, governance health metrics, pain point identification, decision ownership clarity.

**Out of Scope:** Task assignment (use RACI), project execution tracking (use sprint planning), individual performance management, organizational design beyond decision governance.

**Important Caveats:** DACI works best when leadership commits to respecting the framework. Without executive buy-in, Drivers may lack the authority to actually drive decisions. Start with 3-5 high-impact decisions rather than trying to map everything at once.

## Integration Points

| Integration | Direction | What Flows |
|---|---|---|
| `create-prd/` | Feeds into | DACI decisions inform PRD Contacts section and decision log |
| `discovery/identify-assumptions/` | Complements | Surfaces assumptions about who has authority |
| `brainstorm-okrs/` | Complements | OKR ownership aligns with DACI decision ownership |
| `summarize-meeting/` | Feeds into | Meeting summaries capture DACI decision outcomes |
| `senior-pm/` | Complements | Portfolio-level DACI for cross-project decisions |
