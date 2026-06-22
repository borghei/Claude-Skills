---
name: aeo
description: >
  Answer Engine Optimization (AEO): optimize content to be cited by LLMs
  (ChatGPT, Claude, Perplexity, Gemini) in their answers. Use when designing
  content for LLM citation, auditing citability, or structuring Q&A schema.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: marketing
  domain: marketing
  updated: 2026-05-27
  tags: [aeo, answer-engine-optimization, llm-citation, generative-search, ai-content, schema-qa, geo, llm-seo]
---

# Answer Engine Optimization (AEO)

End-to-end practice of optimizing content to be cited by LLMs when they generate answers. Covers the technical foundations (how LLMs select sources), content structuring patterns (Q&A schema, citation-worthy patterns), measurement (which content gets cited, by which LLM, how often), and the strategic positioning that differentiates AEO from traditional SEO and from AI-SEO.

This skill is provider-aware but provider-agnostic: works for content optimized for ChatGPT, Claude, Perplexity, Gemini, Copilot, and emerging AI surfaces.

---

## When to use this skill

| Situation | Skill applies |
|-----------|---------------|
| Designing content strategy that targets LLM citation | Yes — start with **AEO fundamentals** |
| Auditing existing content for LLM citability | Yes — `scripts/aeo_content_auditor.py` |
| Adding Q&A schema to content | Yes — `scripts/schema_qa_generator.py` |
| Tracking which content gets cited by LLMs | Yes — `scripts/citation_extractor.py` |
| Choosing between AEO and traditional SEO investment | Yes — see **AEO vs SEO vs AI-SEO** |
| Ranking in Perplexity / Google AI Overviews | Use `marketing/ai-seo` |
| Traditional SEO (rank in Google search results) | Use `marketing/seo-specialist` |

---

## AEO vs SEO vs AI-SEO

Three distinct (but overlapping) practices. Confusing them leads to wasted investment.

| Practice | Optimizes for | Surface | Success metric |
|----------|---------------|---------|----------------|
| **Traditional SEO** | Google / Bing rankings | SERPs (organic blue links) | Position, clicks |
| **AI-SEO** | AI search engines | Perplexity, Google AI Overviews, You.com | Position in AI search results, traffic from citations |
| **AEO (this skill)** | LLM citation in answers | ChatGPT, Claude, Gemini, Copilot answers | Citation rate, brand mention in LLM outputs |

### Strategic positioning

For most B2B brands:
- **Traditional SEO**: still 50-70% of organic traffic. Don't abandon.
- **AI-SEO**: emerging 10-20% of search-driven engagement. Growing fast.
- **AEO**: 5-15% of LLM-mediated user discovery. Largest growth potential.

Optimize content for all three simultaneously; the techniques substantially overlap.

---

## The AEO funnel

Users find brands through LLMs in a different funnel than search:

```
Traditional search:           AEO funnel:
1. User types query           1. User asks LLM a question
2. SERPs show ~10 results     2. LLM generates answer
3. User clicks one            3. LLM cites N sources (1-10)
4. User reads page            4. User reads answer; may click cited source
5. User converts              5. User attributes answer to LLM (less so to cited brand)
```

Key implications:
- **Citation is the new click.** When LLM cites your content, you don't always get a visit — but you get attribution.
- **Brand-as-source becomes the goal.** Even without click, being cited builds brand association.
- **Quality > volume.** LLMs cite a small number of sources; quality of citation matters more than ranking position.
- **Trust signals matter more.** LLMs avoid citing low-authority sources.

See [references/aeo-fundamentals.md](references/aeo-fundamentals.md) for the deep mechanics of how LLMs select sources, the citation models per provider, and the trust signals that drive selection.

---

## The 5 content patterns that get cited

After analysis of LLM citation behavior, five content patterns dominate:

### Pattern 1: Definitional content with clear claims

LLMs cite sources for definitions, facts, and short claims. Pages that answer "What is X?" with a clean 2-3 sentence definition followed by elaboration get cited often.

**Structure:**
```
[Term] is [crisp definition in 1-2 sentences].

[Elaboration with context and nuance — 1-3 paragraphs].

[Related concepts / scope / boundaries — optional].
```

### Pattern 2: Comparative tables

LLMs use tables to extract comparisons. Markdown tables in published content (or HTML equivalents) get cited when users ask "X vs Y."

```markdown
| Feature | Product A | Product B |
|---------|-----------|-----------|
| Price | $X | $Y |
| Speed | Z ms | W ms |
| Support | 24/7 | Business hours |
```

### Pattern 3: Step-by-step procedural content

"How to [task]" content with explicit numbered steps. LLMs reproduce procedural steps; the cited source becomes the authoritative reference.

### Pattern 4: Statistics + data with sources

LLMs cite content that provides numerical facts with attribution. "According to [your study], X% of [thing] does Y" is repeatable and citable.

### Pattern 5: Lists with explanations

"Top N approaches to X" with each item explained gets cited when users ask comparative or enumeration questions.

See [references/llm-content-structuring.md](references/llm-content-structuring.md) for deep patterns including FAQ schema, citation hooks, voice-search optimization, and LLM-readable structure markers.

---

## Clarify First

Before generating, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Target queries** — the actual questions customers ask LLMs about your category (drives which content to audit and restructure)
- [ ] **Your brand name** — exact wording to track in answers vs competitors (drives citation extraction)
- [ ] **Target LLM surface** — ChatGPT / Claude / Perplexity / Gemini (citation behavior and trust signals differ per provider)
- [ ] **Canonical page/content** — the high-value page to be the authoritative source (drives schema generation + pattern restructuring)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Quick start

