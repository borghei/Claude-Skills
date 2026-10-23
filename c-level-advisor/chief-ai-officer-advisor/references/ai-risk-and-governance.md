# AI Risk & Governance Reference

Practical reference for setting up an AI governance program and the
underlying risk taxonomy. Maps to NIST AI RMF 1.0, ISO/IEC 42001:2023
(AIMS), the EU AI Act, and adjacent expectations from financial-services
model risk management (SR 11-7) and FDA AI/ML guidance.

## 1. Frameworks at a glance

| Framework | Scope | What it cares about |
|-----------|-------|---------------------|
| NIST AI RMF 1.0 | Voluntary, US-origin, sector-agnostic | Govern / Map / Measure / Manage outcomes |
| ISO/IEC 42001:2023 (AIMS) | Certifiable AI management system | Org-level processes, policies, controls |
| EU AI Act | Mandatory in EU, extraterritorial | Risk tiers, conformity, post-market monitoring |
| SR 11-7 (US Fed) | Banks, model risk management | Model lifecycle, validation, documentation |
| FDA AI/ML guidance | Medical software | Predetermined change control, real-world performance |
| ISO/IEC 23894 | Risk management for AI | Risk-management process detail |
| ISO/IEC 5338 | AI system lifecycle | Lifecycle stages and activities |

If you operate across multiple regions, build your control set around
**ISO 42001 + NIST AI RMF**, then layer EU AI Act + sector regs on top.

## 2. NIST AI RMF — 4 core functions

The RMF organizes activities into four functions. A useful checklist:

### Govern
- Risk management roles and accountabilities are defined and resourced.
- Policies are published, signed, and communicated.
- Workforce has appropriate AI literacy for their role.
- Incident reporting and review processes exist.
- Third-party AI relationships are governed.

### Map
- Context for each AI system (purpose, users, deployment setting) is documented.
- Categorization of risk is performed at system intake.
- Impact assessment considers individuals, groups, and society.
- Tradeoffs between accuracy and other values are documented.

### Measure
- Quantitative and qualitative metrics are defined per system.
- Pre-deployment testing (eval) is performed against documented criteria.
- Tracking of performance, fairness, and robustness post-deployment.
- Independent review for high-risk systems.

### Manage
- Risk responses are prioritized and assigned.
- Continuous monitoring detects drift and degradation.
- A documented decommissioning process exists.
- Mechanisms for human override, escalation, and incident response are tested.

## 3. ISO/IEC 42001 — AIMS minimum viable program

A pragmatic ISO 42001 implementation (12-week sprint pattern):

| Week | Workstream | Deliverable |
|------|-----------|-------------|
| 1–2 | Scope + context | AIMS scope statement, interested parties register |
| 3–4 | Policy + leadership | AI policy, roles + responsibilities (RACI) |
| 5–6 | Risk + impact | Risk register, AI impact assessment template, AIIAs for top systems |
| 7–8 | Controls (Annex A) | Statement of applicability across Annex A controls |
| 9–10 | Operations | Operating procedures: change management, supplier management, incident response |
| 11 | Internal audit | First internal audit pass, NCs logged |
| 12 | Management review | Management-review record, corrective actions, certification readiness |

See `ra-qm-team/audit-prep/aims-audit` for the deeper audit-prep playbook.

## 4. EU AI Act — risk tiers and obligations

### Risk tiers

| Tier | Examples | Status |
|------|----------|--------|
| Unacceptable risk | Social scoring, real-time biometric ID in public (with narrow exceptions), manipulative AI | Prohibited |
| High-risk | Annex III categories (employment screening, credit scoring, critical infra, law enforcement, education, medical devices) | Heavy obligations |
| Limited risk | Chatbots, deepfakes | Transparency obligations |
| Minimal risk | Spam filters, video game AI | Voluntary codes of conduct |
| GPAI (general-purpose AI) | Foundation models | Provider obligations; systemic-risk tier adds extra |

### High-risk obligations (Title III, Chapter 2)

A high-risk system requires:

1. **Risk management system** (continuous, throughout lifecycle)
2. **Data and data governance** (representative, relevant, free of errors)
3. **Technical documentation** (Annex IV content)
4. **Record-keeping** (automatic logs of operation)
5. **Transparency and user information**
6. **Human oversight**
7. **Accuracy, robustness, and cybersecurity**
8. **Conformity assessment** before placing on the market
9. **EU declaration of conformity + CE marking**
10. **Post-market monitoring** (Article 72)
11. **Serious incident reporting** (Article 73) — typically 15 days; immediate for fundamental rights breaches or critical infra

### Timeline checkpoints (as amended by the Digital Omnibus, Regulation (EU) 2026/1744)

- 1 Aug 2024 — Act enters into force
- 2 Feb 2025 — Prohibitions on unacceptable-risk practices apply
- 2 Aug 2025 — GPAI obligations apply; governance bodies operational
- 2 Aug 2026 — Article 50 transparency obligations apply
- 2 Dec 2027 — High-risk obligations for Annex III systems apply (moved from 2 Aug 2026)
- 2 Aug 2028 — High-risk obligations for AI in products under EU product-safety law apply (moved from 2 Aug 2027)

Check the [Official Journal text](https://eur-lex.europa.eu/eli/reg/2026/1744/oj) before relying on a date.

## 5. AI Impact Assessment (AIIA) — what to include

Whether you call it AIIA, AI risk assessment, FRIA (Fundamental Rights
Impact Assessment), or model card, a credible assessment includes:

1. **Purpose and deployment context** — who uses it, where, why, with what
2. **Data lineage** — sources, consent, licensing, sensitivity, sovereignty
3. **Modeling approach** — model family, training process, eval methodology
4. **Performance** — headline metrics + subgroup performance + failure modes
5. **Risk identification** — what could go wrong (taxonomy in §6)
6. **Mitigations** — controls in place to reduce each risk
7. **Residual risk** — what remains after mitigations; explicit acceptance
8. **Human oversight** — review/override/escalation paths
9. **Monitoring plan** — what gets watched, with what threshold, by whom
10. **Decommissioning** — when do we kill it; what's the rollback

For high-risk systems, an AIIA is non-negotiable. For low-risk internal
productivity tools, a one-page summary is usually enough.

## 6. AI risk taxonomy (use this for the register)

Group risks for easier tracking. The taxonomy below is a pragmatic
union of NIST, ISO, and common red-teaming categories.

### Model risk
- Inaccuracy / hallucination
- Bias and unfair subgroup performance
- Distribution shift / drift
- Adversarial robustness (input perturbations, jailbreaks)
- Reproducibility and versioning failures

### Data risk
- Data quality (missing, stale, biased)
- Data lineage gaps (can't prove provenance)
- Data leakage (training data exposed in outputs)
- Sensitive data in training without consent
- Cross-border data transfer issues

### Security risk
- Prompt injection (direct and indirect)
- Data exfiltration via the model
- Model theft / weight extraction
- Supply chain (compromised model from a hub)
- Insecure agent tool use

### Privacy risk
- Re-identification of training subjects
- Membership inference attacks
- PII in inputs being logged
- Disclosure of business-confidential info to third-party LLM

### Operational risk
- Vendor lock-in / single foundation-model dependency
- Cost runaway (token explosion, agent loops)
- Latency / availability regressions
- Capability concentration in a single team

### Compliance risk
- EU AI Act / sector regulation non-compliance
- Failure to meet contractual AI/data terms
- IP risk (training on copyrighted content, model output IP ownership)
- Mandatory disclosure obligations missed

### Reputational and human-rights risk
- Harmful or offensive outputs
- Discrimination, disparate impact
- Lack of transparency to users
- Misuse / dual-use

## 7. AI governance committee structure

A two-tier structure works for most companies past the early stage.

### Tier 1 — AI Council (executive)
- **Members:** CEO chair, CAIO sponsor, CTO, CISO, CFO, GC, business-line heads
- **Cadence:** monthly or quarterly
- **Mandate:** strategy approval, budget, principles, top-risk acceptance
- **Out of scope:** technical architecture decisions

### Tier 2 — Model Risk / Technical Review Board
- **Members:** CAIO chair, head of ML/data, head of security, privacy lead, product reps
- **Cadence:** biweekly or weekly
- **Mandate:** approve new models, review eval results, accept residual risk
- **Authority:** can require additional eval; can block deployment; can require fallback

Plus working groups as needed: red team, AI policy, vendor management.

## 8. Model approval workflow

A clean approval workflow (target: ≤2 weeks for low/medium risk):

```
Intake → Risk classification → Eval design → Eval execution
       → Risk review → Approval / Conditional / Reject → Deployment gate
       → Post-deployment monitoring → Quarterly review
```

Approval decisions are recorded in the **model registry** with:
- Model card / fact sheet
- Eval results vs published threshold
- Residual risks and acceptance
- Approver(s) and date
- Review trigger conditions (drift, new use case, new regulation)

## 9. AI incident response

AI incidents are different enough from generic security incidents to deserve
their own playbook.

### Detection triggers
- Eval pass rate drops below threshold
- User-reported harmful output above noise floor
- Drift detector fires on input distribution
- External disclosure (researcher, customer, regulator)
- Cost or latency anomaly

### Response steps
1. **Contain** — disable the model or feature behind a feature flag
2. **Triage** — severity (S1–S4), data-subject impact, regulatory implication
3. **Investigate** — pull logs, reproduce, identify root cause (data, model, prompt, integration)
4. **Notify** — internal (exec, GC, CISO), customer (if contractually required), regulator (if applicable)
5. **Remediate** — fix and re-eval, then re-enable
6. **Post-mortem** — within 5 business days; publish to the AI council

### Regulatory clocks
- EU AI Act Article 73: serious incidents — 15 days (immediate for fundamental rights / critical infra)
- GDPR Article 33: personal data breach — 72 hours to supervisory authority
- Sector-specific (FDA, EMA, banking) — varies; pre-publish your matrix

## 10. Vendor and third-party AI governance

Most AI risk now arrives via vendors. Govern accordingly.

### Vendor intake checklist
- Model provenance (base model, training data summary, evals)
- Data handling: do they train on your inputs/outputs? (default: no)
- Data residency: where are inputs processed and stored?
- Security: SOC 2 / ISO 27001; AI-specific controls
- Contract: indemnity for IP claims, audit rights, exit clause
- Incident notification SLA
- Roadmap visibility and deprecation notice period

### Foundation model contracts — must-haves
- No-training clause covering inputs and outputs
- Defined data residency and processing locations
- Indemnity for output IP claims
- 30-day deprecation notice for any model used in production
- Service credits or refunds for material SLA breaches
- Right to audit summarized governance evidence (or accept a third-party report)

## 11. Mapping table — controls across frameworks

| Control area | NIST AI RMF | ISO 42001 | EU AI Act |
|--------------|-------------|-----------|-----------|
| Governance | Govern 1-6 | Clauses 5, 9 | Art. 17 (QMS) |
| Risk assessment | Map 1-5 | Clauses 6.1, 8.2 | Art. 9 (RMS) |
| Data quality | Measure 2.1, 2.2 | Annex A.7 | Art. 10 |
| Documentation | Govern 1.3, Manage 4 | Clauses 7.5, 8.5 | Art. 11 + Annex IV |
| Human oversight | Manage 3.2 | Annex A.6.2.6 | Art. 14 |
| Robustness | Measure 2.5-2.7 | Annex A.6.2.4 | Art. 15 |
| Post-market monitoring | Manage 4.1 | Clause 9.1 | Art. 72 |
| Incident reporting | Manage 4.3 | Clause 10 | Art. 73 |

A control once, comply many times: design controls to satisfy the union,
not one framework at a time.

## 12. Common pitfalls

- **AI governance committee with no decision rights.** Either give it real authority over approvals and spend, or disband it.
- **Risk register that never gets updated.** Tie ownership to the model registry; review quarterly.
- **Approval workflow that becomes a tollbooth.** Publish SLAs; fast-path low-risk patterns.
- **AIIA template that's 40 pages.** No one fills it out. Keep it to 3–5 pages with deeper appendices.
- **Conflating safety with security.** They share tools but have different threat models and owners.
- **Outsourcing red-teaming once and calling it done.** Continuous adversarial testing should be part of the eval harness, not a one-time engagement.
