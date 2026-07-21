# Focus Block Design

How to build a deep-work session that actually produces something. Most focus
advice stops at "block time on your calendar," which is the easy half. The hard
half is designing the block so the time inside it converts into output.

---

## 1. Why block length is the first decision

Cognitive work has a fixed startup cost. Reloading the problem state — what you
were doing, which constraints apply, what you had already ruled out — takes
15-20 minutes for non-trivial work, and it is paid every time you re-enter,
regardless of how long you stay.

That startup cost sets a hard floor on useful block length:

| Block length | Warmup share | Verdict |
|---|---|---|
| 25 min | ~70% | Adequate for well-defined execution (a known bug, a form to fill). Useless for anything requiring problem state. |
| 45 min | ~40% | Marginal. Works only when you are resuming something you touched hours earlier. |
| **90 min** | ~20% | **Minimum viable block for genuine cognitive work.** Warmup amortises; one real problem gets solved. |
| 120 min | ~15% | The sweet spot for most people. Long enough for depth, short enough to hold quality. |
| 180 min | ~10% | Excellent when the work is genuinely absorbing. Requires a real break afterwards. |
| 240+ min | ~8% | Diminishing returns; quality usually degrades in the last hour. Split it. |

**[PROVEN] 90 minutes is the minimum viable block; 120 is the default target.**
Below 90, warmup dominates and you produce fragments. This is why a day with
five 30-minute gaps is not the same as a day with one 150-minute block, even
though the arithmetic says otherwise — the five gaps yield close to zero.

**Escape hatch:** short blocks are genuinely useful for *pre-defined* execution
where the problem state is already externalised — clearing a code review queue,
filling in a template, transcribing notes. Reserve them for that, and stop
calling it deep work.

---

## 2. The daily ceiling

**Most people sustain 3-4 hours of genuine deep work per day, and that is an
upper bound, not a target to hit daily.**

Beyond roughly 4 hours the work continues but the quality does not — you get
motion without insight, and the deficit shows up as needing to redo the work.
People new to the practice typically manage 1-2 hours, and building to 3 takes
months, not days.

| Practice level | Sustainable daily | Weekly target |
|---|---|---|
| Starting out | 60-90 min | 300-450 min |
| Established | 120-180 min | 600-750 min |
| Peak, protected role | 180-240 min | 900-1000 min |
| Claimed 6+ hours daily | — | Either the definition is loose or it is a short sprint |

Set the weekly target from this table and feed it to
`session_log_analyzer.py --weekly-target`. Targets set from aspiration rather
than from your own logged history produce a demoralising streak of misses,
which reliably kills the habit within a month.

---

## 3. Session structure

A designed session has four parts. Skipping any of them is what makes blocked
time evaporate.

### 3.1 Pre-commitment (the night before, 2 minutes)

**Decide the artefact before the block starts, not during it.** The single
largest source of wasted focus time is spending the first 20 minutes of a
protected block deciding what to work on — you burn the freshest attention of
the day on a decision you could have made while tired.

Write one line: *"Tomorrow 09:30-11:30 I will work on `<artefact>` until
`<observable state>`."* If you cannot name an observable state, the work is not
ready for a deep block; it needs a planning pass first.

### 3.2 Warmup (first 10-15 minutes)

Do not fight the warmup — design for it. Re-read what you wrote last session,
re-open the same files, re-read the problem statement. Resist the urge to count
this as wasted time; the alternative is starting cold in minute 20.

**[RECOMMENDED] Stop mid-thought at the end of a session.** Leaving a sentence
unfinished or a test failing gives the next session an obvious entry point and
cuts warmup roughly in half. Finishing cleanly feels better and costs more.

### 3.3 The block itself

**The single-artefact rule:** one session, one artefact. Not one project — one
file, one document, one problem. The moment a session touches two artefacts, you
pay warmup twice and typically finish neither.

This is the cheapest quality lever available, and `session_log_analyzer.py`
tracks adherence directly. Sessions touching more than one artefact reliably
show lower focus ratings and higher plan-vs-actual drift in almost any log.

Rules inside the block:

- No inbox, no chat, no queue-checking — those are separate work modes
- Capture intrusive thoughts on paper, do not act on them (this is what a
  capture habit is for)
- No task is "just 2 minutes" during a block; the 2-minute rule is a
  processing-mode rule and applying it here costs the task plus re-entry
- If genuinely blocked, spend 10 minutes writing down *why* before switching —
  that note is often more valuable than the work would have been

### 3.4 Close-out (last 5 minutes)

Write two lines: what state the artefact is in, and what the next entry point
is. This is what makes tomorrow's warmup cheap, and it is the step people cut
first when a meeting is about to start — which is precisely why the block after
an unprotected block is always the weakest.

---

## 4. Placement within the day

