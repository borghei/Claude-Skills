---
name: product-vision
description: >
  Write the Product Vision document -- the durable 5-10 year narrative above the
  north-star metric -- using Pichler's Vision Board, Moore's elevator pitch,
  Raskin's strategic narrative, Cagan's 10-year framing, and Amazon Working Backwards.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-06-15
  tech-stack: product-vision, strategic-narrative, working-backwards, vision-board
---
# Product Vision Expert

## Overview

The Product Vision is the narrative that sits above the north-star metric -- the answer to "where are we going and why" that aligns engineers, designers, marketers, executives, and customers around a single point on the horizon. Without a vision, teams optimize local metrics; with a vision, teams optimize toward a shared destination.

A vision is *not* a mission, *not* a strategy, *not* a roadmap. A mission says why the company exists. A strategy says how it will win. A roadmap says what ships next quarter. A vision says where the product will be in 5-10 years -- specific enough to inspire engineering decisions today, ambitious enough to outlast any current technology or market condition. This skill produces the vision document across four canonical formats -- Roman Pichler's **Product Vision Board** (one-page diagnostic), Geoffrey Moore's **elevator pitch** (single-sentence positioning from *Crossing the Chasm*), Andy Raskin's **strategic narrative** (5-act story arc), and Marty Cagan's **10-year horizon** -- plus an Amazon Working Backwards press release and a review checklist for testing whether a vision actually works.

## Core Capabilities

- **Pichler Vision Board** -- one-page, five-block canvas (vision, audience, needs, product, business goals)
- **Moore elevator pitch** -- single-sentence positioning statement that forces specificity
- **Raskin strategic narrative** -- 5-act story arc for pitches, board, all-hands, fundraising
- **Cagan 10-year horizon** -- long-form vision for multi-year architecture and senior hiring
- **Vision Review Checklist** -- score inspiring / concrete / durable / differentiated / memorable

## When to Use

- **New product launch.** Articulate the destination before committing engineering quarters.
- **Major pivot.** Direction has shifted and the old vision no longer fits. Reset.
- **Strategy reset.** Annual or pre-funding-round refresh of the long-term direction.
- **Stakeholder misalignment.** Engineering, design, and exec are pulling in different directions; re-articulating the vision surfaces the disagreement.
- **Hiring at scale.** You need a vision compelling enough that prospective hires can decide whether to join. Vague visions repel strong talent.

## Clarify First

Before generating the vision, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Target customer + their core need** — who and what pain (drives the Pichler Board audience/needs blocks and Moore's "for [customer]")
- [ ] **Format** — Pichler Board / Moore elevator pitch / Raskin narrative / Cagan 10-year (sets the entire structure of the artifact)
- [ ] **Time horizon** — 5 vs 10 years out (calibrates ambition; Cagan 10-year demands a different altitude than a near-term board)
- [ ] **Why now — the change** — the shift that makes this inevitable (drives the Raskin narrative's opening act and the vision's differentiation)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Quick Start

1. Gather inputs: customer interviews, JTBD hierarchy, value proposition canvas, competitive landscape.
2. Pick a starting format -- new product: Pichler Board; reset: Raskin narrative; multi-year: Cagan 10-year.
3. Draft, then **translate into a second format** -- a vision that survives translation is sharp.
4. Run the Vision Review Checklist; rewrite anything scoring under 3 of 5.
5. Test with 3 internal audiences and 2 customers; publish as the first link in onboarding and the cover of strategy decks; revisit annually.

## References

Load the reference that matches the task -- keep this file lean and pull detail on demand:

- **[references/vision-playbook.md](references/vision-playbook.md)** -- the operational playbook: the layer comparison (mission/vision/strategy/roadmap), all four framework templates in detail, the Amazon Working Backwards note, the full Vision Review Checklist, the end-to-end Reconcile worked example, the drafting workflow, troubleshooting, and success criteria. Read this when drafting or reviewing a vision.
- **[references/vision-frameworks-guide.md](references/vision-frameworks-guide.md)** -- the framework theory (Pichler, Moore, Raskin, Cagan, Amazon) with block-by-block guidance and "choosing a framework" advice. Read this when you need the reasoning behind each format.
- **[references/red-flags.md](references/red-flags.md)** -- 10 vision anti-patterns (vision = mission, 12-month vision, vision without a customer, vision as roadmap) with symptoms and fixes. Read this when stress-testing a draft.

Templates live in `assets/`: `vision_board_template.md`, `narrative_vision_template.md`, `elevator_pitch_template.md`, `vision_review_checklist.md`.

## Scope & Limitations

**In scope:** vision drafting across 4 frameworks (Pichler, Moore, Raskin, Cagan); the Vision Review Checklist; worked examples and templates; translation between formats; integration with downstream artifacts (NSM, OKRs, roadmap, PRDs).

**Out of scope:** mission statement writing; strategy document construction (`c-level-advisor/`); brand positioning and messaging (`marketing/`); Working Backwards PR/FAQ (`execution/prfaq/`); NSM definition (`execution/north-star-metric/`); OKR drafting (`execution/brainstorm-okrs/`).

**Caveats:** a vision is *not* a marketing document (marketing language belongs in messaging); a vision that is never used is worse than no vision; the 10-year horizon is uncomfortable for execution-minded teams -- the discomfort is the point; a vision can be wrong -- commit, build, and update on evidence.

## Integration Points

| Integration | Direction | What Flows |
|-------------|-----------|------------|
| `discovery/value-proposition-canvas/` | Receives from | Customer Profile (jobs, pains, gains) feeds Pichler Board "Needs" block |
| `discovery/jtbd-workshop/` | Receives from | Job hierarchy and top outcomes inform the vision's customer + outcome |
| `discovery/customer-interview-script/` | Receives from | Verbatim customer language sharpens vision phrasing |
| `execution/north-star-metric/` | Feeds into | The NSM derives from the vision -- the vision's outcome becomes the NSM input metric tree root |
| `execution/outcome-roadmap/` | Feeds into | The roadmap delivers the vision; every roadmap theme should trace back |
| `execution/brainstorm-okrs/` | Feeds into | OKRs serve the vision -- each quarterly objective should advance one vision pillar |
| `execution/prfaq/` | Complementary | Working Backwards PR is one expression of the vision; the FAQ stress-tests it |
| `execution/create-prd/` | Feeds into | PRDs explicitly reference the vision in Section 3 (Background) |
| `execution/roadmap-communication/` | Feeds into | Vision is the opening frame of every exec/customer roadmap presentation |
| `c-level-advisor/cto-advisor/` | Bidirectional | CTO uses vision to drive architecture bets; vision is informed by tech feasibility |
