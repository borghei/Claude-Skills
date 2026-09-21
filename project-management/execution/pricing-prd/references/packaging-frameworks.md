# Packaging Frameworks

Packaging is the decision about which features belong to which tier, what is included by default, what is a paid add-on, and where the boundaries fall. Pricing is the number on each tier; packaging is the shape of the offering. Most companies treat packaging as the easier of the two — and lose far more revenue to bad packaging than to bad pricing.

This guide synthesizes Madhavan Ramanujam's *Monetizing Innovation*, Hermann Simon's *Confessions of the Pricing Man*, and Stripe's documented patterns.

## The packaging decision

Packaging answers four questions:

1. **What are the tiers?** Free / Starter / Pro / Enterprise — or some other shape.
2. **What is the value carrier in each tier?** The headline feature(s) that justify the price.
3. **Where are the boundaries?** Which feature or limit moves a customer from one tier to the next.
4. **What is the upgrade path?** What triggers a customer to move up.

Bad packaging shows up as:

- Customers using Pro but not because of the Pro headline features
- The middle tier outselling the top tier by a wide margin (under-priced top tier)
- The middle tier almost empty (gap too large)
- Customers asking "what do I get if I upgrade?" (value carrier unclear)

## Good / Better / Best (the three-tier default)

The most common SaaS packaging shape. Works well for predictable B2B value and customers who self-select by maturity.

| Tier | Customer archetype | Value carrier example (analytics) |
|---|---|---|
| **Good** (Starter) | Solo, SMB | Core dashboards, 1 user, 30-day data retention |
| **Better** (Pro) | Growing team | Custom dashboards, unlimited users, 1-year retention, integrations |
| **Best** (Enterprise) | Scaling org | SSO, audit logs, dedicated support, custom retention, contract terms |

Ramanujam's "value gap" principle: each tier should be 2-3x the price of the one below AND deliver 3-5x the value. The tier-to-tier upgrade should feel obvious.

### Common mistake

The middle tier is the highest-revenue tier in many SaaS products because of choice psychology (compromise effect). Packaging should be designed deliberately around this — putting the value-generating features in the middle tier, with the top tier reserved for differentiating capabilities that justify a step-change.

## Per-seat

Pricing per user. Common in collaboration tools (Slack, Notion, Linear, Figma).

| Pros | Cons |
|---|---|
| Predictable revenue per customer | Discourages adoption — every new user has a cost |
| Scales naturally with customer success | Bottoms out for solo users |
| Easy to explain | Mismatched to AI/automation products where value doesn't scale with seats |

**When per-seat fits:** the product's value primarily comes from human collaboration (more humans → more value).

**When per-seat doesn't fit:** the product's value comes from AI inference, data processing, or automation that operates independently of seat count.

### Per-seat + minimum seat count

A common variant for B2B: per-seat with a minimum (e.g. "$10/seat/month, min 5 seats = $50/month floor"). This protects against tiny accounts and signals SMB-or-larger positioning.

## Usage-based

Pricing per API call, per GB, per event, per transaction. Common in infrastructure (Twilio, Stripe, AWS) and AI (OpenAI, Anthropic).

| Pros | Cons |
|---|---|
| Value alignment — customers pay for what they get | Revenue volatility |
| Low barrier to entry (small users pay small bills) | Bill-shock risk — customers receive surprise charges |
| Scales beautifully for cloud-economics products | Hard to forecast |

### Usage-based design considerations

- **Free tier / minimum**: most usage-based products include a free tier or monthly minimum to set expectations.
- **Pre-paid vs post-paid**: pre-paid (commit + overage) gives revenue predictability; post-paid (pure metered) gives customer flexibility.
- **Spend caps**: customers should be able to set a cap to prevent runaway bills.
- **Alerting**: notify customers as they approach tier thresholds.
- **Reasonable rounding**: rounding API calls to the nearest 1000 is fine; rounding to the nearest million is hostile.

## Hybrid (platform fee + usage)

A platform / subscription fee for access plus usage charges for variable consumption. Examples: Twilio's account fee + per-message, Stripe's subscription tools + per-transaction.

| Pros | Cons |
|---|---|
| Revenue floor (platform fee) + upside (usage) | Complex to communicate |
| Fits products with mixed value drivers | Customers struggle to forecast their cost |
| Common in 2024-2026 SaaS | Risk of double-charge perception |

The hybrid model is increasingly common as products bundle AI features (per-call usage) into a flat-fee SaaS surface.

## Outcome-based

