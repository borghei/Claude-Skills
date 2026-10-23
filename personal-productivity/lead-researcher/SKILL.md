---
name: lead-researcher
description: >
  Qualify and prioritize sales leads against an ICP, score lead lists, and
  draft personalized outreach hooks. Use when building a target account list,
  qualifying inbound leads, prepping for outreach, or scoring prospects.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: personal-productivity
  domain: sales-prospecting
  updated: 2026-05-04
  python-tools: lead_qualifier.py
  tech-stack: sales, outbound, CRM
  tags:
    - lead-research
    - icp
    - lead-scoring
    - outreach
    - prospecting
---

# Lead Researcher

Score and qualify sales leads against an Ideal Customer Profile (ICP) definition, then draft outreach hooks tied to specific ICP signals.

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

lead, leads, prospect, prospecting, sales, outbound, ICP, ideal customer profile, qualify, qualification, scoring, account list, target account, outreach, cold email, BDR, SDR, account executive

---

## Clarify First

Before scoring leads, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **ICP definition:** the must-have / nice-to-have / disqualifier attributes; this IS the scoring model.
- **Lead list columns:** company, industry, size, country at minimum; missing fields mean no usable score.
- **GTM motion:** PLG vs sales-led vs channel changes which signals weight highest and the outreach-hook framing.

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

---

## Quick Start

### Score a Lead List in 10 Minutes

1. Define your ICP in `icp.json` using the schema in `assets/icp_schema.json`
2. Save your lead list as a CSV with columns: `company,industry,size,country,website,signals`
3. Run the qualifier:
   ```bash
   python scripts/lead_qualifier.py icp.json leads.csv
   ```
4. Review the ranked output — top 20% is your A-tier outreach list

---

## Core Workflows

### Workflow 1: ICP-Based Lead Scoring

**Goal:** Rank a list of candidate accounts so the top of the list reflects the best fit, not the most recent import.

**Steps:**
1. Build your ICP in `icp.json` — see `assets/icp_schema.json` for the full schema
2. Capture leads in a CSV with at minimum: `company,industry,size,country`
3. Run: `python scripts/lead_qualifier.py icp.json leads.csv`
4. Sort the result by `score` (highest first); the top 20% is your A-tier
5. Discard everything below the disqualification threshold rather than mass-emailing

**Expected Output:** Ranked list with score, tier (A/B/C/disqualified), and reason per lead.

**Time Estimate:** 10-15 minutes for a list of 200 leads.

### Workflow 2: ICP Definition

**Goal:** Convert a fuzzy "we sell to ops teams at mid-market SaaS" intuition into a structured ICP that the qualifier can actually score against.

**Steps:**
1. Pull the company names of your last 20-50 best customers
2. Identify the shared signals: industry, size band, geography, tech stack, pain trigger
3. For each, decide whether it's a **must-have**, **nice-to-have**, or **disqualifier**
4. Encode in `icp.json` per `references/icp_framework.md`
5. Pressure-test by scoring last quarter's closed-won and closed-lost accounts — the model should rank the wins above the losses

**Expected Output:** A versioned `icp.json` that retroactively predicts your past wins.

**Time Estimate:** 1-2 hours for first pass, 30 minutes per quarterly refresh.

### Workflow 3: Outreach Hook Drafting

**Goal:** Write outreach where the personalization actually mentions a real signal, not a fake "I noticed you posted on LinkedIn."

**Steps:**
1. Take the qualifier output for an A-tier lead
2. Read the matched ICP signals — these are your hooks
3. Use the outreach template in `assets/outreach_template.md`
4. Personalize the opening line with the strongest signal (e.g., recent funding, hiring spike, product launch, public quote about a pain you solve)
5. Keep the rest of the email short — sub-90 words

**Expected Output:** First-touch outreach email under 90 words with a real signal-based hook.

**Time Estimate:** 5 minutes per A-tier lead.

---

## Tools

### lead_qualifier.py

Reads an ICP JSON file and a leads CSV, returns a scored & tiered list.

```bash
# Human-readable
python scripts/lead_qualifier.py icp.json leads.csv

# JSON for programmatic use
python scripts/lead_qualifier.py icp.json leads.csv --json
```

**Scoring model:**
- Each ICP attribute has a weight (default 10) and direction (must / nice / disqualify)
- Must-have hits: full weight
- Nice-to-have hits: half weight
- Disqualifier hits: lead drops out of consideration entirely
- Score is normalized to 0-100

---

## Reference Guides

- **`references/icp_framework.md`** — How to define an ICP that actually predicts deal velocity, with worked examples by GTM motion (PLG, sales-led, channel)

---

## Templates

- **`assets/icp_schema.json`** — JSON schema for an ICP definition file
- **`assets/outreach_template.md`** — Cold-touch email template with placeholder slots tied to ICP signals

---

## Best Practices

- **Disqualify hard.** Mediocre leads are worse than no leads — they consume rep time and damage sender reputation.
- **Keep ICP versioned.** When deal velocity drops, your ICP is often stale. Re-derive every quarter.
- **One signal per email.** Multi-signal openers feel like research dumps; one well-chosen signal feels human.
- **Leads are not opportunities.** A scored A-tier lead is permission to reach out, not a forecasted deal.
- **Logs over feel.** Track which signals correlate with closed-won — let data update the ICP, not vibes.

---

## Scope & Limitations

**In Scope:**
- Scoring a leads CSV against an `icp.json` definition with `lead_qualifier.py`: weighted must-have, nice-to-have and disqualifier rules, a 0-100 score, an A, B, C or disqualified tier, and matched signals per lead.
- Building an ICP from closed-won customers, following `references/icp_framework.md` and `assets/icp_schema.json`.
- First-touch outreach hooks tied to one matched signal, using `assets/outreach_template.md`.

**Out of Scope:**
- Finding or enriching leads. The skill does not scrape websites, LinkedIn or data providers.
- Multi-step email sequences and deliverability (see `marketing/cold-email/`).
- Segment-level ICP strategy for go-to-market planning (see `project-management/gtm/ideal-customer-profile/`).
- Pipeline management and revenue forecasting (see `business-growth/revenue-operations/`).
- Writing scores or tiers back to a CRM.

**Important Caveats:**
- All lead data comes from a CSV the user supplies. Signals such as funding or hiring are only as current as that export.
- Scores are heuristic matches of field values against the ICP rules. Missing or inconsistently worded fields lower the score.
- A high score means fit with the ICP as written, not buying intent. An ICP that is not tested against past wins and losses produces confident but wrong rankings.

---

## Integration Points

- Pairs with `marketing/cold-email/` for sequence design
- Pairs with `sales-success/` skills for account executive handoff
- Feeds into `business-growth/` revenue forecasting
