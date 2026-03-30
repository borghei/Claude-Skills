---
name: analytics-tracking
description: >
  End-to-end analytics implementation for web and SaaS products. Covers GA4
  configuration, Google Tag Manager setup, event taxonomy design, conversion
  tracking across Google Ads and Meta, cross-domain tracking, UTM strategy,
  consent management, and data quality auditing. Use when building a tracking
  plan, debugging missing events, setting up GTM, or auditing existing
  analytics.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: marketing
  domain: analytics-implementation
  updated: 2026-03-09
  frameworks: ga4, gtm, event-taxonomy, conversion-tracking
---
# Analytics Tracking - Implementation & Auditing

**Category:** Marketing
**Tags:** GA4, Google Tag Manager, event tracking, conversion tracking, UTM, analytics audit, consent mode

## Overview

Analytics Tracking is the implementation layer for marketing measurement. Bad tracking is worse than no tracking -- duplicate events, missing parameters, unconsented data, and broken conversions lead to decisions based on bad data. This skill covers building tracking right the first time and finding what is broken when it is not.

This skill handles implementation only. For analyzing campaign performance data, use campaign-analytics. For product analytics and in-app behavior, use the product-team skills.

---

## Operating Modes

### Mode 1: Build From Scratch
No analytics in place. Build the tracking plan, implement GA4 + GTM, define event taxonomy, configure conversions.

### Mode 2: Audit Existing Tracking
Tracking exists but data cannot be trusted. Audit coverage, identify gaps, clean up duplicates, fix consent issues.

### Mode 3: Debug Specific Issues
Events are missing, conversions do not match, GTM preview shows fires but GA4 does not record. Structured debugging workflow.

---

## Event Taxonomy Design

Get this right before touching GA4 or GTM. Retrofitting taxonomy is painful and expensive.

### Naming Convention

**Format:** `object_action` (snake_case, past tense verb)

| Correct | Wrong | Why Wrong |
|---------|-------|-----------|
| `form_submitted` | `submitForm` | camelCase, verb-first |
| `plan_selected` | `clickPricingPlan` | Implementation detail, not user action |
| `video_started` | `VideoStart` | PascalCase, inconsistent tense |
| `checkout_completed` | `purchase` | Ambiguous, not a verb phrase |

**Rules:**
1. Always `noun_verb` order, never `verb_noun`
2. Snake_case only -- no camelCase, no hyphens, no PascalCase
3. Past tense verbs: `_started`, `_completed`, `_failed`, `_viewed`
4. Specific enough to be unambiguous, not so verbose it is a sentence
5. Prefix with domain when needed: `onboarding_step_completed`, `billing_plan_selected`

### Standard Event Parameters

Every custom event should include applicable parameters from this table:

| Parameter | Type | Example | Required When |
|-----------|------|---------|---------------|
| `user_id` | string | `usr_abc123` | Always (if authenticated) |
| `plan_name` | string | `professional` | Billing/pricing events |
| `value` | number | `99.00` | Revenue events |
| `currency` | string | `USD` | Always with value |
| `content_group` | string | `onboarding` | Page/flow grouping |
| `method` | string | `google_oauth` | Signup/login events |
| `step_name` | string | `connect_account` | Multi-step flows |
| `step_number` | number | `3` | Multi-step flows |
| `source` | string | `pricing_page` | CTA click events |

### SaaS Event Taxonomy (Reference)

**Core Funnel:**
```
visitor_arrived              (automatic page_view in GA4)
signup_started               (user clicked "Sign up")
signup_completed             (account created)
trial_started                (free trial began)
onboarding_step_completed    (params: step_name, step_number)
feature_activated            (params: feature_name)
plan_selected                (params: plan_name, billing_period)
checkout_started             (params: value, currency, plan_name)
checkout_completed           (params: value, currency, transaction_id)
subscription_renewed         (params: value, plan_name)
subscription_cancelled       (params: cancel_reason, plan_name)
```

**Micro-Conversions:**
```
pricing_viewed
demo_requested               (params: source)
form_submitted               (params: form_name, form_location)
content_downloaded           (params: content_name, content_type)
video_started                (params: video_title)
video_completed              (params: video_title, percent_watched)
chat_opened
help_article_viewed          (params: article_name)
invite_sent                  (params: recipient_role)
integration_connected        (params: integration_name)
```

---

## GA4 Configuration

### Data Stream Setup

1. Create property: GA4 Admin > Properties > Create
2. Add web data stream with your domain
3. Enhanced Measurement -- review each:
   - Page views: Keep enabled
   - Scrolls: Keep enabled
   - Outbound clicks: Keep enabled
   - Site search: Enable if you have search
   - Video engagement: Disable if tracking videos manually (avoids duplicates)
   - File downloads: Disable if tracking via GTM (for better parameters)
