# FDA Software as Medical Device (SaMD) Basics

When healthtech software falls under FDA jurisdiction, when it doesn't, and how the classification works. Pair with `ra-qm-team/fda-compliance/` and `ra-qm-team/iec-62304-compliance/` for the implementation work.

> **Disclaimer:** Orientation only. Medical device classification is a regulatory and clinical determination requiring qualified RA/QM specialists.

---

## What SaMD Means

Software as a Medical Device (SaMD) — software intended to be used for one or more medical purposes that perform these purposes **without being part of a hardware medical device**.

Examples:
- Mobile app analyzing skin photos to flag potential melanoma → SaMD
- Software analyzing CT scans for stroke detection → SaMD
- Continuous glucose monitor's analysis algorithm (when distinct from the sensor hardware) → SaMD candidate
- Mobile app reminding users to take medication → may or may not be SaMD depending on claims

What makes something a medical device under FDA: an **intent to diagnose, treat, prevent, cure, or mitigate a disease or condition**.

---

## What's NOT a Medical Device

- General wellness products (without disease-specific claims)
- Patient-facing reference (Wikipedia for medications)
- Administrative software (scheduling, billing, EHR)
- Practice-management tools
- Software for healthcare professional education
- Lifestyle and weight-management products without disease claims

The key is **claims**. "Helps you sleep better" is wellness. "Treats insomnia" is a regulated claim.

---

## IMDRF Risk Categorization

The International Medical Device Regulators Forum (IMDRF) framework — used by FDA — categorizes SaMD by:

**Significance of information** (rows):
- Treat or diagnose
- Drive clinical management
- Inform clinical management

**State of healthcare situation** (columns):
- Critical
- Serious
- Non-serious

This produces a 4×3 matrix giving categories I (lowest risk) through IV (highest):

| Healthcare situation \ Significance | Inform | Drive | Treat/Diagnose |
|-------------------------------------|--------|-------|----------------|
| Critical | II | III | IV |
| Serious | I | II | III |
| Non-serious | I | I | II |

Higher categories = more rigor in development, validation, and post-market surveillance.

---

## FDA Classes (Domestic)

US FDA classifies medical devices (including SaMD) into:

- **Class I** (low risk) — General controls. Often 510(k) exempt.
- **Class II** (moderate risk) — General + special controls. Usually 510(k) clearance required.
- **Class III** (high risk, life-sustaining or supporting) — Premarket Approval (PMA) required.

Class is determined by the device's intended use and indications.

---

## 510(k) vs De Novo vs PMA

Most SaMD that needs FDA clearance follows one of these paths:

### 510(k) — Premarket Notification
- Demonstrate "substantial equivalence" to a legally-marketed predicate device
- Typical timeline: 3-6 months FDA review
- Lower data burden than De Novo or PMA
- Class I or II devices

### De Novo
- For novel low-to-moderate risk devices with no predicate
- Establishes a new classification
- Typical timeline: 6-12 months FDA review
- Class I or II devices

### PMA — Premarket Approval
- For Class III devices
- Requires clinical trial data
- Typical timeline: 12-24+ months
- Significant capital commitment

Plus newer pathways relevant to digital health:
- **De Novo for AI/ML SaMD** with predetermined change control plans
- **Software Pre-Cert pilots** (limited)

---

## EU MDR (Medical Device Regulation)

EU MDR replaced MDD in 2021 and is more stringent. Software classification under MDR is generally:

- **Class I** — low risk
- **Class IIa** — medium risk
- **Class IIb** — high risk
- **Class III** — highest risk

Rule 11 of MDR specifically addresses software, often pushing software up in classification compared to MDD. Many products that were Class I under MDD are now Class IIa or higher.

A Notified Body conformity assessment is required for Class IIa+. Authorized Representative needed for non-EU manufacturers.

---

## Key Standards

If your product is regulated as a medical device:

- **ISO 13485** — Quality Management System for medical devices
- **ISO 14971** — Risk management for medical devices
- **IEC 62304** — Medical device software lifecycle processes
- **IEC 62366** — Usability engineering for medical devices
- **ISO 27001** + sector profiles — information security
- **21 CFR Part 11** (US) — electronic records and signatures

The RA/QM domain in this repo (`ra-qm-team/`) covers these in implementation depth.

---

## Common Mistakes

- **Calling it "wellness" to avoid regulation.** If your claims are clinical, your classification is too. Marketing claims often determine regulatory status more than the underlying tech.
- **Designing without anticipated regulatory path.** Late-stage retrofitting to 510(k) requirements is more expensive than building to them from start.
- **Underestimating clinical validation.** Most SaMD requires clinical evidence even for 510(k). Plan from start.
- **Single-jurisdiction thinking.** US FDA + EU MDR + Health Canada + Japan PMDA + others all have different requirements. Sequenced submission strategy matters.
- **No post-market surveillance plan.** Adverse-event reporting, periodic safety updates, and (for AI/ML) drift monitoring are required, not optional.
- **Mixing regulated and non-regulated functions in one product.** This often forces the non-regulated function to also be regulated. Consider separation.

---

## Working with RA/QM Specialists

RA = Regulatory Affairs. QM = Quality Management. These are distinct functions that may sit together or separately.

Hire or contract them **early**:
- Regulatory strategist to plan submission pathway
- QM specialist to build/maintain ISO 13485 QMS
- Often a single fractional consultant covers both at early stage

For implementation: this skill complements but does not replace `ra-qm-team/` content. Use this skill for strategic decisions; use RA/QM skills for implementation work.

---

## Resources

- **FDA Digital Health Center of Excellence:** fda.gov/medical-devices/digital-health-center-excellence
- **FDA SaMD page:** fda.gov/medical-devices/software-medical-device-samd
- **IMDRF SaMD documents:** imdrf.org
- **EU MDR:** ec.europa.eu/health/medical-devices/regulatory-framework
- **Notified Body lists** for EU CE marking

For binding decisions, engage qualified RA/QM specialists.
