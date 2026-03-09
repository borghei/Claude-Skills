---
name: cro-advisor
description: >
  Revenue leadership for B2B SaaS companies. Covers revenue forecasting, sales model design,
  pricing strategy, net revenue retention, sales team scaling, pipeline management, and
  board-level revenue reporting. Use when designing the revenue engine, setting quotas,
  modeling NRR, evaluating pricing, building forecasts, scaling sales teams, or when user
  mentions CRO, revenue strategy, sales model, ARR growth, NRR, expansion revenue, churn,
  pricing strategy, sales capacity, pipeline, quota, or MEDDPICC.
license: MIT + Commons Clause
metadata:
  version: 2.0.0
  author: borghei
  category: c-level
  domain: cro-leadership
  updated: 2026-03-09
  frameworks:
    - sales-playbook
    - pricing-strategy
    - nrr-playbook
    - pipeline-management
    - capacity-model
    - revenue-forecasting
  triggers:
    - CRO
    - chief revenue officer
    - revenue strategy
    - ARR
    - MRR
    - sales model
    - pipeline
    - revenue forecasting
    - pricing strategy
    - net revenue retention
    - NRR
    - gross revenue retention
    - expansion revenue
    - upsell
    - cross-sell
    - churn
    - sales capacity
    - quota
    - MEDDPICC
    - PLG
    - product-led growth
    - enterprise sales
    - sales cycle
    - CAC payback
    - magic number
    - win rate
    - ICP
    - ideal customer profile
    - territory design
  cross-references:
    - c-level-advisor/cfo-advisor
    - c-level-advisor/cmo-advisor
    - c-level-advisor/cpo-advisor
    - c-level-advisor/chro-advisor
    - c-level-advisor/ciso-advisor
    - sales-success/
    - business-growth/
---

# CRO Advisor

Revenue frameworks for building predictable, scalable revenue engines -- from first revenue to $100M ARR and beyond. Every recommendation is grounded in pipeline math, not hope.

## Keywords

CRO, chief revenue officer, revenue strategy, ARR, MRR, sales model, pipeline, revenue forecasting, pricing strategy, net revenue retention, NRR, gross revenue retention, GRR, expansion revenue, upsell, cross-sell, churn, customer success, sales capacity, quota, ramp, territory design, MEDDPICC, PLG, product-led growth, sales-led growth, enterprise sales, SMB, self-serve, value-based pricing, usage-based pricing, ICP, ideal customer profile, revenue board reporting, sales cycle, CAC payback, magic number, win rate, pipeline coverage, deal velocity

---

## Revenue Health Diagnostic

Before applying any framework, diagnose the current state.

### Revenue Health Decision Tree

```
START: "How healthy is our revenue engine?"
  |
  v
[Check NRR]
  |
  +-- NRR < 90% --> CRISIS. Existing customers are shrinking.
  |                  Stop scaling sales. Fix retention first.
  |
  +-- NRR 90-100% --> WARNING. Churn eating expansion.
  |                    Diagnose: product gap, CS gap, or ICP problem?
  |
  +-- NRR 100-110% --> HEALTHY. Base is stable. Focus on new logo + expansion.
  |
  +-- NRR > 110% --> STRONG. Expansion engine is working.
                      Check: is it sustainable or driven by price increases?
```

### Revenue Waterfall

```
Opening ARR
  + New Logo ARR       (new customers closed this period)
  + Expansion ARR      (upsell, cross-sell, seat adds)
  - Contraction ARR    (downgrades, reduced usage)
  - Churned ARR        (lost customers)
= Closing ARR

NRR = (Opening + Expansion - Contraction - Churn) / Opening x 100
GRR = (Opening - Contraction - Churn) / Opening x 100
```

---

## Revenue Metrics

### Board-Level Metrics (Monthly/Quarterly)

| Metric | Formula | Target | Red Flag |
|--------|---------|--------|----------|
| ARR Growth YoY | (Current ARR / Prior Year ARR) - 1 | 2x+ early stage, 50%+ growth | Decelerating 2+ quarters |
| NRR | See waterfall above | > 110% | < 100% |
| GRR | See waterfall above | > 85% | < 80% |
| Pipeline Coverage | Open pipeline / Quota | > 3x | < 2x entering quarter |
| Magic Number | Net New ARR x 4 / Prior Q S&M Spend | > 0.75 | < 0.5 |
| CAC Payback | S&M Spend / New ARR x (1/GM%) | < 18 months | > 24 months |
| Quota Attainment | % of reps hitting quota | 60-70% | < 50% |
| Win Rate | Closed-won / (Closed-won + Closed-lost) | > 25% | < 15% |
| Average Sales Cycle | Days from opportunity to close | Stable or decreasing | Increasing 2+ quarters |

### NRR Benchmarks

| NRR Range | Signal | Strategic Implication |
|-----------|--------|----------------------|
| > 130% | World-class (Snowflake, Twilio) | Can grow even with zero new logos |
| 110-130% | Excellent | Strong expansion motion, invest in new logo |
| 100-110% | Healthy | Expansion offsets churn, monitor trends |
| 90-100% | Concerning | Churn exceeds expansion, fix before scaling |
| < 90% | Critical | Leaky bucket, all new revenue evaporates |

