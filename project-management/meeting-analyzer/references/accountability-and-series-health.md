# Accountability and Meeting-Series Health

The models behind commitment tracking and recurring-meeting diagnosis: the
lifecycle an action item moves through, the benchmarks that separate a healthy
register from a decorative one, and how to tell a meeting that decides things
from one that discusses them. Read this when interpreting tracker output, when
follow-through is poor, or when deciding whether to cancel a recurring meeting.

---

## 1. The commitment lifecycle

An action item passes through five states. Most registers only model three, and
the two they skip are where the failures live.

| State | Definition | Failure at this state |
|-------|-----------|-----------------------|
| **Stated** | Said aloud in a meeting | Never written down; exists only in memory |
| **Recorded** | Written with text, owner, date | Recorded without an owner or date — the dominant failure |
| **Accepted** | The owner has acknowledged it | Assigned to someone absent, who never agreed |
| **In progress** | Work has started | Sits at "accepted" for weeks; nobody notices |
| **Closed** | Done, dropped, or explicitly reassigned | Silently abandoned instead of explicitly dropped |

**Accepted is the state teams skip.** Assigning an action to someone who was not
in the room, or who did not verbally take it, produces an item that will not
move and will not be escalated, because the assigner believes it is handled.
Rule: an action assigned to an absent person is provisional until they confirm,
and the register should show it as such.

**Closed includes dropped.** An action the team consciously decides not to do is
closed, not deleted. Deleting it destroys the signal that the meeting generated
work nobody valued — which is exactly the signal the series diagnostic needs.

---

## 2. The two accountability gaps

Every incomplete action has one of two gaps, and they fail differently.

### No owner

"The team will document the metric definitions." Nobody's name is on it, so
nobody's week is affected by it. Diffusion of responsibility is not a character
failing; it is the predictable result of a plural subject.

**Fix at capture time, not at review time.** The note-taker asks "who?" in the
room. Asking a week later means reconstructing a conversation nobody remembers,
and the answer is usually whoever feels most guilty rather than whoever is
right.

### No date, or a vague one

"Lena will produce the breakdown soon." The owner is real; the deadline is not.
Vague dates are worse than absent ones because the owner believes they have
committed, and the requester believes they have received a commitment, and the
two beliefs are about different weeks.

**Ban the vague-date vocabulary explicitly:** soon, ASAP, next sprint, when I
get a chance, in the next few days, eventually. Each has a real date behind it
that the owner is avoiding saying out loud — usually because they are not sure
they can hit it, which is itself the information the room needs.

---

## 3. Follow-through benchmarks [RECOMMENDED]

| Metric | Healthy | Warning | Broken |
|--------|---------|---------|--------|
| Completion rate (closed / total) | 75%+ | 50-75% | under 50% |
| Actions with owner **and** date | 90%+ | 70-90% | under 70% |
| On-time closure (closed by due date) | 70%+ | 50-70% | under 50% |
| Open actions older than 30 days | 0-1 | 2-4 | 5+ |
| Average carry-over count | under 1 | 1-2 | 3+ |

**Completion rate below 50% means the meeting is producing intentions, not
commitments.** At that level the register has stopped being a tracking tool and
become a record of good intentions, which nobody reads and everybody stops
adding to. The recovery is not exhortation — it is cutting the number of
actions the meeting is allowed to generate.

### Carry-over is the leading indicator

Carry-over — the number of times an action has been rolled into the next
meeting without progress — predicts abandonment better than age does. An item
carried three times has usually been silently deprioritised by its owner but
never formally dropped, so it keeps consuming review minutes.

**The three-strike rule:** at the third carry-over, the item is either
re-committed with a new date **stated out loud by the owner**, or explicitly
dropped. It does not get a fourth. This one rule reclaims more review time than
any other change to the ritual.

---

## 4. Reading per-owner data without weaponising it

Per-owner follow-through is the most misusable output in this skill. Low
follow-through has four common causes and only one of them is the person.

