# Funding and Portfolio Allocation

Reference for sourcing research funding, structuring budgets to funder
conventions, and allocating a fixed research budget across competing studies by
decision value rather than by cost or by advocacy.

## 1. Funding sources and what each optimises for


| Source | Optimises for | Budget conventions | Reporting burden |
|--------|---------------|--------------------|------------------|
| **Internal opex** | Speed to decision | Whatever finance accepts; often no overhead | Low — usually a monthly actuals line |
| **Internal capitalised** | Assets with future benefit | Strict rules on what qualifies | Moderate — audit exposure |
| **Public / government grant** | Public benefit, methodological rigour | Detailed categories, capped overhead, restricted transfers | High — periodic financial and scientific reports |
| **Foundation grant** | Mission alignment | Often caps indirect costs sharply | Moderate to high |
| **Industry sponsorship** | Commercial outcome | Negotiated; overhead usually accepted | Moderate — milestone-based |
| **Collaborative consortium** | Shared infrastructure | Cost-share rules, partner-level budgets | High — partner coordination dominates |

Two practical consequences:

- **Restricted funds cannot be reallocated freely.** A grant budget with fixed
  category ceilings is not a single pot; overspending personnel and underspending
  equipment is a compliance problem even when the total is unchanged.
- **Capped overhead shifts costs into direct lines.** Where a funder caps
  indirect recovery, the shortfall does not vanish — it is absorbed by the
  organisation. Know who is absorbing it before accepting the award.

## 2. Grant budget conventions


Most grant budgets use a standard category structure. Names vary; the structure
does not.

| Category | Contents | Common pitfalls |
|----------|----------|-----------------|
| **Personnel** | Salaries plus employer costs, by named role and effort fraction | Effort fractions that exceed a person's availability across all their funded projects |
| **Equipment** | Capital items above a threshold | Threshold varies by funder; below it, items go to consumables |
| **Consumables** | Materials, reagents, participant incentives | Incentives sometimes disallowed or capped |
| **Travel** | Fieldwork, site visits, dissemination | Often capped; conference travel frequently restricted |
| **Participant costs** | Incentives, reimbursement, transport | Some funders require an ethics-approved schedule |
| **Subcontracts** | Partner organisations, vendors | Often carry their own overhead rules and a pass-through cap |
| **Other direct** | Publication fees, archiving, software licences | Publication fees frequently forgotten |
| **Indirect / overhead** | Institutional recovery | Cap and base both vary; check both |

### Justification writing

Every line needs a justification that answers three questions: what it is, why
the study needs it, and how the amount was derived. Reviewers reject on the
third far more often than on the first two.

| Weak | Strong |
|------|--------|
| "Participant incentives: 40,000" | "Participant incentives: 544 screened × 40 + 408 enrolled × 60 = 46,240, at the rate approved by the ethics committee for comparable time burden" |
| "Research assistant: 0.5 FTE" | "Research assistant 0.5 FTE for 18 months: coordinates recruitment across 6 sites at approximately 90 participants per site; derived from 4 hours per enrolled participant plus 8 site-coordination hours per month" |

Deriving the number visibly is what makes it defensible. A round number with no
derivation reads as an estimate that was chosen rather than computed.

## 3. Value of information


The core question in portfolio allocation is not "how much does this study
cost" but "how much is it worth knowing this before we decide."

```
expected decision value = decision value
                        × P(research changes the decision)
                        × reversibility multiplier
```

### Estimating decision value

Decision value is the cost of getting the decision wrong. Estimate it as the
difference between the best and worst realistic outcome of the decision, not as
the total value of the initiative.

| Decision | Wrong-way cost |
|----------|---------------|
| Enter a new market | Sunk entry cost plus opportunity cost of the alternative market |
| Restructure pricing | Revenue at risk across the affected base for the correction period |
| Build a platform capability | Engineering cost plus the delay to everything sequenced behind it |
| Select a clinical endpoint | Cost of the whole study if the endpoint proves unanalysable |

Precision is not required. An order-of-magnitude estimate is enough to separate
a study attached to a seven-figure decision from one attached to a five-figure
decision, and that separation is what the portfolio review needs.

### Estimating the probability of changing the decision

Ask the decision-maker directly: "What result would change your mind?" Then:

| Answer | P(changes decision) |
|--------|--------------------|
| A specific, plausible result they name readily | 0.3 - 0.5 |
| A specific result they consider unlikely | 0.1 - 0.2 |
| "It would have to be extreme" | 0.05 - 0.1 |
| "Nothing would change it" | 0 — do not fund the study |

