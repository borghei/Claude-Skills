---
name: capacity-planner
description: >
  Headcount and delivery-capacity planning — effective capacity from raw
  headcount, hire/contract/defer scenarios, and capacity-vs-commitment gap
  reports. Use when planning a quarter, sizing a hiring ask, or testing whether
  a roadmap fits.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: business-operations
  domain: workforce-planning
  updated: 2026-07-21
  tags: [capacity-planning, headcount, resource-planning, hiring, forecasting]
---

# Capacity Planner

Turns headcount into hours you can actually commit. Most capacity plans fail the
same way: they count people instead of delivered hours, ignore ramp, and size
supply to fit the roadmap rather than the other way round. This skill computes
effective capacity independently, matches it against risk-adjusted demand, and
publishes the cut line.

## When to use this skill

- **Quarterly planning** — deciding what the team can commit to for the next 90 days
- **Testing a roadmap** — a stakeholder has a list and wants to know if it fits
- **Building a hiring ask** — quantifying a structural gap in hours and dollars
- **Hire vs contract vs defer** — choosing how to close a capacity shortfall
- **Mid-quarter replan** — the burn rate diverged and commitments need renegotiating
- **Onboarding impact** — modelling what three new hires actually deliver this quarter

## Inputs the skill expects

- Team roster: name, discipline, seniority, FTE, tenure in months
- Known absence: booked PTO days, on-call rotation weeks per person
- Overhead estimates: meeting load and non-delivery overhead as a percentage
- Working days and hours per day for the period
- Candidate commitments with discipline, hour estimate, confidence band, and priority
- For scenario work: demand curve per quarter, salary/contractor rates, start dates

## Clarify First

Before generating, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Is this a supply question or a demand question?** — sizing a hiring ask and testing a roadmap use different scripts and produce different artifacts
- [ ] **Who counts as delivery capacity?** — including managers, tech leads, or unfilled reqs at full FTE changes the answer by 10-40%
- [ ] **Are the estimates already risk-adjusted?** — applying the confidence inflation twice overstates demand by 40%+; applying it zero times understates it by the same
- [ ] **Is the buffer set from history or from intent?** — the unplanned-work reserve is the single largest lever on the cut line

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Workflows

### Workflow 1 — Model effective capacity

Establishes what the team can actually deliver, computed before anyone looks at
the roadmap. Run this first, always.

1. Build the roster: one entry per person, with real FTE and tenure in months. Use a negative `tenure_months` for someone who has not started yet.
2. Pull **booked** PTO, not average PTO. Q3 and Q4 are not average quarters.
3. Set `meeting_load_pct` from a calendar audit, not from memory — the gap is usually 5-10 points.
4. Run the model and check the effective-hours ratio against the sanity band in `references/capacity-benchmarks.md`: below 45% is structurally broken, above 80% is fiction.
5. Record the per-discipline effective hours — these are the inputs to Workflow 2.

```bash
python3 business-operations/capacity-planner/scripts/capacity_model.py \
  --input business-operations/capacity-planner/assets/sample_team.json \
  --format text
```

### Workflow 2 — Find the cut line

Matches risk-adjusted demand against capacity in priority order and reports what
does not fit.

1. List every candidate commitment with discipline, raw estimate, confidence band, and priority. Mark anything already promised externally with `"committed": true`.
2. Set the buffer from the trailing three quarters of actual unplanned hours. Default 20%; use 30% if the team owns customer-facing incidents.
3. Run the gap analysis and read the cut line, not the totals.
4. Escalate any `committed: true` item above the cut line **this week** — a promise you already know you will miss is a conversation, not a risk.
5. Publish the below-the-line list alongside the plan. That list is the deliverable.

```bash
python3 business-operations/capacity-planner/scripts/commitment_gap.py \
  --input business-operations/capacity-planner/assets/sample_commitments.json \
  --buffer-pct 20 --format text
```

### Workflow 3 — Compare hire, contract, and defer

Applies only to work below the cut line. Never use scenario analysis to justify
a plan that does not fit.

1. Build the demand curve per quarter for the horizon — at least four quarters, eight if the gap looks structural.
2. Define one scenario per realistic option, including a defer scenario as the zero-cost baseline.
3. Run the comparison and read four axes, not just cost: time to relief, cost per delivered hour, reversibility, and knowledge retention.
4. Sense-check the winner against the decision rule in `references/planning-methods.md`. A four-quarter horizon is systematically biased toward contracting because the hire/contract crossover falls at month 9-14.
5. Write the recommendation with its lead time attached. "Hire two engineers" relieves the quarter after next, not this one.

```bash
python3 business-operations/capacity-planner/scripts/scenario_compare.py \
  --input business-operations/capacity-planner/assets/sample_scenarios.json \
  --format json
```

## Decision frameworks

### Gross-to-effective conversion [PROVEN]

Planning figures for one fully-ramped IC over a 63-day quarter:

| Layer | Hours | Running total |
|-------|-------|---------------|
| Gross (63 d x 8 h) | 504 | 504 |
| Booked PTO (5 days) | -40 | 464 |
| On-call (2 weeks @ 40% loss) | -32 | 432 |
| Meetings + overhead (20%) | -86 | 346 |
| Unplanned-work buffer (20%) | -69 | **277 committable** |

**Use 270-300 committable hours per fully-ramped IC per quarter.** A tech lead
delivers 120-160; an engineering manager delivers 0. A mid-level hire starting on
day one of the quarter delivers 90-110.

