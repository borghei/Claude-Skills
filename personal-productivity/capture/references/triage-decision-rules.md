# Triage Decision Rules

How a raw capture becomes something you can execute. This is the processing
half of the system — the part that turns a list of fragments into a set of
commitments you can act on without re-thinking each one.

---

## 1. The processing sequence

Process **one item at a time, in order, without skipping**. Do not scan the list
looking for the easy ones. Skipping is how items become permanently stale: the
hard item you skipped this week is the same hard item you will skip next week,
and after six passes it is untouchable.

For each item, in this order:

1. **Is it actionable?** No → reference, someday, or drop. Yes → continue.
2. **What is the outcome?** Name the state of the world when this is done.
3. **Is it one step or several?** One → action. Several → project with a
   defined first action.
4. **Under 2 minutes?** Yes → do it now. No → continue.
5. **Am I the right person?** No → delegate and track. Yes → continue.
6. **Date-specific?** Yes → calendar. No → next-actions list.

The order matters. Deciding "is it actionable" before "how long will it take"
prevents the most common processing error: doing a 90-second task that should
have been deleted.

---

## 2. The 2-minute rule, correctly applied

**[PROVEN] If an item takes less than 2 minutes, do it during processing rather
than filing it.**

The rationale is arithmetic, not motivational: filing an item, re-reading it
later, re-establishing its context, and then doing it typically costs more total
time than doing it immediately.

Three constraints people ignore:

- **It is a processing-time rule, not an always-rule.** Applying it continuously
  throughout the day makes you infinitely interruptible — you become a
  reactive queue. It applies while you are already in processing mode.
- **2 minutes means 2 minutes.** The honest median for "quick email" is 4-6
  minutes once you account for re-reading the thread. If you are unsure, it is
  over the line.
- **It does not apply during focused work.** A 2-minute task during a deep-work
  block costs the task plus the re-entry cost, which is far larger.

**Escape hatch:** if more than about a third of your inbox qualifies as
2-minute items, your processing session will collapse into an hour of small
tasks. In that case, batch them into a single 20-minute "small tasks" block
immediately after processing rather than doing them inline.

---

## 3. Defer, delegate, drop — choosing between them

| Decision | Test | What it costs you later |
|---|---|---|
| **Do** | < 2 min, and you are in processing mode | Nothing — the cheapest outcome |
| **Defer** | Yours, > 2 min, no one else can do it | A list slot and a weekly re-read |
| **Delegate** | Someone else is better placed, or it is genuinely their remit | A tracking entry and a follow-up date — never zero |
| **Drop** | No meaningful consequence if it never happens | Nothing, and this is underused |

### On dropping

**Drop is the most under-used outcome and the highest-leverage one.** Every
item you keep costs attention at every future review, in perpetuity. A list of
200 items where 60 are dead weight is worse than a list of 140, because the dead
weight trains you to skim rather than read.

Drop when any of these is true:

- The item has survived three weekly reviews with no progress and no external
  pressure. Three passes of "not this week" is a decision; record it as one.
- The originating context is gone (the project shipped, the person left, the
  quarter ended).
- You cannot articulate what happens if it is never done.
- It was aspirational rather than committed — captured as an identity statement
  ("be someone who does X") rather than an outcome.

Dropping is not failure. An item you keep but never do is a small recurring
tax on your attention; deleting it is the only way to stop paying it.

### On delegating

Delegation without tracking is abdication. Every delegated item creates a
**waiting-for** entry with three fields: what, who, and the date you will check.
Without the date, you will either forget it or check compulsively — the latter
being the reason many people avoid delegating at all.

Default follow-up intervals: 3 working days for a same-week deliverable, 1 week
for a multi-week item, and always a check before any external deadline it feeds.

---

## 4. Converting vague captures into next actions

The single highest-value transformation in the whole system. A vague item is not
a small problem — it is an item that will be silently skipped at every review,
because your mind quietly recognises it as an unsolved thinking problem rather
than a task.

### The grammar of a next action

**`<concrete verb> <specific object> [<qualifier that makes it findable>]`**

The verb must describe a *physical, visible* action. "Decide," "think about,"
"handle," and "follow up" fail this test — they name a mental state, not a
movement.

| Vague capture | Diagnosis | Next action |
|---|---|---|
| `Follow up with the landlord` | No verb, no subject matter | `Email the landlord asking when the boiler inspection is scheduled` |
| `Think about pricing` | Mental state, not action | `Draft three pricing options in a doc, one paragraph each` |
| `Q3 offsite stuff` | Topic, no outcome | `List the three decisions the Q3 offsite must produce` |
| `Sort out CI flakiness` | Project disguised as action | Project. First action: `Pull the last 20 CI failures and group them by cause` |
| `Deal with insurance` | Undefined scope | `Read the renewal letter and note the response deadline` |
| `Talk to Priya` | Missing subject | `Ask Priya whether she wants to own the migration doc` |

### The two questions that unstick anything

When an item resists conversion, one of these two always works:

1. **"What does done look like?"** — produces the outcome. If you cannot answer
   in one sentence, it is a project, and possibly one you have not decided to
   take on.
