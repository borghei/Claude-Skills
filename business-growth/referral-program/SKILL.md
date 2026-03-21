---
name: referral-program
description: Referral and affiliate program design covering referral loop architecture, incentive design, trigger moment optimization, viral coefficient modeling, affiliate program structure, and optimization playbook.
version: 1.0.0
author: borghei
category: business-growth
tags: [referral, affiliate, growth, viral, word-of-mouth, acquisition]
triggers:
  - user wants to design or optimize a referral program
  - user mentions refer-a-friend, referral link, or word-of-mouth growth
  - user asks about affiliate programs or partner programs
  - user mentions viral loops, K-factor, or viral coefficient
  - user wants to reduce CAC through referrals
  - user mentions brand ambassador or incentive program
---

# Referral Program

Production-grade referral and affiliate program framework covering the 4-stage referral loop, incentive design methodology, trigger moment optimization, share mechanics, viral coefficient modeling, affiliate program architecture, and systematic optimization playbook. Designed to build programs that compound, not collect dust.

---

## Table of Contents

- [Referral vs Affiliate Decision](#referral-vs-affiliate-decision)
- [The 4-Stage Referral Loop](#the-4-stage-referral-loop)
- [Incentive Design](#incentive-design)
- [Trigger Moment Architecture](#trigger-moment-architecture)
- [Share Mechanics](#share-mechanics)
- [Referred User Experience](#referred-user-experience)
- [Viral Coefficient Modeling](#viral-coefficient-modeling)
- [Affiliate Program Framework](#affiliate-program-framework)
- [Optimization Playbook](#optimization-playbook)
- [Metrics and Benchmarks](#metrics-and-benchmarks)
- [Program Copy Templates](#program-copy-templates)
- [Output Artifacts](#output-artifacts)
- [Related Skills](#related-skills)

---

## Referral vs Affiliate Decision

| Factor | Customer Referral | Affiliate Program |
|--------|------------------|-------------------|
| Who promotes | Your existing customers | External partners, bloggers, influencers |
| Motivation | Loyalty, reward, social currency | Commission, audience monetization |
| Best for | B2C, prosumer, SMB SaaS | B2B SaaS, high LTV, content-heavy niches |
| Activation | Triggered by product satisfaction | Recruited and onboarded proactively |
| Payout | Account credit, discount, or cash reward | Revenue share or flat fee per conversion |
| CAC impact | Low -- reward is typically < 30% of first payment | Variable -- commission determines economics |
| Scale | Scales with active user base | Scales with partner recruitment |

**Decision rule:** If your customers are enthusiastic and social, start with customer referrals. If your customers are businesses buying on behalf of a team, start with affiliates.

---

## The 4-Stage Referral Loop

Every referral program runs on this loop. If any stage is weak, the entire program underperforms.

```
[Trigger Moment] → [Share Action] → [Referred User Converts] → [Reward Delivered] → Loop
```

### Stage 1: Trigger Moment

When you ask customers to refer. Timing is everything.

**High-signal trigger moments:**

| Trigger | Why It Works | When to Fire |
|---------|-------------|-------------|
| After aha moment | User just experienced core value, highest satisfaction | After activation event |
| After milestone | Celebrates achievement, creates social sharing impulse | "You just saved your 100th hour" |
| After great support | Gratitude creates sharing impulse | Post-resolution, NPS 9-10 |
| After renewal/upgrade | Commitment signal, satisfied customer | Day of renewal |
| After public win | Customer tweets about you or posts a case study | Within 24 hours |
| After team growth | New team members = new potential referrers | After Nth team member joins |

**What does NOT work:**
- Asking at signup (no value experienced yet)
- Asking in every email footer (becomes invisible)
- Asking during onboarding (too early, too distracted)
- Generic monthly "refer a friend" email (no trigger, no urgency)

### Stage 2: Share Action

Remove every point of friction between wanting to share and actually sharing.

**Required share mechanics:**
- Personal referral link (unique per user, trackable)
- Pre-filled share message (editable, not locked)
- Multiple share channels: email invite, link copy, social share
- For B2B: Slack/Teams share option
- One-click send on mobile (native share sheet)

**Share message rules:**
- Written in first person (sounds like it is from a friend, not marketing)
- Includes the specific benefit the referrer experienced
- Short (2-3 sentences max)
- Includes the referral link with clear CTA

### Stage 3: Referred User Converts

The referred user lands on your product. Their experience must:

- Show personalization: "Your friend [Name] invited you"
- Display the incentive clearly above the fold
- Reduce signup friction (pre-fill email if available, offer SSO)
- Track attribution from landing through conversion (multi-session)

### Stage 4: Reward Delivered

The reward must be fast and clear. Delayed rewards break the loop.

| Action | Implementation |
|--------|---------------|
| Immediate confirmation | "Your friend just signed up! Here's your reward" |
| In-product visibility | Dashboard: "2 friends joined -- you've earned $40" |
| Email notification | Instant notification when referral converts |
| Easy redemption | Auto-applied credit or one-click claim |

---

## Incentive Design

### Single-Sided vs Double-Sided

| Type | When to Use | Cost | Conversion Impact |
|------|-------------|------|------------------|
| Single-sided (referrer only) | Strong viral hooks, enthusiastic users | Lower | Moderate |
| Double-sided (both get rewarded) | Need to overcome inertia on both sides | Higher | Higher |

**Decision rule:** If referral rate < 1%, go double-sided. If > 5%, single-sided is more profitable.

### Reward Types

| Type | Best For | Examples | Sizing Guideline |
|------|---------|---------|-----------------|
| Account credit | SaaS, subscription | "$20 credit toward your bill" | 10-20% of monthly plan |
| Discount | E-commerce, usage-based | "1 month free" | 1 month or 15-25% of annual |
| Cash | High LTV, B2C | "$50 for each referral" | < 30% of first payment |
| Feature unlock | Freemium products | "Unlock advanced analytics" | Feature value > cost |
| Status/recognition | Community products | "Ambassador badge" | Zero cost, high perceived value |
| Charity donation | Enterprise, mission-driven | "$25 to a cause you choose" | Similar to cash amount |

### Tiered Rewards (Gamification)

For referrers who go beyond 1 referral:

| Tier | Reward | Design Rule |
|------|--------|-------------|
| 1 referral | $20 credit | Easy to reach, immediate gratification |
| 3 referrals | $75 credit + bonus feature | Meaningful step-up, not just 3x |
| 10 referrals | $300 cash + ambassador status | Significant reward, social recognition |

**Rules:**
- Maximum 3 tiers (more is confusing)
- Each tier should feel meaningfully better, not just marginally
- Show progress toward next tier in the dashboard

### Reward Economics

```
Maximum reward per referral = LTV x Target referral CAC ratio

Example:
  Average LTV: $2,000
  Target referral CAC: 15% of LTV
  Maximum reward: $300

  If double-sided:
    Referrer reward: $150
    Referred reward: $150 (or equivalent credit/discount)
```

---

## Trigger Moment Architecture

### In-Product Trigger Points

| Location | Trigger Type | Copy Example |
|----------|-------------|-------------|
| Dashboard widget | Persistent, low-key | "Know someone who'd love [Product]? Give $20, get $20" |
| Post-milestone modal | Celebration moment | "You just hit 1,000 contacts! Share [Product] with a colleague?" |
| Settings/account page | Always available | "Referral Program: Earn $20 for every friend who joins" |
| Success state | After positive outcome | "Great results! Know someone who'd find this useful?" |
| Team invite flow | Natural sharing moment | "Or invite them via referral link and you both get $20" |

### Email Trigger Points

| Trigger | Email Content | Timing |
|---------|-------------|--------|
| Post-activation (first value delivered) | "Loving [Product]? Share it and earn rewards" | 3-5 days after activation |
| Post-NPS (score 9-10) | "Glad you love us! Here's an easy way to share" | Immediately after NPS |
| Post-renewal | "Thanks for staying with us! Share the love" | Day of renewal |
| Monthly digest | "Your referral status: [N] referrals, $[X] earned" | Monthly |

---

## Share Mechanics

### Share Channel Priority

| Channel | B2C Priority | B2B Priority | Implementation |
|---------|-------------|-------------|----------------|
| Email invite | High | Highest | Pre-filled email with referral link |
| Copy link | High | High | One-click copy with confirmation |
| Twitter/X | High | Medium | Pre-filled tweet with referral link |
| LinkedIn | Low | High | Pre-filled post with referral link |
| WhatsApp | High | Low | Deep link to WhatsApp with message |
| Slack/Teams | Low | High | Integration or copyable message |
| SMS | Medium (mobile) | Low | Pre-filled text message |

### Share Message Templates

**Email (B2B):**
```
Subject: I think you'd like [Product]

Hey [Name],

I've been using [Product] for [task/workflow] and it's saved me [specific benefit].
Thought you might find it useful too.

Here's my referral link -- you'll get [referred benefit] when you sign up:
[Referral Link]

[Referrer Name]
```

**Social (B2C):**
```
Been using [Product] for [timeframe] and I'm genuinely impressed.
[Specific thing I love about it].

If you want to try it, use my link and we both get [reward]:
[Referral Link]
```

---

## Referred User Experience

### Referral Landing Page

```
┌──────────────────────────────────────────┐
│  [Referrer Name] invited you to          │
│  [Product]                               │
│                                          │
│  [Referrer's photo if available]         │
│                                          │
│  Your reward: [Incentive details]        │
│                                          │
│  [Sign Up and Claim Your Reward]         │
│                                          │
│  What [Product] does:                    │
│  - Benefit 1                            │
│  - Benefit 2                            │
│  - Benefit 3                            │
│                                          │
│  "Quote from a customer"                │
└──────────────────────────────────────────┘
```

### Attribution Rules

| Scenario | Attribution |
|----------|-----------|
| User clicks link and signs up same session | Attributed to referrer |
| User clicks link, returns 3 days later, signs up | Attributed (30-day cookie) |
| User clicks link but signs up via Google search | Attributed if within cookie window |
| User receives two referral links from different people | First click wins (or last click -- choose one rule) |
| Referred user was already a lead in CRM | Exclude from referral program |

---

## Viral Coefficient Modeling

### K-Factor Calculation

```
K = i x c

i = average invitations sent per user
c = conversion rate of invitations

Example:
  Average user sends 3 invitations
  15% of those invitations convert
  K = 3 x 0.15 = 0.45

K > 1.0 = viral growth (rare outside social products)
K = 0.3-0.7 = strong referral contribution
K < 0.1 = referral program needs work
```

### Improving K-Factor

| Lever | Current | Target | Action |
|-------|---------|--------|--------|
| Increase i (invitations sent) | Low awareness | More users see the program | Improve trigger moments and visibility |
| Increase i (invitations sent) | Users see it but do not share | Make sharing easier | Improve share mechanics, better messaging |
| Increase c (conversion rate) | Users share but invites do not convert | Improve referred landing page | Personalize, add incentive, reduce friction |

---

## Affiliate Program Framework

### Program Structure

| Element | Recommendation |
|---------|---------------|
| Commission model | 20-30% recurring for SaaS, or flat fee per conversion |
| Cookie window | 30 days minimum, 90 days for B2B |
| Payment terms | Monthly, $50 minimum threshold |
| Payment method | PayPal, wire transfer, or affiliate platform payout |
| Tracking platform | PartnerStack, Impact, Rewardful, or custom |

### Affiliate Tier System

| Tier | Criteria | Commission | Benefits |
|------|----------|-----------|----------|
| Standard | Default | 20% recurring | Basic assets, self-serve |
| Silver | 10+ conversions | 25% recurring | Priority support, custom assets |
| Gold | 25+ conversions | 30% recurring | Dedicated manager, co-marketing |
| Strategic | Custom agreement | Custom | Custom terms, revenue share |

### Affiliate Toolkit

Every affiliate needs:

- [ ] Unique tracking link
- [ ] Pre-written email copy (3 variants)
- [ ] Social media copy (Twitter, LinkedIn)
- [ ] Banner ads (3 sizes minimum)
- [ ] Product description sheet (features, benefits, pricing)
- [ ] Comparison table (vs competitors)
- [ ] Landing page optimized for affiliate traffic

### Affiliate Recruitment

| Source | Approach | Volume |
|--------|---------|--------|
| Existing customers (top advocates) | Personal outreach | 10-20 initial |
| Complementary SaaS companies | Partnership pitch | 5-10 |
| Industry bloggers/creators | Outreach with product demo | 10-20 |
| Newsletter curators | Sponsorship conversion to affiliate | 5-10 |
| Review sites | Listing with affiliate link | Ongoing |

**Recruitment rule:** Personalized outreach only. Generic "join our affiliate program" emails convert at < 1%.

---

## Optimization Playbook

### Diagnose Before Optimizing

| Metric | Benchmark | If Below | Fix |
|--------|-----------|----------|-----|
| Program awareness | > 40% of active users know it exists | Promote in-app, post-activation emails, dashboard widget |
| Active referrers | 5-15% of active users | Improve trigger moments, timing, and incentive |
| Share rate | 20-40% of those who see the prompt | Simplify share flow, improve message copy |
| Referred conversion rate | 15-25% | Improve referral landing page, add incentive |
| Reward redemption | > 70% within 30 days | Reduce redemption friction, send reminders |

### Optimization Priority

1. **Fix awareness first** -- If users do not know the program exists, nothing else matters
2. **Fix the share flow** -- If users know but do not share, the friction is too high
3. **Fix the referred experience** -- If users share but referrals do not convert, the landing page fails
4. **Optimize the incentive** -- Only change the reward after the mechanics work

---

## Metrics and Benchmarks

### Key Metrics

| Metric | Formula | Target |
|--------|---------|--------|
| Referral rate | Referrals sent / Active users | 5-15% |
| Active referrers % | Users who sent 1+ referral / Active users | 5-15% |
| Referral conversion rate | Referred signups / Referrals sent | 15-25% |
| Referral CAC | Total reward cost / Referral-acquired customers | < 50% of other CAC |
| Referral revenue % | Revenue from referred customers / Total revenue | 10-25% |
| K-factor | Invitations per user x Conversion rate | 0.3-0.7 |
| Referred customer LTV | LTV of referred vs non-referred | Referred should be higher |

### Revenue Impact Model

```
Monthly referral revenue = Active users x Referral rate x Conversion rate x ACV / 12

Example:
  10,000 active users x 10% referral rate x 20% conversion rate x $600 ACV / 12
  = $10,000/month in new referral-driven MRR

  Annual impact: $120,000 in new ARR
  Reward cost (at $50/referral): 200 referrals x $50 = $10,000
  ROI: 12x return on reward investment
```

---

## Program Copy Templates

### In-App Prompt

```
Know someone who'd love [Product]?

Give [reward], Get [reward]

Share your unique link and you'll both get [reward] when they sign up.

[Share Now]  [Learn More]
```

### Referral Dashboard

```
Your Referral Stats

Referrals Sent: [N]
Friends Joined: [N]
Rewards Earned: $[X]

[Share Your Link]

Your link: [referral-url]  [Copy]

Progress to next reward:
[Progress bar: 2 of 3 referrals for Silver tier]
```

### Referral Email (Post-Activation)

```
Subject: Share [Product] and earn [reward]

Hi [Name],

Glad you're enjoying [Product]!

Share your personal referral link with colleagues, and you'll both get [reward]:

[Referral Link]

So far, you've earned $[X] from [N] referrals.

[Share Now]
```

---

## Output Artifacts

| Artifact | Format | Description |
|----------|--------|-------------|
| Referral Program Design | Full spec | Loop design, incentive structure, trigger moments, share mechanics |
| Incentive ROI Model | Revenue calculation | Reward sizing against LTV/CAC with multiple scenarios |
| Program Copy Set | Complete copy | In-app prompts, emails, share messages, landing page |
| Affiliate Program Spec | Structure + toolkit | Commission model, tiers, recruitment list, partner assets |
| K-Factor Model | Calculation + improvement plan | Current K, target K, lever-by-lever improvement plan |
| Optimization Audit | Metric scorecard | Current metrics vs benchmarks with prioritized fixes |
| Dashboard Specification | UI design | Referral stats, link sharing, progress tracking |

---

## Tool Reference

### 1. referral_economics_calculator.py

Calculates referral program economics including reward sizing, K-factor, referral CAC, ROI projections, and break-even analysis. Models double-sided vs single-sided reward structures.

```bash
python scripts/referral_economics_calculator.py program.json --format text
python scripts/referral_economics_calculator.py program.json --format json
```

| Flag | Type | Description |
|------|------|-------------|
| `program.json` | positional | Path to JSON file with program economics data |
| `--format` | optional | Output format: `text` (default) or `json` |

### 2. referral_funnel_analyzer.py

Analyzes the 4-stage referral loop (trigger, share, convert, reward) with stage-over-stage conversion, identifies the weakest stage, and provides prioritized improvement recommendations.

```bash
python scripts/referral_funnel_analyzer.py funnel.json --format text
python scripts/referral_funnel_analyzer.py funnel.json --format json
```

| Flag | Type | Description |
|------|------|-------------|
| `funnel.json` | positional | Path to JSON file with referral funnel metrics |
| `--format` | optional | Output format: `text` (default) or `json` |

### 3. affiliate_commission_modeler.py

Models affiliate program commission structures across tier levels. Calculates per-tier economics, lifetime partner value, and compares commission models (flat fee vs recurring percentage).

```bash
python scripts/affiliate_commission_modeler.py affiliate.json --format text
python scripts/affiliate_commission_modeler.py affiliate.json --format json
```

| Flag | Type | Description |
|------|------|-------------|
| `affiliate.json` | positional | Path to JSON file with affiliate program data |
| `--format` | optional | Output format: `text` (default) or `json` |

---

## Troubleshooting

| Problem | Likely Cause | Resolution |
|---------|-------------|------------|
| Program awareness below 40% of active users | Referral program is buried in settings or only mentioned in email footers | Add persistent dashboard widget, post-activation prompt, and post-NPS trigger; desktop sharing now outperforms mobile (2026 data) |
| Users see prompt but share rate is below 20% | Share flow has too much friction or pre-filled message is not compelling | Add one-click copy link, native share sheet on mobile, pre-filled first-person message; ensure multiple channels (email, Slack, social) |
| Referrals sent but conversion rate below 15% | Referral landing page lacks personalization or incentive is not prominent | Add referrer name/photo, display incentive above fold, reduce signup friction; mobile-referred users convert 2-3x (2026 data) |
| K-factor below 0.1 | Fundamental program design issue -- either low awareness, high friction, or weak incentive | Diagnose in sequence: fix awareness first, then share flow, then landing page, then incentive (optimize mechanics before rewards) |
| Reward redemption below 70% | Reward delivery is delayed or redemption process is complicated | Auto-apply credits immediately, send instant notification, make redemption one-click; show running total in dashboard |
| Referred customers churn faster than organic | Referral incentive attracts low-intent users or onboarding for referred users is inadequate | Shift from cash/discount rewards to product-value rewards (feature unlock, extended trial); add referred-user onboarding path |
| Affiliate partners not producing conversions | Partners lack proper toolkit or audience mismatch | Provide pre-written copy, banner assets, comparison tables, and dedicated landing pages; audit partner audience fit |

---

## Success Criteria

- K-factor reaches 0.3-0.7 range within 90 days of program launch (strong referral contribution without requiring virality)
- Referral CAC is below 50% of other acquisition channel CAC
- Active referrer percentage reaches 5-15% of active users
- Referral-sourced revenue contributes 10-25% of total new revenue within 6 months
- Referred customer LTV exceeds non-referred customer LTV (typical: 16-25% higher per industry data)
- Reward redemption rate exceeds 70% within 30 days of earning
- Double-sided program achieves 2x+ conversion rate compared to single-sided (validate within first 1,000 referrals)

---

## Scope & Limitations

**In scope:** Customer referral program design (4-stage loop), incentive structure (single-sided, double-sided, tiered), trigger moment architecture, share mechanics, referral landing page specifications, viral coefficient modeling, affiliate program framework (commission models, tier systems, recruitment), and systematic optimization playbook.

**Out of scope:** Referral landing page visual design and CRO (use page-cro), signup flow optimization for referred users (use signup-flow-cro), post-signup onboarding for referred users (use onboarding-cro), churn prevention for referred customers (use churn-prevention), and reward pricing alignment (use pricing-strategy). Scripts operate on local data only -- no integrations with referral platforms (ReferralHero, Viral Loops, PartnerStack, etc.).

**Limitations:** K-factor benchmarks assume consumer or prosumer SaaS; B2B enterprise referral programs have different dynamics (lower K but higher per-referral value). Affiliate commission benchmarks (20-30% recurring) are SaaS-specific; marketplace and e-commerce commissions follow different models. Attribution windows (30-90 day cookies) face increasing limitations from browser privacy features (Safari ITP, Chrome third-party cookie deprecation). Revenue projections are estimates based on provided conversion rates.

---

## Integration Points

- **pricing-strategy** -- Referral reward sizing must align with pricing margins and LTV; reward should be <30% of first payment
- **signup-flow-cro** -- Referred user signup flow should pre-fill email, show referrer context, and minimize friction
- **onboarding-cro** -- Referred users may need different onboarding path (they arrive with context from the referrer)
- **churn-prevention** -- Monitor referred customer retention separately; high referral churn wastes acquisition spend
- **page-cro** -- Referral landing page conversion optimization follows page-cro methodology
- **popup-cro** -- Post-purchase or post-milestone popups are natural referral trigger points

---

## Related Skills

- **pricing-strategy** -- Use when referral reward sizing needs to align with pricing and margin structure.
- **signup-flow-cro** -- Use for optimizing the signup flow that referred users go through.
- **onboarding-cro** -- Use for optimizing the post-signup experience for referred users.
- **churn-prevention** -- Use to ensure referred customers retain at high rates (referral CAC is wasted if they churn).
- **page-cro** -- Use for optimizing the referral landing page conversion rate.