4. Configure domains: add all subdomains in your funnel
5. Data retention: Set to 14 months (maximum for free GA4)

### Conversion Events

Mark as conversions in GA4 Admin > Conversions:
- `signup_completed`
- `checkout_completed`
- `demo_requested`
- `trial_started`

**Rules:**
- Maximum 30 conversion events per property -- curate carefully
- GA4 conversions are retroactive for 6 months when enabled
- Do not mark micro-conversions as conversions unless optimizing ad campaigns for them
- Conversion counting: set to "once per session" for lead events, "every" for purchase events

### Custom Dimensions

Register custom dimensions for any event parameter you want to filter/segment by:

| Parameter | Scope | Dimension Name |
|-----------|-------|----------------|
| `plan_name` | Event | Plan Name |
| `user_id` | User | User ID |
| `content_group` | Event | Content Group |
| `feature_name` | Event | Feature Name |

Register in GA4 Admin > Custom definitions > Create custom dimension.

---

## Google Tag Manager Implementation

### Container Architecture

```
GTM Container
├── Tags
│   ├── GA4 Configuration (All Pages trigger)
│   ├── GA4 Event Tags (one per custom event)
│   ├── Google Ads Conversion Tags (per conversion action)
│   └── Meta Pixel / LinkedIn Insight (if running ads)
├── Triggers
│   ├── All Pages (Page View)
│   ├── DOM Ready
│   ├── Custom Event triggers (one per dataLayer event)
│   └── Element Click triggers (CSS selector based)
└── Variables
    ├── Data Layer Variables (one per dataLayer key)
    ├── Constants (GA4 Measurement ID, etc.)
    └── Lookup Tables (if needed for mapping)
```

### Implementation Pattern: Data Layer Push

Your application pushes events to the data layer. GTM picks them up and sends to GA4.

**Application code:**
```javascript
// Push event when user completes signup
window.dataLayer = window.dataLayer || [];
window.dataLayer.push({
  event: 'signup_completed',
  method: 'email',
  user_id: userId,
  plan_name: 'trial'
});
```

**GTM configuration:**
```
Trigger:
  Type: Custom Event
  Event name: signup_completed

Tag:
  Type: GA4 Event
  Event name: signup_completed
  Parameters:
    method:    {{DLV - method}}
    user_id:   {{DLV - user_id}}
    plan_name: {{DLV - plan_name}}
```

### SPA Handling

Single Page Applications need special attention because page views do not fire automatically on route changes.

**Option A: History change trigger (GTM built-in)**
- Enable "History Change" trigger in GTM
- Fires GA4 page_view on every pushState/popState

**Option B: DataLayer push on route change (more control)**
```javascript
// In your router (React Router, Next.js, etc.)
router.events.on('routeChangeComplete', (url) => {
  window.dataLayer.push({
    event: 'page_view',
    page_location: url,
    page_title: document.title
  });
});
```

---

## Conversion Tracking: Ad Platforms

### Google Ads

**Recommended approach:** Import GA4 conversions into Google Ads (single source of truth).

1. Link GA4 and Google Ads accounts
2. In Google Ads > Goals > Conversions > Import > Google Analytics
3. Select GA4 conversion events to import
4. Set attribution model: Data-driven (if 50+ conversions/month), otherwise Last-click
5. Conversion window: 30 days for lead gen, 90 days for high-consideration B2B

**Enhanced Conversions:** Enable for 15-30% better conversion measurement. Sends hashed first-party data (email, phone) to match conversions that cookies miss.

### Meta (Facebook/Instagram)

1. Install Meta Pixel base code via GTM
2. Configure standard events: `PageView`, `Lead`, `CompleteRegistration`, `Purchase`
3. Conversions API (CAPI): strongly recommended -- client-side pixel loses approximately 30% of conversions due to ad blockers and iOS App Tracking Transparency
4. Deduplication: when using both pixel and CAPI, send the same `event_id` to prevent double-counting

### LinkedIn Insight Tag

1. Install via GTM (Tag type: LinkedIn Insight)
2. Configure conversion events in LinkedIn Campaign Manager
3. Match events to your taxonomy: `signup_completed` -> LinkedIn "Sign-up" conversion

---

## UTM Strategy

### Convention Enforcement

| Parameter | Convention | Example |
|-----------|-----------|---------|
| `utm_source` | Platform name, lowercase | `google`, `linkedin`, `newsletter` |
| `utm_medium` | Traffic type | `cpc`, `email`, `social`, `organic` |
| `utm_campaign` | Campaign identifier | `q1-trial-push`, `brand-awareness-2026` |
| `utm_content` | Creative variant | `hero-cta-blue`, `sidebar-text-link` |
| `utm_term` | Paid keyword (search only) | `saas-analytics-tool` |

