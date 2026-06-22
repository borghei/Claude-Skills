---
name: nist-csf-specialist
description: >
  NIST Cybersecurity Framework 2.0 implementation, assessment, and compliance
  management. Use for CSF 2.0 gap analysis, cybersecurity risk management, maturity
  assessment, CSF profiles, and cross-framework compliance mapping.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: compliance
  domain: cybersecurity-framework
  updated: 2026-06-15
  tags: [nist-csf, cybersecurity, maturity-assessment, risk-management]
---
# NIST CSF 2.0 Specialist

Implement, assess, and manage cybersecurity programs aligned with the NIST Cybersecurity Framework 2.0 — the definitive standard for organizational cybersecurity risk management. CSF 2.0 (Feb 2024) applies to all organizations and adds GOVERN as a sixth, top-level function alongside IDENTIFY, PROTECT, DETECT, RESPOND, and RECOVER.

## Core Capabilities

- **Maturity assessment** — score all 22 categories across 6 functions on the 1–4 tier scale (Partial → Risk Informed → Repeatable → Adaptive) with evidence-backed gap analysis
- **Profiles & gap analysis** — build current and target profiles, then derive a prioritized, phased remediation roadmap
- **Cross-framework mapping** — map CSF categories to ISO 27001:2022, SOC 2 TSC, HIPAA Security Rule, and PCI-DSS v4.0 to reduce dual-audit burden
- **Program implementation** — 12-month phased roadmap covering governance, core protections, detection/response, and resilience

## When to Use

Use this skill when you hear: "NIST cybersecurity framework", "CSF 2.0", "NIST compliance", "cybersecurity risk management", "NIST controls", "NIST assessment", "cybersecurity maturity", "NIST CSF profile", "cybersecurity governance", "cybersecurity program assessment", "CSF gap analysis", or "cross-framework compliance mapping".

## Clarify First

Before running the assessment, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Target tier** — Partial, Risk Informed, Repeatable, or Adaptive goal (drives the gap analysis and remediation roadmap)
- [ ] **Current-state data** — the present maturity scores across the 6 functions / 22 categories (the scoring depends on it)
- [ ] **Task** — maturity assessment, profile/gap analysis, or cross-framework mapping (selects the script and any target framework)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the maturity report.

## Quick Start

```bash
# Assess cybersecurity maturity against a target tier
python scripts/csf_maturity_assessor.py --input assessment.json --target-tier 3 --output maturity_report.json

# Map controls across frameworks
python scripts/csf_control_mapper.py --source-framework nist-csf --target-framework iso27001 --output mapping.json

# Generate a markdown gap analysis
python scripts/csf_maturity_assessor.py --input assessment.json --target-tier 4 --format markdown --output gap_analysis.md

# Build a multi-framework unified matrix
python scripts/csf_control_mapper.py --source-framework nist-csf --target-framework all --output unified_matrix.json
```

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/framework-reference.md](references/framework-reference.md)** — CSF 2.0 overview, the six functions with all categories (key activities, implementation guidance, maturity indicators), profiles, tiers, and the full cross-framework mapping tables (ISO 27001, SOC 2, HIPAA, PCI-DSS). Read when you need framework foundations or mapping detail.
- **[references/assessment-and-roadmap.md](references/assessment-and-roadmap.md)** — per-function assessment checklists, the 5-week maturity-assessment workflow, the 12-month implementation roadmap, validation checkpoints, and success criteria. Read when planning or running an engagement.
- **[references/tools-and-troubleshooting.md](references/tools-and-troubleshooting.md)** — detailed tool capabilities, input JSON format, full usage examples, flag reference tables, and the troubleshooting guide. Read when running the scripts or debugging output.
- **[references/csf-functions-guide.md](references/csf-functions-guide.md)** — complete CSF 2.0 taxonomy: every function, category, subcategory, evidence requirement, and common assessment question. Read for subcategory-level depth during detailed assessment.
- **[references/csf-implementation-playbook.md](references/csf-implementation-playbook.md)** — step-by-step implementation guide with templates, prioritization, and budgeting. Read when standing up or maturing a program.

## Scope & Limitations

**In Scope:**
- NIST CSF 2.0 maturity assessment across all 6 functions and 22 categories
- Current and target profile creation with gap analysis
- Cross-framework control mapping to ISO 27001:2022, SOC 2 TSC, HIPAA Security Rule, and PCI-DSS v4.0
- Implementation roadmap generation with phased milestones
- Tier-based scoring (Partial, Risk Informed, Repeatable, Adaptive)

**Out of Scope:**
- NIST SP 800-53 control-level implementation (CSF is a framework, not a control catalog; use SP 800-53 for prescriptive controls)
- Technical security testing, vulnerability scanning, or penetration testing (use infrastructure-compliance-auditor)
- Sector-specific Community Profiles (the tool provides organizational profiles; community profiles require sector-specific customization)
- Real-time security monitoring or SIEM configuration
- Compliance certification (NIST CSF is voluntary and does not offer formal certification)
- Legal or regulatory advice on specific compliance obligations

## Integration Points

| Skill | Integration |
|-------|------------|
| [soc2-compliance-expert](../soc2-compliance-expert/) | SOC 2 TSC maps directly to CSF functions; use the control mapper to generate a unified control matrix reducing dual-audit burden |
| [information-security-manager-iso27001](../information-security-manager-iso27001/) | ISO 27001 Annex A controls are the implementation backbone for CSF categories; CSF maturity scores inform ISMS continual improvement |
| [infrastructure-compliance-auditor](../infrastructure-compliance-auditor/) | Validates technical controls (access, encryption, monitoring, endpoints) that underpin PROTECT and DETECT function scores |
| [pci-dss-specialist](../pci-dss-specialist/) | PCI-DSS v4.0 requirements map to CSF categories; use cross-framework mapper for payment environments |
| [nis2-directive-specialist](../nis2-directive-specialist/) | NIS2 Article 21 measures align to CSF functions; CSF maturity assessment benchmarks NIS2 compliance posture |
| [dora-compliance-expert](../dora-compliance-expert/) | DORA ICT risk management pillars map to GOVERN and IDENTIFY functions; use CSF as the unifying assessment framework |
