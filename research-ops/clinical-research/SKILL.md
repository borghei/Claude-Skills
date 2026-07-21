---
name: clinical-research
description: >
  Clinical study operations — protocol structure, endpoint selection,
  eligibility design, sample-size and power planning, site feasibility, and
  documentation readiness. Use when planning, auditing, or costing a study.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: research-ops
  domain: clinical-operations
  updated: 2026-07-21
  tags: [protocol, endpoints, sample-size, power, site-feasibility, ich-gcp]
---

# Clinical Research

Operational support for running clinical studies: structuring a protocol so it
survives review, choosing endpoints that are actually analysable, designing
eligibility criteria that do not strangle accrual, planning sample size and
power, and testing whether the site network can deliver the enrolment target.

> **Scope and limits.** This skill supports **study operations** — planning,
> structuring, and auditing. It is not a substitute for a qualified
> biostatistician, and it is not regulatory advice. The sample-size calculator
> assumes a simple parallel design with no interim analyses, multiplicity
> adjustment, covariate adjustment, or clustering; any design departing from
> those assumptions requires a statistician. The protocol auditor checks
> structure and internal consistency, not regulatory acceptability. Every
> artifact produced here needs sign-off from qualified biostatistics, clinical,
> and regulatory affairs personnel before it enters a submission.

## When to use this skill

- **Planning a study** and needing a defensible sample size before the budget
  and site count can be set
- **Auditing a draft protocol** for missing ICH E6 elements before it goes to an
  ethics committee or a sponsor review board
- **Choosing between candidate endpoints** where one is clinically meaningful
  and the other is achievable in the available sample
- **Designing inclusion and exclusion criteria** and needing to see the accrual
  cost of each additional restriction
- **Assessing site feasibility** — deciding how many sites, and which, are
  needed to hit an enrolment target inside the accrual window
- **Diagnosing an under-accruing study** and deciding between adding sites,
  extending the window, or amending eligibility

## Inputs the skill expects

- Study phase, design (parallel, crossover, single-arm), and blinding
- The primary question in a form that names the comparison
- Candidate endpoints with their measurement instrument and timepoint
- Effect size assumptions and their source — prior study, pilot, or literature
- Expected dropout rate, from comparable studies where possible
- For feasibility: candidate sites with eligible population, prior accrual
  attainment, startup time, and competing studies

## Clarify First

Before generating, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **The primary endpoint and its measurement timepoint** — everything downstream (sample size, visit schedule, site burden, cost) derives from it
- [ ] **The effect size and where it came from** — a literature effect and a pilot effect carry very different uncertainty, and a pilot-derived SD needs an inflation allowance
- [ ] **Design features that break the simple formulas** — interim analyses, co-primary endpoints, cluster randomisation, or crossover each require a different calculation and a statistician
- [ ] **The enrolment window and site network available** — a sample size that cannot be accrued is not a plan

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Workflows

### Workflow 1 — Plan sample size and power

1. Fix the primary endpoint and its type: binary, continuous, or time-to-event.
   This selects the design, and the design selects the formula.
2. State the effect size you want to detect and where it came from. **[PROVEN]**
   Power for the smallest effect that would change clinical practice, not for
   the effect you hope to see — the latter systematically under-powers studies.
3. Set alpha (0.05 two-sided unless the protocol justifies otherwise), power
   (80% minimum, 90% where feasible), allocation ratio, and dropout rate.
4. Run the calculator. Read both the analysed n and the enrol n — the dropout
   inflation is the number that drives the budget.
5. If you have a fixed n constrained by budget or accrual, pass it as
   `planned_n_per_group` and read the achieved power instead.
6. Take the result to a biostatistician. This step is not optional.

```bash
python3 research-ops/clinical-research/scripts/sample_size_calculator.py \
  --input research-ops/clinical-research/assets/sample_power_spec.json \
  --format text
```

### Workflow 2 — Audit a protocol outline

1. Map the draft protocol's sections onto the ICH E6 element keys.
2. Enter endpoints with role, measure, timepoint, and analysis population;
   enter inclusion and exclusion criteria verbatim.
