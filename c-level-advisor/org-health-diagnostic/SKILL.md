---
name: org-health-diagnostic
description: >
  Cross-functional organizational health check combining signals from all
  C-suite roles. Scores 8 dimensions on a traffic-light scale with drill-down
  recommendations and cascade analysis. Use when assessing overall company
  health, preparing for board reviews, identifying at-risk functions, diagnosing
  cross-functional problems, or when user mentions org health, health check,
  health dashboard, company health, functional health, or health assessment.
license: MIT + Commons Clause
metadata:
  version: 2.0.0
  author: borghei
  category: c-level
  domain: organizational-health
  updated: 2026-03-09
  frameworks:
    - health-benchmarks
    - 8-dimension-model
    - cascade-analysis
    - stage-adjusted-scoring
    - graceful-degradation
  triggers:
    - org health
    - organizational health
    - health diagnostic
    - health dashboard
    - health check
    - company health
    - functional health
    - team health
    - startup health
    - health scorecard
    - health assessment
    - risk dashboard
    - overall health
    - company assessment
---
# Org Health Diagnostic

Eight dimensions. Traffic lights. Real benchmarks. Surfaces the problems you do not know you have and shows how problems in one dimension cascade to others.

## Keywords

org health, organizational health, health diagnostic, health dashboard, health check, company health, functional health, team health, startup health, health scorecard, health assessment, risk dashboard, cross-functional health, dimension cascade, stage benchmarks

---

## The 8 Dimensions

### Dimension Overview

| # | Dimension | C-Suite Owner | Core Question |
|---|-----------|--------------|---------------|
| 1 | Financial Health | CFO | Can we fund operations and invest in growth? |
| 2 | Revenue Health | CRO | Are customers staying, growing, and recommending us? |
| 3 | Product Health | CPO | Do customers love and use the product? |
| 4 | Engineering Health | CTO | Can we ship reliably and sustain velocity? |
| 5 | People Health | CHRO | Is the team stable, engaged, and growing? |
| 6 | Operational Health | COO | Are we executing our strategy with discipline? |
| 7 | Security Health | CISO | Are we protecting customers and maintaining compliance? |
| 8 | Market Health | CMO | Are we winning in the market and growing efficiently? |

---

### Dimension 1: Financial Health (CFO)

| Metric | Green (7-10) | Yellow (4-6) | Red (1-3) |
|--------|-------------|-------------|-----------|
| Runway (months) | > 18 | 9-18 | < 9 |
| Burn multiple | < 1.5x | 1.5-2.5x | > 2.5x |
| Gross margin | > 70% | 55-70% | < 55% |
| Revenue concentration (top customer) | < 10% | 10-20% | > 20% |
| MoM growth rate | Above benchmark | At benchmark | Below benchmark |

### Dimension 2: Revenue Health (CRO)

| Metric | Green (7-10) | Yellow (4-6) | Red (1-3) |
|--------|-------------|-------------|-----------|
| NRR | > 110% | 100-110% | < 100% |
| Logo churn (annual) | < 5% | 5-10% | > 10% |
| Pipeline coverage (next Q) | > 3x | 2-3x | < 2x |
| CAC payback | < 12 months | 12-18 months | > 18 months |
| Win rate | > 25% | 15-25% | < 15% |

### Dimension 3: Product Health (CPO)

| Metric | Green (7-10) | Yellow (4-6) | Red (1-3) |
|--------|-------------|-------------|-----------|
| NPS | > 40 | 20-40 | < 20 |
| DAU/MAU ratio | > 40% | 20-40% | < 20% |
| Core feature adoption | > 60% | 30-60% | < 30% |
| Time to value | Decreasing QoQ | Stable | Increasing QoQ |
| CSAT | > 4.2/5 | 3.5-4.2 | < 3.5 |

### Dimension 4: Engineering Health (CTO)

