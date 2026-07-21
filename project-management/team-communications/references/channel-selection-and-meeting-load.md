# Channel Selection and Meeting Load

Deep reference for choosing a communication channel, and for auditing and
reducing a team's meeting load. Read this when designing a team communication
charter, running a meeting audit, or arbitrating a "should this be a meeting?"
dispute.

---

## 1. The routing model

Every internal communication is one of five things. Naming which one it is
resolves most channel arguments before they start.

| Channel | What it is for | Durable record | Latency |
|---------|----------------|----------------|---------|
| **Written decision record** | An irreversible or expensive choice needing a named approver | Required | 2-5 days |
| **Async thread** | Reversible choices, questions, and progress among people with shared context | Searchable by default | 4-24 hours |
| **Live meeting** | Low shared context, high disagreement, or a same-day decision | Notes required | Minutes |
| **Live 1:1** | Performance, compensation, conflict, anything with emotional load | Private, no notes distributed | Minutes |
| **Broadcast** | Information going one direction to a large audience | Required | N/A |

### The four routing variables [PROVEN]

Rank them in this order. The first one that fires decides the channel.

1. **Emotional load.** Anything about a person's standing — promotion, pay,
   performance, a decision that reads as a demotion — goes to a live 1:1.
   Text strips tone and the recipient supplies the worst available reading.
   This rule has no exceptions worth taking.
2. **Reversibility.** Bezos's one-way / two-way door distinction. One-way doors
   (schema migrations, pricing changes, public API contracts, org structure)
   need a written record with a named approver, because in eighteen months
   someone will ask why. Two-way doors default to async and get decided by
   whoever owns the area.
3. **Shared context.** Async is a bandwidth trade: it costs round trips but
   returns durable text. When participants do not share the vocabulary, an
   async thread burns four round trips discovering that two people meant
   different things by "settlement." Low context plus a decision means meet.
4. **Urgency versus round-trip cost.** One async round trip across three
   timezones costs roughly 18 hours of wall clock. If the decision is needed
   in less time than that, the meeting is cheaper than the delay — even
   counting the interruption.

### What does *not* determine the channel

- **Seniority of the requester.** A VP wanting a meeting is not a reason;
  a VP lacking context is.
- **Topic importance.** Important and irreversible are different axes. The
  most important decisions often deserve a document precisely *because* they
  are important enough to be re-litigated later.
- **How long it has been since the team last talked.** That is a case for a
  social ritual, booked as one, not for converting working sessions into
  chatting.

---

## 2. Meeting load: the arithmetic

### Cost model

```
weekly person-hours = (duration_min / 60) x occurrences_per_week x attendees
weekly cost         = (duration_min / 60) x occurrences_per_week x SUM(attendee hourly cost)
annual cost         = weekly cost x 46      # 46 productive weeks after holiday and leave
```

Use **fully loaded** hourly cost (salary + employer tax + benefits + overhead),
typically 1.25-1.4x base salary divided by 1,880 working hours. A meeting
priced with base salary alone understates by 30-40% and the audit loses its
teeth exactly where it needs them.

### Load thresholds [RECOMMENDED]

| Weekly meeting hours | Share of week | Diagnosis |
|----------------------|---------------|-----------|
| 0-6h | under 15% | Healthy for an IC |
| 6-10h | 15-25% | Ceiling for makers; watch fragmentation |
| 10-16h | 25-40% | Normal for a manager; fatal for an IC |
| 16h+ | over 40% | Nobody at this level is doing deep work |

The raw hours understate the damage. A 30-minute meeting at 11:00 does not
cost 30 minutes — it costs the two-hour block it splits. Track **maker hours**
(the longest uninterrupted stretches remaining) alongside total meeting hours.
A person with 8 meeting hours arranged as eight separate 1-hour slots has less
usable focus time than a person with 12 hours stacked into two afternoons.

### The 24-hour maker-time target

Each IC needs **at least 24 uninterrupted hours per week**, in blocks of 2+
hours, to do work that requires holding a system in their head. Below that,
throughput falls faster than the hours removed, because every re-entry costs
15-25 minutes of reload.

---

## 3. The meeting verdict rubric

Score each recurring meeting on four questions, then assign a verdict.

| Question | Weight |
|----------|--------|
| Does it have a standing written agenda posted before the meeting? | Structural |
| Are notes and decisions written down where absentees can read them? | Structural |
| How many decisions did the series produce in the last month? | Output |
| Is the attendee count consistent with its stated type? | Design |

| Verdict | Trigger | Action |
|---------|---------|--------|
| **KEEP** | Produces decisions, has agenda and notes | Leave it alone |
| **TRIM** | Produces decisions but leaks structure | Fix the agenda or notes, or cut duration 25% |
| **ASYNC** | Under 1 decision/month, or 8+ people in a "working session" | Convert to a written update with a comment window |
| **KILL** | Under 1 decision/month *and* no agenda | Cancel; announce the replacement channel |

