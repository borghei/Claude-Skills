# Compliance Framework Mapping Reference

Master mapping of infrastructure security controls to compliance frameworks. Use this to satisfy multiple framework requirements with single control implementations.

---

## Supported Frameworks

| # | Framework | Full Name | Version | Focus |
|---|-----------|-----------|---------|-------|
| 1 | SOC 2 | Service Organization Control 2 | Trust Services Criteria 2017 (updated 2022) | Service provider security, availability, processing integrity, confidentiality, privacy |
| 2 | ISO 27001 | ISO/IEC 27001 | 2022 | Information security management system (93 Annex A controls) |
| 3 | HIPAA | Health Insurance Portability and Accountability Act | Security Rule (45 CFR Part 164) | Protected health information (PHI) security |
| 4 | GDPR | General Data Protection Regulation | EU 2016/679 | Personal data protection and privacy |
| 5 | PCI-DSS | Payment Card Industry Data Security Standard | v4.0 (March 2024) | Cardholder data protection |
| 6 | NIS2 | Network and Information Security Directive | EU 2022/2555 | Critical infrastructure cybersecurity |
| 7 | DORA | Digital Operational Resilience Act | EU 2022/2554 | Financial services ICT resilience |
| 8 | NIST CSF | NIST Cybersecurity Framework | 2.0 (February 2024) | Cybersecurity risk management |
| 9 | FedRAMP | Federal Risk and Authorization Management Program | Rev 5 (based on NIST 800-53) | US federal cloud security |
| 10 | CCPA | California Consumer Privacy Act / CPRA | Cal. Civ. Code 1798.100+ | Consumer data privacy rights |

---

## Master Control Mapping Table

### Access Control

| Control | Description | SOC 2 | ISO 27001 | HIPAA | GDPR | PCI-DSS | NIS2 | DORA | NIST CSF | FedRAMP | CCPA |
|---------|-------------|-------|-----------|-------|------|---------|------|------|----------|---------|------|
| Centralized IdP | Single identity provider for all apps | CC6.1 | A.5.15 | 164.312(d) | Art.32 | 8.1 | Art.21.2.j | Art.9.4 | PR.AA-01 | AC-2 | - |
| MFA all users | Multi-factor for every account | CC6.1 | A.8.5 | 164.312(d) | Art.32 | 8.3 | Art.21.2.j | Art.9.4 | PR.AA-03 | IA-2(1) | 1798.150 |
| Phishing-resistant MFA | FIDO2/WebAuthn for admins | CC6.1 | A.8.5 | 164.312(d) | Art.32 | 8.3 | Art.21.2.j | Art.9.4 | PR.AA-03 | IA-2(6) | - |
| SSO (SAML/OIDC) | Federated authentication | CC6.1 | A.8.5 | 164.312(d) | Art.32 | 8.1 | Art.21.2.j | Art.9.4 | PR.AA-01 | AC-2 | - |
| SCIM provisioning | Automated user lifecycle | CC6.2 | A.5.16 | 164.312(a)(1) | Art.32 | 8.1.4 | Art.21.2.j | Art.9.4 | PR.AA-02 | AC-2(2) | - |
| JIT privileged access | Time-limited admin access | CC6.1 | A.8.2 | 164.312(a)(1) | Art.32 | 7.1 | Art.21.2.i | Art.9.4 | PR.AA-05 | AC-2(2) | - |
| Access review (quarterly) | Recertification of access | CC6.2 | A.5.18 | 164.312(a)(1) | Art.32 | 7.1.1 | Art.21.2.j | Art.9.4 | PR.AA-05 | AC-2(3) | - |
| RBAC documented | Role-based access model | CC6.3 | A.5.15 | 164.312(a)(1) | Art.32 | 7.1 | Art.21.2.i | Art.9.4 | PR.AA-05 | AC-3 | - |
| Separation of duties | No conflicting roles | CC6.3 | A.5.3 | 164.312(a)(1) | - | 6.4.2 | Art.21.2.i | Art.9.4 | PR.AA-05 | AC-5 | - |
| Service account governance | Unique creds, rotation, inventory | CC6.1 | A.5.16 | 164.312(d) | Art.32 | 8.5 | Art.21.2.j | Art.9.4 | PR.AA-02 | AC-2 | - |
| SSH key management | ED25519, no root login | CC6.7 | A.8.5 | 164.312(d) | Art.32 | 8.3.2 | - | - | PR.AA-03 | IA-5 | - |
| Password policy (14+ chars) | Strong password requirements | CC6.1 | A.5.17 | 164.312(d) | Art.32 | 8.2.3 | Art.21.2.j | Art.9.4 | PR.AA-03 | IA-5 | - |

