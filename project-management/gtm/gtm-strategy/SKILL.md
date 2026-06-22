---
name: gtm-strategy
description: >
  Integrated go-to-market strategy spanning ICP, motion, channels,
  messaging, success metrics, and launch plan. Use when launching a
  new product, entering a new segment, or auditing why an existing
  GTM isn't working.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: project-management
  domain: go-to-market
  updated: 2026-05-27
  python-tools: gtm_strategy_validator.py
  tech-stack: gtm, go-to-market, motion, launch, beachhead
---

# GTM Strategy

A complete go-to-market strategy is the integrated cross-functional plan:
ICP, motion, channels, messaging, success metrics, and launch sequence.

## When to use this skill

- **New product launch** (full product or major feature)
- **New segment entry** (SMB → ENT; new geography; new vertical)
- **GTM refresh** (current motion stalling)
- **Repositioning** after pivot
- **Pre-fundraise** GTM narrative for investors
- **Post-mortem** on why a launch didn't take

## The 7 components

1. **ICP (Ideal Customer Profile)** — who specifically, why now
2. **Beachhead segment** — first concentrated market
3. **Motion** — PLG / sales-led / hybrid / channel-led
4. **Channels** — how customers find + buy
5. **Messaging + positioning** — what we say
6. **Success metrics** — what we measure
7. **Launch sequence** — what happens in what order

## Clarify First

Before building the GTM strategy, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **ACV / price point** — determines the motion and channel mix (motion-ACV mismatch, e.g. sales-led on $50/mo, breaks unit economics)
- [ ] **ICP and beachhead segment** — the one concentrated market to win first (drives targeting, channels, and messaging; "everyone" dilutes all seven components)
- [ ] **Self-serve readiness** — can the product activate without a human (PLG vs sales-led/committee buying)
- [ ] **Launch trigger and timeline** — what's launching and when (sets the T-90 → T+90 sequence)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Workflow

### Step 1 — Define ICP precisely
- Industry / vertical
- Size band (employees / revenue)
- Geography
- Buyer persona (role, level)
- Tech stack signals
- Job-to-be-done
- Trigger event (why now)

See `project-management/gtm/ideal-customer-profile`.

### Step 2 — Pick the beachhead
Start narrow:
- 1 segment, 1 vertical, 1 geography
- Concentrated enough to develop reference customers
- Reachable via clear channels
- Big enough to learn from but small enough to dominate

Reference: Crossing the Chasm. Don't try to sell to everyone Day 1.

### Step 3 — Pick the motion

| Motion | When | Cost structure |
|--------|------|----------------|
| **PLG (product-led)** | Self-serve product; low ACV ($0-$5K); strong activation | Low CAC; high product investment |
| **Sales-led** | High ACV ($25K+); complex buying committees | High CAC; sales team needed |
| **Marketing-led / inbound** | Mid-ACV ($5K-$25K); content-driven | Medium CAC; content + ops team |
| **Channel-led** | Wide distribution via partners | Medium CAC; partner program needed |
| **Community-led** | Strong category with passionate users | Long ramp; high ongoing investment |
| **Hybrid (PLG + sales)** | PLG to capture; sales to expand | Most modern SaaS; complex to coordinate |

Don't try to run all motions Day 1.

### Step 4 — Channels per motion

| Motion | Primary channels |
|--------|------------------|
| PLG | Web direct, SEO, viral, content, app stores |
| Sales-led | Outbound SDR, AE outbound, events, account-based |
| Marketing-led | SEO, paid, content syndication, webinar |
| Channel-led | Partner program, marketplace |
| Community-led | Open source, community events, integrations |

### Step 5 — Messaging + positioning
- **Positioning:** "[Product] is [category] for [target] who [JTBD], unlike [alternative]"
- **Hero message:** outcome customers want (not feature)
- **Differentiation:** clear "why us vs them"
- **Talk track per segment:** different ICPs need different framing

### Step 6 — Success metrics

| Motion | KPI focus |
|--------|-----------|
| PLG | Signups, activation, free-to-paid conversion, NRR |
| Sales-led | Pipeline coverage, win rate, ACV, cycle time, NRR |
| Marketing-led | MQL → SQL conversion, CPA, content engagement |
| Channel-led | Partner-sourced revenue, partner activity |

