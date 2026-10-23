---
name: investor-update-generator
description: >
  Validate a monthly investor update against a rubric of strong-update
  sections (transparency, decision-relevance, specific asks). Use before
  sending a monthly investor update or setting a fundraise communication cadence.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: personal-productivity
  domain: investor-relations
  updated: 2026-05-04
  python-tools: investor_update_validator.py
  tech-stack: investor-relations, fundraising
  tags:
    - investor-update
    - fundraising
    - founders
    - reporting
---

# Investor Update Generator

Write a monthly investor update and check it against a rubric of what makes updates work. The assistant writes the draft, starting from `assets/investor_update_template.md` and your metrics, asks and news. The one tool, `investor_update_validator.py`, does not generate text: it only scores a finished draft against the rubric.

---

## Keywords

investor update, monthly update, founder update, investor communication, fundraise, lead investor, board, KPIs, asks

---

## Clarify First

Before generating the update, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Stage & cadence:** early-stage monthly vs later-stage quarterly changes which sections the rubric expects.
- **This period's metrics:** the same defined set every month; re-defining metrics signals dishonest reporting.
- **Specific asks:** what you need from investors (intros, hires, advice); the highest-leverage section.
- **Bad news / risks:** strong updates lead with these, so they must be surfaced, not buried.

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

---

## Quick Start

1. Draft your update as `update.md`
2. Run: `python scripts/investor_update_validator.py update.md`
3. Address any missing sections; aim for the rubric score > 80

OR start from scratch with `assets/investor_update_template.md`.

---

## Core Workflows

### Workflow 1: Monthly Update Production
1. First of month: pull metrics dashboard, last update, current asks
2. Draft against `assets/investor_update_template.md`
3. Validate: `python scripts/investor_update_validator.py update.md`
4. Send within 5 business days of month-end

**Time Estimate:** 1-2 hours/month.

### Workflow 2: Update Cadence Establishment
1. Read `references/what_makes_good_updates.md`
2. Decide cadence: monthly is standard for early-stage; quarterly for later-stage
3. Pick distribution: investors only, or extended (advisors, helpful operators)
4. Commit publicly — once you start, don't skip months

**Time Estimate:** 1 week to set up; recurring monthly thereafter.

---

## Tools

### investor_update_validator.py

Scans an update markdown file for the structural sections of a strong update and scores it.

```bash
python scripts/investor_update_validator.py update.md
python scripts/investor_update_validator.py update.md --json
```

---

## Scope & Limitations

**In Scope:**
- Structural validation of a markdown draft with `investor_update_validator.py`: a 0-100 score, sections present, missing or weak sections, and penalties for anti-patterns.
- A monthly update template in `assets/investor_update_template.md`.
- Guidance on what good updates contain: highlights and lowlights, hard numbers, context behind the numbers, and specific asks.
- Setting a monthly or quarterly update cadence and distribution list.

**Out of Scope:**
- Writing the update from company data. Despite the name, the tool validates a draft; it does not generate one.
- Calculating SaaS metrics such as MRR, churn, LTV or CAC (see `finance/saas-metrics-coach/`).
- Board decks and quarterly board materials (see `c-level-advisor/board-deck-builder/`).
- Pitch decks for a fundraise (see `personal-productivity/pitch-deck-reviewer/`).

**Important Caveats:**
- The validator checks for sections by pattern matching. A high score means the structure is present, not that the numbers are right or the update is persuasive.
- No metrics, accounting or cap-table system is read. All figures come from the user.
- The output is not legal or securities advice on what can be disclosed to investors.

---

## Reference Guides

- **`references/what_makes_good_updates.md`** — What separates good investor updates from bad

---

## Templates

- **`assets/investor_update_template.md`** — Monthly update template

---

## Best Practices

- **Send the bad news first.** Investors notice when they only hear the good.
- **Asks specific.** "Help with sales" is too vague; "Intros to VPs of Engineering at SaaS companies 100-1000 employees in NA" is actionable.
- **Cadence > perfection.** A consistent OK update beats a perfect annual one.
- **Same metrics every month.** Defining and re-defining metrics signals dishonest reporting.
- **One page (or one screen).** Past two screens, attention drops.
