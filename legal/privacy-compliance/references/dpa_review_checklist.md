# DPA Review Checklist

Complete reference for reviewing Data Processing Agreements under GDPR Art. 28 and related international requirements.

---

## Table of Contents

- [Art. 28 Required Elements](#art-28-required-elements)
- [Processor Obligations](#processor-obligations)
- [International Transfer Mechanisms](#international-transfer-mechanisms)
- [Transfer Impact Assessment](#transfer-impact-assessment)
- [Common DPA Issues](#common-dpa-issues)
- [Practical Considerations](#practical-considerations)
- [DPA Review Workflow](#dpa-review-workflow)

---

## Art. 28 Required Elements

Every DPA under GDPR must contain the following elements per Art. 28(3):

| # | Required Element | Article | What to Check |
|---|-----------------|---------|---------------|
| 1 | Subject matter and duration | Art. 28(3) | Matches service agreement term; clear start/end |
| 2 | Nature and purpose of processing | Art. 28(3) | Specific, not generic; aligns with actual processing |
| 3 | Types of personal data | Art. 28(3) | Complete list; includes special category if applicable |
| 4 | Categories of data subjects | Art. 28(3) | All categories covered (customers, employees, children) |
| 5 | Controller's obligations and rights | Art. 28(3) | Audit rights, instruction rights, termination rights |
| 6 | Processor processes only on documented instructions | Art. 28(3)(a) | No self-serving exceptions; EU law override clause |
| 7 | Confidentiality obligation on personnel | Art. 28(3)(b) | Statutory obligation or contractual commitment |
| 8 | Security measures (Art. 32) | Art. 28(3)(c) | Specific measures listed or referenced; not just "reasonable" |
| 9 | Sub-processor conditions | Art. 28(3)(d) | General or specific authorization; same obligations flow-down |
| 10 | Assistance with DSR obligations | Art. 28(3)(e) | Technical and organizational measures to assist |
| 11 | Assistance with Art. 32-36 obligations | Art. 28(3)(f) | Security, breach notification, DPIA, prior consultation |
| 12 | Data deletion or return on termination | Art. 28(3)(g) | Clear choice for controller; timeline specified; certification |
| 13 | Audit and inspection rights | Art. 28(3)(h) | Controller can audit or appoint auditor; no unreasonable restrictions |
| 14 | Inform controller of conflicting instructions | Art. 28(3) last para | Processor must flag instructions violating GDPR |

---

## Processor Obligations

### 10 Key Obligations to Verify

| # | Obligation | Key Check Points | Risk if Missing |
|---|-----------|-----------------|-----------------|
| 1 | **Documented instructions only** | No processing beyond controller instructions; EU/member state law exception must specify which law; processor must inform controller before processing under legal obligation | Processor acts as independent controller; joint liability |
| 2 | **Confidentiality** | All personnel under statutory or contractual confidentiality obligation; covers employees, contractors, and agents; survives termination | Unauthorized disclosure; breach notification obligation |
| 3 | **Security measures (Art. 32)** | Pseudonymization, encryption, confidentiality/integrity/availability/resilience, disaster recovery, regular testing; specific measures not just "appropriate" | Security incidents; regulatory findings; penalties |
| 4 | **Sub-processing** | General authorization with notification of changes and objection right (14-30 day window typical); OR specific prior written authorization; same contractual obligations imposed on sub-processors | Uncontrolled data sharing; transfer risks; audit gaps |
| 5 | **DSR assistance** | Technical measures to fulfill access, deletion, portability requests; response timeline (typically 5-10 business days to assist controller); cost allocation | Missed DSR deadlines; regulatory complaints |
| 6 | **Breach notification** | Notify controller without undue delay (specify hours — ideally 24-48); content requirements (nature, categories, approximate numbers, consequences, measures); assist with regulatory notification | Missed 72-hour GDPR reporting window; penalties |
| 7 | **DPIA assistance** | Provide information necessary for controller's DPIA; assist with prior consultation if needed | Incomplete risk assessment; regulatory findings |
| 8 | **Data return/deletion** | Controller choice of return or deletion on termination; timeline (30 days typical); certification of deletion; exceptions for legal retention clearly stated | Data retained indefinitely; continued processing post-termination |
| 9 | **Audit rights** | Controller or appointed third-party auditor access; reasonable notice period (30 days typical); scope covers processing facilities, systems, personnel; frequency (annual minimum); cost allocation | No verification of compliance; accountability gap |
| 10 | **International transfers** | No transfer without controller authorization; transfer mechanism specified; TIA completed; supplementary measures documented | Unlawful transfers; Schrems II violations; significant penalties |

---

## International Transfer Mechanisms

### SCC Module Selection (EU Commission SCCs, June 2021)

| Module | Transfer Scenario | When to Use |
|--------|------------------|-------------|
| **Module 1: C2C** | Controller to Controller | Data sharing between independent controllers |
| **Module 2: C2P** | Controller to Processor | Most common — controller engages processor outside EEA |
| **Module 3: P2P** | Processor to Sub-processor | Processor engages sub-processor outside EEA |
| **Module 4: P2C** | Processor to Controller | Processor in EEA transfers back to non-EEA controller |

### SCC Implementation Checklist

| # | Item | Details |
|---|------|---------|
| 1 | Module selection | Correct module for party roles; may need multiple modules for complex chains |
| 2 | Annex I completion | Parties identified; data exporter/importer; contact details; description of transfer |
| 3 | Annex II completion | Technical and organizational security measures (specific, not generic) |
| 4 | Annex III completion | Sub-processor list (if Module 2/3 with general authorization) |
| 5 | Optional clauses | Docking clause (Clause 7); governing law and jurisdiction selections |
| 6 | No modification of core clauses | SCCs cannot be modified; supplementary clauses can be added if not contradicting |

### UK International Data Transfer Mechanisms

| Mechanism | Description | When to Use |
|-----------|-------------|-------------|
| UK Addendum to EU SCCs | Addendum tables added to EU SCCs | Transfers from UK using EU SCC framework |
| UK IDTA | Standalone UK International Data Transfer Agreement | Alternative to EU SCCs + Addendum |
| UK adequacy regulations | UK equivalency decisions | Transfers to countries UK deems adequate |
| Transitional provisions | Legacy mechanisms during transition | Existing arrangements pre-UK GDPR |

### Transfer Impact Assessment (TIA) Requirements

Every SCC-based transfer requires a TIA under Schrems II:

| Step | Action | Documentation |
|------|--------|---------------|
| 1 | Map the data flow | What data, to whom, which country, purpose |
| 2 | Identify applicable law in recipient country | Surveillance laws, government access powers, intelligence sharing |
| 3 | Assess if third-country law impinges on SCC guarantees | Proportionality, necessity, judicial oversight, remedies |
| 4 | Identify supplementary measures | Technical (encryption, pseudonymization), organizational (policies, training), contractual (additional commitments) |
| 5 | Document the assessment | Retain for accountability; review annually or on material change |
| 6 | Re-assess periodically | Monitor legal developments; update if recipient country laws change |

### Supplementary Measures

| Category | Examples |
|----------|---------|
| Technical | End-to-end encryption with controller-held keys; pseudonymization before transfer; split processing; transport encryption |
| Organizational | Strict purpose limitation policies; access minimization; internal governance for government requests; transparency reporting |
| Contractual | Warrant canary; commitment to challenge government access; immediate notification of access requests; additional audit rights |

---

## Common DPA Issues

| # | Issue | Risk Level | Standard Position | Negotiation Guidance |
|---|-------|-----------|-------------------|---------------------|
| 1 | **Vague security measures** — "commercially reasonable" or "industry standard" without specifics | High | Require specific measures listed in Annex (encryption standards, access controls, testing frequency) | Push for ISO 27001 certification or SOC 2 Type II report as baseline |
| 2 | **Unlimited sub-processing** — general authorization with no notification or objection right | High | Require 30-day prior notification of new sub-processors with objection right and termination option | Accept general authorization only with robust notification mechanism |
| 3 | **Inadequate breach notification timeline** — "reasonable time" or >72 hours | High | Require 24-48 hour notification to allow controller to meet GDPR 72-hour deadline to SA | 36-hour maximum to allow controller assessment time |
| 4 | **No meaningful audit right** — paper audit only, or audit limited to SOC report | Medium | Require on-site audit right (annually minimum) plus right to appoint third-party auditor | Accept SOC 2 Type II plus right to on-site audit on cause |
| 5 | **Unclear data deletion** — no timeline, no certification, broad retention exceptions | Medium | Require 30-day deletion post-termination with written certification; retention exceptions limited to specific legal obligations with citation | Accept 90-day maximum deletion window |
| 6 | **Liability cap covers DPA** — processor caps liability for data protection breaches at service agreement level | Medium | DPA liability should be uncapped or at minimum higher cap than service agreement | Negotiate separate DPA liability cap at 2-3x annual fees |
| 7 | **Missing international transfer provisions** — DPA silent on where data is processed | High | Require explicit data location list; any transfer requires prior consent; SCC execution | Include approved locations Annex; change triggers re-approval |
| 8 | **No DPIA cooperation** — processor not obligated to assist with impact assessments | Medium | Require processor to provide information necessary for controller DPIA per Art. 28(3)(f) | Include specific information processor must provide |

---

## Practical Considerations

### Liability and Indemnification

| Consideration | What to Check | Standard Position |
|---------------|---------------|-------------------|
| Liability alignment | DPA liability not less than service agreement | DPA liability should equal or exceed service agreement caps |
| Indemnification for processor breach | Processor indemnifies controller for fines/claims caused by processor's GDPR violation | Mutual indemnification for respective GDPR breaches |
| Insurance requirements | Cyber liability and professional indemnity insurance | Require certificates of insurance; minimums aligned with data volume and sensitivity |
| Regulatory fine allocation | Who bears fines if imposed on controller due to processor's breach | Processor bears fines attributable to processor's non-compliance |

### Termination Alignment

| Consideration | What to Check | Standard Position |
|---------------|---------------|-------------------|
| DPA term matches service agreement | DPA does not expire before service agreement | Co-terminus with service agreement |
| Data return mechanism | Format, timeline, method for data return | Machine-readable format within 30 days; controller's choice of return or deletion |
| Post-termination processing | Clear prohibition after return/deletion | No processing after data return/deletion except as required by law |
| Transition assistance | Support during migration to new processor | Reasonable transition assistance for 90 days post-termination |

### Data Locations and Security

| Consideration | What to Check | Standard Position |
|---------------|---------------|-------------------|
| Data processing locations | All locations where data is processed, stored, or accessed | Named data centers; country-level at minimum; change notification |
| Security standards | Certifications, audit reports, pen testing | ISO 27001 or SOC 2 Type II; annual pen testing; vulnerability management |
| Encryption standards | At rest, in transit, key management | AES-256 at rest; TLS 1.2+ in transit; customer-managed keys option |
| Access controls | Personnel access, MFA, privileged access management | Role-based access; MFA required; privileged access logged |
| Incident response | Tested plan, communication procedures | Annual tabletop exercises; dedicated security contact |

---

## DPA Review Workflow

### Step-by-Step Review Process

| Step | Action | Time Estimate |
|------|--------|---------------|
| 1 | **Confirm party roles** — Is the counterparty a processor or joint controller? Review actual data flows, not just label. | 15 min |
| 2 | **Check Art. 28 required elements** — Walk through the 14-item checklist above. Flag any missing elements. | 30 min |
| 3 | **Verify 10 processor obligations** — Review each obligation for completeness and specificity. | 45 min |
| 4 | **Assess international transfers** — Identify all transfer destinations; verify mechanism for each (SCC module, adequacy, etc.) | 30 min |
| 5 | **Review sub-processor provisions** — Check current sub-processor list; verify notification/objection mechanism. | 15 min |
| 6 | **Evaluate practical considerations** — Liability caps, insurance, termination, data locations. | 30 min |
| 7 | **Document findings** — Create redline or issue list with risk ratings and requested amendments. | 30 min |
| 8 | **Negotiate amendments** — Prioritize by risk; prepare fallback positions. | Variable |
| 9 | **Final sign-off** — Legal, DPO, and business sign-off before execution. | 15 min |

### Risk Rating Framework

| Rating | Description | Action Required |
|--------|-------------|-----------------|
| Critical | Missing Art. 28 required element; no transfer mechanism; no breach notification | Must resolve before signing |
| High | Vague security measures; unlimited sub-processing; inadequate audit rights | Should resolve before signing; escalate if processor resists |
| Medium | Liability cap concerns; missing insurance; unclear data locations | Negotiate improvement; accept with documented risk if necessary |
| Low | Minor wording preferences; formatting; non-material terms | Document preference; accept if processor's standard |
