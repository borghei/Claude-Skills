---
name: quality-manager-qms-iso13485
description: >
  ISO 13485 Quality Management System implementation and maintenance for medical
  device organizations. Provides QMS design, documentation control, internal
  auditing, CAPA management, and certification support.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: compliance
  domain: quality-management
  updated: 2026-06-15
  tags:
    - iso-13485
    - qms
    - design-control
    - supplier-qualification
    - medical-device
---
# Quality Manager - QMS ISO 13485 Specialist

ISO 13485:2016 Quality Management System implementation, maintenance, and certification support for medical device organizations. Covers the full lifecycle from gap analysis through certification, plus the FDA QMSR transition (effective Feb 2026), digital/electronic QMS, and AI-enabled device considerations.

## Core Capabilities

- **QMS implementation** — gap analysis, Quality Manual (Clause 4.2.2), the 6 mandatory documented procedures, four-tier document hierarchy, certification readiness
- **Document control** — numbering conventions, change control, review schedules, electronic document management (eDMS)
- **Internal audit** — annual audit programs, individual audit execution, auditor qualification, finding classification (Clause 8.2.4)
- **Process validation** — IQ/OQ/PQ protocols, revalidation triggers, special-process examples (Clause 7.5.6)
- **Supplier qualification** — A/B/C categorization, scored evaluation, monitoring, software/cloud provider assessment (Clause 7.4)
- **Cross-framework integration** — FDA QMSR, 21 CFR Part 11 / EU Annex 11, ISO 42001 (AI), remote/hybrid audits, cybersecurity-driven CAPA

## When to Use

- Building an ISO 13485:2016 QMS from scratch or remediating gaps
- Preparing for or transitioning to the FDA QMSR
- Establishing document control, internal audit, validation, or supplier programs
- Modernizing to a digital/electronic QMS (Part 11 / Annex 11)
- Integrating AI-enabled device or cybersecurity requirements into the QMS

## Clarify First

Before building or assessing the QMS, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Task** — QMS implementation/gap analysis, internal audit, process validation, or supplier qualification (picks the workflow and script)
- [ ] **Standard scope** — ISO 13485 only, FDA QMSR transition, or digital QMS (Part 11 / Annex 11) (determines which requirements and retained FDA items apply)
- [ ] **Certification stage** — building from scratch, remediating gaps, or certification readiness (sets the depth)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the deliverable.

## Quick Start

```bash
# Generate an ISO 13485 audit checklist (clause, process, or full system)
python scripts/qms_audit_checklist.py --clause 7.3
python scripts/qms_audit_checklist.py --process design-control
python scripts/qms_audit_checklist.py --audit-type system --output json
python scripts/qms_audit_checklist.py --interactive
```

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/core-workflows.md](references/core-workflows.md)** — step-by-step workflows + tables for QMS implementation, document control, internal audit, process validation, and supplier qualification. Read when executing any core QMS process.
- **[references/process-reference.md](references/process-reference.md)** — ISO 13485 clause structure, management review inputs (5.6.2), record retention, and decision frameworks (exclusions, NC disposition tree, CAPA initiation). Read when mapping clauses or making disposition/CAPA decisions.
- **[references/advanced-integration.md](references/advanced-integration.md)** — FDA QMSR alignment, digital QMS, 21 CFR Part 11 / EU Annex 11, remote audits, ISO 42001 AI integration, software/cloud supplier qualification, cybersecurity CAPA. Read when modernizing the QMS or integrating cross-framework requirements.
- **[references/operations-and-troubleshooting.md](references/operations-and-troubleshooting.md)** — troubleshooting table, success criteria, and the full `qms_audit_checklist.py` flag reference. Read when diagnosing tool output or validating QMS completeness.
- **[references/iso13485-clause-requirements.md](references/iso13485-clause-requirements.md)** — detailed requirements for each ISO 13485:2016 clause with audit questions. Read when interpreting a specific clause in depth.
- **[references/qms-process-templates.md](references/qms-process-templates.md)** — ready-to-use templates for document control, audit, CAPA, supplier, and training. Read when producing QMS artifacts.

## Scope & Limitations

**In Scope:**
- ISO 13485:2016 QMS implementation from gap analysis through certification
- Document control system design (numbering, approval, change control, review schedules)
- Internal audit program planning and execution per Clause 8.2.4
- Process validation methodology (IQ/OQ/PQ) per Clause 7.5.6
- Supplier qualification and monitoring per Clause 7.4
- FDA QMSR transition planning and gap analysis
- Digital QMS implementation (eDMS, Part 11, Annex 11 requirements)
- Remote and hybrid audit methodology
- AI-enabled medical device QMS considerations (ISO 42001 integration)

**Out of Scope:**
- Clinical evaluation or clinical investigation management (use regulatory-affairs-head for clinical evidence strategy)
- Product-specific design control execution (the skill provides the design control framework, not product-specific design inputs/outputs)
- Sterilization validation protocol development (requires product-specific expertise per ISO 11135/11137/17665)
- Regulatory submission preparation (use fda-consultant-specialist or mdr-745-specialist)
- Post-market surveillance program execution (use risk-management-specialist for post-production risk monitoring)
- IT infrastructure or cybersecurity implementation (use infrastructure-compliance-auditor for technical security)

## Integration Points

| Skill | Integration |
|-------|------------|
| [quality-manager-qmr](../quality-manager-qmr/) | QMR oversees QMS effectiveness; management review inputs include QMS process performance metrics |
| [capa-officer](../capa-officer/) | CAPA system (Clause 8.5) is a core QMS process; CAPA effectiveness feeds into management review |
| [qms-audit-expert](../qms-audit-expert/) | Internal audit program (Clause 8.2.4) evaluates QMS processes; audit findings drive CAPA and improvement |
| [quality-documentation-manager](../quality-documentation-manager/) | Document and record control (Clause 4.2) provides the documentation foundation for the entire QMS |
| [risk-management-specialist](../risk-management-specialist/) | ISO 14971 risk management integrates with design control (Clause 7.3) and product realization planning (Clause 7.1) |
| [fda-consultant-specialist](../fda-consultant-specialist/) | QMSR alignment requires mapping FDA-specific requirements (MDR reporting, UDI, Part 11) beyond ISO 13485 |
| [regulatory-affairs-head](../regulatory-affairs-head/) | Regulatory strategy informs QMS scope, market-specific requirements, and certification timelines |