**Decisions per month is the single best proxy for meeting value.** [PROVEN]
It is countable, hard to game without actually deciding things, and it
correctly kills status meetings — which produce zero decisions by design and
should therefore be written documents.

### Attendee-count design rules

| Purpose | Right size | Failure mode above it |
|---------|-----------|-----------------------|
| Decision | 3-5 | Diffusion of responsibility; nobody owns the call |
| Working session | 4-7 | Turns into serial reporting |
| Brainstorm | 5-8 | Loudest voice sets the frame |
| Broadcast | any | None — but then it should not be interactive |

Anything with 8+ attendees and no explicit broadcast label is a broadcast that
has not admitted it. Convert it: send the document, hold a 20-minute optional
Q&A, and give the other 7.5 hours back.

---

## 4. Consolidation

Two recurring meetings are merge candidates when their attendee sets overlap
**60% or more** (Jaccard: shared attendees over the union) and they share a
type. Below 60%, merging just forces half of each room to sit through the
other half's business.

The consolidation sequence that survives contact with a team:

1. **Measure first, propose second.** Show the annual dollar figure. "This
   calendar costs $170K a year" moves people that "we have too many meetings"
   never will.
2. **Cancel the zero-decision meetings outright.** Do not shrink them. A
   30-minute meeting that produces nothing is still a calendar fragment.
3. **Merge the 60%+ overlaps** into one longer session with a segmented
   agenda, and let people leave after their segment.
4. **Declare a no-meeting block** — one full day or two half-days — and defend
   it as an org norm, not a personal preference.
5. **Re-audit in six weeks.** Meeting load regrows; every cancelled meeting
   has a sponsor who will try again.

### The trial-cancellation technique [RECOMMENDED]

Do not debate whether a meeting is valuable. Cancel it for four weeks and ask
what broke. Roughly two-thirds never come back. The remaining third come back
smaller and shorter, because the sponsor now has to justify each invite. This
converts an unwinnable opinion argument into a cheap experiment.

---

## 5. Cross-timezone norms

### Core overlap

**Core overlap** is the number of hours all required participants are awake and
working. Design against it explicitly.

| Overlap | Regime | Rules |
|---------|--------|-------|
| 5h+ | Co-located rhythm | Sync is affordable; still write decisions down |
| 3-5h | Hybrid | Protect overlap for decisions only; all status is written |
| 1-3h | Async-first | Sync only for one-way doors and incidents; rotate the pain |
| under 1h | Fully async | Sync is an escalation, never a routine |

### Rules that hold in every regime [PROVEN]

- **Rotate the unsociable slot.** If one region always takes the 22:00 call,
  that region churns. Rotate quarterly and publish the rotation.
- **Never let a decision depend on presence.** Post the decision, name the
  approver, set a comment deadline of one full working day *for every
  timezone*. Silence past the deadline is consent — but only if the deadline
  genuinely spanned everyone's working day.
- **Write the handoff.** The last person in a timezone writes what they
  finished, what is blocked, and what the next region should pick up. This is
  the single highest-value async ritual in a follow-the-sun team.
- **Record and transcribe every sync that anyone missed.** A meeting a region
  could not attend, with no artefact, is an information tax on that region.
- **Time-stamp in UTC in writing, and never in a relative form.** "Tomorrow
  morning" is meaningless across a date line.

---

## 6. Escalation paths and SLAs

An escalation path exists so that a blocked person knows exactly who to
interrupt and when — without it, blockers sit silently until a status meeting
surfaces them days later.

### Response SLA ladder [RECOMMENDED]

| Urgency band | Definition | Acknowledge | Resolve | Escalate if breached |
|--------------|-----------|-------------|---------|----------------------|
| **P0 — incident** | Customer-facing outage or data loss | 15 min | Until resolved | Immediately, to on-call lead |
| **Same-day** | Blocks someone's work today | 2 working hours | Same day | End of day, to owning manager |
| **This-week** | Blocks work this sprint | 1 working day | 3 working days | Day 4, to owning manager |
| **Scheduled** | Planning, review, non-blocking | 3 working days | Next planning cycle | Day 5, raise in planning |

Acknowledgement is not resolution. "Seen this, answer by Thursday" fully
satisfies the acknowledge SLA and stops the requester from re-pinging.

### The three-strike escalation rule

1. **Strike 1 — ask the owner directly**, in the channel where the work lives,
   with a stated deadline. Not DM: DMs hide the request from anyone who could
   have answered it faster.
2. **Strike 2 — restate publicly with the cost**, after the SLA lapses: what
   is blocked, how much it is costing, what you need. Tag the owner and their
   manager.
3. **Strike 3 — escalate to the shared manager** with a written summary of
   strikes 1 and 2. By this point the escalation is a paperwork exercise, not
   a confrontation, because the record is already public.