**Place your longest block against your peak, not against your gaps.** The
common failure is scheduling deep work into whatever the calendar left over,
which is usually mid-afternoon — the trough for most chronotypes.

| Placement | Works when | Fails when |
|---|---|---|
| First thing (start of day) | You control your morning; peak alertness is early | Your role has a morning support or standup obligation |
| Post-standup (10:00-12:00) | A short fixed morning ritual anchors the day | Standup routinely runs long or spawns immediate follow-ups |
| Immediately after lunch | You are a late-peaking chronotype | You experience a strong post-lunch dip — most people do |
| Late afternoon (15:00-17:00) | Genuine evening type; the office quietens | Decision fatigue has accumulated all day |

**[RECOMMENDED] Anchor the block to the same time daily.** A variable slot has
to be re-decided and re-defended every day, and the decision cost alone erodes
it. A fixed slot becomes something colleagues learn to route around within a
few weeks — the calendar teaches people your availability whether you intend it
or not.

---

## 5. The interruption budget

Treat interruptions as a quantified budget, not an unavoidable condition.

**Each interruption costs roughly 23 minutes of degraded output**, not the
duration of the interruption itself. That figure is the observed re-immersion
time for knowledge work — the interruption feels like 90 seconds and prices like
half an hour.

| Interruptions/hour | Effective output | Verdict |
|---|---|---|
| 0 | ~100% | The block is real |
| 0.5 | ~80% | Acceptable; the practical target |
| 1.0 | ~60% | Ceiling. Above this the block is scheduled but not defended |
| 2.0 | ~30% | You are doing shallow work in a room labelled deep work |
| 3+ | ~10% | Stop protecting this slot; move it |

Budget explicitly: *"This block tolerates one interruption. A second means the
block failed and I reschedule rather than push through."* Naming the budget in
advance turns a vague frustration into a measurable, fixable condition — and
`session_log_analyzer.py` will tell you whether you are inside it.

---

## 6. Measuring the practice

Track four numbers per session. Anything more becomes an administrative task
that competes with the work.

| Field | Why it matters |
|---|---|
| `planned_min` vs `actual_min` | Drift over 20% means blocks are being cut into, or the plan is fiction |
| `interruptions` | The defence metric — the one that predicts whether the habit survives |
| `artefact` | Single-artefact adherence, the cheapest quality lever |
| `focus_rating` (1-5) | Subjective, but the only signal that catches "present but not engaged" |

Review monthly, not weekly. Deep-work volume is noisy week to week — a single
conference or launch swamps the signal — and reacting to weekly noise produces
thrashing. `session_log_analyzer.py` compares the first and second half of the
logged period and flags a change of more than 10% as a real trend.

---

## 7. Diagnostic table

| Symptom | Likely cause | Fix |
|---|---|---|
| Blocks exist but nothing gets finished | No pre-committed artefact; deciding inside the block | Name the artefact and its done-state the night before |
| Sessions consistently run short of plan | Adjacent meetings encroaching, or optimistic planning | Add a 15-min buffer after the block and re-measure |
| High volume, low output | Multiple artefacts per session | Enforce the single-artefact rule for four weeks |
| Good early sessions, poor late ones | Exceeding the daily ceiling | Cap at 3 hours; the fourth hour usually needs redoing |
| Volume decaying week over week | Encroachment that nobody pushed back on | Audit the calendar for what appeared in the slot; defend or move it |
| Cannot start despite protected time | The work is under-specified | The block is being used for work that needs a planning pass first |
| Long blocks exist but feel shallow | Warmup never completes because of low-grade interruptions | Measure interruptions/hour; if above 1.0 the problem is defence, not design |

---

## 8. Breaks and recovery

Deep work is bounded by recovery, not by willpower. A block scheduled after
insufficient recovery produces the hours but not the output, and the resulting
"I did deep work and it didn't help" is one of the main reasons people abandon
the practice.

### Between blocks

**[RECOMMENDED] 15-30 minutes between blocks, and the break must not be
cognitively loaded.** Checking email or chat during a break does not recover
attention — it substitutes one demanding task for another and leaves you
starting the second block already depleted.

| Break activity | Recovery value | Why |
|---|---|---|
| Walking, ideally outside | High | Diffuse attention; frequently surfaces solutions to the problem you just left |
| Staring out of a window | High | Genuinely restorative; feels unproductive and is not |
| Physical chores | Medium-high | Occupies the body, frees the mind |
| Conversation, non-work | Medium | Restorative for extroverts, depleting for introverts |
| Email or chat | **Negative** | Loads new open problems; you begin the next block already primed |
| Social feeds | **Negative** | Rapid context switching — the exact pattern deep work is training against |
| Eating at the desk while reading | Low | Neither rest nor work |

