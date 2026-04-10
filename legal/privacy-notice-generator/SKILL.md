---
name: privacy-notice-generator
description: >
  Draft GDPR-compliant privacy notices for EU/EEA jurisdictions. Supports 6
  notice types, 9 jurisdictions, multi-layer compliance verification. Use for
  privacy notice drafting, compliance checking, and jurisdiction mapping.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: The Glass Room
  category: legal
  domain: privacy-notice
  updated: 2026-04-10
  tags: [privacy-notice, gdpr, data-protection, compliance, eu-privacy]
---
> **⚠️ EXPERIMENTAL** — This skill is provided for educational and informational purposes only. It does NOT constitute legal advice. All responsibility for usage rests with the user. Consult qualified legal professionals before acting on any output.

# Privacy Notice Generator

Tools and guidance for drafting GDPR-compliant privacy notices across EU/EEA jurisdictions and audience types, with multi-layer compliance verification.

---

## Table of Contents

- [Tools](#tools)
  - [Privacy Notice Scaffolder](#privacy-notice-scaffolder)
  - [Notice Compliance Checker](#notice-compliance-checker)
- [Reference Guides](#reference-guides)
- [Workflows](#workflows)
- [Troubleshooting](#troubleshooting)
- [Success Criteria](#success-criteria)
- [Scope & Limitations](#scope--limitations)
- [Anti-Patterns](#anti-patterns)
- [Tool Reference](#tool-reference)

---

## Tools

### Privacy Notice Scaffolder

Generates a privacy notice skeleton with all required sections pre-populated with jurisdiction-specific placeholders and legal references.

```bash
# Website privacy notice for German jurisdiction
python scripts/privacy_notice_scaffolder.py \
  --notice-type website \
  --jurisdiction DE \
  --data-categories personal,contact,usage,cookies \
  --legal-bases consent,contract,legitimate_interests \
  --has-cookies \
  --has-international-transfers

# Employee notice for French jurisdiction with AI processing
python scripts/privacy_notice_scaffolder.py \
  --notice-type employee \
  --jurisdiction FR \
  --data-categories personal,employment,financial,health \
  --legal-bases contract,legal_obligation,consent \
  --has-ai

# B2C customer notice for UK with all features
python scripts/privacy_notice_scaffolder.py \
  --notice-type b2c \
  --jurisdiction UK \
  --data-categories personal,contact,financial,usage,marketing \
  --legal-bases consent,contract,legitimate_interests \
  --has-cookies --has-ai --has-international-transfers \
  --json
```

**Supported Notice Types:**

| Type | Audience | Key Sections |
|------|----------|-------------|
| website | Website/app visitors | Cookies, analytics, tracking technologies |
| applicant | Job applicants | Recruitment data, talent pool, retention periods |
| employee | Employees | Works council, IT monitoring, BYOD, HR data |
| b2b | Business partners | Art. 14 requirements, source disclosure |
| b2c | B2C customers | Soft opt-in, payment processing, loyalty |
| combined | Multiple audiences | Merged sections with audience-specific callouts |

**Supported Jurisdictions:** DE, FR, AT, IT, ES, NL, BE, IE, UK

**13-Section Notice Structure:**
1. Controller identity and contact
2. DPO contact details
3. Data categories collected
4. Purposes and legal bases
5. Recipients and categories
6. International transfers
7. Retention periods
8. Data subject rights
9. Right to withdraw consent
10. Right to complain to SA
11. Automated decision-making
12. Cookies and tracking (if applicable)
13. AI processing (if applicable)

---

### Notice Compliance Checker

Validates a privacy notice text against Art. 13/14 GDPR requirements and generates a compliance score with missing/incomplete elements.

```bash
# Check a privacy notice file
python scripts/notice_compliance_checker.py privacy_notice.md

# Check with jurisdiction-specific requirements
python scripts/notice_compliance_checker.py privacy_notice.md --jurisdiction DE

# Check with notice type for type-specific validation
python scripts/notice_compliance_checker.py privacy_notice.md \
  --jurisdiction DE --notice-type employee

# JSON output
python scripts/notice_compliance_checker.py privacy_notice.md \
  --jurisdiction FR --notice-type website --json
```

**Checks For:**

| Category | Elements Checked |
|----------|-----------------|
| Art. 13 Mandatory | Controller identity, DPO contact, purposes, legal bases, recipients, transfers, retention, all 8 rights, automated decisions, consent withdrawal, SA complaint |
| Art. 14 Additional | Source of data, categories obtained (for indirect collection) |
| General | Art. 21 right to object prominence, plain language, no placeholders, consistent formatting |
| Jurisdiction-specific | DE: Widerspruchsrecht prominence, TDDDG; FR: CNIL recommendations; UK: ICO guidance |

**Output:**
- Compliance score (0-100)
- Missing elements (must-fix)
- Incomplete elements (should-improve)
- Jurisdiction-specific findings
- Type-specific findings

---

## Reference Guides

### Notice Types Guide
`references/notice_types_guide.md`

Detailed guidance for 6 notice types:
- Platform sub-types for website/app notices
- Applicant-specific data categories and retention
- Employee notice with works council and monitoring requirements
- B2B Art. 14 requirements and source disclosure
- B2C soft opt-in and payment processing
- Combined notice merge strategies

### Jurisdiction Requirements
`references/jurisdiction_requirements.md`

Jurisdiction-specific requirements for 9 jurisdictions:
- SA details and registration requirements
- Requirements beyond GDPR baseline
- Standard wording recommendations
- Retention guidance per jurisdiction

### Compliance Verification
`references/compliance_verification.md`

5-layer verification system:
- Jurisdiction-specific checks
- Art. 13/14 mandatory disclosures
- General compliance checks
- Type-specific checks
- AI Act compliance
- Post-generation checklist
- Writing style guide

---

## Workflows

### Workflow 1: SCOPE → INTAKE → DRAFT → VERIFY → DELIVER

```
Step 1: SCOPE — Determine notice parameters
        → Notice type (website/applicant/employee/b2b/b2c/combined)
        → Jurisdiction (DE/FR/AT/IT/ES/NL/BE/IE/UK)
        → Special features (cookies, AI, international transfers)

Step 2: INTAKE — Gather information
        → Controller identity and DPO
        → Data inventory (categories, sources)
        → Purposes and legal bases per category
        → Recipients and processors
        → Transfer destinations and mechanisms
        → Retention periods per category
        → Cookie/tracking inventory (if website)
        → AI processing details (if applicable)

Step 3: DRAFT — Generate notice skeleton
        → python scripts/privacy_notice_scaffolder.py [params]
        → Fill in placeholders with actual information from intake
        → Add jurisdiction-specific clauses
        → Apply writing style guide (you/your, short sentences, tables)

Step 4: VERIFY — Run compliance checker
        → python scripts/notice_compliance_checker.py notice.md --jurisdiction [J] --notice-type [T]
        → Address all missing elements
        → Address incomplete elements
        → Review jurisdiction-specific findings

Step 5: DELIVER — Finalize and publish
        → Legal review sign-off
        → Technical review (links, formatting, accessibility)
        → Translation QA (if multilingual)
        → Publication with version control
        → Set review trigger calendar
```

### Workflow 2: Notice Update

```
Step 1: Identify trigger (new processing, regulation change, annual review)
Step 2: Run compliance checker on current notice
Step 3: Identify gaps and required updates
Step 4: Draft updated sections
Step 5: Re-verify with compliance checker
Step 6: Notify data subjects of material changes
Step 7: Update version date and change log
```

### Workflow 3: Multi-Jurisdiction Notice

```
Step 1: Generate base notice for primary jurisdiction
        → python scripts/privacy_notice_scaffolder.py --jurisdiction [primary] ...
Step 2: Check jurisdiction requirements for additional territories
        → See references/jurisdiction_requirements.md
Step 3: Add jurisdiction-specific supplements
        → DE: TDDDG telecom disclosures, DSK guidance
        → FR: CNIL cookie requirements, LIL specifics
        → UK: ICO guidance, UK transfer mechanisms
Step 4: Verify each jurisdiction version
        → python scripts/notice_compliance_checker.py notice_de.md --jurisdiction DE
        → python scripts/notice_compliance_checker.py notice_fr.md --jurisdiction FR
Step 5: Publish with language/jurisdiction switcher
```

---

## Troubleshooting

| Problem | Possible Cause | Resolution |
|---------|---------------|------------|
| Low compliance score despite complete notice | Missing jurisdiction-specific requirements (e.g., DE Widerspruchsrecht prominence) | Run checker with --jurisdiction flag; review jurisdiction_requirements.md for local additions |
| Scaffolder generates too many sections | Combined notice type includes all audience sections | Use specific notice type instead of combined; or remove irrelevant sections post-generation |
| Art. 14 findings for direct collection | Checker flags Art. 14 requirements for B2B notice type | Correct — B2B often involves indirect collection; ensure source disclosure is included |
| Placeholder text in final notice | Template not fully populated | Search for `[PLACEHOLDER]` and `{{variable}}` markers; all must be replaced before publication |
| Cookie section missing from employee notice | Employee notice type does not include cookies by default | Add --has-cookies flag if employee-facing systems use cookies/tracking |
| AI section not generated | Missing --has-ai flag | Re-run scaffolder with --has-ai; review AI Act Art. 50 transparency requirements |

---

## Success Criteria

- **100% Art. 13/14 compliance score** — all mandatory disclosure elements present; zero missing items
- **Jurisdiction-specific requirements met** — compliance checker confirms local SA requirements addressed
- **Type-specific requirements met** — notice covers all audience-specific data processing activities
- **No placeholder text remaining** — all template variables replaced with actual information
- **Writing style guide followed** — "you/your" voice; short sentences; tables for complex information; precise legal citations
- **Legal review completed** — qualified privacy counsel sign-off on final notice
- **Publication requirements met** — accessible, versioned, dated, with change notification mechanism

---

## Scope & Limitations

**In Scope:**
- Privacy notice skeleton generation for 6 notice types across 9 jurisdictions
- Compliance checking against Art. 13/14 GDPR mandatory disclosures
- Jurisdiction-specific requirement validation (DE, FR, AT, IT, ES, NL, BE, IE, UK)
- Notice type-specific section generation and validation
- AI Act Art. 50 transparency disclosure sections
- Cookie and tracking technology disclosure sections
- Writing style and plain language guidance

**Out of Scope:**
- Legal advice on specific legal basis selection — consult qualified privacy counsel
- Translation services — tool generates English templates; professional translation required
- Cookie consent implementation or CMP configuration
- DPIA generation (see `dpia-assessment` skill)
- Privacy notice hosting or publication infrastructure
- Non-GDPR privacy notice formats (CCPA notice at collection, LGPD notices)
- Sector-specific notices (healthcare, financial services, children's services)

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Better Approach |
|-------------|-------------|-----------------|
| **Copy-paste from another company** | Different processing activities, jurisdictions, and legal bases; exposes liability gaps | Generate skeleton from actual parameters; fill with organization-specific information |
| **One notice for all jurisdictions** | Misses jurisdiction-specific requirements (DE TDDDG, FR CNIL, UK ICO); SA enforcement | Generate jurisdiction-specific versions or supplements using scaffolder per jurisdiction |
| **Generic legal bases** ("we process your data based on applicable law") | Art. 13(1)(c) requires specific legal basis per purpose; generic statement is non-compliant | Map each processing purpose to specific Art. 6(1) basis; document in purpose-basis table |
| **Set and forget** | Processing activities change; regulations evolve; notices become inaccurate | Set review triggers (see compliance_verification.md); run compliance checker quarterly |
| **Overly legalistic language** | Recital 58 requires clear and plain language; complex legal jargon is non-compliant | Follow writing style guide: "you/your" voice, short sentences, tables, examples |

---

## Tool Reference

### privacy_notice_scaffolder.py

Generates a privacy notice skeleton based on notice type, jurisdiction, and processing parameters.

| Flag | Required | Description |
|------|----------|-------------|
| `--notice-type <type>` | Yes | Notice type: website, applicant, employee, b2b, b2c, combined |
| `--jurisdiction <code>` | Yes | Jurisdiction: DE, FR, AT, IT, ES, NL, BE, IE, UK |
| `--data-categories <list>` | Yes | Comma-separated: personal, contact, usage, cookies, financial, health, employment, marketing, biometric |
| `--legal-bases <list>` | Yes | Comma-separated: consent, contract, legal_obligation, legitimate_interests, vital_interests, public_task |
| `--has-cookies` | No | Include cookies and tracking section |
| `--has-ai` | No | Include AI and automated processing section |
| `--has-international-transfers` | No | Include international transfers section |
| `--json` | No | Output in JSON format |

### notice_compliance_checker.py

Validates a privacy notice against Art. 13/14 GDPR requirements.

| Flag | Required | Description |
|------|----------|-------------|
| `<notice_file>` | Yes | Path to privacy notice file (markdown or text) |
| `--jurisdiction <code>` | No | Jurisdiction for local requirements: DE, FR, AT, IT, ES, NL, BE, IE, UK |
| `--notice-type <type>` | No | Notice type for type-specific checks: website, applicant, employee, b2b, b2c, combined |
| `--json` | No | Output in JSON format |
