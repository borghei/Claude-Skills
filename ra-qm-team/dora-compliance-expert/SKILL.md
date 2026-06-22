---
name: dora-compliance-expert
description: >
  DORA (EU 2022/2554) digital operational resilience compliance for financial
  entities, covering all 5 pillars. Use for DORA readiness assessments, ICT risk
  management, incident classification, and third-party ICT oversight.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: compliance
  domain: financial-resilience
  updated: 2026-06-15
  tags: [dora, ict-risk, resilience-testing, financial-services]
---
# DORA Compliance Expert

Tools and guidance for Regulation (EU) 2022/2554 on digital operational resilience for the financial sector (Digital Operational Resilience Act — DORA). DORA is a directly applicable EU regulation (applicable since January 17, 2025) covering 20 types of financial entities and their critical ICT third-party providers. This skill assesses readiness against the five pillars, classifies ICT incidents and computes reporting deadlines, and structures third-party risk and resilience-testing programs.

## Core Capabilities

- **5-pillar readiness assessment** — score ICT risk management, incident management, resilience testing, third-party risk, and information sharing (0–100 per pillar) with gap analysis and prioritized remediation
- **Incident classification & reporting** — classify ICT incidents per Article 18 criteria, determine major-incident status, and compute the 4h / 72h / 1-month reporting deadlines
- **Third-party ICT risk** — register structure, Article 30 contractual provisions, exit strategies, and concentration-risk assessment
- **Resilience testing program design** — basic testing (12 test types) plus advanced Threat-Led Penetration Testing (TLPT) per the TIBER-EU framework

## When to Use

- Running a DORA gap assessment or readiness scorecard for a financial entity
- Classifying an ICT incident and confirming reporting obligations to a competent authority
- Building or auditing an ICT third-party register and contracts
- Designing a digital operational resilience testing program (basic + TLPT)
- Determining whether and how DORA applies to your entity

## Clarify First

Before running the assessment, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Entity scope** — whether the organization is one of DORA's 20 financial-entity types (determines applicability and proportionality)
- [ ] **Task** — 5-pillar readiness, incident classification, third-party register, or testing-program design (picks the tool and workflow)
- [ ] **Incident facts (if classifying)** — clients affected, duration, data loss, criticality, economic impact (drives major-incident determination and the 4h/72h/1-month deadlines)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the assessment.

## Quick Start

```bash
# Generate and run a 5-pillar readiness assessment
python scripts/dora_readiness_checker.py --template > assessment.json
python scripts/dora_readiness_checker.py --config assessment.json --json

# Classify an ICT incident and get reporting deadlines
python scripts/dora_incident_classifier.py --clients-affected 5000 --duration-hours 4 \
  --data-loss yes --services-critical yes --economic-impact 500000
```

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/framework-overview.md](references/framework-overview.md)** — DORA background, legal nature, relationship to NIS2/GDPR/PSD2/MiCA/ISO 27001, the 20 in-scope entity types, proportionality, CTPP designation, and the penalty/enforcement regime. Read when scoping applicability or assessing enforcement exposure.
- **[references/five-pillars-detail.md](references/five-pillars-detail.md)** — article-by-article requirements for all 5 pillars (Articles 5–45), incident classification & reporting deadlines, testing/TLPT, and third-party contractual provisions. Read when assessing a specific pillar or mapping a requirement to its article.
- **[references/dora-five-pillars-guide.md](references/dora-five-pillars-guide.md)** — complete implementation guidance for all 5 pillars with ISO 27001 control mapping, financial-sector-specific requirements, and RTS/ITS references. Read when implementing controls aligned to ISO 27001.
- **[references/dora-third-party-management.md](references/dora-third-party-management.md)** — ICT third-party register template, contractual requirements checklist, exit strategy framework, concentration-risk methodology, and critical-provider oversight. Read when building the register or reviewing contracts.
- **[references/implementation-and-infrastructure.md](references/implementation-and-infrastructure.md)** — 9-month implementation roadmap, quick wins, infrastructure verification checklists, troubleshooting table, and success criteria. Read when planning the program or diagnosing assessment results.
- **[references/tools-and-cli.md](references/tools-and-cli.md)** — full command examples, feature lists, and flag-by-flag reference for both Python scripts. Read when running or scripting the tools.

## Scope & Limitations

**In Scope:**
- Readiness assessment against all 5 DORA pillars with per-pillar scoring
- ICT incident classification per Article 18 criteria with major incident determination
- Reporting deadline calculation (4-hour initial, 72-hour intermediate, 1-month final)
- Incident notification template generation for competent authority submissions
- Third-party risk management guidance including register template and contractual requirements
- Resilience testing program design covering basic and advanced (TLPT) testing
- Gap analysis with prioritized remediation recommendations

**Out of Scope:**
- Actual penetration testing execution or vulnerability scanning -- this skill provides planning and assessment frameworks, not testing tools
- Direct interaction with competent authorities or ESAs (EBA, ESMA, EIOPA)
- Legal determination of entity scope (whether your organization falls under DORA's 20 entity types) -- consult regulatory counsel
- CTPP (Critical Third-Party Provider) oversight framework compliance -- applicable only to ESA-designated providers
- Real-time ICT monitoring or SIEM implementation -- use `infrastructure-compliance-auditor` for technical security controls

**Important Notes:**
- DORA became applicable January 17, 2025; regulators are treating 2025 as a transition year but enforcement is expected to intensify in 2026
- Non-compliance penalties can reach up to 2% of total annual worldwide turnover or 1% of average daily global turnover for up to 6 months (for CTPPs)

## Integration Points

| Skill | Integration | When to Use |
|-------|-------------|-------------|
| `information-security-manager-iso27001` | ISO 27001 controls map directly to DORA Pillar 1 requirements; ISO 27001 certification supports DORA compliance evidence | When building ICT risk management framework aligned with both ISO 27001 and DORA |
| `nis2-directive-specialist` | DORA is lex specialis for financial sector; NIS2 applies residually; coordinate incident reporting timelines | When financial entity also falls under NIS2 scope for non-financial ICT services |
| `infrastructure-compliance-auditor` | Technical infrastructure checks validate DORA Pillar 1 (protection, detection) and Pillar 3 (resilience testing) controls | When assessing actual infrastructure security posture against DORA requirements |
| `nist-csf-specialist` | NIST CSF 2.0 functions map to DORA pillars; useful for organizations with US operations | When building a unified resilience framework across US and EU requirements |

---

*Last Updated: June 2026*
*Regulation Reference: EU 2022/2554*
*Applicable From: January 17, 2025*
