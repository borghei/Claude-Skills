# Capture Conventions

The mechanics of getting every open loop out of your head and into a place you
trust. Capture is the cheapest part of any productivity system and the one that
fails most often, because failure is silent — you never see the thought you
didn't record.

---

## 1. The friction budget

**A capture tool that takes more than 5 seconds to open will not be used when it
matters.** The moments you most need to capture — mid-conversation, driving,
falling asleep, walking between meetings — are exactly the moments when a
five-tap flow loses to "I'll remember it."

| Capture latency | Real-world behaviour |
|---|---|
| < 2 seconds | Captures reliably, including low-value thoughts. Ideal. |
| 2-5 seconds | Captures deliberate thoughts; loses fleeting ones. Acceptable. |
| 5-15 seconds | Captures only what feels important at the time. Systematically loses the small commitments that damage trust when dropped. |
| > 15 seconds | Effectively no capture system. You are running on memory. |

Measure yours honestly: from "thought occurs" to "text is saved," with your
phone locked and in your pocket. Most people discover their real latency is
three times what they assumed.

**[PROVEN] Optimise for latency over organisation at capture time.** A messy
single inbox processed weekly beats a beautifully structured system you bypass
under pressure. Organisation is a processing-time concern, not a capture-time
one.

---

## 2. Capture surfaces, ranked

You will have several capture surfaces because no single one covers every
context. That is fine — what breaks systems is having several surfaces and no
convention for draining them.

| Context | Surface | Why |
|---|---|---|
| At a keyboard | Global hotkey to a plain-text file or task inbox | Lowest latency of any surface; no app switch |
| Phone, hands free | Voice memo or voice-to-text to a single note | The only surface that works while driving or walking |
| Phone, hands available | Home-screen widget writing to one note | Two taps; no app launch |
| In a meeting | A dedicated line prefix in your meeting notes (e.g. `TODO:`) | Keeps capture in the flow of the notes you are already taking |
| Reading | Highlight-to-inbox, or paste the URL with one line of why | The URL alone is near-useless three weeks later |
| Asleep / half-asleep | Paper and pen on the nightstand | Screens wake you up; paper does not |

**The rule that makes this work:** every surface must drain into one place you
review. Six capture surfaces and six review locations is not a system.

---

## 3. The one-inbox principle

**[PROVEN] Aim for one processing inbox, not one capture surface.**

Multiple capture points are unavoidable. Multiple *processing* points are a
choice, and they are the reason most systems collapse: with four places to look,
you can never achieve the feeling of "I have seen everything," which is the
entire psychological payoff of a capture habit.

Acceptable end state: 1 processing inbox, 2 at the outside (typically your task
inbox and your email inbox, since email is a capture surface others write to).

If you have more than two, consolidate:

1. List every place an unprocessed commitment can currently live.
2. For each, decide: does it drain into the primary inbox, or is it primary?
3. Anything that is neither gets closed or automated into the primary.
4. Re-check in four weeks — new inboxes appear quietly (a new chat tool, a
   shared doc "action items" tab, a notebook).

---

## 4. What a good capture looks like

A capture has one job: preserve enough context that your future self can decide
what to do without reconstructing the original thought.

**Minimum viable capture = trigger + outcome hint.**

| Bad capture | Why it fails | Better |
|---|---|---|
| `taxes` | No outcome, no next step, no context. Requires full re-thinking. | `Gather 2026 receipts for accountant — she needs them before Aug 15` |
| `talk to Sam` | About what? Which Sam? | `Ask Sam whether the vendor SOC 2 report arrived` |
| `pricing` | A topic, not a commitment | `Draft three pricing-page headline options for review` |
| A bare URL | Three weeks later you won't recall why you saved it | URL + `— method for measuring context-switch cost, cite in the focus doc` |

You do not need full sentences or perfect phrasing at capture time. You need the
**noun and the verb**: what thing, and what you intend to do to it. Ten extra
characters at capture saves two minutes of reconstruction at processing.

