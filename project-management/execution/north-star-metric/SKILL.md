---
name: north-star-metric
description: >
  Define a North Star Metric (NSM) and its input metric tree, with leading
  indicators, anti-metrics, and counter-metrics. Includes a Python tool that
  renders the metric tree as a Mermaid diagram.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-06-15
  python-tools: metric_tree_builder.py
  tech-stack: north-star, input-metrics, leading-indicators, counter-metrics, omtm
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

Before defining the NSM, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Core customer value the product delivers** — drives NSM candidate selection; the NSM must be a proxy for this, not a revenue lagging metric
- [ ] **Business archetype** — attention / transaction / productivity / marketplace / engagement sets the Amplitude archetype and the input-metric formula (multiplicative/additive/funnel/ratio)
- [ ] **Input metrics the team can directly influence** — the 3-5 nodes of the tree; if the team can't move them, the tree is decoration
- [ ] **Anti-/counter-metrics to guard** — the thresholds that protect customer and business against a gamed NSM

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Quick Start

```bash
python scripts/metric_tree_builder.py --input nsm_spec.json --format mermaid   # render the metric tree
python scripts/metric_tree_builder.py --demo --format markdown                 # worked SaaS productivity NSM
```

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/nsm-playbook.md](references/nsm-playbook.md)** — the five quality tests, Amplitude archetypes + real company examples, the metric-tree structure and input math, leading indicators, anti-/counter-metrics with thresholds, the step-by-step workflow, the `metric_tree_builder.py` reference (flags, input JSON, Mermaid sample), troubleshooting, and success criteria. Read when selecting an NSM or building the tree.
- **[references/nsm-framework-guide.md](references/nsm-framework-guide.md)** — deep dive on three overlapping frameworks (Sean Ellis NSM, Amplitude NSM, Lean Analytics OMTM), input-metric math, and worked examples across five business archetypes. Read when comparing frameworks or working a specific archetype.
- **[references/red-flags.md](references/red-flags.md)** — concrete examples of how NSM specs go wrong, why they're bad, and how to fix them. Read when reviewing an NSM or diagnosing a gamed/lagging metric.
- **assets/nsm_spec_template.md** — fill-in template for an NSM specification matching the tool's JSON shape. Use when drafting a spec.

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
| `executive-reporting/` (senior-pm) | Feeds into | Monthly board packets lead with NSM trend |
