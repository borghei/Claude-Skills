---
name: referral-program
description: "Designs and optimizes referral and affiliate programs covering referral loop architecture, incentive design, trigger moment optimization, viral coefficient modeling, affiliate program structure, and systematic optimization playbooks. Use when the user asks about building a referral program, designing referral incentives, improving referral conversion rates, creating an affiliate program, calculating viral coefficients, optimizing word-of-mouth growth, or analyzing referral funnel performance."
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: business-growth
  updated: 2026-03-31
  tags: [referral, affiliate, growth, viral, word-of-mouth, acquisition]
---

# Referral Program

Production-grade referral and affiliate program framework covering the 4-stage referral loop, incentive design, trigger moment optimization, share mechanics, viral coefficient modeling, affiliate program architecture, and systematic optimization playbook.

## Referral vs Affiliate Decision

| Factor | Customer Referral | Affiliate Program |
|--------|------------------|-------------------|
| Who promotes | Existing customers | External partners, bloggers, influencers |
| Best for | B2C, prosumer, SMB SaaS | B2B SaaS, high LTV, content-heavy niches |
| Payout | Account credit, discount, or cash | Revenue share or flat fee per conversion |
| Scale | Scales with active user base | Scales with partner recruitment |

**Decision rule:** If customers are enthusiastic and social, start with customer referrals. If customers are businesses buying on behalf of a team, start with affiliates.

## Core Workflow

### 1. Define Program Type and Incentive Structure

The agent selects referral or affiliate based on the decision table above, then designs the incentive:

| Type | When to Use | Sizing Guideline |
|------|-------------|-----------------|
| Account credit | SaaS, subscription | 10-20% of monthly plan |
| Cash | High LTV, B2C | < 30% of first payment |
| Feature unlock | Freemium products | Feature value > cost |

**Double-sided vs single-sided rule:** If referral rate < 1%, go double-sided. If > 5%, single-sided is more profitable.

**Reward economics:**
```
Maximum reward = LTV × Target referral CAC ratio (typically 15%)
Example: $2,000 LTV × 15% = $300 max reward
```

**Validate:** Confirm reward is < 30% of first payment and double-sided reward split totals within the maximum.

### 2. Map Trigger Moments

The agent identifies high-signal moments to ask for referrals:

| Trigger | When to Fire |
|---------|-------------|
| After aha moment | After activation event |
| After milestone | "You just saved your 100th hour" |
| After great support | Post-resolution, NPS 9-10 |
| After renewal/upgrade | Day of renewal |

**Validate:** At least 3 trigger moments identified with specific in-product or email implementation points.

### 3. Design Share Mechanics

The agent configures the share flow with these required elements:
- Personal referral link (unique per user, trackable)
- Pre-filled share message (editable, first-person voice, 2-3 sentences)
- Multiple channels: email invite, link copy, social share, Slack/Teams for B2B
- One-click send on mobile (native share sheet)

**Validate:** Share flow has ≤ 2 clicks from trigger to send; at least 3 share channels configured.

### 4. Specify Referred User Experience

The agent designs the referral landing page and attribution:
- Personalization: "Your friend [Name] invited you"
- Incentive displayed above the fold
- Reduced signup friction (pre-fill email, offer SSO)
- Attribution: 30-day cookie minimum, first-click wins

**Validate:** Landing page spec includes referrer name, incentive display, and signup friction reduction.

### 5. Configure Reward Delivery

The agent ensures fast, visible reward fulfillment:
- Immediate confirmation when referral converts
- Dashboard visibility: "2 friends joined — you've earned $40"
- Auto-applied credit or one-click claim
- Progress toward next tier (if using tiered rewards)

**Validate:** Reward delivery is < 24 hours; redemption requires ≤ 1 click.

### 6. Model Viral Coefficient and Optimize

The agent calculates the K-factor and identifies optimization levers:

```
K = i × c
i = average invitations sent per user
c = conversion rate of invitations

K > 1.0 = viral growth (rare outside social products)
K = 0.3-0.7 = strong referral contribution
K < 0.1 = program needs work
```

**Optimization priority (fix in this order):**
1. Awareness — if users do not know the program exists
2. Share flow — if users know but do not share
3. Referred experience — if users share but referrals do not convert
4. Incentive — only change the reward after mechanics work

**Validate:** K-factor calculated with realistic inputs; optimization priorities match the weakest funnel stage.

## Key Metrics

| Metric | Formula | Target |
|--------|---------|--------|
| Active referrers % | Users who sent 1+ referral / Active users | 5-15% |
| Referral conversion rate | Referred signups / Referrals sent | 15-25% |
| Referral CAC | Total reward cost / Referral-acquired customers | < 50% of other CAC |
| K-factor | Invitations per user × Conversion rate | 0.3-0.7 |

## Anti-Patterns

1. **Asking at signup** — The user has experienced no value yet. Referral prompts before the aha moment convert at near-zero rates.
2. **Delayed or complicated rewards** — Reward redemption requiring multiple steps or taking > 24 hours breaks the referral loop. Auto-apply credits immediately.
3. **Generic monthly "refer a friend" emails** — No trigger, no urgency, becomes invisible. Use event-driven triggers tied to product milestones instead.
4. **Optimizing incentive before fixing mechanics** — Doubling the reward does not help if users cannot find the share button. Fix awareness and friction first.
5. **Identical experience for referred users** — Referred users arrive with context from their friend. A generic landing page wastes the social proof advantage.

## Tools

### referral_economics_calculator.py

Calculates reward sizing, K-factor, referral CAC, ROI projections, and break-even analysis.

```bash
python scripts/referral_economics_calculator.py program.json --format text
python scripts/referral_economics_calculator.py program.json --format json
```

| Flag | Type | Description |
|------|------|-------------|
| `program.json` | positional | JSON file with program economics data |
| `--format` | optional | Output format: `text` (default) or `json` |

### referral_funnel_analyzer.py

Analyzes the 4-stage referral loop with stage-over-stage conversion and identifies the weakest stage.

```bash
python scripts/referral_funnel_analyzer.py funnel.json --format text
```

| Flag | Type | Description |
|------|------|-------------|
| `funnel.json` | positional | JSON file with referral funnel metrics |
| `--format` | optional | Output format: `text` (default) or `json` |

### affiliate_commission_modeler.py

Models affiliate commission structures across tier levels with per-tier economics and lifetime partner value.

```bash
python scripts/affiliate_commission_modeler.py affiliate.json --format text
```

| Flag | Type | Description |
|------|------|-------------|
| `affiliate.json` | positional | JSON file with affiliate program data |
| `--format` | optional | Output format: `text` (default) or `json` |

## Troubleshooting

| Problem | Resolution |
|---------|------------|
| Program awareness below 40% | Add persistent dashboard widget, post-activation prompt, and post-NPS trigger |
| Share rate below 20% | Add one-click copy link, native share sheet on mobile, pre-filled first-person message |
| Referral conversion below 15% | Add referrer name/photo to landing page, display incentive above fold, reduce signup friction |
| K-factor below 0.1 | Diagnose in sequence: awareness → share flow → landing page → incentive |
| Referred customers churn faster than organic | Shift from cash/discount rewards to product-value rewards; add referred-user onboarding path |

## References

- [Program Design Guide](references/program-design-guide.md) — Detailed share message templates, affiliate toolkit checklists, tier system design, copy templates, and landing page specifications
- **pricing-strategy** — Referral reward sizing must align with pricing margins and LTV
- **signup-flow-cro** — Referred user signup flow optimization
- **churn-prevention** — Monitor referred customer retention separately