---

## 5. Capture is not commitment

A frequent objection: "if I capture everything, my list becomes unmanageable."

This confuses two operations. Capture says *this crossed my mind*. Processing
says *this is mine to do*. Conflating them means you self-censor at capture time
— filtering with the exact tired, distracted judgement that capture exists to
protect you from.

**[RECOMMENDED] Capture with zero filtering; filter hard at processing.** A
weekly processing pass should delete or defer a meaningful share of what you
captured — if it deletes nothing, you are still filtering too early.

Expect roughly: 15-25% dropped outright, 20-30% filed as reference or someday,
and the remainder converted into actions or projects. A log where 95% becomes an
action means you are only capturing the obvious.

---

## 6. Metadata worth recording

Keep it to what changes a decision. Every extra field is friction paid at every
capture.

| Field | Keep it? | Why |
|---|---|---|
| Text | Required | The capture itself |
| Timestamp | Required — automate it | Drives staleness detection; never type it manually |
| Source | Worth it if automatic | Reveals which inbox leaks; e.g. "half my captures come from Slack" is actionable |
| Context / location | Rarely | High friction, low payoff for most people |
| Priority | No | You cannot judge priority at capture time, and it goes stale |
| Due date | Only if genuinely externally imposed | Self-assigned due dates at capture time are guesses that later create false urgency |

**Do not assign priority at capture time.** Priority is relative to everything
else on the list, and at capture time you are looking at one item in isolation.

---

## 7. Trust, and how it is lost

The value of a capture system is not the list. It is the licence to stop
rehearsing commitments in your head — which your mind only grants once it has
evidence the system is real.

Trust breaks in three ways:

1. **Capture gaps.** Something you captured never appeared anywhere. One
   instance is enough for your mind to resume background rehearsal.
2. **Processing gaps.** Items sit in the inbox for weeks. The inbox becomes a
   place things go to die, so you stop putting anything important there.
3. **Retrieval gaps.** You captured it and processed it, but cannot find it when
   the relevant context arrives.

Of these, **processing gaps are the most common and the most damaging**. The
weekly pass is not optional hygiene; it is the thing that makes capture worth
doing at all. A capture habit without a processing habit is a slower way of
forgetting.

---

## 8. Instrumenting the habit

Two numbers tell you whether the system is real:

| Metric | Healthy | Warning | Broken |
|---|---|---|---|
| Median age of inbox items | < 7 days | 7-14 days | > 14 days |
| Share of items older than 14 days | < 20% | 20-40% | > 40% |
| Share phrased without a concrete verb | < 25% | 25-50% | > 50% |
| Inbox size after weekly pass | 0-3 | 4-10 | > 10 |

`capture_audit.py` computes the first three from a timestamped log. The fourth
you observe directly. If your inbox never reaches near-zero after a pass, either
the pass is too short or you are capturing into a system whose processing step
you have not actually designed.

---

## 9. Failure modes by system type

| System | Characteristic failure | Countermeasure |
|---|---|---|
| Paper notebook | No search; captures stranded on old pages | Transcribe into the digital inbox during the weekly pass |
| Notes app | Becomes a document graveyard; no processing surface | Reserve exactly one note as the inbox; everything else is post-processing |
| Task manager | Capture friction from mandatory fields (project, due date, tags) | Configure a quick-entry path that requires only text |
| Email to self | Mixes with real email; competes with inbound | Use a filter that routes self-mail to a separate label |
| Chat message to self | Excellent latency; terrible retention and no processing state | Fine as a surface, never as the processing inbox |

---

## 10. Setting it up in 30 minutes

1. **Choose the processing inbox.** One place. Plain text is fine.
2. **Wire the three surfaces you actually need** — keyboard, phone, voice —
   into that inbox. Test each with a real capture.
3. **Measure latency** for each surface with your phone locked. Fix anything
   over 5 seconds before adding anything else.
