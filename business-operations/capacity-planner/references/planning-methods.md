# Capacity Planning Methods

How to run the planning cycle: forecast demand, model supply, close the gap, and
govern the plan once the quarter starts. Benchmark numbers live in
`capacity-benchmarks.md`; this file covers method and sequence.

---

## 1. The planning sequence

Run these in order. Reversing steps 2 and 3 is the most common process failure —
teams size the roadmap to the headcount they wish they had, then negotiate
backwards.

1. **Freeze the demand set.** List every candidate commitment with an owner, a
   discipline, an estimate, and a confidence band.
2. **Model supply independently.** Compute effective capacity without looking at
   the demand list. Supply must not be influenced by how much work exists.
3. **Apply the buffer.** Subtract the unplanned-work reserve before matching.
4. **Match in priority order.** Fill capacity top-down; the line where capacity
   runs out is the cut line.
5. **Test scenarios only for the residual.** Hire/contract/defer analysis applies
   to work below the cut line, never to justify the whole plan.
6. **Publish the cut line.** The list of what did *not* make it is the most
   valuable artifact of the exercise.
7. **Track weekly, replan monthly.** Capacity plans decay; the first month is
   accurate, the third is a hypothesis.

**The discipline that matters: supply is computed before demand is seen.** Any
process where capacity is derived from the roadmap produces a plan that always
fits and never holds.

---

## 2. Demand forecasting

### Demand categories

Every hour of team time falls into one of four buckets. Plans that only count
the first bucket over-commit by 30-50%.

| Category | Typical share | How to forecast |
|----------|--------------|-----------------|
| Committed roadmap | 50-65% | Bottom-up estimate per item |
| Keep-the-lights-on | 15-25% | Trailing 3-quarter average of actual hours |
| Unplanned / incident | 10-25% | Trailing average, not aspiration |
| Technical investment | 10-20% | Explicit allocation, defended |

**Set KTLO and unplanned from history, never from intent.** The trailing
three-quarter average of actual hours spent is the only credible input. Teams
that forecast "we'll spend less on incidents next quarter" are forecasting a
behaviour change they have not made.

### Estimating the roadmap

Three approaches, in order of preference:

**[PROVEN] Reference-class estimation.** Find the three most similar things the
team has actually shipped, take their actual hours, use the median. This beats
bottom-up decomposition on anything larger than two weeks because it captures
integration, review, and rework overhead that decomposition always omits.

**[RECOMMENDED] Bottom-up decomposition with inflation.** Break to tasks of one
week or less, sum, then apply the confidence multiplier. Works when the shape is
genuinely understood. Without the multiplier it is systematically 20-40% light.

**[RECOMMENDED] Three-point (PERT) estimation.** `(optimistic + 4 x likely +
pessimistic) / 6`. Useful when a small number of items dominate the plan and you
need the distribution, not just the point. The value is in forcing the
pessimistic case to be spoken aloud.

Avoid: story-point velocity extrapolation across a quarter boundary. Points
drift with team composition, and converting points to hours at a fixed rate
launders an unexamined assumption into a commitment.

### Sizing what has not been designed

Anything without a design gets a **t-shirt size with an hour range**, not a
point estimate:

| Size | Hour range | Meaning |
|------|-----------|---------|
| S | 40-80 h | One person, under a sprint |
| M | 120-240 h | One person, most of a quarter, or two for a sprint |
| L | 320-640 h | Small team, most of a quarter |
| XL | 800+ h | Must be broken down before it can be committed |

**XL items cannot be committed.** Commit to the discovery spike that turns the
XL into a set of L/M items, and commit the rest next cycle.

---

## 3. Supply modelling

### The three questions that set supply

1. **Who is actually here?** Not the org chart — the people who will do delivery
   work during the period, at their real FTE, minus known leave.
2. **What fraction of their time survives overhead?** Meetings, on-call, admin,
   interviews, support.
3. **How ramped are they?** Anyone under six months, and anyone who changed team
   or stack, is not at full output.

### Common supply modelling errors

| Error | Effect | Fix |
|-------|--------|-----|
| Counting managers and leads at full FTE | Overstates by 10-20% | Model leads at 30-45%, managers at 0-15% |
| Counting open reqs as capacity | Overstates by whole FTEs | Only count people with a signed start date, ramped |
| Ignoring ramp for recent hires | Overstates by 40-70% per hire | Apply the curve |
| Averaging PTO instead of taking actual bookings | Understates Q3/Q4 loss | Pull actual booked leave |
| Modelling on-call as zero-cost | Overstates by 8-17% | Apply rotation cost |
| Treating a 0.5 FTE as half output | Overstates | Part-time carries full meeting load; use 0.4 |

The part-time row generalises: overhead is largely **per-person, not
per-hour**. A 0.6 FTE attends the same standups and reviews as a 1.0 FTE, so
their delivery share is lower than their contract fraction.

### Skill-mix constraints

Total hours are necessary but not sufficient. Before committing, verify:

- **No single-person dependency on the critical path.** If one person is the
  only one who can do a committed item, that item's risk is their availability,
  not its estimate.
- **Discipline balance.** 2,000 engineering hours with 40 design hours delivers
  little. Model each discipline's pool separately — this is why the scripts
  bucket by discipline rather than reporting one team number.
- **Review capacity.** Senior review is a shared resource that saturates. If
  every item needs staff-level review, the staff engineer's remaining hours are
  the real ceiling.

---

## 4. Closing the gap

Five levers, in the order they should be considered:

### 1. Cut scope [PROVEN — first resort]

The fastest, cheapest, and most reversible lever. Reducing scope is the only
option that takes effect immediately and costs nothing. Cut from the bottom of
the priority list, and cut whole items rather than trimming every item — a
uniform 20% trim across ten items usually yields ten unfinished items.

