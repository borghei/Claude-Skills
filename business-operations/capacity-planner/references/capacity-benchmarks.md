# Capacity Benchmarks

Reference numbers for turning headcount into deliverable hours. Every figure here
is a starting default to be replaced by your own measured data within two
quarters. Use them to sanity-check a plan, not to win an argument.

---

## 1. The gross-to-effective waterfall

The single most common planning error is treating headcount as capacity. A
1.0 FTE engineer does not deliver 2,080 hours of roadmap work per year. The
waterfall below is what actually survives.

| Layer | Typical deduction | What it covers |
|-------|------------------|----------------|
| Calendar hours | 2,080 h/yr (260 d x 8 h) | Nominal full-time year |
| Public holidays | 8-13 days (64-104 h) | Jurisdiction-dependent |
| Paid time off | 15-25 days (120-200 h) | Vacation, taken not accrued |
| Sick / personal | 4-8 days (32-64 h) | Unplanned absence |
| Meetings + ceremony | 10-30% of remainder | Standups, planning, reviews, 1:1s, all-hands |
| Non-delivery overhead | 8-15% of remainder | Email, admin, training, interviews, compliance |
| On-call | 30-50% of the on-call week | Primary pager duty |
| Ramp | 0-100% multiplier | New hires and internal transfers |

### Effective-hours ratio by role [PROVEN]

Effective hours as a share of gross calendar hours, measured on delivery work:

| Role | Typical ratio | Notes |
|------|--------------|-------|
| Individual-contributor engineer, no on-call | 60-70% | The healthy ceiling for a mature team |
| IC engineer with on-call rotation | 50-60% | Rotation size drives the spread |
| Senior/staff engineer | 45-60% | Design review, mentoring, cross-team pull |
| Tech lead (still coding) | 30-45% | Assume half a person of delivery, at most |
| Engineering manager | 5-15% | Plan for zero; anything delivered is a bonus |
| Designer | 55-65% | Higher meeting load, lower interrupt load |
| QA / test engineer | 60-70% | Lower meeting load than engineering |
| Data analyst | 50-60% | High ad-hoc interrupt rate |
| Support / operations | 25-40% of time to projects | Rest is queue-driven |

**Planning rule [PROVEN]: use 60% for a fully-ramped IC on a team with a
5+ person on-call rotation, and 50% if the rotation is 4 or fewer.** If your
model produces above 80%, it is missing something — go find it before you commit
the quarter.

### Sanity thresholds

| Modelled effective ratio | Interpretation |
|-------------------------|----------------|
| Below 45% | Structurally broken. Meeting load or rotation size is the problem, not the roadmap. |
| 45-55% | Heavy overhead. Common in small teams carrying production. Reduce ceremony before hiring. |
| 55-70% | Healthy band. Most functional teams live here. |
| 70-80% | Optimistic. Verify PTO and interrupt assumptions are real, not aspirational. |
| Above 80% | Fiction. The plan omits at least one deduction layer. |

---

## 2. New-hire ramp curves

Ramp is the deduction planners most often skip, and it is the most expensive one
to skip because it hits exactly when the plan assumed relief was arriving.

### Monthly productivity multiplier by seniority [RECOMMENDED]

Multiplier of a fully-ramped peer's output, by completed months of tenure.

| Month | Junior | Mid | Senior | Staff / Principal |
|-------|--------|-----|--------|-------------------|
| 0 | 0.10 | 0.15 | 0.25 | 0.30 |
| 1 | 0.25 | 0.35 | 0.50 | 0.55 |
| 2 | 0.40 | 0.55 | 0.75 | 0.80 |
| 3 | 0.55 | 0.75 | 0.90 | 1.00 |
| 4 | 0.70 | 0.90 | 1.00 | 1.00 |
| 5 | 0.85 | 1.00 | 1.00 | 1.00 |
| 6 | 1.00 | 1.00 | 1.00 | 1.00 |

**Time to full productivity: junior 6 months, mid 5, senior 4, staff 3.**

