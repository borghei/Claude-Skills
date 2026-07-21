---
name: edtech-advisor
description: >
  Strategic advisory for edtech founders on FERPA/COPPA compliance, K-12 vs higher-ed
  vs L&D dynamics, district sales, and pricing. Use when scoping an edtech product or
  navigating procurement, or mentioning edtech, K-12, FERPA, COPPA, or LMS.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: vertical-advisors
  domain: edtech
  updated: 2026-05-04
  python-tools: student_data_compliance_checker.py
  tech-stack: edtech, education
---

# Edtech Advisor

Strategic frameworks for education-technology founders, operators, and product leaders.

> **Disclaimer:** Frameworks and orientation only. Not legal advice. Edtech compliance (FERPA, COPPA, GDPR, state laws) requires specialist counsel. Use this skill to organize strategy.

---

## Keywords

edtech, K-12, higher education, higher ed, university, college, FERPA, COPPA, GDPR-K, student data, LMS, SIS, learning management, school district, RFP, district sales, corporate learning, L&D, training, certification

---

## Quick Start

1. Run student-data compliance checker on a 1-paragraph product description
2. Identify primary market (K-12 / Higher Ed / Corporate L&D / Direct-to-Learner)
3. Read the corresponding section of `references/edtech_market_dynamics.md`

---

## Core Workflows

### Workflow 1: Student Data Compliance Scoping
1. Run: `python scripts/student_data_compliance_checker.py description.txt`
2. Cross-reference with `references/student_data_privacy.md`
3. Hand findings to counsel — FERPA / COPPA / GDPR-K + state laws
4. Document scope and BAA / Student Data Privacy Agreement (SDPA) inventory

**Time Estimate:** 4-6 weeks for first scope.

### Workflow 2: Market Selection (K-12 vs HiEd vs Corp)
1. Read `references/edtech_market_dynamics.md`
2. Score product fit against each market: buyer, contract length, sales cycle, pricing benchmarks, churn dynamics
3. Pick one primary market for first $1M-$5M ARR
4. Build content, sales motion, and pricing aligned to that market

**Time Estimate:** 4-8 weeks.

### Workflow 3: District Sales Strategy
1. Map district decision-makers: superintendent, assistant superintendent, CTO, curriculum director, principal, teacher
2. Plan procurement path: RFP, sole source, statewide cooperative
3. Plan implementation: PD (professional development), rostering (Clever, ClassLink), SIS integration
4. Validate with reference districts before broader investment

**Time Estimate:** 6-12 months for first major district win.

---

## Tools

### student_data_compliance_checker.py

Scans a product description for indicators of student-data handling and likely compliance regime exposure (FERPA, COPPA, GDPR-K, state laws).

```bash
python scripts/student_data_compliance_checker.py description.txt
python scripts/student_data_compliance_checker.py description.txt --json
```

---

## Reference Guides

- **`references/student_data_privacy.md`** — FERPA, COPPA, GDPR-K, state laws (SOPIPA, NY Ed Law 2-d, etc.)
- **`references/edtech_market_dynamics.md`** — K-12, Higher Ed, Corporate L&D, D2C — buyer, sales cycle, pricing

---

## Templates

- **`assets/sdpa_inventory_template.md`** — Student Data Privacy Agreement and compliance posture template

---

## Integration Points

- Pairs with `legal/` for SDPA / DPA contract review
- Pairs with `marketing/launch-strategy` for back-to-school launch timing
- Pairs with `c-level-advisor/cs-fundraising-advisor` for edtech-specific fundraising

## Best Practices

- **Plan for the academic calendar.** District purchase cycles peak in spring (for fall) and again at end-of-year. Selling in October to start in November is a non-starter.
- **Sign SDPAs before piloting.** Many states require districts to have a Student Data Privacy Agreement before a tool can touch student data — even a free pilot.
- **Don't conflate K-12 and Higher Ed.** Different buyers, different sales cycles, different compliance regimes (FERPA applies to both but how it's interpreted differs).
- **Corporate L&D is not edtech.** It's HR-tech with edtech roots. Different buyer (CHRO / L&D leader), different metrics (completion, retention), different sales motion.
