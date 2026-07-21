---
name: reflect
description: >
  Turn reflection into decisions by scoring predictions against outcomes and
  tracking whether commitments held. Use when running a quarterly review, scoring
  forecast calibration, or reflection keeps producing notes instead of change.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: personal-productivity
  domain: personal-effectiveness
  updated: 2026-07-21
  tags: [reflection, calibration, brier-score, forecasting, commitments]
---

# Reflect

Structured reflection at daily, weekly, and quarterly cadence that ends in a
changed behaviour rather than a paragraph of feelings. The mechanism is testing
recorded beliefs against outcomes: written predictions scored for calibration,
and commitments tracked for whether they actually held.

**Boundary with `weekly-review`:** that skill runs the weekly operating cadence —
what happened, what is next, priorities and blockers. This one is the learning
layer on top: was my judgement any good across weeks and quarters, and what
should change as a result. Run them back to back, operating review first, using
its output as this skill's raw material. Do not duplicate the wins/blockers
synthesis here.

## When to use this skill

- Your reviews produce pleasant notes but nothing ever changes as a result
- You want to know whether to trust your own confidence when making a call
- Delivery dates keep slipping and you suspect the estimates, not the execution
- The same commitment has been carried for months without progress or a decision
- It is quarter end and you need to score judgement, not just report outcomes
- You are starting a prediction log and want a scoring method rather than a journal

## Inputs the skill expects

- A prediction log — `statement`, `confidence`, and `outcome` once resolved
- A commitment log — `text`, `status` (kept/missed/partial/open), optional `due` and `carried_cycles`
- The cadence you are running: daily, weekly, or quarterly
- A reference date for overdue calculations (passed explicitly — the tools never read the clock)
- Optionally a `domain` per prediction, which is where the most actionable signal appears

## Clarify First

Before generating, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Which cadence is being run** — daily, weekly, and quarterly ask genuinely different questions; the wrong set produces either triviality or an hour-long session that gets skipped
- [ ] **Whether resolved predictions exist** — below 20 resolved, calibration is too noisy to act on and the honest output is "keep logging," not a score
- [ ] **Whether a weekly operating review already runs** — determines whether this layers on top or has to carry the operating cadence too
- [ ] **Carry-count history on open commitments** — the three-cycle rule is the sharpest mechanic here and needs the count to fire

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Workflows

### Workflow 1 — Score prediction calibration

Quarterly. The step that converts reflection from storytelling into measurement.

1. Resolve every prediction past its date — true or false, no revising the
   original confidence.
2. Run the scorer with 5 buckets (10 buckets need roughly 50+ predictions to be
   readable).
3. Read the calibration table first: gaps above 10 points in buckets holding 5+
   predictions are real bias, not noise.
4. Read the domain breakdown — bias is rarely uniform, and the worst domain is
   usually your own delivery dates.
5. Pick exactly one correction and re-measure over a full quarter.

```bash
python3 personal-productivity/reflect/scripts/calibration_scorer.py \
  --input personal-productivity/reflect/assets/sample_predictions.json \
  --buckets 5
```

The decomposition is computed over distinct confidence values, so `--buckets`
changes only the displayed table and never the statistics. Verify the identity
`BS = REL - RES + UNC` and the other scoring invariants at any time:

```bash
python3 personal-productivity/reflect/scripts/calibration_scorer.py --selftest
```

Isolate a single domain once you know where the bias lives:

```bash
python3 personal-productivity/reflect/scripts/calibration_scorer.py \
  --input personal-productivity/reflect/assets/sample_predictions.json \
  --domain delivery --buckets 5 --format json
```

### Workflow 2 — Generate a cadence-appropriate prompt set

Weekly, or at whichever cadence you are running.

1. Update commitment statuses from the past cycle — kept, missed, partial, open.
2. Increment `carried_cycles` on anything that rolled over again.
3. Run the generator for the cadence, with today's date for overdue detection.
4. Work the core prompts, then the accountability prompts — each of those needs
   a decision, not a note.
5. Satisfy the closing requirement. If nothing changed, the session was
   journaling.

