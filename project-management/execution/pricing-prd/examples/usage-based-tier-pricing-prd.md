# Example: Pricing PRD for Adding a Usage-Based Tier at Helix Platform

> Real-world scenario showing how to write a tactical pricing PRD with A/B test design end-to-end.

## Context

Helix Platform is a Series-C developer-tools SaaS (~$32M ARR). Today they sell three flat-fee tiers: Free, Pro ($49/mo per workspace), and Team ($199/mo per workspace). Two customer signals have built up over Q1-Q2 2026:

1. Small teams hitting Pro's resource limits but unwilling to pay 4x for Team -- they downgrade or churn.
2. Large teams on Team consuming wildly different amounts of resources, with some leaving money on the table because their bill is capped.

Pricing strategy (`business-growth/pricing-strategy/`) decided in March: add a usage-based component on top of the Team tier, and introduce a new "Scale" tier between Pro and Team. The PM (Hugo Aalto) now needs to write the tactical pricing PRD: page design, packaging, A/B test, grandfathering, comms, rollback.

## Inputs

- Strategy decision: add usage-based component to Team + create Scale tier
- Van Westendorp study (n=180): RAP $89-$199 for Scale tier; OPP $129
- 220 current Team customers; 1,400 Pro customers
- Engineering capacity for billing changes: 5 weeks
- Legal review for usage-based billing in regulated regions

## Applying the skill

1. **Filled the pricing PRD template** (different from feature PRD; new sections for pricing model, packaging, grandfathering, A/B design, rollback).
2. **Locked pricing model decision** -- hybrid (platform fee + metered usage on Team and Scale, flat fee on Pro and Free).
3. **Designed the A/B experiment** at the pricing-page level: control sees current 3-tier; test sees new 4-tier + usage-based. 90/10 split with permanent 5% holdout for long-term measurement.
4. **Wrote the grandfathering policy**: all existing Team customers stay on flat $199 for 12 months; new sign-ups get usage-based from day 1.
5. **Drafted communication plan**: customer email, in-app banner, sales enablement, status page (not for outage, but for pricing change), case-by-case CSM scripts for top accounts.
6. **Wrote rollback criteria**: if conversion rate drops > 1pp or annualized revenue projection drops > 3% in 14 days, rollback.

Key decision quoted: *"Grandfathering 220 customers for 12 months costs us less than the churn risk of forced migration. Customers do not forget bad pricing moves."*

## The artifact

````markdown
# Pricing PRD: Add Scale Tier + Usage-Based Component

**Status:** Final for review
**PM:** Hugo Aalto
**Reviewers:** S. Patel (Head of Finance), M. Reyes (Head of Sales), J. Liu (PMM), M. Hughes (Legal), N. Okafor (Eng)
**Sponsor:** C. Bell (VP Product)
**Date:** 2026-05-22
**Target launch:** 2026-08-01

## 1. Summary

Introduce a new "Scale" tier between Pro and Team, add metered usage-based billing on top of Team and Scale flat fees, and update the pricing page. Existing customers grandfathered for 12 months. Roll out via A/B on the public pricing page with a 90/10 split and a 5% permanent holdout. Targeted to land 12% gross-margin lift on the Team + Scale segments by Q4 2026.

## 2. Contacts

| Role | Name |
|---|---|
| PM | Hugo Aalto |
| Finance | S. Patel |
| Sales | M. Reyes |
| PMM | J. Liu |
| Engineering | N. Okafor |
| Legal | M. Hughes |
| Exec sponsor | C. Bell |

## 3. Background

Customer-feedback triage Q1 2026 surfaced two distinct pricing pains: (1) Pro customers hitting limits but unwilling to 4x to Team; (2) Team customers with uneven usage where light users subsidize heavy users. Pricing-strategy review March 2026 chose to address with packaging change (insert Scale tier) + monetization model change (add usage component on Team and Scale).

Van Westendorp PSM study (n=180) for the proposed Scale tier:
- Optimal Price Point (OPP): $129/mo
- Indifference Price Point (IPP): $109/mo
- Range of Acceptable Pricing: $89 - $199

