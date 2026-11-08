---
name: gtm-strategy
description: >
  Builds and audits a go-to-market plan: beachhead, motion matched to ACV,
  funded channels, tested messaging, owned metrics and a T-90 launch sequence.
  Use when launching a product, entering a segment or fixing a stalled GTM.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: project-management
  domain: go-to-market
  updated: 2026-11-08
  python-tools: gtm_strategy_validator.py
  tech-stack: gtm, go-to-market, motion, launch, beachhead
  tags:
    - go-to-market
    - icp
    - channels
    - messaging
    - launch
---

# GTM Strategy

The agent produces one integrated plan across seven components: ICP, beachhead, motion, channels, messaging, metrics and launch sequence. Each choice has to fit the others; most stalled launches fail at a seam (a sales-led motion on a $4K ACV, channels with no budget, a message nobody tested).

**Done looks like:** an ICP specific enough to build a list from, and one beachhead inside it; a motion that fits the ACV; 2-4 channels, each with budget and an owner; a hero message under 120 characters that names the differentiator and was tested with ICP buyers; 3-6 metrics with targets and owners; three or more lighthouse customers before launch; `gtm_strategy_validator.py` exits 0 with no warnings left unanswered.

## When to Use

- Launching a product or major feature, or entering a new segment, geography or vertical
- A GTM that is stalling, or a repositioning after a pivot
- A pre-fundraise GTM narrative, or a post-mortem on a launch that did not take

Build the ICP itself with `project-management/gtm/ideal-customer-profile`; this skill starts from it.

## Clarify First

Before building the GTM strategy, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **ACV / price point:** determines the motion and channel mix (motion-ACV mismatch, e.g. sales-led on $50/mo, breaks unit economics).
- **ICP and beachhead segment:** the one concentrated market to win first (drives targeting, channels, and messaging; "everyone" dilutes all seven components).
- **Self-serve readiness:** can the product activate without a human (PLG vs sales-led/committee buying).
- **Launch trigger and timeline:** what's launching and when (sets the T-90 → T+90 sequence).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

```bash
# Mid-market sales-led launch: exit 0, no findings
python3 project-management/gtm/gtm-strategy/scripts/gtm_strategy_validator.py \
  --input project-management/gtm/gtm-strategy/assets/sample_gtm.json --format markdown
```

```bash
# "Everyone" ICP, sales-led at $4K ACV, seven unfunded channels, no metrics: exit 1
python3 project-management/gtm/gtm-strategy/scripts/gtm_strategy_validator.py \
  --input project-management/gtm/gtm-strategy/assets/sample_gtm_flawed.json --format markdown
```

```bash
# Input schema and flags
python3 project-management/gtm/gtm-strategy/scripts/gtm_strategy_validator.py --help
```

## Tools Overview

`gtm_strategy_validator.py` is the quality gate for this skill. **What the validator checks:** an ICP with size, vertical, role, job and trigger; a beachhead; motion-ACV fit (sales-led under $10K, PLG over $100K); 1-6 channels with budget and owners; a hero message that exists (fail otherwise), is short and avoids generic terms; the self-reported `differentiator_named` / `tested_with_customers` flags; metrics present (fail otherwise) with targets and owners; lighthouse customers; alignment and budget. It checks that the parts exist and fit each other; it cannot judge whether the strategy will work, and the boolean flags are only as honest as whoever set them.

**Exit codes:** `0` no fail findings · `1` at least one fail (no ICP, channels, hero message or metrics) · `2` unreadable file, invalid JSON or a top level that is not an object. JSON by default, `--format markdown`, `--output FILE`.

## Workflow

1. **ICP.** Take it from `ideal-customer-profile` (size, vertical, geography, role, job, trigger). If it would fit "everyone who manages people", stop and sharpen it first.
2. **Beachhead.** One segment, one vertical, one geography: concentrated enough to produce reference customers, reachable through clear channels, small enough to win.
3. **Motion.** Fit it to ACV and buying complexity: self-serve and low ACV point to PLG, committee buying and $25K+ to sales-led, the middle to marketing-led or inside sales. Run one motion well before adding another. ACV bands and motion tables: `references/gtm-components-deep.md` (appendix).
4. **Channels.** 2-4 that fit the motion and the product (an SEO channel needs a searchable problem; outbound needs a value line an AE can say in 30 seconds). Each gets budget and an owner.
5. **Messaging.** Positioning: "[product] is [category] for [target] who [job], unlike [alternative]". A hero message about the outcome, a named differentiator, talk tracks per persona, tested with ICP buyers.
6. **Metrics.** 3-6 covering pipeline, conversion and quality, each with a target and an owner, reviewed weekly.
7. **Launch sequence.** T-90 ICP and positioning locked; T-60 collateral and pilots; T-30 training and lighthouse commitments; T-7 comms; T+30 and T+90 revisions. Detail: `references/launch-sequence-playbook.md`.
8. **Audit.** Write the plan as JSON (schema in `--help`; `assets/sample_gtm.json` is a complete example) and run the validator. It must pass with no fail findings; then verify that each warning is fixed or has a stated reason.