| Metric | Green (7-10) | Yellow (4-6) | Red (1-3) |
|--------|-------------|-------------|-----------|
| Deploy frequency | Daily | Weekly | Monthly or less |
| Change failure rate | < 5% | 5-15% | > 15% |
| MTTR | < 1 hour | 1-4 hours | > 4 hours |
| Tech debt ratio (% of sprint) | < 20% | 20-35% | > 35% |
| P0/P1 incidents per month | < 2 | 2-5 | > 5 |

### Dimension 5: People Health (CHRO)

| Metric | Green (7-10) | Yellow (4-6) | Red (1-3) |
|--------|-------------|-------------|-----------|
| Regrettable attrition (annual) | < 10% | 10-20% | > 20% |
| eNPS | > 30 | 0-30 | < 0 |
| Time to fill (avg days) | < 45 | 45-90 | > 90 |
| Manager:IC ratio | 1:5-1:8 | 1:3-1:5 or 1:8-1:12 | Outside range |
| Internal promotion rate | > 30% | 15-30% | < 15% |

### Dimension 6: Operational Health (COO)

| Metric | Green (7-10) | Yellow (4-6) | Red (1-3) |
|--------|-------------|-------------|-----------|
| OKR completion rate | > 70% | 50-70% | < 50% |
| Decision cycle time | < 48 hours | 48hrs-1 week | > 1 week |
| Meeting effectiveness | Clear outcomes | Mixed | No outcomes |
| Cross-functional initiative completion | > 80% on time | 50-80% | < 50% |
| Process documentation coverage | > 70% | 40-70% | < 40% |

### Dimension 7: Security Health (CISO)

| Metric | Green (7-10) | Yellow (4-6) | Red (1-3) |
|--------|-------------|-------------|-----------|
| Security incidents (90 days) | 0 | 1-2 minor | 1+ major |
| Compliance status | All current | In progress | Overdue/lapsed |
| Critical vuln remediation SLA | 100% in SLA | > 90% | < 90% |
| Security training completion | > 95% | 80-95% | < 80% |
| Pen test recency | < 12 months | 12-24 months | > 24 months |

### Dimension 8: Market Health (CMO)

| Metric | Green (7-10) | Yellow (4-6) | Red (1-3) |
|--------|-------------|-------------|-----------|
| CAC trend | Improving QoQ | Stable | Worsening QoQ |
| Organic vs paid lead mix | > 50% organic | 30-50% organic | < 30% organic |
| Win rate vs competitors | Improving | Stable | Declining |
| Brand awareness (in ICP) | > 40% | 20-40% | < 20% |
| Pipeline contribution (marketing) | > 40% | 20-40% | < 20% |

---

## Scoring System

### Individual Dimension Score

Each dimension scores 1-10 based on weighted metrics:

```
Dimension Score = Sum(metric_score x metric_weight) / Sum(weights)

Traffic Light:
  Green (7-10):  Healthy -- maintain and optimize
  Yellow (4-6):  Watch -- trend matters (improving or declining?)
  Red (1-3):     Action required -- address within 30 days
```

### Overall Health Score

Weighted average by company stage:

| Dimension | Seed Weight | Series A | Series B | Series C+ |
|-----------|------------|----------|----------|-----------|
| Financial | 20% | 15% | 15% | 15% |
| Revenue | 10% | 20% | 20% | 20% |
| Product | 25% | 20% | 15% | 10% |
| Engineering | 15% | 15% | 15% | 10% |
| People | 10% | 10% | 15% | 15% |
| Operations | 5% | 10% | 10% | 15% |
| Security | 5% | 5% | 5% | 10% |
| Market | 10% | 5% | 5% | 5% |

### Stage-Adjusted Benchmarks

Different stages have different healthy ranges. A Seed company with 6-month runway is normal; a Series C company with 6-month runway is a crisis.