### 2. Reduce overhead [PROVEN — highest ROI]

Before spending money, recover the capacity already owned: shrink the meeting
load, enlarge the on-call rotation, fix the alerts causing the interrupts,
remove the approval step nobody reads. Recovering 8% of effective hours on a
ten-person team is worth most of an FTE and costs nothing.

### 3. Defer [RECOMMENDED]

Move work to a later period. Honest when demand is genuinely lumpy; dishonest
when it merely relocates the over-commitment into next quarter's plan. Test:
does the deferred work have a named later slot with capacity available? If not,
this is a cut being described as a deferral.

### 4. Contract [RECOMMENDED for bounded surges]

Fastest capacity addition (1-3 weeks to start). Correct when the need is
time-boxed, the work is separable, and acceptance criteria are writable in
advance. Wrong when the work requires deep system context or the need is
permanent.

Contracting fails when: the scope is ill-defined (the contractor bills while you
figure it out), the work sits on the critical path of core systems (context
transfer cost exceeds the gain), or you are backfilling a permanent gap
(paying 1.5-2.5x indefinitely).

### 5. Hire [PROVEN for structural gaps, useless for this quarter]

Correct answer to a sustained capacity gap; wrong answer to this quarter's
over-commitment. From approved req to full productivity is **5-8 months**:
8-14 weeks to fill, 3-6 months to ramp. A hire approved today relieves the
quarter after next, at best.

The corollary: **if the gap is structural, the hiring decision is already
late.** Trigger hiring on trend (three consecutive quarters above 85% load), not
on a single quarter's crisis.

---

## 5. Scenario comparison

When comparing hire / contract / defer, compare on four axes — never on cost
alone:

| Axis | Question |
|------|----------|
| Time to relief | Which quarter does the gap actually close? |
| Cost per delivered hour | Total cash over the horizon / incremental hours delivered |
| Reversibility | What does it cost to unwind if demand drops? |
| Knowledge retention | Does the capability remain after the engagement? |

A four-quarter horizon usually favours contracting on cost-per-hour and hiring
on everything else. **Extend the horizon to eight quarters before deciding a
structural gap** — the crossover typically falls between month 9 and 14, so a
four-quarter analysis is systematically biased toward contracting.

### Decision rule [RECOMMENDED]

```
Is the gap expected to persist beyond 4 quarters?
├── No  → Is the work separable with clear acceptance criteria?
│         ├── Yes → Contract
│         └── No  → Defer or cut scope
└── Yes → Is relief needed within 2 quarters?
          ├── No  → Hire
          └── Yes → Hire AND contract as a bridge, with an explicit
                    handover date and knowledge-transfer deliverable
```

The bridge pattern is the honest answer to "we need it now and forever." Its
failure mode is that the handover never happens and the contractor becomes
permanent at contractor rates — so put the handover date and the transfer
artifact in the contract itself.

---

## 6. Governance

### Cadence

| Activity | Frequency | Output |
|----------|-----------|--------|
| Capacity model refresh | Quarterly, before planning | Effective hours per discipline |
| Commitment gap review | Quarterly, at planning | Cut line, published |
| Actuals vs plan check | Weekly | Burn rate, early divergence signal |
| Assumption recalibration | Quarterly, after close | Updated inflation multipliers, ramp curves, buffer |
| Structural gap review | Quarterly | Hire/no-hire trigger check |

### Tracking during the quarter

Track two numbers weekly:

- **Burn ratio** — hours consumed / hours planned to date. Above 1.15 by week 4
  means the plan is already wrong; replan rather than hoping for recovery.
- **Unplanned share** — actual unplanned hours / total hours. If it exceeds the
  buffer for two consecutive weeks, the buffer was set too low and next
  quarter's default must rise.

Both are leading indicators available by week 3-4. Waiting for a milestone to
slip is waiting six weeks for information you already had.

### Closing the loop

After each quarter, record for the next planning cycle:

1. Actual effective-hours ratio vs modelled — corrects the overhead assumptions.
2. Actual vs estimated hours per item, grouped by confidence band — corrects the
   inflation multipliers.
3. Actual unplanned share vs buffer — corrects the reserve.
4. Actual ramp achieved vs curve — corrects the ramp model.

**Two quarters of this replaces every default in `capacity-benchmarks.md` with
your own numbers, which is the point.** A capacity model that is never
back-tested is a spreadsheet, not a plan.

---

## 7. Communicating the plan

The output that changes decisions is not the capacity number — it is the cut
line. Present in this order:

1. **What we are committing to**, with the confidence band for each item.
2. **What did not fit**, explicitly, with the hours gap.
3. **What we would need to fit it** — the scenario, its cost, and its lead time.
4. **What we are assuming** — buffer, ramp, attrition, and what invalidates each.

Never present a plan that fits perfectly. A plan with no cut line means either
the estimates were adjusted to fit the capacity, or the demand list was
truncated before the meeting. Both are worth surfacing.

### Handling the pushback

| Pushback | Response |
|----------|----------|
| "Can't the team just work harder?" | Utilisation above 90% raises cycle time non-linearly. The plan already assumes 70-80%. |
| "We hit these numbers last year." | Show the trailing effective-hours ratio; if it was higher, ask what changed (usually on-call load or headcount mix). |
| "Add the new hire to Q1's plan." | Show the ramp curve: a Q1 mid hire delivers ~35% of an FTE in Q1. |
| "Cut the buffer, we'll manage." | Show last quarter's actual unplanned hours. The buffer is a measurement, not a cushion. |
| "Can we commit it at low confidence?" | Yes, at the inflated estimate, or spend a week de-risking it to medium first. |
