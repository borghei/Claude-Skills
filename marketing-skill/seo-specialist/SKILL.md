---
name: seo-specialist
description: >
  Expert SEO covering technical SEO, content optimization, link building, keyword research, and search analytics.
  Use when auditing technical SEO issues, researching keywords by intent and difficulty, optimizing on-page elements, building link acquisition strategies, or analyzing organic search performance.
version: 1.0.0
author: borghei
category: marketing-growth
tags: [seo, search, keywords, technical-seo, link-building]
---

# SEO Specialist

The agent operates as a senior SEO specialist, delivering technical audits, keyword strategies, on-page optimization, link building plans, and performance analysis for organic search growth.

## Workflow

1. **Run technical audit** - Check crawlability (robots.txt, sitemap, canonical tags), indexability (duplicate content, thin pages), performance (Core Web Vitals), and structure (URL hierarchy, internal linking). Checkpoint: zero critical crawl errors in Search Console.
2. **Research keywords** - Start with seed keywords, expand via competitor analysis and search suggest, analyze by volume/difficulty/intent, and prioritize by business value and ranking opportunity. Checkpoint: each target keyword has a mapped content asset.
3. **Optimize on-page elements** - Apply title tag, meta description, heading hierarchy, keyword placement, image alt text, and schema markup. Checkpoint: primary keyword appears in H1, first 100 words, and title tag.
4. **Build link acquisition plan** - Identify content-based (original research, guides), outreach-based (guest posts, HARO), and relationship-based (partners, testimonials) opportunities. Checkpoint: target links have DA 50+ and topical relevance.
5. **Monitor and report** - Track organic traffic, keyword rankings, Core Web Vitals, and conversion rate. Review weekly; report monthly. Checkpoint: dashboard covers visibility, engagement, and conversions.

## Technical SEO Audit Checklist

**Crawlability:**
- [ ] Robots.txt properly configured
- [ ] XML sitemap submitted and current
- [ ] No critical crawl errors in Search Console
- [ ] Canonical tags on all indexable pages
- [ ] Noindex/nofollow used correctly

**Performance (Core Web Vitals):**

| Metric | Good | Needs Improvement | Poor |
|--------|------|-------------------|------|
| LCP (Largest Contentful Paint) | < 2.5s | 2.5s - 4s | > 4s |
| FID (First Input Delay) | < 100ms | 100 - 300ms | > 300ms |
| CLS (Cumulative Layout Shift) | < 0.1 | 0.1 - 0.25 | > 0.25 |

**Structure:**
- [ ] Clean, descriptive URL slugs
- [ ] Proper heading hierarchy (single H1, logical H2/H3)
- [ ] Internal linking between related content
- [ ] Breadcrumbs implemented

## Keyword Research Process

1. **Seed** - Brainstorm topics, analyze competitors, mine customer interviews
2. **Expand** - Use Ahrefs/SEMrush, Google Suggest, People Also Ask, related searches
3. **Analyze** - Score by search volume, keyword difficulty, search intent, SERP features
4. **Prioritize** - Rank by business value x ranking opportunity

### Keyword Metrics Guide

| Metric | Good | Moderate | Difficult |
|--------|------|----------|-----------|
| Volume | 1000+ | 100-1000 | < 100 |
| Difficulty | < 30 | 30-60 | > 60 |
| CPC (commercial signal) | > $5 | $1-5 | < $1 |

### Search Intent Classification

| Intent | Signal Words | Content Type |
|--------|-------------|-------------|
| Informational | "how to", "what is", "guide" | Blog posts, tutorials |
| Navigational | Brand names, product names | Homepage, product pages |
| Commercial | "best", "reviews", "vs" | Comparison pages, reviews |
| Transactional | "buy", "discount", "pricing" | Product pages, landing pages |

## On-Page Optimization Checklist

**Title Tag:** primary keyword front-loaded, 50-60 characters, compelling for CTR
**Meta Description:** includes keyword, clear value prop, CTA, 150-160 characters
**Headings:** H1 contains primary keyword, H2s contain secondary keywords, logical hierarchy
**Content:** keyword in first 100 words, natural density, related terms (LSI), comprehensive coverage
**Images:** descriptive filenames, keyword-rich alt text, compressed, lazy-loaded

## Example: Optimized Page Structure

```html
<!-- Title: 58 chars, keyword front-loaded -->
<title>Cloud Cost Optimization: 7 Strategies That Cut AWS Bills 40%</title>

<!-- Meta: 155 chars, keyword + value prop + CTA -->
<meta name="description" content="Learn 7 proven cloud cost optimization
strategies used by 500+ engineering teams. Reduce AWS spend by 40% without
sacrificing performance. Free checklist inside.">

<!-- Schema markup for article -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Cloud Cost Optimization: 7 Strategies That Cut AWS Bills 40%",
  "author": {"@type": "Person", "name": "Jane Chen"},
  "datePublished": "2026-02-15",
  "publisher": {
    "@type": "Organization",
    "name": "CloudOps Weekly"
  }
}
</script>

<h1>Cloud Cost Optimization: 7 Strategies That Cut AWS Bills 40%</h1>
<p>Cloud cost optimization is the #1 priority for engineering leaders in 2026...</p>

<h2>1. Right-Size EC2 Instances Using Usage Data</h2>
<h3>How to Identify Oversized Instances</h3>

<h2>FAQ</h2>
<h3>What is cloud cost optimization?</h3>
<h3>How much can cloud optimization save?</h3>
```

## Link Quality Assessment

| Factor | High Quality | Low Quality |
|--------|-------------|-------------|
| Domain Authority | 50+ | < 20 |
| Relevance | Same industry | Unrelated |
| Traffic | Active site | Dead site |
| Link Type | Editorial | Paid/Spam |
| Anchor Text | Natural variation | Exact match spam |

## SEO Performance Dashboard

```
SEO Performance - March 2026
  Organic Traffic: 125,432 (+12% MoM)
  Rankings: Top 3: 45 | Top 10: 234
  Conversions: 542 (+15% MoM)

  Top Growing Keywords
  1. "cloud cost optimization" - #8 -> #3 (+5)
  2. "aws billing alerts"     - #15 -> #7 (+8)
  3. "kubernetes autoscaling"  - New -> #12

  Technical Health
  Core Web Vitals: Pass | Index: 1,234 pages | Crawl Errors: 3
```

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

## Reference Materials

- `references/technical_seo.md` - Technical SEO guide
- `references/keyword_research.md` - Keyword research methods
- `references/link_building.md` - Link building playbook
- `references/algorithm_updates.md` - Google update history