### Encryption

| Control | Description | SOC 2 | ISO 27001 | HIPAA | GDPR | PCI-DSS | NIS2 | DORA | NIST CSF | FedRAMP | CCPA |
|---------|-------------|-------|-----------|-------|------|---------|------|------|----------|---------|------|
| Encryption at rest (data) | Storage encryption | CC6.7 | A.8.24 | 164.312(a)(2)(iv) | Art.32 | 3.4 | Art.21.2.h | Art.9.2 | PR.DS-01 | SC-28 | 1798.150 |
| Encryption at rest (disk) | Full disk encryption | CC6.7 | A.8.24 | 164.312(a)(2)(iv) | Art.32 | 3.4 | Art.21.2.h | Art.9.2 | PR.DS-01 | SC-28 | - |
| Encryption in transit (TLS 1.2+) | Network encryption | CC6.7 | A.8.24 | 164.312(e)(1) | Art.32 | 4.1 | Art.21.2.h | Art.9.2 | PR.DS-02 | SC-8 | 1798.150 |
| Key management (KMS) | Centralized key management | CC6.7 | A.8.24 | 164.312(a)(2)(iv) | Art.32 | 3.5 | Art.21.2.h | Art.9.2 | PR.DS-01 | SC-12 | - |
| Key rotation | Regular key rotation | CC6.7 | A.8.24 | - | Art.32 | 3.6.4 | Art.21.2.h | Art.9.2 | PR.DS-01 | SC-12(1) | - |
| Certificate management | TLS cert lifecycle | CC6.7 | A.8.24 | 164.312(e)(1) | Art.32 | 4.1 | Art.21.2.h | Art.9.2 | PR.DS-02 | SC-17 | - |
| mTLS (service-to-service) | Internal encryption | CC6.7 | A.8.24 | 164.312(e)(1) | Art.32 | 4.1 | Art.21.2.h | Art.9.2 | PR.DS-02 | SC-8(1) | - |

### Network Security

| Control | Description | SOC 2 | ISO 27001 | HIPAA | GDPR | PCI-DSS | NIS2 | DORA | NIST CSF | FedRAMP | CCPA |
|---------|-------------|-------|-----------|-------|------|---------|------|------|----------|---------|------|
| Network segmentation | Isolate environments | CC6.6 | A.8.22 | 164.312(e)(1) | Art.32 | 1.2 | Art.21.2.a | Art.9.2 | PR.IR-01 | SC-7 | - |
| Firewall (default deny) | Deny-all ingress/egress | CC6.6 | A.8.22 | 164.312(e)(1) | Art.32 | 1.2 | Art.21.2.a | Art.9.2 | PR.IR-01 | SC-7 | - |
| WAF deployed | Web application firewall | CC6.6 | A.8.22 | - | Art.32 | 6.6 | Art.21.2.a | Art.9.2 | PR.IR-01 | SC-7 | - |
| DDoS protection | Volumetric attack defense | A1.2 | A.8.22 | - | Art.32 | - | Art.21.2.a | Art.9.2 | PR.IR-04 | SC-5 | - |
| IDS/IPS | Intrusion detection/prevention | CC6.6 | A.8.16 | 164.312(e)(1) | Art.32 | 11.4 | Art.21.2.a | Art.9.2 | DE.CM-01 | SI-4 | - |
| VPN (WireGuard/IPSec) | Secure remote access | CC6.7 | A.8.22 | 164.312(e)(1) | Art.32 | 4.1 | Art.21.2.a | Art.9.2 | PR.DS-02 | SC-8 | - |
| ZTNA | Zero trust network access | CC6.6 | A.8.22 | 164.312(e)(1) | Art.32 | - | Art.21.2.a | Art.9.4 | PR.AA-05 | SC-7 | - |

### Logging and Monitoring

