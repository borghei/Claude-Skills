# Red Flags: Pricing PRD

> Common ways this skill's output goes wrong — concrete examples, why they're bad, and how to fix them.

## How to use this document

Scan the pricing PRD before review with Finance / Legal / Marketing / Sales. Each red flag shows the *bad* version next to the *good* version, anchored to Ramanujam's *Monetizing Innovation*, Van Westendorp's PSM, and controlled pricing-experiment discipline.

---

## Red Flag 1: Van Westendorp without segmentation

**Symptom.** PRD includes a Van Westendorp PSM curve. n=120 respondents. Optimal Price Point: $42/mo. Decision: price at $42.

**Why it's bad.** Van Westendorp aggregated across segments produces a meaningless average. SMB customers' "too expensive" anchor is $20; enterprise's is $200. Pricing at the aggregate optimum overprices SMB and underprices enterprise — losing both ends of the curve.

**Bad example:**
> "Van Westendorp n=120, OPP $42, IPP $36. Decision: launch at $39/mo for all segments."

**Good example:**
> "Van Westendorp segmented:
> SMB (n=42): OPP $18, IPP $14.
> Mid-market (n=48): OPP $46, IPP $38.
> Enterprise (n=30): OPP $180, IPP $140.
> Decision: Good/Better/Best tiers at $19/$49/$199. Each tier targets its segment's IPP-to-OPP band. Aggregate VW curve is informational only; segment-specific curves drive pricing."

**How to catch it.** Read the Van Westendorp section. Are curves reported per segment? If one aggregate curve only, segmentation is missing.

---

## Red Flag 2: Grandfathering omitted

**Symptom.** Pricing PRD covers new pricing, communication, A/B test, rollback. Grandfathering: not mentioned.

**Why it's bad.** Grandfathering is the most-often-skipped section of a pricing PRD and the most-often-cause of customer revolt. Existing customers were promised a price at sign-up; raising it without a plan is a contract violation in some jurisdictions and a trust violation everywhere.

**Bad example:**
> "Pricing PRD: [12 sections covering new pricing]. Grandfathering: [section missing entirely]. Decision: 'we'll move everyone to new pricing on Aug 1.'"

**Good example:**
> "Grandfathering policy (signed off by Legal, Finance, VP Customer Success):
> • Existing annual subscribers: 18 months grandfathering at current price.
> • Existing monthly subscribers: 6 months grandfathering.
> • Trial-to-paid converters within 30 days of pricing change: grandfathered at the price they saw during trial.
> • Rate-limit: no customer pays more than 25% YoY without explicit re-signature.
> • Reviewed against existing enterprise contracts; 8 customers have contracts with explicit price-freeze clauses; they remain at original price for contract term.
> Customer email template in `assets/grandfathering_communication_template.md`."

**How to catch it.** Is the grandfathering section present and reviewed by Legal? If absent, the rollout will revolt.

---

## Red Flag 3: A/B test without statistical design

**Symptom.** Test plan: "Try the new price for 2 weeks, see what happens. If conversion stays similar, ship it."

**Why it's bad.** Pricing experiments need pre-stated hypothesis, primary metric, MDE, sample size, holdout, and stop conditions. Without these, the team will rationalize whatever data shows — confirmation bias dressed as experimentation. Worse, pricing-effect tail (90-day retention, downgrade) often surfaces after the test concludes.

**Bad example:**
> "Test plan: 'Show new pricing to half the visitors; check conversion at 2 weeks; ship if it looks OK.'"