The two negative rows matter more than the positive ones. Most people's breaks
actively harm the following block, which is why "I took a break and the second
session was worse" is such a common report.

### Across the day

The second block of a day is typically 70-80% as productive as the first, and
the third is 50-60%. This decay is normal and not a discipline failure. Plan
around it: put the hardest work first, and schedule the day's shallow work into
the slot where deep work would be least effective anyway.

### Across the week

**Five consecutive days at your daily ceiling is not sustainable.** The
observable pattern is that weeks four and five of a sustained push produce
noticeably worse output than weeks one and two, and the deficit surfaces as
rework rather than as visibly less output — which is why it goes unnoticed.

Plan four days at target and one lighter day. The lighter day is not lost
capacity; it is what keeps the other four at full quality.

---

## 9. Matching block type to work type

Not all cognitive work needs the same block shape. Applying one template to all
of it wastes the most valuable slots on work that did not need them.

| Work type | Ideal block | Notes |
|---|---|---|
| **Novel problem-solving** — architecture, strategy, debugging something genuinely unknown | 120-180 min | The only category that truly needs long blocks; the insight usually arrives past the 60-minute mark |
| **Writing from scratch** | 90-120 min | Long enough to find the structure; past 120 min quality typically declines |
| **Editing and revision** | 45-90 min | Bounded scope, resumable, lower warmup cost |
| **Learning something new** | 60-90 min | Retention drops past 90 min; spacing beats duration |
| **Detailed execution** — known task, known method | 45-60 min | Problem state is already externalised |
| **Review queues** — code review, document feedback | 30-45 min | Genuinely batchable shallow work; do not spend a prime block on it |
| **Planning and decomposition** | 30-45 min | Short by design; if it runs long, the underlying problem is not yet understood |

**[PROVEN] Spend your best block on novel problem-solving, not on execution.**
The most common misallocation is using the protected morning block to clear
well-defined work because it feels productive and finishes cleanly, then
attempting the hard architectural problem at 16:00 when it has no chance. The
work that most needs a long, fresh block is exactly the work that is easiest to
postpone, because its completion is unclear and its progress is unmeasurable.

---

## 10. Attention residue

When you switch from task A to task B, part of your attention remains on A —
particularly when A was left unresolved. This residue degrades performance on B
for a period well beyond the switch itself, and it explains several otherwise
puzzling observations:

- A 15-minute meeting inserted into a block costs far more than 15 minutes
- Checking email *before* a block reliably degrades the block, even though no
  time was taken from it
- Ending a session at an unresolved point makes the *next* session start faster
  (useful residue) but makes the intervening break less restorative (costly
  residue)

### Practical implications

| Situation | Implication |
|---|---|
| Meeting immediately before a block | Leave 15 minutes of buffer; the block otherwise starts with residue from the meeting |
| Email before a block | Do not. One message with an unresolved problem contaminates the entire block |
| Unavoidable interruption mid-block | Write down where you were *before* handling it — this externalises the state and shortens re-entry |
| Switching between two projects in a day | Batch by project across days rather than alternating within a day |
| End of a session | Stop mid-thought for cheap re-entry, but write the close-out note so the residue is on paper rather than in your head |

The close-out note resolves a genuine tension: stopping mid-thought reduces
tomorrow's warmup, but leaving the thought unresolved carries residue into your
evening. Writing it down gets both — the entry point is preserved externally,
and your mind is released from holding it.

---

## 11. Building the capacity

Deep-work capacity behaves like physical training: it responds to progressive
load and it decays without use. People who attempt three-hour blocks on day one
generally fail, conclude they "can't focus," and stop.

### A twelve-week progression

| Weeks | Daily target | Focus of the practice |
|---|---|---|
| 1-2 | One 45-min block | Establishing the slot and the ritual, not the duration |
| 3-4 | One 60-min block | Holding the block without checking anything |
| 5-6 | One 90-min block | First genuinely viable block; expect the last 20 min to be hard |
| 7-8 | One 90-min + one 45-min | Learning that the second block is weaker, and planning for it |
| 9-10 | One 120-min block | The default target shape |
| 11-12 | 120-min + 60-min | A sustainable adult practice |

**Progress the duration only when the current length is comfortable for four
consecutive sessions.** Advancing on schedule rather than on readiness produces
failed sessions, and failed sessions are what kill the habit — not difficulty.

### What improves, and what does not

Improving with practice: time-to-immersion, tolerance for the discomfort of a
hard problem, resistance to self-interruption, accuracy of session planning.

Not improving with practice: the daily ceiling (roughly 3-4 hours for nearly
everyone, regardless of experience), and the cost of external interruption.
Those are structural. No amount of training makes a fragmented calendar work —
which is why defence, covered in the companion reference, matters more than
personal discipline.
