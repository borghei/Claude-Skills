---
name: pitch-deck-reviewer
description: >
  Score a pitch deck (provided as text/markdown summary of slides) against
  YC, Sequoia, and a16z heuristics — does it have the right slides in the
  right order with the right content? Use before sending a deck to investors,
  practicing pitch with a co-founder, or when the user mentions pitch deck,
  fundraising deck, seed deck, or Series A deck review.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: personal-productivity
  domain: fundraising
  updated: 2026-05-04
  python-tools: deck_structure_scorer.py
  tech-stack: fundraising, pitch
---

# Pitch Deck Reviewer

Score a pitch deck's structure against the YC / Sequoia / a16z heuristics.

> **Note:** This evaluates *structure*, not *content quality*. A perfectly-structured deck for a bad business is still a bad pitch. But a poorly-structured deck for a great business often gets passed.

---

## Keywords

pitch deck, pitch, fundraise, fundraising, seed deck, Series A deck, investor deck, slide deck, YC, Y Combinator, Sequoia, a16z

---

## Quick Start

1. Summarize each slide as one bullet in `deck_summary.md` (slide number + title + 1-2 sentences of content)
2. Run: `python scripts/deck_structure_scorer.py deck_summary.md`
3. Address gaps; iterate

---

## Core Workflows

### Workflow 1: Pre-Send Deck Review
1. Summarize deck slide-by-slide in `deck_summary.md`
2. Run scorer
3. Add missing slides (the scorer flags by category)
4. Re-order if structure flow is off
5. Pair with `documents/pptx-toolkit/` for actual pptx audit

**Time Estimate:** 1-2 hours per major deck iteration.

### Workflow 2: First Deck Build (No Existing Deck)
1. Read `references/pitch_deck_heuristics.md`
2. Use the structure rubric (10-15 slides covering specific topics)
3. Draft slide-by-slide
4. Validate as Workflow 1

**Time Estimate:** 1-2 weeks for first complete draft.

---

## Tools

### deck_structure_scorer.py

Reads a markdown file describing the deck slide-by-slide and scores it against required slides per stage.

```bash
python scripts/deck_structure_scorer.py deck_summary.md
python scripts/deck_structure_scorer.py deck_summary.md --json

# For Series A
python scripts/deck_structure_scorer.py deck_summary.md --stage series-a
```

Stages: `seed` (default), `series-a`.

---

## Reference Guides

- **`references/pitch_deck_heuristics.md`** — YC, Sequoia, a16z deck structure heuristics; common mistakes; stage differences

---

## Templates

- **`assets/deck_summary_template.md`** — Slide-by-slide summary template

---

## Best Practices

- **One idea per slide.** If you can't summarize it in one sentence, split it.
- **Numbers, not adjectives.** "Strong growth" is weak. "$80k → $312k MRR over 12 months" is strong.
- **Order matters.** Most decks under-invest in problem framing and the "why now" slide.
- **Don't ship 30+ slides.** A seed deck is 10-12 slides; a Series A deck is 12-15.
- **Demo is not the deck.** Decks introduce; demos persuade. Plan both.
