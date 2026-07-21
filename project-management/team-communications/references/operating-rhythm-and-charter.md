# Operating Rhythm and Communication Charter

Deep reference for designing the recurring shape of a team's communication:
which rituals exist, at what cadence, in what format, and what a written
charter must pin down. Read this when standing up a new team, resetting a
team whose calendar has metastasised, or onboarding someone into an existing
rhythm.

---

## 1. The minimum viable operating rhythm

Most teams do not have a meeting problem. They have an **undesigned rhythm**
problem: rituals accreted one at a time, each solving a real problem, none
ever removed. Design the rhythm top-down instead and the calendar shrinks by
itself.

A delivery team of 5-9 people needs exactly these six rituals. Everything else
must justify its existence against them.

| Ritual | Cadence | Duration | Attendees | Format | Output |
|--------|---------|----------|-----------|--------|--------|
| **Daily sync** | Daily | 10-15 min | Delivery team only | Sync, or written for 3+ timezones | Blockers surfaced and owned |
| **Planning** | Per cycle (1-2 wks) | 45-60 min | Team + PM | Sync | Committed scope |
| **Working session** | Weekly | 60 min | 4-7 with the problem | Sync, agenda-driven | 3-6 decisions |
| **Written status** | Weekly | 0 min live | Broadcast to stakeholders | Async doc | Progress, risk, decision, ask |
| **Review / demo** | Per cycle | 30 min | Team + stakeholders | Sync, optional attendance | Feedback captured |
| **Retro** | Per cycle | 45 min | Delivery team only | Sync | 1-3 owned experiments |

Total: roughly **4-5 hours per person per week**, or 11% of a 40-hour week.
Any team above 10 hours has rituals outside this list that were never
designed — those are the audit targets.

### Rituals that should not exist as meetings [PROVEN]

| Ritual people hold | Why it fails as a meeting | Replace with |
|--------------------|---------------------------|--------------|
| Status roundup | Serial reporting; each person listens to 80% irrelevance | Written status doc |
| "Sync" with no agenda | Fills its allotted time regardless of content | Async thread; book time only when a decision stalls |
| Recurring stakeholder 1:1 with no topic | Manufactures topics to fill the slot | On-demand, plus a standing async channel |
| All-hands roadmap review | Broadcast dressed as a working session | Doc + optional 20-min Q&A |
| Post-mortem with 15 attendees | Blame dynamics scale with audience | 5-person write-up, broadcast the doc |
| Weekly "alignment" between two teams | Alignment is an artefact, not an event | Shared written decision log; meet on conflict |

---

## 2. Ritual design rules

### Every recurring meeting needs four things or it gets cancelled

1. **A named owner** who is accountable for it being worth the money. Not a
   rotating facilitator — a single owner.
2. **A standing agenda posted before it starts.** No agenda by start time is
   an automatic cancellation. This one rule removes more waste than any other,
   because it forces the owner to think about the meeting before the room fills.
3. **A written record** — decisions and actions, posted where absentees read
   it. If nothing was worth writing down, nothing was worth meeting about.
4. **An expiry date.** Every recurring meeting is created with a review date
   3-6 months out. At the review it must be re-justified or it dies. Meetings
   that never expire are how calendars reach 25 hours a week.

### Duration defaults [RECOMMENDED]

Default to **25 and 50 minutes**, not 30 and 60. The gap is not a nicety; it
is what lets someone in back-to-back meetings write the notes from the last
one, which is what makes the written record actually exist.

Meetings expand to fill the time booked. Book the time the agenda needs, not
the time the calendar tool defaults to. A three-item agenda is a 25-minute
meeting.

### The optional-attendance norm

Mark every attendee **required** or **optional**, and mean it. Optional means:
no consequence for declining, notes will cover you, nobody will re-explain in
the next meeting. Teams that mark everyone required teach people that the
marking is noise, and then the only safe move is to attend everything.

A useful forcing function: if more than 60% of a meeting's attendees are
optional, it is a broadcast. Convert it.

---

## 3. Async writing standards

Async only outperforms sync when the writing is good enough to prevent round
trips. Bad async is slower than a meeting, which is why teams that "went
async" without teaching writing quietly went back.

### Document types and when each applies

| Type | Length | Use when | Decision authority |
|------|--------|----------|--------------------|
| **Thread post** | under 200 words | Question, update, reversible call | Area owner decides |
| **Decision record** | 1 page | One-way door, or 3+ people disagree | Named approver, stated in the doc |
| **Design doc** | 2-6 pages | Non-trivial technical approach | Reviewers named; approver named |
| **Narrative memo** | 4-6 pages | Strategy, sequencing, funding | Read together, then discussed |
| **Status update** | under 400 words | Weekly stakeholder cadence | No decision; contains asks |

### The decision record shape [PROVEN]

A decision record that omits any of these will be re-litigated:

