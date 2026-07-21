# Deep-Work Session Log

One entry per session, logged in the last two minutes of the block. If logging
takes longer than that, cut fields until it doesn't — an administrative burden
that competes with the work will be abandoned within a fortnight.

---

## Pre-commitment (write this the night before)

> Tomorrow, **[HH:MM–HH:MM]**, I will work on **[artefact]** until **[observable done-state]**.

If you cannot name an observable done-state, the work is not ready for a deep
block — it needs a planning pass first. Deciding what to work on *inside* the
block burns the freshest attention of your day on a decision you could have made
while tired.

---

## Session entry

```json
{
  "date": "2026-07-21",
  "planned_min": 120,
  "actual_min": 105,
  "interruptions": 1,
  "artefact": "migration-plan.md",
  "focus_rating": 4
}
```

| Field | Required | Notes |
|---|---|---|
| `date` | Yes | `YYYY-MM-DD` |
| `actual_min` | Yes | Minutes actually worked, not minutes blocked |
| `planned_min` | No | Defaults to `actual_min`; drift over 20% means encroachment or optimistic planning |
| `interruptions` | No | Count anything that broke the thread, including self-interruptions |
| `artefact` | No | Single artefact. Use `artefacts: [...]` only when the session genuinely split — that is the signal you want to see |
| `focus_rating` | No | 1-5, subjective. The only field that catches "present but not engaged" |

---

## Close-out (last 5 minutes, before the entry)

- [ ] Current state of the artefact written down in one line
- [ ] Next entry point named — ideally stopping mid-thought, which halves tomorrow's warmup
- [ ] Any blockers captured (not solved)

Skipping close-out is why the session after a rushed one is always the weakest.

---

## Weekly log

| Date | Planned | Actual | Intr. | Artefact | Focus |
|---|---|---|---|---|---|
| | | | | | |
| | | | | | |
| | | | | | |
| | | | | | |
| | | | | | |

---

## Monthly review

Run the analyser — monthly, not weekly. Deep-work volume is noisy week to week
(one conference swamps the signal), and reacting to that noise produces
thrashing.

```bash
python3 scripts/session_log_analyzer.py --input sessions.json --weekly-target 600
```

| Metric | This month | Target |
|---|---|---|
| Total deep-work hours | ____ | Set from the role table in `references/defending-focus-time.md` |
| Median session length | ____ min | ≥ 90 min; 120 is the sweet spot |
| Share of sessions ≥ 90 min | ____ % | > 60% |
| Mean interruptions/hour | ____ | < 1.0 |
| Sessions touching >1 artefact | ____ % | < 30% |
| Trend direction | ____ | stable or improving |

**One change for next month:** _______________________________________

Pick exactly one. Volume, block length, and defence are three different
problems with three different fixes, and working on all of them at once means
you learn nothing about which one mattered.
