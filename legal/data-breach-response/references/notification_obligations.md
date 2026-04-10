# Data Breach Notification Obligations

Multi-regulation notification requirements for personal data breaches including GDPR, CCPA, HIPAA, PCI DSS, NIS2, state breach notification laws, and AI Act.

---

## Table of Contents

- [GDPR Notification](#gdpr-notification)
- [CCPA Notification](#ccpa-notification)
- [HIPAA Notification](#hipaa-notification)
- [PCI DSS Notification](#pci-dss-notification)
- [NIS2 Notification](#nis2-notification)
- [AI Act Serious Incident Reporting](#ai-act-serious-incident-reporting)
- [US State Breach Notification Overview](#us-state-breach-notification-overview)
- [Cross-Border Notification Rules](#cross-border-notification-rules)
- [Controller vs Processor Obligations](#controller-vs-processor-obligations)
- [Phased Notification Guidance](#phased-notification-guidance)
- [Notification Content Requirements](#notification-content-requirements)

---

## GDPR Notification

### Art. 33 — Notification to Supervisory Authority

| Aspect | Requirement |
|--------|-------------|
| **Who notifies** | Controller |
| **Notify whom** | Competent supervisory authority (SA) under Art. 55 |
| **Timeline** | Without undue delay, not later than 72 hours after becoming aware |
| **Trigger** | Personal data breach, unless unlikely to result in risk to rights and freedoms |
| **Exemption** | Only if breach is "unlikely to result in a risk to the rights and freedoms of natural persons" — must be documented |

**Art. 33(3) Required content:**

| Element | Description |
|---------|-------------|
| Nature of breach | Categories and approximate number of data subjects and records |
| DPO contact | Name and contact details of DPO or other point of contact |
| Consequences | Likely consequences of the breach |
| Measures | Measures taken or proposed to address the breach, including mitigation |

**Art. 33(4) Phased notification:** Where it is not possible to provide all information at the same time, the information may be provided in phases without undue further delay.

**Art. 33(5) Documentation:** Controller shall document any personal data breaches, comprising the facts, effects, and remedial action taken. This documentation must enable the SA to verify compliance. Applies to ALL breaches, even those not notified.

### Art. 34 — Communication to Data Subjects

| Aspect | Requirement |
|--------|-------------|
| **Who notifies** | Controller |
| **Notify whom** | Affected data subjects |
| **Timeline** | Without undue delay |
| **Trigger** | Breach "likely to result in a high risk to the rights and freedoms of natural persons" |
| **Language** | Clear and plain language |

**Art. 34(3) Exemptions from individual notification:**

| Exemption | Condition |
|-----------|-----------|
| **(a) Encryption/unintelligibility** | Controller implemented measures rendering data unintelligible (e.g., strong encryption with key not compromised) |
| **(b) Subsequent measures** | Controller has taken subsequent measures ensuring high risk is no longer likely to materialize |
| **(c) Disproportionate effort** | Individual notification would involve disproportionate effort — in which case public communication or similar measure must be used instead |

---

## CCPA Notification

### California Consumer Privacy Act (as amended by CPRA)

| Aspect | Requirement |
|--------|-------------|
| **Who notifies** | Business (any entity meeting CCPA thresholds) |
| **Notify whom** | Affected California residents |
| **Timeline** | "Most expedient time possible and without unreasonable delay" |
| **Trigger** | Unauthorized access to unencrypted and unredacted personal information |

**Personal information under CCPA breach provisions (Civ. Code 1798.81.5):**

| Data Type | Examples |
|-----------|---------|
| SSN | Social Security number |
| Driver's license / state ID | License number, identification card number |
| Financial account | Account number + access code/password |
| Medical / health insurance | Medical information, health insurance information |
| Biometric | Fingerprint, retina, iris, or other unique biometric data |
| Username + password/security question | Credentials enabling access to online account |

**Notice requirements:**

| Element | Requirement |
|---------|-------------|
| Method | Written notice or electronic notice (per consent) |
| Content | Name and contact of notifying entity; types of PI subject to breach; date, estimated date, or date range of breach; description of incident; toll-free telephone number for inquiries |
| Substitute notice | If >500,000 affected or cost >$250,000: email + conspicuous website posting + major statewide media |
| AG notification | If >500 California residents affected |

---

## HIPAA Notification

### Health Insurance Portability and Accountability Act

| Aspect | Requirement |
|--------|-------------|
| **Who notifies** | Covered entity (healthcare providers, health plans, healthcare clearinghouses) |
| **Notify whom** | Affected individuals, HHS, and potentially media |
| **Timeline** | Without unreasonable delay, no later than 60 calendar days from discovery |
| **Trigger** | Breach of unsecured Protected Health Information (PHI) |

**Notification tiers:**

| Affected Individuals | Requirements |
|---------------------|-------------|
| <500 | Notify individuals within 60 days; log with HHS annually |
| >=500 in single state/jurisdiction | Notify individuals + prominent local media within 60 days; notify HHS within 60 days |
| >=500 total | Notify individuals; notify HHS within 60 days (immediate posting on HHS breach portal) |

**Breach presumption:** Any unauthorized acquisition, access, use, or disclosure of PHI is presumed to be a breach unless the covered entity demonstrates a low probability that PHI was compromised based on a 4-factor risk assessment:

| Factor | Assessment |
|--------|-----------|
| 1. Nature and extent of PHI | What data elements were involved |
| 2. Unauthorized person | Who gained access or to whom was it disclosed |
| 3. PHI actually acquired/viewed | Was PHI actually accessed or only potentially exposed |
| 4. Extent of risk mitigation | What steps were taken to reduce harm |

**Safe harbor:** PHI rendered unusable, unreadable, or indecipherable through encryption per NIST guidelines (or destruction) is NOT "unsecured PHI" — breach notification rules do not apply.

---

## PCI DSS Notification

### Payment Card Industry Data Security Standard

| Aspect | Requirement |
|--------|-------------|
| **Who notifies** | Merchant, service provider, or acquiring bank |
| **Notify whom** | Card brands (Visa, Mastercard, etc.) via acquiring bank |
| **Timeline** | Immediately / within 24 hours (varies by card brand) |
| **Trigger** | Known or suspected compromise of cardholder data |

**Card brand specific requirements:**

| Brand | Notification Timeline | Additional Requirements |
|-------|----------------------|------------------------|
| Visa | Within 24 hours to acquirer | Forensic investigation by PFI within 72 hours |
| Mastercard | Immediately upon detection | Account Data Compromise event report |
| American Express | Within 24 hours | Engage PFI within 5 business days |
| Discover | Within 48 hours | Cooperate with Discover investigation |

**Cardholder data elements:**

| Data Element | Storage Permitted | Notification Trigger |
|-------------|-------------------|---------------------|
| Primary Account Number (PAN) | Yes (encrypted) | Yes if compromised |
| Cardholder name | Yes | Yes if with PAN |
| Expiration date | Yes | Yes if with PAN |
| Service code | Yes | Yes if with PAN |
| Full magnetic stripe / CVV2 / PIN | No (never store) | Always if compromised |

---

## NIS2 Notification

### Network and Information Security Directive 2 (EU 2022/2555)

| Aspect | Requirement |
|--------|-------------|
| **Who notifies** | Essential and important entities |
| **Notify whom** | Competent CSIRT and, where applicable, competent authority |
| **Trigger** | Significant incident (as defined by member state transposition) |

**Notification timeline (Art. 23):**

| Phase | Timeline | Content |
|-------|----------|---------|
| **Early warning** | Within 24 hours of becoming aware | Whether incident is suspected of being caused by unlawful or malicious acts; whether it could have cross-border impact |
| **Incident notification** | Within 72 hours of becoming aware | Update to early warning; initial assessment of severity and impact; indicators of compromise where applicable |
| **Intermediate report** | Upon request of CSIRT | Status update with relevant information |
| **Final report** | Within 1 month of incident notification | Detailed description; root cause; mitigation measures; cross-border impact if applicable |

**Significant incident criteria (Art. 23(3)):**

| Criterion | Description |
|-----------|-------------|
| (a) | Has caused or is capable of causing severe operational disruption of services or financial loss |
| (b) | Has affected or is capable of affecting other natural or legal persons by causing considerable material or non-material damage |

---

## AI Act Serious Incident Reporting

### EU AI Act (2024/1689) Art. 62

| Aspect | Requirement |
|--------|-------------|
| **Who reports** | Providers of high-risk AI systems placed on EU market |
| **Report to** | Market surveillance authority of member state where incident occurred |
| **Timeline** | Within 15 days of becoming aware (or immediately if death/serious health damage) |
| **Trigger** | Serious incident involving high-risk AI system |

**Serious incident definition (Art. 3(49)):**

| Type | Description |
|------|-------------|
| Death | AI system caused or contributed to death of a person |
| Serious damage to health | Physical or psychological harm |
| Serious damage to property | Property damage or significant environmental damage |
| Fundamental rights violation | Serious and irreversible breach of fundamental rights |

**Relationship to GDPR:**
- AI Act Art. 62 reporting is SEPARATE from GDPR Art. 33/34 breach notification
- Both may apply to the same incident (e.g., AI system breach involving personal data)
- Different timelines: GDPR 72h vs. AI Act 15 days (or immediate for death/health)
- Different authorities: GDPR supervisory authority vs. AI Act market surveillance authority

---

## US State Breach Notification Overview

All 50 US states have breach notification laws. Key variations:

| State | Timeline | AG Notification Threshold | Notable Provisions |
|-------|----------|--------------------------|-------------------|
| **California** | Most expedient time | >500 residents | Broadest PI definition; private right of action for certain breaches |
| **New York** | Most expedient time | Any number | SHIELD Act expanded PI definition; broad security requirements |
| **Texas** | Within 60 days | >250 residents | AG notification within 60 days |
| **Florida** | Within 30 days | >500 residents | AG within 30 days; 30-day individual notification |
| **Illinois** | Most expedient time | Any number | BIPA for biometric data (private right of action) |
| **Massachusetts** | As soon as practicable | Any number | AG and Office of Consumer Affairs notification |
| **Virginia** | Without unreasonable delay | >1,000 residents | AG notification; consumer reporting agency notification |
| **Colorado** | Within 30 days | >500 residents | AG notification within 30 days |
| **Washington** | Within 30 days | >500 residents | AG notification within 30 days |
| **Connecticut** | Within 60 days | Any number | AG notification without unreasonable delay |

**Common elements across state laws:**

| Element | Typical Requirement |
|---------|-------------------|
| Covered data | SSN, driver's license, financial account + access, medical, biometric (varies) |
| Encryption safe harbor | Most states exempt encrypted data (if key not compromised) |
| Good faith exception | Most states exempt good-faith acquisition by employee/agent |
| AG notification | Threshold varies (any number to 500+) |
| Consumer reporting agencies | Typically required if >1,000 affected in that state |

---

## Cross-Border Notification Rules

### GDPR One-Stop-Shop (Art. 56)

| Scenario | Lead SA | Notification Target |
|----------|---------|-------------------|
| Single establishment in one member state | SA of that member state | That SA |
| Main establishment in one member state, processing across EU | SA of main establishment | Lead SA (who coordinates with concerned SAs) |
| No main establishment but processing EU data | SA of member state most affected | That SA (may need to notify multiple) |
| Processor breach | N/A for processor — controller determines | Controller's lead SA |

### Multi-Regulation Cross-Border

| If processing involves... | Notify under... | Timeline |
|--------------------------|----------------|----------|
| EU data subjects' personal data | GDPR (Art. 33/34) | 72h to SA; without undue delay to subjects |
| California residents' personal info | CCPA | Most expedient time |
| US patients' health info | HIPAA | 60 days |
| Payment card data | PCI DSS | 24h to card brands |
| Essential/important entity in EU | NIS2 (Art. 23) | 24h early warning + 72h notification |
| High-risk AI system | AI Act (Art. 62) | 15 days (immediate if death/health) |

**Best practice:** Notify under the most stringent applicable timeline. If GDPR (72h), NIS2 (24h), and PCI (24h) all apply, prepare for 24h notification and align content for all recipients.

---

## Controller vs Processor Obligations

| Obligation | Controller | Processor |
|------------|-----------|-----------|
| Detect and investigate breach | Primary responsibility | Assist; notify controller of own detection |
| Notify supervisory authority (Art. 33) | **Yes** — sole obligation | **No** — notify controller only |
| Notify data subjects (Art. 34) | **Yes** — sole obligation | **No** |
| Notify controller of breach | N/A | **Yes** — without undue delay (Art. 33(2)) |
| Determine severity | **Yes** | Provide information to support assessment |
| Decide on notification | **Yes** | No decision authority |
| Document breach (Art. 33(5)) | **Yes** — all breaches | **Yes** — assist controller; maintain own records |
| Contractual notification deadline | N/A | Per DPA terms (commonly 24h or 48h) |

### Processor-Specific Obligations

| Obligation | Detail |
|------------|--------|
| **Without undue delay** | Art. 33(2) requires processor to notify controller after becoming aware — no specific hour limit, but "without undue delay" is strict |
| **DPA contractual terms** | Most DPAs specify 24h or 48h — contractual obligation may be stricter than statutory |
| **Assistance** | Processor must assist controller in ensuring compliance with Art. 33-34 obligations (Art. 28(3)(f)) |
| **Sub-processor** | If sub-processor discovers breach, sub-processor notifies processor, processor notifies controller — chain notification |

---

## Phased Notification Guidance

### GDPR Art. 33(4) — Phased Notification

When full information is not available within the 72-hour window, GDPR explicitly permits phased notification.

**Phase 1: Initial notification (within 72h)**

| Content | Status |
|---------|--------|
| Nature of breach | Provide what is known |
| Categories of data subjects | Estimate if exact numbers unavailable |
| DPO contact | Required |
| Likely consequences | Preliminary assessment |
| Measures taken | Containment measures underway |
| Reason for delay | Explain why full information unavailable |

**Phase 2: Supplementary notification (without undue further delay)**

| Content | Status |
|---------|--------|
| Updated scope | Revised numbers and categories |
| Updated consequences | Based on investigation findings |
| Root cause | If determined |
| Additional measures | Remediation actions taken since initial notification |
| Data subject notification status | Whether subjects were notified and how |

### Best Practices for Phased Notification

| Practice | Rationale |
|----------|-----------|
| File initial notification early | Better to notify within 72h with partial information than to miss the deadline |
| Clearly mark as "phased" / "initial" | SA expects follow-up; prevents confusion about completeness |
| Set internal deadline for supplementary | Aim for 14 days after initial; no later than 30 days |
| Track notification status | Maintain record of all notifications (initial + supplementary) |
| Align supplementary with investigation milestones | Update SA as investigation completes phases (containment → analysis → remediation) |

---

## Notification Content Requirements

### Comparison Across Regulations

| Element | GDPR Art. 33 (SA) | GDPR Art. 34 (Subject) | CCPA | HIPAA | NIS2 |
|---------|-------------------|------------------------|------|-------|------|
| Nature of breach | Yes | Yes (clear, plain) | Yes | Yes | Yes |
| Data categories | Yes | Yes | Yes (types of PI) | Yes (types of PHI) | N/A |
| Number affected | Approximate | N/A | N/A | Number affected | Severity/impact |
| DPO / contact | Yes | Yes | Contact info | Contact info | Contact info |
| Consequences | Yes | Yes | N/A | Description of what entity is doing | Impact assessment |
| Measures taken | Yes | Yes | N/A | Steps to protect from harm | Mitigation measures |
| Date of breach | N/A | N/A | Date or date range | Date | Date of detection |
| Recommendations to subjects | N/A | Yes | N/A | Steps individuals can take | N/A |
| Indicators of compromise | N/A | N/A | N/A | N/A | Yes (NIS2 Art. 23) |
| Cross-border impact | N/A | N/A | N/A | N/A | Yes |
| Root cause | N/A (supplementary) | N/A | N/A | N/A | Yes (final report) |

### Data Subject Communication Template Elements

Per GDPR Art. 34, communication to data subjects must include at minimum:

| Element | Example Content |
|---------|----------------|
| What happened | "We detected unauthorized access to our customer database on [date]" |
| What data was affected | "Your name, email address, and encrypted password were accessed" |
| What we are doing | "We have contained the incident, reset all passwords, and engaged forensic investigators" |
| What you can do | "We recommend you change your password on any service where you used the same password" |
| Who to contact | "Contact our DPO at [email] or call [phone] for questions" |
| Clear and plain language | No legal jargon; accessible to general public; translated if multilingual user base |