---

## Sales Model Selection

### Model Comparison Matrix

| Model | ACV Range | Sales Cycle | Team | Best For |
|-------|-----------|-------------|------|----------|
| Self-serve / PLG | $0-$10K | Minutes-days | No sales team | High volume, simple product |
| SMB inside sales | $5K-$50K | 2-6 weeks | SDR + AE | Mid-volume, moderate complexity |
| Mid-market | $25K-$150K | 4-12 weeks | SDR + AE + SE | Complex product, multiple stakeholders |
| Enterprise | $100K-$1M+ | 3-12 months | AE + SE + CSM + exec sponsor | Large organizations, high touch |
| Channel/Partner | Varies | Varies | Partner manager + enablement | Market coverage, geographic reach |

### Model Selection Decision Tree

```
START: "Which sales model?"
  |
  v
[What's the average deal size?]
  |
  +-- < $5K ACV --> Self-serve / PLG
  |                  (add sales assist at $2-5K for upsell)
  |
  +-- $5K-$50K --> Inside sales (SMB)
  |                (SDRs + AEs, high velocity)
  |
  +-- $50K-$200K --> Mid-market
  |                  (SDR + AE + SE, consultative)
  |
  +-- > $200K --> Enterprise
                  (Named accounts, multi-threaded, executive selling)

HYBRID: Most companies evolve to serve 2-3 segments.
Route by ACV and buying complexity.
```

---

## Pipeline Management

### Pipeline Stage Definitions

| Stage | Definition | Exit Criteria | Typical Conversion |
|-------|-----------|---------------|-------------------|
| 0: Lead | Inbound inquiry or outbound target | Qualified as ICP fit | 20-30% to Stage 1 |
| 1: Discovery | First meeting completed | Pain confirmed, authority identified | 50-60% to Stage 2 |
| 2: Evaluation | Active evaluation, demo/POC | Champion identified, timeline set | 40-50% to Stage 3 |
| 3: Proposal | Proposal/pricing delivered | Budget confirmed, decision criteria clear | 50-60% to Stage 4 |
| 4: Negotiation | Terms being negotiated | Legal/procurement engaged | 70-80% to Close |
| 5: Closed-Won | Contract signed | Revenue recognized | -- |
| X: Closed-Lost | Deal lost | Loss reason documented | -- |

### Pipeline Coverage Model

| Quarter Position | Required Pipeline Coverage | Action If Below |
|-----------------|--------------------------|-----------------|
| Q-1 (planning) | 4x quota | Increase top-of-funnel activity |
| Q start | 3x quota | Accelerate existing deals, add pipeline |
| Mid-quarter | 2x quota | Deal acceleration, executive engagement |
| Q-end | 1.5x quota | Forecast adjustment, pull-in deals |

### Deal Qualification: MEDDPICC

| Element | Question | Red Flag |
|---------|----------|----------|
| **M**etrics | What business outcome does the buyer measure? | No quantified value proposition |
| **E**conomic Buyer | Who signs the check? Have we met them? | Never met the decision-maker |
| **D**ecision Criteria | What criteria will they use to decide? | "We'll know it when we see it" |
| **D**ecision Process | What are the steps to get to a yes? | No defined process or timeline |
| **P**aper Process | What legal/procurement steps are required? | Unknown procurement process |
| **I**dentify Pain | What problem are they solving? Is it urgent? | Pain is theoretical, not acute |
| **C**hampion | Who internally advocates for us? | No internal champion identified |
| **C**ompetition | Who else are they evaluating? | "They said no competition" (always wrong) |

---

## Pricing Strategy

### Pricing Model Selection

| Model | Best When | Watch Out For |
|-------|-----------|--------------|
| Per-seat | Value scales with users | Seat consolidation games |
| Usage-based | Value directly tied to consumption | Revenue unpredictability |
| Tiered | Clear feature differentiation between segments | Tier boundaries feel arbitrary |
| Flat-rate | Simple product, uniform usage | Leaves money on table for heavy users |
| Value-based | Clear ROI measurement possible | Requires trust and proof |
| Hybrid | Complex product with multiple value dimensions | Complexity in quoting |

### Pricing Decision Framework

```
START: "How should we price?"
  |
  v
[What is the primary value driver for the customer?]
  |
  +-- Number of users --> Per-seat pricing
  |
  +-- Volume of usage --> Usage-based pricing
  |
  +-- Feature needs differ by segment --> Tiered pricing
  |
  +-- Clear ROI (saves $X) --> Value-based (price at 10-20% of value)
  |
  +-- Multiple value drivers --> Hybrid (base + usage/seats)
```

### Pricing Health Indicators

| Signal | Healthy | Unhealthy |
|--------|---------|-----------|
| Price objection rate | < 20% of proposals | > 40% = value communication broken |
| Discount rate (avg) | < 15% off list | > 25% = pricing not anchored to value |
| Time since last increase | < 12 months | > 24 months = inflation eating margin |
| Price increase churn | < 2% incremental churn | > 5% = increase was too aggressive |
| Win rate after increase | Stable or improved | Dropped > 10 points = over-corrected |

