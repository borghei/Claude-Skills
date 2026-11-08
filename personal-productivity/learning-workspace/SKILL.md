---
name: learning-workspace
description: >
  Set up and run a multi-session study workspace with mission, curriculum,
  lessons and spaced review. Use when learning a topic over weeks, resuming
  study after a gap, checking real understanding, or planning reviews.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: personal-productivity
  domain: personal-effectiveness
  updated: 2026-11-08
  python-tools: workspace_scaffolder.py, review_scheduler.py
  tech-stack: spaced-repetition, retrieval-practice, curriculum-design
  tags: [learning, spaced-repetition, curriculum, retrieval-practice, self-study, tutoring]
---

# Learning Workspace

Most self-study fails between sessions: the next one starts cold, re-teaches what stuck,
skips what didn't, and mistakes a smooth lesson for learning. This skill keeps the
learner's state in plain files — mission, curriculum, numbered lessons and a learning
record — so any session can resume exactly where the last one ended.

The agent acts as the teacher: one idea per lesson, tied to the mission, opened with
retrieval of due items; it records only what the learner has demonstrated.

## When to Use

- Learning a topic over weeks, not answering a one-off question
- Resuming study after a gap
- The learner says "I get it" but cannot apply the idea a week later
- Planning which items to review today and which module comes next

## Clarify First

The mission shapes every lesson choice, so settle it before teaching anything. When an
input is missing or vague and would change the result, ask about it; when it wouldn't,
use a sensible default and say which one you used.

- **The real reason:** "to understand statistics" gives no way to pick the next lesson; "size my own experiments" does.
- **Observable success criteria:** they decide when a module, and the mission, is done.
- **Session length and frequency:** they size each lesson and the review load.
- **Claimed prior knowledge:** it sets the starting point; lesson 1 verifies it.

Ask about the two or three inputs that matter most for this request, not the whole list.
If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

```bash
# Gate a spec, then scaffold the workspace (refuses to overwrite without --force)
python3 personal-productivity/learning-workspace/scripts/workspace_scaffolder.py \
  --input personal-productivity/learning-workspace/assets/sample_workspace_spec.json \
  --output-dir ~/learning/ab-testing-stats
```

```bash
# Before each session: due reviews, resume brief, honesty gate
python3 personal-productivity/learning-workspace/scripts/review_scheduler.py \
  --input personal-productivity/learning-workspace/assets/sample_learning_record_clean.json \
  --today 2026-11-08
```

## Tools Overview

| Tool | Reads | Produces |
|---|---|---|
| `workspace_scaffolder.py` | Spec JSON | Gate findings, then the workspace files and lesson 0001 |
| `review_scheduler.py` | learning-record.json | Next review per item, due list, resume brief, gate findings |

Both take `--format text|json`; the scheduler's `--today` keeps runs reproducible.

### Exit code contract

| Code | Scaffolder | Scheduler |
|---|---|---|
| 0 | Spec valid (files written if `--output-dir`) | Record passes the gate |
| 1 | Vague why, unobservable criteria, broken modules | Unearned `secure`, missing evidence, future review, unrechecked misconception |
| 2 | Unreadable input, or files exist without `--force` | Unreadable or malformed record |

```bash
# Flawed record: exits 1 by design
python3 personal-productivity/learning-workspace/scripts/review_scheduler.py \
  --input personal-productivity/learning-workspace/assets/sample_learning_record.json --today 2026-11-08
```

## Workflow

### Session zero — set up the workspace [RECOMMENDED]

1. Interview for the mission until the answer is an outcome, not a topic.
2. Turn it into 2–4 observable success criteria ("could someone watch me do it?").
3. Draft 4–8 modules in dependency order, each with an observable outcome.
4. Find resources before teaching: at least one primary source and one community.
5. Write the spec, run the scaffolder, fix every error. This is the setup quality gate.

### Run a lesson [PROVEN]

