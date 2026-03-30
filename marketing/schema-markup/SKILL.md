---
name: schema-markup
description: >
  Structured data implementation, validation, and optimization. Covers JSON-LD
  patterns for 20+ schema types, rich snippet eligibility, AI search visibility,
  Knowledge Graph optimization, and CMS-specific deployment guides.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: marketing-growth
  updated: 2026-03-31
  tags: [seo, schema, structured-data, json-ld, rich-snippets, knowledge-graph]
---
# Schema Markup Implementation

Production-grade structured data implementation covering 20+ schema types, rich result eligibility rules, AI search optimization, and CMS-specific deployment patterns. Handles auditing existing markup, implementing new schema, and fixing validation errors.

---

## Table of Contents

- [Operating Modes](#operating-modes)
- [Schema Type Selection Matrix](#schema-type-selection-matrix)
- [Implementation Patterns](#implementation-patterns)
- [Rich Result Eligibility Rules](#rich-result-eligibility-rules)
- [AI Search Optimization](#ai-search-optimization)
- [Knowledge Graph Strategy](#knowledge-graph-strategy)
- [CMS Deployment Guide](#cms-deployment-guide)
- [Validation and Testing](#validation-and-testing)
- [Common Errors and Fixes](#common-errors-and-fixes)
- [Audit Framework](#audit-framework)
- [Output Artifacts](#output-artifacts)
- [Related Skills](#related-skills)

---

## Operating Modes

### Mode 1: Audit Existing Markup
1. Extract all JSON-LD blocks from the page source
2. Validate required vs recommended fields per schema type
3. Cross-reference with Google's current rich result requirements
4. Score completeness 0-100 per schema block
5. Deliver prioritized fix list with corrected JSON-LD

### Mode 2: Implement New Schema
1. Identify page type and matching schema types
2. Select primary + supporting schema combination
3. Generate complete, copy-paste-ready JSON-LD populated with page content
4. Advise on placement method (inline head, CMS plugin, server-side rendering)
5. Test before deployment

### Mode 3: Fix Validation Errors
1. Map Google Search Console errors to specific fields
2. Identify root cause (missing field, wrong format, content mismatch)
3. Deliver corrected JSON-LD with change log
4. Explain the fix to prevent recurrence

---

## Schema Type Selection Matrix

### Primary Schema by Page Type

| Page Type | Primary Schema | Supporting Schema | Rich Result Type |
|-----------|---------------|-------------------|-----------------|
| Homepage | Organization | WebSite + SearchAction | Sitelinks search box |
| Blog post | Article | BreadcrumbList, Person (author), ImageObject | Article card |
| How-to guide | HowTo | Article, BreadcrumbList, ImageObject | How-to steps |
| FAQ page | FAQPage | BreadcrumbList | FAQ dropdowns |
| Product page | Product | Offer, AggregateRating, Review, BreadcrumbList | Product card |
| Local business | LocalBusiness | OpeningHoursSpecification, GeoCoordinates, PostalAddress | Local pack |
| Video page | VideoObject | Article (if embedded) | Video card |
| Category page | CollectionPage | BreadcrumbList, ItemList | -- |
| Event page | Event | Organization, Place, Offer | Event listing |
| Recipe | Recipe | NutritionInformation, AggregateRating | Recipe card |
| Course | Course | Organization, Offer | Course listing |
| Software/App | SoftwareApplication | Offer, AggregateRating | Software card |
| Job posting | JobPosting | Organization, Place | Job listing |
| Review page | Review | Product or LocalBusiness, Rating | Review snippet |
| Podcast episode | PodcastEpisode | PodcastSeries, Person | Podcast card |
| Author page | Person | sameAs links | Knowledge Panel |
| Company page | Organization | sameAs links, ContactPoint | Knowledge Panel |
| Breadcrumb trail | BreadcrumbList | -- | Breadcrumb rich result |
| Site navigation | SiteNavigationElement | -- | -- |
| Dataset | Dataset | DataCatalog | Dataset search |

### Stacking Rules

**Always add:**
- BreadcrumbList to any non-homepage if breadcrumbs exist on the page
- Organization to the homepage (site-wide identity)

**Common valid stacks:**
- Article + BreadcrumbList + Person + ImageObject (blog posts)
- Product + Offer + AggregateRating + BreadcrumbList (product pages)
- LocalBusiness + OpeningHoursSpecification + GeoCoordinates + Review (local pages)
- HowTo + Article + BreadcrumbList + ImageObject (guides)

**Never combine:**
- Product on a page that does not sell a product (Google penalizes misuse)
- Multiple Organization blocks for the same entity (combine into one)
- FAQPage on pages where the Q&A is not visible to users

---

## Implementation Patterns

### JSON-LD Format (Always Use This)

JSON-LD is the only format worth implementing. Google recommends it, it lives in the `<head>`, and it does not touch your HTML markup. Microdata and RDFa are legacy -- do not use them for new implementations.

### Placement

```html
<head>
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "Your Article Title",
    "author": {
      "@type": "Person",
      "name": "Author Name",
      "url": "https://example.com/authors/name",
      "sameAs": ["https://linkedin.com/in/name", "https://twitter.com/name"]
    },
    "datePublished": "2026-01-15",
    "dateModified": "2026-03-01",
    "image": "https://example.com/images/article-hero.jpg",
    "publisher": {
      "@type": "Organization",
      "name": "Company Name",
      "logo": {
        "@type": "ImageObject",
        "url": "https://example.com/logo.png"
      }
    }
  }
  </script>
</head>
```

Multiple `<script type="application/ld+json">` blocks per page are valid. Use separate blocks for unrelated schema types. Nest related types within one block.

### Scope Rules

| Scope | Schema | Placement |
|-------|--------|-----------|
| Site-wide | Organization, WebSite + SearchAction | Homepage template header |
| Per-page | Article, Product, HowTo, FAQPage | Page-specific head injection |
| Per-element | BreadcrumbList | Every non-homepage |
| Conditional | Event, JobPosting | Only on pages with that content type |

---

## Rich Result Eligibility Rules

Google does not give rich results for all valid schema. These are the current requirements (as of 2026):

### Article Rich Result

| Field | Required | Notes |
|-------|----------|-------|
| headline | Yes | Must match visible page title |
| image | Yes | Must be crawlable, min 1200px wide |
| datePublished | Yes | ISO 8601 format |
| dateModified | Recommended | Must be >= datePublished |
| author.name | Yes | Must match a real person or organization |
| author.url | Recommended | Links to author page |
| publisher.name | Yes | |
| publisher.logo | Yes | Max 600x60px |

### Product Rich Result

| Field | Required | Notes |
|-------|----------|-------|
| name | Yes | Product name |
| image | Yes | Product photo |
| offers.price | Yes | Numeric value |
| offers.priceCurrency | Yes | ISO 4217 code |
| offers.availability | Recommended | Use schema.org/InStock etc. |
| aggregateRating.ratingValue | Recommended | Numeric |
| aggregateRating.reviewCount | Recommended | Integer |
| review | Recommended | At least 1 review |

### FAQPage Rich Result

| Field | Required | Notes |
|-------|----------|-------|
| mainEntity | Yes | Array of Question items |
| Question.name | Yes | The question text |
| Question.acceptedAnswer.text | Yes | The answer text |
| Visible on page | Yes | Q&A must be visible to users, not hidden |

### HowTo Rich Result

| Field | Required | Notes |
|-------|----------|-------|
| name | Yes | Title of the how-to |
| step | Yes | Array of HowToStep items |
| step.name | Yes | Step title |
| step.text | Yes | Step description |
| image | Recommended | Per-step or overall |
| totalTime | Recommended | ISO 8601 duration |

---

## AI Search Optimization

AI search systems (Google AI Overviews, Perplexity, ChatGPT Search, Bing Copilot) use structured data for content understanding, citation decisions, and entity recognition.

### Why Schema Matters for AI Search

1. **Content type classification** -- AI systems use `@type` to determine if content is a how-to, product listing, FAQ, or opinion piece
2. **Citation eligibility** -- FAQPage and HowTo schema increase citation likelihood because AI systems can extract structured Q&A and step-by-step content directly
3. **Freshness signals** -- `datePublished` and `dateModified` help AI systems filter by recency
4. **Authority signals** -- `author` with `sameAs` links to known profiles boosts entity recognition
5. **Entity connection** -- `Organization` with `sameAs` links to Wikidata, LinkedIn, and social profiles strengthens entity resolution

### AI Search Schema Playbook

| Action | Priority | Impact |
|--------|----------|--------|
| Add FAQPage schema to any page with Q&A content (even 3 questions) | High | Direct citation in AI answers |
| Add author Person schema with sameAs to LinkedIn, Twitter, Google Scholar | High | Author entity recognition |
| Add Organization with sameAs to Wikidata, LinkedIn, Crunchbase | High | Brand entity recognition |
| Keep dateModified accurate on every content update | Medium | Freshness filtering |
| Add HowTo schema to process/tutorial content | Medium | Step-by-step citation |
| Add SoftwareApplication schema to tool/product pages | Medium | Product recognition in AI answers |

---

## Knowledge Graph Strategy

Getting into Google's Knowledge Graph means your entity (person, company, product) is recognized and displayed in panels, AI answers, and cross-referenced searches.

### Knowledge Graph Entry Requirements

1. **Wikidata entry** -- Create or claim your entity on Wikidata.org
2. **Wikipedia presence** -- A Wikipedia article dramatically increases KG entry probability
3. **Consistent NAP** -- Name, Address, Phone must be identical across all citations
4. **sameAs network** -- Organization schema must link to all official profiles

### sameAs Best Practices

```json
{
  "@type": "Organization",
  "name": "Your Company",
  "url": "https://yourcompany.com",
  "sameAs": [
    "https://www.wikidata.org/wiki/Q12345678",
    "https://en.wikipedia.org/wiki/Your_Company",
    "https://www.linkedin.com/company/yourcompany",
    "https://twitter.com/yourcompany",
    "https://www.crunchbase.com/organization/yourcompany",
    "https://github.com/yourcompany"
  ]
}
```

**Order of importance for sameAs links:**
1. Wikidata (strongest entity signal)
2. Wikipedia
3. LinkedIn
4. Official social profiles
5. Industry directories (Crunchbase, G2, Capterra)

---

## CMS Deployment Guide

### WordPress
- **Yoast SEO / Rank Math**: Auto-generate Article, Organization, BreadcrumbList. Add custom schema via their blocks for HowTo and FAQPage.
- **Custom schema**: Add via `wp_head` action hook or a custom plugin.
- **Avoid**: Plugins that inject schema via JavaScript (Google may not render it).

### Webflow
- **Per-page**: Add custom code in page settings > Custom Code > Head
- **CMS-driven**: Use Webflow CMS to generate dynamic JSON-LD via embedded code blocks with CMS field references
- **Site-wide**: Add Organization schema in Project Settings > Custom Code > Head

### Shopify
- **Product schema**: Auto-generated by most themes. Verify it includes Offer and AggregateRating.
- **Article/Blog schema**: Usually missing -- add manually via theme.liquid or a schema app.
- **Organization**: Add to theme.liquid `<head>` section.

### Next.js / Custom React
- **Server-side rendering**: Generate JSON-LD in the page component and render in `<Head>`.
- **next-seo library**: Provides schema components for common types.
- **Dynamic pages**: Generate schema from your data layer, not hardcoded.

### Static sites (Hugo, Jekyll, Gatsby)
- **Template-level**: Add JSON-LD to layout templates using template variables.
- **Per-page**: Use frontmatter data to populate schema fields dynamically.

### Google Tag Manager (GTM)
- **Warning**: GTM-injected schema is often NOT indexed by Google because it renders client-side after JavaScript execution.
- **Use only when**: No other option exists (no CMS access, no dev resources).
- **Better alternative**: Server-side injection via CMS or template engine.

---

## Validation and Testing

### Three-Layer Validation

Test every schema implementation with all three tools before deployment:

| Tool | URL | What It Checks |
|------|-----|----------------|
| Google Rich Results Test | search.google.com/test/rich-results | Google's parser, rich result eligibility |
| Schema.org Validator | validator.schema.org | Full spec compliance (broader than Google) |
| Google Search Console | Enhancements section | Real-world errors at scale, post-deployment |

### Validation Workflow

1. **Pre-deployment**: Rich Results Test + Schema.org Validator on the rendered HTML
2. **Post-deployment (day 1)**: Check page is crawled via URL Inspection tool in GSC
3. **Post-deployment (week 2-4)**: Check Enhancements section in GSC for errors at scale
4. **Ongoing (monthly)**: Monitor GSC Enhancements for new errors from content updates

---

## Common Errors and Fixes

| Error | Root Cause | Fix |
|-------|-----------|-----|
| Missing `@context` | Schema block has no context declaration | Add `"@context": "https://schema.org"` |
| Missing required field | A required property is absent | Add the field with real content from the page |
| `image` URL is relative | `/image.jpg` instead of absolute URL | Use `https://example.com/image.jpg` |
| `dateModified` < `datePublished` | Impossible date relationship | Ensure dateModified >= datePublished |
| Markup does not match page content | Schema claims content not visible to users | Only add schema for content actually on the page |
| Deprecated property | Using old schema.org property names | Check current spec at schema.org |
| Nested type conflict | Product inside Article incorrectly | Keep types flat or use proper @graph nesting |
| Date format wrong | Not ISO 8601 | Use `"2026-01-15"` or `"2026-01-15T10:30:00Z"` |
| Empty string values | `"name": ""` passes syntax but fails semantics | Use real values, never empty strings |
| Array expected, single value given | `mainEntity` needs array for FAQPage | Wrap in `[]` array brackets |
| Logo too large | Publisher logo exceeds 600x60px | Resize or use a different logo format |
| GTM injection not indexed | Client-side rendering | Move to server-side `<head>` injection |

---

## Audit Framework

### Audit Scorecard (0-100)

| Dimension | Weight | Scoring |
|-----------|--------|---------|
| Required fields present | 40% | -10 per missing required field |
| Recommended fields present | 15% | -3 per missing recommended field |
| Rich result eligibility | 20% | Binary: eligible or not |
| Content-markup match | 15% | -5 per mismatch between schema and visible content |
| sameAs and entity signals | 10% | -5 per missing major platform link |

### Priority Classification

| Priority | Criteria | Action |
|----------|----------|--------|
| P0 Critical | Required field missing, blocks rich result | Fix immediately |
| P1 High | Recommended field missing, reduces eligibility | Fix this week |
| P2 Medium | Content mismatch, deprecated property | Fix this month |
| P3 Low | Missing sameAs link, optional enhancement | Add when convenient |

---

## Output Artifacts

| Artifact | Format | Description |
|----------|--------|-------------|
| Schema Audit Report | Scored table | Per-page schema inventory, completeness score, priority fixes |
| JSON-LD Implementation | Copy-paste code blocks | Complete schema for each page type, populated with placeholder values marked clearly |
| Error Fix Log | Before/after JSON-LD | Each fix explained with root cause and prevention |
| AI Search Gap Analysis | Recommendation table | Missing entity markup, FAQPage opportunities, sameAs gaps |
| CMS Implementation Guide | Step-by-step instructions | Platform-specific deployment instructions |
| Rich Result Eligibility Matrix | Page type x schema x eligibility | Which pages qualify for which rich result types |

---

## Related Skills

- **seo-audit** -- For full technical and content SEO audits spanning beyond structured data. Use when the problem is broader than schema.
- **site-architecture** -- For URL structure and navigation. Use when architecture is the root cause, not schema.
- **programmatic-seo** -- For sites with thousands of pages that need schema at scale. Schema patterns feed into pSEO template design.
- **content-creator** -- For content creation. Use before implementing Article schema to ensure content quality.

---

## Troubleshooting

| Problem | Likely Cause | Fix |
|---------|-------------|-----|
| Schema passes validation but no rich results appear | Missing required fields for rich result eligibility, or Google has not recrawled | Verify against Google Rich Results Test (not just schema.org validator); request reindexing via GSC |
| FAQPage schema not generating FAQ dropdowns | Questions not visible to users on the page, or site lacks sufficient authority | Ensure Q&A content is visible in page HTML, not hidden behind tabs or JS toggles |
| Product schema shows "missing field" warnings in GSC | Required fields (price, availability, review) absent or malformed | Add all required Product + Offer fields; use ISO 4217 for currency, schema.org/InStock for availability |
| GTM-injected schema not being indexed | Client-side rendering — Google may not execute GTM JavaScript for schema | Move schema from GTM to server-side `<head>` injection; GTM schema is unreliable for indexing |
| dateModified older than datePublished | Data entry error or CMS auto-populating incorrectly | Ensure dateModified >= datePublished; audit CMS date field logic |
| Multiple conflicting Organization blocks | Different plugins or templates injecting separate Organization schema | Consolidate into a single Organization block on the homepage; remove duplicates |
| Schema validated but Google shows "content mismatch" | Schema claims content not actually visible to users on the page | Only add schema for content physically present on the page — never fake or hidden content |

---

## Success Criteria

- **Rich result eligibility**: 100% of content pages with appropriate schema types eligible for rich results per Google Rich Results Test
- **Validation pass rate**: Zero errors in Google Search Console Enhancements reports across all schema types
- **Rich result CTR boost**: Structured data pages achieving 20-35% higher CTR than non-structured pages (2026 benchmark from SearchPilot testing)
- **AI citation impact**: FAQPage and HowTo schema present on all informational content pages to maximize AI extraction
- **Entity recognition**: Organization schema with 5+ sameAs links deployed site-wide; brand appearing in Knowledge Graph
- **Coverage breadth**: Schema implemented on 95%+ of indexable pages (BreadcrumbList minimum, content-specific types on relevant pages)
- **Freshness accuracy**: dateModified updated within 24 hours of every content change across all Article schema

---

## Scope & Limitations

**In scope:**
- Schema type selection and JSON-LD implementation for 20+ schema types
- Rich result eligibility verification and optimization
- AI search visibility through structured data
- Knowledge Graph entity optimization
- Schema validation, testing, and error resolution
- CMS-specific deployment guidance (WordPress, Webflow, Shopify, Next.js)

**Out of scope:**
- Content creation for schema-eligible pages (use Content Production)
- Technical SEO beyond structured data (use SEO Audit)
- Microdata or RDFa implementations (JSON-LD only — Google's recommendation)
- Custom schema.org extensions or vocabulary proposals
- Server-side rendering implementation
- CMS plugin development

**Known limitations:**
- Google does not guarantee rich results even with valid schema — authority and content quality also factor in
- GTM-injected schema is frequently not indexed — server-side deployment is required for reliability
- Schema.org spec updates faster than Google's support — not all valid types generate rich results
- Rich result types can be deprecated with minimal notice (e.g., HowTo rich results were restricted in 2023)
- Structured data CTR impact varies by industry and SERP features present

---

## Scripts

```bash
# Validate JSON-LD schema from a file or URL
python scripts/schema_validator.py --file schema.json --json

# Audit a page for schema coverage and completeness
python scripts/schema_validator.py --html page.html --verbose

# Generate JSON-LD templates for common page types
python scripts/schema_generator.py --type Article --title "My Post" --author "Jane" --json
```
