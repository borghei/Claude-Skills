# Statistical Design Plan — <study name>

> Fill this in **before** collecting or looking at data. A plan written after
> the fact is not a plan, and every section below exists because filling it in
> late is where the study goes wrong.

**Owner:** <name>
**Date written:** YYYY-MM-DD
**Decision this informs:** <the specific action that will be taken>

---

## 1. Question

**Business question:** <plain language, one sentence>

**Statistical question:** <restated as a comparison, association, or trend>

**What we will do differently depending on the answer:** <if the answer changes
nothing, stop here and do not run the study>

---

## 2. Primary metric

| Field | Value |
|-------|-------|
| Metric name | |
| Definition (exact) | |
| Unit of measurement (user / session / order) | |
| Outcome type (binary / continuous / count / ordinal) | |
| Baseline value | |

**One primary metric only.** Secondary metrics are listed in section 6 and are
explicitly exploratory.

---

## 3. Decision threshold

| Field | Value |
|-------|-------|
| Minimum effect worth shipping (MDE) | |
| How that was derived | <cost to ship vs value per unit> |
| Direction of interest | one-sided intent / two-sided test |

Set before the data arrive. This is the number that turns the result into a
decision instead of an argument.

---

## 4. Design and sizing

| Field | Value |
|-------|-------|
| Randomized? | yes / no — if no, name the confounders |
| Assignment unit | |
| Groups and allocation | |
| Alpha | 0.05 |
| Power | 0.80 / 0.90 |
| Required n per group | <from test_selector.py> |
| Expected time to reach n | |
| Fixed horizon or sequential? | |

If the achievable n is below the required n, say so **here**, before running.
An underpowered study should be a conscious decision, not a discovery.

---

## 5. Test and assumptions

| Field | Value |
|-------|-------|
| Planned test | <from test_selector.py> |
| Why this test | |
| Fallback if assumptions fail | |
| Assumption checks to run | independence / skew / outliers / variance ratio |

**Independence check (mandatory):** how will you confirm one row per unit?
Clustering is the most common and most damaging violation, and almost nobody
checks it.

---

## 6. Secondary and guardrail metrics

| Metric | Type | Role | Correction |
|--------|------|------|------------|
| | | exploratory / guardrail | Benjamini-Hochberg |

Number of comparisons in the family: **<m>** → corrected alpha: **<alpha/m>**

---

## 7. Stopping rule

- [ ] Fixed horizon: we will look once, at n = <N> or date <D>
- [ ] Group sequential: interim looks at <points> with <spending function>
- [ ] Always-valid: confidence sequences, continuous monitoring

**We will not** monitor a fixed-horizon test and stop on significance.

---

## 8. Pre-specified subgroups

| Subgroup | Why specified in advance |
|----------|--------------------------|
| | |

Any subgroup not listed here is exploratory and will be described as such.

---

## 9. Reporting commitments

- [ ] Effect stated in domain units with a confidence interval
- [ ] Outcome shared regardless of direction or significance
- [ ] Deviations from this plan disclosed in the body, not a footnote
- [ ] If null: the upper bound of the effect we could have missed is stated

---

## Deviations log

| Date | What changed | Why | Approved by |
|------|--------------|-----|-------------|
| | | | |
