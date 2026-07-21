---
name: capture
description: >
  Build a trusted capture-and-triage front door so no commitment lives in your
  head. Use when open loops keep slipping, an inbox has become a backlog, or
  vague notes never turn into action.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: personal-productivity
  domain: personal-effectiveness
  updated: 2026-07-21
  tags: [capture, triage, inbox-zero, next-action, gtd]
---

# Capture

A reliable front door for every commitment, idea, and open loop — and a
processing pass that empties it. Capture is cheap and fails silently: you never
notice the thought you didn't record, only the dropped commitment weeks later.
This skill covers the capture conventions, the triage decision rules that
convert fragments into executable next actions, and the weekly pass that keeps
the inbox at zero.

## When to use this skill

- Commitments keep slipping and you are discovering them from other people's follow-ups
- Your notes app, task inbox, and paper notebook have all become backlogs nobody drains
- The same items get reviewed week after week and never get done
- You are rebuilding a productivity system that collapsed and want the load-bearing part first
- Captured items are phrased as topics (`pricing`, `taxes`) rather than actions
- You want to measure whether the capture habit is actually working, not assume it

## Inputs the skill expects

- A capture log — JSON with `text` and ideally `captured_at`, or a markdown bullet list
- The set of surfaces you currently capture into (phone, notebook, email, chat)
- Which single place you intend to use as the processing inbox
- Your current weekly processing slot, if one exists
- A reference date for staleness analysis (passed explicitly — the tools never read the clock)

## Clarify First

Before generating, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Which inbox is the processing inbox** — the whole design collapses if items drain to more than two places
- [ ] **Whether the log carries capture timestamps** — without them, staleness and habit-health analysis are unavailable and the audit degrades to phrasing only
- [ ] **Whether a weekly processing slot already exists** — determines whether this is a setup job or a repair job
- [ ] **Tolerance for dropping items** — sets how aggressive the drop recommendations are; some users need permission, others need a brake

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Workflows

### Workflow 1 — Triage the inbox into buckets with next actions

Run this at the start of every weekly pass. It does the mechanical sorting so
your judgement is spent on the genuinely ambiguous items.

1. Drain every capture surface into one file (JSON or markdown bullets).
2. Run the triage tool with today's date so ageing is computed.
3. Do the flagged 2-minute items immediately, before filing anything else.
4. Rewrite every item flagged `no-verb` or `unactionable-phrasing` using the
   grammar `<concrete verb> <specific object> <qualifier>`.
5. Move each remaining item to its destination — actions, projects, calendar,
   waiting-for, reference, someday, or the bin.

```bash
python3 personal-productivity/capture/scripts/capture_triage.py \
  --input personal-productivity/capture/assets/sample_capture_log.json \
  --today 2026-07-21
```

Filter to one bucket when working a single destination at a time:

```bash
python3 personal-productivity/capture/scripts/capture_triage.py \
  --input personal-productivity/capture/assets/sample_capture_log.json \
  --today 2026-07-21 --bucket project --format json
```

### Workflow 2 — Audit whether the capture habit is real

Monthly. Answers a different question from triage: not "what is in the inbox"
but "is this system actually working."

1. Run the audit against the full log with a reference date.
2. Read the status line — `healthy`, `at-risk`, or `failing` — and the verdict,
   which names the dominant failure (processing vs phrasing).
3. Check the source breakdown for the leakiest capture surface.
4. Fix exactly one thing before the next month: either restore the processing
   pass, or fix the phrasing habit. Not both — they need different attention.

```bash
python3 personal-productivity/capture/scripts/capture_audit.py \
  --input personal-productivity/capture/assets/sample_capture_log.json \
  --today 2026-07-21
```

Tighten the staleness threshold if you process more than weekly:

```bash
python3 personal-productivity/capture/scripts/capture_audit.py \
  --input personal-productivity/capture/assets/sample_capture_log.json \
  --today 2026-07-21 --stale-days 7 --format json
```

### Workflow 3 — Run the weekly inbox-zero pass

The load-bearing habit. 45 minutes, same slot weekly, defended like a meeting
with someone you respect.

1. Open `assets/weekly-processing-pass.md` and work down it.
2. Gather from every surface (5 min), then triage (5 min).
3. Process every item one at a time without skipping (20 min) — skipping is how
   items become permanently stale.
4. Review projects for missing next actions (8 min), then waiting-for items (5 min).
5. Record the outcome counts on the checklist. Watch the drop rate specifically:
   below 15% means you are filtering too early at capture time.

```bash
mkdir -p build
python3 personal-productivity/capture/scripts/capture_triage.py \
  --input personal-productivity/capture/assets/sample_capture_log.json \
  --today 2026-07-21 --format json > build/triaged.json
```

## Decision frameworks

### The processing sequence

Apply in this order for every item. The order prevents the most common error —
doing a 90-second task that should have been deleted.

| Step | Question | If no | If yes |
|---|---|---|---|
| 1 | Is it actionable? | Reference, someday, or **drop** | Continue |
| 2 | What does done look like? | It is a decision, not a task | Continue |
| 3 | One step only? | Project + define first action | Action |
| 4 | Under 2 minutes? | Continue | Do it now |
| 5 | Am I the right person? | Delegate + follow-up date | Continue |
| 6 | Date-specific? | Next-actions list | Calendar |