| Stage | Runway Target | Burn Multiple | Team Size | Revenue Threshold |
|-------|--------------|---------------|-----------|-------------------|
| Seed | > 12 months | Not applicable | 2-10 | Pre-revenue acceptable |
| Series A | > 18 months | < 3x | 10-40 | > $500K ARR |
| Series B | > 18 months | < 2x | 30-100 | > $3M ARR |
| Series C+ | > 24 months | < 1.5x | 80-300 | > $15M ARR |

---

## Cascade Analysis

### How Dimension Failures Propagate

This is the most important part of the diagnostic. Problems in one dimension inevitably create problems in others.

| If This Is Red... | Watch These Next... | Why |
|-------------------|---------------------|-----|
| Financial | People -> Engineering -> Product | Budget cuts -> hiring freeze -> velocity drops -> product stalls |
| Revenue | Financial -> People -> Market | Cash gap -> attrition risk -> positioning weakens |
| Product | Revenue -> Market -> People | NRR drops -> CAC rises -> top talent leaves |
| Engineering | Product -> Revenue | Features slip -> deals stall on missing features |
| People | Engineering -> Product -> Revenue | Velocity drops -> quality drops -> churn rises |
| Operations | ALL dimensions degrade over time | Execution failure cascades everywhere |
| Security | Revenue (enterprise) -> Financial | Enterprise deals blocked -> revenue impact |
| Market | Revenue -> Financial | Lead pipeline dries up -> sales suffers |

### Cascade Risk Decision Tree

```
START: Dimension scores calculated
  |
  v
[Any dimension RED?]
  |
  +-- NO  --> [Any dimension YELLOW with declining trend?]
  |            |
  |            +-- YES --> Monitor cascade. Check connected dimensions.
  |            +-- NO  --> Healthy. Maintain current approach.
  |
  +-- YES --> [Check cascade connections]
              |
              v
            [Are connected dimensions also Yellow/Red?]
              |
              +-- YES --> SYSTEMIC ISSUE. Root cause in the Red dimension.
              |           Address Red dimension first. Connected will improve.
              |
              +-- NO  --> ISOLATED ISSUE. Fix Red dimension before it cascades.
                          Timeline: 30 days or cascade begins.
```

---

## Dashboard Output Format

```
ORG HEALTH DIAGNOSTIC -- [Company] -- [Date]
Stage: [Seed/A/B/C]   Overall: [Score]/10   Trend: [Improving/Stable/Declining]

DIMENSION SCORES
------------------------------------------------------------
  Financial     [G] 8.2  Runway 14mo, burn 1.6x
  Revenue       [Y] 5.8  NRR 104%, pipeline thin (1.8x)
  Product       [G] 7.4  NPS 42, DAU/MAU 38%
  Engineering   [Y] 5.2  Debt at 30%, MTTR 3.2h
  People        [R] 3.8  Attrition 24%, eNPS -5
  Operations    [Y] 6.0  OKR 65% completion
  Security      [G] 7.8  SOC 2 complete, 0 incidents
  Market        [Y] 5.5  CAC rising, win rate 22%
------------------------------------------------------------

TOP PRIORITIES (address in order)
[R] 1. People: attrition at 24%
       Impact: Engineering velocity drops in 60 days (cascade risk)
       Action: Retention audit + intervention for top 5 at-risk
       Owner: CHRO + CEO | Timeline: This week

[Y] 2. Revenue: pipeline at 1.8x
       Impact: Q+1 miss risk is high
       Action: Add 3 qualified opps in 30 days or adjust forecast
       Owner: CRO | Timeline: 30 days

[Y] 3. Engineering: tech debt at 30%
       Impact: Shipping velocity slows by Q3
       Action: Dedicated debt sprint plan
       Owner: CTO | Timeline: 45 days

CASCADE WARNING
  People [R] --> Engineering [Y] cascade risk
  If attrition continues: engineering velocity drops -> product delays
  -> revenue impact in 2 quarters

DATA GAPS
  [!] Market: Brand awareness data needed
  [!] Operations: Meeting effectiveness not measured
```

---

## Graceful Degradation

