---
name: weekly-review
description: >
  Turn a week's wins, learnings, blockers and OKR progress, gathered by hand
  from your calendar, tasks and journal, into a structured review with
  next-week priorities. Use for a Friday/Sunday weekly review, GTD review, or
  OKR check-in.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: personal-productivity
  domain: personal-effectiveness
  updated: 2026-05-04
  python-tools: weekly_review_synthesizer.py
  tech-stack: GTD, OKRs, productivity
  tags:
    - weekly-review
    - reflection
    - planning
    - productivity
    - okrs
---

# Weekly Review

Turn a hand-filled summary of the week into a structured review covering wins, learnings, blockers, OKR progress and next-week priorities.

---

## Keywords

weekly review, GTD, getting things done, OKR check-in, retrospective, weekly retro, journal, reflection, end of week, EOW

---

## Clarify First

Before synthesizing the review, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **The week's raw inputs:** actual wins, learnings, and blockers; this is the content the review synthesizes, not invented.
- **OKR / goal progress:** current numbers vs target drives the check-in section and flags drift.
- **Next-week priorities:** the top 1-3 commitments the review must end on.

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

---

## Quick Start

1. Fill in `assets/weekly_review_input.json` with the past week's wins, learnings, blockers, OKR progress
2. Run: `python scripts/weekly_review_synthesizer.py weekly_review_input.json`
3. Save the output as your week's review

---

## Core Workflows

### Workflow 1: Standard Friday Review (30 min)
1. Capture 3-5 wins from the past week
2. Capture 1-3 learnings (what surprised you, what you got wrong)
3. Capture top 1-3 blockers / risks for next week
4. Update OKR / goal progress
5. List top 3 priorities for next week
6. Run synthesizer

**Time Estimate:** 30-45 minutes weekly.

### Workflow 2: Bootstrap (First Time)
1. Read `references/weekly_review_methodology.md`
2. Decide cadence (Friday afternoon vs Sunday evening — both work)
3. Block 30-45 min recurring on calendar
4. Use input template; tune over 4 weeks until format works for you

**Time Estimate:** 1 hour to set up; 30-45 min weekly thereafter.

### Workflow 3: Quarterly Pattern Review
1. Save weekly reviews in a single folder
2. Quarterly: read all 12-13 weeks
3. Look for patterns: recurring blockers, energy patterns, OKR drift
4. Adjust cadence, priorities, or commitments based on patterns

**Time Estimate:** 1-2 hours quarterly.

---

## Tools

### weekly_review_synthesizer.py

Renders a hand-filled weekly input JSON as a markdown weekly review. It formats what you entered, adds item counts and self-coach prompts, and does no analysis. `--json` prints the input back as JSON, not a review.

```bash
python scripts/weekly_review_synthesizer.py input.json
python scripts/weekly_review_synthesizer.py input.json --json
```

---

## Scope & Limitations

**In Scope:**
- A markdown weekly review rendered from a hand-filled JSON input (`assets/weekly_review_input.json`) by `weekly_review_synthesizer.py`.
- Sections for wins, learnings, blockers, OKR or goal progress, and next-week priorities.
- GTD weekly review and OKR check-in methodology in `references/weekly_review_methodology.md`.
- Friday review, first-time setup and quarterly pattern review workflows.

**Out of Scope:**
- Pulling inputs from calendars, task tools, journals or OKR software. All content is typed into the JSON.
- Scoring judgement and tracking commitments across quarters (see `personal-productivity/reflect/`).
- Writing OKRs (see `project-management/execution/brainstorm-okrs/`).
- Team retrospectives (see `project-management/sprint-retrospective/`).
- Processing the capture inbox (see `personal-productivity/capture/`).

**Important Caveats:**
- The synthesizer formats the input. It does not analyse it, detect patterns or judge OKR drift.
- The `--json` flag echoes the input rather than producing a JSON review.
- The quarterly pattern review is a manual read of saved reviews. No tool aggregates weeks.

---

## Reference Guides

- **`references/weekly_review_methodology.md`** — GTD weekly review, OKR check-in patterns, common pitfalls

---

## Templates

- **`assets/weekly_review_input.json`** — Input template

---

## Best Practices

- **Block the time.** 30 min recurring; defend against rescheduling.
- **Same time each week.** Habits stick when the trigger is consistent.
- **Capture the pattern, not the noise.** Weekly review is a layer above the moment-to-moment task list.
- **OKR check-in over chase.** Weekly OKR progress is signal; quarterly is the action moment.
- **Compound across weeks.** Reviews are most useful when read in batches.
- **Don't over-format.** A messy review you actually do beats a perfect one you skip.
