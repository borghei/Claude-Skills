# Statistical Planning for Study Operations

The formulas behind the sample size calculator, worked examples you can check
the tool against, and — most importantly — the list of situations where these
formulas do not apply and a statistician is required.

> **This is an operations reference, not a statistics text.** Everything here
> assumes a simple parallel-group design analysed with a standard test. Study
> designs regularly violate those assumptions. Sample size is a protocol element
> that requires biostatistician sign-off; use this to plan, budget, and ask
> better questions, not to finalise.

## 1. When these formulas do NOT apply

Escalate to a statistician immediately if any of the following is true. This is
the most important section in this file.

| Situation | Why the simple formula fails |
|-----------|------------------------------|
| **Interim analyses** | Repeated testing inflates type I error. Requires an alpha spending function and group-sequential boundaries. |
| **Co-primary or multiple primary endpoints** | Power multiplies down (co-primary) or alpha inflates (multiple primary). Requires a multiplicity strategy. |
| **Cluster randomisation** | Participants within a cluster are correlated. Requires a design effect inflation. |
| **Crossover design** | Within-participant comparison uses a different variance and requires carryover assumptions. |
| **Non-inferiority or equivalence** | The hypothesis structure differs; the margin must be clinically justified and the analysis population choice reverses. |
| **Adaptive design** | Sample size re-estimation, arm dropping, and response-adaptive randomisation all require simulation, not a formula. |
| **Stratified or covariate-adjusted analysis** | Adjustment usually reduces required n, but the gain depends on the covariate's correlation with the outcome. |
| **Repeated measures / longitudinal endpoints** | The correlation structure across timepoints drives the sample size. |
| **Competing risks** | Standard log-rank assumptions do not hold. |
| **Non-proportional hazards** | Log-rank loses power; a different test and a different sample size are needed. |
| **Very small expected cell counts** | Normal approximation fails; exact methods required. |
| **Multi-arm trials** | Both multiplicity and allocation strategy change the calculation. |

## 2. Two independent proportions

For a binary endpoint compared between two arms, with allocation ratio
k = n_treatment / n_control:

```
p_bar = (p1 + k*p2) / (1 + k)

n_control = [ z_(1-α/s) * sqrt((1 + 1/k) * p_bar * (1 - p_bar))
              + z_(1-β) * sqrt(p1*(1-p1) + p2*(1-p2)/k) ]^2 / (p1 - p2)^2

n_treatment = k * n_control
```

Where `s` is 1 or 2 for a one- or two-sided test.

### Worked example

p_control = 0.40, p_treatment = 0.55, α = 0.05 two-sided, power = 80%, k = 1.

- z_(0.975) = 1.960, z_(0.80) = 0.842
- p_bar = 0.475
- null term = 1.960 × √(2 × 0.475 × 0.525) = 1.960 × 0.7062 = 1.3841
- alt term = 0.842 × √(0.24 + 0.2475) = 0.842 × 0.6982 = 0.5876
- n = (1.9718)² / (0.15)² = 3.8878 / 0.0225 = **173 per group**

At 15% dropout, enrol ⌈346 / 0.85⌉ = **408 total**.

### Sensitivity to the baseline rate

Required n per group at 80% power, α = 0.05 two-sided, for an absolute
difference of 0.15:

| Control rate | Treatment rate | n per group |
|--------------|----------------|-------------|
| 0.10 | 0.25 | 100 |
| 0.20 | 0.35 | 138 |
| 0.30 | 0.45 | 163 |
| 0.40 | 0.55 | 173 |
| 0.50 | 0.65 | 170 |

The variance of a proportion is maximised at p = 0.5, so the same absolute
difference is most expensive to detect near the middle of the range. If your
control rate estimate is uncertain and near 0.5, size for the worst case.

## 3. Two independent means

For a continuous endpoint:

```
n_control = (1 + 1/k) * (z_(1-α/s) + z_(1-β))^2 * σ^2 / δ^2
```

### Worked example

δ = 4.0, σ = 12.0, α = 0.05 two-sided, power = 80%, k = 1.

- (z + z)² = (1.960 + 0.842)² = 7.849
- n = 2 × 7.849 × 144 / 16 = **142 per group**

### Standardised effect size shortcut

With equal allocation, α = 0.05 two-sided, the required n per group is
approximately `15.7 / d²` at 80% power and `21.0 / d²` at 90%, where d = δ/σ.

| d (δ/σ) | n per group, 80% | n per group, 90% |
|---------|------------------|------------------|
| 0.20 | 393 | 526 |
| 0.30 | 175 | 234 |
| 0.35 | 129 | 172 |
| 0.40 | 99 | 132 |
| 0.50 | 63 | 85 |
| 0.80 | 25 | 33 |

**Going from 80% to 90% power costs about 34% more participants.** That is
usually a better use of budget than it looks, because an under-powered negative
result is worth close to nothing.

### If σ comes from a pilot

A pilot-derived standard deviation is imprecise, and under-estimating σ
under-powers the study. Add roughly 10-15% to n, or use an upper confidence
bound on σ rather than the point estimate.

## 4. Time-to-event (log-rank)

Time-to-event designs are driven by the **number of events**, not the number of
participants. Enrolment is only the means of generating events.

### Required events (Schoenfeld)

```
d = (z_(1-α/s) + z_(1-β))^2 / (P_c * P_t * (ln HR)^2)
```