| Control | Description | SOC 2 | ISO 27001 | HIPAA | GDPR | PCI-DSS | NIS2 | DORA | NIST CSF | FedRAMP | CCPA |
|---------|-------------|-------|-----------|-------|------|---------|------|------|----------|---------|------|
| Centralized logging | All logs to one platform | CC7.2 | A.8.15 | 164.312(b) | Art.30 | 10.5.3 | Art.21.2.b | Art.10 | DE.CM-09 | AU-6 | - |
| SIEM deployed | Security event correlation | CC7.2 | A.8.16 | 164.312(b) | Art.30 | 10.6 | Art.21.2.b | Art.10 | DE.AE-02 | SI-4 | - |
| Audit trail (who/what/when) | Complete audit logging | CC7.2 | A.8.15 | 164.312(b) | Art.30 | 10.2 | Art.21.2.b | Art.10 | DE.CM-09 | AU-3 | 1798.150 |
| Log retention (1 year) | Minimum retention period | CC7.2 | A.8.15 | 164.312(b) | - | 10.7 | Art.21.2.b | Art.10 | DE.CM-09 | AU-11 | - |
| Log integrity | Immutable logs | CC7.2 | A.8.15 | 164.312(b) | - | 10.5 | Art.21.2.b | Art.10 | DE.CM-09 | AU-9 | - |
| Security alerts | Automated alerting | CC7.3 | A.5.25 | 164.308(a)(6) | Art.33 | 10.6 | Art.23 | Art.17 | DE.AE-02 | IR-6 | - |
| FIM (file integrity) | File change monitoring | CC7.2 | A.8.15 | 164.312(b) | - | 11.5 | Art.21.2.b | Art.10 | DE.CM-09 | SI-7 | - |
| UEBA | User behavior analytics | CC7.2 | A.8.16 | - | - | - | Art.21.2.b | Art.10 | DE.AE-01 | SI-4 | - |

### Endpoint Security

| Control | Description | SOC 2 | ISO 27001 | HIPAA | GDPR | PCI-DSS | NIS2 | DORA | NIST CSF | FedRAMP | CCPA |
|---------|-------------|-------|-----------|-------|------|---------|------|------|----------|---------|------|
| MDM deployed | Device management | CC6.7 | A.8.1 | 164.310(d)(1) | Art.32 | - | Art.21.2.d | Art.9.2 | PR.AC-03 | - | - |
| EDR/AV deployed | Endpoint detection | CC6.8 | A.8.7 | 164.308(a)(5)(ii)(B) | Art.32 | 5.1 | Art.21.2.d | Art.9.2 | DE.CM-04 | SI-3 | - |
| Patch management | OS and app patching | CC7.1 | A.8.8 | 164.308(a)(5)(ii)(B) | Art.32 | 6.2 | Art.21.2.d | Art.9.2 | PR.PS-02 | SI-2 | - |
| Screen lock (5 min) | Automatic lock | CC6.1 | A.8.1 | 164.310(b) | - | 8.1.8 | - | - | PR.AC-03 | AC-11 | - |
| USB control | Removable media policy | CC6.7 | A.8.12 | 164.310(d)(1) | Art.32 | 9.7 | Art.21.2.d | Art.9.2 | PR.DS-01 | MP-7 | - |
| Remote wipe | Lost device protection | CC6.7 | A.8.1 | 164.310(d)(2)(iii) | Art.32 | - | Art.21.2.d | Art.9.2 | PR.DS-01 | - | - |

### CI/CD and Supply Chain

| Control | Description | SOC 2 | ISO 27001 | HIPAA | GDPR | PCI-DSS | NIS2 | DORA | NIST CSF | FedRAMP | CCPA |
|---------|-------------|-------|-----------|-------|------|---------|------|------|----------|---------|------|
| Branch protection | Required reviews, status checks | CC7.1 | A.8.25 | - | - | 6.4.2 | Art.21.2.e | Art.9.2 | PR.PS-01 | SA-11 | - |
| Secret scanning | Detect secrets in code | CC6.7 | A.8.4 | 164.312(a)(2)(iv) | Art.32 | 3.4 | Art.21.2.e | Art.9.2 | PR.DS-01 | SA-11 | - |
| SAST (static analysis) | Code security scanning | CC7.1 | A.8.25 | - | - | 6.3.2 | Art.21.2.e | Art.9.2 | PR.PS-01 | SA-11 | - |
| Dependency scanning | Third-party vulnerability | CC7.1 | A.8.8 | - | - | 6.2 | Art.21.2.d | Art.9.2 | PR.PS-02 | SA-11 | - |
| Container scanning | Image vulnerability | CC7.1 | A.8.8 | - | - | 6.2 | Art.21.2.d | Art.9.2 | PR.PS-02 | SA-11 | - |
| SBOM generation | Software bill of materials | CC7.1 | A.5.21 | - | - | - | Art.21.2.d | Art.9.2 | PR.PS-01 | SA-17 | - |
| Artifact signing | Build artifact integrity | CC7.1 | A.8.25 | - | - | - | Art.21.2.e | Art.9.2 | PR.PS-01 | SA-10 | - |
| Deploy approval gates | Production change control | CC7.1 | A.8.25 | - | - | 6.4.5 | Art.21.2.e | Art.9.2 | PR.PS-01 | CM-3 | - |