```
Decision      — one sentence, in the past tense, as if already made
Approver      — one name. Not a team.
Date + status — proposed / accepted / superseded by <link>
Context       — what forced a choice now
Options       — 2-4, each with its main cost. Include "do nothing".
Rationale     — why the chosen option, in terms of the context above
Consequences  — what this makes harder later; what we accept
Comment deadline — a date. Silence past it is consent.
```

The two fields teams skip are **Consequences** and **Approver**, and those are
precisely the two that matter eighteen months later when someone asks "who
decided this and did they know it would do that?"

### Comment discipline

- **Comment deadlines span a full working day in every participant timezone.**
  A 24-hour deadline posted at 17:00 UTC gives Asia-Pacific no working hours
  at all.
- **Silence past the deadline is consent** — but only if the deadline was
  announced in the doc and in the channel, and the doc was readable before the
  clock started.
- **Disagreement in comments escalates to sync after two round trips.** If two
  people have exchanged two rounds of comments without converging, the async
  channel has failed for that topic. Book 20 minutes. Post the outcome back
  into the doc.
- **Resolve threads by editing the doc**, not by replying "good point". A doc
  whose body still contradicts its comments is worse than no doc.

### Channel taxonomy

A flat channel list forces everyone to read everything. Structure it:

| Channel pattern | Contains | Expectation |
|-----------------|----------|-------------|
| `team-<name>` | Working traffic for one team | Members read daily |
| `proj-<name>` | One time-boxed project; archived on close | Participants read daily |
| `<domain>-help` | Inbound questions to a domain owner | Owner triages; SLA applies |
| `<team>-alerts` | Machine output only | No human conversation |
| `announce-<scope>` | Broadcast; posting restricted | Read weekly |

**No decisions in DMs, and no decisions in a private group.** [PROVEN] A
decision made where it cannot be found will be made again, differently, by
someone who could not find it. This is the single most common cause of
"we already decided this" arguments.

---

## 4. Notification and availability norms

Communication load is not only meetings. An engineer interrupted every 20
minutes has no maker time regardless of how empty the calendar looks.

| Norm | Rule |
|------|------|
| **Response expectation** | Nothing outside an incident requires a reply in under 2 working hours |
| **Off-hours** | Messages sent outside a recipient's working hours are scheduled, not sent |
| **@channel / @here** | Requires a stated reason; overuse is a charter violation, not a style preference |
| **Focus blocks** | Honoured like meetings — do not book over them, do not ping into them |
| **No-meeting day** | One full weekday, org-wide. Half-days fragment and fail. |
| **Vacation** | Covered by a named person, stated in the channel topic. Not "reachable if urgent". |

The off-hours rule matters more than it looks. A manager who sends at 22:00
"because it is convenient" teaches the team that 22:00 messages are normal,
and every scheduling tool has a send-later button that removes the cost
entirely.

---

## 5. The written charter

A communication charter is one page. Longer and nobody reads it, which means
it stops being a shared reference and becomes a document you point at during
arguments — the exact opposite of the point.

It must pin down, in order:

1. **Core hours** — the UTC window when all required participants overlap.
2. **Channel rules** — which of the five channels applies to what, in one
   table. Include "no decisions in DMs" explicitly.
3. **Meeting rules** — agenda-or-cancel, notes-required, 25/50 durations,
   required-vs-optional, expiry dates.
4. **Response SLAs** — by urgency band, with acknowledge and resolve times
   separated.
5. **Escalation path** — the three strikes, named by role not by person, plus
   the explicit statement that escalation is a process signal and not an
   attack.
6. **Decision protocol** — what needs a written record, who approves, what
   comment deadline applies, what silence means.
7. **Timezone norms** — rotation of unsociable slots, recording policy,
   handoff writing.
8. **Review date** — the charter itself expires. Six months.

Charters fail in one specific way: they are written once, at team formation,
by the person who cares most, and never revisited. Put the review date in the
document and on the calendar.

---

## 6. Communication maturity model

Use this to diagnose where a team actually is before proposing changes.
Proposing level-4 practices to a level-1 team produces compliance theatre.

| Level | Name | Symptoms | Next move |
|-------|------|----------|-----------|
| **1** | Verbal | Decisions live in people's heads; "ask Priya" is the retrieval mechanism; new joiners take 3 months to be useful | Start writing decisions down. Nothing else yet. |
| **2** | Documented | Decisions get written but inconsistently; docs exist but are not findable; meetings still carry most traffic | Standardise the decision record. Give docs one home. |
| **3** | Structured | Rituals designed, agendas standard, notes reliable, SLAs stated | Audit meeting load; push reversible decisions async |
| **4** | Async-first | Written by default; sync reserved for one-way doors, low context, and incidents; timezone-neutral | Optimise writing quality; reduce doc latency |
| **5** | Self-correcting | Team audits its own load quarterly; meetings expire; charter is revised, not just referenced | Maintain; resist regrowth |

Most delivery teams sit at level 2 and believe they are at level 4 because
they use Slack heavily. Slack volume is not async maturity — high message
volume with low document quality is level 1 conducted in writing.

### Diagnostic questions

Ask these before proposing any change. Each answer places the team on the model.

