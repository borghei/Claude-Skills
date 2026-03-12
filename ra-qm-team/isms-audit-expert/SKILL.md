---
name: isms-audit-expert
description: >
  Information Security Management System auditing for ISO 27001 compliance,
  security control assessment, and certification support. Use when planning ISMS
  audit programs, executing internal or external ISO 27001 audits, testing ISO 27002
  Annex A controls, managing audit findings and corrective actions, or preparing
  for Stage 1/Stage 2 certification and surveillance audits.
triggers:
  - ISMS audit
  - ISO 27001 audit
  - security audit
  - internal audit ISO 27001
  - security control assessment
  - certification audit
  - surveillance audit
  - audit finding
  - nonconformity
---

# ISMS Audit Expert

Internal and external ISMS audit management for ISO 27001 compliance verification, security control assessment, and certification support.

---

## Audit Program Management

### Risk-Based Audit Schedule

| Risk Level | Audit Frequency | Examples |
|------------|-----------------|----------|
| Critical | Quarterly | Privileged access, vulnerability management, logging |
| High | Semi-annual | Access control, incident response, encryption |
| Medium | Annual | Policies, awareness training, physical security |
| Low | Annual | Documentation, asset inventory |

### Workflow: Annual Audit Planning

1. **Review prior audit results** -- analyze previous findings, open items, and risk assessment outputs from the most recent cycle.
2. **Identify high-risk controls** -- flag controls involved in recent security incidents or with outstanding nonconformities.
3. **Determine audit scope** -- define ISMS boundaries, confirm Statement of Applicability (SoA) coverage for the certification cycle.
4. **Assign auditors** -- ensure independence from audited areas; verify auditor competency (ISO 27001 Lead Auditor certification preferred).
5. **Create audit schedule** -- allocate resources, assign dates, and distribute across the year by risk priority.
6. **Obtain management approval** for the finalized audit plan.
7. **Validation checkpoint:** Audit plan covers all 93 Annex A controls within the certification cycle; schedule approved by management; auditor independence confirmed.

### Example: Annual Audit Plan Output

```
ISMS AUDIT PLAN 2026

Prepared by: Information Security Manager
Approved by: CISO
Date: 2026-01-15

Q1 2026 (January-March)
  Scope: Privileged access (A.8.2, A.8.18), Logging (A.8.15, A.8.16)
  Auditor: External consultant (independence required)
  Risk level: Critical

Q2 2026 (April-June)
  Scope: Access control (A.8.3-A.8.5), Incident response (A.5.24-A.5.28)
  Auditor: Internal audit team
  Risk level: High

Q3 2026 (July-September)
  Scope: Physical security (A.7.1-A.7.14), HR security (A.6.1-A.6.8)
  Auditor: Internal audit team
  Risk level: Medium

Q4 2026 (October-December)
  Scope: Policies (A.5.1-A.5.8), Asset management (A.5.9-A.5.14)
  Auditor: Internal audit team
  Risk level: Medium-Low

Coverage: 93/93 Annex A controls scheduled across 4 quarters
```

---

## Audit Execution

### Workflow: Pre-Audit Preparation

1. **Review ISMS documentation** -- policies, Statement of Applicability, risk assessment, and risk treatment plan.
2. **Analyze previous audit reports** -- note open findings and areas requiring follow-up.
3. **Prepare audit plan** -- define interview schedule, control sample, and evidence requirements.
4. **Notify auditees** -- communicate scope, timing, and documentation needed at least 2 weeks in advance.
5. **Prepare control-specific checklists** for all controls in scope.
6. **Validation checkpoint:** All documentation received and reviewed before the opening meeting.

### Workflow: Audit Conduct

1. **Opening Meeting** -- confirm scope, introduce audit team, agree on communication channels and logistics.
2. **Evidence Collection** -- interview control owners, review documentation and records, observe processes in operation, inspect technical configurations.
3. **Control Verification** -- test control design (does it address the risk?), test control operation (is it working as intended?), sample transactions and records, document all evidence.
4. **Closing Meeting** -- present preliminary findings, clarify factual inaccuracies, agree on finding classification, confirm corrective action timelines.
5. **Validation checkpoint:** All controls in scope assessed with documented evidence; findings classified and communicated.

### Evidence Collection Methods

| Method | Use Case | Example |
|--------|----------|---------|
| Inquiry | Process understanding | Interview Security Manager about incident response |
| Observation | Operational verification | Watch visitor sign-in process at reception |
| Inspection | Documentation review | Check access approval records for last quarter |
| Re-performance | Control testing | Attempt login with weak password to verify policy enforcement |

---

## Control Assessment

### ISO 27002 Control Categories

**Organizational Controls (A.5):** Information security policies, roles and responsibilities, segregation of duties, contact with authorities, threat intelligence, information security in projects.

**People Controls (A.6):** Screening and background checks, employment terms, security awareness and training, disciplinary process, remote working security.

**Physical Controls (A.7):** Physical security perimeters, entry controls, securing offices and facilities, physical security monitoring, equipment protection.

**Technological Controls (A.8):** User endpoint devices, privileged access rights, access restriction, secure authentication, malware protection, vulnerability management, backup and recovery, logging and monitoring, network security, cryptography.

### Workflow: Control Testing

