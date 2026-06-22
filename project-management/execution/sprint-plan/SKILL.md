---
name: sprint-plan
description: >
  Plan a sprint that ships — capacity, commitment vs stretch, dependencies,
  and risk identification that prevents mid-sprint surprises. Use to build
  the sprint planning artifact itself.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: project-management
  domain: execution
  updated: 2026-05-27
  python-tools: sprint_planner.py
  tech-stack: sprint-planning, capacity, agile, story-points
---

# Sprint Planning

A sprint plan that survives contact with reality. Covers capacity math,
commit vs stretch separation, dependency identification, and the
pre-sprint review that prevents mid-sprint surprises.

## When to use this skill

- **Sprint kickoff** (every 1-3 weeks)
- **Sprint-plan template** for new teams
- **Sprint-plan audit** when sprints consistently miss
- **Quarter-start planning** (rolled up across sprints)
- **Post-mortem** on a missed sprint (gap analysis)

## The 7 sprint-plan elements

1. **Sprint goal** — one sentence: what this sprint exists to achieve
2. **Team capacity** — actual hours / story points after PTO, on-call, etc.
3. **Commits** — items the team confidently ships
4. **Stretch** — items if everything goes well; nothing depends on
5. **Dependencies** — what must happen by when (external + internal)
6. **Risks** — what could derail; mitigation per risk
7. **Definition of done** — when is each item "done"?

## Clarify First

Before generating the sprint plan, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Sprint goal** — the one-sentence outcome this sprint exists to achieve (element 1; lets you scope and say no to off-goal asks)
- [ ] **Real team capacity** — working days minus PTO/on-call/meetings/interrupts × focus factor (element 2; sizes the commit and prevents the 100%-fill miss)
- [ ] **Backlog readiness** — are candidate items refined, estimated, and ≤5 days (unrefined items are ineligible and blow estimates mid-sprint)
- [ ] **Known dependencies** — cross-team/external blockers with owners (element 5; unconfirmed assumptions become mid-sprint crises)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Workflow

### Step 1 — Define the sprint goal
A good goal:
- One sentence
- States outcome, not output ("ship 3 features" → "complete checkout flow MVP enabling first paid customers")
- Inspires the team
- Lets you say "no" to off-goal asks

### Step 2 — Calculate capacity
Per team member:
- Working days = sprint days - holidays - approved PTO
- Effective hours = days × hours/day × focus factor (typically 0.6-0.75)
- Subtract on-call rotation hours
- Subtract meeting overhead
- Subtract support / interrupt tax

Aggregate across team. This is your real capacity.

### Step 3 — Pull from backlog
Backlog items must be:
- Refined (acceptance criteria clear)
- Estimated (story points or hours)
- No major unknowns

Items that fail this are NOT eligible for the sprint. Send back to refinement.

### Step 4 — Commit vs stretch
- **Commits:** 75-85% of capacity (leaves room for unknowns)
- **Stretch:** 10-15% of capacity (only if commits done)

Stuffing 100% of capacity = guaranteed miss. Reality always intrudes.

### Step 5 — Identify dependencies
For each item:
- Cross-team dependencies (what they need from others)
- External dependencies (vendors, customers)
- Sequencing dependencies (A blocks B)

Each dependency needs:
- Owner
- Date needed by
- Confirmation it's planned

### Step 6 — Identify risks
For each item, list likely risks:
- Technical risk
- Dependency risk (external owner slips)
- Estimate risk (unknowns might double effort)
- Capacity risk (key person may be pulled)

Per risk: likelihood, severity, mitigation, owner.

### Step 7 — Definition of done
Per item:
- Code merged + reviewed
- Tests added
- Telemetry firing
- Docs updated
- Accessibility checked
- Feature flag configured (if applicable)
- QA passed

### Step 8 — Run `sprint_planner.py`
Audit capacity utilization, commit/stretch split, dependency clarity,
DoD coverage.