4. **Schedule the processing pass** — 30 minutes, weekly, recurring, defended.
   Put it where you are reliably at a keyboard and not exhausted.
5. **Run one full pass immediately** on whatever is already scattered around.
   The first pass is long (60-90 minutes) because it drains years of backlog.
6. **Audit after four weeks** with `capture_audit.py`. Adjust the surface that
   generated the most unprocessed items.

Do not add tooling beyond this until you have run four consecutive weekly
passes. Almost every "my system isn't working" problem is a missing processing
pass, not a missing feature.

---

## 11. Where processed items go — the filing taxonomy

Capture is only half a system. An item leaving the inbox needs exactly one
destination, and the destinations must be few enough to choose between in
seconds. Seven is the working maximum; beyond that, filing becomes a decision
problem and processing slows to a crawl.

| Destination | Holds | Reviewed | Typical size |
|---|---|---|---|
| **Next actions** | Single-step items you will do | Daily | 20-50 |
| **Projects** | Multi-step outcomes, each with one visible next action | Weekly | 10-25 |
| **Calendar** | Only genuinely date-specific commitments | Continuously | — |
| **Waiting-for** | Delegated items, each with a person and a check date | Weekly | 5-15 |
| **Reference** | Information with no action attached | On demand, via search | Unbounded |
| **Someday/maybe** | Real interest, no current commitment | Monthly | 20-60 |
| **Bin** | Everything else | Never | — |

**The calendar is the most abused destination.** Putting a non-date-specific
task on a specific day is a way of avoiding the decision about whether you are
actually going to do it. When the day arrives and you do not do it, you drag it
forward — and a calendar containing items you routinely drag stops functioning
as a record of real commitments. Reserve it for things that must happen on that
date because of an external constraint.

### Sizing signals

| Symptom | Meaning |
|---|---|
| Next actions > 60 | You are deferring rather than dropping; run an aggressive drop pass |
| Projects > 30 | More open commitments than any person can advance; most are stalled |
| Waiting-for consistently empty | You are not delegating, or not tracking what you delegate |
| Someday > 100 | It has become a graveyard; nothing there is ever promoted |
| Reference used less than monthly | Your filing is not retrieval-shaped — see §12 |

---

## 12. Filing for retrieval, not for tidiness

Most people file by topic because it feels organised. Retrieval does not work by
topic — it works by whatever fragment you happen to remember, which is usually a
name, a date, or a phrase rather than a category.

**[RECOMMENDED] Prefer search over hierarchy.** A single flat reference store
with good titles beats a deep folder tree for almost everyone, because filing
into a tree requires predicting which branch your future self will look in — a
prediction that is wrong surprisingly often, and expensively, since a
misfiled item is functionally lost.

Where a hierarchy is genuinely needed (shared team stores, regulatory records),
keep it to **one level**. Two levels doubles the filing decision cost and, in
practice, roughly doubles the misfile rate.

### Titles that survive

The title is what you will search on months later, so it should contain the
words you will actually recall.

| Weak title | Why it fails | Better |
|---|---|---|
| `Notes` | Matches everything | `2026-07-14 vendor call — SOC 2 timeline` |
| `Contract` | Which one? | `Northwind MSA — signed 2026-05, renews annually` |
| `Ideas` | Undifferentiated | `Pricing experiment ideas — from Q2 churn analysis` |
| `Screenshot 2026-07-14` | Tool default, no content | `Error state — checkout 500 on expired token` |

**Include a date and a proper noun in every reference title.** Those are the two
fragments people reliably remember, and together they narrow almost any search
to a handful of results.

---

## 13. Capture in hard contexts

The contexts where capture matters most are the ones where standard tooling
fails. Each needs a pre-decided convention, because inventing one in the moment
is exactly what does not happen.

### In a meeting

Interrupting to open a task app is socially costly, so commitments made in
meetings are the most commonly lost category of all — and the most damaging,
because someone else is expecting them.