| Signal | Likely cause | Response |
|--------|--------------|----------|
| One owner holds 40%+ of open actions | Over-assignment, not under-delivery | Redistribute; the room is defaulting to the reliable person |
| High completion, low on-time | Deadlines set by others, not the owner | Have the owner state the date in the room |
| Many `blocked` items | Dependency the owner cannot clear | Escalate the dependency, not the person |
| Low completion across every owner | The meeting generates more actions than the team has capacity for | Cap actions per meeting |

**When every owner looks bad, the meeting is the problem.** A register where
nobody clears their items is describing a capacity mismatch. Treating it as
eight simultaneous performance issues is both wrong and expensive.

Use the data in aggregate with the team, and per-person only in a 1:1 — and
then as a question, not a verdict.

---

## 5. Decision density

**Decision density = decisions produced / person-hours consumed.**

It is the best single measure of whether a recurring meeting earns its cost.
Decisions are countable, hard to inflate without actually deciding something,
and directly connected to why synchronous time is expensive: the whole reason to
put people in a room simultaneously is to converge.

| Density | Reading |
|---------|---------|
| 0.35+ | Healthy — a 60-minute meeting with 5 people produces 2+ decisions |
| 0.15-0.35 | Inefficient — real decisions, too much time or too many people |
| under 0.15 | Below the floor — this is a broadcast or a discussion group |

**What density does not measure.** Brainstorms, incident reviews, retros and
onboarding sessions legitimately produce few decisions and should be excluded
rather than scored badly. Exclude them explicitly; do not lower the floor to
accommodate them, or the floor stops flagging the status meetings it exists to
catch.

### The three diagnoses of a low-density series

1. **Wrong people.** The room lacks whoever can actually decide, so every thread
   ends in "let's take that away". Fix: shrink to the decision owner plus the
   people whose input changes the decision.
2. **Wrong format.** The content is status. Fix: convert to a written update
   with a comment window.
3. **Wrong preparation.** No agenda and no pre-read, so half the time is spent
   loading context. Fix: agenda-or-cancel, plus a pre-read circulated 24 hours
   ahead.

---

## 6. Topic churn

A topic that recurs on the agenda without ever resolving is the clearest signal
that a meeting is substituting discussion for decision.

**Detection heuristic:** a topic is churning when it has appeared 3+ times and
fewer than a third of those appearances coincided with any decision. Since notes
rarely attribute decisions to specific topics, same-occurrence decisions are the
available proxy — treat the output as a shortlist to inspect, not a verdict.

Churn has three causes, distinguishable by asking one question — *who can
actually decide this?*

| Answer | Cause | Fix |
|--------|-------|-----|
| "Nobody in this room" | The decision right sits elsewhere | Escalate; take it off this agenda |
| "It depends who you ask" | Ownership is genuinely contested | Resolve ownership first — that is the real decision |
| "We could, but we keep not" | Missing information, or avoidance | Name the information needed and its owner, with a date |

The third case is the most common and the most expensive. A topic the group is
avoiding will consume ten minutes every week indefinitely, because raising it
feels productive and resolving it feels risky.

---

## 7. Attendance decay

Attendance across a series is the team's revealed preference, and it is more
honest than any survey.

**Signal:** a 15%+ drop between the first and second half of a series indicates
people have concluded it is optional. By the time attendance has decayed this
far, the meeting has usually been unproductive for two months.

Decay interacts badly with notes discipline. When notes are not published,
absentees fall behind, so attendance becomes compulsory to stay informed — which
props up attendance in a meeting nobody values. **High attendance plus low
decision density plus no published notes is a meeting held hostage**, not a
healthy one. Publishing notes is what lets attendance tell the truth.

---

## 8. The review ritual

Reviewing the register is itself a meeting cost. Keep it under five minutes.

**What to review, in order:**

1. **Overdue items only.** Not everything. On-track items need no airtime.
2. **Third-carry-over items.** Re-commit with a date, or drop. No third option.
3. **Unowned and undated items from the last meeting.** Assign now or delete —
   they will not survive another week.
4. **Nothing else.** Reading the full register aloud is how a five-minute review
   becomes a twenty-minute one, and it is why teams stop doing it.

### Escalation ladder for stale actions [RECOMMENDED]

| Age past due | Action |
|--------------|--------|
| 1-7 days | Owner posts a new date in the channel. No meeting time. |
| 8-21 days | Named in the review; owner states the blocker out loud |
| 22-30 days | Owner's manager is looped in — as a capacity question |
| 30+ days | Closed as dropped, with a note saying so |

