---
name: healthtech-advisor
description: >
  Strategic advisory for digital health founders on HIPAA scope, FDA SaMD
  classification, EHR integration, and payor/provider GTM. Use when scoping a
  healthtech idea, classifying PHI, or mentioning HIPAA, FDA SaMD, EHR, or telehealth.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: vertical-advisors
  domain: healthtech
  updated: 2026-05-04
  python-tools: phi_scope_checker.py
  tech-stack: healthtech, digital-health
---

# Healthtech Advisor

Strategic frameworks for digital health and healthtech founders, operators, and product leaders. **Complements** (does not replace) the RA/QM compliance domain. RA/QM covers regulatory and quality management for medical devices; this skill covers business-side strategy for health software companies.

> **Disclaimer:** Frameworks and orientation only. Not legal, regulatory, clinical, or compliance advice. Healthtech businesses need licensed counsel (HIPAA, FDA, fraud-and-abuse), clinical advisors, and qualified RA/QM specialists. Use this skill to organize strategy; engage specialists for binding decisions.

---

## Table of Contents

- [Keywords](#keywords)
- [Quick Start](#quick-start)
- [Core Workflows](#core-workflows)
- [Tools](#tools)
- [Reference Guides](#reference-guides)
- [Templates](#templates)
- [Best Practices](#best-practices)

---

## Keywords

healthtech, digital health, HIPAA, PHI, BAA, business associate, covered entity, FDA SaMD, software as medical device, EHR, EMR, FHIR, HL7, telehealth, digital therapeutics, DTx, payor, provider, value-based care, fee-for-service, RPM, remote patient monitoring

---

## Quick Start

### 10-Minute Scope Check

1. Write a 1-paragraph description of what your product does and what data it touches
2. Run `python scripts/phi_scope_checker.py description.txt`
3. Use the output to scope HIPAA exposure and identify whether you're a Business Associate, Covered Entity, neither, or both

### Pick a GTM

1. Read `references/gtm_patterns.md`
2. Identify your buyer: payor, provider, employer, individual, pharma, government
3. Each GTM has a different sales motion, contract length, and economics — pick before committing engineering

---

## Core Workflows

### Workflow 1: HIPAA Scope and BAA Strategy

**Goal:** Determine whether HIPAA applies, in what capacity (Covered Entity, Business Associate, neither), and what BAAs you need with whom.

**Steps:**
1. Run PHI scope checker on your product description
2. Identify: do you handle PHI on behalf of a Covered Entity (you're a BA), are you a CE yourself, or are you handling consumer-generated health data outside HIPAA?
3. Map BAA requirements: with which Covered Entities you operate as BA, with which subcontractors you operate as BA-of-BA
4. Engage HIPAA-specialist counsel to review scope before launch
5. Operationalize: BA-grade hosting, encryption, access controls, audit logs, breach notification process

**Time Estimate:** 4-8 weeks for first scope and BAA template.

### Workflow 2: FDA SaMD Classification

**Goal:** Determine whether your software is regulated as a medical device by the FDA, and at which classification.

**Steps:**
1. Read `references/fda_samd_basics.md`
2. Apply IMDRF risk categorization framework: severity of healthcare situation × significance of information
3. Determine FDA class (I, II, III) or unregulated wellness category
4. If regulated: pair with `ra-qm-team/fda-compliance/` and `ra-qm-team/iec-62304-compliance/` for the implementation work
5. If unregulated wellness: document why, and avoid claims that would cross into regulated territory

**Time Estimate:** 4-12 weeks for classification, then RA/QM-driven submission timelines.

### Workflow 3: GTM Selection

**Goal:** Pick the buyer segment and sales motion that matches your product.

**Steps:**
1. Read `references/gtm_patterns.md`
2. Map your product's value proposition to each buyer's purchase criteria
3. Recognize the constraints: payor 24-36 month sales cycles, provider IT integration, employer benefits-cycle timing
4. Pick **one** primary motion to start; expand later
5. Build the team that matches the motion — payor sales is different from provider sales is different from D2C

**Time Estimate:** 4-8 weeks for GTM strategy decision.

---

## Tools

### phi_scope_checker.py

Scans a product description for indicators of PHI handling and HIPAA scope. Identifies whether you're likely a Covered Entity, Business Associate, both, or operating outside HIPAA (consumer wellness data).

```bash
python scripts/phi_scope_checker.py description.txt
python scripts/phi_scope_checker.py description.txt --json
```

---

## Reference Guides

- **`references/hipaa_basics.md`** — HIPAA scope, Covered Entity vs Business Associate, BAA requirements, common pitfalls
- **`references/fda_samd_basics.md`** — Software as Medical Device classification, IMDRF framework, US vs EU
- **`references/gtm_patterns.md`** — Payor, provider, employer, individual, pharma, government — sales cycles, contract structures, decision criteria
- **`references/value_based_care_primer.md`** — Fee-for-service vs VBC, capitation, shared savings, ACOs, common models

---

## Templates

- **`assets/hipaa_scope_template.md`** — Document template for capturing HIPAA scope decisions and BAA inventory

---

## Best Practices

- **Engage HIPAA counsel before architecture decisions.** Same point as fintech: regulatory shapes infrastructure.
- **Don't claim HIPAA compliance — be HIPAA compliant.** Marketing claims attract regulator attention; the actual program protects the company.
- **Don't conflate HIPAA and FDA.** They cover different things. HIPAA = data; FDA = device.
- **PHI vs consumer health data.** Apple Health data, fitness tracker data, and consumer wellness data are not always PHI. The status depends on context (Covered Entity relationship), not the data type alone.
- **Plan for state laws.** California (CMIA), Washington (My Health My Data), and others extend beyond HIPAA. Texas, NY have their own.
- **EHR integrations are slow.** Epic, Cerner, athenahealth integrations take months and require partnership programs. Plan accordingly.

---

## Integration Points

- **`ra-qm-team/`** for medical-device-grade compliance work (ISO 13485, MDR, FDA, IEC 62304)
- **`legal/`** for BAA / DPA templates and contract review
- **`engineering/cs-security-engineer`** — healthtech security goes beyond standard SaaS
- **`business-growth/pricing-strategy`** — healthtech pricing has unusual constraints (PMPM, capitation, fee-for-service)
- **`c-level-advisor/cs-fundraising-advisor`** — healthtech investor expectations differ from generic SaaS