3. Run the auditor. It reports missing sections, endpoints that cannot be
   analysed as written, eligibility criteria that conflict or duplicate, and
   gaps in the statistical and safety sections.
4. Clear every `fail` before circulating the draft. Missing sections and an
   unadjusted interim analysis are the two findings most likely to cost you a
   review cycle.

```bash
python3 research-ops/clinical-research/scripts/protocol_auditor.py \
  --input research-ops/clinical-research/assets/sample_protocol.json \
  --format text
```

### Workflow 3 — Test the site network against the enrolment target

1. Collect per-site data: eligible annual population, self-reported accrual
   estimate, prior accrual attainment, startup time, coordinator status, and
   competing studies.
2. Run the feasibility scorer. It discounts self-reported estimates, blends in
   the site's historical attainment, caps against eligible population, and
   subtracts startup time from the accrual window.
3. Read the shortfall. If it is positive, the choice is more sites, a longer
   window, or looser eligibility — decide deliberately rather than discovering
   it at month 14.
4. Use `--select` to test whether a smaller, higher-quality site set beats a
   larger one. It usually does on cost, and often on total accrual.

```bash
python3 research-ops/clinical-research/scripts/site_feasibility_scorer.py \
  --input research-ops/clinical-research/assets/sample_sites.json \
  --select 5 --format text
```

## Decision frameworks

### Endpoint type drives everything

| Endpoint type | Design | Sample driver | Typical relative n |
|---------------|--------|---------------|--------------------|
| **Continuous** (change in a scale) | Two means | Standardised effect size δ/σ | Smallest |
| **Binary** (responder yes/no) | Two proportions | Absolute difference and baseline rate | 2-4x the continuous equivalent |
| **Time-to-event** | Log-rank | Hazard ratio and event probability | Driven by events, not enrolment |
| **Count / rate** | Poisson or negative binomial | Rate ratio and dispersion | Requires a statistician |
| **Composite** | Depends on components | The component that dominates | Interpretation risk is high |

**[PROVEN]** Where the same clinical question can be posed as continuous or
binary, the continuous version needs materially fewer participants.
Dichotomising a continuous measure discards information and inflates n — do it
only when the threshold itself is what is clinically meaningful.

### Effect size sources and their reliability

| Source | Reliability | Adjustment |
|--------|-------------|------------|
| Large completed trial in the same population | **[PROVEN]** highest | Use as-is |
| Meta-analysis of comparable trials | **[PROVEN]** high | Use the pooled estimate; check heterogeneity |
| Single published trial, different population | **[RECOMMENDED]** moderate | Discount by 20-30%; effects rarely transfer intact |
| Internal pilot study | **[RECOMMENDED]** moderate | Add 10-15% to n; a pilot SD is imprecise |
| Clinician consensus on the minimum meaningful difference | **[RECOMMENDED]** | Best basis for the *target*, not for the variance |
| The effect needed to make the business case work | Not a source | This is how under-powered studies get funded |

That last row is a real failure mode. When the affordable sample size is
back-solved into an effect size, the study is designed to fail and the failure
is uninterpretable — you cannot distinguish "no effect" from "not enough people."

### Eligibility restrictiveness

Every criterion trades internal validity for accrual and generalisability.

| Criteria count | Typical effect |
|----------------|----------------|
| Under 15 | Broad, fast accrual, high generalisability |
| 15-25 | Standard for a phase 3 study |
| 25-35 | Screen failure rates climb steeply; accrual timelines stretch |
| Over 35 | Accrual frequently fails; the treated population may not resemble the studied one |

**[RECOMMENDED]** For every criterion beyond about 20, require a written
justification naming the specific safety or interpretability risk it addresses.
Criteria accumulate through review by addition — nobody is ever assigned to
remove one — and the cumulative accrual cost is invisible at the point each is
added.

## Anti-Patterns

