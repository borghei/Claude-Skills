# AI Lifecycle Management Guide

Comprehensive guidance for managing AI systems through all lifecycle stages per ISO 42001:2023 Clause 8 and Annex A.6. Covers design, development, testing, deployment, monitoring, retirement, data management, and model versioning.

---

## Table of Contents

- [Lifecycle Overview](#lifecycle-overview)
- [Stage 1: Design](#stage-1-design)
- [Stage 2: Development](#stage-2-development)
- [Stage 3: Testing and Validation](#stage-3-testing-and-validation)
- [Stage 4: Deployment](#stage-4-deployment)
- [Stage 5: Monitoring and Maintenance](#stage-5-monitoring-and-maintenance)
- [Stage 6: Retirement and Decommissioning](#stage-6-retirement-and-decommissioning)
- [Data Management Across Lifecycle](#data-management-across-lifecycle)
- [Model Versioning and Change Management](#model-versioning-and-change-management)

---

## Lifecycle Overview

```
┌──────────┐    ┌─────────────┐    ┌──────────┐    ┌────────────┐
│  DESIGN  │───>│ DEVELOPMENT │───>│ TESTING  │───>│ DEPLOYMENT │
└──────────┘    └─────────────┘    └──────────┘    └────────────┘
     ^                                                    │
     │                                                    v
     │          ┌──────────────┐    ┌────────────────────────────┐
     └──────────│  RETIREMENT  │<───│ MONITORING & MAINTENANCE   │
                └──────────────┘    └────────────────────────────┘
```

**Gate Reviews:** Each transition between stages requires a formal gate review to verify readiness, address risks, and approve progression.

| Gate | From → To | Key Criteria |
|------|-----------|-------------|
| G1 | Design → Development | Requirements approved, ethical review passed, impact assessment completed |
| G2 | Development → Testing | Model meets baseline performance, code reviewed, data documented |
| G3 | Testing → Deployment | All test criteria met, bias assessment passed, security validated |
| G4 | Deployment → Operation | Monitoring configured, rollback tested, stakeholders notified |
| G5 | Operation → Retirement | Retirement plan approved, data disposal planned, users notified |

---

## Stage 1: Design

### Requirements Definition

**Functional Requirements:**
- Problem statement and business objective
- Input data specification (types, sources, formats)
- Output specification (predictions, classifications, recommendations)
- Performance requirements (accuracy, latency, throughput)
- Scalability and availability requirements

**Responsible AI Requirements:**
- Fairness criteria and protected attribute handling
- Transparency and explainability requirements
- Safety and reliability requirements
- Privacy and data protection requirements
- Security requirements
- Human oversight requirements
- Regulatory compliance requirements (EU AI Act, sector-specific)

### Architecture Design

**Design Decisions to Document:**
- Model architecture selection rationale
- Training approach (supervised, unsupervised, reinforcement, fine-tuning)
- Feature engineering strategy
- Data pipeline architecture
- Inference pipeline design
- Integration architecture (APIs, batch, real-time)
- Failover and fallback design
- Human-in-the-loop integration points

### Ethical Review

Before proceeding to development:
- Conduct ethical review with diverse stakeholders
- Assess potential for discrimination or bias
- Evaluate societal impact (positive and negative)
- Consider dual-use risks
- Document ethical review findings and mitigations
- Obtain ethics board approval for high-risk applications

### Impact Assessment

Per ISO 42001 Annex A.5:
- Assess impact on all identified interested parties
- Evaluate fairness, transparency, safety, privacy, security dimensions
- Map impacts to risk levels
- Define risk treatment measures
- Document residual risk and acceptance rationale

**Gate G1 Checklist:**
- [ ] Requirements documented and approved
- [ ] Architecture design documented
- [ ] Ethical review completed
- [ ] Impact assessment completed
- [ ] Resource requirements identified
- [ ] Development plan approved
- [ ] Risks identified and treatment planned

---

## Stage 2: Development

### Data Preparation

**Data Collection:**
- Document data sources with provenance
- Verify legal basis for data collection and use
- Assess data representativeness for target population
- Document consent/authorization for personal data
- Establish data labeling guidelines and quality criteria

**Data Quality Assessment:**

| Quality Dimension | Assessment Method | Minimum Threshold |
|------------------|-------------------|-------------------|
| Completeness | Missing value analysis | Define per feature |
| Accuracy | Cross-reference with ground truth | > 95% |
| Consistency | Cross-source validation | No contradictions |
| Timeliness | Data freshness analysis | Within defined window |
| Uniqueness | Deduplication analysis | < 1% duplicates |
| Representativeness | Demographic distribution analysis | Proportional to target |

**Bias Assessment in Data:**
- Analyze demographic distribution in training data
- Identify underrepresented groups
- Check for historical bias in labels
- Assess proxy variables for protected attributes
- Document mitigation steps taken (resampling, reweighting, augmentation)

### Model Training

**Development Standards:**
- Use version control for all code, configurations, and data references
- Follow coding standards appropriate to the ML framework
- Document hyperparameter selection rationale
- Implement reproducibility measures (random seeds, environment pinning)
- Conduct code reviews for ML pipeline code
- Separate training, validation, and test datasets (no data leakage)

**Training Documentation:**
- Training data description (size, composition, preprocessing)
- Model architecture and configuration
- Hyperparameter search strategy and results
- Training process (epochs, convergence, compute used)
- Validation results during training
- Known limitations discovered during training

### Code Review for AI

In addition to standard code review:
- Verify data preprocessing does not introduce bias
- Check for data leakage between train/test splits
- Validate feature engineering logic
- Review model serialization and loading
- Verify reproducibility settings
- Check for hardcoded assumptions or thresholds

**Gate G2 Checklist:**
- [ ] Training data documented with provenance
- [ ] Data quality assessment completed
- [ ] Bias assessment conducted on data
- [ ] Model trained and validated
- [ ] Code reviewed
- [ ] Baseline performance metrics met
- [ ] Development artifacts versioned

---

## Stage 3: Testing and Validation

### Functional Testing

| Test Type | Purpose | Criteria |
|-----------|---------|----------|
| Unit tests | Component-level correctness | All pass |
| Integration tests | Pipeline end-to-end correctness | All pass |
| Performance tests | Accuracy, precision, recall on test set | Meet thresholds |
| Latency tests | Response time under load | Within SLA |
| Scalability tests | Behavior under increasing load | Linear scaling |
| Edge case tests | Handling of unusual inputs | Graceful handling |
| Input validation | Rejection of malformed inputs | No unhandled errors |

### Bias and Fairness Testing

**Required Metrics:**

| Metric | Description | Threshold |
|--------|-------------|-----------|
| Demographic parity | Equal positive rates across groups | Ratio > 0.8 |
| Equalized odds | Equal TPR and FPR across groups | Difference < 0.1 |
| Disparate impact | Four-fifths rule compliance | Ratio > 0.8 |
| Calibration | Predicted probabilities match outcomes per group | Within 0.05 |
| Counterfactual fairness | Same prediction if protected attribute changed | Match rate > 95% |

**Testing Approach:**
1. Define protected attributes and demographic groups
2. Create test datasets stratified by protected attributes
3. Measure all fairness metrics per group pair
4. Document any disparities and root cause analysis
5. Apply mitigation if thresholds are not met
6. Retest after mitigation

### Robustness Testing

- **Adversarial testing**: Test with adversarial examples (perturbed inputs)
- **Out-of-distribution**: Test with data outside training distribution
- **Noise tolerance**: Test with noisy or corrupted inputs
- **Missing data**: Test with missing features
- **Temporal robustness**: Test with data from different time periods
- **Stress testing**: Test under resource constraints (CPU, memory, network)

### Security Testing

- **Model extraction**: Assess vulnerability to model stealing attacks
- **Data poisoning**: Validate training pipeline integrity
- **Prompt injection**: Test for prompt injection vulnerabilities (LLMs)
- **API security**: Standard API security testing (authentication, authorization, rate limiting)
- **Input sanitization**: Validate input validation effectiveness
- **Output filtering**: Verify output filtering for harmful content

### Validation by Independent Party

For high-risk AI systems:
- Validation by team independent from development
- Use held-out validation dataset not seen during development
- Validate against original requirements and responsible AI criteria
- Document validation results and any residual concerns
- Obtain sign-off from independent validator

**Gate G3 Checklist:**
- [ ] All functional tests passed
- [ ] Bias and fairness testing completed — thresholds met
- [ ] Robustness testing passed
- [ ] Security testing completed — no critical vulnerabilities
- [ ] Independent validation completed (if required)
- [ ] Test results documented and reviewed
- [ ] Deployment plan approved

---

## Stage 4: Deployment

### Pre-Deployment

**Deployment Plan Must Include:**
- Deployment environment and infrastructure
- Deployment approach (canary, blue-green, rolling, big-bang)
- Rollback procedure and triggers
- Monitoring and alerting configuration
- Stakeholder notification plan
- Go/no-go criteria and decision authority

### Canary and Staged Deployment

**Recommended Approach:**
1. **Shadow mode**: Run new model alongside existing system, compare outputs
2. **Canary (1-5%)**: Route small percentage of traffic to new model
3. **Gradual rollout (5-25-50-100%)**: Increase traffic incrementally
4. **Full deployment**: Route all traffic after validation at each stage

**At each stage, monitor:**
- Model performance metrics vs. baseline
- Fairness metrics vs. baseline
- Error rates and failure modes
- Latency and resource utilization
- User feedback and complaints
- Business metrics impact

### Approval Gates

**Who must approve deployment:**
- AI system owner
- Technical lead
- Risk/compliance representative
- Ethics reviewer (for high-risk systems)
- Business stakeholder

**Approval documentation:**
- Test results summary
- Risk assessment status
- Compliance verification
- Deployment plan
- Rollback plan

### Post-Deployment Verification

Within first 24-72 hours:
- Verify monitoring and alerting is operational
- Confirm model performance matches testing results
- Check fairness metrics in production
- Verify logging and audit trail capture
- Confirm rollback capability is functional
- Validate user-facing transparency mechanisms

**Gate G4 Checklist:**
- [ ] Deployment plan executed
- [ ] Monitoring and alerting confirmed operational
- [ ] Production performance verified against test results
- [ ] Rollback tested and confirmed functional
- [ ] Stakeholders notified
- [ ] Post-deployment verification completed

---

## Stage 5: Monitoring and Maintenance

### Continuous Monitoring

**Performance Monitoring:**
- Model accuracy, precision, recall (vs. baseline and threshold)
- Prediction distribution (detect distribution shifts)
- Response latency (P50, P95, P99)
- Throughput and error rates
- Resource utilization (CPU, GPU, memory)

**Drift Detection:**

| Drift Type | Detection Method | Action Threshold |
|-----------|-----------------|-----------------|
| Data drift | Population Stability Index (PSI) | PSI > 0.2 |
| Feature drift | KS test per feature | p-value < 0.05 |
| Concept drift | Performance degradation over time | Accuracy drop > 5% |
| Prediction drift | Output distribution shift | PSI > 0.1 |
| Label drift | Ground truth label distribution change | Chi-squared test |

**Fairness Monitoring:**
- Continuous tracking of fairness metrics per demographic group
- Alert when fairness metrics cross thresholds
- Quarterly comprehensive fairness review

**Incident Detection:**
- Anomaly detection on model outputs
- User complaint/feedback monitoring
- Automated alerting for performance degradation
- Security event monitoring

### Maintenance Activities

**Routine Maintenance:**
- Weekly: Review monitoring dashboards and alerts
- Monthly: Performance report and trend analysis
- Quarterly: Comprehensive fairness and drift review
- Annually: Full model revalidation and impact reassessment

**Retraining Triggers:**
- Significant data drift detected (PSI > 0.25)
- Performance below acceptable threshold
- Concept drift confirmed by ground truth analysis
- New data sources or features available
- Regulatory or business requirement changes
- Bias detected in production fairness monitoring

**Retraining Process:**
1. Identify need for retraining (trigger event)
2. Prepare updated training data with quality and bias checks
3. Retrain model following development standards
4. Conduct full testing suite (functional, fairness, robustness, security)
5. Validate against production performance
6. Deploy via staged deployment process
7. Monitor post-retraining performance

### Incident Response

**Severity Levels:**

| Level | Description | Response Time | Example |
|-------|-------------|--------------|---------|
| P1 - Critical | AI system causing active harm | < 1 hour | Discriminatory decisions affecting individuals |
| P2 - High | Significant performance degradation | < 4 hours | Model accuracy dropped below minimum threshold |
| P3 - Medium | Non-critical issue affecting quality | < 24 hours | Drift detected but within tolerance |
| P4 - Low | Minor issue, no immediate impact | < 1 week | Documentation gap identified |

**Response Procedure:**
1. **Detect**: Alert triggered or report received
2. **Triage**: Classify severity, assign owner
3. **Contain**: Disable system, rollback, or enable human override
4. **Investigate**: Root cause analysis
5. **Resolve**: Fix and verify
6. **Communicate**: Notify affected parties
7. **Learn**: Document lessons learned, update controls

---

## Stage 6: Retirement and Decommissioning

### Retirement Triggers

- Model superseded by improved version
- Business use case no longer relevant
- Regulatory changes making system non-compliant
- Unacceptable risk that cannot be mitigated
- Cost-benefit analysis no longer favorable
- Technology obsolescence

### Retirement Planning

**Retirement Plan Must Include:**
- Retirement timeline and milestones
- Stakeholder notification plan
- Data disposition plan (archive, delete, anonymize)
- Model artifact archival plan
- Documentation preservation
- Service migration plan (for dependent systems)
- User communication and transition support
- Compliance obligations during and after retirement

### Data Disposition

| Data Type | Disposition Options | Considerations |
|-----------|-------------------|----------------|
| Training data | Archive or delete per retention policy | Legal holds, regulatory requirements |
| Personal data | Delete per privacy law requirements | GDPR Art. 17, CCPA §1798.105 |
| Model artifacts | Archive for audit trail | Retain for regulatory inquiry period |
| Evaluation data | Archive for reproducibility | Anonymize if containing personal data |
| Monitoring logs | Retain per log retention policy | Legal and compliance requirements |
| Configuration | Archive for reference | May be needed for incident investigation |

### Stakeholder Notification

Notify the following parties before retirement:
- End users and affected individuals
- Business stakeholders and system owners
- Downstream system owners (API consumers)
- Regulatory bodies (if required)
- Third-party providers and suppliers
- Internal teams (development, operations, support)

**Notification Timeline:**
- 90 days: Initial notification of planned retirement
- 30 days: Reminder with migration guidance
- 7 days: Final notification
- Day 0: System retired, redirect/deprecation notice active

**Gate G5 Checklist:**
- [ ] Retirement plan approved
- [ ] Stakeholders notified (90/30/7 day)
- [ ] Data disposition executed per plan
- [ ] Model artifacts archived
- [ ] Documentation preserved
- [ ] Dependent systems migrated
- [ ] Retirement verified and confirmed

---

## Data Management Across Lifecycle

### Data Governance Framework

**Principles:**
- **Quality**: Data must meet defined quality standards before use in AI
- **Provenance**: Data origin and transformation history must be traceable
- **Protection**: Personal and sensitive data must be protected throughout lifecycle
- **Minimization**: Only data necessary for the purpose should be collected and retained
- **Fairness**: Data must be assessed for bias and representativeness
- **Retention**: Data must be retained only as long as necessary

### Data Quality Management

**Quality Dimensions:**

| Dimension | Definition | Assessment Frequency |
|-----------|-----------|---------------------|
| Accuracy | Data correctly represents real-world entity | Before each training cycle |
| Completeness | All required data present | Continuous monitoring |
| Consistency | No contradictions across sources | Before each training cycle |
| Timeliness | Data sufficiently current | Continuous monitoring |
| Validity | Data conforms to defined rules/formats | Continuous validation |
| Uniqueness | No unnecessary duplicates | Before each training cycle |

### Data Provenance and Lineage

Document for all data used in AI systems:
- **Origin**: Where did the data come from?
- **Collection method**: How was it collected?
- **Legal basis**: What authorizes its use?
- **Transformations**: What preprocessing was applied?
- **Versioning**: Which version of the data was used?
- **Quality scores**: What were the quality assessment results?
- **Bias assessment**: What bias checks were performed?

### Data Bias Assessment

**Assessment Steps:**
1. Define protected attributes and demographic groups
2. Analyze representation in training data vs. target population
3. Check for historical bias in labels or outcomes
4. Identify proxy variables for protected attributes
5. Test for measurement bias (different accuracy across groups)
6. Document findings and mitigation strategies
7. Repeat assessment when data is updated

**Bias Mitigation Techniques:**

| Technique | Stage | Approach |
|-----------|-------|---------|
| Resampling | Pre-processing | Oversample minority, undersample majority |
| Reweighting | Pre-processing | Assign higher weights to underrepresented samples |
| Data augmentation | Pre-processing | Generate synthetic data for underrepresented groups |
| Adversarial debiasing | In-processing | Train adversarial network to remove bias signals |
| Calibration | Post-processing | Adjust predictions to equalize across groups |
| Threshold adjustment | Post-processing | Set group-specific decision thresholds |

---

## Model Versioning and Change Management

### Version Control Requirements

**What to Version:**
- Source code (ML pipeline, preprocessing, inference)
- Model artifacts (trained weights, architecture files)
- Training data references (dataset version, not data copies)
- Configuration files (hyperparameters, feature definitions)
- Test datasets and evaluation scripts
- Documentation (model card, impact assessment)

### Versioning Scheme

**Recommended: Semantic Versioning for Models**

```
MAJOR.MINOR.PATCH

MAJOR: Architecture change, new training data source, significant behavior change
MINOR: Hyperparameter tuning, incremental retraining, feature addition
PATCH: Bug fix, configuration update, documentation update
```

**Example:**
- v1.0.0: Initial production deployment
- v1.1.0: Retraining with updated data
- v1.1.1: Fixed preprocessing bug
- v2.0.0: New model architecture

### Change Management Process

**Change Types:**

| Change Type | Approval Required | Testing Required |
|-------------|------------------|-----------------|
| Emergency (P1 fix) | AIMS manager + system owner | Abbreviated test suite |
| Standard (planned) | Change board approval | Full test suite |
| Minor (config/docs) | System owner | Relevant tests only |

**Change Request Process:**
1. Submit change request with rationale and impact analysis
2. Assess impact on fairness, safety, privacy, security
3. Review by appropriate authority (see table above)
4. Implement change in development environment
5. Execute required testing
6. Deploy via staged deployment process
7. Verify change in production
8. Update documentation and version records

### Model Registry

Maintain a central model registry containing:
- Model ID and version
- Architecture and framework
- Training data version reference
- Performance metrics (training, validation, production)
- Fairness metrics
- Owner and team
- Deployment status (development, staging, production, retired)
- Risk classification
- Dependencies (libraries, infrastructure)
- Approval records
- Known limitations and constraints

### Rollback Procedures

**When to Roll Back:**
- Performance degradation exceeding threshold
- Fairness violation detected
- Security vulnerability discovered
- Unexpected behavior in production
- Business impact exceeding risk appetite

**Rollback Process:**
1. Decision to rollback (system owner or on-call authority)
2. Redirect traffic to previous model version
3. Verify previous version is serving correctly
4. Disable new version deployment
5. Notify stakeholders of rollback
6. Investigate root cause
7. Plan corrective action before re-deployment
8. Document rollback decision and rationale