That last row is the most valuable output of the exercise, and asking the
question out loud is the only reliable way to reach it. Studies attached to
closed decisions are common in every portfolio and are almost never identified
by ranking.

### The reversibility discount

Information about a decision you can cheaply undo is worth much less than
information about one you cannot.

| Reversibility | Multiplier |
|---------------|-----------|
| Reversible within a sprint | 0.15 |
| Reversible within a quarter | 0.45 |
| Costly to reverse | 0.85 |
| One-way door | 1.0 |

**[PROVEN]** For sprint-reversible decisions, ship an experiment instead of
funding a study. It is faster, it produces observed behaviour rather than
reported preference, and the discount above says the study was never worth much
anyway.

### Automatic zeroes

Two conditions make a study worth nothing regardless of every other input:

1. **The decision has already been made.** The study is documentation. Fund it
   as documentation if it is worth funding at all — but do not count it against
   the research budget or call it evidence.
2. **The answer arrives after the decision deadline.** Either compress the method
   or accept that the decision goes unevidenced. A study reporting after the fact
   consumes budget and changes nothing.

## 4. Allocation mechanics


Rank by expected decision value per unit cost, then fund greedily down the list
until the budget is exhausted. Three refinements the greedy rank does not
capture:

### Concentration

A single study consuming more than about 40% of the allocated budget means one
delay stalls the entire evidence pipeline. Where the concentration is
unavoidable, stage the funding against milestones so a stalling study releases
budget rather than holding it.

### Sequencing

Some studies are prerequisites for others, and some make others unnecessary.
Before finalising:

- **Run cheap evidence first.** Ticket analysis, log analysis, and existing-data
  mining frequently answer part of an expensive study's question and always
  sharpen the rest.
- **Check for redundancy.** Two studies asking overlapping questions of the same
  population should usually be one study with a larger sample.
- **Check dependencies.** A study whose method depends on instrumentation that
  does not exist yet is not fundable this period regardless of its rank.

### Reserve

Hold back 10-15% of the research budget unallocated. Research portfolios are
disrupted by events that were not visible at planning time — a competitor
launch, a regulatory change, a metric moving unexpectedly — and a fully
committed portfolio cannot respond to any of them without cancelling something
mid-flight.

## 5. Portfolio governance


### Review cadence

| Portfolio size | Review cadence |
|----------------|----------------|
| Under 5 active studies | Quarterly |
| 5-15 active studies | Monthly |
| Over 15 | Monthly, with a quarterly deep review |

### Standing agenda

1. **Burn versus delivery** for each active study — the gap, not the spend
2. **Decisions still open?** For each study, is the decision it informs still
   open, and what result would change it
3. **New entrants** ranked against the existing portfolio, not evaluated in
   isolation
4. **Reserve status** and what has drawn on it
5. **Insights delivered** since last review, and what changed as a result

Item 5 is the one that gets dropped and the one that protects the budget. A
research function that cannot name what changed because of its work will lose
its budget in the first serious cost review, regardless of the quality of the
research.

### Stopping rules

Define these before a study starts, not during the awkward conversation:

- **Accrual futility** — if enrolment is below a stated fraction of plan at a
  stated point, the study is re-planned or stopped
- **Decision closure** — if the decision the study informs is made before the
  study reports, the study stops
- **Cost overrun** — if the forecast at completion exceeds budget by more than a
  stated percentage, the study is descoped or re-approved
- **Superseded evidence** — if the question is answered by another source, the
  study stops

Studies almost never stop without a pre-agreed rule. Sunk cost, personal
investment, and the awkwardness of the conversation all push toward continuing,
and each of those is easier to overcome when the rule was agreed in advance by
the same people now sitting in the room.

## 6. Staged funding and tranching


Full up-front funding of a long study transfers all the risk to the funder and
removes every natural decision point. Stage the release instead.

| Stage gate | Released at | Withheld if |
|-----------|-------------|-------------|
| **Setup** | Approval | — |
| **Pilot / first site** | Protocol final, first site live | Protocol still in revision |
| **Scale** | First 10-15% of target enrolled at plan rate | Accrual below half of plan |
| **Completion** | Enrolment complete | Data quality issues unresolved |
| **Reporting** | Database lock | Analysis plan not finalised pre-lock |

