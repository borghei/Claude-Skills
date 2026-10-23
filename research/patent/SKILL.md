---
name: patent
description: >
  Patent research and IP landscape: prior-art search, claim mapping, landscape
  analysis, and freedom-to-operate. Use when conducting a prior-art search,
  mapping an IP landscape, evaluating patentability, or running an FTO analysis.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: research
  domain: research
  updated: 2026-05-27
  tags: [patent, ip, prior-art, freedom-to-operate, patentability, claims, landscape]
---

# Patent Research

A research-focused patent skill (not legal filing). Covers prior-art
search, IP landscape mapping, claim analysis, freedom-to-operate, and
patentability. For formal patent prosecution, work with a licensed
patent attorney.

## When to use this skill

- Conducting a **prior-art search** before filing a provisional patent
- Mapping the **IP landscape** in a technology area
- Evaluating the **patentability** of an invention
- Assessing **freedom-to-operate** before launching a product
- Tracking **competitive patent activity** in a market
- Preparing a **patent strategy** for a startup or R&D group

## Inputs the advisor expects

- Invention description (problem, solution, novelty)
- Technology area + relevant CPC/IPC classifications
- Target jurisdictions (US, EU, JP, CN — IP is jurisdictional)
- Existing prior art known (key references)
- Competitor list
- Timeline pressure (filing deadline, product launch)

## Clarify First

Before running the analysis, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Analysis type (prior-art search, patentability, FTO, or landscape):** these are different deliverables with different methods and outputs.
- **Invention description (problem, solution, novelty):** drives the claims and search classifications.
- **Target jurisdictions (US, EU, JP, CN):** IP is jurisdictional; changes FTO scope and filing strategy.
- **Technology area + CPC/IPC classifications:** drives a search beyond keywords (which misses synonyms/translations).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Workflows

### Workflow 1 — Plan a prior-art search

1. Define invention claims (key novel features).
2. Identify search classifications (CPC / IPC) + keywords.
3. Run `prior_art_search_planner.py` to produce a search plan.
4. Execute on USPTO / EPO / Espacenet / Google Patents / WIPO.

```bash
python3 patent/scripts/prior_art_search_planner.py \
  --input invention.json --format markdown
```

### Workflow 2 — Map the IP landscape

1. Capture identified patents (yours, competitors', adjacent).
2. Run `claim_landscape_mapper.py` to cluster by claim type, owner,
   technology subarea, recency; surface white space + crowded areas.

```bash
python3 patent/scripts/claim_landscape_mapper.py \
  --input patents.json --format markdown
```

### Workflow 3 — Score patentability of an invention

1. Capture invention + closest prior art.
2. Run `patentability_scorer.py` to rate novelty, non-obviousness,
   utility, subject matter eligibility.

```bash
python3 patent/scripts/patentability_scorer.py \
  --input patentability.json --format markdown
```

## Decision frameworks

### The three patentability criteria (US baseline)
1. **Novelty** (35 USC §102): not previously disclosed
2. **Non-obviousness** (35 USC §103): not obvious to person skilled in the art
3. **Utility** (35 USC §101): useful, with practical application

Plus:
- **Subject matter eligibility** (§101): not abstract idea, not law of nature
- **Enablement** (§112): described well enough to be made by skilled artisan
- **Definiteness** (§112): claims clearly distinguish

### Prior-art categories
- **Patents** (issued + published applications)
- **Non-patent literature** (papers, conference, dissertations, technical reports)
- **Commercial products** (sold publicly before filing)
- **Public disclosures** (talks, demos, blog posts — yes, including your own > 1 year prior)
- **Sales activity** (offers for sale, even pre-launch)

Inventors often miss non-patent prior art; this is where searches break.

### Freedom-to-operate (FTO)
Different from patentability. FTO asks: can I commercialize without
infringing someone else's patent?

- Patentability ≠ FTO (your patent could still infringe another)
- FTO is jurisdiction-specific
- Active patents only (not expired); typically 20 years from filing
- Patent attorney involvement essential for formal opinion

### IP strategy by stage
- **Pre-seed:** capture inventions; consider provisional filings; don't over-file
- **Seed/Series A:** strategic provisionals; key utility filings
- **Series B+:** PCT international; continuations to maintain pendency
- **Mature:** portfolio management; licensing; enforcement

## Common engagements

### "We have a new algorithm. Should we patent?"
1. Subject matter eligibility check (§101 — algorithms are tricky)
2. Prior art search (someone has probably published)
3. Strategic value (does patent enable / defend a business position?)
4. Cost-benefit ($5-25K provisional; $30-100K full prosecution)
5. Often answer: keep as trade secret, not patent

### "Run an FTO before our launch"
1. Identify candidate blocking patents (search + competitor review)
2. For each: review claims; assess infringement risk
3. Identify mitigations: design-around, license, abandon, challenge
4. Get formal opinion from patent counsel (insurance against willful infringement)

### "Map the patent landscape in our space"
1. Identify key players (companies + universities)
2. Search by classification + keyword
3. Cluster: by company, by sub-technology, by year
4. Surface white space (uncovered areas) + crowded zones
5. Strategy implications (where to play, where to design-around)

## Anti-patterns to avoid

- **Searching only keywords (no classification).** Misses translations + synonyms.
- **Searching only USPTO.** EPO + WIPO + JP have unique art.
- **Searching only patents.** Non-patent prior art is huge.
- **Public disclosure before filing.** Loses patentability outside US (1-year grace in US only).
- **Filing without prior-art search.** Reviewer finds it; patent invalid.
- **No FTO before product launch.** Surprise injunctions.
- **Patenting everything.** $30K per patent adds up; portfolio bloat distracts.
- **Filing without commercial strategy.** Patents are means, not ends.

## Scope & Limitations

**In Scope:**
- Prior-art search plans from claim elements, keywords, CPC/IPC classifications and jurisdictions with `prior_art_search_planner.py`: database list, query strings and a search log template
- IP landscape maps with `claim_landscape_mapper.py`, clustering patents by owner, technology subarea, recency and claim type to show white space and crowded areas
- Patentability scoring on novelty, non-obviousness, utility, subject matter eligibility and enablement with `patentability_scorer.py`
- Background on patentability criteria, prior-art categories, freedom-to-operate concepts and IP strategy by company stage

**Out of Scope:**
- Drafting, filing or prosecuting patent applications
- Formal freedom-to-operate, infringement or validity opinions. These need a licensed patent attorney.
- IP licensing agreements (see `legal/contract-review/`)
- Strategic IP counsel at company level (see `c-level-advisor/general-counsel-advisor/`)
- Trademarks and copyright

**Important Caveats:**
- The tools do not query USPTO, EPO, WIPO or any patent database. Patents, prior art and the inventor's judgments, such as whether the invention would be obvious, are entered by the user.
- The patentability criteria use a US baseline. Other jurisdictions differ, for example on grace periods for public disclosure.
- No output is a patentability or freedom-to-operate opinion. Patent status, ownership and legal status change, so a landscape is only current on the day it is built.

## References

- `references/prior-art-search-strategy.md` — search databases, classifications, query patterns
- `references/claim-mapping-and-landscape.md` — claim analysis, landscape visualization
- `references/freedom-to-operate-and-patentability.md` — FTO process, patentability criteria

## Related skills

- `legal/contract-review` — IP licensing contracts
- `c-level-advisor/general-counsel-advisor` — strategic IP counsel
- `research/litreview` — non-patent literature search overlap
