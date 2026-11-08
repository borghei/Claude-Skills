---
name: launch-economics
description: >
  Pre-launch unit economics, year-one cash model and a computed go/not-yet
  verdict for a new business. Use when asking "is this profitable", finding
  break-even, sizing startup cash, or deciding whether to launch.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: finance
  domain: venture-viability
  updated: 2026-11-08
  tags: [unit-economics, break-even, cash-runway, small-business, launch, viability]
---

# Launch Economics

Margins decide whether a good idea is a business. This skill builds the numbers
for a business that has not opened yet: what each sale leaves after its own
costs, how many sales a day cover the fixed costs, what year one looks like
month by month, how deep the cash hole gets before the business pays for
itself, and which assumption would sink it. It then computes a verdict from
those numbers and the demand evidence collected so far. The verdict is never
written by hand.

The agent treats every number as traceable: each cost line carries its source
(quote, public price, or estimate), and the report says which conclusions rest
on guesses.

## When to use this skill

- **"Is this profitable?"** for a shop, kitchen, studio, service or online store
  that has not launched
- **Finding break-even** in sales per day and checking it against capacity
- **Sizing the cash** a founder must carry before the business funds itself
- **Stress-testing a plan** against a lower price, slower sales or cost inflation
- **Deciding whether to launch, wait or rework**, with a verdict a partner or
  lender can audit
- **Comparing two versions** of the same idea (different price, premises, model)

For recurring-revenue software metrics (LTV, CAC, churn, MRR) use a SaaS metrics
skill instead; this one models per-sale businesses with a physical or service
capacity.

## Inputs the skill expects

- The unit (one sale as the customer sees it) and its price before sales tax
- Variable cost lines per unit, each tagged `quote`, `public` or `estimate`
- Fixed monthly cost lines and one-off startup cost lines, tagged the same way
- Operating days per month, steady-state sales per day, and capacity per day
- A 12-month ramp of sales per day
- For the verdict: cash available to the founder and every demand test run so far

## Clarify First

The ramp and the largest cost lines shape this output more than anything else.
Settle the inputs below before producing anything. When one is missing or vague
and would change the result, ask about it; when it wouldn't, use a sensible
default and say which one you used.

- **Price and what one unit is:** contribution, break-even and every what-if are
  computed per unit; an average ticket and a best-seller price give different
  businesses.
- **Rent and wages the founder will actually pay:** these dominate fixed costs
  and therefore break-even; an estimate here moves the verdict more than any
  other line.
- **Capacity per day:** without it the model cannot say whether break-even is
  physically reachable.
- **Cash the founder can put in:** the verdict compares it with the cash trough,
  not with the startup budget.

Ask about the two or three inputs that matter most for this request, not the
whole list. If the user wants a result straight away, produce it and state your
assumptions at the top, with every assumed line tagged `estimate`.

## Quick Start

```bash
# 1. Model the economics (exit 1 if any check fails)
python3 finance/launch-economics/scripts/launch_economics.py \
  --input finance/launch-economics/assets/sample_launch_numbers.json

# 2. Save the report as JSON for the verdict
python3 finance/launch-economics/scripts/launch_economics.py \
  --input finance/launch-economics/assets/sample_launch_numbers.json \
  --format json > report.json

# 3. Compute the verdict from the report and the demand evidence
python3 finance/launch-economics/scripts/viability_verdict.py \
  --economics report.json \
  --evidence finance/launch-economics/assets/sample_evidence.json
```

## Tools Overview

| Tool | Input | Output | Exit codes |
|------|-------|--------|------------|
| `launch_economics.py` | Numbers JSON | Contribution, break-even/day, margin at plan, 12-month table, cash needed, payback month, four what-ifs, findings | 0 clean, 1 fail finding, 2 bad input |
| `viability_verdict.py` | Report JSON + evidence JSON | VIABLE / UNCONFIRMED / NOT YET / INCOMPLETE with every check and next actions | 0 VIABLE or UNCONFIRMED, 1 NOT YET or INCOMPLETE, 2 bad input |

Both tools are stdlib-only, deterministic, and support `--format text|json`.
`launch_economics.py` also takes `--price` and `--volume-factor` for quick
what-ifs without editing the file.

