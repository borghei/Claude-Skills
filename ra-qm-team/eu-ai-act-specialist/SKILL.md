---
name: eu-ai-act-specialist
description: EU AI Act (Regulation EU 2024/1689) compliance specialist for AI system risk classification, provider and deployer obligations, GPAI model compliance, conformity assessment, bias detection, and AI governance. Covers the full regulatory lifecycle from system inventory through post-market monitoring.
triggers:
  - EU AI Act
  - artificial intelligence regulation
  - AI risk classification
  - high-risk AI
  - AI compliance
  - AI transparency
  - AI governance
  - conformity assessment AI
  - AI Act obligations
  - GPAI model compliance
  - AI system audit
---

# EU AI Act Compliance Specialist

Production-ready compliance patterns for Regulation (EU) 2024/1689 — the EU Artificial Intelligence Act. Covers risk classification, provider/deployer obligations, GPAI model requirements, conformity assessment, and AI governance.

---

## Table of Contents

- [EU AI Act Overview](#eu-ai-act-overview)
- [Risk Classification System](#risk-classification-system)
- [Provider Obligations for High-Risk AI](#provider-obligations-for-high-risk-ai)
- [Deployer Obligations](#deployer-obligations)
- [General-Purpose AI Models (GPAI)](#general-purpose-ai-models-gpai)
- [Penalties](#penalties)
- [Implementation Timeline](#implementation-timeline)
- [AI Literacy Requirements](#ai-literacy-requirements)
- [AI System Inventory and Classification Workflow](#ai-system-inventory-and-classification-workflow)
- [Conformity Assessment Workflow](#conformity-assessment-workflow)
- [Bias Detection and Fairness Testing Framework](#bias-detection-and-fairness-testing-framework)
- [AI Model Documentation Templates](#ai-model-documentation-templates)
- [Reference Documentation](#reference-documentation)
- [Tools](#tools)

---

## EU AI Act Overview

**Regulation (EU) 2024/1689** — the Artificial Intelligence Act — is the world's first comprehensive legal framework for AI. It establishes harmonized rules for the placing on the market, putting into service, and use of AI systems in the European Union.

### Key Facts

| Attribute | Detail |
|-----------|--------|
| **Regulation** | (EU) 2024/1689 |
| **Adopted** | 13 June 2024 |
| **Published** | 12 July 2024 (Official Journal L 2024/1689) |
| **Entry into force** | 1 August 2024 |
| **Full application** | 2 August 2026 (with phased deadlines) |
| **Scope** | Providers, deployers, importers, distributors, product manufacturers placing or using AI systems in the EU market |
| **Extraterritorial** | Applies to non-EU entities if their AI system output is used in the EU |

### Regulatory Objectives

1. Ensure AI systems placed on the EU market are safe and respect fundamental rights
2. Provide legal certainty for AI investment and innovation
3. Enhance governance and enforcement of AI requirements
4. Develop a single market for lawful, safe, and trustworthy AI

### Definition of AI System (Art. 3(1))

A machine-based system designed to operate with varying levels of autonomy, that may exhibit adaptiveness after deployment, and that, for explicit or implicit objectives, infers from the input it receives how to generate outputs such as predictions, content, recommendations, or decisions that can influence physical or virtual environments.

### Who Is Covered

| Role | Definition | Key Obligations |
|------|-----------|-----------------|
| **Provider** | Develops or has an AI system developed and places it on the market or puts it into service under its own name/trademark | Full compliance: risk management, data governance, technical docs, conformity assessment |
| **Deployer** | Uses an AI system under its authority (except personal non-professional use) | Use per instructions, human oversight, monitoring, incident reporting |
| **Importer** | Places on EU market an AI system from a third country | Verify conformity assessment, CE marking, documentation |
| **Distributor** | Makes AI system available on EU market (not provider or importer) | Verify CE marking, storage/transport conditions |
| **Authorised Representative** | Established in the EU, mandated by a non-EU provider | Act on behalf of provider for conformity and authority liaison |

---

## Risk Classification System

The AI Act uses a **risk-based approach** with four tiers. Classification determines the obligations that apply.

### Tier 1: Unacceptable Risk — Prohibited Practices (Art. 5)

These AI practices are **banned outright** from 2 February 2025:

| Prohibited Practice | Description | Article |
|---------------------|-------------|---------|
| **Social scoring** | AI systems used by public authorities (or on their behalf) to evaluate or classify natural persons based on social behaviour or personal traits, leading to detrimental or unfavourable treatment | Art. 5(1)(c) |
| **Real-time remote biometric identification in public spaces** | Use by law enforcement in publicly accessible spaces, except for narrowly defined exceptions (missing children, imminent terrorist threat, serious criminal suspects) | Art. 5(1)(h) |
| **Emotion recognition in workplace and education** | AI systems inferring emotions of natural persons in the workplace or educational institutions, except for medical or safety reasons | Art. 5(1)(f) |
| **Predictive policing (individual)** | AI systems making risk assessments of natural persons to predict criminal offending based solely on profiling or personality traits | Art. 5(1)(d) |
| **Exploitation of vulnerabilities** | AI that exploits age, disability, or social/economic situation of a person to materially distort their behaviour in a way likely to cause significant harm | Art. 5(1)(b) |
| **Subliminal manipulation** | AI deploying subliminal techniques beyond a person's consciousness to materially distort behaviour causing significant harm | Art. 5(1)(a) |
| **Untargeted facial image scraping** | Creating or expanding facial recognition databases through untargeted scraping from the internet or CCTV footage | Art. 5(1)(e) |
| **Biometric categorization (sensitive attributes)** | AI systems categorizing natural persons based on biometric data to deduce race, political opinions, trade union membership, religious beliefs, sex life, or sexual orientation (except lawful labelling of lawfully acquired biometric data in law enforcement) | Art. 5(1)(g) |

### Tier 2: High-Risk AI Systems (Art. 6, Annex III)

High-risk AI systems are subject to the **full set of provider obligations**. An AI system is high-risk if it falls under Annex III categories OR is a safety component of a product covered by EU harmonisation legislation listed in Annex I.

#### Annex III Categories

| # | Category | Examples |
|---|----------|----------|
| 1 | **Biometric identification and categorisation** | Remote biometric identification (not real-time in public by law enforcement), biometric categorisation by sensitive attributes, emotion recognition |
| 2 | **Critical infrastructure management and operation** | AI managing safety of road traffic, water/gas/heating/electricity supply, digital infrastructure |
| 3 | **Education and vocational training** | AI determining access to or admission to educational institutions, evaluating learning outcomes, monitoring prohibited behaviour during tests, assessing appropriate level of education |
| 4 | **Employment, workers management, and access to self-employment** | AI for recruitment/screening/filtering, promotion/termination decisions, task allocation based on behaviour/traits, performance monitoring |
| 5 | **Access to and enjoyment of essential private and public services** | AI for creditworthiness assessment, risk assessment and pricing in life/health insurance, evaluation of eligibility for public assistance, emergency dispatch prioritization |
| 6 | **Law enforcement** | AI as polygraph or to detect emotional state, deepfake detection in criminal investigations, risk assessment for offending/reoffending, profiling during investigation, crime analytics |
| 7 | **Migration, asylum, and border control** | AI as polygraph for asylum interviews, risk assessment for irregular migration, examining visa/permit applications, identification during border checks |
| 8 | **Administration of justice and democratic processes** | AI assisting judicial authorities in fact-finding and law interpretation, AI intended to influence outcome of elections or referendums |

#### High-Risk Determination Logic (Art. 6)

```
Is the AI system a safety component of a product covered by Annex I EU harmonisation legislation?
├── YES → High-risk (requires third-party conformity assessment per that legislation)
└── NO → Does the AI system fall under an Annex III category?
    ├── YES → Is the AI system performing a narrow procedural task, improving result
    │         of a prior human activity, detecting decision patterns without replacing
    │         human assessment, or performing a preparatory task?
    │   ├── YES (and no significant risk to health, safety, fundamental rights)
    │   │   → NOT high-risk (provider must document this determination)
    │   └── NO → HIGH-RISK — full obligations apply
    └── NO → Not high-risk (may still be limited or minimal risk)
```

### Tier 3: Limited Risk — Transparency Obligations (Art. 50)

These AI systems require **disclosure to users** but do not face the full high-risk obligations:

| System Type | Transparency Requirement |
|-------------|------------------------|
| **AI systems interacting with persons** (chatbots) | Must inform the person they are interacting with an AI system, unless obvious from context |
| **Emotion recognition / biometric categorization** | Must inform exposed persons of system operation and process data in compliance with GDPR/LED |
| **AI-generated or manipulated content** (deepfakes) | Must disclose that content has been artificially generated or manipulated; machine-readable labelling required |
| **AI-generated text on public interest matters** | Must disclose AI generation when published to inform the public, unless editorially reviewed by a human |

### Tier 4: Minimal Risk

AI systems not falling into the above categories. These include:
- AI-enabled video games
- Spam filters
- Inventory management systems
- Manufacturing optimization (non-safety)

**No mandatory requirements**, but providers are encouraged to voluntarily apply codes of conduct (Art. 95), including:
- Voluntary adherence to high-risk requirements
- Environmental sustainability considerations
- AI literacy promotion
- Diversity in development teams

---

## Provider Obligations for High-Risk AI

Providers of high-risk AI systems must comply with **all** of the following:

### 1. Risk Management System (Art. 9)

Establish, implement, document, and maintain a **continuous iterative process** throughout the AI system lifecycle:

1. **Identify and analyse** known and reasonably foreseeable risks to health, safety, and fundamental rights
2. **Estimate and evaluate** risks that may emerge when the system is used in accordance with its intended purpose and under conditions of reasonably foreseeable misuse
3. **Evaluate risks** arising from analysis of data gathered through post-market monitoring
4. **Adopt suitable risk management measures** addressing identified risks
5. Ensure residual risk is **acceptable** considering benefits and state of the art

**Testing requirements:**
- Test prior to placing on market and throughout lifecycle
- Test against preliminarily defined metrics and probabilistic thresholds
- Test in real-world conditions where appropriate

**Key principle:** Risk management measures must reflect state of the art and consider technical knowledge, experience, and accepted standards.

### 2. Data Governance (Art. 10)

Training, validation, and testing datasets must meet quality criteria:

| Requirement | Detail |
|-------------|--------|
| **Design choices** | Document choices about data collection, origin, volume, and labelling |
| **Data preparation** | Annotation, labelling, cleaning, enrichment, aggregation — all documented |
| **Assumptions** | Document what the data is meant to measure and represent |
| **Availability and quantity** | Sufficient for intended purpose |
| **Representativeness** | Representative of the population the system will be used on |
| **Bias examination** | Examine datasets for possible biases likely to affect health, safety, or fundamental rights |
| **Bias mitigation** | Identify and address gaps or shortcomings through appropriate measures |
| **Special categories** | Processing of special category data (Art. 9 GDPR) only where strictly necessary for bias detection/correction, with appropriate safeguards |
| **Geographic/contextual** | Consider specific settings the system will be used in, including geography, behaviour, and context |

### 3. Technical Documentation (Art. 11)

Drawn up **before** the system is placed on the market, must include:

- General description of the AI system
- Detailed description of system elements and development process
- Monitoring, functioning, and control of the AI system
- Description of system appropriateness with respect to intended purpose
- Risk management documentation
- Changes during system lifecycle
- Data governance documentation
- Performance metrics, including for specific affected groups
- Information about training datasets (or where they are maintained)
- Detailed description of the AI system's intended purpose

**Must be kept up to date** throughout the system lifecycle.

### 4. Record-Keeping / Automatic Logging (Art. 12)

High-risk AI systems must enable **automatic recording of events** (logs) throughout the system's lifetime:

- Logs must enable tracing of system operation
- Recording of the period of each use (start/end date)
- Reference database against which input data was checked
- Input data for which the search led to a match
- Identification of natural persons involved in verification of results

**Retention:** Logs must be kept for a period appropriate to the intended purpose (minimum as required by EU/national law).

### 5. Transparency and Information to Deployers (Art. 13)

The AI system must be designed to be **sufficiently transparent** to enable deployers to interpret output and use it appropriately:

- **Instructions for use** must accompany the system, including:
  - Identity and contact details of the provider
  - System characteristics, capabilities, and limitations
  - Intended purpose and any foreseeable misuse
  - Levels of accuracy, robustness, and cybersecurity tested against
  - Known or foreseeable circumstances creating risks
  - Performance regarding specific groups of persons
  - Specifications for input data
  - Human oversight measures
  - Computational and hardware resources needed
  - Expected lifetime and maintenance/care measures
  - Description of logging mechanism (Art. 12)

### 6. Human Oversight (Art. 14)

Designed to be effectively overseen by natural persons during use:

| Oversight Level | Description | When Required |
|----------------|-------------|---------------|
| **Human-in-the-loop** | Human approves every decision before it is applied | Highest risk — individual critical decisions |
| **Human-on-the-loop** | Human monitors operations and can intervene at any time | Standard for most high-risk systems |
| **Human-in-command** | Human has ability to override, reverse, or shut down | All high-risk systems must support this |

**Oversight persons must be able to:**
- Fully understand the AI system's capacities and limitations
- Correctly interpret the AI system's output
- Decide not to use the system or disregard/reverse the output
- Intervene or interrupt the system via a "stop" button or similar

**Automation bias safeguards:** Specific measures to prevent over-reliance on AI system output (automation bias), particularly for high-risk decisions.

### 7. Accuracy, Robustness, and Cybersecurity (Art. 15)

| Property | Requirements |
|----------|-------------|
| **Accuracy** | Achieve and maintain appropriate levels of accuracy for intended purpose; declare levels in instructions for use |
| **Robustness** | Resilient to errors, faults, or inconsistencies in input; include redundancy and fail-safe measures where appropriate |
| **Cybersecurity** | Protect against unauthorised third-party manipulation; address AI-specific vulnerabilities (data poisoning, adversarial examples, model flipping, confidentiality attacks); security proportionate to risks |

### 8. Quality Management System (Art. 17)

Providers must establish a documented QMS covering:

- Strategy for regulatory compliance
- Design and design verification/validation techniques
- Development, quality control, and quality assurance processes
- Examination, test, and validation procedures (before, during, after development)
- Technical specifications and standards applied
- Systems and procedures for data management (collection, analysis, labelling, storage, filtration, mining, aggregation, retention, and any other data operation)
- Risk management system (Art. 9)
- Post-market monitoring (Art. 72)
- Procedures for incident and malfunction reporting
- Communication with competent authorities and notified bodies
- Record-keeping
- Resource management (including supply-chain measures)
- Accountability framework

### 9. Conformity Assessment (Art. 43)

Before placing a high-risk AI system on the market:

| Assessment Path | When Required | Procedure |
|----------------|---------------|-----------|
| **Internal control** (Annex VI) | AI systems listed in Annex III points 2-8, UNLESS the provider applies harmonised standards or common specifications that cover the requirements | Provider self-assesses and documents compliance |
| **Third-party assessment** (Annex VII) | Biometric identification systems (Annex III point 1); systems where harmonised standards do not cover all requirements; when provider chooses not to apply harmonised standards | Notified body reviews documentation and tests system |
| **Based on product legislation** | AI systems that are safety components of products under Annex I | Follow conformity assessment of the relevant product legislation |

### 10. CE Marking (Art. 48)

- Affix **CE marking** visibly, legibly, and indelibly to the high-risk AI system (or its packaging/documentation if not practicable)
- CE marking indicates conformity with the AI Act
- Must be accompanied by the identification number of the notified body (if applicable)
- Must precede placing on the market

### 11. EU Database Registration (Art. 49)

Before placing on the market or putting into service:

- Provider (or authorised representative) must register in the **EU database** established under Art. 71
- Enter required information including: provider identity, system description, intended purpose, conformity assessment status, member states of availability, and any restrictions
- Deployers who are public authorities must also register

### 12. Post-Market Monitoring (Art. 72)

Establish and document a **post-market monitoring system** proportionate to the nature and risks:

- Actively and systematically collect, document, and analyse relevant data
- Data may be provided by deployers or collected through other means
- Assess continuous compliance with requirements
- Feed into risk management system updates
- Post-market monitoring plan must be part of technical documentation
- For high-risk AI, the plan must include analysis of interaction with other AI systems

**Serious incident reporting (Art. 73):**
- Report any serious incident to market surveillance authorities within **15 days** of becoming aware
- Take immediate corrective action
- Report to authorities of all member states where the incident occurred

---

## Deployer Obligations

### Art. 26 — Deployer Requirements

| Obligation | Detail |
|-----------|--------|
| **Use per instructions** | Operate the system in accordance with the provider's instructions for use |
| **Human oversight** | Assign human oversight to natural persons with competence, training, and authority; ensure overseers can effectively monitor |
| **Input data relevance** | Ensure input data is relevant and sufficiently representative for the intended purpose |
| **Monitoring** | Monitor operation based on instructions for use; inform provider/distributor of any risks or incidents |
| **Record-keeping** | Keep logs automatically generated by the system for a period appropriate to purpose (minimum 6 months unless otherwise required) |
| **Inform workers** | Inform workers and their representatives that they will be subject to high-risk AI before putting into service |
| **DPIA** | Carry out a data protection impact assessment (GDPR Art. 35) when required |
| **Fundamental Rights Impact Assessment** | Public bodies and private entities providing public services must perform a fundamental rights impact assessment before deployment (Art. 27) |
| **Incident reporting** | Report serious incidents to provider and market surveillance authority |

### Fundamental Rights Impact Assessment (Art. 27)

Required for deployers that are public bodies or private entities providing public services. Must include:

1. Description of the deployer's processes using the AI system
2. Period and frequency of intended use
3. Categories of natural persons and groups likely to be affected
4. Specific risks of harm likely to affect identified categories
5. Description of human oversight measures
6. Measures to be taken in case of materialization of risks
7. Governance and complaint mechanisms planned

Submit results to the relevant market surveillance authority. Update when circumstances change.

---

## General-Purpose AI Models (GPAI)

### Overview

Title III and Chapter V establish rules for **general-purpose AI models** (GPAI) — AI models trained on broad data at scale, capable of competently performing a wide range of distinct tasks (e.g., large language models, foundation models).

### GPAI Provider Obligations (Art. 53)

All GPAI model providers must:

| Obligation | Detail |
|-----------|--------|
| **Technical documentation** | Draw up and maintain technical documentation of the model and its training/testing process, including information for downstream providers |
| **Information for downstream providers** | Provide sufficient information to enable AI system providers using the GPAI model to understand the model's capabilities and comply with their own obligations |
| **Copyright compliance** | Put in place a policy to comply with EU copyright law (Directive 2019/790), including opt-out mechanisms for text and data mining rights holders |
| **Training data summary** | Make publicly available a sufficiently detailed summary of the content used for training the GPAI model, per a template provided by the AI Office |
| **EU representative** | Non-EU providers must appoint an authorised representative established in the EU |

### Systemic Risk GPAI Models (Art. 51, 55)

A GPAI model is classified as posing **systemic risk** if:

1. It has **high impact capabilities** evaluated based on appropriate technical tools and methodologies (including benchmarks and evaluations)
2. An AI Office decision designates it based on the above, or
3. It was trained with a cumulative compute of more than **10^25 FLOPs** (presumption, rebuttable)

**Additional obligations for systemic risk models (Art. 55):**

| Obligation | Detail |
|-----------|--------|
| **Model evaluation** | Perform standardized model evaluation, including adversarial testing |
| **Red-teaming** | Conduct adversarial red-teaming proportionate to risk level |
| **Systemic risk assessment** | Assess and mitigate possible systemic risks at EU level, including their sources |
| **Track and report incidents** | Track, document, and report serious incidents and possible corrective measures to the AI Office and relevant national authorities |
| **Cybersecurity** | Ensure adequate level of cybersecurity protection for the model and its physical infrastructure |
| **Energy reporting** | Report energy consumption of the model and, where technically feasible, its overall energy efficiency |

### Technical Documentation for GPAI (Annex XI)

Must include:

- Name and version of the model
- Description of the model and its elements (architecture, number of parameters, modalities)
- Description of training and data processing (training methodologies, data sources, data cleaning techniques, type and provenance of data, volume of data)
- Computational resources used (compute used for training — in FLOPs, training time, other relevant details)
- Known or estimated energy consumption for training and inference
- Key design choices including rationale and assumptions
- Description of evaluation procedures, results, and limitations
- Description of measures taken to mitigate identified risks
- Description of post-market monitoring

---

## Penalties

### Art. 99 — Administrative Fines

| Violation Type | Maximum Fine | % of Global Annual Turnover |
|---------------|-------------|----------------------------|
| **Prohibited AI practices** (Art. 5) | **€35 million** | **7%** (whichever is higher) |
| **High-risk AI system violations** (non-compliance with obligations) | **€15 million** | **3%** (whichever is higher) |
| **Incorrect, incomplete, or misleading information** to notified bodies or authorities | **€7.5 million** | **1%** (whichever is higher) |

### Special Provisions

- For **SMEs and startups**, fines are proportionate — the lower of the two amounts (absolute or percentage) applies
- For **Union institutions, agencies, and bodies**, the maximum fine is €1.5 million (prohibited practices) or €750,000 (other violations)
- Each member state lays down rules on other penalties (including non-monetary sanctions)
- Penalties must be effective, proportionate, and dissuasive

---

## Implementation Timeline

| Date | Milestone | Key Requirements |
|------|-----------|-----------------|
| **1 Aug 2024** | Entry into force | Regulation published and takes legal effect |
| **2 Feb 2025** | Prohibited practices + AI literacy | Art. 5 prohibitions apply; Art. 4 AI literacy requirements apply |
| **2 Aug 2025** | GPAI obligations + governance | GPAI model obligations (Art. 53, 55) apply; AI Office and governance structure operational; notified body designation rules apply; penalties for GPAI non-compliance apply |
| **2 Aug 2026** | **Full application** | All remaining provisions apply — high-risk obligations, deployer obligations, transparency obligations, conformity assessment, CE marking, market surveillance, penalties for all categories |
| **2 Aug 2027** | Extended deadline for certain high-risk | High-risk AI systems that are safety components of products covered by Annex I Section B (e.g., certain machinery, toys, lifts, equipment in explosive atmospheres) |

### Critical Dates for Organizations

| Action | Recommended Completion |
|--------|----------------------|
| AI system inventory | By Q2 2025 |
| Risk classification of all AI systems | By Q4 2025 |
| Prohibited practice elimination | By Jan 2025 |
| GPAI compliance (if applicable) | By Jul 2025 |
| High-risk compliance program launch | By Q1 2026 |
| Full high-risk compliance | By Jul 2026 |
| Conformity assessment completion | By Jul 2026 |
| CE marking affixed | By Jul 2026 |
| Post-market monitoring operational | By Jul 2026 |

---

## AI Literacy Requirements

### Art. 4 — AI Literacy

**Effective from 2 February 2025.**

Providers and deployers must take measures to ensure, to their best extent, a **sufficient level of AI literacy** of their staff and other persons dealing with the operation and use of AI systems on their behalf.

**Factors to consider when designing AI literacy measures:**
- Technical knowledge, experience, education, and training of the staff
- Context in which the AI systems are to be used
- Persons or groups of persons on whom the AI systems are to be used

### Recommended AI Literacy Program

1. **Awareness training** — What the AI Act requires, risk categories, obligations
2. **Role-based training** — Specific obligations for providers, deployers, data scientists, managers
3. **Technical training** — System-specific capabilities, limitations, and oversight procedures
4. **Ethics training** — Fundamental rights, bias awareness, responsible AI principles
5. **Ongoing education** — Regular updates as guidance, standards, and best practices evolve

---

## AI System Inventory and Classification Workflow

### Step 1: Inventory All AI Systems

For each AI system in your organization, document:

| Field | Description |
|-------|-------------|
| System name | Unique identifier |
| Provider / Developer | Internal team or external vendor |
| Description | What the system does and how it works |
| Technology | ML model type, training approach, data modalities |
| Intended purpose | Specific use case and context |
| Deployment status | Development / Testing / Production / Retired |
| Users | Internal staff / External end-users / Both |
| Affected persons | Who is subject to the system's decisions |
| Geographic scope | EU / EEA deployment presence |
| Data processed | Types of data (personal, special category, non-personal) |
| Decision impact | Advisory / Automated with human review / Fully automated |
| Integration points | Connected systems and data flows |

### Step 2: Classify Each System

Apply the classification decision tree:

```
1. Does the system meet the Art. 3(1) definition of an AI system?
   ├── NO → Not in scope. Document exclusion rationale.
   └── YES
       2. Does the system fall under a prohibited practice (Art. 5)?
          ├── YES → UNACCEPTABLE RISK — must be discontinued
          └── NO
              3. Is it a safety component of an Annex I product?
                 ├── YES → HIGH-RISK (product legislation path)
                 └── NO
                     4. Does it fall under an Annex III category?
                        ├── YES → Apply Art. 6(3) exception analysis
                        │   ├── Exception applies → LIMITED/MINIMAL RISK (document rationale)
                        │   └── Exception does NOT apply → HIGH-RISK
                        └── NO
                            5. Does Art. 50 transparency obligation apply?
                               ├── YES → LIMITED RISK
                               └── NO → MINIMAL RISK
```

### Step 3: Map Obligations

Based on classification, map applicable obligations and assign owners.

### Step 4: Gap Analysis

Run the compliance checker tool (`scripts/ai_compliance_checker.py`) to identify gaps.

### Step 5: Remediation Planning

Prioritize gaps by:
1. Deadline urgency (earliest applicable date)
2. Penalty severity (prohibited practices first)
3. Number of affected persons
4. Availability of compliance measures

---

## Conformity Assessment Workflow

### Internal Control (Annex VI)

For high-risk AI systems where internal control is sufficient:

```
1. PREPARATION
   ├── Establish QMS (Art. 17)
   ├── Compile technical documentation (Art. 11)
   └── Implement all Chapter III Section 2 requirements

2. INTERNAL ASSESSMENT
   ├── Verify risk management system addresses all identified risks
   ├── Verify data governance meets Art. 10 requirements
   ├── Verify technical documentation is complete and current
   ├── Verify logging capability meets Art. 12
   ├── Verify transparency and instructions for use (Art. 13)
   ├── Verify human oversight design (Art. 14)
   ├── Verify accuracy, robustness, cybersecurity (Art. 15)
   └── Confirm QMS covers all required elements (Art. 17)

3. DECLARATION
   ├── Sign EU Declaration of Conformity (Art. 47)
   ├── Affix CE marking (Art. 48)
   └── Register in EU database (Art. 49)

4. POST-MARKET
   ├── Implement post-market monitoring (Art. 72)
   ├── Maintain documentation updates
   └── Report serious incidents (Art. 73)
```

### Third-Party Assessment (Annex VII)

For biometric identification systems and cases where harmonised standards are insufficient:

```
1. PREPARATION
   ├── All internal control steps
   └── Select and engage notified body

2. QUALITY MANAGEMENT SYSTEM ASSESSMENT
   ├── Notified body reviews QMS documentation
   ├── Assessment of QMS implementation
   ├── Notified body issues QMS certificate or requires corrective action
   └── Ongoing QMS surveillance (annual)

3. TECHNICAL DOCUMENTATION ASSESSMENT
   ├── Notified body reviews complete technical documentation
   ├── Assessment of system against requirements
   ├── Testing and evaluation as needed
   └── Notified body issues type-examination certificate or requires corrective action

4. DECLARATION AND MARKING
   ├── Sign EU Declaration of Conformity
   ├── Affix CE marking with notified body identification number
   └── Register in EU database

5. ONGOING
   ├── Notified body surveillance (periodic audits)
   ├── Inform notified body of significant changes
   └── Maintain all documentation
```

---

## Bias Detection and Fairness Testing Framework

### EU AI Act Requirements for Bias (Art. 10)

Data governance must include:

1. **Examination** of datasets for possible biases
2. **Detection** of biases likely to affect health, safety, or fundamental rights
3. **Mitigation** through appropriate measures (data augmentation, re-sampling, re-weighting)
4. **Special category data** processing only when strictly necessary for bias correction, with safeguards

### Bias Detection Framework

#### Demographic Representation Analysis

Check whether training/testing data adequately represents the population the system will be used on:

| Metric | Description | Threshold |
|--------|-------------|-----------|
| **Representation ratio** | Group proportion in data vs. population | 0.8 - 1.25 (within 20% of expected) |
| **Class imbalance ratio** | Ratio of smallest to largest group | > 0.5 (no group less than half the largest) |
| **Coverage** | Percentage of relevant demographic groups present | 100% of known groups |

#### Outcome Fairness Metrics

| Metric | Definition | Fairness Threshold |
|--------|-----------|-------------------|
| **Demographic parity** | P(positive outcome) is equal across groups | Within 80% (four-fifths rule) |
| **Equalized odds** | True positive and false positive rates equal across groups | Within 80% |
| **Predictive parity** | Positive predictive value equal across groups | Within 80% |
| **Calibration** | Predicted probabilities are accurate for all groups | Within 5 percentage points |

#### Bias Mitigation Strategies

| Strategy | Phase | Description |
|----------|-------|-------------|
| **Data augmentation** | Pre-processing | Generate synthetic data for underrepresented groups |
| **Re-sampling** | Pre-processing | Over-sample minority / under-sample majority |
| **Re-weighting** | Pre-processing | Assign higher weights to underrepresented samples |
| **Adversarial debiasing** | In-processing | Adversarial training to remove protected attribute signal |
| **Threshold adjustment** | Post-processing | Group-specific decision thresholds for equal outcomes |
| **Reject option classification** | Post-processing | Defer uncertain predictions near decision boundary |

### Bias Testing Workflow

```
1. DEFINE PROTECTED ATTRIBUTES
   └── Age, gender, ethnicity, disability, religion, etc.

2. ANALYSE DATA DISTRIBUTION
   └── Run ai_bias_detector.py on dataset statistics

3. EVALUATE OUTCOME FAIRNESS
   └── Calculate demographic parity, equalized odds, predictive parity

4. IDENTIFY PROXY VARIABLES
   └── Check for features correlated with protected attributes

5. IMPLEMENT MITIGATION
   └── Apply appropriate strategy based on findings

6. VALIDATE
   └── Re-run analysis to confirm improvement

7. DOCUMENT
   └── Record all findings, measures taken, and residual bias levels
```

---

## AI Model Documentation Templates

### Template 1: AI System Description

```
AI SYSTEM DESCRIPTION
=====================
System Name:
Version:
Provider:
Date:

1. GENERAL INFORMATION
   - Intended purpose:
   - Target users (deployers):
   - Affected persons:
   - Geographic scope:

2. TECHNICAL ARCHITECTURE
   - Model type:
   - Input data modalities:
   - Output description:
   - Key design choices and rationale:

3. TRAINING AND DATA
   - Training data sources:
   - Data volume and characteristics:
   - Data preparation methods:
   - Bias examination results:

4. PERFORMANCE
   - Accuracy metrics:
   - Robustness testing results:
   - Known limitations:
   - Performance across demographic groups:

5. RISK CLASSIFICATION
   - AI Act classification:
   - Annex III category (if applicable):
   - Justification:
```

### Template 2: Risk Management Documentation

```
RISK MANAGEMENT SYSTEM — AI SYSTEM
===================================
System Name:
Version:
Risk Management Lead:
Date:

1. SCOPE AND OBJECTIVES
   - System boundaries:
   - Risk management lifecycle coverage:

2. RISK IDENTIFICATION
   | Risk ID | Description | Likelihood | Severity | Risk Level |
   |---------|-------------|------------|----------|------------|
   |         |             |            |          |            |

3. RISK EVALUATION
   - Acceptability criteria:
   - Evaluation results:

4. RISK CONTROL MEASURES
   | Risk ID | Measure | Type | Verification | Status |
   |---------|---------|------|-------------|--------|
   |         |         |      |             |        |

5. RESIDUAL RISK ASSESSMENT
   - Residual risk determination:
   - Overall risk-benefit analysis:

6. REVIEW AND UPDATE
   - Review frequency:
   - Trigger conditions for update:
   - Post-market data integration:
```

### Template 3: Human Oversight Procedure

```
HUMAN OVERSIGHT PROCEDURE
=========================
System Name:
Oversight Level: [Human-in-the-loop / Human-on-the-loop / Human-in-command]
Date:

1. OVERSIGHT PERSONNEL
   - Roles and responsibilities:
   - Required competencies:
   - Training requirements:
   - Authority level:

2. MONITORING PROCEDURES
   - Dashboard / interface description:
   - Key indicators monitored:
   - Alert conditions:
   - Review frequency:

3. INTERVENTION PROCEDURES
   - Override mechanism:
   - Escalation path:
   - Stop/shutdown procedure:
   - Decision reversal process:

4. AUTOMATION BIAS SAFEGUARDS
   - Measures implemented:
   - Verification requirements before acting on AI output:
   - Rotation / break requirements:

5. RECORD-KEEPING
   - Logging of oversight actions:
   - Incident documentation:
   - Regular reporting:
```

---

## Reference Documentation

| Document | Path | Description |
|----------|------|-------------|
| Classification Guide | `references/ai-act-classification-guide.md` | Complete Annex III categories, decision trees, prohibited practices, GPAI classification |
| Governance Framework | `references/ai-governance-framework.md` | Organizational structure, ethics board, model lifecycle, conformity assessment procedures |
| Documentation Templates | `references/ai-technical-documentation-templates.md` | Full templates for AI system description, risk management, data governance, testing, human oversight, post-market monitoring, incident reporting, FRIA |

---

## Tools

### AI Risk Classifier

Classifies an AI system into EU AI Act risk categories based on a JSON description and generates a compliance checklist.

```bash
# Classify from JSON file
python scripts/ai_risk_classifier.py --input system_description.json

# Classify from inline JSON
python scripts/ai_risk_classifier.py --inline '{
  "name": "Resume Screener",
  "description": "AI system that screens job applications and ranks candidates",
  "domain": "employment",
  "uses_biometrics": false,
  "decision_type": "automated_with_review",
  "affected_persons": "job applicants",
  "eu_deployment": true
}'

# Output as JSON
python scripts/ai_risk_classifier.py --input system.json --json
```

### AI Compliance Checker

Validates compliance status against all provider and deployer obligations, generates gap analysis, and scores readiness.

```bash
# Check compliance from JSON config
python scripts/ai_compliance_checker.py --input compliance_status.json

# Output as JSON with remediation steps
python scripts/ai_compliance_checker.py --input compliance_status.json --json

# Check deployer obligations only
python scripts/ai_compliance_checker.py --input compliance_status.json --role deployer
```

### AI Bias Detector

Analyzes dataset statistics for bias indicators and generates fairness assessment mapped to Art. 10 requirements.

```bash
# Analyze dataset statistics
python scripts/ai_bias_detector.py --input dataset_stats.json

# Output as JSON
python scripts/ai_bias_detector.py --input dataset_stats.json --json

# Specify protected attributes
python scripts/ai_bias_detector.py --input dataset_stats.json --protected-attributes gender,age_group,ethnicity
```

---

**Regulation Reference:** Regulation (EU) 2024/1689 of the European Parliament and of the Council of 13 June 2024 laying down harmonised rules on artificial intelligence (Artificial Intelligence Act)

**Last Updated:** March 2026
**Version:** 1.0.0
**Status:** Production-ready
