---
name: iso42001-ai-management
description: ISO 42001 AI Management System compliance automation. Assesses organizational readiness for AIMS certification, evaluates AI system impacts, validates governance structures, and checks Annex A controls. Use for ISO 42001 readiness assessments, AI governance planning, AI impact assessments, responsible AI implementation, and AIMS certification preparation.
triggers:
  - ISO 42001
  - AI management system
  - AIMS
  - responsible AI
  - AI governance ISO
  - AI risk management
  - AI management certification
  - trustworthy AI
  - AI quality management
---

# ISO 42001 AI Management System

Tools and guidance for ISO/IEC 42001:2023 — the first international standard for AI Management Systems (AIMS).

---

## Table of Contents

- [Tools](#tools)
  - [AIMS Readiness Checker](#aims-readiness-checker)
  - [AI Impact Assessor](#ai-impact-assessor)
- [Reference Guides](#reference-guides)
- [Workflows](#workflows)
- [Standard Overview](#standard-overview)

---

## Tools

### AIMS Readiness Checker

Assesses organizational readiness against all ISO 42001 clauses and Annex A controls. Scores each clause on a 0-100 scale and identifies gaps for certification preparation.

```bash
# Assess readiness from a JSON profile
python scripts/aims_readiness_checker.py --input org_profile.json

# Generate a blank input template
python scripts/aims_readiness_checker.py --template > org_profile.json

# JSON output for automation
python scripts/aims_readiness_checker.py --input org_profile.json --json

# Export report to file
python scripts/aims_readiness_checker.py --input org_profile.json --output report.json
```

**Assessment Areas:**

| Clause | Area | Key Checks |
|--------|------|-----------|
| Clause 4 | Context | Scope defined, interested parties, AIMS boundaries |
| Clause 5 | Leadership | AI policy, governance structure, management commitment |
| Clause 6 | Planning | Risk assessment methodology, AI objectives, impact assessments |
| Clause 7 | Support | Resources, competence, awareness, documentation |
| Clause 8 | Operation | AI lifecycle, data management, risk treatment, third-party controls |
| Clause 9 | Performance | Monitoring, internal audit, management review |
| Clause 10 | Improvement | Corrective actions, continual improvement, incident management |
| Annex A | Controls | A.2-A.10 control implementation status |

**Output:**
- Overall readiness score (0-100)
- Per-clause scores with maturity level (Initial/Developing/Defined/Managed/Optimized)
- Annex A control implementation status (Implemented/Partial/Not Implemented/Not Applicable)
- Gap analysis with prioritized recommendations
- Certification readiness assessment (Ready/Near Ready/Significant Gaps)

---

### AI Impact Assessor

Generates comprehensive AI impact assessments evaluating fairness, transparency, safety, privacy, and security dimensions. Maps impacts to interested parties and provides risk treatment recommendations.

```bash
# Assess an AI system from a JSON description
python scripts/ai_impact_assessor.py --input ai_system.json

# Generate a blank input template
python scripts/ai_impact_assessor.py --template > ai_system.json

# Export assessment report
python scripts/ai_impact_assessor.py --input ai_system.json --output assessment.json

# Generate markdown report
python scripts/ai_impact_assessor.py --input ai_system.json --format markdown --output assessment.md
```

**Assessment Dimensions:**

| Dimension | Evaluates | Key Factors |
|-----------|----------|-------------|
| Fairness | Bias, discrimination, equity | Training data diversity, protected attributes, outcome parity |
| Transparency | Explainability, interpretability | Model complexity, decision documentation, user disclosure |
| Safety | Reliability, robustness, harm prevention | Failure modes, edge cases, human oversight, fallback mechanisms |
| Privacy | Data protection, consent, minimization | PI processing, consent mechanisms, data retention, anonymization |
| Security | Adversarial resilience, access control | Attack vectors, model integrity, access management, audit logging |
| Accountability | Governance, responsibility, auditability | Decision ownership, audit trails, escalation procedures |

**Features:**
- Risk scoring per dimension (Low/Medium/High/Critical)
- Interested party impact mapping (users, affected individuals, society, regulators)
- Risk treatment options (Avoid, Mitigate, Transfer, Accept)
- Regulatory mapping (EU AI Act risk tier, ISO 42001 Annex A controls)
- Residual risk calculation after treatment
- Markdown and JSON report generation

---

## Reference Guides

### ISO 42001 Clause Guide
`references/iso42001-clause-guide.md`

Comprehensive clause-by-clause guidance:
- All clauses (4-10) with requirements and implementation steps
- Annex A controls (A.2-A.10) detailed with evidence requirements
- Audit questions per clause for internal audit preparation
- Common nonconformity findings and how to avoid them
- Required documented information per clause
- Cross-references to ISO 27001, ISO 9001, and EU AI Act

### AI Lifecycle Management
`references/ai-lifecycle-management.md`

End-to-end AI system lifecycle guidance:
- Lifecycle stages: design, development, testing, deployment, monitoring, retirement
- Design and development controls (requirements, architecture, coding standards)
- Testing and validation requirements (functional, bias, robustness, performance)
- Deployment procedures (staging, canary, rollback, approval gates)
- Monitoring and maintenance (drift detection, performance degradation, retraining)
- Retirement and decommissioning (data disposal, model archival, stakeholder notification)
- Data management across lifecycle (quality, provenance, bias assessment, lineage)
- Model versioning and change management (version control, change impact, approval workflows)

---

## Workflows

### Workflow 1: ISO 42001 Readiness Assessment

```
Step 1: Define AIMS scope
        → Identify AI systems in scope
        → Determine organizational boundaries
        → Document interested parties and requirements

Step 2: Generate assessment template
        → python scripts/aims_readiness_checker.py --template > org_profile.json
        → Fill in organizational details and current state

Step 3: Run readiness assessment
        → python scripts/aims_readiness_checker.py --input org_profile.json

Step 4: Review results
        → Address critical gaps (Clauses 5, 6, 8 typically weakest)
        → Prioritize Annex A controls by risk
        → Develop remediation roadmap

Step 5: Conduct AI impact assessments
        → python scripts/ai_impact_assessor.py --template > ai_system.json
        → Assess each in-scope AI system
        → python scripts/ai_impact_assessor.py --input ai_system.json

Step 6: Plan implementation
        → See references/iso42001-clause-guide.md for requirements
        → See references/ai-lifecycle-management.md for operational controls
```

### Workflow 2: AI System Impact Assessment

```
Step 1: Identify AI system for assessment
        → Document system purpose, inputs, outputs, and decisions
        → Identify affected individuals and groups

Step 2: Generate assessment template
        → python scripts/ai_impact_assessor.py --template > ai_system.json
        → Complete all sections (model details, data sources, deployment context)

Step 3: Conduct assessment
        → python scripts/ai_impact_assessor.py --input ai_system.json --format markdown --output report.md

Step 4: Review dimension scores
        → Fairness: check for bias in training data and outcomes
        → Transparency: verify explainability mechanisms
        → Safety: validate failure modes and human oversight
        → Privacy: confirm data protection measures
        → Security: assess adversarial resilience

Step 5: Implement risk treatments
        → Apply recommended mitigations per dimension
        → Document residual risk acceptance decisions
        → Assign treatment owners and timelines

Step 6: Monitor and review
        → Schedule periodic reassessment (quarterly minimum)
        → Track treatment implementation progress
        → Update assessment when system changes materially
```

### Workflow 3: AIMS Certification Preparation

```
Step 1: Gap analysis
        → python scripts/aims_readiness_checker.py --input org_profile.json
        → Target overall score of 80+ for certification readiness

Step 2: Document AIMS
        → AI policy (Clause 5.2)
        → AIMS scope (Clause 4.3)
        → Risk assessment methodology (Clause 6.1)
        → Statement of Applicability for Annex A controls
        → AI objectives (Clause 6.2)

Step 3: Implement operational controls
        → AI lifecycle procedures (Clause 8)
        → Data management processes (Annex A.7)
        → Third-party management (Annex A.10)
        → Impact assessments for all AI systems (Annex A.5)

Step 4: Conduct internal audit
        → Use references/iso42001-clause-guide.md audit questions
        → Document findings and corrective actions
        → Verify closure of nonconformities

Step 5: Management review
        → Present AIMS performance to top management
        → Review AI objectives achievement
        → Obtain commitment for continual improvement

Step 6: Stage 1 and Stage 2 audits
        → Stage 1: Documentation review (readiness check)
        → Stage 2: Implementation effectiveness audit
        → Address any nonconformities from audit
```

---

## Standard Overview

### ISO 42001:2023 Overview

ISO/IEC 42001:2023 is the world's first international standard for **AI Management Systems (AIMS)**. Published in December 2023, it provides a framework for organizations to responsibly develop, provide, and use AI systems. The standard follows the ISO Harmonized Structure (Annex SL) for management system standards, enabling integration with ISO 27001, ISO 9001, and ISO 14001.

**Key Characteristics:**
- Certifiable management system standard
- Technology-neutral (applies to any AI approach)
- Risk-based approach to AI governance
- PDCA (Plan-Do-Check-Act) cycle
- Applicable to organizations of any size and sector

### AIMS Framework (Plan-Do-Check-Act)

#### Context of the Organization (Clause 4)

| Requirement | Section | Description |
|------------|---------|-------------|
| Organization context | 4.1 | Internal/external issues relevant to AI objectives |
| Interested parties | 4.2 | Stakeholders, their requirements, and expectations |
| AIMS scope | 4.3 | Boundaries and applicability of the AIMS |
| AIMS establishment | 4.4 | Establish, implement, maintain, and improve the AIMS |

#### Leadership (Clause 5)

| Requirement | Section | Description |
|------------|---------|-------------|
| Leadership commitment | 5.1 | Top management demonstrates commitment to AIMS |
| AI policy | 5.2 | Responsible AI principles, ethical guidelines, organizational values |
| Roles and responsibilities | 5.3 | Clear assignment of AIMS roles, authority, and accountability |

**AI Policy Must Include:**
- Commitment to responsible AI development and use
- Ethical principles guiding AI decisions
- Alignment with applicable legal and regulatory requirements
- Commitment to continual improvement of the AIMS
- Framework for setting AI objectives

**AI Governance Structure:**
- AI governance board or committee
- AI system owners with defined accountability
- Data stewards for AI data management
- Ethics review function
- Incident response roles

#### Planning (Clause 6)

| Requirement | Section | Description |
|------------|---------|-------------|
| Risks and opportunities | 6.1 | Actions to address AI-specific risks and opportunities |
| AI risk assessment | 6.1.2 | Methodology for identifying and evaluating AI risks |
| AI objectives | 6.2 | Measurable objectives for responsible AI |
| Impact assessment | 6.1.4 | Assessment of AI system impacts on individuals and society |

**AI Risk Assessment Must Cover:**
- Fairness and non-discrimination risks
- Transparency and explainability gaps
- Safety and reliability concerns
- Privacy and data protection risks
- Security vulnerabilities
- Accountability gaps
- Societal and environmental impacts

#### Support (Clause 7)

| Requirement | Section | Description |
|------------|---------|-------------|
| Resources | 7.1 | Compute, data, expertise, and infrastructure |
| Competence | 7.2 | Required skills for AI roles, training plans |
| Awareness | 7.3 | AI literacy across the organization |
| Communication | 7.4 | Internal/external communication on AI matters |
| Documented information | 7.5 | Document creation, control, and retention |

#### Operation (Clause 8)

| Requirement | Section | Description |
|------------|---------|-------------|
| Operational planning | 8.1 | Planning and controlling AI processes |
| AI risk assessment | 8.2 | Executing risk assessments per methodology |
| AI risk treatment | 8.3 | Implementing risk treatment plans |
| AI system lifecycle | 8.4 | Managing AI systems through all lifecycle stages |

**AI System Lifecycle Stages:**
1. **Design**: Requirements, architecture, ethical review
2. **Development**: Data preparation, model training, coding standards
3. **Testing**: Functional, bias, robustness, performance validation
4. **Deployment**: Staging, approval, monitoring setup
5. **Operation**: Performance monitoring, drift detection, incident response
6. **Retirement**: Decommissioning, data disposal, stakeholder notification

**Data Management for AI:**
- Data quality assessment and improvement
- Data provenance and lineage tracking
- Bias assessment in training and evaluation data
- Data governance and access controls
- Personal data protection measures
- Data retention and disposal procedures

**Third-Party and Supplier Management:**
- AI component supplier evaluation
- Third-party AI service agreements
- Supply chain risk assessment
- Ongoing supplier monitoring

#### Performance Evaluation (Clause 9)

| Requirement | Section | Description |
|------------|---------|-------------|
| Monitoring and measurement | 9.1 | AI system performance metrics and KPIs |
| Internal audit | 9.2 | Planned audits of the AIMS |
| Management review | 9.3 | Top management review of AIMS effectiveness |

**AI Performance Metrics:**
- Model accuracy, precision, recall
- Fairness metrics (demographic parity, equalized odds)
- Latency and availability
- Drift indicators (data drift, concept drift)
- Incident frequency and severity
- Consumer complaint rates

#### Improvement (Clause 10)

| Requirement | Section | Description |
|------------|---------|-------------|
| Nonconformity | 10.1 | Corrective actions for nonconformities |
| Continual improvement | 10.2 | Ongoing enhancement of the AIMS |
| AI incident management | 10.3 | Handling AI system incidents and near-misses |

### Annex A Controls

| Control | Title | Description |
|---------|-------|-------------|
| A.2 | AI Policies | Policies for responsible AI aligned with organizational objectives |
| A.3 | Internal Organization | Roles, responsibilities, segregation of duties for AI |
| A.4 | Resources for AI Systems | Compute, data, tools, and expertise management |
| A.5 | Assessing AI System Impact | Impact assessment processes for AI systems |
| A.6 | AI System Lifecycle | Controls across design, development, deployment, retirement |
| A.7 | Data for AI Systems | Data quality, provenance, bias, governance, protection |
| A.8 | Information for Interested Parties | Transparency, disclosure, and communication |
| A.9 | Use of AI Systems | Acceptable use policies, human oversight, user guidance |
| A.10 | Third-Party Relationships | Supplier management, outsourced AI, component evaluation |

### Annex B — Implementation Guidance

Annex B provides non-normative guidance for implementing Annex A controls:
- Practical examples for each control objective
- Scalability guidance for different organization sizes
- Sector-specific considerations
- Integration points with existing management systems

### Annex C — AI Risk Sources and Objectives

AI-specific risk sources organized by category:
- **Technical risks**: Model failure, data quality, adversarial attacks, drift
- **Ethical risks**: Bias, discrimination, lack of transparency, autonomy erosion
- **Legal risks**: Regulatory non-compliance, liability, intellectual property
- **Societal risks**: Job displacement, misinformation, environmental impact
- **Organizational risks**: Skill gaps, dependency, reputation damage

AI-specific control objectives:
- Ensure fairness and non-discrimination
- Maintain transparency and explainability
- Guarantee safety and reliability
- Protect privacy and data
- Secure AI systems against threats
- Enable accountability and governance

### Annex D — Use of AIMS Across Domains

Sector-specific considerations:
- **Healthcare**: Patient safety, clinical validation, regulatory approval (FDA, MDR)
- **Finance**: Algorithmic trading, credit scoring, anti-money laundering
- **Autonomous systems**: Safety-critical decisions, human override, fail-safe design
- **Human resources**: Hiring bias, employee monitoring, fairness
- **Public sector**: Citizen impact, democratic values, public trust

### Relationship to Other Standards

| Standard | Relationship | Integration Points |
|----------|-------------|-------------------|
| ISO 27001 | Information security | Risk assessment, access controls, incident management |
| ISO 9001 | Quality management | Process approach, document control, continual improvement |
| ISO 14001 | Environmental management | Impact assessment, lifecycle thinking |
| ISO 31000 | Risk management | Risk framework, assessment methodology |
| ISO 22989 | AI concepts/terminology | Foundational definitions |
| ISO 23894 | AI risk management | Risk management guidance |

### Relationship to EU AI Act

| EU AI Act Requirement | ISO 42001 Mapping |
|----------------------|-------------------|
| Risk management system (Art. 9) | Clause 6.1, 8.2, 8.3, Annex A.5 |
| Data governance (Art. 10) | Clause 8.4, Annex A.7 |
| Technical documentation (Art. 11) | Clause 7.5, Annex A.6 |
| Transparency (Art. 13) | Annex A.8 |
| Human oversight (Art. 14) | Annex A.9 |
| Accuracy, robustness, security (Art. 15) | Clause 9.1, Annex A.6 |
| Quality management system (Art. 17) | Full AIMS (Clauses 4-10) |
| Conformity assessment | Certification process |

### Certification Process

| Phase | Activity | Duration |
|-------|----------|----------|
| Preparation | Gap analysis, implementation, internal audit | 6-12 months |
| Stage 1 Audit | Documentation review, readiness assessment | 1-2 days |
| Gap Remediation | Address Stage 1 findings | 1-3 months |
| Stage 2 Audit | Implementation effectiveness assessment | 2-5 days |
| Certification | Certificate issued (3-year validity) | Upon passing |
| Surveillance | Annual surveillance audits | 1-2 days/year |
| Recertification | Full reassessment every 3 years | 2-4 days |

### Implementation Roadmap

**Phase 1 — Foundation (Months 1-3):**
- Define AIMS scope and boundaries
- Establish AI governance structure
- Develop AI policy
- Conduct initial AI system inventory
- Define risk assessment methodology

**Phase 2 — Core Implementation (Months 4-6):**
- Conduct AI risk assessments for all in-scope systems
- Perform impact assessments (Annex A.5)
- Implement AI lifecycle controls (Annex A.6)
- Establish data management processes (Annex A.7)
- Develop third-party management procedures (Annex A.10)

**Phase 3 — Operationalize (Months 7-9):**
- Deploy monitoring and measurement (Clause 9.1)
- Train personnel on AIMS roles and responsibilities
- Implement incident management procedures
- Conduct awareness programs for AI literacy
- Establish communication processes

**Phase 4 — Verify and Certify (Months 10-12):**
- Conduct internal audit (Clause 9.2)
- Hold management review (Clause 9.3)
- Address nonconformities
- Prepare for Stage 1 certification audit
- Compile evidence packages per clause

---

## Troubleshooting

| Problem | Possible Cause | Resolution |
|---------|---------------|------------|
| Readiness score low on Clause 5 (Leadership) despite executive sponsorship | AI policy does not include ethical principles, responsible AI commitment, or framework for setting AI objectives | Update AI policy to explicitly address all required elements: ethical principles, responsible AI, legal alignment, continual improvement commitment, and AI objectives framework; obtain formal management sign-off |
| AI impact assessment returns High/Critical risk across all dimensions | AI system processes sensitive personal data, makes autonomous decisions, and affects large populations without safeguards | Implement targeted mitigations per dimension: human-in-the-loop for safety, bias testing for fairness, explainability mechanisms for transparency, data protection for privacy; re-run assessment after mitigation |
| Annex A controls scored as "Not Implemented" despite operational practices | Practices exist informally but are not documented per ISO 42001 requirements | Document all existing AI practices as formal procedures; create evidence artifacts (policy documents, meeting minutes, risk registers, training records); map to specific Annex A control objectives |
| Certification body auditor questions AI risk assessment methodology | Risk assessment does not cover all seven required risk categories (fairness, transparency, safety, privacy, security, accountability, societal) | Update risk assessment methodology to explicitly address all ISO 42001 risk categories; use `ai_impact_assessor.py` template to ensure comprehensive coverage; document risk criteria and tolerance levels |
| Third-party AI components lack governance controls | Organization uses third-party AI models or APIs without formal evaluation or supplier management | Implement Annex A.10 (Third-Party Relationships) controls; evaluate all third-party AI components; establish contractual requirements for AI service providers; monitor supplier AI practices |
| Data management procedures incomplete for AI lifecycle | Data quality, provenance, and bias assessment not systematically performed for training and evaluation data | Implement Annex A.7 (Data for AI Systems) controls; establish data quality assessment procedures; document data provenance and lineage; conduct bias assessments per dataset; define retention and disposal procedures |
| Stage 1 audit finds AIMS documentation insufficient | Documentation follows generic QMS structure without AI-specific elements | Restructure documentation to address all ISO 42001 clauses (4-10) and Annex A controls (A.2-A.10); include AI-specific policies, risk assessments, impact assessments, and lifecycle procedures |

---

## Success Criteria

- **Overall readiness score of 80+ for certification readiness** -- as measured by `aims_readiness_checker.py`, with all clauses at Defined maturity level or above
- **AI policy established and communicated** -- including ethical principles, responsible AI commitment, legal compliance alignment, continual improvement, and framework for AI objectives, with formal management approval
- **AI impact assessments completed for all in-scope AI systems** -- covering all six dimensions (fairness, transparency, safety, privacy, security, accountability) with risk treatments documented and residual risk accepted by management
- **AI risk assessment methodology covers all required categories** -- fairness, transparency, safety, privacy, security, accountability, and societal/environmental impacts, with defined risk criteria and tolerance levels
- **Annex A controls implemented with evidence** -- A.2 (Policies) through A.10 (Third-Party) with documented procedures, records, and evidence artifacts suitable for certification audit
- **Internal audit conducted against all AIMS clauses** -- with findings documented, corrective actions tracked to closure, and management review completed with documented improvement decisions
- **AI lifecycle procedures operational** -- covering design, development, testing, deployment, monitoring, and retirement stages with documented controls at each gate

---

## Scope & Limitations

**In Scope:**
- ISO 42001:2023 readiness assessment across all clauses (4-10) and Annex A controls (A.2-A.10)
- AI impact assessment across six dimensions (fairness, transparency, safety, privacy, security, accountability)
- AIMS certification preparation including gap analysis, implementation roadmap, and audit readiness
- AI lifecycle management guidance (design through retirement)
- Data management for AI systems (quality, provenance, bias, governance)
- Third-party AI supplier management and evaluation
- Regulatory mapping to EU AI Act requirements
- Integration guidance with ISO 27001, ISO 9001, and ISO 14001

**Out of Scope:**
- Actual AI model development, training, testing, or deployment -- this skill provides governance frameworks, not ML engineering
- Certification body selection, audit scheduling, or certification fee negotiation
- Ethical review board establishment or ethical decision-making beyond procedural guidance
- Specific AI fairness algorithm implementation (e.g., adversarial debiasing, calibrated equalized odds) -- use `eu-ai-act-specialist` bias detector for technical testing
- Environmental impact measurement or carbon footprint calculation for AI training

**Important Notes:**
- ISO 42001 certification follows a 3-year cycle with annual surveillance audits at 12-month intervals
- Major certification bodies (BSI, DNV, TUV, LRQA) have operationalized ISO 42001 audit services as of 2025-2026
- Many organizations pursue dual alignment: ISO 42001 certification for governance controls plus EU AI Code of Practice for regulatory expectations
- The standard's Annex SL structure enables direct integration with ISO 27001, reducing redundant documentation and audit effort

---

## Integration Points

| Skill | Integration | When to Use |
|-------|-------------|-------------|
| `eu-ai-act-specialist` | ISO 42001 AIMS maps directly to EU AI Act requirements; certification demonstrates Art. 17 QMS compliance | When building AI governance satisfying both ISO 42001 and EU AI Act obligations |
| `information-security-manager-iso27001` | ISO 27001 security controls integrate with AIMS via shared Annex SL structure; risk assessment methodologies align | When implementing joint ISMS + AIMS covering both information security and AI governance |
| `gdpr-dsgvo-expert` | AIMS data management (Annex A.7) aligns with GDPR data protection requirements; AI processing requires DPIA | When AI systems process personal data and require both AIMS and GDPR compliance |
| `isms-audit-expert` | Internal audit methodology and finding management shared between ISO 27001 and ISO 42001 | When conducting internal audits covering both ISMS and AIMS |

---

## Tool Reference

### aims_readiness_checker.py

Assesses organizational readiness against all ISO 42001:2023 clauses and Annex A controls.

| Flag | Required | Description |
|------|----------|-------------|
| `--input <file>` | Yes (unless `--template`) | Path to JSON organizational profile for assessment |
| `--template` | No | Generate blank input template to stdout |
| `--json` | No | Output results in JSON format for automation |
| `--output <file>` | No | Export report to specified file path |

**Assessment Scope:** Clause 4 (Context), Clause 5 (Leadership), Clause 6 (Planning), Clause 7 (Support), Clause 8 (Operation), Clause 9 (Performance), Clause 10 (Improvement), and Annex A controls (A.2-A.10).

**Output:** Overall readiness score (0-100), per-clause scores with maturity level (Initial/Developing/Defined/Managed/Optimized), Annex A control implementation status, gap analysis with prioritized recommendations, and certification readiness assessment (Ready/Near Ready/Significant Gaps).

### ai_impact_assessor.py

Generates comprehensive AI impact assessments across six risk dimensions with regulatory mapping.

| Flag | Required | Description |
|------|----------|-------------|
| `--input <file>` | Yes (unless `--template`) | Path to JSON AI system description for assessment |
| `--template` | No | Generate blank AI system template to stdout |
| `--format <fmt>` | No | Output format: `json` (default) or `markdown` |
| `--output <file>` | No | Export assessment report to specified file path |

**Assessment Dimensions:** Fairness (bias, discrimination, equity), Transparency (explainability, interpretability), Safety (reliability, robustness, harm prevention), Privacy (data protection, consent, minimization), Security (adversarial resilience, access control), Accountability (governance, responsibility, auditability).

**Output:** Per-dimension risk scoring (Low/Medium/High/Critical), interested party impact mapping, risk treatment options (Avoid/Mitigate/Transfer/Accept), regulatory mapping (EU AI Act risk tier, ISO 42001 Annex A controls), residual risk calculation, and markdown or JSON report.
