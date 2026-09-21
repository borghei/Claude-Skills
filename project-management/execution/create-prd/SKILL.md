---
name: create-prd
description: >
  PRD scaffolding expert that generates structured product requirements
  documents using an 8-section framework, problem framing canvas, and
  working-backwards press release. Use to spec a new product or feature.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-06-15
  python-tools: prd_scaffolder.py
  tech-stack: prd, product-requirements, documentation
---
# PRD Scaffolding Expert

## Overview

Structured product requirements document creation using a proven 8-section framework. This skill produces clear, jargon-free PRDs that communicate what to build, why it matters, and how success is measured. Every PRD generated follows a consistent structure that keeps engineering, design, and business stakeholders aligned.

## Core Capabilities

- **Pre-PRD framing** — Problem Framing Canvas (user-perspective narrative) and Working Backwards Press Release sharpen the problem before solutions.
- **8-section PRD framework** — Summary, Contacts, Background, Objective (SMART KRs), Market Segments (JTBD), Value Proposition (Value Curve), Solution (P0/P1/P2), Release.
- **Plain-language discipline** — one idea per sentence, specificity over abstraction, 10-second executive test.
- **Scaffolder automation** — `prd_scaffolder.py` generates the skeleton with guided placeholders.

## When to Use

- **New Product Initiative** -- Starting a product from scratch and need a comprehensive spec before development begins.
- **Feature Expansion** -- Adding significant functionality to an existing product that requires cross-team alignment.
- **Stakeholder Alignment** -- Need a single document that answers "what are we building and why?" for everyone involved.

## Clarify First

Before generating the PRD, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Core problem** — one sentence in the user's words; who hurts and how (drives Background + Objective)
- [ ] **Target reader** — exec, engineering, or mixed (sets altitude and which of the 8 sections matter most)
- [ ] **Success metric** — the SMART KR that defines "it worked" (drives Objective)
- [ ] **Scope boundary** — what is explicitly NOT in this release (drives Solution P0/P1/P2 + Release)

Stop rule: ask only the 2–3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the PRD.

## Quick Start

```bash
python scripts/prd_scaffolder.py --product-name "MyProduct" \
  --objective "Short description of the outcome" \
  --segments "Segment A, Segment B"
```

1. Gather context: product name, target segment, core problem.
2. (Optional) Frame the problem first with the Problem Framing Canvas or Working Backwards PR (see `references/prd-framework.md`).
3. Run the scaffolder to generate the skeleton, then fill each of the 8 sections.
4. Review against the checklist in `references/prd-writing-guide.md`, then share for feedback.

## Prototype-First Path

AI app builders, AI design tools, and AI coding assistants make a clickable or working prototype cheaper than a long spec for some work. Use the prototype to learn; keep the PRD to decide.

**Build a prototype first (or alongside the spec) when:**
- The core risk is usability or desirability ("will they understand / want this?"), not feasibility or policy.
- The interaction is hard to describe in prose (new workflow, dense UI, conversational flow).
- Stakeholders are debating opinions that a 20-minute user session would settle.

**Write the spec first when:** the risk is regulatory, data, security, pricing, or cross-team dependency; or the change is a well-understood extension of an existing flow.

**Testing the prototype with users:**
1. Write the hypothesis and pass threshold before the session (see `discovery/brainstorm-experiments/`).
2. Run 5-8 task-based sessions with the target segment; observe, don't demo.
3. Use realistic but synthetic data — never paste customer PII into third-party prototyping tools without approval.
4. Log what users did (task success, errors, time) separately from what they said.

**The PRD still must contain:** the problem and who has it (Background), success metrics (Objective KRs), constraints (technical, legal, budget, timeline), explicit non-goals, and risks/open questions. Link the prototype and the test findings in Section 7 (Solution) — the prototype illustrates the solution, it does not replace the requirements.

**Handoff to engineering:** label the prototype as throwaway or as a starting point, and say which. Generated prototype code is not production code by default — list what it skips (auth, error states, accessibility, performance, security review, data model) so engineering scopes the real build. Hand over the prototype link, the tested flows, the findings, and the P0/P1/P2 scope together.

## References

- `references/prd-framework.md` — read this while writing: the two pre-PRD techniques, full 8-section framework with per-section guidance, writing principles, scaffolder flag reference, troubleshooting, and success criteria.
- `references/prd-writing-guide.md` — read this when polishing a draft: section-by-section writing guide and the review checklist.
- `references/red-flags.md` — read this before sharing the PRD: common ways PRDs go wrong with bad/good examples and fixes.
- `assets/prd_template.md` — complete PRD template ready to fill in.

## Scope & Limitations

**In Scope:** 8-section PRD skeleton generation with guided placeholders; section-by-section writing guidance (plain-language, specificity); market-segment definition by jobs-to-be-done; value-proposition mapping with Value Curve; release planning with Now/Next/Later and explicit deferral.

**Out of Scope:** Technical architecture or system design docs (`engineering/`); user story writing and backlog creation (`execution/job-stories/`, `execution/wwas/`); detailed UX research or usability testing plans (`product-team/`); financial business-case modeling (`finance/`).

**Important Caveats:** A PRD is a communication tool, not a contract — treat it as a living document. The 8-section framework is proven, but lightweight agile teams may need only sections 1, 3, 4, 7, 8, while regulated contexts may need more. A 2025 Carnegie Mellon SEI study found effective requirements management eliminates 50-80% of project defects.

## Integration Points

| Integration | Direction | Description |
|------------|-----------|-------------|
| `discovery/identify-assumptions/` | Receives from | Validated and "Test Now" assumptions populate PRD Section 7 with evidence |
| `discovery/brainstorm-experiments/` | Receives from | Experiment results validate or invalidate PRD assumptions |
| `discovery/pre-mortem/` | Receives from | Tiger mitigations become PRD risk sections |
| `execution/brainstorm-okrs/` | Feeds into | PRD Key Results (Section 4) align with quarterly OKR targets |
| `execution/outcome-roadmap/` | Feeds into | PRD release plan (Section 8) maps to roadmap Now/Next/Later horizons |
| `execution/prioritization-frameworks/` | Receives from | Feature priority (P0/P1/P2) in Section 7 informed by RICE/ICE scoring |
| `senior-pm/` | Feeds into | PRD stakeholder context feeds stakeholder mapper engagement plans |
