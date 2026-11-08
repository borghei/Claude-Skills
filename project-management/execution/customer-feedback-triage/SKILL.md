---
name: customer-feedback-triage
description: >
  Cluster, score and route inbound feature requests from support, sales, NPS
  and exec asks, and draft honest replies. Use when a feedback queue needs
  triaging or a customer needs a defensible yes, no or exploring answer.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-11-08
  python-tools: feedback_triage.py
  tech-stack: [kano-model, jtbd, rice, request-management, marty-cagan]
  tags: [feedback, triage, kano, requests, voice-of-customer, intake]
---
# Customer Feedback Triage

## Overview

Most PMs sit on a chaotic inbound stream — Slack DMs, support tickets, sales call notes, CSAT comments, NPS verbatims, in-app feedback widgets, partner emails, exec one-liners — and have no system for converting that stream into prioritization signal. The default mode is reactive: whoever shouts loudest wins, the loudest channels (sales, executives) dominate, and the actual user job stays invisible.

This skill provides a workflow and a Python tool for handling that stream. Inputs are raw feedback items from many channels. Outputs are deduplicated, categorized, scored, and routed items, plus acknowledgment responses for the customers who sent them.

The frameworks behind it are Marty Cagan's separation of *request* from *opportunity* from *solution*, Noriaki Kano's model of feature-quality categories, a layered customer-development model, and an acknowledge/commit/promise request-management discipline. Detail lives in the references below.

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

Before triaging the feedback, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Feedback items with channel + segment tags:** the verbatims and where each came from (drives clustering, volume counts, and the Kano guess).
- **Segment weights:** which customer segments count more (sets `segment_weight` in the score, i.e. whether enterprise asks outrank long-tail volume).
- **Strategic alignment definition:** what current strategy a request must match (sets the `strategic_alignment` term that boosts on-strategy asks).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Workflow

The tool does the counting; you do the judgement. It deduplicates by distinct customer, guesses Kano and category from keywords, scores, and routes. It does not name the opportunity or decide what to build.

1. **Normalize intake** into the input schema (`references/tool-reference.md`), one verbatim per ask.
2. **Run the tool** for clusters, scores and routing:

```bash
python3 project-management/execution/customer-feedback-triage/scripts/feedback_triage.py \
  --input project-management/execution/customer-feedback-triage/assets/sample_feedback_queue.json --format markdown
```

3. **Write the job for each cluster** you act on. Clusters show `[write the job] keywords: ...` until an item carries `opportunity_label`; replace it with the need ("share results with people who have no login"), not the request ("PDF export").
4. **Check the guesses.** Override Kano or category where the keywords misread the ask; confirm that bug-like clusters (errors, slowness) went to the bug tracker with a `bug-acknowledged` reply.
5. **Decide in the triage meeting** [RECOMMENDED], then record `decision: will-build | won't-build` on the items. Until then every reply is drafted as **exploring**; `suggested_tier` is the score's hint, not a commitment. This keeps to "always acknowledge, sometimes commit, rarely promise".
6. **Feed forward** clusters routed to prioritization with their volume and Kano context; re-run to regenerate replies.

**Done when** every routed cluster has a human-written job label, every reply is exploring or backed by a recorded decision, and no Performance or Basic cluster sits in `to_archive` (the tool never archives them).

`--demo` runs a built-in 12-item queue; `--format` takes `json|markdown|mermaid|confluence|notion|linear`; `--segment-weights 'enterprise=4,smb=1'` and `--threshold 4.0` tune scoring. Formula, cadence and meeting agenda: `references/customer-feedback-triage-guide.md`.

**Exit codes:** 0 report written; 2 missing file, invalid JSON, wrong shape, empty queue or missing required fields.

## Anti-Patterns

### One loud account counted as many
**Mistake:** One enterprise account sends 5 messages about CSV export, and its cluster outranks one backed by 14 distinct customers.
**Why it happens:** Submission count is the number on screen, and repeated messages feel urgent.
**Instead:** Use distinct customers as volume, so five messages from one account count as 1. Compare `distinct_customers` to `request_count` per cluster; a ratio under 0.3 means one shouter.

### Exec requests that skip the queue
**Mistake:** A VP forwards a customer email on Monday and the item tops the roadmap by Tuesday, with no volume check or scoring.
**Why it happens:** Execs do have customer context, and pushing back on them feels risky.
**Instead:** Log exec asks with channel `exec_ask` and run them through the same triage. Send the VP the score and the queue. If more than 30% of roadmap adds over 6 months came from the exec channel, raise it.

### Building the literal request
**Mistake:** A customer asks for PDF export and the team builds it. Excel, CSV and Google Sheets requests follow, and each gets built in turn.
**Why it happens:** The request arrives already shaped as a solution, so it looks ready to build.
**Instead:** Cluster related requests and write the `opportunity_label` as a job, such as "share results with people who don't have a login". If the label is a verb plus a file type, rewrite it before scoring.

Nine more, each with a bad and a good example: `references/red-flags.md`.

## Files

| File | Purpose |
|---|---|
| `scripts/feedback_triage.py` | Cluster, score, route, draft replies |
| `assets/sample_feedback_queue.json` | 12-item queue; one cluster carries a human label and one item a will-build decision |
| `assets/triage_template.md`, `response_templates.md`, `kano_quick_reference.md` | Manual worksheet, reply templates, Kano card |
| `examples/triaging-30-requests.md` | Worked triage of 30 requests |

## References

- **[references/customer-feedback-triage-guide.md](references/customer-feedback-triage-guide.md)** — the full workflow with the 4 frameworks (Cagan, Kano, layered customer development, request management), the 6-phase process, week-over-week cadence, channel-by-channel intake norms, and the weekly triage meeting agenda. Read when running or setting up the triage process.
- **[references/kano-model-deep-dive.md](references/kano-model-deep-dive.md)** — categorization heuristics, edge cases, and time-dynamics of Kano categories. Read when overriding the tool's Kano guess.
- **[references/red-flags.md](references/red-flags.md)** — 12 anti-patterns (squeaky-wheel, sales-driven roadmap, HiPPO, treating requests literally...), plus the common traps, troubleshooting table, and success criteria. Read before the weekly triage meeting and when output looks off.
- **[references/tool-reference.md](references/tool-reference.md)** — `feedback_triage.py` flags, input schema, and all output schemas. Read when scripting or debugging the tool.
- **[assets/triage_template.md](assets/triage_template.md)** — manual triage worksheet for teams not running the Python tool.
- **[assets/response_templates.md](assets/response_templates.md)** — Will-build / Exploring / Won't-build templates with three variants each.
- **[assets/kano_quick_reference.md](assets/kano_quick_reference.md)** — one-page reference card for the five Kano categories.
- Marty Cagan, *Inspired* (2nd ed., 2017) and *Empowered* (2020); Noriaki Kano et al., "Attractive Quality and Must-Be Quality" (1984).

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
| `business-growth/customer-success-manager/` | Bidirectional | CS team is the primary intake source via support tickets and CSAT |
| `sales-success/` | Bidirectional | Sales is the intake source for sales-channel asks; receives won't-build rationale |