Note what the curve implies: a mid-level engineer hired on the first day of a
quarter contributes roughly `(0.15 + 0.35 + 0.55) / 3 = 35%` of an FTE that
quarter. Two such hires are worth 0.7 of a person in their first quarter, not 2.

### Ramp modifiers

Multiply the curve by these when the situation applies:

| Situation | Modifier | Reason |
|-----------|----------|--------|
| Internal transfer, same tech stack | 1.4x (caps at 1.0) | Keeps org context, learns domain only |
| Internal transfer, new stack | 1.15x | Keeps org context, relearns craft |
| Returning alum (< 18 months away) | 1.5x (caps at 1.0) | Context largely intact |
| Unfamiliar domain (regulated, hardware, ML) | 0.75x | Domain knowledge dominates |
| No assigned onboarding buddy | 0.75x | Largest single controllable factor |
| No written onboarding path | 0.85x | Time lost rediscovering the obvious |
| Fully remote, distributed team | 0.90x | Slower informal context transfer |
| Team already above 85% utilisation | 0.80x | Nobody has time to onboard them |

The last row is the trap: hiring into an overloaded team ramps slower precisely
because the team is overloaded. Hiring is not a fast remedy for over-commitment.

### The negative-capacity window [PROVEN]

For roughly the first 4-6 weeks, a new hire consumes more senior capacity than
they produce. Budget **20-30% of one experienced person's time per new hire for
the first month**, tapering to 10% through month three. A team onboarding three
people at once has effectively lost a senior engineer for a quarter.

**Rule: do not onboard more than one new person per three existing team members
per quarter.** Above that ratio, team throughput falls in the hiring quarter.

---

## 3. On-call load

| Rotation size | Share of year on primary | Effective-hours cost per person |
|--------------|-------------------------|--------------------------------|
| 3 people | 33% | 13-17% of annual capacity |
| 4 people | 25% | 10-13% |
| 5 people | 20% | 8-10% |
| 6 people | 17% | 7-8% |
| 8 people | 12.5% | 5-6% |

The per-week cost of carrying the primary pager is **35-45% of that week's
capacity** on a system with normal alert volume, rising above 60% when weekly
paging exceeds five actionable alerts. If your on-call week costs more than half
the week, the fix is alert hygiene, not a larger rotation.

**Rotation floor [PROVEN]: 5 people.** Below that, burnout and attrition costs
exceed the headcount savings within a year.

---

## 4. Meeting and ceremony load

| Team practice | Weekly hours per IC | Share of a 40h week |
|--------------|--------------------|--------------------|
| Daily standup (15 min) | 1.25 | 3% |
| Sprint planning (2-week cadence) | 1.0 | 2.5% |
| Backlog refinement | 1.0 | 2.5% |
| Sprint review + retro | 1.0 | 2.5% |
| Manager 1:1 | 0.5 | 1.5% |
| Team meeting | 1.0 | 2.5% |
| Company all-hands (biweekly) | 0.5 | 1.5% |
| Design/architecture review | 1.0-2.0 | 2.5-5% |
| Interviews (active hiring) | 1.0-3.0 | 2.5-7.5% |
| Incident review | 0.5-1.5 | 1-4% |

A standard agile team runs **12-18% meeting load**. Above 25%, the calendar is
the bottleneck. Above 30%, the team cannot hold a two-hour block of focused work
and effective output collapses faster than the hours suggest — fragmentation
costs an additional 10-20% on top of the meeting hours themselves.

**Recommendation [PROVEN]: protect two no-meeting days per week** before adding
headcount. It is free capacity and typically recovers 5-8% of effective hours.

---

## 5. Utilisation targets

| Planned utilisation | Behaviour |
|--------------------|-----------|
| Below 60% | Under-committed; team will fill the space with low-value work |
| 70-80% | **Target band.** Absorbs incidents without slipping commitments |
| 80-90% | Every surprise costs a commitment; slippage becomes routine |
| Above 90% | Queueing effects dominate; cycle time rises non-linearly and predictability disappears |

