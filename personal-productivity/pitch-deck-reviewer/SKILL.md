---
name: pitch-deck-reviewer
description: >
  Score a pitch deck's structure and content against YC, Sequoia, and a16z
  heuristics. Use before sending a deck to investors, practicing a pitch, or
  reviewing a seed or Series A fundraising deck.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: personal-productivity
  domain: fundraising
  updated: 2026-05-04
  python-tools: deck_structure_scorer.py
  tech-stack: fundraising, pitch
  tags:
    - pitch-deck
    - fundraising
    - startups
    - investors
    - deck-review
---

# Pitch Deck Reviewer

Score a pitch deck's structure against the YC / Sequoia / a16z heuristics.

> **Note:** This evaluates *structure*, not *content quality*. A perfectly-structured deck for a bad business is still a bad pitch. But a poorly-structured deck for a great business often gets passed.

---

## Keywords

pitch deck, pitch, fundraise, fundraising, seed deck, Series A deck, investor deck, slide deck, YC, Y Combinator, Sequoia, a16z

---

## Clarify First

Before scoring the deck, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Funding stage:** seed vs Series A sets the required-slide rubric (`--stage` flag) and what counts as a gap.
- **Slide-by-slide summary:** one bullet per slide (number + title + 1-2 sentences); vague summaries produce false gaps.
- **Round context:** amount raising and traction stage, so the "ask" and "traction" slides are judged against the right bar.

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

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

## Scope & Limitations

**In Scope:**
- Structure scoring of a slide-by-slide markdown summary against the required slides for `seed` or `series-a` (`deck_structure_scorer.py`).
- Gap flags for missing slide categories, with a hint for each.
- YC, Sequoia and a16z structure heuristics, common mistakes and stage differences in `references/pitch_deck_heuristics.md`, plus a summary template.

**Out of Scope:**
- Judging the business, the market or the quality of the content. The scorer checks structure only.
- Reading .pptx or PDF files. Auditing the deck file is covered by `documents/pptx-toolkit/`.
- Financial models and valuation (see `finance/financial-analyst/`).
- Board decks and ongoing investor updates (see `c-level-advisor/board-deck-builder/` and `personal-productivity/investor-update-generator/`).
- Rubrics for rounds later than Series A.

**Important Caveats:**
- The score depends on the summary the user writes. Vague summaries produce false gaps, and keyword-heavy ones can pass a slide that is weak.
- Slides are matched by keyword patterns per category, not by reading the deck.
- The heuristics reflect public guidance from YC, Sequoia and a16z. Individual investors differ, and the guidance changes over time.

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
