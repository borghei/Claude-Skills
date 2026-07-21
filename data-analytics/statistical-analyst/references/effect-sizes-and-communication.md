# Effect Sizes, Intervals, and Communicating Uncertainty

A p-value answers "would this data be surprising if nothing were happening?"
Almost nobody wants the answer to that question. They want to know how big the
effect is and how sure you are. This reference covers effect sizes, intervals,
and how to say all of it to people who do not want a statistics lecture.

---

## 1. What the p-value is not

Four misreadings, in order of how often they appear in real decision memos:

| Claim | Status | What is actually true |
|-------|--------|-----------------------|
| "p = 0.03, so there is a 97% chance the effect is real" | **Wrong** | p is the probability of data this extreme *given no effect*, not the probability of an effect given the data. |
| "p = 0.20, so there is no difference" | **Wrong** | Absence of evidence. The interval may include large effects. |
| "p = 0.001, so the effect is large" | **Wrong** | p conflates effect size with sample size. At n = 500,000 a 0.01% lift gets p < 0.001. |
| "p went from 0.06 to 0.04, the effect strengthened" | **Wrong** | The difference between significant and not significant is not itself significant. |

The single reliable fix is to lead with the effect size and its interval, and
to mention the p-value last or not at all.

---

## 2. Effect sizes by test

| Test | Effect size | Formula | Negligible / small / medium / large |
|------|-------------|---------|-------------------------------------|
| Two-proportion | **Absolute difference** (primary) | p₂ − p₁ | Judge against the business threshold, not a table |
| Two-proportion | Relative lift | (p₂ − p₁)/p₁ | Intuitive but misleading at tiny baselines |
| Two-proportion | Cohen's h | 2·asin√p₂ − 2·asin√p₁ | <0.2 / 0.2 / 0.5 / 0.8 |
| Welch's t | **Mean difference in raw units** (primary) | m₂ − m₁ | Against the business threshold |
| Welch's t | Hedges' g | Cohen's d × (1 − 3/(4N−9)) | <0.2 / 0.2 / 0.5 / 0.8 |
| Chi-square | Cramér's V | √(χ²/(n·min(r−1,c−1))) | <0.1 / 0.1 / 0.3 / 0.5 |
| Mann-Whitney | Rank-biserial r | 1 − 2U₁/(n₁n₂) | <0.1 / 0.1 / 0.3 / 0.5 |
| Correlation | r and r² | — | r² is the share of variance explained |

**[RECOMMENDED] Report the raw-unit effect first and the standardized effect
second.** "Average order value rose $5.54 (95% CI −$0.23 to $11.30)" is a
sentence a business reader can act on. "Hedges' g = 0.41" is a sentence for the
appendix. The standardized measure exists to compare across studies with
different units, which is rarely the question being asked.

**Cohen's thresholds are conventions, not laws.** They were proposed as rough
guidance for psychology research where no domain benchmark existed. In a mature
product, a "negligible" h = 0.04 on conversion can be worth millions, and a
"large" effect on a metric nobody optimizes can be worth nothing. Always
anchor to a domain threshold when one exists.

---

## 3. Confidence intervals

An interval carries everything a p-value does — if it excludes zero, p < α —
plus the magnitude information the p-value throws away. There is no situation
where reporting only the p-value is better.

### Which interval to use

| Quantity | Interval | Why not the obvious one |
|----------|----------|-------------------------|
| Single proportion | **Wilson score** | The textbook normal interval misbehaves badly near 0 and 1 and at small n — it can produce bounds below 0. |
| Difference of proportions | **Newcombe hybrid score** | Built from the two Wilson intervals; far better coverage than the naive normal difference. |
| Difference of means | **Welch t interval** | Does not assume equal variances. |
| Median or rank shift | Hodges-Lehmann, or bootstrap percentile | The rank tests do not produce an interval directly. |
| Anything awkward (ratios, custom metrics) | **Bootstrap percentile**, 10,000 resamples | No closed form needed; the honest default when the statistic is not standard. |

### Reading an interval honestly

