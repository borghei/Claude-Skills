# Calibration and Forecasting

Reflection that does not test predictions against outcomes is storytelling. This
reference covers how to write predictions that can be scored, how scoring works,
and what to change when the score comes back badly.

---

## 1. Why calibration is the core of useful reflection

Memory reconstructs rather than replays. After an outcome is known, the mind
edits the prior belief to match it — you remember having been less surprised
than you were, and having assigned more probability to what happened than you
actually did. This is not a character flaw; it is how recall works, and it makes
unaided reflection systematically self-flattering.

A written prediction with a number attached is the only reliable defence,
because it is a record made *before* the outcome, immune to later editing.

**The practical payoff is not being right more often.** It is knowing how much
to trust your own confidence — which determines how much contingency to build,
how hard to push a decision, and when to seek an outside view. A person who is
right 60% of the time and knows it makes better decisions than one who is right
75% of the time and believes it is 95%.

---

## 2. Writing a scoreable prediction

A prediction is scoreable when a disinterested third party could look at the
world on a stated date and declare it true or false without argument.

**Required elements:** a claim, a resolution date, and a confidence number.

| Not scoreable | Why | Scoreable |
|---|---|---|
| "The migration will go well" | "Well" is undefined | "The migration completes with no rollback and under 30 min downtime, by June 30" — 70% |
| "We'll probably hire someone soon" | No date, no threshold | "We sign a staff engineer offer by August 31" — 55% |
| "Churn should improve" | No magnitude, no date | "Monthly churn is below 3.0% in July" — 60% |
| "This feature will be popular" | No measurable outcome | "At least 15% of active accounts use the feature within 30 days of launch" — 45% |

### Confidence conventions

- Use 50-95% for binary claims. Below 50% means you are predicting the negation
  — restate it that way so the log stays comparable.
- **Avoid 100% and 0%.** They are unfalsifiable in a scoring sense: a single
  miss at 100% produces an unbounded penalty under most rules, and in practice
  nothing you predict about the future deserves them.
- Prefer round increments of 5%. Finer granularity implies a precision you do
  not have and slows logging enough to kill the habit.
- **50% is a legitimate and useful answer.** A log with no 50% predictions
  usually means you are only recording claims you already feel safe about.

### Volume

Aim for **15-30 predictions per quarter**. Below 20 resolved, calibration
estimates are too noisy to act on — a single unlucky quarter looks identical to
genuine overconfidence. Above 40 the logging becomes a chore and the habit dies.

---

## 3. How scoring works

### The Brier score

The mean squared error between stated confidence and outcome, where outcome is 1
or 0:

```
Brier = mean((confidence - outcome)^2)
```

Lower is better. It rewards being right *and* being appropriately uncertain: a
confident correct call scores near 0, a confident wrong call scores near 1, and
hedging to 50% always scores 0.25.

| Brier | Reading |
|---|---|
| < 0.10 | Excellent — either genuine skill or predictions that were too easy |
| 0.10-0.15 | Strong |
| 0.15-0.20 | Good; typical for a practised forecaster on genuinely uncertain questions |
| 0.20-0.25 | Weak — approaching the value of a coin flip |
| > 0.25 | Worse than always saying 50%. Confidence is actively misleading you |

**A low Brier alone is not proof of skill.** Predicting "the sun rises tomorrow"
at 99% produces a superb score and teaches nothing. This is why the skill score
matters.

### Skill score

Compares your Brier against always predicting the base rate:

```
skill = (baseline - brier) / baseline,  where baseline = base_rate * (1 - base_rate)
```

A skill score at or below 0 means your forecasts carry no more information than
knowing how often things generally go your way. Below 0.15 usually means the
predictions are too safe to be useful.

### Murphy decomposition

The Brier score splits into three parts, and they call for different fixes:

```
Brier = reliability - resolution + uncertainty
```

| Component | Meaning | Direction | Fix when bad |
|---|---|---|---|
| **Reliability** | Miscalibration — the gap between stated confidence and observed frequency | Lower better | Adjust your numbers: shade toward 50% if overconfident |
| **Resolution** | Discrimination — how far your forecasts move away from the base rate | Higher better | Take real positions on genuinely uncertain questions |
| **Uncertainty** | Inherent difficulty of the questions you asked | Not controllable | Nothing — it is a property of the question set |

