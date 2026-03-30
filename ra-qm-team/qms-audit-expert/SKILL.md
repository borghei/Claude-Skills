---
name: qms-audit-expert
description: >
  ISO 13485 internal audit expertise for medical device QMS. Covers audit
  planning, execution, nonconformity classification, and CAPA verification. Use
  for internal audit planning, audit execution, finding classification, external
  audit preparation, or audit program management.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: compliance
  domain: quality-audit
  updated: 2026-03-31
  tags: [iso-13485, audit, nonconformity, quality-audit, certification]
---
# QMS Audit Expert

ISO 13485 internal audit methodology for medical device quality management systems.

---

## Table of Contents

- [Audit Planning Workflow](#audit-planning-workflow)
- [Audit Execution](#audit-execution)
- [Nonconformity Management](#nonconformity-management)
- [External Audit Preparation](#external-audit-preparation)
- [Reference Documentation](#reference-documentation)
- [Tools](#tools)

---

## Audit Planning Workflow

Plan risk-based internal audit program:

1. List all QMS processes requiring audit
2. Assign risk level to each process (High/Medium/Low)
3. Review previous audit findings and trends
4. Determine audit frequency by risk level
5. Assign qualified auditors (verify independence)
6. Create annual audit schedule
7. Communicate schedule to process owners
8. **Validation:** All ISO 13485 clauses covered within cycle

### Risk-Based Audit Frequency

| Risk Level | Frequency | Criteria |
|------------|-----------|----------|
| High | Quarterly | Design control, CAPA, production validation |
| Medium | Semi-annual | Purchasing, training, document control |
| Low | Annual | Infrastructure, management review (if stable) |

### Audit Scope by Clause

| Clause | Process | Focus Areas |
|--------|---------|-------------|
| 4.2 | Document Control | Document approval, distribution, obsolete control |
| 5.6 | Management Review | Inputs complete, decisions documented, actions tracked |
| 6.2 | Training | Competency defined, records complete, effectiveness verified |
| 7.3 | Design Control | Inputs, reviews, V&V, transfer, changes |
| 7.4 | Purchasing | Supplier evaluation, incoming inspection |
| 7.5 | Production | Work instructions, process validation, DHR |
| 7.6 | Calibration | Equipment list, calibration status, out-of-tolerance |
| 8.2.2 | Internal Audit | Schedule compliance, auditor independence |
| 8.3 | NC Product | Identification, segregation, disposition |
| 8.5 | CAPA | Root cause, implementation, effectiveness |

### Auditor Independence

Verify auditor independence before assignment:

- [ ] Auditor not responsible for area being audited
- [ ] No direct reporting relationship to auditee
- [ ] Not involved in recent activities under audit
- [ ] Documented qualification for audit scope

---

## Audit Execution

Conduct systematic internal audit:

1. Prepare audit plan (scope, criteria, schedule)
2. Review relevant documentation before audit
3. Conduct opening meeting with auditee
4. Collect evidence (records, interviews, observation)
5. Classify findings (Major/Minor/Observation)
6. Conduct closing meeting with preliminary findings
7. Prepare audit report within 5 business days
8. **Validation:** All scope items covered, findings supported by evidence

### Evidence Collection

| Method | Use For | Documentation |
|--------|---------|---------------|
| Document review | Procedures, records | Document number, version, date |
| Interview | Process understanding | Interviewee name, role, summary |
| Observation | Actual practice | What, where, when observed |
| Record trace | Process flow | Record IDs, dates, linkage |

### Audit Questions by Clause

**Document Control (4.2):**
- Show me the document master list
- How do you control obsolete documents?
- Show me evidence of document change approval

**Design Control (7.3):**
- Show me the Design History File for [product]
- Who participates in design reviews?
- Show me design input to output traceability

**CAPA (8.5):**
- Show me the CAPA log with open items
- How do you determine root cause?
- Show me effectiveness verification records

See `references/iso13485-audit-guide.md` for complete question sets.

### Finding Documentation

Document each finding with:

```
Requirement: [Specific ISO 13485 clause or procedure]
Evidence: [What was observed, reviewed, or heard]
Gap: [How evidence fails to meet requirement]
```

**Example:**
```
Requirement: ISO 13485:2016 Clause 7.6 requires calibration
at specified intervals.

Evidence: Calibration records for pH meter (EQ-042) show
last calibration 2024-01-15. Calibration interval is
12 months. Today is 2025-03-20.

Gap: Equipment is 2 months overdue for calibration,
representing a gap in calibration program execution.
```

---

## Nonconformity Management

Classify and manage audit findings:

1. Evaluate finding against classification criteria
2. Assign severity (Major/Minor/Observation)
3. Document finding with objective evidence
4. Communicate to process owner
5. Initiate CAPA for Major/Minor findings
6. Track to closure
7. Verify effectiveness at follow-up
8. **Validation:** Finding closed only after effective CAPA

### Classification Criteria

| Category | Definition | CAPA Required | Timeline |
|----------|------------|---------------|----------|
| Major | Systematic failure or absence of element | Yes | 30 days |
| Minor | Isolated lapse or partial implementation | Recommended | 60 days |
| Observation | Improvement opportunity | Optional | As appropriate |

### Classification Decision

```
Is required element absent or failed?
├── Yes → Systematic (multiple instances)? → MAJOR
│   └── No → Could affect product safety? → MAJOR
│       └── No → MINOR
└── No → Deviation from procedure?
    ├── Yes → Recurring? → MAJOR
    │   └── No → MINOR
    └── No → Improvement opportunity? → OBSERVATION
```

### CAPA Integration

| Finding Severity | CAPA Depth | Verification |
|------------------|------------|--------------|
| Major | Full root cause analysis (5-Why, Fishbone) | Next audit or within 6 months |
| Minor | Immediate cause identification | Next scheduled audit |
| Observation | Not required | Noted at next audit |

See `references/nonconformity-classification.md` for detailed guidance.

---

## External Audit Preparation

Prepare for certification body or regulatory audit:

1. Complete all scheduled internal audits
2. Verify all findings closed with effective CAPA
3. Review documentation for currency and accuracy
4. Conduct management review with audit as input
5. Prepare facility and personnel
6. Conduct mock audit (full scope)
7. Brief personnel on audit protocol
8. **Validation:** Mock audit findings addressed before external audit

### Pre-Audit Readiness Checklist

**Documentation:**
- [ ] Quality Manual current
- [ ] Procedures reflect actual practice
- [ ] Records complete and retrievable
- [ ] Previous audit findings closed

**Personnel:**
- [ ] Key personnel available during audit
- [ ] Subject matter experts identified
- [ ] Personnel briefed on audit protocol
- [ ] Escorts assigned

**Facility:**
- [ ] Work areas organized
- [ ] Documents at point of use current
- [ ] Equipment calibration status visible
- [ ] Nonconforming product segregated

### Mock Audit Protocol

1. Use external auditor or qualified internal auditor
2. Cover full scope of upcoming external audit
3. Simulate actual audit conditions (timing, formality)
4. Document findings as for real audit
5. Address all Major and Minor findings before external audit
6. Brief management on readiness status

---

## Reference Documentation

### ISO 13485 Audit Guide

`references/iso13485-audit-guide.md` contains:

- Clause-by-clause audit methodology
- Sample audit questions for each clause
- Evidence collection requirements
- Common nonconformities by clause
- Finding severity classification

### Nonconformity Classification

`references/nonconformity-classification.md` contains:

- Severity classification criteria and decision tree
- Impact vs. occurrence matrix
- CAPA integration requirements
- Finding documentation templates
- Closure requirements by severity

---

## Tools

### Audit Schedule Optimizer

```bash
# Generate optimized audit schedule
python scripts/audit_schedule_optimizer.py --processes processes.json

# Interactive mode
python scripts/audit_schedule_optimizer.py --interactive

# JSON output for integration
python scripts/audit_schedule_optimizer.py --processes processes.json --output json
```

Generates risk-based audit schedule considering:
- Process risk level
- Previous findings
- Days since last audit
- Criticality scores

**Output includes:**
- Prioritized audit schedule
- Quarterly distribution
- Overdue audit alerts
- Resource recommendations

### Sample Process Input

```json
{
  "processes": [
    {
      "name": "Design Control",
      "iso_clause": "7.3",
      "risk_level": "HIGH",
      "last_audit_date": "2024-06-15",
      "previous_findings": 2
    },
    {
      "name": "Document Control",
      "iso_clause": "4.2",
      "risk_level": "MEDIUM",
      "last_audit_date": "2024-09-01",
      "previous_findings": 0
    }
  ]
}
```

---

## Audit Program Metrics

Track audit program effectiveness:

| Metric | Target | Measurement |
|--------|--------|-------------|
| Schedule compliance | >90% | Audits completed on time |
| Finding closure rate | >95% | Findings closed by due date |
| Repeat findings | <10% | Same finding in consecutive audits |
| CAPA effectiveness | >90% | Verified effective at follow-up |
| Auditor utilization | 4 days/month | Audit days per qualified auditor |

---

## Troubleshooting

| Problem | Likely Cause | Resolution |
|---------|-------------|------------|
| Schedule optimizer produces no audits for a process | `last_audit_date` is recent and risk level is Low | Low-risk processes are scheduled annually. If the last audit was within 365 days, no new audit is generated. Increase `risk_level` or `criticality_score` to trigger earlier scheduling. |
| Optimizer flags all processes as overdue | Date format in `processes.json` is incorrect | Use ISO 8601 format (`YYYY-MM-DD`) for `last_audit_date`. Invalid dates cause the tool to treat the last audit as missing. |
| Interactive mode does not accept input | Terminal does not support stdin prompts | Use file-based input with `--processes processes.json` instead of `--interactive`. |
| Audit schedule does not cover all ISO 13485 clauses | Input process list is incomplete | The optimizer schedules only the processes provided. Ensure all required clauses (4.2, 5.6, 6.2, 7.3, 7.4, 7.5, 7.6, 8.2.2, 8.3, 8.5) are represented in the input. |
| Finding classified as Minor but should be Major | Classification was applied inconsistently | Apply the decision tree: systematic failure or absent element = Major; isolated lapse = Minor. Consider whether the finding could affect product safety (auto-escalate to Major). |
| External auditor raises finding already closed internally | CAPA effectiveness verification not completed before external audit | Ensure all internal audit findings have completed CAPA with documented effectiveness verification before the external audit date. Close the loop, do not just complete the action. |
| Audit report rejected by process owner | Findings not supported by objective evidence | Every finding must reference specific evidence (document number, record ID, observation details). Rework findings using the Requirement-Evidence-Gap format documented in this skill. |

---

## Success Criteria

- Annual audit schedule covers 100% of ISO 13485 clauses with risk-based frequency (quarterly for high-risk, semi-annual for medium, annual for low)
- Schedule compliance rate exceeds 90% (audits completed on time vs. planned)
- All Major findings result in full root cause analysis CAPA initiated within 30 days and verified effective within 6 months
- Finding closure rate exceeds 95% by due date, with no overdue Major findings at any point
- Repeat finding rate below 10% across consecutive audit cycles, demonstrating effective corrective actions
- Auditor independence verified and documented for every audit assignment (no self-auditing of own work area)
- Mock audit conducted before every external certification or surveillance audit with all Major and Minor findings resolved

---

## Scope & Limitations

**In Scope:**
- ISO 13485:2016 internal audit planning, scheduling, and execution
- Risk-based audit frequency optimization
- Nonconformity classification (Major/Minor/Observation) with decision tree
- CAPA integration for audit findings
- External audit preparation and mock audit protocols
- Audit program metrics and effectiveness tracking

**Out of Scope:**
- External audit execution (this skill supports preparation for and response to external audits, not conducting them)
- Regulatory inspection management (FDA, Notified Body inspections have jurisdiction-specific protocols beyond internal audit scope)
- Detailed CAPA root cause analysis methodology (use capa-officer skill for 5-Why, Fishbone, FTA, FMEA)
- ISO 19011 auditor certification or training program administration
- Technical product testing or process validation
- QMSR-specific audit checklist generation (use quality-manager-qms-iso13485 for QMSR gap analysis)

---

## Integration Points

| Skill | Integration |
|-------|------------|
| [quality-manager-qms-iso13485](../quality-manager-qms-iso13485/) | Provides the QMS process framework that the audit program evaluates; audit results feed into management review inputs |
| [capa-officer](../capa-officer/) | Major and Minor audit findings trigger CAPA initiation; CAPA effectiveness verification closes the audit finding loop |
| [quality-documentation-manager](../quality-documentation-manager/) | Document control audit coverage (Clause 4.2) validates document numbering, approval workflows, and Part 11 compliance |
| [quality-manager-qmr](../quality-manager-qmr/) | Audit program results are a required management review input (Clause 5.6.2); QMR oversees audit program effectiveness |
| [risk-management-specialist](../risk-management-specialist/) | Risk management process audit (Clause 7.1) verifies ISO 14971 implementation and risk file completeness |

---

## Tool Reference

### audit_schedule_optimizer.py

Generates risk-based audit schedules optimized by process risk, findings history, and time since last audit.

| Flag | Required | Description |
|------|----------|-------------|
| `--processes` | Yes (or `--interactive`) | Path to JSON file containing process definitions with `name`, `iso_clause`, `risk_level` (HIGH/MEDIUM/LOW), `last_audit_date`, `previous_findings`, and `criticality_score` |
| `--interactive` | No | Launch interactive mode for guided process entry (alternative to file input) |
| `--output` | No | Output format: `json` for structured output, omit for human-readable text |
