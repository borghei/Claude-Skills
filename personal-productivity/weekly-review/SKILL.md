---
name: weekly-review
description: >
  Synthesize a week of inputs (calendar, tasks, journal, OKR check-ins) into
  a structured weekly review with wins, learnings, blockers, and next-week
  priorities. Use every Friday or Sunday, or when the user mentions weekly
  review, GTD review, OKR check-in, or end-of-week reflection.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: personal-productivity
  domain: personal-effectiveness
  updated: 2026-05-04
  python-tools: weekly_review_synthesizer.py
  tech-stack: GTD, OKRs, productivity
---

# Weekly Review

Synthesize a week into a structured review covering wins, learnings, blockers, and next-week priorities.

---

## Keywords

weekly review, GTD, getting things done, OKR check-in, retrospective, weekly retro, journal, reflection, end of week, EOW

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
4. Adjust cadence, cadence, or commitments based on patterns

**Time Estimate:** 1-2 hours quarterly.

---

## Tools

### weekly_review_synthesizer.py

Reads structured weekly input JSON and produces a markdown weekly review.

```bash
python scripts/weekly_review_synthesizer.py input.json
python scripts/weekly_review_synthesizer.py input.json --json
```

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
