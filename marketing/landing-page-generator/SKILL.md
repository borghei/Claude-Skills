---
name: landing-page-generator
description: >
  Plan and build landing pages: page structure, copy frameworks (PAS, AIDA, BAB),
  CTA strategy, SEO meta and Core Web Vitals. Use when creating landing, campaign,
  lead capture or conversion pages.
license: MIT
metadata:
  version: 1.0.0
  author: borghei
  category: marketing
  domain: conversion
  updated: 2026-11-08
  tags:
    - landing-pages
    - conversion
    - copywriting
    - seo
    - core-web-vitals
---
# Landing Page Generator

Design and build high-converting landing pages using proven copy frameworks, section patterns, and conversion optimization techniques. The agent settles the single goal first, builds only the sections the offer has material for, and checks CTAs, conversion basics and page weight with the bundled tools before launch.

---

## Table of Contents

- [Keywords](#keywords)
- [Quick Start](#quick-start)
- [Core Workflows](#core-workflows)
- [Conversion Optimization Checklist](#conversion-optimization-checklist)
- [Design Style Reference](#design-style-reference)
- [CTA Strategy](#cta-strategy)
- [SEO and Performance](#seo-and-performance)
- [Anti-Patterns](#anti-patterns)
- [Best Practices](#best-practices)
- [Integration Points](#integration-points)

---

## Keywords

landing page, landing page design, conversion optimization, lead capture page, campaign page, marketing page, hero section, CTA strategy, landing page copy, landing page generator, promo page, conversion page, lead gen page, single-page site, landing page template, A/B testing, page layout, above the fold, social proof, pricing table, FAQ section, testimonial block

---

## When to Use

- **A new landing, campaign or lead-capture page** needs a structure, copy plan and CTA strategy
- **A page converts poorly** and needs a checklist pass on message match, CTA and friction
- **Paid or email traffic** needs a page whose headline matches the ad or email
- **A page reads generic** (template sections, vague buttons, invented proof) and needs fixing before launch

## Clarify First

Before generating the page, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Conversion goal & offer:** the single action and what the visitor gets (every page has one goal and one CTA).
- **Target audience & awareness level:** who they are and what they know (selects the copy framework PAS/AIDA/BAB).
- **Key pain point & key benefit:** the problem and the primary outcome (drives the hero headline and Problem/Solution sections).
- **Traffic source:** ads, email, or organic (sets message match and page adaptation).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

### Generate a Landing Page

1. Gather inputs: product, audience, pain point, key benefit, offer
2. Select design style (dark-saas, clean-minimal, bold-startup, enterprise)
3. Choose copy framework (PAS, AIDA, BAB) based on audience awareness
4. Build sections in order: Hero > Problem > Solution > Social Proof > How It Works > CTA
5. Run conversion optimization checklist before publishing
6. Set up A/B test for headline and CTA variants

### Landing Page Brief Template

```markdown
## Landing Page Brief
- Product/Service: [Name]
- Value proposition: [One sentence]
- Target audience: [Who and what they need]
- Key pain point: [Primary problem you solve]
- Key benefit: [Primary outcome they get]
- Offer: [What you are offering — trial, demo, download, purchase]
- Traffic source: [Where visitors come from — ads, email, organic]
- Design style: [dark-saas / clean-minimal / bold-startup / enterprise]
- Copy framework: [PAS / AIDA / BAB]
```

---

## Core Workflows

### Workflow 1: Full Landing Page Build [PROVEN]

**Step 1: Define the Single Goal**

Every landing page has one purpose and one CTA. Define it before anything else:
- What action do you want the visitor to take?
- What does the visitor get in return?
- What is the traffic source (this determines headline matching)?

**Step 2: Select Copy Framework**

| Framework | Best When | Audience Awareness Level |
|-----------|-----------|------------------------|
| PAS (Problem > Agitate > Solve) | Audience knows the problem | Problem-aware |
| AIDA (Attention > Interest > Desire > Action) | Audience needs education | Unaware to problem-aware |
| BAB (Before > After > Bridge) | Audience wants transformation | Solution-aware |

**Step 3: Build Sections in Order**

| Order | Section | Purpose |
|-------|---------|---------|
| 1 | Hero | Communicate value in 5 seconds |
| 2 | Social proof bar | Build instant credibility |
| 3 | Problem statement | Show you understand their pain |
| 4 | Solution / Benefits | Present your answer |
| 5 | How it works | Reduce perceived complexity |
| 6 | Features with benefits | Detail what they get |
| 7 | Testimonials | Proof from real customers |
| 8 | Pricing (if applicable) | Help them decide |
| 9 | FAQ | Handle objections |
| 10 | Final CTA | Repeat the ask with risk reversal |

**Step 4: Write Copy Per Section**

Use the section-specific guidelines in `references/section-and-copy-library.md`.

**Step 5: Optimize for Conversion**

Run the Conversion Optimization Checklist and the three tools before launching:

```bash
python3 marketing/landing-page-generator/scripts/cta_analyzer.py page.html
python3 marketing/landing-page-generator/scripts/conversion_checklist.py page.html --format json
python3 marketing/landing-page-generator/scripts/page_speed_estimator.py page.html
```

Validation checkpoint: all three tools exit 0 (no vague label, a CTA within the first screen of
copy, one h1, a viewport and a title, no FAIL in the speed estimate). The tools cannot tell real proof
from invented proof: check by hand that every logo, quote and count on the page traces to the brief.

### Workflow 2: Campaign Landing Page [PROVEN]

For ad campaigns, email campaigns, or launch events:

**Step 1: Message Match**

The landing page headline MUST match the ad/email that drives traffic:
- If ad says "Reduce churn by 30%," the landing page headline must say "Reduce churn by 30%"
- Mismatched expectations cause immediate bounce

**Step 2: Single Message Focus**

Remove all navigation, sidebar links, and secondary CTAs:
- No header navigation (removes exit paths)
- No footer links except legal requirements
- One CTA repeated 2-3 times on the page
- Every section supports the single conversion goal

**Step 3: Traffic Source Adaptation**

| Traffic Source | Page Adaptation |
|---------------|----------------|
| Paid search (Google) | Lead with the searched keyword in H1 |
| Paid social (Meta, LinkedIn) | Lead with the ad's hook/benefit |
| Email campaign | Lead with the email's promise |
| Organic search | Lead with the comprehensive answer |
| Referral/partner | Lead with the referrer's context |

---

## Conversion Optimization Checklist

### Above the Fold

- [ ] Headline communicates value in under 6 seconds
- [ ] CTA is visible without scrolling on mobile (375px viewport)
- [ ] No more than one navigation option (or no navigation at all)
- [ ] Subheadline adds specificity to the headline
- [ ] Visual supports the message (not decorative)

### Page-Wide

- [ ] Single conversion goal throughout the page
- [ ] CTA appears 2-3 times (hero, mid-page, footer)
- [ ] Social proof appears within the first two scrolls
- [ ] Every feature has a corresponding benefit
- [ ] Objections addressed before the final CTA
- [ ] Risk reversal stated near every CTA
- [ ] No external links that compete with the CTA
- [ ] Form asks for minimum required information

### Trust and Credibility

- [ ] Customer testimonials are named and specific
- [ ] Company logos used with permission
- [ ] Security badges and certifications visible if relevant
- [ ] Privacy policy linked from any data collection form
- [ ] Physical address or company information available

### Mobile

- [ ] Page loads under 3 seconds on mobile
- [ ] CTA button is thumb-friendly (minimum 48px height)
- [ ] Text is readable without zooming (16px minimum)
- [ ] No horizontal scrolling
- [ ] Forms are usable on mobile keyboards

---

## Design Style Reference

### Style Options

| Style | Visual Tone | Best For |
|-------|-----------|----------|
| Dark SaaS | Dark backgrounds, one accent, at most one effect behind the product UI | Developer tools, technical products, modern SaaS |
| Clean Minimal | White backgrounds, subtle borders, clean typography | Professional services, healthcare, education |
| Bold Startup | Large typography, bright colors, dynamic layouts | Consumer products, startups, creative tools |
| Enterprise | Muted tones, structured layouts, conservative design | B2B enterprise, finance, government |

### Visual Hierarchy Rules

1. Headline is the largest text element on the page
2. CTA button is the most visually prominent element
3. Supporting text is noticeably smaller than headlines
4. White space separates sections and creates breathing room
5. Color contrast meets WCAG AA standards (4.5:1 minimum for text)
6. Recommended plan on pricing pages is visually distinguished

---

## CTA Strategy

### CTA Placement

| Position | Purpose | Copy Approach |
|----------|---------|---------------|
| Hero | Primary conversion point | Action + benefit: "Start my free trial" |
| After benefits | Capture interest momentum | The same button; the line under it carries the benefit just shown |
| After social proof | Capitalize on trust | The same button; under it a real, sourced count if the client has one |
| Page footer | Final catch | The same button; under it the risk reversal ("Free for 14 days, no card") |

The button label stays word for word the same at every position, so the visitor sees one action;
what changes is the supporting line under it. A secondary action (a demo, the pricing table) gets one
other label, used the same way everywhere.

### CTA Copy Formulas [PROVEN]

```
[Action Verb] + [What They Get]
```

Never a label that names nothing: "Learn more", "Read more", "Discover", "Explore", "Click here",
"Submit" or "Unlock". `cta_analyzer.py` scores these as `vague`.
- "Start my free trial"
- "Get the complete guide"
- "See pricing for my team"
- "Create my first dashboard"

### Supporting CTA Text

Below the button, reduce friction:
- "No credit card required"
- "Set up in 2 minutes"
- "Cancel anytime"
- "Free for 14 days"
- A real customer count, never a rounded "10,000+"

---

## SEO and Performance

### SEO Checklist

- [ ] Title tag: primary keyword + brand, 50-60 characters
- [ ] Meta description: benefit + CTA, 150-160 characters
- [ ] H1: one per page, includes primary keyword
- [ ] OG image: 1200x630px with product name and value proposition
- [ ] Canonical URL set
- [ ] Image alt text on all images
- [ ] Structured data: FAQPage schema if FAQ section exists
- [ ] Mobile viewport meta tag present

### Performance Targets

| Metric | Target | How to Achieve |
|--------|--------|---------------|
| Largest Contentful Paint (LCP) | Under 2.5 seconds | Optimize hero image, use modern formats (WebP/AVIF) |
| Cumulative Layout Shift (CLS) | Under 0.1 | Set explicit dimensions on all images and embeds |
| Interaction to Next Paint (INP) | 200ms or less | Defer non-critical JavaScript, break up long tasks (INP replaced FID in March 2024) |
| Time to First Byte (TTFB) | Under 600ms | Use CDN, server-side rendering, or static generation |
| Total page weight | Under 1MB | Compress images, minimize JavaScript bundles |

---

## Anti-Patterns

### The Template Section Stack
**Mistake:** Every section built as eyebrow, claim heading, short lede and three icon cards, with a strip of round figures under the hero.
**Why it happens:** It fits any offer, so it is what templates and generators produce first, and it looks finished at a glance.
**Instead:** Keep only the sections the offer has material for. A section with nothing true to say goes; the order in Workflow 1 is a maximum, not a checklist.

### Invented Proof
**Mistake:** "Trusted by 10,000+ teams", three polished testimonials and a logo wall that nobody can source.
**Why it happens:** Social proof ranks high for conversion, and an empty proof slot looks unfinished.
**Instead:** Only proof the client can source and has permission to show, quoted exactly. Without it, show plain facts (price, trial terms, a verifiable count) or nothing. Invented reviews also carry legal risk under consumer-protection rules.

### Vague Buttons
**Mistake:** "Learn more", "Explore" or "Get started" as the main action.
**Why it happens:** They fit every page and feel low-pressure.
**Instead:** A verb plus what the visitor gets ("Start my free trial", "Book a demo for my team"), worded the same in the hero, mid-page and the close.

### Hype in Place of Facts
**Mistake:** Headlines built from "seamless", "cutting-edge", "unlock the power of", "next-level".
**Why it happens:** Without a fact sheet, adjectives fill the space where specifics should go.
**Instead:** Name the category and one measured benefit from the brief. If no fact exists, a plainer line beats an inflated one.

## Best Practices

1. **One page, one goal** — Every element on the page must serve the single conversion objective. If it does not help convert, remove it.

2. **Match the message** — The landing page headline must mirror the ad, email, or link that drove the visit. Mismatched expectations are the top bounce cause.

3. **Remove navigation** — Landing pages should have no header navigation, no sidebar, and no footer links except legal requirements. Every exit path is a lost conversion.

4. **Mobile first** — Design for 375px viewport first. The majority of ad traffic arrives on mobile devices.

5. **Above-the-fold CTA** — The primary CTA must be visible without scrolling on both desktop and mobile.

6. **Social proof early** — Place credibility signals within the first two scrolls. Trust is a prerequisite for conversion.

7. **Minimize form fields** — Every additional field reduces conversion. Ask for the minimum needed to qualify the lead.

8. **Speed is conversion** — Every second of load time reduces conversion rate by approximately 7%. Optimize aggressively.

9. **Test relentlessly** — The headline alone can produce 20-50% conversion differences. A/B test every high-impact element.

10. **Risk reversal near every CTA** — "No credit card required," "Money-back guarantee," "Cancel anytime." Remove the last objection at the moment of decision.

---

## Integration Points

- **Marketing Site Builder** (`engineering/marketing-site-builder`) — Use when building the page (a campaign page here drops the nav; a site page there keeps a short one): one system, copy-tell and copy-device lint, consistency, structure, access and style checks, run together by `finish_gate.py` with written waivers and a round limit.
- **Copywriting** — Use for the copy layer. Landing Page Generator handles structure and optimization. Copywriting handles the words.
- **Ad Creative** — Use for the ads driving traffic to the landing page. Ensure message match between ad and page.
- **Marketing Psychology** — Use psychological principles (anchoring, social proof, loss aversion) to strengthen page elements.
- **Campaign Analytics** — Use to measure landing page performance and feed insights into optimization.
- **Brand Guidelines** — Reference brand visual and voice standards for consistency.
- **Content Humanizer** — Use if page copy sounds robotic or generic after initial drafting.

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| High bounce rate from paid traffic | Headline doesn't match the ad | Ensure exact message match between ad copy and landing page H1. |
| CTA below fold on mobile | Hero section too tall or CTA not prioritized | Test on 375px viewport. CTA must be visible without scrolling. |
| Good traffic but zero conversions | Conversion tracking broken | Verify pixel fires on thank-you page. Test with a real conversion. |
| Slow page load (>3s mobile) | Unoptimized images, heavy JS | Run `page_speed_estimator.py`. Convert images to WebP, defer non-critical JS. |
| Form submissions but no leads in CRM | Form-to-CRM integration broken | Test form submission end-to-end. Check webhook/API connection. |
| Multiple CTAs confusing visitors | Too many conversion paths | Single goal per landing page. All CTAs drive the same action. |
| Low conversion despite good copy | No social proof or risk reversal | Run `conversion_checklist.py`. Add the real, attributed proof the client has, and a true risk reversal ("no credit card") near CTAs; never invent either. |

---

## Success Criteria

- Conversion rate above 6.6% (2025 median across industries) for primary CTA
- Page loads under 3 seconds on mobile (LCP under 2.5s, CLS under 0.1)
- CTA visible above fold on both desktop (1440px) and mobile (375px)
- Single conversion goal with no competing navigation or exit paths
- Message match: landing page headline mirrors the traffic source (ad, email, link)
- Social proof visible within first two scrolls
- A/B test running on headline or CTA at all times for high-traffic pages

---

## Scope & Limitations

**In Scope:** Landing page structure, section patterns, copy framework application, conversion optimization, CTA strategy, SEO meta tags, A/B testing framework, design style guidance.

**Out of Scope:** Page copy writing (use copywriting), paid ad campaigns driving traffic (use paid-ads), CMS/website builder administration, analytics platform setup. Building the page itself on one design system, with copy-tell linting, design-value consistency and a static structure gate, is covered by `engineering/marketing-site-builder`.

**Limitations:** Conversion benchmarks vary significantly by industry, traffic source, and offer type. The 6.6% median is across all industries; SaaS trials may see 10-25% while e-commerce may see 2-3%.

---

## Files

### Tools Overview

### 1. Page Speed Estimator (`scripts/page_speed_estimator.py`)
Estimates Core Web Vitals from HTML source: LCP, CLS risk, script/image analysis, and conversion impact.

```bash
python3 scripts/page_speed_estimator.py page.html
python3 scripts/page_speed_estimator.py page.html --format json
```

### 2. CTA Analyzer (`scripts/cta_analyzer.py`)
Analyzes CTA placement, copy strength, friction level, and consistency across the landing page.

```bash
python3 scripts/cta_analyzer.py page.html
python3 scripts/cta_analyzer.py page.html --format json
```

### 3. Conversion Checklist (`scripts/conversion_checklist.py`)
Runs a 22-point conversion audit from source (structure, CTAs, proof, trust, SEO, mobile, form length) and grades it.

```bash
python3 scripts/conversion_checklist.py page.html
python3 scripts/conversion_checklist.py page.html --format json
```

All three take `--format text|json` (`--json` still works). Exit codes:

| Script | 0 | 1 | 2 |
|---|---|---|---|
| `cta_analyzer.py` | no blocking issue | no CTA, none within the first 60 words of visible copy, or a vague label | missing, unreadable or non-HTML file |
| `conversion_checklist.py` | every gating check passes | H1 missing, more than one H1, no CTA, no viewport or no title | as above |
| `page_speed_estimator.py` | no FAIL check | page over 1MB, or estimated LCP or CLS risk in the poor band | as above |

The proof checks in `conversion_checklist.py` (logos, testimonials, counts) only report what is
missing and never set the exit code: the fix for a missing proof element is the client's real proof
or nothing.

### Reference Documentation

| File | Purpose |
|------|---------|
| `assets/sample_landing_page.html` | A small trial-signup page; all three tools exit 0 |
| `assets/flawed_landing_page.html` | Two h1s, vague labels below the first screen, no viewport, six images without dimensions; all three exit 1 |
| `assets/malformed_landing_page.html` | Plain text with an `.html` name; all three exit 2 |
| `references/section-and-copy-library.md` | Hero, problem, solution, how-it-works, social proof, pricing, FAQ and final CTA patterns; PAS, AIDA and BAB mapped onto the page; A/B testing framework and test log |
