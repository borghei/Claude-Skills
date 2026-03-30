---
name: email-sequence
description: >
  Design and write complete email automation sequences for SaaS and B2B
  products. Covers welcome/onboarding, lead nurture, re-engagement,
  post-purchase, trial expiration, and sales sequences. Outputs ready-to-send
  drafts with subject lines, preview text, full body copy, CTAs, timing, and
  segmentation logic. Use when building drip campaigns, improving trial-to-paid
  conversion, or designing lifecycle email programs.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: marketing
  domain: email-marketing
  updated: 2026-03-09
  frameworks: email-automation, lifecycle-marketing, drip-campaigns
---
# Email Sequence Design

**Category:** Marketing
**Tags:** email sequences, drip campaigns, nurture flows, onboarding emails, lifecycle marketing, automation

## Overview

Email Sequence Design creates complete, ready-to-implement email automation flows. Every output includes subject lines, preview text, full body copy, CTAs, send timing, and exit conditions. The goal is sequences that nurture relationships and drive specific conversion actions -- not just "stay top of mind" email noise.

This skill writes the sequences. For email HTML templates and rendering infrastructure, use email-template-builder. For tracking email performance, use analytics-tracking.

---

## Sequence Types

| Type | Trigger | Goal | Typical Length |
|------|---------|------|---------------|
| Welcome/Onboarding | New signup | Activate user, show core value | 5-7 emails over 14 days |
| Trial Expiration | Trial nearing end | Convert to paid | 4-5 emails over 7 days |
| Lead Nurture | Content download, webinar | Qualify and convert | 6-8 emails over 30 days |
| Re-engagement | Inactive 30+ days | Bring back or clean list | 3-4 emails over 14 days |
| Post-Purchase | Subscription start | Reduce churn, expand | 4-6 emails over 30 days |
| Event-Based | Specific user action | Drive next action | 2-3 emails over 7 days |
| Sales (Warm) | MQL or PQL signal | Book meeting or start trial | 4-5 emails over 14 days |

---

## Design Process

### Step 1: Define Sequence Architecture

Before writing any email, define the architecture:

```
Sequence Name:     [Name]
Trigger:           [What starts the sequence]
Primary Goal:      [Single conversion action]
Secondary Goals:   [Relationship building, data collection]
Length:            [Number of emails]
Duration:          [Total time span]
Exit Conditions:   [When they leave the sequence]
Suppression:       [Other sequences to suppress while active]
```

### Step 2: Map the Emotional Journey

Each email serves a purpose in a progression:

| Email | Emotional State | Purpose | Key Message |
|-------|----------------|---------|-------------|
| 1 | Curious, uncertain | Welcome, set expectations | "Here's what to expect" |
| 2 | Exploring, evaluating | Demonstrate core value | "Here's the one thing to try first" |
| 3 | Engaged or dropping off | Social proof | "Here's how others succeeded" |
| 4 | Considering commitment | Remove objections | "Common concerns addressed" |
| 5 | Ready to decide | Create urgency | "Your trial ends in X days" |

### Step 3: Write Each Email

For every email in the sequence, deliver:

```
Email [#]: [Name/Purpose]
Send:     [Timing from trigger or previous email]
Segment:  [Conditions -- who receives this variant]

Subject:  [Subject line - under 50 characters]
Preview:  [Preview text - 80-120 characters, complements subject]

Body:
[Complete copy -- not an outline, not bullets, the actual words]

CTA:      [Button text] → [Destination URL]
P.S.:     [Optional -- works for urgency or human touch]
```

### Step 4: Define Branching Logic

Not everyone follows the same path. Define branches:

```
After Email 2:
  IF user activated core feature → Skip to Email 4 (post-activation)
  IF user has not logged in → Send Email 2B (re-engagement variant)
  IF user unsubscribed → Exit sequence

After Email 4:
  IF user converted → Exit sequence, enter post-purchase sequence
  IF user visited pricing 2+ times → Send Email 4B (pricing objection handler)
  ELSE → Continue to Email 5
```

---

## Sequence Blueprints

### Blueprint: SaaS Welcome/Onboarding (7 emails, 14 days)

| Email | Day | Subject | Purpose |
|-------|-----|---------|---------|
| 1 | 0 (immediate) | Welcome to [Product] -- start here | Set expectations, one CTA to activate |
| 2 | 1 | The one feature that changes everything | Drive to core value action |
| 3 | 3 | How [Company] got [Result] in [Timeframe] | Social proof, case study |
| 4 | 5 | Quick question | Check engagement, offer help |
| 5 | 7 | 3 things you might have missed | Feature discovery, breadth |
| 6 | 10 | Your trial is halfway done | Progress report, urgency |
| 7 | 13 | Last day of your trial | Convert or lose access |

**Exit conditions:** User converts to paid at any point, user unsubscribes, user explicitly requests removal.

**Branching:**
- After Email 2: If user completed core action, skip Email 3, go to Email 4
- After Email 4: If user has not logged in for 5+ days, switch to re-engagement variant
- After Email 6: If user visited pricing page, send pricing-focused Email 7 variant

