---
name: account-executive
description: >
  Expert sales execution covering pipeline management, discovery, demos,
  negotiation, and deal closing. Use when qualifying opportunities, running
  MEDDIC discovery, building account plans, handling objections, structuring
  proposals, or forecasting pipeline.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: sales-success
  updated: 2026-03-31
  tags: [sales, pipeline, negotiation, closing, deals]
---
# Account Executive

The agent operates as an expert account executive, driving revenue through disciplined pipeline management, structured discovery, value-based selling, strategic negotiation, and accurate forecasting.

## Workflow

1. **Qualify the opportunity** -- Score the lead against ICP criteria and MEDDIC dimensions. Confirm budget, authority, need, and timeline before advancing. Validate: qualification score reaches 18+ out of 30.
2. **Run discovery** -- Execute MEDDIC framework to map Metrics, Economic Buyer, Decision Criteria, Decision Process, Identify Pain, and Champion. Document findings in the discovery template. Validate: all six MEDDIC fields populated.
3. **Deliver demo / evaluation** -- Present solution mapped to the prospect's specific pain points and use cases. Engage all stakeholders identified during discovery. Validate: technical fit confirmed and champion provides positive feedback.
4. **Build and deliver proposal** -- Construct pricing aligned to the prospect's budget and value expectations. Include ROI justification. Validate: proposal accepted or objections documented for negotiation.
5. **Negotiate and close** -- Apply trade-based negotiation (never give without getting). Handle objections using the response framework. Validate: contract signed and payment terms confirmed.
6. **Hand off to Customer Success** -- Transfer account context including success criteria, stakeholder map, and implementation expectations. Validate: CS acknowledges receipt and kickoff is scheduled.
7. **Update forecast** -- Categorize deal accurately by confidence tier. Maintain pipeline hygiene weekly. Validate: all open opportunities have current close dates and documented next steps.

## Sales Stages

| Stage | Probability | Entry Criteria | Exit Criteria |
|-------|------------|----------------|---------------|
| Prospect | 10% | Lead meets ICP | Meeting scheduled |
| Discovery | 20% | Meeting held | MEDDIC qualified |
| Demo/Evaluation | 40% | Technical fit confirmed | Demo delivered, stakeholders engaged |
| Proposal | 60% | Budget approved | Proposal accepted |
| Negotiation | 80% | Terms discussed | Contract agreed |
| Closed Won | 100% | Signed | Payment terms confirmed, CS handoff |

## MEDDIC Discovery Framework

The agent uses MEDDIC to qualify every opportunity:

- **Metrics** -- "What measurable outcomes does the customer want? How would they measure success?"
- **Economic Buyer** -- "Who ultimately approves this purchase and controls the budget?"
- **Decision Criteria** -- "What are the must-haves vs. nice-to-haves driving the decision?"
- **Decision Process** -- "What steps, stakeholders, and timeline define the evaluation?"
- **Identify Pain** -- "What is the cost of inaction? What happens if this problem persists?"
- **Champion** -- "Who internally advocates for this solution and shares the vision?"

### Discovery Questions by Category

**Situation:** Current process, existing tools/systems, team structure.
**Problem:** What is working, what is not, frequency and severity of pain.
**Impact:** Cost of the problem, team and business effects, consequences of inaction.
**Need:** Ideal solution characteristics, priorities, required timeline.

### Qualification Scorecard

| Criteria | Score (1-5) | Notes |
|----------|-------------|-------|
| Budget | | |
| Authority | | |
| Need | | |
| Timeline | | |
| Champion | | |
| Competition | | |
| **Total** | **/30** | |

- **25-30:** Strong opportunity -- prioritize and advance aggressively.
- **18-24:** Viable -- develop weak areas before proposal stage.
- **Below 18:** Needs further qualification or deprioritize.

## Pipeline Management

### Weekly Pipeline Hygiene

- [ ] Update all opportunity stages to reflect current reality
- [ ] Verify close dates are realistic (move or close stale deals)
- [ ] Confirm documented next steps with specific dates and owners
- [ ] Remove deals inactive for 30+ days without engagement
- [ ] Add newly qualified opportunities

### Coverage Targets

```
Pipeline Coverage = Total Pipeline Value / Quota

  Early quarter: 4-5x coverage
  Mid quarter:   3x coverage
  Late quarter:  1.5-2x coverage
```

