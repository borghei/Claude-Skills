---
name: mediation-analysis
description: >
  Dispute analysis and mediation preparation framework. Use when preparing
  for mediation, analyzing disputes, calculating settlement ranges, mapping
  party interests, or developing negotiation strategy.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: The Glass Room
  category: legal
  domain: dispute-resolution
  updated: 2026-04-10
  tags: [mediation, negotiation, dispute-resolution, settlement, BATNA]
---
> **⚠️ EXPERIMENTAL** — This skill is provided for educational and informational purposes only. It does NOT constitute legal advice. All responsibility for usage rests with the user. Consult qualified legal professionals before acting on any output.

# Mediation Analysis

Production-ready framework for analyzing disputes and preparing mediation strategy. Covers the full cycle from dispute assessment through settlement calculation, interest mapping, and mediation readiness.

---

## Table of Contents

- [Operating Modes](#operating-modes)
- [Tools](#tools)
- [Core Analysis Framework](#core-analysis-framework)
- [Underlying Interests Analysis](#underlying-interests-analysis)
- [Legal Analysis](#legal-analysis)
- [Settlement Strategy](#settlement-strategy)
- [Reference Guides](#reference-guides)
- [Workflows](#workflows)
- [Troubleshooting](#troubleshooting)
- [Success Criteria](#success-criteria)
- [Scope and Limitations](#scope-and-limitations)
- [Anti-Patterns](#anti-patterns)
- [Tool Reference](#tool-reference)

---

## Operating Modes

### Mode 1: Guided Information Gathering

Use when starting from scratch without structured materials.

**Step 1 -- Dispute Overview:**
- Who are the parties? (names, roles, relationship)
- What is the dispute about? (summary in neutral terms)
- When did the dispute arise? (timeline of key events)
- What is the current status? (pre-litigation, filed, discovery, trial date)

**Step 2 -- Positions and Claims:**
- What does each party want? (stated positions)
- What are the claimed amounts? (monetary and non-monetary)
- What evidence supports each side?
- What are the weaknesses in each side's case?

**Step 3 -- Context and Constraints:**
- Is there an ongoing relationship? (employment, commercial, family)
- Are there power imbalances? (resources, information, leverage)
- Are there time pressures? (deadlines, statute of limitations)
- What has been tried so far? (direct negotiation, prior mediation)

### Mode 2: Direct Analysis

Use when dispute materials are already available (pleadings, correspondence, statements).

Provide the materials and specify which analysis sections are needed. The framework will extract the structured analysis from the raw materials.

---

## Tools

### Dispute Analyzer

Extracts structured dispute data from text descriptions.

```bash
# Analyze a dispute description
python scripts/dispute_analyzer.py --input dispute.txt

# Analyze with JSON output
python scripts/dispute_analyzer.py --input dispute.txt --json

# Analyze inline text
python scripts/dispute_analyzer.py --text "Party A claims breach of contract for failure to deliver..."

# Save structured analysis
python scripts/dispute_analyzer.py --input dispute.txt --output analysis.json
```

### Settlement Calculator

Calculates BATNA, WATNA, ZOPA, and settlement scenarios.

```bash
# Calculate from parameters file
python scripts/settlement_calculator.py --input params.json

# Calculate with JSON output
python scripts/settlement_calculator.py --input params.json --json

# Quick inline calculation
python scripts/settlement_calculator.py \
  --claimed 500000 \
  --litigation-cost-a 80000 \
  --litigation-cost-b 120000 \
  --probability 0.65 \
  --time-to-trial 18

# Save settlement analysis
python scripts/settlement_calculator.py --input params.json --output settlement.json
```

---

## Core Analysis Framework

The analysis produces 6 sections. Each section builds on the previous.

### Section 1: Case Summary

Write a neutral chronological summary covering:

| Element | Description |
|---------|-------------|
| Parties | Names, roles, and relationship |
| Timeline | Key events in chronological order |
| Dispute trigger | The event that escalated to a dispute |
| Current status | Procedural posture (pre-suit, filed, discovery) |
| Prior resolution attempts | What has been tried |

**Neutrality check:** The summary should be acceptable to both parties. Avoid characterizing conduct as "wrong" or "unreasonable."

### Section 2: Issues in Dispute

For each issue, document:

| Component | Description |
|-----------|-------------|
| Issue statement | Neutral framing of the disputed question |
| Party A position | What Party A asserts and why |
| Party B position | What Party B asserts and why |
| Key evidence | Evidence supporting each side |
| Strength assessment | Strong / Moderate / Weak for each side |
| Legal basis | Applicable law, contract terms, or principles |

### Section 3: Underlying Interests Analysis

Move beyond positions to interests. See detailed section below.

### Section 4: Legal Analysis

Per-issue assessment of legal merits. See detailed section below.

### Section 5: Mediation Strategy and Settlement Directions

BATNA/WATNA, ZOPA, and settlement scenarios. See detailed section below.

### Section 6: Mediation Readiness Checklist

| Item | Status | Notes |
|------|--------|-------|
| All parties agreed to mediate | | |
| Mediator selected and confirmed | | |
| Decision-makers attending or available | | |
| Key documents exchanged or available | | |
| Opening statement prepared | | |
| Settlement authority established | | |
| BATNA/WATNA analysis complete | | |
| Non-monetary interests identified | | |
| Creative options brainstormed | | |
| Authority limits clarified with client | | |

---

## Underlying Interests Analysis

Interests are the needs, concerns, and motivations behind stated positions.

### Interest Categories

| Category | Description | Examples |
|----------|-------------|---------|
| Legal | Rights, entitlements, obligations | Contract rights, statutory claims, precedent |
| Commercial | Business and financial concerns | Revenue, costs, market position, reputation |
| Relational | Relationship preservation | Ongoing business, employment, community ties |
| Emotional | Personal feelings and values | Fairness, respect, acknowledgment, vindication |
| Procedural | How the process unfolds | Speed, privacy, control, voice, transparency |

### Interest Mapping

For each party, map interests by category and priority:

| Party | Interest | Category | Priority | Compatible? |
|-------|----------|----------|----------|-------------|
| A | Preserve business reputation | Commercial | High | Yes -- shared |
| A | Recover financial losses | Legal/Commercial | High | Negotiable |
| B | Avoid setting precedent | Legal | High | Negotiable |
| B | Maintain relationship with A | Relational | Medium | Yes -- shared |

### Shared and Compatible Interests

Identify interests both parties share or that do not conflict:

- **Shared:** Both want confidentiality, speed, cost control
- **Compatible:** A wants acknowledgment, B wants no public admission -- private acknowledgment possible
- **Conflicting:** A wants maximum payment, B wants minimum payment -- negotiation zone needed

### Barriers to Resolution

| Barrier | Description | Mitigation |
|---------|-------------|------------|
| Reactive devaluation | Offers seem less attractive because they come from the other side | Have mediator propose options |
| Anchoring | First number distorts all subsequent negotiation | Use objective criteria to anchor |
| Loss aversion | Parties feel losses more than equivalent gains | Frame in terms of gains vs current state |
| Principal-agent | Party's representative may have different interests | Ensure decision-makers participate |
| Information asymmetry | One party knows more than the other | Structured disclosure through mediator |

---

## Legal Analysis

For each disputed issue, assess:

| Factor | Assessment |
|--------|-----------|
| Applicable law | Statute, regulation, contract term, or common law |
| Strength of claim | Strong (>70%) / Moderate (40-70%) / Weak (<40%) |
| Key uncertainties | Factual disputes, legal ambiguities, evidentiary gaps |
| Likely trial outcome | Best case, worst case, most likely |
| Damages range | If claimant prevails, likely award range |
| Costs to trial | Attorney fees, expert fees, opportunity costs per party |
| Time to resolution | Months/years to trial and potential appeal |

---

## Settlement Strategy

### BATNA / WATNA Analysis

| Metric | Party A | Party B |
|--------|---------|---------|
| Best Alternative (BATNA) | Win at trial, recover full claim + costs | Win at trial, pay nothing + recover costs |
| Worst Alternative (WATNA) | Lose at trial, recover nothing, pay own costs | Lose at trial, pay full claim + costs |
| Most Likely Alternative | Partial recovery minus litigation costs | Partial liability minus litigation costs |
| Litigation cost estimate | $X over Y months | $X over Y months |
| Net expected value | (Probability x Award) - Litigation costs | -(Probability x Award) - Litigation costs |

### ZOPA Identification

The Zone of Possible Agreement exists when Party A's minimum acceptable settlement is less than Party B's maximum they would pay.

```
Party A minimum = Expected trial value - litigation costs - risk discount
Party B maximum = Expected trial liability + litigation costs + risk premium

ZOPA exists when: A minimum < B maximum
ZOPA range: [A minimum ... B maximum]
```

### Settlement Scenarios

| Scenario | Description | When Appropriate |
|----------|-------------|-----------------|
| **Straightforward Compromise** | Split the difference on monetary claims | Simple disputes with clear monetary value |
| **Interest-Based Solution** | Address underlying interests beyond money | Ongoing relationships, non-monetary concerns |
| **Package Deal** | Bundle monetary and non-monetary elements | Complex disputes with multiple issues and interests |

---

## Reference Guides

| Guide | Path | Description |
|-------|------|-------------|
| Mediation Process | `references/mediation_process.md` | 12 stages of mediation with roles and techniques |
| Negotiation Concepts | `references/negotiation_concepts.md` | BATNA, WATNA, ZOPA, interest-based negotiation, barriers |

---

## Workflows

### Workflow 1: Full Mediation Preparation

1. Gather dispute information (Mode 1 or Mode 2).
2. Run `scripts/dispute_analyzer.py` on available materials.
3. Complete the 6-section Core Analysis Framework.
4. Run `scripts/settlement_calculator.py` with dispute parameters.
5. Prepare opening statement and settlement proposals.
6. Complete Mediation Readiness Checklist.
7. **Validation:** All 6 sections complete, BATNA/ZOPA calculated, proposals prepared.

### Workflow 2: Quick Settlement Range

1. Identify claimed amount, litigation costs, and success probability.
2. Run `scripts/settlement_calculator.py` with parameters.
3. Review ZOPA range and three scenarios.
4. Adjust parameters for sensitivity analysis.
5. **Validation:** Settlement range established with supporting rationale.

### Workflow 3: Multi-Party Mediation

1. Map all parties and their relationships.
2. Run dispute analysis for each bilateral relationship.
3. Identify coalition possibilities and shared interests.
4. Calculate settlement ranges for each party pair.
5. Design package deals that address all parties' core interests.
6. **Validation:** Each party pair analyzed, coalitions mapped, package options developed.

---

## Troubleshooting

| Problem | Likely Cause | Resolution |
|---------|-------------|------------|
| ZOPA appears negative | Parties' expectations unrealistic or litigation costs understated | Reality-test each party's BATNA; increase cost estimates |
| Cannot identify interests | Parties stuck on positions | Use "why" questions; explore consequences of winning/losing |
| Power imbalance distorting negotiation | Resource or information asymmetry | Recommend process adjustments; structured information sharing |
| Decision-maker absent | Representative lacks authority | Adjourn until decision-maker available; confirm authority in advance |
| Emotional barriers dominant | Unresolved relational issues | Address emotional interests first; consider apology or acknowledgment |
| Multi-party complexity | Too many bilateral dynamics | Break into sub-mediations; use single-text procedure |

---

## Success Criteria

| Criterion | Target |
|-----------|--------|
| Dispute issues identified | All contested issues listed with positions |
| Interests mapped | At least 3 interests per party, categorized |
| Legal strength assessed | Each issue rated with rationale |
| BATNA/WATNA calculated | Both parties' alternatives quantified |
| ZOPA identified | Settlement range established or confirmed negative |
| Settlement scenarios | Minimum 3 scenarios with rationale |
| Readiness checklist | All items addressed before mediation |

---

## Scope & Limitations

**In scope:** Dispute analysis, interest mapping, settlement calculation, mediation preparation, negotiation strategy.

**Out of scope:** Acting as mediator, providing legal advice, predicting judicial outcomes with certainty, drafting settlement agreements, representing parties.

**Disclaimer:** This skill provides an analytical framework for mediation preparation. It does not constitute legal advice. Settlement calculations are estimates based on inputs provided and should be validated by qualified counsel.

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Better Approach |
|-------------|-------------|-----------------|
| Positional bargaining only | Focuses on what parties demand, ignoring why they want it; leaves value on the table | Map interests first, then generate options that satisfy underlying needs |
| Ignoring litigation costs in settlement math | Parties anchor on the claim amount without factoring in costs to pursue it; produces unrealistic expectations | Always include full litigation costs (fees, time, opportunity cost) in BATNA calculation |
| Assuming equal bargaining power | Power imbalances distort negotiation; weaker party may accept unfavorable terms under pressure | Identify imbalances early; recommend process protections (separate caucuses, information sharing, independent advice) |
| Skipping emotional interests | Emotional needs (respect, acknowledgment, fairness) often drive dispute more than money; ignoring them produces impasse | Include emotional and relational interests in the analysis alongside legal and commercial interests |

---

## Tool Reference

| Tool | Input | Output | Use Case |
|------|-------|--------|----------|
| `dispute_analyzer.py` | Dispute description text | Structured analysis with parties, issues, interests, timeline | First-pass dispute structuring |
| `settlement_calculator.py` | Dispute parameters (amounts, costs, probability) | BATNA/WATNA, ZOPA, 3 settlement scenarios | Quantitative settlement range analysis |
