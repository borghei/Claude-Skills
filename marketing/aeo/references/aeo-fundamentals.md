# AEO Fundamentals

Deep reference on how LLMs select sources to cite, citation mechanisms per provider, the trust signals that drive selection, and the strategic positioning of AEO relative to traditional SEO and AI-SEO.

---

## How LLMs select sources

Modern LLMs use one of three citation mechanisms:

### 1. Training-time citation (implicit)

Sources mentioned in training data become part of the model's parametric knowledge. The model can reproduce facts without explicitly citing source. Brand mentions accumulated over years of training-data presence shape what the model knows.

**Implications:**
- Long-tail brand presence in high-quality sources (Wikipedia, major publications, academic) matters even without per-query citation
- New brands have a cold-start disadvantage
- Content authored in 2024+ may not appear until next training cycle (typically 6-18 month lag)

### 2. Retrieval-time citation (RAG / web-enabled)

When the LLM has web access (ChatGPT browsing, Claude with web search, Perplexity always, Gemini with grounding), it retrieves current sources and cites them in the answer.

**Selection signals (varies by provider):**
- Search ranking (uses upstream search engine: Google / Bing typically)
- Source authority (domain reputation)
- Content recency
- Content relevance to the specific query
- Structured data presence (helps extraction)
- Citation quality from prior interactions

**Implications:**
- Traditional SEO matters — LLMs use search results as input
- Content structure matters — extractable content gets cited more
- Authority matters — established domains preferred over new

### 3. Tool-mediated citation

