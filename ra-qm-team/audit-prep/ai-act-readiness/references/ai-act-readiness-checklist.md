# EU AI Act Readiness Checklist

Detailed punch list per AI Act requirement. For each item: applicability, evidence required, common gap.

---

## Step 1: System classification

Before any other readiness work, classify each AI system.

### Classification decision tree

```
Does the system fall in Annex I prohibited list?
├── Yes → CANNOT DEPLOY
└── No → continue

Does it fit Annex III high-risk list?
├── Yes → high-risk obligations
└── No → continue

Is it a general-purpose AI (GPAI) model?
├── Yes → GPAI provider obligations
└── No → continue

Is there a transparency obligation (interacts with humans, generates content, emotion recognition, biometric categorization)?
├── Yes → limited-risk obligations
└── No → minimal-risk (voluntary code of conduct)
```

### Annex III high-risk areas (8 categories)

1. Biometric identification (real-time + post-event)
2. Critical infrastructure (transport, water, energy)
3. Education and vocational training (admissions, evaluations)
4. Employment (recruitment, evaluation, work allocation)
5. Access to essential services (creditworthiness, eligibility for benefits)
6. Law enforcement (risk assessment, evidence analysis)
7. Migration, asylum, border control
8. Administration of justice and democratic processes

If your system is in any of these AND used in EU OR affecting EU persons, high-risk obligations apply.

---

## High-risk system requirements (Articles 9-15)

### Article 9 — Risk Management

| Item | Evidence | Common gap |
|------|----------|------------|
| Risk management system established | Documented procedure | Ad-hoc only |
| Risk identification continuous | Risk register with updates | One-time list |
| Estimation + evaluation of foreseeable risks | Per-risk assessment | Symptoms, not root causes |
| Mitigation measures | Per-risk mitigation | Mitigations identified; not implemented |
| Testing against mitigations | Test results | Mitigations claimed; not tested |
| Post-market integration | Feedback loop | Risk management stops at deployment |

### Article 10 — Data Governance

| Item | Evidence | Common gap |
|------|----------|------------|
| Training, validation, test data governance | Data documentation | Generic; not AI-system-specific |
| Data quality criteria | Quality metrics | Not measured |
| Representativeness analysis | Demographic + characteristic breakdown | Not analyzed |
| Bias examination | Bias testing report | Not performed |
| Data sources documented | Per-dataset documentation | Source vague |
| Data collection processes | Process documentation | Ad-hoc |
| Data preparation steps | Per-dataset preparation | Not documented |

### Article 11 — Technical Documentation

| Item | Evidence (per Annex IV) | Common gap |
|------|--------|------------|
| General description of system | Document section | Out-of-date |
| Detailed description of system elements | Architecture diagrams | Not maintained |
| Algorithms / models used | Model card | Generic |
| Computational resources | Specifications | Not documented |
| Validation procedures | Per-procedure documentation | V&V skipped |
| Quality management system | QMS documentation | Not formalized |

### Article 12 — Record-keeping (Logging)

| Item | Evidence | Common gap |
|------|----------|------------|
| Automatic logging of events | Log retention proof | Logs not enabled |
| Reference period of records | Logs retained X period | Too short |
| Verification of logging functionality | Log audit | Logs disabled in production |
| Access to logs for authorities | Access procedure | Not established |

### Article 13 — Transparency to Deployers

| Item | Evidence | Common gap |
|------|----------|------------|
| Instructions for use | Per-system instructions | Generic, not actionable |
| Performance characteristics | Documented performance | Marketing claims, not measured |
| Limitations | Documented limitations | Hidden / understated |
| Inputs / outputs expected | Specification | Vague |
| Categories of natural persons affected | Documented | Missing |

### Article 14 — Human Oversight

