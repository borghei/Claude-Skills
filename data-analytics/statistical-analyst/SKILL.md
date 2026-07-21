---
name: statistical-analyst
description: >
  Applied statistics for business and product questions — test selection,
  assumption checks, power planning, effect sizes with intervals, multiplicity
  correction. Use when interpreting an experiment, sizing a study, or vetting
  a claim.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: data-analytics
  domain: statistics
  updated: 2026-07-21
  tags: [statistics, hypothesis-testing, effect-size, power-analysis, experimentation]
---

# Statistical Analyst

Most bad statistics in business are not arithmetic errors. They are the wrong
test on the right data, a null result reported as "no difference," a p-value
mistaken for an effect size, or twenty comparisons run and the one that cleared
0.05 written up. This skill covers the applied path: pick the test the data
shape actually calls for, check the assumptions that carry weight, size the
study before running it, report effects with intervals rather than bare
p-values, and say what you found to people who do not want a statistics lecture.

Everything here runs on the Python standard library — the t, chi-square, and
normal distributions are implemented directly, so there is no scipy dependency
between a question and an answer. Because those implementations are hand-rolled,
`stats_core.py --selftest` verifies all of them against published reference
values; run it once before trusting any result.

## When to use this skill

- An A/B test finished and someone needs to know whether to ship
- A study is being designed and nobody has computed how many observations it needs
- A stakeholder is quoting a p-value as if it were an effect size
- A "no difference" result is about to be reported from a study that was underpowered
- Several variants, metrics, or segments were compared and no correction was applied
- The data are skewed or outlier-heavy and the default t test is about to be run anyway

## Inputs the skill expects

- The business question and what decision it will change
- The outcome variable and its type (binary, continuous, count, ordinal, categorical)
- Group structure — how many groups, independent or paired, randomized or observational
- Observation counts per group, and the unit of measurement (user, session, order)
- The baseline value and the smallest effect worth acting on
- How many comparisons are in the family, and which metric was named primary before the data arrived

## Clarify First

Before analyzing, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **The unit of measurement, and whether each unit appears once** — clustering (many sessions per user counted as independent rows) deflates standard errors and manufactures significance; it invalidates every test below
- [ ] **The smallest effect worth acting on** — without it there is no way to size the study or to say whether a significant result matters
- [ ] **How many comparisons are in the family, and which metric was primary** — decides the correction and whether the result is confirmatory or exploratory
- [ ] **Whether anyone has already looked at the data while it accumulated** — peeking invalidates a fixed-horizon test and changes the whole approach

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Workflows

### Workflow 1 — Choose the test and size the study before collecting data

1. Write down the business question and the decision it changes. If the answer
   changes nothing, stop — do not run the study.
2. Fill in the outcome type, group structure, baseline, and the minimum effect
   worth shipping into a question spec.
3. Run the selector. It returns one test, its load-bearing assumptions, the
   fallback when they fail, and the sample size the stated effect requires.
4. If the achievable sample is below the required sample, say so **before**
   running. An underpowered study should be a conscious decision, not a
   discovery at write-up time.
5. Record everything in `assets/experiment_design_template.md`.

```bash
python3 data-analytics/statistical-analyst/scripts/test_selector.py \
  --input data-analytics/statistical-analyst/assets/sample_question.json \
  --power 0.9
```

### Workflow 2 — Run the test and report the effect, not the p-value

1. Check independence first: count units versus count rows. More rows than
   units means clustering, and no test below is valid until that is handled.
2. Inspect skew and outliers (mean vs median, top and bottom five values). If
   the data are heavy-tailed at small n, switch to Mann-Whitney.
3. Run the test with the number of comparisons in the family declared, so the
   threshold is corrected.
4. Read the effect size and the interval first. Report the effect in domain
   units, the interval in the same units, and the decision implication.

```bash
python3 data-analytics/statistical-analyst/scripts/stats_core.py --selftest

python3 data-analytics/statistical-analyst/scripts/run_test.py \
  --input data-analytics/statistical-analyst/assets/sample_experiment.json \
  --comparisons 3
```