Escalation is a **process failure signal, not an interpersonal act**. Teams
that treat escalation as aggression develop silent blockers, which cost far
more than the discomfort they avoid. Say this out loud in the charter.

---

## 7. Status updates that survive being skimmed

An executive reads your update in 20-40 seconds, on a phone, between two other
meetings. Everything below follows from that.

### The four load-bearing elements

Every update must contain all four. An update missing one is a broken artefact.

| Element | The question it answers | Failure mode when missing |
|---------|------------------------|---------------------------|
| **Progress** | What actually moved, with a number | Reads as activity, not outcomes |
| **Risk** | What could stop us, who owns it | Silence is read as "all fine"; the surprise lands later at 3x the cost |
| **Decision needed** | What choice are you asking them to make | The reader has no reason to engage |
| **Ask** | What specific help do you need, by when | The update is filed, not acted on |

If there genuinely is no decision or ask this period, **write "No decisions
needed this week"** explicitly. The reader cannot distinguish absence from
omission.

### Readability thresholds [PROVEN]

| Metric | Target | Why |
|--------|--------|-----|
| Verdict in the first sentence | Always | Skimmers read sentence one and the bold text |
| Average sentence length | 18-22 words | Above 28 words comprehension falls sharply on mobile |
| Quantified claims | 3+ | "Good progress" and "no progress" are textually identical |
| Longest paragraph | under 80 words | Longer blocks get skipped entirely |
| Total length | under 400 words | Beyond this you are writing for yourself |
| Named sections | 3+ | Lets a reader jump to the part they own |

### Language to delete

- **Hedges** — "somewhat", "mostly", "should be fine", "hopefully", "we think",
  "on track-ish". Each one asks the reader to guess your confidence. State the
  position, or state the unknown and who is closing it.
- **Jargon** — "leverage", "synergy", "circle back", "bandwidth", "double
  down". Replace with the concrete thing that happened.
- **Watermelon status** — green on the outside, red inside. The most expensive
  failure mode in status reporting, because it destroys the reader's ability to
  trust any future green. A single defensible red buys more credibility than a
  quarter of unearned greens.

### The structure that works

```
Verdict line       — GREEN / YELLOW / RED, plus one clause of why
Progress           — 2-4 bullets, each with a number
Risks              — top 2 only, each with owner and mitigation date
Decisions needed   — the choice, the options, your recommendation, the deadline
Asks               — one line each, named person, named date
Next               — 2-3 bullets
```

Two risks, not seven. A list of seven risks tells the reader you have not
prioritised, and they will assume none of them are real.

### Tailoring by audience

The four elements are constant; their weighting is not.

| Audience | Leads with | Wants | Cut |
|----------|-----------|-------|-----|
| **Sponsor / VP** | Verdict + the ask | Decisions they must make, risks to their commitments | Implementation detail, ticket names |
| **Board** | Trajectory against the plan | Trend across periods, material risk, capital implications | Weekly variance, individual names |
| **Peer teams** | What changed that affects them | Interface changes, dependency dates, blockers they own | Internal politics, your risk register |
| **Own team** | What we learned | Context behind decisions, what shifts next period | Executive framing, dollar figures |

The most common error is sending the exec version to the team, which reads as
corporate and tells them nothing they can act on, or the team version to an
exec, which buries the ask under implementation detail.

### The five-second test

Before sending, read only the first sentence, the bold text and the section
headings. If that subset does not convey the verdict, the top risk and the ask,
the update fails — a large share of your readers will see nothing else.

---

## 8. Instrumenting the system

A communication system that is never measured regrows its meeting load within
two quarters. Four measurements, taken quarterly, are enough.

| Measure | Source | Healthy trend |
|---------|--------|---------------|
| Weekly meeting person-hours per IC | Calendar export | Flat or falling |
| Annualised recurring-meeting cost | Calendar export + loaded rates | Falling per head |
| Median status-update score | Update scorer, kept over time | 75+, stable |
| Blocker latency | Time from a blocker existing to it being raised | Under one working day |

**Blocker latency is the outcome measure.** Meeting load and update quality are
inputs; what the system exists to produce is problems surfacing fast. A team
that cut meetings 30% and whose blocker latency went from one day to four made
things worse, and only this measure would have shown it.

Measure it crudely: at the next retro, take the three most recent blockers and
ask when each was first known versus when it was first raised. The gap is the
number. Precision is unnecessary — the difference between one day and four is
the finding, and no instrumentation is needed to see it.

### Regrowth

Expect **20-30% meeting regrowth within six weeks** of any reduction. This is
not failure and not backsliding; it is individual people solving individual
coordination problems the only way they have available. Budget for a second
cut, and put the re-audit on the calendar at the same time as the first one.
The teams that hold their reductions are the ones that scheduled the re-audit
before they needed it.
