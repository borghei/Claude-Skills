# Communication Charter — <Team Name>

**Owner:** <name> · **Version:** 1.0 · **Effective:** <YYYY-MM-DD> · **Review by:** <YYYY-MM-DD, +6 months>

> One page. If this grows past one page, something in it is not a rule.

---

## 1. Core hours

| Region | Working window (local) | UTC window |
|--------|------------------------|------------|
| <region> | <09:00-17:00> | <HH:MM-HH:MM> |
| <region> | <09:00-17:00> | <HH:MM-HH:MM> |

**Core overlap:** <N> hours, <HH:MM-HH:MM UTC>.
Overlap is reserved for decisions and incidents. Status is never sync.

---

## 2. Channel rules

| Situation | Channel | Notes |
|-----------|---------|-------|
| Irreversible / expensive decision | Written decision record in `<location>` | Named approver required |
| Reversible decision, shared context | `#team-<name>` thread | Area owner decides |
| Low shared context + a decision needed | Booked meeting, agenda + pre-read | Notes published within 24h |
| Performance, pay, conflict, anything personal | Live 1:1 | Never in writing first |
| Information to 8+ people, no decision | `#announce-<scope>` or email | No thread expected |

**No decisions in DMs or private groups.** A decision that cannot be found will be made again, differently.

---

## 3. Meeting rules

- No agenda posted by start time → the meeting is cancelled. No exceptions.
- Every recurring meeting has a named owner, a written record, and an **expiry date** (`<YYYY-MM-DD>`); at expiry it is re-justified or it dies.
- Default durations are **25 and 50 minutes**. The gap is for writing the notes.
- Attendees are marked **required** or **optional**, and optional genuinely means no consequence for declining.
- Decisions and actions are posted to `<location>` within 24 hours, with owner and date.
- **No-meeting day:** `<weekday>`, org-wide.
- **Focus blocks** on the calendar are honoured like meetings — no booking over, no pinging into.

---

## 4. Response SLAs

| Urgency | Definition | Acknowledge within | Resolve within |
|---------|-----------|--------------------|----------------|
| P0 — incident | Customer-facing outage or data loss | 15 min | Until resolved |
| Same-day | Blocks someone's work today | 2 working hours | Same day |
| This-week | Blocks work this cycle | 1 working day | 3 working days |
| Scheduled | Planning, review, non-blocking | 3 working days | Next planning cycle |

Acknowledgement is not resolution. "Seen it, answer by Thursday" satisfies the acknowledge SLA.

Messages sent outside a recipient's working hours are **scheduled, not sent**.

---

## 5. Escalation path

Escalation is a **process failure signal, not an interpersonal act**. Nobody is penalised for escalating.

1. **Strike 1** — ask the owner directly, in the channel where the work lives (not DM), with a stated deadline.
2. **Strike 2** — after the SLA lapses, restate publicly with the cost: what is blocked, what it costs, what you need. Tag the owner and their manager.
3. **Strike 3** — escalate to `<shared manager role>` with a written summary of strikes 1 and 2.

**Incidents skip the ladder:** page `<on-call rotation>` immediately.

---

## 6. Decision protocol

- **Needs a written record:** <list the categories — e.g. schema changes, public API contracts, pricing, org structure, vendor commitments over $X>
- **Approver:** one named person per record. Never a team.
- **Comment deadline:** <N> working days, spanning a full working day in **every** participant timezone.
- **Silence past the deadline is consent**, provided the deadline was posted in the doc and the channel.
- **Two rounds of unresolved comments → book 20 minutes.** Post the outcome back into the doc.
- **Decision log lives at:** `<link>`

---

## 7. Timezone norms

- The unsociable meeting slot **rotates quarterly**. Current rotation: `<link>`
- Every sync anyone could not attend is **recorded and its notes published**.
- The last person working in a region writes the **handoff**: finished / blocked / pick up next.
- All times written in **UTC with an explicit date**. Never "tomorrow morning".

---

## 8. Amendments

Raise a change in `#team-<name>`, tagging the charter owner. Changes take effect once the owner posts the updated version. This charter is reviewed on `<YYYY-MM-DD>` regardless of whether anyone has complained about it.
