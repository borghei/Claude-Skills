---
name: account-executive
description: Expert sales execution covering pipeline management, discovery, demos, negotiation, and deal closing.
version: 1.0.0
author: borghei
category: sales-success
tags: [sales, pipeline, negotiation, closing, deals]
---

# Account Executive

Expert-level sales execution for revenue growth.

## Core Competencies

- Pipeline management
- Discovery and qualification
- Solution selling
- Negotiation
- Deal closing
- Account planning
- Forecasting
- Relationship building

## Sales Process

### Sales Stages

```
STAGE 1: PROSPECT (10%)
├── Lead identified
├── Initial outreach
└── Meeting scheduled

STAGE 2: DISCOVERY (20%)
├── Pain points identified
├── Budget confirmed
├── Decision process understood
└── Timeline established

STAGE 3: DEMO/EVALUATION (40%)
├── Solution presented
├── Technical validation
├── Value proposition aligned
└── Stakeholders engaged

STAGE 4: PROPOSAL (60%)
├── Proposal delivered
├── Pricing discussed
├── Terms negotiated
└── Champion confirmed

STAGE 5: NEGOTIATION (80%)
├── Contract reviewed
├── Legal/procurement engaged
├── Final terms agreed
└── Signatures pending

STAGE 6: CLOSED WON (100%)
├── Contract signed
├── Payment terms confirmed
└── Handoff to CS
```

### Stage Criteria

| Stage | Entry Criteria | Exit Criteria |
|-------|---------------|---------------|
| Prospect | Lead meets ICP | Meeting scheduled |
| Discovery | Meeting held | BANT qualified |
| Demo | Technical fit | Demo delivered |
| Proposal | Budget approved | Proposal accepted |
| Negotiation | Terms discussed | Contract agreed |
| Closed | Signed | Payment received |

## Discovery

### MEDDIC Framework

```
M - Metrics
    What measurable outcomes does the customer want?
    "What would success look like? How would you measure it?"

E - Economic Buyer
    Who has the budget authority?
    "Who ultimately approves this purchase?"

D - Decision Criteria
    What factors will drive the decision?
    "What are your must-haves vs nice-to-haves?"

D - Decision Process
    How will they evaluate and decide?
    "Walk me through your evaluation process."

I - Identify Pain
    What problem are they trying to solve?
    "What's the impact of not solving this?"

C - Champion
    Who will advocate for you internally?
    "Who else shares your vision for this?"
```

### Discovery Questions

**Situation:**
- Tell me about your current process for [X]
- What tools/systems are you using today?
- How is your team structured?

**Problem:**
- What's working well? What's not?
- What happens when [problem] occurs?
- How often does this happen?

**Impact:**
- What's the cost of this problem?
- How does this affect your team?
- What happens if you don't solve this?

**Need:**
- What would an ideal solution look like?
- What's most important to you?
- By when do you need this solved?

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

**Score Interpretation:**
- 25-30: Strong opportunity
- 18-24: Work on weak areas
- <18: Needs more qualification

## Pipeline Management

### Pipeline Hygiene

**Weekly Review:**
- [ ] Update all opportunity stages
- [ ] Verify close dates
- [ ] Confirm next steps
- [ ] Remove stale deals
- [ ] Add new opportunities

**Monthly Review:**
- [ ] Analyze win/loss reasons
- [ ] Review pipeline coverage
- [ ] Assess forecast accuracy
- [ ] Identify coaching opportunities

### Pipeline Coverage

```
PIPELINE COVERAGE = Total Pipeline Value / Quota

Targets:
- Early quarter: 4-5x coverage
- Mid quarter: 3x coverage
- Late quarter: 1.5-2x coverage

By Stage:
- Commit: 1x quota minimum
- Best Case: 1.5x quota
- Pipeline: 3x quota
```

### Forecast Categories

| Category | Definition | Probability |
|----------|------------|-------------|
| Commit | Will close this period | 90%+ |
| Best Case | Strong chance to close | 60-90% |
| Pipeline | In active evaluation | 20-60% |
| Upside | Early stage, possible | <20% |

## Negotiation

### Negotiation Principles

**1. Never Negotiate Against Yourself**
- Wait for their counter
- Silence is powerful
- Don't offer discounts unprompted

**2. Trade, Don't Give**
- Always get something in return
- "If I do X, will you do Y?"
- Maintain value perception

**3. Understand Their Constraints**
- Budget limits
- Approval thresholds
- Timing pressures

**4. Create Win-Win**
- Find creative solutions
- Expand the pie
- Long-term relationship focus

### Common Objections

| Objection | Response |
|-----------|----------|
| "Too expensive" | "Compared to what? Let's look at the ROI..." |
| "Need to think about it" | "Of course. What specific concerns should we address?" |
| "Competitor is cheaper" | "What are you comparing? Let's look at total value..." |
| "Bad timing" | "I understand. What would need to change?" |
| "Need more features" | "Which ones? Let's discuss what you're trying to achieve..." |

### Discount Guidelines

```
DISCOUNT TIERS

Standard (0-10%):
- AE authority
- No approval needed

Moderate (10-20%):
- Manager approval
- Requires justification

Deep (20-30%):
- Director approval
- Strategic justification
- Quid pro quo required

Exception (30%+):
- VP approval
- Executive sponsor
- Documented business case
```

## Account Planning

### Account Plan Template

```markdown
# Account Plan: [Account Name]

## Account Overview
- Industry: [Industry]
- Revenue: $[Amount]
- Employees: [Number]
- Current ARR: $[Amount]

## Relationship Map
| Name | Title | Relationship | Influence |
|------|-------|--------------|-----------|
| [Name] | [Title] | Champion | High |
| [Name] | [Title] | Economic Buyer | High |

## Opportunity Assessment
- Whitespace: $[Amount]
- Current products: [List]
- Expansion opportunities: [List]

## Account Strategy
### Short-term (90 days)
- [Goal 1]
- [Goal 2]

### Long-term (12 months)
- [Goal 1]
- [Goal 2]

## Action Plan
| Action | Owner | Date | Status |
|--------|-------|------|--------|
| [Action] | [Name] | [Date] | [Status] |

## Risks
- [Risk 1]: [Mitigation]
```

## Sales Metrics

### Activity Metrics

| Metric | Target |
|--------|--------|
| Calls/day | 50+ |
| Emails/day | 100+ |
| Meetings/week | 15+ |
| Demos/week | 5+ |
| Proposals/week | 2+ |

### Outcome Metrics

| Metric | Target |
|--------|--------|
| Win rate | 25%+ |
| Average deal size | $[X] |
| Sales cycle | [X] days |
| Quota attainment | 100%+ |
| Pipeline coverage | 3x+ |

## Reference Materials

- `references/discovery.md` - Discovery framework
- `references/negotiation.md` - Negotiation tactics
- `references/objections.md` - Objection handling
- `references/forecasting.md` - Forecasting best practices

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
