---
name: deep-work
description: >
  Protect, design, and measure focused work — block defence, session structure,
  interruption budgets, and deep-work ratio. Use when the calendar is fragmented,
  focus blocks keep getting eaten, or output has stalled.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: personal-productivity
  domain: personal-effectiveness
  updated: 2026-07-21
  tags: [deep-work, focus, calendar, fragmentation, interruptions]
---

# Deep Work

Blocking time on a calendar is the easy half; making the time inside the block
convert into output is the hard half. This skill covers both — measuring how
badly meetings fragment your week, defending blocks against encroachment, and
designing sessions so that protected time produces a finished artefact rather
than a warm feeling.

## When to use this skill

- Your calendar looks manageable in total meeting hours but no real work gets done
- Focus blocks exist but keep getting moved, split, or quietly cancelled
- You need to argue for protected time and want fragmentation data rather than a preference
- Sessions happen but produce fragments — nothing reaches a finished state
- You want to know whether your deep-work practice is improving or decaying over months
- A 30-minute meeting keeps landing in the middle of your only long block

## Inputs the skill expects

- A calendar export as JSON — `date`, `start`, `end`, `title`, optional `fixed` flag
- Your working-window hours (defaults to 09:00-17:00)
- Your role, which sets a realistic deep-work ratio target (40-60% IC, 20-30% manager)
- A session log with `date` and `actual_min`, ideally `interruptions` and `artefact`
- Your current weekly deep-work target in minutes, set from logged history rather than aspiration

## Clarify First

Before generating, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Role and realistic target ratio** — the 0.40 default is an IC figure and will flag every manager's calendar as failing, which is noise not signal
- [ ] **Which meetings are genuinely immovable** — the `fixed` flag determines whether a reschedule proposal is actionable or fantasy
- [ ] **Working-window hours** — a 9-5 window on someone who works 07:00-15:00 produces meaningless ratios
- [ ] **Whether the goal is diagnosis or advocacy** — arguing for protected time leads with recovery cost; personal tuning leads with block length

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Workflows

### Workflow 1 — Diagnose calendar fragmentation and get a reschedule

Run weekly against the coming week, before it fills up.

1. Export the calendar to JSON with `date`, `start`, `end`, `title`.
2. Mark genuinely immovable events with `"fixed": true` — the search skips them.
3. Run the analyser with your role's target ratio.
4. Read the per-day table: any day with a longest block under 90 minutes
   produced no substantive individual work, whatever your output log says.
5. Make the one move it proposes. One move per week is politically sustainable;
   a wholesale calendar rewrite is not.

```bash
python3 personal-productivity/deep-work/scripts/calendar_fragmentation.py \
  --input personal-productivity/deep-work/assets/sample_calendar.json \
  --target 0.40
```

For a manager's calendar with a longer working window and a role-appropriate
target — the same file scored at the 0.40 IC default reads as failing on 14 of
20 days, which is target miscalibration rather than a real finding:

```bash
python3 personal-productivity/deep-work/scripts/calendar_fragmentation.py \
  --input personal-productivity/deep-work/assets/sample_calendar_manager_4weeks.json \
  --day-start 08:00 --day-end 18:00 --min-block 90 --target 0.25
```

### Workflow 2 — Track whether the practice is improving

Monthly, not weekly. Weekly volume is noisy enough that reacting to it produces
thrashing.

1. Log each session at close-out using `assets/session-log-template.md`.
2. Run the analyser with a weekly target set from your own logged history.
3. Read the trend line — a change over 10% between the first and second half of
   the period is real; anything less is noise.
4. Read the findings, which name specific structural failures rather than
   general encouragement.
5. Fix exactly one thing. Volume, block length, and defence are three different
   problems; working all three at once teaches you nothing about which mattered.

```bash
python3 personal-productivity/deep-work/scripts/session_log_analyzer.py \
  --input personal-productivity/deep-work/assets/sample_sessions.json \
  --weekly-target 600
```

### Workflow 3 — Make the case for protected time

When you need a manager or team to concede structural change.

1. Export two to four weeks of calendar history and run the fragmentation tool.
2. Lead with the **recovery cost** figure, not the meeting-hours figure.
   "Meetings take 9 hours a week" invites a debate about which meetings matter;
   "fragmentation costs another 6 hours a week in re-immersion, on top of the
   meetings" reframes it as waste.
3. Show the count of days with zero viable blocks.
4. Propose the specific single move the tool identifies — concrete, small, and
   reversible asks get agreed; general ones get sympathy.
5. Re-run after four weeks and report the delta. The follow-up measurement is
   what turns a one-off concession into a standing arrangement.

```bash
mkdir -p build
python3 personal-productivity/deep-work/scripts/calendar_fragmentation.py \
  --input personal-productivity/deep-work/assets/sample_calendar_manager_4weeks.json \
  --target 0.40 --format json > build/fragmentation.json
```

## Decision frameworks

### Block length vs usable output

| Block | Warmup share | Verdict |
|---|---|---|
| 25 min | ~70% | Pre-defined execution only. Not deep work. |
| 45 min | ~40% | Marginal — works only when resuming something touched hours ago |
| **90 min** | ~20% | **[PROVEN] Minimum viable block.** Warmup amortises; one real problem gets solved |
| 120 min | ~15% | The default target — depth without quality decay |
| 180 min | ~10% | Excellent for absorbing work; needs a real break after |
| 240+ min | ~8% | Diminishing returns; split it |

Problem-state reload costs 15-20 minutes and is paid on every re-entry. This is
why five 30-minute gaps are not equivalent to one 150-minute block — the gaps
yield close to zero.

