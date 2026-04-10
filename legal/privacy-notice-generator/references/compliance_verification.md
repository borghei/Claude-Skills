# Privacy Notice Compliance Verification

5-layer compliance verification system with post-generation checklists and writing style guide.

---

## Table of Contents

- [5-Layer Verification System](#5-layer-verification-system)
  - [Layer 1: Jurisdiction-Specific Requirements](#layer-1-jurisdiction-specific-requirements)
  - [Layer 2: Art. 13/14 Mandatory Disclosures](#layer-2-art-1314-mandatory-disclosures)
  - [Layer 3: General Checks](#layer-3-general-checks)
  - [Layer 4: Type-Specific Checks](#layer-4-type-specific-checks)
  - [Layer 5: AI Act Compliance](#layer-5-ai-act-compliance)
- [Post-Generation Checklist](#post-generation-checklist)
- [Writing Style Guide](#writing-style-guide)
- [Common Compliance Failures](#common-compliance-failures)

---

## 5-Layer Verification System

### Layer 1: Jurisdiction-Specific Requirements

Run jurisdiction check first — these are the most commonly missed items.

| Jurisdiction | Check | Requirement | Pass Criteria |
|-------------|-------|-------------|---------------|
| DE | Widerspruchsrecht | Art. 21 DSGVO right to object displayed separately and prominently | Separate heading/section; bold text; not buried in general rights list |
| DE | TDDDG reference | TDDDG §25 referenced for cookie/telemedia consent | TDDDG cited alongside GDPR for website/app notices |
| DE | BDSG §26 | Employee data processing basis cited | §26 BDSG referenced in employee/applicant notices |
| DE | DPO §38 BDSG | DPO appointment disclosure if 20+ employees | DPO section present with contact details |
| FR | CNIL compliance | CNIL cookie consent guidance followed | No "continue browsing" consent; equal reject/accept prominence |
| FR | LIL reference | Loi Informatique et Libertés cited where applicable | LIL referenced for supplementary provisions |
| FR | LCEN mentions | Legal mentions (publisher, hosting) | Mentions légales present or linked |
| AT | DSB reference | DSB as supervisory authority | DSB contact details in complaint section |
| AT | Works council | Works council (Betriebsrat) reference in employee notices | Works council notification for IT systems |
| IT | Garante reference | Garante as supervisory authority | Garante contact details |
| IT | Marketing granularity | Separate consent for marketing, profiling, third-party sharing | Granular consent mechanism described |
| ES | LOPDGDD reference | LOPDGDD cited alongside GDPR | LOPDGDD referenced |
| ES | Digital rights | Digital disconnection right in employee notices | Art. 88 LOPDGDD referenced |
| NL | Cookie wall prohibition | No cookie wall practice | Clear statement that access not conditional on cookie consent |
| BE | Bilingual notice | French/Dutch versions for Brussels; appropriate language per region | Language versions available or noted |
| IE | DPC reference | DPC as supervisory authority | DPC contact details |
| UK | UK GDPR citation | "UK GDPR" not "GDPR" for UK processing | UK GDPR and DPA 2018 cited |
| UK | PECR reference | PECR referenced for cookies/marketing | PECR cited in cookie and marketing sections |
| UK | ICO registration | ICO registration number if applicable | Registration number or reference included |

---

### Layer 2: Art. 13/14 Mandatory Disclosures

Every privacy notice must include these elements. Missing any item is a compliance failure.

| # | Element | GDPR Article | Required Content | Common Gaps |
|---|---------|-------------|-----------------|-------------|
| 1 | Controller identity | Art. 13(1)(a) | Full legal name, registered address, contact details | Using brand name only; missing registration number |
| 2 | DPO contact | Art. 13(1)(b) | Name or title, email, postal address | Missing when DPO appointed; no dedicated contact |
| 3 | Purposes of processing | Art. 13(1)(c) | Specific purpose for each processing activity | Vague purposes ("improve services"); bundled purposes |
| 4 | Legal basis per purpose | Art. 13(1)(c) | Specific Art. 6(1) basis for each purpose | Generic "applicable law"; missing basis for some purposes |
| 5 | Legitimate interests | Art. 13(1)(d) | Specific interests pursued (if LI basis used) | "Our legitimate interests" without specification |
| 6 | Recipients | Art. 13(1)(e) | Named recipients or specific categories | "Third parties" without categorization |
| 7 | Transfer info | Art. 13(1)(f) | Countries, mechanisms (adequacy/SCCs/BCRs) | Missing transfer mechanism; generic "secure transfer" |
| 8 | Retention periods | Art. 13(2)(a) | Specific period or criteria for each category | "As long as necessary"; no per-category periods |
| 9 | Right to access | Art. 13(2)(b) | Right exists; how to exercise | Missing exercise method |
| 10 | Right to rectification | Art. 13(2)(b) | Right exists; how to exercise | Listed but no exercise method |
| 11 | Right to erasure | Art. 13(2)(b) | Right exists; applicable restrictions | No mention of restrictions/exceptions |
| 12 | Right to restriction | Art. 13(2)(b) | Right exists; when applicable | Often omitted entirely |
| 13 | Right to object | Art. 13(2)(b) | Right exists; separate prominence | Buried in rights list; not prominent |
| 14 | Right to portability | Art. 13(2)(b) | Right exists; format information | Missing format specification |
| 15 | Consent withdrawal | Art. 13(2)(c) | How to withdraw; not affecting prior processing | Missing withdrawal method; missing "prior processing" language |
| 16 | SA complaint right | Art. 13(2)(d) | SA name and contact details | Generic "supervisory authority"; missing contact |
| 17 | Automated decisions | Art. 13(2)(f) | Existence, logic, significance, consequences | Missing "meaningful information about logic"; missing consequences |

**Art. 14 Additional Requirements (indirect collection):**

| # | Element | Art. 14 Reference | Required Content |
|---|---------|-------------------|-----------------|
| 18 | Source of data | Art. 14(2)(f) | Named source or category; whether publicly available |
| 19 | Categories obtained | Art. 14(1)(d) | Categories of personal data obtained from source |
| 20 | Timing of notice | Art. 14(3) | Within reasonable period, max 1 month; at first communication |

---

### Layer 3: General Checks

| # | Check | Pass Criteria | Severity |
|---|-------|---------------|----------|
| 1 | Art. 21 object right prominence | Separate heading or bold formatting; not just listed with other rights | High |
| 2 | DPO contact provided (if appointed) | Dedicated contact details (not general info@ email) | High |
| 3 | Cookie consent mechanism referenced | How to manage cookies; link to settings | High (website) |
| 4 | Transfer mechanism specified | Adequacy decision, SCCs, BCRs — named, not generic | High |
| 5 | AI/automated processing disclosure | Art. 22 requirements met if applicable | High |
| 6 | Children's data handling | Age verification; parental consent if applicable | High |
| 7 | Special category dual basis | Both Art. 6 AND Art. 9 basis stated for special category data | High |
| 8 | No placeholder text remaining | Zero instances of [PLACEHOLDER], {{variable}}, [TBD], [INSERT] | Critical |
| 9 | Plain language | "You/your" voice; sentences under 25 words average; no unexplained legal terms | Medium |
| 10 | Consistent formatting | Uniform heading hierarchy; consistent table format | Medium |
| 11 | Version date present | "Last updated" or "Effective date" visible | Medium |
| 12 | Contact method specified | How to exercise rights (email, form, postal); response timeframe | High |
| 13 | Accessible format | Headings for navigation; adequate contrast; screen reader compatible | Medium |
| 14 | Change notification | How data subjects will be notified of material changes | Medium |

---

### Layer 4: Type-Specific Checks

#### Applicant Notice

| # | Check | Requirement | Severity |
|---|-------|-------------|----------|
| 1 | §26 BDSG reference (DE) | Employment law basis cited for DE applicant data | High (DE) |
| 2 | Retention period specified | Default 6 months; AGG defense period | High |
| 3 | Talent pool consent separate | Not bundled with application submission | High |
| 4 | Background check basis | Legal basis specified if background checks performed | High |
| 5 | Diversity data handling | Voluntary basis; anonymization after use | Medium |

#### Employee Notice

| # | Check | Requirement | Severity |
|---|-------|-------------|----------|
| 1 | Works council notification | Reference to works council involvement (DE/AT) | High (DE/AT) |
| 2 | IT monitoring scope | What is monitored; purpose; access to results | High |
| 3 | BYOD policy | Scope of employer access; data segregation | Medium |
| 4 | Health data Art. 9 basis | Specific Art. 9(2) basis for health data | High |
| 5 | Performance data transparency | How performance data used; retention | Medium |

#### B2B Notice

| # | Check | Requirement | Severity |
|---|-------|-------------|----------|
| 1 | Art. 14 source disclosure | Source of data clearly identified | High |
| 2 | Categories obtained | What data obtained from each source | High |
| 3 | Notice timing | Within 1 month or at first communication | Medium |
| 4 | Publicly available indicator | Whether data from public sources | Medium |

#### B2C Notice

| # | Check | Requirement | Severity |
|---|-------|-------------|----------|
| 1 | Soft opt-in rules | Existing customer marketing basis explained | Medium |
| 2 | Payment processor disclosure | Payment processor identity and role | High |
| 3 | Loyalty program data | Purpose, profiling, retention if applicable | Medium |
| 4 | Marketing opt-out | Easy unsubscribe mechanism described | High |

---

### Layer 5: AI Act Compliance

If the organization deploys AI systems, additional Art. 50 transparency requirements apply.

| # | Check | AI Act Reference | Requirement |
|---|-------|-----------------|-------------|
| 1 | AI system identification | Art. 50(1) | Individuals informed they are interacting with AI |
| 2 | AI system purpose | Art. 50(2) | Purpose of AI system disclosed |
| 3 | Emotion recognition | Art. 50(3) | Disclosure if emotion recognition or biometric categorization used |
| 4 | Deep fake / synthetic content | Art. 50(4) | Disclosure if content artificially generated or manipulated |
| 5 | High-risk AI | Art. 26(11) | Human oversight measures; right to explanation of AI-assisted decisions |
| 6 | GPAI output marking | Art. 50(2) | Machine-readable marking for AI-generated content |

---

## Post-Generation Checklist

### Legal Review (5 Items)

| # | Item | Reviewer | Sign-off |
|---|------|----------|---------|
| 1 | All legal bases correctly matched to purposes | Privacy counsel | ☐ |
| 2 | Retention periods comply with applicable law | Privacy counsel | ☐ |
| 3 | Transfer mechanisms correctly identified and implemented | Privacy counsel | ☐ |
| 4 | Exemptions and restrictions accurately stated | Privacy counsel | ☐ |
| 5 | Jurisdiction-specific requirements addressed | Local counsel | ☐ |

### Technical Review (4 Items)

| # | Item | Reviewer | Sign-off |
|---|------|----------|---------|
| 1 | All links functional and correct | Web developer | ☐ |
| 2 | Cookie categories match CMP configuration | Web developer | ☐ |
| 3 | Rights exercise mechanism operational | Product team | ☐ |
| 4 | Privacy notice accessible from all relevant touchpoints | QA team | ☐ |

### Translation QA (5 Items)

| # | Item | Reviewer | Sign-off |
|---|------|----------|---------|
| 1 | Legal terms correctly translated (not just literal) | Legal translator | ☐ |
| 2 | Jurisdiction-specific legal references maintained | Legal translator | ☐ |
| 3 | SA name and contact in local language | Legal translator | ☐ |
| 4 | Consistent terminology across notice | Legal translator | ☐ |
| 5 | Cultural appropriateness of examples and tone | Local reviewer | ☐ |

### Publication Requirements (5 Items)

| # | Item | Details | Sign-off |
|---|------|---------|---------|
| 1 | Version number and date visible | "Version X.X — Last updated DD Month YYYY" | ☐ |
| 2 | Change log maintained | What changed, when, why | ☐ |
| 3 | Previous versions archived | Accessible for accountability | ☐ |
| 4 | Notification mechanism | How data subjects informed of material changes | ☐ |
| 5 | Prominent placement | Footer link, registration flow, first-use screen | ☐ |

### Ongoing Review Triggers (6 Items)

| # | Trigger | Action | Timeline |
|---|---------|--------|----------|
| 1 | New processing activity | Review and update affected sections | Before processing begins |
| 2 | New jurisdiction | Add jurisdiction-specific supplement | Before targeting new jurisdiction |
| 3 | Regulatory change | Review against new requirements | Within 30 days of change |
| 4 | SA guidance publication | Review against guidance | Within 30 days |
| 5 | Annual review | Full compliance check | Every 12 months |
| 6 | Data breach | Review notice accuracy post-incident | Within 7 days |

---

## Writing Style Guide

### Voice and Tone

| Principle | Guideline | Example |
|-----------|-----------|---------|
| Address directly | Use "you" and "your data" | "We process **your** personal data..." not "The data subject's data is processed..." |
| Active voice | Controller as actor | "We collect your email address" not "Your email address is collected" |
| Plain language | No unexplained legal jargon | "We delete your data after 2 years" not "Data is subject to erasure upon expiry of the retention period" |
| Precise citations | Cite specific articles | "Under Art. 15 GDPR, you have the right..." not "Under applicable law..." |
| Short sentences | Average under 25 words | Split long legal sentences into digestible parts |
| Concrete periods | Specific retention | "We keep your data for 6 months" not "We keep your data as long as necessary" |

### Formatting Guidelines

| Element | Recommendation |
|---------|---------------|
| Tables | Use for purposes/legal bases mapping; retention periods; recipient lists; rights overview |
| Headings | Clear hierarchy (H1 title, H2 major sections, H3 subsections); descriptive not numbered |
| Bold | Key rights, important deadlines, controller name |
| Lists | For enumerated rights, data categories, processing purposes |
| Links | SA website, rights exercise form, cookie settings, related policies |
| Callouts | Jurisdiction-specific notes; special category warnings; AI processing flags |

### Language Level

| Jurisdiction | Recommended Level | Notes |
|-------------|-------------------|-------|
| NL | B1 (AP guidance) | AP explicitly recommends B1 language level |
| All others | Plain language (Recital 58) | Clear and plain language; avoid legalese; explain technical terms |
| Children | Age-appropriate | Simple vocabulary; visual aids; shorter sentences |

### Terms to Avoid

| Avoid | Use Instead |
|-------|-------------|
| "Data subject" | "You" |
| "Processing" (alone) | "Use", "collect", "store", "share" (be specific) |
| "Legitimate interests" (unexplained) | "Our legitimate interest in [specific interest], such as [example]" |
| "Third parties" (unnamed) | Name categories: "our IT service providers", "payment processors" |
| "As long as necessary" | Specific period: "for 2 years after your last purchase" |
| "Applicable law" | Specific law: "Art. 6(1)(c) GDPR" or "§147 AO (German Tax Code)" |

---

## Common Compliance Failures

| Rank | Failure | Frequency | Impact | Fix |
|------|---------|-----------|--------|-----|
| 1 | Missing specific legal basis per purpose | Very common | High — SA enforcement priority | Map each purpose to Art. 6(1) basis in table format |
| 2 | Generic retention periods | Very common | High — fails Art. 13(2)(a) | Define per-category retention with legal basis |
| 3 | No Art. 21 prominence | Common | Medium — DE/AT enforcement | Separate section with bold formatting |
| 4 | Missing transfer mechanism | Common | High — Schrems II enforcement | Name mechanism (adequacy/SCCs) per transfer |
| 5 | Incomplete rights list | Occasional | Medium | Include all 8 rights with exercise method |
| 6 | No DPO contact despite appointment | Occasional | Medium | Dedicated DPO section with email and address |
| 7 | Placeholder text in published notice | Rare but critical | Critical | Search and replace all placeholders before publishing |
| 8 | Missing Art. 14 source for indirect collection | Common (B2B) | High | Source disclosure with public availability indicator |
| 9 | Missing AI/automated decision disclosure | Increasing | High — AI Act enforcement | Add Art. 22 section; Art. 50 AI Act if applicable |
| 10 | Cookie notice non-compliant | Very common | Medium — active enforcement | Granular consent; no pre-ticked; equal reject/accept |
