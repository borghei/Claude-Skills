# Change Communication Cadence

Timing rules for change programmes that run longer than a single announcement. The recurring
error is treating communication as an event rather than a schedule: one large send at T-0,
then silence, then surprise at low adoption.

---

## The five-touch pattern [PROVEN]

For any change with a horizon of two weeks or more, five touches with decreasing length
outperform both a single send and a weekly drumbeat.

| Touch | Timing | Length | Content | Channel |
|-------|--------|--------|---------|---------|
| 1. Announcement | T+0 | Full | The five required elements | Live where possible, then written |
| 2. FAQ update | T+3 days | 200-400 words | The questions actually asked, verbatim | Same thread + durable page |
| 3. Manager check-in | T+1 week | Conversation | Where the message did not land | Existing manager forum |
| 4. Progress note | T+2 weeks | Under 150 words | What has happened; what is next | Written |
| 5. Close-out | T+4 weeks | Under 150 words | Confirm done; retire the FAQ | Written |

Touch 2 is the one most often skipped and the one that most changes outcomes. Publishing the
real questions — including the hostile ones — signals that the channel is genuine. Publishing
a pre-written anticipated-questions list signals the opposite, and readers tell the difference
immediately.

### When to extend

Add touches only for changes where behaviour must persist: a new security practice, a
performance process, a way of working. Add a T+8 week and T+12 week reinforcement, each under
100 words, each citing one concrete example of the new behaviour working. Do not extend for
one-off structural changes; there is nothing left to reinforce.

---

## Lead time by blast radius [PROVEN]

Blast radius counts people whose *work or employment changes*, not people who receive the mail.

| Radius | Pre-broadcast lead | Manager enablement | Exec pre-brief | Influencer pre-brief |
|--------|--------------------|--------------------|----------------|----------------------|
| 1-10 | Same day | No | No | No |
| 11-50 | 1-2 days | Yes, 60 min | Yes | No |
| 51-250 | 3-5 days | Yes, 60 min + FAQ | Yes, 3-5 days out | Optional |
| 250+ | 5-10 days | Yes, plus a dedicated manager Q&A channel | Yes, 7-10 days out | Yes, 2-3 days out |

**Longer is not better.** Beyond roughly 10 days of cascade, leak probability approaches
certainty, and a leaked change is strictly worse than a slightly under-briefed one: you lose
control of framing and the sequence collapses anyway. If you need more than 10 days, the
problem is decision-making speed, not communication.

### Influencer pre-brief

At 250+ people, identify 5-10 people with informal standing — long tenure, high trust, no
management authority. Brief them 2-3 days ahead under explicit confidentiality. They are not
there to endorse the change; they are there so that when the questions start, the people
others turn to are not hearing it for the first time. Skipping this step at large scale is
why some changes acquire a hostile narrative within an hour of announcement.

---

## Manager enablement pack

Anything requiring manager enablement needs this content, delivered live, at least 24 hours
before broadcast.

1. **The talk track.** 150-250 words a manager can say in their own words. Not a script to
   read aloud — managers reading a script verbatim is worse than no cascade.
2. **Explicit confidentiality boundaries.** What they may say now, what they must wait on,
   and what they must not speculate about. Ambiguity here produces both leaks and silence.
3. **The three hardest questions**, with real answers. Typically: "Is my job safe?",
   "Why now?", and "Was this decided before you asked for our input?"
4. **What to do when they do not know.** The correct answer is "I do not know, I will find
   out by <date>" and a route to escalate. Managers invent answers when they have not been
   given permission to say they do not know.
5. **A reporting channel** for what they hear back, live within 48 hours of broadcast.

---

## Timing rules that hold [RECOMMENDED]

| Rule | Reason |
|------|--------|
| Never announce a material change on a Friday | Nobody is available to answer questions, and the weekend rumour cycle runs unopposed |
| Never announce in the last hour of the working day | Same failure, compressed |
| For distributed teams, pick the hour that is workday for the most-affected region | The most-affected group should not read it at 23:00 |
| Put a live Q&A within 24 hours of any high-impact announcement | The question volume peaks in the first day and decays fast |
| Leave at least 48 hours between a change announcement and any unrelated celebratory message | Adjacency reads as tone-deafness |
| For deadline-driven changes, send reminders only to non-completers | Reminding compliant people trains the org to filter your sends |

---

## Feedback windows

| Change type | Window | What you are asking |
|-------------|--------|---------------------|
| Irreversible structural (reorg, reduction, shutdown) | None | Nothing. Do not invite input |
| Reversible policy | 5-10 business days | Specific, scoped: implementation details, exceptions |
| Way-of-working proposal | 2-3 weeks | Genuinely open: whether to do it at all |
| Migration / deadline | None | Questions only |