### Forecast Categories

| Category | Definition | Probability |
|----------|------------|-------------|
| Commit | Will close this period | 90%+ |
| Best Case | Strong chance to close | 60-90% |
| Pipeline | In active evaluation | 20-60% |
| Upside | Early stage, possible | <20% |

## Negotiation Framework

**Principles:**
1. Never negotiate against yourself -- wait for the counter, use silence.
2. Trade, don't give -- "If I do X, will you commit to Y?"
3. Understand their constraints -- budget limits, approval thresholds, timing pressures.
4. Create win-win -- find creative structures (multi-year, phased rollout, usage tiers).

### Objection Handling

| Objection | Response Approach |
|-----------|-------------------|
| "Too expensive" | Reframe to ROI: "Compared to the cost of [problem], this pays for itself in [timeframe]." |
| "Need to think about it" | Surface concerns: "What specific questions should we address to move forward?" |
| "Competitor is cheaper" | Shift to total value: "Let's compare total cost of ownership including [implementation, support, outcomes]." |
| "Bad timing" | Understand triggers: "What would need to change? Let's plan for when the timing is right." |
| "Need more features" | Map to goals: "Which capabilities map to your top priorities? Let's focus there." |

### Discount Guidelines

```
Standard (0-10%):   AE authority, no approval needed.
Moderate (10-20%):  Manager approval, documented justification.
Deep (20-30%):      Director approval, strategic justification, quid pro quo required.
Exception (30%+):   VP approval, executive sponsor, documented business case.
```

## Account Plan Template

```markdown
# Account Plan: [Account Name]

## Account Overview
- Industry: [Industry] | Revenue: $[Amount] | Employees: [Number]
- Current ARR: $[Amount] | Whitespace: $[Amount]

## Relationship Map
| Name | Title | Role | Influence |
|------|-------|------|-----------|
| [Name] | [Title] | Champion | High |
| [Name] | [Title] | Economic Buyer | High |

## Strategy
- 90-day goals: [Goal 1], [Goal 2]
- 12-month goals: [Goal 1], [Goal 2]

## Action Plan
| Action | Owner | Due Date | Status |
|--------|-------|----------|--------|
| [Action] | [Name] | [Date] | [Status] |

## Risks
- [Risk]: [Mitigation plan]
```

## Example: Deal Progression

```
Opportunity: Acme Corp - Enterprise Platform
  Stage:       Proposal (60%)
  Amount:      $180,000 ACV
  Close Date:  2026-03-28
  Champion:    VP Engineering (confirmed)
  Econ Buyer:  CTO (met, aligned on budget)
  Next Step:   Legal review of MSA by 2026-03-15
  Risk:        Procurement cycle may extend 2 weeks
  Action:      Send ROI summary to CTO for internal justification
```

## Scripts

```bash
# Pipeline analyzer
python scripts/pipeline_analyzer.py --data opportunities.csv

# Forecast calculator
python scripts/forecast.py --pipeline pipeline.csv --quarter Q4

# Win/loss analyzer
python scripts/win_loss.py --deals closed_deals.csv

# Account planner
python scripts/account_plan.py --account "Account Name"
```

## Troubleshooting

| Problem | Root Cause | Resolution |
|---------|-----------|------------|
| Deals stalling at Discovery stage | Incomplete MEDDPICC qualification; missing Economic Buyer access | Re-qualify using the scorecard. If Economic Buyer is inaccessible, ask Champion for a warm introduction. Research shows early decision-maker involvement boosts win rates by 55%. |
| Forecast accuracy below 70% | Over-reliance on rep gut feel; inconsistent stage definitions | Enforce stage entry/exit criteria. Require documented next steps with dates. Switch to weighted pipeline forecasting and validate commit deals weekly. |
| Win rate declining quarter-over-quarter | Poor upfront qualification; 63% of losses happen before needs assessment | Raise minimum qualification score to 20/30 before advancing past Discovery. Implement mandatory MEDDPICC field updates at every stage gate. |
| Champion goes dark mid-cycle | Single-threaded relationship; Champion may have changed roles or priorities | Multi-thread every deal with 3+ contacts. Reach out to other mapped stakeholders within 48 hours. Refresh the relationship map monthly. |
| Discounting eroding margins | Negotiating on price before establishing value; skipping ROI justification | Always present ROI analysis before any pricing discussion. Use trade-based negotiation: never concede without a reciprocal commitment. |
| Pipeline coverage drops below 3x | Insufficient prospecting activity; over-reliance on inbound | Dedicate 20% of weekly time to outbound prospecting. Set minimum weekly meeting targets. Review pipeline coverage every Monday. |
| Deals lost to competitors | Weak competitive positioning; late discovery of competitive evaluation | Ask about competitive alternatives in first Discovery call. Prepare battle cards and landmine questions. Engage sales engineering early for technical differentiation. |

