# AI Hallucination Patterns in Legal Content

5 known hallucination patterns with descriptions, real-world examples, detection techniques, and prevention strategies. Plus quality score rubric and adversarial review principles.

---

## Table of Contents

- [Overview](#overview)
- [Pattern 1: Plausible but Wrong Article Numbers](#pattern-1-plausible-but-wrong-article-numbers)
- [Pattern 2: Confident but Incorrect Dates](#pattern-2-confident-but-incorrect-dates)
- [Pattern 3: Mixing Guidance and Legal Requirements](#pattern-3-mixing-guidance-and-legal-requirements)
- [Pattern 4: Outdated Legal References](#pattern-4-outdated-legal-references)
- [Pattern 5: Arithmetic Errors in Timeline Calculations](#pattern-5-arithmetic-errors-in-timeline-calculations)
- [Detection Quick Reference](#detection-quick-reference)
- [Quality Score Rubric](#quality-score-rubric)
- [Adversarial Review Principles](#adversarial-review-principles)

---

## Overview

AI language models generate legal content that sounds authoritative but frequently contains errors that could mislead readers or cause legal harm. These errors follow predictable patterns.

| Pattern | Severity | Frequency | Detection Difficulty |
|---------|----------|-----------|---------------------|
| Wrong article numbers | CRITICAL | High | Medium -- requires source checking |
| Incorrect dates | HIGH | High | Medium -- requires calendar verification |
| Guidance as law | HIGH | Very High | Hard -- requires understanding authority hierarchy |
| Outdated references | HIGH | Medium | Medium -- requires currency checking |
| Timeline arithmetic | MODERATE | High | Easy -- requires basic math |

**Why these patterns occur:**
- AI models are trained on large text corpora that include outdated, incorrect, and informal legal content.
- Models generate plausible-sounding text by statistical pattern matching, not by reasoning from source material.
- Legal content requires precision that exceeds what statistical text generation can reliably produce.
- Models cannot verify their own outputs against current, authoritative sources.

---

## Pattern 1: Plausible but Wrong Article Numbers

### Description

AI models generate article, section, or paragraph numbers that sound correct for the statute being discussed but do not actually exist or refer to a different topic than claimed.

### Why It Happens

Models learn that certain statutes have articles in certain ranges and that specific topics appear at specific article numbers. They generate numbers that fit the statistical pattern but are not always correct.

### Examples

| AI-Generated Claim | Actual Reality | Error Type |
|-------------------|---------------|------------|
| "AI Act Article 42(5) requires..." | Article 42 has only paragraphs (1)-(4) | Non-existent subsection |
| "GDPR Article 83(7) provides for..." | Article 83 has only paragraphs (1)-(6) | Non-existent paragraph |
| "Under NIS2 Article 35..." | NIS2 has 46 articles; Art. 35 exists but covers a different topic | Wrong topic attribution |
| "DORA Article 55(3)(b)..." | Article 55 does not have a paragraph 3(b) | Fabricated sub-reference |
| "Section 1798.150(a)(1)(B) of the CCPA..." | Subsection structure is different | Wrong internal structure |

### Detection Techniques

1. **Cross-reference every article number** against the official statute text.
2. **Check maximum article/section number** for the statute (e.g., GDPR has 99 articles; any reference above 99 is immediately wrong).
3. **Verify internal structure** (paragraph numbers, subsections, letters).
4. **Confirm topic match** -- even if the article number exists, verify it covers the topic claimed.
5. **Be especially suspicious of high subsection numbers** (e.g., paragraph (7) or higher is uncommon).

### Prevention Strategies

- Always provide article text directly from the official source when drafting.
- Cross-reference every article number before including it in output.
- When uncertain about a specific subsection, cite the article broadly rather than fabricating precision.
- Use EUR-Lex, govinfo.gov, or other official databases for real-time verification.

---

## Pattern 2: Confident but Incorrect Dates

### Description

AI models state implementation timelines, effective dates, and compliance deadlines with false confidence. Dates are typically close to correct but off by weeks, months, or occasionally years.

### Why It Happens

Training data contains multiple draft versions, proposals, and commentary that discuss various proposed dates. Models conflate proposed dates with final dates, or confuse entry-into-force with application dates.

### Examples

| AI-Generated Claim | Actual Reality | Error |
|-------------------|---------------|-------|
| "The AI Act applies from August 1, 2026" | Phased application: prohibited practices Feb 2025, high-risk Aug 2026, other provisions Aug 2027 | Oversimplified; missed phased timeline |
| "GDPR entered into force on May 25, 2018" | Entered into force May 24, 2016; became applicable May 25, 2018 | Confused entry-into-force with application date |
| "NIS2 transposition deadline is October 2024" | Transposition deadline is October 17, 2024 | Imprecise (missing day) |
| "DORA applies from January 2025" | DORA applies from January 17, 2025 | Imprecise (missing day) |
| "CCPA was enacted in 2019" | Signed into law June 28, 2018; effective January 1, 2020 | Wrong year for both enactment and effectiveness |

### Detection Techniques

1. **Verify every date** against the official source (Official Journal, government gazette).
2. **Check for phased timelines** -- most modern legislation has multiple application dates.
3. **Distinguish entry-into-force from application date** (EU law routinely has a 2-year gap).
4. **Verify the specific day**, not just month and year.
5. **Cross-reference timeline with official implementation guidance** from the relevant authority.

### Prevention Strategies

- Always cite the specific article that establishes the timeline (e.g., "Article 113 of the AI Act").
- Present phased timelines as tables, not single dates.
- When uncertain about a specific date, state the uncertainty: "approximately" or "subject to verification."
- Maintain a reference table of verified key dates for frequently discussed statutes.

---

## Pattern 3: Mixing Guidance and Legal Requirements

### Description

AI models frequently treat non-binding guidance, recommendations, and best practices as if they were binding legal requirements. This is one of the most common and dangerous hallucination patterns.

### Why It Happens

Training data often discusses guidance and legislation together without clearly distinguishing authority levels. Models generate text that conflates "ENISA recommends" with "NIS2 requires" or "EDPB guidance states" with "GDPR mandates."

### Examples

| AI-Generated Claim | Actual Reality | Error |
|-------------------|---------------|-------|
| "ENISA requires organizations to conduct annual penetration testing" | ENISA publishes guidance; NIS2 Art. 21 requires risk management measures but does not mandate annual pen testing | Guidance presented as statutory requirement |
| "The EDPB mandates that consent pop-ups must include a reject button of equal size" | EDPB issues guidelines; specific UI requirements may come from national DPA enforcement | Advisory guidance stated as mandate |
| "NIST CSF requires organizations to maintain an asset inventory" | NIST CSF is a voluntary framework; it recommends, not requires | Voluntary framework stated as requirement |
| "The ICO requires a DPIA for all AI systems" | ICO provides guidance on when DPIAs are needed; GDPR Art. 35 sets the legal threshold | Guidance-level interpretation stated as rule |
| "ISO 27001 legally requires annual management reviews" | ISO 27001 is a voluntary standard; management reviews are a certification requirement, not a legal requirement | Standard requirement conflated with legal obligation |

### Detection Techniques

1. **Check the source type:** Is the cited source a statute/regulation (binding) or guidance/recommendation (non-binding)?
2. **Verify the verb:** Does the source actually "require" or does it "recommend/suggest/encourage"?
3. **Check the authority chain:** Does the guidance body have rule-making authority, or only advisory authority?
4. **Look for conditional language:** Guidance often uses "should" while law uses "shall/must."
5. **Verify the enforcement mechanism:** Non-binding guidance typically has no enforcement mechanism.

### Authority Level Quick Reference

| Source Type | Binding? | Examples |
|------------|----------|---------|
| Statute/Regulation | Yes | GDPR, AI Act, CCPA, NIS2, DORA |
| Delegated/Implementing act | Yes | Commission implementing regulations |
| Agency rule (US) | Yes (after notice and comment) | FTC rules, SEC rules |
| Court decision | Yes (within jurisdiction) | CJEU rulings, Supreme Court decisions |
| Agency guidance | No | EDPB guidelines, ICO guidance, CNIL guides |
| International standard | No (unless mandated by statute) | ISO 27001, NIST CSF |
| Industry body recommendation | No | ENISA reports, CIS benchmarks |

### Prevention Strategies

- Always verify whether the cited source has binding legal authority.
- Use precise language: "EDPB recommends..." not "EDPB requires..."
- Clearly distinguish statutory requirements from guidance-level best practices.
- When guidance informs compliance, state: "While not legally binding, [guidance body] recommends..."

---

## Pattern 4: Outdated Legal References

### Description

AI models cite provisions that have been repealed, superseded, or substantially amended. The model's training data includes historical versions of laws that are no longer in force.

### Why It Happens

Training corpora contain legal texts from many time periods. Models may cite the Data Protection Directive (95/46/EC) rather than GDPR, or reference pre-amendment versions of statutes.

### Examples

| AI-Generated Claim | Actual Reality | Error |
|-------------------|---------------|-------|
| "Under the Data Protection Directive 95/46/EC, Article 25..." | Directive 95/46/EC was repealed and replaced by GDPR in 2018 | Citing repealed legislation |
| "The Safe Harbor framework governs EU-US data transfers" | Safe Harbor was invalidated by Schrems I (2015); replaced by Privacy Shield, then by the EU-US Data Privacy Framework | Citing invalidated framework |
| "Under the FDA's Quality System Regulation (21 CFR 820)..." | QSR is being replaced by QMSR aligned with ISO 13485 | Citing regulation under active replacement |
| "PCI-DSS 3.2.1 requires..." | PCI-DSS 4.0 was released in 2022 with transition period | Citing superseded version |
| "Under the pre-amendment CCPA..." | CPRA amendments are in effect as of January 2023 | Citing pre-amendment version |

### Detection Techniques

1. **Check the date of the cited instrument.** Older instruments are more likely to be superseded.
2. **Search for "repealed by" or "amended by"** on the official source.
3. **Verify on the official database** (EUR-Lex shows consolidated versions with amendment history).
4. **Check for successor instruments** -- most repeals come with replacement legislation.
5. **Verify version numbers** for standards (ISO, PCI-DSS, NIST).

### Prevention Strategies

- Always verify that the cited provision is current and in force.
- Use consolidated texts from official sources (EUR-Lex, eCFR).
- When citing standards, specify the version number and date.
- Note when a provision is in transition (e.g., "QSR/QMSR transition period").

---

## Pattern 5: Arithmetic Errors in Timeline Calculations

### Description

AI models make mathematical errors when calculating dates, deadlines, and timelines. This includes miscounting days, months, or years, and confusing business days with calendar days.

### Why It Happens

AI models generate text token by token and do not perform actual arithmetic. Date calculations require calendar awareness that models lack. Models approximate rather than calculate.

### Examples

| AI-Generated Claim | Actual Reality | Error |
|-------------------|---------------|-------|
| "72 hours from Friday 5pm is Monday 5pm" | 72 hours from Friday 5pm is Monday 5pm -- correct in this case, but models often get this wrong with holidays | May not account for time zones or holidays |
| "18 months from January 2025 is July 2026" | 18 months from January 2025 is July 2026 -- correct | Verify independently; models often miscalculate |
| "4% of EUR 50 billion is EUR 200 million" | 4% of EUR 50 billion is EUR 2 billion | Order of magnitude error |
| "The deadline is 60 business days from notification" | Statute says "60 days" (calendar days), not business days | Calendar vs business day confusion |
| "3 years from entry into force (2024) means compliance by 2026" | 3 years from 2024 is 2027 | Basic arithmetic error |

### Detection Techniques

1. **Recalculate every timeline independently** using a calendar.
2. **Verify whether the statute specifies calendar days or business days.**
3. **Check for time zone issues** in cross-border timelines.
4. **Verify percentage calculations** by doing the math.
5. **Watch for order-of-magnitude errors** (million vs billion, days vs months).
6. **Cross-reference calculated dates against published official timelines.**

### Prevention Strategies

- Calculate all dates manually and verify against the statutory text.
- Present timelines in table format with start date, rule, and calculated end date.
- Specify whether days are calendar or business days.
- Use specific dates rather than relative calculations when possible.

---

## Detection Quick Reference

| What to Check | How to Check | Tool |
|--------------|-------------|------|
| Article numbers | Cross-reference against official statute | EUR-Lex, eCFR, official code |
| Dates | Verify against Official Journal or statute text | Official gazette database |
| Authority level | Confirm binding vs advisory status | Check source type and issuing body |
| Currency of law | Check for amendments and repeals | Consolidated text databases |
| Arithmetic | Recalculate independently | Calculator, calendar |
| Entity names | Verify official name and jurisdiction | Organization's official website |
| Penalty amounts | Cross-reference against penalty provision | Statutory text |

---

## Quality Score Rubric

| Score | Rating | Criteria |
|-------|--------|---------|
| **5/5** | Distribution Ready | Zero CRITICAL or HIGH findings. All citations verified against official sources. All dates confirmed. All arithmetic checked. Complete disclaimers. Speculation properly qualified. Suitable for client distribution. |
| **4/5** | Minor Revisions | Zero CRITICAL findings. Maximum 1-2 HIGH findings with clear, simple fixes. Most citations verified. Minor imprecisions in dates or numbers. Adequate disclaimers. Safe to distribute after targeted corrections. |
| **3/5** | Moderate Revisions | Zero CRITICAL findings. 3-5 HIGH findings. Some unverified citations. Some dates or numbers not confirmed. Incomplete disclaimers. Needs focused revision before distribution. |
| **2/5** | Major Revisions | 1 or more CRITICAL findings (wrong article numbers, materially incorrect claims). Multiple HIGH findings. Significant unverified content. Missing key disclaimers. Not safe to distribute. |
| **1/5** | Not Distribution Ready | Multiple CRITICAL findings. Pervasive inaccuracies across the document. Hallucination patterns evident throughout. No disclaimers. Requires complete rework from verified sources. |

### Score Decision Tree

```
Are there any CRITICAL findings?
├── YES → Score 2 or 1 (depending on count and pervasiveness)
└── NO → Count HIGH findings
    ├── 0 HIGH → Score 5 (if all verified) or 4 (if minor gaps)
    ├── 1-2 HIGH → Score 4 (if simple fixes) or 3 (if complex)
    └── 3+ HIGH → Score 3 or 2 (depending on severity and scope)
```

---

## Adversarial Review Principles

### The Red Team Mindset

| Principle | Application |
|-----------|------------|
| **You are the opponent** | Your job is to find every weakness, not to confirm the document is good |
| **Assume the worst** | Every unverified claim is wrong until proven right |
| **Follow the money** | Errors in financial calculations, penalties, and deadlines cause the most harm |
| **Check the basics first** | The most obvious facts (dates, names, article numbers) are where most errors hide |
| **Trust nothing** | AI confidence is not correlated with accuracy; the most confident claims are often the most wrong |
| **Document everything** | Every finding, every verification, every source -- create a complete audit trail |
| **Think like the reader** | What would a reader who trusts this document do? What harm would an error cause? |

### Verification Prioritization

When time is limited, verify in this order:

| Priority | Category | Rationale |
|----------|----------|-----------|
| 1 | Legal citations (article numbers) | Most likely to be hallucinated; creates false obligations |
| 2 | Dates and deadlines | Wrong deadlines cause compliance failures |
| 3 | Penalty amounts | Wrong penalties cause incorrect risk assessment |
| 4 | Binding vs non-binding characterization | Confusing guidance for law wastes resources or creates false security |
| 5 | Arithmetic | Calculation errors compound through analysis |
| 6 | Entity names and jurisdictions | Less likely to cause direct harm but undermines credibility |
