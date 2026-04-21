# Referral Program Design Guide

Detailed reference material for designing and implementing referral and affiliate programs.

## Tiered Rewards (Gamification)

| Tier | Reward | Design Rule |
|------|--------|-------------|
| 1 referral | $20 credit | Easy to reach, immediate gratification |
| 3 referrals | $75 credit + bonus feature | Meaningful step-up, not just 3x |
| 10 referrals | $300 cash + ambassador status | Significant reward, social recognition |

**Rules:** Maximum 3 tiers. Each tier should feel meaningfully better, not just marginally. Show progress toward next tier in the dashboard.

## In-Product Trigger Points

| Location | Trigger Type | Copy Example |
|----------|-------------|-------------|
| Dashboard widget | Persistent, low-key | "Know someone who'd love [Product]? Give $20, get $20" |
| Post-milestone modal | Celebration moment | "You just hit 1,000 contacts! Share [Product] with a colleague?" |
| Settings/account page | Always available | "Referral Program: Earn $20 for every friend who joins" |
| Success state | After positive outcome | "Great results! Know someone who'd find this useful?" |
| Team invite flow | Natural sharing moment | "Or invite them via referral link and you both get $20" |

## Email Trigger Points

| Trigger | Email Content | Timing |
|---------|-------------|--------|
| Post-activation | "Loving [Product]? Share it and earn rewards" | 3-5 days after activation |
| Post-NPS (score 9-10) | "Glad you love us! Here's an easy way to share" | Immediately after NPS |
| Post-renewal | "Thanks for staying with us! Share the love" | Day of renewal |
| Monthly digest | "Your referral status: [N] referrals, $[X] earned" | Monthly |

## Share Channel Priority

| Channel | B2C Priority | B2B Priority |
|---------|-------------|-------------|
| Email invite | High | Highest |
| Copy link | High | High |
| Twitter/X | High | Medium |
| LinkedIn | Low | High |
| WhatsApp | High | Low |
| Slack/Teams | Low | High |

## Share Message Templates

**Email (B2B):**
```
Subject: I think you'd like [Product]

Hey [Name],

I've been using [Product] for [task/workflow] and it's saved me [specific benefit].
Thought you might find it useful too.

Here's my referral link — you'll get [referred benefit] when you sign up:
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

## Referral Landing Page Specification

Required elements:
- Referrer name and photo (if available)
- Incentive details displayed above the fold
- Simplified signup (pre-fill email, offer SSO)
- Product benefits (3 bullet points)
- Customer testimonial

## Attribution Rules

| Scenario | Attribution |
|----------|-----------|
| Clicks link and signs up same session | Attributed to referrer |
| Clicks link, returns 3 days later | Attributed (30-day cookie) |
| Clicks link but signs up via Google search | Attributed if within cookie window |
| Two referral links from different people | First click wins |
| Already a lead in CRM | Exclude from referral program |

## Affiliate Program Structure

| Element | Recommendation |
|---------|---------------|
| Commission model | 20-30% recurring for SaaS, or flat fee per conversion |
| Cookie window | 30 days minimum, 90 days for B2B |
| Payment terms | Monthly, $50 minimum threshold |

### Affiliate Tier System

| Tier | Criteria | Commission |
|------|----------|-----------|
| Standard | Default | 20% recurring |
| Silver | 10+ conversions | 25% recurring |
| Gold | 25+ conversions | 30% recurring |
| Strategic | Custom agreement | Custom |

### Affiliate Toolkit Checklist

Every affiliate needs:
- Unique tracking link
- Pre-written email copy (3 variants)
- Social media copy (Twitter, LinkedIn)
- Banner ads (3 sizes minimum)
- Product description sheet
- Comparison table (vs competitors)
- Landing page optimized for affiliate traffic

### Affiliate Recruitment

| Source | Approach | Volume |
|--------|---------|--------|
| Existing customers (top advocates) | Personal outreach | 10-20 initial |
| Complementary SaaS companies | Partnership pitch | 5-10 |
| Industry bloggers/creators | Outreach with product demo | 10-20 |

**Rule:** Personalized outreach only. Generic "join our affiliate program" emails convert at < 1%.

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
Referrals Sent: [N]  |  Friends Joined: [N]  |  Rewards Earned: $[X]
[Share Your Link]
Your link: [referral-url]  [Copy]
Progress to next reward: [Progress bar: 2 of 3 referrals for Silver tier]
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

## Revenue Impact Model

```
Monthly referral revenue = Active users × Referral rate × Conversion rate × ACV / 12

Example:
  10,000 active users × 10% × 20% × $600 ACV / 12 = $10,000/month new MRR
  Annual impact: $120,000 in new ARR
  Reward cost (at $50/referral): 200 × $50 = $10,000
  ROI: 12x return on reward investment
```