Competitor anchors (Linear and Cursor list prices as of September 2026): GitHub Copilot for Teams $19/seat-mo; Linear Basic $10/user-mo and Business $16/user-mo (billed yearly); Cursor Teams Standard seat $40/user-mo (Premium seat $120/user-mo). Our value prop differs (workspace, not seat), so direct comparison is loose.

## 4. Objective

**Business benefit:**
- KR1: Gross margin on Team + Scale segments lifts >= 12% within 6 months (counter: customer satisfaction NPS does not drop > 5)
- KR2: Pro -> Scale upgrade rate >= 8% within 6 months (customers stuck at Pro upgrade in)
- KR3: Avg revenue per Team customer lifts >= 20% (driven by usage)

**Customer benefit:**
- Light users on Team pay less (savings ~$50-80/mo for the 30th-percentile usage customer)
- Heavy users get explicit value at the right price (no more "I'm hitting the cap")
- New Scale tier closes the Pro -> Team affordability gap

## 5. Market Segments

| Segment | Willingness-to-pay (Van Westendorp) | Current tier | Proposed tier |
|---|---|---|---|
| Solo developers / hobbyists | Free is right | Free | Free |
| Small dev teams (2-5 ppl) | ~$49 flat | Pro | Pro |
| Growing teams (6-15 ppl) | $89-$199 (OPP $129) | Pro -> Team migration churn here | **Scale** ($129) |
| Established teams (16-50 ppl) | $199 + usage | Team | Team (with usage) |
| Enterprises (50+) | Custom | Team -> Enterprise | Enterprise (sales-led) |

## 6. Solution: Pricing Model

### 6.1 Tier structure (proposed)

| Tier | Flat fee | Usage component | Target segment |
|---|---|---|---|
| Free | $0 | None | Solo |
| Pro | $49/mo | None | Small teams |
| **Scale (new)** | **$129/mo** | None initially; usage added in v2 | Growing teams |
| Team | $199/mo + $X/usage unit above included quota | Yes | Established teams |
| Enterprise | Custom | Custom | Sales-led |

### 6.2 Pricing model decision (Ramanujam, *Monetizing Innovation*)

**Chosen: Hybrid (platform fee + metered usage on Team only initially; Scale gets usage in v2).**

| Model | Why we chose / rejected |
|---|---|
| Pure tier | Rejected: cliffs are the problem we're trying to solve |
| Pure usage | Rejected: cash-flow volatility too high for a public company; "bill shock" risk |
| Hybrid (chosen) | Predictable platform value + variable feature value |
| Per-seat | Rejected (our value scales with workspace, not seats) |
| Outcome-based | Rejected (hard to define "outcome" for a developer-tools product) |

### 6.3 Usage units (Team tier)

The metered unit is "compute-minutes" (one billable unit per minute of active workspace compute). Included quota: 20,000 compute-minutes/mo per workspace. Overage: $0.012 / compute-minute. Cap (optional, customer-set): hard cap to prevent runaway bills.

Rationale for compute-minutes: directly tied to value delivered; customer-controllable; cleanly measurable; defensible in invoice disputes.

### 6.4 Packaging changes

| Feature | Free | Pro | Scale | Team | Enterprise |
|---|:-:|:-:|:-:|:-:|:-:|
| Workspaces | 1 | 3 | 10 | 30 | unlimited |
| Compute-minutes (incl) | 500 | 5,000 | 15,000 | 20,000 | 20,000+ |
| Overage rate | n/a | n/a | n/a | $0.012/min | negotiated |
| SSO | no | no | yes | yes | yes |
| Audit log | no | no | 30d | 90d | 365d |
| Priority support | no | no | yes | yes | dedicated |
| Custom domain | no | no | no | yes | yes |
| SLA | no | no | no | 99.9% | 99.99% |

## 7. Grandfathering

### Existing customer treatment

**Pro customers (1,400 accounts):** No change. Free to upgrade to Scale or Team.

