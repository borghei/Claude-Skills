# MLS and Brokerage Mechanics

Most proptech businesses interact with MLS (Multiple Listing Service) data and brokerage operations. The mechanics matter because access, licensing, and structure determine what's possible and what's permitted.

---

## MLS Basics

The Multiple Listing Service is a private, member-only database of properties for sale (and sometimes for lease) maintained by local brokers. There is **no national MLS**: there are ~580 MLS organizations across the US, each governed by its own rules.

**Membership:**
- Broker memberships (firms)
- Agent memberships (individuals affiliated with member brokers)
- Some MLSs have other categories (lender, appraiser)

**Data access methods:**
- **IDX (Internet Data Exchange):** Public-facing display of listings; available to broker members and their licensed websites
- **VOW (Virtual Office Website):** Display to registered "consumers" of the broker; shows more data than IDX
- **RESO Web API:** Modern API standard for both IDX and VOW
- **MLS-direct feed:** Bulk data feed for member use
- **Aggregator (CoreLogic, Black Knight):** Reseller of MLS data to large platforms

**Display rules:** Each MLS sets rules — some require consumer registration, some allow only X days of historical data, some prohibit display of sold listings. Some MLSs are notoriously restrictive (e.g., NWMLS in Pacific Northwest).

---

## Brokerage Licensing

To operate as a real estate broker in a US state, the firm and individual brokers must hold state licenses.

**Key roles:**
- **Salesperson / agent:** Licensed individual; must work under a broker
- **Designated broker / managing broker / broker-in-charge:** The firm's licensed broker who supervises agents
- **Firm license:** The brokerage entity's license

**State requirements typically include:**
- Pre-license education (60-180 hours depending on state)
- State exam
- Background check / fingerprinting
- Errors-and-omissions insurance
- Fee
- Continuing education (annual / biennial)

**Operating in multiple states:**
- Each state requires separate licensure
- Reciprocity exists between some states but is patchy
- Multi-state operations typically require a Designated Broker per state

---

## RESPA Section 8

The Real Estate Settlement Procedures Act prohibits:
- Kickbacks
- Unearned fees
- Fee splitting

In settlement services (title, escrow, mortgage, insurance, etc.) related to federally-related residential transactions.

**What this means in practice:**
- "Pay me for sending you customers" arrangements are illegal
- Affiliated Business Arrangements (ABAs) — where a broker has an affiliated title company — require:
  - Written disclosure to consumer
  - Customer cannot be required to use the affiliated business
  - Must comply with structural rules

**This kills many "lead generation" / "referral fee" business models** in proptech that look fine on the surface. Engage RESPA-specialist counsel early.

---

## Fair Housing

The Fair Housing Act prohibits discrimination based on:
- Race / color
- Religion
- Sex (including sexual orientation, gender identity post-Bostock)
- National origin
- Familial status
- Disability

Plus state and local additional protected classes (source of income, etc.).

**Implications for proptech:**
- Listings and search algorithms cannot rank by demographic characteristics
- "School quality" and "neighborhood quality" filters have been challenged as proxies for race
- Tenant screening algorithms must be auditable for disparate impact
- Image filters in listings (e.g., excluding listings showing certain neighborhoods) have triggered enforcement
- Targeted advertising can violate Fair Housing if the targeting excludes protected classes

The 2019 settlement between Facebook and HUD (and subsequent FCC actions) significantly raised enforcement attention on algorithmic Fair Housing.

---

## Brokerage Models for Proptech

Proptech companies that touch transactions choose one of these structures:

### Get the broker license (own brokerage)
- Examples: Compass, Redfin, Side
- Cost: capital + state-by-state licensing
- Control: full
- Margin: full commission economics

### Partner with a brokerage
- Examples: Many "tech-enabled" but white-label brokerages
- Cost: lower up-front
- Control: shared with broker partner
- Margin: split with broker partner

### Stay outside the transaction
- Examples: Pure data / SaaS / lead-gen products
- Cost: no licensing
- Control: bounded — you don't touch the regulated transaction
- Margin: no commission economics, but lower regulatory risk

### Refer to brokers
- Examples: HomeLight (consumer-side referrals), various lead-gen products
- Cost: low
- Margin: referral fees (subject to RESPA scrutiny)
- Compliance: heavy structuring needed

The 2023-2024 NAR antitrust settlements have **reshuffled** transaction-side economics significantly. Buyer-side commissions are no longer presumptively paid by sellers; this changes brokerage business models materially. Counsel involvement is essential.

---

## RESO Web API

Real Estate Standards Organization's modern API. Increasingly the standard for MLS data access.

**Why it matters:**
- Cleaner than legacy IDX/VOW formats
- Better interop across MLSs
- Granular permissions for IDX vs VOW vs full feed
- Photo / media handling improved

Most new MLSs offer RESO Web API. Older MLSs are migrating. If you're building, prefer RESO over legacy formats where available.

---

## Common Mistakes

1. **Skipping the broker conversation.** "We don't need a broker — we're tech." If you touch the transaction, you do.
2. **MLS-by-MLS scaling shock.** Adding new MLSs is slow, paperwork-heavy, and varies in technical detail.
3. **RESPA blindness.** Many lead-gen and referral models are quietly illegal until restructured.
4. **Algorithm-blind fair housing.** Default ranking algorithms can produce disparate impact even with no explicit demographic data.
5. **Underestimating per-state cost.** 50-state operation can mean 50 brokerage-license maintenance burdens.
6. **Aggregator dependency.** Aggregators (CoreLogic, Black Knight) can pull data on you; have a multi-source plan.

---

## Resources

- **NAR (National Association of Realtors):** nar.realtor — industry context
- **RESO (Real Estate Standards Organization):** reso.org — data standards
- **CFPB RESPA pages:** consumerfinance.gov — settlement services rules
- **HUD Fair Housing:** hud.gov/fair_housing
- **State real estate regulator websites** — listed at arello.com (regulator association)

For binding decisions, engage real-estate-specialist counsel.
