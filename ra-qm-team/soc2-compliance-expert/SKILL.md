---
name: soc2-compliance-expert
description: SOC 2 Type I and Type II compliance management covering all Trust Services Criteria, audit preparation, evidence collection, infrastructure security validation, and continuous compliance monitoring
triggers:
  - soc 2 audit
  - trust services criteria
  - type II report
  - SOC 2 readiness
  - SOC 2 gap analysis
  - security controls audit
  - availability controls
  - processing integrity
  - confidentiality controls
  - privacy controls
  - SOC 2 evidence collection
  - audit preparation
---

# SOC 2 Compliance Expert

Production-ready SOC 2 Type I and Type II compliance management covering all Trust Services Criteria (TSC), infrastructure security validation, evidence collection automation, and end-to-end audit preparation.

## Table of Contents

- [SOC 2 Overview](#soc-2-overview)
- [Trust Services Criteria Deep-Dive](#trust-services-criteria-deep-dive)
- [Readiness Assessment Workflow](#readiness-assessment-workflow)
- [Evidence Collection Framework](#evidence-collection-framework)
- [Infrastructure Security Checks](#infrastructure-security-checks)
- [Access Control Deep-Dive](#access-control-deep-dive)
- [Vendor and Third-Party Risk Management](#vendor-and-third-party-risk-management)
- [Employee Security Awareness Training](#employee-security-awareness-training)
- [Incident Response Plan Requirements](#incident-response-plan-requirements)
- [Business Continuity and Disaster Recovery](#business-continuity-and-disaster-recovery)
- [Audit Timeline and Observation Period](#audit-timeline-and-observation-period)
- [Common Audit Findings and Remediation](#common-audit-findings-and-remediation)
- [SOC 2 Report Types and Distribution](#soc-2-report-types-and-distribution)
- [Tools](#tools)
- [References](#references)

---

## SOC 2 Overview

### What Is SOC 2?

SOC 2 (System and Organization Controls 2) is an auditing framework developed by the American Institute of Certified Public Accountants (AICPA). It evaluates an organization's information systems against five Trust Services Criteria: Security, Availability, Processing Integrity, Confidentiality, and Privacy.

SOC 2 reports are the gold standard for demonstrating that a service organization has implemented effective controls to protect customer data and ensure reliable service delivery.

### Type I vs Type II

| Aspect | Type I | Type II |
|--------|--------|---------|
| **Scope** | Design of controls at a point in time | Design AND operating effectiveness over a period |
| **Duration** | Single date (snapshot) | Observation period (3-12 months, typically 6-12) |
| **Evidence** | Control descriptions, design review | Control descriptions + testing of operational evidence |
| **Cost** | $20K-$60K (first audit) | $40K-$150K (first audit) |
| **Timeline** | 1-3 months to prepare | 6-15 months (includes observation period) |
| **Value** | Demonstrates control design intent | Proves controls work consistently over time |
| **Customer Preference** | Acceptable for early-stage companies | Required by enterprise customers |
| **Renewal** | Typically one-time stepping stone | Annual renewal required |

**Recommendation:** Start with Type I to validate control design, then transition to Type II within 6 months. Most enterprise buyers require Type II reports less than 12 months old.

### AICPA Standards

SOC 2 audits are performed under:
- **SSAE 18** (Statement on Standards for Attestation Engagements No. 18)
- **AT-C Section 105** - Concepts Common to All Attestation Engagements
- **AT-C Section 205** - Examination Engagements
- **TSP Section 100** - 2017 Trust Services Criteria for Security, Availability, Processing Integrity, Confidentiality, and Privacy

The Trust Services Criteria are organized around the **COSO 2013 Internal Control Framework** (Committee of Sponsoring Organizations of the Treadway Commission), which provides 17 principles across 5 components.

### Audit Window Considerations

- **Type I:** Select a date after all controls are implemented and documented
- **Type II:** Minimum 3-month observation period (6-12 months preferred by most auditors)
- **Bridge Letters:** Cover gaps between report periods for customer requests
- **Carve-outs vs Inclusive Method:** Decide how to handle subservice organizations (cloud providers, SaaS tools)

---

## Trust Services Criteria Deep-Dive

### CC1: Control Environment

The foundation of all other controls. Establishes organizational commitment to integrity, ethical values, and competence.

**COSO Principles Covered:**
1. Commitment to integrity and ethical values
2. Board of directors independence and oversight
3. Organizational structure, authority, and responsibility
4. Commitment to competence
5. Accountability enforcement

**Required Controls:**

| Control | Description | Evidence |
|---------|-------------|----------|
| CC1.1 | Code of conduct/ethics policy | Signed acknowledgments, policy document |
| CC1.2 | Board/management oversight structure | Org chart, board meeting minutes, committee charters |
| CC1.3 | Defined roles and responsibilities | Job descriptions, RACI matrices |
| CC1.4 | Hiring and competency standards | Background check policy, training records |
| CC1.5 | Performance evaluation and accountability | Review templates, disciplinary procedures |

**Tone at the Top:**
- Executive leadership must visibly champion security
- Security metrics should be reported to the board quarterly
- Security budget allocation demonstrates organizational commitment
- Information security policy must be signed by CEO/CISO

**Board Oversight Requirements:**
- Documented board or committee charter for risk oversight
- Quarterly security briefings to the board or audit committee
- Board review and approval of information security policy annually
- Independent directors with cybersecurity expertise (recommended)

### CC2: Communication and Information

Ensures the organization generates, uses, and communicates quality information to support internal controls.

**Required Controls:**

| Control | Description | Evidence |
|---------|-------------|----------|
| CC2.1 | Internal communication of objectives and responsibilities | Security awareness materials, policy portal |
| CC2.2 | External communication with customers and regulators | Privacy policy, security page, breach notification procedures |
| CC2.3 | System description accuracy and completeness | Documented system boundaries, data flow diagrams |

**Internal Communication Requirements:**
- Information security policy distributed to all employees
- Security awareness training completion tracking
- Incident reporting channels documented and accessible
- Change management notifications to affected parties
- Security bulletin distribution for emerging threats

**External Communication Requirements:**
- Public-facing security page or trust center
- Customer notification procedures for incidents
- SLA documentation and status pages
- Regulatory notification procedures (breach laws)
- Subprocessor list maintenance and update notifications

**System Description (Section III of SOC 2 Report):**
- Principal service commitments and system requirements
- Components of the system (infrastructure, software, people, procedures, data)
- System boundaries and interconnections
- Complementary user entity controls (CUECs)
- Complementary subservice organization controls (CSOCs)

### CC3: Risk Assessment

Organization identifies and analyzes risks to achievement of its objectives.

**Required Controls:**

| Control | Description | Evidence |
|---------|-------------|----------|
| CC3.1 | Risk identification for business objectives | Risk register, annual risk assessment |
| CC3.2 | Fraud risk assessment | Fraud risk matrix, anti-fraud controls |
| CC3.3 | Change management risk identification | Change impact assessments, regulatory monitoring |
| CC3.4 | Risk assessment of significant changes | M&A risk reviews, new product security assessments |

**Risk Identification Process:**
1. Asset inventory and classification (data, systems, people)
2. Threat identification (internal, external, environmental)
3. Vulnerability assessment (technical, procedural, human)
4. Likelihood and impact scoring (qualitative or quantitative)
5. Risk treatment decisions (accept, mitigate, transfer, avoid)
6. Residual risk documentation and acceptance

**Fraud Risk Considerations:**
- Segregation of duties analysis
- Management override controls
- Financial reporting fraud risks
- Data manipulation risks
- Social engineering vulnerability assessment
- Insider threat program

**Change Management Risk:**
- New technology adoption risks
- Personnel changes (key-person dependencies)
- Regulatory changes impacting controls
- Business model changes affecting data handling
- Third-party relationship changes

### CC4: Monitoring Activities

Ongoing and periodic evaluations to ascertain whether controls are present and functioning.

**Required Controls:**

| Control | Description | Evidence |
|---------|-------------|----------|
| CC4.1 | Ongoing monitoring and separate evaluations | Continuous monitoring dashboards, periodic control testing |
| CC4.2 | Deficiency communication and remediation | Finding reports, remediation tracking, management reporting |

**Ongoing Monitoring:**
- Automated security monitoring (SIEM, IDS/IPS)
- Real-time alerting for control failures
- KPI/KRI dashboards for security metrics
- Automated compliance scanning (cloud posture management)
- Continuous vulnerability scanning

**Separate Evaluations:**
- Internal audit program (at least annual)
- Penetration testing (at least annual, quarterly recommended)
- Third-party security assessments
- Control self-assessments by process owners
- Tabletop exercises for incident response

**Deficiency Reporting:**
- Severity classification (critical, high, medium, low)
- Root cause analysis for all high/critical findings
- Remediation timelines with owner assignment
- Management reporting cadence (monthly minimum)
- Board/committee escalation thresholds

### CC5: Control Activities

Actions established by policies and procedures to mitigate risks.

**Required Controls:**

| Control | Description | Evidence |
|---------|-------------|----------|
| CC5.1 | Selection and development of control activities | Control design documentation, risk-control mapping |
| CC5.2 | Technology general controls | IT general controls documentation |
| CC5.3 | Policy and procedure deployment | Policy management system, version control, acknowledgments |

**Control Activity Categories:**
- **Preventive:** Access controls, input validation, encryption
- **Detective:** Logging, monitoring, anomaly detection, auditing
- **Corrective:** Incident response, backup restoration, patch management
- **Compensating:** Additional controls when primary controls have gaps

**Technology General Controls (ITGCs):**
- Logical access to programs and data
- Program change management
- Program development lifecycle
- Computer operations (job scheduling, backup, problem management)

**Policy Deployment Requirements:**
- Centralized policy management system
- Annual review and update cycle
- Version control with change tracking
- Employee acknowledgment tracking
- Exception management process with documented approvals

### CC6: Logical and Physical Access Controls

Controls over access to systems, data, and facilities.

**Required Controls:**

| Control | Description | Evidence |
|---------|-------------|----------|
| CC6.1 | Logical access security (authentication, authorization) | IAM configurations, SSO setup, MFA enforcement |
| CC6.2 | Access provisioning based on role | Role definitions, access request workflows |
| CC6.3 | Access modification and removal | Joiner/mover/leaver procedures, access reviews |
| CC6.4 | Physical access restrictions | Badge system logs, visitor logs, data center controls |
| CC6.5 | Logical access to assets removed upon termination | Offboarding checklists, access removal evidence |
| CC6.6 | External access points protection | Firewall rules, VPN configurations, WAF rules |
| CC6.7 | Data transmission encryption | TLS configurations, encryption standards |
| CC6.8 | Unauthorized or malicious software prevention | Endpoint protection, application whitelisting |

**Authentication Requirements:**
- Multi-factor authentication (MFA) enforced for all users
- Password policy: minimum 12 characters, complexity requirements
- Account lockout after 5 failed attempts
- Session timeout: 15 minutes for sensitive systems, 30 minutes general
- Single Sign-On (SSO) via SAML 2.0 or OIDC for all SaaS applications

**MFA Standards:**
- TOTP (Time-based One-Time Password): Minimum acceptable
- FIDO2/WebAuthn: Preferred (phishing-resistant)
- Hardware security keys (YubiKey 5 series): Required for privileged access
- SMS-based MFA: Not acceptable (SIM swap vulnerability)

**Access Review Cadence:**
- Privileged access: Quarterly
- Standard access: Semi-annual
- Service accounts: Quarterly
- Third-party access: Quarterly
- Dormant accounts: Monthly automated detection

**Physical Security:**
- Data center access: Biometric + badge + escort for visitors
- Office access: Badge system with audit trail
- Visitor management: Sign-in/sign-out, escort requirements
- Environmental controls: Fire suppression, HVAC monitoring, water detection
- CCTV: 90-day retention minimum at entry/exit points

### CC7: System Operations

Controls over system monitoring, incident management, and recovery.

**Required Controls:**

| Control | Description | Evidence |
|---------|-------------|----------|
| CC7.1 | Vulnerability management and detection | Vulnerability scan reports, patch management records |
| CC7.2 | Security event monitoring and anomaly detection | SIEM configurations, alert rules, monitoring dashboards |
| CC7.3 | Security incident evaluation and response | Incident response plan, incident tickets, post-mortems |
| CC7.4 | Business continuity planning | BCP document, DR runbooks, test results |
| CC7.5 | Recovery from incidents and disasters | Recovery procedures, RTO/RPO documentation, test results |

**Vulnerability Management Program:**
- External vulnerability scanning: Monthly minimum
- Internal vulnerability scanning: Monthly minimum
- Penetration testing: Annual minimum (quarterly for critical systems)
- Web application security testing: With each major release
- Remediation SLAs: Critical (24h), High (7d), Medium (30d), Low (90d)
- Container image scanning: On every build

**Change Management (System Operations):**
- Change Advisory Board (CAB) process for significant changes
- Emergency change procedures with post-hoc review
- Rollback plans required for all production changes
- Change testing in non-production environments
- Change calendar and blackout windows

**Incident Detection and Response:**
- 24/7 monitoring capability (SOC or managed service)
- Defined severity levels (SEV1-SEV4) with response SLAs
- Incident commander designation and escalation paths
- Communication templates for internal and external notification
- Post-incident review (blameless post-mortem) within 5 business days

### CC8: Change Management

Controls over system changes, including authorization, testing, and deployment.

**Required Controls:**

| Control | Description | Evidence |
|---------|-------------|----------|
| CC8.1 | Change authorization, design, development, and testing | Change tickets, approval workflows, test results |

**Change Authorization Process:**
1. Change request submission with business justification
2. Impact assessment (security, performance, compliance)
3. Peer code review (minimum one reviewer, two for critical systems)
4. Approval from change authority (manager/CAB based on risk level)
5. Testing in staging/pre-production environment
6. Deployment with rollback plan
7. Post-deployment validation
8. Change record closure with documentation

**Testing Requirements:**
- Unit tests for all code changes
- Integration tests for cross-system changes
- Security testing (SAST/DAST) for application changes
- Performance testing for infrastructure changes
- User acceptance testing (UAT) for significant changes

**Deployment Controls:**
- Automated deployment pipelines (CI/CD)
- Separation of development, staging, and production environments
- Production access restricted (no developer access to production data)
- Deployment audit trail with who, what, when
- Automated rollback capability

**Emergency Changes:**
- Defined criteria for emergency classification
- Abbreviated approval process (single authorized approver)
- Post-implementation review within 48 hours
- Retroactive documentation and full change record
- Trend tracking for emergency change frequency

### CC9: Risk Mitigation

Controls for mitigating risks through vendor management, business disruption planning, and risk transfer.

**Required Controls:**

| Control | Description | Evidence |
|---------|-------------|----------|
| CC9.1 | Vendor risk identification and assessment | Vendor risk assessments, due diligence records |
| CC9.2 | Business disruption risk management | BIA results, insurance certificates, risk transfer documentation |

**Vendor Management Requirements:**
- Vendor security questionnaire (SIG Lite or custom)
- Annual SOC 2 report review for critical vendors
- Contractual security requirements (DPA, SLA, right to audit)
- Vendor risk tiering (critical, high, medium, low)
- Annual reassessment of critical and high-risk vendors
- Subprocessor list maintenance

**Risk Transfer:**
- Cyber liability insurance coverage
- Technology errors and omissions (E&O) insurance
- Business interruption insurance
- Crime/fidelity insurance for fraud protection
- Annual coverage review against risk profile

### A1: Availability

Additional criteria for organizations including Availability in their SOC 2 scope.

**Required Controls:**

| Control | Description | Evidence |
|---------|-------------|----------|
| A1.1 | Capacity planning and performance monitoring | Capacity plans, monitoring dashboards, auto-scaling configs |
| A1.2 | Disaster recovery and business continuity | DR plan, failover testing, backup verification |
| A1.3 | Recovery testing and validation | DR test results, RTO/RPO achievement records |

**Capacity Planning:**
- Current utilization monitoring (CPU, memory, storage, network)
- Growth forecasting based on historical trends
- Auto-scaling configurations with limits
- Capacity threshold alerting (70%, 85%, 95%)
- Annual capacity planning review

**Disaster Recovery:**
- Recovery Time Objective (RTO): Defined per system tier
- Recovery Point Objective (RPO): Defined per data classification
- Multi-region/multi-AZ deployment for critical systems
- Automated failover for Tier 1 systems
- DR site maintained in different geographic region

**Backup and Restore:**
- Daily backups minimum for production data
- Point-in-time recovery capability for databases
- Backup encryption at rest and in transit
- Monthly backup restoration testing
- 30-day retention minimum (90 days recommended)
- Air-gapped or immutable backups for ransomware protection

**SLA Management:**
- Uptime commitment: 99.9% minimum (99.95% or 99.99% for critical)
- Scheduled maintenance windows documented
- Status page with real-time availability
- SLA credit/penalty structure
- Monthly availability reporting

### PI1: Processing Integrity

Additional criteria for organizations including Processing Integrity in scope.

**Required Controls:**

| Control | Description | Evidence |
|---------|-------------|----------|
| PI1.1 | Completeness, accuracy, timeliness, and authorization of processing | Data validation rules, reconciliation procedures, processing logs |
| PI1.2 | Error detection and correction | Error handling procedures, exception reports |
| PI1.3 | Input and output verification | Input validation rules, output reconciliation |
| PI1.4 | Processing authorization and scheduling | Job scheduling, approval workflows |
| PI1.5 | Data quality and integrity monitoring | Data quality dashboards, integrity checks |

**Data Processing Controls:**
- Input validation (type checking, range validation, format enforcement)
- Processing checksums and hash verification
- Duplicate detection and prevention
- Transaction sequencing and ordering guarantees
- Batch processing reconciliation (record counts, control totals)

**Error Handling:**
- Defined error codes and classifications
- Automated retry with exponential backoff
- Dead letter queues for failed messages
- Error notification and escalation procedures
- Error trend analysis and root cause correction

### C1: Confidentiality

Additional criteria for organizations including Confidentiality in scope.

**Required Controls:**

| Control | Description | Evidence |
|---------|-------------|----------|
| C1.1 | Confidential information identification and classification | Data classification policy, classification labels |
| C1.2 | Confidential information disposal | Data retention schedule, disposal procedures, certificates of destruction |

**Data Classification Levels:**
- **Public:** No restrictions (marketing materials, public docs)
- **Internal:** Company-internal only (internal memos, procedures)
- **Confidential:** Restricted access (customer data, financial records, PII)
- **Highly Confidential/Restricted:** Need-to-know only (encryption keys, trade secrets)

**Encryption Requirements:**
- Data at rest: AES-256 (minimum AES-128)
- Data in transit: TLS 1.2+ (TLS 1.3 preferred)
- Database encryption: Transparent Data Encryption (TDE) or field-level
- Key management: Hardware Security Module (HSM) for production keys
- Key rotation: Annual minimum (90 days for high-sensitivity)

**Data Disposal:**
- Cryptographic erasure for cloud storage
- DOD 5220.22-M or NIST 800-88 for physical media
- Certificate of destruction from disposal vendors
- Disposal tracking in asset management system
- Retention schedule aligned with legal/regulatory requirements

**NDA Management:**
- NDA required before sharing confidential information
- NDA register maintained with expiration tracking
- Annual review of active NDAs
- Mutual NDA template for vendor relationships
- Integration with vendor management program

### P1: Privacy

Additional criteria for organizations including Privacy in scope.

**Required Controls:**

| Control | Description | Evidence |
|---------|-------------|----------|
| P1.1 | Privacy notice and consent | Privacy policy, cookie consent, terms of service |
| P1.2 | Choice and consent management | Consent records, opt-out mechanisms |
| P1.3 | Personal information collection limitation | Data minimization analysis, collection justification |
| P1.4 | Use, retention, and disposal | Retention schedules, purpose limitation documentation |
| P1.5 | Access rights for data subjects | DSR procedures, response tracking |
| P1.6 | Disclosure to third parties | Subprocessor agreements, DPAs |
| P1.7 | Data quality assurance | Data accuracy procedures, correction workflows |
| P1.8 | Monitoring and enforcement | Privacy impact assessments, compliance monitoring |

**Notice Requirements:**
- Clear, conspicuous privacy notice
- Categories of personal information collected
- Purposes for collection and processing
- Third-party sharing disclosures
- Data subject rights explanation
- Cookie/tracking technology disclosures

**Consent Management:**
- Granular consent options (not all-or-nothing)
- Consent withdrawal mechanism (as easy as granting)
- Consent records with timestamp and version
- Age verification for minors' data
- Double opt-in for marketing communications

**Data Subject Rights:**
- Right to access (response within 30 days)
- Right to correction/rectification
- Right to deletion/erasure
- Right to data portability (machine-readable format)
- Right to restrict processing
- Right to object to processing
- Automated decision-making transparency

**Retention and Disposal:**
- Data retention schedule by category
- Automated retention enforcement
- Legal hold capability
- Disposal verification and logging
- Backup data included in retention scope

---

## Readiness Assessment Workflow

### Phase 1: Gap Analysis (Weeks 1-4)

1. **Scope Definition**
   - Determine which TSC categories to include (Security is mandatory)
   - Define system boundaries and components
   - Identify subservice organizations (carve-out vs inclusive)
   - Document principal service commitments

2. **Current State Assessment**
   - Inventory existing policies and procedures
   - Map current controls to TSC requirements
   - Interview process owners and control operators
   - Review existing audit reports and assessments
   - Run `soc2_readiness_checker.py` against organization configuration

3. **Gap Identification**
   - Document missing controls per TSC category
   - Identify controls that exist but lack evidence
   - Assess controls that exist but are not operating effectively
   - Prioritize gaps by risk and remediation effort

**Tool:** `scripts/soc2_readiness_checker.py` -- Automates gap analysis against all TSC categories

### Phase 2: Remediation (Weeks 5-16)

1. **Policy Development**
   - Draft/update information security policy
   - Create supporting procedures for each control domain
   - Establish policy review and approval workflows
   - Deploy policies via centralized management system

2. **Technical Controls Implementation**
   - Configure identity provider and enforce SSO/MFA
   - Deploy endpoint security (MDM, EDR, disk encryption)
   - Implement logging and monitoring (SIEM)
   - Configure backup and disaster recovery
   - Harden cloud infrastructure

3. **Process Implementation**
   - Establish access review procedures
   - Implement change management workflow
   - Create incident response procedures
   - Deploy vendor management program
   - Launch security awareness training

4. **Evidence Collection Setup**
   - Configure automated evidence collection
   - Establish evidence repository structure
   - Define evidence refresh cadence
   - Test evidence completeness

**Tool:** `scripts/evidence_collector.py` -- Generates checklists and tracks evidence collection status

### Phase 3: Pre-Audit (Weeks 17-20)

1. **Internal Readiness Assessment**
   - Conduct mock audit against all in-scope TSC
   - Validate evidence completeness and quality
   - Test control operating effectiveness
   - Run `soc2_infrastructure_auditor.py` for technical validation

2. **Remediate Pre-Audit Findings**
   - Address any remaining gaps
   - Strengthen evidence where auditor may question
   - Conduct management review of readiness

3. **Auditor Selection and Engagement**
   - Select CPA firm with SOC 2 experience
   - Negotiate scope, timeline, and fees
   - Schedule audit kickoff meeting
   - Prepare system description draft

**Tool:** `scripts/soc2_infrastructure_auditor.py` -- Validates infrastructure configurations against SOC 2 requirements

### Phase 4: Audit Execution (Observation Period + Fieldwork)

1. **Type I Audit** (if applicable)
   - Auditor reviews control design at a point in time
   - Management provides assertions
   - Auditor issues Type I report
   - Address any findings before Type II observation begins

2. **Type II Observation Period** (3-12 months)
   - Controls must operate consistently throughout
   - Evidence collected continuously
   - No control gaps or failures during period
   - Regular check-ins with auditor (quarterly recommended)

3. **Fieldwork** (2-4 weeks after observation period)
   - Auditor selects samples and tests controls
   - Management provides requested evidence
   - Auditor interviews key personnel
   - Draft report review
   - Final report issuance

---

## Evidence Collection Framework

### Evidence by TSC Category

| TSC | Evidence Type | Collection Method | Refresh Frequency |
|-----|---------------|-------------------|-------------------|
| CC1 | Code of conduct acknowledgments | HR system export | Annual |
| CC1 | Org chart, board minutes | Manual collection | Quarterly |
| CC2 | Security awareness training records | LMS export | Annual/ongoing |
| CC2 | System description document | Manual authoring | Annual + changes |
| CC3 | Risk assessment report | Annual assessment | Annual |
| CC3 | Risk register | GRC platform export | Quarterly |
| CC4 | Penetration test reports | Third-party vendor | Annual |
| CC4 | Vulnerability scan results | Scanner export | Monthly |
| CC5 | Policy documents with version history | Policy management system | Annual review |
| CC6 | Access review completion records | IAM/IGA platform | Quarterly |
| CC6 | MFA enrollment report | IdP dashboard | Monthly |
| CC6 | Terminated user access removal | HRIS + IdP correlation | Per event |
| CC7 | Vulnerability remediation tracking | Ticketing system | Ongoing |
| CC7 | Incident response records | Incident management tool | Per event |
| CC8 | Change tickets with approvals | ITSM/ticketing system | Per change |
| CC8 | Code review evidence | Git platform (PR history) | Per change |
| CC9 | Vendor risk assessments | GRC platform | Annual |
| CC9 | Vendor SOC 2 reports | Vendor request | Annual |
| A1 | Uptime monitoring reports | Monitoring platform | Monthly |
| A1 | DR test results | Manual documentation | Semi-annual |
| A1 | Backup verification logs | Backup system | Monthly |
| PI1 | Data validation/reconciliation reports | Application logs | Per process |
| C1 | Data classification inventory | Manual/automated | Annual |
| C1 | Encryption configuration evidence | Infrastructure configs | Quarterly |
| P1 | Privacy impact assessments | Manual documentation | Per new processing |
| P1 | DSR response tracking | Privacy management tool | Per request |

### Automation Strategies

**GRC Platforms:** Vanta, Drata, Secureframe, Laika, Tugboat Logic, AuditBoard
- Automated evidence collection via API integrations
- Continuous control monitoring
- Auditor collaboration portals
- Policy management with acknowledgment tracking

**Infrastructure-as-Evidence:**
- Cloud configuration snapshots (AWS Config, Azure Policy, GCP Org Policies)
- Infrastructure-as-Code (Terraform state as evidence of configuration)
- Git history as evidence of change management
- CI/CD pipeline logs as evidence of deployment controls

**Manual Evidence Optimization:**
- Create evidence collection calendar aligned with refresh frequencies
- Assign evidence owners per control domain
- Use standardized naming conventions for evidence artifacts
- Maintain evidence index with last-collected dates

**Tool:** `scripts/evidence_collector.py` -- Generates per-category checklists, tracks status, calculates readiness

---

## Infrastructure Security Checks

### Cloud Provider Security

#### AWS Security Controls
| Control | AWS Service | SOC 2 Mapping |
|---------|-------------|---------------|
| Encryption at rest | KMS, S3 default encryption | CC6.1, C1.1 |
| Encryption in transit | ACM, ALB/NLB TLS termination | CC6.7, C1.1 |
| Access management | IAM, SSO, Organizations | CC6.1-CC6.3 |
| Logging | CloudTrail, CloudWatch, VPC Flow Logs | CC7.2, CC4.1 |
| Network security | Security Groups, NACLs, WAF | CC6.6 |
| Configuration compliance | AWS Config, Security Hub | CC4.1, CC5.2 |
| Backup | AWS Backup, S3 versioning | A1.2 |
| Secrets | Secrets Manager, Parameter Store | CC6.1 |

#### Azure Security Controls
| Control | Azure Service | SOC 2 Mapping |
|---------|---------------|---------------|
| Encryption at rest | Azure Key Vault, Storage encryption | CC6.1, C1.1 |
| Encryption in transit | Application Gateway, Front Door | CC6.7, C1.1 |
| Access management | Azure AD, PIM, Conditional Access | CC6.1-CC6.3 |
| Logging | Azure Monitor, Log Analytics, NSG Flow Logs | CC7.2, CC4.1 |
| Network security | NSGs, Azure Firewall, WAF | CC6.6 |
| Configuration compliance | Azure Policy, Defender for Cloud | CC4.1, CC5.2 |
| Backup | Azure Backup, geo-redundant storage | A1.2 |
| Secrets | Key Vault | CC6.1 |

#### GCP Security Controls
| Control | GCP Service | SOC 2 Mapping |
|---------|-------------|---------------|
| Encryption at rest | Cloud KMS, default encryption | CC6.1, C1.1 |
| Encryption in transit | Cloud Load Balancing, Certificate Manager | CC6.7, C1.1 |
| Access management | Cloud IAM, Identity Platform, BeyondCorp | CC6.1-CC6.3 |
| Logging | Cloud Audit Logs, Cloud Logging | CC7.2, CC4.1 |
| Network security | VPC Firewall, Cloud Armor | CC6.6 |
| Configuration compliance | Security Command Center, Policy Intelligence | CC4.1, CC5.2 |
| Backup | Cloud Storage, persistent disk snapshots | A1.2 |
| Secrets | Secret Manager | CC6.1 |

### DNS Security

| Check | Requirement | SOC 2 Mapping |
|-------|-------------|---------------|
| **SPF** | `v=spf1` record published, `-all` qualifier | CC6.6, CC2.2 |
| **DKIM** | 2048-bit RSA minimum, key rotation annual | CC6.6, CC2.2 |
| **DMARC** | Policy `p=reject` or `p=quarantine` | CC6.6, CC2.2 |
| **DNSSEC** | Domain signed, DS records at registrar | CC6.6 |
| **CAA** | CAA records restricting certificate issuance | CC6.6 |

### TLS/SSL Configuration

| Check | Requirement | SOC 2 Mapping |
|-------|-------------|---------------|
| **Minimum TLS** | TLS 1.2 (TLS 1.3 preferred) | CC6.7 |
| **Cipher suites** | AEAD ciphers only (AES-GCM, ChaCha20-Poly1305) | CC6.7 |
| **Certificate** | SHA-256+ signature, 2048-bit RSA or P-256 ECDSA | CC6.7 |
| **HSTS** | `max-age=31536000; includeSubDomains; preload` | CC6.7 |
| **Certificate management** | Automated renewal (Let's Encrypt, ACM) | CC6.7 |
| **OCSP stapling** | Enabled for performance and privacy | CC6.7 |

### Endpoint Security

| Check | Requirement | SOC 2 Mapping |
|-------|-------------|---------------|
| **MDM enrollment** | All company devices enrolled | CC6.8 |
| **Disk encryption** | FileVault (macOS), BitLocker (Windows) | CC6.1, C1.1 |
| **EDR/Antivirus** | CrowdStrike, SentinelOne, or equivalent | CC6.8 |
| **OS patching** | Critical patches within 14 days | CC7.1 |
| **Screen lock** | Auto-lock after 5 minutes | CC6.1 |
| **Firewall** | Host firewall enabled | CC6.6 |
| **USB restrictions** | Removable media blocked or monitored | C1.1 |

### Network Security

| Check | Requirement | SOC 2 Mapping |
|-------|-------------|---------------|
| **Segmentation** | Production, staging, development isolated | CC6.6 |
| **WAF** | Web Application Firewall on all public endpoints | CC6.6 |
| **DDoS protection** | Cloud provider DDoS (AWS Shield, Cloudflare) | A1.1 |
| **VPN/Zero Trust** | Remote access via VPN or ZTNA | CC6.6 |
| **Egress filtering** | Outbound traffic restricted to known destinations | CC6.6 |

### Container Security

| Check | Requirement | SOC 2 Mapping |
|-------|-------------|---------------|
| **Image scanning** | Trivy, Snyk, or equivalent on every build | CC7.1 |
| **Base images** | Minimal, hardened base images (distroless/Alpine) | CC7.1 |
| **Runtime policies** | No privileged containers, read-only root fs | CC6.1 |
| **Registry** | Private registry with access controls | CC6.1 |
| **Kubernetes** | RBAC, network policies, pod security standards | CC6.1, CC6.6 |
| **Secrets** | External secrets operator, never in images | CC6.1 |

### CI/CD Pipeline Security

| Check | Requirement | SOC 2 Mapping |
|-------|-------------|---------------|
| **Signed commits** | GPG-signed commits required | CC8.1 |
| **Branch protection** | PR required, approvals enforced, no force push | CC8.1 |
| **SAST** | Static analysis on every PR (Semgrep, SonarQube) | CC7.1, CC8.1 |
| **DAST** | Dynamic testing in staging | CC7.1 |
| **Dependency scanning** | SCA on every build (Dependabot, Snyk) | CC7.1 |
| **Secret scanning** | Pre-commit hooks and CI scanning | CC6.1 |
| **Build reproducibility** | Deterministic builds, SBOM generation | CC8.1, PI1.1 |
| **Deployment audit** | Immutable deployment logs | CC8.1, CC4.1 |

**Tool:** `scripts/soc2_infrastructure_auditor.py` -- Validates infrastructure configurations against all checks above

---

## Access Control Deep-Dive

### Identity Provider Configuration

**SSO Requirements:**
- SAML 2.0 or OpenID Connect (OIDC) for all SaaS applications
- Centralized identity provider (Okta, Azure AD, Google Workspace, OneLogin)
- Just-in-time (JIT) provisioning where supported
- Group-based access assignment (not individual)
- Session duration: 8-12 hours maximum

**SCIM Provisioning:**
- Automated user provisioning and deprovisioning
- Group membership synchronization
- Real-time deprovisioning on termination
- Attribute mapping standardization
- SCIM-enabled applications inventory

### MFA Enforcement

| Method | Security Level | Use Case |
|--------|----------------|----------|
| SMS/Voice | Not Acceptable | Deprecated - SIM swap risk |
| Email OTP | Not Acceptable | Phishing risk |
| TOTP (Authenticator app) | Acceptable | Standard user access |
| Push notification | Good | Standard user access with IdP app |
| FIDO2/WebAuthn | Excellent | All users (phishing-resistant) |
| Hardware key (YubiKey) | Excellent | Privileged access, admin accounts |

**MFA Policy:**
- MFA required for all users, no exceptions
- Hardware keys required for: admin accounts, production access, root/break-glass
- MFA registration within 24 hours of onboarding
- Lost device procedures documented
- MFA bypass requires CISO approval with time-limited exception

### Privileged Access Management (PAM)

**Just-in-Time (JIT) Access:**
- No standing privileged access (zero standing privileges)
- Time-bound access grants (maximum 8 hours)
- Approval workflow for privileged access requests
- Automated revocation after time window expires
- Full session recording for privileged access

**Break-Glass Procedures:**
- Break-glass accounts stored in secure vault (sealed)
- Dual-custody access (two approvers required)
- Usage triggers immediate security review
- Credentials rotated after every use
- Annual testing of break-glass procedures

**Service Account Governance:**
- Inventory of all service accounts with owners
- No interactive login for service accounts
- API key rotation: 90 days maximum
- Service account access reviews: Quarterly
- Shared credential prohibition
- Secrets stored in vault (HashiCorp Vault, AWS Secrets Manager)

### API Key and Secret Rotation

| Secret Type | Maximum Lifetime | Rotation Method |
|-------------|-----------------|-----------------|
| API keys | 90 days | Automated rotation via vault |
| Database credentials | 90 days | Dynamic secrets (Vault) |
| SSH keys | 1 year | Certificate-based preferred |
| TLS certificates | 1 year (90 days recommended) | Automated via ACME/ACM |
| Encryption keys | 1 year | Key management service |
| OAuth tokens | Per session | Refresh token rotation |
| Personal access tokens | 90 days | Developer self-service rotation |

---

## Vendor and Third-Party Risk Management

### Vendor Risk Assessment Process

1. **Classification** -- Tier vendors by data access and criticality
   - **Critical:** Processes/stores customer data, system availability dependency
   - **High:** Access to internal data, significant business impact
   - **Medium:** Limited data access, moderate business impact
   - **Low:** No data access, minimal business impact

2. **Due Diligence Requirements by Tier**

| Tier | SOC 2 Report | Security Questionnaire | Pen Test | Contract Review | Reassessment |
|------|-------------|----------------------|----------|----------------|--------------|
| Critical | Required | Full SIG | Review results | Full legal review | Annual |
| High | Required | SIG Lite | Request summary | Security addendum | Annual |
| Medium | Preferred | Custom short-form | Not required | Standard terms | Biennial |
| Low | Not required | Not required | Not required | Standard terms | As needed |

3. **Contractual Requirements**
   - Data Processing Agreement (DPA)
   - Security requirements addendum
   - Right to audit clause
   - Breach notification obligations (24-72 hours)
   - Data return/destruction on termination
   - Subprocessor notification and approval
   - Insurance requirements

### Subprocessor Management
- Maintain current subprocessor list
- Customer notification 30 days before new subprocessor
- Objection mechanism for customers
- Annual subprocessor reassessment

---

## Employee Security Awareness Training

### Training Requirements

| Training Type | Audience | Frequency | Duration |
|---------------|----------|-----------|----------|
| Security awareness | All employees | Annual + onboarding | 30-60 min |
| Phishing simulation | All employees | Monthly | Ongoing |
| Secure development | Engineering | Annual | 2-4 hours |
| Incident response | IR team | Quarterly tabletop | 1-2 hours |
| Privacy awareness | Data handlers | Annual | 30-60 min |
| Privileged access | Admins/SREs | Annual | 1-2 hours |

### Training Content Requirements
- Social engineering and phishing recognition
- Password security and MFA usage
- Data classification and handling
- Incident reporting procedures
- Clean desk and screen lock policies
- Acceptable use policy review
- Remote work security practices
- Physical security awareness

### Tracking and Reporting
- 100% completion required (30-day grace period for new hires)
- Completion tracked in LMS with exportable reports
- Non-completion escalation to manager, then HR
- Phishing simulation failure triggers additional training
- Annual training effectiveness assessment

---

## Incident Response Plan Requirements

### IRP Structure

1. **Preparation**
   - Incident response team defined with contact information
   - Communication channels established (dedicated Slack, bridge line)
   - Incident management tool configured (PagerDuty, Opsgenie)
   - Runbooks for common incident types
   - Legal and PR contacts on retainer

2. **Detection and Analysis**
   - Monitoring and alerting coverage
   - Severity classification criteria
   - Initial triage procedures
   - Escalation matrix

3. **Containment, Eradication, Recovery**
   - Short-term containment (isolate affected systems)
   - Evidence preservation procedures
   - Root cause identification
   - System restoration and validation
   - Return to normal operations

4. **Post-Incident Activity**
   - Blameless post-mortem within 5 business days
   - Lessons learned documentation
   - Control improvement recommendations
   - Customer/regulatory notification assessment
   - Metrics tracking (MTTD, MTTR, MTTC)

### Severity Levels

| Severity | Definition | Response Time | Update Frequency | Example |
|----------|-----------|---------------|-------------------|---------|
| SEV1 | Critical business impact, data breach | 15 minutes | Every 30 minutes | Active data exfiltration |
| SEV2 | Major impact, service degradation | 30 minutes | Every 1 hour | Production outage |
| SEV3 | Moderate impact, partial degradation | 4 hours | Every 4 hours | Non-critical system failure |
| SEV4 | Low impact, no customer effect | Next business day | Daily | Failed security scan |

### Breach Notification Requirements
- Internal notification: Immediately upon confirmation
- Customer notification: Within 72 hours (per contract/regulation)
- Regulatory notification: Per applicable law (GDPR: 72h, CCPA: expedient)
- Law enforcement: As required by legal counsel
- Insurance carrier: Per policy terms (typically 24-48 hours)

---

## Business Continuity and Disaster Recovery

### Business Impact Analysis (BIA)

For each critical system, document:
- Maximum Tolerable Downtime (MTD)
- Recovery Time Objective (RTO)
- Recovery Point Objective (RPO)
- Minimum Business Continuity Objective (MBCO)
- Dependencies (upstream and downstream systems)

### DR Strategy by Tier

| Tier | RTO | RPO | Strategy | Example |
|------|-----|-----|----------|---------|
| Tier 1 | < 1 hour | < 15 min | Active-active multi-region | Core API, database |
| Tier 2 | < 4 hours | < 1 hour | Warm standby | Internal tools, admin |
| Tier 3 | < 24 hours | < 24 hours | Backup/restore | Reporting, analytics |
| Tier 4 | < 72 hours | < 72 hours | Rebuild from IaC | Dev/staging environments |

### DR Testing Requirements
- Full DR failover test: Annual minimum
- Tabletop exercise: Semi-annual
- Backup restoration test: Monthly
- Communication tree test: Semi-annual
- Results documented with lessons learned
- RTO/RPO achievement tracking

---

## Audit Timeline and Observation Period

### Typical Timeline (First SOC 2)

| Phase | Duration | Activities |
|-------|----------|------------|
| Scoping | 2-4 weeks | Define TSC, system boundaries, auditor selection |
| Gap Analysis | 2-4 weeks | Assess current controls, identify gaps |
| Remediation | 8-16 weeks | Implement missing controls, policies, procedures |
| Type I Audit | 2-4 weeks | Point-in-time control design assessment |
| Type II Observation | 3-12 months | Controls operate, evidence collected continuously |
| Type II Fieldwork | 2-4 weeks | Auditor testing, evidence review, interviews |
| Report Issuance | 2-4 weeks | Draft review, management response, final report |

### Observation Period Best Practices
- Start observation period only after all controls are operational
- Maintain evidence collection discipline throughout entire period
- Document any control exceptions or deviations immediately
- Conduct quarterly self-assessments during observation period
- Maintain regular communication with auditor (quarterly check-ins)
- Do not make significant control changes during observation period

### Annual Renewal
- Begin renewal planning 3 months before observation period ends
- Maintain continuous compliance between audit periods
- Address any prior-year findings before new observation period
- Bridge letters available for gaps between reports

---

## Common Audit Findings and Remediation

### Top 10 Most Common Findings

| # | Finding | Severity | Remediation |
|---|---------|----------|-------------|
| 1 | Incomplete or untimely access reviews | High | Automate reviews via IGA platform, set calendar reminders |
| 2 | Missing MFA for some systems | High | Enforce MFA via IdP conditional access, eliminate exceptions |
| 3 | Incomplete security awareness training | Medium | Automate enrollment, escalation for non-completion |
| 4 | Change management bypasses | High | Enforce branch protection, remove direct production access |
| 5 | Vendor SOC 2 reports not collected | Medium | Maintain vendor review calendar, automate reminders |
| 6 | Incomplete system description | Medium | Engage auditor early for system description review |
| 7 | Missing or outdated policies | Medium | Implement policy management tool, annual review cycle |
| 8 | Insufficient logging coverage | High | Audit log coverage, centralize in SIEM, alert on gaps |
| 9 | No DR testing evidence | High | Schedule semi-annual DR tests, document results |
| 10 | Terminated user access not removed promptly | Critical | Automate deprovisioning via SCIM, same-day requirement |

### Handling Exceptions and Deviations
- Document exception reason, risk accepted, compensating controls
- Management approval required for all exceptions
- Time-bound exceptions with expiration dates
- Exception register reviewed quarterly
- Auditor informed of all material exceptions proactively

---

## SOC 2 Report Types and Distribution

### Report Components

1. **Section I:** Independent Service Auditor's Report (opinion letter)
2. **Section II:** Management's Assertion
3. **Section III:** Description of the System
4. **Section IV:** Trust Services Criteria, Controls, Tests, and Results (Type II)
5. **Section V:** Other Information (optional)

### Report Types

| Report | Content | Distribution |
|--------|---------|-------------|
| SOC 2 Type I | Control design at a point in time | Restricted use (NDA required) |
| SOC 2 Type II | Control design + operating effectiveness | Restricted use (NDA required) |
| SOC 3 | General use summary (no control details) | Public distribution allowed |

### Distribution Best Practices
- Require mutual NDA before sharing SOC 2 reports
- Use secure portal for report distribution (not email attachments)
- Track all report recipients
- Watermark reports with recipient name
- Share only current-period reports (archive prior years)
- SOC 3 report or trust center for public-facing assurance

---

## Tools

### SOC 2 Readiness Checker
`scripts/soc2_readiness_checker.py`

Automated readiness assessment against all Trust Services Criteria. Accepts a JSON configuration describing an organization's current controls and produces a scored readiness report with gap identification and remediation guidance.

```bash
# Full readiness assessment with human-readable output
python scripts/soc2_readiness_checker.py --config org-controls.json

# JSON output for programmatic use
python scripts/soc2_readiness_checker.py --config org-controls.json --format json

# Check specific TSC categories only
python scripts/soc2_readiness_checker.py --config org-controls.json --categories security availability

# Include cloud provider control mapping
python scripts/soc2_readiness_checker.py --config org-controls.json --cloud-mapping
```

### Evidence Collector
`scripts/evidence_collector.py`

Evidence collection management tool that generates per-category checklists, tracks evidence status, and calculates overall audit readiness percentage.

```bash
# Generate evidence checklist for all TSC categories
python scripts/evidence_collector.py --generate-checklist --categories all

# Track evidence status from existing collection file
python scripts/evidence_collector.py --status evidence-tracker.json

# Update evidence item status
python scripts/evidence_collector.py --update evidence-tracker.json --item CC6.1-MFA --status collected

# Generate readiness dashboard
python scripts/evidence_collector.py --dashboard evidence-tracker.json

# Export for auditor
python scripts/evidence_collector.py --export evidence-tracker.json --format json
```

### Infrastructure Auditor
`scripts/soc2_infrastructure_auditor.py`

Technical infrastructure audit tool that validates configurations against SOC 2 requirements covering DNS, TLS, cloud security, endpoint security, CI/CD, and secrets management.

```bash
# Full infrastructure audit
python scripts/soc2_infrastructure_auditor.py --config infra-config.json

# Audit specific domains
python scripts/soc2_infrastructure_auditor.py --config infra-config.json --domains dns tls cloud

# JSON output with severity ratings
python scripts/soc2_infrastructure_auditor.py --config infra-config.json --format json

# Generate sample configuration template
python scripts/soc2_infrastructure_auditor.py --generate-template
```

---

## References

- [Trust Services Criteria Guide](references/trust-services-criteria-guide.md) -- Complete TSC reference with control objectives, implementation guidance, and common audit questions
- [Infrastructure Security Controls](references/infrastructure-security-controls.md) -- Cloud, DNS, TLS, endpoint, container, and CI/CD security reference with specific configurations
- [Audit Preparation Playbook](references/audit-preparation-playbook.md) -- End-to-end audit preparation guide with timelines, checklists, and cost estimation