## Workflows

### Workflow 1 — Build the numbers

1. Write down the unit and the price before tax. If the ticket varies, use the
   average and record how it was estimated.
2. List variable costs per unit, fixed costs per month and startup costs. File
   each line in the right bucket (see `references/pre-launch-unit-economics.md`).
3. Tag every line with its source. Figures only the founder can supply, such as
   a landlord's quote or the pay they plan to offer, are asked for, not invented.
4. Set the 12-month ramp. If a pre-sale, pop-up or panel ran, use it to anchor
   month 1 and say how.
5. Run `launch_economics.py`. Resolve every `FAIL` before going further; each
   `WARN` needs one sentence in the memo.

```bash
python3 finance/launch-economics/scripts/launch_economics.py \
  --input numbers.json --format text
```

### Workflow 2 — Find the line to watch and improve the margin

1. Read the what-if table. The most sensitive driver is the assumption the plan
   cannot afford to get wrong.
2. Run each improvement lever as a what-if rather than estimating its effect:

```bash
python3 finance/launch-economics/scripts/launch_economics.py --input numbers.json --price 52
python3 finance/launch-economics/scripts/launch_economics.py --input numbers.json --volume-factor 0.8
```

3. Record three levers with the margin before and after each, and keep only the
   ones the founder can actually pull.
4. Validate that the improved model still respects capacity; a price cut that
   needs more volume than the counter can serve is not an improvement.

### Workflow 3 — Compute the verdict

1. Save the report with `--format json`.
2. Write the evidence file: `funding_available` and every demand test with
   people reached, people converted, and whether the real price was shown.
3. Run `viability_verdict.py`. The verdict is the quality gate: the agent never
   writes VIABLE by hand and never rounds a failing number into a passing one.
4. If the verdict is NOT YET, lead the memo with the failing checks and the
   action that fixes each. If UNCONFIRMED, the next step is a priced real-world
   test aimed at the most sensitive driver.
5. Fill `assets/viability-memo-template.md` with the same numbers, word for word.

```bash
python3 finance/launch-economics/scripts/viability_verdict.py \
  --economics report.json --evidence evidence.json --format json
```

### Validation checkpoint before sharing the memo

Use this checklist; every box must pass before the memo leaves the founder's
desk:

- [ ] Every cost line has a source tag, and the three largest are quotes
- [ ] Prices are before sales tax, and the memo says so
- [ ] Cash needed in the memo is the trough from the tool, not the startup total
- [ ] Verdict pasted from the tool output, with its failing checks listed
- [ ] Simulated demand, if any, is labelled as simulated and never quoted as a customer

## Decision frameworks

### What the verdict means and what to do next

| Verdict | Meaning | Recommended next step |
|---------|---------|-----------------------|
| **VIABLE** | Numbers pass and real people paid at the real price | **[RECOMMENDED]** Commit spend in stages, re-running the model on real month-1 data |
| **UNCONFIRMED** | Numbers pass; demand is simulated, unpriced or too small a sample | **[PROVEN]** Run a pre-sale or pop-up at the real price before signing a lease |
| **NOT YET** | At least one check fails | **[PROVEN]** Fix the failing number first; do not spend on brand or marketing yet |
| **INCOMPLETE** | An input is missing | Fill the gap; do not substitute a guess for a missing check |

### Healthy ranges for a small launch

| Measure | Healthy | Flag when |
|---------|---------|-----------|
| Break-even / capacity | Under 60% | Over 100% (fail): the business cannot break even at full stretch |
| Month-1 ramp / plan | 30-60% | 80% or more (warn): needs evidence |
| Payback | Within 12 months | Beyond 12 months (warn) |
| Estimated share of cost base | Under 50% | Over 50% (warn): get quotes |
| Funding / cash needed | 1.2x or more | Under 1.0x (fail), 1.0-1.2x (warn) |

**[RECOMMENDED]** Fund the trough plus 20%. Pre-launch timelines slip, and every
month of delay is a month of fixed costs without revenue.

### Which lever to pull first

**[RECOMMENDED]** Test a price rise before a cost cut. The whole price increase
lands in contribution, while most cost cuts touch quality the customer notices.
Cut costs first only when one variable line (often a platform commission) is
larger than the contribution itself.

