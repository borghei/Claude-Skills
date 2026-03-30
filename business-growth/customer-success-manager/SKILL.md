---
name: customer-success-manager
description: >
  Monitors customer health, predicts churn risk, and identifies expansion
  opportunities using weighted scoring models for SaaS customer success
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: business-growth
  domain: customer-success
  updated: 2026-02-06
  tags: [customer-success, churn, health-score, expansion, saas]
  python-tools: health_score_calculator.py, churn_risk_analyzer.py, expansion_opportunity_scorer.py
  tech-stack: customer-success, saas-metrics, health-scoring
---
# Customer Success Manager

Production-grade customer success analytics with multi-dimensional health scoring, churn risk prediction, and expansion opportunity identification. Three Python CLI tools provide deterministic, repeatable analysis using standard library only -- no external dependencies, no API calls, no ML models.

---

## Table of Contents

- [Capabilities](#capabilities)
- [Input Requirements](#input-requirements)
- [Output Formats](#output-formats)
- [How to Use](#how-to-use)
- [Scripts](#scripts)
- [Reference Guides](#reference-guides)
- [Templates](#templates)
- [Best Practices](#best-practices)
- [Limitations](#limitations)

---

## Capabilities

- **Customer Health Scoring**: Multi-dimensional weighted scoring across usage, engagement, support, and relationship dimensions with Red/Yellow/Green classification
- **Churn Risk Analysis**: Behavioral signal detection with tier-based intervention playbooks and time-to-renewal urgency multipliers
- **Expansion Opportunity Scoring**: Adoption depth analysis, whitespace mapping, and revenue opportunity estimation with effort-vs-impact prioritization
- **Segment-Aware Benchmarking**: Configurable thresholds for Enterprise, Mid-Market, and SMB customer segments
- **Trend Analysis**: Period-over-period comparison to detect improving or declining trajectories
- **Executive Reporting**: QBR templates, success plans, and executive business review templates

---

## Input Requirements

All scripts accept a JSON file as positional input argument. See `assets/sample_customer_data.json` for complete examples.

### Health Score Calculator

```json
{
  "customers": [
    {
      "customer_id": "CUST-001",
      "name": "Acme Corp",
      "segment": "enterprise",
      "arr": 120000,
      "usage": {
        "login_frequency": 85,
        "feature_adoption": 72,
        "dau_mau_ratio": 0.45
      },
      "engagement": {
        "support_ticket_volume": 3,
        "meeting_attendance": 90,
        "nps_score": 8,
        "csat_score": 4.2
      },
      "support": {
        "open_tickets": 2,
        "escalation_rate": 0.05,
        "avg_resolution_hours": 18
      },
      "relationship": {
        "executive_sponsor_engagement": 80,
        "multi_threading_depth": 4,
        "renewal_sentiment": "positive"
      },
      "previous_period": {
        "usage_score": 70,
        "engagement_score": 65,
        "support_score": 75,
        "relationship_score": 60
      }
    }
  ]
}
```

### Churn Risk Analyzer

```json
{
  "customers": [
    {
      "customer_id": "CUST-001",
      "name": "Acme Corp",
      "segment": "enterprise",
      "arr": 120000,
      "contract_end_date": "2026-06-30",
      "usage_decline": {
        "login_trend": -15,
        "feature_adoption_change": -10,
        "dau_mau_change": -0.08
      },
      "engagement_drop": {
        "meeting_cancellations": 2,
        "response_time_days": 5,
        "nps_change": -3
      },
      "support_issues": {
        "open_escalations": 1,
        "unresolved_critical": 0,
        "satisfaction_trend": "declining"
      },
      "relationship_signals": {
        "champion_left": false,
        "sponsor_change": false,
        "competitor_mentions": 1
      },
      "commercial_factors": {
        "contract_type": "annual",
        "pricing_complaints": false,
        "budget_cuts_mentioned": false
      }
    }
  ]
}
```

### Expansion Opportunity Scorer

```json
{
  "customers": [
    {
      "customer_id": "CUST-001",
      "name": "Acme Corp",
      "segment": "enterprise",
      "arr": 120000,
      "contract": {
        "licensed_seats": 100,
        "active_seats": 95,
        "plan_tier": "professional",
        "available_tiers": ["professional", "enterprise", "enterprise_plus"]
      },
      "product_usage": {
        "core_platform": {"adopted": true, "usage_pct": 85},
        "analytics_module": {"adopted": true, "usage_pct": 60},
        "integrations_module": {"adopted": false, "usage_pct": 0},
        "api_access": {"adopted": true, "usage_pct": 40},
        "advanced_reporting": {"adopted": false, "usage_pct": 0}
      },
      "departments": {
        "current": ["engineering", "product"],
        "potential": ["marketing", "sales", "support"]
      }
    }
  ]
}
```

---

## Output Formats

All scripts support two output formats via the `--format` flag:

- **`text`** (default): Human-readable formatted output for terminal viewing
- **`json`**: Machine-readable JSON output for integrations and pipelines

---

## How to Use

### Quick Start

```bash
# Health scoring
python scripts/health_score_calculator.py assets/sample_customer_data.json
python scripts/health_score_calculator.py assets/sample_customer_data.json --format json

# Churn risk analysis
python scripts/churn_risk_analyzer.py assets/sample_customer_data.json
python scripts/churn_risk_analyzer.py assets/sample_customer_data.json --format json

# Expansion opportunity scoring
python scripts/expansion_opportunity_scorer.py assets/sample_customer_data.json
python scripts/expansion_opportunity_scorer.py assets/sample_customer_data.json --format json
```

### Workflow Integration

```bash
# 1. Score customer health across portfolio
python scripts/health_score_calculator.py customer_portfolio.json --format json > health_results.json

# 2. Identify at-risk accounts
python scripts/churn_risk_analyzer.py customer_portfolio.json --format json > risk_results.json

# 3. Find expansion opportunities in healthy accounts
python scripts/expansion_opportunity_scorer.py customer_portfolio.json --format json > expansion_results.json

# 4. Prepare QBR using templates
# Reference: assets/qbr_template.md
```

---

## Scripts

### 1. health_score_calculator.py

**Purpose:** Multi-dimensional customer health scoring with trend analysis and segment-aware benchmarking.

**Dimensions and Weights:**
| Dimension | Weight | Metrics |
|-----------|--------|---------|
| Usage | 30% | Login frequency, feature adoption, DAU/MAU ratio |
| Engagement | 25% | Support ticket volume, meeting attendance, NPS/CSAT |
| Support | 20% | Open tickets, escalation rate, avg resolution time |
| Relationship | 25% | Executive sponsor engagement, multi-threading depth, renewal sentiment |

**Classification:**
- Green (75-100): Healthy -- customer achieving value
- Yellow (50-74): Needs attention -- monitor closely
- Red (0-49): At risk -- immediate intervention required

**Usage:**
```bash
python scripts/health_score_calculator.py customer_data.json
python scripts/health_score_calculator.py customer_data.json --format json
```

### 2. churn_risk_analyzer.py

**Purpose:** Identify at-risk accounts with behavioral signal detection and tier-based intervention recommendations.

**Risk Signal Weights:**
| Signal Category | Weight | Indicators |
|----------------|--------|------------|
| Usage Decline | 30% | Login trend, feature adoption change, DAU/MAU change |
| Engagement Drop | 25% | Meeting cancellations, response time, NPS change |
| Support Issues | 20% | Open escalations, unresolved critical, satisfaction trend |
| Relationship Signals | 15% | Champion left, sponsor change, competitor mentions |
| Commercial Factors | 10% | Contract type, pricing complaints, budget cuts |

**Risk Tiers:**
- Critical (80-100): Immediate executive escalation
- High (60-79): Urgent CSM intervention
- Medium (40-59): Proactive outreach
- Low (0-39): Standard monitoring

**Usage:**
```bash
python scripts/churn_risk_analyzer.py customer_data.json
python scripts/churn_risk_analyzer.py customer_data.json --format json
```

### 3. expansion_opportunity_scorer.py

**Purpose:** Identify upsell, cross-sell, and expansion opportunities with revenue estimation and priority ranking.

**Expansion Types:**
- **Upsell**: Upgrade to higher tier or more of existing product
- **Cross-sell**: Add new product modules
- **Expansion**: Additional seats or departments

**Usage:**
```bash
python scripts/expansion_opportunity_scorer.py customer_data.json
python scripts/expansion_opportunity_scorer.py customer_data.json --format json
```

---

## Reference Guides

| Reference | Description |
|-----------|-------------|
| `references/health-scoring-framework.md` | Complete health scoring methodology, dimension definitions, weighting rationale, threshold calibration |
| `references/cs-playbooks.md` | Intervention playbooks for each risk tier, onboarding, renewal, expansion, and escalation procedures |
| `references/cs-metrics-benchmarks.md` | Industry benchmarks for NRR, GRR, churn rates, health scores, expansion rates by segment and industry |

---

## Templates

| Template | Purpose |
|----------|---------|
| `assets/qbr_template.md` | Quarterly Business Review presentation structure |
| `assets/success_plan_template.md` | Customer success plan with goals, milestones, and metrics |
| `assets/onboarding_checklist_template.md` | 90-day onboarding checklist with phase gates |
| `assets/executive_business_review_template.md` | Executive stakeholder review for strategic accounts |

---

## Best Practices

1. **Score regularly**: Run health scoring weekly for Enterprise, bi-weekly for Mid-Market, monthly for SMB
2. **Act on trends, not snapshots**: A declining Green is more urgent than a stable Yellow
3. **Combine signals**: Use all three scripts together for a complete customer picture
4. **Calibrate thresholds**: Adjust segment benchmarks based on your product and industry
5. **Document interventions**: Track what actions you took and outcomes for playbook refinement
6. **Prepare with data**: Run scripts before every QBR and executive meeting

---

## Limitations

- **No real-time data**: Scripts analyze point-in-time snapshots from JSON input files
- **No CRM integration**: Data must be exported manually from your CRM/CS platform
- **Deterministic only**: No predictive ML -- scoring is algorithmic based on weighted signals
- **Threshold tuning**: Default thresholds are industry-standard but may need calibration for your business
- **Revenue estimates**: Expansion revenue estimates are approximations based on usage patterns

---

---

## Tool Reference

### 1. health_score_calculator.py

**Purpose:** Multi-dimensional customer health scoring with trend analysis and segment-aware benchmarking.

```bash
python scripts/health_score_calculator.py customer_data.json
python scripts/health_score_calculator.py customer_data.json --format json
```

| Flag | Required | Description |
|------|----------|-------------|
| `customer_data.json` | Yes | JSON file with customer health data (usage, engagement, support, relationship metrics) |
| `--format` | No | Output format: text (default) or json |

**Dimensions and Weights:** Usage (30%), Engagement (25%), Support (20%), Relationship (25%)

**Classification:** Green (75-100), Yellow (50-74), Red (0-49) -- thresholds adjust by segment (Enterprise, Mid-Market, SMB)

### 2. churn_risk_analyzer.py

**Purpose:** Identify at-risk accounts with behavioral signal detection and tier-based intervention recommendations.

```bash
python scripts/churn_risk_analyzer.py customer_data.json
python scripts/churn_risk_analyzer.py customer_data.json --format json
```

| Flag | Required | Description |
|------|----------|-------------|
| `customer_data.json` | Yes | JSON file with churn risk signals (usage decline, engagement drop, support issues, relationship signals, commercial factors) |
| `--format` | No | Output format: text (default) or json |

**Risk Tiers:** Critical (80-100), High (60-79), Medium (40-59), Low (0-39)

**Signal Weights:** Usage Decline (30%), Engagement Drop (25%), Support Issues (20%), Relationship Signals (15%), Commercial Factors (10%)

### 3. expansion_opportunity_scorer.py

**Purpose:** Identify upsell, cross-sell, and expansion opportunities with revenue estimation and priority ranking.

```bash
python scripts/expansion_opportunity_scorer.py customer_data.json
python scripts/expansion_opportunity_scorer.py customer_data.json --format json
```

| Flag | Required | Description |
|------|----------|-------------|
| `customer_data.json` | Yes | JSON file with customer contract, product usage, and department data |
| `--format` | No | Output format: text (default) or json |

**Expansion Types:** Upsell (tier upgrade), Cross-sell (new modules), Expansion (seats/departments)

---

## Troubleshooting

| Problem | Likely Cause | Solution |
|---------|-------------|----------|
| Health scores do not correlate with actual churn | Default thresholds do not match your product | Calibrate segment thresholds using historical churn data; compare 90-day retained vs churned cohorts |
| All accounts show as Yellow | Thresholds too strict or data quality issues | Review input data completeness; adjust benchmarks in health_score_calculator.py constants for your industry |
| Churn risk scores are uniformly low | Missing key signals (champion left, competitor mentions) | Ensure all signal categories have data; missing data defaults to low risk, which understates actual risk |
| Expansion scores do not reflect reality | Product usage data is incomplete or stale | Verify product_usage fields cover all modules; run with fresh data exports from your product analytics |
| Scripts error on input data | JSON format does not match expected schema | Reference the Input Requirements section for exact JSON structure; validate JSON before running |
| Trend analysis shows no change | Previous period data not provided | Include the previous_period block in health score input for meaningful trend comparison |
| Intervention recommendations feel generic | Segment is not specified | Always include the segment field (enterprise, mid-market, smb) for segment-appropriate playbooks |

---

## Success Criteria

- Health scores run weekly for Enterprise, bi-weekly for Mid-Market, monthly for SMB accounts
- Portfolio health distribution: 60%+ Green, less than 15% Red
- Churn risk critical accounts have executive escalation within 48 hours
- Expansion pipeline generated covers 20%+ of net retention target
- Health score trends (improving/declining) drive proactive outreach before renewal window
- QBR preparation includes health score, risk assessment, and expansion opportunities for every strategic account
- Intervention playbooks followed for all High and Critical risk accounts

---

## Scope & Limitations

- **In scope:** Customer health scoring, churn risk analysis, expansion opportunity identification, segment benchmarking, trend analysis, QBR preparation
- **Out of scope:** CRM integration, real-time monitoring, predictive ML modeling, automated outreach
- **Data dependency:** Scripts analyze point-in-time JSON snapshots; data must be exported manually from your CRM/CS platform
- **Deterministic scoring:** All analysis is algorithmic based on weighted signals -- no machine learning predictions
- **Threshold tuning:** Default thresholds are industry-standard benchmarks; calibrate for your specific product and customer base
- **Revenue estimates:** Expansion revenue estimates are approximations based on usage patterns, not binding forecasts

---

## Integration Points

- **churn-prevention** -- High-risk accounts from churn_risk_analyzer.py should trigger cancel flow optimization and save offer review
- **revenue-operations** -- Expansion opportunities feed into pipeline forecasting; health scores inform forecast confidence
- **onboarding-cro** -- When health scores show low usage in early lifecycle, the root cause is often poor activation
- **pricing-strategy** -- When expansion analysis reveals pricing as a barrier to upsell, feed into pricing-strategy for packaging review
- **competitive-teardown** -- When churn risk signals include competitor mentions, use teardown data to build counter-positioning

---

**Last Updated:** March 2026
**Tools:** 3 Python CLI tools
**Dependencies:** Python 3.7+ standard library only