```bash
python3 personal-productivity/reflect/scripts/reflection_prompt_generator.py \
  --input personal-productivity/reflect/assets/sample_commitments.json \
  --cadence weekly --as-of 2026-07-21
```

Quarterly, where structural change is allowed — note the quarterly log carries
`carried_cycles`, which is what fires the three-cycle rule:

```bash
python3 personal-productivity/reflect/scripts/reflection_prompt_generator.py \
  --input personal-productivity/reflect/assets/sample_commitments_quarterly.json \
  --cadence quarterly --as-of 2026-07-21 --format json
```

### Workflow 3 — Run the quarterly reflection end to end

90 minutes, once a quarter. The only cadence where role, commitments, and method
are on the table.

1. Score the prediction log (20 min) — Workflow 1.
2. Read the quarter's weekly reflections in one sitting (15 min). Individually
   unremarkable; in a batch they expose patterns invisible at weekly resolution.
3. Work the quarterly prompts from `assets/quarterly-reflection-template.md` (20 min).
4. Decide (20 min): kill one commitment, change one method, and give every
   chronic commitment an explicit date/delegate/kill decision.
5. Write next quarter's predictions with confidence numbers (15 min).

```bash
python3 personal-productivity/reflect/scripts/reflection_prompt_generator.py \
  --input personal-productivity/reflect/assets/sample_commitments_quarterly.json \
  --cadence quarterly --as-of 2026-07-21
```

## Decision frameworks

### Cadence selection

| Cadence | Time | Question it answers | Skip it when |
|---|---|---|---|
| Daily | 5 min | What did today prove me wrong about? | Time is short — this is the optional layer |
| **Weekly** | 20 min | Did my commitments hold, and what pattern explains the misses? | **Never — this is the load-bearing cadence** |
| Quarterly | 90 min | Is my judgement calibrated, and what structural thing must change? | Never; it is the only place structural change happens |

**[PROVEN] Start with weekly only.** The most common failure is starting daily
because it looks smallest, missing three days, and abandoning everything. Weekly
carries most of the value and survives a missed week without collapsing.

### Reading a Brier score

| Brier | Reading |
|---|---|
| < 0.10 | Excellent — or the predictions were too easy; check the skill score |
| 0.10-0.15 | Strong |
| 0.15-0.20 | Good; typical for a practised forecaster on genuinely uncertain questions |
| 0.20-0.25 | Weak — approaching a coin flip |
| > 0.25 | Worse than always saying 50%. Your confidence is actively misleading you |

The score decomposes into **reliability** (miscalibration — lower better) and
**resolution** (discrimination — higher better). The common pattern is decent
reliability with near-zero resolution: you have learned to hedge everything to
the base rate, which is safe and useless. The reverse — sharp judgement, wrong
numbers — is more valuable, because numeric calibration is easy to correct and
directional judgement is not.

### Commitment keep rate

| Keep rate | Reading | Action |
|---|---|---|
| > 85% | Under-committing; commitments are safe rather than execution strong | Commit to something that might fail |
| 60-85% | Healthy | Continue |
| < 60% | Committing to more than you deliver | **Cut the number of commitments before trying to improve execution** |

The instinct at a low keep rate is to try harder, which reliably fails — the
cause is volume, not effort. Halve the commitments and the rate usually recovers
on its own.

### The three-cycle rule `[PROVEN]`

A commitment carried three cycles without progress is not waiting for time; it
is waiting for a decision you keep declining to make. Carrying it a fourth time
*is* the decision — to never do it — so make it explicitly: commit to a date,
delegate it, or kill it.

### Where overconfidence concentrates

| Domain | Typical bias |
|---|---|
| **Your own delivery dates** | **Strongly overconfident — the most reliable bias in professional forecasting** |
| Sales / deal closing | Overconfident; role-required optimism leaks in |
| Competitor timing | Overconfident on when, decent on what |
| Other teams' delivery | Better calibrated — no inside view to be optimistic with |
| Metrics and trends | Reasonably calibrated; anchored to observable history |
| Hiring outcomes | Often underconfident; rejection memories are salient |

If you log only one category, log your own delivery dates: largest bias, fastest
resolution cycle, most immediate payoff in planning.

