# Multi-Framework Readiness Matrix

Per-framework reference: scope, audit cadence, certification timing, typical cost, prerequisite frameworks, post-certification surveillance.

---

## SOC 2

| Aspect | Detail |
|--------|--------|
| Scope | Trust Services Criteria (Security mandatory; Availability, Confidentiality, Processing Integrity, Privacy optional) |
| Type I | Design of controls at point in time |
| Type II | Design + operating effectiveness over observation period (6-12 months) |
| Audit duration | 1-2 weeks audit week; 3-12 months observation for Type II |
| Initial cost | $20k-$60k Type I; $40k-$150k Type II |
| Annual cost | Audit + audit prep team time |
| Auditor | CPA firm with SOC 2 license (AICPA-accredited) |
| Output | SOC 2 report (Type I or Type II) |
| Renewal cadence | Annual (for Type II) |
| Effective standards | AICPA TSP (2017 + updates) |
| Use case | B2B customer requirement (most common entry point) |

---

## ISO 27001

| Aspect | Detail |
|--------|--------|
| Scope | Information Security Management System (ISMS) + Annex A controls |
| Stage 1 | Documentation review (1-3 days) |
| Stage 2 | Operational assessment (3-10 days onsite) |
| Initial cost | $30k-$100k (varies by org size + auditor) |
| Annual cost | Annual surveillance audits ($10k-$30k) |
| Auditor | Accredited certification body |
| Output | ISO 27001:2022 certificate (3-year validity) |
| Surveillance | Annual (Years 1+2); re-certification Year 3 |
| Effective standard | ISO 27001:2022 + ISO 27002:2022 controls |
| Use case | Global / international customer requirement; many EU/APAC customers prefer |

---

## NIST CSF

| Aspect | Detail |
|--------|--------|
| Scope | 6 functions (Govern + Identify + Protect + Detect + Respond + Recover) |
| Self-assessment | Most orgs use NIST CSF as internal framework; not certified |
| Optional 3rd party | NIST recommends but doesn't mandate 3rd-party assessment |
| Cost | Low (self-assessment); $20k-$100k for 3rd-party |
| Output | Maturity profile (Current + Target) |
| Use case | US federal customers; internal framework; aligns with US regs |
| Updates | NIST CSF 2.0 (Feb 2024) added Govern function |

---

## NIS2 (EU Directive)

| Aspect | Detail |
|--------|--------|
| Scope | EU member states; specific sectors (energy, banking, healthcare, digital infra, etc.) |
| Mandatory | Yes; effective Oct 2024 |
| Cost | Implementation cost; member states' competent authorities don't issue certificates |
| Output | Self-attestation; subject to enforcement by authorities |
| Penalty | Up to €10M or 2% of worldwide annual turnover |
| Coverage | Essential entities (high penalties) + Important entities |
| Use case | Mandatory for in-scope organizations operating in EU |

---

## DORA (EU Regulation)

| Aspect | Detail |
|--------|--------|
| Scope | EU financial services + ICT third-party providers |
| Mandatory | Yes; effective Jan 17, 2025 |
| 5 pillars | ICT risk management, incident reporting, resilience testing, third-party risk, information sharing |
| Cost | Implementation; ongoing operations + threat-led penetration testing for critical entities |
| Output | Compliance with regulatory technical standards (RTS) |
| Penalty | Up to 2% worldwide turnover (institutions) / €5M (ICT providers) |
| Use case | EU financial services + their ICT vendors |

---

## PCI-DSS

| Aspect | Detail |
|--------|--------|
| Scope | Cardholder data environment (CDE) |
| Levels | 1-4 (volume of card transactions) |
| L1 / L2 | Annual QSA audit ($50k-$300k) |
| L3 / L4 | SAQ (Self-Assessment Questionnaire) |
| Cost | High for L1; declining for L4 |
| Output | Report on Compliance (ROC) for L1; AOC for others |
| Validity | Annual |
| Use case | Anyone storing/processing/transmitting card data |

---

## GDPR

| Aspect | Detail |
|--------|--------|
| Scope | EU personal data; controller + processor obligations |
| Mandatory | Yes; effective 2018 |
| Self-attestation | No certification body; supervisory authority enforcement |
| Cost | Implementation; DPO if required; ongoing operations |
| Penalty | Up to €20M or 4% worldwide turnover |
| Output | DPIA + ROPA + privacy notices + DPA + breach process |
| Surveillance | Supervisory authority inquiries; customer DPA audits |
| Use case | Anyone processing EU personal data |

