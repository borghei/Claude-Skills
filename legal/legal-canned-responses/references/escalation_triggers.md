# Legal Escalation Triggers Reference

Comprehensive guide to universal and category-specific escalation triggers for legal inquiry handling.

## Table of Contents

- [Escalation Protocol](#escalation-protocol)
- [Universal Triggers](#universal-triggers)
- [Category-Specific Triggers](#category-specific-triggers)
- [Escalation Response Procedure](#escalation-response-procedure)
- [Customization Guidelines](#customization-guidelines)
- [Severity Classification](#severity-classification)
- [Routing Directory](#routing-directory)

## Escalation Protocol

When any escalation trigger is detected, the following protocol applies immediately:

| Step | Action | Detail |
|------|--------|--------|
| 1. Stop | Halt template response | Do not send any templated or automated response |
| 2. Alert | Notify designated counsel | Contact the routing destination specified by the trigger |
| 3. Explain | Provide escalation context | Include matched triggers, severity, and original inquiry |
| 4. Recommend | Suggest routing | Follow the routing recommendation for the matched trigger |
| 5. Draft | Mark for review | If a draft is prepared, mark "FOR COUNSEL REVIEW ONLY" |

## Universal Triggers

Universal triggers apply to ALL inquiry categories. If any universal trigger matches, the inquiry must be escalated regardless of category.

### UT-001: Potential or Active Litigation

| Field | Value |
|-------|-------|
| Severity | HIGH |
| Routing | General Counsel |
| Keywords | litigation, lawsuit, sue/suing, filed complaint, court order, injunction, legal action, class action |
| Reason | Legal exposure requires immediate counsel assessment to preserve rights and manage defense |

### UT-002: Regulatory Investigation

| Field | Value |
|-------|-------|
| Severity | HIGH |
| Routing | General Counsel / Regulatory Affairs |
| Keywords | regulatory investigation, regulator, enforcement action, compliance investigation, regulatory inquiry, sanction |
| Reason | Regulatory responses require strategic approach; wrong response can worsen exposure |

### UT-003: Government or Law Enforcement Contact

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Routing | General Counsel (Immediate) |
| Keywords | government inquiry, law enforcement, FBI, DOJ, Department of Justice, SEC, FTC, FDA, police, prosecutor, grand jury, subpoena, warrant, civil investigative demand |
| Reason | Constitutional and procedural rights at stake; improper response can waive protections |

### UT-004: Binding Legal Commitment

| Field | Value |
|-------|-------|
| Severity | HIGH |
| Routing | Contracts / General Counsel |
| Keywords | binding commitment, sign agreement, execute contract, guarantee, indemnify, waiver, release of claims |
| Reason | Cannot create legal obligations without proper authority and counsel review |

### UT-005: Criminal Liability Exposure

| Field | Value |
|-------|-------|
| Severity | CRITICAL |
| Routing | General Counsel (Immediate) |
| Keywords | criminal, fraud, bribery, corruption, embezzlement, money laundering, whistleblower, criminal liability, criminal investigation |
| Reason | Criminal exposure requires immediate privilege-protected counsel involvement |

### UT-006: Media Attention

| Field | Value |
|-------|-------|
| Severity | HIGH |
| Routing | General Counsel + Communications |
| Keywords | media, press, reporter, journalist, newspaper, news article, Wall Street Journal, New York Times, Bloomberg, Reuters, public statement, press release |
| Reason | Reputational risk requires coordinated legal-communications response strategy |

### UT-007: Unprecedented Situation

| Field | Value |
|-------|-------|
| Severity | MEDIUM |
| Routing | Senior Counsel |
| Keywords | first time, never before/seen/encountered, unprecedented, no precedent, novel issue/situation, uncharted |
| Reason | No existing template applies; bespoke legal analysis required |

### UT-008: Multi-Jurisdictional Conflict

| Field | Value |
|-------|-------|
| Severity | HIGH |
| Routing | International / General Counsel |
| Keywords | multi-jurisdictional, cross-border, international dispute, conflict of laws, foreign government/authority/court, extraterritorial |
| Reason | Cross-border legal complexity may involve conflicting obligations |

## Category-Specific Triggers

### Data Subject Requests (DSR)

| ID | Trigger | Severity | Routing | Keywords |
|----|---------|----------|---------|----------|
| DSR-001 | Minor Data Subject | HIGH | Privacy Counsel | minor, child, under [age], parent consent |
| DSR-002 | Litigation Hold Conflict | HIGH | Litigation + Privacy Counsel | litigation hold, legal hold, preservation |
| DSR-003 | HR/Employment Matter | MEDIUM | Employment Counsel + Privacy | employee file/record, HR, human resources, termination, disciplinary |
| DSR-004 | Special Category Data | HIGH | Privacy Counsel | health, medical, biometric, genetic, racial, ethnic, sexual, religious, political, trade union |

**DSR Escalation Notes:**
- Minors: COPPA (US) requires verifiable parental consent; GDPR Art. 8 sets age threshold at 16 (member states may lower to 13)
- Litigation hold conflicts: DSR fulfillment may require deletion that conflicts with hold; cannot resolve without counsel
- Special categories: Art. 9 GDPR processing requires explicit consent or specific legal basis

### Discovery/Litigation Holds

| ID | Trigger | Severity | Routing | Keywords |
|----|---------|----------|---------|----------|
| DIS-001 | Criminal Liability | CRITICAL | General Counsel (Immediate) | criminal, fraud, destruction of evidence, spoliation |
| DIS-002 | Unclear Hold Scope | HIGH | Litigation Counsel | unclear scope, what documents/data, how far back, scope question |
| DIS-003 | Deletion Conflict | CRITICAL | Litigation Counsel (Immediate) | already deleted, purged, destroyed, auto-delete, retention policy |

**Discovery Escalation Notes:**
- Spoliation: Any indication that relevant data may have been deleted after hold triggers immediate escalation
- Scope questions: Over-preservation is safer than under-preservation; counsel must define boundaries

### Privacy Inquiries

| ID | Trigger | Severity | Routing | Keywords |
|----|---------|----------|---------|----------|
| PRI-001 | Data Breach | CRITICAL | Privacy Counsel + CISO | breach, leak, unauthorized access, data incident, compromised |

**Privacy Escalation Notes:**
- GDPR Art. 33: 72-hour notification obligation to supervisory authority
- State breach notification laws (US): Varying timelines and requirements

### Vendor Legal Questions

| ID | Trigger | Severity | Routing | Keywords |
|----|---------|----------|---------|----------|
| VEN-001 | Vendor Dispute/Threat | HIGH | Contracts / General Counsel | threatening, dispute, breach of contract, terminate agreement, penalty |

### NDA Requests

| ID | Trigger | Severity | Routing | Keywords |
|----|---------|----------|---------|----------|
| NDA-001 | Competitor NDA | HIGH | General Counsel + Business | competitor, competing, rival |
| NDA-002 | Government/Military | HIGH | Government Contracts Counsel | government, military, defense, classified, security clearance |

**NDA Escalation Notes:**
- Competitor NDAs may create antitrust risk; scope must be carefully limited
- Government/military NDAs involve ITAR, EAR, and classified information handling requirements

### Subpoena/Legal Process

| ID | Trigger | Severity | Routing | Keywords |
|----|---------|----------|---------|----------|
| SUB-001 | Always Escalate | CRITICAL | General Counsel (Immediate) | ALL subpoena inquiries |

**Subpoena Escalation Notes:**
- Every subpoena or legal process matter must be reviewed by counsel without exception
- Privilege review required before any document production
- Third-party data may require notice to data subjects
- Cross-border subpoenas may conflict with foreign data protection laws (e.g., GDPR blocking statutes)

### Insurance Notifications

| ID | Trigger | Severity | Routing | Keywords |
|----|---------|----------|---------|----------|
| INS-001 | Coverage Dispute | HIGH | Insurance / General Counsel | deny/denied/denial, coverage dispute, reservation of rights, bad faith |

## Escalation Response Procedure

### When Escalation Is Detected

```
1. STOP - Do not send any templated response
2. ALERT - Notify the routing destination immediately
3. EXPLAIN - Provide:
   - Original inquiry text
   - Matched trigger(s) with IDs
   - Severity classification
   - Recommended routing
4. RECOMMEND - Suggest next steps based on trigger type
5. DRAFT - If any preliminary response prepared:
   - Mark "FOR COUNSEL REVIEW ONLY"
   - Do NOT send until counsel approves
   - Document the hold in tracking system
```

### Escalation Documentation

| Field | Required | Description |
|-------|----------|-------------|
| Inquiry date | Yes | Date/time the inquiry was received |
| Inquiry source | Yes | Who submitted the inquiry (name, email, role) |
| Category | Yes | Response category (DSR, vendor, etc.) |
| Trigger ID(s) | Yes | Which trigger(s) matched |
| Severity | Yes | Highest matched severity level |
| Routing | Yes | Where escalation was sent |
| Counsel response | Yes | Counsel's direction and date |
| Resolution | Yes | Final outcome and date |

## Customization Guidelines

### Tone Customization

| Audience | Tone Adjustment |
|----------|----------------|
| Internal employee | Direct, informative; reference internal policies |
| External customer | Professional, empathetic; reference privacy notices |
| Regulatory body | Formal, precise; reference legal obligations |
| Counterparty counsel | Legal-professional; reference contractual terms |
| Insurance carrier | Factual, timely; reference policy terms |

### Jurisdiction Customization

| Jurisdiction | Key Adjustments |
|-------------|----------------|
| EU/EEA | Reference GDPR articles; use "data subject" terminology; include DPA contact |
| US (California) | Reference CCPA/CPRA; use "consumer" terminology; include opt-out rights |
| US (Federal) | Reference SOX/Dodd-Frank as applicable; use federal terminology |
| UK | Reference UK GDPR/DPA 2018; reference ICO; use UK-specific terminology |
| Multi-jurisdiction | Use broadest protections; reference all applicable frameworks |

### Adding Custom Triggers

When adding organization-specific triggers:

| Consideration | Guidance |
|---------------|----------|
| Specificity | Use specific terms, not generic words that cause false positives |
| Testing | Test new triggers against 50+ sample inquiries before deployment |
| Review | Have counsel approve all custom triggers |
| Documentation | Document rationale for each custom trigger |
| Maintenance | Review custom triggers quarterly; retire unused ones |

## Severity Classification

| Severity | Definition | Response Time | Approver |
|----------|-----------|---------------|----------|
| CRITICAL | Immediate legal risk; rights may be waived or lost | Within 1 hour | General Counsel |
| HIGH | Significant legal risk; requires counsel strategy | Within 4 hours | Senior Counsel |
| MEDIUM | Moderate risk; counsel guidance needed | Within 24 hours | Counsel |
| LOW | Minor risk; informational escalation | Within 48 hours | Legal Operations |

## Routing Directory

| Destination | Types of Matters | Typical Triggers |
|-------------|-----------------|------------------|
| General Counsel | Litigation, government, criminal, strategic | UT-001, UT-003, UT-005 |
| Privacy Counsel | Data protection, DSRs, breaches | DSR-001, DSR-004, PRI-001 |
| Litigation Counsel | Discovery, holds, disputes | DIS-001, DIS-002, DIS-003 |
| Employment Counsel | Employee matters, HR | DSR-003 |
| Contracts Counsel | Vendor, NDA, commitments | UT-004, VEN-001 |
| Regulatory Affairs | Regulatory inquiries | UT-002 |
| Communications | Media, public statements | UT-006 |
| Insurance Counsel | Coverage, claims | INS-001 |
| International Counsel | Cross-border, multi-jurisdiction | UT-008 |
| Government Contracts | Government/military | NDA-002 |