1. Run the scheduler; read the resume brief and warm-up list.
2. Pick one win at the edge of what is `secure`, tied to a success criterion.
3. Warm-up: retrieval of due items, no notes; the learner self-grades each.
4. Teach one idea from a cited source, ask for a prediction, show a worked example.
5. Practice with faded examples and immediate feedback.
6. Exit check with two check types (explain-back plus transfer).
7. Update the record and re-run the scheduler; the gate must pass before closing.

### Check understanding [PROVEN]

Use two or more check types per lesson; any single one can be passed on fluency alone.
A confident wrong answer is a misconception: let the prediction fail, give the
replacement model, record it with a recheck date 2–5 days out.

| Answer | Meaning | Record |
|---|---|---|
| Correct, fast, own words | Learned today | Evidence; schedule review |
| Correct with hints | Partly formed | `partial` |
| Right words, cannot apply | Fluency without a model | No evidence yet |
| Confident and wrong | Misconception | Open misconception + recheck |

### Resume after a gap [RECOMMENDED]

1. Run the scheduler. `restart_mode: rebuild` (21+ days) means no new material: retrieve
   everything due, re-teach failures, recheck misconceptions.
2. Re-read the mission with the learner; long gaps often mean the goal moved.

Spacing: intervals grow 1 → 3 → 7 → 14 → 30 → 60 → 120 days; a failure resets, a partial
repeats the step. `secure` needs three spaced recalls including a 5+ day gap. Validate
the record after every session with the lesson template's checklist.

## Anti-Patterns

### Teaching the Topic Instead of the Mission
**Mistake:** Working through a textbook's table of contents because the learner said "teach me statistics".
**Why it happens:** The topic is easy to name; the reason takes questioning to surface.
**Instead:** Get the outcome first; cut every module that moves no success criterion.

### Mistaking a Smooth Lesson for Learning
**Mistake:** Marking concepts understood because the learner followed along and nodded.
**Why it happens:** Fluency during a lesson feels exactly like mastery.
**Instead:** Record evidence only from production tasks, and mark `secure` only after spaced recall. The scheduler fails `secure` items without a spaced streak.

### Correcting a Misconception Once
**Mistake:** Stating the right answer and moving on.
**Why it happens:** The learner agrees, so it looks fixed.
**Instead:** Record it as open with a recheck date and test it later on a new surface. Misconceptions come back under pressure.

### Teaching From Memory
**Mistake:** Building lessons from recall with no source.
**Why it happens:** It is faster.
**Instead:** Cite a primary resource in each lesson and point the learner to it next.

## Files

| File | Purpose |
|---|---|
| `scripts/` | The scaffolder and the review scheduler |
| `assets/lesson-template.md` | Lesson plan with timings and the after-lesson checklist |
| `assets/learning-record-entry-template.md` | JSON snippets for items, reviews, misconceptions, sessions |
| `assets/sample_*.json` | Clean (exit 0) and flawed (exit 1) specs and records |

## Reference Documentation

- [references/learning-science.md](references/learning-science.md) — retrieval, spacing, load, fading, misconceptions; read when designing a lesson.
- [references/workspace-formats.md](references/workspace-formats.md) — every file's format and the record schema; read when a tool rejects a file.
- [references/session-playbook.md](references/session-playbook.md) — setup, lesson, check and resume scripts; read at session start.

## Scope & Limitations

**In Scope:** mission and success-criteria design; dependency-ordered curricula; one-idea
lessons with retrieval warm-ups and faded practice; understanding checks and misconception
handling; a spaced review schedule; resuming from files alone.

**Out of Scope:**
- Reflection into behaviour change: `personal-productivity/reflect/`.
- Protecting study time: `personal-productivity/deep-work/`.
- Literature reviews: `research/litreview/`.

**Important Caveats:**
- The tools read files the learner keeps; they cannot see whether a grade was honest.
- The interval ladder is a sound default, not a personal memory model; compress it for a hard deadline.
- Vague-language checks are keyword heuristics.
