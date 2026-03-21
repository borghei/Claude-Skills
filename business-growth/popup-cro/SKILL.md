---
name: popup-cro
description: Popup and modal optimization for conversion. Covers exit-intent, slide-ins, banners, timing optimization, frequency capping, audience targeting, compliance, and A/B testing frameworks for lead capture, promotions, and announcements.
version: 1.0.0
author: borghei
category: business-growth
tags: [cro, popup, modal, exit-intent, lead-capture, conversion-optimization]
triggers:
  - user wants to create or optimize popups or modals
  - user mentions exit intent, popup conversions, or lead capture popup
  - user asks about slide-in, overlay, or announcement banner
  - user reports low email list growth
  - user has high bounce rate and wants to capture exiting visitors
  - user asks about popup compliance or Google intrusive interstitials
---

# Popup CRO

Production-grade popup optimization framework covering format selection, trigger engineering, audience targeting, frequency capping, copy design, compliance requirements, and structured A/B testing. Handles lead capture, promotional, announcement, and feedback popups across web and mobile.

---

## Table of Contents

- [Initial Assessment](#initial-assessment)
- [Format Selection Matrix](#format-selection-matrix)
- [Trigger Engineering](#trigger-engineering)
- [Audience Targeting](#audience-targeting)
- [Frequency and Suppression Rules](#frequency-and-suppression-rules)
- [Popup Copy Architecture](#popup-copy-architecture)
- [Strategy by Business Type](#strategy-by-business-type)
- [Mobile Popup Design](#mobile-popup-design)
- [Compliance Requirements](#compliance-requirements)
- [Multi-Popup Conflict Resolution](#multi-popup-conflict-resolution)
- [A/B Test Framework](#ab-test-framework)
- [Metrics and Benchmarks](#metrics-and-benchmarks)
- [Output Artifacts](#output-artifacts)
- [Related Skills](#related-skills)

---

## Initial Assessment

### Required Context

| Question | Why It Matters |
|----------|---------------|
| What is the popup purpose? (lead capture, promotion, announcement, feedback) | Determines format and trigger |
| What existing popups are running? | Conflict resolution needed |
| What traffic sources? (paid, organic, direct) | Targeting and trigger strategy |
| New vs returning visitor split? | Personalization opportunity |
| Mobile vs desktop traffic split? | Mobile compliance requirements |
| Current popup performance? (if exists) | Baseline for optimization |
| Any compliance requirements? (GDPR, CCPA) | Legal constraints on data capture |

---

## Format Selection Matrix

| Format | Best For | Intrusiveness | Mobile Friendly | Conversion Rate |
|--------|----------|--------------|-----------------|-----------------|
| Center modal | High-value offers, exit intent | High | With adaptation | 3-10% |
| Slide-in (corner) | Newsletter, content offers | Low | Yes | 1-5% |
| Top bar | Announcements, promotions | Very low | Yes | 0.5-2% |
| Bottom bar | Cookie consent, CTAs | Very low | Yes | 0.5-2% |
| Full-screen overlay | Major promotions, welcome mats | Very high | No (Google penalizes) |2-8% |
| Inline expansion | Content upgrades within articles | Very low | Yes | 2-7% |
| Exit-intent modal | Final capture attempt | Medium | Desktop only | 2-5% |

### Format Decision Tree

```
What is the goal?
├── Lead capture (email)
│   ├── Blog/content page → Slide-in (scroll trigger) or inline expansion
│   ├── Landing page → Exit-intent modal
│   └── Homepage → Time-delayed center modal
├── Promotion/discount
│   ├── E-commerce → Center modal (entry or timed)
│   └── SaaS → Top bar with countdown
├── Announcement
│   ├── New feature → Top bar (sticky)
│   └── Event/webinar → Slide-in or center modal
└── Feedback/survey
    └── Post-interaction → Slide-in (bottom corner)
```

---

## Trigger Engineering

### Trigger Types and Use Cases

| Trigger | How It Works | Best For | Risk |
|---------|-------------|----------|------|
| Exit intent | Mouse moves toward browser close/back | Last-chance capture | Desktop only |
| Time delay | Appears after N seconds | Low-commitment offers | Too early = annoying |
| Scroll depth | Appears at N% scroll | Content-engaged visitors | Must calibrate to content length |
| Page count | Appears after N page views | Multi-visit engagement | Requires cookie tracking |
| Click trigger | User clicks a specific element | Lead magnets, CTAs | Requires obvious trigger element |
| Inactivity | No interaction for N seconds | Re-engagement | Can feel intrusive |

### Optimal Trigger Settings

| Trigger | Setting | Rationale |
|---------|---------|-----------|
| Time delay | 15-30 seconds | < 10s feels aggressive, > 60s misses visitors |
| Scroll depth | 50-70% | User has consumed enough content to be engaged |
| Page count | 2-3 pages | Visitor has shown interest beyond a single page |
| Exit intent | Mouse leaves viewport | Last opportunity before they leave |
| Click trigger | Prominent CTA button or text link | Explicit user intent |

### Trigger Combinations

Layer triggers for better targeting:

| Combination | When to Use |
|------------|-------------|
| Scroll 50% + Time 20s | Ensures both engagement and time on page |
| Page count 3 + Exit intent | Only show to visitors who have browsed multiple pages and are leaving |
| Click trigger + Email not captured | Only show form to non-subscribers |

---

## Audience Targeting

### Segmentation Rules

| Segment | Popup Strategy |
|---------|---------------|
| New visitors (first visit) | Welcome offer, newsletter signup, content upgrade |
| Returning visitors (2-5 visits) | Deeper offer, free trial, demo request |
| Returning visitors (5+ visits) | Direct CTA, consultation offer |
| Email subscribers | Never show email capture popup |
| Existing customers | Feature announcements, upgrade offers only |
| Paid traffic visitors | Message-matched offer, no generic popup |
| Mobile visitors | Non-intrusive format only (slide-in or bottom bar) |

### Exclusion Rules

Always exclude these segments from popups:

- Users who already converted (subscribed, signed up, purchased)
- Users who dismissed the same popup in this session
- Users who dismissed the same popup in the last 7 days
- Users in the checkout or payment flow
- Users on legal/compliance pages (privacy, terms)

---

## Frequency and Suppression Rules

### Frequency Caps

| Rule | Setting | Rationale |
|------|---------|-----------|
| Max popups per session | 1 | Multiple popups per visit destroys trust |
| Cooldown after dismissal | 7 days minimum | Respect the user's "no" |
| Cooldown after close (X button) | 3-7 days | Less aggressive than dismissal |
| Max popups per month | 3-4 | More than this and users feel harassed |
| Post-conversion suppression | Permanent for that popup type | Never ask again once they converted |

### Suppression Priority

If multiple popups compete for the same user in the same session, use this priority:

| Priority | Popup Type | Why |
|----------|-----------|-----|
| 1 | Cookie consent / legal | Required by law |
| 2 | Exit intent (if triggered) | Last chance, highest intent signal |
| 3 | Time-delayed / scroll-triggered | Planned engagement |
| 4 | Announcement bar | Lowest priority, always available |

---

## Popup Copy Architecture

### Anatomy of High-Converting Popup Copy

```
HEADLINE: What they get (benefit-focused, 6-10 words)
SUBHEADLINE: Why they should care (supporting detail, 1 sentence)
[FORM: Minimum fields]
[PRIMARY CTA: Action-oriented, 2-4 words]
[DECLINE TEXT: Respectful, neutral, 3-6 words]
[TRUST ELEMENT: Privacy or social proof, 1 line]
```

### Copy Examples by Type

**Newsletter Signup:**
- Headline: "Get Weekly Growth Tactics"
- Subheadline: "Join 15,000 marketers who get our Tuesday newsletter"
- CTA: "Subscribe"
- Decline: "No thanks"
- Trust: "Unsubscribe anytime. No spam."

**Content Upgrade:**
- Headline: "Get the Full SEO Checklist"
- Subheadline: "85 checks organized by priority. PDF download."
- CTA: "Send Me the Checklist"
- Decline: "I'll skip it"
- Trust: "Free. No credit card required."

**Exit Intent (E-commerce):**
- Headline: "Wait -- 15% Off Your First Order"
- Subheadline: "Use code WELCOME15 at checkout"
- CTA: "Claim My Discount"
- Decline: "I'll pay full price"
- Trust: "Valid for 24 hours"

### Decline Text Rules

- Never use shame language ("No, I don't want to save money")
- Keep it neutral: "No thanks", "Maybe later", "Not now", "I'll skip it"
- Font size should be readable (not tiny text designed to be missed)
- Position clearly below or beside the CTA

---

## Strategy by Business Type

### E-commerce

| Popup | Trigger | Offer |
|-------|---------|-------|
| Welcome discount | Entry (new visitors, 5-second delay) | 10-15% off first order |
| Exit intent | Mouse exit on product/cart page | Higher discount or free shipping |
| Cart abandonment | Return visit after cart abandonment | Reminder + incentive |
| Post-purchase | Thank you page | Referral offer or cross-sell |

### B2B SaaS

| Popup | Trigger | Offer |
|-------|---------|-------|
| Content upgrade | Scroll 50% on blog post | Related PDF, checklist, template |
| Demo request | Pricing page exit intent | "Talk to sales" with calendar link |
| Newsletter | Blog, 3rd page view | Weekly insights email |
| Feature announcement | Login, existing users | New feature with CTA to try it |

### Content / Media

| Popup | Trigger | Offer |
|-------|---------|-------|
| Newsletter | Scroll 60% on article | "Get articles like this weekly" |
| Content gate | After 3 free articles | Subscription or email for access |
| Social follow | Scroll bottom of article | Follow on social platforms |

---

## Mobile Popup Design

### Google Intrusive Interstitials Policy

Google penalizes mobile pages that show intrusive interstitials. Avoid:
- Full-screen popups that cover the main content
- Popups that the user must dismiss before accessing content
- Above-the-fold layouts where the popup pushes content below the fold

### Mobile-Safe Formats

| Format | Mobile Safe? | Notes |
|--------|-------------|-------|
| Bottom bar | Yes | Small, non-blocking |
| Top bar | Yes | Small, dismissable |
| Slide-in (small) | Yes | Corner, < 30% of screen |
| Center modal (small) | Conditional | Only if easily dismissable and shown after engagement |
| Full-screen overlay | No | Penalized by Google |
| Exit intent | N/A | Not available on mobile |

### Mobile Design Rules

- Touch targets minimum 44x44px for close button and CTA
- Close button (X) must be clearly visible and easily tappable
- Popup must not cover more than 50% of the screen
- Form inputs must trigger appropriate mobile keyboards
- Test on actual mobile devices (not just responsive preview)

---

## Compliance Requirements

### GDPR (EU)

- Checkbox for consent (pre-checked is not valid consent)
- Clear privacy policy link
- State what you will do with their email
- Easy unsubscribe in all subsequent emails
- Data processing purpose must be specified

### CCPA (California)

- "Do Not Sell My Personal Information" link if applicable
- Privacy policy must be accessible
- Users can request data deletion

### CAN-SPAM (US)

- Must honor unsubscribe requests within 10 business days
- Must include physical address in emails
- Subject lines cannot be deceptive

### Cookie Consent (EU/UK)

- Cookie consent banner takes priority over all other popups
- Must not set non-essential cookies before consent
- Must offer granular consent options

---

## Multi-Popup Conflict Resolution

### Priority System

If your site runs multiple popups, implement these rules:

1. **Legal popups first** -- Cookie consent before any other popup
2. **One popup per session** -- After legal popup, only one marketing popup
3. **Priority ranking** -- Exit intent > Scroll-triggered > Time-delayed > Announcement bar
4. **No stacking** -- Never show two popups simultaneously
5. **Queue system** -- If multiple popups qualify, show highest priority and suppress the rest for this session

### Implementation Rules

- Maintain a global popup state manager
- Each popup checks the state before rendering
- Record which popups the user has seen, dismissed, or converted on
- Share state across tabs if possible (localStorage)

---

## A/B Test Framework

### High-Impact Tests

| Test | Hypothesis | Metric |
|------|-----------|--------|
| Trigger timing (15s vs 30s vs scroll) | Scroll trigger captures more engaged users | Conversion rate + bounce rate |
| Offer type (discount vs content) | Content offers attract higher-quality leads | Conversion rate + lead quality |
| Copy variation (benefit vs urgency) | Benefit-focused converts better long-term | Conversion rate |
| Format (modal vs slide-in) | Slide-in has lower bounce impact | Conversion rate + bounce rate |
| Decline text (neutral vs shame-free) | Neutral decline text maintains trust | Brand sentiment + repeat visits |

### Test Rules

- Run each test for minimum 1,000 impressions per variant
- Track both popup conversion rate AND page-level metrics (bounce, time on page)
- A popup that converts 10% but increases bounce by 20% is a net negative

---

## Metrics and Benchmarks

### Key Metrics

| Metric | Formula | Benchmark |
|--------|---------|-----------|
| Popup conversion rate | Conversions / Impressions | 2-5% (good), 5-10% (excellent) |
| Popup view rate | Impressions / Eligible page views | Depends on trigger settings |
| Bounce rate impact | Bounce rate with popup - without | Should be < 5% increase |
| Email quality score | Popup leads who engage / Total popup leads | > 30% open subsequent emails |
| Revenue per popup lead | Revenue from popup leads / Total popup leads | Compare to other lead sources |

---

## Output Artifacts

| Artifact | Format | Description |
|----------|--------|-------------|
| Popup Strategy Map | Type x trigger x audience x frequency table | Complete popup inventory with conflict rules |
| Complete Copy Set | Per-popup copy | Headline, subheadline, CTA, decline text, trust element |
| Mobile Adaptation Guide | Per-format recommendations | Mobile-safe formats, sizing, dismiss behavior |
| Compliance Checklist | Per-regulation requirements | GDPR, CCPA, CAN-SPAM, cookie consent |
| A/B Test Plan | Prioritized table | Hypotheses ranked by expected impact |
| Multi-Popup Priority Map | Priority ranking | Conflict resolution rules for concurrent popups |

---

## Tool Reference

### 1. popup_strategy_auditor.py

Audits existing popup configurations for compliance, frequency conflicts, targeting gaps, and mobile safety. Reads a JSON inventory of popups and flags issues against best practices.

```bash
python scripts/popup_strategy_auditor.py popups.json --format text
python scripts/popup_strategy_auditor.py popups.json --format json
```

| Flag | Type | Description |
|------|------|-------------|
| `popups.json` | positional | Path to JSON file with popup inventory and rules |
| `--format` | optional | Output format: `text` (default) or `json` |

### 2. popup_ab_test_calculator.py

Calculates statistical significance for popup A/B tests. Takes impressions and conversions for control and variant, computes conversion rates, relative lift, confidence level, and recommends whether to ship, continue testing, or abandon.

```bash
python scripts/popup_ab_test_calculator.py test.json --format text
python scripts/popup_ab_test_calculator.py test.json --format json
```

| Flag | Type | Description |
|------|------|-------------|
| `test.json` | positional | Path to JSON file with A/B test data |
| `--format` | optional | Output format: `text` (default) or `json` |

### 3. popup_roi_estimator.py

Estimates revenue impact of popup lead capture by modeling lead volume, conversion rates, and customer lifetime value. Compares popup-sourced leads against other channels.

```bash
python scripts/popup_roi_estimator.py roi_data.json --format text
python scripts/popup_roi_estimator.py roi_data.json --format json
```

| Flag | Type | Description |
|------|------|-------------|
| `roi_data.json` | positional | Path to JSON file with popup performance and revenue data |
| `--format` | optional | Output format: `text` (default) or `json` |

---

## Troubleshooting

| Problem | Likely Cause | Resolution |
|---------|-------------|------------|
| Popup conversion rate below 2% | Wrong trigger timing, weak offer, or poor copy | Test scroll-triggered (50-70%) vs time-delayed; use benefit-focused headline; add countdown timer (lifts to 14.4% avg per 2026 benchmarks) |
| Bounce rate increases >5% after adding popup | Popup fires too early or covers too much screen on mobile | Increase time delay to 15-30s or switch to scroll trigger; use slide-in format instead of center modal |
| Email list quality drops (low open rates from popup leads) | Generic offer attracts low-intent subscribers | Switch to content upgrade offers specific to the page; add qualification question |
| Multiple popups fire in same session | No global popup state manager or priority system implemented | Implement session-level state tracking via localStorage; enforce one-popup-per-session rule with priority ranking |
| Mobile popup triggers Google penalty | Full-screen overlay or popup covers content before engagement | Switch to bottom bar, slide-in (<30% screen), or inline expansion format; test with Google Mobile-Friendly Tool |
| Exit-intent not working on mobile | Exit-intent relies on mouse movement which does not exist on mobile | Use scroll-up or inactivity trigger as mobile alternative; segment trigger rules by device type |
| Cookie consent popup conflicts with marketing popup | No priority system; both fire simultaneously | Legal popups always take priority; queue marketing popup to fire only after consent is given |

---

## Success Criteria

- Popup conversion rate reaches 3-5% (good) or 5-10% (excellent) within 30 days of optimization
- Bounce rate impact stays below 5% increase compared to no-popup baseline
- Email lead quality maintains >30% open rate on subsequent emails from popup-sourced leads
- Mobile popup compliance passes Google Mobile-Friendly Test with zero warnings
- Frequency capping limits impressions to max 1 per session and 3-4 per month per user
- Zero GDPR/CCPA compliance violations in popup consent flows
- Gamified or countdown-enhanced popups reach 13%+ average conversion rate (2026 benchmark)

---

## Scope & Limitations

**In scope:** Popup and modal format selection, trigger engineering, audience targeting, frequency capping, copy architecture, mobile-safe design, multi-popup conflict resolution, compliance requirements (GDPR, CCPA, CAN-SPAM, cookie consent), and structured A/B testing for lead capture, promotional, announcement, and feedback popups.

**Out of scope:** Form field-level optimization within popups (use form-cro), page-level conversion optimization around the popup (use page-cro), in-app onboarding modals and tooltips (use onboarding-cro), registration flows triggered by popups (use signup-flow-cro). Scripts operate on local data only -- no integrations with popup platforms (OptinMonster, Wisepops, etc.) or analytics tools.

**Limitations:** Conversion benchmarks are aggregate industry averages from 2025-2026 studies (Popupsmart 10K+ campaigns, Wisepops 1B+ displays) and vary significantly by industry, traffic source, and offer type. Exit-intent detection is desktop-only; mobile alternatives (scroll-up, inactivity) have different performance characteristics. Google intrusive interstitial penalties apply to mobile search traffic specifically -- direct/paid traffic is less affected.

---

## Integration Points

- **form-cro** -- Popup form fields should follow form-cro field reduction and validation standards
- **page-cro** -- Page conversion should be optimized before layering popups; popup performance depends on page quality
- **signup-flow-cro** -- Popup-to-signup handoff should maintain context and pre-fill captured email
- **paywall-upgrade-cro** -- In-app upgrade modals share frequency capping and UX principles with marketing popups
- **onboarding-cro** -- Product onboarding tooltips and modals should use separate state management from marketing popups
- **referral-program** -- Post-purchase or post-conversion popups can trigger referral program prompts

---

## Related Skills

- **form-cro** -- Use when the form inside the popup needs field-level optimization (field count, validation, layout).
- **page-cro** -- Use when the page surrounding the popup needs conversion optimization. Fix the page first, then add popups.
- **onboarding-cro** -- Use when popups/modals are part of in-app onboarding (tooltips, checklists, feature tours).
- **signup-flow-cro** -- Use when the popup leads into a registration flow that needs optimization.