### Back-Solved Power
**Mistake:** Deciding the affordable sample size first, then choosing the effect
size that makes that n reach 80% power.
**Why it happens:** The budget is fixed before the science is planned, and the
calculation is treated as a document to produce rather than a constraint to
respect.
**Instead:** Compute n from the smallest clinically meaningful effect. If that n
is unaffordable, the honest options are to seek more funding, run a smaller
study explicitly labelled as a pilot with a feasibility objective, or not run
it. A study powered for an implausibly large effect consumes the same budget and
produces an uninterpretable result.

### The Optimistic Site Estimate
**Mistake:** Building the accrual plan on the enrolment rates sites report during
feasibility questionnaires.
**Why it happens:** Sites want to be selected, the estimate is made by someone
who is not the person who will do the recruiting, and nobody is ever penalised
for an optimistic feasibility response.
**Instead:** Discount every self-reported estimate substantially and weight by
the site's actual attainment on previous studies. Cross-check against the
eligible population they reported — a site claiming 8 participants a month from
a clinic seeing 180 eligible patients a year is claiming a screening yield that
does not occur. Plan for the discounted number and treat outperformance as
upside.

### Criterion Creep
**Mistake:** Each protocol review round adds two or three exclusion criteria, and
the final protocol has 40.
**Why it happens:** Every reviewer can name a subgroup that might complicate
interpretation, and adding an exclusion is a costless-looking way to resolve the
comment. Nobody's job is to remove one.
**Instead:** Cap the criteria count in the protocol plan and treat additions as
trade-offs requiring an explicit removal or a written justification of the
accrual cost. Track the projected screen failure rate as criteria accumulate and
put that number in front of reviewers.

### The Unanalysable Endpoint
**Mistake:** A primary endpoint like "improvement in patient wellbeing" with no
named instrument, threshold, or timepoint.
**Why it happens:** It is written early as a placeholder during objective-setting
and is never converted into an operational definition.
**Instead:** Every endpoint needs four things before the protocol circulates: the
instrument, the metric derived from it, the threshold or contrast that defines
the outcome, and the timepoint. If any of the four is missing, the endpoint
cannot be powered, collected consistently, or analysed.

### Silent Interim Looks
**Mistake:** Planning an interim analysis without an alpha spending function,
or examining accumulating data informally "just to see how it is going."
**Why it happens:** Interim looks feel like prudent management, and the
statistical cost is invisible to anyone not looking for it.
**Instead:** Pre-specify every interim analysis with its alpha spending function
and stopping boundaries, and restrict access to unblinded accumulating data to
an independent monitoring committee. Unadjusted repeated testing inflates type I
error, and an informal look by the sponsor team compromises the trial's
integrity even when nothing is acted on.

## Files

| File | Purpose |
|------|---------|
| `scripts/sample_size_calculator.py` | Sample size and power CLI: input validation, dropout inflation, planning warnings, and reporting |
| `scripts/power_formulas.py` | Design formulas imported by `sample_size_calculator.py`: the two-proportion, two-mean (with t-correction), and log-rank sample-size calculations, the achieved-power inversions, and the method notes reported with every result. Edit here to revise the statistics |
| `scripts/protocol_auditor.py` | Audits a protocol outline against ICH E6 elements, endpoint definitions, and eligibility consistency |
| `scripts/protocol_rules.py` | Rule definitions imported by `protocol_auditor.py`: the ICH E6 required-section table and its guidance strings, vague-measure and DSMB-phase thresholds, the SAE reporting window, severity ordering, and the finding accumulator. Edit here to revise what the audit expects |
| `scripts/site_feasibility_scorer.py` | Discounts site accrual estimates and tests the network against the enrolment target |
| `references/protocol-and-endpoint-design.md` | ICH E6 protocol contents, endpoint hierarchies, eligibility design, estimand framing |
| `references/statistical-planning.md` | Formulas, worked examples, design effects, interim analysis, and when to escalate to a statistician |
| `assets/protocol-outline-template.md` | The protocol skeleton with every required element |
| `assets/sample_power_spec.json` | Runnable input for the sample size calculator |
| `assets/sample_protocol.json` | Runnable input for the protocol auditor |
| `assets/sample_sites.json` | Runnable input for the site feasibility scorer |
