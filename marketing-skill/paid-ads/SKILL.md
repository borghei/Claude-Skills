---
name: paid-ads
description: Plan, execute, and optimize paid advertising campaigns across Google Ads, Meta Ads, LinkedIn Ads, Twitter/X, and TikTok. Covers campaign structure, audience targeting, budget allocation, bid strategies, retargeting, attribution, and performance optimization. Use when running PPC campaigns, setting up ad accounts, optimizing ROAS/CPA, or when user mentions paid ads, PPC, Google Ads, Meta Ads, LinkedIn Ads, ad campaigns, retargeting, audience targeting, budget optimization, ROAS, CPA, or ad performance.
license: MIT
metadata:
  version: 1.0.0
  author: borghei
  category: marketing
  domain: advertising
  updated: 2026-03-09
---

# Paid Ads

Campaign strategy, audience targeting, budget optimization, and performance management across all major advertising platforms.

---

## Table of Contents

- [Keywords](#keywords)
- [Quick Start](#quick-start)
- [Platform Selection Guide](#platform-selection-guide)
- [Campaign Structure Framework](#campaign-structure-framework)
- [Audience Targeting by Platform](#audience-targeting-by-platform)
- [Budget Allocation Strategy](#budget-allocation-strategy)
- [Bid Strategy Progression](#bid-strategy-progression)
- [Retargeting Playbook](#retargeting-playbook)
- [Performance Optimization](#performance-optimization)
- [Attribution and Measurement](#attribution-and-measurement)
- [Pre-Launch Checklist](#pre-launch-checklist)
- [Best Practices](#best-practices)
- [Integration Points](#integration-points)

---

## Keywords

paid ads, PPC, pay-per-click, Google Ads, Meta Ads, Facebook Ads, Instagram Ads, LinkedIn Ads, Twitter Ads, TikTok Ads, paid media, ROAS, CPA, CPC, CPM, audience targeting, retargeting, remarketing, budget optimization, bid strategy, ad campaigns, conversion tracking, lookalike audiences, campaign structure, ad performance, paid search, paid social

---

## Quick Start

### Launch a Campaign

1. Define campaign goal (leads, sales, traffic, awareness)
2. Select platform based on audience and intent
3. Set up conversion tracking and verify with test conversion
4. Build campaign structure with proper naming conventions
5. Define audience targeting
6. Set budget and bid strategy
7. Create ad creative (use Ad Creative skill)
8. Launch and monitor for 7 days before making changes

### Optimize an Existing Campaign

1. Pull performance data for last 14-30 days
2. Identify primary issue (high CPA, low CTR, low ROAS)
3. Use the optimization levers in the Performance Optimization section
4. Make one change at a time, wait 3-5 days between changes
5. Document every change and its impact

---

## Platform Selection Guide

### Platform Comparison

| Platform | Best For | Audience Signal | Typical CPC | Minimum Budget |
|----------|----------|----------------|-------------|----------------|
| **Google Search** | High-intent demand capture | Search keywords (what they want now) | $1-8 (B2B: $5-20) | $1,500/mo |
| **Google Display** | Awareness, retargeting | Browsing behavior, interests | $0.30-1.50 | $1,000/mo |
| **Google Performance Max** | Multi-format automation | Mixed signals, Google's ML | Varies | $2,000/mo |
| **Meta (FB/IG)** | Demand generation, B2C, visual products | Interests, behaviors, lookalikes | $0.50-3.00 | $1,000/mo |
| **LinkedIn** | B2B, decision-maker targeting | Job title, company, industry, seniority | $5-15 | $2,000/mo |
| **Twitter/X** | Tech audiences, thought leadership | Followers, interests, keywords | $0.50-3.00 | $500/mo |
| **TikTok** | 18-34 demographics, brand awareness | Interests, behaviors, creator affinity | $0.30-1.50 | $1,000/mo |
| **Reddit** | Niche communities, tech/gaming | Subreddit targeting | $0.50-2.00 | $500/mo |

### Platform Selection Decision Tree

```
Is the audience actively searching for your solution?
├── Yes → Google Search Ads
└── No → Do you know their job title or company?
    ├── Yes → LinkedIn Ads (B2B) or Meta Ads (B2C)
    └── No → Is your product visual or lifestyle?
        ├── Yes → Meta Ads (Instagram) or TikTok
        └── No → Is your audience technical?
            ├── Yes → Reddit Ads or Twitter/X
            └── No → Meta Ads (Facebook) or Google Display
```

---

## Campaign Structure Framework

### Account Hierarchy

```
Account
├── Campaign 1: [Objective] - [Product/Offer]
│   ├── Ad Group/Set 1: [Audience Segment A]
│   │   ├── Ad 1: [Creative Variant 1]
│   │   ├── Ad 2: [Creative Variant 2]
│   │   └── Ad 3: [Creative Variant 3]
│   └── Ad Group/Set 2: [Audience Segment B]
│       ├── Ad 1: [Creative Variant 1]
│       └── Ad 2: [Creative Variant 2]
└── Campaign 2: [Objective] - [Product/Offer]
```

### Naming Conventions

```
[Platform]_[Objective]_[Audience]_[Offer]_[Date]

Examples:
GOOG_Search_Brand_FreeTrial_2026Q1
META_Conv_Lookalike-Customers_Demo_Mar26
LI_LeadGen_CMOs-SaaS-500_Whitepaper_2026Q1
TIKTOK_Aware_18-34-Tech_BrandVideo_Mar26
```

### Campaign Types by Objective

| Objective | Google | Meta | LinkedIn |
|-----------|--------|------|----------|
| Awareness | Display, YouTube, PMax | Reach, Video Views | Brand Awareness |
| Consideration | Search, Display | Traffic, Engagement | Website Visits |
| Conversion | Search, PMax | Conversions, Leads | Lead Gen Forms |
| Retargeting | Display, Search (RLSA) | Custom Audiences | Matched Audiences |

---

## Audience Targeting by Platform

### Google Ads Targeting

| Targeting Type | Use When | How |
|---------------|----------|-----|
| Keyword targeting | Capturing search intent | Exact, phrase, and broad match keywords |
| Audience targeting | Layering intent signals | In-market, affinity, custom intent |
| RLSA | Retargeting in search | Website visitor lists on search campaigns |
| Customer Match | Targeting known contacts | Upload email lists for matched targeting |
| Similar audiences | Expanding from known customers | Google's lookalike from customer lists |

**Keyword match type strategy:**
- **Exact match** [keyword]: Highest intent, lowest volume, highest CPC
- **Phrase match** "keyword": Medium intent, medium volume
- **Broad match** keyword: Lowest intent, highest volume, lowest CPC (use with smart bidding)

### Meta Ads Targeting

| Targeting Type | Use When | How |
|---------------|----------|-----|
| Interest targeting | Cold prospecting | Layer 2-3 related interests |
| Lookalike audiences | Expanding from customers | 1-3% lookalike from best customers (by LTV) |
| Custom audiences | Retargeting | Website visitors, email lists, video viewers |
| Broad targeting | Trusting Meta's ML | No targeting restrictions, let the algorithm find converters |
| Detailed targeting | Narrow audience needed | Combine demographics + interests + behaviors |

**Lookalike best practices:**
- Seed with best customers (by LTV), not all customers
- Start with 1% lookalike (most similar), expand to 3-5% once proven
- Create separate lookalikes from different seeds (customers, trial users, email subscribers)

### LinkedIn Ads Targeting

| Targeting Type | Use When | How |
|---------------|----------|-----|
| Job title | Targeting decision-makers | Specific titles (CMO, VP Marketing, Head of Growth) |
| Job function | Broader role targeting | Marketing, Engineering, Finance |
| Company size | Enterprise vs. SMB | Employee count ranges |
| Industry | Vertical-specific campaigns | LinkedIn's industry categories |
| Seniority | C-suite vs. individual contributor | Manager, Director, VP, CXO |
| Skills | Technical targeting | Listed skills on profiles |
| Company list | ABM targeting | Upload target account lists |

**LinkedIn targeting rules:**
- Minimum audience size: 50,000 for awareness, 20,000 for conversion
- Layer 2-3 targeting dimensions maximum (more layers = too narrow)
- Exclude competitors, agencies, and job seekers if not relevant

---

## Budget Allocation Strategy

### Budget by Campaign Phase

**Phase 1: Testing (Weeks 1-4)**

| Allocation | Purpose |
|-----------|---------|
| 40% | Proven/safe campaigns (brand search, retargeting) |
| 40% | Testing new audiences and creative |
| 20% | Experimental channels or formats |

**Phase 2: Optimization (Weeks 5-8)**

| Allocation | Purpose |
|-----------|---------|
| 60% | Winning combinations from testing |
| 25% | Iterating on promising but unproven |
| 15% | New tests |

**Phase 3: Scaling (Weeks 9+)**

| Allocation | Purpose |
|-----------|---------|
| 70% | Proven performers |
| 20% | Expansion (new audiences, lookalikes, broader targeting) |
| 10% | Ongoing testing |

### Budget Scaling Rules

- Increase budget by 20-30% at a time, never more
- Wait 3-5 days between increases for algorithm learning
- Monitor CPA for 48 hours after increase — if CPA spikes, hold
- Never double a budget overnight (disrupts algorithm learning)
- If CPA increases > 30% after scaling, revert and investigate

### Budget Minimums by Platform

| Platform | Minimum Viable Monthly Budget | Optimal Monthly Budget |
|----------|------------------------------|----------------------|
| Google Search | $1,500 | $5,000+ |
| Google Display | $1,000 | $3,000+ |
| Meta Ads | $1,000 | $3,000+ |
| LinkedIn Ads | $2,000 | $5,000+ |
| TikTok Ads | $1,000 | $3,000+ |
| Reddit Ads | $500 | $2,000+ |

---

## Bid Strategy Progression

### Strategy Ladder

| Stage | Strategy | When to Use | Requirements |
|-------|----------|-------------|-------------|
| 1 | Manual CPC | Starting out, need control | None |
| 2 | Max Clicks | Building traffic data | Budget cap set |
| 3 | Target CPA | Optimizing for conversions | 30+ conversions/month |
| 4 | Target ROAS | Optimizing for revenue | 50+ conversions/month + revenue data |
| 5 | Value-based | Maximizing revenue | Conversion value tracking, 100+ conversions/month |

### Bid Strategy Rules

- Start with Manual CPC or Max Clicks until you have conversion data
- Switch to automated bidding after 30+ conversions in 30 days
- Set CPA targets 10-20% above your actual target (give the algorithm room)
- Never change bid strategy and creative at the same time
- Allow 14 days of learning phase after switching strategies

---

## Retargeting Playbook

### Funnel-Based Retargeting

| Funnel Stage | Audience | Message | Window | Frequency |
|-------------|----------|---------|--------|-----------|
| Top | Blog readers, video viewers | Educational, social proof | 30-90 days | 1-2x/week |
| Middle | Pricing/feature page visitors | Case studies, demos, comparisons | 7-30 days | 3-5x/week |
| Bottom | Cart/trial abandoners | Urgency, objection handling, offer | 1-7 days | Daily OK |

### Retargeting Audience Setup

| Audience | Source | Platform | Priority |
|----------|--------|----------|----------|
| All website visitors (30 days) | Pixel | All platforms | Medium |
| Pricing page visitors (14 days) | Pixel | All platforms | High |
| Cart/trial abandoners (7 days) | Pixel + Events | All platforms | Highest |
| Email subscribers (non-customers) | Email list | Meta, LinkedIn | Medium |
| Video viewers (50%+ watched) | Platform event | Meta, YouTube | Medium |
| Blog readers (engaged, 60s+) | Pixel + Events | All platforms | Low-Medium |

### Exclusions (Critical)

Always exclude:
- Existing paying customers (unless running upsell campaigns)
- Recent converters (7-14 day exclusion window)
- Bounced visitors (under 10 seconds on site)
- Irrelevant page visitors (careers, support, legal)
- Competitor employees (LinkedIn)

---

## Performance Optimization

### Optimization Decision Tree

```
Is CPA above target?
├── CTR is low (< 1% search, < 0.5% social)
│   ├── Creative fatigue? → Refresh creative
│   ├── Audience mismatch? → Refine targeting
│   └── Ad relevance low? → Improve message match
├── CTR is good, conversion rate low
│   ├── Landing page issue? → Audit page (speed, copy, CTA)
│   ├── Offer mismatch? → Align ad promise with page offer
│   └── Audience too broad? → Narrow targeting
└── CTR and CVR are good, CPA still high
    ├── CPM too high? → Try different placements/platforms
    ├── Competition driving up bids? → Adjust bid strategy
    └── Attribution issue? → Check conversion tracking
```

### Key Metrics by Objective

| Objective | Primary Metrics | Benchmarks (B2B SaaS) |
|-----------|----------------|----------------------|
| Awareness | CPM, Reach, Video View Rate | CPM: $5-15, VVR: 15-25% |
| Consideration | CTR, CPC, Time on Site | CTR: 1-3%, CPC: $2-8 |
| Conversion | CPA, ROAS, Conversion Rate | CPA: $50-200, CR: 2-5% |
| Retargeting | CPA, ROAS, Frequency | CPA: 30-50% lower than prospecting |

### Creative Fatigue Detection

| Signal | Threshold | Action |
|--------|-----------|--------|
| CTR declining week over week | 20%+ decline over 2 weeks | Refresh creative |
| Frequency above threshold | > 3 (display), > 5 (retargeting) | Expand audience or refresh |
| CPA increasing with stable CTR | 15%+ increase over 2 weeks | Test new creative angles |
| Engagement rate dropping | 30%+ decline | Full creative overhaul |

### Weekly Optimization Routine

| Task | Time | What to Check |
|------|------|---------------|
| Budget pacing | 5 min | Spend vs. plan, daily/weekly trends |
| CPA/ROAS check | 10 min | Performance vs. targets, by campaign |
| Top/bottom performers | 10 min | Pause worst, scale best |
| Audience analysis | 10 min | Which segments are converting? |
| Creative performance | 10 min | CTR by creative, fatigue signals |
| Frequency check | 5 min | Any audiences over-exposed? |
| Landing page CVR | 5 min | Post-click conversion rate |
| Competitor check | 5 min | New competitors in auction? |

---

## Attribution and Measurement

### Attribution Reality Check

| What Platforms Report | Reality |
|---------------------|---------|
| "This campaign drove 100 conversions" | Platform attribution is inflated by 20-50% |
| "ROAS is 5x" | Likely includes assisted conversions that would have converted anyway |
| Last-click attribution | Ignores all touchpoints before the final click |
| View-through conversions | Often just people who would have converted regardless |

### Practical Attribution Approach

1. **Use UTM parameters consistently** — Tag every campaign, ad, and link
2. **Track in GA4 as source of truth** — Compare platform data to GA4
3. **Calculate blended CAC** — Total marketing spend / Total new customers
4. **Use incrementality testing** — Hold-out tests to measure true lift
5. **Compare platform data vs. CRM data** — The gap is your attribution inflation

### UTM Standards

```
utm_source: google | meta | linkedin | twitter | tiktok | reddit
utm_medium: cpc | paid-social | display | video | sponsored
utm_campaign: [campaign-name-lowercase-hyphenated]
utm_content: [ad-variant-identifier]
utm_term: [keyword] (search only)
```

---

## Pre-Launch Checklist

### Tracking

- [ ] Pixel/tag installed and firing correctly
- [ ] Conversion events defined and tested with real test conversion
- [ ] UTM parameters added to all ad destination URLs
- [ ] GA4 goals/events configured to match conversion events
- [ ] Attribution window set appropriately (7 or 28 day)

### Landing Page

- [ ] Page loads under 3 seconds on mobile
- [ ] Page is mobile-responsive
- [ ] Headline matches the ad message
- [ ] CTA is above the fold on mobile
- [ ] Form works and submits to CRM/email system
- [ ] Thank you page/event fires conversion tracking

### Campaign Setup

- [ ] Budget set correctly (daily or lifetime)
- [ ] Bid strategy selected and configured
- [ ] Audience targeting reviewed (not too broad or narrow)
- [ ] Negative keywords added (Google Search)
- [ ] Exclusions configured (existing customers, competitors)
- [ ] Ad schedule set (if time-specific targeting needed)
- [ ] Geographic targeting verified
- [ ] Device targeting reviewed

### Creative

- [ ] 3+ creative variants per ad group/set
- [ ] All creative meets platform specifications
- [ ] Copy validated against platform policies
- [ ] Landing page URL correct for each ad

---

## Best Practices

1. **Tracking first, creative second** — Never launch without verified conversion tracking. A campaign without attribution is guesswork.

2. **Start narrow, expand gradually** — Begin with your highest-intent, most-defined audience. Expand after proving the funnel works.

3. **One change at a time** — Changing audience, creative, and bid strategy simultaneously makes it impossible to know what worked.

4. **Give algorithms time** — Do not judge campaign performance before the learning phase completes (typically 50 conversions or 7 days).

5. **Creative is the biggest lever** — On most platforms, creative quality matters more than targeting precision. Test creative aggressively.

6. **Match ad to landing page** — The #1 conversion killer is mismatched expectations between ad and landing page.

7. **Budget concentration beats distribution** — $3,000 on one proven platform outperforms $500 spread across six platforms.

8. **Build retargeting from day one** — Install pixels and build audiences even before you spend on retargeting.

9. **Compare platform data to reality** — Platform-reported conversions are always higher than actual. Use CRM and GA4 as the source of truth.

10. **Document everything** — Every campaign change, test result, and learning should be recorded. Institutional knowledge prevents repeating mistakes.

---

## Integration Points

- **Ad Creative** — Use for writing ad copy, generating headlines, and creating creative variations. Paid Ads handles the campaign strategy; Ad Creative handles the copy.
- **Landing Page Generator** — Use for building the landing pages ads drive traffic to.
- **Campaign Analytics** — Use for measuring campaign performance, attribution analysis, and ROI calculation.
- **Marketing Context** — Use as foundation for audience targeting and messaging alignment.
- **Marketing Psychology** — Apply psychological principles to improve ad creative and landing page conversion.
- **Copywriting** — Use for optimizing landing page copy to improve post-click conversion rates.