Not all data is always available. The diagnostic handles partial data:

| Data Availability | Approach |
|------------------|----------|
| All metrics available | Full scoring, all dimensions |
| Missing 1-2 metrics per dimension | Score available metrics, flag gaps |
| Missing entire dimension | Exclude from overall score, flag as "[data needed]" |
| Only 3-4 dimensions have data | Partial diagnostic, clearly marked |

---

## Diagnostic Cadence

| Frequency | Scope | Audience |
|-----------|-------|----------|
| Weekly | Scorecard metrics only (2-3 per dimension) | Leadership team |
| Monthly | Full 8-dimension assessment | CEO + direct reports |
| Quarterly | Deep diagnostic with cascade analysis + benchmarks | Board-ready report |
| Annual | Full diagnostic + year-over-year comparison + strategy implications | Board + investors |

---

## Red Flags

- Any dimension Red for 2+ consecutive months -- systemic problem, not a blip
- 3+ dimensions Yellow simultaneously -- organizational strain, prioritize ruthlessly
- Overall score declining 3+ months -- strategic review needed
- Cascade warning triggered and not addressed in 30 days -- will get worse
- Data gaps persist for 2+ cycles -- measurement culture problem
- Score improving but team sentiment declining -- measurement gaming
- No dimension ever Red -- either the company is exceptional or standards are too low

---

## Integration with C-Suite

| Dimension | Owner Skill | Drill-Down |
|-----------|------------|------------|
| Financial | CFO Advisor (`cfo-advisor`) | Deep financial analysis |
| Revenue | CRO Advisor (`cro-advisor`) | Pipeline and retention analysis |
| Product | CPO Advisor (`cpo-advisor`) | PMF assessment and portfolio review |
| Engineering | CTO Advisor (`cto-advisor`) | Technical health and debt analysis |
| People | CHRO Advisor (`chro-advisor`) | Retention, engagement, org design |
| Operations | COO Advisor (`coo-advisor`) | Process maturity, execution cadence |
| Security | CISO Advisor (`ciso-advisor`) | Risk register, compliance status |
| Market | CMO Advisor (`cmo-advisor`) | Positioning, channel effectiveness |

---

## Output Artifacts

| Request | Deliverable |
|---------|-------------|
| "How healthy is the company?" | Full 8-dimension dashboard with traffic lights |
| "What should we fix first?" | Prioritized action list with cascade analysis |
| "Prepare health section for board" | Board-ready health summary with trends |
| "Compare to last quarter" | Quarter-over-quarter comparison with trend arrows |
| "Where are we at risk?" | Cascade risk map with interconnected failures |
| "What data do we need?" | Data gap analysis with collection recommendations |

---

## Troubleshooting

| Problem | Likely Cause | Resolution |
|---------|-------------|------------|
| Scores consistently show all green but team sentiment is negative | Metrics being gamed or standards set too low; measurement doesn't capture reality | Cross-reference quantitative scores with qualitative signals (exit interviews, Glassdoor, skip-level conversations); raise benchmarks to industry-standard levels |
| Cascade analysis shows systemic issue but leadership disagrees | Red dimension owners resistant to acknowledging problems | Present cascade evidence with data: "People Red for 2 months → Engineering Yellow → Product delays in pipeline"; use McKinsey OHI principle of benchmarking against external data |
| Data gaps persist across multiple diagnostic cycles | No measurement infrastructure; teams don't prioritize data collection | Assign data collection to specific owners with deadlines; start with proxy metrics where direct measurement is unavailable |
| Diagnostic takes too long to produce (> 2 weeks) | Trying to measure everything perfectly instead of using available data | Apply graceful degradation: score what you have, flag gaps, iterate; a partial diagnostic now beats a perfect one in 6 weeks |
| Different stakeholders interpret traffic light scores differently | No shared understanding of what Green/Yellow/Red means operationally | Document specific thresholds for each metric in each dimension; share calibration examples ("Red runway = less than 9 months at current burn") |
| Quarterly diagnostic shows no change despite interventions | Wrong interventions, or interventions not given enough time, or measuring lagging indicators | Verify interventions target root cause not symptoms; check leading indicators alongside lagging ones; allow 2 quarters for structural changes to show in scores |
| Board wants a single number but diagnostic is multi-dimensional | Board unfamiliar with the 8-dimension model | Provide the weighted overall score (1-10) as headline with stage-adjusted weighting; drill-down dimensions available on request |

