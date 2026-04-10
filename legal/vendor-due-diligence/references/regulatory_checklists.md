# Vendor Regulatory Compliance Checklists

Pre-built compliance checklist templates for 8 regulatory frameworks. Each checklist covers key requirements, assessment questions, and gap analysis prompts for vendor due diligence.

## Table of Contents

- [How to Use These Checklists](#how-to-use-these-checklists)
- [1. GDPR (General Data Protection Regulation)](#1-gdpr-general-data-protection-regulation)
- [2. DORA (Digital Operational Resilience Act)](#2-dora-digital-operational-resilience-act)
- [3. NIS2 (Network and Information Security Directive)](#3-nis2-network-and-information-security-directive)
- [4. SOX (Sarbanes-Oxley Act)](#4-sox-sarbanes-oxley-act)
- [5. PCI DSS (Payment Card Industry Data Security Standard)](#5-pci-dss-payment-card-industry-data-security-standard)
- [6. ISO 27001 / SOC 2](#6-iso-27001--soc-2)
- [7. HIPAA (Health Insurance Portability and Accountability Act)](#7-hipaa-health-insurance-portability-and-accountability-act)
- [8. FedRAMP (Federal Risk and Authorization Management Program)](#8-fedramp-federal-risk-and-authorization-management-program)
- [Cross-Framework Gap Analysis](#cross-framework-gap-analysis)

## How to Use These Checklists

1. Identify which frameworks apply to your vendor relationship based on your industry, data types, and jurisdictions
2. Issue the relevant checklists as part of the vendor questionnaire
3. Score each item as: Compliant / Partially Compliant / Non-Compliant / Not Applicable
4. Use the gap analysis prompts to investigate non-compliant or partially compliant items
5. Feed results into the vendor risk scoring tool for the Compliance dimension

## 1. GDPR (General Data Protection Regulation)

**Applies when:** Vendor processes personal data of EU/EEA residents on your behalf.

| # | Requirement | Assessment Question | Evidence Required |
|---|------------|--------------------|--------------------|
| 1 | Data Processing Agreement | Does vendor have a GDPR-compliant DPA template or accept yours? | Signed DPA or template |
| 2 | Lawful basis for processing | Can vendor confirm processing is limited to your documented instructions? | DPA Art. 28 provisions |
| 3 | Sub-processor management | Does vendor maintain a list of sub-processors with notification process? | Sub-processor list; notification mechanism |
| 4 | Data breach notification | Can vendor notify you of personal data breaches within 72 hours? | Incident response plan; breach notification SLA |
| 5 | Data subject rights support | Can vendor assist with DSAR fulfillment (access, deletion, portability)? | DSAR process documentation |
| 6 | International data transfers | If data leaves EEA, what transfer mechanism is used (SCCs, adequacy)? | SCCs; Transfer Impact Assessment |
| 7 | Data deletion/return | Will vendor delete or return all personal data upon contract termination? | Data retention/deletion policy |
| 8 | Records of processing | Does vendor maintain records of processing activities per Art. 30? | ROPA documentation |
| 9 | DPIA support | Can vendor provide information needed for Data Protection Impact Assessments? | DPIA contribution process |
| 10 | DPO designation | Has vendor appointed a DPO where required? | DPO contact details |

**Gap Analysis Prompts:**
- If no DPA: Is vendor willing to negotiate one? What is timeline?
- If no sub-processor list: How does vendor manage sub-processing today?
- If data transfers outside EEA: Are Standard Contractual Clauses current (post-Schrems II)?

## 2. DORA (Digital Operational Resilience Act)

**Applies when:** You are a financial entity (bank, insurer, investment firm) engaging an ICT third-party service provider.

| # | Requirement | Assessment Question | Evidence Required |
|---|------------|--------------------|--------------------|
| 1 | ICT risk management | Does vendor have an ICT risk management framework? | ICT risk policy documentation |
| 2 | Incident classification and reporting | Can vendor classify and report ICT-related incidents per DORA taxonomy? | Incident classification matrix; reporting SLA |
| 3 | Digital operational resilience testing | Does vendor participate in or conduct threat-led penetration testing (TLPT)? | TLPT reports; testing schedule |
| 4 | Third-party risk provisions | Does vendor's contract include all DORA Art. 28 required provisions? | Contract clause mapping to DORA Art. 28 |
| 5 | Exit strategy | Has vendor documented an exit strategy and transition plan? | Exit plan; data portability assessment |
| 6 | Sub-outsourcing controls | Does vendor notify and obtain consent for material sub-outsourcing? | Sub-outsourcing policy and register |
| 7 | Audit and inspection rights | Will vendor provide audit access as required by DORA? | Contractual audit clause; pooled audit option |
| 8 | Business continuity | Does vendor test business continuity and disaster recovery annually? | BCP/DR test results; recovery time objectives |
| 9 | Concentration risk | Does vendor's market position create concentration risk? | Market share data; alternative provider assessment |
| 10 | Regulatory access | Will vendor facilitate direct access by your financial regulator? | Contractual regulatory access clause |

**Gap Analysis Prompts:**
- If no exit plan: What data formats and migration support does vendor provide?
- If no TLPT: What alternative security testing does vendor conduct?
- If audit access refused: Will vendor accept pooled audit arrangement?

## 3. NIS2 (Network and Information Security Directive)

**Applies when:** You are an essential or important entity under NIS2 and the vendor is part of your supply chain.

| # | Requirement | Assessment Question | Evidence Required |
|---|------------|--------------------|--------------------|
| 1 | Risk analysis and security policies | Does vendor maintain documented information security policies? | Security policy suite |
| 2 | Incident handling | Does vendor have an incident response plan with defined reporting timelines? | IR plan; 24-hour early warning capability |
| 3 | Business continuity | Does vendor maintain backup management, disaster recovery, and crisis management? | BCP/DR documentation and test results |
| 4 | Supply chain security | Does vendor assess and manage their own supply chain security? | Third-party risk management program |
| 5 | Vulnerability handling | Does vendor have a vulnerability disclosure and patching program? | Vulnerability management policy; patch SLAs |
| 6 | Cybersecurity hygiene | Does vendor enforce basic cybersecurity practices (training, patching, access control)? | Training records; patch compliance metrics |
| 7 | Cryptography and encryption | Does vendor use appropriate encryption and cryptographic controls? | Encryption standards documentation |
| 8 | Access control | Does vendor enforce multi-factor authentication and role-based access? | Access control policy; MFA implementation evidence |
| 9 | Asset management | Does vendor maintain an inventory of network and information systems? | Asset inventory; configuration management |
| 10 | Security assessment | Does vendor conduct regular security effectiveness assessments? | Audit reports; security metrics |

**Gap Analysis Prompts:**
- If no supply chain program: How does vendor select and monitor their own suppliers?
- If no vulnerability program: What is vendor's mean time to patch critical vulnerabilities?
- If no MFA: What compensating controls protect access to your data?

## 4. SOX (Sarbanes-Oxley Act)

**Applies when:** Vendor processes, stores, or transmits financial data that affects your financial reporting.

| # | Requirement | Assessment Question | Evidence Required |
|---|------------|--------------------|--------------------|
| 1 | Internal controls | Does vendor maintain internal controls over processes affecting your financial data? | SOC 1 Type II report; ICFR documentation |
| 2 | Audit trails | Does vendor maintain immutable audit trails for all financial data transactions? | Audit log architecture; retention policy |
| 3 | Segregation of duties | Does vendor enforce segregation of duties for financial processes? | SoD matrix; access control documentation |
| 4 | Change management | Does vendor have formal change management for systems processing financial data? | Change management policy; CAB process |
| 5 | Access controls | Does vendor restrict access to financial data based on least-privilege? | Access review reports; RBAC documentation |
| 6 | Data integrity | Does vendor ensure completeness and accuracy of financial data processing? | Reconciliation procedures; data validation |
| 7 | Backup and recovery | Can vendor recover financial data to a known good state? | Backup policy; recovery test results |
| 8 | Audit cooperation | Will vendor cooperate with your external auditors? | Contractual audit clause; auditor access |

**Gap Analysis Prompts:**
- If no SOC 1: Can vendor obtain SOC 1 Type II within 12 months?
- If no audit trails: How can you demonstrate data integrity to your auditors?
- If limited SoD: What compensating controls exist?

## 5. PCI DSS (Payment Card Industry Data Security Standard)

**Applies when:** Vendor processes, stores, or transmits cardholder data.

| # | Requirement | Assessment Question | Evidence Required |
|---|------------|--------------------|--------------------|
| 1 | Network security | Does vendor maintain secure network architecture (firewalls, segmentation)? | Network diagrams; firewall rules review |
| 2 | Cardholder data protection | Does vendor encrypt stored cardholder data? Is PAN masked in displays? | Encryption documentation; data flow diagrams |
| 3 | Vulnerability management | Does vendor maintain anti-malware and patch management programs? | AV deployment; patch compliance reports |
| 4 | Access control | Does vendor restrict access to cardholder data on need-to-know basis? | Access control policy; review reports |
| 5 | Network monitoring | Does vendor monitor and test networks regularly? | IDS/IPS deployment; network scan results |
| 6 | Security policy | Does vendor maintain a comprehensive information security policy? | Security policy suite; employee acknowledgments |
| 7 | PCI DSS validation | What level of PCI DSS compliance has vendor achieved? | AOC (Attestation of Compliance); ROC or SAQ |
| 8 | Incident response | Does vendor have a PCI-specific incident response plan? | IR plan; notification procedures for card brands |
| 9 | Tokenization/encryption | Does vendor use tokenization or point-to-point encryption to reduce scope? | Tokenization architecture; P2PE validation |
| 10 | Third-party management | Does vendor assess PCI compliance of their own service providers? | Third-party compliance program |

**Gap Analysis Prompts:**
- If no AOC: What is the timeline for PCI DSS validation?
- If cardholder data is not tokenized: What scope reduction measures are in place?
- If no network segmentation: How is cardholder data environment isolated?

## 6. ISO 27001 / SOC 2

**Applies when:** You require independent assurance of the vendor's information security controls.

| # | Requirement | Assessment Question | Evidence Required |
|---|------------|--------------------|--------------------|
| 1 | ISMS / Security program | Does vendor maintain a formal Information Security Management System? | ISO 27001 certificate or SOC 2 Type II report |
| 2 | Risk assessment | Does vendor conduct regular information security risk assessments? | Risk assessment methodology; most recent results |
| 3 | Control implementation | Are controls mapped to ISO 27001 Annex A or SOC 2 Trust Service Criteria? | Statement of Applicability or SOC 2 control matrix |
| 4 | Internal audit | Does vendor conduct internal audits of their ISMS? | Internal audit schedule and findings |
| 5 | Management review | Does leadership review the security program regularly? | Management review minutes; security KPIs |
| 6 | Continuous improvement | Does vendor track and remediate audit findings? | Corrective action register; finding closure rates |
| 7 | Certification/attestation currency | Is the ISO 27001 certificate or SOC 2 report current (within 12 months)? | Certificate dates; SOC 2 report period |
| 8 | Scope adequacy | Does the certification scope cover the services provided to you? | Scope statement; service mapping |
| 9 | Exception management | How does vendor handle control exceptions? | Exception process; compensating controls |
| 10 | Incident metrics | Does vendor track and report security incident metrics? | Incident dashboard; trend analysis |

**Gap Analysis Prompts:**
- If certification scope doesn't cover your services: What controls apply outside the certified scope?
- If SOC 2 Type I only: What is timeline for Type II?
- If exceptions exist: Are compensating controls documented and tested?

## 7. HIPAA (Health Insurance Portability and Accountability Act)

**Applies when:** Vendor will create, receive, maintain, or transmit Protected Health Information (PHI) on your behalf.

| # | Requirement | Assessment Question | Evidence Required |
|---|------------|--------------------|--------------------|
| 1 | Business Associate Agreement | Will vendor execute a BAA meeting HIPAA requirements? | Signed BAA or BAA template |
| 2 | PHI safeguards (administrative) | Does vendor have administrative safeguards for PHI? | Security policies; workforce training records |
| 3 | PHI safeguards (physical) | Does vendor have physical safeguards for PHI? | Facility access controls; workstation policies |
| 4 | PHI safeguards (technical) | Does vendor have technical safeguards for PHI? | Access controls; encryption; audit controls |
| 5 | Breach notification | Can vendor notify you of PHI breaches within required timeframe? | Breach notification procedures; SLA |
| 6 | Minimum necessary standard | Does vendor limit PHI access to minimum necessary for the service? | Data minimization practices; access controls |
| 7 | Sub-contractor management | Does vendor ensure sub-contractors also comply with HIPAA? | Sub-contractor BAAs; oversight program |
| 8 | Risk analysis | Has vendor conducted a HIPAA-specific risk analysis? | Risk analysis report; remediation plan |
| 9 | Disposal | Does vendor properly dispose of PHI when no longer needed? | Data disposal procedures; certificate of destruction |
| 10 | Audit trail | Does vendor maintain audit trails for PHI access and modifications? | Audit log configuration; retention policy |

**Gap Analysis Prompts:**
- If no BAA: Is vendor willing to execute one? What is timeline?
- If no HIPAA risk analysis: How does vendor assess PHI-related risks?
- If sub-contractors handle PHI: Are downstream BAAs in place?

## 8. FedRAMP (Federal Risk and Authorization Management Program)

**Applies when:** Vendor provides cloud services to U.S. federal agencies or processes federal data.

| # | Requirement | Assessment Question | Evidence Required |
|---|------------|--------------------|--------------------|
| 1 | Authorization status | Has vendor achieved FedRAMP authorization (JAB or Agency)? | FedRAMP authorization letter; marketplace listing |
| 2 | Impact level | At what impact level is vendor authorized (Low, Moderate, High)? | Authorization boundary documentation |
| 3 | Continuous monitoring | Does vendor maintain a continuous monitoring program? | ConMon plan; monthly vulnerability scans; POA&M |
| 4 | Incident response | Does vendor meet FedRAMP incident response requirements (US-CERT reporting)? | IR plan; US-CERT reporting procedures |
| 5 | System security plan | Does vendor maintain a current SSP? | System Security Plan; date of last update |
| 6 | Annual assessment | Does vendor undergo annual third-party assessment (3PAO)? | 3PAO assessment reports; date of last assessment |
| 7 | POA&M management | Does vendor maintain and remediate Plan of Action & Milestones? | POA&M register; remediation timelines |
| 8 | Supply chain risk | Does vendor assess supply chain risks per NIST 800-161? | Supply chain risk management plan |
| 9 | Data sovereignty | Is all federal data stored within the United States? | Data residency documentation |
| 10 | Encryption (FIPS 140-2) | Does vendor use FIPS 140-2 validated cryptographic modules? | FIPS certificates; encryption architecture |

**Gap Analysis Prompts:**
- If no FedRAMP authorization: What is the timeline and sponsoring agency?
- If authorization is at Low impact: Does your use case require Moderate or High?
- If POA&M items are overdue: What is the remediation plan?

## Cross-Framework Gap Analysis

When multiple frameworks apply, use this matrix to identify overlapping requirements and consolidated gaps.

| Requirement Area | GDPR | DORA | NIS2 | SOX | PCI DSS | ISO/SOC | HIPAA | FedRAMP |
|-----------------|------|------|------|-----|---------|---------|-------|---------|
| Encryption | Yes | Yes | Yes | - | Yes | Yes | Yes | Yes |
| Access control | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Incident response | Yes | Yes | Yes | - | Yes | Yes | Yes | Yes |
| Audit rights | Yes | Yes | - | Yes | - | Yes | - | Yes |
| Data deletion | Yes | - | - | - | - | - | Yes | - |
| Business continuity | - | Yes | Yes | - | - | Yes | - | Yes |
| Vulnerability mgmt | - | Yes | Yes | - | Yes | Yes | - | Yes |
| Third-party risk | Yes | Yes | Yes | - | Yes | Yes | Yes | Yes |
| Breach notification | Yes | Yes | Yes | - | Yes | - | Yes | Yes |
| Change management | - | - | - | Yes | Yes | Yes | - | Yes |

**Consolidation approach:** If a vendor is compliant with the most stringent applicable framework, they likely satisfy the overlapping requirements of less stringent ones. ISO 27001 + SOC 2 Type II provides the broadest baseline coverage.
