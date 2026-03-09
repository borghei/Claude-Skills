# Regulatory Affairs, Quality Management & Compliance Skills — Claude Code Guidance

This guide covers the **20 production-ready compliance skills** spanning medical device regulations, information security, privacy, financial resilience, AI governance, and infrastructure security. This is the most comprehensive open-source compliance skills library available.

## Compliance Skills Overview (20 Skills)

### Strategic Leadership (2 skills)
- **regulatory-affairs-head** — RA strategy, regulatory intelligence, FDA/EU/global pathways
- **quality-manager-qmr** — QMS oversight, management review, quality culture, KPIs

### Quality Systems (3 skills)
- **quality-manager-qms-iso13485** — ISO 13485:2016 compliance, process management, supplier qualification
- **capa-officer** — CAPA management, root cause analysis (5-Why, Fishbone, FTA, FMEA)
- **quality-documentation-manager** — Document control, 21 CFR Part 11, electronic signatures

### Risk & Security Management (2 skills)
- **risk-management-specialist** — ISO 14971:2019, risk analysis, FMEA, post-production monitoring
- **information-security-manager-iso27001** — ISO 27001:2022 ISMS, 93 Annex A controls, cloud security

### Regulatory Specialization (2 skills)
- **mdr-745-specialist** — EU MDR 2017/745, Annex VIII classification, GSPR, EUDAMED, UDI
- **fda-consultant-specialist** — FDA 510(k)/PMA/De Novo, QSR/QMSR, HIPAA, cybersecurity

### Audit & Compliance (3 skills)
- **qms-audit-expert** — ISO 13485 internal/external audits, nonconformity management
- **isms-audit-expert** — ISO 27001 ISMS audits, security control testing, certification support
- **gdpr-dsgvo-expert** — GDPR/DSGVO compliance, DPIA, data subject rights, German BDSG

### Information Security & Cybersecurity (3 skills) — NEW
- **soc2-compliance-expert** — SOC 2 Type I/II, Trust Services Criteria (CC1-CC9, A1, PI1, C1, P1), infrastructure security
- **nist-csf-specialist** — NIST CSF 2.0, 6 functions (Govern/Identify/Protect/Detect/Respond/Recover), maturity assessment
- **pci-dss-specialist** — PCI-DSS v4.0, 12 requirements, cardholder data environment, tokenization

### Privacy (1 skill) — NEW
- **ccpa-cpra-privacy-expert** — CCPA/CPRA, California consumer privacy, data mapping, opt-out mechanisms

### AI Governance (2 skills) — NEW
- **eu-ai-act-specialist** — EU AI Act (2024/1689), risk classification, GPAI obligations, conformity assessment
- **iso42001-ai-management** — ISO 42001:2023 AIMS, AI lifecycle governance, impact assessment

### Financial Sector (1 skill) — NEW
- **dora-compliance-expert** — DORA (EU 2022/2554), 5 pillars, ICT risk management, resilience testing

### Cybersecurity Directives (1 skill) — NEW
- **nis2-directive-specialist** — NIS2 (EU 2022/2555), 10 minimum measures, incident reporting, supply chain

### Cross-Cutting Infrastructure (1 skill) — NEW
- **infrastructure-compliance-auditor** — Vanta-level infrastructure audit across ALL frameworks (cloud, DNS, TLS, endpoints, access controls, containers, CI/CD, secrets, logging, physical security)

**Total:** 20 specialized compliance skills | 35+ Python tools | 40+ reference guides

## Compliance Frameworks Coverage

| Framework | Primary Skill | Supporting Skills | Status |
|-----------|--------------|-------------------|--------|
| **ISO 13485:2016** | quality-manager-qms-iso13485 | qms-audit-expert, quality-manager-qmr | ✅ Complete |
| **ISO 14971:2019** | risk-management-specialist | fda-consultant-specialist, mdr-745-specialist | ✅ Complete |
| **ISO 27001:2022** | information-security-manager-iso27001 | isms-audit-expert, soc2-compliance-expert | ✅ Complete |
| **ISO 42001:2023** | iso42001-ai-management | eu-ai-act-specialist | ✅ NEW |
| **MDR 2017/745** | mdr-745-specialist | regulatory-affairs-head, risk-management-specialist | ✅ Complete |
| **FDA 21 CFR 820/QMSR** | fda-consultant-specialist | quality-manager-qms-iso13485, capa-officer | ✅ Enhanced |
| **SOC 2 Type I/II** | soc2-compliance-expert | infrastructure-compliance-auditor, nist-csf-specialist | ✅ NEW |
| **NIST CSF 2.0** | nist-csf-specialist | soc2-compliance-expert, infrastructure-compliance-auditor | ✅ NEW |
| **PCI-DSS v4.0** | pci-dss-specialist | infrastructure-compliance-auditor, soc2-compliance-expert | ✅ NEW |
| **GDPR/DSGVO** | gdpr-dsgvo-expert | ccpa-cpra-privacy-expert, information-security-manager-iso27001 | ✅ Enhanced |
| **CCPA/CPRA** | ccpa-cpra-privacy-expert | gdpr-dsgvo-expert | ✅ NEW |
| **HIPAA** | fda-consultant-specialist | information-security-manager-iso27001, soc2-compliance-expert | ✅ Complete |
| **EU AI Act** | eu-ai-act-specialist | iso42001-ai-management, gdpr-dsgvo-expert | ✅ NEW |
| **NIS2 Directive** | nis2-directive-specialist | information-security-manager-iso27001, infrastructure-compliance-auditor | ✅ NEW |
| **DORA** | dora-compliance-expert | information-security-manager-iso27001, nis2-directive-specialist | ✅ NEW |
| **21 CFR Part 11** | quality-documentation-manager | fda-consultant-specialist | ✅ Complete |
| **IEC 62304** | fda-consultant-specialist | regulatory-affairs-head | ✅ Referenced |
| **IEC 62443** | information-security-manager-iso27001 | nis2-directive-specialist | ✅ Referenced |

