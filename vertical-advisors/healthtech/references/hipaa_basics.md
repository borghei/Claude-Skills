# HIPAA Basics for Healthtech Founders

A founder's-eye view of HIPAA — what it is, who it applies to, what compliance means in practice. **Orientation, not legal advice.**

---

## What HIPAA Is

The Health Insurance Portability and Accountability Act (HIPAA), enacted 1996, has two parts most healthtechs care about:

- **Privacy Rule** — what you can and can't do with Protected Health Information (PHI)
- **Security Rule** — how you must protect electronic PHI (ePHI)

Plus:
- **Breach Notification Rule** — what you must do when ePHI is compromised
- **Enforcement Rule** — penalty structure (corrective action plans, fines up to $1.5M/violation/year)

HIPAA is enforced by the HHS Office for Civil Rights (OCR). State Attorneys General also have enforcement authority.

---

## Who HIPAA Applies To

HIPAA applies to two categories:

### Covered Entities (CEs)
- Health plans (Medicare, Medicaid, private insurers)
- Healthcare clearinghouses
- Healthcare providers who electronically transmit health information for HIPAA-covered transactions

If you're a healthcare provider, you're almost certainly a CE.

### Business Associates (BAs)
- Anyone who creates, receives, maintains, or transmits PHI on behalf of a Covered Entity
- Examples: cloud hosting, billing services, EHR vendors, analytics, claims processors, healthtech SaaS serving providers

If your customer is a Covered Entity and your product touches PHI, you're a BA.

### What's NOT under HIPAA
- Consumer wellness data (Fitbit, Apple Health, period trackers) outside a clinical context
- Employer-sponsored wellness programs (in some configurations)
- Direct-to-consumer products with no provider relationship
- Research data (different framework — Common Rule)

> **Caveat:** Even when HIPAA doesn't apply, state laws often do. Washington's My Health My Data Act, California's CMIA, Connecticut's data privacy law, and others extend protections to consumer health data.

---

## What PHI Is

Protected Health Information = individually identifiable health information held or transmitted by a CE or BA.

The "individually identifiable" part is broad. The 18 HIPAA identifiers include obvious ones (name, SSN) and less obvious (dates more granular than year, geographic info smaller than state, biometric identifiers, photos, certain device identifiers).

**Health information** includes anything related to:
- Past/present/future physical or mental health condition
- Healthcare provided to the individual
- Past/present/future payment for healthcare

When you combine "individually identifiable" + "health information" in a CE/BA context, you have PHI.

---

## The Business Associate Agreement (BAA)

A BAA is a contract that:
- Establishes the BA's obligations to safeguard PHI
- Limits what the BA can do with PHI
- Requires the BA to flow down requirements to subcontractors
- Specifies breach notification procedures

**You need a signed BAA before you handle PHI**, both with:
- Each Covered Entity customer (you sign as BA)
- Each subcontractor that handles PHI on your behalf (you sign as the customer's BA, your subcontractor is BA-of-BA)

Common BA-of-BA cases:
- Cloud hosting (AWS, GCP, Azure all offer BAA programs)
- Email / messaging (need BAA with vendor or use HIPAA-specific tooling)
- Analytics (Google Analytics 4 in standard config is NOT BAA-compatible for PHI)
- Customer support (Zendesk, Intercom — depends on configuration)
- Sub-processors of every kind

A missing or wrongly-scoped BAA is a frequent OCR enforcement target.

---

## Privacy Rule Highlights

The Privacy Rule covers permitted uses and disclosures of PHI. Key concepts:

- **Treatment, Payment, Operations (TPO):** PHI can be used for these without explicit patient authorization
- **Patient authorization** required for marketing, sale of PHI, most other uses
- **Minimum necessary:** Only use/disclose the minimum PHI needed for the task
- **De-identification:** PHI that has been properly de-identified per HIPAA standards is no longer PHI
- **Right of access:** Patients can request their records (response timeline rules apply)
- **Notice of Privacy Practices:** Required posting and distribution

---

## Security Rule Highlights

The Security Rule covers safeguards for ePHI in three categories:

### Administrative safeguards
- Risk analysis and management
- Workforce training and access management
- Contingency planning (backup, disaster recovery)
- Periodic evaluation of compliance

### Physical safeguards
- Facility access controls
- Workstation use and security
- Device and media controls

### Technical safeguards
- Access controls (unique user IDs, automatic logoff)
- Audit controls (logging access to ePHI)
- Integrity controls (detection of unauthorized alteration)
- Transmission security (encryption in transit)
- Encryption at rest (technically "addressable" but effectively required)

---

## Breach Notification Rule

A "breach" is any acquisition, access, use, or disclosure of unsecured PHI not permitted by the Privacy Rule, where there is a probability of compromise to PHI.

If a breach occurs:
- Notify individuals within 60 days
- Notify HHS within 60 days (immediately if affecting 500+ individuals in a state)
- Notify media if 500+ individuals in a state
- BAs must notify CEs within timelines specified in the BAA (often shorter)

"Unsecured PHI" generally means PHI not encrypted to NIST standards. Encryption provides safe-harbor from breach notification in most cases.

---

## Common Pitfalls

- **No BAA at all.** "We're not a CE so HIPAA doesn't apply." If you're a BA, you need a BAA. Period.
- **BAA chain breaks.** You have a BAA with your customer but not with your subcontractor. The subcontractor is processing PHI without contractual safeguards. Risk for everyone.
- **Wrong cloud configuration.** AWS / GCP / Azure offer BAA programs but only certain services are covered, and only in certain configurations. Check the matrix.
- **Email / SMS leaks.** Sending PHI in plain email or SMS is a recurring OCR finding. Need encrypted email or HIPAA-specific channels.
- **Mobile-app analytics.** Default analytics SDKs often capture device IDs that are HIPAA identifiers when correlated with health data. Disable or sanitize.
- **Marketing without authorization.** "We email patients about our other services" — this often requires patient authorization and is a common enforcement target.
- **Data sales.** Selling PHI requires explicit patient authorization and is heavily restricted.
- **De-identification done poorly.** "Removing names" is not de-identification. There are two HIPAA-approved methods (Safe Harbor and Expert Determination).

---

## Penalties

OCR penalty structure (current):
- Tier 1: Did not know → $137-$68,928 per violation
- Tier 2: Reasonable cause → $1,379-$68,928 per violation
- Tier 3: Willful neglect, corrected → $13,785-$68,928 per violation
- Tier 4: Willful neglect, not corrected → $68,928-$2,067,813 per violation
- Annual cap per violation type: $2,067,813

Plus state AG actions, private rights of action under some state laws, and reputational damage.

Many cases settle with corrective action plans (CAPs) lasting 2-3 years.

---

## What to Do Before Launch

1. **Engage HIPAA-specialist counsel.** Generic privacy lawyers often miss specifics.
2. **Document scope:** are you a CE, BA, both, or neither? In writing.
3. **Inventory PHI flows:** what comes in, what goes out, what's stored, where.
4. **BAA inventory:** signed with all CEs and all subcontractors handling PHI.
5. **Privacy and Security policies:** documented, trained, attested to.
6. **Risk analysis:** documented; updated annually.
7. **Breach process:** documented; tested.
8. **Workforce training:** on initial onboarding and annually thereafter.
9. **HIPAA-eligible cloud configuration:** verified, documented.

If any of these is "we'll figure it out later," you're not ready to launch with PHI.