**Good example:**
> "A/B test design (locked in writing 1 week before launch):
> Hypothesis: 'Raising Pro from $29 to $39 will increase ARPU by >= 15% without dropping conversion below 95% CI lower bound of current 4.2% rate.'
> Primary metric: ARPU (revenue per visitor).
> Secondary metrics: trial-to-paid, D30 downgrade, D90 retention (watch, don't optimize).
> MDE: 10% relative; 80% power; 5% significance.
> Sample size: 24,000 visitors/arm (computed pre-launch).
> Test duration: minimum 4 weeks (2x weekly seasonality cycle); maximum 12 weeks.
> Holdout: 5% permanent control at old price for 90 days post-launch.
> Stop conditions: stop if churn in variant > control by 3+ percentage points; stop if MDE achieved at week 4.
> Eligibility: anonymous visitors who have not previously seen the existing price."

**How to catch it.** Read the A/B section. Are hypothesis, MDE, sample size, and stop conditions all numeric and pre-stated? If "we'll see how it goes", design is missing.

---

## Red Flag 4: Pricing tested on existing customers without consent

**Symptom.** A/B test exposes 50% of existing logged-in customers to new pricing. They see a different price on the pricing page than what they signed up at.

**Why it's bad.** Showing different prices to existing customers raises consumer-protection concerns in some jurisdictions (GDPR-related fairness, US state-level laws on dynamic pricing). It also damages trust — customers comparing notes feel manipulated.

**Bad example:**
> "Test: 50/50 split across all visitors including logged-in returning users. Variant sees $39; control sees $29. Reddit thread: 'Why am I seeing a different price than my friend?'"

**Good example:**
> "Test eligibility (signed off by Legal):
> • Anonymous visitors only.
> • New email signups within last 30 days who have not yet seen a price.
> • Excluded: returning users with accounts; existing customers; users with active price-freeze contracts.
> Disclosure: pricing experiments disclosed in the Terms of Service and pricing FAQ.
> If customers ask: standard response acknowledges experiment, honors the price they saw at decision time."

**How to catch it.** Read the eligibility criteria. Does it exclude existing customers? If existing customers can see variant prices, legal review is missing.

---

## Red Flag 5: Vanity-metric optimization

**Symptom.** Test shows conversion up 8%. Team declares victory and ships. 90 days later, ARPU is down 12%, churn up 4 points.

**Why it's bad.** Optimizing conversion at the expense of ARPU loses net revenue. Lower price → more sign-ups → worse-fit customers → higher churn → lower lifetime value. Conversion is a vanity metric for pricing experiments; ARPU and 90-day retention are what matter.

**Bad example:**
> "Test concluded: variant ($25) had 18% higher conversion than control ($29). Decision: ship the $25 price. 90 days later: ARPU down 12%, D60 retention down 5 points, net revenue net negative."

**Good example:**
> "Primary metric: ARPU (revenue per visitor). Not conversion. This locks the team into optimizing the right outcome.
> Result: variant ($25) had 18% higher conversion but 9% lower ARPU. Variant lost on the primary metric. Decision: keep $29 (or test $32 next).
> Cohort tracking: 90-day retention monitored for both arms; informs whether the conversion lift compounds long-term."

**How to catch it.** Read the primary-metric line in the test design. If "conversion rate" alone, the test will optimize for the wrong outcome.

---

## Red Flag 6: Mix-shift mistaken for treatment effect

**Symptom.** Test ran on a paid-acquisition campaign. New pricing tested well. Rolled out broadly to organic traffic; performance collapses.

**Why it's bad.** Different traffic sources have different price sensitivity. A test that ran on one source (paid, with high-intent visitors) does not generalize to others (organic, lower-intent). Mix shift over the rollout produces the apparent collapse.

**Bad example:**
> "Test ran exclusively on Google Ads traffic for 4 weeks. Pricing +20% accepted; conversion stable. Roll out to organic + email + direct: conversion drops 18%. 'Test result didn't hold.'"

**Good example:**
> "Test eligibility: stratified random across all traffic sources (paid search, organic, direct, email, referral) in proportion to current acquisition mix. Sample size per source meets MDE per stratum (or test source-by-source separately). Mix-shift analysis at conclusion: results consistent across sources, or breakdown reported with caveats. Rollout assumes the test's traffic mix; if rollout introduces a new mix (e.g., new paid channel launching), re-baseline before extrapolating."

**How to catch it.** Read the test eligibility. Does it stratify by traffic source? If single-source, results may not generalize.

---

## Red Flag 7: Communication plan missing channels

**Symptom.** Pricing change announced. Customer email goes out. Sales team finds out from a customer. Support gets a wave of tickets they can't answer.

**Why it's bad.** Pricing changes touch every customer-facing function. Skipping any channel produces customer confusion (different stories from sales vs support vs in-app) and team chaos (sales improvising; support escalating). The cost is paid in trust, not just tickets.

**Bad example:**
> "Communication plan: customer email + blog post. (Sales: not enabled. Support: not briefed. In-app: not updated.)"

**Good example:**
> "Communication plan (all channels assigned with owner + date):
> • Sales enablement: PMM owns; battle card by T-21; mandatory training T-14.
> • Support enablement: Support Lead owns; macros + escalation paths by T-7.
> • Customer email: PMM owns; 8 weeks before change for any increase; segment-tailored.
> • In-app banner: PM owns; live at T-0; links to FAQ.
> • Pricing page: PM owns; live at T-0.
> • Status page: PM owns; note + link at T-0.
> • Press / blog: PMM owns; live at T-0 (or T-1 for embargoed press).
> Each channel has draft copy in the PRD, reviewed by Legal."

**How to catch it.** Read the communication section. Are sales, support, in-app, pricing page, status page, press all named with owners? Missing any = chaos predicted.

---

## Red Flag 8: No rollback criteria

**Symptom.** New pricing live. Conversion drops 20%. Team debates for 5 days whether this is "noise" or "a real signal". Customers continue to lose interest.

**Why it's bad.** Rollback criteria written under pressure are bad rollback criteria. Pre-agreed thresholds remove the debate; the rollout reverses automatically when triggered. Improvised criteria mean the team holds out hope while damage accumulates.

**Bad example:**
> "Rollback plan: 'monitor metrics; if things look bad, we'll discuss.'"

**Good example:**
> "Rollback criteria (pre-agreed in PRD, signed by VP Product + Finance):
> | Trigger | Threshold | Action |
> | New signup conversion | > 10 pts relative drop, sustained 5 business days | Pause new traffic to new pricing; investigate |
> | Existing customer churn | > 2x baseline 30-day churn | Pause comm; offer 6-month price freeze to affected cohort |
> | Support ticket volume | > 3x baseline, sustained 3 business days | Add support capacity; reassess comm |
> | Public sentiment | > 100 negative mentions on Twitter in 24h | PR / leadership response; consider price freeze |
> | Revenue net impact | Below lower-bound projection in financial model | Re-evaluate with Finance |
> Triggered: rollout reverses; rationale documented for the post-launch retro."

**How to catch it.** Read the rollback section. Are thresholds numeric and pre-agreed? If "we'll discuss", no rollback criteria.

---

## Red Flag 9: Public enterprise pricing

**Symptom.** Pricing page publishes enterprise tier at $499/mo. Enterprise sales team complains: every deal anchors at $499.

**Why it's bad.** Public enterprise pricing leaves negotiation room on the table. Enterprise customers expect to negotiate; publishing a number sets the ceiling, not the floor. It also commoditizes the enterprise tier — buyers compare on the published number rather than the bespoke value.

**Bad example:**
> "Pricing page: Good $19, Better $49, Best (Enterprise) $499."

**Good example:**
> "Pricing page: Good $19, Better $49, Enterprise 'Contact sales'. Enterprise pricing is sales-led; AE tools include the price floor ($299), the target ($499), and the discount-authority limits per deal size. Mid-market customers can self-serve Good and Better; Enterprise routes to a 30-min discovery call."

**How to catch it.** Look at the published pricing page. Is the top tier a "Contact sales" CTA or a fixed number? Fixed = sales authority degraded.

---

## Red Flag 10: Cliffs (steep tier-to-tier jumps)

**Symptom.** Pricing tiers: Starter $9, Pro $99, Business $999. Customers at Pro who outgrow it downgrade rather than upgrade because the jump is too steep.

**Why it's bad.** Packaging principle: value gap between tiers should be at least 2x; price gap should match. A 10x price jump (Pro→Business here) with only a 2-3x value increase causes customers to fall off the upgrade ramp.

**Bad example:**
> "Starter $9 (1 user), Pro $99 (5 users), Business $999 (20 users). Pro customers wanting 6 users: downgrade rather than pay $999."

**Good example:**
> "Starter $19 (3 users), Pro $79 (10 users), Team $249 (30 users), Business $799 (100 users). Each tier is roughly 3x the previous. Pro customers wanting 11-15 users have a natural step up to Team. Value gaps explicit: Pro adds reporting + integrations; Team adds advanced permissions + SSO; Business adds audit logs + dedicated support."

**How to catch it.** Compute price ratios between tiers. > 5x is a cliff. Compute value ratios; if value ratio is < 50% of price ratio, the tier is mispriced.

---

## Red Flag 11: PPP arbitrage unaddressed

**Symptom.** Pricing localized to PPP (purchasing-power parity): US $39, India $9, Brazil $12. Customers use VPNs + Indian payment cards from US.

**Why it's bad.** PPP-adjusted pricing unlocks emerging-market revenue but creates arbitrage incentives. Without geo-IP + payment-method controls, US customers route around US pricing via VPN. The revenue gain is offset by leakage.

**Bad example:**
> "PPP pricing live globally. No controls. Three months later: 23% of 'India tier' subscribers have US payment processing addresses. ~$2M ARR leakage."

**Good example:**
> "PPP-adjusted pricing with controls:
> • Geo-IP + payment-method consistency check at signup.
> • Require local payment method for local price (Indian card for Indian price).
> • Periodic re-verification of billing-country for renewals.
> • Customers with mismatch: auto-prompted to confirm address; if confirmed mismatch, charged at the corrected tier.
> • Audit: monthly review of payment-country distribution vs registered-country distribution."

**How to catch it.** If PPP pricing is offered, are geo-IP + payment-method controls in place? If no, arbitrage is happening.

---

## Red Flag 12: Per-seat pricing for an AI product

**Symptom.** AI assistant priced per seat ($29 per user per month). Customers add fewer users (the team that hires more users to use AI pays more, discouraging adoption).

**Why it's bad.** AI value does not scale with seats — it scales with usage. Per-seat pricing punishes adoption: the team that wants every employee to use the AI is the one that pays the most. Customers respond by limiting seats, which limits adoption, which limits value, which limits expansion revenue.

**Bad example:**
> "AI assistant: $29/user/month. Reality: customers buy 5 seats for a 50-person team, share logins, AI usage stays low, expansion zero."

**Good example:**
> "AI assistant: per-conversation usage-based pricing ($0.30 per conversation) with a $99/mo platform fee. Per-seat option: only as an unlimited-conversation enterprise tier ($999/mo for orgs that prefer predictability).
> Per-conversation aligns price with value: more usage → more value delivered → more revenue. No adoption disincentive. Model APIs (Anthropic, OpenAI) are priced on usage, so our cost scales with usage too; per-seat pricing leaves that cost unhedged."

**How to catch it.** Is the product AI-mediated, and is pricing per-seat? If yes, value-to-price alignment is broken.

---

## Red Flag Quick Reference

| # | Anti-pattern | One-line check |
|---|---|---|
| 1 | Van Westendorp without segmentation | Are curves reported per segment? |
| 2 | Grandfathering omitted | Is the grandfathering section present and Legal-reviewed? |
| 3 | A/B test without statistical design | Hypothesis, MDE, sample size, stop conditions — all numeric? |
| 4 | Test exposed to existing customers | Does eligibility exclude logged-in returning users? |
| 5 | Vanity-metric optimization | Is the primary metric ARPU (not conversion)? |
| 6 | Mix-shift mistaken for effect | Did the test stratify by traffic source? |
| 7 | Communication plan missing channels | Sales / support / in-app / pricing page / status page / press all named? |
| 8 | No rollback criteria | Are rollback thresholds numeric and pre-agreed? |
| 9 | Public enterprise pricing | Is the top tier "Contact sales"? |
| 10 | Cliffs between tiers | Compute price ratios; > 5x = cliff |
| 11 | PPP arbitrage unaddressed | Are geo-IP + payment-method controls in place? |
| 12 | Per-seat AI pricing | Is the AI product priced per seat or per usage? |

## Related Reading

- SKILL.md Troubleshooting
- references/pricing-experimentation-guide.md
- references/packaging-frameworks.md
- Madhavan Ramanujam & Georg Tacke, *Monetizing Innovation* (2016)
- Patrick Campbell, "Pricing as a feature"
- Peter Van Westendorp, "NSS-Price Sensitivity Meter" (1976)
- `business-growth/pricing-strategy/` (strategic input)
- `feature-flag-strategy/` (rollout mechanics)
- `create-prd/` (sections 1-2 shared)
- `finance/` (financial model)
- `launch-playbook/` (the launch coordination)
