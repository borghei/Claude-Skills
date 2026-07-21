# License vs. Partner Playbook

For each regulated capability your fintech needs, you have two paths: get the license yourself, or partner with someone who has it. This playbook is the decision framework.

---

## The 4-Axis Decision Grid

Score each capability on these four axes (1-5 scale):

| Axis | Question |
|------|----------|
| **Cost** | Capital requirement + legal + ongoing compliance staff. License = high; partner = lower. |
| **Time** | Authorization timeline. License = 12-36 months; partner = 4-12 weeks. |
| **Control** | How much you can change without external approval. License = high; partner = constrained. |
| **Economics** | Margin you keep. License = full; partner = partner takes 10-50% of relevant economics. |

If license scores significantly higher on Control + Economics for the long run, consider getting it. If partner scores higher on Cost + Time for the next 18-24 months, partner.

---

## When to Get the License

Get the license yourself when:

1. **The capability is the moat.** If your differentiation is "we're the licensed bank that can do X partners can't," you must own the license.
2. **Partner economics destroy unit economics.** If a partner takes 30%+ of revenue and your margin without it is 35%, you can't outgrow the partner.
3. **You have the capital and patience.** $5M-$50M+ depending on the regime, plus 1-3 years.
4. **You can hire the regulated talent.** Compliance officers, MLROs, BSA officers don't appear by themselves.
5. **The market reward is large enough.** A US national bank charter is worth fighting for; a single state MTL alone usually isn't.

## When to Partner

Partner when:

1. **You're testing fit.** Most early-stage fintechs should partner because the business itself isn't validated yet.
2. **The capability is undifferentiated.** Card issuing for most fintechs is undifferentiated infrastructure — buy it.
3. **Speed matters more than economics.** First-to-market in a fintech wave often beats fully-licensed second movers.
4. **You don't have the team.** Hiring an MLRO, head of compliance, and risk committee chair before you have product-market fit is expensive.

---

## Common Partner Categories

### Sponsor banks (US)
- **What they provide:** FDIC-insured deposits, debit/credit card issuing rails, sometimes lending
- **Examples:** Cross River, Evolve, Pathward, Sutton Bank, Lead Bank
- **Economics:** Bank gets a slice of interchange + monthly fees + sometimes deposit float
- **Risk:** Bank-level risk decisions can change overnight (post-2023, regulators tightened sponsor-bank oversight)

### BaaS / banking-as-a-service platforms
- **What they provide:** Wraps sponsor bank with developer-friendly API, sometimes additional services
- **Examples:** Synapse (failed 2024), Unit, Treasury Prime, Bond, Solid
- **Economics:** Take a cut of interchange + fixed fees + per-transaction
- **Risk:** Platform layer adds another point of failure (Synapse failure stranded customer funds)

### Card issuing platforms
- **What they provide:** Programmatic card issuing, often abstracted from underlying sponsor bank
- **Examples:** Marqeta, Lithic, Highnote
- **Economics:** Per-card and per-transaction fees, often combined with sponsor bank fees

### Acquiring / payment processors
- **What they provide:** Card acceptance, merchant services
- **Examples:** Stripe, Adyen, Worldpay, Checkout.com
- **Economics:** Per-transaction (typically 2.9% + 30¢ for Stripe pricing on cards)

### KYC / identity / fraud
- **What they provide:** ID verification, document checks, risk scoring, sanctions / PEP screening
- **Examples:** Alloy, Sardine, Persona, Onfido, Jumio
- **Economics:** Per-verification + monthly platform fees

### European EMI / PI partners
- **What they provide:** Payment / e-money authorization with EU passporting
- **Examples:** ClearBank, Modulr, Currency Cloud, Paynetics
- **Economics:** Vary widely

---

## Partner-Failure Planning

A partner can:
- Lose its license (regulator action)
- Be acquired (priorities shift)
- Hit rate-limits or capacity constraints
- Charge significant fee increases
- Fail outright (Synapse 2024)

**Your obligation to customers persists even when your partner fails.** Plan accordingly:

1. **Multi-partner architecture where feasible.** Two card issuers > one. Two KYC vendors > one.
2. **Direct customer relationship.** Don't let partners insert themselves between you and your users in a way that survives partner failure.
3. **Customer-funds segregation visibility.** Know exactly where customer money sits and how to recover it.
4. **Quarterly partner-risk review.** Including: solvency, regulatory standing, executive turnover, news cycle.
5. **Termination plan.** Documented exit path for each material partner, with timeline and cost estimate.

---

## A Word on "Bank Sponsorship Quality"

Not all sponsor banks are equal. After 2023's regulatory tightening:

- Banks under regulatory consent orders cannot freely add fintech programs
- Some banks have effectively closed to new fintech partnerships
- Quality of compliance support varies enormously
- Regulators look at the "bank's third-party risk management" — meaning your operational practices come under their scrutiny via the bank

Ask before signing:
- How many fintech programs does this bank run today?
- Has the bank been subject to consent orders, MRAs (Matters Requiring Attention) from regulators?
- What's the bank's current capital position and recent examination history (if disclosable)?
- Who are the named compliance contacts and what's the SLA on issues?

---

## Decision Documentation Template

For each capability decided, document:

```
Capability: [e.g., card issuing]
Decision: [license / partner]
Partner (if applicable): [name]
Why: [1-2 sentences]
Cost: [annual]
Economics impact: [margin)]
Termination plan: [link or summary]
Re-evaluation date: [12-18 months out]
```

Treat this document as living; revisit at every major round and at least annually.
