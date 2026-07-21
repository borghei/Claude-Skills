---
name: team-communications
description: >
  Design a delivery team's communication system — channel routing, meeting-load
  reduction, status structure, escalation SLAs, timezone norms. Use when the
  calendar is full, updates go unread, or blockers surface late.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-07-21
  tags: [async, meeting-load, status-updates, escalation, timezones, team-operations]
---

# Team Communications

The operating system a delivery team runs its information on: which channel a
given message belongs in, how much the recurring calendar actually costs, how a
status update survives a 20-second executive skim, and what happens when
someone is blocked. Most teams never design this — it accretes, one
well-intentioned meeting at a time, until 30% of the week is gone and blockers
still surface three days late.

## When to use this skill

- **The calendar is full and nobody can say why** — you need the meeting load
  measured in person-hours and dollars before you can argue about it
- **Status updates go unread** — stakeholders keep asking questions the update
  already answered, which means it is not skimmable
- **Blockers surface late** — a problem that existed Monday first appears in
  Thursday's status, because there is no escalation path with an SLA
- **A team goes distributed or adds a third timezone** — the sync-heavy rhythm
  that worked co-located silently taxes one region
- **Recurring "should this be a meeting?" arguments** — you need a routing rule
  the team agreed to in advance, not a per-case negotiation
- **New team formation** — write the charter on day one, before the calendar
  fills with rituals nobody will later feel able to cancel

## Inputs the skill expects

- A calendar export of recurring meetings: title, duration, cadence, attendees,
  day and start time (UTC)
- The people involved with roles, timezones, and fully-loaded hourly cost
- Recent decision counts per recurring meeting (last month), plus whether each
  has an agenda and written notes
- A draft status update, or a recent one that failed to land
- The team's core-hours overlap and current escalation path, if either exists
- What is currently going wrong: unread updates, late blockers, or calendar load

## Clarify First

Before generating, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Which failure you are fixing — load, unread updates, or late blockers** — the three have opposite remedies; cutting meetings without installing written status makes late blockers worse
- [ ] **Core-hours overlap across the team** — under 3 hours the recommendation inverts from "meet on disagreement" to "sync is an escalation"
- [ ] **Whether cancelling meetings is actually in scope** — an audit you cannot act on is a grievance document; if the calendar is fixed, the leverage moves entirely to written quality
- [ ] **Fully-loaded hourly cost, or permission to estimate it** — the dollar figure is what moves stakeholders; base salary alone understates by 30-40%

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Workflows

### Workflow 1 — Audit and cut the meeting load

1. Export recurring meetings into the calendar JSON shape (see
   `assets/sample_calendar.json`): people with hourly cost and timezone,
   meetings with duration, cadence, attendees, day, start time.
2. Record **decisions produced in the last month** per meeting series, and
   whether each has an agenda and written notes. This is the input the audit
   turns on — estimate it with the meeting owner rather than skipping it.
3. Run the auditor. Read three outputs: total annual cost, per-meeting
   verdicts, and per-person maker hours.
4. Publish the numbers **before proposing any cut**. Agreement that the total
   is too high has to precede the argument about any specific meeting.
5. Cancel every `KILL` outright, convert every `ASYNC` to a written update with
   a comment window, then merge the 60%+ audience overlaps.
6. Re-audit in six weeks. Expect 20-30% regrowth — that is normal, cut it again.

```bash
python3 project-management/team-communications/scripts/meeting_load_auditor.py \
  --input project-management/team-communications/assets/sample_calendar.json \
  --maker-hours-target 24 --format text
```

### Workflow 2 — Route the week's communications

1. List the decisions, announcements and questions currently pending, one entry
   each in `assets/sample_messages.json` shape.
2. For each, record the four routing variables: reversibility (`one_way` /
   `two_way`), stakeholder count, shared context (`low` / `medium` / `high`),
   and hours until it is needed.
3. Run the router. Every message gets a channel, an urgency band, an SLA, and
   the reason — which is what makes the routing defensible when someone
   disagrees.
4. Check the sync share. Above 34% the team is buying calendar time to
   compensate for thin written context; fix the writing, not the calendar.
5. Freeze the resulting rules into the charter template so the next routing
   argument resolves by reference instead of by seniority.

```bash
python3 project-management/team-communications/scripts/channel_router.py \
  --input project-management/team-communications/assets/sample_messages.json \
  --core-overlap-hours 3 --format text
```

### Workflow 3 — Score a status update before sending it

1. Draft the update against `assets/status_update_template.md`.
2. Score it. The tool checks the four load-bearing elements (progress, risk,
   decision needed, ask), executive readability, and skimmability.
3. Fix in the order the tool lists — completeness gaps first, because a missing
   ask costs more than a long sentence.
4. Anything under 70 does not get sent. Rewrite and re-score.
5. Keep the scores. A team whose median drifts below 70 over a quarter has a
   reporting problem, not a bad week.

```bash
python3 project-management/team-communications/scripts/status_update_scorer.py \
  --input project-management/team-communications/assets/sample_status_update.json \
  --format text
```

## Decision frameworks

### Channel routing — first rule that fires wins [PROVEN]

| Rank | Condition | Channel |
|------|-----------|---------|
| 1 | Emotional load: performance, pay, conflict, standing | Live 1:1 |
| 2 | Irreversible (one-way door) + a decision needed | Written decision record with a named approver |
| 3 | 8+ people and no decision to make | Broadcast |
| 4 | Low shared context + a decision needed | Live meeting with agenda and pre-read |
| 5 | Decision needed within 8 hours | Live meeting — faster than one async round trip |
| 6 | Everything else | Async thread |