```bash
python3 project-management/execution/sprint-plan/scripts/sprint_planner.py \
  --input sprint_plan.json --format markdown
```

## Decision frameworks

### Capacity math (per 2-week sprint, 8-person team)

```
2 weeks = 10 working days
Per person:
  - 10 days × 8 hours = 80 hours raw
  - Minus PTO/holidays (e.g., 1 day) = 72 hours
  - Minus meetings (~10 hrs) = 62 hours
  - Minus on-call (~4 hrs avg) = 58 hours
  - Minus interrupts/support (~6 hrs) = 52 hours
  - Focus factor 0.7 = ~36 hours of "real" work

Team of 8 × 36 hours = 288 effective hours
                     = ~28 person-days of real engineering work
```

Most teams over-estimate capacity by 30-50%. Track actuals to calibrate.

### Commitment discipline

| Filled at | Outcome |
|-----------|---------|
| 100%+ | Always miss |
| 90-100% | Usually miss; no room for unknowns |
| 80-90% | Often achievable; healthy |
| 70-80% | Conservative; safer commits |
| < 70% | Under-committing; team disengaged |

Target: 80% commits + 15% stretch.

### Sprint goal vs feature list

| Sprint goal | Why better |
|-------------|------------|
| "Complete checkout MVP" | Outcome-aligned; defines what "done" looks like |
| "Ship feature X + Y + Z" | Feature list; what if one slips? |
| "Improve performance" | Vague; no done state |

A good sprint goal lets you say "we did it" or "we didn't" clearly.

### Item sizing

Stories should be 1-5 days each. Stories > 5 days:
- Split into smaller stories
- Add a planning task to break them down
- Don't commit until refined

### When to descope vs add capacity

Mid-sprint, when you realize commit is too much:
- **Descope:** drop a stretch item; cleanly remove from sprint
- **Add capacity:** rare; usually means borrowing from next sprint
- **Push:** absolute last resort; deal carefully with stakeholders

Discipline: descope early. Heroic late nights = burnout + bugs.

## Common engagements

### "Plan our next sprint"
1. Pull team's velocity history (last 3-5 sprints).
2. Calculate this sprint's capacity.
3. Choose sprint goal aligned with quarter OKRs.
4. Pull from backlog; verify items refined.
5. Commit to 80%; stretch 15%.
6. Identify dependencies + risks.
7. Define done per item.

### "Why are we missing every sprint?"
1. Audit last 3 sprint plans + actuals.
2. Diagnose: over-commit? estimation? unrefined items? interrupts?
3. Tighten capacity math.
4. Increase refinement discipline.
5. Track interrupts; reduce them.

### "Quarter planning rolled up from sprints"
1. Define quarter goal (themes).
2. Identify ~6 sprints of capacity.
3. Allocate to: themes, tech debt, support, OKRs.
4. Draft per-sprint goals.
5. Refresh per sprint planning meeting.

## Anti-patterns to avoid

- **100% capacity commit.** Always miss.
- **Mid-sprint scope add without descope.** Burnout + bugs.
- **No sprint goal.** Random feature list.
- **Unrefined items committed.** Discovered complexity blows estimates.
- **Dependency assumption without owner confirmation.** Slips.
- **No risk identification.** Risks surface as crises.
- **No DoD.** "Done" varies by person.
- **Velocity ignored.** Repeat estimation mistakes.

## References

- `references/capacity-math.md` — deep on per-person capacity, focus factor, interrupt tax
- `references/sprint-anti-patterns.md` — common failures + fixes

## Related skills

- `project-management/scrum-master` — process facilitation
- `project-management/execution/backlog-refinement` — pre-sprint item prep
- `project-management/execution/story-splitting` — sizing large stories
- `project-management/execution/cycle-time-analyzer` — velocity tracking
- `project-management/sprint-retrospective` — post-sprint learning
- `c-level-advisor/vpe-advisor` — capacity planning at scale
