# Eval Methodology, Regression Statistics, and Budgets

How to read an eval run without fooling yourself: scoring rubrics, the
statistics that apply at agent-eval sample sizes, cost and latency budgets, and
CI wiring.

---

## 1. Scoring: three layers, in order of trust

| Layer | Mechanism | Trust | Cost |
|-------|-----------|-------|------|
| **Programmatic** | Tool calls, arguments, parsed JSON, error state, budgets | High — exact and reproducible | Free |
| **Reference-based** | Compare against a stored expected answer with a similarity or containment rule | Medium — brittle to rewording | Free |
| **Model-graded** | An LLM judge scores against a rubric | Low-medium — noisy, drifts with the judge model | Expensive |

**[PROVEN] Push as much of your rubric as possible down to the programmatic
layer.** Teams reach for LLM judges first because natural-language output feels
unassertable, then spend months debugging judge noise. Most of what "correct"
means for a *tool-using agent* is structural: did it call the right tool, with
the right arguments, in the right order, and refrain from the forbidden ones.
That is programmatic, free, and does not drift.

This skill's scripts implement the programmatic layer only. They call no models
and reach no network, which is why they can run on every commit.

### If you do add a model-graded layer

Four rules that keep it from becoming decoration:

1. **Pin the judge model and version.** A judge upgrade silently rescores your
   entire history. Treat the judge version like a schema migration.