Where P_c and P_t are the allocation proportions. With 1:1 allocation this
simplifies to `4 * (z + z)² / (ln HR)²`.

### Required events (Freedman)

```
d = ((1 + HR) / (1 - HR))^2 * (z_(1-α/s) + z_(1-β))^2
```

Freedman is generally the more conservative of the two. The calculator reports
both; a large gap between them signals an extreme hazard ratio where the choice
of formula matters and a statistician should decide.

### Required events at 80% power, α = 0.05 two-sided, 1:1

| Hazard ratio | Events (Schoenfeld) |
|--------------|--------------------|
| 0.50 | 66 |
| 0.60 | 121 |
| 0.67 | 196 |
| 0.70 | 247 |
| 0.75 | 380 |
| 0.80 | 631 |

The cost of detecting a modest hazard ratio rises very steeply. Moving the
target from HR 0.70 to HR 0.80 more than doubles the required events.

### Converting events to enrolment

```
n_total = d / P(event)
```

Under exponential survival with uniform accrual over A months plus F months of
additional follow-up:

```
λ = ln(2) / median_survival
P(event) = 1 - (e^(-λF) - e^(-λ(F+A))) / (λ * A)
```

Compute this per arm and weight by allocation.

### Worked example

HR = 0.70, control median 18 months, accrual 24 months, follow-up 12 months,
α = 0.05 two-sided, 80% power, 1:1.

- Events required = 4 × (2.802)² / (ln 0.70)² = 31.40 / 0.1272 = **247 events**
- λ_control = 0.6931 / 18 = 0.03851 → P(event | control) = 0.589
- Implied treatment median = 18 / 0.70 = 25.7 → λ = 0.02696 → P(event) = 0.467
- Overall P(event) = 0.528
- n_total = 247 / 0.528 = **468 participants**
- At 15% dropout: enrol **551**

### The lever that is usually overlooked

Because the design is event-driven, **extending follow-up is often cheaper than
enrolling more participants.** In the example above, extending follow-up from 12
to 24 months raises the event probability enough to cut the required enrolment
substantially, at the cost of a longer study. Model both before defaulting to
"enrol more."

## 5. Dropout inflation

```
n_enrol = n_analysed / (1 - dropout_rate)
```

| Dropout | Inflation |
|---------|-----------|
| 5% | 1.05x |
| 10% | 1.11x |
| 15% | 1.18x |
| 20% | 1.25x |
| 30% | 1.43x |

Source the rate from comparable completed studies in the same population, not
from optimism. Longer studies, more burdensome visit schedules, and
placebo-controlled designs all raise it.

Note the distinction: this inflates for participants who provide **no analysable
endpoint data**. A participant who discontinues treatment but is still followed
to the endpoint is not a dropout for this purpose under an ITT analysis — which
is exactly why the protocol should mandate continued follow-up after treatment
discontinuation.

## 6. Design effect for clustering

If randomisation is at a cluster level (site, ward, practice) but the endpoint is
measured on individuals:

```
DEFF = 1 + (m - 1) * ICC
n_clustered = n_individual * DEFF
```

Where m is the average cluster size and ICC the intracluster correlation.

| Cluster size | ICC 0.01 | ICC 0.05 | ICC 0.10 |
|--------------|----------|----------|----------|
| 10 | 1.09x | 1.45x | 1.90x |
| 25 | 1.24x | 2.20x | 3.40x |
| 50 | 1.49x | 3.45x | 5.90x |

Clustering is expensive and routinely forgotten in early planning. Even a small
ICC with large clusters can double or triple the required sample. If your design
randomises anything other than individual participants, this applies to you.

## 7. Interim analyses

Repeated significance testing on accumulating data inflates type I error:

| Unadjusted looks | Actual type I error (nominal 0.05) |
|------------------|-----------------------------------|
| 1 (final only) | 0.05 |
| 2 | ~0.08 |
| 3 | ~0.11 |
| 5 | ~0.14 |

Alpha spending functions distribute the total alpha across looks. Two families
in common use:

- **O'Brien-Fleming** — very conservative early, near-nominal at the final
  analysis. Costs little in final-analysis power, so stopping early requires an
  extreme result. **[RECOMMENDED]** default for efficacy monitoring.
- **Pocock** — constant boundary across looks. Easier to stop early, at a
  meaningful cost to final-analysis power.

Futility monitoring is separate from efficacy monitoring and does not inflate
type I error, but it does reduce power. Both must be pre-specified.

## 8. Planning checklist

- [ ] Endpoint type identified: binary, continuous, time-to-event, or other
- [ ] Effect size stated with its source, and discounted if from a different population
- [ ] σ inflated if derived from a small pilot
- [ ] Alpha and sidedness stated; two-sided unless justified
- [ ] Power at least 80%; 90% considered given the cost ratio
- [ ] Allocation ratio stated
- [ ] Dropout rate sourced from comparable studies, not assumed
- [ ] For time-to-event: event probability derived from median survival, accrual, and follow-up
- [ ] For time-to-event: extending follow-up evaluated against enrolling more
- [ ] Clustering checked — design effect applied if randomisation is not individual
- [ ] Every interim analysis has a spending function and boundaries
- [ ] Multiplicity strategy defined if more than one primary comparison
- [ ] Accrual feasibility tested against the site network before the n is fixed
- [ ] Biostatistician has reviewed and signed off