### Secrets Management

| Control | Description | SOC 2 | ISO 27001 | HIPAA | GDPR | PCI-DSS | NIS2 | DORA | NIST CSF | FedRAMP | CCPA |
|---------|-------------|-------|-----------|-------|------|---------|------|------|----------|---------|------|
| Secrets manager | Centralized secret storage | CC6.7 | A.8.24 | 164.312(a)(2)(iv) | Art.32 | 3.5 | Art.21.2.h | Art.9.2 | PR.DS-01 | SC-28 | - |
| Secret rotation (90d) | Regular credential rotation | CC6.1 | A.5.17 | 164.312(d) | Art.32 | 8.2.4 | Art.21.2.j | Art.9.4 | PR.AA-03 | IA-5 | - |
| No secrets in code | Code scanning for secrets | CC6.7 | A.8.4 | 164.312(a)(2)(iv) | Art.32 | 3.4 | Art.21.2.e | Art.9.2 | PR.DS-01 | SA-11 | - |
| Pre-commit hooks | Prevent secret commits | CC6.7 | A.8.4 | 164.312(a)(2)(iv) | Art.32 | 3.4 | Art.21.2.e | Art.9.2 | PR.DS-01 | SA-11 | - |
| HSM for critical keys | Hardware key protection | CC6.7 | A.8.24 | 164.312(a)(2)(iv) | Art.32 | 3.5 | Art.21.2.h | Art.9.2 | PR.DS-01 | SC-12(1) | - |

### Physical Security

| Control | Description | SOC 2 | ISO 27001 | HIPAA | GDPR | PCI-DSS | NIS2 | DORA | NIST CSF | FedRAMP | CCPA |
|---------|-------------|-------|-----------|-------|------|---------|------|------|----------|---------|------|
| DC SOC 2 report | Provider security assurance | CC6.4 | A.5.21 | 164.310(a)(1) | Art.28 | 9.1 | Art.21.2.d | Art.28 | GV.SC-06 | PE-1 | - |
| Badge access | Physical entry control | CC6.4 | A.7.2 | 164.310(a)(1) | - | 9.1 | Art.21.2.f | - | PR.AC-03 | PE-3 | - |
| Media disposal | NIST 800-88 destruction | CC6.5 | A.7.14 | 164.310(d)(2)(i) | Art.32 | 9.8 | Art.21.2.h | Art.9.2 | PR.IP-06 | MP-6 | - |
| Visitor management | Visitor logging and escort | CC6.4 | A.7.2 | 164.310(a)(1) | - | 9.4 | Art.21.2.f | - | PR.AC-03 | PE-8 | - |

---

## Control Overlap Analysis

### Highest-Overlap Controls (Implement First)

These controls satisfy the most frameworks simultaneously:

| Control | Frameworks Covered | Priority |
|---------|-------------------|----------|
| MFA enforcement | 9/10 (all except CCPA) | P0 — Immediate |
| Encryption at rest | 9/10 | P0 — Immediate |
| Encryption in transit (TLS 1.2+) | 9/10 | P0 — Immediate |
| Centralized logging | 8/10 | P0 — Immediate |
| Access control (RBAC) | 8/10 | P0 — Immediate |
| Audit trail (who/what/when) | 8/10 | P0 — Immediate |
| Patch management | 8/10 | P1 — Week 1 |
| Network segmentation | 8/10 | P1 — Week 1 |
| EDR/AV deployed | 8/10 | P1 — Week 1 |
| Incident response plan | 8/10 | P1 — Week 1 |
| Secret management | 8/10 | P1 — Week 1 |
| Key management | 7/10 | P2 — Month 1 |
| IDS/IPS | 7/10 | P2 — Month 1 |
| SIEM deployed | 7/10 | P2 — Month 1 |
| SBOM generation | 5/10 | P3 — Quarter 1 |