1. **Audit existing content**: `python3 scripts/aeo_content_auditor.py --path ./content`
2. **Add Q&A schema to high-value pages**: `python3 scripts/schema_qa_generator.py --content article.md`
3. **Track citations from competitors**: `python3 scripts/citation_extractor.py --query "What is X?" --brand "Your Brand"`
4. **Iterate**: monthly content review with AEO scoring

---

## End-to-end workflows

### Workflow: AEO content strategy from scratch

1. **Identify target queries** — what questions do potential customers ask LLMs about your category?
2. **Audit competitor citations** — which brands get cited for those queries? `scripts/citation_extractor.py`
3. **Audit your existing content** — score current content for AEO patterns: `scripts/aeo_content_auditor.py`
4. **Prioritize 10-20 high-value pages** — those that should be the canonical source
5. **Restructure per AEO patterns** — definitional content, tables, step-by-step, statistics
6. **Add structured data** — `scripts/schema_qa_generator.py` generates FAQ schema
7. **Build authority signals** — backlinks, citations, mentions
8. **Monitor monthly** — track citation rate trend

### Workflow: Audit individual content piece

1. Run `scripts/aeo_content_auditor.py --path article.md --format markdown`
2. Review per-pattern scoring (5 patterns above)
3. Identify gaps: missing definition, no table, no clear steps, no stats, no list
4. Restructure to add 2-3 missing patterns
5. Add FAQ schema with `scripts/schema_qa_generator.py`
6. Re-audit to confirm improvements

### Workflow: Competitive citation analysis

1. Identify 10-20 key queries in your category
2. Query each LLM (ChatGPT, Claude, Perplexity, Gemini) with those questions
3. Record citations + brands mentioned
4. Analyze: which brands dominate? what content do they have?
5. Identify white-space queries (no clear dominant source yet)
6. Prioritize content creation for white-space queries

### Workflow: Measure AEO performance

1. **Citation rate**: % of queries where your brand is cited (target: 30%+ for category leaders)
2. **Brand mention rate**: % of queries where your brand is mentioned (cited or not)
3. **Source quality**: are you cited as primary source or supporting?
4. **Click-through from citations**: traffic attributable to LLM citations (requires source tracking)
5. **Voice tracking**: how is your brand characterized (positive / neutral / negative attributes)

See [references/citation-tracking-and-measurement.md](references/citation-tracking-and-measurement.md) for measurement methodologies, attribution challenges, and competitive benchmarking.

---

## Common AEO failures

- **Optimizing only for Google SERP**: misses the LLM citation surface entirely
- **Generic content without specific claims**: LLMs prefer specific, factual content over generic explanation
- **No structure markers** (headings, lists, tables): LLMs can't extract specific information
- **No FAQ schema**: missed opportunity for Q&A surfacing in AI Overviews
- **Stuffed keyword content**: LLMs prefer natural language with clear meaning
- **No authority signals**: LLMs avoid citing low-trust sources
- **Outdated content**: LLMs prefer recent, current content
- **Hidden behind paywalls**: LLMs can't cite what they can't access
- **No structured data**: missed opportunity for richer extraction
- **Brand-first content**: LLMs prefer informational content over promotional

---

## LLM-by-LLM citation behavior

Different LLMs have different citation behaviors:

| LLM | Citation style | What gets cited |
|-----|----------------|-----------------|
| ChatGPT | Inline citations (when web-enabled); fewer otherwise | Recent, authoritative sources |
| Claude | Citations when grounding enabled (tools); generally avoids unsupported claims | High-quality sources, evidence-based |
| Perplexity | Always cites sources prominently | Recent + authoritative sources |
| Google Gemini / AI Overviews | Cites in AI Overviews + Gemini responses | High-ranking pages + structured data |
| Copilot (Microsoft) | Cites sources prominently | Sources varied |
| Meta AI | Lighter citation | Limited transparency |

Optimize content with structure markers (headings, lists, tables) and authority signals (links, citations, expert attribution) — works across all of these.

---

## Tooling

| Script | Purpose |
|--------|---------|
| `scripts/aeo_content_auditor.py` | Score content for AEO patterns (definition, table, steps, stats, list, structure markers) |
| `scripts/citation_extractor.py` | Parse LLM responses (saved transcripts) for brand citations + competitive analysis |
| `scripts/schema_qa_generator.py` | Generate JSON-LD FAQ schema from content (FAQPage / QAPage / HowTo) |

---

## References

- [aeo-fundamentals.md](references/aeo-fundamentals.md) — how LLMs select sources; citation mechanisms per provider; trust signals
- [llm-content-structuring.md](references/llm-content-structuring.md) — content patterns; Q&A schema; voice-search; structure markers
- [citation-tracking-and-measurement.md](references/citation-tracking-and-measurement.md) — measurement methodologies; attribution; benchmarking

---

## Related skills

- `marketing/ai-seo` — AI search engine ranking (Perplexity, Google AI Overviews); complementary to AEO
- `marketing/seo-specialist` — traditional SEO (Google rankings); foundational; still 50-70% of organic
- `marketing/seo-audit` — technical SEO audit
- `marketing/programmatic-seo` — scaled content production with SEO patterns
- `c-level-advisor/cs-cmo-advisor` — strategic AEO investment decisions
