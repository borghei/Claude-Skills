---
name: sales-engineer
description: >
  Analyzes RFP responses for coverage gaps, builds competitive feature matrices,
  and plans proof-of-concept engagements for pre-sales engineering
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: business-growth
  domain: sales-engineering
  updated: 2026-03-31
  tags: [sales-engineering, demos, poc, technical-sales, solutions]
---
# Sales Engineer Skill

A production-ready skill package for pre-sales engineering that bridges technical expertise and sales execution. Provides automated analysis for RFP/RFI responses, competitive positioning, and proof-of-concept planning.

## Overview

**Role:** Sales Engineer / Solutions Architect
**Domain:** Pre-Sales Engineering, Solution Design, Technical Demos, Proof of Concepts
**Business Type:** SaaS / Pre-Sales Engineering

### What This Skill Does

- **RFP/RFI Response Analysis** - Score requirement coverage, identify gaps, generate bid/no-bid recommendations
- **Competitive Technical Positioning** - Build feature comparison matrices, identify differentiators and vulnerabilities
- **POC Planning** - Generate timelines, resource plans, success criteria, and evaluation scorecards
- **Demo Preparation** - Structure demo scripts with talking points and objection handling
- **Technical Proposal Creation** - Framework for solution architecture and implementation planning
- **Win/Loss Analysis** - Data-driven competitive assessment for deal strategy

### Key Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| Win Rate | Deals won / total opportunities | >30% |
| Sales Cycle Length | Average days from discovery to close | <90 days |
| POC Conversion Rate | POCs resulting in closed deals | >60% |
| Customer Engagement Score | Stakeholder participation in evaluation | >75% |
| RFP Coverage Score | Requirements fully addressed | >80% |

## 5-Phase Workflow

### Phase 1: Discovery & Research

**Objective:** Understand customer requirements, technical environment, and business drivers.

**Activities:**
1. Conduct technical discovery calls with stakeholders
2. Map customer's current architecture and pain points
3. Identify integration requirements and constraints
4. Document security and compliance requirements
5. Assess competitive landscape for this opportunity

**Tools:** Use `rfp_response_analyzer.py` to score initial requirement alignment.

**Output:** Technical discovery document, requirement map, initial coverage assessment.

### Phase 2: Solution Design

**Objective:** Design a solution architecture that addresses customer requirements.

**Activities:**
1. Map product capabilities to customer requirements
2. Design integration architecture
3. Identify customization needs and development effort
4. Build competitive differentiation strategy
5. Create solution architecture diagrams

**Tools:** Use `competitive_matrix_builder.py` to identify differentiators and vulnerabilities.

**Output:** Solution architecture, competitive positioning, technical differentiation strategy.

### Phase 3: Demo Preparation & Delivery

**Objective:** Deliver compelling technical demonstrations tailored to stakeholder priorities.

**Activities:**
1. Build demo environment matching customer's use case
2. Create demo script with talking points per stakeholder role
3. Prepare objection handling responses
4. Rehearse failure scenarios and recovery paths
5. Collect feedback and adjust approach

**Templates:** Use `demo_script_template.md` for structured demo preparation.

**Output:** Customized demo, stakeholder-specific talking points, feedback capture.

### Phase 4: POC & Evaluation

**Objective:** Execute a structured proof-of-concept that validates the solution.

**Activities:**
1. Define POC scope, success criteria, and timeline
2. Allocate resources and set up environment
3. Execute phased testing (core, advanced, edge cases)
4. Track progress against success criteria
5. Generate evaluation scorecard

**Tools:** Use `poc_planner.py` to generate the complete POC plan.

**Templates:** Use `poc_scorecard_template.md` for evaluation tracking.

**Output:** POC plan, evaluation scorecard, go/no-go recommendation.

### Phase 5: Proposal & Closing

**Objective:** Deliver a technical proposal that supports the commercial close.

**Activities:**
1. Compile POC results and success metrics
2. Create technical proposal with implementation plan
3. Address outstanding objections with evidence
4. Support pricing and packaging discussions
5. Conduct win/loss analysis post-decision

**Templates:** Use `technical_proposal_template.md` for the proposal document.

**Output:** Technical proposal, implementation timeline, risk mitigation plan.

## Python Automation Tools

### 1. RFP Response Analyzer

**Script:** `scripts/rfp_response_analyzer.py`

**Purpose:** Parse RFP/RFI requirements, score coverage, identify gaps, and generate bid/no-bid recommendations.

**Coverage Categories:**
- **Full (100%)** - Requirement fully met by current product
- **Partial (50%)** - Requirement partially met, workaround or configuration needed
- **Planned (25%)** - On product roadmap, not yet available
- **Gap (0%)** - Not supported, no current plan

**Priority Weighting:**
- Must-Have: 3x weight
- Should-Have: 2x weight
- Nice-to-Have: 1x weight

**Bid/No-Bid Logic:**
- **Bid:** Coverage score >70% AND must-have gaps <=3
- **Conditional Bid:** Coverage score 50-70% OR must-have gaps 2-3
- **No-Bid:** Coverage score <50% OR must-have gaps >3

