# ISO 42001:2023 Clause-by-Clause Guide

Comprehensive implementation guidance for ISO/IEC 42001:2023 — AI Management Systems (AIMS). Covers all clauses (4-10), Annex A controls (A.2-A.10), audit questions, common findings, and evidence requirements.

---

## Table of Contents

- [Clause 4 — Context of the Organization](#clause-4--context-of-the-organization)
- [Clause 5 — Leadership](#clause-5--leadership)
- [Clause 6 — Planning](#clause-6--planning)
- [Clause 7 — Support](#clause-7--support)
- [Clause 8 — Operation](#clause-8--operation)
- [Clause 9 — Performance Evaluation](#clause-9--performance-evaluation)
- [Clause 10 — Improvement](#clause-10--improvement)
- [Annex A Controls](#annex-a-controls)
- [Cross-Standard Mapping](#cross-standard-mapping)
- [EU AI Act Alignment](#eu-ai-act-alignment)

---

## Clause 4 — Context of the Organization

### 4.1 Understanding the Organization and Its Context

**Requirement:** Determine external and internal issues relevant to the organization's purpose and that affect its ability to achieve the intended outcomes of its AIMS.

**AI-Specific Issues to Document:**
- External: Regulatory landscape (EU AI Act, national AI strategies), industry standards, public trust in AI, competitor AI capabilities, technology evolution, societal expectations for responsible AI
- Internal: AI maturity level, data infrastructure, talent availability, organizational culture toward AI adoption, existing management systems (ISO 27001, 9001)

**Implementation Steps:**
1. Conduct environmental scan for AI-related factors
2. Assess organizational AI maturity using a maturity model
3. Identify regulatory requirements applicable to AI systems
4. Document stakeholder expectations regarding AI
5. Review annually and update when context changes materially

**Evidence Required:**
- Context analysis document
- PESTLE or similar environmental analysis for AI factors
- AI maturity assessment results

**Audit Questions:**
- How has the organization identified external issues affecting its use of AI?
- What internal factors have been considered in establishing the AIMS?
- How does the organization monitor changes in its AI context?

**Common Findings:**
- Context analysis is generic and does not address AI-specific issues
- No consideration of societal impact or public trust factors
- Context not reviewed when new AI systems are deployed

### 4.2 Understanding the Needs and Expectations of Interested Parties

**Requirement:** Determine interested parties relevant to the AIMS and their requirements.

**Key Interested Parties for AI:**

| Interested Party | Typical Requirements |
|-----------------|---------------------|
| Consumers/users | Transparency, fairness, privacy, safety, explainability |
| Affected individuals | Non-discrimination, redress mechanisms, informed consent |
| Regulators | Compliance with AI regulations, reporting, documentation |
| Employees | AI literacy, job security concerns, ethical guidelines |
| Shareholders/investors | Risk management, governance, responsible innovation |
| Society | Safety, environmental impact, democratic values |
| Business partners | Data quality, security, liability allocation |
| Industry bodies | Standards compliance, best practices |

**Evidence Required:**
- Interested party register with requirements
- Stakeholder engagement records
- Regulatory requirement mapping

**Audit Questions:**
- Who are the interested parties for each AI system?
- How are their requirements determined and monitored?
- How are conflicting requirements between parties resolved?

### 4.3 Determining the Scope of the AIMS

**Requirement:** Determine the boundaries and applicability of the AIMS to establish its scope.

**Scope Considerations:**
- Which AI systems are included (all, or subset by risk level)
- Organizational units involved in AI development, deployment, and use
- Third-party AI systems used by the organization
- Geographic boundaries and regulatory jurisdictions
- Integration with existing management systems (ISO 27001, ISO 9001)

**Evidence Required:**
- AIMS scope statement document
- AI system inventory within scope
- Justification for any exclusions

**Audit Questions:**
- What AI systems are included in the AIMS scope?
- Are there AI systems excluded from scope? What is the justification?
- Does the scope cover third-party AI components and services?

### 4.4 AI Management System

**Requirement:** Establish, implement, maintain, and continually improve the AIMS in accordance with the standard.

**Evidence Required:**
- AIMS manual or integrated documentation
- Process maps for AIMS
- Continual improvement records

---

## Clause 5 — Leadership

### 5.1 Leadership and Commitment

**Requirement:** Top management shall demonstrate leadership and commitment with respect to the AIMS.

**Demonstration Methods:**
- Allocating adequate resources (budget, personnel, compute, data)
- Establishing AI policy and objectives
- Integrating AIMS requirements into business processes
- Promoting continual improvement and responsible AI
- Supporting other relevant management roles
- Communicating the importance of effective AI governance

**Evidence Required:**
- Management meeting minutes showing AI governance topics
- Resource allocation records (budget, headcount)
- Management communications on AI policy

**Audit Questions:**
- How does top management demonstrate commitment to the AIMS?
- What resources have been allocated for AI governance?
- How is AI governance integrated into business strategy?

**Common Findings:**
- Management commitment is stated but not substantiated with resource allocation
- AI governance is delegated without management oversight
- No regular management review of AIMS effectiveness

### 5.2 Policy

**Requirement:** Establish an AI policy that is appropriate, provides a framework for objectives, includes commitment to satisfy requirements, and includes commitment to continual improvement.

**AI Policy Must Include:**
- Commitment to responsible and ethical AI development and use
- Principles for fairness, transparency, safety, privacy, and accountability
- Alignment with organizational values and applicable regulations
- Framework for setting and reviewing AI objectives
- Commitment to continual improvement of the AIMS
- Commitment to satisfying applicable regulatory requirements
- Statement on human oversight of AI decisions

**Evidence Required:**
- Documented AI policy signed by top management
- Communication records (email, intranet, training)
- Policy review records

**Audit Questions:**
- Does the AI policy cover responsible AI principles?
- How is the policy communicated across the organization?
- When was the policy last reviewed and updated?
- Do employees understand and apply the policy?

### 5.3 Organizational Roles, Responsibilities, and Authorities

**Requirement:** Ensure responsibilities and authorities for relevant roles are assigned, communicated, and understood.

**Key Roles:**

| Role | Responsibility |
|------|---------------|
| AIMS Management Representative | Overall AIMS effectiveness, reporting to management |
| AI Governance Board | Strategic oversight, policy decisions, risk appetite |
| AI System Owner | Accountable for individual AI system performance and compliance |
| Data Steward | Data quality, governance, privacy for AI data |
| AI Ethics Officer/Board | Ethical review of AI applications |
| AI Risk Manager | AI-specific risk assessment and treatment |
| Model Validator | Independent model validation and testing |
| Incident Manager | AI incident response and management |

**Evidence Required:**
- Organizational chart with AIMS roles
- Role descriptions with authorities
- Appointment records

---

## Clause 6 — Planning

### 6.1 Actions to Address Risks and Opportunities

**Requirement:** Determine risks and opportunities relevant to the AIMS and plan actions to address them.

**AI-Specific Risk Categories:**

| Category | Risk Examples |
|----------|-------------|
| Technical | Model failure, data quality issues, adversarial attacks, drift, hallucination |
| Ethical | Bias, discrimination, lack of explainability, autonomy erosion |
| Legal | Regulatory non-compliance, liability, IP infringement, contract breach |
| Societal | Job displacement, misinformation, environmental impact, public trust erosion |
| Organizational | Skill gaps, vendor lock-in, shadow AI, reputational damage |
| Security | Data poisoning, model extraction, prompt injection, unauthorized access |

**Risk Assessment Methodology Must Define:**
- Risk identification process (how risks are discovered)
- Risk analysis (likelihood and impact assessment criteria)
- Risk evaluation (risk acceptance criteria and thresholds)
- Risk treatment options (Avoid, Mitigate, Transfer, Accept)
- Risk ownership and accountability
- Risk review frequency

**Evidence Required:**
- Risk assessment methodology document
- Risk register with AI-specific risks
- Risk treatment plans
- Risk acceptance records

### 6.2 AI Management System Objectives and Planning to Achieve Them

**Requirement:** Establish measurable AI objectives and plan how to achieve them.

**Example AI Objectives:**

| Objective | Metric | Target | Timeline |
|-----------|--------|--------|----------|
| Bias reduction | Demographic parity difference | < 0.05 | 6 months |
| Transparency | % of AI decisions with explanations | 100% for high-risk | Q2 |
| Incident reduction | AI incidents per quarter | < 2 | Ongoing |
| Compliance | Regulatory requirements met | 100% | Ongoing |
| Literacy | Employees completing AI training | > 90% | Annual |

**Evidence Required:**
- Documented AI objectives (SMART criteria)
- Plans to achieve objectives (who, what, when, resources)
- Monitoring and measurement records

---

## Clause 7 — Support

### 7.1 Resources

**AI-Specific Resources:**
- **Compute**: GPU/TPU capacity, cloud resources, training infrastructure
- **Data**: Training datasets, evaluation datasets, production data pipelines
- **Expertise**: Data scientists, ML engineers, AI ethics specialists, domain experts
- **Tools**: ML platforms, monitoring tools, testing frameworks, version control
- **Infrastructure**: Development environments, staging, production, backup

### 7.2 Competence

**Required Competencies:**

| Role Type | Competencies |
|-----------|-------------|
| AI developers | ML fundamentals, data engineering, model evaluation, responsible AI |
| AI operators | Deployment, monitoring, incident response, performance tuning |
| Business users | AI literacy, limitations awareness, human oversight practices |
| Governance | Risk assessment, regulatory compliance, ethical evaluation |
| Data management | Data quality, privacy, governance, bias assessment |

**Evidence Required:**
- Competence requirements per role
- Training records and certifications
- Competence evaluation results

### 7.3 Awareness

**All relevant persons must be aware of:**
- The AI policy
- Their contribution to AIMS effectiveness
- Implications of not conforming to AIMS requirements
- Responsible AI principles and their practical application

### 7.5 Documented Information

**Required Documented Information:**

| Document | Clause | Type |
|----------|--------|------|
| AI policy | 5.2 | Maintained |
| AIMS scope | 4.3 | Maintained |
| Risk assessment methodology | 6.1 | Maintained |
| Risk assessment results | 6.1, 8.2 | Retained |
| AI objectives | 6.2 | Maintained |
| Competence evidence | 7.2 | Retained |
| Operational procedures | 8.1 | Maintained |
| Impact assessments | 8.2, A.5 | Retained |
| AI lifecycle records | 8.4, A.6 | Retained |
| Monitoring results | 9.1 | Retained |
| Internal audit results | 9.2 | Retained |
| Management review records | 9.3 | Retained |
| Nonconformity records | 10.1 | Retained |
| Statement of Applicability | Annex A | Maintained |

---

## Clause 8 — Operation

### 8.1 Operational Planning and Control

**Requirement:** Plan, implement, and control processes needed to meet requirements and implement actions from Clause 6.

### 8.2 AI Risk Assessment

**Requirement:** Perform AI risk assessments at planned intervals or when significant changes are proposed.

**When to Conduct Risk Assessment:**
- Before developing a new AI system
- Before deploying an AI system to production
- When significant changes are made to an AI system
- After an AI incident
- At planned intervals (annually minimum)
- When the external context changes materially

### 8.3 AI Risk Treatment

**Treatment Options:**

| Option | When to Apply | Example |
|--------|--------------|---------|
| Avoid | Risk exceeds appetite, no viable mitigation | Discontinue high-risk AI application |
| Mitigate | Risk can be reduced to acceptable level | Add human oversight, improve data quality |
| Transfer | Risk better managed by another party | Insurance, contractual allocation |
| Accept | Residual risk within appetite after treatment | Document acceptance rationale |

### 8.4 AI System Lifecycle

**See:** [ai-lifecycle-management.md](ai-lifecycle-management.md) for detailed lifecycle guidance.

**Evidence Required:**
- Lifecycle procedures per stage
- Design records (requirements, architecture, ethical review)
- Development records (data preparation, model training, code review)
- Testing records (functional, bias, robustness, performance)
- Deployment records (approval, staging, monitoring setup)
- Operational records (monitoring logs, performance reports)
- Retirement records (decommissioning plan, data disposal)

---

## Clause 9 — Performance Evaluation

### 9.1 Monitoring, Measurement, Analysis, and Evaluation

**AI Performance Metrics to Monitor:**

| Category | Metrics |
|----------|---------|
| Accuracy | Precision, recall, F1-score, AUROC, RMSE (as applicable) |
| Fairness | Demographic parity, equalized odds, disparate impact ratio |
| Reliability | Uptime, response time, throughput, error rate |
| Drift | Data drift (PSI, KS test), concept drift, prediction drift |
| Safety | Incident count, near-miss count, harm severity |
| Compliance | Regulatory requirements met, audit findings |
| User satisfaction | Complaints, feedback scores, adoption rates |

### 9.2 Internal Audit

**Audit Program Requirements:**
- Planned intervals (annually minimum)
- Covers all AIMS clauses and applicable Annex A controls
- Auditor independence from area being audited
- Audit criteria, scope, frequency, and methods defined
- Results reported to relevant management

**Audit Evidence Checklist:**
- [ ] AIMS scope and policy documents
- [ ] Risk assessments and treatment plans
- [ ] AI system inventory and lifecycle records
- [ ] Competence and training records
- [ ] Monitoring and measurement results
- [ ] Incident and nonconformity records
- [ ] Management review minutes
- [ ] Statement of Applicability

### 9.3 Management Review

**Inputs to Management Review:**
- Status of actions from previous reviews
- Changes in internal/external issues
- AI system performance and trends
- Audit results
- Nonconformities and corrective actions
- Monitoring and measurement results
- AI incident reports
- Interested party feedback
- Opportunities for improvement

**Outputs from Management Review:**
- Decisions on improvement opportunities
- Changes to AIMS (scope, policy, objectives)
- Resource allocation decisions
- Risk appetite adjustments

---

## Clause 10 — Improvement

### 10.1 Nonconformity and Corrective Action

**Process:**
1. Identify nonconformity
2. React to control and correct it
3. Evaluate need for action to eliminate cause
4. Implement corrective action
5. Review effectiveness
6. Update risks and opportunities if needed
7. Make changes to AIMS if needed

### 10.2 Continual Improvement

**Improvement Sources:**
- Internal audit findings
- Management review outputs
- AI incident lessons learned
- Industry best practice evolution
- Regulatory changes
- Technology advancement
- Stakeholder feedback

### 10.3 AI Incident Management (AI-Specific)

**Incident Types:**
- Model producing biased or discriminatory outputs
- Unexpected model behavior or hallucination
- Data breach involving AI training/inference data
- AI system causing harm (physical, financial, psychological)
- Adversarial attack on AI system
- AI system producing unsafe outputs
- Significant performance degradation

**Incident Management Process:**
1. Detection and reporting
2. Classification (severity, impact, scope)
3. Containment (disable, rollback, human override)
4. Investigation (root cause analysis)
5. Resolution and recovery
6. Communication to interested parties
7. Lessons learned and preventive actions
8. Documentation and evidence preservation

---

## Annex A Controls

### A.2 — AI Policies

**Objective:** Provide management direction and support for AI in accordance with business requirements and applicable laws.

**Requirements:**
- Define policies for AI development, deployment, and use
- Include responsible AI principles (fairness, transparency, safety, privacy)
- Approve policies at management level
- Communicate to all relevant persons
- Review at planned intervals

**Evidence:** AI policy document, communication records, review records

**Audit Questions:**
- Is there a documented AI policy?
- Does it cover responsible AI principles?
- Is it communicated to all employees involved with AI?
- When was it last reviewed?

### A.3 — Internal Organization for AI

**Objective:** Establish a management framework to initiate and control AI implementation.

**Requirements:**
- Define roles and responsibilities for AI governance
- Implement segregation of duties (development vs. validation vs. deployment)
- Establish AI governance committee or board
- Define escalation and decision-making authority

**Evidence:** Org chart, role descriptions, governance charter, meeting minutes

### A.4 — Resources for AI Systems

**Objective:** Achieve and maintain appropriate protection and management of resources.

**Requirements:**
- Identify and provide resources for each AI system
- Manage compute, data, and expertise resources
- Plan for resource scaling and capacity
- Address resource dependencies and single points of failure

**Evidence:** Resource inventory, capacity plans, budget allocation

### A.5 — Assessing AI System Impact

**Objective:** Identify and evaluate impacts of AI systems on individuals and society.

**Requirements:**
- Establish impact assessment process
- Conduct assessments before deployment and periodically thereafter
- Evaluate fairness, safety, privacy, transparency, and societal impact
- Document assessment results and treatment decisions
- Review when systems change materially

**Evidence:** Impact assessment procedure, completed assessments, treatment records

### A.6 — AI System Lifecycle

**Objective:** Ensure controls throughout the AI system lifecycle.

**Requirements:**
- Define lifecycle stages and gates
- Implement design, development, testing, deployment, monitoring, and retirement controls
- Version control for models and data
- Change management procedures
- Testing and validation requirements

**Evidence:** Lifecycle procedure, stage-gate records, version history, test results

### A.7 — Data for AI Systems

**Objective:** Ensure appropriate management of data used in AI systems.

**Requirements:**
- Data quality assessment and improvement
- Data provenance and lineage tracking
- Bias assessment for training and evaluation data
- Data governance and access controls
- Personal data protection measures
- Data retention and disposal
- Data labeling quality assurance

**Evidence:** Data governance policy, quality reports, provenance records, bias assessments

### A.8 — Information for Interested Parties

**Objective:** Provide appropriate transparency about AI systems.

**Requirements:**
- Disclose use of AI to affected individuals
- Provide information about AI system capabilities and limitations
- Enable meaningful human oversight
- Publish transparency reports or model cards
- Communicate AI-related incidents to affected parties

**Evidence:** Disclosure mechanisms, model cards, transparency reports, incident communications

### A.9 — Use of AI Systems

**Objective:** Ensure responsible use of AI systems.

**Requirements:**
- Define acceptable use policies for AI systems
- Implement human oversight mechanisms
- Provide user guidance and training
- Monitor use for compliance with acceptable use
- Prevent misuse through technical and organizational controls

**Evidence:** Acceptable use policy, human oversight procedures, user guidance, monitoring records

### A.10 — Third-Party Relationships

**Objective:** Manage risks associated with third-party AI components and services.

**Requirements:**
- Evaluate third-party AI suppliers before engagement
- Include AI-specific requirements in contracts
- Monitor third-party compliance with requirements
- Manage AI supply chain risks
- Conduct due diligence on third-party training data

**Evidence:** Supplier evaluation records, contracts, monitoring records, due diligence reports

---

## Cross-Standard Mapping

### ISO 42001 to ISO 27001 Mapping

| ISO 42001 | ISO 27001 | Integration Approach |
|-----------|-----------|---------------------|
| 4.1 Context | 4.1 Context | Extend existing context analysis with AI factors |
| 5.2 AI Policy | 5.2 Information Security Policy | Create AI policy referencing/extending security policy |
| 6.1 Risk Assessment | 6.1.2 Risk Assessment | Use same methodology, add AI-specific risk categories |
| 7.5 Documented Info | 7.5 Documented Information | Use same document control system |
| 8.2 AI Risk Assessment | 8.2 Risk Assessment | Extend risk register with AI risks |
| 9.2 Internal Audit | 9.2 Internal Audit | Combine audit programs, add AI audit criteria |
| 9.3 Management Review | 9.3 Management Review | Add AI performance to review inputs |
| A.7 Data for AI | A.8.10-12 Data controls | Extend data controls for AI-specific requirements |
| A.10 Third Party | A.5.19-23 Supplier | Extend supplier management for AI components |

### ISO 42001 to ISO 9001 Mapping

| ISO 42001 | ISO 9001 | Integration Approach |
|-----------|----------|---------------------|
| 4.4 AIMS | 4.4 QMS | Integrate AI management into existing QMS |
| 7.1 Resources | 7.1 Resources | Add AI resource requirements to resource planning |
| 7.2 Competence | 7.2 Competence | Add AI competence to training program |
| 8.1 Operational Planning | 8.1 Operational Planning | Include AI processes in operational planning |
| 9.1 Monitoring | 9.1 Monitoring | Add AI metrics to quality measurement |
| 10.1 Nonconformity | 10.1 Nonconformity | Use same CAPA process for AI nonconformities |

---

## EU AI Act Alignment

### High-Risk AI Systems (Articles 6-15, 17)

| EU AI Act Requirement | ISO 42001 Mapping | Implementation Guidance |
|----------------------|-------------------|------------------------|
| Risk management system (Art. 9) | 6.1, 8.2, 8.3, A.5 | Use ISO 42001 risk framework to satisfy Art. 9 |
| Data governance (Art. 10) | A.7 | Data quality, bias assessment, provenance per A.7 |
| Technical documentation (Art. 11) | 7.5, A.6 | Lifecycle documentation satisfies Art. 11 + Annex IV |
| Record-keeping (Art. 12) | 7.5, 9.1 | Audit trails and monitoring records |
| Transparency (Art. 13) | A.8 | Stakeholder information and disclosure |
| Human oversight (Art. 14) | A.9 | Human oversight mechanisms per A.9 |
| Accuracy, robustness, cybersecurity (Art. 15) | 9.1, A.6 | Performance monitoring and lifecycle controls |
| Quality management system (Art. 17) | Full AIMS | ISO 42001 AIMS satisfies Art. 17 QMS requirement |
| Conformity assessment (Art. 43) | 9.2, Certification | Internal audit + certification process |

### Using ISO 42001 Certification for EU AI Act Compliance

ISO 42001 certification can support EU AI Act conformity assessment:
- Demonstrates a functioning quality management system (Art. 17)
- Provides evidence of risk management (Art. 9)
- Shows data governance practices (Art. 10)
- Documents human oversight procedures (Art. 14)

**Note:** ISO 42001 certification alone does not guarantee EU AI Act compliance. Additional technical requirements specific to the AI system must also be met.