2. **"What is the very next physical thing I would do, if I sat down to do this
   right now?"** — produces the action. The answer is often smaller than
   expected: open a file, find a phone number, re-read an email.

If both questions fail, the item is not a task — it is an unmade decision. File
it as a decision to make, with its own next action: `Decide whether to X by
<date>`.

### The "first action is usually information-gathering" pattern

For genuinely uncertain items, the honest first action is nearly always
retrieval, not execution: find the document, ask the question, check the
constraint. Writing `Migrate the database` as a next action guarantees paralysis;
`Check which tables still reference the legacy schema` does not.

---

## 5. Actions vs projects

**A project is anything requiring more than one action.** Not "a big thing" —
two steps is a project.

This threshold feels aggressively low and it is the point. The failure mode it
prevents is the multi-step item sitting on a next-actions list, being skipped
every review because it is not actually doable in one sitting.

| Item | Type | Why |
|---|---|---|
| `Sign the insurance renewal` | Action | One physical step |
| `Book flights and reserve the hotel` | Project | Two actions; first is `Book flights for the 14th` |
| `Read the incident write-up` | Action | One step, even if it takes 40 minutes |
| `Launch the onboarding flow` | Project | Many steps, several owners |

Every project needs exactly one **defined and visible next action**. A project
list where some entries have no next action is where work quietly stalls — and
finding those entries is the main job of the weekly pass.

---

## 6. The weekly inbox-zero pass

**[PROVEN] 30-45 minutes, weekly, same slot, defended.** This is the load-bearing
habit. Everything else degrades gracefully; this does not.

### Sequence (45 minutes)

| Minutes | Step | Output |
|---|---|---|
| 0-5 | Gather: drain every capture surface into the one inbox | A single list |
| 5-10 | Run `capture_triage.py` for a first-pass classification | Bucketed items with suggested next actions |
| 10-30 | Process each item using the sequence in §1 — no skipping | Empty inbox |
| 30-38 | Review the project list: does every project have a visible next action? | No stalled projects |
| 38-43 | Review waiting-for items: anything overdue a nudge? | Follow-ups sent or scheduled |
| 43-45 | Scan someday/maybe: promote anything now relevant, drop anything dead | A someday list you still believe in |

### Inbox zero means empty, not "triaged"

The inbox is empty when every item has left it for a specific destination:
next-actions, project list, calendar, waiting-for, reference, someday, or the
bin. "I looked at all of them" is not processing — items that stay in the inbox
after a pass have had a decision deferred, and deferring the same decision
weekly is how a five-item inbox becomes a fifty-item one.

**Escape hatch:** when the backlog is genuinely too large for one session
(typically the first pass, or after a holiday), declare inbox bankruptcy on
anything older than 60 days — move it wholesale to a `backlog-archive` file and
process only the recent items. You will retrieve fewer than 5% of the archived
items, and the alternative is skipping the pass entirely.

---

## 7. Diagnosing a failing system

| Symptom | Root cause | Fix |
|---|---|---|
| Inbox grows every week | Processing pass is not happening, or is too short | Restore the pass; extend to 60 min for four weeks to clear the debt |
| Same items reviewed repeatedly, never done | Vague phrasing, or undecided commitment | Rewrite as concrete next actions; drop what survives three reviews |
| You do tasks that were never on the list | Capture latency too high, or trust already lost | Fix the fastest capture surface first |
| List is long but nothing feels urgent | No outcomes attached; everything reads as optional | Add "what does done look like" to each project |
| You avoid opening the system | It contains items you have decided not to do but not deleted | Aggressive drop pass; the list must contain only real commitments |
| Everything is a 2-minute task | Real work is not being captured, only admin | Check whether project-level work is being tracked anywhere at all |

---

## 8. Numbers worth knowing

| Rule of thumb | Value | Source of the number |
|---|---|---|
| 2-minute threshold | 2 min | Filing + re-reading + re-contextualising typically exceeds the task itself past this point |
| Weekly pass duration | 30-45 min | Enough for 20-40 items at 60-90 seconds each |
| Per-item processing time | 60-90 sec | Longer means you are doing the work, not deciding about it |
| Stale threshold | 14 days | One missed weekly pass is recoverable; two signals habit failure |
| Rotten threshold | 45 days | Three missed passes — the item is almost certainly a drop |
| Drop rate at processing | 15-25% | Below this, you are filtering too early at capture time |
| Post-pass inbox size | 0-3 | Anything above 10 means decisions were deferred, not made |
| Someday review cadence | Monthly | Weekly is too often to be useful; quarterly lets it rot |

---

## 9. A worked triage session

Fourteen captured items, processed in order. This is what 60-90 seconds per item
actually looks like in practice.