## Anti-Patterns

### The Startup-Budget Fallacy
**Mistake:** Raising exactly the startup budget and treating it as the money needed.
**Why it happens:** The fit-out and equipment list is concrete; early operating losses feel hypothetical.
**Instead:** Fund the cash trough the tool reports (startup spend plus early
losses) plus a 20% buffer. The trough is usually 20-50% above the startup total.

### Month One at Plan
**Mistake:** Copying steady-state volume into month 1 of the ramp.
**Why it happens:** The plan volume was the number used to decide the idea was good, so it gets reused everywhere.
**Instead:** Start at 30-60% of plan unless a pre-sale or pilot measured more,
and cite that test. The tool warns at 80% for exactly this reason.

### Percentage Fees Frozen in Place
**Mistake:** Entering card or platform fees as fixed money amounts, then running a price what-if.
**Why it happens:** The fee was converted once at the original price and never revisited.
**Instead:** Recompute percentage-based variable costs at each tested price and
re-run. A 30% platform commission rises with every price increase.

### The Panel as Proof
**Mistake:** Treating a simulated buyer panel's buy rate as demand evidence and calling the plan viable.
**Why it happens:** The panel produced a number, and numbers feel like data.
**Instead:** Use the panel to find objections and segments, then confirm with a
priced real test. The verdict tool caps panel-only evidence at UNCONFIRMED.

### Writing the Verdict by Hand
**Mistake:** Summarising a plan as "profitable" because the steady-state month is positive.
**Why it happens:** The steady-state month is the most flattering view and the easiest to read.
**Instead:** Paste the computed verdict. Year one, capacity and funding are
separate checks, and a positive steady state can coexist with all three failing.

## Reference Documentation

- `references/pre-launch-unit-economics.md` — choosing the unit, filing costs,
  sourcing numbers, setting a ramp, reading outputs, improving a thin margin
- `references/demand-evidence-ladder.md` — what each kind of demand test proves,
  why simulated buyers cannot confirm demand, picking thresholds

## Files

| File | Purpose |
|------|---------|
| `scripts/launch_economics.py` | Unit economics, break-even, 12-month cash model, what-ifs, findings |
| `scripts/viability_verdict.py` | Computed verdict from the economics report and demand evidence |
| `references/pre-launch-unit-economics.md` | How to build and read pre-launch numbers |
| `references/demand-evidence-ladder.md` | Evidence strength, test selection, threshold rationale |
| `assets/sample_launch_numbers.json` | Sound example: a bicycle repair counter (exit 0) |
| `assets/sample_launch_numbers_flawed.json` | Deliberately flawed example: delivery kitchen (exit 1) |
| `assets/sample_economics_report.json` | JSON report from the sound example, input for the verdict |
| `assets/sample_economics_report_flawed.json` | JSON report from the flawed example |
| `assets/sample_evidence.json` | Evidence that confirms demand (verdict VIABLE, exit 0) |
| `assets/sample_evidence_flawed.json` | Panel-only and unpriced evidence with thin funding (NOT YET, exit 1) |
| `assets/viability-memo-template.md` | The memo a verdict ships in |

## Scope & Limitations

**In Scope:**
- Per-unit contribution, break-even per day, operating margin at plan and a
  12-month cash model with `launch_economics.py`
- Cash trough, payback month and four fixed what-ifs (price, volume, unit cost,
  fixed cost)
- A computed verdict combining economics, funding and demand evidence with
  `viability_verdict.py`
- Guidance on sourcing numbers, setting a ramp and choosing the next demand test

**Out of Scope:**
- SaaS subscription metrics such as LTV, CAC, churn and MRR
- Valuation, DCF and fundraising terms
- Tax, payroll, depreciation and legal structure
- Generating the demand evidence itself (running panels, pre-sales or pilots)

**Important Caveats:**
- Outputs are projections. They are only as good as the inputs, and inputs
  tagged `estimate` are guesses with reasoning, not facts.
- The model has one price and one unit cost; multi-product businesses should use
  a weighted average ticket and say so.
- Operating profit is before tax and before owner pay beyond the wages listed.
- Not financial, tax or legal advice. An accountant should confirm structure,
  payroll costs and tax before money moves.
