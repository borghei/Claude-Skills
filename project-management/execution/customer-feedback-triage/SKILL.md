---
name: customer-feedback-triage
description: >
  Inbound customer-feedback triage system. Categorize, deduplicate, score, and
  respond to feature requests from support, sales, NPS, in-app feedback, and
  exec asks (Kano + Cagan). Feeds clean signal into prioritization-frameworks.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-06-15
  python-tools: feedback_triage.py
  tech-stack: [kano-model, jtbd, rice, request-management, marty-cagan]
  tags: [feedback, triage, kano, requests, voice-of-customer, intake]
---
# Customer Feedback Triage

## Overview

Most PMs sit on a chaotic inbound stream — Slack DMs, support tickets, sales call notes, CSAT comments, NPS verbatims, in-app feedback widgets, partner emails, exec one-liners — and have no system for converting that stream into prioritization signal. The default mode is reactive: whoever shouts loudest wins, the loudest channels (sales, executives) dominate, and the actual user job stays invisible.

This skill provides a workflow and a Python tool for handling that stream. Inputs are raw feedback items from many channels. Outputs are deduplicated, categorized, scored, and routed items, plus acknowledgment responses for the customers who sent them.

The frameworks behind it are Marty Cagan's separation of *request* from *opportunity* from *solution*, Noriaki Kano's model of feature-quality categories, Reforge's customer-development model, and ProductPlan's request-management playbook. Detail lives in the references below.

## Core Capabilities

- **Intake & normalization** — one verbatim record per ask across 8 channels (support, sales, social, NPS, in-app, exec, partner, interview)
- **Dedup & clustering** — group items by underlying opportunity even when literal requests differ
- **Kano + Cagan classification** — Basic/Performance/Delight/Indifferent/Reverse, and Request → Opportunity → Solution
- **Segment-aware scoring** — `kano_weight × log10(volume+1) × segment_weight × (1 + strategic_alignment)` as a coarse router (not a final RICE)
- **Response discipline** — Will-build / Exploring / Won't-build templates; always acknowledge, sometimes commit, rarely promise
- **Feed-forward routing** — to prioritization, discovery, backlog, bug tracker, or strategy

## When to Use

- You have a backlog of customer feedback that is not being processed.
- Sales or Customer Success is constantly forwarding feature requests and expecting a per-request answer.
- An executive is acting as a request channel and the roadmap is drifting accordingly.
- You are setting up a new feedback intake process (post-launch, post-funding, scaling beyond founder-led product).
- You need to respond to a customer who sent a feature request and you have to say "yes", "no", or "exploring" in a defensible way.
- You want a defensible audit trail for "we heard you but said no" decisions.

### When not to use

- For genuine product discovery (do not let feedback triage replace discovery — see `discovery/interview-synthesis/`).
- For prioritizing already-triaged items against each other (that is `prioritization-frameworks/`).
- For bug triage (use the bug triage process in your tracker — though the workflow here applies to feature-request items).

## Clarify First

Before triaging the feedback, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Feedback items with channel + segment tags** — the verbatims and where each came from (drives clustering, volume counts, and the Kano guess)
- [ ] **Segment weights** — which customer segments count more (sets `segment_weight` in the score, i.e. whether enterprise asks outrank long-tail volume)
- [ ] **Strategic alignment definition** — what current strategy a request must match (sets the `strategic_alignment` term that boosts on-strategy asks)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Quick Start

```bash
# Triage a JSON queue of inbound feedback
python scripts/feedback_triage.py --input queue.json --format markdown

# See a sample triage queue across all 6 output formats
python scripts/feedback_triage.py --demo --format markdown
```

The tool ships with `--format json|markdown|mermaid|confluence|notion|linear` per `SHARED_OUTPUT_SCHEMA.md`. The 6-phase workflow (intake → triage → categorize → score → respond → feed forward) and the scoring formula live in the workflow guide reference.

## References

- **[references/customer-feedback-triage-guide.md](references/customer-feedback-triage-guide.md)** — the full workflow with the 4 frameworks (Cagan, Kano, Reforge, ProductPlan), the 6-phase process, week-over-week cadence, channel-by-channel intake norms, and the weekly triage meeting agenda. Read when running or setting up the triage process.
- **[references/kano-model-deep-dive.md](references/kano-model-deep-dive.md)** — categorization heuristics, edge cases, and time-dynamics of Kano categories. Read when overriding the tool's Kano guess.
- **[references/red-flags.md](references/red-flags.md)** — 12 anti-patterns (squeaky-wheel, sales-driven roadmap, HiPPO, treating requests literally...), plus the common traps, troubleshooting table, and success criteria. Read before the weekly triage meeting and when output looks off.
- **[references/tool-reference.md](references/tool-reference.md)** — `feedback_triage.py` flags, input schema, and all output schemas. Read when scripting or debugging the tool.
- **[assets/triage_template.md](assets/triage_template.md)** — manual triage worksheet for teams not running the Python tool.
- **[assets/response_templates.md](assets/response_templates.md)** — Will-build / Exploring / Won't-build templates with three variants each.
- **[assets/kano_quick_reference.md](assets/kano_quick_reference.md)** — one-page reference card for the five Kano categories.
- Marty Cagan, *Inspired* (2nd ed., 2017) and *Empowered* (2020); Noriaki Kano et al., "Attractive Quality and Must-Be Quality" (1984); Reforge "Customer Development"; ProductPlan, "How to Manage Product Feedback".

## Scope & Limitations

**In Scope:** Inbound feedback intake schema, deduplication and clustering, Kano-based categorization, segment-aware volume scoring, response templating, routing to downstream skills (discovery, prioritization, backlog).

**Out of Scope:** Bug triage (use the team's bug tracker process). User research and interview-driven discovery (see `discovery/interview-synthesis/`). Detailed prioritization scoring with RICE/ICE/WSJF (see `prioritization-frameworks/`). Customer-relationship management (CRM is the system of record for the customer, this skill is the system of record for the request). NPS analysis methodology (this skill ingests NPS verbatims as one channel among many).

**Important Caveats:** The Kano guess and clustering are transparent keyword/word-overlap heuristics — not ML; override liberally and, above ~500 items/month, augment with semantic clustering offline. The scoring formula is a coarse router, not a substitute for RICE/ICE. "Acknowledge, sometimes commit, rarely promise" is a discipline the templates support but cannot enforce; Sales and CS need explicit training to avoid promising in customer conversations.

## Integration Points

| Integration | Direction | What flows |
|---|---|---|
| `prioritization-frameworks/` | Feeds into | High-priority triaged Feature requests flow in with volume and Kano context as inputs to RICE/ICE/WSJF |
| `discovery/identify-assumptions/` | Feeds into | Recurring opportunity themes surface implicit product assumptions |
| `discovery/interview-synthesis/` | Feeds into | Top customers per cluster become the target list for follow-up interviews |
| `discovery/brainstorm-experiments/` | Feeds into | High-signal opportunities motivate experiment design |
| `wwas/` | Feeds into | Backlog-ready items move into Why-What-Acceptance format |
| `job-stories/` | Feeds into | Final backlog items use Job Stories format if team prefers JTBD framing |
| `senior-pm/` | Bidirectional | Stakeholder map informs segment weights; triage output informs stakeholder updates |
| `business-growth/customer-success/` | Bidirectional | CS team is the primary intake source via support tickets and CSAT |
| `sales-success/` | Bidirectional | Sales is the intake source for sales-channel asks; receives won't-build rationale |
