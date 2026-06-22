---
name: roadmap-communication
description: >
  Same roadmap, three audiences. Produce executive, customer, and internal
  roadmap variants with audience-appropriate framing, detail, and risk language.
  Use for quarterly roadmap publication, board packets, and customer/sales roadmaps.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-06-15
  tech-stack: roadmap, communication, now-next-later, outcome-roadmap, marty-cagan
---
# Roadmap Communication Expert

## Overview

A single roadmap cannot serve every audience. Executives need confidence and strategic framing. Customers need plausible promises with credible timelines. Internal teams need detail, dependency awareness, and honest risk. When PMs publish one roadmap to all three, one audience is always wrong -- either the executives are bored, customers feel misled, or engineers feel managed.

This skill produces three variants of the same underlying roadmap, each tailored to its audience. The underlying source of truth -- the roadmap data -- stays single; the framing, level of detail, risk language, and visualization all change. The variants share names and identifiers so a customer reference can be traced back through the internal variant to the actual ticket. The structural backbone is **Now / Next / Later** (Janna Bastow, ProdPad), which Marty Cagan calls "right-sizing the roadmap" -- forecast confidence decreases with time horizon, so commit explicitly to "Now," name "Next" by theme, and keep "Later" deliberately fuzzy.

## Core Capabilities

- **Three audience variants** — executive (outcome-led, confidence-rated, 1 page), customer (theme-led, benefit-framed, no firm dates), and internal (feature-led with owners, dependencies, and explicit risk).
- **Now / Next / Later right-sizing** — encode the confidence gradient and calibrate it per audience.
- **Outcome-vs-feature framing** — translate features into customer outcomes for the executive and customer variants.
- **Triangulation check** — trace one Now item across all three variants to guarantee consistent identity and framing.

## When to Use

- **Quarterly roadmap publication** -- the regular cadence where you communicate to multiple audiences.
- **Pre-board meeting** -- the executive variant feeds the board packet.
- **Annual customer conference** -- the customer variant becomes the conference roadmap session.
- **Engineering kickoff** -- the internal variant grounds sprint planning across multiple teams.
- **Sales enablement** -- the customer variant feeds sales reps' "what's coming" pitch.

### When NOT to Use

- For a single-team backlog with one stakeholder (one roadmap suffices).
- For tactical sprint planning (use `../scrum-master/` outputs).
- For incident communication or in-flight project status (use `status-update-generator/`).

## Clarify First

Before generating the variants, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Target audience(s)** — executive, customer, internal, or all three (each is a distinct variant with different detail, framing, and risk language)
- [ ] **The roadmap source of truth** — Now/Next/Later items with owners and dates (the internal variant is authored first; exec/customer derive from it)
- [ ] **Date-commitment policy** — what you can promise customers publicly (the customer variant strips firm dates; the exec variant gets confidence ratings instead)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Quick Start

1. **Author the internal variant first** — it is the source of truth (owners, dates, dependencies, risks). Use `assets/internal_roadmap_template.md`.
2. **Derive the executive variant** — promote each Now item to its parent outcome, add confidence ratings, cap at 1 page. Use `assets/executive_roadmap_template.md`.
3. **Derive the customer variant** — translate features to benefits, strip dates beyond the current quarter, use "exploring / in development / shipping soon." Use `assets/customer_roadmap_template.md`.
4. **Run the triangulation check** — trace one Now item across all three; the framings must be consistent. Re-publish on a fixed cadence.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/roadmap-variants-playbook.md](references/roadmap-variants-playbook.md)** — the variant comparison tables, the "right-size the roadmap" principle, outcome-vs-feature framing, the detailed structure for each of the three variants, the authoring workflow, troubleshooting, and success criteria. Read when building or reviewing the variants.
- **[references/roadmap-communication-guide.md](references/roadmap-communication-guide.md)** — the origin of Now/Next/Later (Bastow), Cagan's right-size principle, the outcome-vs-feature debate (Cagan, Torres), and worked examples of all three variants for the same project. Read for theory and full examples.
- **[references/red-flags.md](references/red-flags.md)** — common ways roadmap artifacts go wrong, each with bad/good examples. Read before publishing any variant.
- **[assets/executive_roadmap_template.md](assets/executive_roadmap_template.md)** — fill-in template for the executive variant.
- **[assets/customer_roadmap_template.md](assets/customer_roadmap_template.md)** — fill-in template for the customer variant.
- **[assets/internal_roadmap_template.md](assets/internal_roadmap_template.md)** — fill-in template for the internal variant (the source of truth).

## Scope & Limitations

**In Scope:**
- Three roadmap variants (executive, customer, internal) from a shared underlying spec
- Now / Next / Later horizon structure with audience-appropriate detail
- Outcome-based framing for executive and customer variants
- Detailed feature/dependency/risk framing for internal variant
- Triangulation check ensuring consistency across variants
- Templates for each variant

**Out of Scope:**
- Backlog prioritization (use `prioritization-frameworks/`)
- OKR drafting (use `brainstorm-okrs/`)
- NSM definition (use `north-star-metric/`)
- Outcome-roadmap transformation (use `outcome-roadmap/`)
- Sprint planning (use `../scrum-master/`)
- Marketing launch copy (handoff to marketing skills)
- Detailed dependency graphs (use `dependency-map/`)

**Important Caveats:**
- Three variants triple the maintenance load. Teams without the discipline to keep them aligned will be better off publishing only the internal variant and disclaiming everything else. The three-variant pattern is for teams that can sustain quarterly re-publication.
- The customer variant is a public commitment. Treat updates as carefully as you treat a launch. Surprise changes erode trust.
- The internal variant must remain non-public. Sales reps must be trained to quote the customer variant only.
- Outcome-based roadmaps require an NSM and OKRs to function. Without those, "outcomes" are unmeasurable aspirations.

## Integration Points

| Integration | Direction | Description |
|-------------|-----------|-------------|
| `execution/outcome-roadmap/` | Receives from | Outcome decomposition feeds the executive variant |
| `execution/north-star-metric/` | Receives from | NSM and inputs are the executive variant's metrics |
| `execution/brainstorm-okrs/` | Receives from | KRs map to internal roadmap items |
| `execution/create-prd/` | Receives from | Each Now-quarter feature in the internal variant links to its PRD |
| `execution/prfaq/` | Receives from | PR/FAQ summaries become the seed of customer variant theme descriptions |
| `execution/prioritization-frameworks/` | Receives from | Prioritization scores determine which items make Now / Next / Later |
| `execution/dependency-map/` | Pairs with | Internal-variant dependencies are sourced from the dependency map |
| `execution/status-update-generator/` | Feeds into | Weekly status updates reference roadmap variant deltas |
| `../senior-pm/` | Feeds into | Portfolio roll-ups aggregate executive variants across teams |
| `marketing/` (skills domain) | Hands off to | Customer variant feeds product marketing content calendars and launch comms |
