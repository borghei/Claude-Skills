# Value-Based Care Primer

A primer on US healthcare payment models, focused on the shift from fee-for-service to value-based care (VBC). Understanding payment models is essential for healthtech founders selling to payors, providers, or operating in adjacent spaces.

---

## Why Payment Models Matter

In healthcare, **how money flows determines what gets built**. A platform that improves quality but hurts a provider's revenue under fee-for-service won't get adopted, no matter how clinically excellent. The same platform under capitated payment may be exactly what the provider needs.

Most healthtech founders underestimate this. The product-market fit question is not just "does this help patients" but "does this help in a way that aligns with how the buyer gets paid."

---

## Fee-for-Service (FFS)

**How it works:** Provider gets paid for each service rendered — visit, procedure, lab, imaging.

**Incentives:**
- Volume of services
- Higher-coded services (better-paying ICD-10 / CPT combinations)
- Specialty referrals (each one bills)

**What works in FFS:**
- Documentation tools that capture more billable services
- Coding optimization (within compliance)
- Revenue cycle (claims, denials, appeals)
- Throughput improvements

**What doesn't work in FFS:**
- Programs that reduce visit volume
- Programs that shift care to lower-paid settings
- Population-health tools (no payment for prevention)

Most US healthcare is still primarily FFS, despite a decade of "VBC is coming."

---

## Value-Based Care Models

VBC ties payment to outcomes, quality, or risk-bearing — not to service volume. The category includes many specific models.

### Pay-for-Performance (P4P)
- Modest bonuses or penalties for hitting quality metrics
- Lowest risk for provider
- Common in commercial payor contracts

### Bundled Payments
- Single payment for an episode of care (e.g., joint replacement bundle covers surgery + 90 days post)
- Provider keeps the difference if costs are below bundle price; loses if above
- Used by CMS BPCI programs

### Shared Savings
- Provider and payor share in savings vs. a benchmark
- Provider has upside but limited downside (one-sided)
- Or two-sided risk (savings AND losses shared)

### Accountable Care Organizations (ACOs)
- Providers organized to take responsibility for total cost of care for an attributed population
- Shared savings (one-sided) or shared risk (two-sided) with Medicare
- Programs: MSSP, ACO REACH, commercial-ACO contracts

### Capitation
- Fixed per-member-per-month (PMPM) payment regardless of services rendered
- Provider keeps difference if cost < PMPM; loses if cost > PMPM
- Pure form: very rare; semi-capitation (cap on certain services) more common

### Global Capitation / Full Risk
- Provider takes full responsibility for total cost of care for population
- Common in Medicare Advantage delegated arrangements
- High-risk, high-reward

### Direct Contracting / ACO REACH
- CMS programs where providers contract directly for full risk
- Replaces some Medicare ACO programs

---

## Medicare Advantage

Important to understand because so much VBC happens here:

- Private health plans (Medicare Advantage Organizations, MAOs) contract with CMS to cover Medicare beneficiaries
- MAOs receive a capitated PMPM from CMS, adjusted for beneficiary risk (HCC scoring)
- MAOs delegate risk to providers, often via:
  - Capitation arrangements (providers paid PMPM)
  - Shared-risk arrangements
  - Full-risk delegated arrangements (provider takes total cost of care)

This creates a market for healthtech tools that:
- Improve risk-adjustment accuracy (HCC capture)
- Reduce avoidable utilization (ER visits, readmissions)
- Improve Star Ratings (CMS quality metrics — affects MAO reimbursement)
- Enable provider risk-bearing (analytics, patient engagement, care management)

---

## What Each Model Means for Healthtech

### Selling under FFS
- Frame value as revenue increase or cost reduction at margin
- "Capture more billable encounters" / "reduce no-shows" / "denial reduction"
- Avoid "reduce ER visits" framing — provider may earn from those

### Selling into VBC contracts
- Frame value as total-cost-of-care reduction or quality-metric improvement
- "Reduce admissions per 1000" / "raise Star Rating from X to Y"
- Quantify in PMPM terms — that's how the buyer thinks

### Selling to risk-bearing providers
- Frame value as risk margin improvement
- Capitated providers want: lower utilization, better risk capture, lower per-member cost
- Risk-bearing providers will pay for tools that protect their margin

### Selling to payors
- Frame value as medical-loss-ratio (MLR) improvement, member outcome improvement, or Star Rating uplift
- Quantify in claims-cost reduction or member-retention terms

---

## Key Acronyms / Concepts

- **PMPM** — per-member-per-month (capitated payment unit)
- **PEPM** — per-employee-per-month (employer benefit pricing unit)
- **MLR** — Medical Loss Ratio (% of premiums spent on care vs. admin)
- **HCC** — Hierarchical Condition Categories (Medicare Advantage risk adjustment)
- **HEDIS** — quality measures used by NCQA (heavily relevant for payors)
- **CAHPS** — patient experience surveys
- **Star Ratings** — CMS quality ratings for MA plans (1-5 stars; 4+ stars get bonus payments)
- **MSSP** — Medicare Shared Savings Program
- **ACO REACH** — CMS direct-contracting program
- **VBP** — Value-Based Purchasing (CMS hospital quality program)

---

## Common Mistakes

- **Building for VBC but selling to FFS.** A great total-cost-of-care reducer that pitches to a fee-for-service practice is selling them on losing revenue.
- **Ignoring risk adjustment.** Many "outcomes" comparisons are useless without risk-adjustment context — sicker patients have worse outcomes regardless of care quality.
- **Confusing P4P with capitation.** "Value-based" covers a wide spectrum of risk; the specific model determines what tools have value.
- **Underestimating the PMPM math.** PMPM contracts have economics that often surprise founders — small per-member numbers, large populations.
- **Pure VBC focus when most market is still FFS.** Paint the road map to a hybrid market reality.

---

## Resources

- **CMS Innovation Center (CMMI):** innovation.cms.gov
- **NEJM Catalyst:** catalyst.nejm.org — VBC research
- **Health Affairs:** healthaffairs.org — policy and payment model deep dives
- **Rock Health / SVB digital-health reports** — market context
- **AHIP** (America's Health Insurance Plans) — payor industry context

For binding decisions on payment-model strategy, engage healthcare-finance specialists.
