---
name: pptx-toolkit
description: >
  Audit PowerPoint (.pptx) decks for slide count, text density, embedded images
  and fonts, hidden slides, speaker notes, and animation density. Use when
  reviewing a board deck, sales deck, or conference talk before sending.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: documents
  domain: document-automation
  updated: 2026-05-04
  python-tools: pptx_auditor.py
  tech-stack: pptx, OOXML
  tags:
    - pptx
    - powerpoint
    - presentation-audit
    - slides
    - ooxml
---

# Pptx Toolkit

Audit `.pptx` files using the standard library only — no `python-pptx` required. Reads OOXML directly via `zipfile` + `xml.etree`.

---

## Table of Contents

- [Keywords](#keywords)
- [Quick Start](#quick-start)
- [Core Workflows](#core-workflows)
- [Tools](#tools)
- [Reference Guides](#reference-guides)
- [Templates](#templates)
- [Best Practices](#best-practices)
- [Scope & Limitations](#scope--limitations)

---

## Keywords

pptx, PowerPoint, slide deck, presentation, board deck, sales deck, deck review, slide density, speaker notes, animation, hidden slides

---

## Clarify First

Before running the audit, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Deck purpose (board/investor, sales, or conference talk):** sets the density caps, speaker-notes coverage, and animation limits (the rubric differs per type).
- **Delivery context (sent to be read vs presented live from notes):** changes whether bare slides and animations are acceptable.
- **Whether hidden slides should ship:** distinguishes intentional backup slides from leftover narrative cruft.

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

```bash
python scripts/pptx_auditor.py deck.pptx
```

Outputs: slide count, hidden slide count, slides with speaker notes, words per slide (with per-slide breakdown), image and embedded-media count, animation node count, theme name.

---

## Core Workflows

### Workflow 1: Pre-Meeting Deck Review

**Goal:** Catch the issues that make decks look unprofessional in the room — overstuffed slides, missing speaker notes, leftover hidden slides from prior versions.

**Steps:**
1. Run audit
2. Slides with > 50 words → flag for content reduction
3. Slides without speaker notes for a board / investor deck → add notes or mark "intentionally bare"
4. Hidden slides → confirm they should ship hidden, or delete
5. Animation count > 100 across deck → likely over-animated; trim

**Time Estimate:** 5-10 minutes per deck.

### Workflow 2: Board / Investor Deck Audit

**Goal:** Hold a board / investor deck to a higher quality bar with a structured audit trail.

**Steps:**
1. Run audit; export JSON for archival alongside the deck
2. Apply the rubric in `references/deck_density_rubric.md`
3. Flag slides over density caps; trim to one idea per slide
4. Pair with `cs-board-deck-builder` skill for narrative review

**Time Estimate:** 30-60 minutes per board deck.

### Workflow 3: Pre-Conference Talk Deck Check

**Goal:** Stage-ready deck — hidden / cut slides removed, speaker notes complete, animations rehearsable.

**Steps:**
1. Audit; ensure slide count matches dry-run timing budget
2. Speaker notes coverage > 90% (for talks where you'll deliver from notes)
3. Animations under 50 across the talk (more invites timing accidents on stage)
4. Embedded video / audio: confirm present and play locally

**Time Estimate:** 15 minutes pre-rehearsal.

---

## Tools

### pptx_auditor.py

Reads a `.pptx` file as a ZIP archive and parses OOXML directly. No external dependencies.

```bash
python scripts/pptx_auditor.py deck.pptx
python scripts/pptx_auditor.py deck.pptx --json
```

**Reports:**
- Slide count and hidden-slide count
- Slides with speaker notes (count and percentage)
- Words per slide (mean, max, full distribution)
- Top-N densest slides
- Image / embedded-media count
- Animation timing node count
- Theme name

---

## Reference Guides

- **`references/deck_density_rubric.md`** — Words-per-slide guidance by deck purpose (board, sales, talk, training); animation philosophy; speaker-notes pattern

---

## Templates

- **`assets/deck_handoff_checklist.md`** — Pre-meeting deck sign-off checklist

---

## Best Practices

- **One idea per slide.** If you can't summarize the slide in one sentence, it has more than one idea.
- **Speaker notes are documentation.** Slides without notes leave readers (post-meeting) guessing what the talk track was.
- **Delete hidden slides before sending.** Hidden slides are often older versions left for "just in case" — they survive forever and leak narrative context.
- **Animations are timing risk.** Every animation is a place where the live demo can desync from the speaker.

---

## Scope & Limitations

**In Scope:**
- Read-only audit of `.pptx` files with `scripts/pptx_auditor.py`, which parses OOXML with `zipfile` and `xml.etree` and needs no third-party package
- Slide and hidden-slide counts, speaker-notes coverage, words per slide with the densest slides, image and embedded-media count, animation timing nodes, and theme name
- Three workflows: pre-meeting review, board or investor deck audit, and pre-conference talk check
- A deck density rubric with words-per-slide targets by deck purpose, plus a handoff checklist

**Out of Scope:**
- Creating, editing or restyling slides; the tool only reads
- Building a board deck's narrative and content (see `c-level-advisor/board-deck-builder/`)
- Reviewing a pitch deck's story for investors (see `personal-productivity/pitch-deck-reviewer/`)
- Producing slides from markdown (see `markdown-html/md-slides/`)

**Important Caveats:**
- The auditor does not render slides. Layout, overlap, contrast, font use and brand compliance are not checked.
- Word counts and animation counts measure density, not quality. The thresholds in the workflows, such as 50 words per slide, are rules of thumb; the rubric sets different targets by deck purpose.
- It counts embedded media but cannot confirm that video or audio plays; the talk workflow says to test playback locally.

---

## Integration Points

- Pairs with `c-level-advisor/board-deck-builder` for board / investor decks
- Pairs with `marketing/launch-strategy` for launch-deck reviews
- Used by `cs-pr-comms-lead` for press / partner decks
