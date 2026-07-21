# Weekly Processing Pass — Checklist

**Slot:** _______________  (same time every week, recurring, defended)
**Duration:** 45 minutes
**Date of this pass:** _______________

---

## 0. Before you start (2 min)

- [ ] Notifications off, single window, no email visible
- [ ] Capture log open
- [ ] Timer set for 45 minutes

---

## 1. Gather (5 min)

Drain every capture surface into the one processing inbox.

- [ ] Phone notes / voice memos
- [ ] Paper notebook and loose paper
- [ ] Browser tabs left open as reminders
- [ ] Meeting notes marked `TODO:`
- [ ] Chat messages sent to self
- [ ] Desktop / downloads folder
- [ ] Anything on the physical desk

**Inbox count after gathering:** _______

---

## 2. First-pass classification (5 min)

```bash
python3 scripts/capture_triage.py --input capture_log.json --today YYYY-MM-DD
```

- [ ] Reviewed the bucket distribution
- [ ] Noted the count of items flagged `unactionable-phrasing` or `no-verb`
- [ ] Did the flagged 2-minute items right now

---

## 3. Process every item (20 min)

One at a time, in order, no skipping. For each:

1. Actionable? → if no: reference / someday / **drop**
2. What does done look like? (one sentence)
3. One step or several? → several means project + defined first action
4. Under 2 minutes? → do it now
5. Someone else's? → delegate + record who + follow-up date
6. Date-specific? → calendar, not the list

**Target: inbox empty.** Not "reviewed" — empty.

| Outcome | Count | Healthy range |
|---|---|---|
| Done during the pass | ____ | — |
| New actions | ____ | — |
| New projects | ____ | — |
| Delegated (waiting-for) | ____ | — |
| Filed as reference | ____ | — |
| Someday | ____ | 20-30% combined with reference |
| **Dropped** | ____ | **15-25% — if zero, you filtered too early** |
| Left in inbox | ____ | 0-3 |

---

## 4. Project review (8 min)

- [ ] Every project has exactly one visible next action
- [ ] Projects with no next action — fix now, or demote to someday
- [ ] Projects with no progress in 3 weeks — flagged for a keep/drop decision

**Stalled projects found:** _______

---

## 5. Waiting-for review (5 min)

- [ ] Every delegated item has a follow-up date
- [ ] Overdue follow-ups sent now
- [ ] Items waiting more than 2 weeks with no reply — escalated or taken back

---

## 6. Someday scan (2 min)

- [ ] Anything now relevant → promoted to a project
- [ ] Anything dead → dropped without guilt

---

## 7. Health check (monthly)

```bash
python3 scripts/capture_audit.py --input capture_log.json --today YYYY-MM-DD
```

| Metric | This month | Target |
|---|---|---|
| Median inbox age | ____ d | < 7 d |
| Share older than 14 days | ____ % | < 20% |
| Share without a concrete verb | ____ % | < 25% |
| Status | ____ | healthy |

**One change for next month:** _______________________________________
