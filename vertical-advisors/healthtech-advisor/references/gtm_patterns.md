# Healthtech GTM Patterns

Healthtech has distinctive go-to-market motions per buyer segment. Picking the wrong motion is one of the most common reasons healthtech startups fail despite real product demand.

---

## The Six Buyer Segments

| Buyer | Primary value | Sales cycle | Contract | ACV range |
|-------|---------------|-------------|----------|-----------|
| Payor (insurance) | Cost reduction, member outcomes, regulatory compliance | 18-36 months | Multi-year, capitated or PMPM | $1M-$50M |
| Provider (hospital/clinic) | Workflow efficiency, revenue capture, quality metrics | 9-18 months | 3-5 year, PEPM or per-encounter | $100K-$10M |
| Employer (self-insured) | Healthcare cost reduction, employee experience | 6-12 months | Annual or multi-year, PMPM | $100K-$10M |
| Individual (D2C) | Personal health outcome | 1-30 days | Subscription or one-time | $10-$200/year |
| Pharma | Drug development, real-world evidence, patient services | 12-24 months | Multi-year, milestone-based | $500K-$50M |
| Government (Medicare, Medicaid, VA) | Cost, access, regulatory mandate | 12-36 months | Contract vehicle (GSA, IDIQ) | $100K-$100M |

A startup picking "all of the above" almost always under-resources each motion and wins none.

---

## Payor Sales

**Buyer:** Health plans (Aetna, BCBS, UnitedHealth, smaller regionals, Medicare Advantage plans)

**What they buy:**
- Cost reduction (clinical or administrative)
- Member-outcome improvement (Star Ratings, HEDIS, CAHPS)
- Regulatory compliance (interoperability, transparency)
- New member acquisition / retention

**How they buy:**
- 18-36 month cycle from first contact to contract
- Decision-makers: Chief Medical Officer, Chief Innovation Officer, VP Clinical Operations, VP IT, Procurement
- Pilots common (often unpaid or token-paid for 6-12 months)
- Procurement and legal review are slow and detailed

**What works:**
- Quantitative ROI claim grounded in published or peer-reviewed evidence
- Reference customers from peer payors
- Co-investment from payor for the pilot
- Strong clinical and actuarial advisors

**What doesn't work:**
- Generic "AI healthcare" pitches
- Founder-led sales without payor-experienced sales hires
- Trying to charge for pilots when peers offer them free

**Capital intensity:** High — long sales cycle requires runway. Most payor-focused healthtechs need $20M+ to reach meaningful ARR.

---

## Provider Sales (Hospital / Health System)

**Buyer:** Hospitals, health systems, large physician groups

**What they buy:**
- Workflow efficiency for clinicians (which directly affects retention)
- Revenue cycle optimization
- Quality metrics improvement
- IT modernization

**How they buy:**
- 9-18 month cycle for enterprise deals
- Decision-makers: CMIO, CMO, CIO, CFO, COO, sometimes CEO
- IT review for EHR integration is gating
- Procurement / GPO contracts often involved

**What works:**
- Tight integration with the dominant EHR (Epic, Cerner, athena, Meditech)
- Clinician-led champion model
- Reference sites within the same health system or peer system
- Outcomes data, not feature lists

**What doesn't work:**
- "We don't need EHR integration" — you do
- Selling to IT before clinical buy-in
- Selling to clinical without IT pre-alignment

**EHR integration:**
- **Epic** — App Orchard / Epic on FHIR — partnership program with technical and business hurdles
- **Cerner / Oracle Health** — Code Console — lower bar, faster iteration
- **athenahealth** — More open marketplace
- **Smaller EHRs** — vary widely

**Capital intensity:** High — sales cycle still long, integration heavy. Plan $15M+ runway for meaningful ARR.

---

## Employer Sales (Self-Insured)

**Buyer:** Mid-market and large self-insured employers; benefits brokers and consultants

**What they buy:**
- Healthcare cost reduction
- Employee experience and retention
- Population-health programs (musculoskeletal, behavioral health, fertility, etc.)
- Wellness and prevention

