# CCPA/CPRA Requirements Guide

Complete requirements reference for the California Consumer Privacy Act (CCPA) and California Privacy Rights Act (CPRA), with regulatory references, implementation guidance, and multi-state privacy law comparison.

---

## Table of Contents

- [Regulatory Framework](#regulatory-framework)
- [Consumer Rights Requirements](#consumer-rights-requirements)
- [Privacy Policy Requirements](#privacy-policy-requirements)
- [Service Provider and Contractor Requirements](#service-provider-and-contractor-requirements)
- [Sensitive Personal Information Requirements](#sensitive-personal-information-requirements)
- [Enforcement and Penalties](#enforcement-and-penalties)
- [Multi-State Privacy Law Comparison](#multi-state-privacy-law-comparison)
- [CCPA vs GDPR Detailed Comparison](#ccpa-vs-gdpr-detailed-comparison)

---

## Regulatory Framework

### CCPA (Cal. Civ. Code §1798.100-1798.199.100)

| Section | Title | Key Requirement |
|---------|-------|----------------|
| §1798.100 | General Duties | Disclose PI categories, business purposes; data minimization (CPRA) |
| §1798.105 | Right to Delete | Delete PI upon verifiable consumer request |
| §1798.106 | Right to Correct | Correct inaccurate PI (CPRA addition) |
| §1798.110 | Right to Know | Disclose categories and specific pieces of PI |
| §1798.115 | Right to Know (Disclosure) | Disclose PI sold, shared, or disclosed for business purpose |
| §1798.120 | Right to Opt-Out | Opt out of sale or sharing of PI |
| §1798.121 | Right to Limit SPI Use | Limit use and disclosure of SPI (CPRA addition) |
| §1798.125 | Non-Discrimination | No retaliation for exercising rights |
| §1798.130 | How Rights are Exercised | Methods for submitting requests, response timelines |
| §1798.135 | Opt-Out Requirements | "Do Not Sell or Share" link, GPC, opt-out mechanisms |
| §1798.140 | Definitions | Personal information, business, service provider, SPI, etc. |
| §1798.145 | Exemptions | HIPAA, GLBA, FCRA, employment, B2B exemptions |
| §1798.150 | Private Right of Action | Data breach private action, $100-$750 per consumer |
| §1798.155 | CPPA Enforcement | Administrative enforcement by CPPA |
| §1798.185 | Rulemaking | CPPA rulemaking authority, cybersecurity audits, risk assessments |
| §1798.199.10-40 | CPPA | Establishment of California Privacy Protection Agency |

### CPRA Key Amendments (Effective January 1, 2023)

1. **Created California Privacy Protection Agency (CPPA)** as dedicated enforcement body
2. **Right to Correct** inaccurate PI (§1798.106)
3. **Right to Limit Use of SPI** (§1798.121)
4. **Data minimization and purpose limitation** (§1798.100(c))
5. **Sensitive Personal Information** category with enhanced protections
6. **Contractor** distinction from service providers (§1798.140(j))
7. **Automated decision-making** disclosure requirements (§1798.185(a)(16))
8. **Cybersecurity audits** for high-risk processing (§1798.185(a)(15)(B))
9. **Risk assessments** for processing presenting significant risk (§1798.185(a)(15)(A))
10. **Consumer threshold** increased from 50,000 to 100,000 consumers/households
11. **Right to Data Portability** in machine-readable format (§1798.130)
12. **Expanded opt-out** to cover "sharing" (cross-context behavioral advertising)

---

## Consumer Rights Requirements

### Right to Know (§1798.100, §1798.110)

**What businesses must disclose upon request:**
- Categories of PI collected
- Specific pieces of PI collected
- Categories of sources from which PI is collected
- Business or commercial purpose for collecting, selling, or sharing PI
- Categories of third parties to whom PI is disclosed
- Categories of PI sold or shared (past 12 months)

**Implementation Requirements:**
- Provide at least two methods for submitting requests (toll-free number + one other method)
- Online-only businesses may provide email-only method
- Respond within 45 calendar days of receipt
- May extend up to 90 days total with notice to consumer
- Deliver information covering the 12-month period preceding the request
- Provide information in a portable, readily usable format
- Free of charge (no more than twice in a 12-month period)

### Right to Delete (§1798.105)

**Requirements:**
- Delete PI collected from the consumer upon verifiable request
- Direct service providers and contractors to delete
- Notify third parties to whom PI was sold or shared

**Exceptions (§1798.105(d)):**
- Complete the transaction for which PI was collected
- Detect security incidents or protect against malicious activity
- Debug to identify and repair functionality errors
- Exercise free speech or another right provided by law
- Comply with California Electronic Communications Privacy Act
- Scientific, historical, or statistical research in the public interest
- Internal uses reasonably aligned with consumer expectations
- Comply with a legal obligation

### Right to Opt-Out of Sale/Sharing (§1798.120)

**Requirements:**
- Consumer right to direct business not to sell or share PI
- "Sell" includes monetary or other valuable consideration
- "Share" includes cross-context behavioral advertising (CPRA)
- Must provide "Do Not Sell or Share My Personal Information" link
- Must honor Global Privacy Control (GPC) signals
- No verification required for opt-out requests
- Wait at least 12 months before requesting re-opt-in
- Children under 16: affirmative opt-in required
- Children under 13: parental/guardian consent required

### Right to Correct (§1798.106, CPRA)

**Requirements:**
- Consumer right to request correction of inaccurate PI
- Business must use commercially reasonable efforts to correct
- Must consider the nature and documented purpose of PI
- Must direct service providers and contractors to correct
- Response timeline: 45 calendar days

### Right to Limit Use of SPI (§1798.121, CPRA)

**Requirements:**
- Consumer right to limit use and disclosure of SPI
- Business must limit use to purposes necessary for service/goods requested
- Must provide "Limit the Use of My Sensitive Personal Information" link
- Permitted uses: performing services, ensuring security/integrity, short-lived uses, quality/safety of products, servicing accounts

### Right to Non-Discrimination (§1798.125)

**Prohibited discrimination includes:**
- Denying goods or services
- Charging different prices or rates
- Providing a different level or quality of goods or services
- Suggesting any of the above

**Permitted practices:**
- Financial incentive programs with consumer opt-in
- Loyalty programs with value proportional to PI provided
- Different pricing for services funded by PI sale (with disclosure)

### Right to Data Portability (§1798.130, CPRA)

**Requirements:**
- PI must be provided in a portable, readily usable format
- Format must be technically feasible for transmission to another entity
- Applies to Right to Know requests for specific pieces of PI

---

## Privacy Policy Requirements

### Required Content (§1798.130(a)(5))

A privacy policy must include:

1. **Categories of PI collected** in the preceding 12 months
2. **Categories of SPI collected** (CPRA)
3. **Categories of sources** from which PI is collected
4. **Business or commercial purposes** for collecting, selling, or sharing
5. **Categories of third parties** to whom PI is disclosed
6. **Categories of PI sold or shared** in the preceding 12 months (by PI category and third-party category)
7. **Categories of PI disclosed for business purpose** in preceding 12 months
8. **Retention periods** for each category of PI (CPRA)
9. **Consumer rights description** and how to exercise them
10. **Methods for submitting requests** (toll-free number, website address)
11. **"Do Not Sell or Share My Personal Information" link** or explanation
12. **"Limit the Use of My Sensitive Personal Information" link** (CPRA)
13. **Right to non-discrimination** statement
14. **Date of last update**

### Format Requirements

- Written in plain, straightforward language
- Available in the languages in which the business operates
- Posted conspicuously on the business's website homepage
- Accessible to consumers with disabilities (WCAG compliance recommended)
- Updated at least every 12 months
- Include effective date of last update

### Notice at Collection (§1798.100(b))

At or before the point of collection, businesses must inform consumers of:
- Categories of PI to be collected
- Purposes for which PI will be used
- Whether PI is sold or shared
- Retention periods
- Link to full privacy policy

---

## Service Provider and Contractor Requirements

### Service Provider Agreements (§1798.140(ag))

Written agreement must include:
- Identify specific business purpose for processing
- Prohibit selling or sharing PI received from/on behalf of business
- Prohibit retaining, using, or disclosing PI outside the direct business relationship
- Prohibit combining PI with other sources (unless permitted)
- Require compliance with CCPA/CPRA obligations
- Grant business right to ensure provider uses PI consistently with CCPA
- Require notification if unable to meet obligations
- Require provider to use reasonable security measures
- Allow business to stop and remediate unauthorized use

### Contractor Agreements (§1798.140(j), CPRA)

In addition to service provider requirements:
- Contractor must certify understanding of restrictions
- Contract must prohibit selling or sharing PI
- Must grant audit rights to the business
- Must require notification to business of subcontractor engagement

### Third-Party Obligations

- Must comply with consumer opt-out requests
- Must provide same level of privacy protection as the business
- Must notify business if unable to meet obligations
- Business must take steps to stop and remediate unauthorized use

---

## Sensitive Personal Information Requirements

### SPI Categories (§1798.140(ae))

| # | Category | Examples |
|---|----------|---------|
| 1 | Government identifiers | SSN, driver's license, state ID, passport |
| 2 | Account credentials | Username + password, security question, access code |
| 3 | Financial with credentials | Account number + access code allowing account access |
| 4 | Precise geolocation | Location within 1,850-foot radius |
| 5 | Protected classifications | Racial/ethnic origin, religious beliefs, union membership |
| 6 | Genetic data | DNA sequences, genetic markers |
| 7 | Communications content | Mail, email, text message content (unless intended recipient) |
| 8 | Biometric data | Used for purpose of uniquely identifying a consumer |
| 9 | Health information | Physical or mental health condition or treatment |
| 10 | Sex life/orientation | Sexual orientation, sex life data |

### SPI Business Obligations

- Provide "Limit the Use of My Sensitive Personal Information" link on homepage
- Limit use to what is necessary to perform services/provide goods
- Do not use SPI for purposes beyond those disclosed at collection
- Apply enhanced security controls (encryption, access restrictions)
- Include SPI categories in privacy policy disclosures
- Honor consumer requests to limit SPI use without verification burden

---

## Enforcement and Penalties

### CPPA Enforcement (§1798.155, §1798.199.10-40)

- **Investigative powers**: Subpoenas, audits, inspections
- **Administrative fines**: $2,500 per unintentional violation, $7,500 per intentional violation
- **30-day cure period**: Eliminated under CPRA for CPPA enforcement (AG may still offer)
- **Rulemaking authority**: Cybersecurity audit rules, risk assessment rules, automated decision-making

### AG Enforcement

- Retains enforcement authority alongside CPPA
- May bring civil actions in superior court
- Penalties: $2,500 per unintentional, $7,500 per intentional violation
- No cap on total penalties (per-violation basis)

### Private Right of Action (§1798.150)

- **Limited scope**: Only for data breaches resulting from failure to maintain reasonable security
- **Statutory damages**: $100-$750 per consumer per incident (or actual damages, whichever greater)
- **30-day cure notice**: Consumer must provide 30-day written notice before filing suit
- **AG may intervene**: AG can prosecute action instead of consumer
- **No private right of action** for other CCPA violations

---

## Multi-State Privacy Law Comparison

### Key US State Privacy Laws

| Feature | CCPA/CPRA (CA) | VCDPA (VA) | CPA (CO) | CTDPA (CT) | TDPSA (TX) |
|---------|---------------|------------|----------|------------|------------|
| Effective | Jan 2020 / Jan 2023 | Jan 2023 | Jul 2023 | Jul 2023 | Jul 2024 |
| Scope | $25M rev, 100K consumers, or 50% PI rev | 100K consumers or 25K + 50% rev | 100K consumers or 25K + PI rev | 100K consumers or 25K + 50% rev | Process PI of TX residents |
| Opt-out model | Yes | Yes | Yes (universal opt-out) | Yes (universal opt-out) | Yes |
| Right to Know | Yes | Yes | Yes | Yes | Yes |
| Right to Delete | Yes | Yes | Yes | Yes | Yes |
| Right to Correct | Yes (CPRA) | Yes | Yes | Yes | Yes |
| Right to Portability | Yes (CPRA) | Yes | Yes | Yes | Yes |
| Right to Opt-Out Sale | Yes | Yes (sale, profiling, targeted ads) | Yes (sale, profiling, targeted ads) | Yes (sale, profiling, targeted ads) | Yes |
| SPI Category | Yes (CPRA) | Consent-based | Consent-based | Consent-based | Consent-based |
| Private Right of Action | Data breaches only | No | No | No | No |
| Cure Period | No (CPPA) | 30 days (sunsets 2025) | 60 days (sunsets 2025) | 60 days | 30 days |
| Enforcer | CPPA + AG | AG | AG | AG | AG |
| Data Minimization | Yes (CPRA) | Yes | Yes | Yes | Yes |
| DPIA Required | Risk assessments (CPRA) | Yes | Yes | Yes | Yes |
| Universal Opt-Out | GPC required | Opt-out mechanism by 2025 | Required by Jul 2024 | Required by Jan 2025 | No |

### State Law Interaction Strategy

For organizations operating across multiple states:
1. **Use CCPA/CPRA as baseline** — it is the most comprehensive and strictest
2. **Layer state-specific requirements** on top (e.g., VCDPA's DPIA requirements)
3. **Implement universal opt-out signals** (GPC) to satisfy multiple states simultaneously
4. **Maintain a single comprehensive privacy policy** addressing all state requirements
5. **Track new state laws** — 15+ states have enacted comprehensive privacy laws as of 2025

---

## CCPA vs GDPR Detailed Comparison

| Aspect | CCPA/CPRA | GDPR |
|--------|----------|------|
| **Jurisdiction** | California residents | EU/EEA data subjects globally |
| **Legal basis model** | Opt-out (no legal basis required for collection) | Opt-in (requires legal basis per Art. 6) |
| **Data scope** | Personal information (broadly defined) | Personal data (broadly defined) |
| **Controller/processor** | Business / service provider / contractor | Controller / processor |
| **Consent standard** | Opt-out of sale/sharing; opt-in for minors | Freely given, specific, informed, unambiguous |
| **Sensitive data** | SPI with limit-use right | Special category with explicit consent (Art. 9) |
| **DPO requirement** | None | Required for certain processing (Art. 37) |
| **Breach notification** | AG notification, private right of action | 72-hour DPA notification (Art. 33), data subject notification (Art. 34) |
| **Penalties** | $2,500-$7,500 per violation + private action ($100-$750) | Up to 4% global annual revenue or EUR 20M |
| **Cross-border transfers** | No transfer restrictions | Adequacy, SCCs, BCRs, or derogations |
| **Records of processing** | Privacy policy disclosures | Record of processing activities (Art. 30) |
| **Children's data** | Opt-in under 16, parental under 13 | Varies by member state (13-16), parental consent |
| **Right to object** | Opt-out of sale/sharing | Object to legitimate interest processing (Art. 21) |
| **Automated decisions** | Disclosure (CPRA rulemaking) | Right not to be subject to solely automated decisions (Art. 22) |
| **Private action** | Data breaches only | Varies by member state (Art. 82) |
| **Regulatory body** | CPPA (state-level) | DPAs (per member state) + EDPB |
| **Extraterritorial** | Businesses meeting thresholds doing business in CA | Any entity processing EU residents' data |

### Dual Compliance Strategy

For organizations subject to both CCPA/CPRA and GDPR:
1. Use GDPR's higher consent standard as default for EU users
2. Apply CCPA/CPRA opt-out model for California consumers
3. Implement GPC and cookie consent for both frameworks
4. Maintain unified data subject/consumer rights workflow with framework-specific response templates
5. Map CCPA PI categories to GDPR data categories in a single data inventory
6. Apply the stricter requirement where frameworks overlap