An interval of [−0.23, +11.30] on a dollar effect is not "no effect." It is
"anywhere from slightly negative to a large gain — this study did not resolve
the question." That is a different, and far more useful, statement than "not
significant." State the upper bound out loud: it tells the reader what you
have failed to rule out.

Conversely, an interval of [+0.1%, +0.3%] on conversion is a *precise* result,
even if the effect is small. Precision and magnitude are separate axes; the
combination determines the decision.

### The four interval shapes and what each means

| Interval relative to zero and the decision threshold | Reading |
|------------------------------------------------------|---------|
| Entirely above threshold | Ship. Effect is real and big enough. |
| Above zero, straddles threshold | Real effect, unclear whether it clears the bar. Collect more or decide on cost. |
| Straddles zero, narrow | Genuinely no meaningful effect. This is the only case where "no difference" is honest. |
| Straddles zero, wide | Inconclusive. The study could not answer the question. Do not report as "no effect." |

The last two look identical in a significance test and are opposite conclusions.
This is the strongest single argument for reporting intervals.

---

## 4. Communicating to non-statisticians

### The four-line result

Every statistical result a decision-maker sees should fit this shape:

1. **The finding, in domain units.** "Checkout completion rose 1.2 percentage
   points, from 8.2% to 9.4%."
2. **The uncertainty, in the same units.** "Plausible range: +0.1 to +2.3
   points."
3. **The decision implication.** "Even the low end clears our 0.5-point
   shipping bar, so this ships."
4. **The main caveat.** "One caveat: three variants were tested, so this was
   assessed against a corrected threshold."

No test names, no p-values, no Greek. If asked, the details are in the appendix.

### Language substitutions

| Instead of | Say |
|------------|-----|
| "Statistically significant" | "Larger than we'd expect from chance variation" |
| "Not significant" | "This study couldn't tell the difference" (if wide) or "Any effect is smaller than X" (if narrow) |
| "p < 0.05" | "Plausible range excludes zero" |
| "We failed to reject the null" | "We didn't find an effect, and here's how big an effect we could have missed" |
| "Trending toward significance" | Nothing. Delete the sentence. It means "not significant" with hope attached. |

### Visuals that carry uncertainty

Point estimates without error bars are the most common way uncertainty gets
lost between the analysis and the decision. Prefer:

- **Interval plots** — point estimate with the CI, decision threshold drawn as a
  vertical line. One glance answers the whole question.
- **Overlapping distributions** rather than two bars of means, when the spread
  is part of the story.
- **Cumulative results over time with widening-to-narrowing intervals**, which
  makes the peeking problem visible rather than tempting.

Avoid bar charts of two means with no error bars, dual y-axes, and truncated
axes that turn a 1% difference into a visual doubling.

---

## 5. Practical significance vs statistical significance

Build the threshold before the analysis:

1. **What does the effect cost to ship and maintain?** Engineering time,
   support load, complexity.
2. **What is the effect worth per unit?** Revenue per conversion, cost per
   ticket avoided.
3. **The break-even effect is the decision threshold.** Anything below it is
   not worth shipping regardless of its p-value.

Then the analysis produces a decision rather than a debate:

| Interval vs threshold | Decision |
|-----------------------|----------|
| Entirely above | Ship |
| Entirely below (including negative) | Do not ship |
| Straddles the threshold | Collect more data, or decide on strategic grounds and say that is what you did |

**[PROVEN] Setting the threshold before seeing the data is the highest-leverage
practice in applied statistics.** It converts a post-hoc argument about whether
a 0.4-point lift is "meaningful" into a pre-agreed rule, and it removes the
incentive to keep slicing the data until something clears 0.05.

---

## 6. Reporting checklist

Before any statistical result leaves your hands:

- [ ] The effect is stated in domain units, first
- [ ] An interval accompanies every point estimate
- [ ] The decision threshold is stated and was set before the analysis
- [ ] The test used and its key assumption are named, with the assumption check
- [ ] Sample size per group is stated
- [ ] The number of comparisons in the family is disclosed, with the correction
- [ ] If the result is null, the upper bound of what could have been missed is stated
- [ ] Any deviation from the original plan (metric changes, segment additions,
      stopping early) is disclosed in the body, not a footnote
- [ ] Nothing says "trending toward significance"
