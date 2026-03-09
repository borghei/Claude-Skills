---
name: risk-management-specialist
description: Medical device risk management specialist implementing ISO 14971 throughout product lifecycle. Provides risk analysis, risk evaluation, risk control, and post-production information analysis.
triggers:
  - risk management
  - ISO 14971
  - risk analysis
  - FMEA
  - fault tree analysis
  - hazard identification
  - risk control
  - risk matrix
  - benefit-risk analysis
  - residual risk
  - risk acceptability
  - post-market risk
---

# Risk Management Specialist

ISO 14971:2019 risk management implementation throughout the medical device lifecycle.

---

## Table of Contents

- [Risk Management Planning Workflow](#risk-management-planning-workflow)
- [Risk Analysis Workflow](#risk-analysis-workflow)
- [Risk Evaluation Workflow](#risk-evaluation-workflow)
- [Risk Control Workflow](#risk-control-workflow)
- [Post-Production Risk Management](#post-production-risk-management)
- [Risk Assessment Templates](#risk-assessment-templates)
- [Decision Frameworks](#decision-frameworks)
- [Tools and References](#tools-and-references)

---

## Risk Management Planning Workflow

Establish risk management process per ISO 14971.

### Workflow: Create Risk Management Plan

1. Define scope of risk management activities:
   - Medical device identification
   - Lifecycle stages covered
   - Applicable standards and regulations
2. Establish risk acceptability criteria:
   - Define probability categories (P1-P5)
   - Define severity categories (S1-S5)
   - Create risk matrix with acceptance thresholds
3. Assign responsibilities:
   - Risk management lead
   - Subject matter experts
   - Approval authorities
4. Define verification activities:
   - Methods for control verification
   - Acceptance criteria
5. Plan production and post-production activities:
   - Information sources
   - Review triggers
   - Update procedures
6. Obtain plan approval
7. Establish risk management file
8. **Validation:** Plan approved; acceptability criteria defined; responsibilities assigned; file established

### Risk Management Plan Content

| Section | Content | Evidence |
|---------|---------|----------|
| Scope | Device and lifecycle coverage | Scope statement |
| Criteria | Risk acceptability matrix | Risk matrix document |
| Responsibilities | Roles and authorities | RACI chart |
| Verification | Methods and acceptance | Verification plan |
| Production/Post-Production | Monitoring activities | Surveillance plan |

### Risk Acceptability Matrix (5x5)

| Probability \ Severity | Negligible | Minor | Serious | Critical | Catastrophic |
|------------------------|------------|-------|---------|----------|--------------|
| **Frequent (P5)** | Medium | High | High | Unacceptable | Unacceptable |
| **Probable (P4)** | Medium | Medium | High | High | Unacceptable |
| **Occasional (P3)** | Low | Medium | Medium | High | High |
| **Remote (P2)** | Low | Low | Medium | Medium | High |
| **Improbable (P1)** | Low | Low | Low | Medium | Medium |

### Risk Level Actions

| Level | Acceptable | Action Required |
|-------|------------|-----------------|
| Low | Yes | Document and accept |
| Medium | ALARP | Reduce if practicable; document rationale |
| High | ALARP | Reduction required; demonstrate ALARP |
| Unacceptable | No | Design change mandatory |

---

## Risk Analysis Workflow

Identify hazards and estimate risks systematically.

### Workflow: Conduct Risk Analysis

1. Define intended use and reasonably foreseeable misuse:
   - Medical indication
   - Patient population
   - User population
   - Use environment
2. Select analysis method(s):
   - FMEA for component/function analysis
   - FTA for system-level analysis
   - HAZOP for process deviations
   - Use Error Analysis for user interaction
3. Identify hazards by category:
   - Energy hazards (electrical, mechanical, thermal)
   - Biological hazards (bioburden, biocompatibility)
   - Chemical hazards (residues, leachables)
   - Operational hazards (software, use errors)
4. Determine hazardous situations:
   - Sequence of events
   - Foreseeable misuse scenarios
   - Single fault conditions
5. Estimate probability of harm (P1-P5)
6. Estimate severity of harm (S1-S5)
7. Document in hazard analysis worksheet
8. **Validation:** All hazard categories addressed; all hazards documented; probability and severity assigned

### Hazard Categories Checklist

| Category | Examples | Analyzed |
|----------|----------|----------|
| Electrical | Shock, burns, interference | ☐ |
| Mechanical | Crushing, cutting, entrapment | ☐ |
| Thermal | Burns, tissue damage | ☐ |
| Radiation | Ionizing, non-ionizing | ☐ |
| Biological | Infection, biocompatibility | ☐ |
| Chemical | Toxicity, irritation | ☐ |
| Software | Incorrect output, timing | ☐ |
| Use Error | Misuse, perception, cognition | ☐ |
| Environment | EMC, mechanical stress | ☐ |

### Analysis Method Selection

| Situation | Recommended Method |
|-----------|-------------------|
| Component failures | FMEA |
| System-level failure | FTA |
| Process deviations | HAZOP |
| User interaction | Use Error Analysis |
| Software behavior | Software FMEA |
| Early design phase | PHA |

### Probability Criteria

| Level | Name | Description | Frequency |
|-------|------|-------------|-----------|
| P5 | Frequent | Expected to occur | >10⁻³ |
| P4 | Probable | Likely to occur | 10⁻³ to 10⁻⁴ |
| P3 | Occasional | May occur | 10⁻⁴ to 10⁻⁵ |
| P2 | Remote | Unlikely | 10⁻⁵ to 10⁻⁶ |
| P1 | Improbable | Very unlikely | <10⁻⁶ |

### Severity Criteria

| Level | Name | Description | Harm |
|-------|------|-------------|------|
| S5 | Catastrophic | Death | Death |
| S4 | Critical | Permanent impairment | Irreversible injury |
| S3 | Serious | Injury requiring intervention | Reversible injury |
| S2 | Minor | Temporary discomfort | No treatment needed |
| S1 | Negligible | Inconvenience | No injury |

See: [references/risk-analysis-methods.md](references/risk-analysis-methods.md)

---

## Risk Evaluation Workflow

Evaluate risks against acceptability criteria.

### Workflow: Evaluate Identified Risks

1. Calculate initial risk level from probability × severity
2. Compare to risk acceptability criteria
3. For each risk, determine:
   - Acceptable: Document and accept
   - ALARP: Proceed to risk control
   - Unacceptable: Mandatory risk control
4. Document evaluation rationale
5. Identify risks requiring benefit-risk analysis
6. Complete benefit-risk analysis if applicable
7. Compile risk evaluation summary
8. **Validation:** All risks evaluated; acceptability determined; rationale documented

### Risk Evaluation Decision Tree

```
Risk Estimated
      │
      ▼
Apply Acceptability Criteria
      │
      ├── Low Risk ──────────► Accept and document
      │
      ├── Medium Risk ───────► Consider risk reduction
      │   │                    Document ALARP if not reduced
      │   ▼
      │   Practicable to reduce?
      │   │
      │   Yes──► Implement control
      │   No───► Document ALARP rationale
      │
      ├── High Risk ─────────► Risk reduction required
      │   │                    Must demonstrate ALARP
      │   ▼
      │   Implement control
      │   Verify residual risk
      │
      └── Unacceptable ──────► Design change mandatory
                               Cannot proceed without control
```

### ALARP Demonstration Requirements

| Criterion | Evidence Required |
|-----------|-------------------|
| Technical feasibility | Analysis of alternative controls |
| Proportionality | Cost-benefit of further reduction |
| State of the art | Comparison to similar devices |
| Stakeholder input | Clinical/user perspectives |

### Benefit-Risk Analysis Triggers

| Situation | Benefit-Risk Required |
|-----------|----------------------|
| Residual risk remains high | Yes |
| No feasible risk reduction | Yes |
| Novel device | Yes |
| Unacceptable risk with clinical benefit | Yes |
| All risks low | No |

---

## Risk Control Workflow

Implement and verify risk control measures.

### Workflow: Implement Risk Controls

1. Identify risk control options:
   - Inherent safety by design (Priority 1)
   - Protective measures in device (Priority 2)
   - Information for safety (Priority 3)
2. Select optimal control following hierarchy
3. Analyze control for new hazards introduced
4. Document control in design requirements
5. Implement control in design
6. Develop verification protocol
7. Execute verification and document results
8. Evaluate residual risk with control in place
9. **Validation:** Control implemented; verification passed; residual risk acceptable; no unaddressed new hazards

### Risk Control Hierarchy

| Priority | Control Type | Examples | Effectiveness |
|----------|--------------|----------|---------------|
| 1 | Inherent Safety | Eliminate hazard, fail-safe design | Highest |
| 2 | Protective Measures | Guards, alarms, automatic shutdown | High |
| 3 | Information | Warnings, training, IFU | Lower |

### Risk Control Option Analysis Template

```
RISK CONTROL OPTION ANALYSIS

Hazard ID: H-[XXX]
Hazard: [Description]
Initial Risk: P[X] × S[X] = [Level]

OPTIONS CONSIDERED:
| Option | Control Type | New Hazards | Feasibility | Selected |
|--------|--------------|-------------|-------------|----------|
| 1 | [Type] | [Yes/No] | [H/M/L] | [Yes/No] |
| 2 | [Type] | [Yes/No] | [H/M/L] | [Yes/No] |

SELECTED CONTROL: Option [X]
Rationale: [Justification for selection]

IMPLEMENTATION:
- Requirement: [REQ-XXX]
- Design Document: [Reference]

VERIFICATION:
- Method: [Test/Analysis/Review]
- Protocol: [Reference]
- Acceptance Criteria: [Criteria]
```

### Risk Control Verification Methods

| Method | When to Use | Evidence |
|--------|-------------|----------|
| Test | Quantifiable performance | Test report |
| Inspection | Physical presence | Inspection record |
| Analysis | Design calculation | Analysis report |
| Review | Documentation check | Review record |

### Residual Risk Evaluation

| After Control | Action |
|---------------|--------|
| Acceptable | Document, proceed |
| ALARP achieved | Document rationale, proceed |
| Still unacceptable | Additional control or design change |
| New hazard introduced | Analyze and control new hazard |

---

## Post-Production Risk Management

Monitor and update risk management throughout product lifecycle.

### Workflow: Post-Production Risk Monitoring

1. Identify information sources:
   - Customer complaints
   - Service reports
   - Vigilance/adverse events
   - Literature monitoring
   - Clinical studies
2. Establish collection procedures
3. Define review triggers:
   - New hazard identified
   - Increased frequency of known hazard
   - Serious incident
   - Regulatory feedback
4. Analyze incoming information for risk relevance
5. Update risk management file as needed
6. Communicate significant findings
7. Conduct periodic risk management review
8. **Validation:** Information sources monitored; file current; reviews completed per schedule

### Information Sources

| Source | Information Type | Review Frequency |
|--------|------------------|------------------|
| Complaints | Use issues, failures | Continuous |
| Service | Field failures, repairs | Monthly |
| Vigilance | Serious incidents | Immediate |
| Literature | Similar device issues | Quarterly |
| Regulatory | Authority feedback | As received |
| Clinical | PMCF data | Per plan |

### Risk Management File Update Triggers

| Trigger | Response Time | Action |
|---------|---------------|--------|
| Serious incident | Immediate | Full risk review |
| New hazard identified | 30 days | Risk analysis update |
| Trend increase | 60 days | Trend analysis |
| Design change | Before implementation | Impact assessment |
| Standards update | Per transition period | Gap analysis |

### Periodic Review Requirements

| Review Element | Frequency |
|----------------|-----------|
| Risk management file completeness | Annual |
| Risk control effectiveness | Annual |
| Post-market information analysis | Quarterly |
| Risk-benefit conclusions | Annual or on new data |

---

## Risk Assessment Templates

### Hazard Analysis Worksheet

```
HAZARD ANALYSIS WORKSHEET

Product: [Device Name]
Document: HA-[Product]-[Rev]
Analyst: [Name]
Date: [Date]

| ID | Hazard | Hazardous Situation | Harm | P | S | Initial Risk | Control | Residual P | Residual S | Final Risk |
|----|--------|---------------------|------|---|---|--------------|---------|------------|------------|------------|
| H-001 | [Hazard] | [Situation] | [Harm] | [1-5] | [1-5] | [Level] | [Control ref] | [1-5] | [1-5] | [Level] |
```

### FMEA Worksheet

```
FMEA WORKSHEET

Product: [Device Name]
Subsystem: [Subsystem]
Analyst: [Name]
Date: [Date]

| ID | Item | Function | Failure Mode | Effect | S | Cause | O | Control | D | RPN | Action |
|----|------|----------|--------------|--------|---|-------|---|---------|---|-----|--------|
| FM-001 | [Item] | [Function] | [Mode] | [Effect] | [1-10] | [Cause] | [1-10] | [Detection] | [1-10] | [S×O×D] | [Action] |

RPN Action Thresholds:
>200: Critical - Immediate action
100-200: High - Action plan required
50-100: Medium - Consider action
<50: Low - Monitor
```

### Risk Management Report Summary

```
RISK MANAGEMENT REPORT

Product: [Device Name]
Date: [Date]
Revision: [X.X]

SUMMARY:
- Total hazards identified: [N]
- Risk controls implemented: [N]
- Residual risks: [N] Low, [N] Medium, [N] High
- Overall conclusion: [Acceptable / Not Acceptable]

RISK DISTRIBUTION:
| Risk Level | Before Control | After Control |
|------------|----------------|---------------|
| Unacceptable | [N] | 0 |
| High | [N] | [N] |
| Medium | [N] | [N] |
| Low | [N] | [N] |

CONTROLS IMPLEMENTED:
- Inherent safety: [N]
- Protective measures: [N]
- Information for safety: [N]

OVERALL RESIDUAL RISK: [Acceptable / ALARP Demonstrated]
BENEFIT-RISK CONCLUSION: [If applicable]

APPROVAL:
Risk Management Lead: _____________ Date: _______
Quality Assurance: _____________ Date: _______
```

---

## Decision Frameworks

### Risk Control Selection

```
What is the risk level?
        │
        ├── Unacceptable ──► Can hazard be eliminated?
        │                    │
        │                Yes─┴─No
        │                 │     │
        │                 ▼     ▼
        │            Eliminate  Can protective
        │            hazard     measure reduce?
        │                           │
        │                       Yes─┴─No
        │                        │     │
        │                        ▼     ▼
        │                   Add       Add warning
        │                   protection + training
        │
        └── High/Medium ──► Apply hierarchy
                            starting at Level 1
```

### New Hazard Analysis

| Question | If Yes | If No |
|----------|--------|-------|
| Does control introduce new hazard? | Analyze new hazard | Proceed |
| Is new risk higher than original? | Reject control option | Acceptable trade-off |
| Can new hazard be controlled? | Add control | Reject control option |

### Risk Acceptability Decision

| Condition | Decision |
|-----------|----------|
| All risks Low | Acceptable |
| Medium risks with ALARP | Acceptable |
| High risks with ALARP documented | Acceptable if benefits outweigh |
| Any Unacceptable residual | Not acceptable - redesign |

---

## Tools and References

### Scripts

| Tool | Purpose | Usage |
|------|---------|-------|
| [risk_matrix_calculator.py](scripts/risk_matrix_calculator.py) | Calculate risk levels and FMEA RPN | `python risk_matrix_calculator.py --help` |

**Risk Matrix Calculator Features:**
- ISO 14971 5x5 risk matrix calculation
- FMEA RPN (Risk Priority Number) calculation
- Interactive mode for guided assessment
- Display risk criteria definitions
- JSON output for integration

### References

| Document | Content |
|----------|---------|
| [iso14971-implementation-guide.md](references/iso14971-implementation-guide.md) | Complete ISO 14971:2019 implementation with templates |
| [risk-analysis-methods.md](references/risk-analysis-methods.md) | FMEA, FTA, HAZOP, Use Error Analysis methods |

### Quick Reference: ISO 14971 Process

| Stage | Key Activities | Output |
|-------|----------------|--------|
| Planning | Define scope, criteria, responsibilities | Risk Management Plan |
| Analysis | Identify hazards, estimate risk | Hazard Analysis |
| Evaluation | Compare to criteria, ALARP assessment | Risk Evaluation |
| Control | Implement hierarchy, verify | Risk Control Records |
| Residual | Overall assessment, benefit-risk | Risk Management Report |
| Production | Monitor, review, update | Updated RM File |

---

## Related Skills

| Skill | Integration Point |
|-------|-------------------|
| [quality-manager-qms-iso13485](../quality-manager-qms-iso13485/) | QMS integration |
| [capa-officer](../capa-officer/) | Risk-based CAPA |
| [regulatory-affairs-head](../regulatory-affairs-head/) | Regulatory submissions |
| [quality-documentation-manager](../quality-documentation-manager/) | Risk file management |

---

## AI-Specific Risk Management (ISO 14971 + AI Risk Considerations)

### AI/ML Medical Device Risk Categories

Traditional ISO 14971 hazard categories must be extended for AI/ML-based devices:

| AI-Specific Hazard | Description | Severity Potential | Detection Difficulty |
|--------------------|-------------|-------------------|---------------------|
| Model bias | Discriminatory outputs across patient subgroups | S3-S5 (misdiagnosis) | High — requires subgroup analysis |
| Data drift | Input data distribution shifts from training data | S2-S4 (degraded performance) | Medium — requires monitoring |
| Concept drift | Clinical ground truth changes over time | S3-S5 (outdated predictions) | High — requires clinical validation |
| Adversarial inputs | Intentionally crafted inputs to deceive model | S2-S5 (incorrect output) | High — requires adversarial testing |
| Hallucination/confabulation | Plausible but incorrect outputs | S3-S5 (false diagnosis) | Medium — requires output validation |
| Training data poisoning | Corrupted training data leads to systematic errors | S3-S5 | Very High — requires data provenance |
| Automation complacency | Users over-trust AI outputs | S3-S5 (missed clinical findings) | Medium — requires human factors study |

### AI Risk Analysis Methodology

```
Step 1: AI System Characterization
        → Define intended use, user population, clinical context
        → Classify: locked algorithm vs. adaptive vs. continuously learning
        → Map to SaMD risk framework (IMDRF)

Step 2: AI-Specific Hazard Identification
        → Apply standard ISO 14971 hazard categories
        → ADD: data quality hazards, algorithmic hazards, integration hazards
        → Consider: training data representativeness, edge cases, failure modes

Step 3: AI Failure Mode Analysis
        → Extend FMEA with AI-specific failure modes:
           - False positive/negative beyond acceptable rates
           - Performance degradation over time
           - Out-of-distribution input handling
           - Feature importance shift
        → For each failure mode: determine harm pathway to patient

Step 4: AI-Specific Risk Controls
        → Confidence thresholds (reject uncertain predictions)
        → Human-in-the-loop for high-risk decisions
        → Input validation and out-of-distribution detection
        → Continuous performance monitoring with drift detection
        → Automated model retraining safeguards
        → Fail-safe modes when AI system is unavailable

Step 5: AI Risk Monitoring Plan
        → Define performance metrics and acceptable thresholds
        → Establish monitoring frequency (real-time, daily, weekly)
        → Define retraining triggers and validation requirements
        → Plan for model versioning and rollback procedures
```

### AI Risk Acceptability Considerations

| Risk Factor | Additional Consideration for AI |
|-------------|--------------------------------|
| Probability | Include statistical confidence intervals for model performance |
| Severity | Consider both direct harm and harm from delayed correct treatment |
| Detectability | Factor in opacity of AI decision-making (explainability) |
| Benefit | Quantify clinical benefit vs. non-AI alternative |
| ALARP | State-of-the-art includes current AI best practices (GMLP) |

---

## Cybersecurity Risk Integration (IEC 81001-5-1)

### Health Software Cybersecurity Risk Management

IEC 81001-5-1:2021 establishes cybersecurity lifecycle requirements for health software. Integrate with ISO 14971:

| ISO 14971 Stage | IEC 81001-5-1 Integration | Combined Output |
|----------------|--------------------------|-----------------|
| Risk Management Plan | Include cybersecurity scope, threat modeling methodology | Combined RM + cybersecurity plan |
| Hazard identification | Add cybersecurity threat identification (STRIDE, attack trees) | Extended hazard analysis with cyber threats |
| Risk estimation | Estimate probability based on threat landscape and exploitability | Risk register with cyber-specific likelihood factors |
| Risk control | Implement security controls as risk mitigations | Controls traceable to both safety and security risks |
| Residual risk | Evaluate residual cybersecurity risk | Combined residual risk assessment |
| Post-production | Monitor threat landscape, CVE databases, incident reports | Integrated PMS + security monitoring |

### Cybersecurity Threat Categories for Medical Devices

| Threat Category | Examples | ISO 14971 Harm Pathway |
|----------------|----------|----------------------|
| Unauthorized access | Credential theft, privilege escalation | Modification of device settings → patient harm |
| Data breach | PHI exfiltration, ransomware | Loss of data availability → delayed treatment |
| Denial of service | Network flooding, resource exhaustion | Device unavailable → delayed diagnosis/treatment |
| Malware | Ransomware, trojans, supply chain compromise | Device malfunction → incorrect output |
| Data integrity | Man-in-the-middle, data manipulation | Corrupted clinical data → incorrect treatment |
| Supply chain | Compromised dependencies, malicious updates | Backdoor access → any harm pathway |

### Cybersecurity FMEA Extension

Add these columns to standard FMEA for cybersecurity failure modes:

```
CYBERSECURITY FMEA EXTENSION

| ID | Component | Security Function | Threat | Attack Vector | Exploitability | Impact | S | O | D | RPN | Security Control |
|----|-----------|-------------------|--------|---------------|---------------|--------|---|---|---|-----|-----------------|
| CS-001 | Auth module | User authentication | Credential theft | Phishing | High (8) | Full access | 8 | 6 | 4 | 192 | MFA + session management |
| CS-002 | Data store | Data confidentiality | SQL injection | Network input | Medium (5) | Data breach | 9 | 4 | 3 | 108 | Parameterized queries + WAF |
| CS-003 | Update mechanism | Integrity | Supply chain | Compromised update | Low (3) | Malware install | 10 | 2 | 7 | 140 | Code signing + integrity verification |
```

---

## Supply Chain Risk Management

### Medical Device Supply Chain Risks

| Risk Category | Description | Probability | Impact | Control Strategy |
|--------------|-------------|-------------|--------|-----------------|
| Single-source component | Critical component from sole supplier | Medium | Critical | Dual-source qualification, safety stock |
| Counterfeit components | Fraudulent parts entering supply chain | Low-Medium | Catastrophic | Supplier audits, incoming inspection, chain of custody |
| Supplier quality failure | Supplier QMS breakdown | Medium | High | Supplier qualification, periodic audits, quality agreements |
| Software dependency | Vulnerable or unsupported open-source library | High | Medium-High | SBOM management, vulnerability scanning, update policy |
| Geopolitical disruption | Sanctions, trade restrictions, supply interruption | Low-Medium | High | Geographic diversification, buffer inventory |
| Raw material shortage | Rare earth, specialty materials unavailability | Low | High | Alternative material qualification, forward contracts |

### Supply Chain Risk Assessment Workflow

```
Step 1: Supply Chain Mapping
        → Identify all direct suppliers (Tier 1)
        → Map critical Tier 2 and Tier 3 suppliers
        → Document component criticality (safety-critical, quality-critical, standard)

Step 2: Supplier Risk Scoring
        → Quality risk: past performance, certification status, audit results
        → Financial risk: stability, dependency on your business
        → Geographic risk: natural disaster, political stability
        → Cyber risk: supplier's information security posture
        → Concentration risk: single-source, regional concentration

Step 3: Risk Treatment
        → Critical suppliers: quality agreements, annual audits, dual-sourcing
        → High-risk suppliers: enhanced monitoring, contingency plans
        → Medium-risk suppliers: periodic review, performance metrics
        → Low-risk suppliers: standard purchasing controls

Step 4: Ongoing Monitoring
        → Supplier scorecard tracking (quality, delivery, responsiveness)
        → Annual supplier risk reassessment
        → Trigger-based reassessment (quality event, financial change, M&A)
```

---

## Post-Market Risk Monitoring Automation

### Automated Signal Detection

| Data Source | Automation Approach | Alert Threshold |
|------------|--------------------|-----------------|
| Complaint database | Statistical process control (SPC) charts on complaint rates | >2 sigma deviation from baseline |
| Adverse event reports | NLP-based classification + trend analysis | Any serious event; trend >3x baseline |
| Literature monitoring | Automated PubMed/regulatory database searches | New publication on similar device adverse events |
| Field service data | Automated failure rate tracking | Failure rate exceeds design MTBF by >20% |
| Social media/forums | Keyword monitoring for device-related complaints | Cluster of similar complaints in 30-day window |
| Regulatory databases | MAUDE, EUDAMED vigilance module, BfArM monitoring | New recall or safety communication for similar device |

### Risk Management File Update Automation

```
Automated Trigger → Risk Review Decision Tree

New complaint received
    → Classify by hazard category (auto or manual)
    → Check: Known hazard?
        YES → Update frequency data → Recalculate risk level
                → Risk level changed? → Flag for risk management review
        NO  → New hazard identified → Initiate risk analysis
              → Estimate initial risk → Determine controls needed
              → Update risk management file

Trend threshold exceeded
    → Generate trend report with statistical analysis
    → Convene risk management review within 30 days
    → Update risk management file with new probability estimates
    → Evaluate if additional risk controls needed
    → If safety issue: initiate FSCA/field action assessment
```

---

## Cross-Reference: NIST Cybersecurity Framework Risk Assessment

Map ISO 14971 risk management to NIST CSF 2.0 for comprehensive risk coverage:

| ISO 14971 Process | NIST CSF 2.0 Function | Integration Point |
|-------------------|----------------------|-------------------|
| Hazard identification | Identify (ID.RA) | Combine clinical and cyber threat identification |
| Risk estimation | Identify (ID.RA-03, ID.RA-04) | Unified likelihood and impact scales |
| Risk evaluation | Identify (ID.RA-05, ID.RA-06) | Single risk register with combined acceptance criteria |
| Risk control | Protect (PR), Detect (DE) | Security controls as risk mitigations |
| Residual risk evaluation | Govern (GV.RM) | Combined residual risk statement |
| Post-production monitoring | Detect (DE.CM, DE.AE) | Unified monitoring for safety and security events |

> **See also:** `../information-security-manager-iso27001/SKILL.md` for ISO 27001 security controls that serve as risk mitigations.

---

## Cross-Reference: DORA ICT Risk Management

For medical device companies operating as or supplying to financial entities in the EU, the Digital Operational Resilience Act (DORA, Regulation 2022/2554) adds ICT risk requirements:

| DORA Requirement | ISO 14971 Integration | Action |
|-----------------|----------------------|--------|
| ICT risk management framework (Art. 6) | Extend risk management plan to include ICT risks | Add ICT-specific risk categories to hazard analysis |
| ICT incident management (Art. 17) | Align with post-production monitoring | Unified incident classification and response |
| Digital operational resilience testing (Art. 24-27) | Complement risk control verification | Include penetration testing in verification activities |
| Third-party ICT risk (Art. 28-30) | Extend supply chain risk management | Assess ICT service providers per DORA requirements |
| Information sharing (Art. 45) | Enhance post-market information sources | Participate in threat intelligence sharing arrangements |

---

## Enhanced FMEA with Cybersecurity Failure Modes

### Combined Safety-Security FMEA Template

```
COMBINED SAFETY-SECURITY FMEA

Product: [Device Name]
Subsystem: [Subsystem]
Date: [Date]

TRADITIONAL SAFETY FAILURE MODES:
| ID | Item | Function | Failure Mode | Effect | S | Cause | O | Detection | D | RPN | Control |
|----|------|----------|--------------|--------|---|-------|---|-----------|---|-----|---------|
| FM-001 | Sensor | Measure vital sign | Incorrect reading | Wrong diagnosis | 8 | Calibration drift | 4 | Self-test | 3 | 96 | Auto-calibration |

CYBERSECURITY FAILURE MODES:
| ID | Asset | Security Objective | Threat | Attack Vector | Exploitability (O) | Impact (S) | Detection (D) | RPN | Security Control |
|----|-------|-------------------|--------|---------------|-------------------|-----------|---------------|-----|-----------------|
| CS-001 | Sensor data | Integrity | Data manipulation | MITM attack | 3 | 8 | 5 | 120 | TLS + data signing |
| CS-002 | Firmware | Integrity | Malicious update | Supply chain | 2 | 10 | 6 | 120 | Secure boot + code signing |
| CS-003 | User interface | Availability | DoS attack | Network flooding | 5 | 6 | 4 | 120 | Rate limiting + redundancy |

AI/ML FAILURE MODES (if applicable):
| ID | Component | ML Function | Failure Mode | Clinical Effect | S | Cause | O | Detection | D | RPN | ML Control |
|----|-----------|-------------|--------------|----------------|---|-------|---|-----------|---|-----|-----------|
| AI-001 | Classifier | Diagnose condition | False negative | Missed diagnosis | 9 | Distribution shift | 4 | Performance monitoring | 5 | 180 | Drift detection + human review |
| AI-002 | Classifier | Diagnose condition | Biased output | Health disparity | 8 | Unrepresentative training data | 3 | Subgroup analysis | 6 | 144 | Fairness constraints + diverse data |

COMBINED RPN THRESHOLDS:
>200: Critical — Immediate action required (all categories)
100-200: High — Action plan within 30 days
50-100: Medium — Monitor and consider action
<50: Low — Accept and monitor
```

### Cybersecurity-Safety Interaction Analysis

| Safety Control | Cybersecurity Impact | Mitigation |
|---------------|---------------------|------------|
| Alarm system | Alarm suppression via unauthorized access | Access control + alarm integrity monitoring |
| Fail-safe mode | Denial of service forcing perpetual safe mode | Rate limiting + redundant communication |
| Software update | Malicious update compromising safety function | Code signing + dual authorization + rollback capability |
| Data logging | Log tampering concealing safety events | Append-only logs + cryptographic integrity |
| User authentication | Lockout preventing emergency use | Break-glass procedures + local override |

---

## Enhanced Risk Management — AI, Cybersecurity & Cross-Framework Integration

### AI-Specific Risk Management

When managing risk for AI/ML medical devices, extend ISO 14971 with:

- **AI Model Risk:** Training data bias, model drift, adversarial attacks, explainability gaps
- **Performance Degradation:** Monitor for distribution shift, concept drift, and data quality issues
- **Algorithmic Bias:** Demographic parity, equalized odds, calibration across subgroups
- **Human-AI Interaction Risks:** Over-reliance, automation bias, alert fatigue, trust calibration
- **Cross-reference:** See `eu-ai-act-specialist` for EU AI Act risk classification

### Cybersecurity Risk Integration (IEC 81001-5-1)

- **Health Software Cybersecurity:** IEC 81001-5-1 extends ISO 14971 for cybersecurity
- **Threat Modeling:** STRIDE methodology applied to medical device architecture
- **Cybersecurity FMEA:** Failure modes include unauthorized access, data breach, ransomware, supply chain attack
- **Vulnerability Management:** CVSS scoring integrated with ISO 14971 severity/probability matrix
- **Cross-reference:** See `infrastructure-compliance-auditor` for technical security checks

### Supply Chain Risk Management

- **Component Risk:** Third-party software vulnerabilities (SBOM-based assessment)
- **Supplier Risk:** Single-source dependencies, geopolitical risks, quality history
- **Cloud Risk:** Data residency, service availability, vendor lock-in
- **Cross-reference:** See `nis2-directive-specialist` for NIS2 supply chain requirements

### Cross-Framework Risk Mapping

| Risk Area | ISO 14971 | NIST CSF 2.0 | DORA | NIS2 |
|-----------|-----------|-------------|------|------|
| Risk Assessment | Clause 4 | ID.RA | Art. 6 | Art. 21.1 |
| Risk Treatment | Clause 7 | PR (all) | Art. 9 | Art. 21.2 |
| Monitoring | Clause 9 | DE.CM | Art. 10 | Art. 21.2.f |
| Incident Response | Clause 9 | RS.MA | Art. 17 | Art. 23 |
| Continuous Improvement | Clause 10 | ID.IM | Art. 13 | Art. 21.2.f |
