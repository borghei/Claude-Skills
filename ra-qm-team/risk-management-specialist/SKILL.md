---
name: risk-management-specialist
description: >
  Medical device risk management specialist implementing ISO 14971 throughout
  product lifecycle. Provides risk analysis, risk evaluation, risk control, and
  post-production information analysis.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: compliance
  domain: risk-management
  updated: 2026-06-15
  tags: [iso-14971, risk-analysis, fmea, risk-register, medical-device]
---
# Risk Management Specialist

ISO 14971:2019 risk management implementation throughout the medical device lifecycle — planning, hazard analysis, risk evaluation, risk control, residual-risk assessment, and post-production monitoring — extended for AI/ML, cybersecurity (IEC 81001-5-1), supply chain, and cross-framework alignment (NIST CSF, DORA, NIS2).

## Core Capabilities

- **Risk management planning** — scope, 5x5 acceptability matrix, RACI, verification and post-production planning
- **Risk analysis & evaluation** — hazard identification across 9 categories, P1-P5 / S1-S5 estimation, ALARP, benefit-risk triggers
- **Risk control** — priority hierarchy (inherent safety → protective measures → information for safety), verification methods, residual-risk evaluation
- **Post-production monitoring** — information sources, review triggers, RM-file update procedures, periodic review
- **Extended domains** — AI/ML risk (bias, drift, adversarial inputs), health-software cybersecurity, supply chain risk, cross-framework mapping

## When to Use

- Implementing ISO 14971:2019 across the device lifecycle
- Building a hazard analysis / risk register using FMEA, FTA, HAZOP, or Use Error Analysis
- Evaluating residual risk and demonstrating ALARP or benefit-risk acceptability
- Extending risk management to AI/ML devices, cybersecurity, or supply chain
- Setting up post-production risk monitoring and Risk Management File update triggers

## Clarify First

Before running the risk assessment, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Device and intended use** — what it is and its use context (drives the hazard categories and benefit-risk analysis)
- [ ] **Lifecycle stage** — planning, hazard analysis, risk control, or post-production (picks the workflow)
- [ ] **Acceptability criteria** — the 5x5 matrix thresholds and ALARP definition (determines the risk-evaluation outcomes)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the risk register.

## Quick Start

```bash
# ISO 14971 risk level (probability × severity, 1-5 each)
python scripts/risk_matrix_calculator.py --probability 3 --severity 4

# FMEA Risk Priority Number (severity / occurrence / detection, 1-10 each)
python scripts/risk_matrix_calculator.py --fmea --severity 8 --occurrence 4 --detection 3

# Guided interactive assessment, or list the full criteria scales
python scripts/risk_matrix_calculator.py --interactive
python scripts/risk_matrix_calculator.py --list-criteria
```

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/risk-process.md](references/risk-process.md)** — full ISO 14971 process: planning, analysis, evaluation, control, and post-production workflows; 5x5 acceptability matrix; probability/severity criteria; hazard checklist; and the decision frameworks. Read when executing any lifecycle stage.
- **[references/risk-analysis-methods.md](references/risk-analysis-methods.md)** — FMEA, FTA, HAZOP, Use Error Analysis, and software hazard analysis methods. Read when choosing and applying a hazard-analysis technique.
- **[references/iso14971-implementation-guide.md](references/iso14971-implementation-guide.md)** — complete ISO 14971:2019 implementation framework with templates. Read for clause-level implementation detail.
- **[references/templates-and-tools.md](references/templates-and-tools.md)** — Hazard Analysis / FMEA worksheets, Risk Management Report template, full `risk_matrix_calculator.py` flag reference, troubleshooting table, and success criteria. Read when documenting assessments or diagnosing tool issues.
- **[references/extended-risk-domains.md](references/extended-risk-domains.md)** — AI/ML risk categories and methodology, IEC 81001-5-1 cybersecurity integration, supply chain risk, post-market monitoring automation, combined safety-security FMEA, and NIST CSF / DORA / NIS2 cross-framework mapping. Read for connected, software, or AI-enabled devices.

## Scope & Limitations

**In Scope:**
- ISO 14971:2019 risk management process implementation (planning, analysis, evaluation, control, residual risk, production/post-production)
- 5x5 risk matrix calculation and FMEA RPN scoring
- Hazard analysis methodology guidance (FMEA, FTA, HAZOP, Use Error Analysis, PHA)
- Risk control hierarchy application and verification planning
- Benefit-risk analysis framework
- Post-production risk monitoring and risk file update triggers
- AI/ML-specific risk management extensions (model bias, drift, adversarial inputs)
- Cybersecurity risk integration per IEC 81001-5-1
- Supply chain risk assessment methodology
- Cross-framework risk mapping (ISO 14971, NIST CSF, DORA, NIS2)

**Out of Scope:**
- Clinical investigation design or execution (risk management informs clinical strategy but does not execute studies)
- Software hazard analysis per IEC 62304 (the skill references software risk but detailed software lifecycle management requires IEC 62304 expertise)
- Biocompatibility testing or ISO 10993 evaluation (the skill identifies biological hazards but does not execute biocompatibility testing)
- Cybersecurity penetration testing or vulnerability scanning (use infrastructure-compliance-auditor for technical security testing)
- CAPA root cause analysis execution (use capa-officer for 5-Why, Fishbone, FTA, FMEA-based root cause investigation)
- Regulatory submission of risk management files (use regulatory-affairs-head for submission strategy and packaging)

## Integration Points

| Skill | Integration |
|-------|------------|
| [quality-manager-qms-iso13485](../quality-manager-qms-iso13485/) | Risk management (Clause 7.1) integrates with QMS product realization planning; risk file is part of the Design History File |
| [capa-officer](../capa-officer/) | Post-market risk signals may trigger CAPA; CAPA root cause analysis methods (FMEA, FTA) overlap with risk analysis techniques |
| [regulatory-affairs-head](../regulatory-affairs-head/) | Risk management file is required for FDA submissions and EU MDR Technical Documentation; benefit-risk analysis supports clinical evaluation |
| [quality-documentation-manager](../quality-documentation-manager/) | Risk management file and records must be controlled per document control procedures (Clause 4.2) |
| [fda-consultant-specialist](../fda-consultant-specialist/) | FDA cybersecurity guidance (2025 update) requires integration of security risks into ISO 14971 processes for premarket submissions |
| [infrastructure-compliance-auditor](../infrastructure-compliance-auditor/) | Technical security controls validated by the infrastructure auditor serve as risk mitigations for cybersecurity threats in the risk assessment |
| [nist-csf-specialist](../nist-csf-specialist/) | NIST CSF risk assessment (ID.RA) maps to ISO 14971 hazard identification and risk estimation; unified risk register possible |
