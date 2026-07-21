# KYC / AML Basics for Fintech

Know-Your-Customer (KYC) and Anti-Money-Laundering (AML) are the largest source of regulatory friction for most fintechs. Done well, they protect the business and barely affect users. Done poorly, they kill conversion *and* fail audits.

> **Disclaimer:** Orientation only. KYC/AML programs require an MLRO (UK/EU) or BSA officer (US) and program documentation reviewed by counsel. Don't operate without one.

---

## What KYC Is

KYC is the set of practices a financial institution uses to:
1. **Identify** the customer (verify they are who they claim to be)
2. **Understand** the customer's risk profile (source of funds, expected activity)
3. **Monitor** ongoing activity for deviations from expected
4. **Report** suspicious activity to regulators

KYC is mandated by AML laws (BSA in US, MLD in EU/UK) — not by individual regulators. Failing KYC means failing the underlying AML obligation.

---

## Tiered KYC

A tiered approach reduces friction at signup and adds verification as customers do more.

### Tier 0 — Account creation
- Email + phone (verified via OTP)
- Limit: read-only, no funds movement
- Use: explore product, save preferences

### Tier 1 — Basic KYC
- Government ID (passport, driver's license, national ID)
- Selfie / liveness check
- Address (often verified via document upload or third-party data)
- Limit: low-value transactions per day / month
- Use: most retail flows

### Tier 2 — Enhanced KYC
- Source of funds documentation
- Sometimes proof of income or employment
- Higher limits
- Use: larger transactions, business / high-net-worth users

### Tier 3 — Enhanced Due Diligence (EDD)
- Source of wealth (not just funds)
- PEP / sanctions screening with manual review
- Often direct contact with the customer
- Use: politically exposed persons, high-risk geographies, very large transactions

---

## The KYC Stack

Most fintechs assemble KYC from vendors rather than build:

| Layer | Examples | What they do |
|-------|----------|--------------|
| Identity verification | Persona, Onfido, Jumio, Veriff | ID document + selfie + liveness |
| Identity data | Socure, Sentilink, LexisNexis | Watchlist, address, fraud signals |
| Sanctions / PEP | Refinitiv, Dow Jones, ComplyAdvantage | OFAC / UN / EU lists, PEPs |
| Risk scoring | Alloy, Sardine, Sift | Combine signals into a decision |
| Transaction monitoring | Hummingbird, Unit21, ComplyAdvantage TM | Pattern detection, alerts |

Pick one identity vendor and one TM vendor at minimum. Add sanctions/PEP. Risk scoring usually pays for itself by reducing manual review.

---

## Risk-Based Approach

Regulators generally accept a **risk-based** approach: not every customer needs the same scrutiny. The key is documenting your risk model and applying it consistently.

### Risk factors to consider
- **Geography:** Customer's country, IP geography, transaction counterparty geography
- **Customer type:** Individual / business / institutional, age, occupation
- **Product type:** Higher risk = cross-border, high-velocity, anonymity-supporting
- **Transaction patterns:** Velocity, amounts, counterparties, channels
- **Time:** Account age, recent changes in pattern

### Risk-rating model
- Score each customer at onboarding (low / medium / high)
- Re-score periodically (annually for low, quarterly for medium, monthly for high)
- Trigger re-score on events: large transactions, new high-risk counterparty, change of address to high-risk jurisdiction, sanctions list update

---

## Transaction Monitoring (TM)

TM is rule-based + (increasingly) ML-based detection of suspicious patterns:

### Common rule families
- **Velocity:** N transactions of $X within Y minutes
- **Amount:** Single transaction over threshold (varies by product / customer tier)
- **Pattern:** Multiple small deposits then one large withdrawal (structuring)
- **Geography:** Transaction to / from high-risk jurisdiction
- **Counterparty:** Transaction to / from sanctioned, PEP, or known-bad-actor account
- **Behavioral:** Activity inconsistent with customer's stated profile

### Alerts → Cases → SARs
- Rule fires → alert
- Analyst reviews → opens case if substantive
- Case investigation → file SAR (Suspicious Activity Report) with FinCEN if warranted
- SAR within 30 days of detection (US); equivalent timeframes in EU

### Calibration
- New rules should be tested in shadow before going live
- Track alert-to-case ratio (>20:1 means rules are too sensitive)
- Track case-to-SAR ratio (varies by business, often 5:1 to 20:1)

---

## Sanctions Screening

Sanctions screening is **non-negotiable** and **strict liability** — meaning intent doesn't matter; matching a sanctioned entity creates exposure regardless of knowledge.

- Screen at onboarding (block / hold for review)
- Screen on every transaction (or per-counterparty for repeated activity)
- Screen against US OFAC, UN, EU consolidated lists at minimum
- Use fuzzy matching with documented thresholds
- Document every false positive decision

A single OFAC violation can cost millions. Customer experience pales next to this risk.

---

## The MLRO / BSA Officer

In the EU/UK, regulated firms must appoint a Money Laundering Reporting Officer (MLRO). In the US, an equivalent BSA Officer.

This person:
- Owns the AML program
- Files SARs with FinCEN / equivalent
- Is the regulator's named contact for AML matters
- Has personal liability in some jurisdictions

The MLRO must have authority and resources. Founders sometimes try to be MLRO themselves; this works only at very small scale and even then is risky. Hire an experienced MLRO before you operate at scale.

---

## Common Pitfalls

- **Set-and-forget rules.** Rules need quarterly tuning at minimum.
- **No model documentation.** "Why does Tier 2 require source of funds?" needs a documented answer for auditors.
- **Vendor over-reliance.** A vendor's "yes" on KYC is not your safe harbor — you remain responsible.
- **Customer experience scapegoating.** Yes, KYC adds friction; no, "remove the friction" is not a valid program decision.
- **No periodic refresh.** Customer profiles need to be re-verified periodically (commonly annually for low-risk, more often for higher-risk).
- **Untested rules.** Production-tested rules in shadow first; never roll out live without baseline.
- **No exit playbook.** When a customer is exited for AML reasons, the process needs to be documented (regulators will ask).

---

## Building vs. Buying

For early-stage fintech: **buy almost everything.** Identity verification, transaction monitoring, and sanctions screening are commodities at this point — building them is rarely worth the engineering investment.

Build only the orchestration layer: how vendor decisions feed into your workflows, customer experience around verification, and risk-rating model.

Once at scale (millions of customers, ML on transaction data starts to outperform rules), consider building components.
