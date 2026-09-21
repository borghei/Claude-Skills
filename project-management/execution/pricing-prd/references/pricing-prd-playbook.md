# Pricing PRD Playbook

> Read this when authoring a pricing PRD end-to-end: structure, pricing-model decision, willingness-to-pay research, packaging, grandfathering, communication, A/B design, rollback, regional pricing, UX checklist, anti-patterns, workflow, tools, troubleshooting, and success criteria.

## Pricing PRD vs Feature PRD

A pricing PRD shares some sections with the standard 8-section PRD (`create-prd/`) but has critical additions:

| Section | Feature PRD | Pricing PRD |
|---|---|---|
| Summary | Same | Same |
| Background | Why now | Plus market context: competitor pricing moves, willingness-to-pay research |
| Objective | KRs (engagement, retention) | KRs explicitly named: ARPU, conversion rate, gross margin, churn |
| Market segments | JTBD-based | Plus willingness-to-pay band per segment |
| Solution | Features | Pricing model + packaging + page design |
| Release | T-shirt sizes | Cohort strategy, grandfathering, rollback, holdout |
| **NEW: Pricing model** | n/a | Tier/usage/hybrid decision with rationale |
| **NEW: Packaging** | n/a | What features in what tier, with rationale |
| **NEW: Grandfathering** | n/a | Existing customer treatment |
| **NEW: Communication plan** | n/a | Customer email, in-app, status page, sales enablement |
| **NEW: A/B design** | n/a | Test/control split, primary metric, MDE, holdout |
| **NEW: Rollback criteria** | n/a | Defined thresholds at which the rollout is reversed |
| **NEW: Regional pricing** | n/a | Currency, tax inclusion, PPP, compliance |

## Pricing Model Decision

### Tier vs Usage vs Hybrid

| Model | When it fits | Risks |
|---|---|---|
| **Tier (Good/Better/Best)** | Predictable value per customer, clear packaging boundaries, B2B sales-led motion | Cliffs at tier boundaries; customers downgrade rather than upgrade |
| **Usage-based** | Value scales with usage (API calls, GB, events), self-serve, technical buyer | Revenue unpredictability, billing surprises, customer churn from bill shock |
| **Hybrid (platform fee + usage)** | Multi-product, predictable platform value + variable feature value | Complexity in pricing communication; customers confused about expected cost |
| **Per-seat** | Collaboration product, value scales linearly with users | Discourages adoption (gating new users behind expansion); declining in 2025-2026 |
| **Outcome-based** | Vendor confident in measurable outcome (e.g. revenue lift, leads generated) | Hard to define; risk of customer disputing outcome measurement |

Ramanujam's *Monetizing Innovation* argues that the pricing model decision should precede the feature design, not follow it: "design the product around the price, not the price around the product". The PRD should state which model was chosen and why other models were rejected.

### Common pricing-model anti-patterns

- **Per-seat for an AI product**: AI value does not scale with seats; per-seat punishes adoption.
- **Usage-based without a floor**: customers can drop to $0 in a slow month; cash flow becomes volatile.
- **Tier with one feature differentiating Good from Better**: customers shop around the differentiator; either bundle more value into Better or merge tiers.
- **Public enterprise pricing**: enterprise pricing should be sales-led; publishing it leaves negotiation room on the table and creates floor effects.

## Willingness-to-Pay Research

Three methods, ranked from quickest to most rigorous:

### Van Westendorp Price Sensitivity Meter

A four-question survey administered to 50-200 prospects/customers per segment:

1. At what price would you consider this product **too expensive** to consider buying?
2. At what price would you consider this product **too cheap** to be of high quality?
3. At what price would you consider this product to be **getting expensive** but you might still consider buying?
4. At what price would you consider this product to be a **bargain**?

The intersections of the cumulative response curves yield:

- **Range of Acceptable Pricing (RAP)**: between the "too cheap" and "too expensive" curve intersections.
- **Optimal Price Point (OPP)**: where "too cheap" and "too expensive" cross.
- **Indifference Price Point (IPP)**: where "expensive" and "bargain" cross — the price the median customer perceives as fair.

Limits: stated preference, not revealed; ignores feature dimensions; works best at the price-point level, not the packaging level.

### Conjoint analysis

A pairwise-choice survey that asks customers to choose between bundle configurations at different price points. Yields willingness-to-pay per feature.

Stronger than Van Westendorp because it captures the feature-price tradeoff. Weaker for cost-of-survey: typically requires 200-500 respondents per segment and statistical analysis software.

### Pricing experiments (revealed preference)

