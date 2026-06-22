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

---

## Keywords

lead, leads, prospect, prospecting, sales, outbound, ICP, ideal customer profile, qualify, qualification, scoring, account list, target account, outreach, cold email, BDR, SDR, account executive

---

## Clarify First

Before scoring leads, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **ICP definition** — the must-have / nice-to-have / disqualifier attributes; this IS the scoring model
- [ ] **Lead list columns** — company, industry, size, country at minimum; missing fields mean no usable score
- [ ] **GTM motion** — PLG vs sales-led vs channel changes which signals weight highest and the outreach-hook framing

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

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

## Integration Points

- Pairs with `marketing/cold-email/` for sequence design
- Pairs with `sales-success/` skills for account executive handoff
- Feeds into `business-growth/` revenue forecasting