### Workflow 3 — Audit someone else's statistical claim

1. Ask what the unit of measurement was and whether units repeat. This finds
   more real errors than every distributional check combined.
2. Ask how many comparisons were run in total, including the ones not reported,
   and whether the primary metric was named before the data arrived.
3. Re-run the test from the raw counts, with the true comparison count.
4. If the claim is a null result, compute the interval and state the largest
   effect the study could have missed — "no difference" and "we could not tell"
   look identical in a significance test and are opposite conclusions.

```bash
python3 data-analytics/statistical-analyst/scripts/run_test.py \
  --input data-analytics/statistical-analyst/assets/sample_revenue.json \
  --test welch_t --comparisons 4 --format json
```

## Decision frameworks

### Test selection

| Question | Outcome | Groups | Test | Effect size |
|----------|---------|--------|------|-------------|
| Difference | Binary | 2 independent | [PROVEN] Two-proportion z | Absolute difference; Cohen's h |
| Difference | Binary | 2 paired | [PROVEN] McNemar | Odds ratio on discordant pairs |
| Difference | Binary/categorical | 3+ | [PROVEN] Chi-square of independence | Cramér's V |
| Difference | Continuous, symmetric | 2 independent | [PROVEN] Welch's t | Mean difference; Hedges' g |
| Difference | Continuous, skewed or n<15 | 2 independent | [PROVEN] Mann-Whitney U | Rank-biserial r |
| Difference | Continuous | 3+ | [RECOMMENDED] One-way ANOVA | Eta-squared |
| Difference | Count per exposure | 2 | [RECOMMENDED] Poisson rate ratio | Rate ratio |
| Association | Two continuous | — | [PROVEN] Pearson, or Spearman if skewed | r, r² |
| Change over time | Any | — | [RECOMMENDED] Interrupted time series | Level and slope change |

**Use Welch's t, never Student's t, as the two-group default.** It does not
assume equal variances and costs a fraction of a degree of freedom when they
are equal. Testing for equal variance first and then choosing is worse than
always using Welch — the pre-test inflates the error rate of the whole
procedure.

### Reading an interval against your decision threshold

| Interval position | Reading | Action |
|-------------------|---------|--------|
| Entirely above the threshold | Real and big enough | Ship |
| Above zero, straddles the threshold | Real, unclear if it clears the bar | Collect more, or decide on cost |
| Straddles zero, **narrow** | Genuinely no meaningful effect | Do not ship — and this is the only case where "no difference" is honest |
| Straddles zero, **wide** | Study could not answer the question | Report as inconclusive, state the upper bound |

The last two are identical in a significance test and are opposite conclusions.
That is the strongest single argument for reporting intervals.

### Sample size reality check

Per group, α = 0.05, power = 0.80:

| Baseline rate | Relative effect to detect | n per group |
|---------------|---------------------------|-------------|
| 2% | +10% | ~78,000 |
| 8% | +10% | ~28,500 |
| 8% | +25% | ~4,900 |
| 20% | +10% | ~9,000 |
| 20% | +25% | ~1,600 |

Most product experiments are sized by "how long can we wait," which is how
underpowered studies get written up as "no difference."

## Anti-Patterns

### P-hacking by exploration
**Mistake:** Twenty metrics, six segments, and three time windows get compared; the one combination that clears p < 0.05 becomes the headline.
**Why it happens:** It rarely feels like cheating. Each individual comparison is a reasonable question, the analyst is genuinely curious, and the tooling makes slicing free. Nobody counts the comparisons because nobody wrote them down.
**Instead:** Name one primary metric before the data arrive and pre-register the subgroups you will examine. Everything else is exploratory, gets Benjamini-Hochberg correction, and is reported as hypothesis-generating rather than decisive. With α = 0.05 and 20 uncorrected comparisons, the chance of at least one false positive is 64% — a coin flip dressed as a finding.

