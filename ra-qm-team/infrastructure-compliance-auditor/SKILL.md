---
name: infrastructure-compliance-auditor
description: >
  Cross-framework infrastructure security audit across cloud, network, and CI/CD.
  Use for infrastructure and cloud security audits, security posture assessment,
  and validating technical controls for SOC 2, ISO 27001, and NIST CSF.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: compliance
  domain: infrastructure-security
  updated: 2026-06-15
  tags: [infrastructure-audit, cloud-security, dns, tls, compliance-automation]
---
# Infrastructure Compliance Auditor

Cross-cutting infrastructure security audit across ALL compliance frameworks. Replaces manual Vanta-style checks with deterministic, repeatable, evidence-generating infrastructure audits covering cloud, DNS, TLS, endpoints, access control, network, containers, CI/CD, secrets, logging, and physical security. Maps 250+ controls to 10 standards (SOC 2, ISO 27001, HIPAA, GDPR, PCI-DSS, NIS2, DORA, NIST CSF, FedRAMP, CCPA) with severity-weighted scoring.

## Core Capabilities

- **11 audit domains** — cloud (AWS/Azure/GCP), DNS, TLS/SSL, endpoints, access control, network, container/K8s, CI/CD, secrets, logging/monitoring, physical security
- **250+ controls** — each with a check ID, severity rating, and multi-framework mapping
- **Framework mapping** — collect-evidence-once, map-to-many strategy across 10 standards
- **Deterministic scoring** — severity-weighted per-domain and overall scores (0-100) with an audit-readiness rating
- **Evidence generation** — JSON and markdown reports suitable for auditor consumption

## When to Use

Reach for this skill on: "infrastructure audit", "cloud security audit", "infrastructure compliance", "DNS security audit", "TLS audit", "endpoint security", "access control audit", "network security assessment", "infrastructure security", "cloud compliance", "Vanta alternative", "compliance automation", "security posture assessment", "hardware security keys", or "YubiKey compliance".

## Clarify First

Before running the audit, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Audit domains** — which of the 11 (cloud, DNS, TLS, endpoints, access, network, container, CI/CD, secrets, logging, physical) are in scope (determines which checks run)
- [ ] **Target frameworks** — which standards to map findings to (SOC 2, ISO 27001, HIPAA, PCI-DSS, NIS2…) (drives the control mapping and report)
- [ ] **Infrastructure config** — the JSON describing actual state, including cloud provider (AWS/Azure/GCP) (the checks and CIS baseline depend on it)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the audit report.

## Quick Start

### Run Full Infrastructure Audit

```bash
python scripts/infra_audit_runner.py --config infrastructure.json --output audit_report.json
```

### Audit DNS Security for a Domain

```bash
python scripts/dns_security_checker.py --domain example.com --output dns_report.json
```

### Audit Access Controls

```bash
python scripts/access_control_auditor.py --config access_controls.json --output access_report.json
```

### Generate Compliance-Mapped Report

```bash
python scripts/infra_audit_runner.py --config infrastructure.json --frameworks soc2,iso27001,hipaa --format markdown --output compliance_report.md
```

## Tools

| Tool | Purpose | Input |
|------|---------|-------|
| `infra_audit_runner.py` | Full infrastructure audit across all 11 domains | JSON config describing infrastructure |
| `dns_security_checker.py` | DNS-specific security audit (SPF, DKIM, DMARC, DNSSEC, CAA, MTA-STS) | Domain name |
| `access_control_auditor.py` | Access control, MFA, SSO, PAM, RBAC audit | JSON config describing access controls |

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/audit-control-catalog.md](references/audit-control-catalog.md)** — the full 250+ control catalog across all 11 audit domains plus the framework coverage matrix. Read when you need exact check IDs, controls, severities, and framework mappings for any domain.
- **[references/audit-workflows.md](references/audit-workflows.md)** — audit workflows, pre/post-audit validation checklists, the severity-weighted scoring methodology, and success criteria. Read when planning or executing an audit and interpreting scores.
- **[references/tool-reference.md](references/tool-reference.md)** — CLI flag reference for the three audit scripts plus a troubleshooting table. Read when running the tools or diagnosing unexpected output.
- **[references/cloud-security-baseline.md](references/cloud-security-baseline.md)** — AWS / Azure / GCP CIS Benchmark deep-dive. Read for cloud-provider hardening detail beyond the catalog.
- **[references/access-control-standards.md](references/access-control-standards.md)** — MFA, SSO, PAM, Zero Trust, and YubiKey implementation standards. Read when designing identity and access controls.
- **[references/compliance-framework-mapping.md](references/compliance-framework-mapping.md)** — control-to-framework master mapping. Read when aligning evidence across multiple certifications.

## Scope & Limitations

**In Scope:**
- Infrastructure security audit across 11 domains: Cloud, DNS, TLS/SSL, Endpoints, Access Control, Network, Containers/K8s, CI/CD, Secrets, Logging/Monitoring, Physical Security
- Framework mapping to 10 compliance standards: SOC 2, ISO 27001, HIPAA, GDPR, PCI-DSS, NIS2, DORA, NIST CSF, FedRAMP, CCPA
- 250+ individual control checks with severity-weighted scoring
- DNS security validation including SPF, DKIM, DMARC, DNSSEC, CAA, MTA-STS, and subdomain takeover risk
- Access control audit covering IdP, SSO, MFA, FIDO2/hardware keys, PAM, RBAC, service accounts, SSH keys, API keys, and Zero Trust
- Evidence-generating reports in JSON and markdown formats for auditor consumption

**Out of Scope:**
- Actual penetration testing, vulnerability scanning, or active exploitation -- this skill performs configuration-based assessment, not active testing
- Cloud provider API calls or live infrastructure scanning -- the tool works with JSON configuration input describing your infrastructure state
- Compliance certification or attestation -- this skill identifies gaps but does not replace formal SOC 2, ISO 27001, or PCI-DSS audits
- Application security testing (SAST/DAST) beyond CI/CD pipeline configuration checks
- Compliance program management, policy writing, or governance documentation

**Important Notes:**
- SOC 2 2026 best practices demand real-time monitoring dashboards flagging control deficiencies within 48 hours; periodic spot-checks are no longer sufficient
- Zero Trust architecture is increasingly expected across all frameworks; perimeter-based security alone is insufficient for SOC 2, ISO 27001, and NIS2
- Compliance automation platforms (Drata, Vanta, Sprinto) complement but do not replace the deterministic checks this tool provides

## Integration Points

| Skill | Integration | When to Use |
|-------|-------------|-------------|
| `soc2-compliance-expert` | SOC 2 Trust Services Criteria mapped to infrastructure controls; evidence collection for SOC 2 Type II | When infrastructure audit supports SOC 2 certification |
| `information-security-manager-iso27001` | ISO 27001 Annex A technological controls validated by infrastructure checks | When ISO 27001 certification requires evidence of technical control implementation |
| `nist-csf-specialist` | NIST CSF 2.0 Protect and Detect functions mapped to infrastructure domains | When building unified security posture across NIST and other frameworks |
| `dora-compliance-expert` | DORA Pillar 1 and Pillar 3 controls validated by infrastructure security checks | When financial entity requires infrastructure evidence for DORA compliance |
| `pci-dss-specialist` | PCI-DSS v4.0 network security, encryption, and access control requirements mapped to checks | When cardholder data environment requires infrastructure compliance validation |
| `gdpr-dsgvo-expert` | Technical privacy controls (encryption, access controls, data masking) supporting GDPR Art. 32 | When infrastructure controls support personal data protection requirements |