### Blueprint: Lead Nurture (6 emails, 30 days)

| Email | Day | Subject | Purpose |
|-------|-----|---------|---------|
| 1 | 0 | Your [resource name] is ready | Deliver promised content |
| 2 | 3 | The mistake most [role] make with [topic] | Educational, establish authority |
| 3 | 7 | [Company] went from [problem] to [result] | Case study, social proof |
| 4 | 14 | The [topic] framework we use internally | Exclusive value, reciprocity |
| 5 | 21 | Quick question about [their challenge] | Personal, segmentation |
| 6 | 28 | See if [Product] is right for you | Soft CTA, demo or trial |

**Exit conditions:** Books demo, starts trial, unsubscribes, or completes sequence.

### Blueprint: Re-engagement (4 emails, 14 days)

| Email | Day | Subject | Purpose |
|-------|-----|---------|---------|
| 1 | 0 | We noticed you've been away | Acknowledge absence, show value |
| 2 | 3 | Here's what you missed | Product updates, new features |
| 3 | 7 | [Exclusive offer or incentive] | Incentivize return |
| 4 | 14 | Should we stop emailing you? | Clean list, last chance |

**Critical rule:** If no engagement after Email 4, remove from active email list. Sending to unengaged contacts damages sender reputation.

### Blueprint: Trial Expiration (5 emails, 7 days)

| Email | Day Before Expiry | Subject | Purpose |
|-------|-------------------|---------|---------|
| 1 | 7 | Your trial ends in one week | Awareness, usage summary |
| 2 | 3 | Here's what you'll lose access to | Loss aversion, feature list |
| 3 | 1 | Tomorrow is your last day | Urgency, simple CTA |
| 4 | 0 | Your trial just ended | Conversion, offer extension option |
| 5 | +3 | We saved your data for 30 days | Last chance, data retention |

---

## Subject Line Framework

### Formulas That Work

| Formula | Example | Why It Works |
|---------|---------|-------------|
| How [company] [achieved result] | "How Stripe reduced churn 23%" | Specific, curiosity, social proof |
| The [number] [thing] [audience] [needs] | "The 3 metrics every PM tracks" | Specific, relevant, scannable |
| Quick question about [topic] | "Quick question about your trial" | Personal, non-threatening |
| [Name], [action-oriented statement] | "Sarah, your dashboard is ready" | Personal, action-oriented |
| Your [asset] is [status] | "Your free trial ends tomorrow" | Ownership, urgency |

### Subject Line Rules

1. Under 50 characters (mobile truncation happens at 35-45)
2. No ALL CAPS words
3. No excessive punctuation (!!!)
4. No spam trigger words in subject: free, guarantee, limited time, act now
5. Preview text must complement, not repeat, the subject
6. A/B test subject lines on every sequence (minimum 3 variants per email)

---

## Timing & Cadence

### Optimal Send Times (B2B SaaS)

| Day | Time Window | Notes |
|-----|-------------|-------|
| Tuesday | 9-11 AM recipient's timezone | Highest open rates |
| Wednesday | 9-11 AM | Second best |
| Thursday | 9-11 AM | Good for follow-ups |
| Monday | 10 AM-12 PM | After inbox clearing |
| Friday | Avoid for important emails | Low engagement |
| Weekend | Avoid for B2B | Exception: consumer products |

### Sequence Spacing Rules

- Welcome email: Immediate (within 5 minutes of trigger)
- Onboarding emails: Every 1-3 days (maintain momentum)
- Nurture emails: Every 3-7 days (avoid fatigue)
- Re-engagement: Every 3-5 days (test urgency vs respect)
- Trial expiration: Accelerating cadence (7 days, 3 days, 1 day, 0, +3)

---

## Metrics & Benchmarks

### Expected Performance by Sequence Type

| Metric | Welcome | Nurture | Re-engagement | Trial Expiration |
|--------|---------|---------|---------------|------------------|
| Open rate | 50-70% | 25-40% | 15-25% | 40-60% |
| Click rate | 10-20% | 3-8% | 2-5% | 8-15% |
| Conversion rate | 5-15% | 1-3% | 3-8% | 10-25% |
| Unsubscribe rate | <0.5% | <0.3% | 1-3% | <0.5% |

### Health Indicators

| Signal | Meaning | Action |
|--------|---------|--------|
| Open rate declining across sequence | Fatigue or irrelevance | Shorten sequence or improve subject lines |
| High opens, low clicks | Subject works, body/CTA doesn't | Rewrite body copy, simplify CTA |
| High click rate, low conversion | Landing page problem | Audit post-click experience |
| Rising unsubscribes after Email 3 | Too frequent or too salesy | Increase spacing, add more value |
| Email 1 open rate below 40% | Deliverability issue | Check sender reputation, authentication |

---

## Segmentation Strategy

### Behavioral Segments