This is a queueing property, not a motivational one: as utilisation approaches
100%, wait time approaches infinity. Planning a team to 95% utilisation
guarantees late delivery even if every estimate is correct.

**Reserve 20% of effective capacity for unplanned work as the default.** Adjust
by context:

| Context | Buffer |
|---------|--------|
| Greenfield product, no production users | 10% |
| Stable product, mature ops | 15-20% |
| Legacy system, high defect inflow | 25-35% |
| Team owns customer-facing incidents | 30% |
| Active compliance/audit period | +5-10% on top |

---

## 6. Estimation inflation

Raw estimates are systematically optimistic. Inflate by confidence band:

| Confidence | Definition | Multiplier |
|-----------|------------|-----------|
| High | Team has shipped something near-identical; design complete | 1.15x |
| Medium | Shape is understood; unknowns are known | 1.40x |
| Low | New domain, new dependency, or design not started | 1.90x |
| Unknown | No breakdown exists | 1.90x, and flag it |

**A commitment made at "low" confidence should never be made externally.** If a
customer date depends on it, either spend a week de-risking it into "medium"
first, or commit the date at the inflated number.

Calibrate these multipliers against your own history after two quarters:
`actual_hours / original_estimate`, grouped by the confidence recorded at
estimation time. Most teams find their "medium" multiplier sits between 1.3 and
1.6.

---

## 7. Attrition and shrinkage

| Factor | Typical annual rate | Capacity implication |
|--------|--------------------|--------------------|
| Voluntary attrition, tech | 12-15% | One departure per 7-8 people per year |
| Voluntary attrition, high-growth | 18-25% | Plan continuous backfill |
| Internal transfer out | 5-10% | Same capacity effect as attrition |
| Parental leave | Varies | 3-12 months at 0; must be modelled explicitly |
| Extended medical leave | 1-3% of headcount at any time | Model as a haircut, not a person |

**Plan the year at 92-95% of nominal headcount** to absorb normal attrition and
backfill lag. A role takes 8-14 weeks to fill and then ramps — a departure in
January is not replaced in effective terms until roughly July.

---

## 8. Hire vs contract economics

| Dimension | Permanent hire | Contractor |
|-----------|---------------|------------|
| Time to start | 8-14 weeks | 1-3 weeks |
| Ramp to full productivity | 3-6 months | 1-2 months on scoped work |
| Productivity ceiling | 100% | 85-95%; rarely absorbs deep system context |
| Hourly cost (loaded) | Salary x 1.25-1.40 / ~1,900 h | 1.5-2.5x the equivalent loaded rate |
| Cost commitment | Ongoing; expensive to reverse | Ends with the contract |
| Retains knowledge | Yes | No — assume it leaves with them |
| Break-even vs contractor | ~9-14 months | — |

**Recommendation [PROVEN]: hire for permanent capability, contract for a
bounded surge with clear acceptance criteria.** Contractors win the first two
quarters on cost-per-delivered-hour and lose decisively past a year. If the need
is structural and ongoing, contracting is a way of paying a premium to postpone
a decision.

The loading multiplier of 1.25-1.40 on base salary covers employer tax,
benefits, equipment, software seats, and facilities. Use 1.30 as the default and
replace it with your finance team's actual figure.

---

## 9. Quick reference card

```
Effective hours (quarter, 1.0 FTE, fully ramped, on-call, 63 working days):
  63 d x 8 h                        = 504 h gross
  - 5 PTO days                      = -40 h
  - 2 on-call weeks @ 40%           = -32 h
  - 20% meetings + overhead         = -86 h
  --------------------------------------------
  effective                         ~ 346 h  (69% of gross)
  minus 20% unplanned buffer        ~ 277 h committable

Quarterly committable hours per fully-ramped IC: 270-300 h
Quarterly committable hours per first-quarter mid hire: 90-110 h
Quarterly committable hours per tech lead: 120-160 h
Quarterly committable hours per manager: 0
```

Use these as the back-of-envelope figures in a planning meeting; use the scripts
when the number has to survive scrutiny.
