# Fintech Regulatory Landscape

A founder's-eye map of fintech regulators in the US and EU, what each covers, and the trigger patterns that bring you under their oversight. This is **orientation**, not legal advice — every fintech needs specialist counsel.

---

## United States

US fintech regulation is a patchwork of federal and state regulators. The same business can fall under five regulators simultaneously.

### FinCEN (Financial Crimes Enforcement Network)
- **What:** Anti-money-laundering (AML) and counter-terrorist-financing (CTF) for money services businesses
- **Triggers:** Money transmission, currency exchange, MSB activity, cryptocurrency exchange
- **Key obligations:** Register as MSB, AML program, suspicious activity reports (SARs), customer due diligence (CDD)

### OCC (Office of the Comptroller of the Currency)
- **What:** National bank charters, federal savings associations, federal branches of foreign banks
- **Triggers:** Direct deposit-taking with national bank charter
- **Key obligations:** Capital, liquidity, governance per OCC standards. Most fintechs avoid by partnering with chartered banks.

### FDIC (Federal Deposit Insurance Corporation)
- **What:** Deposit insurance for member banks, supervisory authority for state non-member banks
- **Triggers:** "FDIC-insured" claim — only valid if deposits are at an FDIC-member bank
- **Key obligations:** Disclosure rules around what is and isn't FDIC-insured (a frequent area of regulatory action against fintechs)

### CFPB (Consumer Financial Protection Bureau)
- **What:** Consumer financial products and services
- **Triggers:** Consumer-facing finance — lending, payments, deposits, debt collection
- **Key obligations:** UDAAP (no unfair, deceptive, or abusive practices), specific regulations (Reg E for electronic funds, Reg Z for credit, Reg DD for deposits)

### State Banking Commissioners (50 states + DC)
- **What:** State-level oversight of money transmitters, lenders, and state-chartered banks
- **Triggers:** Most fintech activity at scale touches state law in some way
- **Key obligations:** Money transmitter licenses (MTLs) — separate license per state, with varying standards. NMLS portal for applications. Most fintechs avoid via sponsor-bank or BaaS partnership.

### SEC (Securities and Exchange Commission) + FINRA
- **What:** Securities markets, investment advisers, broker-dealers
- **Triggers:** Anything looking like securities — fractional shares, retail investing, "tokens" with profit expectation, RIA-like advice
- **Key obligations:** Broker-dealer or RIA registration, FINRA membership for BDs, custody rule under Investment Advisers Act

### CFTC (Commodity Futures Trading Commission)
- **What:** Commodities, futures, derivatives, some crypto
- **Triggers:** Bitcoin, Ethereum (treated as commodities), futures, perps
- **Key obligations:** Vary; often relevant for crypto exchanges with leveraged products

### NYDFS (New York Department of Financial Services)
- **What:** New York's banking and insurance regulator; outsized influence due to NY market
- **Triggers:** Operating in NY, especially crypto (BitLicense)
- **Key obligations:** BitLicense for crypto (one of the most stringent regimes in the world)

### State Attorneys General
- **What:** Consumer protection enforcement under state UDAP statutes
- **Triggers:** Consumer harm complaints (real or alleged)
- **Key obligations:** Cooperative responses to inquiries; pre-emptive disclosure hygiene

---

## European Union and United Kingdom

EU fintech regulation is generally more harmonized than US, but operates through national competent authorities (NCAs) per member state.

### EBA (European Banking Authority)
- **What:** EU-level coordinating authority for banking and payments
- **Issues:** Technical standards, EBA guidelines

### National Competent Authorities (NCAs)
- **Examples:** FCA (UK), BaFin (Germany), ACPR (France), AFM/DNB (Netherlands), CSSF (Luxembourg), FINMA (Switzerland — non-EU but adjacent)
- **Triggers:** Authorization required to provide regulated services in any member state
- **Passporting:** Authorization in one EEA member state generally allows passporting to others (not UK post-Brexit)

### Key EU regimes

**PSD2 (Payment Services Directive 2)**
- Triggers: payment services to EU residents
- Authorization tiers: Payment Institution (PI), Electronic Money Institution (EMI)
- Adds: strong customer authentication (SCA) requirements, open banking access (AISP, PISP)

**MiCA (Markets in Crypto-Assets)**
- Triggers: crypto-asset issuance or service provision in EU
- Authorization required for CASPs (Crypto-Asset Service Providers)
- Phased rollout completing in 2025-2026

**MiFID II (Markets in Financial Instruments Directive)**
- Triggers: investment services (broker, advisor, portfolio manager)
- Authorization as Investment Firm

**CRR/CRD (Capital Requirements Regulation / Directive)**
- Triggers: deposit-taking credit institution
- Most fintechs avoid by being PI/EMI rather than credit institution

**GDPR (General Data Protection Regulation)**
- Triggers: any personal data of EU residents
- Sector-agnostic but often most-onerous regime for fintechs

**DORA (Digital Operational Resilience Act)**
- Triggers: financial entities + their critical ICT third-party service providers
- Operational resilience, ICT risk management, incident reporting

---

## Common Trigger Patterns (Decision Heuristics)

Use these as conversation-starters with counsel — never as conclusions.

| If your business… | You probably need to think about… |
|-------------------|----------------------------------|
| Holds customer fiat balances | Money transmission OR sponsor bank |
| Issues debit/credit cards | BIN sponsor + card-network rules + PCI-DSS |
| Originates loans | Lending licenses OR partner-bank originator |
| Trades / advises on stocks | Broker-dealer OR RIA |
| Operates with cryptocurrencies | FinCEN MSB + NYDFS BitLicense + state MTLs (US); MiCA (EU) |
| Sends EU-to-EU payments | PSD2 PI / EMI |
| Stores customer financial data | GLBA + GDPR + state privacy laws |
| Markets to consumers | CFPB / UDAAP attention |
| Calls itself "FDIC-insured" | True only via FDIC-member bank — disclosure scrutiny |

---

## Common Mistakes

- **Treating regulation as last-mile.** Regulation shapes architecture, partnerships, and pricing. Bringing it in late is expensive.
- **Assuming partner = no regulator relationship.** Even with a BaaS provider, regulators may look through to you and customers see your brand.
- **One-state US thinking.** US is 50+ regulators. Either get all the licenses (rare) or partner.
- **"It's just SaaS."** SaaS for a regulated industry is not unregulated. Vendor-of-record obligations apply.
- **Ignoring sanctions.** OFAC sanctions screening is non-negotiable. A small slip can kill the company.

---

## Where to Read More

- **CFPB:** consumerfinance.gov — supervision, enforcement actions, regulations
- **FinCEN:** fincen.gov — MSB registration, AML guidance
- **NMLS:** nmlsconsumeraccess.org — state license registry
- **EBA:** eba.europa.eu — payments, technical standards
- **National regulators:** FCA, BaFin, ACPR, AFM each publish founder-friendly authorization guides

For binding decisions on any specific business, **engage fintech-specialist counsel.**