---

## HIPAA

| Aspect | Detail |
|--------|--------|
| Scope | US protected health information (PHI) |
| Applies to | Covered Entities (CEs) + Business Associates (BAs) |
| Mandatory | Yes for CEs/BAs |
| Self-attestation | No certification; HHS OCR enforces |
| Cost | Implementation; ongoing operations |
| Penalty | $100-$50k per violation; up to $1.5M per incident type per year |
| Output | Security risk assessment + safeguards + breach process |
| Surveillance | OCR investigations; customer (CE) audit of BAs |
| Use case | US healthcare; PHI processors |

---

## ISO 13485 / 14971 / MDR / FDA (Medical Devices)

| Aspect | Detail |
|--------|--------|
| Scope | Medical devices (manufacturing, design, distribution) |
| Standards | ISO 13485 (QMS), ISO 14971 (risk), MDR / FDA QSR (regulatory) |
| Mandatory | Yes for device manufacturers in respective markets |
| Initial cost | $100k-$1M+ (program build); $30k-$200k per audit |
| Output | Certificates + CE marking / FDA clearance / approval |
| Surveillance | Annual + per-product reviews |
| Use case | Medical device industry |

---

## ISO 42001 (AI Management System)

| Aspect | Detail |
|--------|--------|
| Scope | AI Management System (AIMS) |
| Stage 1 + 2 | Like ISO 27001 |
| Initial cost | $30k-$100k |
| Annual cost | Surveillance ($10k-$30k) |
| Output | ISO 42001:2023 certificate (3-year) |
| Use case | AI-developing organizations; emerging requirement |

---

## EU AI Act

| Aspect | Detail |
|--------|--------|
| Scope | AI systems used in EU OR affecting EU persons |
| Mandatory | Yes; phased timeline (Aug 2025 GPAI; Aug 2026 transparency; Dec 2027 / Aug 2028 high-risk) |
| Conformity assessment | Internal control (most) OR notified body (specific) |
| Cost | $30k-$200k+ (notified body); internal control lower |
| Output | EU Declaration of Conformity + CE marking + database registration |
| Use case | High-risk AI systems; GPAI providers |

---

## Cross-framework cost comparison (illustrative annual)

| Framework combo | Initial | Annual (steady-state) |
|-----------------|---------|----------------------|
| SOC 2 Type II only | $80k | $60k |
| SOC 2 + ISO 27001 | $160k | $90k (saves on overlap) |
| SOC 2 + ISO 27001 + NIST CSF | $180k | $100k |
| SOC 2 + ISO 27001 + HIPAA | $200k | $110k |
| SOC 2 + ISO 27001 + GDPR | $200k | $120k (GDPR ongoing) |
| SOC 2 + ISO 27001 + PCI-DSS L1 | $300k | $150k |
| Med-device: ISO 13485 + FDA QSR + MDR | $500k+ | $250k+ |

---

## Auditor coordination

### Same auditor for multiple frameworks

Some firms cover multiple frameworks (SOC 2 + ISO 27001 + PCI-DSS). Benefits:
- Single relationship
- Reduced briefing overhead
- Coordinated audit schedules

Drawbacks:
- Independence concerns (single firm too embedded)
- Concentration risk if firm has issues

### Different auditors

Different firms for different frameworks. Benefits:
- Specialization (PCI QSA vs SOC 2 CPA vs ISO 27001 certification body)
- Independence

Drawbacks:
- More relationships to manage
- Audit weeks not coordinated (multiple disruptions)

---

## Cheat sheet

| Question | Answer |
|----------|--------|
| Start with which? | Customer-demanded; often SOC 2 Type I |
| SOC 2 vs ISO 27001? | If selling US enterprise: SOC 2 first; if global: ISO 27001 |
| When to add second framework? | After first is operational; substantial overlap with SOC 2 + ISO 27001 |
| Same auditor for SOC 2 + ISO 27001? | Possible; depends on firm; some specialize in one |
| How long for SOC 2 Type I from scratch? | 3-6 months |
| How long for ISO 27001 from scratch? | 6-12 months |
| Shared evidence rate? | 60-80% overlap between SOC 2 + ISO 27001 |
| Multi-framework GRC tool needed? | At 3+ frameworks; complexity overhead justifies |
| When to consult external? | Initial certification; novel framework; complex multi-framework |
