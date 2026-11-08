---
name: brainstorm-experiments
description: >
  Designs cheap experiments with a pre-set pass bar (at least X% of Y will do Z) and
  picks the method. Use when validating an idea before building, testing willingness to
  pay, or choosing between fake door, landing page and A/B test.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: product-discovery
  updated: 2026-11-08
  python-tools: experiment_designer.py
  tech-stack: pretotyping, lean-validation, ab-testing, xyz-hypothesis
  tags:
    - experiments
    - pretotyping
    - lean-validation
    - discovery
---
# Experiment Design Expert

## Overview

Design fast, low-cost experiments to validate product hypotheses before committing to full development. This skill applies Alberto Savoia's pretotyping philosophy ("Make sure you are building The Right It before you build It right") alongside lean experimentation methods for both new and existing products.

## Core Capabilities

- **XYZ hypotheses** — frame every test as "At least X% of Y will do Z" with a pre-set pass/fail threshold.
- **SITG + YODA discipline** — prefer skin-in-the-game signals (money, time, reputation) and Your Own Data over surveys and benchmarks.
- **Method selection** — landing page, explainer video, pre-order, concierge MVP (new products); fake door, feature stub, A/B test, Wizard of Oz, in-app survey (existing).
- **5-step process** — hypothesis, method, metric/threshold, timeboxed run, evaluate (pass/fail/inconclusive).
- **Automated design** — `experiment_designer.py` suggests 2-3 experiments per hypothesis with metric, threshold, effort, and duration.

## When to Use

- You have a product idea or feature hypothesis and need to validate it cheaply.
- You want to test willingness to pay or genuine user interest, not just stated preference.
- You need to choose the right experiment method for your context (new vs. existing product).

## Clarify First

Before designing the experiment, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Hypothesis to test:** the specific belief stated as "At least X% of Y will do Z" (drives `hypothesis_text` and the pass/fail threshold).
- **Product type:** new vs existing (selects the method catalog: landing page / pre-order / concierge vs fake door / feature stub / A-B test).
- **Target segment:** who "Y" is in the hypothesis (drives the metric and who you expose the test to).
- **Available SITG signal:** what skin-in-the-game you can capture (money, time, reputation) given budget/tooling (narrows realistic methods).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Workflow

1. Write each belief as "At least X% of Y will do Z within T" and settle the Clarify First inputs.
2. Run `experiment_designer.py` for method suggestions; pick the cheapest method that captures a skin-in-the-game signal.
3. Record method, X% pass bar, minimum sample, counter-metric and timebox in `assets/experiment_plan_template.md` before launch.
4. Done when the result is called pass, fail or inconclusive against the bar written before launch, with the counter-metric checked.

```bash
python3 project-management/discovery/brainstorm-experiments/scripts/experiment_designer.py project-management/discovery/brainstorm-experiments/assets/sample_hypotheses.json         # exit 0
python3 project-management/discovery/brainstorm-experiments/scripts/experiment_designer.py project-management/discovery/brainstorm-experiments/assets/sample_hypotheses_flawed.json  # exit 1: no X%
python3 project-management/discovery/brainstorm-experiments/scripts/experiment_designer.py --demo --format json
```

Each hypothesis needs `hypothesis_text`, `target_segment`, and `product_type` (`new`/`existing`). The tool suggests up to 3 methods by keyword match (treat them as suggestions, not a ranking you must follow) and sets each method's pass bar to the hypothesis's own X%, showing the method's typical range only as context. Exit codes: 0 every hypothesis has an X% bar, 1 at least one has none, 2 bad input (missing file, invalid JSON, no hypotheses).

## Prototype-First Experiments

An AI-built prototype is one more method with the same XYZ bar. Use it when the riskiest assumption is usability of a specific interaction, not demand (a fake door or landing page is cheaper for that). Test with 5-8 target users on scripted tasks and synthetic data. Fidelity levels, kill criteria and the handoff are in `discovery/ai-prototyping`.

## Anti-Patterns

### Sample too small to mean anything
**Mistake:** Eight users see the test, five click, and the team reports "62.5% conversion" and moves on.
**Why it happens:** Small tests are quick, and an early good number is tempting to believe.
**Instead:** Write down the minimum sample size next to the XYZ threshold before the test starts. Don't stop early because the result looks good. The sample-size rules of thumb are in `references/experiment-methods.md`.

### Pretotype that takes weeks
**Mistake:** The "quick smoke test" takes six weeks and three engineers, and the team is committed before data comes back.
**Why it happens:** The team keeps polishing the test so it feels fair to the idea.
**Instead:** Keep the time from idea to live experiment under one week. If it will take longer, pick a cheaper method from the catalog, such as a fake door, landing page or concierge MVP.

### No counter-metric
**Mistake:** The test measures clicks on "Upgrade" and ignores whether those users paid, stayed or were happy.
**Why it happens:** The primary metric is the one tied to the hypothesis, so it gets all the attention.
**Instead:** Declare at least one counter-metric before launch and record it in `assets/experiment_plan_template.md`. Count a pass only if the primary metric clears its threshold and the counter-metric holds.

Nine more, each with a bad and a good example: `references/red-flags.md`.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/methodology-and-tools.md](references/methodology-and-tools.md)** — the XYZ/SITG/YODA principles, the experiment-type catalog for new and existing products, the 5-step process, `experiment_designer.py` usage and flags, output template, troubleshooting, success criteria, and bibliography. Read when designing or scripting an experiment.
- **[references/experiment-methods.md](references/experiment-methods.md)** — Savoia's pretotyping manifesto and pretotype types, the full lean-experiment catalog (discovery and validation), metric selection guide, threshold-setting framework, sample-size rules of thumb, and 8 common pitfalls. Read for the deep method reference.
- **[references/red-flags.md](references/red-flags.md)** — anti-patterns (confirmation-biased design, no pre-set threshold, vanity metrics, peeking) with bad/good experiment specs. Read before running an experiment.

## Scope & Limitations

**In Scope:** XYZ hypothesis formulation and validation; experiment method selection for new products (landing page, pre-order, concierge, explainer video) and existing products (fake door, feature stub, A/B test, Wizard of Oz, in-app survey); automated experiment design from hypothesis keyword analysis; metric selection, success threshold definition, and effort/duration estimation.

**Out of Scope:** statistical power analysis or sample size calculation (use dedicated A/B test platforms); experiment infrastructure setup (feature flags, analytics instrumentation); running the actual experiment (this skill designs, not executes); long-term product strategy or roadmap decisions (`execution/outcome-roadmap/`).

**Important Caveats:** pretotyping validates demand and value, not usability or performance; in-app surveys are the weakest SITG signal — use only when behavioral experiments are impractical; the tool's keyword-to-signal matching is heuristic — override when domain knowledge dictates a better method.

## Files

| File | Purpose |
|------|---------|
| `scripts/experiment_designer.py` | Method suggestions with metric, pass bar, effort, duration and SITG level per hypothesis |
| `assets/sample_hypotheses.json`, `assets/sample_hypotheses_flawed.json` | Runnable inputs: sound (exit 0) and missing pass bar (exit 1) |
| `assets/experiment_plan_template.md` | Experiment plan to fill in before launch |
| `examples/ai-summarization-willingness-to-pay-experiment.md` | Worked example |
| `references/*.md` | See References |
