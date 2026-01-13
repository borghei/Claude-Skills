---
name: seo-specialist
description: Expert SEO covering technical SEO, content optimization, link building, keyword research, and search analytics.
version: 1.0.0
author: Claude Skills
category: marketing-growth
tags: [seo, search, keywords, technical-seo, link-building]
---

# SEO Specialist

Expert-level search engine optimization.

## Core Competencies

- Technical SEO
- On-page optimization
- Content SEO
- Link building
- Keyword research
- Local SEO
- Analytics and reporting
- Algorithm updates

## Technical SEO

### Site Audit Checklist

**Crawlability:**
- [ ] Robots.txt properly configured
- [ ] XML sitemap submitted
- [ ] No crawl errors in Search Console
- [ ] Proper use of noindex/nofollow
- [ ] Canonical tags implemented

**Indexability:**
- [ ] Important pages indexed
- [ ] Duplicate content resolved
- [ ] Thin content identified
- [ ] Pagination handled correctly

**Performance:**
- [ ] Core Web Vitals passing
- [ ] Mobile-friendly
- [ ] HTTPS implemented
- [ ] Page speed optimized

**Structure:**
- [ ] Clean URL structure
- [ ] Proper heading hierarchy
- [ ] Internal linking optimized
- [ ] Breadcrumbs implemented

### Core Web Vitals

```
LCP (Largest Contentful Paint)
├── Good: < 2.5s
├── Needs Improvement: 2.5s - 4s
└── Poor: > 4s

FID (First Input Delay)
├── Good: < 100ms
├── Needs Improvement: 100ms - 300ms
└── Poor: > 300ms

CLS (Cumulative Layout Shift)
├── Good: < 0.1
├── Needs Improvement: 0.1 - 0.25
└── Poor: > 0.25
```

### Schema Markup

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Article Title",
  "author": {
    "@type": "Person",
    "name": "Author Name"
  },
  "datePublished": "2024-01-15",
  "dateModified": "2024-01-20",
  "image": "https://example.com/image.jpg",
  "publisher": {
    "@type": "Organization",
    "name": "Company Name",
    "logo": {
      "@type": "ImageObject",
      "url": "https://example.com/logo.png"
    }
  }
}
```

## Keyword Research

### Research Process

```
1. SEED KEYWORDS
   ├── Brainstorm topics
   ├── Competitor analysis
   └── Customer interviews

2. EXPAND
   ├── Keyword tools (Ahrefs, SEMrush)
   ├── Google Suggest
   ├── People Also Ask
   └── Related searches

3. ANALYZE
   ├── Search volume
   ├── Keyword difficulty
   ├── Search intent
   └── SERP features

4. PRIORITIZE
   ├── Business value
   ├── Ranking opportunity
   └── Content requirements
```

### Keyword Metrics

| Metric | Good | Moderate | Difficult |
|--------|------|----------|-----------|
| Volume | 1000+ | 100-1000 | <100 |
| Difficulty | <30 | 30-60 | >60 |
| CPC | >$5 | $1-5 | <$1 |

### Search Intent Types

**Informational:**
- "how to", "what is", "guide"
- Content: Blog posts, guides, tutorials

**Navigational:**
- Brand names, specific products
- Content: Homepage, product pages

**Commercial:**
- "best", "reviews", "vs"
- Content: Comparison, reviews, lists

**Transactional:**
- "buy", "discount", "pricing"
- Content: Product pages, landing pages

## On-Page Optimization

### Page Optimization Checklist

**Title Tag:**
- Primary keyword included
- Front-loaded if possible
- 50-60 characters
- Compelling for clicks

**Meta Description:**
- Includes keyword
- Clear value proposition
- Call to action
- 150-160 characters

**Headings:**
- H1 contains primary keyword
- H2s contain secondary keywords
- Logical hierarchy
- Descriptive and scannable

**Content:**
- Keyword in first 100 words
- Natural keyword usage
- Related terms included
- Comprehensive coverage

**Images:**
- Descriptive file names
- Alt text with keywords
- Compressed for speed
- Lazy loading enabled

### Content Optimization Template

```markdown
# [Primary Keyword] - [Compelling Hook]

[Introduction with primary keyword in first 100 words]

## [H2 with Secondary Keyword]

[Content section]

### [H3 with Related Term]

[Subsection content]

## FAQ

### [Question with keyword]
[Answer]

## Conclusion

[Summary with CTA]
```

## Link Building

### Link Building Strategies

**Content-Based:**
- Original research and data
- Comprehensive guides
- Infographics and visual content
- Tools and calculators

**Outreach-Based:**
- Guest posting
- HARO (Help a Reporter Out)
- Podcast appearances
- Expert roundups

**Relationship-Based:**
- Partner exchanges
- Testimonials
- Case studies
- Co-marketing

### Link Quality Assessment

| Factor | High Quality | Low Quality |
|--------|-------------|-------------|
| Domain Authority | 50+ | <20 |
| Relevance | Same industry | Unrelated |
| Traffic | Active site | Dead site |
| Link Type | Editorial | Paid/Spam |
| Anchor Text | Natural | Exact match |

### Outreach Template

```
Subject: [Personalized hook]

Hi [Name],

[Personalized opening referencing their content]

[Value proposition - what you're offering]

[Clear ask]

[Sign off]
```

## Analytics & Reporting

### SEO Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│                   SEO Performance - [Period]                 │
├─────────────────────────────────────────────────────────────┤
│  Organic Traffic    Rankings          Conversions           │
│  125,432           Top 3: 45         542                    │
│  +12% MoM          Top 10: 234       +15% MoM               │
├─────────────────────────────────────────────────────────────┤
│  Top Growing Keywords                                        │
│  1. [Keyword] - #8 → #3 (+5)                               │
│  2. [Keyword] - #15 → #7 (+8)                              │
│  3. [Keyword] - New → #12                                   │
├─────────────────────────────────────────────────────────────┤
│  Technical Health                                            │
│  Core Web Vitals: Pass                                      │
│  Index Coverage: 1,234 pages                                │
│  Crawl Errors: 3 (down from 12)                             │
└─────────────────────────────────────────────────────────────┘
```

### Key Metrics

**Visibility:**
- Organic traffic
- Keyword rankings
- SERP features won
- Share of voice

**Engagement:**
- Bounce rate
- Time on site
- Pages per session
- Scroll depth

**Conversions:**
- Organic conversions
- Conversion rate
- Revenue from organic
- Assisted conversions

## Reference Materials

- `references/technical_seo.md` - Technical SEO guide
- `references/keyword_research.md` - Keyword research methods
- `references/link_building.md` - Link building playbook
- `references/algorithm_updates.md` - Google update history

## Scripts

```bash
# Site audit
python scripts/site_audit.py --url https://example.com --output audit.html

# Keyword research
python scripts/keyword_research.py --seed "cloud computing" --output keywords.csv

# Rank tracker
python scripts/rank_tracker.py --keywords keywords.csv --domain example.com

# Backlink analyzer
python scripts/backlink_analyzer.py --domain example.com --output links.csv
```
