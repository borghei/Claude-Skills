---
name: proptech-advisor
description: >
  Strategic advisory for proptech founders on real-estate segments, MLS/brokerage
  models, licensing, and business models. Use when scoping a proptech idea or when
  the user mentions proptech, MLS, brokerage, iBuyer, or RESPA.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: vertical-advisors
  domain: proptech
  updated: 2026-05-04
  python-tools: market_segment_classifier.py
  tech-stack: proptech, real-estate
  tags:
    - proptech
    - real-estate
    - mls
    - brokerage
    - licensing
---

# Proptech Advisor

Strategic frameworks for property-technology founders, operators, and product leaders.

> **Disclaimer:** Frameworks only. Real estate is heavily regulated state-by-state — engage real-estate-licensed counsel for binding decisions.

---

## Keywords

proptech, real estate, real-estate, MLS, brokerage, broker, agent, iBuyer, property management, multifamily, commercial real estate, CRE, RESPA, fair housing, listings, transaction, escrow, title

---

## Clarify First

Proptech advice turns on where the product sits in the real-estate transaction and in which states it operates. Settle the inputs below before producing anything. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Segment:** Transaction, listings, financing, property management, services, or data and infrastructure. Regulatory exposure differs sharply between them, and `market_segment_classifier.py` reports considerations per segment it detects.
- **Role in the transaction:** Becoming a broker, partnering with one, referring to brokers, or staying outside the transaction. Brokerage needs a license, full MLS access usually needs broker membership, and referral fees and affiliated business arrangements fall under RESPA Section 8.
- **States:** Licensing, agency, escrow and disclosure rules vary by state, and each state requires separate licensure. A national launch and a single-state pilot need different plans.
- **Residential or commercial:** They differ in buyers, deal sizes, sales cycles and regulation. Residential products that rank or filter properties also carry fair-housing disparate-impact risk.

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

---

## Quick Start

```bash
python scripts/market_segment_classifier.py description.txt
```

Classifies a proptech idea by segment (transaction / listings / financing / management / services / data) and surfaces the regulatory and business considerations for that segment.

---

## Core Workflows

### Workflow 1: Market Segment Classification
1. Run the classifier to identify the segment
2. Cross-reference with `references/proptech_segments.md`
3. Identify regulatory exposure: state real-estate licensing, RESPA, fair housing, MLS access
4. Decide go/no-go before deeper investment

**Time Estimate:** 4-6 weeks for first scope.

### Workflow 2: Brokerage / MLS Strategy
1. Read `references/mls_and_brokerage.md`
2. Decide: become a broker (license required), partner with one, or stay outside the transaction
3. Plan MLS access strategy (RESO Web API, IDX, VOW, broker reciprocity)
4. Engage real-estate counsel before customer-facing launch

**Time Estimate:** 4-12 weeks depending on path.

### Workflow 3: Residential vs Commercial Decision
1. Each is a different industry. Commercial has different buyers, deal sizes, sales cycles, regulations.
2. Pick one for first $1M-$5M ARR; expand only after that motion is repeatable.

**Time Estimate:** 4-8 weeks.

---

## Tools

### market_segment_classifier.py

Classifies a proptech business description into one or more proptech segments and surfaces the regulatory considerations for each.

```bash
python scripts/market_segment_classifier.py description.txt
python scripts/market_segment_classifier.py description.txt --json
```

**Segments detected:**
- Transaction (iBuyer, marketplace, brokerage tech)
- Listings (search, valuation, comparable analysis)
- Financing (mortgage tech, alt financing, rent-to-own)
- Management (property management, multifamily ops, tenant experience)
- Services (insurance, title, escrow, inspection, moving)
- Data and infrastructure (PropTech B2B SaaS for industry players)

---

## Scope & Limitations

**In Scope:**
- Segment classification across transaction, listings, financing, management, services, and data and infrastructure, with regulatory and business-model notes per segment, from `market_segment_classifier.py`
- Brokerage and MLS strategy: becoming a broker, partnering or staying outside the transaction, and MLS access through RESO Web API, IDX, VOW and broker reciprocity
- Regulatory exposure orientation for state licensing, RESPA Section 8 and fair housing
- The residential versus commercial decision and a segment assessment template

**Out of Scope:**
- State licensing applications, RESPA structuring or fair-housing legal review (engage real-estate counsel)
- Mortgage lending and money-movement licensing in depth (see `vertical-advisors/fintech-advisor/`)
- Two-sided marketplace mechanics such as liquidity and take rate (see `vertical-advisors/marketplace-advisor/`)
- Property valuation models or MLS data integration code

**Important Caveats:**
- The classifier matches keywords in your description. It can miss a segment or flag one that does not apply, so read its output against the references.
- The output is a framework, not legal advice, as the disclaimer above states. Rules on licensing, agency, escrow and disclosure differ by state.
- Commission structures and MLS access rules face ongoing antitrust scrutiny, so check current MLS and state rules before launch.

---

## Reference Guides

- **`references/proptech_segments.md`** — Segments overview, regulatory exposure per segment, business model patterns
- **`references/mls_and_brokerage.md`** — How MLS works, IDX/VOW/RESO, broker licensing, partnership models

---

## Templates

- **`assets/proptech_segment_assessment.md`** — Decision template for capturing segment, regulatory, GTM decisions

---

## Best Practices

- **Real estate is state-by-state.** US has 50+ regulatory regimes for licensing, agency, fair housing, escrow, and disclosure.
- **MLS is gated.** Most MLSs require broker membership for full access. Plan accordingly.
- **RESPA is real.** Real Estate Settlement Procedures Act prohibits kickbacks; affiliated business arrangements need proper structuring.
- **Fair housing is non-negotiable.** Algorithms ranking properties by neighborhood demographics or "school quality" can produce illegal disparate impact.
- **Residential and commercial are different industries.** Don't try to serve both in one product.
- **Cyclical industry.** Transaction-based proptech sees revenue swings with rate cycles; build resilience.
