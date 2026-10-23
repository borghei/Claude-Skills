---
name: dossier
description: >
  Structured intelligence dossiers on companies, people, markets, or domains,
  with source triangulation and fact/inference discipline. Use when preparing a
  deal-prep dossier, executive briefing, or due-diligence overview.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: research
  domain: research
  updated: 2026-05-27
  tags: [dossier, intelligence, due-diligence, market-entry, briefing, research]
---

# Intelligence Dossier

A research skill for producing structured intelligence dossiers — the
kind of document a CEO reads before a meeting, a PM reads before
market-entry, or an investor reads before due diligence.

## When to use this skill

- **Deal-prep dossier** before a major partnership / acquisition meeting
- **Executive briefing** ahead of a board, customer, or regulator meeting
- **Market-entry analysis** for a new geography or vertical
- **Due-diligence overview** for investment or M&A consideration
- **Competitor profile** in depth
- **Person dossier** ahead of executive recruiting or board engagement

## Inputs the advisor expects

- Subject (company / person / market / domain)
- Purpose (deal-prep, due diligence, briefing — affects depth + emphasis)
- Audience (exec, board, working team)
- Timeline / deadline
- Known starting sources
- Sensitive areas to dig into

## Clarify First

Before building the dossier, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Subject + subject type (company / person / market):** selects the outline template and which sections apply.
- **Purpose (deal-prep, due diligence, briefing, market-entry):** drives depth, emphasis, and the Implications section.
- **Audience (exec, board, working team):** sets altitude and length of the executive summary.
- **Key decision or risk to inform:** drives the Risks + Open Questions and Recommendations sections.

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Workflows

### Workflow 1 — Generate dossier outline

1. Specify subject type + purpose.
2. Run `dossier_outline_generator.py` to produce a structured outline
   tailored to subject + purpose.
3. Assign owners + research targets per section.

```bash
python3 dossier/scripts/dossier_outline_generator.py \
  --subject-type company --purpose deal-prep --format markdown
```

### Workflow 2 — Validate source triangulation

1. Capture claims with supporting sources.
2. Run `source_triangulation_validator.py` to check each claim has
   multiple independent supporting sources + source reliability.
3. Flag thinly-sourced claims for additional research.

```bash
python3 dossier/scripts/source_triangulation_validator.py \
  --input claims_with_sources.json --format markdown
```

### Workflow 3 — Separate facts from inferences

1. Capture dossier statements.
2. Run `fact_inference_separator.py` to classify each statement and
   flag unsupported inferences.

```bash
python3 dossier/scripts/fact_inference_separator.py \
  --input dossier_statements.json --format markdown
```

## Decision frameworks

### The dossier hierarchy

A useful structure for any dossier:

1. **Executive summary** (1 page, lead with takeaway)
2. **Subject overview** (facts: what they are)
3. **Context** (market, history, environment)
4. **Capabilities + assets** (what they can do)
5. **People + leadership** (who runs it)
6. **Performance + trajectory** (numbers, trends)
7. **Relationships + ecosystem** (who they're with)
8. **Risks + open questions** (what we don't know)
9. **Implications + recommendations** (so what)
10. **Sources + methodology** (how we know)

## Fact vs inference discipline

Three categories per statement:

| Category | Definition | Example |
|----------|------------|---------|
| **Fact** | Verifiable, sourced | "Founded 2018; HQ in Chicago" |
| **Inference** | Reasoned from facts | "Likely targeting enterprise segment based on hiring pattern" |
| **Speculation** | No supporting evidence | "Might pivot to AI next year" |

A trustworthy dossier separates these clearly. Mixing them = loss of credibility.

### Source reliability scoring (Admiralty Code adapted)

| Reliability | Code | Description |
|-------------|------|-------------|
| Completely reliable | A | Established, history of completely reliable info |
| Usually reliable | B | History of mostly reliable info |
| Fairly reliable | C | History of reliable info with notable errors |
| Not usually reliable | D | Limited history; mixed accuracy |
| Unreliable | E | Known for inaccurate info |
| Cannot be judged | F | New / unknown source |

| Information credibility | Code | Description |
|--------------------------|------|-------------|
| Confirmed | 1 | Confirmed by other independent sources |
| Probably true | 2 | Not confirmed; consistent with other info |
| Possibly true | 3 | Not confirmed; reasonable but unsupported |
| Doubtful | 4 | Inconsistent with other info |
| Improbable | 5 | Contradicted by other info |
| Cannot be judged | 6 | New info; no validation possible |

A "B-2" rated claim is "usually reliable source, probably true" — workable. An "F-6" claim is "unknown source, unverified" — barely worth including.

### Triangulation principle

For each significant claim:
- **1 source:** anecdotal; flag explicitly
- **2 independent sources:** workable (most dossier claims should reach this)
- **3+ independent sources:** confirmed; safe to assert

"Independent" means not derived from the same underlying source. Two news
articles citing the same press release ≠ 2 independent sources.

## Common engagements

### "Build a dossier on company X before our acquisition meeting"
1. Run outline generator (subject=company, purpose=deal-prep).
2. Pull: financials, leadership, products, customers, IP, tech stack,
   regulatory posture.
3. Identify red flags: undisclosed litigation, key person dependencies,
   customer concentration, regulatory risk.
4. Recommendations: questions to ask in meeting; deal structure implications.

### "Executive briefing for senator's office meeting"
1. Run outline (subject=person/organization, purpose=briefing).
2. Pull: voting record, recent statements, committee assignments,
   donor profile, alignment with our position.
3. Anticipate likely questions; prepare positions.

### "Market-entry analysis for [country]"
1. Run outline (subject=market, purpose=market-entry).
2. Pull: market size, growth, competitive landscape, regulatory,
   distribution, cultural / business norms, talent.
3. Compare entry options (direct, partner, acquisition).

## Anti-patterns to avoid

- **Mixing facts + inferences without labels.** Reader can't calibrate trust.
- **Single-source claims presented as confirmed.** Anecdote dressed as data.
- **Unsourced "everyone knows" claims.** Often turn out wrong.
- **Padding with low-relevance facts.** Bloated dossier loses signal.
- **Burying risks at the end.** Risks should be surfaced upfront.
- **No update mechanism.** Stale dossier on important subject = bad decisions.
- **Adversarial language about subject.** Bias erodes credibility.

## Scope & Limitations

**In Scope:**
- Dossier outlines tailored to subject type (company, person, market) and purpose (deal-prep, due diligence, briefing, market entry) with `dossier_outline_generator.py`
- Source triangulation checks with `source_triangulation_validator.py`: single-source claims, low-reliability sources and sources that are not independent
- Fact, inference and speculation labelling with `fact_inference_separator.py`, flagging unsupported inferences and over-confident speculation
- The ten-part dossier hierarchy and source rating with an adapted Admiralty Code

**Out of Scope:**
- Collecting the information. The skill structures and checks research the user gathers.
- Academic literature search (see `research/litreview/`)
- Legal due diligence and legal risk opinions (see `c-level-advisor/general-counsel-advisor/`)
- Competitor teardowns for positioning and sales use (see `business-growth/competitive-teardown/`)

**Important Caveats:**
- The tools do not search the web or any database. Claims, sources, reliability codes and independence links are all entered by the user.
- Source independence is only as accurate as the `independent_from` links supplied. Two articles that repeat one press release count as independent unless the user marks them.
- Classification of statements uses the declared category, the evidence attached and wording patterns. It is a check, not a verification of the facts.
- A dossier is a snapshot. Facts about companies, people and markets go stale and need a set review date.

## References

- `references/dossier-frameworks-and-structure.md` — outline patterns per subject type
- `references/source-triangulation-and-reliability.md` — source assessment, triangulation
- `references/fact-vs-inference-discipline.md` — categorization + writing patterns

## Related skills

- `research/litreview` — academic literature search
- `c-level-advisor/ceo-advisor` — strategic briefing patterns
- `c-level-advisor/general-counsel-advisor` — legal due diligence overlap
- `business-growth/competitive-teardown` — competitive intel angle
- `business-growth/customer-success-manager` — account research patterns
