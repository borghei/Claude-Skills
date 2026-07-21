# Defending Focus Time

Blocking time is easy and nearly worthless on its own. The work is defending
the block against a steady, well-intentioned stream of encroachment — and doing
it without acquiring a reputation for being unavailable.

---

## 1. How encroachment actually happens

Focus time is rarely destroyed by one big meeting. It is eroded by a sequence of
individually reasonable requests, none of which feels worth refusing:

1. **The scheduling-tool default.** Free/busy shows your block as free (or as a
   low-stakes "focus" event others feel comfortable overriding), so meetings
   land in it automatically.
2. **The 30-minute wedge.** A short meeting drops into the middle of a
   120-minute block. Nominally you lose 30 minutes; actually you lose the block,
   because two 45-minute halves are below the viable threshold.
3. **The polite ask.** "I know you have something, but this is the only time
   everyone can make." Refusing feels obstructive, so you move the block — and
   a block that moves weekly is not a block.
4. **Self-encroachment.** You schedule your own admin into it because it is the
   only free space you can see. This is the most common cause and the least
   discussed.
5. **Slow creep.** The block shrinks 15 minutes at a time as adjacent meetings
   run long, until it is 45 minutes and silently useless.

**The 30-minute wedge is the highest-cost pattern and the one people concede
most readily**, because the arithmetic of block splitting is invisible. Losing
30 minutes from a 120-minute block does not cost 30 minutes — it costs the
entire block.

---

## 2. Calendar mechanics that work

Ranked by effectiveness per unit of social cost.

### [PROVEN] Make the block look like a real meeting

Give it a specific name (`Migration RFC — drafting`), not `Focus time` or
`DNS`. Named work reads as a commitment to something; generic focus blocks read
as availability with a preference attached. Set it busy, not free, and make it
recurring rather than added weekly.

### [PROVEN] Put the block at a boundary, not in the middle

A block from 09:00-11:00 has one exposed edge. A block from 11:00-13:00 has two,
and meetings collect on both. Where you have a choice, place deep work at the
start or end of the working day so encroachment can only come from one side.

### [RECOMMENDED] Consolidate meetings rather than spreading them

The same five meetings arranged as one dense afternoon versus scattered across
the week produce completely different amounts of usable focus time. Two meetings
placed at 10:00 and 15:00 destroy more of a day than four meetings stacked
13:00-15:00.

`calendar_fragmentation.py` searches single-meeting moves and reports the one
that buys back the most contiguous time. Run it weekly on the coming week and
make the one move it proposes — one move per week is politically sustainable in
a way that a wholesale calendar rewrite is not.

### [RECOMMENDED] Declare meeting-free hours at team level

A team-wide no-meeting window (typically mornings, or one full day) is far more
durable than individual blocks, because it removes the per-instance negotiation
entirely. It requires a manager's endorsement, which is exactly why it is worth
proposing with fragmentation data rather than as a preference.

### [EXPERIMENTAL] Publish office hours as the release valve

Two fixed 45-minute windows per week for anything that would otherwise become an
ad-hoc meeting. This works well when your interruptions are mostly requests for
your time, and poorly when they are genuine incidents. **Risk:** if you do not
staff the office hours reliably, people learn to route around them and
interrupt anyway — worse than not offering them.

---

## 3. Declining and moving, in words

Three sentences carry almost all of the load. State the constraint, offer a real
alternative, and skip the apology — apologising invites negotiation.

| Situation | What to say |
|---|---|
| Meeting lands in the block | "I have committed work in that slot. I can do 13:00 or 13:30 the same day — either works." |
| Recurring meeting eats the block | "This series overlaps my drafting block. Could we move it 30 minutes later, or should I send notes and skip?" |
| The 30-minute wedge | "That would split my only long block this week. Can we put it against the 11:00 meeting so the morning stays whole?" |
| Genuinely unavoidable | Move the block, do not delete it — and move it the same day, not to "sometime this week," which means never. |
| Someone asks you to move it repeatedly | "I have moved this three weeks running and the work has not progressed. I need to keep Thursday morning fixed." |

**The asymmetry worth understanding:** the person scheduling has one slot to
fill and no visibility into what they are displacing. They are not overriding
your priorities; they cannot see them. Naming the cost concretely — "that splits
my only long block this week" — converts an invisible cost into a visible
tradeoff, and most people adjust once it is visible.

---

## 4. Defending against yourself

Self-encroachment is the largest single source of lost focus time, and no
calendar convention protects against it.

| Self-encroachment | Countermeasure |
|---|---|
| Scheduling admin into the block because it looks free | Keep a separate, explicitly named admin block; admin expands to fill deep-work time if allowed |
| Starting with "quick" inbox triage | Inbox before a block is the single most reliable way to lose it — one message reframes the whole session |
| Working on whatever feels urgent that morning | Pre-commit the artefact the night before; do not renegotiate inside the block |
| Extending the block instead of stopping | Past the daily ceiling, output quality falls enough that the extra hour usually needs redoing |
| Treating the block as flexible because it is self-imposed | Only you can devalue it — every self-cancellation makes the next one easier |

