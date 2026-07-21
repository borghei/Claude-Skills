# Quarterly Reflection

**Quarter:** _______  **Date:** _______  **Time budget:** 90 minutes

The one cadence where structural change is allowed to happen. Weekly reflection
tunes; this one decides.

---

## 1. Score the predictions (20 min)

```bash
python3 scripts/calibration_scorer.py --input predictions.json --buckets 5
```

| Metric | Value | Reading |
|---|---|---|
| Resolved | ____ | ≥ 20 for a trustworthy estimate |
| Brier | ____ | < 0.20 good; > 0.25 worse than always saying 50% |
| Skill score | ____ | ≤ 0 means no more informative than the base rate |
| Overall gap | ____ | + is overconfident, − is underconfident |
| Worst domain | ____ | Usually your own delivery dates |

**Were the errors in a consistent direction?** _______________________________

---

## 2. Read the quarter's weekly reflections (15 min)

Read all twelve in one sitting. Individually unremarkable; in a batch they show
patterns invisible at weekly resolution.

**Recurring themes (3-5):**

1. _______________________________________
2. _______________________________________
3. _______________________________________

**The same blocker that appeared more than twice:** ___________________________

---

## 3. Prompts (20 min)

**Which quarter-start predictions were wrong, and in what direction?**

**What did I commit to and never start? What does that pattern say about what I actually value — as opposed to what I say I value?**

**Where was I overconfident, and what did it cost in decisions made on that confidence?**

**What did I learn that changed how I work, versus what I merely read about?**

**If I were advising someone else with this quarter's record, what would I tell them to stop doing?**

> This last prompt does disproportionate work. The advice you would give someone
> else is consistently clearer and more decisive, because it carries none of the
> sunk cost or self-image attached to your own record.

---

## 4. Decide (20 min)

### Kill one thing (required)

Every quarterly reflection kills at least one commitment — a recurring meeting,
a project, a metric nobody acts on, a habit that has not paid off.

This is not arbitrary. Commitments accumulate monotonically: each was added for
a reason and none individually feels worth removing, so without a forced removal
four quarters of additions leave no room for anything new.

**Killing:** _______________________________________
**Because:** _______________________________________

### Change one method

**From:** _______________________________________
**To:** _______________________________________

Phrase it as a rule, not an intention. "No meetings before 11:00 on Tuesdays and
Thursdays" is testable next week; "be better about deep work" is not, which is
why intentions survive for years unkept.

### Chronic commitments — decide each

Any commitment carried 3+ cycles. Carrying it again is a decision to never do
it, so make the decision explicitly.

| Commitment | Cycles carried | Decision (date / delegate / kill) |
|---|---|---|
| | | |
| | | |

---

## 5. Next quarter's predictions (15 min)

15-30 predictions with explicit confidence. Include your own delivery dates —
the highest-bias, fastest-resolving, most useful category to log.

| Statement | Domain | Confidence | Resolve by |
|---|---|---|---|
| | | | |
| | | | |
| | | | |
| | | | |
| | | | |

---

## Closing check

- [ ] One commitment killed
- [ ] One method changed, phrased as a rule
- [ ] Every chronic commitment given an explicit decision
- [ ] Next quarter's predictions written with confidence numbers
- [ ] One calibration correction chosen — exactly one

If none of these boxes is ticked, this was a reading exercise rather than a
reflection.
