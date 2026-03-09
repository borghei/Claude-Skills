---
name: paywall-upgrade-cro
description: In-app paywall and upgrade screen optimization covering feature gate design, usage limit UX, trial expiration flows, upgrade trigger timing, save offer strategy, and ethical monetization patterns.
version: 1.0.0
author: borghei
category: business-growth
tags: [cro, paywall, upgrade, freemium, monetization, upsell]
triggers:
  - user wants to optimize in-app paywall or upgrade screens
  - user mentions upgrade modal, feature gate, or upsell
  - user wants to convert free users to paid
  - user mentions trial expiration screen or limit reached screen
  - user has low freemium conversion rate
  - user asks about pricing page within an app
---

# Paywall & Upgrade Screen CRO

Production-grade framework for in-product upgrade flows. Covers feature gate design, usage limit UX, trial expiration sequences, upgrade trigger timing, dark pattern avoidance, and ethical monetization. Distinct from public pricing pages (use page-cro for those) -- this focuses on in-product moments where users have already experienced value.

---

## Table of Contents

- [Initial Assessment](#initial-assessment)
- [The Value-First Principle](#the-value-first-principle)
- [Paywall Trigger Architecture](#paywall-trigger-architecture)
- [Paywall Screen Design](#paywall-screen-design)
- [Feature Gate Patterns](#feature-gate-patterns)
- [Usage Limit UX](#usage-limit-ux)
- [Trial Expiration Flows](#trial-expiration-flows)
- [Timing and Frequency Rules](#timing-and-frequency-rules)
- [Upgrade Flow Optimization](#upgrade-flow-optimization)
- [Dark Pattern Avoidance](#dark-pattern-avoidance)
- [Platform-Specific Considerations](#platform-specific-considerations)
- [Metrics and Benchmarks](#metrics-and-benchmarks)
- [A/B Test Framework](#ab-test-framework)
- [Output Artifacts](#output-artifacts)
- [Related Skills](#related-skills)

---

## Initial Assessment

### Required Context

| Question | Why It Matters |
|----------|---------------|
| What is the upgrade model? (freemium to paid, trial to paid, tier upgrade) | Determines the paywall type |
| What is free vs paid? | Defines the value gap to communicate |
| What triggers upgrade prompts today? | Identifies current trigger points |
| What is the current free-to-paid conversion rate? | Baseline for improvement |
| What is the aha moment for users? | Determines when the paywall should appear |
| What pricing model? (per seat, usage, flat) | Affects paywall messaging |
| Mobile app, web app, or both? | Platform-specific requirements |

---

## The Value-First Principle

The single most important rule in paywall design: **The user must have experienced real value before seeing an upgrade prompt.**

### Value-First Checklist

- [ ] User has completed the activation event (aha moment reached)
- [ ] User has used the product at least 2-3 times
- [ ] User has created or stored data they would lose
- [ ] The upgrade feels like a natural next step, not a trap

### When to Show vs When NOT to Show

| Show | Do Not Show |
|------|------------|
| After aha moment is reached | During onboarding |
| When user hits a genuine limit | On first login |
| When user clicks a paid feature | When user is in the middle of a task |
| After milestone completion | Immediately after a frustrating experience |
| On session start (gentle reminder) | After every action |

---

## Paywall Trigger Architecture

### Trigger Types

| Trigger | When It Fires | Best For |
|---------|--------------|----------|
| Feature gate | User clicks a locked feature | Feature-differentiated tiers |
| Usage limit | User reaches a quota | Usage-based pricing |
| Trial expiration | Trial period ending | Time-limited trial models |
| Time-based | After N days of active use | Freemium nurture |
| Milestone-based | After user achieves X | Upsell at success moments |
| Team-based | When team grows past free seat limit | Per-seat models |

### Trigger Priority Map

| User State | Primary Trigger | Timing |
|-----------|----------------|--------|
| Activated, under limits | Feature gate (when they try paid feature) | On click |
| Approaching limit | Soft warning (80% of limit) | Proactive |
| Hit limit | Usage limit paywall | On action that exceeds limit |
| Trial day 7 of 14 | Trial ending reminder | Session start |
| Trial day 13 of 14 | Urgent trial expiration | Session start + email |
| Trial day 14 | Trial expired | On login |
| Active for 30+ days, free | Value-based upgrade prompt | Session start, once per week |

---

## Paywall Screen Design

### Screen Anatomy

```
┌─────────────────────────────────────┐
│ [X Close / "Not now"]               │  Escape hatch (always visible)
│                                     │
│ HEADLINE: Value-focused             │  "Unlock [feature] to [benefit]"
│                                     │
│ [Feature preview / screenshot]      │  Show what they are missing
│                                     │
│ KEY BENEFITS:                       │
│ - Benefit 1                        │
│ - Benefit 2                        │
│ - Benefit 3                        │
│                                     │
│ PRICE: $X/month                    │  Clear, simple pricing
│ (or plan comparison)               │
│                                     │
│ [UPGRADE CTA - Primary]           │  "Start Pro Plan"
│ [Maybe Later - Secondary]          │  Clear secondary action
│                                     │
│ "Join 5,000+ teams on Pro"        │  Social proof
└─────────────────────────────────────┘
```

### Copy Patterns by Trigger Type

| Trigger | Headline Pattern | CTA Pattern |
|---------|-----------------|-------------|
| Feature gate | "Unlock [Feature] to [Benefit]" | "Upgrade to [Plan]" |
| Usage limit | "You've used all [N] [resources]" | "Get Unlimited [Resources]" |
| Trial expiring | "Your trial ends in [N] days" | "Continue with [Plan]" |
| Milestone | "You just hit [milestone]! Keep growing with Pro" | "Upgrade & Keep Growing" |
| Time-based | "[Product] Pro helps teams like yours [benefit]" | "See Pro Features" |

---

## Feature Gate Patterns

### Soft Gate (Preview + Lock)

User can see what the feature does but cannot use it fully.

```
┌──────────────────────────────┐
│  [Feature Preview]           │  Blurred screenshot or partial result
│                              │
│  [Lock Icon] Pro Feature     │
│                              │
│  [Feature name] lets you:    │
│  - Capability 1              │
│  - Capability 2              │
│                              │
│  [Upgrade to Pro - $X/mo]   │
│  [Maybe Later]              │
└──────────────────────────────┘
```

### Hard Gate (Block + Explain)

User cannot access the feature at all. Show the value clearly.

```
┌──────────────────────────────┐
│  [Lock Icon]                 │
│                              │
│  This feature is available   │
│  on the Pro plan             │
│                              │
│  What you get:               │
│  - Benefit 1                 │
│  - Benefit 2                 │
│  - Benefit 3                 │
│                              │
│  [Upgrade to Pro]            │
│  [Compare Plans]             │
└──────────────────────────────┘
```

### Feature Gate Design Rules

- Always explain WHY the feature is valuable (not just that it is locked)
- Show what the feature produces (output preview) when possible
- Include a "Compare Plans" link for users who want more detail
- Do not gate features the user was already using during trial

---

## Usage Limit UX

### Approaching Limit (80% Warning)

```
┌──────────────────────────────────┐
│  [Progress Bar: 80%]            │
│  You've used 80 of 100 credits  │
│                                  │
│  [Get More Credits]  [Dismiss]  │
└──────────────────────────────────┘
```

### At Limit (100%)

```
┌──────────────────────────────────────┐
│  [Progress Bar: 100%]               │
│  You've reached your monthly limit  │
│                                      │
│  Free: 100 credits | Pro: Unlimited │
│                                      │
│  [Upgrade to Pro]                   │
│  [Delete items to free space]       │  Alternative action
└──────────────────────────────────────┘
```

### Usage Limit Rules

- Show usage context before the limit hits (progress indicators in the UI)
- Provide an alternative action (delete, archive, export) when possible
- Never delete user data when limits are reached
- Allow grace period (do not cut off mid-task)

---

## Trial Expiration Flows

### Trial Countdown Sequence

| Day | Channel | Message | Tone |
|-----|---------|---------|------|
| Day 7 (of 14) | In-app banner | "7 days left in your trial" | Informational |
| Day 10 | Email | "4 days left -- here's what you've accomplished" | Value summary |
| Day 12 | In-app modal | "2 days left -- don't lose access to [feature]" | Mild urgency |
| Day 13 | Email | "Tomorrow is your last day" | Urgency + offer |
| Day 14 | In-app full screen | "Your trial has ended" | Clear options |
| Day 15 | Email | "We kept your data safe -- reactivate anytime" | Reassurance |

### Trial Expiration Screen Design

```
┌─────────────────────────────────────────┐
│  Your trial has ended                    │
│                                          │
│  What you accomplished during trial:     │
│  - Created [N] projects                 │  Personalized data
│  - Invited [N] team members             │
│  - Saved an estimated [X] hours         │
│                                          │
│  What happens now:                       │
│  - Your data is saved for 30 days       │
│  - Read-only access to existing work    │
│  - Full access resumes when you upgrade │
│                                          │
│  [Continue with Pro - $X/mo]            │
│  [Remind Me Later]  [Downgrade to Free] │
└─────────────────────────────────────────┘
```

---

## Timing and Frequency Rules

### Frequency Caps

| Rule | Implementation |
|------|---------------|
| Max 1 paywall per session | Do not interrupt twice in one visit |
| 3-7 day cooldown after dismissal | If they click "Not now", wait at least 3 days |
| Never during active task | If user is creating, editing, or mid-workflow, do not interrupt |
| Cap at 3 per month | After 3 dismissals in a month, stop showing until next month |
| Track annoyance signals | If user closes paywall within 1 second repeatedly, increase cooldown |

### Escalation Pattern

| Attempt | Approach | Invasiveness |
|---------|----------|-------------|
| 1 | Subtle banner or sidebar widget | Low |
| 2 | Modal with value proposition | Medium |
| 3 | Modal with special offer (discount/extended trial) | Medium-High |
| 4+ | Reduce frequency, switch to email nurture | Low (change channel) |

---

## Upgrade Flow Optimization

### From Paywall Click to Payment

| Step | Optimization |
|------|-------------|
| 1. Click upgrade CTA | Opens upgrade flow (do not redirect to external page if avoidable) |
| 2. Plan selection | Pre-select the recommended plan, show comparison |
| 3. Payment | Pre-fill known info (email, name), support all payment methods |
| 4. Confirmation | Immediate access to paid features, confirmation email |
| 5. Post-upgrade | Guide to newly unlocked features, celebration moment |

### Friction Reduction

- Keep the upgrade flow in-context (modal or slide-out, not a full page redirect)
- Pre-fill all known information
- Support saved payment methods and one-click upgrade for returning upgraders
- Show price clearly before the payment step (no surprise charges)

---

## Dark Pattern Avoidance

### Patterns to NEVER Use

| Dark Pattern | Why It Fails | Ethical Alternative |
|-------------|-------------|---------------------|
| Hidden close button | Breaks trust, generates support tickets | Clear X in top-right corner |
| Shame copy ("No, I don't want to grow my business") | Manipulative, reduces brand respect | "Maybe later" or "Not now" |
| Countdown timer (fake urgency) | Users discover it resets, destroys credibility | Only use for genuinely expiring offers |
| Confusing plan selection | Users feel tricked, higher refund rate | Clear plan names with honest comparison |
| Blocking critical actions | Users feel trapped, generates churn | Allow continued use of existing features |
| Making downgrade difficult | Regulatory risk (especially in EU/CA) | One-click downgrade option |

---

## Platform-Specific Considerations

### iOS App Store

- Apple requires in-app purchase (IAP) for digital goods/services
- Apple takes 30% commission (15% for small business program)
- Must comply with App Store Review Guidelines 3.1
- Cannot link to external payment pages from within the app
- Must clearly communicate subscription terms and renewal

### Google Play

- Similar IAP requirements as iOS
- Google Play billing required for digital goods
- 15% commission on first $1M in annual revenue, then 30%
- Must provide clear subscription management

### Web App

- Full control over payment flow and presentation
- Can offer any payment method
- No platform commission
- Can A/B test freely without app review delays

---

## Metrics and Benchmarks

### Key Metrics

| Metric | Formula | Benchmark |
|--------|---------|-----------|
| Paywall impression rate | Users who see paywall / Active users | Track, no universal benchmark |
| Paywall CTR | Upgrade clicks / Paywall impressions | 5-15% |
| Upgrade completion rate | Completed upgrades / Upgrade clicks | 30-60% |
| Free-to-paid conversion | Paid users / Total free users | 2-5% for freemium, 15-30% for trial |
| Revenue per user (ARPU) | Total revenue / Active users | Segment-dependent |
| Post-upgrade churn (30-day) | Churned within 30 days / New paid users | < 10% |

### Warning Signals

| Signal | Diagnosis | Action |
|--------|-----------|--------|
| CTR < 3% | Paywall copy or timing is wrong | Test different triggers and messaging |
| Completion < 20% | Upgrade flow has too much friction | Simplify payment flow |
| Post-upgrade churn > 15% | Value not matching expectations | Review feature access and onboarding |
| Free-to-paid < 1% | Paywall appears before value is delivered | Delay triggers until after activation |

---

## A/B Test Framework

### High-Impact Tests

| Test | Hypothesis | Metric |
|------|-----------|--------|
| Trigger timing (earlier vs later) | Later trigger = higher conversion rate | Free-to-paid conversion |
| Soft gate vs hard gate | Soft gate (preview) converts better | Feature gate CTR |
| Copy variation | Value-focused vs urgency-focused | Paywall CTR |
| Price presentation | Monthly vs annual default | ARPU |

### Test Measurement

- Run for minimum 2 weeks or 100 conversions per variant
- Track upgrade rate AND 30-day post-upgrade retention
- A test that increases upgrades but increases churn is a net negative

---

## Output Artifacts

| Artifact | Format | Description |
|----------|--------|-------------|
| Paywall Trigger Map | Trigger x timing x frequency table | All trigger points with rules and cooldowns |
| Screen Copy Set | Complete screen designs | Headline, benefits, CTA, escape hatch for each paywall type |
| Upgrade Flow Diagram | Step-by-step flow | Paywall click to post-upgrade confirmation |
| Dark Pattern Audit | Checklist | Review of existing paywall for manipulative patterns |
| Trial Expiration Sequence | Day-by-day plan | In-app + email sequence for trial countdown |
| A/B Test Backlog | Prioritized table | Test ideas ranked by expected impact |

---

## Related Skills

- **page-cro** -- Use for public pricing page optimization. Paywall-upgrade-cro handles in-product upgrade moments.
- **onboarding-cro** -- Use when users have not reached activation. Do not show paywalls before the aha moment.
- **pricing-strategy** -- Use when the pricing model itself needs redesigning (tier structure, value metric, price points).
- **churn-prevention** -- Use when users upgrade but then churn. If they never upgrade, the problem is here.
- **signup-flow-cro** -- Use for the initial registration flow. Paywall-upgrade-cro handles post-signup monetization.
