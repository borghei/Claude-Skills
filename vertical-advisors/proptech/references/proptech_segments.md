# Proptech Segments

Proptech is fragmented into segments with very different economics, regulatory exposure, and capital requirements. Knowing which segment you're in is the foundation of strategy.

---

## Segment 1: Transaction

**What it does:** Helps people buy / sell properties. Includes iBuyers (Opendoor-style), tech-enabled brokerages (Compass, Redfin), digital brokerages, and transaction marketplaces.

**Examples:** Opendoor, Offerpad (iBuyers); Compass, Side, Redfin (brokerages); Realtor.com, HomeLight (matching/referral)

**Regulatory:**
- Real estate brokerage license per state where you operate
- Antitrust scrutiny on commission structures (post-NAR settlement, dramatically changed dynamics)
- RESPA Section 8 on referral kickbacks
- Fair housing in customer-facing flows
- iBuyers face additional securities considerations if syndicated capital

**Capital intensity:** Highest in proptech for iBuyers (huge balance sheet for inventory). Brokerages need agent-recruiting capital.

**Common failure modes:** Cyclicality (rate environment kills volume), unit economics that don't survive in tighter markets, agent-network economics (high agent splits compress margins).

---

## Segment 2: Listings & Search

**What it does:** Helps buyers find properties to look at; sometimes provides valuation.

**Examples:** Zillow, Redfin (search); Trulia (legacy, now Zillow-owned); HomeLight; specialty platforms (commercial real estate listings)

**Regulatory:**
- MLS access via IDX (Internet Data Exchange), VOW (Virtual Office Website), or RESO Web API
- Display rules vary by MLS (different MLS rules per metro)
- Fair housing on rankings (filtering by demographics or "school district" can be challenged)

**Business models:**
- Lead-gen to agents (per-lead, $20-$200+ depending on market)
- Referral fees from agents who close
- Premium listings to agents
- Advertising
- Some now offer brokerage services (Zillow tried, retreated)

**Capital intensity:** Moderate; can be efficient at scale but consolidating market makes new entrants hard.

---

## Segment 3: Financing

**What it does:** Originates or facilitates real estate financing.

**Examples:** Better, Rocket (mortgage tech); Roam (assumable mortgages); Hometap, Point (home equity investment); Divvy, Pathway (rent-to-own)

**Regulatory:**
- Mortgage origination requires NMLS individual + company licenses
- State-by-state lender licensing
- CFPB oversight (Reg Z, RESPA, ECOA, HMDA)
- Fair lending (ECOA + state)
- For alternative financing: novel structures often need careful regulatory analysis (is this a loan, an equity investment, or something else?)

**Business models:**
- Origination fees / points
- Interest rate spread (for portfolio lenders)
- Equity sharing (home equity investments)
- SaaS to lenders for back-office

**Capital intensity:** Very high if balance-sheet lender. Moderate if broker / origination-only.

**Cyclicality:** Mortgage volume tracks rates; expect 50-70% revenue swings between cycles.

---

## Segment 4: Property Management

**What it does:** Operates rentals — single-family, multifamily, vacation rental, or commercial.

**Examples:** Roofstock (SFR), AppFolio (multifamily SaaS), Airbnb (STR platform), Vacasa (STR ops), Pacaso (fractional ownership)

**Regulatory:**
- Property manager license required in some states (California, Florida, others)
- State landlord-tenant laws on screening, deposits, evictions, notice periods
- Fair housing on tenant screening (algorithms have been challenged)
- Local STR regulations (some cities ban or heavily regulate)
- Multifamily: rent-control jurisdictions add complexity

**Business models:**
- % of rent collected (typical 8-12% for SFR; lower per unit for multifamily)
- SaaS per-unit/month for property management software
- Service fees (maintenance markup, leasing fees)
- For STR platforms: take rate on bookings

**Capital intensity:** Varies — software low, ownership/operations high.

---

## Segment 5: Services (Insurance, Title, Escrow, Inspection, Moving)

**What it does:** Provides settlement and ancillary services for real estate transactions.

**Examples:** Hippo (insurance), Doma (title), States Title, Hippo Insurance, Porch (services bundle)

**Regulatory:**
- Insurance producer / agency license per state
- Title and escrow licensed in most states
- RESPA Section 8: prohibits kickbacks for referrals to settlement services. Affiliated business arrangements (ABAs) require disclosure and structure.
- State unfair claims practices laws

**Business models:**
- Fee per transaction
- Commission on insurance
- Markup on services

**Capital intensity:** Low to moderate; insurance reserves can be heavy if balance-sheet underwriter.

---

## Segment 6: Data & Infrastructure (B2B SaaS)

**What it does:** Provides software and data to brokerages, agents, lenders, property managers, and other industry players.

**Examples:** AppFolio, Buildium (PM software); Lone Wolf, Real Geeks (agent CRM); Reonomy, CoreLogic (CRE data); Cherre (data infrastructure)

**Regulatory:**
- Lower direct exposure than transaction segments
- But: if your product feeds decisions on lending, leasing, or insurance, fair lending / fair housing implications flow through
- Customer compliance becomes your concern (your customer is the regulated entity)

**Business models:**
- SaaS subscription per seat / per unit / per transaction
- Data licensing
- Marketplace take rates

**Capital intensity:** Standard B2B SaaS economics; faster path to profitability than transaction segments.

---

## Segment 7: Commercial Real Estate (CRE)

A separate world. Different buyers, deal sizes, sales cycles, regulatory regimes.

**Examples:** VTS (CRE leasing tech), Hightower (now VTS), Reonomy (CRE data), Cherre, Yardi/MRI (legacy CRE software)

**Differences from residential:**
- Sophisticated parties (institutions, REITs, family offices)
- Fewer consumer-protection rules
- Larger deal sizes (transactions in millions)
- Longer sales cycles
- Securities considerations for syndications and REITs
- Different software ecosystem

Don't try to serve residential and commercial in one product unless you have very deep domain expertise in both.

---

## Segment Choice Heuristics

| Segment | Capital intensity | Regulatory burden | Cyclicality | Time to revenue |
|---------|-------------------|-------------------|-------------|-----------------|
| Transaction (iBuyer) | Very high | High | Very high | Long |
| Transaction (brokerage) | High | High | High | Medium |
| Listings & Search | Moderate | Moderate (MLS) | Moderate | Medium |
| Financing (origination) | High | Very high | Very high | Long |
| Financing (B2B SaaS) | Low | Moderate | Moderate | Short |
| Property Management (ops) | Low to moderate | Moderate | Moderate | Medium |
| Property Management (SaaS) | Low | Low | Low | Short |
| Services | Low to moderate | High (state by state) | Moderate | Medium |
| Data & Infrastructure | Low | Low | Low | Short |
| CRE (any) | Varies | Lower | Lower | Long (slow buyer) |

**Heuristic:** If you have less than $5M to spend, B2B SaaS / data / infrastructure is the easiest segment to get to revenue. Transaction-side proptech generally needs $20M+ to reach meaningful scale.

---

## Common Mistakes

1. **Picking transaction without capital.** Transaction proptech is capital-intensive; underestimating burn rate is the #1 reason these companies fail.
2. **Ignoring MLS politics.** Each MLS has its own rules; some metros are gated.
3. **Underestimating state-by-state complexity.** A multi-state proptech rollout takes years.
4. **Confusing residential and commercial.** Different industries.
5. **Cyclicality blindness.** Models that work in a hot market collapse in a cool one. Stress-test for ½ market activity.
6. **RESPA naivete.** Every kickback or referral fee on settlement services has been examined; structure carefully.
