# Citation Tracking and Measurement

Reference for measuring AEO performance: citation rate, brand mention rate, sentiment, attribution challenges, competitive benchmarking, dashboard design.

---

## What to measure

### Primary AEO metrics

| Metric | Definition | Target |
|--------|-----------|--------|
| **Citation rate** | % of target queries where your brand is cited | 30%+ for category leaders; 10%+ for emerging |
| **Brand mention rate** | % of target queries where your brand is mentioned (cited or not) | 50%+ for category leaders |
| **Source quality** | Are you cited as primary source or supporting? | Aim for primary on category-defining queries |
| **Citation sentiment** | Positive / neutral / negative characterization in cited context | > 80% positive/neutral |
| **Share of voice (SOV) in citations** | Your citations / total citations across competitors | Aim for top-3 in category |
| **Click-through from citations** | Traffic attributable to LLM citations (if measurable) | Variable; growing |

### Secondary metrics

| Metric | Definition |
|--------|-----------|
| **Citation freshness** | Average age of content cited |
| **Citation distribution by surface** | Which LLM cites you most (ChatGPT vs Claude vs Perplexity etc.) |
| **Query coverage** | % of in-category queries where you appear |
| **Long-tail vs head citation** | Citations for high-volume vs niche queries |
| **Schema markup rate** | % of your content with valid, page-appropriate schema (FAQ / QAPage / HowTo optional — low impact, no Google rich result for FAQ/HowTo) |

---

## Citation extraction methodology

### Manual method (small scale, qualitative)

1. **Identify target queries** — list of 20-50 queries in your category
2. **Query each LLM** — submit each query to ChatGPT, Claude, Perplexity, Gemini, Copilot
3. **Capture full response** — text + citations (where shown)
4. **Tag for analysis** — brand mentions, source URLs, sentiment

**Pros:** Captures full context; sentiment analysis possible
**Cons:** Doesn't scale; sample-based; LLM responses vary across queries

### Semi-automated method (medium scale)

1. **API-based querying** — use LLM APIs to programmatically query
2. **Parse responses** — extract citations + brand mentions
3. **Store in DB** — query / LLM / response / citations
4. **Dashboard** — citation rate over time

**Pros:** Scales to hundreds of queries; consistent capture
**Cons:** API costs; doesn't capture consumer-LLM behavior (no API access for ChatGPT-app, only API responses)

### Third-party tracker tools

Emerging category of tools that track brand mentions in LLMs:
- Profound, Otterly, Athena, others
- Subscribe-based; track your brand vs competitors
- Provide dashboards + alerts

Best for: ongoing tracking without DIY infrastructure.

---

## Attribution challenges

AEO attribution is harder than SEO attribution:

### Challenge 1: No referrer

When a user clicks a citation in an LLM response, the referrer is often the LLM domain (chat.openai.com, claude.ai, perplexity.ai) — not preserving the originating query.

**Workaround:**
- UTM parameters on cited URLs (if you control them)
- Cohort analysis: traffic from LLM domains
- Survey users ("How did you hear about us?" → "AI assistant / ChatGPT")

### Challenge 2: No-click citations

Most LLM citations don't generate a click. Brand mention exists; web traffic doesn't change.

**Workaround:**
- Measure brand-mention rate (not just citation-driven traffic)
- Brand-awareness lift survey (annual)
- Direct-traffic increase as proxy

### Challenge 3: LLM response variability

Same query, multiple responses, different citations. Statistical significance requires multiple samples per query.

**Workaround:**
- Query each LLM 3-5x per target query
- Use median citation rate, not single-instance

### Challenge 4: Training-time vs retrieval-time

When LLM cites without web grounding, the brand mention comes from training data. Hard to attribute to specific content investment.

**Workaround:**
- Track brand mentions in long-term training-data-proxy sources (Wikipedia, major publications)
- Distinguish "with browsing" vs "without browsing" citations

### Challenge 5: Sentiment / characterization variability

LLM may cite you but characterize you neutrally or negatively. Citation alone insufficient.

**Workaround:**
- Capture full context, not just URL
- Sentiment classification per citation
- Track narrative shifts over time

---

## Sampling methodology

### Query selection

Pick queries representative of your category:

- **Definitional queries**: "What is X?"
- **Comparison queries**: "X vs Y"
- **Best-of queries**: "Best X for Y"
- **How-to queries**: "How to X"
- **Recommendation queries**: "Should I use X?"
- **Brand-specific queries**: "Is [brand] worth it?", "[brand] review"

Aim for 50-200 queries per category.

### Sampling frequency

- **Daily**: for time-sensitive industries (news, finance)
- **Weekly**: standard
- **Monthly**: for slow-moving categories

### LLM sampling

Sample across LLMs in proportion to your audience's usage:

| LLM | Approximate market share (2026) | Recommended sampling weight |
|-----|--------------------------------|------------------------------|
| ChatGPT | 60-65% | 60% of queries |
| Gemini | 15-20% | 20% of queries |
| Claude | 8-12% | 10% of queries |
| Perplexity | 5-8% | 5% of queries |
| Copilot | 3-5% | 3% of queries |
| Other | 1-3% | 2% of queries |

Adjust per actual audience usage (verify via survey).

---

## Competitive benchmarking

