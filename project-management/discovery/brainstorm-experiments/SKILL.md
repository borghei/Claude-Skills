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

## Troubleshooting

| Symptom | Likely Cause | Resolution |
|---------|-------------|------------|
| Tool suggests only low-SITG experiments | Hypothesis text lacks action-oriented keywords (pay, purchase, upgrade) | Rewrite hypothesis using explicit behavioral verbs; check KEYWORD_SIGNALS mapping in script |
| All experiments recommended are the same method | Hypothesis signals are too narrow or product_type is wrong | Verify `product_type` is set correctly (new vs. existing); broaden hypothesis to cover more intent signals |
| Demo mode works but custom input fails | Input JSON schema does not match expected format (missing `hypotheses` key) | Validate JSON has top-level `hypotheses` array with `hypothesis_text`, `target_segment`, `product_type` per entry |
| Experiment results are always inconclusive | Sample size too small or experiment duration too short for the metric | Extend timebox, increase traffic allocation, or choose a metric with higher signal-to-noise ratio |
| Fake door test shows high clicks but feature never builds | No decision framework tied to experiment outcome | Define clear pass/fail thresholds before running; document the "if pass, then build" commitment upfront |
| Team runs experiments but never acts on results | Results not connected to roadmap or prioritization process | Feed experiment outcomes into `identify-assumptions/` for re-scoring; link to `execution/outcome-roadmap/` |

## Success Criteria

- Every product hypothesis has a falsifiable XYZ statement before experiment design begins
- Experiments measure Skin-in-the-Game (SITG) signals, not stated preferences
- Pass/fail thresholds are defined before the experiment runs, not after
- Experiment duration does not exceed 4 weeks for any single hypothesis
- At least 70% of experiments produce a clear pass or fail verdict (not inconclusive)
- Results directly feed the build/pivot/abandon decision within 1 week of experiment completion
- Your Own Data (YODA) principle is followed -- no reliance on industry benchmarks for go/no-go decisions

## Scope & Limitations

**In Scope:**
- XYZ hypothesis formulation and validation for product ideas
- Experiment method selection for both new products (landing page, pre-order, concierge, explainer video) and existing products (fake door, feature stub, A/B test, Wizard of Oz, in-app survey)
- Automated experiment design suggestions based on hypothesis keyword analysis
- Metric selection, success threshold definition, and effort/duration estimation

**Out of Scope:**
- Statistical power analysis or sample size calculation (use dedicated A/B test platforms)
- Experiment infrastructure setup (feature flags, analytics instrumentation)
- Running the actual experiment (this skill designs experiments, not executes them)
- Long-term product strategy or roadmap decisions (see `execution/outcome-roadmap/`)

**Important Caveats:**
- Pretotyping is for validating demand and value, not for measuring usability or performance.
- In-app surveys are the weakest SITG signal. Use them only when behavioral experiments are impractical.
- The tool's keyword-to-signal matching is heuristic-based. Review suggested experiments and override when domain knowledge dictates a better method.

## Integration Points

| Integration | Direction | Description |
|------------|-----------|-------------|
| `brainstorm-ideas/` | Receives from | Ideas generated become hypotheses for experiment design |
| `identify-assumptions/` | Receives from | "Test Now" assumptions become hypotheses for this skill |
| `pre-mortem/` | Feeds into | Experiment results inform pre-mortem risk assessment before full build |
| `execution/create-prd/` | Feeds into | Validated hypotheses become PRD assumptions with evidence |
| `execution/brainstorm-okrs/` | Feeds into | Experiment metrics may become OKR key results |
| `execution/outcome-roadmap/` | Feeds into | Experiment outcomes inform Now/Next/Later roadmap placement |

## Tool Reference

### experiment_designer.py

Suggests 2-3 experiment designs for each product hypothesis based on keyword signal analysis.

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `input_file` | positional | (optional) | Path to JSON file with hypotheses array |
| `--demo` | flag | off | Run with built-in sample data (3 hypotheses) |
| `--format` | choice | `text` | Output format: `text` or `json` |

## References

- Alberto Savoia, *The Right It* (2019)
- Eric Ries, *The Lean Startup* (2011)
- Jeff Gothelf & Josh Seiden, *Lean UX* (2013)
- Teresa Torres, *Continuous Discovery Habits* (2021)