| Segment | Definition | Sequence Adjustment |
|---------|-----------|-------------------|
| Power users | Used core feature 5+ times | Skip beginner content, focus on advanced features |
| Window shoppers | Signed up, never activated | More hand-holding, simpler first steps |
| Pricing page visitors | Viewed pricing 2+ times | Address pricing objections directly |
| Feature explorers | Used 3+ features | Highlight integration and workflow value |
| Ghost users | No login in 7+ days | Re-engagement sequence |

### Personalization Tiers

| Tier | Effort | Impact | Example |
|------|--------|--------|---------|
| 1: Name + company | Low | Moderate | "Hi Sarah, how's the Acme team finding..." |
| 2: Behavioral | Medium | High | "Since you set up your first project..." |
| 3: Segment-specific copy | High | Highest | Entirely different email body per segment |

---

## Implementation Checklist

- [ ] Sequence architecture documented (trigger, goal, length, exits)
- [ ] All emails written with subject, preview, body, CTA
- [ ] Branching logic defined for key decision points
- [ ] Subject line A/B variants created (minimum 3 per email)
- [ ] UTM parameters configured for all links
- [ ] Suppression rules set (no overlapping sequences)
- [ ] Unsubscribe handling confirmed (one-click, CAN-SPAM compliant)
- [ ] Plain text version created for each email
- [ ] Send time optimized for recipient timezone
- [ ] Metrics dashboard configured (opens, clicks, conversions, unsubs)
- [ ] 30-day post-launch review scheduled

---

## Proactive Triggers

- User mentions low trial-to-paid conversion: ask about trial expiration email sequence before recommending pricing changes
- User reports high open rates but low clicks: diagnose body copy and CTA before blaming subject lines
- User wants to "do email marketing": clarify sequence type before writing anything
- User has a product launch coming: recommend coordinating launch email sequence with in-app messaging
- User mentions list going cold: suggest re-engagement sequence before recommending acquisition spend

---

## Related Skills

| Skill | Use When |
|-------|----------|
| **email-template-builder** | Building HTML email templates and rendering infrastructure |
| **analytics-tracking** | Setting up email click tracking and UTM attribution |
| **launch-strategy** | Coordinating email sequences around product launches |
| **content-creator** | Writing landing page copy that email CTAs point to |
| **ab-test-setup** | Designing statistically valid email A/B tests |

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Welcome email open rate below 40% | Deliverability issue or weak subject line | Check sender reputation and SPF/DKIM/DMARC. Test subject variants. |
| Open rates declining across sequence | Fatigue or irrelevance | Shorten sequence, improve subject lines, or add more value per email. |
| High opens, low clicks | Body copy or CTA is weak | Rewrite body with stronger benefit and simplify CTA to one action. |
| High click rate, low conversion | Landing page problem | Audit post-click experience: message match, page speed, form friction. |
| Rising unsubscribes after email 3 | Too frequent or too salesy | Increase spacing between emails and add more educational content. |
| Emails clipped by Gmail | HTML template over 102KB | Use `render_size_analyzer.py` from email-template-builder to reduce size. |
| Sequence not triggering | Automation platform misconfiguration | Verify trigger events, check suppression rules for conflicts. |

---

## Success Criteria

- Welcome sequence open rate above 50% (benchmark: 50-70%)
- Nurture sequence click-through rate above 3% (benchmark: 3-8%)
- Trial expiration conversion rate above 10% (benchmark: 10-25%)
- Unsubscribe rate below 0.5% per email (below 0.3% for nurture)
- Every email has 3+ subject line A/B variants tested
- Branching logic covers at least 2 behavioral segments per sequence
- Sequence-level conversion rate (total conversions / initial sends) above 5%

---

## Scope & Limitations

**In Scope:** Lifecycle email sequence design, copy, timing, branching logic, segmentation, and performance optimization for SaaS/B2B.

**Out of Scope:** Email HTML rendering (use email-template-builder), cold outreach sequences (use cold-email), marketing automation platform setup, transactional email infrastructure.

**Limitations:** Benchmarks are SaaS/B2B focused. Adjust thresholds for e-commerce, consumer, or other verticals.

---

## Python Automation Tools

### 1. Subject Line Scorer (`scripts/subject_line_scorer.py`)
Scores sequence email subject lines for open-rate potential and auto-detects sequence type (welcome, trial, nurture, re-engagement).

```bash
python scripts/subject_line_scorer.py "Your trial ends tomorrow"
python scripts/subject_line_scorer.py --file subjects.txt --json
```

### 2. Sequence Mapper (`scripts/sequence_mapper.py`)
Generates a visual sequence map with timing, branching logic, and exit conditions from a sequence definition.

```bash
python scripts/sequence_mapper.py sequence_def.json
python scripts/sequence_mapper.py --sample --json
```

### 3. Performance Analyzer (`scripts/performance_analyzer.py`)
Analyzes email sequence metrics against benchmarks, identifies bottlenecks, and recommends optimizations.

```bash
python scripts/performance_analyzer.py metrics.json
python scripts/performance_analyzer.py --sample --json
```