### Framework-Specific Controls (Low Overlap)

These controls are required by only 1-2 frameworks:

| Control | Framework | Priority |
|---------|-----------|----------|
| PCI DSS scoping (CDE isolation) | PCI-DSS only | Required if processing cards |
| DPIA (Data Protection Impact Assessment) | GDPR, CCPA | Required if processing EU/CA personal data |
| ICT resilience testing (TLPT) | DORA only | Required for financial services |
| NIS2 incident reporting (24h/72h) | NIS2 only | Required for critical infrastructure |
| FedRAMP authorization package | FedRAMP only | Required for US federal cloud |
| HIPAA BAA (Business Associate Agreement) | HIPAA only | Required for PHI processing |

---

## Prioritization Guide for Multi-Framework Compliance

### If pursuing SOC 2 + ISO 27001 (most common combination)

**Overlap: ~85%** — Most SOC 2 controls map directly to ISO 27001 Annex A controls.

Implementation order:
1. Access control (IdP, SSO, MFA, RBAC) — satisfies CC6.1-CC6.3 + A.5.15-A.8.5
2. Encryption (at rest + in transit) — satisfies CC6.7 + A.8.24
3. Logging and monitoring — satisfies CC7.2 + A.8.15-A.8.16
4. Change management (CI/CD security) — satisfies CC7.1 + A.8.25
5. Vendor management — satisfies CC9.2 + A.5.19-A.5.21
6. Incident response — satisfies CC7.3-CC7.4 + A.5.24-A.5.28
7. Physical security — satisfies CC6.4-CC6.5 + A.7.1-A.7.14

### If pursuing SOC 2 + HIPAA (healthcare SaaS)

**Overlap: ~70%** — HIPAA has specific PHI requirements beyond SOC 2.

Additional HIPAA-specific:
1. PHI inventory and data flow mapping
2. Business Associate Agreements (BAAs)
3. Minimum necessary standard (data minimization)
4. Patient rights (access, amendment, accounting)
5. Breach notification (60 days to HHS, individuals)
6. Risk analysis (annual, documented)
7. Contingency plan (emergency mode, disaster recovery)

### If pursuing SOC 2 + PCI-DSS (fintech/payments)

**Overlap: ~60%** — PCI-DSS has prescriptive requirements beyond SOC 2.

Additional PCI-DSS-specific:
1. Cardholder Data Environment (CDE) scoping and isolation
2. Quarterly ASV (Approved Scanning Vendor) scans
3. Annual penetration testing
4. PAN (Primary Account Number) masking/tokenization
5. Key management lifecycle (custodians, split knowledge)
6. Wireless scanning (quarterly)
7. Service provider management (PCI compliance verification)

### If pursuing NIS2 + DORA (EU critical infrastructure + financial)

**Overlap: ~75%** — DORA is more prescriptive than NIS2.

Combined requirements:
1. ICT risk management framework
2. Incident reporting (NIS2: 24h early warning, 72h full; DORA: 4h initial, 72h intermediate)
3. Resilience testing (DORA: TLPT for significant entities)
4. Supply chain security (both)
5. Business continuity and DR
6. Board-level accountability

---

## Evidence Collection Strategy

### Single-Evidence, Multi-Framework Approach

For each control, collect ONE evidence artifact that satisfies ALL applicable frameworks:

| Evidence Type | Example | Satisfies |
|--------------|---------|-----------|
| **Policy Document** | Access Control Policy v3.0 | SOC 2 CC6.1, ISO 27001 A.5.15, HIPAA 164.312(a), PCI-DSS 7.1 |
| **Configuration Screenshot** | MFA enforcement in Okta | SOC 2 CC6.1, ISO 27001 A.8.5, HIPAA 164.312(d), PCI-DSS 8.3 |
| **Audit Log Export** | 90 days of authentication logs | SOC 2 CC7.2, ISO 27001 A.8.15, HIPAA 164.312(b), PCI-DSS 10.2 |
| **Review Minutes** | Q1 Access Review meeting notes | SOC 2 CC6.2, ISO 27001 A.5.18, PCI-DSS 7.1.1 |
| **Scan Report** | Quarterly vulnerability scan | SOC 2 CC7.1, ISO 27001 A.8.8, PCI-DSS 11.2, NIST CSF DE.CM-08 |
| **Test Results** | DR test results document | SOC 2 A1.2, ISO 27001 A.5.30, HIPAA 164.308(a)(7), PCI-DSS 12.10 |
| **Training Records** | Security awareness completion | SOC 2 CC1.4, ISO 27001 A.6.3, HIPAA 164.308(a)(5), PCI-DSS 12.6 |
| **Vendor Assessment** | Cloud provider SOC 2 report | SOC 2 CC9.2, ISO 27001 A.5.21, HIPAA 164.308(b), PCI-DSS 12.8 |
| **Incident Record** | Security incident response log | SOC 2 CC7.4, ISO 27001 A.5.26, HIPAA 164.308(a)(6), PCI-DSS 12.10 |
| **Risk Register** | Annual risk assessment | SOC 2 CC3.1, ISO 27001 Cl.6.1, HIPAA 164.308(a)(1), PCI-DSS 12.2 |

### Evidence Collection Calendar

| Frequency | Evidence | Owner |
|-----------|----------|-------|
| **Daily** | Automated scan results (pushed to evidence repo) | Security tooling |
| **Weekly** | Patch compliance report | IT operations |
| **Monthly** | Access provisioning/deprovisioning report | IAM team |
| **Quarterly** | Access recertification results | Managers + Security |
| **Quarterly** | Vulnerability scan results | Security |
| **Quarterly** | Security awareness training completion | HR |
| **Semi-annually** | Penetration test results | External vendor |
| **Semi-annually** | DR/BC test results | IT operations |
| **Annually** | Risk assessment | Security + Leadership |
| **Annually** | Policy review and updates | Security + Legal |
| **Annually** | Vendor security assessments | Security + Procurement |
| **Annually** | SOC 2 report from cloud providers | Security |
| **On change** | Change management records | Engineering |
| **On incident** | Incident response documentation | Security |

---

## Framework-Specific Quick Reference

### SOC 2 Trust Services Criteria (Most Common)

| Category | Criteria | Focus |
|----------|----------|-------|
| CC1 | Control Environment | Organization, management, board oversight |
| CC2 | Communication and Information | Internal/external communication |
| CC3 | Risk Assessment | Risk identification, analysis, management |
| CC4 | Monitoring Activities | Ongoing evaluation of controls |
| CC5 | Control Activities | Policies and procedures |
| CC6 | Logical and Physical Access | Authentication, authorization, physical security |
| CC7 | System Operations | Change management, monitoring, incident response |
| CC8 | Change Management | System changes, testing, approval |
| CC9 | Risk Mitigation | Vendor management, business continuity |
| A1 | Availability | System availability and recovery |
| PI1 | Processing Integrity | Accurate, complete processing |
| C1 | Confidentiality | Data protection |
| P1 | Privacy | Personal information handling |

### ISO 27001:2022 Annex A Control Families

| Family | Controls | Focus |
|--------|----------|-------|
| A.5 | Organizational (37 controls) | Policies, roles, threat intel, asset management |
| A.6 | People (8 controls) | Screening, terms, awareness, remote working |
| A.7 | Physical (14 controls) | Perimeters, entry, equipment, media |
| A.8 | Technological (34 controls) | Access, crypto, endpoints, logging, development |

### NIST CSF 2.0 Functions

| Function | Code | Focus |
|----------|------|-------|
| Govern | GV | Risk management strategy, roles, policies |
| Identify | ID | Asset management, risk assessment, improvement |
| Protect | PR | Access control, awareness, data security, platform security |
| Detect | DE | Continuous monitoring, adverse event analysis |
| Respond | RS | Incident management, analysis, mitigation, reporting |
| Recover | RC | Recovery planning, communication |

---

**Last Updated:** March 2026
**Frameworks Covered:** 10 (SOC 2, ISO 27001, HIPAA, GDPR, PCI-DSS, NIS2, DORA, NIST CSF, FedRAMP, CCPA)
**Total Control Mappings:** 250+
