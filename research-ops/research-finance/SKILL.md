---
name: research-finance
description: >
  Research budgeting and funding operations — study budget construction, cost
  per participant and per insight, burn against milestones, and portfolio
  prioritisation by decision value. Use when costing, tracking, or ranking research.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: research-ops
  domain: research-finance
  updated: 2026-07-21
  tags: [budget, burn-rate, earned-value, portfolio, funding, cost-per-insight]
---

# Research Finance

The money side of research operations: building a study budget that funds what
the study will actually consume, tracking spend against delivery rather than
against the calendar, and deciding which research to fund when the portfolio
asks for more than the budget holds.

## When to use this skill

- **Costing a study** before a funding request, where the budget will be
  scrutinised line by line and a missing line item becomes unfunded work
- **Answering "what does this cost per participant"** — the number every funder,
  finance partner, and sponsor asks first
- **Tracking a programme mid-flight** and needing to know whether the spend is
  buying delivery or just buying time
- **Forecasting an overrun** early enough to descope rather than late enough to
  need supplementary funding
- **Prioritising a research portfolio** that asks for more than the budget
  available
- **Defending a research budget** against a finance partner who sees a cost
  centre and needs to see decision value

## Inputs the skill expects

- Unit costs: per participant, per site, per site-month, and fixed programme costs
- Enrolment target, screen failure rate, site count, and duration
- Contingency and overhead rates your organisation applies
- For tracking: budget at completion, weighted milestones with completion, and
  planned versus actual spend by period
- For portfolio work: each study's cost, the value of the decision it informs,
  and the probability it changes that decision
- Decision deadlines — a study that lands after the decision is worth nothing

## Clarify First

Before generating, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Screen failure or recruitment yield rate** — budgets built on enrolled participants alone systematically under-fund screening, which is real work on real people
- [ ] **Whether overhead and contingency are inside or outside the quoted number** — the same study is quoted at wildly different totals depending on this, and the mismatch surfaces after the award
- [ ] **The decision each study informs and its value** — without it a portfolio can only be ranked by cost, which funds the cheap studies rather than the valuable ones
- [ ] **Who holds the budget and what triggers a change request** — determines how much contingency you need and how granular the tracking must be

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Workflows

### Workflow 1 — Build a study budget from unit costs

1. Separate costs into four blocks: per participant, per site, per site-month,
   and fixed. Most under-budgeting comes from costs sitting in the wrong block —
   site coordination billed as fixed rather than per site-month is the classic.
2. Mark which per-participant costs are incurred on **screened** rather than
   enrolled participants. Screening is charged on everyone screened.
3. Set contingency and overhead. **[RECOMMENDED]** 10% contingency minimum;
   8% is the floor below which every protocol amendment becomes a change request.
4. Run the builder. Read the cost per enrolled participant and the cost per
   insight — those are the two numbers the funding conversation turns on.
5. Clear every `fail`. They are all cases of work the study will do and the
   budget does not fund.

```bash
python3 research-ops/research-finance/scripts/study_budget_builder.py \
  --input research-ops/research-finance/assets/sample_budget.json \
  --format text
```

### Workflow 2 — Track burn against milestone delivery

1. Weight the milestones by share of total work, not by how visible they are.
   Enrolment usually carries 40-50% of the weight; setup milestones feel
   important and are cheap.
2. Record planned and actual spend by period.
3. Run the tracker. It computes earned value, cost and schedule performance, and
   the estimate at completion.
4. Act on the spend-versus-delivery gap, not on the spend-versus-calendar view.
   A programme at 36% spent and 24% delivered is heading for a 50% overrun,
   and the monthly finance report showing "on budget" will not tell you that.

```bash
python3 research-ops/research-finance/scripts/burn_vs_milestone_tracker.py \
  --input research-ops/research-finance/assets/sample_burn.json \
  --format text
```

### Workflow 3 — Prioritise the portfolio by decision value

1. For each candidate study, state the decision it informs, the cost of getting
   that decision wrong, and the probability the study changes the choice.
2. Record decision reversibility and the decision deadline.
3. Run the prioritiser. It computes expected decision value, discounts for
   reversibility, zeroes out studies that arrive too late or inform decisions
   already made, and allocates the budget greedily by value per unit cost.
4. Take the `fail` findings to the portfolio review directly. "This study informs
   a decision that has already been made" is a conversation worth having out
   loud, and the ranking alone will not force it.

```bash
python3 research-ops/research-finance/scripts/portfolio_prioritizer.py \
  --input research-ops/research-finance/assets/sample_portfolio.json \
  --budget 400000 --format text
```

## Decision frameworks

### Where research budgets under-fund themselves

| Omission | Consequence | Fix |
|----------|-------------|-----|
| **Screen failure** | Screening work on non-enrolled participants is unfunded | Gross participant costs up by 1/(1 − failure rate) |
| **Site coordination as fixed** | Understates cost of a long study | Charge per site-month for the full duration |
| **Close-out and reporting** | Runs out of money at the least recoverable moment | Budget close-out, database lock, and the final report explicitly |
| **Data management** | Absorbed into "IT" and then contested | Separate line, sized against participant count |
| **Statistics beyond the plan** | Analysis is charged as an overrun | Fund the analysis plan and one round of additional analysis |
| **Protocol amendments** | Every change becomes a change request | 10% contingency minimum |
| **Currency and inflation on multi-year studies** | Real cost drifts above the award | Explicit escalation line on studies over 24 months |

### Interpreting the cost performance index

