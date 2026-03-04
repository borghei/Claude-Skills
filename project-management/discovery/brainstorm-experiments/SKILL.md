---
name: brainstorm-experiments
description: Experiment design expert using pretotyping and lean validation for both new product concepts and existing product features.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: project-management
  domain: product-discovery
  updated: 2026-03-04
  python-tools: experiment_designer.py
  tech-stack: pretotyping, lean-validation, ab-testing, xyz-hypothesis
---

# Experiment Design Expert

## Overview

Design fast, low-cost experiments to validate product hypotheses before committing to full development. This skill applies Alberto Savoia's pretotyping philosophy ("Make sure you are building The Right It before you build It right") alongside lean experimentation methods for both new and existing products.

### When to Use

- You have a product idea or feature hypothesis and need to validate it cheaply.
- You want to test willingness to pay or genuine user interest, not just stated preference.
- You need to choose the right experiment method for your context (new vs. existing product).

## Core Principles

### 1. XYZ Hypothesis Format

Every experiment starts with a falsifiable hypothesis:

**"At least X% of Y will do Z."**

| Component | Description | Example |
|-----------|-------------|---------|
| **X%** | The success threshold | 15% |
| **Y** | The target population | trial users who reach the dashboard |
| **Z** | The specific measurable action | click "Upgrade to Pro" within 7 days |

A good XYZ hypothesis is specific, measurable, and has a clear pass/fail threshold set before the experiment runs.

### 2. Skin-in-the-Game (SITG)

Stated interest is unreliable. Valid experiments measure actions that require commitment:
- **Money** -- Pre-orders, deposits, paid waitlists.
- **Time** -- Signing up, completing a multi-step flow, scheduling a demo.
- **Reputation** -- Sharing with colleagues, posting publicly.

Always prefer SITG signals over surveys, likes, or verbal feedback.

### 3. Your Own Data (YODA)

Do not rely on market reports, competitor benchmarks, or industry averages. Run your own experiment with your own audience to get Your Own Data. Others' data reflects their context, not yours.

## Experiment Types

### For New Products

| Method | Description | Best For | Effort | Duration |
|--------|-------------|----------|--------|----------|
| **Landing Page** | Single-page site describing the product with a CTA (sign up, pre-order) | Testing value proposition and demand | Low | 1-2 weeks |
| **Explainer Video** | Short video demonstrating the concept with a CTA | Testing comprehension and interest | Low-Medium | 1-2 weeks |
| **Pre-Order / Waitlist** | Accept payment or email for a product that does not exist yet | Testing willingness to pay | Low | 2-4 weeks |
| **Concierge MVP** | Deliver the service manually to a small group, as if automated | Testing whether the solution actually solves the problem | Medium | 2-4 weeks |

### For Existing Products

| Method | Description | Best For | Effort | Duration |
|--------|-------------|----------|--------|----------|
| **Fake Door Test** | Add a button/link for a feature that does not exist; measure clicks | Testing demand for a specific feature | Low | 1-2 weeks |
| **Feature Stub** | Build minimal version (e.g., static mockup) behind a flag | Testing engagement with a feature concept | Low-Medium | 1-2 weeks |
| **A/B Test** | Show variant to a percentage of users; measure conversion | Testing incremental changes to existing flows | Medium | 2-4 weeks |
| **Wizard of Oz** | Feature appears automated to user but is manually operated behind the scenes | Testing complex features before building automation | Medium-High | 2-4 weeks |
| **Survey (In-App)** | Targeted survey shown to users who match specific behavioral criteria | Testing preferences when SITG methods are impractical | Low | 1 week |

## Methodology

### Step 1: Write the XYZ Hypothesis

Start with the assumption you need to test. Convert it into XYZ format.

**Weak:** "Users will like the new dashboard."
**Strong:** "At least 30% of active users who see the new dashboard will set it as their default view within 5 days."

### Step 2: Select the Experiment Method

Choose based on:
- **Product type** (new vs. existing)
- **What you are testing** (demand, usability, willingness to pay, engagement)
- **Available effort** (team capacity and timeline)
- **Required confidence** (directional signal vs. statistically significant result)

### Step 3: Define the Metric and Threshold

| Element | Description |
|---------|-------------|
| **Primary metric** | The single number that determines pass/fail |
| **Success threshold** | The minimum value to consider the hypothesis validated |
| **Secondary metrics** | Additional signals to watch (but not used for pass/fail) |
| **Guardrail metrics** | Metrics that must NOT degrade (e.g., existing conversion rate) |

### Step 4: Run the Experiment

- **Set a timebox.** Every experiment has a fixed end date.
- **Do not peek.** Avoid checking results daily and making early calls.
- **Document everything.** Record setup, audience, duration, and any anomalies.

### Step 5: Evaluate Results

| Outcome | Meaning | Next Action |
|---------|---------|-------------|
| **Clear pass** | Metric exceeds threshold | Proceed to build or next validation stage |
| **Clear fail** | Metric well below threshold | Pivot, modify hypothesis, or abandon |
| **Inconclusive** | Metric near threshold or insufficient sample | Extend duration, increase sample, or refine experiment |

## Python Tool: experiment_designer.py

Design experiments from hypotheses using the CLI tool:

```bash
# Run with demo data
python3 scripts/experiment_designer.py --demo

# Run with custom input
python3 scripts/experiment_designer.py input.json

# Output as JSON
python3 scripts/experiment_designer.py input.json --format json
```

### Input Format

```json
{
  "hypotheses": [
    {
      "hypothesis_text": "At least 20% of trial users will click Upgrade within 7 days",
      "target_segment": "trial users on free plan",
      "product_type": "existing"
    }
  ]
}
```

### Output

For each hypothesis, the tool suggests 2-3 experiment designs with method, metric, success threshold, effort level, and duration estimate.

See `scripts/experiment_designer.py` for full documentation.

## Output Template

Use `assets/experiment_plan_template.md` to document each experiment:

- Experiment card with hypothesis, method, metric, threshold, owner, timeline
- Experiment tracker for managing multiple concurrent experiments
- Results documentation for recording outcomes and decisions

## Integration with Other Discovery Skills

- Use `brainstorm-ideas/` to generate ideas that become hypotheses.
- Use `identify-assumptions/` to find the riskiest assumptions to test.
- After experiments, use `pre-mortem/` before committing to full build.

## References

- Alberto Savoia, *The Right It* (2019)
- Eric Ries, *The Lean Startup* (2011)
- Jeff Gothelf & Josh Seiden, *Lean UX* (2013)
- Teresa Torres, *Continuous Discovery Habits* (2021)