1. "Where is the decision about X written down?" — if the answer is a person,
   level 1.
2. "What happens if someone misses Tuesday's sync?" — if they fall behind,
   the meeting has no written record.
3. "How long until a new joiner can make a call without asking?" — over six
   weeks means the context is undocumented.
4. "When did you last cancel a recurring meeting?" — never means no expiry
   discipline.
5. "What is the response SLA on a blocking question?" — no answer means
   blockers sit until someone notices.

---

## 7. Rollout sequence for a rhythm reset [RECOMMENDED]

Changing how a team communicates fails when it arrives as an edict. This
sequence has the best odds:

1. **Week 0 — measure.** Run the meeting-load audit. Publish the numbers,
   including the annual dollar figure, without proposing anything yet.
2. **Week 1 — agree the problem.** Get explicit agreement that the number is
   too high before discussing any specific meeting. Skipping this turns every
   subsequent proposal into a defence of someone's meeting.
3. **Week 2 — cut the zero-decision meetings.** Start with the ones nobody
   defends. Early wins buy credibility for the contested cuts.
4. **Week 3 — install the written status.** This is what makes the cancelled
   status meetings survivable. Do it before, not after.
5. **Week 4 — write the charter** with the team, in one 50-minute session,
   from the decisions already made in weeks 2-3.
6. **Week 6 — merge the overlapping meetings** once the written channel has
   proven it works.
7. **Week 12 — re-audit.** Publish the delta. Expect 20-30% regrowth and cut
   it again; this is normal, not failure.

The two steps teams skip are 1 and 4 — measurement and the written artefact.
Without measurement the change is opinion versus opinion. Without the charter
the change decays as soon as the person driving it moves on.

### Handling the three predictable objections

Every rhythm reset meets the same three objections. Prepare the answers.

**"But we'll lose alignment."** Alignment is an artefact, not an event. What the
meeting was producing was a shared understanding that decayed until the next
one. A written decision log produces the same understanding and does not decay.
Offer the trial cancellation: four weeks, and if alignment measurably drops,
it comes back. It almost never does.

**"My stakeholders expect the meeting."** Usually true, and usually about
confidence rather than content. Replace it with a written update on the same
cadence plus a standing offer of time on demand. Stakeholders who wanted
information take the document; stakeholders who wanted reassurance take the
offer, and they take it perhaps twice a quarter.

**"It's only 30 minutes."** It is 30 minutes multiplied by attendees, multiplied
by 46 weeks, plus the focus block it fragments. Give the annual number. A
weekly 30-minute meeting with eight people at loaded rates costs roughly $46,000
a year, and nobody has ever approved a $46,000 line item with no owner and no
agenda.

---

## 8. Onboarding someone into the rhythm

A new joiner reveals the quality of a communication system faster than any
audit. What they struggle to find is what does not exist.

### Week one checklist

- [ ] Charter read, with the core hours and escalation path pointed out explicitly
- [ ] Added to `team-` and relevant `proj-` channels; shown which are broadcast-only
- [ ] Shown where decisions live, and asked to find one from six months ago unaided
- [ ] Walked through one past status update and told which parts drove action
- [ ] Told which recurring meetings are genuinely optional — and believed
- [ ] Given the name of who to escalate to, before they need it

### The six-week test

At six weeks, ask: *can this person make a decision in their area without asking
anyone?* If not, the blocker is nearly always undocumented context, not the
person's ramp. That is a level-1 or level-2 signal on the maturity model
regardless of how modern the tooling looks.

The second diagnostic: ask them what surprised them about how the team
communicates. New joiners lose this perception within about two months, so the
window is short and the answers are unusually honest.

---

## 9. Failure modes of the rhythm itself

| Failure | What it looks like | Root cause | Fix |
|---------|-------------------|------------|-----|
| **Ritual inflation** | Every problem produces a new recurring meeting | Meetings are the only intervention the team knows | Require every new recurring meeting to name one it replaces |
| **The shadow meeting** | The real decision happens in a DM before the meeting | The meeting has the wrong people, or is too large to be safe | Fix the invite list; make the pre-decision public |
| **Notes theatre** | Detailed notes nobody reads, no decisions extractable | Note-taking optimised for completeness over retrievability | Label decisions and actions explicitly; drop the transcript |
| **Async performativity** | Long docs written to demonstrate rigour, not to decide | Writing has become a status signal | Cap decision records at one page; require an approver and a deadline |
| **Charter drift** | The charter says one thing, the team does another | No review date; nobody owns it | Charter has an owner and a hard expiry |
| **Calendar defence** | Focus blocks booked over routinely | Blocks are treated as preferences, not commitments | Leadership declines the override publicly, once — that is usually enough |

**Ritual inflation is the default state.** Absent a rule, a team's calendar
grows monotonically, because adding a meeting solves a visible problem now and
removing one solves a diffuse problem later. The "name what it replaces" rule
is the cheapest available brake, and it works because it forces the sponsor to
think about the calendar as a fixed budget rather than an open field.