**How they buy:**
- 6-12 month cycle, aligned to benefits enrollment cycles (typically Q1-Q2 for Jan 1 starts)
- Decision-makers: Head of Benefits, CHRO, sometimes CFO
- Brokers (Mercer, Aon, Alliant, regional) heavily influence
- Consultants validate ROI claims

**What works:**
- Clear ROI framing in employer terms (PMPM cost, claims cost reduction, productivity)
- Broker / consultant relationships
- Carve-out vs. carve-in clarity (whether your service replaces or supplements existing benefits)
- Employer references at similar headcount and industry

**What doesn't work:**
- Selling to HR generalists at small employers (under 5,000 lives) — not enough volume to justify carve-out
- Generic wellness pitches without measurable health outcomes
- Tech-heavy pitches to non-technical buyers

**Capital intensity:** Moderate — faster cycle than payor, more achievable for $5M-$15M Series A.

---

## Direct-to-Consumer

**Buyer:** Individuals

**What they buy:**
- Convenience (telehealth)
- Specific condition management (mental health, dermatology, fertility, etc.)
- Wellness and lifestyle
- Cosmetic / non-essential health (whitening, aesthetic dermatology)

**How they buy:**
- Days to weeks from first touch to purchase
- Decision-maker: the individual (often paying out of pocket or via FSA/HSA)
- Friction killers: pricing transparency, asynchronous flows, mobile-first

**What works:**
- Specific, well-defined consumer problems (better treatment than current SoC, faster, cheaper, or all three)
- Strong brand and demand generation
- Tight unit economics (CAC payback < 12 months)
- Insurance reimbursement increasingly important even in D2C

**What doesn't work:**
- Generic "healthcare" with no clear category
- Treating consumers like patients in a clinical setting
- Underestimating the cost of CAC in a brand-driven market

**Capital intensity:** Variable — some D2C health verticals (Hims, Ro) reached scale on $50M-$100M; others are venture-incompatible.

**Caveat:** Most "D2C" healthtechs eventually need provider relationships (telehealth requires licensed clinicians; medications require prescriptions). Pure D2C without clinical involvement is rare.

---

## Pharma Sales

**Buyer:** Pharmaceutical companies

**What they buy:**
- Real-world evidence (RWE)
- Clinical trial recruitment, retention, decentralization
- Patient services / hub services
- Companion diagnostics or digital biomarkers
- Marketing / commercialization support

**How they buy:**
- 12-24 month cycle
- Decision-makers: vary widely by use case — Medical Affairs, Clinical Operations, Commercial, Patient Services
- Procurement is enterprise-grade

**What works:**
- Specific use case tied to a drug or therapeutic area
- Validated outcomes from prior pharma engagements
- Regulatory expertise (FDA submissions, RWE methodology)

**What doesn't work:**
- Generic "pharma platform" pitches
- Founder unfamiliarity with drug development cycle

**Capital intensity:** Variable — pharma deals are large but slow.

---

## Government Sales

**Buyer:** Medicare, Medicaid, VA, IHS, military health

**What they buy:**
- Specific RFP-driven solutions
- Pilot / innovation programs (CMMI, VA Innovation Network)

**How they buy:**
- 12-36 months
- Contract vehicles (GSA Schedule, IDIQ, SBIR, OTA)
- Heavy compliance (FedRAMP, FISMA)

**What works:**
- Persistence and capital
- FedRAMP authorization (or partner with one already authorized)
- Specific RFP responses, not generic capability decks

**What doesn't work:**
- Trying to sell direct without contract vehicle
- Underestimating compliance burden

**Capital intensity:** Very high — months to years before first dollar.

---

## Common Mistakes

1. **Picking too many buyers.** Each of the above requires a specialized sales motion, team, and content. Pick one for first $1M-$5M ARR; expand only after that motion is repeatable.
2. **Founder-led without segment expertise.** Payor and provider sales especially require sales hires who have done the same motion before.
3. **Pivoting to a new buyer mid-stride.** Each pivot resets the sales motion clock.
4. **Underestimating EHR integration.** Allow 6-12 months for first integration; 3-6 for subsequent.
5. **Pricing without market reference.** Healthtech pricing benchmarks vary wildly by segment; getting it 10x wrong is common.
6. **Confusing pilot revenue with real revenue.** Most healthtech pilots don't convert; track conversion rate carefully.