For a stalling GTM, audit the current plan first and fix the first broken seam (ICP, motion fit, channels, message, metrics) before touching the next.

## Anti-Patterns

### Motion mismatched with ACV
**Mistake:** A field-sales motion sells a $4K-a-year product.
**Why it happens:** The team copies the motion of a company it admires.
**Instead:** Pick the motion from ACV and buying complexity, and check CAC payback before hiring for it.

### Channels listed, not funded
**Mistake:** Seven channels in the plan, none with budget or an owner.
**Why it happens:** Listing channels feels like coverage.
**Instead:** Fund 2-4 channels properly and name who runs each; the rest wait for evidence.

### Launch as a moment
**Mistake:** "Ship and announce", with no lighthouse customers or sequence.
**Why it happens:** The launch date is fixed before the GTM work starts.
**Instead:** Work back from T-90 and secure three or more lighthouse customers before the announcement.

More with fixes: `references/gtm-anti-patterns.md`.

## Scope & Limitations

**In Scope:**
- A go-to-market strategy across seven components: ICP, beachhead segment, motion, channels, messaging and positioning, success metrics and launch sequence
- Motion choice by ACV across PLG, sales-led, marketing-led, channel-led, community-led and hybrid
- Channel mapping per motion, channel-product fit checks and KPI focus per motion (tables in the reference appendix)
- A T-90 to T+90 launch sequence
- A plan audit for ICP completeness, beachhead, motion-ACV fit, funded and owned channels, message basics, metric targets and lighthouse customers (`gtm_strategy_validator.py`)

**Out of Scope:**
- Building and scoring the ICP in depth (see `project-management/gtm/ideal-customer-profile/`)
- Marketing launch execution such as campaigns and content (see `marketing/launch-strategy/`)
- Setting price and packaging (see `business-growth/pricing-strategy/`)
- Sales operations, pipeline tooling and forecasting (see `business-growth/revenue-operations/`)
- The cross-functional launch-day checklist (see `project-management/execution/launch-playbook/`)

**Important Caveats:**
- `gtm_strategy_validator.py` audits a hand-written JSON document. Flags such as `specific_enough` and `tested_with_customers` are self-reported.
- The ACV bands for motion fit are rules of thumb. They do not replace the team's own unit economics.
- The tool uses no market data. Segment size, channel performance and competitor positioning come from the team's own research.
- Beachhead choice, motion and budget stay leadership decisions, and the plan needs a refresh after launch data arrives.

## Files

| File | Purpose |
|------|---------|
| `scripts/gtm_strategy_validator.py` | GTM plan audit |
| `assets/sample_gtm.json` | Mid-market HR analytics launch; exits 0 |
| `assets/sample_gtm_flawed.json` | Unfocused launch plan; exits 1 |
| `assets/gtm_strategy_template.md` | Fill-in template |

## Reference Documentation

- [references/gtm-components-deep.md](references/gtm-components-deep.md): ICP, motion, channels, messaging; appendix with motion/ACV, channel and KPI tables
- [references/launch-sequence-playbook.md](references/launch-sequence-playbook.md): T-90 to T+90 playbook
- [references/gtm-anti-patterns.md](references/gtm-anti-patterns.md): Common failures and fixes

## Related skills

- `project-management/gtm/ideal-customer-profile` — ICP definition
- `project-management/strategy-frameworks/business-model-canvas` — model behind GTM
- `marketing/launch-strategy` — marketing execution layer
- `business-growth/customer-success-manager` — post-sale GTM
- `c-level-advisor/cro-advisor` — sales / revenue strategy
- `c-level-advisor/cmo-advisor` — marketing strategy