**Convention:** a line prefix inside your meeting notes. `TODO:` for yours,
`WAIT:` for something someone else owes you. Both get extracted during the
weekly pass with a search. This keeps capture in the flow of the notes you are
already taking, at zero social cost.

### Mid-conversation, no notes open

Say it out loud: "let me write that down." This is not rudeness — it reads as
taking the other person seriously, and it buys the five seconds you need. The
alternative is nodding and losing it, which is the actual discourtesy.

### While reading

A bare URL is close to useless within three weeks. **Capture the link plus one
clause on why you saved it.** The clause is what makes it retrievable and, more
importantly, what lets you decide during processing whether it is reference,
an action, or a drop — a decision that is impossible from the URL alone.

### Driving, walking, showering

Voice capture is the only surface that works, and these contexts generate a
disproportionate share of genuinely valuable thoughts because the mind is
unloaded. Accept that voice-to-text will be imperfect; a garbled transcript you
can decode within a week beats a perfect thought you lost.

### Half-asleep

Paper on the nightstand. A phone screen wakes you enough to cost 20 minutes of
sleep, so the capture is real but the price is too high — and after two nights
of that, you stop capturing at all.

---

## 14. Setup recipes by tool type

Three configurations that meet the latency requirement. Pick the row matching
what you already use rather than adopting a new tool, since tool migration is
where most system rebuilds die.

### Plain text file `[PROVEN]`

The most durable option and the fastest. One file, append-only, one line per
capture.

- **Keyboard:** a global hotkey bound to a two-line script that appends a
  timestamped line and closes. Sub-second.
- **Phone:** any note-syncing app pointed at the same file.
- **Processing:** open the file, work top to bottom, delete lines as they leave.
- **Why it wins:** no schema, no fields, no app launch, no vendor. The scripts
  in this skill read the markdown bullet form directly.

### Task manager

- **Configure a quick-entry path requiring only text** — no mandatory project,
  due date, or tag. Mandatory fields are the single most common cause of a task
  manager being abandoned as a capture surface, because they turn a two-second
  action into a fifteen-second one.
- Route quick entries to a dedicated Inbox project; process weekly.
- Turn off any prompt asking you to schedule at capture time.

### Notes app

- **Reserve exactly one note as the inbox** and pin it. Everything else in the
  app is post-processing storage.
- Add a home-screen widget or share-sheet action that appends to that one note.
- The failure mode here is the app becoming a document graveyard where the
  inbox note is just one document among thousands — pinning is what prevents it.

---

## 15. Recovering a collapsed system

Most people arrive at this skill after a system has already failed. Restarting
is a different job from starting, and the difference matters: you have a backlog
carrying real guilt attached to it.

1. **Do not reorganise first.** The instinct is to rebuild the structure. The
   structure is not what failed — the processing pass is. Rebuilding the tree
   is procrastination that looks like work.
2. **Declare bankruptcy on the old backlog.** Move everything older than 60 days
   to a `backlog-archive` file untouched. You will retrieve under 5% of it, and
   anything genuinely important will resurface on its own via someone asking.
3. **Run one full gathering pass** on everything from the last 60 days. Expect
   60-90 minutes; this is the longest session you will run.
4. **Schedule the weekly pass before doing anything else.** Recurring, defended,
   at a time you are reliably at a keyboard and not exhausted. Friday afternoon
   works for many; Monday morning works for others; both beat "when I get to it."
5. **Run four consecutive passes before judging the system.** Two passes is not
   enough to feel the payoff, and the payoff — the licence to stop rehearsing
   commitments in your head — is what makes the habit self-sustaining.
6. **Audit at week five** with `capture_audit.py`, and change exactly one thing.

The guilt attached to an old backlog is itself a reason people avoid the system.
Archiving wholesale removes the guilt in one action and costs almost nothing —
which is precisely why it works better than the more virtuous-feeling plan of
processing it all properly.