When LLMs use specific tools (Anthropic's Computer Use, OpenAI function calls, etc.), citations come from tool outputs. Less common for typical user queries.

---

## What makes content citable

Beyond search ranking, specific content properties increase citation rate:

### Property 1: Specificity over generality

LLMs cite specific claims. "The recommended ratio is 1:7" is more citable than "the ratio depends on context."

### Property 2: Extractable structure

LLMs can extract:
- Numbered lists
- Tables with clear headers
- Q&A pairs
- Definitions with clear subject-verb-object structure
- Step-by-step procedures

LLMs cannot reliably extract:
- Narrative prose with implicit structure
- Information embedded in images without alt text
- Content in PDFs (most LLMs can't read PDFs natively)
- Tweet / social-media-style fragments

### Property 3: Citation-friendly URL structure

LLMs cite URLs. Good URL structure:
- Permanent / stable
- Human-readable (slug includes topic)
- Accessible (no login wall; no JS-only rendering)
- Indexed (in Google's index = likely in LLM's reach)

### Property 4: Author + publication date visible

LLMs prefer cite-able sources with author attribution + date. Avoid:
- Anonymous content
- Hidden dates
- "Last updated" without specific date

### Property 5: Authority signals

- Domain authority (Ahrefs DR, Moz DA — proxies)
- Inbound links from other authoritative domains
- Wikipedia presence
- Citations in academic / news sources
- Industry recognition (analyst reports referencing brand)

---

## Trust signals (what LLMs avoid)

LLMs (their training and grounding pipelines) systematically de-prioritize:

- Spammy domains
- Aggressive ads
- Thin content (low word count, low information density)
- AI-generated content without human review (yes, ironic)
- Content with high engagement-bait patterns
- Sources flagged for misinformation
- Hate speech / extreme content
- Affiliate-link farms
- Outdated content for time-sensitive topics
- Content behind paywalls (mostly; some LLMs handle some paywalls)

---

## Citation mechanisms per provider

### ChatGPT (OpenAI)

**Without browsing:** Cites primarily from training-time knowledge. Citations are implicit (brand mentions appear in answers, but no source links).

**With browsing/search:** Cites with inline links when answer requires recent / specific information. Browsing typically engaged for time-sensitive or specific factual queries.

**ChatGPT search** (the SearchGPT prototype was folded into ChatGPT in 2024): More explicit inline citations with source links, similar to the Perplexity model. Served from the `OAI-SearchBot` index.

### Claude (Anthropic)

**Native:** Tends to avoid citing without evidence; less likely to provide specific URL citations than ChatGPT.

**With tools / grounding:** Cites sources when web search / retrieval is part of the response.

**Quality bias:** Strong preference for high-quality, evidence-based sources. Lower tolerance for low-authority citations.

### Perplexity

**Citation-first:** Every answer includes source citations prominently displayed. Multiple sources per answer (typically 4-10).

**Search-grounded:** All answers run through search before answering. Heavy use of recent web content.

**Implications for AEO:** Perplexity is the most-amenable to AEO investment. If you rank in their search, you get cited.

### Google Gemini / AI Overviews

**AI Overviews (in Google Search):** Inline citations to source pages. Selected for queries where AI Overview is shown (mostly informational queries).

**Gemini conversational:** Cites sources when relevant; web-grounded by default in many use cases.

**Implications:** Google AI Overviews are heavily SEO-driven. If you rank top 10 in Google, you have a shot at AI Overview citation.

### Microsoft Copilot

**Bing-grounded:** Most answers grounded in Bing search results. Citations prominently displayed.

**SharePoint / enterprise:** Internal sources cited for enterprise Copilot.

### Meta AI

**Limited transparency:** Citations less consistent. Brand presence in training data more important than retrieval-time.

---

## Citation distribution patterns

Observed patterns in LLM citations:

| Pattern | Description |
|---------|-------------|
| **Winner-take-most** | For specific factual queries, 1-3 sources dominate (often Wikipedia + 1-2 authoritative sites) |
| **Diverse for opinion queries** | "Best X for Y" queries cite 5-10 sources, more democratic |
| **Recency bias** | News / current-event queries cite recent sources heavily |
| **Authority bias** | Health / legal / financial queries cite high-authority sources (.gov, .edu, major publications) |
| **Brand bias** | When asking about specific brand, the brand's own content is cited (often #1) |

---

## Strategic AEO positioning

### When AEO matters most

| Industry / context | AEO importance |
|---------------------|----------------|
| B2B SaaS / Tech | High; technical buyers ask LLMs |
| Professional services (legal, accounting, consulting) | High; high-trust info-seeking |
| Healthcare | High but regulated; trust signals critical |
| Finance | High but regulated |
| Consumer brands | Medium; consumer LLM use growing |
| Local services | Medium; LLM doesn't replace local search well |
| E-commerce | Variable; product-specific queries vs research queries |

### When NOT to invest in AEO

- **Pre-PMF brands without informational content**: AEO requires content investment that may not return
- **Hyperlocal businesses**: Google Maps still dominates local queries
- **Pure transactional commerce**: "Buy X" queries less LLM-mediated than "Research X" queries
- **Highly regulated content** that can't make specific claims: AEO benefits from specificity

### AEO investment levels

| Investment level | Activities | Quarterly time |
|------------------|------------|----------------|
| Minimal | Direct answers + visible Q&A on existing top pages; monitor citation | 4-8 hours |
| Standard | Top-20-pages restructuring per AEO patterns; monthly tracking | 40-60 hours |
| Comprehensive | Content strategy + production + monitoring + competitive analysis | 100-200 hours |
| Strategic | Above + brand-positioning campaigns (PR / partnerships) | 300+ hours |

---

## How LLMs evolve (and what to track)

LLM citation behavior changes:
- New training cycles → updated parametric knowledge
- New search providers → different retrieval-time citation
- New product features → AI Overviews, Perplexity Pro, etc.

Track:
- LLM market share (which to optimize for)
- New citation surfaces (AI Overviews, Perplexity Spaces, etc.)
- Provider policy changes (training data opt-outs, paywall handling)
- Industry citation patterns in your category

---

## Common AEO misconceptions

### Misconception 1: "AEO = AI-generated content"

False. AI-generated content is often de-prioritized. AEO is about content STRUCTURE and AUTHORITY, not authorship.

### Misconception 2: "AEO is just SEO with new keywords"

False. AEO requires structure (tables, lists, Q&A), specificity (claims, statistics), and authority (trust signals) beyond keyword optimization.

### Misconception 3: "If we rank #1 in Google we'll be cited by LLMs"

Mostly true for Perplexity + Google AI Overviews. Less true for ChatGPT / Claude where training-time mentions matter.

### Misconception 4: "AEO replaces SEO"

False. SEO is still 50-70% of traffic. AEO adds another channel.

### Misconception 5: "We can measure AEO precisely like SEO"

False. AEO measurement is harder. Citations don't always link back; brand mentions in LLM answers are hard to detect; provider attribution varies.

### Misconception 6: "Just add Q&A schema and we're optimized"

Partly. Q&A schema helps extraction; doesn't substitute for content structure + authority.

---

## AEO and brand voice

AEO content has a tension with brand voice:
- AEO content prefers: factual, structured, specific
- Brand voice often: personal, narrative, distinctive

Balance:
- Brand pages (homepage, about) stay brand-voice
- Knowledge content (blogs, guides, docs) goes AEO-structured
- Product pages mix (top: brand; bottom: structured specs / FAQ)

---

## Cheat sheet

| Question | Answer |
|----------|--------|
| Where to start? | Audit existing content for AEO patterns; restructure top 10 pages |
| Which LLM to optimize for? | All, simultaneously — techniques overlap |
| AEO vs SEO investment split? | 60-70% SEO foundation; 20-30% AEO restructuring + measurement |
| Time to see results? | 3-6 months for content updates to be indexed + reflected in LLM citations |
| Most-impactful single tactic? | Direct 1-2 sentence answers at the top of your top 20 pages |
| How to measure? | Citation extraction from saved LLM queries; brand mention rate |
| When does AEO replace SEO? | It doesn't; it's a parallel channel |
| Does AEO help conversions? | Indirectly — brand mention in LLM answer drives brand awareness; conversion comes later |