The common pattern is **decent reliability with near-zero resolution**: you have
learned to hedge everything to the base rate, which is safe and useless. The
opposite — high resolution, poor reliability — is more valuable, because
directional judgement is hard to acquire and numeric calibration is easy to
correct.

### Verifying the decomposition

The identity `BS = REL - RES + UNC` holds **exactly** only when the components
are computed by grouping on distinct forecast values. Grouping into coarse
display buckets discards the within-bin variance and the identity stops closing
— a discrepancy of 0.003-0.005 on a typical log, which is small enough to look
like a rounding artefact and is not.

`calibration_scorer.py` therefore computes the decomposition over distinct
confidence values, independently of `--buckets`, which controls only the
displayed table. The identity is asserted on every run of `--selftest`:

```bash
python3 scripts/calibration_scorer.py --selftest
```

**Caveat for near-continuous confidences.** Distinct-value grouping assumes you
state confidence on a coarse grid — the 5% increments recommended in §2. If
every prediction carries a unique value (54.3%, 71.8%, …), each group holds one
prediction, `observed` is 0 or 1, and reliability collapses toward a value with
no useful meaning while resolution absorbs everything. That is the
mathematically honest result for a log with no repeated forecasts, and it is
another reason to round to 5%: it is what makes the reliability component
interpretable at all.

---

## 4. Reading the calibration table

Group predictions by stated confidence and compare to what actually happened.

| Stated | n | Said | Actual | Gap | Reading |
|---|---|---|---|---|---|
| 50-60% | 8 | 55% | 50% | +5% | Calibrated |
| 60-80% | 14 | 67% | 71% | -4% | Calibrated |
| 80-100% | 9 | 87% | 44% | +43% | Severe overconfidence at the top end |

The pattern above is the most common one in real logs: **calibration holds in
the middle range and collapses at high confidence.** People are reasonable about
things they know are uncertain, and badly wrong about things that feel certain —
because "feels certain" is exactly where you stop looking for disconfirming
evidence.

**Thresholds:** a gap above 10 percentage points in a bucket holding at least 5
predictions is a real bias, not noise. Below 5 predictions, ignore the bucket.

---

## 5. The domains where people are most overconfident

Breaking calibration down by domain is usually more actionable than the overall
number, because bias is rarely uniform.

| Domain | Typical bias | Why |
|---|---|---|
| **Own delivery dates** | Strongly overconfident | The plan is imagined without the interruptions, dependencies, and rework that always arrive. This is the single most reliable bias in professional forecasting |
| Own team's output | Overconfident | Same mechanism, one step removed |
| Other teams' delivery | Better calibrated, sometimes pessimistic | No inside view to be optimistic with |
| Sales / deal closing | Overconfident | Optimism is functionally required in the role; it leaks into forecasts |
| Metrics and trends | Reasonably calibrated | Anchored to observable history |
| Hiring outcomes | Mixed, often underconfident | Salient memories of rejections dominate |
| Competitor behaviour | Overconfident on timing, decent on direction | Direction is inferable; timing is not |

**[PROVEN] If you log only one category, log your own delivery dates.** It has
the largest bias, the fastest resolution cycle, and the most immediate practical
payoff in planning.

---

## 6. Correcting a bad score

Apply one correction at a time and re-measure over a full quarter. Changing
several things at once means you learn nothing about which worked.

### If overconfident (gap > +10%)

1. **Shade toward 50% by the measured gap.** If you are 15 points overconfident,
   subtract 15 from every stated confidence for a quarter. Crude, and it works
   better than trying to reason your way to better numbers.
2. **Apply the outside view before the inside view.** Ask "how long have
   comparable things taken?" before "how long should this take?" The reference
   class beats the plan almost every time.
3. **Run a pre-mortem on anything above 80%.** Assume it failed; write the three
   most likely reasons. If you can generate three plausible failure modes in two
   minutes, 90% was the wrong number.

### If underconfident (gap < -10%)

Rarer, and it has a real cost — you hedge decisions you should be making
decisively, and others read the hedging as lack of judgement. State the
confidence you actually hold rather than the one that feels socially safe.

### If skill score is near zero

