# Embedded Finance Patterns

Embedded finance — financial products delivered inside non-financial applications — is one of the largest fintech opportunities of the decade. This guide covers architectural patterns and common business model traps.

---

## The Five Embedded-Finance Building Blocks

Most embedded-finance products are combinations of these:

1. **Embedded payments** — accept cards inside another product (Stripe Connect, Adyen for Platforms)
2. **Embedded accounts** — bank accounts inside a non-bank product (Mercury, Brex for verticals)
3. **Embedded cards** — branded debit/credit cards (Lithic, Marqeta)
4. **Embedded lending** — loans originated inside a product flow (Klarna, Affirm, Stripe Capital)
5. **Embedded insurance** — insurance offered inside another product (Cover Genius, Stable)

Most B2B "embedded fintech" startups address one of these for a specific vertical (construction, healthcare, real estate, hospitality).

---

## Architectural Pattern: BaaS Stack

```
+-------------------------------------+
|  Your product / brand (you)         |
|  - UX                                |
|  - Customer support                  |
|  - Risk decisions you control        |
+-------------------------------------+
              |
              | (API, often via BaaS platform)
              v
+-------------------------------------+
|  BaaS platform (e.g., Unit, Bond)    |
|  - Aggregated bank-as-API            |
|  - Compliance tooling                |
|  - Vendor connectors                 |
+-------------------------------------+
              |
              | (regulated relationship)
              v
+-------------------------------------+
|  Sponsor bank (chartered)            |
|  - FDIC-insured deposits             |
|  - Card issuance authority           |
|  - Regulatory relationships          |
+-------------------------------------+
```

You face the customer; the bank faces the regulator. The BaaS platform abstracts the bank.

---

## Distribution-Led vs. Product-Led

### Distribution-led
- A non-fintech company adds finance to its existing customer base
- Examples: Shopify Capital (lending to merchants), Toast (payments + cards for restaurants)
- Strength: customer acquisition cost is near zero
- Weakness: product depth often shallow vs. specialized fintechs

### Product-led (vertical fintech)
- A fintech specialized for a single industry from day one
- Examples: Mercury (startups), Ramp (corporate cards), Brex (early specialization)
- Strength: workflows match the vertical exactly
- Weakness: must invest separately in customer acquisition

The most successful embedded-finance companies tend to be distribution-led incumbents who add a financial layer, OR product-led fintechs who become so deeply specialized in a vertical that they become the SaaS-of-record there.

---

## Common Business Model Patterns

### Interchange-driven
- Free / cheap product subsidized by interchange revenue from a co-branded card
- Works when: high transaction volume, recurring spend
- Watch out for: regulated interchange caps in EU, durbin-amendment dynamics in US

### Float-driven
- Earn yield on customer deposits or in-flight funds
- Works when: large balance sheets, reasonable interest-rate environment
- Watch out for: rate sensitivity, regulatory changes on what fintechs can earn

### Subscription + interchange
- SaaS subscription + financial product economics
- Works when: clear ROI on the financial product, e.g. payroll on cards
- Watch out for: customers feeling double-charged

### Lending margin
- Originate loans against own or partner balance sheet
- Works when: superior underwriting via vertical-specific data
- Watch out for: credit cycles will eventually hit; reserve appropriately

### Take rate on payments
- Cut of GMV
- Works when: high-volume merchants, vertical-specific value-add
- Watch out for: incumbent payment processors compress margins over time

---

## Common Traps

### Trap 1: Confusing distribution with retention
"We have 1M users, we'll cross-sell finance" assumes your users want a financial product from you. Often they don't. Validate willingness to pay before building.

### Trap 2: Mistaking interchange for free money
Interchange revenue feels passive but comes with chargebacks, fraud, sponsor-bank fees, network fees, BaaS fees. Net retention of interchange is often 30-50% of gross.

### Trap 3: Underestimating compliance overhead
The compliance organization (KYC ops, transaction monitoring analysts, MLRO, periodic audits) scales with customer count and transaction volume. Embedded finance founders often under-budget this by 2-3x.

### Trap 4: Sponsor-bank lock-in
A migration from one sponsor bank to another can take 6-18 months and require customer re-papering. Negotiate exit / portability up front.

### Trap 5: BaaS-platform fragility
The 2024 Synapse failure stranded customer funds for months. Diligence the BaaS platform's solvency, governance, and bank relationships — not just the API.

### Trap 6: "We'll go full-stack later"
Many distribution-led companies plan to eventually replace their BaaS partner with their own license. Few actually do, because by the time they're large enough the regulatory cost is too high. Plan partner economics for the long term.

---

## Key Diligence Questions for Any Embedded-Finance Build

Before committing to an embedded-finance line of business:

1. **Regulatory:** Which regulators apply? Have specialist counsel confirmed in writing.
2. **Architecture:** License vs. partner vs. multi-partner? What happens at partner failure?
3. **Economics:** Net economics after partner fees, compliance staff, fraud, sponsor-bank haircuts.
4. **Customer:** Validated willingness to pay (or accept ad-supported / cross-subsidized model)?
5. **Operations:** Headcount required for compliance, ops, risk at 1k / 10k / 100k customers?
6. **Capital:** Float, reserves, capital requirements at scale?
7. **Exit:** Termination plan with each partner — cost, timeline, customer impact?

If any answer is "we'll figure it out later," consider whether the line of business is mature enough to commit to.

---

## Resources

- **CB Insights / a16z fintech reports** — landscape and trends
- **Alloy Labs Alliance / Bank Director** — sponsor-bank perspective
- **Fintech Business Weekly (Jason Mikula)** — analytical, particularly on regulatory issues
- **Tearsheet** — embedded finance case studies
- **a16z Future of Fintech series** — strategic frameworks

For binding decisions, engage fintech-specialist counsel and qualified financial advisors.
