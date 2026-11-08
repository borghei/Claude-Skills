---
name: north-star-metric
description: >
  Pick the one metric that tracks customer value, decompose it into inputs
  with leading indicators and guardrail metrics. Use when defining the metric
  a team optimises before writing OKRs, or when a dashboard has no headline.
license: MIT + Commons Clause
metadata:
  version: 1.0.2
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-11-08
  python-tools: metric_tree_builder.py
  tech-stack: north-star, input-metrics, leading-indicators, counter-metrics, omtm
  tags:
    - north-star-metric
    - metric-tree
    - leading-indicators
    - counter-metrics
---
# North Star Metric (NSM) Expert

## Overview

A North Star Metric (NSM) is the single number that best represents the value your product delivers to its customers. Sean Ellis popularized the framing; Amplitude codified the playbook; Lean Analytics calls a related concept the "One Metric That Matters" (OMTM). The NSM is **one** number, not a dashboard. Its job is to align the entire team -- engineering, marketing, sales, support -- on a shared definition of "we won this quarter."

This skill produces a complete NSM specification: the NSM itself, 3-5 **input metrics** the team can directly influence, the **leading indicators** that move days or weeks before the inputs, the **anti-metrics** (things that must NOT move in the wrong direction), and **counter-metrics** that guard against gaming. The Python tool (`metric_tree_builder.py`) emits the spec as JSON, Markdown, or a Mermaid tree diagram for a README or Confluence page.

This is the first artifact a team should produce after defining strategy and before writing OKRs. Once the NSM is set, OKRs map directly to moving the input metrics, and roadmaps justify themselves by which input metric they target.

## Core Capabilities

- **NSM selection** — score candidates against the five tests (customer value, strategic alignment, leading, single number, movable) and the five Amplitude archetypes.
- **Metric-tree decomposition** — break the NSM into 3-5 input metrics with an explicit formula (multiplicative / additive / funnel / ratio).
- **Leading indicators** — assign 2-3 per input that move before the input does (the daily/weekly dashboard).
- **Guardrails** — anti-metrics (protect the customer) and counter-metrics (protect the business), each with explicit thresholds.
- **Rendering** — Mermaid tree, JSON dashboard config, or Markdown via the Python tool.

## When to Use

- **New product or strategic direction** -- before OKRs and roadmap, define the NSM and inputs.
- **Strategic re-alignment** -- the dashboard has 47 metrics and no one knows which to optimize.
- **Cross-functional friction** -- marketing, product, and growth disagree on what "success" means.
- **Investor / board reporting** -- the NSM becomes the headline metric.
- **A/B experimentation guardrails** -- every test reports NSM impact plus counter-metric impact.

