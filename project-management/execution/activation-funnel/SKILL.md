---
name: activation-funnel
description: >
  Design and analyze activation funnels (AARRR / AAARRR Pirate Metrics) with
  conversion + drop-off math, bottleneck detection, and Mermaid funnel diagrams.
  Includes a stdlib Python tool that emits all 6 shared PM output formats.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-06-15
  python-tools: funnel_analyzer.py
  tech-stack: aarrr, pirate-metrics, activation, conversion-funnel, growth, north-star
---
# Activation Funnel Expert

## Overview

A funnel is the single most useful diagnostic tool a growth or onboarding PM owns. It turns a fuzzy product story ("users drop off somewhere") into a numbered, actionable picture ("76% land, 41% start setup, 9% finish setup, 4% take the activation action -- the biggest drop is between start and finish setup at 32 percentage points").

This skill specifies funnel structures using **Dave McClure's AARRR** (Acquisition, Activation, Retention, Revenue, Referral) and its broader cousin **AAARRR** (which adds Awareness on the front), and analyzes them with a stdlib Python tool (`funnel_analyzer.py`). The tool ingests a JSON funnel definition (stages with counts) and outputs stage-by-stage conversion and drop-off, a Mermaid flowchart, and a bottleneck call-out — in all six SHARED_OUTPUT_SCHEMA formats so the analysis travels into Jira, Linear, Confluence, Notion, or a PR.

The activation step is the centerpiece. Sean Ellis defined the "activated user" as one who has done the thing that statistically predicts retention (Slack's 2000 messages, Facebook's "7 friends in 10 days", Dropbox's "1 file in 1 folder on 1 device"). Pin the activation event before you optimize the funnel that leads to it.

## Core Capabilities

- **Funnel structure** — define stages as events using AARRR or AAARRR; compress to 4-7 stages.
- **Conversion + drop-off math** — per-stage conversion, absolute and relative drop, cumulative conversion, bottleneck detection (largest absolute vs largest relative drop).
- **Activation event definition** — Sean Ellis framework to pin the predictive "aha" event (count + window + action).
- **Counter-metric pairing** — guard every stage against gaming; leading-vs-lagging indicator design.
- **Six-format output** — render the analysis + Mermaid diagram for Jira, Linear, Confluence, Notion, or a PR.

## When to Use

- **New onboarding design** -- specify the funnel events from signup to value.
- **Drop-off diagnosis** -- signups grow but completion is flat; where is the leak?
- **Activation metric definition** -- pick the "aha" event that predicts long-term retention.
- **Cross-functional alignment** -- get marketing, product, and growth to agree on one funnel definition.
- **QBR / A/B test design** -- one canonical funnel drives the conversation and makes primary + counter-metrics obvious.

**When NOT to use:** pre-PMF discovery (use `discovery/`); top-of-funnel channel attribution (marketing tools); revenue-cohort retention (data-analytics domain); when events are not instrumented.

## Clarify First

Before analyzing the funnel, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Stages + counts** — the actual events and the user count at each step (drives every conversion/drop-off number and the bottleneck call-out)
- [ ] **Activation event** — the Sean Ellis "aha" event that defines an activated user (sets the funnel's centerpiece stage and the activation rate)
- [ ] **Cohort window** — the time period the counts are drawn from (snapshot funnels mix cohorts and lie; this scopes every number)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Quick Start

```bash
python scripts/funnel_analyzer.py --input funnel.json --format markdown   # conversion + drop-off + bottleneck
python scripts/funnel_analyzer.py --demo --format mermaid                 # worked SaaS funnel diagram
```

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/funnel-analysis-playbook.md](references/funnel-analysis-playbook.md)** — full AARRR/AAARRR stage tables, the aha-event definition method, conversion/drop-off math, counter-metric pairing, leading-vs-lagging indicators, the step-by-step workflow, the `funnel_analyzer.py` reference (flags, input JSON, Mermaid sample), troubleshooting, and success criteria. Read when building or analyzing a funnel.
- **[references/pirate-metrics-deep-dive.md](references/pirate-metrics-deep-dive.md)** — McClure's AARRR + AAARRR, Andrew Chen funnel mechanics, the Reforge growth model, and NSM-funnel linkage. Read when designing the overall growth model around the funnel.
- **[references/activation-aha-moment-patterns.md](references/activation-aha-moment-patterns.md)** — Ellis's framework plus 12 worked activation-event examples (Slack, FB, Dropbox, Airbnb, Notion, Spotify, Duolingo, Twitter, HubSpot, Pinterest, LinkedIn, Figma). Read when choosing or validating the activation event.
- **[references/red-flags.md](references/red-flags.md)** — concrete examples of how funnel output goes wrong, why it's bad, and how to fix it. Read when reviewing a funnel analysis or diagnosing a misleading chart.
- **assets/funnel_design_canvas.md** — workshop canvas for defining the funnel. Use in a design session.
- **assets/activation_metric_worksheet.md** — worksheet for picking the activation event. Use when pinning the aha event.
- **assets/sample_funnel.json** — a working JSON example matching the tool input. Use as a starting template.

## Scope & Limitations

**In Scope:** funnel definition (events, stages, transitions) via AARRR/AAARRR; conversion + drop-off math and bottleneck detection; Mermaid rendering; activation-event selection (Ellis); counter-metric pairing; cohort-vs-snapshot distinction; all 6 output formats.

**Out of Scope:** pulling raw event data (input is JSON — use Amplitude/Mixpanel/PostHog/Looker); statistical significance testing (`discovery/brainstorm-experiments/`, data-analytics); cohort-retention analysis; channel attribution (marketing tools); building the UX/A/B test; forecasting.

**Caveats:** a funnel implies a linear flow — real products branch and re-enter, so complement with branched analysis. Snapshot funnels mix cohorts and lie; always specify the cohort window. Top-stage gains amplify downstream and can mislead investment — look at both absolute and relative drop. Re-validate the activation event against fresh retention cohorts every 1-2 quarters.

## Integration Points

| Integration | Direction | Description |
|---|---|---|
| `north-star-metric/` | Pairs with | Activation rate is often the NSM or a top input metric in the NSM tree |
| `brainstorm-okrs/` | Feeds into | Funnel-stage targets become KRs (e.g., "improve activation from 28% to 36%") |
| `prioritization-frameworks/` | Feeds into | Fix-the-funnel projects ranked by RICE / weighted-score |
| `discovery/brainstorm-experiments/` | Pairs with | Each funnel leak suggests testable experiments to plug it |
| `discovery/identify-assumptions/` | Pairs with | "Users will complete step 3 if we shorten it" is an assumption to validate |
| `status-update-generator/` | Feeds into | Weekly funnel deltas appear in Highlights / Risks |
| `outcome-roadmap/` | Pairs with | Roadmap items justify themselves by which funnel stage they target |
| `cycle-time-analyzer/` | Pairs with | Cycle time to fix funnel leaks is part of flow analysis |
| `data-analytics/` (domain) | Pairs with | Telemetry instrumentation; cohort analysis; stat sig |
