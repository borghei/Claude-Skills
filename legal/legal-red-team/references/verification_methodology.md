# Verification Methodology Reference

Complete adversarial verification framework for AI-generated legal content. Covers the 6-step methodology, source hierarchy, citation validation procedures, and verification statistics.

---

## Table of Contents

- [Adversarial Mindset Principles](#adversarial-mindset-principles)
- [Six-Step Verification Methodology](#six-step-verification-methodology)
- [Source Hierarchy for Legal Verification](#source-hierarchy-for-legal-verification)
- [Citation Validation Procedures](#citation-validation-procedures)
- [Cross-Referencing Techniques](#cross-referencing-techniques)
- [Verification Statistics Tracking](#verification-statistics-tracking)
- [Common Verification Failures](#common-verification-failures)

---

## Adversarial Mindset Principles

The core principle: **assume error until proven correct.** AI-generated legal content is inherently unreliable until verified.

| Principle | Description |
|-----------|-------------|
| Assume error | Every factual claim, citation, date, and number is wrong until you verify it |
| Seek contradictory evidence | Do not just confirm -- actively try to disprove claims |
| Question every number | Dates, amounts, percentages, and article numbers are the highest-risk elements |
| Demand sources | Any claim without a verifiable source is suspect |
| Test logical consistency | Do the claims in the document make sense together? Do timelines add up? |
| Beware of confidence | AI models are most dangerous when they sound most certain |
| Check the obvious | The most basic facts (names, dates, locations) are often where errors hide |

---

## Six-Step Verification Methodology

### Step 1: Initial Review

**Goal:** Identify all verifiable claims in the document.

| Element to Identify | What to Mark |
|---------------------|-------------|
| Legal citations | Article numbers, section references, regulation names |
| Dates | Effective dates, deadlines, implementation timelines |
| Numbers | Monetary amounts, percentages, thresholds, penalties |
| Entity names | Organizations, agencies, courts, legislative bodies |
| Factual assertions | "The law requires...", "Companies must...", "The regulation provides..." |
| Predictive claims | "Courts will likely...", "It is expected that..." |
| Source attributions | "According to [source]...", "As stated by [authority]..." |

**Output:** A marked-up document with every verifiable element highlighted and categorized.

### Step 2: Source Verification (ALWAYS Web Search)

**Goal:** Verify every factual claim against official sources.

**Mandatory rule:** Always attempt to verify from the official source. Do not rely on the AI's own confidence or on secondary summaries.

| Verification Target | Primary Source | Secondary Source |
|--------------------|---------------|-----------------|
| EU legislation text | EUR-Lex (eur-lex.europa.eu) | National transposition databases |
| EU implementation dates | Official Journal of the EU | European Commission website |
| US federal statute text | United States Code (uscode.house.gov) | Cornell LII (law.cornell.edu) |
| US federal regulation text | eCFR (ecfr.gov) | Federal Register (federalregister.gov) |
| UK legislation text | legislation.gov.uk | Explanatory notes |
| Court decisions | Official reporters, court websites | Westlaw, LexisNexis |
| Agency guidance | Agency official website (.gov, .europa.eu) | Published FAQs and guidance documents |
| International treaties | UN Treaty Collection | Government treaty databases |
| Penalty amounts | Statutory text (primary source) | Enforcement action press releases |
| Organizational facts | Organization's official website | Official filings and reports |

**Process for each claim:**
1. Identify the claim and its source attribution.
2. Locate the official source.
3. Read the relevant provision directly.
4. Compare the claim to the source text.
5. Record: Verified / Incorrect / Unverifiable / Partially Correct.
6. If incorrect, note the correct information and the source.

### Step 3: Arithmetic Verification

**Goal:** Independently verify every calculation.

| Calculation Type | Verification Method |
|-----------------|-------------------|
| Timeline (days/months) | Count manually from start date to end date |
| Percentage of revenue | Recalculate from stated base figures |
| Fine ranges | Cross-reference against statutory text |
| Deadline calculations | Verify using the statute's own counting rules |
| Compounding | Recalculate step by step |
| Currency conversions | Use the date-specific exchange rate |

**Common arithmetic errors in AI content:**

| Error Type | Example |
|-----------|---------|
| Off-by-one in month counting | "18 months from May 2025" stated as "November 2026" (should be November 2026 -- correct, but check carefully) |
| Wrong year in multi-year timeline | "3 years from 2024" stated as "2026" (should be 2027) |
| Percentage miscalculation | "4% of EUR 50 billion" stated as "EUR 200 million" (should be EUR 2 billion) |
| Mixing financial year and calendar year | Revenue calculated on wrong period |
| Inconsistent rounding | Numbers don't add up due to premature rounding |

### Step 4: Citation Validation

**Goal:** Verify every legal citation exists and says what the document claims.

| Validation Step | Check |
|----------------|-------|
| 1. Citation format | Is the citation in the correct format for its jurisdiction? |
| 2. Source exists | Does the cited statute, article, or section actually exist? |
| 3. Content accuracy | Does the cited provision say what the document claims? |
| 4. Currency | Is this the current, in-force version? Has it been amended or repealed? |
| 5. Authority level | Is the source characterized at the correct level (binding vs guidance)? |
| 6. Jurisdiction match | Does the citation apply to the jurisdiction discussed? |

### Step 5: Speculation Identification

**Goal:** Distinguish fact from opinion, certainty from prediction.

| Category | Language Signals | Appropriate? |
|----------|-----------------|-------------|
| Fact | "The regulation requires..." | Yes, if verified |
| Qualified interpretation | "This likely means..." | Yes, if properly qualified |
| Prediction | "Courts will probably hold..." | Acceptable if clearly marked as prediction |
| Unqualified prediction | "This will be enforced starting..." | Not acceptable -- must add qualifier |
| Opinion stated as fact | "Companies must [non-statutory obligation]" | Not acceptable -- reframe or cite source |
| Guidance stated as law | "EDPB requires..." | Not acceptable -- clarify as guidance |

### Step 6: Disclaimer Review

**Goal:** Verify all required disclaimers are present and adequate.

| Required Disclaimer | Minimum Content |
|--------------------|----------------|
| Not legal advice | "This document does not constitute legal advice and should not be relied upon as such." |
| Jurisdiction limitations | "This analysis covers [specific jurisdictions]. Laws may differ in other jurisdictions." |
| Date of preparation | "Current as of [date]. Laws and regulations may have changed since this date." |
| Professional consultation | "Consult qualified legal counsel for advice specific to your circumstances." |
| AI-generated disclosure | "This document was generated/assisted by artificial intelligence." |
| Accuracy limitations | "While efforts have been made to ensure accuracy, independent verification is recommended." |

---

## Source Hierarchy for Legal Verification

### Tier 1: Primary Legislation (Highest Authority)

| Source Type | Examples | Verification Status |
|------------|---------|-------------------|
| Constitution | US Constitution, EU Treaties | Definitive |
| Statutes | GDPR, AI Act, CCPA, Clean Air Act | Definitive when from official source |
| Regulations | CFR, EU implementing regulations | Definitive when from official source |

### Tier 2: Official Interpretive Sources

| Source Type | Examples | Verification Status |
|------------|---------|-------------------|
| Court decisions | Supreme Court, CJEU, High Court | Binding within jurisdiction |
| Agency decisions | FTC enforcement actions, DPA decisions | Authoritative within scope |

### Tier 3: Authoritative Guidance

| Source Type | Examples | Verification Status |
|------------|---------|-------------------|
| Agency guidance | EDPB guidelines, ICO guidance, FTC guidance | Persuasive; not binding |
| Implementing standards | ISO standards, NIST frameworks | Reference standards; not law |
| Official FAQs | European Commission FAQs, agency FAQs | Informative; can change |

### Tier 4: Secondary Sources

| Source Type | Examples | Verification Status |
|------------|---------|-------------------|
| Legal treatises | Practitioner texts, annotated codes | Scholarly; not authoritative |
| Law review articles | Academic legal journals | Scholarly; not authoritative |
| Legal news | Law firm alerts, legal publications | Informational; verify underlying claims |

### Tier 5: Informal Sources (Lowest Reliability)

| Source Type | Examples | Verification Status |
|------------|---------|-------------------|
| Blog posts | Law firm blogs, tech blogs | May contain errors; never cite as authority |
| News articles | General media coverage of legal topics | Frequently inaccurate on legal details |
| Social media | LinkedIn posts, Twitter/X threads | Unreliable; never cite |
| AI-generated summaries | ChatGPT, Gemini, Claude outputs | Must be independently verified |

---

## Citation Validation Procedures

### Bluebook (US) Citation Format

| Element | Format | Example |
|---------|--------|---------|
| US Code | [Title] U.S.C. § [Section] | 15 U.S.C. § 7702 |
| CFR | [Title] C.F.R. § [Section] | 16 C.F.R. § 312.2 |
| Federal statute (session) | Pub. L. No. [Number], § [Section], [Statutes] | Pub. L. No. 117-328, § 101 |
| Court case | [Party] v. [Party], [Volume] [Reporter] [Page] ([Year]) | Brown v. Board, 347 U.S. 483 (1954) |

### EU Citation Format

| Element | Format | Example |
|---------|--------|---------|
| Regulation | Regulation (EU) [Year]/[Number] | Regulation (EU) 2016/679 |
| Directive | Directive (EU) [Year]/[Number] | Directive (EU) 2022/2555 |
| Article reference | Article [N]([paragraph])([letter]) | Article 83(5)(a) |
| CJEU case | Case C-[Number]/[Year] | Case C-311/18 (Schrems II) |

### OSCOLA (UK) Citation Format

| Element | Format | Example |
|---------|--------|---------|
| UK statute | [Short Title] [Year], s [Section] | Data Protection Act 2018, s 3 |
| SI | [Title] [Year] (SI [Year]/[Number]) | The GDPR (SI 2019/419) |
| Case | [Party] v [Party] [[Year]] [Court] [Number] | [2019] UKSC 22 |

---

## Cross-Referencing Techniques

### Triangulation

Verify claims using at least 2 independent sources.

| Method | Description |
|--------|-------------|
| Source triangulation | Verify the same fact from 2+ independent sources |
| Method triangulation | Use different verification methods for the same claim |
| Temporal triangulation | Check if the claim was true at the stated date (not just currently) |

### Consistency Checking

| Check | Method |
|-------|--------|
| Internal consistency | Do claims within the document contradict each other? |
| External consistency | Do claims match what other authoritative sources say? |
| Logical consistency | Do the conclusions follow from the premises? |
| Mathematical consistency | Do the numbers add up across the document? |

---

## Verification Statistics Tracking

Track verification results for quality assessment.

| Metric | How to Calculate |
|--------|-----------------|
| Verification rate | Claims verified / Total claims identified |
| Accuracy rate | Claims verified correct / Claims verified |
| Citation accuracy | Citations confirmed / Citations checked |
| Date accuracy | Dates confirmed / Dates checked |
| Hallucination rate | Hallucinations found / Total claims |
| Severity distribution | Count of CRITICAL / HIGH / MODERATE / LOW findings |

### Sample Verification Log

| # | Claim | Category | Source Checked | Result | Severity |
|---|-------|----------|---------------|--------|----------|
| 1 | "GDPR Art. 83(5) fines up to EUR 20M" | Citation | EUR-Lex | Verified | -- |
| 2 | "AI Act applies from August 2026" | Date | EUR-Lex | Partially correct (phased) | MODERATE |
| 3 | "ENISA requires annual testing" | Authority | ENISA website | Incorrect (guidance, not requirement) | HIGH |

---

## Common Verification Failures

| Failure Mode | Why It Happens | Prevention |
|-------------|---------------|------------|
| Trusting AI confidence | Model sounds certain, so reviewer assumes correctness | Always verify regardless of AI's confidence level |
| Checking only flagged items | Automated tools miss contextual errors | Manually review a random sample of unflagged claims |
| Verifying against another AI | Using one AI to fact-check another | Always verify against official, non-AI sources |
| Stopping at first confirmation | Found one source supporting the claim; stopped looking | Check at least 2 independent sources for important claims |
| Ignoring absence of evidence | Could not find supporting source; assumed claim is too obscure | If you cannot verify it, flag it as unverified |
| Time pressure shortcuts | Deadline pressure reduces verification thoroughness | Budget adequate time; prioritize CRITICAL items if time is limited |
