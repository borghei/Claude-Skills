---
name: programmatic-seo
description: >
  Programmatic page generation at scale using template-based SEO, data
  pipelines, and automated content production. Covers keyword pattern mining,
  template architecture, data sourcing, quality control, and indexation strategy
  for 100-100K+ page deployments.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: marketing-growth
  updated: 2026-03-31
  tags: [seo, programmatic, templates, content-at-scale, data-driven-seo]
---
# Programmatic SEO

Production-grade framework for building SEO page sets at scale. Covers the full lifecycle from keyword pattern discovery through template design, data pipeline construction, quality assurance, and post-launch optimization. Designed for deployments ranging from 50 to 100,000+ pages.

---

## Table of Contents

- [When to Use vs When Not To](#when-to-use-vs-when-not-to)
- [Initial Assessment](#initial-assessment)
- [The 14 Playbooks](#the-14-playbooks)
- [Playbook Selection Matrix](#playbook-selection-matrix)
- [Keyword Pattern Mining](#keyword-pattern-mining)
- [Data Pipeline Architecture](#data-pipeline-architecture)
- [Template Design System](#template-design-system)
- [Quality Control Framework](#quality-control-framework)
- [Internal Linking Architecture](#internal-linking-architecture)
- [Indexation Strategy](#indexation-strategy)
- [Launch Sequence](#launch-sequence)
- [Post-Launch Optimization](#post-launch-optimization)
- [Anti-Patterns and Penalty Avoidance](#anti-patterns-and-penalty-avoidance)
- [Decision Matrix: Build vs Skip](#decision-matrix-build-vs-skip)
- [Output Artifacts](#output-artifacts)
- [Related Skills](#related-skills)

---

## When to Use vs When Not To

**Use this skill when:**
- You have a repeating keyword pattern with 50+ variations
- You have (or can acquire) structured data to populate pages
- The search intent is consistent across variations
- Your domain has sufficient authority to compete

**Do NOT use when:**
- Each page requires unique editorial content (use content-creator instead)
- Total addressable pages < 30 (manual content is more effective)
- You lack a data source and would be generating thin placeholder content
- Your domain authority is below DR 20 and competitors are DR 60+

---

## Initial Assessment

Before designing any pSEO strategy, answer these questions. Skip nothing.

### 1. Opportunity Validation

| Question | Why It Matters | Red Flag |
|----------|---------------|----------|
| What is the repeating keyword pattern? | Defines the template structure | Pattern is vague or inconsistent |
| What is the aggregate monthly search volume? | Determines ROI ceiling | < 5,000 aggregate monthly searches |
| How many unique pages can you generate? | Scope the project | < 50 pages (too few) or > 50K without data infrastructure |
| What does the SERP look like for sample queries? | Competitive feasibility | Page 1 dominated by DR 80+ editorial content |
| Is intent informational, navigational, or transactional? | Template design | Mixed intent across the same pattern |

### 2. Data Source Evaluation

Rate your data source on this scale:

| Tier | Source Type | Defensibility | Example |
|------|-----------|---------------|---------|
| S | Proprietary first-party | Unbeatable | Your product usage data, internal benchmarks |
| A | Product-derived | Strong | Aggregated user analytics, customer outcomes |
| B | User-generated | Moderate | Community reviews, submitted content |
| C | Licensed exclusive | Moderate | Paid data feed no competitor has |
| D | Public aggregated | Weak | Government data, public APIs |
| F | Scraped commodity | None | Wikipedia rewrites, copied listings |

**Rule: Do not build pSEO on Tier F data.** Google penalizes commodity rewrites. If your only data source is public and easily replicable, invest in acquiring Tier A-C data first.

### 3. Competitive Moat Assessment

For 5 sample queries in your pattern, analyze page 1 results:

- What is the average Domain Rating of ranking pages?
- Are existing results programmatic or editorial?
- What unique data do ranking pages provide?
- What is the content depth (word count, data richness, UX quality)?

**Go/No-Go threshold:** If the average DR gap between you and page 1 is > 30 AND existing results have proprietary data, the opportunity requires either a differentiated approach or domain authority building first.

---

## The 14 Playbooks

| # | Playbook | Pattern | Example | Data Requirement |
|---|----------|---------|---------|-----------------|
| 1 | Templates | "[Type] template" | "resume template", "invoice template" | Template files + metadata |
| 2 | Curation | "best [category]" | "best CRM for startups" | Product/service reviews + ratings |
| 3 | Conversions | "[X] to [Y]" | "100 USD to EUR" | Conversion logic/API |
| 4 | Comparisons | "[X] vs [Y]" | "Notion vs Confluence" | Feature data for both products |
| 5 | Examples | "[type] examples" | "landing page examples" | Curated example collection |
| 6 | Locations | "[service] in [city]" | "coworking in Austin" | Location-specific data |
| 7 | Personas | "[product] for [audience]" | "CRM for real estate" | Audience-specific use cases |
| 8 | Integrations | "[A] + [B] integration" | "Slack Asana integration" | Integration documentation |
| 9 | Glossary | "what is [term]" | "what is churn rate" | Domain expertise |
| 10 | Translations | Content in N languages | Localized guides | Translation + localization data |
| 11 | Directory | "[category] tools" | "AI writing tools" | Tool listings + evaluations |
| 12 | Profiles | "[entity name]" | "Stripe company profile" | Entity-level data |
| 13 | Statistics | "[topic] statistics" | "SaaS churn statistics 2026" | Verified statistical data |
| 14 | Calculators | "[topic] calculator" | "LTV calculator" | Calculation logic + inputs |

---

## Playbook Selection Matrix

| If you have... | Primary Playbook | Secondary Layer |
|----------------|-----------------|-----------------|
| A product with many integrations | Integrations | Comparisons |
| A design/creative tool | Templates + Examples | Personas |
| A multi-segment audience | Personas | Comparisons |
| Local/regional presence | Locations | Directory |
| A tool/utility product | Calculators + Conversions | Glossary |
| Deep domain expertise | Glossary + Statistics | Curation |
| A competitor landscape to exploit | Comparisons + Curation | Directory |
| User-generated content | Examples + Directory | Profiles |

**Layering rule:** Combine up to 2 playbooks per page set. Example: "Best coworking spaces in [city]" = Curation + Locations.

---

## Keyword Pattern Mining

### Step 1: Pattern Identification

Extract the repeating structure from seed keywords:

```
Seed: "react developer salary san francisco"
Pattern: [role] salary [city]
Variables: role (200+ options), city (500+ options)
Max pages: 200 x 500 = 100,000
```

### Step 2: Volume Distribution Analysis

Not all variable combinations have search volume. Map the distribution:

| Tier | Volume Range | Typical % of Total Pages | Strategy |
|------|-------------|-------------------------|----------|
| Head | 1,000+ monthly | 2-5% | Priority indexation, highest content quality |
| Torso | 100-999 monthly | 15-25% | Standard template, full deployment |
| Long-tail | 10-99 monthly | 40-50% | Template with conditional content blocks |
| Zero-volume | < 10 monthly | 20-40% | Noindex OR skip unless data is uniquely valuable |

### Step 3: Intent Classification

For each pattern, verify intent consistency:

| Intent Type | Template Implications | CTA Strategy |
|------------|----------------------|--------------|
| Informational | Data-heavy, educational content | Newsletter, related content |
| Commercial investigation | Comparison tables, pros/cons | Free trial, demo |
| Transactional | Pricing, availability, features | Buy now, sign up |
| Navigational | Brand-specific, direct answer | Product page link |

---

## Data Pipeline Architecture

### Pipeline Design

```
[Data Source] → [Extraction] → [Transformation] → [Enrichment] → [Validation] → [Template Population] → [Quality Check] → [Publish]
```

### Data Quality Gates

Every record must pass these gates before page generation:

| Gate | Check | Failure Action |
|------|-------|---------------|
| Completeness | All required fields populated | Skip page, log for manual review |
| Accuracy | Data matches source, no staleness > 90 days | Flag for refresh |
| Uniqueness | No duplicate records | Merge or deduplicate |
| Minimum richness | Page will have > 300 words of unique content | Skip or enrich |
| Legal compliance | Data usage rights verified | Block publication |

### Update Cadence

| Data Type | Recommended Update Frequency | Staleness Penalty |
|-----------|------------------------------|-------------------|
| Pricing data | Weekly | High (users notice immediately) |
| Company/product data | Monthly | Medium |
| Statistical data | Quarterly | Low if year-tagged |
| Glossary/educational | Semi-annually | Very low |
| Location data | Monthly | Medium (closures, address changes) |

---

## Template Design System

### Page Architecture

Every programmatic page must have these zones:

```
┌─────────────────────────────────────┐
│ Zone 1: Unique Header               │  H1 with target keyword, unique intro paragraph
├─────────────────────────────────────┤
│ Zone 2: Primary Data Section         │  The core data/content for this specific page
├─────────────────────────────────────┤
│ Zone 3: Contextual Analysis          │  Insights, comparisons, trends specific to this entity
├─────────────────────────────────────┤
│ Zone 4: Related Data                 │  Adjacent data points that add depth
├─────────────────────────────────────┤
│ Zone 5: Internal Navigation          │  Related pages, breadcrumbs, category links
├─────────────────────────────────────┤
│ Zone 6: CTA                         │  Conversion element matched to intent
└─────────────────────────────────────┘
```

### Uniqueness Requirements

Each page MUST have at least 3 of these 5 uniqueness sources:

1. **Unique data points** -- Numbers, facts, or attributes specific to this entity
2. **Conditional content blocks** -- Sections that appear/disappear based on data attributes
3. **Calculated insights** -- Derived metrics (percentages, comparisons, rankings)
4. **Contextual recommendations** -- "If X, then Y" advice blocks based on the data
5. **User-generated content** -- Reviews, comments, or community contributions

### URL Structure

**Always use subfolders.** Never subdomains for pSEO.

| Pattern | URL Template | Example |
|---------|-------------|---------|
| Location | `/[service]/[city]/` | `/coworking/austin/` |
| Comparison | `/compare/[a]-vs-[b]/` | `/compare/notion-vs-confluence/` |
| Integration | `/integrations/[partner]/` | `/integrations/slack/` |
| Glossary | `/glossary/[term]/` | `/glossary/churn-rate/` |
| Persona | `/[product]-for-[audience]/` | `/crm-for-real-estate/` |

---

## Quality Control Framework

### Pre-Publication QA Checklist

**Content Quality:**
- [ ] Each page has > 300 words of unique content (not counting shared template elements)
- [ ] H1 is unique and contains the target keyword
- [ ] Meta title is unique (< 60 chars) and meta description is unique (< 155 chars)
- [ ] No broken data references (empty fields rendered as "N/A" or blank)
- [ ] At least 2 conditional content blocks triggered per page
- [ ] No duplicate pages targeting the same keyword

**Technical SEO:**
- [ ] Canonical tag points to self
- [ ] Hreflang tags if multilingual
- [ ] Schema markup renders without errors
- [ ] Page loads in < 3 seconds
- [ ] Mobile responsive

**Internal Linking:**
- [ ] Breadcrumb trail is complete
- [ ] 3-5 related pages linked contextually
- [ ] Hub page links to this page
- [ ] No orphan pages in the set

### Thin Content Detection

Run this check against every generated page:

| Signal | Threshold | Action |
|--------|-----------|--------|
| Unique word count | < 200 unique words | Block publication |
| Content similarity to another page in set | > 80% Jaccard similarity | Merge or differentiate |
| Data fields populated | < 60% of template fields | Skip or enrich |
| User time-on-page (post-launch) | < 15 seconds average | Review and improve |
| Bounce rate (post-launch) | > 85% | Review intent match |

---

## Internal Linking Architecture

### Hub-and-Spoke Model

```
                    ┌─────────┐
                    │  HUB    │  /coworking/
                    │  PAGE   │  (ranks for "coworking spaces")
                    └────┬────┘
          ┌──────────────┼──────────────┐
     ┌────┴────┐    ┌────┴────┐    ┌────┴────┐
     │ SPOKE 1 │    │ SPOKE 2 │    │ SPOKE 3 │
     │ /austin/│    │ /denver/│    │ /seattle/│
     └────┬────┘    └────┬────┘    └────┬────┘
          │              │              │
     Cross-links between related spokes
```

**Linking rules:**
- Hub links DOWN to every spoke (or top 50 spokes if > 200 pages)
- Every spoke links UP to the hub
- Spokes link ACROSS to 3-5 related spokes (geographic proximity, thematic similarity)
- Deep pages link UP to their spoke AND the hub
- Cross-silo links only when contextually genuine

### Pagination for Large Sets

If a hub page has > 50 spokes, implement paginated sub-hubs:

```
/coworking/                     → Top cities + browse by state
/coworking/california/          → All California cities
/coworking/california/page/2/   → Paginated if > 25 cities
```

---

## Indexation Strategy

### Crawl Budget Management

| Page Set Size | Strategy |
|--------------|----------|
| < 500 pages | Single XML sitemap, submit all |
| 500-5,000 | Segmented sitemaps by category |
| 5,000-50,000 | Segmented sitemaps + priority scoring + IndexNow |
| 50,000+ | Programmatic sitemap generation + crawl budget monitoring + strategic noindex |

### Indexation Priority

| Priority | Pages | Action |
|----------|-------|--------|
| P0 | Hub pages | Submit immediately, internal link from homepage |
| P1 | Head-volume spokes (top 10%) | Submit in first sitemap batch |
| P2 | Torso-volume spokes | Submit in second batch, 1-2 weeks later |
| P3 | Long-tail spokes | Submit gradually over 4-6 weeks |
| P4 | Zero-volume pages | Noindex unless data is uniquely valuable |

### IndexNow Integration

For large-scale updates, use IndexNow to notify search engines immediately:

```
POST https://api.indexnow.org/indexnow
{
  "host": "yoursite.com",
  "key": "your-api-key",
  "urlList": ["https://yoursite.com/page1", "https://yoursite.com/page2"]
}
```

---

## Launch Sequence

### Phase 1: Pilot (Week 1-2)
- Deploy 20-50 pages from head-volume tier
- Submit sitemap with pilot pages only
- Monitor indexation rate daily
- Check for crawl errors in Search Console

### Phase 2: Scale (Week 3-6)
- Deploy remaining torso-volume pages in batches of 100-500
- Add cross-links between deployed pages
- Monitor thin content warnings
- Track impressions in Search Console

### Phase 3: Long-Tail (Week 7-12)
- Deploy long-tail pages
- Noindex zero-volume pages (keep them crawlable but not indexed)
- Begin link acquisition outreach for hub pages

### Phase 4: Optimization (Ongoing)
- A/B test template variations on head-volume pages
- Refresh stale data quarterly
- Add conditional content blocks based on engagement data
- Monitor for keyword cannibalization across the set

---

## Post-Launch Optimization

### Metrics Dashboard

| Metric | Frequency | Target |
|--------|-----------|--------|
| Indexation rate | Weekly | > 90% of submitted pages indexed within 60 days |
| Organic impressions | Weekly | Trending up month-over-month |
| Average position (by tier) | Bi-weekly | Head pages: top 10; Torso: top 30 |
| Click-through rate | Monthly | > 3% for head pages |
| Bounce rate | Monthly | < 70% |
| Conversion rate | Monthly | > 1% for transactional intent |
| Pages per session | Monthly | > 1.5 |

### Optimization Playbook

| Signal | Diagnosis | Action |
|--------|-----------|--------|
| Indexed but not ranking | Content quality or authority gap | Enrich content, build links to hub |
| Ranking but low CTR | Title/description not compelling | A/B test meta titles |
| Ranking but high bounce | Intent mismatch or thin content | Audit against search intent, add data |
| Deindexed after initial indexing | Thin content penalty | Improve uniqueness, reduce similarity |
| Crawled but not indexed | Quality threshold not met | Add more unique content per page |

---

## Anti-Patterns and Penalty Avoidance

| Anti-Pattern | Why It Fails | Prevention |
|-------------|-------------|------------|
| City-name swapping | Same content + different city = doorway page penalty | Each location page needs unique local data |
| Keyword stuffing in templates | Unnatural density triggers spam filters | Keep keyword density 1-2%, write naturally |
| Generating pages for zero-demand queries | Wastes crawl budget, signals low quality | Validate demand before generating |
| No internal links to pSEO pages | Orphan pages get deprioritized | Connect every page to the hub-spoke structure |
| Stale data never refreshed | Users lose trust, Google notices | Set update cadence per data type |
| All pages identical structure | Lack of variation signals automation to Google | Use 3-5 template variants |

---

## Decision Matrix: Build vs Skip

Score each dimension 1-5, then apply the threshold.

| Dimension | Weight | 1 (Skip) | 5 (Build) |
|-----------|--------|----------|-----------|
| Search demand | 30% | < 1K aggregate monthly | > 50K aggregate monthly |
| Data quality | 25% | Public/scraped, easily replicated | Proprietary, defensible |
| Competitive gap | 20% | DR gap > 40, strong incumbents | DR gap < 15, weak/no incumbents |
| Template feasibility | 15% | Each page needs unique editorial | Clean template fits all variations |
| Business alignment | 10% | No conversion path from these pages | Direct path to core product |

**Scoring guide:**
- 4.0+ weighted average: Build immediately
- 3.0-3.9: Build if resources allow, validate with pilot first
- 2.0-2.9: Invest in data quality or authority first
- < 2.0: Do not build

---

## Output Artifacts

| Artifact | Format | Description |
|----------|--------|-------------|
| Opportunity Analysis | Markdown table | Keyword patterns x volume x data source x difficulty x business alignment |
| Playbook Recommendation | Decision matrix | If/then mapping with rationale and real-world examples |
| Page Template Specification | Annotated wireframe (markdown) | URL pattern, zone structure, uniqueness sources, conditional logic |
| Data Pipeline Spec | Flow diagram (text) | Source > extraction > transformation > validation > publication |
| Quality Scorecard | Checklist + thresholds | Pre-publication QA gates with pass/fail criteria |
| Indexation Plan | Phased timeline | Priority tiers, sitemap structure, crawl budget allocation |
| Post-Launch Dashboard | Metric table | KPIs, targets, review cadence, optimization triggers |

---

## Related Skills

- **seo-audit** -- Run after pSEO pages are live to diagnose indexation issues, thin content warnings, or ranking problems across the page set.
- **schema-markup** -- Add structured data to pSEO templates (Product, FAQ, LocalBusiness) for rich snippet eligibility at scale.
- **site-architecture** -- Plan hub-and-spoke structure and crawl budget management for large pSEO deployments (500+ pages).
- **competitor-alternatives** -- Use the Comparisons playbook when building "[X] vs [Y]" pages; competitor-alternatives has dedicated comparison page frameworks.
- **content-creator** -- Use when individual pages in the set need editorial-quality unique content beyond template generation.

---

## Troubleshooting

| Problem | Likely Cause | Fix |
|---------|-------------|-----|
| Google deindexed 90%+ of pSEO pages | Thin content — pages have insufficient unique content (<300 words) or >80% similarity | Increase unique content per page to 500+ words; ensure 30-40% differentiation between pages |
| Pages indexed but getting zero traffic | Pages target zero-volume keywords or content does not match search intent | Validate demand before generating; noindex zero-volume pages; verify intent alignment |
| "Doorway pages" manual action in GSC | Template pages with only variable substitution (city name swap) and no unique value | Add genuinely unique data per page — local stats, specific recommendations, conditional content blocks |
| Hub page ranks but spokes do not | Spokes missing inbound internal links or hub not linking down to spokes | Verify bidirectional hub-spoke linking; add contextual cross-links between related spokes |
| Crawl budget exhausted before all pages indexed | Too many pages submitted at once or low-value pages consuming crawl resources | Phase deployment in batches of 100-500; use tiered indexation with strategic noindex |
| Content similarity too high across page set | Template lacks conditional content blocks; only variable substitution used | Add 3-5 conditional content sections per template that change based on data attributes |
| AI content detection flagging pSEO pages | Over-reliance on AI generation without human editorial review | Use AI for data enrichment only, not full content generation; sample 5-10% for quality review |

---

## Success Criteria

- **Indexation rate**: 90%+ of submitted pages indexed within 60 days of deployment
- **Content uniqueness**: Every page has 500+ unique words with <40% similarity to any other page in the set (2026 Google threshold)
- **Head keyword rankings**: Top 10% of pages (by volume) ranking in top 30 within 90 days
- **Organic traffic growth**: Page set generating measurable organic traffic within 60 days of full deployment
- **Thin content rate**: Zero pages flagged as thin content in Google Search Console
- **Bounce rate**: Below 70% average across the page set (indicating intent match)
- **Conversion rate**: 1%+ for transactional intent pages, measurable lead capture for informational pages

---

## Scope & Limitations

**In scope:**
- Keyword pattern mining and volume distribution analysis
- Data pipeline design (source > extraction > transformation > validation > publication)
- Template architecture with uniqueness requirements
- Quality control frameworks including thin content detection
- Hub-and-spoke internal linking for pSEO page sets
- Phased indexation strategy and crawl budget management
- Post-launch optimization and monitoring dashboards

**Out of scope:**
- Individual editorial content creation (use Content Production)
- Data collection or web scraping implementation
- CMS or static site generator setup and configuration
- Server infrastructure for large-scale deployments
- Paid acquisition for pSEO pages
- Legal compliance for data usage rights

**Known limitations:**
- Google's 2026 helpful content system can deindex large page sets retroactively if quality drops below threshold
- Programmatic SEO at Tier F data (public/scraped) carries high penalty risk regardless of template quality
- Engagement metrics (bounce rate, time on page) now influence indexation decisions for pSEO pages
- AI content detection is improving — fully automated content generation without human oversight is increasingly risky
- Travel site case study: 50,000 city-swap pages had 98% deindexed within 3 months (per 2025 industry data)

---

## Scripts

```bash
# Analyze keyword patterns for pSEO opportunities
python scripts/keyword_pattern_miner.py --keywords keywords.csv --json

# Score page templates for content quality and uniqueness
python scripts/template_scorer.py --template template.html --data sample_data.json

# Validate data quality for pSEO data pipeline
python scripts/data_validator.py --file data.csv --rules rules.json --json
```
