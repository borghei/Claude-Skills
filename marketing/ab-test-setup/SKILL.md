---
name: ab-test-setup
description: >
  Design and analyze A/B tests: sample size, test duration, and statistical
  significance for conversion experiments. Use when setting up an A/B test,
  calculating sample size, designing an experiment, or analyzing results.
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

## Clarify First

Before designing the test, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Hypothesis + primary metric:** what change you expect and the single metric that judges it (drives test plan + analysis).
- **Baseline conversion rate:** the current rate the metric sits at today (drives sample size calculation).
- **Minimum detectable effect (MDE):** smallest lift worth detecting (drives required samples + duration).
- **Daily traffic available:** eligible visitors per day per variant (determines how long the test must run).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

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

## Scope & Limitations

**In Scope:**
- Sample size and duration estimates for conversion-rate tests with `sample_size_calculator.py`, using the two-proportion z-test formula with configurable alpha, power, one- or two-sided testing, allocation and variant count
- Test plan generation from a JSON config (hypothesis, primary and secondary metrics, variants, traffic split) with `test_designer.py`
- Results analysis with `results_analyzer.py`: two-proportion z-test, p-value, confidence interval and Cohen's h effect size, with optional Bayesian analysis and batch mode for reviewing several tests
- A methodology guide covering statistical foundations, common pitfalls such as peeking and multiple comparisons, and sequential and Bayesian approaches

**Out of Scope:**
- Running the experiment, assigning traffic or serving variants; the skill does not connect to any testing platform
- Event tracking and instrumentation that produces the visitor and conversion counts (see `marketing/analytics-tracking/`)
- Continuous metrics such as revenue per user, regression and other statistical methods beyond proportion tests (see `data-analytics/statistical-analyst/`)
- Deciding what to test on a page or form (see `business-growth/page-cro/` and `business-growth/form-cro/`)

**Important Caveats:**
- The tools model binary conversion metrics only. Visitor and conversion counts are entered by hand in JSON.
- `results_analyzer.py` compares two variants (control and treatment). For A/B/n tests it does not compare every arm, and `sample_size_calculator.py` does not adjust alpha for multiple variants.
- The tools do not check for sample ratio mismatch, segment effects, novelty effects or peeking. The reference guide explains these, but you have to check for them yourself.
- The effect-size table is a rough guide. Your own baseline and MDE should drive the plan.
