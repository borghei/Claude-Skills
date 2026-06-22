---
name: information-security-manager-iso27001
description: >
  ISO 27001:2022 ISMS implementation and cybersecurity governance for HealthTech
  and MedTech. Use for ISMS design, risk assessment per Clause 6.1.2, Annex A
  controls, ISO 27001 certification, security audits, and incident response.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: compliance
  domain: information-security
  updated: 2026-06-15
  tags: [iso-27001, isms, annex-a, information-security, cloud-security]
---
# Information Security Manager - ISO 27001

Implement and manage Information Security Management Systems (ISMS) aligned with ISO 27001:2022 and healthcare regulatory requirements. Covers the full lifecycle: scoping, risk assessment per Clause 6.1.2, selection and implementation of the 93 Annex A controls across four themes, certification readiness, incident response, and cross-framework mapping to SOC 2, NIST CSF 2.0, and NIS2 — with cloud-specific (AWS/Azure/GCP) and Zero Trust guidance.

## Core Capabilities

- **ISMS implementation** — scope/context definition, risk treatment, Statement of Applicability (SoA), monitoring metrics, certification readiness (Stage 1/2)
- **Risk assessment** — Clause 6.1.2 methodology, asset classification, threat/vulnerability modeling, Likelihood × Impact scoring, treatment planning
- **Control implementation** — all 93 Annex A:2022 controls (Organizational, People, Physical, Technological) with cloud-provider mappings and Zero Trust integration
- **Incident response** — detection, triage/classification, containment, recovery, and lessons learned
- **Cross-framework alignment** — ISO 27001 ↔ SOC 2 TSC ↔ NIST CSF 2.0 ↔ NIS2, plus supply chain and hardware-key (FIDO2) requirements

## When to Use

Use this skill when you hear: "implement ISO 27001", "ISMS implementation", "security risk assessment", "information security policy", "ISO 27001 certification", "security controls implementation", "incident response plan", "healthcare data security", "medical device cybersecurity", or "security compliance audit".

## Clarify First

Before running the assessment, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **ISMS scope** — which systems, locations, and data are inside the boundary (drives the Statement of Applicability and risk assessment)
- [ ] **Task** — ISMS implementation, risk assessment, gap analysis, or incident response (picks the workflow and script)
- [ ] **Threat context** — general, healthcare, or cloud (selects the threat catalog and changes the risk register inputs)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the report.

## Quick Start

```bash
# Run a security risk assessment
python scripts/risk_assessment.py --scope "patient-data-system" --output risk_register.json

# Check ISO 27001 compliance status
python scripts/compliance_checker.py --standard iso27001 --controls-file controls.csv

# Generate a gap analysis report
python scripts/compliance_checker.py --standard iso27001 --gap-analysis --output gaps.md
```

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/workflows-and-tools.md](references/workflows-and-tools.md)** — step-by-step ISMS implementation, risk assessment, and incident-response workflows; validation checkpoints; certification-readiness checklists; worked healthcare example; troubleshooting; success criteria; and full `risk_assessment.py` / `compliance_checker.py` flag tables. Read when executing any end-to-end workflow or looking up a script flag.
- **[references/annex-a-controls.md](references/annex-a-controls.md)** — complete enumeration of all 93 Annex A:2022 controls across the four themes plus the 11 controls new in 2022. Read when building/updating a Statement of Applicability or mapping a 2013 SoA to 2022.
- **[references/cloud-and-cross-framework.md](references/cloud-and-cross-framework.md)** — AWS/Azure/GCP control mappings, Zero Trust architecture integration, hardware security key (FIDO2/WebAuthn) requirements, supply chain security, and ISO 27001 ↔ SOC 2 / NIST CSF / NIS2 mappings. Read when implementing in a specific cloud, designing Zero Trust, or pursuing multiple certifications.
- **[references/iso27001-controls.md](references/iso27001-controls.md)** — Annex A control implementation guidance with evidence requirements and audit preparation. Read for control selection for the SoA and audit prep.
- **[references/risk-assessment-guide.md](references/risk-assessment-guide.md)** — risk methodology selection, asset classification criteria, threat modeling approaches, and risk calculation methods. Read before designing the risk assessment process.
- **[references/incident-response.md](references/incident-response.md)** — detailed response procedures, escalation matrices, communication templates, and recovery checklists. Read when building or running the incident response plan.

## Scope & Limitations

**In Scope:** ISO 27001:2022 ISMS implementation (all 93 Annex A controls across 4 themes); risk assessment per Clause 6.1.2 with configurable threat catalogs (general, healthcare, cloud); compliance checking and gap analysis against ISO 27001/27002; cross-framework mapping to SOC 2 TSC, NIST CSF 2.0, and NIS2; cloud-specific controls for AWS/Azure/GCP; Zero Trust integration with phased roadmap; hardware security key (FIDO2/WebAuthn) requirements; supply chain controls including SBOM and vendor risk tiering.

**Out of Scope:** ISO 27001 certification audit execution (preparation guidance only, not audit services); implementation of specific security tools (SIEM, EDR, DLP, WAF — mapped to categories only); penetration testing or vulnerability scanning execution (use `infrastructure-compliance-auditor`); ISO 27701/27017/27018 implementation beyond cross-reference; physical security system design beyond control requirements.

**Important Notes:**
- The ISO 27001:2013 to 2022 transition deadline was October 2025; all certifications must now conform to the 2022 edition.
- The 2022 revision introduced 11 entirely new controls, notably A.5.7 (Threat intelligence), A.5.23 (Cloud services), A.8.9 (Configuration management), A.8.16 (Monitoring activities), and A.8.28 (Secure coding).
- Integration with other standards (ISO 27701, ISO 42001, ISO 9001) via the harmonized Annex SL structure is becoming standard practice.

## Integration Points

| Skill | Integration | When to Use |
|-------|-------------|-------------|
| `isms-audit-expert` | Internal and external ISMS audit management; control testing and finding management | When planning or executing ISO 27001 audits and tracking corrective actions |
| `infrastructure-compliance-auditor` | Technical infrastructure checks validate ISO 27001 Annex A technological controls | When assessing actual infrastructure security posture against ISO 27001 requirements |
| `soc2-compliance-expert` | SOC 2 Trust Services Criteria mapped to ISO 27001 controls for dual compliance | When organization requires both ISO 27001 certification and SOC 2 Type II report |
| `gdpr-dsgvo-expert` | GDPR Art. 32 security of processing aligned with ISO 27001 controls; A.5.34 PII protection | When ISMS must support GDPR compliance requirements |
| `nist-csf-specialist` | NIST CSF 2.0 functions mapped to ISO 27001 for organizations with US operations | When building unified security framework across ISO 27001 and NIST CSF |
| `dora-compliance-expert` | ISO 27001 controls support DORA Pillar 1 (ICT Risk Management) requirements for financial entities | When financial entity uses ISO 27001 as foundation for DORA compliance |