**Critical rules:**
- Never tag organic traffic with UTMs (overrides GA4 automatic attribution)
- Never tag direct/internal links with UTMs
- Use a UTM builder spreadsheet or tool -- manual entry causes inconsistency
- Lowercase everything -- `Google` and `google` are different sources in GA4

### Attribution Windows

| Platform | Default | Recommended for SaaS |
|---------|---------|---------------------|
| GA4 | 30 days | 30-90 days (match your sales cycle) |
| Google Ads | 30 days | 30 days (trial), 90 days (enterprise) |
| Meta | 7-day click, 1-day view | 7-day click only (view-through inflates) |
| LinkedIn | 30 days | 30 days |

---

## Cross-Domain Tracking

For funnels crossing domains (e.g., `acme.com` to `app.acme.com`):

1. GA4 Admin > Data Streams > Configure tag settings > Configure your domains > Add both domains
2. GTM: GA4 Configuration tag > Fields to Set > `linker` > Add domains
3. Admin > Data Streams > List unwanted referrals > Add both domains

**Verification:** Visit domain A, click link to domain B, check GA4 DebugView. The session should NOT restart. If a new session starts, cross-domain tracking is broken.

---

## Consent Management

### Consent Mode v2

Required for EU compliance and for maintaining data quality in consent-heavy markets.

| Setting | No Consent Mode | Basic | Advanced |
|---------|----------------|-------|----------|
| User declines cookies | Zero data | Zero data | Modeled data (GA4 estimates) |
| Data quality impact | 25-40% data loss in EU | 25-40% data loss | 5-15% data loss |
| Implementation effort | None | Medium | Medium-High |

**Recommendation:** Implement Advanced Consent Mode v2 via GTM with a CMP (Cookiebot, OneTrust, Usercentrics).

**Expected consent rates by region:**
- EU/EEA: 60-75%
- UK: 70-80%
- US: 85-95%
- Rest of world: 80-90%

### Implementation via GTM

```
1. Install CMP tag (fires first, before any other tags)
2. Set default consent state:
   - analytics_storage: denied
   - ad_storage: denied
   - ad_user_data: denied
   - ad_personalization: denied
3. CMP updates consent state on user choice
4. GA4 and ad tags respect consent automatically
```

---

## Data Quality Auditing

### Audit Checklist

**Event Quality:**
- [ ] No duplicate events (check GTM Preview for double-fires)
- [ ] All custom events have required parameters
- [ ] Event names follow naming convention
- [ ] No PII in event parameters (names, emails, phone numbers)
- [ ] Enhanced Measurement not duplicating GTM custom events

**Configuration Quality:**
- [ ] Data retention set to 14 months
- [ ] Internal traffic filter enabled (office and developer IPs)
- [ ] Bot filtering enabled (default in GA4)
- [ ] Cross-domain tracking working (if applicable)
- [ ] Custom dimensions registered for filtered parameters
- [ ] Conversion events marked correctly

**Consent Quality:**
- [ ] Consent Mode v2 implemented (if serving EU users)
- [ ] CMP banner appearing on first visit
- [ ] Tags respect consent state (no firing before consent)
- [ ] Consent state persisting across pages

### Common Data Quality Issues

| Issue | Symptom | Root Cause | Fix |
|-------|---------|------------|-----|
| Inflated page views | 2x expected volume | GTM page_view + Enhanced Measurement | Disable Enhanced page_view |
| Missing conversions | GA4 and Ads numbers differ | Attribution window mismatch | Align windows |
| (not set) pages | Pages show as "/(not set)" | SPA routing not handled | Implement SPA tracking |
| Self-referrals | Own domain in referral report | Missing cross-domain config | Add domains to referral exclusion |
| Direct traffic spike | Paid traffic showing as direct | UTMs missing or stripped | Audit UTM usage |
| Zero EU data | No traffic from EU markets | Consent blocks all tracking | Implement Advanced Consent Mode |

### Debugging Workflow

```
Step 1: Open GTM Preview mode
  - Is the tag firing? Check triggers and conditions
  - Is the data layer populated? Check dataLayer in console

Step 2: Check GA4 DebugView (Admin > DebugView)
  - Is the event appearing? If yes, GTM is working
  - Are parameters populated? Check parameter values

Step 3: Check GA4 Realtime report
  - Events appearing with 5-minute delay? Normal
  - Events not appearing at all? Check measurement ID

Step 4: Check Network tab (DevTools)
  - Filter by "collect" or "analytics"
  - Is the request being sent? Check status code
  - Is the request being blocked? Check ad blockers / consent
```