**When NOT to use:** very early-stage discovery (use `discovery/` first — you don't yet know what value you deliver); pure infrastructure work with an indirect user-value chain; before the org has aligned on strategy (the NSM exposes disagreement but does not resolve it).

## Clarify First

Before defining the NSM, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Core customer value the product delivers:** drives NSM candidate selection; the NSM must be a proxy for this, not a revenue lagging metric.
- **Business archetype:** attention / transaction / productivity / marketplace / engagement sets the Amplitude archetype and the input-metric formula (multiplicative/additive/funnel/ratio).
- **Input metrics the team can directly influence:** the 3-5 nodes of the tree; if the team can't move them, the tree is decoration.
- **Anti-/counter-metrics to guard:** the thresholds that protect customer and business against a gamed NSM.

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Workflow

1. **Choose the NSM** [RECOMMENDED] by scoring 2-4 candidates against the five tests (customer value, strategic alignment, leading, single number, movable). Details: `references/nsm-playbook.md`.
2. **Decompose** into 3-5 inputs with a formula you can write down, and check the numbers multiply or add up to the NSM's current value.
3. **Add** 2-3 leading indicators per input (each with how far ahead it moves), anti-metrics and counter-metrics with thresholds, and a baseline plus trend next to every target.
4. **Render** the finished spec for a README, Confluence or Notion. The tool renders and checks shape; it does not choose the metric, so run it only once the spec exists:

```bash
python3 project-management/execution/north-star-metric/scripts/metric_tree_builder.py \
  --input project-management/execution/north-star-metric/assets/sample_nsm_spec.json --format mermaid
# --format markdown|json|confluence|notion|linear, --output FILE; --demo renders the same sample
```

**Done when** the formula reproduces the NSM's current value from the inputs (the sample: 28,000 WAA x 0.44 publishers = about 12,400), every input has a leading indicator and every target has a baseline.

**Exit codes:** 0 rendered; 2 missing file, invalid JSON, or a spec without an `nsm` object and an `inputs` list of named items.

## Anti-Patterns

### Inputs with no formula to the NSM
**Mistake:** The input metrics are "loosely related" to the NSM: marketing launches, NPS, feature adoption. Nobody can write the equation.
**Why it happens:** Picking metrics that feel important is faster than working out how the NSM actually decomposes.
**Instead:** Write the formula explicitly (multiplicative, additive, funnel or ratio), for example `WAA = new signups x activation rate x 4-week retention`. If the team cannot write it, the inputs are correlated at best, and moving them may not move the NSM.

### Leading indicators that are really lagging
**Mistake:** "Weekly retention" is listed as the leading indicator for weekly retention.
**Why it happens:** Any metric close to the input feels predictive.
**Instead:** For each leading indicator, state how many days or weeks before the input it moves. If the answer is zero or "same time", replace it with an earlier signal, such as day-1 sessions or first-action completion for new signups.

### Target with no baseline
**Mistake:** "Reach 50,000 WAA by Q4", with no current value and no trend.
**Why it happens:** The target is the exciting part, and pulling the history takes a data request.
**Instead:** Record the current value and the last 4 quarters of trajectory next to every target, and state how far above trend the target sits. If the metric can't be reported from today's instrumentation, ship the instrumentation first.

Nine more, each with a bad and a good example: `references/red-flags.md`.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/nsm-playbook.md](references/nsm-playbook.md)** — the five quality tests, Amplitude archetypes + real company examples, the metric-tree structure and input math, leading indicators, anti-/counter-metrics with thresholds, the step-by-step workflow, the `metric_tree_builder.py` reference (flags, input JSON, Mermaid sample), troubleshooting, and success criteria. Read when selecting an NSM or building the tree.
- **[references/nsm-framework-guide.md](references/nsm-framework-guide.md)** — deep dive on three overlapping frameworks (Sean Ellis NSM, Amplitude NSM, Lean Analytics OMTM), input-metric math, and worked examples across five business archetypes. Read when comparing frameworks or working a specific archetype.
- **[references/red-flags.md](references/red-flags.md)** — concrete examples of how NSM specs go wrong, why they're bad, and how to fix them. Read when reviewing an NSM or diagnosing a gamed/lagging metric.

## Files

| File | Purpose |
|---|---|
| `scripts/metric_tree_builder.py` | Renders a finished NSM spec |
| `assets/sample_nsm_spec.json` | SaaS productivity NSM with two inputs, indicators and guardrails |
| `assets/nsm_spec_template.md` | Fill-in spec template matching the JSON shape |
| `examples/acme-analytics-nsm.md` | Worked NSM |

## Scope & Limitations

**In Scope:** NSM selection across 5 archetypes; input-metric tree decomposition with explicit math; leading-indicator selection per input; anti-/counter-metric definition with thresholds; the Python rendering tool; handoff to OKR drafting and roadmap prioritization.

**Out of Scope:** building actual analytics dashboards (BI tools — this produces the spec); statistical experiment design (`discovery/brainstorm-experiments/`); financial/revenue forecasting (`finance/`); OKR drafting (`brainstorm-okrs/`); data quality validation (`data-analytics/`).

**Caveats:** an NSM exposes strategic disagreement but does not resolve it — escalate the strategy decision, not the metric debate. Pure financial outputs (revenue, ARR) are usually too lagging; pick a customer-value proxy that revenue follows from. The NSM aligns; teams still need component metrics for diagnostics. A team without instrumentation cannot operate against an NSM — spend on telemetry first.

## Integration Points

| Integration | Direction | Description |
|-------------|-----------|-------------|
| `discovery/brainstorm-ideas/` | Receives from | Opportunity discovery defines what value to deliver; NSM measures it |
| `discovery/identify-assumptions/` | Receives from | NSM candidates surface assumptions about what customers value |
| `execution/brainstorm-okrs/` | Feeds into | NSM becomes the quarterly Objective; inputs become Key Results |
| `execution/outcome-roadmap/` | Feeds into | Roadmap items justify themselves by which input metric they target |
| `execution/prioritization-frameworks/` | Pairs with | NSM impact is one of the scoring criteria (e.g., RICE Impact, Weighted) |
| `execution/status-update-generator/` | Feeds into | NSM and input movements feature in Highlights of weekly updates |
| `data-analytics/` (domain) | Pairs with | NSM spec becomes the schema for dashboards and event taxonomies |
| `senior-pm/` | Feeds into | Monthly board packets lead with NSM trend |