## Infrastructure Security Checks

The **infrastructure-compliance-auditor** skill provides Vanta-level automated checks across:

| Area | What's Checked | Frameworks |
|------|---------------|------------|
| **Cloud Security** | AWS/Azure/GCP IAM, S3/storage, VPC, encryption, logging | SOC 2, ISO 27001, NIST CSF, NIS2 |
| **DNS Security** | DNSSEC, SPF, DKIM, DMARC, CAA, MTA-STS | SOC 2, NIS2, NIST CSF |
| **TLS/SSL** | Certificate management, cipher suites, HSTS, mTLS | PCI-DSS, SOC 2, ISO 27001 |
| **Endpoint Security** | MDM, disk encryption, EDR, patch management | SOC 2, ISO 27001, NIST CSF |
| **Access Control** | SSO, MFA, FIDO2/YubiKey, PAM, RBAC, Zero Trust | ALL frameworks |
| **Network Security** | Segmentation, WAF, DDoS, VPN, IDS/IPS, ZTNA | PCI-DSS, NIS2, DORA |
| **Container Security** | Image scanning, K8s RBAC, pod security, service mesh | SOC 2, NIST CSF |
| **CI/CD Security** | Signed commits, secret scanning, SAST/DAST, SBOM | SOC 2, NIST CSF, EU AI Act |
| **Secrets Management** | Vault, rotation policies, git scanning, HSM | ALL frameworks |
| **Logging & Monitoring** | SIEM, audit trails, retention, UEBA, anomaly detection | ALL frameworks |
| **Physical Security** | Data center, office access, media disposal | SOC 2, PCI-DSS, ISO 27001 |

## Compliance Agent

The **cs-compliance-auditor** agent (`agents/compliance/cs-compliance-auditor.md`) orchestrates all 20 compliance skills for comprehensive multi-framework audits. It:

1. **Identifies applicable frameworks** based on industry, region, data types, and company size
2. **Scans infrastructure** (code, configs, cloud, DNS, TLS, access controls)
3. **Generates compliance scorecard** with per-framework readiness scores
4. **Produces remediation roadmap** with prioritized actions and timelines

## Regulatory Workflows

### Workflow 1: SaaS Company Compliance (SOC 2 + GDPR + ISO 27001)
```
1. Infrastructure Audit → infrastructure-compliance-auditor
2. SOC 2 Readiness Assessment → soc2-compliance-expert
3. GDPR Compliance Check → gdpr-dsgvo-expert
4. ISO 27001 Gap Analysis → information-security-manager-iso27001
5. Cross-Framework Control Mapping → nist-csf-specialist
6. Remediation Planning → cs-compliance-auditor (agent)
```

### Workflow 2: Medical Device Development (MDR + FDA + ISO 13485)
```
1. Risk Management (ISO 14971) → risk-management-specialist
2. QMS Process Setup (ISO 13485) → quality-manager-qms-iso13485
3. Technical Documentation (MDR) → mdr-745-specialist
4. FDA Submission → fda-consultant-specialist
5. Clinical Evaluation → regulatory-affairs-head
6. Cybersecurity Assessment → infrastructure-compliance-auditor
```

### Workflow 3: AI Product Compliance (EU AI Act + ISO 42001 + GDPR)
```
1. AI System Risk Classification → eu-ai-act-specialist
2. AIMS Implementation → iso42001-ai-management
3. Data Protection Impact Assessment → gdpr-dsgvo-expert
4. Bias Detection & Fairness → eu-ai-act-specialist
5. Infrastructure Security → infrastructure-compliance-auditor
6. Conformity Assessment → eu-ai-act-specialist
```

