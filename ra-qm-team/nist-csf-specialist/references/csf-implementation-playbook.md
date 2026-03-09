# NIST CSF 2.0 Implementation Playbook

Step-by-step implementation guide for organizations adopting NIST CSF 2.0, including profile creation, gap analysis, prioritization, cross-framework mapping, and resource planning.

---

## Table of Contents

- [Pre-Implementation Readiness](#pre-implementation-readiness)
- [Step 1: Scope and Prioritize](#step-1-scope-and-prioritize)
- [Step 2: Create Current Profile](#step-2-create-current-profile)
- [Step 3: Define Target Profile](#step-3-define-target-profile)
- [Step 4: Gap Analysis](#step-4-gap-analysis)
- [Step 5: Remediation Roadmap](#step-5-remediation-roadmap)
- [Step 6: Implementation Execution](#step-6-implementation-execution)
- [Step 7: Continuous Monitoring and Improvement](#step-7-continuous-monitoring-and-improvement)
- [Cross-Framework Mapping Tables](#cross-framework-mapping-tables)
- [Resource and Budget Planning](#resource-and-budget-planning)
- [Templates](#templates)

---

## Pre-Implementation Readiness

### Executive Sponsorship

Before starting, secure executive sponsorship (CEO, CTO, or board member). Without visible leadership support, CSF implementation efforts stall at the policy stage.

**Actions:**
- Present business case for CSF 2.0 adoption to executive leadership
- Quantify risk exposure using breach cost data (IBM Cost of a Data Breach report benchmarks)
- Identify regulatory drivers (contractual requirements, insurance mandates, customer expectations)
- Secure budget commitment for assessment phase at minimum

### Team Composition

| Role | Responsibility | Allocation |
|------|---------------|------------|
| Executive Sponsor | Removes barriers, approves budget, champions program | 5% |
| Program Lead (CISO or delegate) | Drives implementation, manages timeline, coordinates teams | 50-100% |
| Security Architect | Assesses technical controls, designs solutions | 50% |
| Risk Analyst | Conducts risk assessments, maintains risk register | 50% |
| Compliance Analyst | Maps regulatory requirements, maintains evidence | 25-50% |
| IT Operations Representative | Provides infrastructure context, implements technical controls | 25% |
| Business Unit Representatives | Provide business context, validate priorities | 10% per BU |

### Document Collection Checklist

Gather before starting the assessment:

- [ ] Current cybersecurity policies and standards
- [ ] Network architecture diagrams
- [ ] Asset inventory (CMDB or equivalent)
- [ ] Previous audit and assessment reports
- [ ] Risk register (if exists)
- [ ] Incident response plan
- [ ] Business continuity and disaster recovery plans
- [ ] Vendor/supplier inventory
- [ ] Regulatory compliance obligations list
- [ ] Organizational chart with security roles highlighted
- [ ] Current security tool inventory
- [ ] Training program documentation
- [ ] Board reporting materials related to cybersecurity

---

## Step 1: Scope and Prioritize

### Define Organizational Scope

Determine which parts of the organization are in scope for initial CSF implementation:

**Option A — Enterprise-wide:** All business units, systems, and processes. Recommended for organizations under regulatory mandate or those pursuing comprehensive program improvement.

**Option B — Business unit or system-specific:** Focus on a critical business unit, product line, or system. Recommended for initial adoption to demonstrate value before expanding.

**Option C — Regulatory-driven scope:** Scope matches a specific regulatory requirement (e.g., systems processing healthcare data for HIPAA, cardholder data for PCI-DSS). Pragmatic when regulatory compliance is the primary driver.

### Prioritize Functions

While all six functions are important, organizations should prioritize based on their current state:

| Starting Position | Recommended Priority |
|---|---|
| No formal security program | GOVERN → IDENTIFY → PROTECT |
| Basic security controls exist | IDENTIFY → DETECT → RESPOND |
| Mature security program seeking governance improvement | GOVERN → DETECT → RECOVER |
| Post-breach remediation | RESPOND → RECOVER → PROTECT → DETECT |
| Regulatory compliance driven | Map regulations first, then address gaps by function |

---

## Step 2: Create Current Profile

### Assessment Methodology

For each CSF category, assess using a combination of:

1. **Documentation Review** — Do policies, procedures, and standards exist?
2. **Stakeholder Interviews** — Are processes understood and followed?
3. **Technical Validation** — Are controls implemented and effective?
4. **Evidence Collection** — Can implementation be demonstrated?

### Scoring Rubric

| Score | Tier | Criteria |
|-------|------|----------|
| 0 | Not Implemented | No evidence of implementation |
| 1 | Partial | Ad hoc, inconsistent, undocumented |
| 2 | Risk Informed | Documented but not consistently implemented; management aware |
| 3 | Repeatable | Formally documented, consistently implemented, regularly reviewed |
| 4 | Adaptive | Continuously improved, predictive, industry-leading, data-driven |

### Assessment Approach per Function

**GOVERN Assessment:**
- Review governance documentation (charter, policies, risk strategy)
- Interview CISO, CTO, board members about cybersecurity governance
- Validate board reporting cadence and content quality
- Assess supply chain risk management program maturity
- Score: Documentation quality + consistency of execution + leadership engagement

**IDENTIFY Assessment:**
- Audit asset inventory accuracy through sampling
- Review risk assessment methodology and recent outputs
- Evaluate threat intelligence integration
- Validate improvement tracking and action closure rates
- Score: Completeness of inventory + risk assessment rigor + improvement velocity

**PROTECT Assessment:**
- Test MFA enforcement (try to access systems without MFA)
- Review access control configurations on critical systems
- Validate encryption for data at rest and in transit
- Run hardening compliance scans against CIS Benchmarks
- Test backup restoration capability
- Score: Technical control effectiveness + coverage + maintenance discipline

**DETECT Assessment:**
- Verify SIEM log source coverage against asset inventory
- Review detection rule coverage against MITRE ATT&CK
- Assess SOC operational maturity (staffing, playbooks, escalation)
- Evaluate threat hunting program
- Score: Detection coverage + response timeliness + analytical capability

**RESPOND Assessment:**
- Review incident response plan currency
- Evaluate tabletop exercise results
- Assess forensic readiness (tools, trained staff, procedures)
- Test communication procedures
- Score: Plan quality + team capability + exercise results

**RECOVER Assessment:**
- Test disaster recovery procedures and measure RPO/RTO
- Validate backup integrity through restoration tests
- Assess recovery communication effectiveness
- Review post-incident improvement follow-through
- Score: DR test results + backup reliability + communication readiness

---

## Step 3: Define Target Profile

### Target Tier Selection

Select target tiers based on organizational risk appetite, regulatory requirements, and available resources:

**Tier 3 (Repeatable)** is the standard target for most organizations. It represents a mature, documented, and consistently executed program.

**Tier 4 (Adaptive)** is appropriate for organizations in high-risk sectors (financial services, critical infrastructure, healthcare) or those with significant threat exposure.

### Target Profile Development Process

1. **Identify Regulatory Minimums** — Some regulations effectively mandate certain tier levels:
   - PCI-DSS mandates Tier 3+ for cardholder data environments
   - HIPAA requires at least Tier 2+ with specific technical controls
   - SOX cybersecurity controls typically need Tier 3+
   - NIST 800-171 (CMMC) maps closely to Tier 3

2. **Assess Business Risk** — Higher business impact systems need higher tiers:
   - Revenue-critical systems: Tier 3-4
   - Customer-facing systems: Tier 3-4
   - Internal support systems: Tier 2-3
   - Development/test environments: Tier 2

3. **Consider Industry Benchmarks** — Use industry averages as a reference point:
   - Financial services: Average Tier 3, leaders at Tier 4
   - Healthcare: Average Tier 2, leaders at Tier 3
   - Manufacturing: Average Tier 2, leaders at Tier 3
   - Technology: Average Tier 3, leaders at Tier 4

4. **Resource Constraints** — Be realistic about achievable improvements:
   - Moving one tier typically takes 12-18 months per category
   - Budget for technology, staffing, and consulting support
   - Account for organizational change management

---

## Step 4: Gap Analysis

### Gap Identification

For each category, calculate the gap between current and target:

```
Gap = Target Tier - Current Tier
```

### Gap Classification

| Gap | Severity | Typical Remediation Timeline |
|-----|----------|------------------------------|
| 3+ | CRITICAL | Immediate action, 3-6 months to achieve interim state |
| 2 | HIGH | 6-12 months, significant investment required |
| 1 | MEDIUM | 6-12 months, incremental improvement |
| 0 | At Target | Maintain and continuously improve |

### Gap Prioritization Framework

Prioritize gaps using a weighted scoring model:

| Factor | Weight | Scoring |
|--------|--------|---------|
| Regulatory Impact | 30% | High (10) — regulation mandates control; Medium (5) — recommended; Low (1) — optional |
| Risk Reduction | 25% | High (10) — addresses critical risk; Medium (5) — moderate risk; Low (1) — minimal risk |
| Gap Size | 20% | 3+ (10); 2 (7); 1 (3) |
| Implementation Feasibility | 15% | Easy (10); Moderate (5); Difficult (1) |
| Cost Efficiency | 10% | Addresses multiple gaps (10); Single gap (5); Partial (1) |

**Prioritization Score = Σ(Factor Score × Weight)**

### Using the Assessment Tool

```bash
# Generate gap analysis
python scripts/csf_maturity_assessor.py \
  --input current_assessment.json \
  --target-tier 3 \
  --format markdown \
  --output gap_analysis.md

# Map gaps to other framework requirements
python scripts/csf_control_mapper.py \
  --source-framework nist-csf \
  --target-framework all \
  --format markdown \
  --output unified_matrix.md
```

---

## Step 5: Remediation Roadmap

### Phased Approach

**Phase 1: Quick Wins and Critical Gaps (Months 1-3)**
- Enable MFA for all users (PR.AA)
- Deploy or tune SIEM for critical log sources (DE.CM)
- Document incident response plan (RS.MA)
- Establish asset inventory baseline (ID.AM)
- Create cybersecurity policy framework (GV.PO)

**Phase 2: Foundation Building (Months 4-6)**
- Implement PAM for privileged accounts (PR.AA)
- Deploy data loss prevention for critical data (PR.DS)
- Establish risk management strategy (GV.RM)
- Conduct comprehensive risk assessment (ID.RA)
- Launch security awareness program (PR.AT)

**Phase 3: Program Maturation (Months 7-9)**
- Implement zero trust architecture principles (PR.AA)
- Deploy EDR/XDR across all endpoints (DE.CM)
- Establish threat hunting program (DE.AE)
- Test incident response via tabletop exercises (RS.MA)
- Apply hardening baselines across all systems (PR.PS)

**Phase 4: Optimization and Resilience (Months 10-12)**
- Implement supply chain risk management (GV.SC)
- Test and validate disaster recovery (RC.RP)
- Establish continuous improvement processes (ID.IM)
- Deploy SOAR for automated response (RS.MI)
- Conduct full maturity reassessment

### Roadmap Template

| Phase | Month | Category | Activity | Owner | Budget | Status |
|-------|-------|----------|----------|-------|--------|--------|
| 1 | 1-3 | PR.AA | Deploy MFA organization-wide | Security Eng | $50K | |
| 1 | 1-3 | DE.CM | Configure SIEM critical log sources | SOC Lead | $30K | |
| 1 | 1-3 | RS.MA | Document and test IR plan | CISO | $10K | |
| 2 | 4-6 | PR.AA | Implement PAM solution | Security Eng | $100K | |
| 2 | 4-6 | GV.RM | Establish risk management strategy | Risk Analyst | $20K | |
| 3 | 7-9 | PR.PS | Apply CIS Benchmarks across infrastructure | IT Ops | $40K | |
| 3 | 7-9 | DE.AE | Launch threat hunting program | SOC Lead | $60K | |
| 4 | 10-12 | GV.SC | Implement C-SCRM program | Compliance | $30K | |
| 4 | 10-12 | RC.RP | DR testing and validation | IT Ops | $25K | |

---

## Step 6: Implementation Execution

### Implementation Best Practices

1. **Start with governance** — Without governance (GOVERN), technical controls lack strategic direction
2. **Build from identify** — You cannot protect what you have not identified
3. **Layer defenses** — Implement PROTECT, then DETECT, then RESPOND, then RECOVER
4. **Test continuously** — Validate controls through exercises and assessments
5. **Measure progress** — Track maturity scores monthly during active implementation

### Common Implementation Pitfalls

| Pitfall | Mitigation |
|---------|------------|
| Tool-first approach | Define process first, then select tools to support |
| No executive sponsorship | Secure commitment before starting; use breach cost data |
| Scope creep | Define scope clearly in Phase 1; resist expanding mid-cycle |
| Compliance checkbox mentality | Focus on risk reduction, not just documentation |
| Ignoring GOVERN function | GOVERN drives everything; skip it and implementation lacks direction |
| Perfect is the enemy of good | Aim for Tier 3 first, then iterate toward Tier 4 |
| No stakeholder engagement | Involve business units early; security is everyone's responsibility |

### Control Implementation Pattern

For each control being implemented:

1. **Document** — Write the policy/standard/procedure
2. **Implement** — Deploy the technical or administrative control
3. **Test** — Validate the control works as intended
4. **Evidence** — Capture proof of implementation for auditors
5. **Monitor** — Establish ongoing monitoring for the control
6. **Review** — Schedule periodic review of control effectiveness

---

## Step 7: Continuous Monitoring and Improvement

### Ongoing Assessment Cadence

| Activity | Frequency | Owner |
|----------|-----------|-------|
| Full CSF maturity assessment | Annual | Program Lead |
| Function-specific deep dives | Quarterly (rotate functions) | Security Team |
| Risk register review | Quarterly | Risk Analyst |
| Policy review | Annual | Compliance |
| Tabletop exercise | Quarterly | IR Lead |
| Full incident simulation | Annual | CISO |
| Board reporting | Quarterly | CISO |
| Supplier assessments | Annual for critical, biannual for others | Compliance |
| Training and phishing simulations | Quarterly | Security Awareness Lead |

### Metrics Dashboard

Track these metrics quarterly:

**GOVERN Metrics:**
- Policy coverage (% of CSF categories with approved policies)
- Board reporting frequency and metrics completeness
- Supplier assessment coverage (% of critical suppliers assessed)

**IDENTIFY Metrics:**
- Asset inventory accuracy (validated through sampling)
- Risk assessment currency (% of critical systems with current risk assessment)
- Improvement action closure rate

**PROTECT Metrics:**
- MFA adoption rate (% of users with MFA enabled)
- Privileged access review completion rate
- Patch SLA compliance (% patched within SLA by severity)
- Training completion rate
- Data classification coverage

**DETECT Metrics:**
- SIEM log source coverage (% of critical systems sending logs)
- Mean Time to Detect (MTTD)
- Detection true positive rate
- MITRE ATT&CK detection coverage (% of techniques with rules)

**RESPOND Metrics:**
- Mean Time to Respond (MTTR)
- Incident containment success rate
- Tabletop exercise completion rate
- Regulatory notification compliance rate

**RECOVER Metrics:**
- RPO/RTO achievement rate (actual vs target)
- Backup restoration success rate
- Post-incident improvement implementation rate

---

## Cross-Framework Mapping Tables

### NIST CSF 2.0 → ISO 27001:2022 Detailed Mapping

| CSF ID | CSF Category | ISO 27001 Clause/Control | Notes |
|--------|---|---|---|
| GV.OC | Organizational Context | 4.1, 4.2, A.5.1, A.5.2, A.5.4 | Context of the organization, interested parties |
| GV.RM | Risk Management Strategy | 6.1, 6.1.2, 6.1.3, A.5.3 | Risk assessment and treatment process |
| GV.RR | Roles and Responsibilities | 5.3, A.5.2, 7.1, 7.2 | Roles, competence, resources |
| GV.PO | Policy | A.5.1, A.5.37 | Policies for information security |
| GV.OV | Oversight | 9.1, 9.2, 9.3, 10.1 | Monitoring, internal audit, management review |
| GV.SC | Supply Chain | A.5.19–A.5.23 | Supplier relationship security |
| ID.AM | Asset Management | A.5.9, A.5.10, A.5.11, A.5.12, A.5.13, A.8.1 | Asset inventory, classification, labeling |
| ID.RA | Risk Assessment | 6.1.2, A.5.7, A.8.8 | Risk assessment process, threat intel, vuln mgmt |
| ID.IM | Improvement | 10.1, 10.2 | Continual improvement, corrective action |
| PR.AA | Access Control | A.5.15–A.5.18, A.8.2–A.8.5 | Identity, authentication, access management |
| PR.AT | Training | A.6.3, 7.2, 7.3 | Awareness, competence |
| PR.DS | Data Security | A.8.10–A.8.12, A.8.24, A.8.25 | Data protection, cryptography |
| PR.PS | Platform Security | A.8.9, A.8.19, A.8.20 | Configuration, software, network security |
| PR.IR | Resilience | A.5.29, A.5.30, A.8.6, A.8.14 | Continuity, capacity, redundancy |
| DE.CM | Monitoring | A.8.15, A.8.16 | Logging, monitoring |
| DE.AE | Event Analysis | A.5.7, A.8.15, A.8.16 | Threat intel, log analysis |
| RS.MA | Incident Management | A.5.24–A.5.26 | Incident planning, assessment, response |
| RS.AN | Incident Analysis | A.5.27, A.5.28 | Lessons learned, evidence |
| RS.CO | Communication | A.5.5, A.5.6, A.5.26 | Authority and interest group contact |
| RS.MI | Mitigation | A.5.26 | Incident response actions |
| RC.RP | Recovery Execution | A.5.29, A.5.30 | ICT continuity |
| RC.CO | Recovery Communication | A.5.5, A.5.6 | Communication during recovery |

### NIST CSF 2.0 → SOC 2 TSC Detailed Mapping

| CSF Function | SOC 2 TSC | TSC Description |
|---|---|---|
| GOVERN | CC1.1–CC1.5 | Control Environment: integrity, ethics, oversight, structure, accountability |
| GOVERN | CC2.1–CC2.3 | Communication and Information: quality, internal, external |
| IDENTIFY | CC3.1–CC3.4 | Risk Assessment: objectives, identification, analysis, change impact |
| PROTECT | CC5.1–CC5.3 | Control Activities: selection, implementation, technology controls |
| PROTECT | CC6.1–CC6.8 | Logical and Physical Access: controls, credentials, authorization, encryption |
| DETECT | CC7.1–CC7.5 | System Operations: monitoring, anomalies, evaluation, response, remediation |
| RESPOND | CC7.3–CC7.5 | System Operations: evaluation, response, remediation |
| RECOVER | CC9.1–CC9.2 | Risk Mitigation: identification, vendor management |
| RECOVER | A1.1–A1.3 | Availability: capacity, recovery, testing |

### NIST CSF 2.0 → HIPAA Security Rule Detailed Mapping

| CSF Category | HIPAA Provision | HIPAA Description |
|---|---|---|
| GV.OC, GV.RM | §164.308(a)(1)(i) | Security management process |
| GV.RR | §164.308(a)(2) | Assigned security responsibility |
| GV.PO | §164.316(a), (b) | Policies, procedures, documentation |
| GV.SC | §164.308(b)(1), §164.314(a) | Business associate contracts |
| ID.RA | §164.308(a)(1)(ii)(A) | Risk analysis |
| ID.RA | §164.308(a)(1)(ii)(B) | Risk management |
| PR.AA | §164.312(a)(1) | Access control |
| PR.AA | §164.312(a)(2)(i) | Unique user identification |
| PR.AA | §164.312(d) | Person or entity authentication |
| PR.AT | §164.308(a)(5) | Security awareness and training |
| PR.DS | §164.312(a)(2)(iv) | Encryption and decryption |
| PR.DS | §164.312(e)(1) | Transmission security |
| PR.PS | §164.310(a)(1), (d)(1) | Facility access, device and media |
| DE.CM | §164.312(b) | Audit controls |
| DE.AE | §164.308(a)(1)(ii)(D) | Information system activity review |
| RS.MA | §164.308(a)(6)(i), (ii) | Security incident procedures |
| RC.RP | §164.308(a)(7)(ii)(B), (C) | Disaster recovery, emergency mode |
| RS.CO, RC.CO | §164.404, §164.408 | Breach notification |

### NIST CSF 2.0 → PCI-DSS v4.0 Detailed Mapping

| CSF Category | PCI-DSS Requirements | PCI-DSS Description |
|---|---|---|
| GV.PO | Req 12.1 | Information security policy |
| GV.RR | Req 12.1.2, 12.4.1 | Roles, executive responsibility |
| GV.RM | Req 12.3.1, 12.3.2 | Targeted risk analysis |
| GV.SC | Req 12.8 | Third-party service providers |
| GV.OV | Req 12.4.2 | PCI DSS compliance reviews |
| ID.AM | Req 2.1, 2.2, 12.5.1 | System inventory, scope documentation |
| ID.RA | Req 6.3.1, 11.3 | Vulnerability identification, pen testing |
| PR.AA | Req 7.1–7.3, 8.1–8.6 | Access control, authentication |
| PR.AT | Req 12.6 | Security awareness |
| PR.DS | Req 3.1–3.7, 4.1–4.2 | Data protection, cryptography |
| PR.PS | Req 1.1–1.5, 2.1–2.3, 5.1–5.4, 6.1–6.3 | Network, config, malware, secure dev |
| DE.CM | Req 10.1–10.7, 11.1–11.6 | Logging, monitoring, testing |
| RS.MA | Req 12.10.1–12.10.4 | Incident response plan |
| RS.AN | Req 12.10.5, 12.10.6 | IR improvement, alerts |

---

## Resource and Budget Planning

### Estimated Investment by Organization Size

| Category | Small (<500 employees) | Mid-size (500-5,000) | Enterprise (5,000+) |
|----------|------------------------|---------------------|---------------------|
| Assessment | $20K-50K | $75K-150K | $200K-500K |
| Technology (Year 1) | $50K-150K | $200K-500K | $500K-2M |
| Staffing (Annual) | 2-3 FTE | 5-10 FTE | 15-30 FTE |
| Training | $10K-25K | $50K-100K | $150K-300K |
| Consulting | $25K-75K | $100K-250K | $250K-750K |
| **Year 1 Total** | **$150K-400K** | **$600K-1.5M** | **$1.5M-5M** |
| **Annual Ongoing** | **$100K-250K** | **$400K-800K** | **$1M-3M** |

### Technology Investment Priorities

**Phase 1 (Highest ROI):**
- MFA/SSO platform — Addresses PR.AA, most common attack vector
- SIEM or managed SIEM — Enables DE.CM, foundational for detection
- Vulnerability scanner — Supports ID.RA, PR.PS

**Phase 2 (Strong ROI):**
- PAM solution — Addresses PR.AA for privileged accounts
- EDR/XDR — Enhances DE.CM endpoint visibility
- DLP — Supports PR.DS data protection

**Phase 3 (Program Maturation):**
- SOAR — Automates RS.MA, RS.MI response activities
- GRC platform — Supports GV.OV, GV.PO governance and compliance
- Threat intelligence platform — Enhances DE.AE, ID.RA

**Phase 4 (Advanced Capabilities):**
- UEBA — Advanced DE.AE behavioral analytics
- SBOM management — Supports GV.SC supply chain
- Zero trust platform — Advanced PR.AA architecture

### Staffing Model

**Minimum viable security team (small organization):**
- CISO (fractional or part-time)
- Security Engineer (1 FTE)
- Security Analyst/SOC (1 FTE, or managed SOC)

**Mature security team (mid-size):**
- CISO (1 FTE)
- Security Architects (2 FTE)
- Security Engineers (2-3 FTE)
- SOC Analysts (3-5 FTE, or hybrid with managed SOC)
- GRC/Compliance Analyst (1-2 FTE)
- Risk Analyst (1 FTE)

---

## Templates

### Assessment Input Template

```json
{
  "organization": "Your Organization Name",
  "assessment_date": "YYYY-MM-DD",
  "assessor": "Assessment Team Lead Name",
  "functions": {
    "GOVERN": {
      "GV.OC": { "score": 0, "evidence": "", "notes": "" },
      "GV.RM": { "score": 0, "evidence": "", "notes": "" },
      "GV.RR": { "score": 0, "evidence": "", "notes": "" },
      "GV.PO": { "score": 0, "evidence": "", "notes": "" },
      "GV.OV": { "score": 0, "evidence": "", "notes": "" },
      "GV.SC": { "score": 0, "evidence": "", "notes": "" }
    },
    "IDENTIFY": {
      "ID.AM": { "score": 0, "evidence": "", "notes": "" },
      "ID.RA": { "score": 0, "evidence": "", "notes": "" },
      "ID.IM": { "score": 0, "evidence": "", "notes": "" }
    },
    "PROTECT": {
      "PR.AA": { "score": 0, "evidence": "", "notes": "" },
      "PR.AT": { "score": 0, "evidence": "", "notes": "" },
      "PR.DS": { "score": 0, "evidence": "", "notes": "" },
      "PR.PS": { "score": 0, "evidence": "", "notes": "" },
      "PR.IR": { "score": 0, "evidence": "", "notes": "" }
    },
    "DETECT": {
      "DE.CM": { "score": 0, "evidence": "", "notes": "" },
      "DE.AE": { "score": 0, "evidence": "", "notes": "" }
    },
    "RESPOND": {
      "RS.MA": { "score": 0, "evidence": "", "notes": "" },
      "RS.AN": { "score": 0, "evidence": "", "notes": "" },
      "RS.CO": { "score": 0, "evidence": "", "notes": "" },
      "RS.MI": { "score": 0, "evidence": "", "notes": "" }
    },
    "RECOVER": {
      "RC.RP": { "score": 0, "evidence": "", "notes": "" },
      "RC.CO": { "score": 0, "evidence": "", "notes": "" }
    }
  }
}
```

### Executive Summary Template

```
NIST CSF 2.0 Maturity Assessment — Executive Summary
Organization: [Name]
Date: [Date]
Assessor: [Name]

OVERALL MATURITY: [Score] / 4.0 ([Tier Name])
TARGET: [Target Score] / 4.0 ([Target Tier Name])

FUNCTION SCORES:
  GOVERN:   [Score] / 4.0  [▓▓▓░░░░░]
  IDENTIFY: [Score] / 4.0  [▓▓▓▓░░░░]
  PROTECT:  [Score] / 4.0  [▓▓░░░░░░]
  DETECT:   [Score] / 4.0  [▓▓▓░░░░░]
  RESPOND:  [Score] / 4.0  [▓▓░░░░░░]
  RECOVER:  [Score] / 4.0  [▓░░░░░░░]

TOP GAPS:
  1. [Category] — Gap: [X] tiers, Priority: [CRITICAL/HIGH]
  2. [Category] — Gap: [X] tiers, Priority: [CRITICAL/HIGH]
  3. [Category] — Gap: [X] tiers, Priority: [HIGH]

RECOMMENDED NEXT STEPS:
  Phase 1 (Months 1-3): [Summary]
  Phase 2 (Months 4-6): [Summary]
  Phase 3 (Months 7-12): [Summary]

ESTIMATED INVESTMENT: $[Amount] over 12 months
RISK REDUCTION: [Estimated] critical/high gaps closed
```
