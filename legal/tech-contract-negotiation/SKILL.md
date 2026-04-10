---
name: tech-contract-negotiation
description: >
  Negotiation frameworks for technology services agreements, B2B contracts,
  and professional services deals. Use when reviewing or negotiating tech contracts.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: The Glass Room
  category: legal
  domain: contract-negotiation
  updated: 2026-04-10
  tags: [contract-negotiation, technology-agreements, B2B, SLA, indemnification]
---
> **⚠️ EXPERIMENTAL** — This skill is provided for educational and informational purposes only. It does NOT constitute legal advice. All responsibility for usage rests with the user. Consult qualified legal professionals before acting on any output.

# Tech Contract Negotiation Skill

## Overview

Production-ready negotiation toolkit for technology services agreements, professional services contracts, and B2B transactions. Provides a Three-Position Framework (provider-favorable, balanced, client-favorable) for every major provision, Deal-Size Tactics across 5 tiers, Five-Tier Objection Handling, regulatory leverage arguments, and concession roadmaps. Designed for legal counsel, procurement leads, and sales/deal desk teams negotiating technology contracts from $100K to $10M+.

## Table of Contents

- [Tools](#tools)
- [Reference Guides](#reference-guides)
- [Workflows](#workflows)
- [Troubleshooting](#troubleshooting)
- [Success Criteria](#success-criteria)
- [Scope & Limitations](#scope--limitations)
- [Anti-Patterns](#anti-patterns)
- [Tool Reference](#tool-reference)

## Tools

### 1. Negotiation Position Analyzer (`scripts/negotiation_position_analyzer.py`)

Analyzes contract text and classifies each provision as provider-favorable, balanced, or client-favorable based on keyword patterns and structural analysis. Generates a position map and recommended negotiation priorities.

```bash
# Analyze a contract draft
python scripts/negotiation_position_analyzer.py contract_draft.txt

# JSON output for integration
python scripts/negotiation_position_analyzer.py contract_draft.txt --json

# Analyze from a specific party's perspective
python scripts/negotiation_position_analyzer.py contract_draft.txt --perspective client
```

### 2. Deal Complexity Scorer (`scripts/deal_complexity_scorer.py`)

Takes deal parameters and scores complexity across 7 dimensions. Recommends deal tier (1-5), expected timeline, number of rounds, and key focus areas.

```bash
# Score deal complexity from parameters file
python scripts/deal_complexity_scorer.py deal_params.json

# JSON output
python scripts/deal_complexity_scorer.py deal_params.json --json

# Override deal value for quick what-if
python scripts/deal_complexity_scorer.py deal_params.json --deal-value 5000000
```

## Reference Guides

| Reference | Purpose |
|-----------|---------|
| `references/three_position_framework.md` | Provider/balanced/client positions for 5 major provisions with deal-size tactics |
| `references/objection_handling.md` | Five-tier objection methodology, prediction matrix, communication templates |
| `references/regulatory_leverage.md` | GDPR, DORA, NIS2, SOX leverage arguments, concession roadmap, industry considerations |

## Workflows

### Workflow 1: Pre-Negotiation Assessment

1. **Classify the deal** -- Run `deal_complexity_scorer.py` with deal parameters to determine tier, timeline, and focus areas
2. **Analyze the draft** -- Run `negotiation_position_analyzer.py` on the initial contract to map current positions
3. **Identify gaps** -- Compare position map against your target positions from `three_position_framework.md`
4. **Prepare objection responses** -- Review `objection_handling.md` for predicted objections based on client type
5. **Map regulatory leverage** -- Identify applicable frameworks from `regulatory_leverage.md`

### Workflow 2: Active Negotiation

1. **Open with position** -- Use the Opening Position Statement template from `objection_handling.md`
2. **Handle pushback** -- Apply Five-Tier Objection Handling: Acknowledge, Market Context, Business Rationale, Alternatives, Bright Lines
3. **Track concessions** -- Follow the 4-tier concession roadmap (Easy Gives through Bright Lines)
4. **Re-analyze after redlines** -- Run `negotiation_position_analyzer.py` on each revised draft
5. **Close** -- Use Closing the Deal template; verify no Bright Lines were crossed

### Workflow 3: Deal Review and Approval

1. **Final position analysis** -- Run analyzer on execution-ready draft
2. **Complexity validation** -- Confirm final terms match expected deal tier parameters
3. **Regulatory check** -- Verify all mandatory regulatory provisions are present
4. **Document concessions** -- Record what was traded and why for future negotiations
5. **Approval package** -- Combine position map, complexity score, and concession log

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Analyzer flags everything as "provider-favorable" | Input is a vendor's first draft (expected behavior) | Use `--perspective provider` to flip the analysis; compare against balanced baseline |
| Complexity scorer returns Tier 5 for a small deal | High regulatory or multi-jurisdictional flags triggered | Review the regulatory and jurisdiction inputs; lower if overestimated |
| Position map shows no IP provisions detected | Contract uses non-standard terminology for IP clauses | Check for terms like "work product," "deliverables ownership," or "background IP" manually |
| Deal timeline estimate seems too short | Scorer does not account for internal approval delays | Add internal review buffer (typically 1-2 weeks per approval level) to the estimated timeline |
| Objection framework doesn't cover a specific pushback | Counterparty raised an atypical demand | Start with Acknowledge tier; frame using closest Market Context example; escalate to Bright Lines if needed |
| Regulatory leverage arguments rejected as irrelevant | Framework doesn't apply to counterparty's jurisdiction | Verify which regulations actually bind each party; remove inapplicable leverage points |

## Success Criteria

- **Position Accuracy**: Analyzer correctly classifies 85%+ of provisions when validated against expert review
- **Deal Tier Alignment**: Complexity scorer tier matches actual negotiation effort within one tier for 90% of deals
- **Negotiation Efficiency**: Average number of negotiation rounds reduced by 30% compared to ad-hoc approach
- **Concession Tracking**: 100% of material concessions documented with rationale and trade-off analysis
- **Bright Line Protection**: Zero instances of crossing defined Bright Lines without executive escalation and approval
- **Regulatory Coverage**: All applicable regulatory provisions identified and addressed in 95%+ of contracts
- **Time-to-Signature**: Deals close within estimated timeline +/- 20% for 80% of negotiations

## Scope & Limitations

**This skill covers:**
- Technology services agreements, SaaS subscriptions, professional services contracts, and B2B licensing deals
- Negotiation position analysis for liability, IP, payment, SLA, and warranty provisions
- Deal complexity scoring with tier-based recommendations for timeline, rounds, and focus areas
- Regulatory leverage for GDPR, DORA, NIS2, and SOX in technology contract contexts
- Objection handling frameworks and communication templates for common negotiation scenarios

**This skill does NOT cover:**
- Employment agreements, M&A transactions, real estate contracts, or consumer-facing terms of service
- Jurisdiction-specific legal advice or attorney-client privileged analysis (this is a framework, not legal counsel)
- Contract drafting from scratch (assumes an existing draft to analyze and negotiate)
- Litigation strategy, dispute resolution beyond contract clauses, or enforcement proceedings
- Price negotiation tactics for commodity purchases or non-technology procurement

## Anti-Patterns

| Anti-Pattern | Why It Fails | Better Approach |
|--------------|-------------|-----------------|
| Treating every provision as a Bright Line | Counterparty disengages when everything is non-negotiable | Classify provisions into 4 concession tiers; trade Easy Gives early to build goodwill |
| Skipping deal complexity assessment | Under-preparing for complex deals or over-preparing for simple ones | Always run complexity scorer first to calibrate effort, timeline, and approval requirements |
| Using regulatory leverage when the regulation doesn't apply | Destroys credibility and trust with informed counterparties | Verify applicability before citing any regulation; use the genuine-vs-preference test from the framework |
| Accepting "this is our standard template" at face value | Every template is negotiable; accepting defaults leaves value on the table | Analyze the "standard" template with the position analyzer to identify moveable provisions |
| Negotiating provisions in isolation | Conceding on SLAs without linking to liability caps creates exposure | Use the Three-Position Framework holistically; link related provisions (SLAs to credits to liability) |

## Tool Reference

### `scripts/negotiation_position_analyzer.py`

Analyze contract text and classify provisions by negotiation position.

```
usage: negotiation_position_analyzer.py [-h] [--json] [--perspective {provider,client}]
                                         input_file

positional arguments:
  input_file            Path to contract text file (.txt or .md)

options:
  -h, --help            Show help message and exit
  --json                Output results as JSON
  --perspective {provider,client}
                        Analysis perspective (default: client)
```

**Outputs:** Provision-by-provision position classification (provider-favorable / balanced / client-favorable), overall position score, position distribution summary, and prioritized negotiation recommendations.

### `scripts/deal_complexity_scorer.py`

Score deal complexity across 7 dimensions and recommend negotiation parameters.

```
usage: deal_complexity_scorer.py [-h] [--json] [--deal-value DEAL_VALUE]
                                  input_file

positional arguments:
  input_file            Path to JSON file with deal parameters

options:
  -h, --help            Show help message and exit
  --json                Output results as JSON
  --deal-value DEAL_VALUE
                        Override deal value in dollars
```

**Outputs:** 7-dimension complexity breakdown (value, regulatory, technical, multi-party, duration, strategic importance, IP sensitivity), composite score, deal tier (1-5), recommended timeline, expected negotiation rounds, and key focus areas.
