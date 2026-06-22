---
name: prfaq
description: >
  Amazon Working Backwards PR/FAQ generator that forces customer-outcome
  thinking before any code is written. Produces a press release, an internal
  FAQ, and an external FAQ as a single decision artifact.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-06-15
  tech-stack: working-backwards, pr-faq, amazon-method, narrative-memo
---
# PR/FAQ (Working Backwards) Expert

## Overview

The PR/FAQ is Amazon's "working backwards" artifact: before any team is funded to build a product, the PM writes a future-dated press release and an FAQ that anticipates every hard question. The discipline forces clarity on customer, problem, and outcome before a single design decision is made. If the team cannot write a compelling, credible PR/FAQ, the idea is not ready.

Use this skill when you need a high-fidelity narrative artifact for funding review, executive sponsorship, or a "should we even do this?" decision. The output is a single Markdown document with three sections: the press release, an internal FAQ (the questions your CFO, lawyer, and head of engineering will ask), and an external FAQ (the questions customers and press will ask). The PR/FAQ is not a PRD substitute -- it precedes the PRD -- and is not a marketing draft. The "Press Release Test" is the bar: if the press release would not strike a customer as genuinely newsworthy, the idea needs more work.

## Core Capabilities

- **Press release** -- the 9-part future-dated release in plain customer language, with the Press Release Test and headline/quote failure modes
- **Internal FAQ** -- 10-20 honest Q&A pairs across 9 required categories (demand, business model, strategic fit, competition, feasibility, ops, legal, risk, scope/alternatives)
- **External FAQ** -- buyer- and customer-facing questions that double as the first draft of help-center and sales-enablement content
- **Review choreography** -- the "5 readers" rule, versioning, and handoff to the PRD

## When to Use

- **Funding gate** -- A new initiative needs executive approval before spend.
- **Concept stress-test** -- An idea is exciting internally but you suspect the customer narrative is weak.
- **Cross-team alignment** -- Eng, design, marketing, and exec sponsors need one document they all agree on before kickoff.
- **Portfolio bake-off** -- Two or three competing ideas need apples-to-apples comparison; PR/FAQs reveal the strongest customer story.
- **Reframe a stalled project** -- A product in flight has lost the customer plot; rewriting the PR/FAQ surfaces what was lost.

**When NOT to use:** incremental features on an existing product (use `wwas/` or `job-stories/`); a signed-off PRD mid-build; pure technical infrastructure with no end-customer narrative.

## Clarify First

Before generating the PR/FAQ, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Customer + problem** — the "for [customer]" and the pain they feel today (drives the one-liner and press-release lead)
- [ ] **What makes it newsworthy** — the genuinely-new outcome (drives the headline and the Press Release Test pass/fail)
- [ ] **Hardest internal objection** — the CFO/eng/legal question you most fear (sets which of the 9 internal-FAQ categories to load)
- [ ] **Decision being made** — funding gate vs concept stress-test vs reframe (sets the bar and the primary reader)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Quick Start

1. Complete the one-liner: "We are announcing \[product\] for \[customer\] that does \[outcome\]."
2. Draft the press release first; do not write any FAQ until it passes the Press Release Test with one outside reader.
3. Write the internal FAQ in question/answer pairs (PM asks, sponsor/finance/eng answers), then the external FAQ last.
4. Run the "5 readers" rule, date and save the artifact, then hand off to `create-prd/`.

Use `assets/prfaq_template.md` as the fill-in scaffold. See `references/prfaq-playbook.md` for the full structure, FAQ categories, sample questions, workflow, and troubleshooting.

## References

- **[references/prfaq-playbook.md](references/prfaq-playbook.md)** — the Working Backwards method, the 9-part press-release structure and test, internal/external FAQ category requirements and sample questions, the authoring workflow, troubleshooting, and success criteria. Read when drafting or reviewing a PR/FAQ.
- **[references/working-backwards-guide.md](references/working-backwards-guide.md)** — deep dive on the Amazon method, its origin/intent, and the review choreography that makes it effective. Read for context on why the discipline works.
- **[references/red-flags.md](references/red-flags.md)** — common ways a PR/FAQ goes wrong, with concrete fixes. Read before circulating a draft for review.
- `assets/prfaq_template.md` — complete fill-in PR/FAQ template (PR + internal FAQ + external FAQ).

## Scope & Limitations

**In scope:** press-release drafting in the Working Backwards format; internal FAQ across the 9 categories; external buyer/customer FAQ; the Press Release Test protocol; handoff to PRD (`create-prd/`) and roadmap (`outcome-roadmap/`).

**Out of scope:** marketing/ad copy or external launch press (handoff to marketing); detailed PRD authoring (`create-prd/`); OKR definition (`brainstorm-okrs/`); backlog drafting (`wwas/`, `job-stories/`); pricing strategy or financial modeling (`finance/`).

**Caveats:** The PR/FAQ is an internal alignment artifact, not for external publication. The format works best in cultures that tolerate written narrative memos; slide-deck cultures may need to adopt it gradually. A weak PR/FAQ is a feature, not a bug — it surfaces a weak idea; fix the idea, do not inflate the language.

## Integration Points

| Integration | Direction | Description |
|-------------|-----------|-------------|
| `discovery/brainstorm-ideas/` | Receives from | Top-ranked opportunity solutions become PR/FAQ candidates |
| `discovery/identify-assumptions/` | Receives from | Assumptions populate internal FAQ "what we do not know yet" answers |
| `discovery/pre-mortem/` | Receives from | Tiger risks populate internal FAQ "failure modes" answers |
| `execution/create-prd/` | Feeds into | Approved PR/FAQ becomes the prologue and scope anchor for the PRD |
| `execution/brainstorm-okrs/` | Feeds into | Press release outcomes become OKR candidates |
| `execution/outcome-roadmap/` | Feeds into | PR/FAQ launch date and v1 scope inform roadmap horizon placement |
| `execution/roadmap-communication/` | Feeds into | PR/FAQ summary becomes the executive-variant roadmap narrative |
| `marketing/` (skills domain) | Hands off to | After launch approval, marketing teams adapt the PR into actual launch press materials |