The last row is the one that matters. **Auto-closing at 30 days is not giving
up** — it is refusing to maintain a fiction. If the item genuinely matters, its
closure will be noticed within a week and it will be re-opened with a real date.
If nobody notices, it did not matter, and the register is now honest again.

---

## 9. Capping actions per meeting

The most effective intervention on a broken register is not better tracking. It
is generating fewer commitments.

**Rule of thumb:** a 60-minute meeting of five people can absorb **three to five
actions**. Beyond that, the marginal action is a wish. Teams that leave meetings
with twelve actions close about the same absolute number as teams that leave
with four — the extra eight simply arrive stale.

| Meeting length | Attendees | Sustainable actions |
|----------------|-----------|--------------------|
| 25 min | 3-5 | 1-2 |
| 50-60 min | 4-7 | 3-5 |
| 90 min (planning) | 5-9 | 5-8 |

When the room generates more than the cap, close the meeting by asking which
three matter this week and explicitly parking the rest. Parked is a real state
and it is honest; "assigned" for something nobody will start is not.

**Watch the ratio.** Actions per decision above roughly 4:1 means the meeting is
distributing work rather than converging on choices. That is not automatically
wrong — planning meetings look like this by design — but in a session billed as
a decision forum it means the decisions are being deferred into tasks.

---

## 10. Reconstructing a decision log from history

A frequent request when joining a project: *why is the system like this?*

1. **Extract decisions from all past notes.** Ignore the actions entirely —
   they are stale and reconstructing them wastes the effort.
2. **Order chronologically and mark supersession.** Later decisions frequently
   overturn earlier ones without saying so, and an unmarked superseded decision
   is worse than a missing one because someone will act on it.
3. **Flag decisions with no recorded approver.** These are the fragile ones —
   they will be re-litigated by whoever was absent, and knowing which they are
   tells you where to expect resistance.
4. **Note what is missing.** A system behaviour with no decision behind it in
   the record was either decided informally or never decided at all. Both are
   worth knowing before you change it.
5. **Publish it once and maintain it going forward.** A reconstruction that is
   not maintained decays within a quarter and is then actively misleading.

Expect to recover perhaps 60% of the real decision history. That is enough to
answer most "why is this like this" questions and to identify the two or three
load-bearing choices worth asking a long-tenured colleague about directly.

---

## 11. Interpretation traps

| Trap | Why it misleads | Correct reading |
|------|-----------------|-----------------|
| High action count read as productivity | Generating work is easy; closing it is not | Read completion rate, not volume |
| 100% completion read as excellence | Often means only trivially safe actions get recorded | Check whether hard items are being recorded at all |
| Rising completion after a review push | Owners closing easy items to clear the board | Check on-time rate and the age of what closed |
| One meeting with poor completion | May legitimately own the hardest work | Compare action *difficulty*, not just counts |
| Low decision count in a retro | Retros produce understanding, not decisions | Exclude retros from density scoring |
| Zero overdue items | Suspiciously clean; dates may be set after the fact | Check whether due dates precede closure dates |

**100% completion deserves as much scrutiny as 40%.** A register where
everything closes on time is usually a register that only receives safe,
already-started work, while the genuinely uncertain commitments are made verbally
and tracked nowhere. Ask which of the last month's hardest problems appear in
the register. If none do, the register is measuring the wrong things
successfully.

---

## 12. Wiring this into an existing ritual

The tracking only works if it attaches to something the team already does.

| Ritual | Attachment point | Duration added |
|--------|-----------------|----------------|
| Weekly working session | Parse notes after; review overdue at the top of the next | 5 min |
| Sprint retro | Bring completion rate and carry-over counts as data | 5 min |
| Meeting audit | Run the series diagnostic across the recurring calendar | one-off |
| Quarterly planning | Decision log review — what did we commit to, what changed | 15 min |

Do **not** create a new meeting to review the register. A team whose response to
poor follow-through is an additional recurring meeting has diagnosed the problem
exactly backwards, and the new meeting will itself generate actions nobody
closes.
