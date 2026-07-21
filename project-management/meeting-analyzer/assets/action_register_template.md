# Action Register — <Team / Meeting Series>

**Maintained by:** <name> · **Reviewed:** every <meeting> · **Last updated:** <YYYY-MM-DD>

> Review rule: overdue items and third carry-overs only. Reading the full
> register aloud is how a 5-minute review becomes a 20-minute one.

---

## Open actions

| ID | Action | Owner | Due | Created | Carried | Status |
|----|--------|-------|-----|---------|---------|--------|
| a-001 | <Verb + object, one action per row> | <Name> | <YYYY-MM-DD> | <YYYY-MM-DD> | 0 | open |
| a-002 |  |  |  |  |  | in_progress |
| a-003 |  |  |  |  |  | blocked |

**Status values:** `open` · `in_progress` · `blocked` · `done` · `dropped`

**Rules:**
- One action per row. "Sam scopes it and Lena confirms the schema" is two rows.
- Owner is one named person. Never "the team", "we", or "TBD".
- Due is an ISO date. Never "soon", "ASAP", "next sprint", or "when I get a chance".
- An action assigned to someone absent is **provisional** until they confirm — mark it `(unconfirmed)`.

---

## Third carry-over — decide now

Items carried three times get re-committed with a new date **stated by the owner**, or dropped. There is no fourth carry.

| ID | Action | Owner | Carried | Re-commit to | Or drop |
|----|--------|-------|---------|--------------|---------|
|  |  |  | 3 | <YYYY-MM-DD> | [ ] |

---

## Decisions log

| Date | Decision | Approver | Rationale | Supersedes |
|------|----------|----------|-----------|------------|
| <YYYY-MM-DD> | <What was decided, past tense> | <one name> | <one clause> | <ID or —> |

A decision with no named approver will be re-litigated by whoever was absent.

---

## Open questions

| Question | Owner | Answer needed by | Blocks |
|----------|-------|------------------|--------|
| <the actual question> | <Name> | <YYYY-MM-DD> | <what it blocks, or —> |

An unowned open question is how a known unknown becomes a surprise. Owner and date are required here too.

---

## Closed this period

| ID | Action | Owner | Closed | On time | Outcome |
|----|--------|-------|--------|---------|---------|
|  |  |  | <YYYY-MM-DD> | yes/no | done / dropped |

Dropped items stay in the record. Deleting them destroys the signal that this meeting generated work nobody valued.

---

## Health snapshot

| Metric | This period | Target |
|--------|-------------|--------|
| Completion rate | <%> | 75%+ |
| Actions with owner **and** date | <%> | 90%+ |
| On-time closure | <%> | 70%+ |
| Open beyond 30 days | <n> | 0-1 |
| Average carry-over | <n> | under 1 |

If every owner looks bad, the meeting is generating more actions than the team has capacity for. Cap actions per meeting rather than treating it as several simultaneous performance issues.
