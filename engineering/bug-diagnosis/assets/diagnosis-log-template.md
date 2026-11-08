# Diagnosis Log — <bug title>

**Reported by:** <name / ticket>  **Owner:** <name>  **Opened:** YYYY-MM-DD
**Status:** investigating | fixed | blocked
**Debug tag:** `[DBG-xxxx]` (every temporary log line carries it)

## 1. Symptom

- Expected: <what should happen>
- Actual: <exact error text, wrong value or measured latency — redacted>
- First seen: <date, release, or commit>
- Scope: <who / which inputs are affected; who is not>

## 2. Reproduction signal

| Field | Value |
|-------|-------|
| Command | `<one command; secrets read from environment variables>` |
| Asserts | <the specific symptom it checks> |
| Runs / red runs | <n> / <n> |
| Runtime | <seconds> |
| Minimised | yes / no — <what was removed> |
| Pinned | clock, seed, locale, network, workers |

## 3. Hypotheses (write all before testing any)

| ID | Mechanism | Prediction (if … then …) | Experiment | Prior | Cost (min) | Status | Evidence |
|----|-----------|--------------------------|------------|-------|-----------|--------|----------|
| H1 | | | | | | open | |
| H2 | | | | | | open | |
| H3 | | | | | | open | |

## 4. Experiments (one variable each)

| # | Hypothesis | Change | Variable changed | Result | Notes |
|---|------------|--------|------------------|--------|-------|
| 1 | | | | | |

## 5. Bisection (if used)

- Space: commits / input records / flags / dependency versions
- Good: <state>  Bad: <state>
- Result: <first bad state> — attach `git bisect log` or the halving trail

## 6. Cause

<The confirmed hypothesis, the evidence that confirmed it, and why it produces
the symptom.>

## 7. Fix and regression test

- Regression test: `<path::name>` — seen failing before the fix: yes / no
- If no test: reason no seam reaches the failure pattern
- Original signal green after fix: yes / no
- `grep -rn "<debug tag>"` returns nothing: yes / no
- Shared artefacts passed through `redact_scan.py`: yes / no

## 8. Follow-ups

- <design issue surfaced, monitoring gap, related bugs>