### Share of voice (SOV) in citations

```
SOV (your brand) = your citations / total citations across all brands × 100%
```

For each target query:
- List all brands cited
- Calculate share for each
- Aggregate across queries

Healthy SOV by stage:
- Category leader: 25-40% SOV
- Top 3: 10-25%
- Growing: 5-15%
- Emerging: < 5%

### Competitor citation analysis

For competitors that out-cite you:
- Which queries do they win?
- What content do they have for those queries?
- What's the structure / format?
- What's their authority profile?

Compete by:
- Building equivalent content (better structured)
- Targeting white-space queries (no clear leader yet)
- Building authority through earned media

### Share of citations by content type

Track which content types drive your citations:
- Blog posts (informational)
- Documentation (technical)
- Product pages (transactional)
- Research / reports (data-driven)
- Customer stories (social proof)

Helps allocate content investment.

---

## Sentiment analysis

For each citation, classify sentiment:

| Sentiment | Definition | Example |
|-----------|-----------|---------|
| Positive | Brand favorably characterized | "[Your brand] is widely considered the leading X" |
| Neutral | Mentioned as one of several options | "Among the options are [your brand]..." |
| Negative | Brand unfavorably characterized | "[Your brand] is known for [negative trait]" |

### Detection methods

- **Manual**: human reviewers tag citations (small samples)
- **LLM-assisted**: use LLM to classify sentiment of citations (medium scale)
- **Automated**: NLP-based sentiment analysis (large scale; less accurate for nuance)

Target: > 80% positive/neutral; investigate negative citations (often based on outdated info or specific incidents).

---

## Dashboard design

### Daily / weekly view

- Citation rate trend (line chart, last 90 days)
- Top 10 queries cited for (table)
- New negative citations (alert)
- LLM-by-LLM distribution (bar chart)

### Monthly view

- Citation rate by category
- Share of voice trend
- Content type contribution
- Sentiment distribution
- Competitive comparison

### Quarterly view

- AEO ROI estimate
- Content investment vs citation lift
- Strategic recommendations

---

## Tooling stack (recommended)

| Tool category | Examples | Use |
|---------------|----------|-----|
| LLM APIs | OpenAI, Anthropic, Google AI Studio, Perplexity | Query LLMs programmatically |
| Citation extraction | Custom scripts (our `citation_extractor.py`) | Parse responses |
| Storage | Postgres / BigQuery / Snowflake | Store query + response + citations |
| Dashboarding | Looker / Tableau / Metabase | Visualize trends |
| Specialized tools | Profound / Otterly / Athena | Ongoing competitive tracking |
| Sentiment | LLM-as-judge or NLP libraries | Classify sentiment |

---

## Common measurement failures

### Failure 1: Measuring only what's easy

E.g., only counting Perplexity citations (most explicit) and ignoring ChatGPT / Claude (less explicit).

### Failure 2: Single-LLM bias

Optimizing for one LLM (often ChatGPT) and missing where audience actually queries.

### Failure 3: Conflating mention with citation

Brand mentioned in LLM response = mention. Brand-source URL referenced = citation. Different metrics.

### Failure 4: Ignoring sentiment

Citation count up, but negative? Worse than no citation. Always measure sentiment.

### Failure 5: Not segmenting by query intent

Branded queries (asking about your brand) ≠ category queries (asking about your space). Citations from each have different value.

### Failure 6: Over-relying on direct-traffic proxy

Direct traffic increase has many causes; LLM attribution requires more rigorous methodology.

---

## ROI estimation

Estimate AEO ROI:

```
AEO ROI = (Estimated brand-awareness lift × Brand value per impression × Citation count)
          - AEO investment cost
```

Approximations:
- Brand-awareness lift per citation: typically equivalent to a low-quality social media impression (~$0.01-$0.10 brand value)
- Or: citation in high-trust context (LLM-cited as authoritative) ~ $0.50-$2.00 brand value per impression
- Aggregate across thousands of citations per month

Specifics vary; require survey-based validation.

### Budget allocation guide

Quarterly AEO investment by stage:

| Stage | Investment | Activities |
|-------|------------|-----------|
| Pre-PMF | $0 | Focus on PMF; AEO can wait |
| Early growth | $5k-$15k/quarter | Audit + restructure top 10 pages; visible Q&A blocks; basic tracking |
| Growth | $20k-$50k/quarter | Content production + tracking + competitive analysis |
| Scale | $50k-$200k/quarter | Strategic AEO program + brand-positioning campaigns |
| Category leader | $200k+ | Continuous + dominate citation in category |

---

## Cheat sheet

| Question | Answer |
|----------|--------|
| How often to measure? | Weekly for trend; monthly for strategy |
| How many queries to sample? | 50-200 in your category |
| Which LLMs to track? | All major ones; weight per audience usage |
| Citation count alone meaningful? | Partially; pair with sentiment + share of voice |
| Attribution to specific content? | Hard for ChatGPT/Claude; clearer for Perplexity |
| Manual vs automated tracking? | Automated for scale; manual for sentiment / nuance |
| When to invest in 3rd-party tool? | When sampling > 200 queries per month |
| Most-important single metric? | Citation rate trend over time |
| Biggest measurement risk? | Conflating mention with citation; ignoring sentiment |