### Which lever closes the gap

| Gap size | Persists beyond 4 quarters? | Lever | Time to relief |
|----------|----------------------------|-------|----------------|
| Any | — | **Cut scope** [PROVEN] | Immediate |
| Under 10% | No | **Reduce overhead** [PROVEN] | 2-4 weeks |
| 10-30% | No | **Defer**, with a named later slot | Immediate |
| 10-40% | No, work is separable | **Contract** [RECOMMENDED] | 1-3 weeks |
| Any | Yes | **Hire** [PROVEN for structural gaps] | 5-8 months |
| Large | Yes, needed within 2 quarters | **Hire + contract bridge** [RECOMMENDED] | 1-3 weeks, handover at Q+2 |

Consider them in this order. Reducing overhead is the highest-ROI lever and is
almost always skipped because it is nobody's job — recovering 8% of effective
hours on a ten-person team is worth most of an FTE and costs nothing.

The bridge pattern's failure mode is that the handover never happens and the
contractor becomes permanent at contractor rates. Put the handover date and the
knowledge-transfer artifact in the contract itself.

### Estimation inflation by confidence [RECOMMENDED]

| Confidence | Definition | Multiplier |
|-----------|------------|-----------|
| High | Team has shipped something near-identical; design complete | 1.15x |
| Medium | Shape understood; unknowns are known | 1.40x |
| Low | New domain, new dependency, or design not started | 1.90x |

Recalibrate against your own `actual / original estimate` history after two
quarters. Most teams land between 1.3 and 1.6 for "medium". Never make an
external commitment at "low" confidence — either de-risk it to medium first, or
commit the date at the inflated number.

### Utilisation bands [PROVEN]

| Planned utilisation | Behaviour |
|--------------------|-----------|
| Below 60% | Under-committed; the space fills with low-value work |
| 70-80% | **Target.** Absorbs incidents without slipping commitments |
| 80-90% | Every surprise costs a commitment |
| Above 90% | Queueing effects dominate; cycle time rises non-linearly |

This is queueing theory, not motivation. Planning to 95% guarantees late
delivery even when every estimate is correct.

## Anti-Patterns

### Headcount as capacity
**Mistake:** Multiplying FTE count by working hours and calling it capacity — 8 engineers x 504 hours = 4,032 hours available.
**Why it happens:** It is the only number that is easy to get, and it is the number finance and leadership already track. Effective hours require measurement nobody has set up.
**Instead:** Run the gross-to-effective waterfall every time. The real figure is 50-70% of gross, and the gap is where every over-commitment lives. If you have no measured overhead data, use 60% and start measuring this quarter.

### Hiring to fix this quarter
**Mistake:** Responding to a capacity gap by opening requisitions, then planning as if the new people contribute in the current period.
**Why it happens:** Hiring is the lever with the clearest approval path — a headcount ask is a familiar conversation in a way that "we are cutting three roadmap items" is not.
**Instead:** Hiring relieves the quarter after next at the earliest: 8-14 weeks to fill plus 3-6 months to ramp. Close the current gap by cutting scope or contracting, and trigger hiring on a three-quarter trend above 85% load rather than on one bad quarter. Onboarding into an overloaded team also ramps 20% slower, because nobody has time to onboard anyone.

### The plan that fits perfectly
**Mistake:** Presenting a capacity plan where demand lands within a few percent of supply, with nothing below the cut line.
**Why it happens:** Estimates get quietly adjusted downward during planning until the roadmap fits the team, or the demand list is truncated before the meeting so it never appears.
**Instead:** Treat a perfect fit as evidence of a process failure and go find which number moved. Every honest plan has a visible cut line, and the below-the-line list is the most useful artifact the exercise produces — it is what lets a stakeholder trade priorities rather than discover in week 10 that their item was never going to happen.

### Buffer as optimism dial
**Mistake:** Setting the unplanned-work reserve to whatever makes the plan work — dropping from 20% to 10% when the roadmap does not fit.
**Why it happens:** The buffer looks like slack, and slack looks like something to be negotiated away. It has no advocate in the room.
**Instead:** Set the buffer from the trailing three quarters of actual unplanned hours; it is a measurement, not a cushion. If unplanned work exceeded the buffer for two consecutive weeks last quarter, the correct move is to raise it. Cutting the buffer does not create capacity — it just relocates the shortfall to week 10, where it costs more.

## Files

| File | Purpose |
|------|---------|
| `scripts/capacity_model.py` | Converts roster + overhead + ramp into effective hours per person and per discipline |
| `scripts/commitment_gap.py` | Inflates estimates by confidence, fills capacity in priority order, reports the cut line |
| `scripts/scenario_compare.py` | Projects hire/contract/defer scenarios over a horizon with cost per delivered hour |
| `references/capacity-benchmarks.md` | Effective-hours ratios by role, ramp curves, on-call and meeting load, utilisation bands, hire-vs-contract economics |
| `references/planning-methods.md` | Planning sequence, demand forecasting, gap-closing levers, governance cadence, stakeholder pushback responses |
| `assets/capacity-plan-template.md` | Quarterly capacity plan with cut line, gap options, risks, and weekly tracking |
| `assets/sample_team.json` | Seven-person roster covering ramping hires, part-time, and multiple disciplines |
| `assets/sample_commitments.json` | Nine commitments against the capacity produced by `capacity_model.py` on the sample roster |
| `assets/sample_scenarios.json` | Four-quarter demand curve with hire, contract, and defer scenarios |
