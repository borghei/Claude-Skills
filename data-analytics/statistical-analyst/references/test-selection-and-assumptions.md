# Test Selection, Assumptions, and Power

The decision procedure for choosing a statistical test, what each test actually
assumes, what happens when the assumption fails, and how to size a study before
running it.

---

## 1. The selection tree

Answer four questions in order. They determine the test almost uniquely.

1. **What kind of question is it?** Difference between groups / association
   between variables / change over time.
2. **What kind of outcome is it?** Binary, continuous, count, ordinal, categorical.
3. **How many groups, and are they paired?**
4. **What does the distribution look like?** Roughly symmetric, skewed,
   outlier-heavy — and how many observations per group.

| Question | Outcome | Groups | Test | Effect size |
|----------|---------|--------|------|-------------|
| Difference | Binary | 2, independent | Two-proportion z | Cohen's h, absolute + relative lift |
| Difference | Binary | 2, paired | McNemar (exact if few discordant pairs) | Odds ratio on discordant pairs |
| Difference | Binary/categorical | 3+ | Chi-square of independence | Cramér's V |
| Difference | Continuous, symmetric | 2, independent | **Welch's t** | Hedges' g |
| Difference | Continuous, skewed / n<15 | 2, independent | Mann-Whitney U | Rank-biserial r |
| Difference | Continuous | 2, paired | Paired t (Wilcoxon signed-rank if skewed) | Cohen's d on differences |
| Difference | Continuous | 3+ | One-way ANOVA (Kruskal-Wallis if shapes differ) | Eta-squared |
| Difference | Ordinal | 2 / 3+ | Mann-Whitney / Kruskal-Wallis | Rank-biserial / epsilon-squared |
| Difference | Count per exposure | 2 | Poisson rate ratio (negative binomial if overdispersed) | Rate ratio |
| Association | Two continuous | — | Pearson (Spearman if skewed/ordinal) | r, r² |
| Change over time | Any | — | Interrupted time series / segmented regression | Level and slope change |

**[PROVEN] Use Welch's t, not Student's t, as your default two-group test.**
Welch does not assume equal variances, and when variances *are* equal it loses
almost nothing (a fraction of a degree of freedom). The common practice of
running a variance test first and then choosing between the two is worse than
just always using Welch — the pre-test inflates the Type I error rate of the
procedure as a whole.

---

## 2. What each test actually assumes

Most stated "assumptions" are not equally load-bearing. What matters is how the
result degrades when each one fails.

### Two-proportion z

| Assumption | Load-bearing? | Failure mode |
|------------|---------------|--------------|
| ≥5 events and ≥5 non-events per group | Yes | Normal approximation breaks; p-values wrong in both directions. Use Fisher's exact. |
| Independent observations | **Critically** | One user counted twice, or users clustered in accounts, deflates the standard error and manufactures significance. |
| Randomized assignment | For causal claims | Without it you have an association, not an effect. |

### Welch's t

| Assumption | Load-bearing? | Failure mode |
|------------|---------------|--------------|
| Normality of the *sampling distribution of the mean* | Only at small n | At n ≥ 30 per group the CLT covers most real skew. At n < 15 with heavy skew, use ranks. |
| Equal variances | **No** — that is the point of Welch | — |
| Independence | **Critically** | Same as above. |
| No influential outliers | Yes | A single extreme value can move the mean and inflate the variance enough to hide a real effect. Inspect, do not silently drop. |

Note what the normality assumption is *about*: the sampling distribution of the
mean, not the raw data. "My data are not normally distributed" is not by itself
a reason to abandon a t test at n = 200 per group.

### Chi-square of independence

| Assumption | Load-bearing? | Failure mode |
|------------|---------------|--------------|
| Expected cell count ≥ 5 | Yes | Approximation degrades. Collapse sparse categories or use Fisher's exact. |
| One observation per unit | **Critically** | Counting events rather than users, when users generate many events, is the single most common way this test is misused. |
| Categories mutually exclusive | Yes | Multi-select survey questions are not a contingency table. |

### Mann-Whitney U

| Assumption | Load-bearing? | Failure mode |
|------------|---------------|--------------|
| Independence | **Critically** | Same as above. |
| Similar distribution shapes | For the *interpretation* | Without it, a significant result means "one distribution is stochastically larger," which is not the same as "the medians differ." Say what you mean. |
| ~8+ per group for the normal approximation | Yes | Below that, use the exact distribution or report descriptives only. |

---

## 3. Power and sample size

Sizing is not optional paperwork. A study that cannot detect the effect you
care about produces a null result that means nothing, and everyone reads it as
"no difference."

### The four quantities

Alpha, power, effect size, and n. Fix any three and the fourth follows.
Conventional defaults are α = 0.05 and power = 0.80, meaning you accept a 20%
chance of missing a real effect of the size you specified.