---

## 5. Role-calibrated targets

The right deep-work ratio is not universal. Applying an IC target to a manager
produces guaranteed failure and, usually, abandonment of the practice.

| Role | Realistic deep-work ratio | Notes |
|---|---|---|
| IC, individual output (engineer, writer, analyst, designer) | 40-60% | Below 40% the role is misconfigured, not the calendar |
| Senior IC / tech lead | 30-40% | Coordination is genuine work; the ratio is lower by design |
| Team manager | 20-30% | Meetings are the job; protect two blocks a week, not two a day |
| Director and above | 10-20% | Deep work happens in defended pockets, often outside standard hours |
| On-call / support rotation | 0-10% during rotation | Do not schedule deep work into a rotation; it fails and teaches you the habit does not work |

Feed the row you occupy to `calendar_fragmentation.py --target`. The default of
0.40 is the IC figure and will flag almost every manager's calendar as failing,
which is noise rather than signal.

---

## 6. Interruption budgeting

An interruption budget is a number you decide in advance, not a hope.

**Setting the budget:**

1. Measure the current rate — log interruptions for two weeks without changing
   anything. Most people guess low by roughly half.
2. Set the budget one step below the current rate, not at zero. Zero is
   unachievable in most roles and failing it immediately kills the practice.
3. Define what happens when the budget is exceeded: **reschedule the block
   rather than pushing through**. Pushing through teaches you that protected
   time yields shallow work, which is the belief you are trying to disprove.

**Reducing the rate, in order of payoff:**

| Action | Typical reduction | Cost |
|---|---|---|
| Close chat entirely (not "away" — closed) | 40-60% | Requires one team conversation about response expectations |
| Phone in another room | 20-30% | None |
| Notifications off at OS level during the block | 15-25% | Occasional missed genuine urgency |
| Physical relocation | 30-50% | Not always available |
| Advance notice of the block to your immediate team | 10-20% | One message, weekly |

**The response-time conversation is worth having explicitly.** Most teams have
never stated their real expectation and default to an imagined one that is far
more aggressive than anyone actually needs. "I check chat at 11:00, 14:00, and
16:30; for anything genuinely urgent, call me" is almost always accepted without
objection — and it is the single highest-leverage sentence in this document.

---

## 7. Making the case with data

When you need to argue for protected time — to a manager, or to a team — bring
the numbers rather than the preference.

1. Export two to four weeks of calendar and run `calendar_fragmentation.py`.
2. Lead with the **recovery cost** figure. "Meetings consume 9 hours a week"
   invites debate about whether the meetings are necessary. "Fragmentation costs
   an additional 6 hours a week in re-immersion time, on top of the meetings
   themselves" reframes it as waste rather than as a priority dispute.
3. Show the days with zero viable blocks. A week with no 90-minute block is a
   week in which no substantive individual work occurred, whatever the output
   log suggests.
4. Propose the specific single move the tool identifies — not "fewer meetings."
   A concrete, small, reversible ask gets agreed; a general one gets sympathy.
5. Re-run after four weeks and report the delta. The follow-up measurement is
   what converts a one-off concession into a durable arrangement.

---

## 8. Meeting hygiene that buys back time

Fragmentation is downstream of meeting culture. Five changes, ranked by hours
recovered per unit of political capital spent.

### [PROVEN] Default to 25 and 50 minutes

Meetings expand to their scheduled length regardless of content. Shortening the
default recovers 10-20% of total meeting time and, more importantly, creates the
buffer that stops meetings from bleeding into adjacent blocks. Most calendar
tools support this as a one-time account setting — the highest ratio of hours
recovered to effort spent available anywhere in this document.

### [PROVEN] Audit recurring meetings quarterly

Recurring meetings are created for a reason and outlive it silently, because
nobody owns cancelling them. Every quarter, for each recurring meeting:

- What decision does this produce? If none, it is a status update — a written
  update serves the same purpose at a fraction of the cost.
- Would anyone notice if it stopped? Test by cancelling for three weeks rather
  than debating it; the empirical answer arrives faster than the argument.
- Does it need everyone? Attendance is the most reversible dimension and the
  least defended.

**Cancel one recurring meeting per quarter as a standing rule.** Meetings
accumulate monotonically otherwise: each is added for a reason, none is
individually worth the awkwardness of removing.

### [RECOMMENDED] Require an agenda or decline

A meeting with no stated purpose cannot be prepared for and usually produces no
decision. Declining with "happy to join — what decision are we making?" is
received far better than a flat decline, and roughly half the time it converts
the meeting into an email.

### [RECOMMENDED] Batch your own meetings

