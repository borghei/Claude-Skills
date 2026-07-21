# Prediction Log

Append-only. **Never revise a prediction after the outcome is known** — the log's
entire value is that it records what you believed before you knew, which is the
one thing memory cannot be trusted to preserve.

---

## Writing a scoreable prediction

A prediction is scoreable when a disinterested third party could look at the
world on the resolution date and declare it true or false without argument.

**Claim + resolution date + confidence number.**

| Not scoreable | Scoreable |
|---|---|
| "The migration will go well" | "The migration completes with no rollback and under 30 min downtime, by June 30" — 70% |
| "We'll hire someone soon" | "We sign a staff engineer offer by August 31" — 55% |
| "Churn should improve" | "Monthly churn is below 3.0% in July" — 60% |

**Conventions:** 50-95% only (below 50%, restate as the negation). Round to 5%.
Avoid 100% and 0% — nothing about the future deserves them. 50% is a legitimate
answer, and a log with no 50% entries usually means you are only recording
claims you already feel safe about.

**Volume:** 15-30 per quarter. Below 20 resolved, the calibration estimate is
too noisy to act on; above 40, logging becomes a chore and the habit dies.

---

## Entries

```json
{
  "predictions": [
    {
      "id": "P1",
      "statement": "The migration ships before end of Q2",
      "domain": "delivery",
      "confidence": 0.70,
      "made_on": "2026-07-21",
      "resolve_by": "2026-09-30",
      "outcome": null
    }
  ]
}
```

| Field | Required | Notes |
|---|---|---|
| `statement` | Yes | Must be resolvable by a third party |
| `confidence` | Yes | 0-1 or 0-100; both accepted |
| `outcome` | Yes at resolution | `true` / `false`; `null` or `"unresolved"` while pending |
| `domain` | Recommended | Drives the per-domain breakdown — where the actionable signal lives |
| `made_on`, `resolve_by` | Recommended | `resolve_by` is what stops predictions rotting unresolved |

---

## Table format

| ID | Statement | Domain | Conf. | Made | Resolve by | Outcome |
|---|---|---|---|---|---|---|
| | | | | | | |
| | | | | | | |
| | | | | | | |

---

## Weekly (5 min): resolve what is due

- [ ] Every prediction past its `resolve_by` marked true or false
- [ ] Disputed resolutions noted — a dispute means the statement was underspecified; write the next one tighter
- [ ] New predictions added for decisions made this week

An unresolved prediction teaches nothing. Resolution is the cheap step people
skip, and skipping it is what makes prediction logs quietly useless.

---

## Quarterly (30 min): score

```bash
python3 scripts/calibration_scorer.py --input predictions.json --buckets 5
```

| Metric | This quarter | Target |
|---|---|---|
| Resolved count | ____ | ≥ 20 |
| Brier score | ____ | < 0.20 |
| Skill score | ____ | > 0.15 |
| Overall gap | ____ | within ±10% |
| Worst domain | ____ | — |

**One correction for next quarter:** _______________________________________

Apply exactly one and re-measure over a full quarter. Changing several things
at once means you learn nothing about which of them worked.

If overconfident, the crude correction outperforms the clever one: subtract the
measured gap from every stated confidence for a quarter. Expect the worst domain
to be your own delivery dates — that bias is close to universal, and finding it
is the point rather than a failure.