Your predictions are too safe. You are forecasting things whose outcome is
already known, or hedging everything to the base rate. Fix by predicting things
you might be *wrong* about — the point of the log is to find your errors, and a
log with no errors in it has failed at its only job.

---

## 7. Cadence

| Activity | Cadence | Time |
|---|---|---|
| Write predictions | As decisions arise; sweep at quarter start | 10 min |
| Resolve due predictions | Weekly, during the operating review | 5 min |
| Score the log | Quarterly | 30 min |
| Act on the score | Quarterly, one correction only | Part of quarterly reflection |

**Do not score monthly.** With 15-30 predictions per quarter, a month yields too
few resolved items to distinguish signal from luck, and reacting to that noise
produces exactly the thrashing the practice is meant to eliminate.

---

## 8. Common failures

| Failure | Symptom | Fix |
|---|---|---|
| Vague predictions | Arguments at resolution time about whether it came true | Add a threshold and a date; a third party must be able to score it |
| Only easy predictions | Excellent Brier, skill score near zero | Predict things you might be wrong about |
| Retrospective editing | "I always thought that would happen" | The log is append-only; never revise a prediction after the fact |
| Never resolving | Large pending pile, nothing scored | Resolve weekly; an unresolved prediction teaches nothing |
| Scoring too often | Reacting to noise, constant strategy changes | Quarterly only |
| Treating the score as a grade | Shame, then abandonment | It is an instrument reading. A bad score is information you did not have, which is the entire point |

---

## 9. A worked scoring example

Twenty-seven resolved predictions over a quarter. The output below is the shape
of a real first-quarter log, and the story it tells is the common one.

```
Brier 0.294 | skill vs base rate -0.19
Mean confidence 72% vs actual hit rate 56% — gap +16%
reliability 0.074 | resolution 0.031

stated       n   said  actual    gap  verdict
40%-60%      4    55%     25%   +30%  too-few
60%-80%     14    67%     71%    -4%  calibrated
80%-100%     9    87%     44%   +42%  overconfident

By domain:
  delivery    n=9  brier=0.450  gap=+32%
  sales       n=4  brier=0.377  gap=+51%
  strategy    n=5  brier=0.229  gap=+9%
  metrics     n=6  brier=0.173  gap=-3%
  hiring      n=3  brier=0.069  gap=-25%
```

### Reading it

1. **Brier 0.294 is worse than always saying 50%.** Stated confidence is
   actively misleading — worse than useless, because decisions were made on it.
2. **The mid-range bucket is well calibrated (-4%).** Judgement is not broken.
   This is important: the instinct on seeing a bad Brier is "I have poor
   judgement," and the table says otherwise.
3. **The top bucket is catastrophic (+42%).** Predictions stated at 87% came
   true 44% of the time. This is the whole problem, and it is confined to one
   bucket.
4. **The 40-60% bucket holds 4 predictions — ignore it.** Below 5, a single
   outcome moves the rate by 25 points. The tool labels it `too-few` for this
   reason.
5. **Delivery and sales carry the damage.** Both are domains where the forecaster
   has an inside view and a stake in the answer.
6. **Hiring is underconfident (-25%) on 3 predictions** — too few to act on, but
   worth watching next quarter.

### What to change

Exactly one thing: **stop using confidence above 80% for your own delivery
dates.** Not "be more careful" — a specific, testable rule. Cap delivery-date
confidence at 75% for a quarter and re-measure.

Note what is *not* the conclusion. "Improve my judgement" is unactionable. "Be
less optimistic" is an intention. The bucketed table converts a vague sense of
being wrong into a bounded rule affecting roughly nine predictions a quarter.

### The following quarter

Expect the Brier to improve to roughly 0.20-0.22 from the capping rule alone,
with no improvement in underlying judgement whatsoever. This is worth
understanding clearly: **most of the available gain is in reporting your
uncertainty honestly, not in being right more often.** Calibration is a
cheap fix; discrimination is the hard one.

---

## 10. Reference classes and the outside view

The most reliable single technique for correcting overconfidence, and the reason
delivery-date predictions are so consistently wrong.

### Inside view vs outside view

The **inside view** builds an estimate from the specifics: the steps involved,
who is doing them, how long each should take. It is detailed, feels rigorous,
and is systematically optimistic — because it models the plan succeeding and
cannot enumerate the interruptions, dependencies, and rework that have not
happened yet.