A live A/B test of two price points against new sign-ups. The strongest evidence — revealed willingness to pay — but only available once the team is willing to deploy the change. See "A/B Testing Pricing" below.

## Packaging Decisions

Packaging is which features go in which tier. The decisions are:

1. **What goes in the entry tier?** Enough to deliver the core promise; not so much that customers never upgrade.
2. **What is the value carrier in each tier?** Each tier should have one or two "headline" features that justify the price.
3. **Where are the boundaries?** The boundary between tiers should map to a measurable usage characteristic (number of seats, number of integrations, support level), not to a feature toggle that feels arbitrary.
4. **What is the trial mechanism?** Time-bound (14 days), feature-limited (free tier with caps), reverse-trial (start on Pro, downgrade if usage is low).

### Packaging principles

- Each tier should have a clear customer archetype. Good = solo / SMB; Better = small team / growing; Best = scaling org / enterprise.
- The "value gap" between tiers should be at least 2x. If Better is 1.5x the price of Good, the customer hesitates; if it's 2-3x the price with 3-5x the value, the upgrade is clear.
- Avoid more than 4 tiers. Customers cannot evaluate more than 4-5 options without choice paralysis.

## Grandfathering Policy

The most-often-skipped section of a pricing PRD. Existing customers were promised a price at sign-up; raising it without a plan is a contract violation in some jurisdictions and a trust violation everywhere.

Three grandfathering strategies:

| Strategy | Description | Use when |
|---|---|---|
| **Permanent grandfathering** | Existing customers keep their original price indefinitely | Brand-sensitive customer base; small enough that revenue impact is bearable |
| **Time-bounded grandfathering** | Existing customers keep price for N months/years, then migrate | Common pattern; 12-month grandfathering is typical |
| **No grandfathering** | All customers migrate to new pricing on a stated date | Use only if old pricing was clearly a beta / launch promo |

A grandfathering decision must:

- State the duration in writing (in the PRD and in the customer communication).
- State the migration mechanism (auto, opt-in, opt-out) and the customer's choices.
- Include a rate-limit on how quickly customers can be moved (e.g. "no customer pays more than 25% more YoY without explicit re-signature").
- Be reviewed by Legal in regulated regions (EU consumer law, California subscription auto-renewal laws, etc.).

See `assets/grandfathering_communication_template.md` for a worked customer email.

## Communication Plan

Every pricing change requires a communication plan with at least these channels:

| Channel | Audience | Lead time | Content |
|---|---|---|---|
| **Internal: sales enablement** | AEs, SDRs, CSMs | 2-4 weeks before launch | Battle card, FAQ, talk-track for objections |
| **Internal: support enablement** | Support agents | 1-2 weeks before launch | Macro responses, escalation paths |
| **Customer email (existing)** | All paying customers | 4-8 weeks before any price increase | Honest explanation, new price, grandfathering terms, opt-out mechanism if any |
| **In-app banner / modal** | Logged-in users | At launch | New pricing visible, link to FAQ |
| **Pricing page** | Public | At launch | New page live |
| **Status page** | Public | At launch | Note of pricing change, link to FAQ |
| **Press / blog post** | External | At launch (or 24h before) | If the change is strategic — new tier, new model — write the story |

Pricing changes that omit any of these channels typically generate support ticket spikes, public Twitter complaints, and trust erosion. The communication plan is not optional.

## A/B Testing Pricing

### The legal and ethical question

Showing different prices to different customers raises consumer-protection concerns in some jurisdictions. Common safeguards:

- Test new prices **only to prospects who have not yet seen the existing price** (new sign-ups, anonymous visitors). Avoid testing on existing customers without explicit consent.
- Do not segment by personal attribute (age, gender, ethnicity, geography in some regions) without legal review.
- Be prepared to honor whichever price was shown to the customer at the moment of decision — do not retroactively change it.
- Disclose pricing experiments in your Terms of Service or pricing FAQ if the volume is material.

When in doubt, run pricing tests on anonymous visitors only, not on returning users with an account.

### Test design

A pricing experiment needs:

| Element | Detail |
|---|---|
| **Hypothesis** | Stated in advance: "raising the Pro tier from $29 to $39 will increase ARPU by ≥ 15% without dropping conversion below the 95% CI lower bound of current rate." |
| **Primary metric** | Choose one. Usually ARPU (revenue per visitor) or conversion-to-paid rate. |
| **Secondary metrics** | Watch but do not optimize. Activation rate, trial-to-paid, downgrade rate, churn at 30 days. |
| **MDE (minimum detectable effect)** | Stated in advance with statistical power. Typical: 80% power, 5% significance, MDE of 5-10% relative. |
| **Sample size** | Computed before launch. Pricing tests typically need 5,000-50,000 visitors per arm depending on baseline conversion. |
| **Test duration** | Minimum 2 weeks (to cover weekly seasonality); maximum 12 weeks (to avoid drift in customer mix). |
| **Holdout** | A small permanent control group on the old price (e.g. 5-10%) for 90 days post-rollout to measure cohort retention. |
| **Stop conditions** | Stated in advance: "stop early if churn in the variant arm exceeds the control arm by 3+ percentage points." |

### Common A/B test pitfalls

- **Vanity-metric optimization**: optimizing conversion at the expense of ARPU. Higher conversion at a lower price can be worse net revenue.
- **Short-window readout**: pricing effects often surface at the 30-90 day mark (renewal, downgrade) rather than at sign-up.
- **Mix shift**: a lower price attracts a different customer mix (more SMB, less enterprise). The treatment "works" in the test but degrades unit economics.
- **Selection bias from traffic source**: paid acquisition customers behave differently from organic; ensure the test runs across the traffic mix.
- **Sample-size cargo-culting**: copying another team's "we ran for 4 weeks" without computing the required sample size for your baseline.

## Rollback Criteria

Define before launch the conditions under which the team will reverse the rollout. Examples:

| Condition | Threshold | Action |
|---|---|---|
| New-sign-up conversion drops | > 10 percentage points relative for > 5 business days | Pause new traffic to new pricing; investigate |
| Existing-customer churn spikes | > 2x baseline 30-day churn rate | Pause communication; offer 6-month price freeze to affected cohort |
| Customer support volume spikes | > 3x baseline for > 3 business days | Add support capacity; reassess communication |
| Twitter / public sentiment | Sustained negative coverage, >100 mentions in 24 hours | PR / leadership response; consider price freeze |
| Revenue net impact | Below the lower-bound projection in the financial model | Re-evaluate with finance |

A rollout that hits a rollback threshold should not be argued mid-incident. The conditions were written in advance precisely to remove debate.

## Regional Pricing

For multi-region products, the PRD should specify:

| Decision | Options |
|---|---|
| Currency | USD only, local currency, customer choice |
| Tax inclusion | VAT-inclusive (EU norm), VAT-exclusive (US norm), per-region |
| Purchasing-power parity (PPP) adjustment | None, manual per-region, formulaic |
| Subscription terms by region | Auto-renewal disclosure (EU), 7-day cancellation right (EU), CCPA-required disclosures (CA) |
| Payment methods by region | Card, ACH, SEPA, iDEAL, regional wallets |
| Pricing localization tier | Same tier names globally, region-specific tier structure |

PPP-adjusted pricing can substantially increase emerging-market revenue but risks arbitrage if currency conversions favor migration. Most teams that try PPP-adjusted pricing add geo-IP + payment-method controls to discourage arbitrage.

## Pricing-Page UX Checklist

A pricing page is the conversion surface. The checklist in `assets/pricing_page_checklist.md` covers:

- Headline value proposition above the tiers
- 3-4 tier maximum on the primary view
- Most-popular tier visually highlighted
- Feature-comparison table below the tiers
- Per-feature explanation on hover/click
- FAQ section addressing top 5 objections
- Trust signals (customer logos, security badges, testimonials)
- CTA per tier with verb-led copy ("Start free trial", not "Sign up")
- Pricing toggle (monthly / annual) with annual discount visible
- Currency toggle (if multi-region)
- Tax-inclusive / -exclusive disclosure visible
- Contact-sales path for enterprise

## Pricing Anti-Patterns

Common mistakes the PRD should explicitly guard against:

| Anti-pattern | What goes wrong |
|---|---|
| **Cliffs** | Pricing tiers with steep jumps cause customers to downgrade rather than upgrade |
| **Hidden fees** | Setup fees, overage charges, "starting at" pricing — corrode trust at billing time |
| **Decoy effect gone wrong** | Adding a "deliberately-worse" middle tier to push customers to a target tier backfires if customers notice |
| **Unbundling everything** | Per-feature pricing creates choice paralysis and a long sales cycle |
| **Bundling everything** | Single-tier pricing leaves money on the table for high-value customers |
| **Price-anchoring on cost** | Pricing to cover engineering cost ignores customer willingness-to-pay (Ramanujam's main critique) |
| **Round numbers obsession** | $29 → $30 feels different despite being only $1 change; respect the price-point psychology but don't obsess |
| **"Limited-time" pricing forever** | Customers stop believing in promotions; train them to expect discounts |
| **Pricing-page redesign without test** | Treating the pricing page as a marketing asset rather than a conversion asset |

## Workflow

1. **Strategy → Tactic**: confirm that `business-growth/pricing-strategy/` has run and produced a strategic direction. The pricing PRD operationalizes that direction.
2. **Willingness-to-pay**: gather data (Van Westendorp survey, conjoint, or competitor benchmarks). Document in PRD.
3. **Packaging**: decide tiers, value carriers, boundaries, trial mechanism.
4. **Grandfathering**: decide policy; review with legal in regulated regions.
5. **Communication plan**: draft all channels with copy.
6. **A/B design**: hypothesis, primary metric, MDE, sample size, holdout, stop conditions.
7. **Rollback criteria**: thresholds and actions, signed off by leadership.
8. **Regional**: currencies, tax, PPP, payment methods.
9. **Pricing page UX**: design the page; review against checklist.
10. **Sign-off**: PM + Finance + Legal + Marketing + Sales.
11. **Launch**: execute communication plan; monitor metrics dashboard daily for first 2 weeks, weekly for first quarter.
12. **Post-launch retro**: 90 days after launch, write a retrospective covering predicted vs actual on ARPU, conversion, churn.

## Tools

This skill is template-driven. No Python automation. The artifacts are:

| Artifact | Purpose |
|---|---|
| `assets/pricing_prd_template.md` | Full 13-section pricing PRD template |
| `assets/pricing_experiment_design.md` | A/B test design worksheet with hypothesis, MDE, holdout |
| `assets/pricing_page_checklist.md` | UX review checklist for the pricing page |
| `assets/grandfathering_communication_template.md` | Customer email for grandfathering communication |
| `references/pricing-experimentation-guide.md` | Deep guide on pricing A/B tests, mix-shift detection |
| `references/packaging-frameworks.md` | Tier/usage/hybrid frameworks, Ramanujam-style packaging |

## Troubleshooting

| Symptom | Likely Cause | Resolution |
|---|---|---|
| A/B test shows revenue lift but churn rises 90 days later | Short readout window; treatment attracted a worse-fitting customer mix | Extend readout to 90+ days; add cohort retention to primary metrics; consider re-running on a different acquisition channel mix |
| Existing customers revolt after price increase | Grandfathering communication came too late or felt impersonal | Personalize the comm (from a real exec); offer a longer grandfathering window or one-time renewal discount; publish the rationale |
| Sales reports "customers asking why we're more expensive than X" | Pricing page does not communicate differentiated value | Strengthen value carrier per tier; add competitive comparison table; ensure sales has fresh battle card |
| Conversion drops in the lower tier after raising the upper tier | Customers anchored on the new upper-tier price and downgraded | This is sometimes desirable (margin shift). If not, narrow the value gap by adding to the lower tier |
| PPP-adjusted pricing creates arbitrage (customers using VPNs) | Geo-IP and payment-method controls not in place | Add billing-country verification at payment time; require local payment method for local price |
| Sales team continues quoting old pricing weeks after launch | Sales enablement was a memo, not a process | Run a mandatory enablement session; gate quoting tools to new pricing only; track price-realized vs price-listed |
| A/B test never reaches significance | Underpowered (sample too small for the effect size) | Recompute MDE for the realistic effect size; extend test duration; consider that the effect may genuinely be too small to detect — that's a finding |

## Success Criteria

- Every pricing change ships with a written PRD covering all 13 sections (no section skipped)
- Grandfathering policy is decided and communicated before any customer sees the new price
- A/B tests have hypothesis, primary metric, MDE, and rollback criteria stated in writing before launch
- Communication plan is executed across all required channels with documented copy
- 90-day post-launch retro is written and compared against pre-launch projections
- Customer support volume returns to baseline within 30 days of launch
- ARPU and conversion changes are within ± 20% of the financial model projection at 90 days
- Sales enablement is completed before launch; sales-quoted price matches listed price 95%+ of the time

## Sources & Frameworks

- Madhavan Ramanujam & Georg Tacke, *Monetizing Innovation: How Smart Companies Design the Product Around the Price* (2016)
- Patrick Campbell, "Pricing as a feature"
- Peter Van Westendorp, "NSS-Price Sensitivity Meter" (1976) — original methodology
- Gabriel Weinberg & Justin Mares, *Traction* (2015) — chapter on pricing as a channel
- Stripe, "Atlas Guide to Pricing" — https://stripe.com/atlas/guides/pricing
- Hermann Simon, *Confessions of the Pricing Man* (2015) — strategic pricing context