**The scoping sentence matters more than the window length.** "We are not revisiting whether
to do this; we do want to hear where the 25 August deadline breaks for your team" produces
usable input. "Let us know your thoughts" produces either silence or a referendum on the
decision itself, and then you either ignore it or reopen a settled question.

---

## Measuring whether it landed

Open rates measure delivery, not comprehension. Three signals that actually correlate:

1. **Question quality drift.** Week 1 questions should be "what does this mean for me";
   by week 3 they should be about implementation detail. If week 3 still looks like week 1,
   the message did not land and repeating it louder will not help — the structure was wrong.
2. **Manager escalation volume.** A short spike then decay is healthy. Flat-zero means
   managers are not being asked, which usually means people have decided asking is pointless.
3. **Completion rate against the required action**, if there is one. This is the only hard
   number available and it is the one worth reporting to leadership.

A change where 90% opened the email and 20% took the action was a communication failure,
regardless of what the dashboard says.

---

## Incident and crisis cadence

Incidents invert the normal rules. The five-touch pattern assumes you have time to prepare;
an incident assumes you do not, and the governing constraint is that **silence is filled by
speculation faster than you can correct it**.

| Phase | Timing | Content | Rule |
|-------|--------|---------|------|
| First notice | Within 30 min of confirmation | What is affected, what we know, next update time | Send before you have the cause. "We do not know yet" is a complete message |
| Holding updates | Every 60 min, or at the promised time | What changed since last update, even if nothing | Never miss a promised update time. Missing one costs more than the outage |
| Resolution | Within 30 min of restoration | What is working again, what may still be degraded | Do not declare all-clear before you are sure; a retracted all-clear is very expensive |
| Preliminary cause | Within 24 hours | What happened, in plain words, what we are checking | Avoid blame and avoid the word "unprecedented" |
| Post-mortem | Within 5 business days | Timeline, cause, actions with owners and dates | Publish internally in full. Partial post-mortems read as cover |

**The promised-update-time discipline is the whole practice.** A team that says "next update
at 15:00" and updates at 15:00 with "no change yet" retains credibility through a long
outage. A team that goes quiet for three hours loses it permanently, and the loss transfers
to the next incident.

---

## Distributed and multi-timezone sequencing

A cascade designed for one office breaks across timezones: the sequence that gives managers
24 hours of lead in London gives the Singapore team zero.

| Constraint | Approach |
|-----------|----------|
| Most-affected group is in one region | Anchor T+0 to that region's mid-morning. Everyone else adjusts |
| Impact is evenly distributed | Two synchronised broadcasts within the same rolling 24h, with identical written content published simultaneously |
| Manager cascade across regions | Brief all managers at a single time, even if inconvenient for some. Staggered manager briefings guarantee a leak between regions |
| Live Q&A | Run two sessions, not one recording. A recording is not a Q&A, and the region that gets the recording knows it was second |

Never let a region learn about a change from a colleague in another region. It is the most
reliably resented failure in distributed organisations, and it is entirely avoidable by
briefing managers globally at one time.

---

## Worked example: six-week policy rollout

A change to the performance-review process affecting 300 people, announced 1 September,
effective 15 October.

| Date | Touch | Audience | Channel | Notes |
|------|-------|----------|---------|-------|
| Aug 22 (T-10d) | Exec pre-brief | Leadership team | Small group | Confirm the decision is final before anything else moves |
| Aug 27 (T-5d) | Influencer pre-brief | 8 long-tenured ICs | 1:1 | Under confidentiality. Not endorsement — inoculation |
| Aug 29 (T-3d) | Manager enablement | 34 managers | 60-min live + FAQ | Talk track, boundaries, three hardest questions |
| Sep 1 (T+0) | Announcement | All 300 | All-hands + written | Five required elements; feedback window scoped to implementation only |
| Sep 4 (T+3d) | FAQ update | All | Doc + original thread | Real questions asked, verbatim, including the hostile ones |
| Sep 8 (T+7d) | Manager check-in | Managers | Manager forum | Where did it not land |
| Sep 15 (T+14d) | Progress note | All | Written, 120 words | Feedback window closes; what we changed because of it |
| Sep 29 (T+28d) | Close-out | All | Written | Training dates; FAQ retired |
| Oct 15 | Effective date | — | — | No new communication needed if the above worked |

Note what is absent: no communication between 29 September and the effective date. Once the
close-out has landed, further messages are noise and they train people to skim. The effective
date itself needs no announcement — if it does, the rollout communication failed.