**Usage:**
```bash
# Human-readable output
python scripts/rfp_response_analyzer.py assets/sample_rfp_data.json

# JSON output
python scripts/rfp_response_analyzer.py assets/sample_rfp_data.json --format json

# Help
python scripts/rfp_response_analyzer.py --help
```

**Input Format:** See `assets/sample_rfp_data.json` for the complete schema.

### 2. Competitive Matrix Builder

**Script:** `scripts/competitive_matrix_builder.py`

**Purpose:** Generate feature comparison matrices, calculate competitive scores, identify differentiators and vulnerabilities.

**Feature Scoring:**
- **Full (3)** - Complete feature support
- **Partial (2)** - Partial or limited feature support
- **Limited (1)** - Minimal or basic feature support
- **None (0)** - Feature not available

**Usage:**
```bash
# Human-readable output
python scripts/competitive_matrix_builder.py competitive_data.json

# JSON output
python scripts/competitive_matrix_builder.py competitive_data.json --format json
```

**Output Includes:**
- Feature comparison matrix with scores
- Weighted competitive scores per product
- Differentiators (features where our product leads)
- Vulnerabilities (features where competitors lead)
- Win themes based on differentiators

### 3. POC Planner

**Script:** `scripts/poc_planner.py`

**Purpose:** Generate structured POC plans with timeline, resource allocation, success criteria, and evaluation scorecards.

**Default Phase Breakdown:**
- **Week 1:** Setup - Environment provisioning, data migration, configuration
- **Weeks 2-3:** Core Testing - Primary use cases, integration testing
- **Week 4:** Advanced Testing - Edge cases, performance, security
- **Week 5:** Evaluation - Scorecard completion, stakeholder review, go/no-go

**Usage:**
```bash
# Human-readable output
python scripts/poc_planner.py poc_data.json

# JSON output
python scripts/poc_planner.py poc_data.json --format json
```

**Output Includes:**
- POC plan with phased timeline
- Resource allocation (SE, engineering, customer)
- Success criteria with measurable metrics
- Evaluation scorecard (functionality, performance, integration, usability, support)
- Risk register with mitigation strategies
- Go/No-Go recommendation framework

## Reference Knowledge Bases

| Reference | Description |
|-----------|-------------|
| `references/rfp-response-guide.md` | RFP/RFI response best practices, compliance matrix, bid/no-bid framework |
| `references/competitive-positioning-framework.md` | Competitive analysis methodology, battlecard creation, objection handling |
| `references/poc-best-practices.md` | POC planning methodology, success criteria, evaluation frameworks |

## Asset Templates

| Template | Purpose |
|----------|---------|
| `assets/technical_proposal_template.md` | Technical proposal with executive summary, solution architecture, implementation plan |
| `assets/demo_script_template.md` | Demo script with agenda, talking points, objection handling |
| `assets/poc_scorecard_template.md` | POC evaluation scorecard with weighted scoring |
| `assets/sample_rfp_data.json` | Sample RFP data for testing the analyzer |
| `assets/expected_output.json` | Expected output from rfp_response_analyzer.py |

## Communication Style

- **Technical yet accessible** - Translate complex concepts for business stakeholders
- **Confident and consultative** - Position as trusted advisor, not vendor
- **Evidence-based** - Back every claim with data, demos, or case studies
- **Stakeholder-aware** - Tailor depth and focus to audience (CTO vs. end user vs. procurement)

## Integration Points

- **Marketing Skills** - Leverage competitive intelligence and messaging frameworks from `../../marketing/`
- **Product Team** - Coordinate on roadmap items flagged as "Planned" in RFP analysis from `../../product-team/`
- **C-Level Advisory** - Escalate strategic deals requiring executive engagement from `../../c-level-advisor/`
- **Customer Success** - Hand off POC results and success criteria to CSM from `../customer-success-manager/`

---

## Tool Reference

### 1. rfp_response_analyzer.py

Parses RFP/RFI requirements and scores coverage using Full/Partial/Planned/Gap categories. Generates weighted coverage scores, gap analysis, effort estimation, and bid/no-bid recommendations.

```bash
python scripts/rfp_response_analyzer.py rfp_data.json
python scripts/rfp_response_analyzer.py rfp_data.json --format json
```

| Flag | Type | Description |
|------|------|-------------|
| `rfp_data.json` | positional | Path to JSON file with RFP requirements and coverage data |
| `--format` | optional | Output format: `text` (default) or `json` |

**Bid/No-Bid Logic:**
- **Bid:** Coverage score >70% AND must-have gaps <=3
- **Conditional Bid:** Coverage score 50-70% OR must-have gaps 2-3
- **No-Bid:** Coverage score <50% OR must-have gaps >3

### 2. competitive_matrix_builder.py

Generates feature comparison matrices, calculates weighted competitive scores, identifies differentiators and vulnerabilities, and produces win themes.

```bash
python scripts/competitive_matrix_builder.py competitive_data.json
python scripts/competitive_matrix_builder.py competitive_data.json --format json
```

