---
name: business-investment-advisor
description: >
  This skill should be used when the user asks to "screen investments", "analyze a portfolio",
  "evaluate investment opportunities", "run due diligence", "assess investment risk",
  "calculate ROI", or "diversify portfolio holdings".
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: finance
  domain: investment
  updated: 2026-04-02
  tags: [investment, portfolio, due-diligence, roi, risk-analysis, diversification]
---
# Business Investment Advisor Skill

## Overview

Production-ready investment analysis toolkit for screening opportunities, analyzing portfolio composition, and generating due diligence checklists. Designed for business owners, angel investors, and corporate development teams evaluating investments from $50K to $50M.

## Quick Start

```bash
# Screen investments by criteria (ROI, risk, payback)
python scripts/investment_screener.py opportunities.json --min-roi 15 --max-payback 36

# Analyze portfolio diversification and risk exposure
python scripts/portfolio_analyzer.py portfolio.json

# Generate due diligence checklist for an investment target
python scripts/due_diligence_checklist.py --type saas --stage series-a --amount 500000
```

## Tools Overview

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| `investment_screener.py` | Filter & rank investments | JSON with opportunity data | Ranked opportunities + scores |
| `portfolio_analyzer.py` | Portfolio risk & diversification | JSON with holdings | Risk report + recommendations |
| `due_diligence_checklist.py` | DD checklist generation | Investment parameters | Structured checklist + scoring |

## Workflows

### Workflow 1: Opportunity Evaluation Pipeline

1. Compile investment opportunities into JSON format (see Common Patterns)
2. Run `investment_screener.py` with your criteria filters
3. Review ranked results focusing on composite score
4. For top candidates, run `due_diligence_checklist.py` to generate investigation plan
5. After DD completion, update portfolio model and run `portfolio_analyzer.py`

### Workflow 2: Portfolio Health Check

1. Export current holdings to JSON format
2. Run `portfolio_analyzer.py` to assess diversification
3. Review concentration risk, sector exposure, and liquidity analysis
4. Use recommendations to identify rebalancing opportunities
5. Screen new opportunities with `investment_screener.py` to fill gaps

### Workflow 3: Due Diligence Sprint

1. Run `due_diligence_checklist.py` with target parameters
2. Assign checklist items to team members with deadlines
3. Score each item as investigation progresses (0-10)
4. Re-run with `--score-file` to get weighted DD score
5. Use composite score to support go/no-go decision

## Reference Documentation

See `references/investment-frameworks.md` for detailed frameworks including:
- Investment scoring methodology
- Risk assessment matrix
- Portfolio diversification guidelines
- Due diligence phase frameworks
- Industry-specific evaluation criteria

## Common Patterns

### Pattern: Investment Opportunities JSON
```json
{
  "opportunities": [
    {
      "name": "TechCo SaaS",
      "type": "equity",
      "sector": "technology",
      "stage": "series-a",
      "amount": 250000,
      "expected_roi_pct": 25.0,
      "risk_level": "high",
      "payback_months": 36,
      "revenue": 1200000,
      "revenue_growth_pct": 85.0,
      "gross_margin_pct": 78.0,
      "burn_rate_monthly": 80000,
      "runway_months": 18
    }
  ]
}
```

### Pattern: Portfolio Holdings JSON
```json
{
  "portfolio": {
    "total_invested": 2000000,
    "holdings": [
      {
        "name": "Investment A",
        "type": "equity",
        "sector": "technology",
        "invested": 250000,
        "current_value": 375000,
        "date_invested": "2024-06-15",
        "stage": "series-a",
        "liquidity": "illiquid",
        "status": "active"
      }
    ]
  }
}
```

### Risk Level Definitions

| Level | Expected Return | Loss Probability | Typical Payback |
|-------|----------------|-----------------|-----------------|
| Low | 5-10% | < 10% | < 24 months |
| Medium | 10-20% | 10-30% | 24-48 months |
| High | 20-40% | 30-50% | 36-60 months |
| Very High | 40%+ | > 50% | 48+ months |
