# EDPB Criteria for DPIA Threshold Assessment

Complete reference for the 9 EDPB criteria, Art. 35(3) mandatory triggers, two-criterion presumption rule, and multi-jurisdictional analysis.

---

## Table of Contents

- [Art. 35(3) Mandatory Triggers](#art-353-mandatory-triggers)
- [EDPB 9 Criteria](#edpb-9-criteria)
- [Two-Criterion Presumption Rule](#two-criterion-presumption-rule)
- [Criterion Detailed Analysis](#criterion-detailed-analysis)
- [Multi-Jurisdictional DPIA Analysis](#multi-jurisdictional-dpia-analysis)
- [National Blacklist Overview](#national-blacklist-overview)
- [Threshold Decision Matrix](#threshold-decision-matrix)

---

## Art. 35(3) Mandatory Triggers

These three triggers make a DPIA mandatory regardless of any other analysis. If any one is met, the DPIA must be conducted before processing begins.

| Trigger | Article | Description | Examples |
|---------|---------|-------------|----------|
| **(a) Automated decisions with legal effect** | Art. 35(3)(a) | Systematic and extensive evaluation of personal aspects based on automated processing, including profiling, on which decisions are based that produce legal effects concerning the natural person or similarly significantly affect them | Credit scoring, automated insurance pricing, automated recruitment screening, algorithmic content moderation affecting access to services |
| **(b) Large-scale special/criminal data** | Art. 35(3)(b) | Processing on a large scale of special categories of data referred to in Art. 9(1), or of personal data relating to criminal convictions and offences referred to in Art. 10 | Hospital patient record systems, national health registries, genetic testing services, large-scale biometric authentication, criminal background check databases |
| **(c) Systematic public area monitoring** | Art. 35(3)(c) | Systematic monitoring of a publicly accessible area on a large scale | City-wide CCTV systems, facial recognition in public spaces, Wi-Fi tracking in shopping centers, smart city sensor networks, body-worn cameras in public-facing roles |

**Key interpretation notes:**

- "Legal effect" includes denial of credit, employment decisions, social benefits determinations, and immigration decisions
- "Similarly significant effect" includes effects that influence circumstances, behavior, or choices and have a prolonged or permanent impact (WP 251 rev.01)
- "Large scale" has no fixed numeric threshold — assessed by number of data subjects, data volume, geographic extent, and duration (see Criterion 5 below)
- "Publicly accessible area" includes streets, shopping centers, parks, and any area generally open to the public regardless of ownership

---

## EDPB 9 Criteria

Source: EDPB (formerly WP29) Guidelines on Data Protection Impact Assessment, WP 248 rev.01.

| # | Criterion | Description |
|---|-----------|-------------|
| 1 | Evaluation or scoring | Profiling and predicting, especially concerning data subjects' performance at work, economic situation, health, personal preferences, interests, reliability, behavior, location, or movements |
| 2 | Automated decision-making with legal/significant effect | Processing aimed at taking decisions on data subjects producing legal effects or similarly significantly affecting them |
| 3 | Systematic monitoring | Processing used to observe, monitor, or control data subjects, including data collected through networks or systematic monitoring of publicly accessible areas |
| 4 | Sensitive data or highly personal data | Processing of special categories (Art. 9), criminal data (Art. 10), or data considered highly personal (financial, location, communications, browsing) |
| 5 | Large scale processing | Assessed by: number of data subjects, volume of data items, geographic extent, duration or permanence of processing |
| 6 | Matching or combining datasets | Combining datasets from different processing operations or different controllers in a way that would exceed data subjects' reasonable expectations |
| 7 | Vulnerable data subjects | Data concerning persons where there is an imbalance of power: children, employees, patients, elderly, mentally ill, asylum seekers |
| 8 | Innovative technology | Use of novel technology including AI, machine learning, IoT, biometrics, blockchain, deep fakes, autonomous vehicles |
| 9 | Preventing exercise of right or service | Processing that prevents data subjects from exercising a right, using a service, or entering into a contract |

---

## Two-Criterion Presumption Rule

Per WP 248 rev.01, paragraph II.C:

> "In most cases, a data controller can consider that a processing meeting two criteria would require a DPIA to be carried out. In general, the WP29 considers that the more criteria are met by the processing, the more likely it is to present a high risk to the rights and freedoms of data subjects, and therefore to require a DPIA, regardless of the measures which the controller envisages to adopt."

### Decision Logic

| Criteria Met | Verdict | Action Required |
|-------------|---------|-----------------|
| 0 | Not Required | Document threshold assessment |
| 1 | Recommended | DPIA recommended as good practice; document rationale if not conducting |
| 2 | Presumptively Required | DPIA required unless controller can document why processing does not result in high risk |
| 3+ | Required | DPIA required; multiple criteria indicate elevated risk profile |

### Rebutting the Presumption

The two-criterion presumption can be rebutted, but:

- The controller must **document specific reasons** why the processing does not result in high risk despite meeting two or more criteria
- The documentation must be **available to the supervisory authority** upon request
- Supervisory authorities may **challenge the rebuttal** and require a DPIA anyway
- In practice, rebutting the presumption is **rarely advisable** — conducting the DPIA is usually less effort than documenting and defending a rebuttal

---

## Criterion Detailed Analysis

### Criterion 1: Evaluation or Scoring

| Indicator | Weight | Examples |
|-----------|--------|---------|
| Profiling based on behavior | High | User behavior tracking for ad targeting, content recommendation |
| Credit or financial scoring | High | Credit score calculation, fraud detection scoring |
| Performance evaluation | Medium | Employee performance algorithms, student assessment tools |
| Health risk prediction | High | Predictive health analytics, insurance risk scoring |
| Location-based profiling | Medium | Movement pattern analysis, geofencing-based profiles |
| Personality assessment | High | Psychometric testing, behavioral prediction models |

### Criterion 2: Automated Decision-Making

| Indicator | Weight | Examples |
|-----------|--------|---------|
| Automated approval/denial | High | Loan applications, insurance claims, visa processing |
| Service eligibility determination | High | Benefits eligibility, service tier assignment |
| Price personalization | Medium | Dynamic pricing based on personal data, insurance premium calculation |
| Content restriction | Medium | Age verification, content moderation, account suspension |
| Employment decisions | High | Automated CV screening, algorithmic scheduling, automated termination |

### Criterion 3: Systematic Monitoring

| Indicator | Weight | Examples |
|-----------|--------|---------|
| CCTV/video surveillance | High | Workplace cameras, retail analytics, public space monitoring |
| Online tracking | Medium | Cookie-based tracking, cross-site tracking, fingerprinting |
| Location tracking | High | GPS tracking of employees/vehicles, mobile app location services |
| Communication monitoring | High | Email monitoring, call recording, messaging surveillance |
| IoT sensor data collection | Medium | Smart home data, wearable devices, connected vehicle telemetry |

### Criterion 4: Sensitive or Highly Personal Data

| Data Type | Article Reference | Sensitivity |
|-----------|------------------|-------------|
| Health data | Art. 9(1) | Special category |
| Genetic data | Art. 9(1) | Special category |
| Biometric data (for identification) | Art. 9(1) | Special category |
| Racial or ethnic origin | Art. 9(1) | Special category |
| Political opinions | Art. 9(1) | Special category |
| Religious or philosophical beliefs | Art. 9(1) | Special category |
| Trade union membership | Art. 9(1) | Special category |
| Sex life or sexual orientation | Art. 9(1) | Special category |
| Criminal convictions/offences | Art. 10 | Restricted processing |
| Financial data | WP29 guidance | Highly personal |
| Location data | WP29 guidance | Highly personal |
| Communication content | WP29 guidance | Highly personal |

### Criterion 5: Large Scale — Four-Factor Test

| Factor | Assessment Questions | Examples |
|--------|---------------------|----------|
| **(a) Number of data subjects** | How many individuals are affected? Absolute number and proportion of relevant population | >10,000 data subjects typically qualifies; city-wide or regional scope |
| **(b) Volume of data** | How much data per subject? How many data items total? | Multiple data categories per subject; high granularity |
| **(c) Geographic extent** | Regional, national, international? Multiple jurisdictions? | Nationwide service; EU-wide processing; multi-country operations |
| **(d) Duration or permanence** | Ongoing or one-time? How long is data retained? | Continuous processing; long retention periods; permanent records |

**Note:** A single GP practice processing patient data is NOT large scale (Recital 91). A hospital system serving a region IS large scale. No fixed numeric threshold exists — all four factors must be considered together.

### Criterion 6: Matching or Combining

| Indicator | Weight | Examples |
|-----------|--------|---------|
| Cross-platform data combination | High | Combining social media data with purchase history |
| Third-party data enrichment | High | Augmenting customer records with data broker information |
| Multiple controller data sharing | Medium | Joint controllership combining datasets |
| Unexpected correlation | High | Combining datasets for purposes beyond original collection |

### Criterion 7: Vulnerable Data Subjects

| Vulnerable Group | Power Imbalance | Considerations |
|-----------------|-----------------|----------------|
| Children | Cannot validly consent (under 16, or national threshold) | Parental consent; age-appropriate design; best interests |
| Employees | Economic dependence on employer | Cannot freely consent in employment context (WP29); EDPB Guidelines 2/2023 |
| Patients | Dependent on healthcare providers | Difficulty withholding consent for treatment-linked processing |
| Elderly | Potential cognitive/technological barriers | Accessibility of information and consent mechanisms |
| Asylum seekers | Dependent on state authorities | Power imbalance with processing entity |
| Students | Dependent on educational institution | Institutional pressure to consent |

### Criterion 8: Innovative Technology

| Technology | Risk Factors | Assessment Notes |
|-----------|-------------|-----------------|
| AI/Machine Learning | Opacity, bias, unpredictability | Both training and inference phases; EDPB Opinion 28/2024 |
| Facial recognition | Biometric data, surveillance | Art. 9 special category when used for identification |
| IoT devices | Pervasive collection, limited control | Data minimization challenges; consent difficulties |
| Blockchain | Immutability conflicts with erasure right | Art. 17 tension; pseudonymization approaches |
| Generative AI | Training data provenance, output accuracy | Purpose limitation; accuracy principle; transparency |
| Deepfake technology | Identity, consent, accuracy | Potential for fraud, defamation, manipulation |

### Criterion 9: Preventing Exercise of Rights

| Scenario | Impact | Examples |
|----------|--------|---------|
| Mandatory processing for service access | Denies choice | "Accept tracking or no access" |
| Credit scoring affecting contracts | Financial exclusion | Loan denial based on automated scoring |
| Content filtering affecting expression | Rights limitation | Algorithmic content suppression |
| Access control based on biometrics | Physical access restriction | Biometric-only building entry |

---

## Multi-Jurisdictional DPIA Analysis

When processing spans multiple EU/EEA member states, the DPIA analysis must consider:

| Step | Action | Reference |
|------|--------|-----------|
| 1 | Identify all jurisdictions where data subjects are located | Art. 35(1) |
| 2 | Check Art. 35(3) triggers (universal — apply everywhere) | Art. 35(3) |
| 3 | Apply EDPB 9-criteria assessment | WP 248 rev.01 |
| 4 | Check each jurisdiction's national blacklist | Art. 35(4) |
| 5 | Check each jurisdiction's national whitelist | Art. 35(5) |
| 6 | Apply most restrictive requirement | Principle of highest protection |
| 7 | Document multi-jurisdictional analysis | Accountability principle |

**Lead supervisory authority:** Under the one-stop-shop mechanism (Art. 56), the lead SA for cross-border processing is the SA of the main establishment. However, DPIA obligations apply regardless of which SA is lead.

---

## National Blacklist Overview

Processing types requiring DPIA per national supervisory authority published lists (Art. 35(4)). This is non-exhaustive — always check current SA-published lists.

### Germany (DSK / State DPAs)

| Processing Type | Notes |
|----------------|-------|
| Processing of biometric data for identification in public spaces | Stricter than base GDPR |
| Profiling with risk of discrimination | Includes credit scoring |
| Processing employee data using AI | Specific to employment context |
| Large-scale processing of location data | Includes fleet tracking, app location |
| Automated analysis of audio/video recordings | CCTV analytics, call center monitoring |

### France (CNIL)

| Processing Type | Notes |
|----------------|-------|
| Health data processing for research | Even with pseudonymization |
| Biometric processing for access control | Workplace biometric systems |
| Genetic data processing | Any scale |
| Profiling with legal/significant effects | Broader than Art. 35(3)(a) |
| Processing of vulnerable persons' data at large scale | Includes social services |

### Ireland (DPC)

| Processing Type | Notes |
|----------------|-------|
| Processing involving innovative technology | Broad interpretation |
| Large-scale profiling | Lower threshold than some SAs |
| Processing preventing exercise of rights | Strict interpretation |
| Systematic monitoring of employees | Workplace surveillance |

### Belgium (APD/GBA)

| Processing Type | Notes |
|----------------|-------|
| Processing of biometric data | Any identification purpose |
| Processing of genetic data | Including research contexts |
| Processing for direct marketing based on profiling | Stricter than some SAs |
| Processing of judicial data on large scale | Broader than Art. 10 alone |

### Netherlands (AP)

| Processing Type | Notes |
|----------------|-------|
| Covert investigation or monitoring | Including fraud investigation |
| Blacklists or exclusion lists | Internal warning systems |
| Processing of financial data indicating financial status | Broader financial data scope |
| Biometric data for identification | Similar to DE |

### Italy (Garante)

| Processing Type | Notes |
|----------------|-------|
| Processing data for automated decisions including profiling | Broad scope |
| Processing genetic, biometric, health data on large scale | Lower threshold |
| Systematic monitoring of employees | Including productivity monitoring |
| Data collected via IoT applications | Smart devices, wearables |

### Poland (UODO)

| Processing Type | Notes |
|----------------|-------|
| Processing using biometric data | For identification or verification |
| Processing of genetic data | All contexts |
| Processing of location data | Including mobile tracking |
| Processing data for credit/insurance scoring | Explicit inclusion |

---

## Threshold Decision Matrix

Quick reference combining all trigger sources:

| Trigger Source | Threshold | Result if Met |
|---------------|-----------|---------------|
| Art. 35(3)(a) — automated decisions with legal effect | Any match | DPIA mandatory |
| Art. 35(3)(b) — large-scale special/criminal data | Any match | DPIA mandatory |
| Art. 35(3)(c) — systematic public area monitoring | Any match | DPIA mandatory |
| EDPB criteria — 2 or more met | 2+ of 9 | DPIA presumptively required |
| EDPB criteria — 1 met | 1 of 9 | DPIA recommended |
| National blacklist — processing type listed | Any match | DPIA mandatory per that SA |
| National whitelist — processing type listed | Any match | DPIA not required per that SA |
| None of the above | No matches | DPIA not required (document assessment) |

**Priority order:** Art. 35(3) > National blacklist > EDPB criteria > National whitelist. A whitelist entry cannot override an Art. 35(3) trigger.