The scale gate is the important one. It is the last point at which a study
running at half the planned accrual can be re-planned cheaply, and it is
routinely skipped because the setup money is already spent and stopping feels
wasteful. Releasing the scale tranche against an accrual test converts that
sunk-cost pressure into an explicit decision.

**[RECOMMENDED]** Tie tranches to delivery evidence, not to elapsed time. A
calendar-based tranche releases money to a stalled study automatically, which is
precisely the failure the staging was meant to prevent.

## 7. Cost-share and matched funding


Consortium and grant funding frequently requires the recipient to contribute a
share. Two traps:

- **In-kind contributions must be evidenced.** Staff time counted as cost-share
  needs timesheets or an auditable allocation basis. "Approximately 0.3 FTE" is
  not evidence, and it is a common audit finding.
- **The same contribution cannot be counted twice.** Staff time already charged
  to another funded project cannot also serve as cost-share here. Track the
  denominator — each person's total committed effort across all funded work —
  not just each project's numerator.

Maintain a single effort-commitment register across the whole portfolio. Without
it, over-commitment is invisible until an audit or until someone genuinely runs
out of hours, and both discoveries are expensive.

## 8. Reallocating mid-flight


When a study stops, is descoped, or underspends, the released money should be
reallocated deliberately rather than absorbed.

Order of preference:

1. **Fund the highest-ranked deferred study** from the last portfolio review.
   The ranking already exists; use it.
2. **Top up the reserve** if it has been drawn down below 10%.
3. **Accelerate an in-flight study** whose constraint is money rather than time.
4. **Return it.** If none of the above applies, returning the money is a better
   outcome than spending it on the next-cheapest available study, and it
   materially strengthens the next funding request.

The failure mode is the fourth option never being considered. Underspend that
gets absorbed into marginal work teaches finance that the original request was
padded, which is paid back with interest at the next budget cycle.

## 9. Defending the research budget


Research is a cost centre on the P&L and an investment in the decision log. The
gap between those two framings is where research budgets are lost.

What survives a cost review:

- **A decision log.** Every study, the decision it informed, and what changed as
  a result. Maintained continuously — it cannot be reconstructed under pressure.
- **Named avoided costs.** "The pricing study changed the tier structure before
  launch; the rejected structure would have cost an estimated X in the affected
  base." Estimates are fine if the basis is stated.
- **Cost per decision-ready insight**, trended over time. A falling number
  demonstrates an improving function.
- **The counterfactual.** What the organisation decided without evidence in the
  same period, and what those decisions cost when they went wrong.

What does not survive: activity metrics. Studies run, participants interviewed,
reports published, and sessions moderated all measure effort, not value, and
presenting them invites the reviewer to treat research as overhead to be
minimised.

**[PROVEN]** The single highest-leverage habit is recording, at the moment a
decision is made, which research informed it and what would have been decided
otherwise. Retrospective reconstruction of that record is unconvincing precisely
because it is retrospective.

## 10. Multi-year and multi-currency programmes


| Risk | Mitigation |
|------|-----------|
| Salary escalation | Explicit annual escalation line; do not absorb it into contingency |
| Vendor rate increases | Fix rates in the contract for the study duration where possible |
| Currency movement on cross-border sites | Budget in the currency of spend; state the assumed rate and the exposure |
| Funder disbursement delay | Model the working-capital gap; a grant paid in arrears needs bridge funding |
| Scope drift across years | Annual re-baseline against the original decision value |

The annual re-baseline is the one most often skipped. A three-year programme
approved against a decision that has since been made, deferred, or superseded
should be stopped or re-scoped — and only an explicit annual check surfaces that.

## 11. Allocation checklist


- [ ] Every study states the decision it informs and who makes it
- [ ] Decision value estimated as the cost of getting it wrong
- [ ] Decision-maker asked directly what result would change their mind
- [ ] Reversibility classified and the discount applied
- [ ] Decision deadline recorded; studies reporting after it excluded
- [ ] Studies informing closed decisions identified and cut
- [ ] Cheap existing-evidence work sequenced before expensive commissioned work
- [ ] Redundant and overlapping studies merged
- [ ] Method dependencies checked before funding
- [ ] No single study above ~40% of allocated budget, or staged if unavoidable
- [ ] 10-15% reserve held unallocated
- [ ] Stopping rules agreed per study before start
- [ ] Review cadence set to portfolio size
- [ ] Insights-delivered reporting in the standing agenda