**Team customers (220 accounts):** Grandfathered at flat $199 for 12 months from launch (until 2027-08-01). After 12 months, the usage component activates. CSMs notify each customer at 9 months (3-month heads-up) and 11 months (1-month heads-up).

**Enterprise (custom contracts):** Honor existing contracts. New enterprise sign-ups get the new structure.

### Rationale

Forced migration of 220 paying customers risks churn estimated at 8-12% (industry comp). Grandfathering for 12 months reduces this risk to <2% while giving the team time to refine the usage model with new sign-ups.

## 8. A/B Test Design

| Parameter | Value |
|---|---|
| Test scope | Public pricing page (acme.com/pricing) |
| Control | Current 3-tier structure (Free, Pro, Team) |
| Test | New 4-tier with usage explanation (Free, Pro, Scale, Team) |
| Holdout | 5% (permanent; for long-term measurement) |
| Split | 47.5% Control / 47.5% Test / 5% Holdout |
| Primary metric | Trial-to-paid conversion rate, mid-market traffic |
| MDE | 0.4pp (4.1% -> 4.5% expected) |
| Power | 80% |
| Significance | 95% (two-sided) |
| Duration to power | 21 days at current traffic |
| Counter-metric | NPS on pricing-page clarity |
| Counter-metric 2 | Trial-start rate (don't sacrifice top-of-funnel for revenue downstream) |

### Flag

`pricing_page_4tier_usage_v1` in LaunchDarkly. Retirement date: 2026-10-01 (8 weeks post-launch). See `feature-flag-strategy/`.

### Statistical guardrails

- Assignment is sticky (cookie + fingerprint + cohort).
- No personalized pricing (UK/EU consumer-law compliance).
- Holdout group is sticky for 90 days post-rollout for long-term measurement.

## 9. Rollback Criteria

| Trigger | Rollback action |
|---|---|
| Trial-to-paid conversion drops > 1pp vs control sustained 14 days | Rollback test cohort to control |
| Trial-start rate drops > 0.5pp sustained 14 days | Rollback |
| NPS on pricing clarity drops > 10 points vs baseline | Rollback |
| Annualized revenue projection drops > 3% in 14 days | Rollback |
| Sev1 billing incident attributed to new structure | Immediate rollback + post-mortem |

Rollback = flag to 0% (control everywhere). Existing grandfathered customers unaffected (they remain on flat $199).

## 10. Regional / Localization

| Region | Treatment |
|---|---|
| US | Standard launch |
| UK | Cleared by Legal -- no consumer-law conflict |
| EU | GDPR-compliant (no individualized pricing); usage metering anonymized for retention |
| Japan + APAC | Localized pricing in JPY/AUD/SGD (post-launch v1.1) |

## 11. Communication Plan

### Customer email (Team customers, 220 accounts)

```
Subject: An update on Helix Team pricing -- and 12 months to plan

Hi {first_name},

We're updating Helix pricing on August 1, 2026. Here's what it means for
your account.

What's changing
We're adding a new "Scale" tier ($129/mo) between Pro and Team, and
introducing a usage-based component on Team pricing for new sign-ups
(compute-minutes above a 20,000/mo included quota at $0.012/minute).

What's NOT changing for you
You stay on flat $199/mo until August 2027 -- a full year. You don't pay
usage. You don't have to do anything.

Why we're changing
We've heard from teams larger than Pro can fit but smaller than Team makes
sense -- they need Scale. We've also heard from heavy Team users that
the flat cap doesn't reflect their actual value, and from light Team
users that they'd like to pay less for less usage.

What to expect
- Aug 1, 2026: New pricing live on acme.com for new sign-ups.
- May 1, 2027: 3-month heads-up email from your CSM about the migration.
- July 1, 2027: 1-month heads-up email.
- Aug 1, 2027: Usage-based component activates on your account; your CSM
  will walk through usage projections with you in July.

Where to learn more
- Pricing page: acme.com/pricing
- FAQ: docs.acme.com/pricing-update-2026
- Reply to this email and I'll personally answer.

Hugo Aalto
PM, Helix Platform
```

### In-app banner (Team customers)

```
A pricing update is coming. Team customers stay on $199/mo through Aug
2027. [Learn more] [Dismiss]
```

### Status page entry

```
2026-08-01: Pricing update -- new Scale tier and usage-based billing
for new Team sign-ups. Existing customers grandfathered through Aug
2027.
```

### Sales enablement

- New pricing battlecard (1-page)
- "How to talk about usage-based billing" guide
- "When NOT to switch a grandfathered customer early" guide
- Revised quoting tool

### CSM scripts (top 20 accounts)

- Personal email from CSM 2 days before public email
- 30-min walkthrough call offered
- "I notice you're using X compute-minutes today; here's what your bill would look like under the new pricing" individual analysis

## 12. Engineering Scope

| Component | Estimate | Owner |
|---|---|---|
| Pricing page redesign | 2 weeks | Frontend |
| A/B framework integration | 0.5 week | Eng platform |
| Stripe billing schema update (usage metering) | 1 week | Backend |
| Compute-minute metering pipeline | 2 weeks | Data Platform |
| Customer-facing usage dashboard | 1 week | Frontend |
| Grandfather flag in account model | 0.5 week | Backend |
| Documentation + help center updates | 0.5 week | Tech writers |
| Total | ~5 weeks | -- |

## 13. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Bill shock on new sign-ups | Med | High | Hard cap option (customer-set); usage alerts at 80%; documented "what to expect" guide |
| Pricing-page confusion (4 tiers vs 3) | Med | Med | A/B test catches; NPS counter-metric; rollback criteria |
| Grandfathered customers feel locked-in when usage launches in 2027 | Med | High | 9-month + 1-month heads-ups; CSM-led migration walks; option to stay on flat for additional fee (not committed in v1) |
| EU compliance gap | Low | High | Legal cleared; usage metering anonymized |
| Sales team mis-pitches Scale to Team accounts (down-sell) | Med | Med | Enablement explicit on segment; quoting tool guides |
| Engineering can't ship in 5 weeks | Med | Med | Pricing page can ship without usage component; usage component is v1.1 if needed |

## 14. Success Criteria

- A/B test reaches significance with test arm >= control on conversion
- 12-month gross margin lift on Team + Scale >= 12%
- Pro -> Scale upgrade rate >= 8% by month 6
- Grandfathered customer churn during the 12-month window <= 2%
- NPS on pricing clarity does not drop > 5
- Zero Sev1 billing incidents

## 15. What we are NOT doing

- Personalized pricing per visitor (UK/EU consumer-law)
- Forced migration of grandfathered customers before 2027
- Removing existing flat-fee option for new Team sign-ups (we still offer flat as a "bring your own cap" config)
- Public pricing for Enterprise (sales-led)
- A second usage dimension besides compute-minutes (one-thing-at-a-time)
````

## Why this works

- The pricing model decision is made explicitly and the rejected alternatives are documented (Ramanujam discipline).
- Grandfathering 220 Team customers for 12 months is named as a deliberate cost trade-off, with churn-risk math.
- The A/B design has a 5% permanent holdout (not just a temporary test), so long-term lift is measurable in 2027.
- Rollback criteria are numeric and pre-locked, so a panicked rollback decision doesn't happen by feel.
- "What we are NOT doing" (Section 15) heads off the most common pricing-PRD failures: personalized pricing (consumer-law violation), forced migration (churn), second usage dimension (complexity).

## What's next

- Pair with [../../business-growth/pricing-strategy/](../../business-growth/pricing-strategy/) -- this PRD executes that strategy.
- Use [../feature-flag-strategy/](../feature-flag-strategy/) for the A/B mechanics on the pricing page.
- Use [../launch-playbook/](../launch-playbook/) for the 2026-08-01 launch coordination.
- Pair with [../create-prd/](../create-prd/) for any feature dependencies (usage dashboard, cap controls).
- Use [../post-mortem/](../post-mortem/) if a billing incident triggers rollback.
- Re-engage [../../finance/](../../finance/) for the 12-month grandfathering revenue model.