When you must schedule something, place it adjacent to an existing meeting
rather than in open space. This is entirely within your control, requires no
one's agreement, and is the single most effective anti-fragmentation habit
available to an individual.

### [EXPERIMENTAL] Asynchronous decision documents

Replace recurring decision meetings with a written proposal, a comment window,
and a short synchronous session only for unresolved points. **Risk:** requires
genuine team discipline about reading before commenting; without it you get the
document *and* the meeting, which is worse than either alone.

---

## 9. Remote, hybrid, and open-plan

The defence problem differs by environment, and applying the wrong tactics
wastes effort.

### Remote

Fewer physical interruptions, but chat expectations are typically more
aggressive because presence is inferred from responsiveness.

| Tactic | Notes |
|---|---|
| Status message with a return time | "Heads down until 11:30" — far more effective than a generic away indicator, because it answers the question the other person actually has |
| Close chat, do not minimise it | Minimised chat still generates badge counts, and a badge count is an interruption |
| Agree explicit response-time expectations | The highest-leverage conversation available; most teams have never stated theirs |
| Separate urgent channel | A phone call for genuine urgency makes closing chat safe rather than reckless |

**The trap in remote work is presence signalling** — staying responsive to
demonstrate you are working. It reliably destroys deep work, and it substitutes
a proxy for the output that would actually demonstrate it.

### Open-plan office

The hardest environment; physical interruption is cheap for the interrupter and
expensive for you.

| Tactic | Effectiveness |
|---|---|
| Relocate — a booth, an empty room, a library | Highest by a wide margin. Everything else is a partial mitigation |
| Headphones as a visible signal | Moderate, and only if the team has agreed what they mean |
| A physical do-not-disturb marker | Moderate; works when the team has bought into the convention |
| Facing away from the walkway | Small but free |
| Working from home on deep-work days | High where policy allows it |

**[RECOMMENDED] If your role requires substantial deep work and you sit
open-plan, relocation is the intervention.** Signalling tactics reduce
interruptions by perhaps 20%; relocating reduces them by 80%+. Negotiating for
that is a better use of political capital than negotiating individual meetings.

### Hybrid

The specific hazard is that office days fill with meetings *because* you are
there, leaving home days for real work — which is fine if deliberate, and
destructive if it happens by default and your deep work lands on days you are
also handling domestic interruptions. Decide it explicitly rather than letting
the calendar decide.

---

## 10. Defending time as a manager

Managers face the inverse problem: their calendar is legitimately full of other
people's needs, and the standard advice — block time, decline meetings — reads
as neglecting the job.

### What actually works

| Tactic | Why it fits the role |
|---|---|
| **Two blocks a week, not two a day** | Realistic; a manager's deep work is episodic — strategy documents, performance reviews, planning |
| **Batch 1:1s onto one or two days** | Preserves whole days elsewhere; 1:1s scattered across five days destroy all five |
| **Protect the same slot weekly and tell the team why** | Modelling matters more than the hours: a team whose manager visibly protects focus time protects their own |
| **Delegate the meeting, not just the work** | Sending someone else to represent the team develops them and returns the hour |
| **Office hours instead of ad-hoc availability** | Concentrates interruption into a known window |

**Do not apply IC targets to a management calendar.** A 40% deep-work target on
a manager's week is not achievable and produces a weekly experience of failure,
which ends the practice within a month. Use 20-30%, and set
`calendar_fragmentation.py --target 0.25`.

### The signal a manager sends

A manager who never protects focus time teaches the team that focus time is not
legitimate — no matter what they say about it. This is the strongest argument
for a manager maintaining the practice even at low volume: the modelling effect
on the team usually exceeds the personal output gained.

---

## 11. A four-week defence programme

Do not attempt all of this at once. One change per week, measured.

| Week | Change | Measure |
|---|---|---|
| 1 | Baseline only — change nothing, run `calendar_fragmentation.py` on the past two weeks | Current deep-work ratio, longest blocks, recovery cost |
| 2 | Set meeting defaults to 25/50 min. Schedule your own meetings adjacent to existing ones | Re-run; expect a small ratio improvement |
| 3 | Name and protect one recurring block at a day boundary. Tell your immediate team | Count how many times it was encroached |
| 4 | Make the one move the tool proposes each week. Have the response-time conversation | Re-run; compare against the week-1 baseline |

**Expected result: a 10-20 percentage point improvement in deep-work ratio over
four weeks**, most of it from meeting defaults and adjacency batching rather
than from declining anything. This matters politically — the largest gains come
from changes nobody has to agree to, which means you can demonstrate results
before asking anyone for a concession.

After four weeks, re-measure and decide whether the remaining gap is a calendar
problem or a role problem. If your role genuinely requires more coordination
than your target allows, the honest conclusion is to change the target rather
than continue failing against it — an unreachable target abandoned in month two
is worth less than a modest one held for a year.
