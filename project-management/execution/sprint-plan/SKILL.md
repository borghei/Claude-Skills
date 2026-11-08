---
name: sprint-plan
description: >
  Build and audit the plan for one iteration: goal, real capacity, commit vs stretch,
  dependencies, risks and definition of done. Use when planning the next
  sprint or auditing a plan for a team that keeps missing its sprints.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: project-management
  domain: execution
  updated: 2026-11-08
  python-tools: sprint_planner.py
  tech-stack: sprint-planning, capacity, agile, story-points
  tags:
    - sprint-planning
    - capacity
    - commitment
    - scrum
    - risk
---

# Sprint Planning

The goal is a plan the team actually finishes: one sentence of purpose, commits sized to real
capacity, a small stretch nothing depends on, and every dependency and risk owned before day 1.
Done means `sprint_planner.py` reports no `fail` findings and every `warn` is either fixed or
accepted out loud.

## When to Use

- Sprint kickoff (every 1-3 weeks) or a template for a new team
- Auditing the plan of a team that misses most sprints
- Gap analysis after a missed sprint

Backlog refinement before the sprint, story splitting and retrospectives are separate skills (see Scope).

## Clarify First

Before generating the sprint plan, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Sprint goal:** the one-sentence outcome; it is what lets the team say no to off-goal asks.
- **Real team capacity:** per-person hours after PTO, on-call, meetings and interrupts, times a focus factor. This sizes the commit.
- **Backlog readiness:** candidate items refined, estimated and ≤5 days each; unrefined items blow up mid-sprint.
- **Known dependencies:** cross-team or external blockers with an owner who has confirmed.

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Workflow

1. **Goal.** One sentence stating an outcome, not a feature list ("customers can pay with a saved card", not "ship X, Y, Z"). You should be able to say at the end whether it was met.
2. **Capacity.** Per person: (sprint days − PTO − holidays) × hours/day, minus meetings, on-call and interrupt tax, times a focus factor (0.6-0.75 is a common starting point; calibrate against actuals). Sum it. Make sure `total_available_hours` equals the per-person sum, or say why not. Worked math: `references/capacity-math.md`.
3. **Eligible items.** Only refined, estimated items of ≤5 days (≤8 points). Send the rest back to refinement or split them.
4. **Commit vs stretch** [RECOMMENDED]. Commits about 80% of capacity (75-85%), stretch about 10%, and keep total fill at or under 90%. The reason: unplanned work takes 10-20% of most sprints, so plans filled past 90% usually miss and past 100% always do. Cross-check commit points against average velocity of the last 3-5 sprints.
5. **Dependencies.** Each one has an owner, a needed-by date and the owner's confirmation. Unconfirmed is a risk, not a plan.
6. **Risks.** One or two per commit item (technical, dependency, estimate, key person), each with mitigation and owner.
7. **Definition of done.** Per item; the default set the audit checks is code reviewed, tests, telemetry, docs. Add a11y, QA or flag configuration where they apply.
8. **Audit and fix** until there are no `fail` findings:

```bash
python3 project-management/execution/sprint-plan/scripts/sprint_planner.py \
  --input project-management/execution/sprint-plan/assets/sample_sprint_plan.json --format markdown
```

Mid-sprint, when commits turn out too big: drop stretch first, then descope a commit early and tell stakeholders. Adding hours is rarely real capacity.

## Tool: `sprint_planner.py`

Reads a JSON plan (shape in `--help` and `assets/sample_sprint_plan.json`) and reports findings by severity.

| Severity | Checks |
|---|---|
| fail | No goal, no capacity, no items; commits exceed capacity; commit + stretch over 100% of capacity |
| warn | Commit + stretch over 90%; commits over 1.1 × commit target; per-member hours not matching the total (±5%); commit target over 90%; commit points over average velocity; unrefined items; items ≥13 points; no assignee; dependencies without owner or confirmation |
| info | Stretch well over its target; commit items with no risks; missing default DoD items |

Flags: `--input FILE` (required), `--format json|markdown` (default json), `--output FILE`.

**Exit codes:** 0 no `fail` findings, 1 at least one `fail` (`assets/sample_sprint_plan_flawed.json` exits 1 by design: 117% fill), 2 missing file, invalid JSON or wrong shape.

## Anti-Patterns

### Filling to 100%
**Mistake:** Commits plus stretch add up to all available hours.
**Why it happens:** Every item feels important and empty capacity looks like waste.
**Instead:** Commit about 80%, stretch about 10%; the rest absorbs the unplanned work that always arrives.

### A feature list instead of a goal
**Mistake:** The goal reads "ship A, B and C".
**Why it happens:** Listing items is easier than naming the outcome they serve.
**Instead:** Name the outcome; when one item slips, the goal tells you what to protect.

### Committing unrefined items
**Mistake:** An item with open questions goes into commits "to get started".
**Why it happens:** The item is urgent and refinement was skipped.
**Instead:** Refine first or make it stretch; discovered complexity is the main source of mid-sprint blowups.

### Assumed dependencies
**Mistake:** "Platform will have the API ready" with no named owner who agreed.
**Why it happens:** Asking feels like friction; the other team's plan is assumed.
**Instead:** Get the owner's confirmation and date in the plan, or list it as a risk with a mitigation.

### Capacity without PTO and on-call
**Mistake:** Team size × sprint days × 8 hours.
**Why it happens:** It is quick and looks precise.
**Instead:** Compute per person and reconcile with the total; most teams overestimate capacity this way by a third or more.

More, with fixes and a bad-to-good worked plan: `references/sprint-anti-patterns.md`.

## Files

| File | Purpose |
|---|---|
| `scripts/sprint_planner.py` | Plan audit (above) |
| `assets/sample_sprint_plan.json` | Sound plan: 86% fill, exits 0 |
| `assets/sample_sprint_plan_flawed.json` | Over-filled plan with mismatched capacity, unrefined items, unowned dependency; exits 1 |
| `assets/sprint_plan_template.md` | Plan document template |

## References

- `references/capacity-math.md` — per-person formula, focus factor, capacity drains, role and quarter capacity. Read when computing capacity.
- `references/sprint-anti-patterns.md` — 15 failure modes with fixes and a worked plan. Read when auditing a team that keeps missing.

## Scope & Limitations

**In Scope:** goal, capacity, commit and stretch, dependencies, risks and DoD for one sprint; auditing that plan; diagnosing repeatedly missed sprints.

**Out of Scope:** refining and estimating items (`project-management/execution/backlog-refinement/`); splitting large stories (`project-management/execution/story-splitting/`); review capacity for agent-delegated work (`project-management/execution/agents-in-the-team/`); retrospectives (`project-management/sprint-retrospective/`); quarter planning (`project-management/execution/quarterly-planning/`); velocity and flow metrics (`project-management/execution/cycle-time-analyzer/`).

**Important Caveats:**
- The tool reads a hand-written JSON plan; it does not pull from Jira, Linear or calendars.
- `refined` and dependency `confirmed` are self-reported. The tool checks that they are set, not that they are true.
- The goal, what is commit or stretch, and mid-sprint descoping stay team decisions.
