---
name: marketing-ops
description: Central marketing operations hub covering MarTech stack management, marketing automation, data management, attribution modeling, campaign orchestration, skill routing, and cross-functional coordination. Use when routing marketing questions, orchestrating multi-skill campaigns, managing MarTech stack, setting up marketing automation, or when user mentions marketing ops, campaign plan, marketing help, marketing priorities, coordinate marketing, MarTech, marketing automation, data management, or attribution.
license: MIT
metadata:
  version: 1.0.0
  author: borghei
  category: marketing
  domain: operations
  updated: 2026-03-09
---

# Marketing Ops

Central command for marketing operations — routing questions, orchestrating campaigns, managing MarTech, and coordinating across all marketing functions.

---

## Table of Contents

- [Keywords](#keywords)
- [Quick Start](#quick-start)
- [Skill Routing Matrix](#skill-routing-matrix)
- [Campaign Orchestration](#campaign-orchestration)
- [MarTech Stack Management](#martech-stack-management)
- [Marketing Automation Framework](#marketing-automation-framework)
- [Data Management](#data-management)
- [Attribution Framework](#attribution-framework)
- [Marketing Audit](#marketing-audit)
- [Best Practices](#best-practices)
- [Integration Points](#integration-points)

---

## Keywords

marketing ops, marketing operations, MarTech stack, marketing automation, campaign orchestration, skill routing, marketing coordination, data management, attribution, marketing technology, campaign management, workflow automation, lead management, marketing analytics, marketing infrastructure, CRM integration, email automation, lead scoring

---

## Quick Start

### Route a Marketing Question

1. Identify what the user is trying to accomplish
2. Match to the routing matrix below
3. Route to the correct skill with context
4. If multiple skills are needed, create an orchestration plan

### Orchestrate a Campaign

1. Check that marketing context exists (if not, create it first)
2. Identify all skills needed for the campaign
3. Sequence skills in the correct order
4. Execute each phase, passing outputs to the next
5. Measure results using campaign analytics

---

## Skill Routing Matrix

### Content Skills

| User Says | Route To | Not This |
|-----------|----------|----------|
| "Write a blog post," "content ideas," "what should I write" | Content Strategy | Not Copywriting (that is for page copy) |
| "Write copy for my homepage," "landing page copy," "headline" | Copywriting | Not Content Strategy (that is for planning) |
| "Edit this copy," "proofread," "polish this" | Copy Editing | Not Copywriting (that is for writing new) |
| "Social media post," "LinkedIn post," "tweet" | Social Content | Not Content Strategy (that is for planning) |
| "Write an article end-to-end," "content production" | Content Production | Not Content Strategy (production has the full pipeline) |
| "Sounds too robotic," "make it human," "AI watermarks" | Content Humanizer | Not Copy Editing (that is for editorial quality) |
| "Marketing ideas," "brainstorm," "what else can I try" | Marketing Ideas | Not Content Strategy (that is for content specifically) |

### SEO Skills

| User Says | Route To | Not This |
|-----------|----------|----------|
| "SEO audit," "technical SEO," "on-page SEO" | SEO Specialist | Not AI SEO (that is for AI search engines) |
| "AI search," "ChatGPT visibility," "Perplexity," "GEO" | AI SEO | Not SEO Specialist (that is traditional SEO) |

### Conversion Skills

| User Says | Route To | Not This |
|-----------|----------|----------|
| "Landing page," "campaign page," "lead capture page" | Landing Page Generator | Not Copywriting (generator includes structure + copy) |
| "Brand guidelines," "style guide," "brand voice" | Brand Guidelines | Not Marketing Context (guidelines are implementation) |

### Channel Skills

| User Says | Route To | Not This |
|-----------|----------|----------|
| "Paid ads," "Google Ads," "Meta ads," "ad campaign" | Paid Ads | Not Ad Creative (that is for copy, not strategy) |
| "Ad copy," "ad headlines," "ad variations," "RSA" | Ad Creative | Not Paid Ads (that is for campaign strategy) |
| "Cold email," "outreach," "prospecting email" | Cold Email | Not Content Production (cold email has different rules) |

### Strategy Skills

| User Says | Route To | Not This |
|-----------|----------|----------|
| "Marketing context," "who is my customer," "ICP" | Marketing Context | Set up before other skills |
| "Marketing strategy," "how to market" | Marketing Ideas | Not Marketing Ops (ops is for execution routing) |
| "Psychology," "persuasion," "why people buy" | Marketing Psychology | Not Copywriting (psychology is the theory layer) |

---

## Campaign Orchestration

### Campaign Type: Product/Feature Launch

```
Sequence:
1. Marketing Context (verify foundation exists)
2. Content Strategy (plan launch content)
3. Copywriting (write landing page and email copy)
4. Landing Page Generator (build the conversion page)
5. Ad Creative (create ad copy for paid promotion)
6. Paid Ads (set up campaign targeting and budget)
7. Social Content (create organic social posts)
8. Cold Email (targeted outreach to prospects)
9. Campaign Analytics (measure results)
```

### Campaign Type: Content Marketing Sprint

```
Sequence:
1. Content Strategy (plan topics and calendar)
2. Content Production (research, write, optimize each piece)
3. Content Humanizer (polish for natural voice)
4. AI SEO (optimize for AI search citation)
5. Social Content (distribute across platforms)
6. Campaign Analytics (track performance)
```

### Campaign Type: Lead Generation Blitz

```
Sequence:
1. Marketing Context (verify ICP and messaging)
2. Landing Page Generator (build conversion pages)
3. Ad Creative (generate ad variations)
4. Paid Ads (launch campaigns)
5. Cold Email (parallel outbound effort)
6. Campaign Analytics (measure and optimize)
```

### Campaign Type: Brand Awareness

```
Sequence:
1. Marketing Context (define brand foundation)
2. Brand Guidelines (establish visual and verbal standards)
3. Content Strategy (plan thought leadership content)
4. Social Content (build social presence)
5. Content Production (create pillar content)
6. Campaign Analytics (measure reach and engagement)
```

### Campaign Type: Conversion Optimization

```
Sequence:
1. Marketing Psychology (identify behavioral levers)
2. Copy Editing (audit existing page copy)
3. Copywriting (rewrite underperforming sections)
4. Landing Page Generator (redesign conversion pages)
5. Campaign Analytics (set up A/B tests and track results)
```

---

## MarTech Stack Management

### Core Stack Components

| Category | Purpose | Common Tools | Integration Priority |
|----------|---------|-------------|---------------------|
| CRM | Customer data management | Salesforce, HubSpot, Pipedrive | Critical |
| Marketing Automation | Email, workflows, scoring | HubSpot, Marketo, ActiveCampaign | Critical |
| Analytics | Traffic and behavior tracking | GA4, Mixpanel, Amplitude | Critical |
| Email Platform | Email sending and deliverability | SendGrid, Mailchimp, Customer.io | Critical |
| Ad Platforms | Paid advertising | Google Ads, Meta Ads, LinkedIn Ads | High |
| SEO Tools | Keyword research and tracking | Ahrefs, SEMrush, Moz | High |
| Social Management | Publishing and scheduling | Buffer, Hootsuite, Sprout Social | Medium |
| Content Management | Content creation and hosting | WordPress, Webflow, Ghost | High |
| Attribution | Multi-touch attribution | Attribution App, Dreamdata | Medium |
| ABM | Account-based marketing | Demandbase, 6sense, Terminus | Medium (B2B) |

### Stack Evaluation Framework

When evaluating new tools:

| Criterion | Weight | Scoring |
|-----------|--------|---------|
| Does it solve a validated problem? | 30% | Clear need (3), Nice to have (2), Speculative (1) |
| Does it integrate with existing stack? | 25% | Native integration (3), API available (2), Manual export (1) |
| Total cost of ownership | 20% | Under budget (3), At budget (2), Over budget (1) |
| Time to value | 15% | Under 1 week (3), 1-4 weeks (2), 4+ weeks (1) |
| Team capability to use it | 10% | Self-serve (3), Training needed (2), Expert required (1) |

**Rule:** Never add a tool that does not integrate with your CRM. Disconnected data is worse than no data.

### Stack Audit Checklist

- [ ] Every tool has a clear owner responsible for it
- [ ] Every tool connects to CRM or central data warehouse
- [ ] No overlapping tools doing the same job
- [ ] All contracts reviewed annually for cost optimization
- [ ] Data flows documented between tools
- [ ] Integration health monitored (failures flagged within 24 hours)
- [ ] Tool adoption measured (tools nobody uses should be cut)

---

## Marketing Automation Framework

### Automation Priority by Impact

| Automation | Impact | Complexity | Build First |
|-----------|--------|-----------|-------------|
| Welcome/onboarding email sequence | High | Low | Yes |
| Lead scoring | High | Medium | Yes |
| Abandoned cart/trial follow-up | High | Low | Yes |
| Event-triggered emails (usage milestones) | High | Medium | Second priority |
| Lead routing to sales | High | Low | Yes |
| Social media scheduling | Medium | Low | Second priority |
| Reporting dashboards | Medium | Medium | Second priority |
| Content personalization | Medium | High | Third priority |
| Predictive lead scoring | Medium | High | Third priority |
| Dynamic content insertion | Low-Medium | High | Later |

### Lead Scoring Model

| Signal Type | Examples | Score |
|-------------|---------|-------|
| Demographic fit | Matches ICP (title, company size, industry) | +10 to +25 |
| Behavioral - high intent | Visited pricing page, requested demo, viewed case study | +15 to +25 |
| Behavioral - engagement | Opened 3+ emails, downloaded content, attended webinar | +5 to +15 |
| Behavioral - product | Used free trial, reached activation milestone | +20 to +30 |
| Negative signals | Competitor employee, student email, unsubscribed | -10 to -50 |

**Lead score thresholds:**
- 0-25: Nurture (automated email sequences)
- 26-50: Marketing Qualified Lead (MQL) — deeper engagement
- 51-75: Sales Qualified Lead (SQL) — route to sales
- 76+: Hot lead — immediate sales outreach

### Email Automation Sequences

| Sequence | Trigger | Emails | Duration |
|----------|---------|--------|----------|
| Welcome | New signup | 5-7 | 14 days |
| Onboarding | Started trial | 4-6 | 14 days |
| Re-engagement | Inactive 30 days | 3-4 | 21 days |
| Win-back | Churned | 3-5 | 30 days |
| Nurture | Downloaded content | 5-7 | 45 days |
| Upsell | Reached plan limit | 2-3 | 7 days |
| Referral | 90 days active + high NPS | 2 | 7 days |

---

## Data Management

### Data Quality Framework

| Dimension | Definition | How to Measure |
|-----------|-----------|---------------|
| Completeness | Required fields are filled | % of records with complete required fields |
| Accuracy | Data matches reality | Sample audit against source of truth |
| Consistency | Same data, same format everywhere | Cross-system comparison |
| Timeliness | Data is current | % of records updated within defined freshness window |
| Uniqueness | No duplicate records | Duplicate rate in CRM |

### Data Hygiene Schedule

| Task | Frequency | Owner |
|------|-----------|-------|
| Deduplicate CRM records | Monthly | Marketing Ops |
| Verify email addresses | Before every campaign | Marketing Ops |
| Update firmographic data | Quarterly | Marketing Ops |
| Clean inactive contacts | Quarterly | Marketing Ops |
| Audit UTM parameter consistency | Monthly | Marketing Ops |
| Review lead scoring accuracy | Quarterly | Marketing + Sales |
| Sync CRM with marketing automation | Continuous (automated) | System |

### UTM Parameter Standards

Consistent UTM tagging is foundational for attribution:

```
utm_source: [platform] — google, linkedin, facebook, email, partner-name
utm_medium: [channel type] — cpc, organic, email, social, referral
utm_campaign: [campaign name] — product-launch-q1, blog-promo-march
utm_content: [variant] — headline-a, cta-blue, audience-cmo
utm_term: [keyword] — for paid search only
```

**Rules:**
- Always lowercase
- Use hyphens, not spaces or underscores
- Document all campaign names in a shared registry
- Validate UTMs before launching any campaign

---

## Attribution Framework

### Attribution Models

| Model | How It Works | Best For | Limitation |
|-------|-------------|---------|-----------|
| First-touch | 100% credit to first interaction | Understanding acquisition channels | Ignores nurture touchpoints |
| Last-touch | 100% credit to final interaction | Understanding conversion triggers | Ignores awareness touchpoints |
| Linear | Equal credit to all touchpoints | Simple multi-touch understanding | Treats all touches equally |
| Time-decay | More credit to recent touchpoints | Long sales cycles | May undervalue awareness |
| Position-based (U-shaped) | 40% first, 40% last, 20% middle | Balanced view | Arbitrary weighting |
| Data-driven | ML-based weighting | Sophisticated programs | Requires large data volume |

### Attribution Implementation Checklist

- [ ] UTM parameters standardized and enforced
- [ ] All marketing channels tagged consistently
- [ ] CRM captures source/medium/campaign for every lead
- [ ] Conversion events defined and tracked
- [ ] Attribution model selected and documented
- [ ] Reporting cadence established (weekly + monthly)
- [ ] Channel ROI calculated and compared monthly

---

## Marketing Audit

### Full Marketing Audit Structure

| Area | What to Assess | Key Questions |
|------|---------------|---------------|
| Strategy | Positioning, ICP, messaging | Is our positioning differentiated? Do we know our ICP? |
| Content | Quality, quantity, performance | Is content driving traffic and conversions? |
| SEO | Rankings, technical health, content gaps | Are we visible for target keywords? |
| Paid | ROAS, CPA, channel mix | Are paid campaigns profitable? |
| Email | List health, engagement, automation | Are sequences driving conversions? |
| Social | Reach, engagement, brand consistency | Are we building audience and trust? |
| MarTech | Stack utilization, integration health | Are our tools connected and used? |
| Data | Quality, attribution, reporting | Can we trust our data and attribution? |

### Audit Scoring

For each area, score 1-5:

| Score | Status | Action |
|-------|--------|--------|
| 1 | Not present | Build from scratch |
| 2 | Basic but underperforming | Significant improvement needed |
| 3 | Functional | Optimize and iterate |
| 4 | Strong | Maintain and scale |
| 5 | Best-in-class | Protect and document |

---

## Best Practices

1. **Context first, always** — Check that marketing context exists before any marketing work. Everything works better with context.

2. **Route precisely** — A question routed to the wrong skill produces wrong-shaped output. Use the routing matrix.

3. **Orchestrate, do not fragment** — Multi-skill campaigns need a sequence plan. Ad hoc execution produces inconsistent results.

4. **Own the data** — Marketing ops is responsible for data quality. Bad data produces bad decisions.

5. **Standardize UTMs** — Inconsistent UTM parameters make attribution impossible. Enforce standards before launching campaigns.

6. **Audit tools annually** — Every tool should justify its cost and usage. Cut tools nobody uses.

7. **Automate the repeatable** — If you do it every week, automate it. Manual processes do not scale.

8. **Document everything** — Campaign playbooks, automation logic, data flows, tool configurations. Tribal knowledge is fragile.

9. **Align with sales** — Marketing ops and sales ops must share data definitions, lead scoring criteria, and attribution models.

10. **Measure what matters** — Track leading indicators (MQLs, pipeline velocity) alongside lagging indicators (revenue, ROI).

---

## Integration Points

- **Marketing Context** — Foundation for all marketing operations. Create this first.
- **Campaign Analytics** — Use for measuring outcomes of orchestrated campaigns.
- **All Marketing Skills** — Marketing Ops routes questions and orchestrates workflows across the full skill ecosystem.
- **Content Strategy** — Coordinate content calendar with campaign schedule.
- **Paid Ads** — Coordinate paid campaigns with organic efforts and landing pages.
- **Cold Email** — Coordinate outbound with inbound campaigns to avoid audience overlap.

---

## Troubleshooting

| Symptom | Likely Cause | Resolution |
|---------|-------------|------------|
| Marketing and sales disagree on lead quality | Lead scoring thresholds not aligned or model not validated against outcomes | Run lead_scoring_simulator.py with historical data; validate that high-scored leads convert at 2x+ the rate of low-scored |
| MarTech stack costs growing 20%+ YoY without proportional ROI | Tool proliferation without consolidation; unused tools not audited | Run martech_stack_auditor.py quarterly; cut tools with <30% utilization; consolidate overlapping categories |
| Campaign data siloed across platforms, attribution impossible | No unified UTM standard; tools not integrated through CRM | Standardize UTM parameters (lowercase, hyphens, documented registry); require CRM integration for every tool |
| Lead routing to sales takes >24 hours | Manual handoff process; no automation between marketing automation and CRM | Implement automated lead routing rules; route hot leads (76+ score) within 15 minutes |
| Email deliverability dropping below 90% | List hygiene not maintained; bounced/inactive contacts not cleaned | Deduplicate monthly; verify addresses before campaigns; clean inactive contacts quarterly |
| Budget spent evenly across channels regardless of performance | No performance-based allocation framework in place | Use campaign_budget_allocator.py with historical ROAS data; shift budget quarterly toward highest performers |
| Multi-skill campaigns produce inconsistent messaging | No orchestration sequence defined; skills executed ad hoc | Follow campaign orchestration templates; always start with marketing context verification |

---

## Success Criteria

- All MarTech tools connected to CRM with verified data flow
- MarTech stack audit score above 70/100 with zero critical gaps
- Lead scoring model validated: high-scored leads convert at 2x+ rate of low-scored
- UTM parameters 100% standardized and validated before every campaign launch
- Campaign orchestration follows documented sequences with context verified first
- Budget allocation reviewed and adjusted quarterly based on channel ROI data
- Data quality: <5% duplicate rate in CRM, <2% email bounce rate, >95% required fields complete

---

## Scope & Limitations

**In Scope:** Skill routing and orchestration, campaign sequencing, MarTech stack management and auditing, marketing automation (email sequences, lead scoring, lead routing), data quality management, UTM standardization, attribution framework setup, marketing audit methodology, budget allocation.

**Out of Scope:** Individual channel execution (see channel-specific skills), analytics implementation (see analytics-tracking skill), content creation (see content-creator skill), sales operations and CRM administration (sales ops function).

**Limitations:** Marketing ops is the coordination layer, not the execution layer. Tool auditing uses self-reported utilization data; actual usage may differ. Lead scoring models require minimum 50+ historical conversions for meaningful validation. Budget allocation assumes linear channel scaling; real channels have diminishing returns.

---

## Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/martech_stack_auditor.py` | Audit MarTech stack for gaps, redundancies, and optimization opportunities | `python scripts/martech_stack_auditor.py stack.json --demo` |
| `scripts/campaign_budget_allocator.py` | Allocate marketing budget across campaigns by priority and performance | `python scripts/campaign_budget_allocator.py campaigns.json --budget 100000 --strategy balanced` |
| `scripts/lead_scoring_simulator.py` | Simulate and validate lead scoring models against actual outcomes | `python scripts/lead_scoring_simulator.py leads.json --demo` |