---

## Success Criteria

- All 8 dimensions scored with traffic lights within 5 business days of data collection start
- Cascade analysis correctly predicts downstream impacts: when a Red dimension is not addressed, connected dimensions degrade within 2 quarters
- Stage-adjusted benchmarks applied correctly: Seed company not held to Series C standards and vice versa
- Top 3 priorities identified with specific owners, timelines, and verification methods
- Data gaps reduced by at least 50% between first and second diagnostic cycle
- Board-ready health summary produced quarterly with trend comparison to prior quarter
- Overall health score trending stable or improving over 3 consecutive quarters

---

## Scope & Limitations

- **In scope:** 8-dimension organizational health scoring, traffic light dashboards, cascade analysis, stage-adjusted benchmarks, graceful degradation for partial data, diagnostic cadence recommendations, board-ready reporting
- **Out of scope:** Deep functional diagnostics within a single dimension (use the respective C-suite advisor skill); employee engagement survey design and administration (use CHRO Advisor); financial auditing (use external auditors); security penetration testing (use CISO Advisor)
- **Limitation:** Diagnostic quality depends on data accuracy; garbage in, garbage out applies -- verify data sources
- **Limitation:** McKinsey OHI benchmarks are based on large enterprise data; early-stage companies may need adjusted benchmarks
- **Limitation:** The 8-dimension model is a simplification; some organizations may need additional dimensions (e.g., ESG, regulatory) depending on industry
- **Limitation:** Cascade predictions are based on common patterns; specific organizations may have unique cascade paths

---

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `cfo-advisor` | Financial Health dimension deep dive | Health financial score → CFO detailed analysis |
| `cro-advisor` | Revenue Health dimension deep dive | Health revenue score → CRO pipeline review |
| `cpo-advisor` | Product Health dimension deep dive | Health product score → CPO PMF assessment |
| `cto-advisor` | Engineering Health dimension deep dive | Health engineering score → CTO tech debt plan |
| `chro-advisor` | People Health dimension deep dive | Health people score → CHRO retention strategy |
| `coo-advisor` | Operational Health dimension deep dive | Health operations score → COO process review |
| `ciso-advisor` | Security Health dimension deep dive | Health security score → CISO risk register |
| `cmo-advisor` | Market Health dimension deep dive | Health market score → CMO channel review |
| `strategic-alignment` | Health scores inform alignment priorities | Health priorities → Alignment focus areas |
| `executive-mentor` | Red dimensions trigger executive coaching focus | Health red flags → Mentor challenge areas |

---

## Python Tools

| Tool | Purpose | Usage |
|------|---------|-------|
| `scripts/org_health_scorer.py` | Score all 8 dimensions with traffic lights, stage-adjusted weighting, and overall health calculation | `python scripts/org_health_scorer.py --stage series-a --financial 7.5 --revenue 5.8 --product 7.2 --engineering 5.0 --people 3.5 --operations 6.0 --security 7.8 --market 5.5 --json` |
| `scripts/span_of_control_analyzer.py` | Analyze manager-to-IC ratios across the organization and flag unhealthy spans | `python scripts/span_of_control_analyzer.py --org-file org_structure.csv --json` |
| `scripts/engagement_benchmarker.py` | Benchmark engagement metrics against industry standards and flag gaps | `python scripts/engagement_benchmarker.py --enps 15 --attrition 18 --time-to-fill 60 --promotion-rate 20 --industry saas --json` |