| # | Capture | Decision | Result |
|---|---|---|---|
| 1 | `Call the dentist to move Thursday's appointment` | Actionable, one step, over 2 min (needs their opening hours) | Next actions: `Call dentist 0800-xxx to move Thu 14:00` |
| 2 | `Reply to Dana about the contract redline` | Actionable, under 2 min | **Done during the pass** |
| 3 | `Launch the new onboarding flow` | Actionable, many steps | Project. First action: `List the three screens the flow must cover` |
| 4 | `taxes` | Cannot tell — no outcome | Ask "what does done look like?" → receipts to accountant. Project, first action: `Find the accountant's document checklist email` |
| 5 | `Think about the pricing page rewrite` | Mental state, not action | `Draft three headline options, one paragraph each` |
| 6 | `https://example.org/attention-residue — switch-cost method` | Not actionable | Reference, titled `Attention residue — switch-cost measurement method` |
| 7 | `Someday learn to sail` | Real interest, no commitment | Someday/maybe, monthly review |
| 8 | `Follow up with the landlord` | No verb, no subject | Ask "next physical thing?" → `Email landlord asking when boiler inspection is scheduled` |
| 9 | `Book flights and reserve the conference hotel` | Two actions | Project. First action: `Book flights for the 14th` |
| 10 | `Sign the insurance renewal` | Actionable, under 2 min | **Done during the pass** |
| 11 | `nvm — vendor already cancelled the invoice` | Context gone | **Dropped** |
| 12 | `Q3 offsite stuff` | Topic, no outcome | `List the three decisions the Q3 offsite must produce` |
| 13 | `Read the incident write-up from Tuesday` | One step, 40 min | Next actions — length does not make it a project |
| 14 | `Sort out the CI flakiness` | Project disguised as action | Project. First action: `Pull the last 20 CI failures and group by cause` |

**Session outcome:** 2 done, 4 next actions, 5 projects, 1 reference, 1 someday,
1 dropped. Elapsed: 18 minutes.

Three things worth noticing:

- **Five of fourteen were projects, not actions.** This ratio is normal and is
  the main reason unprocessed lists stall — multi-step items sitting on a
  next-actions list get skipped every review, because they cannot be done in one
  sitting and your mind knows it.
- **Item 13 is an action despite taking 40 minutes.** Duration is irrelevant to
  the action/project distinction; step count is the only test.
- **Only one item was dropped**, below the healthy 15-25% band. That is a signal
  the capture habit is filtering too early — the log contains only items already
  judged worth keeping.

---

## 10. Waiting-for mechanics

Delegation without tracking is abdication, and it is the most common gap in
otherwise functional systems.

### The three required fields

| Field | Why |
|---|---|
| **What** | Phrased as the deliverable you expect, not the request you made |
| **Who** | A specific person, never a team — "the platform team owes me X" tracks nothing |
| **Check date** | Without it you either forget or check compulsively; the latter is why many people avoid delegating |

### Follow-up intervals

| Situation | First check |
|---|---|
| Same-week deliverable | 3 working days |
| Multi-week item | 1 week |
| Anything feeding an external deadline | Always a check before the deadline, regardless |
| Item that has already slipped once | Halve the previous interval |

### Escalation ladder

Two weeks with no reply is the point at which a polite nudge has demonstrably
failed. Escalate in this order, one step per cycle:

1. **Re-ask with a date attached.** Most non-responses are queue position, not
   refusal, and a specific date moves you up the queue.
2. **Ask whether it is still theirs.** Often the answer is no and nobody told
   you. This resolves a surprising share of stalled items at zero social cost.
3. **Offer to take it back.** Frequently produces immediate movement, and if it
   does not, you have learned what you needed to know.
4. **Escalate or drop.** Both are legitimate. What is not legitimate is carrying
   it silently for another two months.

**A waiting-for list that only grows is not a tracking system, it is a record of
things that are not going to happen.** Every item should exit within a defined
window — delivered, taken back, or dropped.

---

## 11. Someday/maybe, kept honest

The someday list is where systems quietly rot. It absorbs everything you cannot
face deciding about, and once it passes a hundred items nobody reads it — which
means nothing there will ever be promoted, which means it is a bin with a
comforting label.

### Rules that keep it alive

- **Review monthly.** Weekly is too often to be useful — nothing changes in a
  week. Quarterly lets it rot past the point of being read.
- **Cap it at roughly 50 items.** Over the cap, drop the bottom before adding.
  A capped list gets read; an uncapped one does not.
- **Every item needs a trigger**, not just a description. `Learn Rust` is inert;
  `Learn Rust — when a project actually needs it` tells the monthly review what
  to check for.
- **Promote or drop; never just re-read.** An item surviving six monthly reviews
  untouched is aspiration rather than intention. Drop it. If it matters, it will
  come back, and it will come back with a reason attached.

### What belongs there

| Belongs | Does not belong |
|---|---|
| Genuine interests with no current slot | Things you feel you *should* want to do |
| Ideas awaiting a triggering condition | Commitments you have made to other people |
| Projects deliberately paused with a reason | Items you are avoiding deciding about |
| Purchases past a spending threshold | Anything with a real deadline |

**The distinction that matters:** someday/maybe holds things you would genuinely
choose if conditions changed. It does not hold things you have committed to and
are avoiding — those belong on the project list where their staleness is
visible, or in the bin. Using someday as a place to hide avoided commitments is
what turns it into a graveyard, and it is the single most common way an
otherwise good system loses credibility with its own owner.
