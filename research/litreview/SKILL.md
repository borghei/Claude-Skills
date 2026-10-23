---
name: litreview
description: >
  Literature review for academic and R&D research: search strategy, source
  assessment, synthesis, and citation management. Use when conducting a
  systematic literature review, building a bibliography, or preparing a
  research-grounded report.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: research
  domain: research
  updated: 2026-05-27
  tags: [literature-review, research, citation, synthesis, prisma, academic]
---

# Literature Review

A structured literature-review skill grounded in PRISMA-style protocols
(adapted for non-medical fields), source-assessment frameworks, and
thematic synthesis patterns.

## When to use this skill

- Conducting a **systematic literature review** on a specific question
- Building a **research bibliography** for a paper, report, or grant
- Performing a **scoping review** to map a field
- Auditing an existing review for **gaps, bias, or methodological flaws**
- Synthesizing findings from a **structured set of sources**
- Preparing a **research-grounded section** of a longer report

## Inputs the advisor expects

- Research question(s) — specific, answerable
- Inclusion / exclusion criteria
- Time bound (e.g., past 5 years)
- Geographic / domain bound
- Source types accepted (peer-reviewed, gray literature, conference)
- Existing seed sources (if any)

## Clarify First

Before building the review, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Research question (PICO frame):** makes search and synthesis tractable; vague questions yield unfocused reviews.
- **Review type (systematic, scoping, or narrative):** sets rigor, criteria stringency, and output structure (e.g. whether a PRISMA flow is needed).
- **Inclusion / exclusion criteria (year range, source type, methodology):** drives screening and reproducibility.
- **Synthesis goal (answer a specific question vs map a field):** selects the synthesis approach.

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Workflows

### Workflow 1 — Plan and execute the search

1. Refine the research question (PICO / PEO format works).
2. Run `search_strategy_builder.py` against the question + criteria to
   produce a search strategy (database list, queries, filters).
3. Execute searches; capture results.

```bash
python3 litreview/scripts/search_strategy_builder.py \
  --input question.json --format markdown
```

### Workflow 2 — Score source quality and relevance

1. Capture each source with metadata (authors, date, venue, methodology).
2. Run `source_quality_scorer.py` to grade each on 6 quality dimensions
   + relevance to question.
3. Triage: include / exclude / read-in-full.

```bash
python3 litreview/scripts/source_quality_scorer.py \
  --input sources.json --format markdown
```

### Workflow 3 — Synthesize findings into themes

1. Tag each source with themes + key findings.
2. Run `thematic_synthesis_builder.py` to cluster sources by theme,
   surface evidence strength, identify gaps.

```bash
python3 litreview/scripts/thematic_synthesis_builder.py \
  --input tagged_sources.json --format markdown
```

## Decision frameworks

### Search strategy — the PICO frame
- **P**opulation / problem
- **I**ntervention / phenomenon of interest
- **C**omparator (if relevant)
- **O**utcome

A well-framed question makes search and synthesis tractable.

### Inclusion / exclusion criteria
- Year range
- Language
- Source type (peer-reviewed, gray, conference, preprint)
- Methodology (empirical, theoretical, review)
- Geographic scope
- Quality threshold

Publish criteria up front; apply consistently.

### Source quality dimensions

| Dimension | Question |
|-----------|----------|
| Methodology | Is the method sound? |
| Sample / dataset | Is it adequate for the claim? |
| Peer review | Has it been peer-reviewed? |
| Reproducibility | Is data / code available? |
| Recency | Is it current? |
| Citation impact | Has it been cited / accepted? |

A single sub-dimension is rarely fatal; the combination matters.

### Synthesis approaches

| Approach | When |
|----------|------|
| Narrative synthesis | Heterogeneous sources; explanatory |
| Thematic synthesis | Multiple sources address common themes |
| Meta-analysis | Quantitative, comparable studies |
| Realist synthesis | Complex interventions; context-mechanism-outcome |
| Scoping review | Mapping a field rather than answering specific question |

For most non-clinical fields, **thematic synthesis** is the default.

## Common engagements

### "Help me build the literature review for my paper"
1. Frame the research question (PICO).
2. Define inclusion criteria.
3. Identify search databases / repositories.
4. Execute searches; deduplicate.
5. Screen titles + abstracts; full-text the candidates.
6. Tag and synthesize.
7. Write: gaps, themes, my contribution.

### "Audit my draft literature review"
1. Check the search strategy: reproducible? comprehensive?
2. Check inclusion criteria: applied consistently?
3. Check synthesis: themes substantiated?
4. Check gap identification: real gaps, or convenient?
5. Check citation balance: not over-relying on a single source / group.

### "Map the landscape of [research area]"
1. Conduct a scoping review (different from systematic).
2. Less stringent quality criteria; broader scope.
3. Goal: map the field, not answer specific question.
4. Output: themes, gaps, key authors, key venues.

## Anti-patterns to avoid

- **Search strategy that's "Google Scholar for keywords."** Not reproducible.
- **Inclusion criteria written after seeing results.** Cherry-picking.
- **Synthesizing only confirming sources.** Bias.
- **Citing without reading.** Cite chains repeat errors.
- **No quality scoring.** All sources weighted equally.
- **No gap discussion.** Reader can't see what's not known.
- **Over-reliance on one author / group / venue.** Hidden bias.
- **No PRISMA-style flow diagram (for systematic reviews).** Process opaque.

## Scope & Limitations

**In Scope:**
- Search strategies from a PICO-style question with `search_strategy_builder.py`: Boolean query strings per database, filters and a PRISMA-style log template
- Source scoring on six quality dimensions (methodology, sample, peer review, reproducibility, recency, citation impact) plus relevance with `source_quality_scorer.py`, triaged to include, exclude or read in full
- Theme-by-source evidence tables with `thematic_synthesis_builder.py`, showing well-supported, contested and gap themes
- Guidance on inclusion criteria, PRISMA discipline adapted for non-medical fields, and choosing among narrative, thematic, scoping and other synthesis approaches

**Out of Scope:**
- Running the searches and retrieving full texts. The user executes the queries in each database.
- Meta-analysis statistics and effect-size pooling (see `data-analytics/statistical-analyst/` for general statistics)
- Patent prior-art searching (see `research/patent/`)
- Writing grant proposals that build on the review (see `research/grants/`)

**Important Caveats:**
- The tools have no database access. Source metadata, theme tags and findings are entered by the user, and quality scores are heuristics built from that metadata.
- The output is not a registered systematic review protocol. Pre-registration, dual independent screening and a formal risk-of-bias tool are steps the user must do separately.
- Database syntax and coverage change over time, so generated queries need testing in each database before use.

## References

- `references/search-strategy-and-prisma.md` — search patterns, PRISMA discipline
- `references/source-quality-assessment.md` — quality dimensions, common assessments
- `references/synthesis-and-citation-management.md` — synthesis approaches, citation hygiene

## Related skills

- `research/grants` — grant proposals built on literature
- `research/patent` — IP-focused literature search
- `research/dossier` — intelligence research patterns
- `product-team/research-summarizer` — synthesizing qualitative research