### Peeking at a running experiment
**Mistake:** The dashboard is checked daily and the test is stopped the moment p dips below 0.05.
**Why it happens:** The data are right there, stopping early saves time and traffic, and each individual look feels harmless. The intuition that "more data can only help" is exactly backwards here.
**Instead:** Fix the horizon, compute n up front, and do not look — or use a method built for continuous monitoring (group sequential with O'Brien-Fleming spending, or always-valid confidence sequences). Repeated peeking at an uncorrected fixed-horizon test drives the real false-positive rate to 20-30%: a random walk crosses the threshold eventually even when nothing is happening. If it has already happened, report the result as exploratory and re-run with a fixed horizon.

### Reading a null result as "no effect"
**Mistake:** p = 0.31, so the memo says the change made no difference and the feature is killed.
**Why it happens:** "Not significant" sounds like "no effect," and the alternative sentence — "we ran a study that could not answer the question" — is uncomfortable to write.
**Instead:** Report the interval. If it runs from −0.2% to +4.1%, the study is consistent with a substantial gain and has ruled out almost nothing. State the largest effect you could have missed. Only a *narrow* interval around zero supports "no meaningful effect," and that distinction is invisible in the p-value.

### Confusing significance with importance
**Mistake:** At n = 400,000 a 0.02% conversion difference reaches p < 0.001 and gets a roadmap slot.
**Why it happens:** p-values conflate effect size with sample size, so at large n everything is significant. The number looks impressive precisely because the sample is large.
**Instead:** Set the decision threshold from the economics — cost to ship divided by value per unit — before the analysis. Then compare the interval to that threshold, not to zero. The reciprocal error matters equally: at small n, an important effect can miss significance and get discarded.

### Ignoring the unit of measurement
**Mistake:** A test on 50,000 sessions from 4,000 users treats every session as an independent observation.
**Why it happens:** The event table has 50,000 rows, the tooling counts rows, and the resulting p-value is gratifyingly small. It is invisible unless someone explicitly compares row count to unit count.
**Instead:** Aggregate to the unit of assignment before testing, or use a cluster-robust method. Treating clustered rows as independent can understate the standard error several-fold and turn pure noise into a highly significant result. This is the single most common invalidating error in applied product analytics, and the cheapest to check.

## Files

| File | Purpose |
|------|---------|
| `scripts/test_selector.py` | Recommends one test from question type, outcome type, group structure, and distribution; returns assumptions, fallback, required sample size for a stated MDE, and design warnings |
| `scripts/run_test.py` | Runs two-proportion z, Welch's t, chi-square, and Mann-Whitney with effect sizes, confidence intervals, Bonferroni-adjusted thresholds, and assumption warnings |
| `scripts/test_impl.py` | The four test implementations behind `run_test.py`, with their effect-size magnitude readings; `--selftest` verifies each against a worked example |
| `scripts/stats_core.py` | Normal, Student's t, and chi-square distributions plus the Wilson interval, in stdlib `math` only; `--selftest` verifies all 18 against published reference values |
| `references/test-selection-and-assumptions.md` | Selection tree, which assumptions are load-bearing and how each fails, power formulas and sizing tables, multiple-comparison corrections, sequential testing |
| `references/effect-sizes-and-communication.md` | Effect sizes per test with thresholds, interval choice and interpretation, language for non-statisticians, practical-vs-statistical significance, reporting checklist |
| `assets/sample_question.json` | Question spec for the selector — an underpowered 3-variant conversion test |
| `assets/sample_experiment.json` | Two-proportion conversion data |
| `assets/sample_revenue.json` | Continuous order-value data for Welch's t |
| `assets/sample_contingency.json` | 3x4 contingency table for chi-square |
| `assets/sample_session_times.json` | Right-skewed time-on-task data for Mann-Whitney |
| `assets/experiment_design_template.md` | Pre-registration template: question, primary metric, decision threshold, sizing, stopping rule, deviations log |