1. **Identify control objective** from the relevant ISO 27002 clause.
2. **Determine testing method** -- inquiry, observation, inspection, or re-performance based on control type.
3. **Define sample size** -- base on population size and risk level (e.g., 25 samples for quarterly access reviews, 5 for annual policy reviews).
4. **Execute test** and document results with specific evidence references.
5. **Evaluate control effectiveness** -- effective, partially effective, or ineffective.
6. **Validation checkpoint:** Evidence supports conclusion; finding documented if control is not fully effective.

### Example: Control Test Working Paper

```
CONTROL TEST WORKING PAPER

Control: A.8.2 - Privileged access rights
Objective: Privileged access is restricted and managed
Test date: 2026-03-10
Auditor: J. Smith

Test procedure:
  1. Obtained list of privileged accounts from IAM system (42 accounts)
  2. Selected sample of 10 accounts (25% sample rate)
  3. For each account, verified:
     - Documented business justification exists
     - Manager approval on file
     - Quarterly access review completed
     - No dormant accounts (last login within 90 days)

Results:
  - 8/10 accounts: All criteria met (PASS)
  - 1/10: Missing quarterly review for Q4 2025 (MINOR NC)
  - 1/10: No documented business justification (MINOR NC)

Conclusion: Control partially effective - minor nonconformity raised
Finding reference: ISMS-2026-007
```

---

## Finding Management

### Finding Classification

| Severity | Definition | Response Time |
|----------|------------|---------------|
| Major Nonconformity | Control failure creating significant risk | 30 days |
| Minor Nonconformity | Isolated deviation with limited impact | 90 days |
| Observation | Improvement opportunity | Next audit cycle |

### Finding Documentation Template

```
Finding ID: ISMS-2026-007
Control Reference: A.8.2 - Privileged access rights
Severity: Minor Nonconformity

Evidence:
- 1 of 10 sampled privileged accounts missing Q4 2025 review
- 1 of 10 sampled accounts lacks documented business justification
- Screenshots of IAM records and review log exported 2026-03-10

Risk Impact:
- Unreviewed privileged access increases insider threat exposure
- Non-justified accounts may represent unnecessary attack surface

Root Cause:
- Access review process relies on manual tracking; no automated reminder

Recommendation:
- Implement automated quarterly review reminders via IAM platform
- Require business justification field as mandatory in provisioning workflow
- Backfill missing reviews within 14 days
```

### Workflow: Corrective Action

1. **Auditee acknowledges** finding and severity classification.
2. **Root cause analysis** completed within 10 business days.
3. **Corrective action plan** submitted with target dates and responsible owners.
4. **Actions implemented** by responsible parties per the plan.
5. **Auditor verifies effectiveness** -- re-tests control with fresh evidence.
6. **Finding closed** with documented evidence of resolution.
7. **Validation checkpoint:** Root cause addressed; recurrence prevented; evidence of effective correction on file.

---

## Certification Support

### Stage 1 Audit Preparation Checklist

- [ ] ISMS scope statement finalized
- [ ] Information security policy (management signed)
- [ ] Statement of Applicability (SoA) complete
- [ ] Risk assessment methodology and results documented
- [ ] Risk treatment plan current
- [ ] Internal audit results available (past 12 months)
- [ ] Management review minutes on file

### Stage 2 Audit Preparation Checklist

- [ ] All Stage 1 findings addressed and closed
- [ ] ISMS operational for minimum 3 months
- [ ] Evidence of control implementation across all SoA controls
- [ ] Security awareness training records for all personnel
- [ ] Incident response evidence (if incidents occurred)
- [ ] Access review documentation for the audit period

### Surveillance Audit Cycle

| Period | Focus |
|--------|-------|
| Year 1, Q2 | High-risk controls, Stage 2 findings follow-up |
| Year 1, Q4 | Continual improvement, control sample |
| Year 2, Q2 | Full surveillance |
| Year 2, Q4 | Re-certification preparation |

---

## Tools

| Script | Purpose | Usage |
|--------|---------|-------|
| `isms_audit_scheduler.py` | Generate risk-based audit plans | `python scripts/isms_audit_scheduler.py --year 2026 --format markdown` |

```bash
# Generate annual audit plan
python scripts/isms_audit_scheduler.py --year 2026 --output audit_plan.json

# With custom control risk ratings
python scripts/isms_audit_scheduler.py --controls controls.csv --format markdown

# Generate plan for specific quarters only
python scripts/isms_audit_scheduler.py --year 2026 --quarters Q1 Q2 --format json
```

---

## References

| File | Content |
|------|---------|
| [iso27001-audit-methodology.md](references/iso27001-audit-methodology.md) | Audit program structure, pre-audit phase, certification support |
| [security-control-testing.md](references/security-control-testing.md) | Technical verification procedures for ISO 27002 controls |
| [cloud-security-audit.md](references/cloud-security-audit.md) | Cloud provider assessment, configuration security, IAM review |

---

## Audit Performance Metrics

| KPI | Target | Measurement |
|-----|--------|-------------|
| Audit plan completion | 100% | Audits completed vs. planned |
| Finding closure rate | >90% within SLA | Closed on time vs. total |
| Major nonconformities | 0 at certification | Count per certification cycle |
| Audit effectiveness | Incidents prevented | Security improvements implemented |

---

## Compliance Framework Integration

| Framework | ISMS Audit Relevance |
|-----------|---------------------|
| GDPR | A.5.34 Privacy, A.8.10 Information deletion |
| HIPAA | Access controls, audit logging, encryption |
| PCI DSS | Network security, access control, monitoring |
| SOC 2 | Trust Services Criteria mapped to ISO 27002 |