| CPI | Meaning | Action |
|-----|---------|--------|
| **Above 1.05** | Delivery is running ahead of spend | Verify the milestone weights are honest before celebrating |
| **0.95 – 1.05** | On plan | Continue monitoring |
| **0.85 – 0.95** | Drifting | Identify the driver now; it rarely self-corrects |
| **0.70 – 0.85** | Materially over | Descope or seek funding — decide deliberately |
| **Below 0.70** | Forecast overrun above 40% | Stop and re-plan. Continuing spends the remaining budget on the same inefficiency. |

**[PROVEN]** The single most useful number in research finance is the gap
between percent spent and percent delivered. A gap above 20 points is the
reliable early signal of a supplementary funding request, and it appears months
before the calendar-based view shows anything wrong.

### Value of information

A study is worth funding to the extent that it changes a decision, and a decision
is worth informing to the extent that getting it wrong is expensive.

```
expected decision value = decision value × P(research changes the decision)
                          × reversibility multiplier
```

| Reversibility | Multiplier | Reasoning |
|---------------|-----------|-----------|
| Reversible in a sprint | 0.15 | A wrong choice costs one sprint to undo — information is nearly worthless |
| Reversible in a quarter | 0.45 | Correctable, but at real cost |
| Costly to reverse | 0.85 | Most of the decision value is genuinely at stake |
| One-way door | 1.0 | Full decision value at stake |

Two studies are automatically worth zero regardless of their inputs: one
informing a decision already made, and one answering after the decision deadline.
Both are common, and both survive portfolio review because nobody asks the
question directly.

### Cost per insight benchmarks

Cost per insight is a blunt instrument and a useful one — it forces a comparison
across methods that otherwise get evaluated in isolation.

| Method | Typical cost per decision-ready insight | Notes |
|--------|----------------------------------------|-------|
| Support ticket / call analysis | Lowest | Evidence already paid for; only analysis time |
| Instrumentation analysis | Low | Assumes instrumentation exists |
| Interview round (6-8 sessions) | Moderate | Recruiting and incentives dominate |
| Survey (400 completes) | Moderate | Panel cost dominates; falls sharply with an owned list |
| Experiment | Moderate | Engineering time is the real cost, and it is usually uncounted |
| Multi-site clinical study | Highest by orders of magnitude | Regulatory and site infrastructure dominate |

**[RECOMMENDED]** Count engineering time in experiment costs. It is the most
frequently omitted research cost in product organisations, and omitting it makes
experiments look free relative to studies that carry an explicit invoice.

## Anti-Patterns

### Budgeting the Enrolled, Screening the Many
**Mistake:** Building the participant budget on the enrolment target when the
protocol will screen substantially more people to reach it.
**Why it happens:** The enrolment number is the one in the protocol and the one
everyone quotes. The screen failure rate lives in a different section, if it is
written down at all.
**Instead:** Gross every screening-stage cost up by 1/(1 − screen failure rate).
At a 25% failure rate that is a third more screening assessments than the
enrolment target implies — and screening is real clinical work on real people
that someone has to pay for.

### Tracking Spend Against the Calendar
**Mistake:** A monthly report showing spend versus planned spend, with no
delivery measure alongside it.
**Why it happens:** Spend and calendar are both easy to measure and both come
from finance systems automatically. Delivery requires someone to assess
milestone completion honestly.
**Instead:** Weight the milestones, assess completion each period, and report the
spend-delivery gap as the headline. A study spending exactly to plan while
enrolling at half rate looks perfectly healthy on a calendar view and is heading
for a large overrun.

### Front-Loaded Milestone Weights
**Mistake:** Assigning heavy weights to setup milestones — protocol approved,
ethics obtained, first site activated — so the programme shows 40% delivered
before a single participant is enrolled.
**Why it happens:** Setup milestones are discrete, visible, and satisfying to
complete. Enrolment is a long grind with no natural checkpoints.
**Instead:** Weight by share of actual work and cost. Enrolment typically
deserves 40-50% of the total weight. Front-loaded weights hide exactly the
problem earned-value tracking exists to expose, and they hide it during the
window when descoping is still possible.

### Ranking the Portfolio by Cost
**Mistake:** Funding the cheap studies first because more of them fit in the
budget.
**Why it happens:** Cost is known precisely and decision value is an estimate, so
the ranking gravitates to the number that feels solid.
**Instead:** Rank by expected decision value per unit cost. A rough estimate of
decision value beats no estimate — it at least surfaces the studies costing more
than the decision is worth. Funding by cost systematically starves the expensive
studies attached to the largest decisions, which is precisely backwards.

### Funding the Decision Already Made
**Mistake:** A study that will report after the choice has been committed, kept
in the portfolio to validate it.
**Why it happens:** The work was scoped when the decision was still open, and
cancelling it feels like admitting the decision was made prematurely.
**Instead:** Ask directly, at every portfolio review, whether each study's
decision is still open and what result would change it. If nothing would, cut the
study and redirect the money. This is documentation, and it should be funded as
documentation if it is funded at all.

## Files

| File | Purpose |
|------|---------|
| `scripts/study_budget_builder.py` | Expands unit costs into line items, applies screen-failure grossing, contingency, and overhead; reports unit economics |
| `scripts/burn_vs_milestone_tracker.py` | Earned-value tracking of spend against milestone delivery, with completion forecast and overrun warning |
| `scripts/portfolio_prioritizer.py` | Ranks studies by expected decision value per unit cost and allocates a fixed budget |
| `references/research-cost-models.md` | Cost structures by method, unit-cost drivers, cost-per-insight modelling, common omissions |
| `references/funding-and-portfolio-allocation.md` | Funding sources, grant budget conventions, value-of-information method, portfolio governance |
| `assets/study-budget-template.md` | The budget document a funding request ships in |
| `assets/sample_budget.json` | Runnable input for the budget builder |
| `assets/sample_burn.json` | Runnable input for the burn tracker |
| `assets/sample_portfolio.json` | Runnable input for the portfolio prioritiser |