**[RECOMMENDED] Use power = 0.90 for decisions that are expensive to reverse.**
The extra sample is usually cheaper than shipping the wrong thing, and 80%
power means one in five real effects goes undetected.

### Formulas

For two proportions, per group:

```
n = (z_{α/2} + z_β)² × [p₁(1−p₁) + p₂(1−p₂)] / (p₂ − p₁)²
```

For two means, per group:

```
n = 2(z_{α/2} + z_β)² / d²      where d = MDE / SD
```

`test_selector.py` computes both. The number is usually much larger than
people expect — the calibration table below is why so many product experiments
are underpowered:

| Baseline rate | Relative MDE | n per group (α=0.05, power=0.80) |
|---------------|--------------|----------------------------------|
| 2% | +10% | ~78,000 |
| 2% | +25% | ~13,000 |
| 8% | +5% | ~113,000 |
| 8% | +10% | ~28,500 |
| 8% | +25% | ~4,900 |
| 20% | +10% | ~9,000 |
| 20% | +25% | ~1,600 |

### The MDE conversation is the important one

Sizing forces the question "how small an effect would still be worth shipping?"
That is a business question, not a statistical one, and it is the most valuable
part of the exercise. If the honest answer is "we'd ship for a 1% relative
lift" and you have 4,000 users per arm, the correct conclusion is that the
experiment cannot answer the question — decide by judgement and say so, rather
than running an underpowered test and dressing the judgement in a p-value.

### The winner's curse

In an underpowered study, the effects that *do* reach significance are
systematically overestimated — they had to be large to clear the bar. This is
why a 40% lift in a small test becomes 6% at full rollout. Expect regression
toward the truth, and never plan a roadmap on the point estimate from an
underpowered experiment.

---

## 4. Multiple comparisons

Every additional comparison in a family raises the chance of at least one false
positive: with α = 0.05, testing 3 variants gives 14%, 10 metrics gives 40%,
20 segments gives 64%.

| Correction | Controls | Use when | Cost |
|------------|----------|----------|------|
| **Bonferroni** (α/m) | Family-wise error rate | Few comparisons; a false positive is expensive | Conservative; loses power fast as m grows |
| **Holm-Bonferroni** | Family-wise error rate | Same, always preferable to plain Bonferroni | Uniformly more powerful, same guarantee |
| **Benjamini-Hochberg** | False discovery rate | Many exploratory comparisons, e.g. metric scans | Allows a controlled proportion of false positives |
| **None, pre-registered primary metric** | — | The best answer | Requires deciding before you look |

**[PROVEN] The strongest defence is one pre-registered primary metric.**
Corrections manage the damage from testing many things; naming the primary
metric before the data arrive avoids it. Secondary metrics are then explicitly
labelled exploratory, corrected with Benjamini-Hochberg, and treated as
hypothesis-generating rather than decisive.

---

## 5. Assumption-checking without a stats package

You do not need a normality test — and you should not use one, since at large n
they reject on trivial deviations and at small n they have no power. Do this
instead:

| Check | Method | Threshold for concern |
|-------|--------|-----------------------|
| Skew | Compare mean and median | Mean more than ~10% from median |
| Outliers | Sort and inspect the top and bottom 5 values | A single value more than 3 SD out, or contributing >5% of a total |
| Variance ratio | Larger sample variance / smaller | >4x — Welch handles it, but ask why |
| Independence | Count units vs count rows | Rows > units means clustering; use a cluster-robust method |
| Bimodality | Histogram with ~20 bins | Two clear modes means you are averaging two populations — split them |

The independence check catches more real errors than every distributional check
combined, and almost nobody performs it.

---

## 6. Sequential testing and peeking

Fixed-horizon tests assume you look once, at the end. Checking the p-value
daily and stopping when it dips below 0.05 raises the actual false-positive
rate to roughly 20-30% depending on how often you look — the p-value will
eventually wander below the threshold by chance even when nothing is happening.

Three legitimate options:

1. **Fixed horizon.** Compute n up front, do not look, decide at the end.
   Simplest and correct. [PROVEN]
2. **Group sequential (O'Brien-Fleming spending).** Pre-specify a small number
   of interim looks with adjusted thresholds — early looks require far more
   extreme evidence. [PROVEN]
3. **Always-valid inference (mixture sequential probability ratio tests,
   confidence sequences).** Look continuously with intervals valid at every
   moment; the cost is wider intervals. [RECOMMENDED] — well-founded, but the
   implementation is easy to get wrong, so use a vetted library rather than
   hand-rolling.

What is never acceptable: monitoring an uncorrected fixed-horizon test daily
and stopping on significance. If it has already happened, the honest move is to
report the result as exploratory and re-run with a fixed horizon.