The vendor charges based on measurable customer outcomes (revenue lift, leads generated, hours saved). Examples are rarer because of measurement difficulty.

| Pros | Cons |
|---|---|
| Strongest value alignment | Hard to define and audit outcomes |
| Differentiates the seller (confidence signal) | Vendor exposed to customer's implementation quality |
| Highest contract values when it works | Long sales cycles; legal complexity |

Outcome-based works in narrow domains where the outcome is unambiguous (e.g. "leads generated and accepted into CRM") and where the vendor has high confidence in producing it.

## Mixing models within a product

Most SaaS products mix at least two models:

- A subscription tier for the platform (per-seat or per-account)
- A usage-based meter on a specific feature (AI calls, storage, exports)
- Add-on subscriptions for specific capabilities (advanced security, dedicated support)

The complexity grows quickly. The packaging discipline is to keep the pricing page simple (the page can show the headline subscription) while the actual billing supports the multi-model reality.

## The Ramanujam packaging principles (synthesized)

From *Monetizing Innovation*, applied to SaaS:

1. **Design around the price, not the price around the product.** Decide what customers will pay before deciding what to build. Build to that price.
2. **Segment first, package second.** Different customer segments need different packages. A one-size product is rare.
3. **Find the willingness-to-pay band per segment.** Use Van Westendorp or conjoint.
4. **Don't undercharge for the entry tier.** A free or near-free tier should be designed to convert, not to be the destination.
5. **Make the value carrier of each tier obvious.** Customers should not need to read a comparison table to understand the upgrade.
6. **Avoid more than 4 tiers on the page.** Choice paralysis at 5+. If you need 7 SKUs, hide some behind sales.

## The "trial" decision

| Trial mechanism | When it fits |
|---|---|
| **Free tier** (always free, feature-limited) | Self-serve product, viral adoption potential, freemium economics |
| **Time-bounded trial** (14 or 30 days) | Mid-market and enterprise B2B; trial-to-paid funnel optimization |
| **Reverse trial** (start full-featured, downgrade after period) | Conversion-optimized; customers experience the full product before paying |
| **Sales-led trial** (no public trial, customer must talk to sales) | Enterprise; complex products needing implementation support |

Reverse trial is the rising pattern in 2024-2026: customers see what they would lose at downgrade, not what they would gain at upgrade — and loss-aversion drives conversion.

## Common packaging traps

| Trap | Description | Fix |
|---|---|---|
| **The "death star" Enterprise tier** | Top tier includes 30+ features; customers can't tell what they're paying for | Pick 3-5 headline differentiators; hide the long tail in a feature list |
| **The "rebranded Free" Pro tier** | The Pro tier is Free + minor convenience features | Add genuine value — typically integrations, automation, or seat scaling |
| **The arbitrary boundary** | A feature is in Pro but the customer can't tell why | Boundaries should map to a measurable customer characteristic (seats, volume, support level) |
| **The 5-tier page** | Tier overload | Collapse to 3-4 on the page; offer custom for >Pro needs |
| **Identical pricing pages across segments** | One page for SMB and enterprise | Build a dedicated enterprise surface (often "Contact sales") |
| **No anchor tier** | All tiers feel reasonably-priced; no "expensive" option to anchor | Add a higher-priced tier even if few buy it — it shifts perception of the rest |
| **Pricing the lowest tier at the cost-of-fulfillment** | Floor price covers your cost but ignores customer willingness | Test the floor; many customers would pay more for the entry tier |

## Migrating between packaging models

Migrating from per-seat to per-usage (or vice versa) is one of the most disruptive pricing changes. Considerations:

- **Communicate early and clearly.** Customers need 60-90 days to adjust expectations and budgets.
- **Grandfather extensively.** Existing customers should be able to stay on the old model for at least 12 months.
- **Run side-by-side pricing for new customers** for a transition period to compare conversion.
- **Build the calculator.** Customers need a "what would my bill look like under the new model?" tool.
- **Train sales and support.** Both teams will face customer questions for months.

## See also

- `references/pricing-experimentation-guide.md` — for A/B-testing the packaging decisions
- `assets/pricing_prd_template.md` — the 13-section PRD
- `business-growth/pricing-strategy/` — strategic-level decisions that precede packaging

## References

- Madhavan Ramanujam & Georg Tacke, *Monetizing Innovation* (2016)
- Hermann Simon, *Confessions of the Pricing Man* (2015)
- Stripe Atlas, "Pricing" guide — https://stripe.com/atlas/guides/pricing
