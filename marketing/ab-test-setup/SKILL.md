---
name: ab-test-setup
description: >
  This skill should be used when the user asks to "set up an A/B test", "calculate sample size",
  "design an experiment", "analyze A/B test results", "check statistical significance",
  "determine test duration", or "evaluate conversion rate experiments".
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: marketing
  domain: experimentation
  updated: 2026-04-02
  tags: [ab-testing, experimentation, statistics, sample-size, conversion-rate]
---
# A/B Test Setup Skill

## Overview

Production-ready A/B testing toolkit for calculating sample sizes, designing rigorous test plans, and analyzing results with statistical significance testing. Designed for growth teams, product managers, and marketers who need to make data-driven decisions from controlled experiments.

## Quick Start

```bash
# Calculate required sample sizes for a test
python scripts/sample_size_calculator.py --baseline 0.05 --mde 0.10 --power 0.80

# Design a complete A/B test plan
python scripts/test_designer.py test_config.json

# Analyze A/B test results
python scripts/results_analyzer.py results.json
```

## Tools Overview

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| `sample_size_calculator.py` | Sample size calculation | Baseline rate, MDE, power | Required samples + duration |
| `test_designer.py` | Test plan design | JSON test config | Complete test plan document |
| `results_analyzer.py` | Results analysis | JSON with test results | Statistical analysis + recommendation |

## Workflows

### Workflow 1: New A/B Test Setup

1. Define hypothesis and success metric
2. Run `sample_size_calculator.py` with baseline conversion and minimum detectable effect
3. Create test configuration JSON (see Common Patterns)
4. Run `test_designer.py` to generate complete test plan
5. Share plan with stakeholders for alignment before launch

### Workflow 2: Test Results Analysis

1. Collect test results into JSON format
2. Run `results_analyzer.py` to get statistical significance
3. Review confidence interval, p-value, and effect size
4. Check for segment-level effects if overall result is inconclusive
5. Make ship/no-ship decision based on analysis

### Workflow 3: Experimentation Program Review

1. Compile results from multiple past tests
2. Run `results_analyzer.py --batch` on all results
3. Review win rate, average effect size, and velocity
4. Identify patterns in winning vs losing tests
5. Optimize test pipeline based on learnings

## Reference Documentation

See `references/ab-testing-guide.md` for comprehensive methodology covering:
- Statistical foundations (z-tests, confidence intervals)
- Sample size theory and trade-offs
- Common experimentation pitfalls
- Multi-variant and sequential testing
- Bayesian vs frequentist approaches

## Common Patterns

### Pattern: Test Configuration JSON
```json
{
  "test_name": "Homepage CTA Button Color",
  "hypothesis": "Changing the CTA button from blue to green will increase click-through rate",
  "metric_primary": "cta_click_rate",
  "metric_secondary": ["signup_rate", "bounce_rate"],
  "baseline_rate": 0.045,
  "minimum_detectable_effect": 0.10,
  "significance_level": 0.05,
  "power": 0.80,
  "variants": [
    {"name": "control", "description": "Current blue CTA button"},
    {"name": "treatment", "description": "Green CTA button"}
  ],
  "daily_traffic": 5000,
  "allocation": {"control": 0.50, "treatment": 0.50}
}
```

### Pattern: Test Results JSON
```json
{
  "test_name": "Homepage CTA Button Color",
  "variants": {
    "control": {"visitors": 12500, "conversions": 563},
    "treatment": {"visitors": 12500, "conversions": 625}
  },
  "metric": "cta_click_rate",
  "significance_level": 0.05
}
```

### Quick Reference: Common Effect Sizes

| Context | Small Effect | Medium Effect | Large Effect |
|---------|-------------|---------------|--------------|
| Conversion Rate | 2-5% relative | 5-15% relative | > 15% relative |
| Revenue per User | 1-3% | 3-8% | > 8% |
| Engagement Rate | 3-5% | 5-10% | > 10% |