| Item | Evidence | Common gap |
|------|----------|------------|
| Oversight measures designed | Per-deployment design | Theater oversight (button that doesn't work) |
| Oversight personnel competent | Training records | Untrained users |
| System interpretable | Explainability mechanism | Black-box |
| Intervention capability | Tested intervention | Never tested |
| Stop mechanism | Tested stop | Not tested |

### Article 15 — Accuracy, Robustness, Cybersecurity

| Item | Evidence | Common gap |
|------|----------|------------|
| Accuracy metrics declared | Performance benchmark | Not declared |
| Robustness to adversarial inputs | Adversarial testing report | Not tested |
| Cybersecurity controls | Security documentation | Generic IT security, not AI-specific |
| Resilience to data poisoning | Per-training-cycle | Not assessed |

---

## Quality Management System (Article 17)

| Item | Evidence | Common gap |
|------|----------|------------|
| QMS documented | QMS manual / procedures | Not formalized for AI |
| Compliance strategy | Documented | Implicit only |
| Techniques + procedures for development | Per development stage | Not documented |
| Testing strategy | Per system | Ad-hoc |
| Resource management | Documented | Reactive |
| Communication procedures | Internal + external | Informal |

---

## Conformity Assessment (Article 43, Annex VII)

Two paths for high-risk systems:

| Path | When |
|------|------|
| **Internal control** (Annex VI) | For systems based on harmonized standards or common specifications; many systems |
| **Third-party (notified body)** (Annex VII) | For biometric ID; some safety-critical; voluntary for others |

### Pre-assessment readiness

- Technical documentation complete
- QMS documented and operating
- Conformity assessment procedure followed
- Internal records ready
- Self-declaration drafted (for internal control path)
- Notified body engaged (for third-party path)

### Post-assessment

- EU Declaration of Conformity signed
- CE marking applied (where applicable)
- Registration in EU database (Article 71)

---

## Post-Market Monitoring (Article 72)

| Item | Evidence | Common gap |
|------|----------|------------|
| Post-market monitoring plan | Documented plan | Not documented |
| Active monitoring | Monitoring tool / process | Reactive only |
| Performance drift detection | Metrics + alerts | Not measured |
| Issue tracking | Issue log | Issues not tracked |
| Periodic reviews | Quarterly minimum | Skipped |

---

## Serious Incident Reporting (Article 73)

| Item | Evidence | Common gap |
|------|----------|------------|
| Process for identifying serious incidents | Procedure | Not defined |
| Reporting capability (15 days serious, 2 days widespread / death) | Communication channel | Not tested |
| Past-period incidents documented | Incident log | Not maintained |

---

## AI Literacy (Article 4)

Effective Feb 2025; mandatory.

| Item | Evidence | Common gap |
|------|----------|------------|
| AI literacy of personnel | Training records | Not provided |
| Different roles, different training | Role-based content | Generic only |
| Refresh on changes | Periodic refresher | One-time |

---

## Limited-risk (transparency) obligations (Article 50)

For:
- Chatbots / AI interacting with humans → disclose to user
- Deepfakes → disclose as AI-generated
- Emotion recognition / biometric categorization → inform users
- AI-generated content (text, image, audio, video) → machine-readable mark + disclosure

| Item | Evidence | Common gap |
|------|----------|------------|
| Disclosure to user | UI evidence | Hidden / unclear |
| Machine-readable marking (synthetic content) | Implementation | Not implemented |
| Clear and visible | Design review | Buried in terms |

---

## EU Database Registration (Article 71)

For high-risk systems before placing on market:
- Provider registered
- System registered with technical details
- Updates within 30 days of changes

---

## Cheat sheet

| Question | Answer |
|----------|--------|
| First step? | Classify the system (Annex III check) |
| When is the deadline? | High-risk: 2 Dec 2027 (Annex III), 2 Aug 2028 (Annex I); transparency: 2 Aug 2026; GPAI: 2 Aug 2025 |
| Notified body required? | For biometric ID; voluntary for most others (use internal control) |
| What's most overlooked? | Article 4 AI literacy training; Article 50 user disclosure |
| Risk management timing? | Continuous; not one-time |
| Most common misclassification? | Treating system as limited-risk when in Annex III scope |
| AI Act vs GDPR? | Both apply; GDPR governs personal data; AI Act governs the AI system |
| AI Act vs ISO 42001? | AI Act is regulation; ISO 42001 is voluntary standard for AI management system |