---

## Sales Team Scaling

### Capacity Model

```
Required AEs = Target New ARR / (Quota x Attainment Rate x Ramp Factor)

Example:
  Target: $5M new ARR
  Quota per AE: $1M
  Attainment: 65%
  Ramp factor: 0.85 (accounts for ramp time)

  Required AEs = $5M / ($1M x 0.65 x 0.85) = 9.1 --> Hire 10 AEs
```

### Sales Team Structure by ARR

| ARR | Team Structure | Key Hires |
|-----|---------------|-----------|
| $0-$1M | Founder-led sales | No sales team yet |
| $1-$3M | 1-2 AEs | First AE, maybe first SDR |
| $3-$10M | 3-6 AEs, 2-4 SDRs, 1 sales manager | First sales manager, first SE |
| $10-$25M | VP Sales, 2 teams, SDR team, SE team | VP Sales, Rev Ops, CS Manager |
| $25-$50M | CRO, multiple segments, CS org | CRO, segment leaders, enablement |
| $50M+ | Full revenue org | SVPs, regional leaders, strategy |

### Quota Setting Guidelines

| Metric | Guideline |
|--------|-----------|
| Quota : OTE ratio | 4-6x (e.g., $800K quota for $160K OTE) |
| Ramp period | 3-6 months depending on sales cycle |
| Ramp quota | 25% (M1-2), 50% (M3-4), 75% (M5-6), 100% (M7+) |
| Quota coverage target | Hire for 120-130% of plan (accounts for attrition + ramp) |
| % of team hitting quota | Target 60-70%. < 50% = quota too high. > 80% = too low. |

---

## Red Flags

- NRR declining 2 quarters in a row -- customer value proposition is broken
- Pipeline coverage < 3x entering quarter -- forecasting a miss
- Win rate dropping while sales cycle extends -- competitive pressure or ICP drift
- < 50% of AEs quota-attaining -- comp plan, ramp, or quota calibration issue
- Average deal size declining -- moving downmarket under pressure
- Magic Number < 0.5 -- sales spend not converting to revenue
- Forecast accuracy < 80% -- pipeline quality or rep sandbagging
- Single customer > 15% of ARR -- concentration risk
- "Too expensive" in > 40% of loss notes -- value demonstration broken, not price
- Expansion ARR < 20% of total new ARR -- upsell motion missing
- No win/loss analysis process -- learning nothing from every deal outcome
- Sales and CS not aligned on health scoring -- churn surprises

---

## Integration with C-Suite

| When... | CRO Works With... | To... |
|---------|-------------------|-------|
| Pricing changes | CPO + CFO | Align value positioning, model margin impact |
| Product roadmap | CPO (`cpo-advisor`) | Ensure features support ICP and close pipeline |
| Headcount plan | CFO + CHRO | Capacity model with ROI justification |
| NRR declining | CPO + COO | Root cause: product gap or CS process failure |
| Enterprise expansion | CEO (`ceo-advisor`) | Executive sponsorship for key accounts |
| Revenue targets | CFO (`cfo-advisor`) | Bottom-up model to validate top-down targets |
| Pipeline SLA | CMO (`cmo-advisor`) | MQL-to-SQL conversion, CAC by channel |
| Security reviews | CISO (`ciso-advisor`) | Unblock enterprise deals with security artifacts |
| Sales ops | COO (`coo-advisor`) | RevOps staffing, commission infrastructure |
| Sales hiring | CHRO (`chro-advisor`) | Comp plans, ramp modeling, territory design |
| Competitive wins/losses | Competitive Intel (`competitive-intel`) | Battlecard updates, positioning |

---

## Proactive Triggers

- NRR < 100% -- retention must be fixed before scaling acquisition
- Pipeline coverage < 3x -- forecast at risk, flag to CEO immediately
- Win rate declining 2+ quarters -- sales process or product alignment issue
- Top customer > 20% of ARR -- concentration risk, diversify immediately
- No pricing review in 12+ months -- likely leaving revenue on the table
- Expansion revenue < 15% of new ARR -- missing upsell/cross-sell opportunity
- Sales cycle lengthening -- competitive or product issue, investigate
- > 30% discount rate on deals -- pricing or value communication problem

---

## Output Artifacts

| Request | Deliverable |
|---------|-------------|
| "Forecast next quarter" | Pipeline-based forecast with confidence intervals and scenarios |
| "Analyze our churn" | Cohort analysis with at-risk accounts and intervention plan |
| "Review our pricing" | Pricing analysis with benchmarks, value framework, recommendations |
| "Scale the sales team" | Capacity model with quota, ramp, territories, comp plan |
| "Revenue board section" | ARR waterfall, NRR, pipeline coverage, forecast, risks |
| "Design sales process" | Stage definitions, qualification criteria, deal review cadence |
| "Win/loss analysis" | Aggregate findings by competitor, segment, and reason |
