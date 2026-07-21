---
name: fintech-advisor
description: >
  Strategic advisory for fintech founders on US/EU regulatory triggers,
  license-vs-partner, KYC/AML, and embedded finance. Use when scoping a fintech idea
  or regulatory exposure, or mentioning fintech, money transmitter, neobank, KYC,
  or PSD2.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: vertical-advisors
  domain: fintech
  updated: 2026-05-04
  python-tools: regulatory_trigger_checker.py
  tech-stack: fintech, banking, payments
---

# Fintech Advisor

Strategic frameworks for fintech founders, operators, and product leaders. Knowledge-heavy by design — the right answer in fintech is usually a regulatory and economic judgment, not a calculation.

> **Disclaimer:** This skill provides frameworks and orientation. It is **not** legal, regulatory, securities, tax, or investment advice. Every fintech business needs licensed legal counsel. Use this skill to organize internal thinking; engage specialist counsel for binding decisions.

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

fintech, payments, banking, neobank, lending, money transmitter, KYC, AML, PSD2, open banking, BaaS, banking-as-a-service, embedded finance, card issuing, ACH, SEPA, stablecoin, crypto, broker-dealer, RIA, regulation, compliance

---

## Quick Start

### Initial Regulatory Triage in 10 Minutes

1. Write a 1-paragraph description of what your fintech does (who pays whom, in what form, who holds the funds)
2. Run `python scripts/regulatory_trigger_checker.py business_description.txt`
3. Use the output as input to a conversation with a fintech-licensed lawyer — never as the conclusion

### License vs. Partner Decision

1. Read `references/license_vs_partner_playbook.md`
2. For each capability you need (hold funds, issue cards, originate loans, send payments), decide: get a license, or partner with a licensed entity (BaaS, sponsor bank)
3. Most early-stage fintechs partner. License only if the unit economics or moat absolutely require it.

---

## Core Workflows

### Workflow 1: Regulatory Exposure Scoping

**Goal:** Understand which US / EU regulatory regimes a proposed fintech business model triggers, before committing to architecture.

**Steps:**
1. Write a clear business description: who pays whom, what is held by whom, where the entity operates
2. Run the trigger checker for a quick orientation
3. Map each trigger to the relevant regulator (FinCEN, OCC, state banking commissioners, SEC, CFPB, FCA, BaFin, ACPR)
4. Engage specialist counsel before designing infrastructure
5. Document the regulatory architecture as part of the company's compliance file

**Time Estimate:** 4-8 weeks of legal scoping for a meaningful new build.

### Workflow 2: License vs. Partner

**Goal:** Decide whether to get the regulated capability yourself, or buy it from a partner.

**Steps:**
1. List capabilities needed: KYC/identity, custody, issuing, acquiring, lending, FX, deposit-taking
2. For each, score on the 4-axis grid in `license_vs_partner_playbook.md`: cost, time, control, economics
3. Pick partners only where the regulator-of-record relationship can survive partner failure
4. Document fallback plans if the partner is ever rate-limited, deprecates, or fails

**Time Estimate:** 6-12 weeks for major capability decisions.

### Workflow 3: KYC/AML Program Design

**Goal:** Build a KYC/AML program that satisfies regulators *and* doesn't kill conversion.

**Steps:**
1. Read `references/kyc_aml_basics.md`
2. Design tiered KYC: minimal at signup, enhanced when usage patterns trigger thresholds
3. Pick risk-scoring vendor (Alloy, Sardine, Persona, Onfido) and write integration plan
4. Establish ongoing monitoring: transaction monitoring rules, periodic refresh, sanctions / PEP screening
5. Engage MLRO (Money Laundering Reporting Officer) before going live

**Time Estimate:** 8-16 weeks for first-time program design.

---

## Tools

### regulatory_trigger_checker.py

Scans a business description for keywords and patterns that map to regulatory regimes in the US and EU. Output is a list of candidate triggers, **not** a legal opinion.

```bash
python scripts/regulatory_trigger_checker.py business_description.txt
python scripts/regulatory_trigger_checker.py business_description.txt --json
```

**Triggers detected:**
- Money transmission (state-by-state US, e-money/payment institution EU)
- Lending (CFPB, state lending licenses, EU consumer credit)
- Securities (SEC broker-dealer, RIA, EU MiFID)
- Banking / deposit-taking (OCC, FDIC, EU credit institution)
- Payment services (PSD2 in EU, FCA in UK)
- Cryptocurrency (FinCEN MSB, NYDFS BitLicense, MiCA in EU)
- Custody of customer assets

---

## Reference Guides

- **`references/regulatory_landscape.md`** — Map of US and EU fintech regulators, what each covers, common trigger patterns
- **`references/license_vs_partner_playbook.md`** — When to get a license, when to partner, partner failure planning
- **`references/kyc_aml_basics.md`** — KYC tiers, risk-based monitoring, MLRO role, common pitfalls
- **`references/embedded_finance_patterns.md`** — BaaS architecture, distribution-led fintech, B2B2C patterns

---

## Templates

- **`assets/regulatory_architecture_template.md`** — Document template for capturing regulatory decisions and partner choices

---

## Best Practices

- **Engage fintech-specialist counsel from day one.** General-purpose corporate lawyers will miss regulatory triggers. The cost of specialist counsel up front is a fraction of the cost of a regulatory mistake.
- **Don't hide behind partners.** Even with a BaaS provider, your customers see *your* brand and the regulator may look through to you. Plan for partner failure.
- **State-by-state US is real.** Money transmitter laws are state-level — 49 different licenses possible. Most fintechs partner to avoid this.
- **Sanctions are absolute.** A $100 OFAC violation can cost $10M. Sanctions screening is non-negotiable.
- **Treat compliance as product.** Frictionless KYC and clear customer comms about why you're asking for documents are a competitive advantage.

---

## Integration Points

- Pairs with `c-level-advisor/cs-fundraising-advisor` — investors expect a clear regulatory architecture
- Pairs with `engineering/cs-security-engineer` — fintech security goes beyond standard SaaS
- Pairs with `legal/` skills for contract / partner agreements
- Pairs with `business-growth/pricing-strategy` — fintech pricing has unusual constraints (interchange, FX spread, float)
