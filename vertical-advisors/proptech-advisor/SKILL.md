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
---

# Proptech Advisor

Strategic frameworks for property-technology founders, operators, and product leaders.

> **Disclaimer:** Frameworks only. Real estate is heavily regulated state-by-state — engage real-estate-licensed counsel for binding decisions.

---

## Keywords

proptech, real estate, real-estate, MLS, brokerage, broker, agent, iBuyer, property management, multifamily, commercial real estate, CRE, RESPA, fair housing, listings, transaction, escrow, title

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
