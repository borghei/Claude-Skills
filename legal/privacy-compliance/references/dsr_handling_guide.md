# Data Subject Request Handling Guide

Comprehensive reference for handling data subject requests across 9 privacy regulations, from intake through response and regulatory monitoring.

---

## Table of Contents

- [Request Types](#request-types)
- [Intake Process](#intake-process)
- [Identity Verification](#identity-verification)
- [Response Timelines](#response-timelines)
- [Exemptions by Regulation](#exemptions-by-regulation)
- [Response Process](#response-process)
- [Request Type Details](#request-type-details)
- [Regulatory Monitoring](#regulatory-monitoring)

---

## Request Types

| # | Request Type | Description | Key Regulations |
|---|-------------|-------------|-----------------|
| 1 | **Access** | Provide copy of personal data and processing information | All 9 regulations |
| 2 | **Deletion/Erasure** | Delete personal data ("right to be forgotten") | GDPR Art. 17, CCPA §1798.105, LGPD Art. 18(VI), PIPL Art. 47, UK GDPR Art. 17 |
| 3 | **Correction/Rectification** | Correct inaccurate personal data | GDPR Art. 16, CCPA §1798.106, LGPD Art. 18(III), PIPL Art. 46, UK GDPR Art. 16 |
| 4 | **Portability** | Receive data in structured, machine-readable format | GDPR Art. 20, CCPA §1798.130, LGPD Art. 18(V), PIPL Art. 45, PDPA §26F |
| 5 | **Restriction of processing** | Limit processing while dispute is resolved | GDPR Art. 18, LGPD Art. 18(IV), PIPL Art. 44, UK GDPR Art. 18 |
| 6 | **Objection** | Object to processing based on legitimate interests or direct marketing | GDPR Art. 21, CCPA §1798.120 (opt-out of sale), UK GDPR Art. 21 |
| 7 | **Automated decision opt-out** | Right not to be subject to solely automated decisions with legal/significant effects | GDPR Art. 22, CCPA §1798.185, LGPD Art. 20, PIPL Art. 24, UK GDPR Art. 22 |
| 8 | **Withdraw consent** | Withdraw previously given consent for processing | GDPR Art. 7(3), LGPD Art. 18(IX), PDPA §16, PIPL Art. 15, UK GDPR Art. 7(3) |

---

## Intake Process

### Step 1: Receive Request

| Channel | Considerations |
|---------|---------------|
| Email to privacy@company.com | Standard channel; auto-acknowledge receipt |
| Web form (privacy portal) | Preferred — captures structured data; auto-generates tracking ID |
| Physical mail | Scan and log; may require follow-up for verification |
| In-person/phone | Document in writing; confirm details with requestor |
| Third-party agent | Verify agent authorization; may require power of attorney |
| Social media / public channel | Direct to private channel; do not disclose personal data publicly |

### Step 2: Log and Categorize

| Field | Required | Notes |
|-------|----------|-------|
| Request ID | Auto-generated | Format: DSR-YYYY-NNNN |
| Date received | Timestamp | Starts deadline clock |
| Requestor name | Yes | As provided by data subject |
| Contact method | Yes | Email, address, or phone for response |
| Request type(s) | Yes | May combine multiple types (access + deletion) |
| Applicable regulation | Determined | Based on requestor location and data processing context |
| Data subject identifier | Yes | How to locate their data in systems |
| Urgency flags | Auto | PIPL/LGPD = 15-day deadline; CCPA = 10-business-day ack |

### Step 3: Acknowledge Receipt

| Regulation | Acknowledgment Requirement | Timeline |
|-----------|---------------------------|----------|
| GDPR | No formal ack requirement (best practice: immediate) | Recommended: same business day |
| CCPA/CPRA | Formal acknowledgment required | 10 business days |
| LGPD | Immediate confirmation of receipt | Promptly |
| POPIA | No formal requirement | Best practice: 5 business days |
| PIPEDA | No formal requirement | Best practice: 5 business days |
| PDPA | Reasonable effort to respond | As soon as practicable |
| Privacy Act (AU) | Acknowledge and provide timeframe | 14 calendar days |
| PIPL | No formal requirement | Promptly |
| UK GDPR | No formal ack requirement (best practice: immediate) | Recommended: same business day |

---

## Identity Verification

### Verification Methods by Risk Level

| Risk Level | Data Sensitivity | Verification Method | Examples |
|-----------|-----------------|-------------------|----------|
| Low | Public-facing data, non-sensitive | Email confirmation from account email | Newsletter preferences, public profile |
| Medium | Account data, purchase history | Login verification + security question OR email + phone confirmation | E-commerce account, service records |
| High | Financial, health, sensitive data | Government-issued ID + account verification | Banking records, medical records, HR files |
| Very High | Special category data, children's data | In-person verification OR notarized authorization + ID | Health records, children's education data |

### Verification Principles

| Principle | Description |
|-----------|-------------|
| Proportionality | Verification must be proportionate to sensitivity of data; do not over-verify |
| No additional data collection | Do not collect more personal data than necessary for verification (Art. 11(2) GDPR) |
| Existing relationship | Use existing authentication if data subject has an account |
| Reasonable effort | If identity cannot be confirmed, may request additional evidence — document efforts |
| Time impact | Verification time counts within deadline — verify promptly |
| Agent requests | Third-party agents require written authorization (power of attorney or equivalent) |

### CCPA-Specific Verification Requirements

| Request Type | Verification Level |
|-------------|-------------------|
| Right to know (categories) | Reasonable degree of certainty |
| Right to know (specific pieces) | Reasonably high degree of certainty |
| Right to delete | Reasonable degree of certainty (non-sensitive) / Reasonably high (sensitive) |
| Right to opt-out of sale | No verification required (must honor) |

---

## Response Timelines

| Regulation | Ack Deadline | Response Deadline | Extension Available | Max Total Time | Extension Conditions |
|-----------|-------------|------------------|-------------------|---------------|---------------------|
| GDPR | Best practice | 30 calendar days | +60 calendar days | 90 calendar days | Complex request or high volume; must notify data subject within initial 30 days with reasons |
| CCPA/CPRA | 10 business days | 45 calendar days | +45 calendar days | 90 calendar days | Reasonably necessary; must notify consumer |
| LGPD | Promptly | 15 calendar days | None | 15 calendar days | No extension provision; simplified format immediately, complete within 15 days |
| POPIA | Best practice | 30 calendar days | None | 30 calendar days | Adequate reasons for refusal only |
| PIPEDA | Best practice | 30 calendar days | +30 calendar days | 60 calendar days | Required to meet deadline impracticable; written notice with new date and reason |
| PDPA | As practicable | 30 calendar days | None standard | 30 calendar days | May take longer if reasonable; must inform requestor |
| Privacy Act (AU) | 14 days | 30 calendar days | +30 calendar days | 60 calendar days | If reasonable; must notify with reasons |
| PIPL | Promptly | 15 calendar days | +15 calendar days | 30 calendar days | Notify with reasons for extension |
| UK GDPR | Best practice | 30 calendar days | +60 calendar days | 90 calendar days | Complex or numerous requests; notify within initial 30 days |

---

## Exemptions by Regulation

### GDPR / UK GDPR Exemptions

| Exemption | Applies To | Legal Basis |
|-----------|-----------|-------------|
| Legal claims | Erasure, restriction | Art. 17(3)(e) — establishment, exercise, or defense of legal claims |
| Legal obligation | Erasure | Art. 17(3)(b) — compliance with legal obligation requiring processing |
| Public interest | Erasure, objection | Art. 17(3)(d) — public interest in public health; Art. 21(1) balancing |
| Freedom of expression | Erasure | Art. 17(3)(a) — exercising right of freedom of expression and information |
| Archiving/research | Erasure, rectification | Art. 17(3)(d) — archiving in public interest, scientific/historical research, statistics |
| Manifestly unfounded/excessive | All rights | Art. 12(5) — may charge reasonable fee or refuse; must demonstrate manifestly unfounded |
| Third-party rights | Access, portability | Recital 63 — must not adversely affect rights and freedoms of others |
| Trade secrets | Access | Right of access must not adversely affect trade secrets or IP |

### CCPA/CPRA Exemptions

| Exemption | Applies To | Section |
|-----------|-----------|---------|
| Legal compliance | Deletion | §1798.105(d)(8) — legal obligation |
| Security/fraud | Deletion | §1798.105(d)(2) — detect security incidents, protect against fraud |
| Existing transaction | Deletion | §1798.105(d)(1) — complete transaction for which PI collected |
| Internal uses compatible | Deletion | §1798.105(d)(7) — internal uses reasonably aligned with expectations |
| Free speech | Deletion | §1798.105(d)(4) — exercise free speech |
| Public interest research | Deletion | §1798.105(d)(6) — public interest; consumer expectations; de-identified |
| Litigation hold | Deletion | Implied — legal proceedings preservation |

### LGPD Exemptions

| Exemption | Applies To | Article |
|-----------|-----------|---------|
| Legal obligation | Deletion | Art. 16(I) — legal or regulatory compliance |
| Research | Deletion | Art. 16(II) — research bodies; anonymization where possible |
| Transfer to third party | Deletion | Art. 16(III) — if necessary and regulation requirements met |
| Controller's own use | Deletion | Art. 16(IV) — exclusive use; anonymized data |

### Cross-Regulation Exemption Matrix

| Exemption Category | GDPR | CCPA | LGPD | POPIA | PIPEDA | PDPA | Privacy Act | PIPL | UK GDPR |
|-------------------|------|------|------|-------|--------|------|-------------|------|---------|
| Legal compliance | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Legal claims/litigation | Yes | Implied | No | Yes | Yes | No | Yes | Yes | Yes |
| Public interest | Yes | Yes | No | Yes | No | Yes | Yes | Yes | Yes |
| Freedom of expression | Yes | Yes | No | No | No | No | No | No | Yes |
| Third-party rights | Yes | No | No | Yes | Yes | Yes | Yes | No | Yes |
| Regulatory retention | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Research/archiving | Yes | Yes | Yes | No | No | Yes | No | No | Yes |

---

## Response Process

### 6-Step Response Procedure

| Step | Action | Key Considerations |
|------|--------|-------------------|
| **1. Gather data** | Search all systems where data subject's personal data may reside: production databases, backups, logs, third-party processors, email archives, CRM, HR systems | Create comprehensive data map; do not rely on single source; include data held by processors |
| **2. Apply exemptions** | Review applicable exemptions for the specific regulation and request type; document exemption basis | Exemptions must be specific and documented; partial exemptions possible (redact exempt portions, provide rest) |
| **3. Prepare response** | Format data per request type: access = copy of data + processing info; portability = structured machine-readable format (JSON/CSV); deletion = confirmation of deletion from all systems | Access response must include: purposes, categories, recipients, retention, rights information, source (Art. 14) |
| **4. Cite legal basis for denials** | If denying (full or partial), cite specific legal provision: GDPR article, CCPA section, etc. | Never deny without legal basis citation; explain in plain language |
| **5. Inform of complaint right** | Include information about right to lodge complaint with supervisory authority (name, contact details) | GDPR Art. 77; CCPA — right to complain to CPPA/AG; LGPD — right to complain to ANPD |
| **6. Document** | Record complete request lifecycle: receipt date, verification, search scope, exemptions applied, response content, delivery method, delivery date | Retain documentation for statute of limitations period (typically 3-6 years); include decision rationale |

### Response Format Requirements

| Request Type | GDPR Format | CCPA Format | General Best Practice |
|-------------|-------------|-------------|----------------------|
| Access | Copy of data + Art. 15(1) info; electronic format if electronic request | Specific pieces of PI collected; categories; sources; purposes; third parties | Structured document; table format for data inventory |
| Deletion | Confirmation of deletion; list of systems; notification to recipients | Confirmation of deletion; confirmation that service providers also deleted | Written confirmation with scope of deletion |
| Correction | Confirmation of correction; notification to recipients Art. 19 | Confirmation of correction | Specify what was corrected |
| Portability | Structured, commonly used, machine-readable format (JSON, CSV, XML) | Categories and specific pieces in readily usable format | JSON preferred; include data dictionary |

---

## Request Type Details

### Access Requests — Required Information in Response

| Category | GDPR Art. 15(1) | Notes |
|----------|-----------------|-------|
| Confirmation of processing | Yes/no whether data is processed | Even "no data" is a valid response |
| Copy of personal data | Complete copy of all personal data | Include derived/inferred data |
| Purposes of processing | Each purpose for which data is used | Be specific, not generic |
| Categories of data | Types of personal data processed | Use clear categories |
| Recipients | Named recipients or categories | Actual recipients preferred |
| Retention periods | Per category or criteria for determining | Specific periods or criteria |
| Data subject rights | Rectification, erasure, restriction, objection | Standard template clause |
| Right to complain | SA name and contact details | Territory-specific SA |
| Source of data | If not collected from data subject (Art. 14) | Name source if possible |
| Automated decisions | Existence, logic, significance, consequences | Art. 22 — meaningful info about logic |
| International transfers | Safeguards under Art. 46 | SCC/adequacy reference |

### Deletion Requests — Scope Requirements

| System | Include in Deletion | Retention Exception |
|--------|-------------------|-------------------|
| Production databases | Yes | Legal retention requirements |
| Backup systems | Yes (next rotation cycle acceptable) | May defer to backup rotation schedule |
| Logs and analytics | Yes (pseudonymize or delete) | Security log retention (limited period) |
| Third-party processors | Yes — notify per Art. 17(2) | Processor's own legal obligations |
| Email and communications | Yes | Litigation hold if applicable |
| Paper records | Yes | Archival requirements |
| Publicly available copies | "Reasonable steps" to inform third parties | Art. 17(2) best efforts |

---

## Regulatory Monitoring

### What to Monitor

| Area | Sources | Frequency |
|------|---------|-----------|
| New legislation | Government gazettes, law firm alerts, IAPP, regulatory websites | Monthly |
| Enforcement actions | SA decision registers, court databases, GDPR Enforcement Tracker | Monthly |
| Regulatory guidance | SA guidelines, opinions, blog posts, consultation papers | Monthly |
| Industry standards | ISO standards updates, CoC developments, certification schemes | Quarterly |
| Transfer mechanism changes | Adequacy decision reviews, SCC updates, BCR developments | Quarterly |

### 5-Step Monitoring Approach

| Step | Action | Output |
|------|--------|--------|
| 1 | **Subscribe** — Set up alerts for all applicable SAs and regulatory bodies | Alert feeds configured |
| 2 | **Triage** — Weekly review of alerts; categorize by relevance and urgency | Prioritized change list |
| 3 | **Assess impact** — For relevant changes, assess impact on current practices and documented obligations | Impact assessment document |
| 4 | **Plan remediation** — If practice changes needed, create action plan with timeline and responsible parties | Remediation plan |
| 5 | **Implement and document** — Execute changes; update policies, notices, DPAs, training materials; log the change | Updated documentation |

### Escalation Criteria

| Trigger | Action | Timeline |
|---------|--------|----------|
| New regulation enacted in jurisdiction where data subjects reside | Full applicability assessment | 30 days from enactment |
| SA issues enforcement action in your sector | Review own practices against findings | 14 days |
| SCC/adequacy decision invalidated or amended | Re-assess all transfers relying on mechanism | Immediately |
| New SA guidance on DSR handling | Review and update DSR procedures | 30 days |
| Regulatory investigation or inquiry received | Engage legal counsel; preserve all records; respond within deadline | Immediately |
| Data breach potentially triggering multi-regulation notification | Assess notification obligations per regulation; notify within shortest applicable deadline | Within 24 hours |
| Significant change to processing activities | Re-run regulation applicability assessment | Before new processing begins |
