---
name: site-architecture
description: Information architecture, URL hierarchy, internal linking strategy, navigation design, and silo structure for websites. Covers architectural audits, new site planning, crawl equity optimization, and topic cluster mapping.
version: 1.0.0
author: borghei
category: marketing-growth
tags: [seo, information-architecture, internal-linking, url-structure, navigation, siloing]
triggers:
  - user mentions site architecture or information architecture
  - user asks about URL structure, internal linking, or navigation design
  - user mentions breadcrumbs, topic clusters, hub pages, or silo structure
  - user has orphan pages or crawl depth issues
  - user is planning a site restructure or URL reorganization
  - seo-audit reveals structural problems as the root cause
---

# Site Architecture & Internal Linking

Production-grade website architecture framework covering URL hierarchy design, internal linking strategy, navigation optimization, silo structure, and crawl equity management. Handles architecture audits, new site planning, and restructuring existing sites.

---

## Table of Contents

- [Operating Modes](#operating-modes)
- [URL Structure Design](#url-structure-design)
- [Navigation Architecture](#navigation-architecture)
- [Silo Structure and Topic Clusters](#silo-structure-and-topic-clusters)
- [Internal Linking Strategy](#internal-linking-strategy)
- [Crawl Equity Management](#crawl-equity-management)
- [Architecture Audit Framework](#architecture-audit-framework)
- [Restructuring Playbook](#restructuring-playbook)
- [Architecture Patterns by Site Type](#architecture-patterns-by-site-type)
- [Common Mistakes](#common-mistakes)
- [Output Artifacts](#output-artifacts)
- [Related Skills](#related-skills)

---

## Operating Modes

### Mode 1: Audit Current Architecture
Existing site needs structural assessment. Analyze depth distribution, orphan pages, link equity flow, and navigation effectiveness.

### Mode 2: Plan New Architecture
Building from scratch or full redesign. Map business goals to site sections, design URL hierarchy, plan navigation, and define content silos.

### Mode 3: Internal Linking Optimization
Structure is fine but link equity flow needs improvement. Identify hub pages, map spoke content, fix orphans, and optimize anchor text.

### Mode 4: URL Restructuring
Changing URLs on an existing site. Plan the new structure, build redirect maps, and manage the migration.

---

## URL Structure Design

### Depth Guidelines

| Depth | Example | Use When | SEO Impact |
|-------|---------|----------|------------|
| 1 level (flat) | `/cold-email-tips` | Blog posts, standalone pages | Best crawl equity per page |
| 2 levels | `/email-marketing/cold-email-tips` | Category is a rankable page itself | Good, category page accumulates authority |
| 3 levels | `/solutions/marketing/email-automation` | Product families, nested services | Acceptable if each level has content |
| 4+ levels | `/a/b/c/d/page` | Never | Diluted equity, poor UX, crawl issues |

**Decision rule:** If the intermediate directory URL (`/email-marketing/`) will NOT be a real page with its own content and ranking target, do not create the directory. Flat is better than empty hierarchy.

### URL Construction Rules

| Rule | Good | Bad | Why |
|------|------|-----|-----|
| Use hyphens | `/seo-audit` | `/seo_audit` | Underscores are not word separators for Google |
| Be descriptive | `/pricing` | `/pricing-page` | Redundant suffixes add nothing |
| Keep short | `/guides/technical-seo` | `/guides/technical-seo-audit-checklist-complete-guide` | Readability matters |
| Include keyword | `/guides/seo-audit` | `/guides/article?id=4827` | Descriptive URLs rank better |
| Be consistent with trailing slashes | Pick one: `/about` or `/about/` | Mix of both | Inconsistency creates duplicate content |
| Use lowercase | `/about-us` | `/About-Us` | Case sensitivity varies by server |

### URL Patterns by Site Type

| Site Type | Pattern | Example |
|-----------|---------|---------|
| SaaS | `/features/[feature]`, `/solutions/[use-case]`, `/integrations/[partner]` | `/features/analytics`, `/solutions/marketing`, `/integrations/slack` |
| E-commerce | `/[category]/[subcategory]/[product]` | `/mens/shoes/running-shoes-pro` |
| Blog/Content | `/blog/[slug]` or `/blog/[category]/[slug]` | `/blog/seo-audit-guide` |
| Local business | `/[service]/[location]` | `/plumbing/austin-tx` |
| Documentation | `/docs/[section]/[page]` | `/docs/api/authentication` |
| Marketplace | `/[category]/[listing]` | `/designers/john-smith` |

---

## Navigation Architecture

### Navigation Zones

Every site has 6 navigation zones. Each serves a different purpose and carries different SEO weight.

| Zone | Items | SEO Weight | Design Rule |
|------|-------|------------|-------------|
| Primary nav | 5-8 items max | High (sitewide equity) | Only pages you want to rank for. Never "Resources" without a landing page. |
| Secondary nav | 3-7 per section | Medium | Sub-navigation within a section/silo |
| Breadcrumbs | Dynamic | High (upward equity) | Every non-homepage page. Each segment must be a real link. |
| Footer nav | 8-15 items max | Low-Medium | Key pages only. Not a dumping ground for every page. |
| Contextual (in-content) | 3-5 per page | Highest | Most powerful signal. Natural editorial links within body content. |
| Sidebar | 5-10 items | Low-Medium | Related content, category listing |

### Primary Navigation Design

**Rules:**
- 5-8 items maximum. Cognitive overload starts at 9+ items.
- Every nav item links to a page you actively want to rank.
- Dropdown menus are fine, but the parent item must be a clickable, crawlable link (not just a hover trigger).
- Do not put utility pages (Contact, Privacy, Terms) in primary nav -- they belong in the footer.
- Mobile nav must expose the same structure as desktop nav (no hidden critical pages).

### Breadcrumb Implementation

Add breadcrumbs to every non-homepage page. They serve three functions:

1. **UX**: Show users their location in the hierarchy
2. **SEO**: Create sitewide upward internal links to hub/category pages
3. **Rich results**: Enable BreadcrumbList schema for SERP breadcrumbs

**Format:** `Home > Category > Subcategory > Current Page`

**Rules:**
- Every breadcrumb segment must be a real, crawlable link
- Never use breadcrumbs as styled text without links
- Add BreadcrumbList schema markup alongside visible breadcrumbs
- Breadcrumb hierarchy should match URL hierarchy

---

## Silo Structure and Topic Clusters

### Hub-and-Spoke Model

A silo is a self-contained cluster of content about one topic, where all pages link to each other and to a central hub page.

```
                    ┌──────────────────┐
                    │     HUB PAGE     │
                    │   /seo/          │
                    │   (Pillar content)│
                    └────────┬─────────┘
            ┌────────────────┼────────────────┐
       ┌────┴────┐      ┌───┴────┐      ┌────┴────┐
       │ SPOKE 1 │      │ SPOKE 2│      │ SPOKE 3 │
       │technical│      │on-page │      │  link   │
       │  seo    │      │  seo   │      │building │
       └────┬────┘      └───┬────┘      └────┬────┘
            │                │                │
       Cross-links     Cross-links      Cross-links
       between         between          between
       related         related          related
       spokes          spokes           spokes
```

### Building Topic Clusters

**Step 1:** Identify 3-7 core topics for your site (these become your silos)

**Step 2:** For each topic, create one pillar page (the hub) that covers the topic broadly

**Step 3:** Create spoke content for each major sub-question or sub-topic

**Step 4:** Implement linking:
- Hub links DOWN to every spoke
- Every spoke links UP to the hub (with keyword-rich anchor text)
- Spokes link ACROSS to related spokes within the same silo
- Cross-silo links are fine when contextually genuine

**Step 5:** Build the content before building the links. Links to non-existent content are useless.

### Silo Depth Guidelines

| Silo Size | Recommended Depth | Structure |
|-----------|------------------|-----------|
| 3-5 spokes | Flat | Hub + spokes, all at same level |
| 6-15 spokes | Shallow nested | Hub > Sub-hubs > Spokes |
| 16-50 spokes | Two-level | Hub > Category sub-hubs > Individual spokes |
| 50+ spokes | Paginated | Hub > Category sub-hubs > Paginated spoke listings |

---

## Internal Linking Strategy

### Link Equity Power Stack

Not all internal links carry equal weight. From most to least powerful:

| Rank | Link Type | Weight | When to Use |
|------|-----------|--------|-------------|
| 1 | In-content contextual link | Highest | Natural editorial links within body copy |
| 2 | Hub page link | High | Pillar page linking to all its spokes |
| 3 | Navigation link | Medium | Sitewide, consistent, but diluted by ubiquity |
| 4 | Breadcrumb link | Medium | Upward equity flow, consistent |
| 5 | Footer link | Low | Sitewide, Google discounts these |
| 6 | Sidebar link | Low | Often not in main content flow |

### Anchor Text Strategy

| Type | Example | Usage | Signal Strength |
|------|---------|-------|-----------------|
| Partial match | "effective cold email strategies" | Primary approach (60-70% of links) | Strong |
| Exact match | "cold email templates" | Use sparingly (10-15% of links) | Strong but risky if overused |
| Branded | "our email guide" | Natural variation (10-15%) | Moderate |
| Descriptive | "this comprehensive guide" | Natural variation (5-10%) | Weak but natural |
| Generic | "click here", "learn more" | Avoid (< 5%) | None -- wasted signal |
| Naked URL | `https://example.com/guide` | Never for internal links | None |

### Orphan Page Detection and Resolution

An orphan page is indexed in Google but has zero inbound internal links. It is invisible to the site's link graph.

**Detection method:**
1. Export all indexed URLs (GSC Coverage or site: query)
2. Export all internal link targets (crawl tool or link extraction)
3. Pages in set A but not set B are orphans

**Resolution actions:**

| Orphan Type | Action |
|-------------|--------|
| Valuable content, belongs in a silo | Add contextual links from 3+ related pages |
| Old content, still relevant | Link from hub page and 1-2 spokes |
| Outdated content, no value | Redirect to relevant page or noindex |
| Utility page (shouldn't be indexed) | Add noindex |

### Internal Linking Audit Checklist

| Check | Pass Criteria |
|-------|---------------|
| Every content page has 3-5 outbound internal links | No page links only to itself or navigation |
| Every target page has 3+ inbound internal links | No orphans in the indexed set |
| Hub pages link to all their spokes | Complete coverage |
| Anchor text is descriptive and varied | No > 30% exact match for any keyword |
| No broken internal links | 0 broken links |
| Link depth from homepage < 4 clicks | 95%+ of pages within 3 clicks |

---

## Crawl Equity Management

### Homepage Equity Distribution

The homepage is your highest-equity page. Use it wisely.

| Homepage Link Target | Priority |
|---------------------|----------|
| Hub/pillar pages (top of each silo) | Highest -- link from homepage content area |
| Key product/service pages | High -- link from homepage or primary nav |
| Top-performing content | Medium -- link if contextually relevant |
| Utility pages (contact, about) | Low -- footer links only |
| Blog index | Medium -- primary or secondary nav |

### Crawl Budget Allocation

| Page Category | % of Crawl Budget | Optimization |
|--------------|-------------------|--------------|
| Money pages (product, pricing, features) | 20-30% | Internal link from homepage + nav |
| Pillar content (hub pages) | 20-30% | Extensive internal linking |
| Spoke content (blog, guides) | 30-40% | Linked from hubs + contextual |
| Utility pages (about, contact, legal) | 5-10% | Footer links only, minimal crawl |
| Tag/archive/pagination | < 5% | Noindex if thin, limit crawling |

---

## Architecture Audit Framework

### Audit Scorecard

| Dimension | Weight | Check |
|-----------|--------|-------|
| Crawl depth | 20% | 95%+ pages within 3 clicks of homepage |
| Orphan pages | 20% | 0 orphan pages in indexed set |
| URL cleanliness | 15% | Clean, descriptive, consistent URLs |
| Navigation completeness | 15% | All key pages accessible via primary/secondary nav |
| Internal link coverage | 15% | Every page has 3+ inbound internal links |
| Silo coherence | 10% | Topic clusters are well-defined with clear hub-spoke relationships |
| Breadcrumb implementation | 5% | Present on all non-homepage pages with schema |

### Red Flag Indicators

| Signal | Severity | Action |
|--------|----------|--------|
| Pages > 3 clicks from homepage | High | Create shortcuts via nav or hub page links |
| Hub page has no content (just links) | High | Add pillar content to all hub pages |
| Generic anchor text dominant (> 30%) | Medium | Rewrite anchor text to be descriptive |
| No breadcrumbs on deep pages | Medium | Implement breadcrumbs with BreadcrumbList schema |
| Sitemap includes noindex pages | Medium | Filter sitemap to only indexable pages |
| Primary nav links to utility pages | Low | Move Contact/Privacy to footer |
| Footer contains 50+ links | Low | Reduce to 8-15 key pages |

---

## Restructuring Playbook

### When to Restructure

| Signal | Restructure? | Alternative |
|--------|-------------|-------------|
| Complete URL overhaul needed | Yes | -- |
| Adding 3 new sections | Partial -- new sections only | -- |
| Fixing orphan pages | No | Add internal links, no URL changes needed |
| Improving nav | No | Update navigation, keep URLs |
| Moving to new CMS | Yes (usually) | Keep URL structure if CMS supports it |

### Restructuring Steps

1. **Crawl current site** -- Export all URLs, internal links, and rankings
2. **Map current to new** -- Create 1:1 URL redirect mapping
3. **Build redirect rules** -- 301 redirects for every changed URL
4. **Chain existing redirects** -- Update old redirects to point to final destination
5. **Update internal links** -- Point to new URLs (do not rely on redirects for internal links)
6. **Update sitemap** -- Reflect new URL structure
7. **Monitor for 60 days** -- Watch for crawl errors, ranking changes, traffic impact

---

## Architecture Patterns by Site Type

### SaaS Website

```
/                           Homepage
├── /features/              Features hub
│   ├── /features/analytics Analytics feature
│   └── /features/reporting Reporting feature
├── /solutions/             Solutions hub (by use case)
│   ├── /solutions/marketing Marketing use case
│   └── /solutions/sales    Sales use case
├── /integrations/          Integrations hub
│   ├── /integrations/slack Slack integration
│   └── /integrations/salesforce Salesforce integration
├── /pricing                Pricing page
├── /blog/                  Blog index
│   ├── /blog/seo-guide     Blog post
│   └── /blog/growth-tips   Blog post
├── /docs/                  Documentation
└── /about                  About page
```

### E-commerce Site

```
/                           Homepage
├── /[category]/            Category page (with content)
│   ├── /[category]/[subcategory]/ Subcategory (with content)
│   │   └── /[category]/[subcategory]/[product] Product page
│   └── /[category]/[product]      Product (if no subcategory)
├── /brands/                Brand hub
│   └── /brands/[brand]     Brand page
├── /blog/                  Content hub
└── /sale/                  Promotions hub
```

### Content/Media Site

```
/                           Homepage
├── /[topic]/               Topic hub (pillar content)
│   ├── /[topic]/[subtopic] Subtopic article
│   └── /[topic]/[guide]    In-depth guide
├── /authors/               Author hub
│   └── /authors/[name]     Author page
├── /tools/                 Free tools hub
│   └── /tools/[tool]       Individual tool
└── /newsletter             Newsletter signup
```

---

## Common Mistakes

| Mistake | Why It Hurts | Fix |
|---------|-------------|-----|
| Orphan pages | No equity flows in, Google deprioritizes | Add contextual internal links from related content |
| URL changes without redirects | Lost link equity and broken backlinks | Always 301 redirect old URLs |
| Deep nesting (4+ levels) | Diluted crawl equity, confusing UX | Flatten structure |
| Empty category pages | Thin pages do not rank | Add pillar content to all category/hub pages |
| Homepage linking to nothing | Wastes highest-equity page | Link from home to all hub pages |
| Footer with 100+ links | Dilutes equity across too many targets | Limit footer to 8-15 key pages |
| Navigation not matching user mental model | Users leave, engagement drops | Run card-sort testing with real users |
| Dynamic parameter URLs | Creates duplicate content | Canonicalize or block with robots.txt |
| Sitewide sidebar links to every post | Diluted equity, adds noise | Remove or limit to "popular" posts |

---

## Output Artifacts

| Artifact | Format | Description |
|----------|--------|-------------|
| Architecture Audit Scorecard | Weighted score table | Per-dimension scores with red flag indicators |
| Site Tree Diagram | Text-based hierarchy | Visual URL structure with annotations |
| URL Specification Table | Table | URL pattern, title template, parent page, schema type per section |
| Internal Linking Plan | Hub-spoke map | Topic cluster map with anchor text guidelines and orphan fix list |
| Redirect Map | Before/after URL table | 1:1 mapping for URL restructuring with 301 implementation |
| Navigation Spec | Zone-by-zone design | Primary, secondary, breadcrumb, footer, and contextual nav plans |

---

## Related Skills

- **seo-audit** -- For comprehensive SEO audits where architecture is one of several problem areas. Use seo-audit for the full picture, site-architecture for deep structural work.
- **schema-markup** -- For adding BreadcrumbList and other structured data after architecture decisions are finalized.
- **programmatic-seo** -- For hub-and-spoke structures at scale when generating hundreds of template-based pages.
- **content-creator** -- For creating the pillar content that hub pages need to rank effectively.

---

## Troubleshooting

| Problem | Likely Cause | Fix |
|---------|-------------|-----|
| Orphan pages appearing in Google index | Pages exist in sitemap or have external links but no internal links pointing to them | Add contextual internal links from 3+ related pages; update hub pages to include them |
| Crawl depth exceeds 4+ clicks for key pages | Flat navigation missing or hub pages not linking to spokes | Create shortcut links via primary nav, hub page content blocks, or featured sections |
| Category/hub pages ranking poorly | Hub pages have no substantive content — just link lists | Add 800+ words of pillar content to every hub page; they must rank on their own merit |
| Redirect chains after site migration | Old redirects not updated to point to final destination; chains accumulate over multiple migrations | Audit all existing redirects; collapse chains so every redirect points directly to the final URL |
| Internal links using generic anchor text | "Click here" and "learn more" anchor text dominating internal links | Rewrite anchors to be descriptive with partial-match keywords; aim for 60-70% partial match |
| New sections not getting crawled | No internal links from existing high-authority pages to new section | Add contextual links from homepage and related hub pages; submit new section sitemap |

---

## Success Criteria

- **Crawl depth**: 95%+ of indexable pages reachable within 3 clicks from homepage
- **Zero orphan pages**: No indexed pages without at least 3 inbound internal links
- **URL cleanliness**: 100% of URLs follow the established pattern — lowercase, hyphenated, descriptive, consistent trailing slash policy
- **Navigation coverage**: All key revenue and pillar pages accessible via primary or secondary navigation
- **Internal link density**: Every content page has 3-5 outbound contextual internal links with descriptive anchor text
- **Silo coherence**: Each topic cluster has a defined hub page with bidirectional links to all spokes
- **Breadcrumb coverage**: BreadcrumbList schema present on 100% of non-homepage pages

---

## Scope & Limitations

**In scope:**
- URL hierarchy design and restructuring
- Navigation architecture (primary, secondary, breadcrumb, footer, contextual, sidebar)
- Silo structure and topic cluster planning
- Internal linking strategy and optimization
- Crawl equity analysis and optimization
- Architecture audits with scored reports
- URL migration planning with redirect mapping

**Out of scope:**
- Content creation for hub pages (use Content Production)
- Schema markup implementation (use Schema Markup)
- Technical SEO beyond architecture (use SEO Audit)
- Visual design or UX design of navigation
- CMS development or template coding
- External link building

**Known limitations:**
- Crawl equity distribution is estimated — Google does not publish exact PageRank flow data
- Architecture changes on large sites (10K+ pages) require careful phased migration to avoid traffic loss
- Navigation testing (card sorts, tree tests) requires user research tools and participants
- Cross-silo linking recommendations are qualitative — no deterministic formula exists for optimal cross-linking density

---

## Scripts

```bash
# Analyze sitemap for depth and structure issues
python scripts/sitemap_analyzer.py --file sitemap.xml --json

# Check URLs for redirect chains and patterns
python scripts/redirect_checker.py --file urls.txt --json

# Map internal link structure from a sitemap
python scripts/link_mapper.py --sitemap sitemap.xml --json
```