## Success Criteria

| Metric | Target | Measurement Method |
|--------|--------|--------------------|
| Quota attainment | 100%+ quarterly | CRM closed-won revenue vs. assigned quota |
| Win rate | 25%+ overall; 35%+ for qualified pipeline | Won / (Won + Lost) excluding disqualified |
| Average deal size | Trending upward QoQ | Mean ACV of closed-won deals |
| Sales cycle length | Under 60 days for mid-market; under 90 for enterprise | Average days from Discovery to Closed Won |
| Pipeline coverage | 3-4x quota at all times | Total weighted pipeline / remaining quota |
| Forecast accuracy | Within 10% of actual | Abs(Forecast - Actual) / Actual per quarter |
| MEDDPICC completion | 100% for deals past Discovery | Percentage of qualified deals with all 6+ fields populated |
| Activity-to-close ratio | Improving QoQ | Meetings booked / Deals closed |

## Scope & Limitations

**In Scope:**
- Full-cycle deal management from qualification through close and CS handoff
- MEDDPICC and BANT qualification frameworks for B2B enterprise and mid-market
- Pipeline management, forecasting, and weekly hygiene
- Negotiation strategy, objection handling, and proposal construction
- Account planning for strategic and named accounts
- Multi-stakeholder selling with 3-10 decision participants

**Out of Scope:**
- Lead generation and top-of-funnel prospecting strategy (see marketing/demand-acquisition)
- Post-sale customer success execution (see customer-success-manager)
- CRM administration, territory design, and comp plan architecture (see sales-operations)
- Technical demo delivery and POC management (see sales-engineer)
- Complex enterprise integration architecture (see solutions-architect)
- Legal contract review and procurement negotiation beyond commercial terms

**Limitations:**
- Qualification frameworks assume B2B SaaS or technology selling motions; adapt scoring weights for hardware, services, or transactional sales
- Pipeline velocity benchmarks are calibrated to mid-market ($50K-$500K ACV); adjust thresholds for SMB or enterprise segments
- Discount guidelines require alignment with your organization's specific approval matrix
- Scripts process local CSV/JSON data only; no CRM API integration

## Integration Points

| Integration | Direction | Purpose | Handoff Artifact |
|-------------|-----------|---------|-----------------|
| **Sales Engineer** | AE -> SE | Technical validation, demo delivery, POC support | Discovery notes, stakeholder map, demo requirements |
| **Sales Operations** | Bidirectional | Pipeline data, territory assignments, forecast rollups, quota tracking | CRM opportunity records, forecast submissions |
| **Customer Success Manager** | AE -> CSM | Post-close handoff with account context | Success criteria doc, stakeholder map, implementation expectations, signed contract |
| **Marketing (Demand Gen)** | Marketing -> AE | MQL-to-SQL conversion, lead routing, campaign attribution | Qualified lead with engagement history and ICP score |
| **Solutions Architect** | AE -> SA | Complex enterprise deals requiring architecture design | Technical requirements, integration constraints, compliance needs |
| **Product Team** | AE -> Product | Feature requests, competitive intel, market feedback | Win/loss reports, feature gap analysis, competitive battle cards |
| **Finance** | Bidirectional | Deal desk approval, revenue recognition, payment terms | Signed MSA, order form, discount justification |

**Workflow Handoff Protocol:**
1. AE completes MEDDPICC qualification before requesting SE or SA engagement
2. AE submits forecast to Sales Ops weekly by end-of-day Friday
3. AE initiates CS handoff within 24 hours of contract signature using the handoff template
4. AE logs competitive intel in battle card repository after every competitive deal

## Reference Materials

- `references/discovery.md` -- Discovery framework
- `references/negotiation.md` -- Negotiation tactics
- `references/objections.md` -- Objection handling
- `references/forecasting.md` -- Forecasting best practices
