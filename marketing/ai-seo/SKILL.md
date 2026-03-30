---
name: ai-seo
description: >
  Optimize content for AI search engines including Google AI Overviews, ChatGPT,
  Perplexity, Claude, Gemini, and Microsoft Copilot. Covers generative engine
  optimization (GEO), AI citability audits, content structuring for extraction,
  schema markup, bot access configuration, and monitoring. Use when optimizing
  for AI search, AI overviews, generative search, LLM visibility, semantic
  search, entity optimization, or when user mentions AI SEO, GEO, Perplexity
  citations, ChatGPT visibility, or AI-generated answers.
license: MIT
metadata:
  version: 1.0.0
  author: borghei
  category: marketing
  domain: seo
  updated: 2026-03-09
---
# AI SEO

Generative engine optimization (GEO) for getting cited by AI search platforms — not just ranked in traditional results.

---

## Table of Contents

- [Keywords](#keywords)
- [Quick Start](#quick-start)
- [How AI Search Differs from Traditional SEO](#how-ai-search-differs-from-traditional-seo)
- [The Three Pillars of AI Citability](#the-three-pillars-of-ai-citability)
- [Core Workflows](#core-workflows)
- [Content Patterns That Get Cited](#content-patterns-that-get-cited)
- [Schema Markup for AI Discovery](#schema-markup-for-ai-discovery)
- [Bot Access Configuration](#bot-access-configuration)
- [Monitoring and Tracking](#monitoring-and-tracking)
- [Best Practices](#best-practices)
- [Integration Points](#integration-points)

---

## Keywords

AI SEO, generative engine optimization, GEO, AI overviews, Google SGE, ChatGPT citations, Perplexity SEO, Claude citations, AI search optimization, semantic search, entity optimization, LLM visibility, AI-generated answers, structured data, schema markup, content extractability, AI citability, GPTBot, PerplexityBot, ClaudeBot, answer engine optimization

---

## Quick Start

### Run an AI Visibility Audit

1. Check robots.txt for AI bot access (GPTBot, PerplexityBot, ClaudeBot)
2. Test top 10 target queries on Perplexity, ChatGPT, and Google AI Overviews
3. Document which queries cite you, which cite competitors, and what content format wins
4. Score key pages against the Extractability Checklist
5. Prioritize pages with highest gap between search volume and current AI citation presence

### Optimize a Page for AI Citation

1. Add a clear definition block in the first 200 words for informational queries
2. Structure content with self-contained H2 sections that can be extracted independently
3. Add numbered steps for process queries, comparison tables for "X vs Y" queries
4. Replace all vague claims with attributed statistics ("According to [Source], [Year]")
5. Implement FAQPage, HowTo, or Article schema markup
6. Verify AI bots are allowed in robots.txt

---

## How AI Search Differs from Traditional SEO

### The Fundamental Shift

Traditional SEO gets your page ranked. AI SEO gets your content cited. These are different optimization targets.

| Dimension | Traditional SEO | AI SEO |
|-----------|----------------|--------|
| Goal | Rank on page 1 | Get cited in AI-generated answers |
| Success metric | Click-through rate | Citation frequency |
| Content priority | Keyword density | Answer extractability |
| Authority signal | Backlinks + domain authority | Backlinks + answer quality + attribution |
| User interaction | User clicks your link | AI extracts your answer; user may never visit |
| Content format | Long-form comprehensive | Self-contained extractable blocks |
| Optimization unit | The page | The paragraph or section |

### What Carries Over from Traditional SEO

- Domain authority still matters. AI systems prefer credible sources.
- Backlinks still signal trust and expertise.
- Technical SEO fundamentals (page speed, mobile-friendly, clean HTML) still apply.
- Quality content with original insights still wins.

### What Changes

- Keyword density matters less than answer clarity and directness
- Page-level optimization expands to section-level and paragraph-level optimization
- Internal linking serves discoverability for AI crawlers, not just PageRank flow
- Structured data becomes a primary signal, not a nice-to-have

---

## The Three Pillars of AI Citability

### Pillar 1: Structure (Extractable)

AI systems pull content in chunks. They find the paragraph, list, or definition that directly answers a query and extract it. Your content must be structured so answers are self-contained.

**Extractability requirements:**
- Definition blocks for "what is X" queries — tight, 1-2 sentence definitions in the first 200 words
- Numbered steps for "how to do X" queries — verb-first, self-contained steps
- Comparison tables for "X vs Y" queries — clean table format with headers
- FAQ blocks for question-based queries — explicit Q&A pairs
- Statistics with full attribution for data-oriented queries

**Anti-patterns that kill extractability:**
- Burying the answer in paragraph 8 of a 4,000-word essay
- Requiring context from previous sections to understand any individual section
- Using narrative prose for comparisons that should be tables
- Placing key definitions only in the conclusion

### Pillar 2: Authority (Citable)

AI systems do not just extract the most relevant answer — they extract the most credible one.

**Authority signals in the AI era:**
- **Domain authority** — High-DA domains get preferential citation
- **Author attribution** — Named authors with credentials outperform anonymous pages
- **Citation chains** — Your content cites credible sources, making you credible in turn
- **Recency** — AI systems prefer current information for time-sensitive queries
- **Original data** — Proprietary research, surveys, and studies get cited more because AI cannot find this data elsewhere
- **Consistent entity presence** — Your brand appears across authoritative sources as an entity

### Pillar 3: Presence (Discoverable)

AI systems must be able to find and index your content.

**Technical requirements:**
- AI crawlers allowed in robots.txt
- Fast page load and clean HTML
- No JavaScript-only rendering for important content
- Schema markup for content type classification
- Proper canonical signals
- HTTPS with valid certificates

---

## Core Workflows

### Workflow 1: AI Visibility Audit

**Step 1: Bot Access Verification**

Check robots.txt for AI crawler permissions:

```
# These bots must NOT be blocked for AI visibility:
GPTBot          # OpenAI / ChatGPT
PerplexityBot   # Perplexity
ClaudeBot       # Anthropic / Claude
Google-Extended # Google AI Overviews
anthropic-ai    # Anthropic (alternate)
Applebot-Extended  # Apple Intelligence
cohere-ai       # Cohere
```

If any AI bot is blocked, that is the single highest priority fix. Zero visibility on that platform until resolved.

**Step 2: Citation Testing**

Test top 10 target queries on each platform:

| Platform | How to Test | What to Record |
|----------|-------------|----------------|
| Perplexity | Search at perplexity.ai, check Sources panel | Cited? Which competitors cited? Content format winning? |
| ChatGPT | Web browsing enabled, check citations | Same |
| Google AI Overviews | Google query, check AI Overview panel | Same |
| Microsoft Copilot | Search at copilot.microsoft.com, check source cards | Same |
| Claude | Web search enabled queries | Same |

**Step 3: Content Extractability Scoring**

Score each key page (0-7):

- [ ] Clear definition of core concept in first 200 words
- [ ] Numbered lists or step-by-step sections for process queries
- [ ] FAQ section with direct Q&A pairs
- [ ] Statistics cited with source name and year
- [ ] Comparisons in table format (not narrative)
- [ ] H1 phrased as an answer or direct statement
- [ ] Schema markup present (FAQPage, HowTo, Article)

Interpretation: 0-3 = needs major restructuring. 4-5 = good baseline. 6-7 = strong.

**Step 4: Competitive Citation Analysis**

For each target query, document:
- Who is currently being cited (top 3 sources per platform)
- What content format wins (definition, list, table, quote)
- What your content lacks that cited competitors provide
- Where you have unique data or expertise competitors lack

### Workflow 2: Page Optimization for AI Citation

**Step 1: Lead with the Answer**

The first paragraph must contain the core answer to the target query. No preamble, no context-setting, no "In today's landscape..." openers.

**Step 2: Structure Self-Contained Sections**

Every H2 section must be answerable as a standalone excerpt:
- Each section opens with its main point
- Each section contains its own evidence
- No section requires reading previous sections to be understood
- Each section could be quoted out of context and still make sense

**Step 3: Add Extractable Content Blocks**

Insert 2-3 of these per key page:
- Definition block (first 200 words)
- Numbered how-to steps (5-10 max, verb-first)
- Comparison table (clean headers, structured data)
- FAQ pairs (question matches natural language query)
- Attributed statistics ("According to [Source] ([Year]), X% of...")
- Expert quote block ("[Name], [Role at Organization]: '[quote]'")

**Step 4: Replace Vague with Specific**

Find and replace every vague claim:
- "Many companies" → name the companies or cite the count
- "Studies show" → name the study, organization, and year
- "Significantly improved" → state the percentage improvement
- "Leading brands" → name at least one
- "Experts say" → name the expert with credentials

**Step 5: Add Schema Markup**

Implement JSON-LD in the page head:

| Content Type | Schema | Impact |
|-------------|--------|--------|
| FAQ sections | FAQPage | High — AI extracts Q&A pairs directly |
| Step-by-step guides | HowTo | High — AI uses step structure |
| Articles and posts | Article | Medium — establishes content authority |
| Product pages | Product | Medium — product comparison queries |
| Author pages | Person | Medium — author credibility signal |
| Company pages | Organization | Medium — entity authority |

### Workflow 3: Entity Optimization

**Step 1: Define Your Entity**

Ensure your brand exists as a recognized entity across the web:
- Wikipedia or Wikidata presence
- Google Knowledge Panel
- Consistent NAP (name, address, phone) across citations
- Structured About page with Organization schema

**Step 2: Build Entity Associations**

Connect your entity to relevant topics:
- Publish original research on topics you want to be cited for
- Get mentioned (with links) on authoritative sites in your domain
- Contribute expert quotes to industry publications
- Maintain active presence on platforms AI systems index

**Step 3: Strengthen the Citation Chain**

Create a network of credible references:
- Your content cites authoritative sources
- Authoritative sources cite your content
- Your author pages link to credentials and publications
- Your brand appears in industry roundups and comparisons

---

## Content Patterns That Get Cited

### Pattern 1: Definition Block

```markdown
**[Term]** is [concise definition in 1-2 sentences]. [One sentence of context
explaining why it matters or how it differs from related concepts].
```

Place within the first 200 words. No hedging, no preamble.

### Pattern 2: Numbered Steps

Requirements for AI extraction:
- Steps are numbered (not bulleted)
- Each step starts with an action verb
- Each step is self-contained (could be quoted alone)
- 5-10 steps maximum (AI truncates longer lists)
- Each step has a brief explanation (1-2 sentences)

### Pattern 3: Comparison Table

Two-column or multi-column tables with clean headers:

```markdown
| Dimension | Option A | Option B |
|-----------|----------|----------|
| Price | $X/mo | $Y/mo |
| Key Feature | Description | Description |
| Best For | Use case | Use case |
```

### Pattern 4: FAQ Block

Explicit Q&A pairs. Questions should match natural language queries:

```markdown
### What is [topic]?
[Direct answer in 1-2 sentences.]

### How does [topic] work?
[Step-by-step explanation.]
```

Mark up with FAQPage schema for maximum discoverability.

### Pattern 5: Attributed Statistics

```markdown
According to [Source Name] ([Year]), X% of [population] [finding].
```

Complete attribution is critical. Unattributed statistics get deprioritized because AI cannot verify the source.

### Pattern 6: Expert Quote Block

```markdown
"[Quote]" — [Name], [Role] at [Organization]
```

Named experts with credentials produce citable units AI systems pick up.

---

## Schema Markup for AI Discovery

### Priority Implementations

**FAQPage Schema (highest impact for informational queries):**

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What is [topic]?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "[Direct answer]"
      }
    }
  ]
}
```

**HowTo Schema (high impact for process queries):**

```json
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "How to [do thing]",
  "step": [
    {
      "@type": "HowToStep",
      "name": "Step name",
      "text": "Step description"
    }
  ]
}
```

**Article Schema (medium impact, establishes authority):**

```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Title",
  "author": {
    "@type": "Person",
    "name": "Author Name",
    "url": "https://author-page"
  },
  "datePublished": "2026-01-15",
  "dateModified": "2026-03-01"
}
```

Validate all schema at schema.org/validator before deployment.

---

## Bot Access Configuration

### Recommended robots.txt Configuration

```
# Allow all AI search crawlers
User-agent: GPTBot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: Applebot-Extended
Allow: /

User-agent: cohere-ai
Allow: /
```

### Training vs. Citation Access

Some organizations want to allow AI citation but block training. This distinction is difficult to enforce because:
- Most AI crawlers use the same bot for both indexing and training
- Blocking the bot blocks both citation and training
- There is no industry-standard mechanism to allow one and block the other

Recommendation: Allow AI bots if you want AI citation visibility. The citation benefits outweigh the training concerns for most commercial content.

---

## Monitoring and Tracking

### Weekly Citation Tracking (20 minutes/week)

Test top 10 target queries on Perplexity and ChatGPT:
- Were you cited? (yes/no)
- Citation rank (1st source, 2nd, 3rd)
- What text was used from your content?
- Any new competitors appearing?

### Google Search Console for AI Overviews

Use the "Search type: AI Overviews" filter in Google Search Console:
- Which queries trigger AI Overview impressions for your site
- Click-through rate from AI Overviews (typically 50-70% lower than organic)
- Which pages get cited most frequently

### Monthly Monitoring Checklist

| Signal | What to Check | Tool |
|--------|---------------|------|
| Perplexity citations | Top 10 queries | Manual testing |
| ChatGPT citations | Top 10 queries | Manual testing |
| Google AI Overviews | Impressions and clicks | Google Search Console |
| Copilot citations | Top 5 queries | Manual testing |
| AI bot crawl activity | Crawl frequency and pages | Server logs / Cloudflare |
| Competitor citations | Who is getting cited for your queries | Manual testing |
| Content freshness | Date signals on key pages | Content audit |

### When Citations Drop

Diagnostic checklist when you lose a citation:
1. Did robots.txt change? (Check for accidental AI bot blocks)
2. Did a competitor publish more extractable content?
3. Did your page structure change? (Restructuring can break citation patterns)
4. Did your domain authority drop? (Check backlink profile)
5. Did the query intent shift? (AI systems may reinterpret the query)

---

## Best Practices

1. **Optimize at the section level, not just the page level** — AI extracts paragraphs and sections, not entire pages. Every H2 block should be independently citable.

2. **Lead with the answer, always** — The first 200 words determine whether AI systems find your content useful. Put the answer there.

3. **Attribute everything** — Unattributed statistics, unnamed experts, and sourceless claims reduce your citability. Name names.

4. **Update quarterly** — AI systems prefer recent content. Update publish dates and refresh data points every 90 days.

5. **Build entity presence** — The stronger your brand's entity recognition across the web, the more AI systems trust and cite you.

6. **Do not choose between traditional SEO and AI SEO** — They are complementary. Many optimization signals overlap. Run both.

7. **Test on multiple platforms** — A page cited on Perplexity may not be cited on ChatGPT. Optimize for the platforms your audience uses.

8. **Monitor competitors monthly** — Track who gets cited for your target queries and study what content patterns they use.

9. **Avoid JavaScript-rendered content for key answers** — AI crawlers may not execute JavaScript. Ensure important content is in the initial HTML.

10. **Implement schema early** — FAQPage and HowTo schema are quick wins with outsized impact on AI discoverability.

---

## Integration Points

- **SEO Specialist** — Use for traditional search ranking optimization. Run AI SEO and traditional SEO in parallel.
- **Content Production** — Use to create the underlying content before optimizing for AI citation.
- **Content Humanizer** — Use after writing. AI-sounding content performs worse in AI citations — AI systems prefer credible, human-sounding writing.
- **Content Strategy** — Use when deciding which topics and queries to target for AI visibility.
- **Marketing Analytics** — Use campaign analytics tools to track the business impact of AI citation traffic.

---

## Troubleshooting

| Problem | Likely Cause | Fix |
|---------|-------------|-----|
| Content not cited despite high DA | Poor extractability — answers buried in prose | Restructure with definition blocks, numbered steps, and FAQ pairs in first 200 words |
| Cited on Perplexity but not ChatGPT | Different crawling and indexing pipelines per platform | Verify bot access for all AI crawlers; test rendering without JavaScript |
| AI Overview shows competitor instead | Competitor has more extractable, better-attributed content | Audit competitor's cited content format and match or exceed specificity |
| Citation dropped after site update | Page restructure broke the extraction pattern AI was using | Compare old vs new page structure; restore extractable blocks |
| GPTBot blocked in robots.txt unknowingly | CMS update or security plugin overwrote robots.txt | Audit robots.txt after every CMS or plugin update; set up monitoring |
| Schema markup present but no rich results | Missing required fields or content-markup mismatch | Validate with Google Rich Results Test; ensure schema matches visible page content |
| AI cites your data but not your brand | Missing entity signals — no Organization schema or sameAs links | Implement Organization schema with sameAs to Wikidata, LinkedIn, and social profiles |

---

## Success Criteria

- **AI citation rate**: Achieve citation in 30%+ of target queries across Perplexity, ChatGPT, and Google AI Overviews within 90 days of optimization
- **Extractability score**: Score 6-7 out of 7 on the Content Extractability Scoring checklist for all key pages
- **Bot access**: Zero AI crawlers blocked in robots.txt — verified monthly with automated monitoring
- **Entity recognition**: Brand appears in Google Knowledge Panel and is recognized as an entity on Wikidata
- **Schema coverage**: 100% of content pages have appropriate JSON-LD schema (Article, FAQPage, or HowTo) validated without errors
- **Freshness cadence**: All key pages updated within the last 90 days with current dateModified signals
- **CTR from AI Overviews**: Maintain organic CTR above 0.8% for queries where AI Overviews appear (benchmark: average drops to 0.61% with AI Overviews per 2026 data)

---

## Scope & Limitations

**In scope:**
- Optimizing content structure for AI extraction and citation
- Bot access configuration and monitoring
- Schema markup implementation for AI discoverability
- Entity optimization and Knowledge Graph presence
- Citation tracking across AI search platforms
- Content pattern design (definitions, steps, tables, FAQs)

**Out of scope:**
- Traditional organic ranking optimization (use SEO Specialist)
- Content creation from scratch (use Content Production)
- Paid search or paid AI placement strategies
- AI model training data licensing or opt-out negotiations
- Platform-specific API integrations for automated tracking
- Social media optimization for AI-adjacent platforms

**Known limitations:**
- AI citation tracking is largely manual — no standardized API exists across platforms
- Citation algorithms are opaque and change frequently without notice
- Blocking AI training while allowing citation is not technically enforceable with current bot protocols
- AI Overviews reduce traditional organic CTR by approximately 42-47% (2026 benchmarks), and this cannot be fully mitigated

---

## Scripts

```bash
# Analyze content for AI citability signals
python scripts/content_scorer.py page.html --json

# Simulate how content might appear in AI search results
python scripts/serp_simulator.py --query "what is cloud cost optimization" --content page.md

# Analyze keyword opportunities for AI search visibility
python scripts/keyword_analyzer.py --keywords keywords.csv --json
```
