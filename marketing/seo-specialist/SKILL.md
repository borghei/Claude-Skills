---
name: seo-specialist
description: >
  Expert SEO covering technical SEO, content optimization, link building,
  keyword research, and search analytics. Use when auditing technical SEO
  issues, researching keywords by intent and difficulty, optimizing on-page
  elements, building link acquisition strategies, or analyzing organic search
  performance.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: marketing-growth
  updated: 2026-03-31
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

---

## Troubleshooting

| Problem | Likely Cause | Fix |
|---------|-------------|-----|
| Rankings dropped after Google core update | E-E-A-T signals insufficient or content quality below new thresholds | Audit content against December 2025 / March 2026 core update criteria — add experience signals, author credentials, original data |
| High impressions but low CTR | Title tags and meta descriptions not compelling enough for the SERP | Rewrite titles with numbers, power words, and clear value props; test meta descriptions with hooks |
| FID replaced by INP — pages now failing CWV | INP measures all interactions, not just first — JS-heavy pages fail | Break long JS tasks, defer third-party scripts, audit event handlers; 43% of sites still fail INP in 2026 |
| Indexed pages declining in Search Console | Google tightening quality bar — deindexing thin or duplicate content | Consolidate thin pages, add unique content, improve E-E-A-T signals on remaining pages |
| AI Overviews stealing clicks from position 1 | Google AI Overviews now appear in 50%+ of queries, reducing organic CTR by ~42% | Optimize for AI citation (extractable content blocks), add FAQ schema, target queries less likely to trigger AI Overviews |
| Keyword cannibalization across blog and product pages | Multiple pages competing for same keyword with conflicting intent | Map one primary keyword per page, consolidate or redirect competing pages, differentiate intent |

---

## Success Criteria

- **Organic traffic growth**: 10%+ month-over-month organic traffic growth sustained over 6 months
- **Top 10 rankings**: 50%+ of target keywords ranking in top 10 positions within 6 months
- **Core Web Vitals**: All three metrics passing (LCP < 2.5s, INP < 200ms, CLS < 0.1) at 75th percentile — only 47-55% of sites achieve this in 2026
- **CTR performance**: Position 1 achieving 25%+ CTR, position 3 achieving 10%+ CTR (2026 benchmarks)
- **Conversion from organic**: Organic traffic converting at 2%+ for B2B, 2.5%+ for e-commerce (industry benchmarks)
- **Indexation health**: 95%+ of target pages indexed with zero critical crawl errors
- **E-E-A-T compliance**: Author bylines, credentials, and experience signals on 100% of content pages

---

## Scope & Limitations

**In scope:**
- Technical SEO auditing (crawlability, indexation, Core Web Vitals, site structure)
- Keyword research, intent classification, and prioritization
- On-page optimization (title tags, meta descriptions, headings, content, schema)
- Link building strategy and opportunity identification
- Organic search performance monitoring and reporting
- Algorithm update impact assessment and recovery planning

**Out of scope:**
- Paid search / Google Ads management
- Social media marketing and optimization
- Content writing and production (use Content Production skill)
- AI-specific search optimization (use AI SEO skill)
- Website development or code deployment
- Brand strategy and positioning

**Known limitations:**
- Keyword difficulty scores vary significantly across tools — no single source of truth
- Google algorithm changes 500-600 times per year; strategies require continuous adaptation
- AI Overviews are reducing organic CTR — position 1 no longer guarantees high click volume
- Backlink analysis requires third-party tools (Ahrefs, SEMrush, Moz) for comprehensive data
- INP optimization often requires developer involvement for JavaScript refactoring

---

## Integration Points

- **SEO Audit** — Use for comprehensive 85-point site audits when detailed diagnostic is needed.
- **AI SEO** — Use alongside traditional SEO for AI search citation optimization.
- **Schema Markup** — Use for structured data implementation after on-page optimization.
- **Site Architecture** — Use when structural issues (deep nesting, orphan pages) block ranking progress.
- **Content Strategy** — Use for topic selection and editorial calendar planning before SEO optimization.
- **Content Humanizer** — Use when content flagged as AI-generated needs authenticity improvement.

---

## Scripts

```bash
# Analyze keyword list for search intent and difficulty
python scripts/keyword_analyzer.py --keywords keywords.csv --json

# Simulate SERP appearance for a page
python scripts/serp_simulator.py --title "Cloud Cost Optimization Guide" --description "Learn 7 proven strategies..." --url "/guides/cloud-cost" --json

# Score content for on-page SEO quality
python scripts/content_scorer.py article.md --keyword "cloud cost optimization" --json
```