The **outside view** ignores the specifics and asks: how long have comparable
things actually taken? It feels lazy and crude, and it is more accurate.

### Applying it

1. **Define the reference class.** "Migrations of this size in this codebase,"
   "candidates at this stage of our pipeline," "features scoped at two weeks."
   Broad enough for several examples; narrow enough to be comparable.
2. **Find the base rate.** How often did they succeed? How long did they take?
   Your own history is usually available and rarely consulted.
3. **Start from the base rate**, then adjust for genuine differences — sparingly.
   The universal error is adjusting too far toward optimism, because the reasons
   *this* case is different are always vividly available.

| Estimate | Inside view | Outside view | Which was right |
|---|---|---|---|
| Migration completion | "Three weeks — the steps are clear" | "The last four migrations took 5-9 weeks" | Outside, nearly always |
| Hiring timeline | "Six weeks — pipeline looks strong" | "Our last three hires took 11-16 weeks" | Outside |
| Feature delivery | "Two sprints" | "Similar features have taken 3-5 sprints" | Outside |

**[PROVEN] Ask the outside-view question before writing any confidence number
about your own delivery.** Costs 30 seconds and is the single most effective
correction available.

### Why it works

Reference-class data already contains the failure modes you cannot enumerate in
advance — the sick week, the dependency that was not ready, the requirement that
changed. You do not need to predict *which* disruption will occur, only that
disruptions occur at their historical rate. The inside view attempts the former,
which is impossible; the outside view uses the latter, which is measurable.

---

## 11. Scoring rules other than Brier

Brier is the default because it is simple, bounded, and easy to compute. Two
alternatives are worth knowing.

| Rule | Formula | Property | When to prefer it |
|---|---|---|---|
| **Brier** | `(p - o)^2` | Bounded 0-1; gentle on confident errors | Default — good for personal logs |
| **Log score** | `-ln(p)` if true, `-ln(1-p)` if false | Unbounded; brutal on confident errors | When confident errors are genuinely catastrophic |
| **Absolute** | `abs(p - o)` | Linear; not strictly proper | Never — it rewards hedging to 0 or 1 |

**Avoid the absolute-error rule.** It is not a *strictly proper* scoring rule,
meaning it can be gamed: under it, your best strategy is to state 0% or 100%
regardless of what you actually believe — the exact opposite of the honesty the
practice is meant to build. Brier and log score are both strictly proper: each
is optimised by reporting your true belief, which is the property that makes
them useful.

**The log score's practical drawback** is that a single 99%-confident miss
produces a penalty large enough to dominate the entire quarter, which is
statistically defensible and demoralising. For a personal practice, Brier's
gentleness is a feature — the goal is a habit that survives, and a scoring rule
that makes one bad call ruin a quarter does not help.

---

## 12. Group and team forecasting

Calibration extends usefully to teams, with three caveats.

### The mechanics

- **Everyone predicts independently before discussing.** Discussion before
  prediction destroys the signal entirely — the first confident voice anchors
  everyone else, and you end up measuring that person's confidence repeatedly.
- **Aggregate by median, not mean.** The median resists the single wildly
  confident outlier that otherwise drags the group estimate.
- **Score individually and in aggregate.** The aggregate is usually better
  calibrated than most individuals, which is itself worth demonstrating.

### The caveats

1. **Never tie scores to performance review.** The instant calibration affects
   compensation, everyone hedges to 50% and the practice dies. It must stay a
   learning instrument, and that requires it to be visibly safe.
2. **Beware the seniority anchor.** If the most senior person predicts first,
   you are measuring their view with extra steps. Independent submission is
   structurally necessary, not merely polite.
3. **Expect resistance from the accurate.** People with good judgement often
   dislike being scored, because the downside (being shown wrong) is vivid and
   the upside (being shown right) is what they already assumed.

### What teams gain

The largest benefit is not better forecasts — it is **discovering that the team
disagrees**. A group that has always assumed shared assumptions will find that
stated confidence on the same question ranges from 30% to 90%, which surfaces a
substantive disagreement that discussion alone had smoothed over. That discovery
is usually worth more than the calibration score itself.
