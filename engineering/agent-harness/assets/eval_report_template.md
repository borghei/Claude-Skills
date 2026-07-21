# Agent Eval Report — <suite name>

**Candidate:** <run id> (<model / prompt sha>)
**Baseline:** <run id> (<model / prompt sha>)
**Date:** YYYY-MM-DD
**Decision requested:** ship / hold / ship with waiver

---

## Verdict

<One sentence. Lead with the decision, not the numbers.>

| Signal | Baseline | Candidate | Movement |
|--------|----------|-----------|----------|
| Critical failures | | | |
| Scenarios regressed | — | | |
| Scenarios fixed | — | | |
| Pass rate (95% CI) | | | |
| Total cost | | | |
| Mean latency | | | |

---

## Critical failures

> Any entry here blocks release. If empty, write "None."

| Scenario | Assertion | What the agent did | Blast radius |
|----------|-----------|--------------------|--------------|
| | | | |

---

## Regressions

| Scenario | Failing assertions | Suspected cause | Owner |
|----------|--------------------|-----------------|-------|
| | | | |

## Fixes

| Scenario | Previously failing | Confirmed by |
|----------|--------------------|--------------|
| | | |

---

## Budget drift

> Scenarios whose cost or latency moved more than the drift threshold, even
> where both runs stayed inside budget.

| Scenario | Cost Δ | Latency Δ | Cause |
|----------|--------|-----------|-------|
| | | | |

---

## Statistical read

- Discordant scenarios (flipped either direction): **<b + c>**
- Exact McNemar p: **<p>**
- Interpretation: <If fewer than ~6 flipped, state that the p-value is not
  informative at this size and that the decision rests on the individual
  regressions above.>
- Noise floor: <flips observed when the identical config was diffed against
  itself, or "not measured" — and if not measured, say so.>

---

## Waivers requested

| Scenario | Why the regression is acceptable | Approver | Expires |
|----------|----------------------------------|----------|---------|
| | | | |

---

## Follow-ups

- [ ] New scenarios added from this run's findings
- [ ] Budgets re-derived from the accepted run
- [ ] Baseline report promoted to `release-current.report.json`
