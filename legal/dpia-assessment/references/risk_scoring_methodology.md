# DPIA Risk Scoring Methodology

Risk scoring system for Data Protection Impact Assessments from the data subject perspective per GDPR Recital 75 and EDPB guidance.

---

## Table of Contents

- [Scoring Scales](#scoring-scales)
- [Rights Categories](#rights-categories)
- [Risk Level Thresholds](#risk-level-thresholds)
- [Mitigation Effectiveness Scoring](#mitigation-effectiveness-scoring)
- [Residual Risk Calculation](#residual-risk-calculation)
- [Art. 36 Consultation Triggers](#art-36-consultation-triggers)
- [Risk Catalog](#risk-catalog)

---

## Scoring Scales

### Likelihood Scale

Likelihood assesses the probability of the risk materializing given the processing activity and its context.

| Level | Label | Probability | Description | Indicators |
|-------|-------|-------------|-------------|------------|
| 1 | Negligible | <5% | Extremely unlikely given current controls and processing context | No known attack vector; multiple layers of protection; no precedent |
| 2 | Limited | 5-25% | Unlikely but cannot be entirely ruled out | Theoretical vulnerability exists; similar incidents rare in industry |
| 3 | Significant | 25-50% | Reasonable possibility | Known vulnerabilities in similar systems; some industry precedent; partial controls |
| 4 | Maximum | 50-75% | More likely than not to occur | Active threats targeting similar processing; control gaps identified; industry incidents common |
| 5 | Almost certain | >75% | Expected to occur | Demonstrated vulnerability; active exploitation attempts; no effective controls |

### Severity Scale (Data Subject Perspective)

Severity is assessed exclusively from the data subject perspective per Recital 75. This is NOT about business impact to the controller.

| Level | Label | Description | Examples of Impact on Data Subjects |
|-------|-------|-------------|-------------------------------------|
| 1 | Negligible | Minor inconvenience that data subjects can easily overcome | Brief delay in service; minor administrative correction needed; temporary limited access |
| 2 | Limited | Significant inconvenience that data subjects can overcome with some effort | Need to re-register for service; minor financial cost to remediate; time spent dealing with issue |
| 3 | Significant | Consequences that data subjects may overcome with serious difficulties | Financial loss requiring recovery effort; reputational damage in limited circle; emotional distress |
| 4 | Maximum | Irreversible or very difficult to overcome consequences | Identity theft with financial impact; discriminatory treatment; job loss; health consequences |
| 5 | Critical | Consequences that cannot be overcome; existential impact | Physical harm or danger; severe financial ruin; irreversible discrimination; loss of liberty |

### Recital 75 Risk Sources

Recital 75 identifies these specific risk outcomes that must be assessed:

| Risk Outcome | Typical Severity |
|-------------|-----------------|
| Discrimination | 3-5 |
| Identity theft or fraud | 3-5 |
| Financial loss | 2-4 |
| Damage to reputation | 2-4 |
| Loss of confidentiality of data protected by professional secrecy | 3-5 |
| Unauthorized reversal of pseudonymisation | 2-4 |
| Significant economic or social disadvantage | 3-5 |
| Deprivation of rights and freedoms | 4-5 |
| Prevention from exercising control over personal data | 2-4 |
| Physical harm | 4-5 |

---

## Rights Categories

DPIA risks must be mapped to the specific fundamental rights they affect. This ensures the assessment covers all dimensions of impact.

| Category | Relevant Rights | GDPR Articles | Charter Articles |
|----------|----------------|---------------|-----------------|
| **Right to privacy** | Protection of personal data; private and family life | Art. 5, 6, 25, 32 | Art. 7, 8 EU Charter |
| **Non-discrimination** | Equal treatment regardless of protected characteristics | Art. 5(1)(a), 22 | Art. 21 EU Charter |
| **Freedom of expression** | Ability to express opinions without surveillance chilling effects | Art. 85, 89 | Art. 11 EU Charter |
| **Right to information** | Transparency about processing; access to own data | Art. 12-15 | Art. 8(2) EU Charter |
| **Right to not be subject to automated decisions** | Human involvement in significant decisions; right to explanation | Art. 22 | Art. 8, 47 EU Charter |
| **Right to physical safety** | Protection from physical harm resulting from data processing | Art. 32 | Art. 3 EU Charter |

### Mapping Guidance

When adding a risk to the register, select the **primary** rights category affected:

| If the risk involves... | Primary category |
|------------------------|-----------------|
| Unauthorized access to personal data | right-to-privacy |
| Biased algorithmic decisions | non-discrimination |
| Surveillance or monitoring chilling effects | freedom-of-expression |
| Lack of transparency about processing | right-to-information |
| Automated decisions without human review | right-to-not-be-subject-to-automated-decisions |
| Safety implications of data misuse | right-to-physical-safety |

---

## Risk Level Thresholds

Risk Score = Likelihood x Severity. Thresholds follow the standard 5x5 matrix.

| Score Range | Level | Color | Action Required |
|-------------|-------|-------|-----------------|
| 1-4 | Low | Green | Accept residual risk. Document in DPIA. No further mitigation required. |
| 5-9 | Medium | Yellow | Consider additional mitigations. Document rationale if accepting. Monitor. |
| 10-15 | High | Orange | Additional mitigations required before processing. DPO consultation mandatory. |
| 16-25 | Very High | Red | Processing cannot proceed. Art. 36 prior consultation with SA required. Fundamental redesign or additional safeguards mandatory. |

### Risk Level Decision Table

| Likelihood \ Severity | 1 (Negligible) | 2 (Limited) | 3 (Significant) | 4 (Maximum) | 5 (Critical) |
|----------------------|-----------------|-------------|------------------|-------------|---------------|
| **5 (Almost certain)** | 5 Medium | 10 High | 15 High | 20 Very High | 25 Very High |
| **4 (Maximum)** | 4 Low | 8 Medium | 12 High | 16 Very High | 20 Very High |
| **3 (Significant)** | 3 Low | 6 Medium | 9 Medium | 12 High | 15 High |
| **2 (Limited)** | 2 Low | 4 Low | 6 Medium | 8 Medium | 10 High |
| **1 (Negligible)** | 1 Low | 2 Low | 3 Low | 4 Low | 5 Medium |

---

## Mitigation Effectiveness Scoring

When applying a mitigation, assess its effectiveness in reducing likelihood and severity.

### Likelihood Reduction

| Reduction | Effectiveness | Examples |
|-----------|--------------|---------|
| 0 | No effect on likelihood | Mitigation addresses severity only (e.g., insurance) |
| 1 | Minor reduction | Basic access controls; awareness training; policy documentation |
| 2 | Moderate reduction | Role-based access control; encryption at rest; regular audits |
| 3 | Significant reduction | Multi-factor authentication; zero-trust architecture; automated monitoring |
| 4 | Major reduction | End-to-end encryption; complete data anonymization; processing redesign |

### Severity Reduction

| Reduction | Effectiveness | Examples |
|-----------|--------------|---------|
| 0 | No effect on severity | Mitigation addresses likelihood only (e.g., stronger authentication) |
| 1 | Minor reduction | Incident response plan; data subject notification procedures; pseudonymization |
| 2 | Moderate reduction | Data minimization; purpose limitation enforcement; retention limits |
| 3 | Significant reduction | Pseudonymization with separated key management; human oversight for automated decisions |
| 4 | Major reduction | Full anonymization; processing scope reduction; data subject opt-out mechanisms |

### Mitigation Type Reference

| Mitigation Type | Typical L Reduction | Typical S Reduction | Notes |
|----------------|--------------------|--------------------|-------|
| Encryption (at rest) | 1-2 | 1 | Reduces unauthorized access likelihood; limits breach severity |
| Encryption (in transit) | 1-2 | 0-1 | Protects data in motion |
| Pseudonymization | 1 | 1-2 | Reduces re-identification risk; not anonymization |
| Access control (RBAC) | 2 | 0 | Limits who can access data |
| Data minimization | 0-1 | 2-3 | Reduces data available if breach occurs |
| Retention limits | 0 | 1-2 | Limits data available over time |
| Human oversight | 0-1 | 2-3 | For automated decisions; reduces harm from errors |
| Consent management | 1 | 1 | Ensures lawful processing; enables data subject control |
| Audit logging | 1 | 0-1 | Deters misuse; enables detection and response |
| Incident response plan | 0 | 1-2 | Reduces impact through rapid response |
| Data subject notification | 0 | 1 | Enables subjects to take protective action |
| Anonymization | 3-4 | 3-4 | Removes personal data status entirely |
| Differential privacy | 2-3 | 2-3 | Statistical privacy guarantees for aggregate queries |
| Bias testing/auditing | 0-1 | 2-3 | For AI systems; reduces discriminatory outcomes |
| Transparency measures | 0 | 1-2 | Privacy notices, algorithmic explanations |

---

## Residual Risk Calculation

Residual risk is calculated after applying all mitigations to a risk.

### Formula

```
Residual Likelihood = max(1, Original Likelihood - Sum of Likelihood Reductions)
Residual Severity   = max(1, Original Severity - Sum of Severity Reductions)
Residual Score      = Residual Likelihood x Residual Severity
Residual Level      = Level corresponding to Residual Score
```

### Rules

- Residual likelihood and severity cannot go below 1 (risk is never zero)
- Multiple mitigations are cumulative in their reductions
- Mitigations with overlapping mechanisms should not be double-counted
- Residual risk must be documented even if Low
- If residual risk remains Very High after all feasible mitigations, Art. 36 consultation is mandatory

### Example

| Step | Likelihood | Severity | Score | Level |
|------|-----------|----------|-------|-------|
| Original risk | 4 | 4 | 16 | Very High |
| After mitigation 1 (RBAC, L-2, S-0) | 2 | 4 | 8 | Medium |
| After mitigation 2 (data minimization, L-0, S-2) | 2 | 2 | 4 | Low |

---

## Art. 36 Consultation Triggers

### When Prior Consultation is Required

Art. 36(1): The controller shall prior to processing consult the supervisory authority where the DPIA under Art. 35 indicates that the processing would result in a high risk **in the absence of measures taken by the controller to mitigate the risk**.

In practice, this means:

| Residual Risk Level | Art. 36 Obligation |
|--------------------|--------------------|
| Low | No consultation required |
| Medium | No consultation required |
| High | Consultation not strictly required; voluntary consultation recommended |
| Very High | **Prior consultation MANDATORY** |

### Consultation Process

| Step | Requirement | Timeline |
|------|-------------|----------|
| 1 | Submit DPIA to supervisory authority | Before processing begins |
| 2 | Include: purposes, means, safeguards, DPO contact, DPIA results | With submission |
| 3 | SA acknowledges receipt | Varies by SA |
| 4 | SA provides written advice | Within 8 weeks (Art. 36(2)) |
| 5 | SA may extend for complex cases | Additional 6 weeks with notice |
| 6 | Controller must follow SA advice | Before processing begins |

### Borderline Cases

For residual risks near the High/Very High boundary (scores 14-16):

- **Score 14-15 (High):** Formal Art. 36 not required, but voluntary consultation demonstrates accountability. Document the borderline assessment.
- **Score 16 (Very High):** Art. 36 consultation is mandatory. Even if the controller considers the risk adequately mitigated, the score threshold triggers the obligation.

---

## Risk Catalog

20+ common DPIA risks organized by type with typical severity and likelihood ranges.

### Unauthorized Access / Confidentiality

| Risk | Typical L | Typical S | Primary Rights Category |
|------|----------|----------|------------------------|
| External attacker gains access to personal data | 2-4 | 3-5 | right-to-privacy |
| Insider threat — employee accesses data without authorization | 2-3 | 2-4 | right-to-privacy |
| Third-party processor breach | 2-3 | 3-4 | right-to-privacy |
| Cloud storage misconfiguration exposes data | 2-4 | 3-5 | right-to-privacy |
| Unencrypted data intercepted in transit | 1-3 | 2-4 | right-to-privacy |

### Excessive Collection / Purpose Limitation

| Risk | Typical L | Typical S | Primary Rights Category |
|------|----------|----------|------------------------|
| Data collected beyond stated purpose | 2-4 | 2-3 | right-to-privacy |
| Function creep — data used for new undisclosed purpose | 3-4 | 2-4 | right-to-information |
| Excessive data collection relative to stated purpose | 2-3 | 2-3 | right-to-privacy |
| Inadequate privacy notice — data subjects uninformed | 3-4 | 2-3 | right-to-information |

### Retention / Deletion

| Risk | Typical L | Typical S | Primary Rights Category |
|------|----------|----------|------------------------|
| Data retained beyond necessary period | 3-4 | 2-3 | right-to-privacy |
| Inability to delete data upon request (Art. 17) | 2-3 | 2-4 | right-to-privacy |
| Backup retention prevents complete erasure | 3-4 | 1-3 | right-to-privacy |
| Lack of automated retention enforcement | 3-4 | 2-3 | right-to-privacy |

### Cross-Border Transfer

| Risk | Typical L | Typical S | Primary Rights Category |
|------|----------|----------|------------------------|
| Transfer to inadequate country without safeguards | 2-3 | 3-4 | right-to-privacy |
| Standard Contractual Clauses not implemented | 2-3 | 3-4 | right-to-privacy |
| Transfer Impact Assessment not conducted | 3-4 | 2-3 | right-to-privacy |

### Automated Decision-Making / Profiling

| Risk | Typical L | Typical S | Primary Rights Category |
|------|----------|----------|------------------------|
| Automated decisions without human review option | 2-4 | 3-5 | right-to-not-be-subject-to-automated-decisions |
| Algorithmic bias producing discriminatory outcomes | 2-4 | 3-5 | non-discrimination |
| Lack of transparency in automated logic | 3-4 | 2-4 | right-to-information |
| Inaccurate profiling leading to unfair treatment | 2-4 | 3-5 | non-discrimination |
| No mechanism to contest automated decisions | 2-3 | 3-4 | right-to-not-be-subject-to-automated-decisions |

### Surveillance / Monitoring

| Risk | Typical L | Typical S | Primary Rights Category |
|------|----------|----------|------------------------|
| Chilling effect on behavior from monitoring awareness | 3-5 | 2-4 | freedom-of-expression |
| Disproportionate employee monitoring | 3-4 | 2-4 | right-to-privacy |
| Location tracking beyond necessary scope | 2-4 | 2-4 | right-to-privacy |
| Biometric data collection without adequate safeguards | 2-3 | 4-5 | right-to-privacy |

### Safety

| Risk | Typical L | Typical S | Primary Rights Category |
|------|----------|----------|------------------------|
| Data breach enables physical stalking or harassment | 1-2 | 4-5 | right-to-physical-safety |
| AI system makes safety-critical decision based on inaccurate data | 1-3 | 4-5 | right-to-physical-safety |
| Medical data inaccuracy leads to treatment error | 1-2 | 4-5 | right-to-physical-safety |