2. **Calibrate against human labels.** Score 50 transcripts by hand, measure
   judge-human agreement (Cohen's kappa). Below κ = 0.6 the judge is not usable
   as a gate.
3. **Use a rubric with discrete anchored levels, not a 1-10 scale.** "Fully
   answered / partially answered / did not answer / harmful" produces far more
   stable judgments than a continuous score.
4. **Never let the judge see which arm it is grading.** Blind and shuffle, or
   you will measure the judge's prior, not the agent.

---

## 2. Reading a run: the pass rate is the least useful number

The aggregate pass rate is a summary of a small sample and moves on noise. Read
a run in this order:

1. **Critical failures.** Any nonzero count blocks, regardless of pass rate.
2. **The regression list.** Which specific scenarios flipped from pass to fail.
3. **Budget drift.** Cost and latency per scenario versus the previous run.
4. **Pass rate with its interval.** Last, and only with the interval attached.

`eval_diff.py` prints them in exactly this order for that reason.

The sample data shipped in `assets/` makes the point: baseline and candidate
both score 83.3%, and the candidate contains a critical prompt-injection
regression. A team gating on pass rate ships it.

---

## 3. The statistics that actually apply

### Wilson interval, not the normal approximation

At n = 30 with 26 passes, the textbook normal interval gives [0.75, 0.98] and
misbehaves badly near 0 and 1. The Wilson score interval is well-behaved at
small n and at extreme proportions, and is what `eval_diff.py` reports.

Half-widths at 85% pass, for calibration:

| n | 95% CI half-width |
|---|-------------------|
| 10 | ±22 pts |
| 30 | ±13 pts |
| 100 | ±7 pts |
| 300 | ±4 pts |

**Implication:** with a 30-scenario suite you cannot detect a 5-point
regression from the aggregate rate. You can detect it from the paired diff.

### Paired comparison — McNemar, exact

Both runs execute the *same* scenarios, so the arms are paired and you should
never compare two independent proportions. The relevant data are only the
**discordant** scenarios:

|  | Candidate passes | Candidate fails |
|--|------------------|-----------------|
| **Baseline passes** | a (concordant) | **b (regressions)** |
| **Baseline fails** | **c (fixes)** | d (concordant) |

The null hypothesis is that a flipped scenario is equally likely to flip either
way, i.e. b and c are draws from Binomial(b+c, 0.5). `eval_diff.py` computes
the **exact** two-sided binomial p-value rather than the chi-square
approximation, because at b+c < 25 the approximation is unreliable — and at
agent-eval sizes b+c is almost always under 25.

### The small-sample honesty rule

**[RECOMMENDED] Below about 6 discordant scenarios, report the regressions and
suppress the p-value.** With b = 2, c = 0 the exact p is 0.50; with b = 4,
c = 0 it is 0.125. Neither reaches significance, and neither means the
regression is not real — it means the test has no power there. Reporting
"p = 0.13, not significant" next to a scenario where the agent refunded money
it should not have is statistical theatre. `eval_diff.py` prints the guidance
line instead of a bare p-value for this reason.

**A single critical-severity regression is actionable at n = 1.** Significance
testing is for aggregate movement, never for safety failures.

### Run-to-run variance

Before attributing any change to your prompt edit, know your noise floor:
**run the identical configuration twice and diff it against itself.** If four
scenarios flip on a no-op change, four flips carry no information. Teams that
skip this step spend weeks chasing phantom regressions.

Reduce the floor by: setting temperature to 0 where the product allows,
replaying tool results rather than calling live backends, and rerunning only
the flipped scenarios (n = 5 repeats) to separate flaky scenarios from real
regressions.

---

## 4. Cost and latency budgets

A correct-but-unaffordable agent is a failed agent, and cost regressions are
invisible to correctness scoring. Budget every scenario.

### Setting budgets

| Budget | Set it at | Rationale |
|--------|-----------|-----------|
| **Per-scenario latency** | p95 of the last good run × 1.3 | Absorbs normal variance, catches a doubling |
| **Per-scenario cost** | Median of the last good run × 1.5 | Token use is spikier than latency |
| **Suite total cost** | Sum of per-scenario budgets | The number finance asks about |
| **Turn ceiling** | Observed max + 2 | Catches loops before the token bill does |

Declare defaults once in the suite and override only where a scenario is
legitimately more expensive:

```json
"defaults": {"max_latency_ms": 12000, "max_cost_usd": 0.08, "max_turns": 8}
```

`scenario_runner.py` injects the defaults as `minor`-severity assertions for
any scenario that does not declare its own, so budgets are reported everywhere
without blocking a release on a slow Tuesday.

### Drift, not thresholds, catches the slow bleed

A budget catches a step change. It does not catch 8% cost growth per release,
which compounds to a doubling in nine releases. `eval_diff.py --drift-threshold
0.15` flags any scenario whose cost or latency moved more than 15% against the
baseline even when both runs are inside budget. Review the drift list every
release; that is where the retrieval change that quietly tripled the context
window shows up.

### The four causes of cost regression, in frequency order

1. **Retrieval or context growth** — more documents stuffed per turn. Largest
   and most common.
2. **Extra tool round-trips** — a prompt change made the agent verify twice.
   Visible as a turn-count increase.
3. **Retry loops on tool errors** — cheap when rare, ruinous when a backend
   degrades. Cap retries in the agent, assert `max_tool_calls` in the suite.
4. **Model swap** — obvious, and the only one teams reliably notice.

---

## 5. CI wiring

**[RECOMMENDED] Two gates, not one.**

```bash
# Gate 1 — safety. Runs on every PR touching prompts, tools, or model config.
python3 scripts/scenario_runner.py \
  --suite evals/suites/safety.json \
  --transcripts evals/runs/pr-${PR}.json \
  --strict-critical --format json > report.json

# Gate 2 — regression against the last release. Blocks on any flip.
python3 scripts/eval_diff.py \
  --baseline evals/reports/release-current.report.json \
  --candidate report.json \
  --fail-on-regression --drift-threshold 0.15
```

Gate 1 exits 2 on any critical failure and is non-negotiable. Gate 2 exits 2 on
any regression and should be overridable by a human with a written reason —
some regressions are intentional trades, and a gate no one can override gets
deleted.

Store `report.json` as a build artifact for every run. The report history is
what lets you answer "when did this start" six weeks later, and it costs
kilobytes.

### What to put in the PR comment

Four lines, in this order: critical failure count, regressed scenario IDs,
cost delta, pass rate with interval. Anything longer does not get read.

---

## 6. Anti-patterns in eval methodology

| Anti-pattern | Consequence | Fix |
|--------------|-------------|-----|
| Gating on aggregate pass rate alone | Ships critical regressions at flat pass rate | Gate on `--strict-critical` and the paired diff |
| Comparing runs from different suite versions | Meaningless diff | Pin the suite; treat suite edits as their own PR |
| Tuning the prompt until the suite passes | Overfits to 30 scenarios | Hold out 20% of scenarios; never look at them during iteration |
| Rerunning until green | Selects for lucky runs | Fix the seed/temperature, or report the mean of k runs |
| No noise floor measurement | Chases phantom regressions | Diff an identical config against itself first |
| Judge model upgraded mid-history | Silently rescores everything | Pin and version the judge |
| Budgets set once and never revisited | Budgets drift above reality and stop binding | Re-derive from the last good run each release |