### Interruption budget

Each interruption costs roughly **23 minutes** of degraded output, not the
duration of the interruption. `[PROVEN]`

| Interruptions/hour | Effective output | Verdict |
|---|---|---|
| 0 | ~100% | The block is real |
| 0.5 | ~80% | Acceptable — the practical target |
| 1.0 | ~60% | Ceiling. Above this, blocked but not defended |
| 2.0 | ~30% | Shallow work in a room labelled deep work |
| 3+ | ~10% | Move the slot; this one cannot be defended |

Set the budget one step below your measured rate, never at zero — zero is
unachievable in most roles and failing it immediately kills the practice. Define
the consequence in advance: exceeding the budget means **reschedule the block**,
not push through. Pushing through teaches you that protected time yields shallow
work, which is the belief you are trying to disprove.

### Role-calibrated targets

| Role | Deep-work ratio | Daily sustainable |
|---|---|---|
| IC — engineer, writer, analyst, designer | 40-60% | 2-4 h |
| Senior IC / tech lead | 30-40% | 2-3 h |
| Team manager | 20-30% | 1-2 h, two blocks a week |
| Director+ | 10-20% | Defended pockets |
| On-call rotation | 0-10% | Do not schedule deep work into a rotation |

**Most people sustain 3-4 hours of genuine deep work per day as an upper bound.**
Beyond that the work continues but the quality does not, and the deficit shows
up as needing to redo it.

### Session design rules `[PROVEN]`

| Rule | Why |
|---|---|
| Pre-commit the artefact the night before | Deciding inside the block burns your freshest attention on a decision you could make while tired |
| One session, one artefact — not one project | Two artefacts means paying warmup twice and finishing neither |
| Stop mid-thought at close-out | An unfinished sentence halves tomorrow's warmup; finishing cleanly feels better and costs more |
| No 2-minute tasks inside the block | The 2-minute rule is a processing-mode rule; here it costs the task plus 23 minutes of re-entry |
| Place blocks at a day boundary | A midday block has two exposed edges and collects meetings on both |

## Anti-Patterns

### Blocking Time Without Defending It
**Mistake:** Putting recurring "Focus time" on the calendar, then moving or shortening it whenever anyone asks.
**Why it happens:** The block is self-imposed, so it feels like the one commitment with no external cost to breaking. Each individual concession is genuinely reasonable.
**Instead:** Name the block after the actual work (`Migration RFC — drafting`), set it busy rather than free, and place it at a day boundary so it has one exposed edge instead of two. When it must move, move it the same day — "sometime this week" means never. Track how often you move it; a block that relocates weekly is not a block, it is a preference.

### Conceding the 30-Minute Wedge
**Mistake:** Accepting a short meeting into the middle of a long block because giving up 30 minutes seems like a small concession.
**Why it happens:** The arithmetic of block splitting is invisible. Losing 30 minutes from 120 looks like a 25% cost.
**Instead:** Recognise that it costs the whole block — two 45-minute halves are both under the viable threshold, so the real loss is 120 minutes, not 30. Counter with placement rather than refusal: "Can we put it against the 11:00 meeting so the morning stays whole?" Scheduling people have one slot to fill and no visibility into what they are displacing; naming the cost converts an invisible loss into a visible tradeoff, and most people adjust.

### Deciding What to Work On Inside the Block
**Mistake:** Arriving at a protected block and spending the first 20 minutes choosing what to do with it.
**Why it happens:** The block was defended as generic focus time rather than committed to a specific artefact, so the decision has nowhere else to live.
**Instead:** Write one line the night before: "Tomorrow 09:30-11:30 I will work on `<artefact>` until `<observable state>`." If you cannot name an observable done-state, the work is not ready for a deep block — it needs a planning pass first, which is itself a legitimate and much shorter session.

### Measuring Hours Blocked Instead of Work Done
**Mistake:** Tracking calendar time reserved for deep work and treating a full-looking week as a successful one.
**Why it happens:** Blocked hours are trivially countable; actual focus is not. The metric that is easy to collect displaces the one that matters.
**Instead:** Log `actual_min`, `interruptions`, and the single `artefact` per session, then run `session_log_analyzer.py`. Plan-vs-actual drift over 20% and interruption rates above 1.0/hour are the two numbers that predict whether the habit survives — and both are invisible if you only count what the calendar reserved.

## Files

| File | Purpose |
|---|---|
| `scripts/calendar_fragmentation.py` | Per-day longest block, context-switch count, deep-work ratio vs target, plus a searched single-meeting reschedule proposal |
| `scripts/session_log_analyzer.py` | Weekly volume rollup, session-length distribution, interruption rate, plan-vs-actual drift, single-artefact adherence, and trend detection |
| `references/focus-block-design.md` | Block-length economics, daily ceilings, four-part session structure, placement by chronotype, interruption budgeting, diagnostic table |
| `references/defending-focus-time.md` | Encroachment patterns, calendar mechanics ranked by social cost, decline scripts, self-encroachment, role-calibrated targets, making the data case |
| `assets/session-log-template.md` | Pre-commitment prompt, session-entry schema, close-out checklist, monthly review table |
| `assets/sample_calendar.json` | Five-day IC calendar with one heavily fragmented day, so the reschedule search has something to find |
| `assets/sample_calendar_manager_4weeks.json` | 104 events over 20 working days of a meeting-dense manager calendar — drives the role-calibrated target example and the four-week advocacy export |
| `assets/sample_sessions.json` | Four weeks of sessions with a visible improving trend and two failed sessions, exercising every finding |
