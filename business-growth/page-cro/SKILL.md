---
name: page-cro
description: Landing page and marketing page conversion rate optimization covering value proposition clarity, headline effectiveness, CTA hierarchy, visual flow, social proof placement, objection handling, and structured A/B testing.
version: 1.0.0
author: borghei
category: business-growth
tags: [cro, landing-page, conversion-optimization, copywriting, ux]
triggers:
  - user wants to optimize conversions on a marketing page
  - user says a page is not converting or has high bounce rate
  - user mentions CRO or conversion rate optimization
  - user is building a new landing page and wants conversion review
  - user is running paid traffic to a page
  - user mentions pricing page optimization
---

# Page CRO

Production-grade conversion rate optimization framework for marketing pages. Covers the 7-dimension analysis framework, page-type-specific playbooks, copy alternatives methodology, above-the-fold engineering, social proof hierarchy, objection handling patterns, and structured A/B test design.

---

## Table of Contents

- [Initial Assessment](#initial-assessment)
- [The 7-Dimension CRO Framework](#the-7-dimension-cro-framework)
- [Above-the-Fold Engineering](#above-the-fold-engineering)
- [Social Proof Hierarchy](#social-proof-hierarchy)
- [Objection Handling Architecture](#objection-handling-architecture)
- [Page-Type Playbooks](#page-type-playbooks)
- [Copy Alternatives Methodology](#copy-alternatives-methodology)
- [Traffic Source Matching](#traffic-source-matching)
- [A/B Test Framework](#ab-test-framework)
- [Metrics and Benchmarks](#metrics-and-benchmarks)
- [Output Artifacts](#output-artifacts)
- [Related Skills](#related-skills)

---

## Initial Assessment

### Required Context

| Question | Why It Matters |
|----------|---------------|
| What page type? (homepage, landing page, pricing, feature, blog) | Determines the CRO framework to apply |
| What is the primary conversion goal? | Focuses the analysis |
| Where is traffic coming from? (organic, paid, email, social) | Drives message-match requirements |
| What is the current conversion rate? | Establishes the baseline |
| What does the post-click flow look like? | The page may convert fine but the next step fails |
| Do you have heatmaps or session recordings? | Behavioral data reveals what analytics cannot |
| What have you already tried? | Avoids re-testing failed experiments |

---

## The 7-Dimension CRO Framework

Analyze every marketing page across these 7 dimensions, in order of typical impact.

### Dimension 1: Value Proposition Clarity (Highest Impact)

**The 5-second test:** Can a first-time visitor understand what this is, who it is for, and why they should care within 5 seconds?

| Signal | Pass | Fail |
|--------|------|------|
| Primary benefit is stated explicitly | "Save 10 hours/week on reporting" | "Next-generation analytics platform" |
| Written in customer language | "See which campaigns drive revenue" | "Multi-touch attribution solution" |
| Differentiator is clear | "The only CRM built for agencies" | "A better CRM" |
| Specificity | Includes numbers, timeframes, outcomes | Vague superlatives ("powerful", "innovative") |

### Dimension 2: Headline Effectiveness

**Headline scoring rubric:**

| Criteria | Score 0 | Score 1 | Score 2 |
|----------|---------|---------|---------|
| Communicates core value | No | Partially | Clearly |
| Specific (numbers, outcomes) | Generic | Somewhat specific | Very specific |
| Addresses target audience | Generic | Implied | Explicit |
| Matches traffic source | No connection | Loose match | Exact message match |
| Emotional or logical hook | Neither | One | Both |

**Total: 0-10. Score < 6 = rewrite needed.**

### Dimension 3: CTA Hierarchy and Placement

| Check | Pass | Fail |
|-------|------|------|
| One clear primary CTA | Single, prominent action | Multiple competing CTAs |
| CTA visible without scrolling | Above the fold | Below the fold only |
| CTA copy communicates value | "Start Free Trial" | "Submit" |
| CTA repeated at decision points | After benefits, after social proof, at bottom | Only at top or only at bottom |
| Secondary CTA is clearly secondary | Smaller, different color, text link | Same visual weight as primary |

### Dimension 4: Visual Hierarchy and Scannability

| Check | Pass | Fail |
|-------|------|------|
| Most important element is most prominent | Headline + CTA dominate | Navigation or image dominates |
| Scannable in 10 seconds | Key points visible via headings, bold, bullets | Wall of text |
| Adequate white space | Breathing room between sections | Cluttered, dense layout |
| Images support the message | Product screenshots, relevant imagery | Stock photos, decorative graphics |
| F-pattern or Z-pattern layout | Content follows natural eye flow | Random placement |

### Dimension 5: Social Proof and Trust

| Check | Pass | Fail |
|-------|------|------|
| Customer logos visible | Recognizable logos above the fold | No logos or unknown companies |
| Testimonials are specific | "Increased revenue by 40%" | "Great product!" |
| Testimonials are attributed | Full name, title, company, photo | Anonymous or first-name-only |
| Trust badges present (where relevant) | Security, compliance, awards | No trust indicators |
| Numbers-based proof | "10,000+ teams use..." | No scale indicators |

### Dimension 6: Objection Handling

| Check | Pass | Fail |
|-------|------|------|
| Price/value objection addressed | ROI calculation, "starts at $X" | No pricing context |
| "Will this work for me?" answered | Use cases, industry examples | Generic positioning only |
| Risk reduction offered | Free trial, guarantee, no CC required | No risk reversal |
| Implementation concern addressed | "Set up in 5 minutes" | No setup/complexity context |
| FAQ section present | Addresses top 5 objections | No FAQ or irrelevant questions |

### Dimension 7: Friction Points

| Check | Pass | Fail |
|-------|------|------|
| Form is optimized | Minimal fields, clear labels | Too many fields, unclear purpose |
| Next step is clear | Obvious path forward from every section | Confusing navigation or dead ends |
| Mobile experience | Fully responsive, touch-friendly | Desktop-only design |
| Load time | < 3 seconds | > 5 seconds |
| No distracting elements | Clean, focused design | Popups, auto-play video, chat widget on load |

---

## Above-the-Fold Engineering

The above-the-fold area is the most valuable real estate on any page. It determines whether visitors scroll or bounce.

### Required Elements (Above the Fold)

```
┌──────────────────────────────────────────┐
│  [Nav: Logo + 3-5 links + Primary CTA]  │
├──────────────────────────────────────────┤
│                                          │
│  HEADLINE: Primary value proposition     │
│                                          │
│  SUBHEADLINE: Supporting detail          │
│                                          │
│  [PRIMARY CTA BUTTON]                   │
│  [Secondary CTA: text link]             │
│                                          │
│  [Social proof: logos or stat]           │
│                                          │
│  [Hero image or product screenshot]      │
│                                          │
└──────────────────────────────────────────┘
```

### Above-the-Fold Rules

- Headline is the largest text on the page
- CTA button is the most visually prominent interactive element
- Social proof appears above the fold (even just logo strip)
- Hero image shows the product in use (not abstract graphics)
- No auto-play video or animation that distracts from the CTA
- Navigation is minimal (3-5 items max, CTA in nav)

---

## Social Proof Hierarchy

Not all social proof is equal. Use the right type at the right location.

### Social Proof Power Ranking

| Rank | Type | Strength | Best Placement |
|------|------|----------|----------------|
| 1 | Case study with metrics | "Company X increased revenue 40% in 3 months" | Mid-page, after benefits section |
| 2 | Named testimonial with photo | Full name, title, company, headshot | Near CTA, after objection handling |
| 3 | Aggregate numbers | "10,000+ teams" or "4.8/5 on G2" | Above the fold, near headline |
| 4 | Customer logos | Recognizable brand logos | Above the fold, logo strip |
| 5 | Awards/badges | "G2 Leader 2026", "SOC2 Certified" | Footer or near CTA |
| 6 | Generic testimonial | "Great product!" -- no specifics | Do not use (no credibility) |

### Placement Rules

- Logo strip: Above the fold, below the CTA
- Testimonials: After the section that makes the claim they validate
- Case studies: Mid-page, as their own section
- Numbers: Inline with headline or subheadline
- Trust badges: Near the primary CTA and near the form

---

## Objection Handling Architecture

### The 5 Universal Objections

Every product page must address these five objections. If the page does not, conversions leak.

| Objection | How to Address | Page Element |
|-----------|---------------|--------------|
| "Is this worth the money?" | ROI calculator, pricing comparison, "saves X hours" | Benefits section + pricing context |
| "Will this work for my situation?" | Industry examples, use case sections, persona targeting | "Who uses this" section |
| "Is this hard to set up?" | "Set up in 5 minutes", onboarding preview, integration logos | Feature section or FAQ |
| "What if it doesn't work?" | Free trial, money-back guarantee, no CC required | Near CTA |
| "Why this over alternatives?" | Comparison table, differentiators, switcher testimonials | Mid-page or FAQ |

### FAQ Design for Objection Handling

The FAQ section should be the last defense before conversion. Structure it to address the 5 objections:

1. "How long does setup take?" (complexity objection)
2. "Can I cancel anytime?" (commitment objection)
3. "What's included in the free trial?" (value objection)
4. "Do you integrate with [popular tool]?" (compatibility objection)
5. "How is this different from [competitor]?" (alternatives objection)

---

## Page-Type Playbooks

### Homepage

| Element | Best Practice |
|---------|---------------|
| Audience | Cold visitors who may not know you |
| Headline | Position the company, not a single feature |
| CTA split | Primary: "Start Free Trial" / Secondary: "See Demo" or "Learn More" |
| Content | Overview of benefits, social proof, feature highlights, use cases |
| Navigation | Full site navigation (unlike landing pages) |

### Landing Page (Paid Traffic)

| Element | Best Practice |
|---------|---------------|
| Navigation | Remove or minimize (no escape routes) |
| Headline | Message-match with the ad that drove the click |
| CTA | Single action, repeated 2-3 times down the page |
| Content | Complete argument on one page: problem > solution > proof > CTA |
| Social proof | Directly relevant to the ad audience |

### Pricing Page

| Element | Best Practice |
|---------|---------------|
| Plan presentation | Good-Better-Best with recommended plan highlighted |
| Toggle | Annual/Monthly with savings percentage shown |
| Feature comparison | Full table below the fold |
| FAQ | "Which plan is right for me?" as first question |
| CTA | Per-plan CTA with plan-specific copy |
| Social proof | Logos and testimonials relevant to each tier |

### Feature Page

| Element | Best Practice |
|---------|---------------|
| Headline | Benefit of the feature, not the feature name |
| Content | Use cases > technical capabilities |
| Demo | Screenshot, GIF, or interactive demo |
| CTA | "Try this feature" or "Start Free Trial" |
| Internal links | Link to related features and pricing |

### Blog Post

| Element | Best Practice |
|---------|---------------|
| CTA type | Contextual inline CTA matching the content topic |
| Placement | After introduction, at natural breaks, at end |
| CTA style | Inline banner or text link, not aggressive popup |
| Content CTA | Offer a related resource (template, checklist, tool) |

---

## Copy Alternatives Methodology

When recommending copy changes, always provide 2-3 alternatives with reasoning.

### Alternative Generation Framework

For each key element (headline, subheadline, CTA), generate variants across these axes:

| Axis | Variant A | Variant B | Variant C |
|------|-----------|-----------|-----------|
| Benefit focus | Outcome-focused | Problem-focused | Feature-focused |
| Specificity | Numbers and data | Customer quote | Use case scenario |
| Tone | Direct and assertive | Conversational | Aspirational |

### Example

**Current headline:** "Marketing Automation Software"

| Variant | Copy | Rationale |
|---------|------|-----------|
| A (outcome) | "Generate 3X More Qualified Leads Without Adding Headcount" | Specific outcome + pain point |
| B (problem) | "Stop Losing Leads Because Your Team Can't Follow Up Fast Enough" | Addresses the pain directly |
| C (social proof) | "How 2,000+ Marketing Teams Hit Their Pipeline Targets" | Authority + specificity |

**Recommendation:** Test A first (most specific), B if A does not outperform current (different psychological angle).

---

## Traffic Source Matching

Different traffic sources require different page optimization strategies.

| Source | Visitor State | Page Must Do |
|--------|-------------|-------------|
| Paid search (brand) | Knows you, high intent | Fast path to action, minimal education |
| Paid search (non-brand) | Problem-aware, solution-seeking | Prove you solve their specific problem |
| Paid social | Interrupted, low intent | Hook attention, educate, build interest |
| Organic search | Research-mode | Comprehensive content, gradual conversion |
| Email | Already engaged | Deliver on the email promise, reduce friction |
| Referral | Pre-sold by referrer | Validate referrer's recommendation, fast CTA |

### Message Match Audit

For paid traffic: Compare the ad copy with the landing page headline. They must share:
- The same language/terminology
- The same promise
- The same offer
- Visual consistency (if display ad)

**Mismatch = wasted ad spend.** Users who click an ad about "free SEO audit" and land on a generic homepage will bounce.

---

## A/B Test Framework

### Test Priority Matrix

| Priority | What to Test | Expected Impact |
|----------|-------------|-----------------|
| 1 | Headline copy | 10-30% conversion lift |
| 2 | CTA copy and color | 5-20% conversion lift |
| 3 | Social proof placement | 5-15% conversion lift |
| 4 | Above-the-fold layout | 5-20% conversion lift |
| 5 | Form field reduction | 5-10% completion lift |
| 6 | Hero image vs video | 2-10% lift (variable) |

### Test Design Rules

- One variable per test (unless running a multivariate test with sufficient traffic)
- Minimum 200 conversions per variant before declaring a winner
- Run for full business cycles (minimum 2 weeks)
- Track downstream metrics (not just page conversion, but lead quality / revenue)

### Fix vs Test Decision

| Situation | Action |
|-----------|--------|
| Obvious UX problem (broken form, missing CTA) | Fix immediately, no test needed |
| Missing social proof | Add it, no test needed |
| Headline copy alternative | A/B test |
| Layout change | A/B test |
| Removing page elements | A/B test |
| Adding a new section | A/B test |

---

## Metrics and Benchmarks

### Conversion Rate Benchmarks

| Page Type | Below Average | Average | Good | Excellent |
|-----------|-------------|---------|------|-----------|
| SaaS homepage | < 2% | 2-4% | 4-7% | > 7% |
| Landing page (paid) | < 5% | 5-10% | 10-20% | > 20% |
| Pricing page | < 3% | 3-5% | 5-10% | > 10% |
| Blog post (to email) | < 1% | 1-3% | 3-5% | > 5% |
| Feature page | < 2% | 2-5% | 5-8% | > 8% |

### Key Metrics

| Metric | What It Tells You |
|--------|------------------|
| Bounce rate | Is the page meeting visitor expectations? |
| Scroll depth | How much of the page are visitors seeing? |
| Time on page | Are visitors reading or immediately leaving? |
| CTA click rate | Is the CTA compelling and visible? |
| Form start rate | Are visitors beginning the conversion process? |
| Form completion rate | Are they finishing it? |

---

## Output Artifacts

| Artifact | Format | Description |
|----------|--------|-------------|
| CRO Audit Report | 7-dimension analysis | Per-dimension assessment with severity ratings |
| Quick Wins List | Bullet list (max 5) | Implementable today with expected impact |
| High-Impact Recommendations | Structured list | Each with rationale, effort estimate, and success metric |
| Copy Alternatives | Side-by-side table | 2-3 variants per key element with reasoning |
| A/B Test Plan | Prioritized table | Hypothesis, variant, success metric, priority |
| Traffic Source Matching Audit | Source x page element table | Message match assessment per traffic source |

---

## Related Skills

- **form-cro** -- Use when the form on the page is the specific bottleneck (field optimization, validation, mobile form UX).
- **signup-flow-cro** -- Use when users convert on the page but drop off during the signup/registration process.
- **popup-cro** -- Use when considering a popup as an additional conversion layer on the page.
- **onboarding-cro** -- Use when post-conversion activation is the real problem and the page itself converts adequately.
- **pricing-strategy** -- Use when the pricing page needs structural redesign (tier structure, value metric), not just CRO tweaks.