---

## Proactive Triggers

Surface these findings without being asked:

- Events firing on every page load with identical parameters: misconfigured trigger causing data inflation
- No `user_id` parameter on authenticated events: cannot connect analytics to CRM or understand cohorts
- GA4 conversion count differs from Google Ads by more than 15%: attribution window or deduplication issue
- No consent mode in EU markets: legal exposure and 25-40% data underreporting
- All pages showing as `/(not set)`: SPA routing not handled properly
- `utm_source` showing as `direct` for known paid campaigns: UTMs missing or being stripped by redirects

---

## Related Skills

| Skill | Use When |
|-------|----------|
| **campaign-analytics** | Analyzing marketing performance and channel ROI (not implementation) |
| **ab-test-setup** | Designing experiments (this skill's events feed A/B tests) |
| **launch-strategy** | Tracking events for product launches |
| **email-sequence** | Setting up email click tracking and UTM parameters |

---

## Troubleshooting

| Symptom | Likely Cause | Resolution |
|---------|-------------|------------|
| GA4 shows 50% less traffic than expected after privacy changes | Client-side tracking blocked by ad blockers and ITP/ETP cookie expiry | Implement server-side GTM tagging — recovers 20-40% of lost attribution data within first quarter |
| Conversion counts differ between GA4 and Google Ads by >15% | Attribution window mismatch or deduplication failure between pixel and CAPI | Align attribution windows across platforms and ensure matching `event_id` for deduplication |
| Events fire in GTM Preview but do not appear in GA4 reports | Measurement ID mismatch, consent mode blocking, or data processing delay | Check Measurement ID in GA4 Configuration tag, verify consent state, wait 24-48 hours for standard reports |
| UTM parameters show as (not set) in GA4 | UTMs stripped by redirects, social platform link wrappers, or internal links overwriting | Audit redirect chains, use UTM-safe shorteners, never tag internal links with UTMs |
| Server-side container returns 400 errors | Malformed event payload or missing required fields in Measurement Protocol requests | Validate payload against GA4 Measurement Protocol schema, check required `client_id` and `api_secret` |
| Enhanced Measurement duplicating custom GTM events | Both Enhanced Measurement and GTM firing the same event type (e.g., page_view, scroll) | Disable the overlapping Enhanced Measurement toggle for events you track via GTM |
| Consent Mode v2 reporting zero EU data instead of modeled data | Default consent state not set before GA4 tag fires, or CMP not updating consent correctly | Ensure consent defaults fire as the very first tag in GTM before all other tags |

---

## Success Criteria

- All custom events follow consistent `noun_verb` snake_case naming convention with zero violations in schema audit
- GA4 conversion counts match ad platform conversion counts within 10% variance
- Server-side tracking recovers 20%+ of previously lost attribution data within 90 days of deployment
- UTM parameter validation passes 100% on all active campaigns (no mixed case, no spaces, no missing required params)
- Consent Mode v2 limits EU data loss to under 15% via behavioral modeling
- Event parameters contain zero PII violations as verified by automated schema checker
- Data retention set to 14 months, internal traffic filtered, and cross-domain tracking verified

---

## Scope & Limitations

**In Scope:** GA4 configuration, GTM implementation, event taxonomy design, conversion tracking setup, UTM strategy, consent management, data quality auditing, server-side tagging architecture, cross-domain tracking, ad platform conversion integration (Google Ads, Meta, LinkedIn).

**Out of Scope:** Product analytics platforms (Amplitude, Mixpanel), data warehouse configuration, custom ETL pipelines, mobile app tracking (Firebase), marketing attribution modeling (see marketing-analyst skill), A/B test statistical analysis (see ab-test-setup skill).

**Limitations:** Server-side tracking requires a cloud-hosted GTM container (GCP, AWS, or third-party) with associated infrastructure costs. Privacy-first analytics with Consent Mode v2 produces modeled data for non-consented users — modeled data has 5-15% variance from actual. This skill does not make LLM or API calls; all validation is deterministic.

---

## Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/utm_validator.py` | Validate UTM parameters for consistency and naming conventions | `python scripts/utm_validator.py urls.csv --json` |
| `scripts/event_schema_checker.py` | Validate event names and parameters against taxonomy, detect PII | `python scripts/event_schema_checker.py events.json --json` |
| `scripts/funnel_drop_off_analyzer.py` | Analyze conversion funnels and identify biggest drop-off points | `python scripts/funnel_drop_off_analyzer.py --stages "Visitors:10000,Signups:1200,Paid:120"` |
