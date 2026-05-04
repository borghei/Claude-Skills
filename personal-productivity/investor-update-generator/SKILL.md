---
name: investor-update-generator
description: >
  Validate that a monthly investor update has the structural sections that
  separate strong updates (transparent, decision-relevant, asks specific) from
  weak ones (PR-style, all-good-news, no asks). Use before sending a monthly
  investor update, or when the user mentions investor update, monthly update,
  or fundraise communication cadence.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: personal-productivity
  domain: investor-relations
  updated: 2026-05-04
  python-tools: investor_update_validator.py
  tech-stack: investor-relations, fundraising
---

# Investor Update Generator

Validate a draft monthly investor update against a rubric of what makes them work — and provide a starting template if you don't have one yet.

---

## Keywords

investor update, monthly update, founder update, investor communication, fundraise, lead investor, board, KPIs, asks

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
