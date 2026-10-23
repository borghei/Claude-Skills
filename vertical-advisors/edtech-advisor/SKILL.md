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
  tags:
    - edtech
    - ferpa
    - coppa
    - k-12
    - district-sales
---

# Edtech Advisor

Strategic frameworks for education-technology founders, operators, and product leaders.

> **Disclaimer:** Frameworks and orientation only. Not legal advice. Edtech compliance (FERPA, COPPA, GDPR, state laws) requires specialist counsel. Use this skill to organize strategy.

---

## Keywords

edtech, K-12, higher education, higher ed, university, college, FERPA, COPPA, GDPR-K, student data, LMS, SIS, learning management, school district, RFP, district sales, corporate learning, L&D, training, certification

---

## Clarify First

Edtech advice depends most on who the learners are, who buys the product, and where they are. Settle the inputs below before producing anything. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Learner age and who the customer is:** COPPA applies to services directed to children under 13 or that knowingly collect their data. When a school is the customer, it can authorize collection for educational purposes in place of parents, and FERPA reaches the vendor through the school official exception. A direct-to-learner product for under-13s needs verifiable parental consent instead.
- **Market:** K-12, Higher Ed, Corporate L&D and direct-to-learner have different buyers, contract lengths, sales cycles and pricing. FERPA is interpreted differently in K-12 and Higher Ed, and Corporate L&D behaves more like HR-tech.
- **States and countries:** State laws such as SOPIPA and NY Ed Law 2-d add obligations beyond FERPA, and many states require a Student Data Privacy Agreement before a tool touches student data, even in a free pilot. Learners in the EU bring GDPR-K into scope.

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

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

## Scope & Limitations

**In Scope:**
- Student-data compliance scoping for FERPA, COPPA, GDPR-K and state laws such as SOPIPA and NY Ed Law 2-d
- Keyword-based scanning of a product description for student-data handling and likely regimes with `student_data_compliance_checker.py`
- Market selection across K-12, Higher Ed, Corporate L&D and direct-to-learner by buyer, contract length, sales cycle and pricing
- District sales planning: decision-makers, procurement paths (RFP, sole source, statewide cooperative), rostering and SIS integration
- An SDPA and compliance posture inventory template

**Out of Scope:**
- Drafting or reviewing SDPA and DPA contracts (pairs with `legal/`, as noted in Integration Points)
- Privacy programs beyond student data, such as GDPR or CCPA in general (see `legal/privacy-compliance/` and `ra-qm-team/ccpa-cpra-privacy-expert/`)
- Launch timing and campaigns (see `marketing/launch-strategy/`)
- Curriculum design, accessibility audits or LMS integration engineering

**Important Caveats:**
- The checker matches keywords in your description. It shows likely exposure, not whether a law applies, so missing or vague wording can hide a regime.
- The output is orientation only and not legal advice, as the disclaimer above states. Findings go to specialist counsel.
- State student-privacy laws differ and change. Check the current rules in each state where you sell.

---

## Integration Points

- Pairs with `legal/` for SDPA / DPA contract review
- Pairs with `marketing/launch-strategy` for back-to-school launch timing
- Pairs with `agents/c-level/cs-fundraising-advisor.md` (agent) for edtech-specific fundraising

## Best Practices

- **Plan for the academic calendar.** District purchase cycles peak in spring (for fall) and again at end-of-year. Selling in October to start in November is a non-starter.
- **Sign SDPAs before piloting.** Many states require districts to have a Student Data Privacy Agreement before a tool can touch student data — even a free pilot.
- **Don't conflate K-12 and Higher Ed.** Different buyers, different sales cycles, different compliance regimes (FERPA applies to both but how it's interpreted differs).
- **Corporate L&D is not edtech.** It's HR-tech with edtech roots. Different buyer (CHRO / L&D leader), different metrics (completion, retention), different sales motion.
