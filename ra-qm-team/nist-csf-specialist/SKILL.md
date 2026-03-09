---
name: nist-csf-specialist
description: NIST Cybersecurity Framework 2.0 implementation, assessment, and compliance management. Use for NIST cybersecurity framework, CSF 2.0, NIST compliance, cybersecurity risk management, NIST controls, NIST assessment, cybersecurity maturity, NIST CSF profile, cybersecurity governance, CSF gap analysis, cybersecurity program development, and cross-framework compliance mapping.
---

# NIST CSF 2.0 Specialist

Implement, assess, and manage cybersecurity programs aligned with the NIST Cybersecurity Framework 2.0 — the definitive standard for organizational cybersecurity risk management.

---

## Table of Contents

- [Trigger Phrases](#trigger-phrases)
- [Quick Start](#quick-start)
- [Tools](#tools)
- [NIST CSF 2.0 Overview](#nist-csf-20-overview)
- [Six Core Functions](#six-core-functions)
- [CSF Profiles](#csf-profiles)
- [CSF Tiers](#csf-tiers)
- [Cross-Framework Mapping](#cross-framework-mapping)
- [Infrastructure Security Assessment](#infrastructure-security-assessment)
- [Maturity Assessment Workflow](#maturity-assessment-workflow)
- [Implementation Roadmap](#implementation-roadmap)
- [Reference Guides](#reference-guides)
- [Validation Checkpoints](#validation-checkpoints)

---

## Trigger Phrases

Use this skill when you hear:
- "NIST cybersecurity framework"
- "CSF 2.0"
- "NIST compliance"
- "cybersecurity risk management"
- "NIST controls"
- "NIST assessment"
- "cybersecurity maturity"
- "NIST CSF profile"
- "cybersecurity governance"
- "cybersecurity program assessment"
- "CSF gap analysis"
- "cross-framework compliance mapping"

---

## Quick Start

### Assess Cybersecurity Maturity

```bash
python scripts/csf_maturity_assessor.py --input assessment.json --target-tier 3 --output maturity_report.json
```

### Map Controls Across Frameworks

```bash
python scripts/csf_control_mapper.py --source-framework nist-csf --target-framework iso27001 --output mapping.json
```

### Generate Gap Analysis

```bash
python scripts/csf_maturity_assessor.py --input assessment.json --target-tier 4 --format markdown --output gap_analysis.md
```

### Multi-Framework Unified Matrix

```bash
python scripts/csf_control_mapper.py --source-framework nist-csf --target-framework all --output unified_matrix.json
```

---

## Tools

### csf_maturity_assessor.py

Comprehensive maturity assessment engine for NIST CSF 2.0.

**Capabilities:**
- Scores each function and category on a 1–4 tier scale
- Compares current profile against target profile
- Generates prioritized gap analysis with remediation actions
- Maps gaps to specific CSF subcategories
- Produces JSON or Markdown output

**Usage:**

```bash
# Full maturity assessment with gap analysis
python scripts/csf_maturity_assessor.py \
  --input current_state.json \
  --target-tier 3 \
  --output report.json

# Markdown report for executive presentation
python scripts/csf_maturity_assessor.py \
  --input current_state.json \
  --target-tier 4 \
  --format markdown \
  --output executive_report.md

# Assess specific functions only
python scripts/csf_maturity_assessor.py \
  --input current_state.json \
  --functions GOVERN,IDENTIFY,PROTECT \
  --target-tier 3 \
  --output partial_report.json
```

**Input Format (current_state.json):**

```json
{
  "organization": "Acme Corp",
  "assessment_date": "2026-03-09",
  "assessor": "Security Team",
  "functions": {
    "GOVERN": {
      "GV.OC": {
        "score": 2,
        "evidence": "Mission documented, partial stakeholder mapping",
        "notes": "Legal requirements catalog incomplete"
      },
      "GV.RM": {
        "score": 1,
        "evidence": "No formal risk management strategy",
        "notes": "Risk appetite not defined"
      }
    },
    "IDENTIFY": {
      "ID.AM": {
        "score": 3,
        "evidence": "CMDB maintained, automated discovery",
        "notes": "Shadow IT gap exists"
      }
    }
  }
}
```

### csf_control_mapper.py

Cross-framework control mapping engine.

**Capabilities:**
- Maps NIST CSF 2.0 categories to ISO 27001, SOC 2, HIPAA, PCI-DSS
- Identifies overlapping controls for multi-framework programs
- Generates unified control matrices
- Highlights gaps unique to each framework

**Usage:**

```bash
# Map CSF to ISO 27001
python scripts/csf_control_mapper.py \
  --source-framework nist-csf \
  --target-framework iso27001 \
  --output iso_mapping.json

# Map CSF to all supported frameworks
python scripts/csf_control_mapper.py \
  --source-framework nist-csf \
  --target-framework all \
  --output unified_matrix.json

# Map specific functions only
python scripts/csf_control_mapper.py \
  --source-framework nist-csf \
  --target-framework soc2 \
  --functions GOVERN,PROTECT \
  --output soc2_mapping.json

# Markdown output for documentation
python scripts/csf_control_mapper.py \
  --source-framework nist-csf \
  --target-framework iso27001 \
  --format markdown \
  --output mapping_report.md
```

---

## NIST CSF 2.0 Overview

### What Changed in CSF 2.0

Released in February 2024, NIST CSF 2.0 represents a major evolution from the original 2014 framework and 2018 v1.1 update:

**Expanded Scope:** CSF 2.0 applies to ALL organizations — not just critical infrastructure. Small businesses, government agencies, higher education, and nonprofits are now explicitly in scope.

**New GOVERN Function:** The most significant change. GOVERN elevates cybersecurity governance to a top-level function, recognizing that executive leadership, policy, and oversight are prerequisites for effective cybersecurity.

**Enhanced Supply Chain Focus:** Cybersecurity Supply Chain Risk Management (C-SCRM) is now a category under GOVERN, reflecting the reality that supply chain attacks are a primary threat vector.

**Improved Guidance:** CSF 2.0 includes implementation examples and quick-start guides that were absent in earlier versions. The framework is more actionable and prescriptive while maintaining its flexible, risk-based approach.

**Profile Updates:** Profiles are now more clearly defined as organizational profiles (describing current/target states) and community profiles (sector-specific templates).

### Framework Architecture

```
┌─────────────────────────────────────────────────────┐
│                    CSF CORE                          │
│                                                     │
│  ┌─────────┐                                        │
│  │ GOVERN  │ ← NEW: Overarching governance          │
│  └────┬────┘                                        │
│       │                                             │
│  ┌────▼────┐  ┌─────────┐  ┌────────┐  ┌─────────┐│
│  │IDENTIFY │→ │ PROTECT  │→ │ DETECT │→ │ RESPOND ││
│  └─────────┘  └─────────┘  └────────┘  └────┬────┘│
│                                              │      │
│                                         ┌────▼────┐ │
│                                         │ RECOVER │ │
│                                         └─────────┘ │
├─────────────────────────────────────────────────────┤
│                   PROFILES                           │
│          Current State ↔ Target State                │
├─────────────────────────────────────────────────────┤
│                    TIERS                             │
│    Partial → Risk Informed → Repeatable → Adaptive  │
└─────────────────────────────────────────────────────┘
```

---

## Six Core Functions

### 1. GOVERN (GV) — NEW in CSF 2.0

The GOVERN function establishes and monitors the organization's cybersecurity risk management strategy, expectations, and policy. It is the connective tissue across all other functions.

#### GV.OC — Organizational Context

Understanding the organization's mission, stakeholder expectations, and dependencies is the foundation for all cybersecurity decisions.

**Key Activities:**
- Document organizational mission, objectives, and stakeholder expectations
- Catalog legal, regulatory, and contractual cybersecurity obligations
- Map critical business processes and their technology dependencies
- Define risk appetite and risk tolerance statements
- Identify internal and external stakeholders with cybersecurity interests

**Implementation Guidance:**
- Maintain a regulatory obligations register updated quarterly
- Conduct annual stakeholder mapping exercises
- Align cybersecurity objectives with enterprise risk management (ERM)
- Document dependencies between business processes and IT assets

**Maturity Indicators:**
| Tier | Indicator |
|------|-----------|
| Tier 1 | Ad hoc understanding of mission and obligations |
| Tier 2 | Documented mission alignment, partial regulatory catalog |
| Tier 3 | Formal stakeholder mapping, complete regulatory register, defined risk appetite |
| Tier 4 | Dynamic risk appetite adjustment, continuous stakeholder engagement, real-time regulatory tracking |

#### GV.RM — Risk Management Strategy

**Key Activities:**
- Establish cybersecurity risk management strategy aligned to enterprise risk
- Define organizational risk tolerance levels (quantitative where possible)
- Create formal risk statements approved by leadership
- Integrate cybersecurity risk into strategic planning and investment decisions
- Review and update risk strategy based on threat landscape changes

**Implementation Guidance:**
- Use quantitative risk analysis methods (FAIR, Monte Carlo) for critical assets
- Maintain risk tolerance thresholds per business unit and asset class
- Present risk posture to the board at least quarterly
- Establish risk acceptance criteria and approval workflows
- Link risk management outcomes to budget allocation

#### GV.RR — Roles, Responsibilities, and Authorities

**Key Activities:**
- Define CISO role, reporting structure, and authority
- Establish cybersecurity responsibilities across all organizational levels
- Ensure board-level cybersecurity oversight
- Define authority for cybersecurity decisions (incident response, risk acceptance)
- Integrate cybersecurity responsibilities into HR processes (job descriptions, performance reviews)

**Implementation Guidance:**
- CISO should report to CEO or board (not buried under IT)
- Create a RACI matrix for cybersecurity functions
- Include cybersecurity objectives in executive performance metrics
- Establish a cybersecurity steering committee with cross-functional representation
- Document delegation of authority for emergency cybersecurity decisions

#### GV.PO — Policy

**Key Activities:**
- Develop comprehensive cybersecurity policy framework
- Ensure policies are informed by organizational context and risk strategy
- Establish policy review and update cadence (annual minimum)
- Communicate policies to all stakeholders including third parties
- Enforce policy compliance through technical and administrative controls

**Implementation Guidance:**
- Structure policies in a hierarchy: Policy → Standards → Procedures → Guidelines
- Tag policies with applicable regulatory requirements
- Use exception management processes for policy deviations
- Measure policy awareness and compliance rates
- Automate policy distribution and acknowledgment tracking

#### GV.OV — Oversight

**Key Activities:**
- Review cybersecurity strategy execution and outcomes
- Report cybersecurity risk posture to governance bodies (board, committees)
- Establish KPIs and KRIs for cybersecurity performance
- Conduct management reviews of the cybersecurity program
- Adjust strategy based on performance metrics and changing risk landscape

**Key Metrics:**
- Mean Time to Detect (MTTD) and Mean Time to Respond (MTTR)
- Percentage of critical assets with current risk assessments
- Policy compliance rate across business units
- Vulnerability remediation timelines (critical/high/medium/low)
- Security awareness training completion and phishing simulation results
- Third-party risk assessment coverage

#### GV.SC — Cybersecurity Supply Chain Risk Management

**Key Activities:**
- Establish C-SCRM policies and procedures
- Assess cybersecurity risk of suppliers, vendors, and partners
- Include cybersecurity requirements in procurement and contracts
- Monitor supply chain cybersecurity posture continuously
- Plan for supply chain disruption and compromise scenarios

**Implementation Guidance:**
- Tier suppliers by criticality and data access level
- Require SOC 2 Type II or equivalent from critical suppliers
- Include right-to-audit clauses in contracts
- Monitor supplier breach disclosures and vulnerability announcements
- Maintain a software bill of materials (SBOM) for critical applications
- Validate supplier incident response capabilities

---

### 2. IDENTIFY (ID)

The IDENTIFY function develops organizational understanding to manage cybersecurity risk to systems, assets, data, and capabilities.

#### ID.AM — Asset Management

**Key Activities:**
- Maintain comprehensive hardware and software asset inventories
- Classify assets by criticality and sensitivity
- Map data flows between systems, networks, and external parties
- Identify and catalog all data repositories (structured and unstructured)
- Track software licensing and end-of-life/end-of-support status
- Discover and manage shadow IT

**Implementation Guidance:**
- Deploy automated asset discovery tools (agent-based and network-based)
- Maintain a Configuration Management Database (CMDB)
- Tag assets with owner, criticality, data classification, and regulatory scope
- Conduct quarterly asset reconciliation
- Integrate asset inventory with vulnerability management and patch systems

#### ID.RA — Risk Assessment

**Key Activities:**
- Identify and document vulnerabilities across all asset types
- Integrate threat intelligence feeds into risk assessment processes
- Conduct risk analysis combining likelihood and impact
- Prioritize risks based on organizational risk tolerance
- Document risk assessment results and risk treatment decisions

**Implementation Guidance:**
- Use standardized risk assessment methodologies (NIST SP 800-30, FAIR, OCTAVE)
- Maintain a risk register with assigned owners and treatment plans
- Conduct risk assessments for new systems, major changes, and annually
- Incorporate threat intelligence from ISACs, CISA advisories, and vendor bulletins
- Use vulnerability scanning results as input to risk assessment

#### ID.IM — Improvement

**Key Activities:**
- Conduct post-incident lessons learned reviews
- Track improvement actions to completion
- Benchmark cybersecurity program against peers and standards
- Integrate improvement insights into program planning and budgeting
- Share lessons learned across the organization

**Implementation Guidance:**
- Schedule blameless post-mortems within 2 weeks of significant incidents
- Maintain an improvement action tracker with deadlines and owners
- Conduct annual program maturity assessments
- Participate in industry information sharing organizations

---

### 3. PROTECT (PR)

The PROTECT function implements appropriate safeguards to ensure delivery of critical services.

#### PR.AA — Identity Management, Authentication, and Access Control

**Key Activities:**
- Implement identity governance and administration (IGA)
- Enforce multi-factor authentication (MFA) for all users — prioritize FIDO2/WebAuthn and hardware keys (YubiKey)
- Deploy single sign-on (SSO) with SAML/OIDC integration
- Implement privileged access management (PAM) for administrative accounts
- Adopt zero trust architecture principles (never trust, always verify)
- Enforce least privilege and just-in-time (JIT) access models
- Conduct regular access reviews and certification campaigns

**Implementation Guidance:**
- Require phishing-resistant MFA (FIDO2) for administrative and high-risk access
- Deploy PAM solutions with session recording and credential vaulting
- Implement network micro-segmentation aligned with zero trust
- Automate user provisioning/deprovisioning tied to HR systems
- Review privileged access monthly, standard access quarterly
- Maintain identity federation with partners using SAML/OIDC

#### PR.AT — Awareness and Training

**Key Activities:**
- Deliver role-based cybersecurity training (developer, executive, general staff)
- Conduct regular phishing simulation campaigns
- Provide specialized training for privileged users and administrators
- Measure training effectiveness through testing and behavioral metrics
- Update training content based on current threats

**Implementation Guidance:**
- Require annual security awareness training for all personnel
- Quarterly phishing simulations with progressive difficulty
- Track and remediate repeat phishing test failures
- Provide secure coding training for developers (OWASP Top 10)
- Executive training should focus on risk governance and incident decisions

#### PR.DS — Data Security

**Key Activities:**
- Encrypt data at rest using AES-256 or equivalent
- Encrypt data in transit using TLS 1.2+ (prefer TLS 1.3)
- Implement data loss prevention (DLP) controls
- Classify data per organizational taxonomy (Public, Internal, Confidential, Restricted)
- Manage encryption keys using HSMs or KMS
- Apply data retention and disposal policies

**Implementation Guidance:**
- Deploy endpoint DLP, network DLP, and cloud DLP
- Automate data classification using content inspection and ML
- Implement database activity monitoring for sensitive data stores
- Use tokenization for sensitive data in non-production environments
- Rotate encryption keys per policy (annually minimum)
- Secure backup data with same encryption standards as production

#### PR.PS — Platform Security

**Key Activities:**
- Implement system hardening baselines (CIS Benchmarks, DISA STIGs)
- Maintain patch management program with defined SLAs
- Enforce configuration management and drift detection
- Secure operating systems, applications, firmware, and containers
- Remove or disable unnecessary services, ports, and protocols

**Implementation Guidance:**
- Apply CIS Level 1 (minimum) or Level 2 benchmarks across all systems
- Patch critical vulnerabilities within 72 hours, high within 30 days
- Deploy configuration management tools (Ansible, Chef, Puppet, Terraform)
- Use immutable infrastructure patterns where possible
- Conduct regular hardening compliance scans
- Maintain golden images for standard deployments

#### PR.IR — Technology Infrastructure Resilience

**Key Activities:**
- Design redundancy into critical infrastructure components
- Implement failover mechanisms (active-active, active-passive)
- Conduct capacity planning aligned with business growth
- Test disaster recovery procedures regularly
- Maintain geographically distributed backups

**Implementation Guidance:**
- Define RPO/RTO for each critical system
- Test failover monthly for Tier 1 systems
- Conduct annual disaster recovery exercises
- Maintain 3-2-1 backup strategy (3 copies, 2 media types, 1 offsite)
- Monitor infrastructure capacity and alert at 80% utilization

---

### 4. DETECT (DE)

The DETECT function defines activities to identify the occurrence of a cybersecurity event.

#### DE.CM — Continuous Monitoring

**Key Activities:**
- Deploy and tune SIEM for centralized log collection and correlation
- Implement IDS/IPS for network threat detection
- Deploy EDR/XDR on all endpoints
- Monitor network traffic for anomalies (NetFlow, full packet capture for critical segments)
- Monitor cloud workloads and SaaS applications
- Establish security operations center (SOC) — internal or managed

**Implementation Guidance:**
- Centralize logs from all systems, applications, network devices, and cloud services
- Retain logs per regulatory requirements (minimum 1 year, 90 days hot)
- Tune SIEM rules quarterly to reduce false positives
- Implement user and entity behavior analytics (UEBA)
- Monitor DNS queries for indicators of compromise
- Deploy honeypots/honeytokens in critical network segments

#### DE.AE — Adverse Event Analysis

**Key Activities:**
- Correlate events from multiple sources to identify incidents
- Implement anomaly detection for baseline deviations
- Conduct proactive threat hunting campaigns
- Analyze alerts for true positives and escalate confirmed events
- Maintain detection playbooks for known attack patterns

**Implementation Guidance:**
- Develop threat hunting hypotheses based on threat intelligence
- Conduct weekly or monthly threat hunting exercises
- Map detection rules to MITRE ATT&CK techniques
- Maintain detection coverage matrix against ATT&CK
- Automate alert triage using SOAR playbooks
- Track detection efficacy metrics (true positive rate, MTTD)

---

### 5. RESPOND (RS)

The RESPOND function includes activities to take action regarding a detected cybersecurity incident.

#### RS.MA — Incident Management

**Key Activities:**
- Maintain an incident response plan (IRP) tested annually
- Define incident classification and severity levels
- Establish escalation procedures and communication chains
- Activate incident response team based on severity
- Coordinate response activities across technical and business teams

**Implementation Guidance:**
- Classify incidents: P1 (Critical), P2 (High), P3 (Medium), P4 (Low)
- P1 response initiation within 15 minutes, P2 within 1 hour
- Maintain on-call rotation for incident response team
- Conduct tabletop exercises quarterly and full simulations annually
- Integrate IRP with business continuity and crisis management plans

#### RS.AN — Incident Analysis

**Key Activities:**
- Conduct forensic analysis of compromised systems
- Determine root cause, attack vector, and scope of compromise
- Assess business impact (data loss, operational disruption, financial)
- Document analysis findings in incident report
- Preserve evidence chain of custody for potential legal proceedings

**Implementation Guidance:**
- Maintain forensic toolkit and trained forensic analysts
- Use write-blockers and forensic images for evidence preservation
- Document all analysis steps and findings in real-time
- Engage external forensic support for major incidents
- Maintain relationships with law enforcement contacts

#### RS.CO — Incident Response Reporting and Communication

**Key Activities:**
- Notify internal stakeholders per communication plan
- Report to regulatory authorities per legal requirements
- Communicate with affected individuals when required
- Coordinate with law enforcement when appropriate
- Manage media communications through designated spokesperson

**Implementation Guidance:**
- Pre-draft notification templates for common incident types
- Know regulatory notification timelines: GDPR (72 hours), HIPAA (60 days), state breach laws (varies)
- Maintain external communication templates reviewed by legal counsel
- Designate a single point of communication for each incident
- Document all communications as part of incident record

#### RS.MI — Incident Mitigation

**Key Activities:**
- Execute containment actions to limit incident scope
- Eradicate threat actor presence from the environment
- Initiate recovery procedures for affected systems
- Validate containment effectiveness before declaring contained
- Monitor for threat actor re-entry during and after mitigation

**Implementation Guidance:**
- Pre-define containment strategies: network isolation, account disable, endpoint quarantine
- Maintain containment playbooks for ransomware, data breach, insider threat, DDoS
- Validate removal of all persistence mechanisms before recovery
- Monitor compromised accounts and systems for 90 days post-incident
- Apply lessons learned to prevent recurrence

---

### 6. RECOVER (RC)

The RECOVER function identifies activities to maintain resilience and restore capabilities after an incident.

#### RC.RP — Incident Recovery Plan Execution

**Key Activities:**
- Execute recovery procedures per documented plans
- Prioritize system restoration based on business criticality
- Validate system integrity before returning to production
- Restore from known-good backups after verifying backup integrity
- Conduct post-recovery validation testing

**Implementation Guidance:**
- Restore Tier 1 (critical) systems first, then Tier 2, Tier 3
- Verify backup integrity and absence of compromise before restore
- Rebuild from golden images rather than cleaning compromised systems
- Validate application functionality and data integrity post-recovery
- Obtain business owner sign-off before declaring recovery complete

#### RC.CO — Incident Recovery Communication

**Key Activities:**
- Communicate recovery status to internal and external stakeholders
- Manage public communications and reputation
- Provide updates to regulators on recovery progress
- Document recovery activities and timeline
- Communicate improvements made to prevent recurrence

**Implementation Guidance:**
- Provide regular status updates during recovery (hourly for P1, daily for P2)
- Coordinate public messaging with legal, PR, and executive leadership
- Prepare customer-facing FAQs for significant incidents
- Issue post-incident summary to all stakeholders within 30 days
- Demonstrate corrective actions taken to rebuild trust

---

## CSF Profiles

Profiles enable organizations to describe their current cybersecurity posture and their target state.

### Current Profile

A snapshot of how the organization currently manages cybersecurity risk, assessed against CSF categories and subcategories.

**Creating a Current Profile:**
1. For each CSF category, assess the current implementation level
2. Document evidence supporting the assessment
3. Identify which tier best describes current practices
4. Note dependencies and constraints

### Target Profile

The desired cybersecurity state, informed by business objectives, regulatory requirements, and risk appetite.

**Creating a Target Profile:**
1. Review organizational context (GV.OC) — mission, obligations, risk appetite
2. Determine target tier for each category based on risk tolerance
3. Prioritize categories based on business criticality
4. Align target profile with available resources and timeline

### Gap Analysis

The difference between current and target profiles drives the implementation roadmap.

**Gap Analysis Process:**
1. Compare current tier to target tier for each category
2. Identify categories with the largest gaps
3. Assess effort required to close each gap (people, process, technology)
4. Prioritize based on risk reduction impact and implementation feasibility
5. Create phased remediation plan with milestones

---

## CSF Tiers

Tiers describe the degree to which an organization's cybersecurity risk management practices exhibit the characteristics defined in the framework.

### Tier 1 — Partial

- **Risk Management Process:** Ad hoc, not formalized
- **Integrated Risk Management:** Limited awareness of cybersecurity risk at organizational level
- **External Participation:** No formal collaboration or information sharing
- **Example:** Small business with antivirus and firewall but no formal security program, no documented policies, reactive approach to incidents

### Tier 2 — Risk Informed

- **Risk Management Process:** Risk-aware but not organization-wide policy
- **Integrated Risk Management:** Awareness of risk at management level, some cybersecurity investment
- **External Participation:** Informal information sharing
- **Example:** Mid-size company with documented security policies, basic vulnerability scanning, security awareness training, but inconsistent implementation across departments

### Tier 3 — Repeatable

- **Risk Management Process:** Formal, expressed as policy, regularly updated
- **Integrated Risk Management:** Organization-wide risk-informed approach
- **External Participation:** Active participation in information sharing
- **Example:** Enterprise with comprehensive security program, SIEM/SOC, regular assessments, defined risk appetite, consistent policy enforcement, mature incident response

### Tier 4 — Adaptive

- **Risk Management Process:** Continuously improved based on lessons learned and predictive indicators
- **Integrated Risk Management:** Cybersecurity risk management is part of organizational culture
- **External Participation:** Active contribution to broader cybersecurity ecosystem
- **Example:** Organization using threat intelligence-driven defense, continuous control validation, automated response, adaptive risk management that adjusts in real-time to changing threat landscape

---

## Cross-Framework Mapping

NIST CSF 2.0 maps to multiple compliance frameworks, enabling organizations to satisfy multiple requirements simultaneously.

### NIST CSF → ISO 27001:2022

| CSF Function | CSF Category | ISO 27001 Annex A Controls |
|---|---|---|
| GOVERN | GV.OC | A.5.1, A.5.2 (Policies, Roles) |
| GOVERN | GV.RM | A.5.3 (Segregation of Duties) |
| GOVERN | GV.PO | A.5.1 (Information Security Policy) |
| GOVERN | GV.SC | A.5.19-5.23 (Supplier Relations) |
| IDENTIFY | ID.AM | A.5.9, A.5.10, A.8.1 (Asset Management) |
| IDENTIFY | ID.RA | A.5.7 (Threat Intelligence), A.8.8 (Vulnerability Management) |
| PROTECT | PR.AA | A.5.15-5.18, A.8.2-8.5 (Access Control) |
| PROTECT | PR.DS | A.8.10-8.12, A.8.24 (Cryptography, Data) |
| PROTECT | PR.PS | A.8.9 (Configuration), A.8.19 (Software Installation) |
| DETECT | DE.CM | A.8.15, A.8.16 (Logging, Monitoring) |
| RESPOND | RS.MA | A.5.24-5.28 (Incident Management) |
| RECOVER | RC.RP | A.5.29, A.5.30 (ICT Continuity) |

### NIST CSF → SOC 2 Trust Service Criteria

| CSF Function | SOC 2 TSC |
|---|---|
| GOVERN | CC1 (Control Environment), CC2 (Communication) |
| IDENTIFY | CC3 (Risk Assessment) |
| PROTECT | CC5 (Control Activities), CC6 (Logical & Physical Access) |
| DETECT | CC7 (System Operations) |
| RESPOND | CC7 (System Operations), CC8 (Change Management) |
| RECOVER | CC9 (Risk Mitigation), A1 (Availability) |

### NIST CSF → HIPAA Security Rule

| CSF Function | HIPAA Safeguard |
|---|---|
| GOVERN | Administrative Safeguards (§164.308) |
| IDENTIFY | Risk Analysis (§164.308(a)(1)) |
| PROTECT | Access Control (§164.312(a)), Transmission Security (§164.312(e)) |
| DETECT | Audit Controls (§164.312(b)), Integrity Controls (§164.312(c)) |
| RESPOND | Security Incident Procedures (§164.308(a)(6)) |
| RECOVER | Contingency Plan (§164.308(a)(7)) |

### NIST CSF → PCI-DSS v4.0

| CSF Function | PCI-DSS Requirements |
|---|---|
| GOVERN | Req 12 (Organizational Policies) |
| IDENTIFY | Req 2 (Secure Configurations), Req 12.4 (Risk Assessment) |
| PROTECT | Req 3-4 (Data Protection), Req 7-8 (Access Control), Req 9 (Physical) |
| DETECT | Req 10-11 (Logging, Testing) |
| RESPOND | Req 12.10 (Incident Response) |
| RECOVER | Req 12.10.2 (Recovery Procedures) |

---

## Infrastructure Security Assessment

### Assessment Across All Functions

**GOVERN Assessment:**
- Review governance documentation completeness
- Validate board reporting cadence and content
- Assess supply chain risk management program maturity
- Evaluate policy framework coverage and currency

**IDENTIFY Assessment:**
- Audit asset inventory accuracy (sample validation)
- Review risk assessment methodology and outputs
- Evaluate threat intelligence integration
- Assess improvement tracking and closure rates

**PROTECT Assessment:**
- Test authentication controls (MFA enforcement, password policy)
- Review access control configurations (least privilege validation)
- Assess encryption implementation (at rest, in transit, key management)
- Validate hardening baselines against benchmarks
- Test backup and recovery capabilities

**DETECT Assessment:**
- Validate SIEM log coverage (are all critical systems sending logs?)
- Test detection rules against MITRE ATT&CK scenarios
- Assess SOC operational maturity
- Review threat hunting program effectiveness

**RESPOND Assessment:**
- Review incident response plan currency and completeness
- Evaluate IR team capabilities and training
- Assess forensic readiness
- Test communication plans and notification workflows

**RECOVER Assessment:**
- Test disaster recovery procedures and measure RPO/RTO achievement
- Validate backup integrity through restore testing
- Assess recovery communication effectiveness
- Review post-incident improvement tracking

---

## Maturity Assessment Workflow

### Phase 1: Preparation (Week 1)

1. **Define Scope** — Identify organizational units, systems, and processes in scope
2. **Gather Documentation** — Collect policies, procedures, architecture diagrams, audit reports
3. **Schedule Interviews** — Book time with CISO, IT leadership, security team, business stakeholders
4. **Review Prior Assessments** — Analyze previous CSF assessments, audit findings, penetration test results

### Phase 2: Assessment (Weeks 2-3)

1. **Function-by-Function Evaluation** — Assess each category using the csf_maturity_assessor tool
2. **Evidence Collection** — Gather artifacts supporting each score (screenshots, configs, reports)
3. **Stakeholder Interviews** — Validate documented state against operational reality
4. **Technical Validation** — Verify technical controls through testing (not just documentation)

### Phase 3: Analysis (Week 4)

1. **Score Compilation** — Aggregate scores across all functions and categories
2. **Gap Analysis** — Compare current profile to target profile
3. **Risk Prioritization** — Rank gaps by risk exposure and remediation effort
4. **Cross-Reference** — Map findings to applicable regulatory requirements

### Phase 4: Reporting and Roadmap (Week 5)

1. **Executive Summary** — High-level maturity scores with trend analysis
2. **Detailed Findings** — Category-level findings with evidence and recommendations
3. **Remediation Roadmap** — Phased plan with milestones, owners, and resource requirements
4. **Board Presentation** — Strategic summary suitable for governance bodies

---

## Implementation Roadmap

### Phase 1: Foundation (Months 1-3)

**Focus: GOVERN + IDENTIFY**

- Establish cybersecurity governance structure (GV.RR)
- Define organizational context and risk appetite (GV.OC, GV.RM)
- Develop or update cybersecurity policy framework (GV.PO)
- Conduct comprehensive asset inventory (ID.AM)
- Perform baseline risk assessment (ID.RA)

**Deliverables:**
- Cybersecurity charter and governance structure
- Risk appetite statement
- Policy framework
- Asset inventory
- Baseline risk register

### Phase 2: Core Protections (Months 4-6)

**Focus: PROTECT**

- Implement identity and access management improvements (PR.AA)
- Deploy MFA organization-wide (PR.AA)
- Enhance data protection controls (PR.DS)
- Apply hardening baselines to all systems (PR.PS)
- Establish security awareness program (PR.AT)

**Deliverables:**
- MFA deployment complete
- PAM solution operational
- Data classification applied to critical data
- Hardened system baselines deployed
- Training program launched

### Phase 3: Visibility and Response (Months 7-9)

**Focus: DETECT + RESPOND**

- Deploy or enhance SIEM/SOC capabilities (DE.CM)
- Develop detection rules mapped to MITRE ATT&CK (DE.AE)
- Update incident response plan and test via tabletop (RS.MA)
- Establish forensic readiness (RS.AN)
- Develop communication templates and procedures (RS.CO)

**Deliverables:**
- SIEM operational with critical log sources
- Detection coverage for top ATT&CK techniques
- Tested incident response plan
- Forensic toolkit and procedures
- Communication templates approved

### Phase 4: Resilience and Maturity (Months 10-12)

**Focus: RECOVER + Continuous Improvement**

- Test and validate disaster recovery procedures (RC.RP)
- Establish recovery communication procedures (RC.CO)
- Launch supply chain risk management program (GV.SC)
- Implement continuous improvement processes (ID.IM)
- Conduct year-one maturity reassessment

**Deliverables:**
- DR procedures tested and validated
- C-SCRM program operational
- Improvement tracking system active
- Year-one maturity assessment complete
- Year-two roadmap drafted

---

## Reference Guides

| Guide | Description |
|-------|-------------|
| [CSF Functions Guide](references/csf-functions-guide.md) | Complete reference for all 6 functions, categories, subcategories, evidence requirements |
| [CSF Implementation Playbook](references/csf-implementation-playbook.md) | Step-by-step implementation guide with templates, prioritization, and budgeting |

---

## Validation Checkpoints

### Before Starting Assessment
- [ ] Scope defined and approved by stakeholders
- [ ] Assessment team identified with appropriate expertise
- [ ] Prior assessment results and audit reports collected
- [ ] Target tier defined for each function

### During Assessment
- [ ] Each category scored with supporting evidence
- [ ] Stakeholder interviews conducted and documented
- [ ] Technical controls validated (not just documented)
- [ ] Cross-framework obligations identified

### After Assessment
- [ ] Gap analysis completed with prioritized recommendations
- [ ] Remediation roadmap with milestones and owners
- [ ] Executive summary prepared for governance bodies
- [ ] Reassessment timeline established

### Implementation Validation
- [ ] Phase milestones achieved on schedule
- [ ] Controls tested and validated post-implementation
- [ ] Metrics established and baseline measurements taken
- [ ] Continuous monitoring operational