### Workflow 4: Financial Services (DORA + NIS2 + PCI-DSS)
```
1. DORA Pillar Assessment → dora-compliance-expert
2. NIS2 Entity Classification → nis2-directive-specialist
3. PCI-DSS Scoping → pci-dss-specialist
4. ICT Risk Management → dora-compliance-expert
5. Resilience Testing Plan → dora-compliance-expert
6. Infrastructure Audit → infrastructure-compliance-auditor
```

### Workflow 5: Privacy Compliance (GDPR + CCPA + HIPAA)
```
1. Data Inventory & Mapping → ccpa-cpra-privacy-expert
2. GDPR Assessment → gdpr-dsgvo-expert
3. CCPA/CPRA Gap Analysis → ccpa-cpra-privacy-expert
4. HIPAA Risk Assessment → fda-consultant-specialist
5. Cross-Privacy Framework Alignment → gdpr-dsgvo-expert
```

### Workflow 6: QMS Audit Preparation
```
1. Internal Audit → qms-audit-expert
2. CAPA Implementation → capa-officer
3. Document Review → quality-documentation-manager
4. Management Review → quality-manager-qmr
5. Certification Audit → qms-audit-expert
```

## Cross-Framework Control Mapping

| Control Area | SOC 2 | ISO 27001 | NIST CSF | NIS2 | DORA | PCI-DSS | HIPAA | GDPR |
|-------------|-------|-----------|----------|------|------|---------|-------|------|
| Access Control | CC6.1 | A.8.5 | PR.AA | Art.21.2.j | Art.9.4 | Req 7-8 | §164.312(d) | Art.32 |
| Encryption | CC6.7 | A.8.24 | PR.DS | Art.21.2.h | Art.9.2 | Req 3-4 | §164.312(a)(2)(iv) | Art.32 |
| Incident Response | CC7.4 | A.5.24 | RS.MA | Art.23 | Art.17 | Req 12.10 | §164.308(a)(6) | Art.33 |
| Risk Assessment | CC3.1 | Cl.6.1 | ID.RA | Art.21.1 | Art.6 | Req 12.2 | §164.308(a)(1) | Art.35 |
| Logging | CC7.2 | A.8.15 | DE.CM | Art.21.2.b | Art.10 | Req 10 | §164.312(b) | Art.30 |
| Business Continuity | A1.2 | A.5.30 | RC.RP | Art.21.2.c | Art.11 | Req 12.10 | §164.308(a)(7) | Art.32 |
| Vendor Management | CC9.2 | A.5.19 | GV.SC | Art.21.2.d | Art.28 | Req 12.8 | §164.308(b) | Art.28 |
| Training | CC1.4 | A.6.3 | PR.AT | Art.21.2.g | Art.13 | Req 12.6 | §164.308(a)(5) | Art.39 |

## Integration Patterns

- **RA/QM ↔ Engineering:** Regulatory requirements inform technical design decisions
- **RA/QM ↔ Product:** Compliance requirements shape product features and roadmap
- **RA/QM ↔ Security:** ISO 27001 + SOC 2 align with security engineering practices
- **RA/QM ↔ Infrastructure:** Infrastructure auditor validates technical controls for all frameworks
- **RA/QM ↔ AI Governance:** EU AI Act + ISO 42001 inform AI system design and deployment

## Quick Start by Industry

| Your Industry | Start With | Then Add |
|---------------|-----------|----------|
| **SaaS / Tech** | soc2-compliance-expert | gdpr-dsgvo-expert, nist-csf-specialist |
| **Healthcare** | fda-consultant-specialist | quality-manager-qms-iso13485, risk-management-specialist |
| **FinTech** | dora-compliance-expert | pci-dss-specialist, nis2-directive-specialist |
| **AI / ML** | eu-ai-act-specialist | iso42001-ai-management, gdpr-dsgvo-expert |
| **Medical Devices** | mdr-745-specialist | iso42001-ai-management (for AI devices) |
| **E-Commerce** | pci-dss-specialist | gdpr-dsgvo-expert, ccpa-cpra-privacy-expert |
| **Critical Infrastructure** | nis2-directive-specialist | nist-csf-specialist, infrastructure-compliance-auditor |
| **Any (Infrastructure)** | infrastructure-compliance-auditor | Framework-specific skills as needed |

## Additional Resources

- **Compliance Agent:** `agents/compliance/cs-compliance-auditor.md`
- **Main Documentation:** `../CLAUDE.md`
- **Standards Library:** `../standards/`

---

**Last Updated:** March 9, 2026
**Skills Deployed:** 20/20 compliance skills production-ready
**Frameworks Covered:** 18 compliance frameworks
**Focus:** Enterprise compliance — from medical devices to SaaS, from AI governance to financial resilience
