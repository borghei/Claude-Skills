---
name: paid-ads
description: >
  Plan, execute, and optimize paid ad campaigns across Google, Meta, LinkedIn,
  Twitter/X, and TikTok, covering targeting, budget, bid strategies, and
  retargeting. Use when running PPC campaigns, setting up ad accounts, or
  optimizing ROAS/CPA.
license: MIT
metadata:
  version: 1.0.0
  author: borghei
  category: marketing
  domain: advertising
  updated: 2026-09-21
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
- [Automated Campaign Types](#automated-campaign-types)
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

## Clarify First

Before building the campaign, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Campaign objective** — leads, sales, traffic, or awareness (drives platform selection, campaign type, bid strategy, and success metrics)
- [ ] **Target audience** — who they are and their intent signal (drives platform selection and targeting setup)
- [ ] **Monthly budget** — total spend available (determines viable platforms, bid-strategy stage, and budget-phase allocation)
- [ ] **Conversion action & offer** — the action you are paying for and the offer behind it (drives campaign structure, tracking, and ad-to-page match)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

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
| Optimized targeting / audience signals | Expanding from known customers | Similar audiences were retired in Aug 2023. Use optimized targeting (Display, Demand Gen), audience signals (Performance Max), or Lookalike segments seeded from Customer Match / site visitors (Demand Gen, Video) |

**Keyword match type strategy:**
- **Exact match** [keyword]: Highest intent, lowest volume, highest CPC
- **Phrase match** "keyword": Medium intent, medium volume
- **Broad match** keyword: Lowest intent, highest volume, lowest CPC (use with smart bidding)

### Meta Ads Targeting

| Targeting Type | Use When | How |
|---------------|----------|-----|
| Interest targeting | Cold prospecting | Layer 2-3 related interests |
| Lookalike audiences | Expanding from customers | 1-3% lookalike from best customers (by LTV); in Advantage+ audience, lookalikes act as suggestions, not hard limits |
| Custom audiences | Retargeting | Website visitors, email lists, video viewers |
| Broad targeting / Advantage+ audience | Trusting Meta's ML | Only audience controls (location, minimum age, language, custom audience exclusions) are hard limits; everything else is a suggestion |
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

## Automated Campaign Types

Both Google and Meta now default new campaigns toward AI-driven, goal-based formats. Treat them as a trade: you give up placement, query, and audience control in exchange for reach and machine optimization. Feed them good inputs and set guardrails. (As of September 2026 — these products change frequently; check each platform's help center before launch.)

| Campaign type | Platform | What it does | What you give up |
|---------------|----------|--------------|------------------|
| **Advantage+ sales / app / leads campaigns** | Meta | End-to-end automation of audience, placements, budget, and creative combinations for the sales, app promotion, and leads objectives | Detailed targeting becomes suggestions; placement and budget split handled by Meta |
| **Advantage+ audience** | Meta | Uses your audience inputs as suggestions and expands beyond them when likely to improve results | Interests/lookalikes are no longer limits — only location, minimum age, language, and custom audience exclusions are hard controls |
| **Performance Max** | Google | One goal-based campaign across Search, Shopping, YouTube, Display, Discover, Gmail, and Maps | Channel mix and most placement choice; audience signals guide learning but are not targeting |
| **AI Max for Search** (2025) | Google | Optimization layer on a Search campaign: search term matching beyond your keywords (broad match + keywordless), text customization, final URL expansion | Exact query control; generated headlines/descriptions; landing-page choice (if URL expansion is on) |
| **Demand Gen** | Google | Visual/video campaigns on YouTube (incl. Shorts), Discover, Gmail, and Display with Lookalike segments and optimized targeting | Fine placement control; lookalike reach can extend past seed similarity |

**Ads in AI Overviews and AI Mode (Google):** there is no separate campaign type and no direct placement targeting. Text and Shopping ads from Search (with broad match or AI Max), Shopping, and Performance Max campaigns are eligible automatically; you cannot opt out, and Google Ads does not segment AI Overview ad reporting. Ads *within* AI Overviews are limited to English in a subset of countries (incl. the US), while ads above/below AI Overviews run in all AI Overview markets. ([About ads and AI Overviews](https://support.google.com/google-ads/answer/16297775))

**When to use automated campaigns:**
- Conversion tracking is verified and the account has steady conversion volume (automation learns from your conversion data)
- You can supply creative volume (multiple images, videos, headlines per asset group / ad set)
- You have a tested manual baseline to compare against — run as an experiment where the platform supports it (e.g., AI Max experiments)

**How to feed them:**
- **Conversion quality** — optimize for the event that correlates with revenue (qualified lead, purchase, value), not cheap proxies (page views, form starts). Pass values and import offline conversions / CAPI events so the model learns from real outcomes.
- **Creative volume and variety** — supply all asset types; refresh fatigued assets rather than restarting campaigns.
- **Audience signals** — Customer Match lists, converters, and site-visitor lists as signals (Google) or suggestions (Meta).

**Guardrails:**

| Guardrail | Google | Meta |
|-----------|--------|------|
| Brand traffic | Brand exclusions (PMax, Search/AI Max); brand inclusions in AI Max | Exclude existing-customer custom audiences |
| Query control | Account- and campaign-level negative keywords (PMax negatives apply to Search/Shopping inventory) | n/a |
| Landing pages | Turn off final URL expansion or use URL exclusions / URL inclusions | Set destination per ad |
| Audience limits | Location and language settings | Audience controls: location, minimum age, language, custom audience exclusions |
| Reporting | PMax channel performance and search terms reports; AI Max search terms reporting | Breakdowns by placement/age/gender |

Sources: [About Performance Max](https://support.google.com/google-ads/answer/10724817), [About AI Max for Search](https://support.google.com/google-ads/answer/15910366), [How AI Max works](https://support.google.com/google-ads/answer/15910187), [Brand exclusions](https://support.google.com/google-ads/answer/14505308), [Demand Gen Lookalike segments](https://support.google.com/google-ads/answer/13541369), [Meta Advantage+](https://www.facebook.com/business/ads/meta-advantage-plus), [Advantage+ audience](https://www.facebook.com/business/help/273363992030035).

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

**Meta attribution windows (as of September 2026):** Meta stopped returning the 7-day view and 28-day view windows on January 12, 2026. The remaining windows are 1-day click, 7-day click, 28-day click (Insights API), 1-day engaged view, and 1-day view ([Meta for Developers, Oct 2025](https://developers.facebook.com/blog/post/2025/10/16/ads-insights-api-metric-availability-updates/)). Historical reports that used 7- or 28-day view will not match current numbers — note the break in any trend line.

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
- [ ] Attribution window set appropriately and documented (e.g., Meta: 7-day click + 1-day view; 7-/28-day view windows no longer exist)

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

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| CPA above target with low CTR | Creative fatigue or audience mismatch | Refresh creative. Use `ad_copy_scorer.py` to validate new copy. |
| CPA above target with good CTR | Landing page conversion issue | Audit post-click experience: message match, page speed, form friction. |
| CTR dropping week over week | Creative fatigue (>3 frequency) | Refresh creative every 2-4 weeks. Expand audience to reduce frequency. |
| Budget not spending | Audience too narrow or bid too low | Check audience size with `audience_sizer.py`. Increase bid 10-20%. |
| Platform reports inflated conversions | Attribution window too wide | Compare platform data to GA4/CRM. Use incrementality testing for true lift. |
| Performance Max underperforming | Insufficient or low-quality conversion data | Build steady conversion volume first (start with Search), optimize to a revenue-linked conversion, and add brand exclusions + negatives so PMax is not just harvesting branded traffic. |
| CPA spikes after budget increase | Algorithm learning disrupted | Never increase budget more than 20-30% at a time. Wait 3-5 days between changes. |

---

## Success Criteria

- CPA within target range for campaign objective (B2B SaaS: $50-200 for qualified leads)
- ROAS above 3x for revenue-focused campaigns
- CTR above platform benchmarks: 2-5% search, 0.5-2% social
- Conversion tracking verified with test conversion before launch
- Budget allocation: 70% proven / 20% expansion / 10% testing (at scale)
- All campaigns have proper UTM tagging and GA4 attribution configured
- Weekly optimization routine completed with documented changes

---

## Scope & Limitations

**In Scope:** Campaign strategy, platform selection, audience targeting, budget allocation, bid strategies, retargeting, performance optimization, attribution, pre-launch checklists.

**Out of Scope:** Ad copy writing (use ad-creative), landing page design (use landing-page-generator), creative design/production, marketing automation, CRM configuration.

**Limitations:** Budget minimums and CPC benchmarks are directional estimates. Actual costs vary by industry, geography, and competition. Platform-reported metrics are typically 20-50% inflated versus CRM truth.

---

## Python Automation Tools

### 1. Ad Copy Scorer (`scripts/ad_copy_scorer.py`)
Scores ad copy against platform specs, compliance rules, and conversion best practices.

```bash
python scripts/ad_copy_scorer.py --headline "Cut churn by 30%" --description "See how 1200 SaaS teams reduced churn" --platform google
python scripts/ad_copy_scorer.py --file ads.json --json
```

### 2. CPC / CPA / ROAS Calculator (`scripts/cpc_calculator.py`)
Calculates key advertising metrics from campaign data with industry benchmarks.

```bash
python scripts/cpc_calculator.py --spend 5000 --clicks 1200 --conversions 45 --revenue 12000 --platform meta
python scripts/cpc_calculator.py --file campaign.json --json
```

### 3. Audience Sizer (`scripts/audience_sizer.py`)
Estimates target audience size and recommends budget based on platform and targeting criteria.

```bash
python scripts/audience_sizer.py --platform linkedin --targeting "CMOs at SaaS companies 50-500 employees"
python scripts/audience_sizer.py --file targeting.json --json
```
