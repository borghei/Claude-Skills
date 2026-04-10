---
name: legal-red-team
description: >
  Adversarial verification for AI-generated legal content. Use when fact-checking
  legal documents, validating citations, detecting hallucinations, scoring
  document quality, or assessing distribution readiness.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: The Glass Room
  category: legal
  domain: quality-assurance
  updated: 2026-04-10
  tags: [legal-verification, fact-checking, hallucination-detection, quality-scoring, red-team]
---
> **⚠️ EXPERIMENTAL** — This skill is provided for educational and informational purposes only. It does NOT constitute legal advice. All responsibility for usage rests with the user. Consult qualified legal professionals before acting on any output.

# Legal Red Team

Production-ready adversarial verification framework for AI-generated legal content. Covers factual accuracy, citation validation, arithmetic checking, speculation detection, and distribution readiness scoring.

---

## Table of Contents

- [Verification Categories](#verification-categories)
- [Tools](#tools)
- [Six-Step Methodology](#six-step-methodology)
- [Severity Taxonomy](#severity-taxonomy)
- [Quality Score](#quality-score)
- [Known Hallucination Patterns](#known-hallucination-patterns)
- [Reference Guides](#reference-guides)
- [Workflows](#workflows)
- [Troubleshooting](#troubleshooting)
- [Success Criteria](#success-criteria)
- [Scope and Limitations](#scope-and-limitations)
- [Anti-Patterns](#anti-patterns)
- [Tool Reference](#tool-reference)

---

## Verification Categories

Every AI-generated legal document must be checked across 6 categories.

| # | Category | What to Check | Red Flags |
|---|----------|--------------|-----------|
| 1 | **Factual Accuracy** | Dates, references, numbers, entity names, timelines | Wrong effective dates, confused entity names, incorrect amounts |
| 2 | **Legal Authority Citations** | Primary/secondary sources, format, hierarchy, currency | Non-existent articles, wrong section numbers, outdated citations |
| 3 | **Arithmetic Validation** | Timelines, percentages, financial calculations, deadlines | Date math errors, percentage miscalculations, compounding mistakes |
| 4 | **Source Verification** | Verifiable claims, official sources, cross-referencing | Unverifiable assertions stated as fact, single-source claims |
| 5 | **Speculation Detection** | Opinion vs fact, uncertainty language, predictive claims | Predictions stated as certainty, guidance treated as binding law |
| 6 | **Disclaimer Adequacy** | Legal advice disclaimers, jurisdiction, date, professional consultation | Missing disclaimers, overly broad claims, no jurisdiction limits |

---

## Tools

### Legal Fact Checker

Scans legal text for verifiable claims and flags potential hallucination patterns.

```bash
# Check a legal document
python scripts/legal_fact_checker.py --input document.txt

# Check with JSON output
python scripts/legal_fact_checker.py --input memo.txt --json

# Check inline text
python scripts/legal_fact_checker.py --text "Under GDPR Article 83(5), fines can reach EUR 20 million..."

# Save verification report
python scripts/legal_fact_checker.py --input document.txt --output report.json
```

### Legal Quality Scorer

Scores legal document quality across all 6 verification categories.

```bash
# Score a document
python scripts/legal_quality_scorer.py --input document.txt

# Score with JSON output
python scripts/legal_quality_scorer.py --input document.txt --json

# Score with detailed breakdown
python scripts/legal_quality_scorer.py --input document.txt --verbose

# Save quality assessment
python scripts/legal_quality_scorer.py --input document.txt --output assessment.json
```

---

## Six-Step Methodology

### Step 1: Initial Review

Read the entire document with an adversarial mindset. For each claim, ask:

- Is this verifiable?
- Does this sound too specific to be generated without a source?
- Does this sound too confident for an uncertain area?

Mark every factual assertion, citation, date, number, and predictive statement.

### Step 2: Source Verification (ALWAYS Web Search)

For every verifiable claim, attempt to verify against official sources.

| Source Type | Verification Method | Examples |
|-------------|-------------------|---------|
| EU legislation | EUR-Lex official database | eur-lex.europa.eu |
| US federal law | congress.gov, govinfo.gov | Official code and statutes |
| US regulations | eCFR, Federal Register | ecfr.gov |
| UK legislation | legislation.gov.uk | Official statute database |
| Court decisions | Court databases, Westlaw, LexisNexis | Official reporters |
| Agency guidance | Agency official website | Direct download from .gov/.europa.eu |
| International treaties | UN Treaty Collection | treaties.un.org |

**Rule:** If a claim cannot be verified from an official source, flag it. Do not assume accuracy.

### Step 3: Arithmetic Verification

Check every calculation, date computation, and numerical claim.

| Check Type | Method |
|-----------|--------|
| Timeline calculations | Count days/months/years between stated dates |
| Percentage calculations | Recalculate from base figures |
| Financial computations | Verify arithmetic and compounding |
| Deadline calculations | Confirm against statutory text |
| Penalty ranges | Cross-check against statute |

### Step 4: Citation Validation

For every legal citation, verify:

| Element | Check |
|---------|-------|
| Source exists | Does the cited statute/article/section actually exist? |
| Content matches | Does the cited provision say what the document claims? |
| Citation format | Is the citation in correct format for the jurisdiction? |
| Currency | Is this the current, in-force version? |
| Hierarchy correct | Is the source characterized at the right authority level? |

### Step 5: Speculation Identification

Distinguish fact from opinion, certainty from prediction.

| Language Pattern | Classification | Action |
|-----------------|---------------|--------|
| "The law requires..." | Factual claim | Verify against statutory text |
| "Courts will likely..." | Speculation | Flag; add uncertainty qualifier |
| "It is recommended..." | Guidance | Verify source; clarify if binding |
| "Best practice suggests..." | Opinion | Label as opinion; cite source |
| "This means that..." | Interpretation | Flag if stated as fact without authority |
| "Companies must..." | Obligation claim | Verify statutory basis |

### Step 6: Disclaimer Review

Every AI-generated legal document must include:

| Required Element | Description |
|-----------------|-------------|
| Not legal advice | Clear statement that content is informational only |
| Jurisdiction limitations | Which jurisdictions are and are not covered |
| Date of preparation | When the content was prepared (law changes) |
| Professional consultation | Recommendation to consult qualified legal counsel |
| AI-generated disclosure | Statement that content was generated or assisted by AI |
| Accuracy limitations | Acknowledgment that verification is recommended |

---

## Severity Taxonomy

| Severity | Definition | Examples | Action |
|----------|-----------|---------|--------|
| **CRITICAL** | Factually wrong in a way that could cause legal harm | Wrong article number creating false obligation, incorrect penalty amount, non-existent legal requirement | Must fix before any distribution |
| **HIGH** | Materially misleading or unverifiable | Guidance stated as binding law, unverifiable timeline, confident but unsourced claim | Must fix or add prominent caveat |
| **MODERATE** | Imprecise or potentially confusing | Ambiguous language, minor date discrepancy, incomplete citation | Should fix; acceptable with caveat |
| **LOW** | Style or formatting issue | Citation format inconsistency, missing cross-reference, minor redundancy | Fix if time permits |

---

## Quality Score

| Score | Rating | Distribution Status | Criteria |
|-------|--------|-------------------|----------|
| **5/5** | Distribution Ready | Safe to distribute | Zero CRITICAL/HIGH issues; all citations verified; disclaimers complete |
| **4/5** | Minor Revisions | Safe after small fixes | Zero CRITICAL; 1-2 HIGH issues with clear fixes; most citations verified |
| **3/5** | Moderate Revisions | Needs work before distribution | Zero CRITICAL; 3+ HIGH issues; some unverified citations |
| **2/5** | Major Revisions | Not safe to distribute | 1+ CRITICAL issues; multiple HIGH issues; significant unverified content |
| **1/5** | Not Distribution Ready | Requires complete rework | Multiple CRITICAL issues; pervasive inaccuracies; unreliable throughout |

---

## Known Hallucination Patterns

AI models exhibit 5 recurring patterns when generating legal content.

| # | Pattern | Description | Detection Technique |
|---|---------|-------------|-------------------|
| 1 | **Plausible but wrong article numbers** | AI generates article/section numbers that sound correct but do not exist (e.g., "Article 42(5)" when only 42(1)-(4) exist) | Cross-reference every article number against official statute text |
| 2 | **Confident but incorrect dates** | Implementation timelines, effective dates, or deadlines stated with false confidence (off by weeks or months) | Verify every date against official timeline from the statute or implementing body |
| 3 | **Mixing guidance and legal requirements** | Treating non-binding recommendations as binding obligations (e.g., stating ENISA recommendations as NIS2 requirements) | Check whether cited source is binding legislation vs guidance; verify authority level |
| 4 | **Outdated legal references** | Citing superseded or repealed provisions without noting they are no longer in force | Verify currency of every cited provision; check for amendments and repeals |
| 5 | **Arithmetic errors in timeline calculations** | Miscounting days, months, or years between dates; wrong deadline calculations | Independently calculate every timeline; do not trust AI date math |

See `references/hallucination_patterns.md` for detailed examples and prevention strategies.

---

## Reference Guides

| Guide | Path | Description |
|-------|------|-------------|
| Verification Methodology | `references/verification_methodology.md` | Complete 6-step methodology with source hierarchy and citation formats |
| Hallucination Patterns | `references/hallucination_patterns.md` | 5 patterns with examples, detection, and prevention strategies |

---

## Workflows

### Workflow 1: Full Adversarial Review

1. Run `scripts/legal_fact_checker.py` on the document.
2. Review flagged items and verify each against official sources.
3. Run `scripts/legal_quality_scorer.py` for category scores.
4. For each CRITICAL/HIGH finding, document: the error, the correct information, and the source.
5. Produce a verification report with findings by severity.
6. Assign quality score and distribution readiness assessment.
7. **Validation:** Every verifiable claim checked, score assigned, recommendations provided.

### Workflow 2: Quick Citation Check

1. Run `scripts/legal_fact_checker.py` on the document.
2. Focus on citation extraction results.
3. Verify each extracted citation against official source.
4. Flag any citation that cannot be verified.
5. **Validation:** All citations verified or flagged.

### Workflow 3: Pre-Distribution Gate

1. Run `scripts/legal_quality_scorer.py` on the final document.
2. Review composite score.
3. If score < 4/5, document must not be distributed.
4. If score >= 4/5, verify CRITICAL count is zero.
5. Confirm all disclaimers are present and adequate.
6. **Validation:** Quality score >= 4/5, zero CRITICAL issues, disclaimers complete.

---

## Troubleshooting

| Problem | Likely Cause | Resolution |
|---------|-------------|------------|
| Too many false positives | Regex patterns matching non-legal text | Narrow input to legal content only; use context-aware review |
| Cannot verify citation | Source not freely accessible | Note as "unverifiable from public sources"; do not assume correct |
| AI-generated text has no citations | Content is entirely unsourced | Flag entire document as unverified; score as 2/5 or lower |
| Hallucination pattern detected | AI confabulation of legal details | Replace with verified information from official source |
| Document mixes jurisdictions | No clear jurisdiction scope | Flag as HIGH; recommend splitting by jurisdiction |
| Quality score seems too high | Automated scoring has limits | Always supplement automated scoring with manual review |

---

## Success Criteria

| Criterion | Target |
|-----------|--------|
| Citations verified | 100% of legal citations checked against official sources |
| Hallucination patterns scanned | All 5 known patterns checked |
| Arithmetic validated | Every calculation independently verified |
| Severity assigned | Every finding classified CRITICAL/HIGH/MODERATE/LOW |
| Quality score calculated | Composite score with per-category breakdown |
| Disclaimers verified | All 6 required disclaimer elements present |
| Distribution decision | Clear go/no-go recommendation with rationale |

---

## Scope & Limitations

**In scope:** Verifying factual claims in legal text, validating citations, detecting hallucination patterns, scoring document quality, assessing distribution readiness.

**Out of scope:** Verifying legal conclusions or interpretations, assessing litigation strategy, replacing professional legal review, accessing paid legal databases (Westlaw, LexisNexis).

**Disclaimer:** This skill provides a structured adversarial verification methodology. It catches common AI errors but cannot guarantee complete accuracy. Professional legal review remains essential for high-stakes documents.

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Better Approach |
|-------------|-------------|-----------------|
| Trusting AI-generated citations without verification | AI models routinely generate plausible but non-existent legal citations; unverified citations in distributed documents create serious credibility and legal risk | Verify every citation against official sources; assume wrong until proven right |
| Relying solely on automated checking | Automated tools catch patterns but miss contextual errors, mischaracterizations, and subtle hallucinations | Use automated tools for first pass, then conduct manual review of all flagged items and a sample of unflagged items |
| Skipping the "adversarial mindset" | Confirmation bias leads reviewers to accept plausible-sounding content; legal text that "sounds right" may still be wrong | Actively seek to disprove every claim; assume error until verified; question every specific number, date, and citation |
| Distributing with score 3/5 or below | MODERATE and HIGH issues in distributed documents undermine credibility and may cause legal harm | Set a firm distribution threshold at 4/5; no exceptions without documented risk acceptance by a qualified reviewer |

---

## Tool Reference

| Tool | Input | Output | Use Case |
|------|-------|--------|----------|
| `legal_fact_checker.py` | Legal document text | Verification report with flagged claims, citations, dates, hallucination alerts | First-pass automated scanning of legal content |
| `legal_quality_scorer.py` | Legal document text | Quality score (1-5) with per-category breakdown and severity-classified findings | Pre-distribution quality gate |