Seniority of the requester never appears in this table. A VP wanting a meeting
is not a reason; a VP lacking context is (rank 4).

### Meeting verdicts — decisions per month is the test [PROVEN]

| Verdict | Trigger | Action |
|---------|---------|--------|
| **KEEP** | Produces decisions, has agenda and notes | Leave it alone |
| **TRIM** | Produces decisions but leaks structure | Fix the agenda or notes, or cut duration 25% |
| **ASYNC** | Under 1 decision/month, or 8+ people in a "working session" | Written update + comment window |
| **KILL** | Under 1 decision/month **and** no agenda | Cancel; announce the replacement channel |

Decisions per month is the best available proxy for value: countable, hard to
game without actually deciding things, and it correctly kills status meetings,
which produce zero decisions by design.

### Load and readability thresholds [RECOMMENDED]

| Metric | Healthy | Danger |
|--------|---------|--------|
| IC meeting hours per week | under 6h (15%) | over 10h (25%) |
| Uninterrupted maker hours per week | 24h+ | under 20h |
| Sync share of routed traffic | under 34% | over 50% |
| Status update length | under 400 words | over 600 words |
| Average sentence length | 18-22 words | over 28 words |
| Quantified claims per update | 3+ | 0 |

### Escalation

Acknowledgement is not resolution — "seen it, answer Thursday" fully satisfies
an acknowledge SLA and stops the requester re-pinging. Escalation is a **process
failure signal, not an interpersonal act**; say so in the charter, or the team
develops silent blockers, which cost far more than the discomfort they avoid.

The full SLA ladder by urgency band and the three-strike escalation rule are in
`references/channel-selection-and-meeting-load.md`; the charter template ships
them ready to fill in.

## Anti-Patterns

### Watermelon Status
**Mistake:** Reporting green week after week, then going red two weeks before the deadline.
**Why it happens:** Each individual week genuinely feels recoverable, and a yellow invites questions the author does not yet have answers to. Optimism compounds silently.
**Instead:** Go yellow the week a risk becomes plausible, not the week it becomes certain, and attach an owner and a mitigation date. One defensible red buys more credibility than a quarter of unearned greens — and the scorer's risk element exists precisely to force the disclosure.

### Cutting Meetings Without Installing the Written Channel
**Mistake:** Cancelling the status meeting and the alignment sync in the same week the audit lands, with nothing replacing them.
**Why it happens:** The audit makes the waste vivid and the cuts feel like the whole intervention. The written replacement is unglamorous and gets deferred.
**Instead:** Install the weekly written status **first**, run both for one cycle, then cancel. The meetings were carrying real information badly; removing the carrier before building a new one converts a load problem into a late-blocker problem, which is more expensive.

### Escalation Treated as Aggression
**Mistake:** A team where going to a manager about a blocker is read as tattling, so people wait and hint instead.
**Why it happens:** Nobody wrote down what escalation is for, so everyone infers it from the one time it went badly.
**Instead:** Write in the charter that escalation is a process failure signal, not an interpersonal act, and specify the three strikes by role. Making the ladder public converts strike 3 into a paperwork step rather than a confrontation, because the record already exists.

### Async Adopted Without Teaching Writing
**Mistake:** Declaring the team async-first, then watching decisions take two weeks and quietly reinstating the meetings.
**Why it happens:** Async is treated as a channel choice rather than a skill. High Slack volume is mistaken for async maturity, when it is often level-1 verbal culture conducted in writing.
**Instead:** Standardise the decision record shape — decision, approver, options with costs, consequences, comment deadline — before removing sync time. Escalate to a 20-minute call after two unresolved comment rounds, and post the outcome back into the doc.

### The Immortal Recurring Meeting
**Mistake:** A meeting created for a launch three years ago that still runs weekly with six attendees.
**Why it happens:** Nobody has standing to cancel someone else's meeting, and the original owner has left, so it has no one to defend or kill it.
**Instead:** Give every recurring meeting an expiry date 3-6 months out at creation, plus a named owner. At expiry it is re-justified or it dies by default. Where one already exists with no owner, trial-cancel it for four weeks and ask what broke — roughly two-thirds never come back.

## Files

| File | Purpose |
|------|---------|
| `scripts/meeting_load_auditor.py` | Person-hours, annual cost, KEEP/TRIM/ASYNC/KILL verdicts, double bookings, consolidation proposal |
| `scripts/channel_router.py` | Routes each message to sync / async / written decision / 1:1 / broadcast with reasons and an SLA |
| `scripts/status_update_scorer.py` | Scores a draft 0-100 on completeness, executive readability and skimmability |
| `references/channel-selection-and-meeting-load.md` | Routing model, cost arithmetic, verdict rubric, consolidation, timezone regimes, escalation ladder, status thresholds, instrumentation |
| `references/operating-rhythm-and-charter.md` | Six-ritual minimum rhythm, ritual design rules, async writing standards, channel taxonomy, maturity model, rollout sequence, failure modes |
| `assets/communication_charter_template.md` | One-page charter: core hours, channel and meeting rules, SLAs, escalation, decision protocol, timezone norms |
| `assets/status_update_template.md` | Update skeleton built for a 20-second executive skim |
| `assets/sample_calendar.json` | Runnable 8-person, 8-meeting calendar export |
| `assets/sample_messages.json` | Runnable set of 7 pending communications |
| `assets/sample_status_update.json` | Runnable mid-quality draft (scores 50 — REVISE) |