Set targets; track weekly; tune.

### Step 7 — Launch sequence
- **T-90:** ICP locked; positioning v1; channels chosen; team aligned
- **T-60:** Sales/marketing collateral ready; pilot customers identified
- **T-30:** Internal training; lighthouse customer commitments
- **T-7:** Launch comms prepped; press / analyst briefed
- **T-0:** Launch
- **T+30:** Iterate based on early signal
- **T+90:** GTM v2 incorporating learnings

### Step 8 — Run `gtm_strategy_validator.py`
Audit GTM doc for: ICP specificity, motion fit, channel coherence,
messaging clarity, metric definition, sequence realism.

```bash
python3 project-management/gtm/gtm-strategy/scripts/gtm_strategy_validator.py \
  --input gtm.json --format markdown
```

## Decision frameworks

### Motion fit by ACV

| ACV | Likely motion |
|-----|---------------|
| < $1K | PLG; consumer-style |
| $1K-$10K | PLG-led; light sales-assist |
| $10K-$50K | Marketing-led + inside sales |
| $50K-$250K | Sales-led with marketing support |
| $250K+ | Enterprise sales-led; long cycle |

Cross these and economics break.

### Beachhead vs broad

Going broad Day 1:
- Diluted messaging
- No reference customers
- Sales motion thinly stretched
- No moat in any segment

Beachhead first:
- Win the segment
- Build reference customers
- Develop battle-tested motion
- Then expand adjacent

Geoffrey Moore: cross the chasm one bowling pin at a time.

### Channel-product fit

Each channel has product-fit assumptions:
- SEO: long content; SERP-able problem
- Paid: clear high-intent keywords; LTV > 2-3x CAC
- Outbound: defined ICP; AE can articulate value in 30 seconds
- Channel: partners economically incentivized; product fits their offering
- Community: passionate users + room to participate
- Viral: collaboration / sharing built into product

If channel-product fit is off, channel won't deliver regardless of effort.

## Common engagements

### "Help us launch product X in market Y"
1. Confirm ICP precision (or sharpen).
2. Pick beachhead segment.
3. Choose motion based on ACV + product complexity.
4. Map channels to motion.
5. Draft positioning + messaging.
6. Define success metrics + targets.
7. Build T-90 → T+90 launch sequence.

### "Our GTM is stalling — what's wrong?"
1. Audit each component for clarity + execution.
2. Common failures:
   - ICP too broad
   - Motion mismatch with ACV
   - Channels not delivering pipeline
   - Messaging not differentiated
   - Metrics not tracked
3. Identify the breakpoint; fix one at a time.

### "Should we move from PLG to sales-led?"
1. Look at ACV trend: rising with enterprise = yes
2. Look at pipeline: enterprise inquiries unanswered = yes
3. Look at unit economics: PLG CAC payback < sales CAC payback?
4. Plan hybrid: PLG capture + sales expansion (most common path)

## Anti-patterns to avoid

- **ICP = "everyone."** Diluted strategy.
- **Motion mismatched with ACV.** Sales motion on $50/mo = unit economics broken.
- **Channels listed; not invested.** Knowing channels doesn't activate them.
- **Generic messaging.** "Faster, better, cheaper."
- **No success metrics.** Can't tune what you can't measure.
- **Launch sequence = "ship and see."** Predictable underperformance.
- **All motions at once.** Try one; succeed before adding.

## References

- `references/gtm-components-deep.md` — ICP, motion, channels, messaging deep
- `references/launch-sequence-playbook.md` — T-90 → T+90 playbook
- `references/gtm-anti-patterns.md` — common failures + fixes

## Related skills

- `project-management/gtm/ideal-customer-profile` — ICP definition
- `project-management/strategy-frameworks/business-model-canvas` — model behind GTM
- `marketing/launch-strategy` — marketing execution layer
- `business-growth/customer-success-manager` — post-sale GTM
- `c-level-advisor/cro-advisor` — sales / revenue strategy
- `c-level-advisor/cmo-advisor` — marketing strategy