| Flag | Type | Description |
|------|------|-------------|
| `competitive_data.json` | positional | Path to JSON file with feature comparison data |
| `--format` | optional | Output format: `text` (default) or `json` |

**Scoring:** Full (3), Partial (2), Limited (1), None (0)

### 3. poc_planner.py

Generates structured POC plans with phased timelines, resource allocation, success criteria, evaluation scorecards, risk registers, and go/no-go frameworks.

```bash
python scripts/poc_planner.py poc_data.json
python scripts/poc_planner.py poc_data.json --format json
```

| Flag | Type | Description |
|------|------|-------------|
| `poc_data.json` | positional | Path to JSON file with POC scope and requirements |
| `--format` | optional | Output format: `text` (default) or `json` |

**Default Phase Breakdown:** Week 1 Setup, Weeks 2-3 Core Testing, Week 4 Advanced Testing, Week 5 Evaluation

---

## Troubleshooting

| Problem | Likely Cause | Resolution |
|---------|-------------|------------|
| RFP coverage score below 50% triggering No-Bid | Product gaps in must-have requirements or incorrect coverage assessment | Review gap items -- distinguish true gaps from items addressable via configuration, integration, or roadmap commitment; reassess before declining |
| Competitive matrix shows vulnerabilities in 3+ categories | Product gaps relative to a specific competitor, or scoring does not reflect actual competitive dynamics | Validate scoring with field SEs who have competed against this vendor; focus battlecard on differentiators where you lead, not where you trail |
| POC-to-close conversion below 60% | POC scope too broad, success criteria not aligned with buyer priorities, or wrong stakeholders involved | Narrow POC to 3-5 use cases tied to buyer's stated pain; get written agreement on success criteria before starting; ensure executive sponsor participates in evaluation |
| Win rate below 30% | Technical win but commercial loss, late involvement in deal, or poor discovery leading to misaligned demos | Engage earlier in sales cycle; improve discovery quality using MEDDIC framework; align demo storyline to buyer's language not product features |
| Demo-to-POC conversion below 40% | Demo did not address buyer's specific use case or was too generic | Customize every demo to buyer's stated requirements; use their data or industry-specific scenarios; include Q&A and next-step proposal at end |
| RFP response time exceeds 2 weeks | Manual response process without templates or pre-built content library | Build a response library indexed by requirement category; use rfp_response_analyzer.py to prioritize effort on must-have items |
| Stakeholder engagement score below 75% | Key decision-makers not involved in technical evaluation | Map stakeholder roles early; ensure executive briefing alongside technical deep-dives; send personalized follow-up to each stakeholder |

---

## Success Criteria

- Win rate exceeds 30% across all competitive opportunities
- Sales cycle length stays below 90 days from discovery to close
- POC-to-close conversion rate exceeds 60%
- RFP coverage score averages above 80% for opportunities pursued (bid decisions working correctly)
- Competitive matrix identifies minimum 3 clear differentiators per competitor
- Customer engagement score exceeds 75% (measured by stakeholder participation in evaluation milestones)
- Average RFP response time drops below 5 business days with structured response library

---

## Scope & Limitations

**In scope:** RFP/RFI response analysis and scoring, competitive feature matrix construction, proof-of-concept planning and evaluation, demo preparation frameworks, technical proposal structure, win/loss analysis methodology, and stakeholder engagement tracking across the 5-phase pre-sales workflow (Discovery, Solution Design, Demo, POC, Proposal).

**Out of scope:** Sales strategy and territory planning (account executive function), pricing and commercial terms negotiation (use pricing-strategy), post-sale implementation and customer success (use customer-success-manager), marketing content and competitive messaging (use marketing skills), and product roadmap decisions based on RFP gaps (use product-team). Tools analyze static data exports -- no integrations with CRM systems (Salesforce, HubSpot) or RFP platforms (Loopio, Arphie).

**Limitations:** Bid/no-bid thresholds are configurable but defaults assume B2B SaaS with 30%+ win-rate targets. Competitive matrix scoring is only as accurate as the input data -- validate scores with field experience against specific competitors. POC timelines assume standard 5-week engagement; highly regulated industries (healthcare, government) may require 2-3x longer. AI-assisted RFP tools (emerging in 2025-2026) can reduce response time 60-80% but are not integrated here.

---

## Integration Points

- **revenue-operations** -- Pipeline deals requiring technical validation flow through SE workflow; SE win/loss data feeds pipeline analysis
- **customer-success-manager** -- POC results and success criteria hand off to CSM for post-close adoption tracking
- **pricing-strategy** -- Competitive pricing data from matrix builder informs pricing positioning decisions
- **product-team** -- RFP gaps flagged as "Planned" or "Gap" feed into product roadmap prioritization
- **c-level-advisor** -- Strategic deals requiring executive engagement escalate through C-level advisory workflow
- **marketing** -- Competitive intelligence from marketing feeds into battlecard creation and positioning

---

**Last Updated:** March 2026
**Status:** Production-ready
**Tools:** 3 Python automation scripts
**References:** 3 knowledge base documents
**Templates:** 5 asset files
