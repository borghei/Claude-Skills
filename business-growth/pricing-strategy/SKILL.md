---
name: pricing-strategy
description: SaaS pricing design and optimization covering value metric selection, tier architecture, price point research, pricing page design, price increase execution, and competitive pricing analysis.
version: 1.0.0
author: borghei
category: business-growth
tags: [pricing, monetization, packaging, saas, value-based-pricing, revenue]
triggers:
  - user wants to design or redesign pricing
  - user mentions pricing tiers, packaging, or value metric
  - user asks about price increase strategy
  - user mentions pricing page optimization or conversion
  - user asks about per-seat, usage-based, or flat-rate pricing
  - user mentions freemium vs free trial decision
  - user reports high trial-to-paid conversion (possible underpricing signal)
---

# Pricing Strategy

Production-grade SaaS pricing framework covering the three pricing axes (value metric, packaging, price point), value-based pricing methodology, tier architecture, pricing research methods, pricing page design, price increase execution, and competitive pricing positioning. Pricing is positioning -- the right price communicates as much about your product as your marketing does.

---

## Table of Contents

- [Operating Modes](#operating-modes)
- [The Three Pricing Axes](#the-three-pricing-axes)
- [Value Metric Selection](#value-metric-selection)
- [Tier Architecture](#tier-architecture)
- [Value-Based Pricing](#value-based-pricing)
- [Pricing Research Methods](#pricing-research-methods)
- [Pricing Page Design](#pricing-page-design)
- [Price Increase Playbook](#price-increase-playbook)
- [Freemium vs Free Trial Decision](#freemium-vs-free-trial-decision)
- [Competitive Pricing Analysis](#competitive-pricing-analysis)
- [Pricing Signals and Diagnostics](#pricing-signals-and-diagnostics)
- [Output Artifacts](#output-artifacts)
- [Related Skills](#related-skills)

---

## Operating Modes

### Mode 1: Design From Scratch
No pricing exists or full rebuild needed. Work through value metric, tier structure, price points, and page design.

### Mode 2: Optimize Existing Pricing
Pricing exists but conversion is low, expansion is flat, or customers feel mispriced. Audit, benchmark, and identify specific improvements.

### Mode 3: Price Increase
Prices need to go up. Design a strategy that increases revenue without burning customer relationships.

---

## The Three Pricing Axes

Every pricing decision lives across three axes. Most teams skip to price point. That is backwards.

```
     ┌──────────────────┐
     │   VALUE METRIC    │  What do you charge for?
     │  (how it scales)  │  (per seat, per usage, per feature)
     └────────┬─────────┘
              │
     ┌────────┴─────────┐
     │   PACKAGING       │  What is in each tier?
     │  (what you get)   │  (feature bundles, limits, support levels)
     └────────┬─────────┘
              │
     ┌────────┴─────────┐
     │   PRICE POINT     │  How much?
     │  (the number)     │  (actual dollar amount)
     └──────────────────┘
```

Lock in the value metric first, then packaging, then test the price point.

---

## Value Metric Selection

### Common Value Metrics

| Metric | Best For | Examples | Scales With Value? |
|--------|---------|---------|-------------------|
| Per seat / user | Collaboration tools, CRMs | Salesforce, Notion, Linear | Yes if all users are active |
| Per usage | APIs, infrastructure, AI | Stripe, Twilio, OpenAI | Yes |
| Per feature | Platform plays, modular products | HubSpot, Intercom | Somewhat |
| Flat fee | Simple products, SMB market | Basecamp, Calendly | No (subsidizes heavy users) |
| Per outcome | Measurable ROI products | Commission-based tools | Perfectly |
| Hybrid | Most mature SaaS | Base fee + usage, seat + features | Yes |

### Selection Criteria

Answer these 4 questions:

| Question | Answer Points To |
|----------|-----------------|
| What makes a customer willing to pay MORE? | That is your value metric |
| Does the metric scale with their success? | If they grow, you should grow |
| Is it easy to understand? | Complexity kills conversion |
| Is it hard to game? | Customers should not be able to work around it |

### Value Metric Red Flags

| Red Flag | Problem | Fix |
|---------|---------|-----|
| Per-seat in a tool where 1 power user does all the work | Seats do not scale with value | Switch to usage or feature-based |
| Flat fee when some customers get 10x the value of others | Subsidizing heavy users | Add usage tiers or hybrid model |
| Per-API-call when volume varies wildly week to week | Unpredictable bills cause churn | Add usage bands or committed minimums |
| Per-feature when core value requires multiple features | Nickel-and-diming perception | Bundle core features, gate advanced only |

---

## Tier Architecture

### Good-Better-Best (3 Tiers)

Three tiers is the standard because it anchors perception.

| Tier | Role | Pricing Rule | Feature Rule |
|------|------|-------------|-------------|
| Entry (Good) | Captures price-sensitive segment | Covers your costs minimum | Core product, limited usage |
| Middle (Better) | Where you push most customers | 2-3x entry tier | Everything a growing company needs |
| Top (Best) | High-value enterprise customers | 3-5x entry or custom | SSO, audit logs, SLA, dedicated support |

### Feature Allocation Framework

| Feature Category | Entry Tier | Middle Tier | Top Tier |
|-----------------|-----------|------------|---------|
| Core product | Limited | Full | Full |
| Usage limits | Low | Medium | High/Unlimited |
| Users/seats | 1-3 | 5-25 or unlimited | Unlimited |
| Integrations | Basic (3-5) | Full | Full + custom |
| Reporting | Basic | Advanced | Custom |
| Support | Email (48h) | Priority (24h) | Dedicated CSM |
| Admin features | -- | -- | SSO, SCIM, audit logs |
| SLA | -- | -- | 99.9% uptime |
| Data retention | 90 days | 1 year | Unlimited |
| API access | -- | Rate-limited | Full |

### Tier Naming

| Approach | Examples | Best For |
|----------|---------|---------|
| Size-based | Starter, Growth, Enterprise | Universal SaaS |
| Capability-based | Basic, Pro, Enterprise | Feature-differentiated products |
| Audience-based | Individual, Team, Organization | Collaboration tools |
| Persona-based | Freelancer, Agency, Enterprise | Audience-segmented products |

**Naming rules:**
- Names should be instantly understandable
- Avoid jargon or made-up words
- The default/recommended plan should be visually highlighted

---

## Value-Based Pricing

### The Pricing Corridor

```
[Cost floor] ... [Next-best alternative] ... [YOUR PRICE] ... [Perceived value]
```

### Step-by-Step

**Step 1: Define the next-best alternative**
- What would the customer do without your product?
- What does that cost them? (competitor, manual process, hiring)

**Step 2: Estimate value delivered**
- Time saved x hourly rate of the person using it
- Revenue generated or protected
- Cost of errors/risk avoided
- Ask customers: "What would you lose if you stopped using us?"

**Step 3: Price in the corridor**
- Price at 10-20% of documented value delivered
- Above the next-best alternative (signals confidence)
- Below the perceived value ceiling (customer feels good ROI)

### Conversion Rate as a Pricing Signal

| Trial-to-Paid Rate | Signal | Action |
|-------------------|--------|--------|
| > 40% | Likely underpriced | Test a 20-30% price increase |
| 15-30% | Healthy for most SaaS | Optimize packaging, not price |
| < 10% | Possibly overpriced OR trial experience is broken | Investigate whether the issue is price or activation |

---

## Pricing Research Methods

### Van Westendorp Price Sensitivity Meter

Four questions asked to 30+ current customers or qualified prospects:

1. At what price would this be so cheap you would question its quality?
2. At what price would this be a great deal?
3. At what price would this start to feel expensive but still acceptable?
4. At what price would this be too expensive to consider?

**Interpretation:** Plot four curves. The intersection of "too cheap" and "too expensive" gives the acceptable range. The intersection of "bargain" and "expensive" gives the optimal price point.

### MaxDiff Analysis

Show respondents sets of features and ask which they value most and least. Reveals relative value of each feature for tier allocation decisions.

**When to use:** Deciding which features go in which tier.

### Competitor Benchmarking

| Step | Action |
|------|--------|
| 1 | List direct competitors and alternatives customers compare you to |
| 2 | Record published pricing (plans, prices, value metrics) |
| 3 | Note what is included at each tier |
| 4 | Identify where you over-deliver and under-deliver vs each |
| 5 | Position relative to market: premium (+20-40%), parity, value (-10-20%) |

**Do not copy competitor prices.** Their pricing reflects their cost structure and positioning, not yours.

### Customer Willingness-to-Pay Interview

Ask existing customers (especially champions):
- "How would you describe the ROI of [product] to your CFO?"
- "What would you do if the price doubled? Tripled?"
- "What is the most you would pay before you would switch?"
- "If you had to cut 50% of your budget, would this survive?"

---

## Pricing Page Design

### Above the Fold

**Required elements:**
- Plan names with clear positioning
- Prices with monthly/annual toggle (annual shows savings: "Save 20%" or "2 months free")
- 3-5 bullet differentiators per plan
- CTA button per plan
- "Most Popular" or "Recommended" badge on the middle tier
- "Most Popular" plan should be the default tab/column

### Below the Fold

- **Full feature comparison table** -- Comprehensive, scannable, uses checkmarks and X marks
- **FAQ section** -- The 5 objections that stop purchases:
  1. "Can I cancel anytime?"
  2. "What happens when I hit limits?"
  3. "Do you offer refunds?"
  4. "Is my data secure?"
  5. "Can I switch plans later?"
- **Social proof** -- Logos, testimonials, case studies relevant to each tier
- **Security badges** -- SOC2, ISO 27001, GDPR (if applicable)

### Annual vs Monthly Toggle

- Default to showing annual pricing (it improves LTV)
- Show savings explicitly: "Save 20%" or "$X/year (saves $Y)"
- Do NOT hide monthly pricing -- hiding it creates distrust
- Monthly/annual toggle should be above the plan cards

### Enterprise Tier Design

| Approach | When to Use |
|----------|-------------|
| Published price | When enterprise pricing is standardized |
| "Contact Sales" | When pricing requires custom scoping |
| "Starting at $X" | Balance transparency with flexibility |

---

## Price Increase Playbook

### Strategy Selection

| Strategy | Risk Level | Use When |
|---------|-----------|---------|
| New customers only | Low | Testing market response, significant uncertainty |
| Grandfather + scheduled increase | Medium | Loyal customer base, want to preserve relationships |
| Tied to new value | Low | Clear product improvements justify the increase |
| Plan restructure | Medium | Packaging changes alongside price changes |
| Uniform increase | Medium-High | Price is clearly below market, confident in value |

### Execution Timeline

| Week | Action |
|------|--------|
| Week -12 | Decide strategy, model revenue impact at 80%, 90%, 100% retention |
| Week -8 | Segment customers by risk (annual contracts, champions vs detractors, usage level) |
| Week -6 | Prepare communication (email, in-app, FAQ, CS talking points) |
| Week -4 | Announce to existing customers (60+ day notice for annual contracts) |
| Week -4 | Offer lock-in: "Keep current price for 12 months with annual commitment" |
| Week 0 | New pricing goes live for new customers |
| Week +4 | Existing customer pricing changes (if not grandfathered) |
| Week +12 | Review: churn rate, downgrade rate, support ticket volume, revenue impact |

### Communication Template

Subject: "Changes to your [Product] plan"

- Paragraph 1: What is changing and when
- Paragraph 2: Why (new features, investment in X, market alignment)
- Paragraph 3: What this means for them specifically (old price -> new price)
- Paragraph 4: Options (lock in current price with annual, downgrade, contact support)
- CTA: "View your options" or "Talk to your account manager"

### Expected Impact

For a 20-30% price increase:
- Expected churn: 5-15% of affected customers
- Revenue impact: Net positive if churn < (increase % / (100% + increase %))
- Example: 25% increase is net positive if churn < 20%

---

## Freemium vs Free Trial Decision

| Factor | Freemium | Free Trial |
|--------|---------|------------|
| Product complexity | Simple, quick time-to-value | Complex, needs exploration |
| Network effects | Strong (value increases with users) | Weak |
| Market size | Very large TAM, need top-of-funnel | Focused market |
| Sales motion | Self-serve, product-led | Sales-assisted |
| Conversion rate target | 2-5% free-to-paid | 15-30% trial-to-paid |
| Revenue urgency | Can afford long payback | Need revenue sooner |

### Freemium Tier Design Rules

- Free tier must deliver real, ongoing value (not a crippled experience)
- The limit that triggers upgrade should be a natural success indicator
- Free users should be able to see what paid features look like (soft gates, previews)
- Do not remove value from free tier once established (erodes trust)

---

## Competitive Pricing Analysis

### Pricing Position Map

```
                    Premium ($$$)
                         │
                         │
     [Competitor B]      │    [Your Product?]
                         │
 Narrow ─────────────────┼──────────────────── Broad
 Feature Set             │                Feature Set
                         │
     [Competitor C]      │    [Competitor A]
                         │
                         │
                    Value ($)
```

### Positioning Strategy

| Your Position | Pricing Approach | Messaging |
|--------------|-----------------|-----------|
| Premium | 20-40% above market average | "The [category] built for teams that demand the best" |
| Value leader | At or slightly below market | "Enterprise features at [segment] prices" |
| Disruptor | Radically different model | "Why pay per seat? [Product] is [price] for unlimited users" |
| Challenger | Slightly below the leader | "Everything [Leader] does, at half the price" |

---

## Pricing Signals and Diagnostics

### Pricing Health Check

| Signal | Diagnosis | Action |
|--------|-----------|--------|
| Trial-to-paid > 40% | Underpriced | Test 20-30% increase |
| All customers on middle tier | No upsell path | Add enterprise features or higher tier |
| Customers never ask about price | Too cheap | Increase price |
| Churn rate > 5% monthly | Fix churn before pricing changes | Use churn-prevention first |
| Price unchanged for 2+ years | Inflation alone justifies 10-15% increase | Plan an increase |
| Only one pricing option | No anchoring, no upsell | Add tiers |
| Frequent discount requests | Possible overpricing or poor value communication | Audit value proposition |

---

## Output Artifacts

| Artifact | Format | Description |
|----------|--------|-------------|
| Pricing Strategy Document | Structured analysis | Value metric, packaging, price points with rationale |
| Tier Architecture | Feature allocation table | What goes in each tier with justification |
| Pricing Page Specification | Layout + copy | Above-fold design, feature table, FAQ, toggle behavior |
| Price Increase Plan | Timeline + communications | Strategy selection, rollout schedule, email templates |
| Competitive Pricing Analysis | Comparison table + position map | Market pricing landscape with positioning recommendation |
| Van Westendorp Survey | Question set + interpretation guide | Ready-to-deploy pricing research |
| Pricing Health Scorecard | Signal + diagnosis table | Current pricing health assessment with action items |

---

## Related Skills

- **page-cro** -- Use for optimizing the pricing page conversion rate (layout, CTA, social proof). Not for pricing structure or tier design.
- **churn-prevention** -- Use when churn is the underlying issue. Fix retention before raising prices.
- **competitive-teardown** -- Use for comprehensive competitive analysis. Feed teardown pricing data into this skill.
- **paywall-upgrade-cro** -- Use for in-app upgrade prompts and paywalls. Different from public pricing page design.
- **signup-flow-cro** -- Use for optimizing the signup flow that follows pricing page conversion.