## Anti-Patterns

### Reflection as Journaling
**Mistake:** Writing a thoughtful account of how the period went, feeling clarified, and changing nothing.
**Why it happens:** Writing is pleasant and feels productive; deciding is uncomfortable and can be wrong. Given a prompt with no wrong answer — "how did the week go?" — the session drifts to narration.
**Instead:** Require every session to close with a named change, phrased as a rule rather than an intention. "No meetings before 11:00 on Tuesdays and Thursdays" is testable next week; "be better about deep work" can survive years unkept. If a session produces no rule, mark it as journaling in the log — after three consecutive entries, the prompts are wrong and need replacing.

### Reflecting Against Memory Instead of Records
**Mistake:** Asking "was I right about that?" and consulting recollection for the answer.
**Why it happens:** It does not feel like a failure mode. Memory reconstructs rather than replays, and it edits the prior belief toward the known outcome — so you sincerely remember having been less surprised, and having assigned more probability to what happened, than you did.
**Instead:** Write predictions with explicit confidence numbers before outcomes are known, and treat the log as append-only. The number written in advance is the only thing later reflection cannot quietly rewrite. This is precisely why calibration scoring is the core of the practice rather than an optional extra.

### Only Predicting Safe Things
**Mistake:** Filling the prediction log with claims you are already confident about, then reading the excellent Brier score as evidence of good judgement.
**Why it happens:** A bad score feels like a grade, so the log drifts toward things that will score well. Predicting "the sun rises tomorrow" at 99% produces a superb Brier and teaches nothing.
**Instead:** Watch the skill score, which compares you against always predicting the base rate. At or below zero, your forecasts carry no information beyond knowing how often things generally go your way. Deliberately log predictions you might be wrong about — finding your errors is the log's only job, and a log with no errors in it has failed at it.

### Scoring Too Often
**Mistake:** Reviewing calibration monthly or after every significant miss, then adjusting the approach each time.
**Why it happens:** A bad outcome creates an urge to fix something immediately, and the log is right there.
**Instead:** Score quarterly. With 15-30 predictions per quarter, a month yields too few resolved items to distinguish bias from luck, and reacting to that noise produces exactly the thrashing the practice exists to eliminate. Apply one correction per quarter and hold it for a full cycle — changing several things at once means you learn nothing about which of them worked.

## Files

| File | Purpose |
|---|---|
| `scripts/calibration_scorer.py` | CLI entry point: assembles the report (Brier, Murphy decomposition, calibration table, per-domain breakdown, skill score vs base rate, worst-calls list), renders text/JSON, and runs `--selftest` asserting 12 scoring invariants |
| `scripts/calibration_core.py` | Scoring internals imported by `calibration_scorer.py`: log loading, record normalisation, Murphy decomposition (exact — grouped on distinct forecast values, independent of `--buckets`), bucketing, per-domain stats, and the significance thresholds |
| `scripts/reflection_prompt_generator.py` | Cadence-specific prompt sets with per-commitment accountability prompts, keep-rate interpretation, and a closing requirement |
| `references/calibration-and-forecasting.md` | Writing scoreable predictions, Brier and skill-score interpretation, Murphy decomposition, domain-specific bias table, correction protocols |
| `references/reflection-cadences.md` | Daily/weekly/quarterly prompt sets, the boundary with the weekly operating review, three-cycle rule, keep-rate bands, what makes reflection fail |
| `assets/prediction-log-template.md` | Prediction-log format, confidence conventions, weekly resolution ritual, quarterly scoring table |
| `assets/quarterly-reflection-template.md` | Timed 90-minute quarterly agenda with the kill list, chronic-commitment decisions, and next-quarter predictions |
| `assets/sample_predictions.json` | 30 predictions (27 resolved, 3 pending) showing realistic delivery-date overconfidence, so scoring runs out of the box |
| `assets/sample_commitments.json` | One week of commitments — 10 items spanning kept/missed/partial/open with two chronic carries, for the weekly cadence |
| `assets/sample_commitments_quarterly.json` | One quarter of commitments — 18 items with four chronic carries and three overdue, for the quarterly cadence |