### Do / defer / delegate / drop

| Decision | Test | [PROVEN] threshold |
|---|---|---|
| **Do** | Under 2 min and you are in processing mode | 2 min — filing plus re-contextualising exceeds the task past this point |
| **Defer** | Yours, over 2 min, no one else can do it | Costs a list slot and a weekly re-read, forever |
| **Delegate** | Someone else is better placed | Always creates a waiting-for entry with a date — 3 working days for same-week items, 1 week otherwise |
| **Drop** | No meaningful consequence if never done | Survived 3 weekly reviews with no progress = drop it; that is a decision, so record it as one |

**Drop is the most under-used outcome and the highest-leverage one.** A healthy
pass drops 15-25% of items. Below that you are filtering at capture time, which
uses exactly the tired, distracted judgement that capture exists to protect you
from.

### Habit-health thresholds

| Metric | Healthy | Warning | Broken |
|---|---|---|---|
| Median inbox age | < 7 days | 7-14 days | > 14 days |
| Share older than 14 days | < 20% | 20-40% | > 40% |
| Share with no concrete verb | < 25% | 25-50% | > 50% |
| Inbox size after a pass | 0-3 | 4-10 | > 10 |
| Capture latency (locked phone to saved text) | < 2 sec | 2-5 sec | > 15 sec — you are running on memory |

### Converting a vague capture

Two questions unstick anything. `[PROVEN]`

1. **"What does done look like?"** → produces the outcome. No one-sentence
   answer means it is a project, or an undecided commitment.
2. **"What is the very next physical thing I would do?"** → produces the action.
   The honest answer is usually smaller than expected and often
   information-gathering: find the file, ask the question, check the constraint.

If both fail, it is not a task but an unmade decision. File it as
`Decide whether to X by <date>`.

## Anti-Patterns

### The Multi-Inbox System
**Mistake:** Capturing into six places and reviewing all six, so no single review ever produces the feeling of having seen everything.
**Why it happens:** Each surface was added for a good local reason — voice memos for the car, a notebook for meetings, chat-to-self for links. Nobody decides to have six inboxes; they accumulate.
**Instead:** Keep as many capture *surfaces* as you need, but exactly one *processing* inbox (two at the outside, when email is unavoidable). Every surface must drain into it. List every place an unprocessed commitment can currently live, and for each decide: drains into the primary, or is the primary. Anything else gets closed.

### Filtering at Capture Time
**Mistake:** Deciding whether something is worth capturing before writing it down, to keep the list manageable.
**Why it happens:** A long list feels like failure, so people self-censor. It sounds like discipline.
**Instead:** Capture with zero filtering and filter hard at processing. The judgement you apply mid-meeting or half-asleep is exactly the judgement capture exists to bypass. If your processing pass drops nothing, that is the tell — you are pre-filtering, and the items you silently discard are the small commitments whose loss damages trust most.

### The Permanent Almost-Task
**Mistake:** Leaving items phrased as topics or mental states — `pricing`, `follow up with Sam`, `think about the roadmap` — and reviewing them week after week.
**Why it happens:** The phrasing feels sufficient at capture time because the full context is still in your head. It evaporates within days, leaving a fragment that reads as a task but cannot be executed.
**Instead:** Enforce the grammar `<concrete verb> <specific object> <qualifier>`, where the verb names something physically visible. "Decide," "handle," and "follow up" fail the test. Run `capture_triage.py` and rewrite everything it flags `no-verb` — those are the items your mind has been quietly skipping at every review.

### Triaged But Not Empty
**Mistake:** Reading through the whole inbox during the weekly pass, feeling current, and leaving the items in place.
**Why it happens:** Reading is fast and feels like progress; deciding is slow and each decision has a small cost. Under time pressure, review substitutes for processing.
**Instead:** Inbox zero means every item has physically left the inbox for a specific destination. Items remaining after a pass have had a decision deferred, and the same decision will be deferred next week — that is precisely how a five-item inbox becomes a fifty-item one. If the backlog is genuinely too large, declare bankruptcy on anything over 60 days old and archive it wholesale rather than skipping the pass.

## Files

| File | Purpose |
|---|---|
| `scripts/capture_triage.py` | Sorts a capture log into action / project / reference / someday / drop, suggests a next action per item, flags 2-minute tasks and unactionable phrasing |
| `scripts/capture_audit.py` | Scores capture-habit health — staleness, rot, phrasing quality, source leaks — and names the dominant failure mode |
| `references/capture-conventions.md` | Friction budget, capture-surface ranking, the one-inbox principle, metadata worth recording, how trust is lost |
| `references/triage-decision-rules.md` | Processing sequence, 2-minute rule constraints, do/defer/delegate/drop tests, vague-to-actionable conversion, weekly pass mechanics |
| `assets/weekly-processing-pass.md` | Timed 45-minute checklist for the weekly inbox-zero pass with outcome-count targets |
| `assets/capture-log-template.md` | Capture-log format, quality reminders, and the JSON schema the scripts read |
| `assets/sample_capture_log.json` | 14-item sample log exercising every bucket and flag, so both workflows run out of the box |
