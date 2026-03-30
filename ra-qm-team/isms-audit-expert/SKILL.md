---
name: isms-audit-expert
description: >
  Information Security Management System auditing for ISO 27001 compliance,
  security control assessment, and certification support. Use when planning ISMS
  audit programs, executing internal or external ISO 27001 audits, testing ISO
  27002 Annex A controls, managing audit findings and corrective actions, or
  preparing for Stage 1/Stage 2 certification and surveillance audits.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: compliance
  domain: security-audit
  updated: 2026-03-31
  tags: [iso-27001, isms-audit, security-testing, certification, controls]
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

---

## Troubleshooting

| Problem | Possible Cause | Resolution |
|---------|---------------|------------|
| Audit plan does not cover all 93 Annex A controls within the certification cycle | Controls not inventoried against the 2022 four-theme structure or risk-based scheduling gaps | Use `isms_audit_scheduler.py` with a complete controls CSV covering all 93 controls; ensure the 3-year cycle allocates quarterly audits for critical controls and annual coverage for all others |
| Major nonconformity found during certification audit | Systemic control failure or complete absence of a required ISMS element | Conduct immediate root cause analysis; develop corrective action plan with 30-day target; re-test the control with fresh evidence; schedule verification audit with certification body |
| Auditor independence challenged by certification body | Internal auditors assigned to areas they manage or operate | Establish clear auditor independence policy; never assign auditors to areas they are responsible for; consider external consultants for high-risk control areas; document independence verification for each audit |
| Evidence collection incomplete for technological controls (A.8) | Technical configurations not captured, logs not retained, or screenshots not timestamped | Prepare control-specific evidence checklists before audit; request system administrators to export configurations; ensure log retention covers the audit period; timestamp all evidence artifacts |
| Finding closure rate below 90% target | Corrective actions not prioritized, unclear ownership, or insufficient follow-up | Assign specific owners with due dates for every finding; implement automated tracking with escalation at 50% and 75% of SLA; conduct monthly corrective action reviews |
| Surveillance audit identifies regression in previously passed controls | Controls degraded after initial certification due to staff changes, system updates, or process drift | Implement continuous compliance monitoring (not just annual checks); schedule monthly control spot-checks for high-risk areas; include control effectiveness in management review |
| Sample-based testing misses systemic issues | Sample size too small or selection biased toward known-good records | Calculate sample size based on population and risk level (minimum 25 for quarterly reviews); use random selection methods; increase sample for areas with prior findings |

---

## Success Criteria

- **Audit plan completion rate of 100%** -- all scheduled audits executed within the planned quarter, with no deferrals or cancellations without management approval
- **Zero major nonconformities at certification/surveillance audits** -- all systemic control failures identified and corrected during internal audits before external assessment
- **Finding closure rate above 90% within SLA** -- major nonconformities closed within 30 days, minor within 90 days, observations addressed by next audit cycle
- **All 93 Annex A controls audited within the 3-year certification cycle** -- with critical controls (A.8.2, A.8.5, A.8.8, A.8.15) audited quarterly and high-risk controls semi-annually
- **Audit evidence documented with specific references** -- every finding includes control reference, evidence type (inquiry/observation/inspection/re-performance), sample details, and conclusion
- **Auditor competency verified** -- all assigned auditors have ISO 27001 Lead Auditor certification or equivalent, with independence confirmed for each audit engagement

---

## Scope & Limitations

**In Scope:**
- Risk-based annual audit planning and scheduling across all 93 ISO 27001:2022 Annex A controls
- Audit execution workflows including pre-audit preparation, evidence collection, control testing, and closing meetings
- Finding management with severity classification (Major NC, Minor NC, Observation) and corrective action tracking
- Certification support for Stage 1 (documentation review) and Stage 2 (implementation effectiveness) audits
- Surveillance audit preparation and recertification planning
- Control-specific testing procedures for organizational, people, physical, and technological control themes
- Audit performance metrics and KPI tracking

**Out of Scope:**
- Actual certification body selection, engagement, or fee negotiation
- Technical penetration testing or vulnerability scanning -- use `infrastructure-compliance-auditor` for technical checks
- ISO 27001 ISMS implementation -- use `information-security-manager-iso27001` for implementation guidance
- SOC 2 or other framework-specific audit execution beyond ISO 27001 cross-reference
- Legal or contractual advice on audit findings or regulatory reporting obligations

**Important Notes:**
- ISO 27001:2013 certifications expired after October 2025; all audits must now conform to the 2022 edition with 93 controls across 4 themes
- 81% of organizations are pursuing ISO 27001 certification as of 2025 (up from 67% in 2024), reflecting heightened market demand for certified security programs
- Best practice is to embed ISMS audit findings into continuous improvement rather than treating audits as periodic compliance events

---

## Integration Points

| Skill | Integration | When to Use |
|-------|-------------|-------------|
| `information-security-manager-iso27001` | ISMS implementation provides the controls and documentation that audits assess | When audit findings require control improvements or ISMS enhancements |
| `infrastructure-compliance-auditor` | Technical infrastructure checks provide audit evidence for Annex A technological controls | When audit requires evidence of A.8 technological control implementation |
| `soc2-compliance-expert` | SOC 2 audit evidence and Trust Services Criteria overlap with ISO 27001 controls | When organization maintains both ISO 27001 and SOC 2 compliance programs |
| `capa-officer` | Audit findings requiring formal corrective action feed into CAPA process | When major nonconformities require structured root cause analysis and corrective action |

---

## Tool Reference

### isms_audit_scheduler.py

Generates risk-based annual audit plans with quarterly scheduling based on control risk ratings.

| Flag | Required | Description |
|------|----------|-------------|
| `--year <year>` | No | Target year for audit plan (default: current year) |
| `--controls <file>` | No | CSV file with custom control risk ratings (columns: `control_id`, `name`, `risk`); defaults to built-in risk ratings for 18 key controls |
| `--quarters <list>` | No | Generate plan for specific quarters only (e.g., `--quarters Q1 Q2`) |
| `--format <fmt>` | No | Output format: `json` (default) or `markdown` |
| `--output <file>` | No | Export audit plan to specified file path |

**Audit Frequency by Risk Level:**
- `critical`: Quarterly (4x per year) -- e.g., A.8.2 Privileged access, A.8.5 Authentication, A.8.8 Vulnerabilities, A.8.15 Logging
- `high`: Semi-annual (2x per year) -- e.g., A.5.15 Access control, A.5.24 Incident management, A.8.7 Malware protection
- `medium`: Annual (1x per year) -- e.g., A.5.1 Policies, A.6.3 Awareness training, A.7.1 Physical perimeters
- `low`: Annual (1x per year) -- e.g., Documentation, asset inventory

**Output:** Quarterly audit schedule with control assignments, auditor allocation guidance, risk-based prioritization, and coverage tracking ensuring all controls are scheduled within the certification cycle.
