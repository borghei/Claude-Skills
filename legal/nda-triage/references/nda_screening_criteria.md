# NDA Screening Criteria

Complete evaluation reference for rapid NDA triage. Covers all 10 screening criteria with detailed sub-items, classification rules, and redline approaches for common issues.

---

## Table of Contents

- [Classification Framework](#classification-framework)
- [Criterion 1: Agreement Structure](#criterion-1-agreement-structure)
- [Criterion 2: Definition of Confidential Information](#criterion-2-definition-of-confidential-information)
- [Criterion 3: Obligations](#criterion-3-obligations)
- [Criterion 4: Standard Carveouts](#criterion-4-standard-carveouts)
- [Criterion 5: Permitted Disclosures](#criterion-5-permitted-disclosures)
- [Criterion 6: Term and Duration](#criterion-6-term-and-duration)
- [Criterion 7: Return and Destruction](#criterion-7-return-and-destruction)
- [Criterion 8: Remedies](#criterion-8-remedies)
- [Criterion 9: Problematic Provisions](#criterion-9-problematic-provisions)
- [Criterion 10: Governing Law](#criterion-10-governing-law)
- [Common NDA Issues and Redline Approaches](#common-nda-issues-and-redline-approaches)

---

## Classification Framework

### Overall Classification Rules

| Classification | Trigger | Routing | Timeline |
|---------------|---------|---------|----------|
| GREEN | All 10 criteria pass; no problematic provisions; all 5 carveouts present | Business approver | Sign within 24 hours |
| YELLOW | 1-2 criteria fail; minor issues detected; 1-2 missing carveouts | Legal counsel | Review within 48 hours |
| RED | 3+ criteria fail; critical provisions (non-compete, IP assignment); 3+ missing carveouts | Senior counsel | Review within 5 business days |

### Per-Criterion Classification Impact

| Criterion | GREEN | YELLOW | RED |
|-----------|-------|--------|-----|
| Agreement Structure | Parties, purpose, direction clear | One element unclear | Parties unidentified or structure ambiguous |
| Definition | Bounded, with marking requirement | Broad but reasonable | "All information of any kind" with no limits |
| Obligations | Standard of care, use restriction, disclosure limits | One element missing | No obligations specified |
| Standard Carveouts | All 5 present | 1-2 missing | 3+ missing |
| Permitted Disclosures | Representatives with need-to-know | Representatives without need-to-know | No permitted disclosures (or overly broad) |
| Term & Duration | 2-5 years with reasonable survival | 1-year or 7+ year term | Perpetual with no termination |
| Return/Destruction | Return or destroy with certification | Return or destroy without certification | No return/destruction obligation |
| Remedies | Injunctive relief, no liquidated damages | Injunctive relief with broad indemnification | Liquidated damages or penalty clauses |
| Problematic Provisions | None detected | Residuals or audit rights | Non-compete, non-solicitation, IP assignment, exclusivity |
| Governing Law | Favorable or neutral jurisdiction | Unfamiliar but acceptable jurisdiction | No governing law or hostile jurisdiction |

---

## Criterion 1: Agreement Structure

### What to Check

| Sub-Item | Standard | Red Flag |
|----------|----------|----------|
| Parties | Full legal names with entity type | Vague references ("the parties") |
| Direction | Clearly mutual or one-way | Ambiguous (purports to be mutual but obligations are one-sided) |
| Purpose | Specific purpose stated | No purpose or overly broad ("any purpose") |
| Effective Date | Clearly stated or determinable | Missing or ambiguous |
| Signatures | Authorized signatories identified | No signature block or unauthorized signer |

### Mutual vs. One-Way

| Type | When Appropriate | Key Difference |
|------|-----------------|----------------|
| Mutual (Bilateral) | Both parties will share confidential information | Both parties have equal obligations |
| One-Way (Unilateral) | Only one party discloses confidential information | Only receiving party has obligations |

**Watch for:** NDAs labeled "mutual" but with one-sided obligations. Check that both parties are bound by the same restrictions.

---

## Criterion 2: Definition of Confidential Information

### What to Check

| Sub-Item | Standard | Red Flag |
|----------|----------|----------|
| Scope | Bounded to information related to the stated purpose | "All information of any kind, in any form" |
| Marking | Written info marked "Confidential"; oral confirmed in writing within 10-30 days | No marking requirement (everything is confidential) |
| Form | Covers written, oral, visual, and electronic | Limited to only one form |
| Specificity | Categories of information listed | Vague catch-all with no categories |
| Exclusions | Standard carveouts referenced | No exclusions from definition |

### Definition Scope Spectrum

| Scope Level | Example Language | Classification |
|-------------|-----------------|----------------|
| Narrow (best) | "Information specifically designated as Confidential and relating to [purpose]" | GREEN |
| Standard | "Non-public information relating to the business, technology, or finances of the disclosing party" | GREEN |
| Broad | "Any and all information disclosed by either party, whether written, oral, or visual" | YELLOW |
| Overbroad | "All information of any kind, nature, or description, in any form or medium, relating to the disclosing party or its business" | YELLOW/RED |

---

## Criterion 3: Obligations

### What to Check

| Sub-Item | Standard | Red Flag |
|----------|----------|----------|
| Standard of Care | "Reasonable care" or "same degree of care as own confidential information" | "Absolute" or "best efforts" to protect |
| Use Restriction | Use solely for the stated purpose | No use restriction |
| Disclosure Limits | Limit to need-to-know personnel | No limits on internal disclosure |
| Written Agreements | Require written confidentiality agreements from recipients | No downstream protection required |
| Security Measures | Reasonable technical and organizational measures | Specific expensive security requirements |

### Standard of Care Comparison

| Standard | Meaning | Appropriateness |
|----------|---------|-----------------|
| "Reasonable care" | Objectively reasonable measures | Market standard; recommended |
| "Same degree of care" | Same as party uses for own information | Common; acceptable |
| "Best efforts" | Highest possible standard | Overly burdensome; negotiate down |
| "Absolute" | Guarantees no disclosure | Unacceptable; no party can guarantee |

---

## Criterion 4: Standard Carveouts

All five of the following carveouts must be present for GREEN classification.

### The Five Required Carveouts

| # | Carveout | Standard Language | Why Required |
|---|----------|-------------------|--------------|
| 1 | Public Knowledge | "Information that is or becomes publicly available through no fault of the receiving party" | Cannot restrict public information |
| 2 | Prior Possession | "Information that was already known to the receiving party prior to disclosure, as documented by written records" | Protects pre-existing knowledge |
| 3 | Independent Development | "Information independently developed by the receiving party without use of or reference to the confidential information" | Protects internal R&D and innovation |
| 4 | Third-Party Receipt | "Information received from a third party who is not under a confidentiality obligation to the disclosing party" | Cannot restrict information freely available from others |
| 5 | Legal Compulsion | "Information required to be disclosed by law, regulation, court order, or governmental authority, provided the receiving party gives prompt notice" | Cannot violate legal obligations |

### Missing Carveout Impact

| Missing Carveout | Risk Level | Impact |
|-----------------|-----------|--------|
| Public Knowledge | YELLOW | May be implied by law, but should be explicit |
| Prior Possession | YELLOW | Creates risk of contamination claims against pre-existing knowledge |
| Independent Development | YELLOW | Can block entire R&D programs; high-impact for technology companies |
| Third-Party Receipt | YELLOW | Forces due diligence on every piece of information received from third parties |
| Legal Compulsion | YELLOW | May be implied by law, but notice obligation is important |
| Any 3+ missing | RED | Fundamentally deficient NDA; requires comprehensive redline |

### Legal Compulsion Sub-Requirements

The legal compulsion carveout should include:

| Element | Standard | Preferred |
|---------|----------|-----------|
| Prompt notice to discloser | Required | "Promptly, and in any event prior to disclosure" |
| Cooperation with protective order | Recommended | "Cooperate with efforts to obtain protective order" |
| Minimize scope of disclosure | Recommended | "Disclose only the minimum amount required" |
| Waiver if notice impossible | Recommended | "If notice is prohibited by law, waived" |

---

## Criterion 5: Permitted Disclosures

### What to Check

| Sub-Item | Standard | Red Flag |
|----------|----------|----------|
| Representatives | Employees, officers, directors with need-to-know | No specification of who may receive |
| Advisors | Legal counsel, accountants, financial advisors | Advisors excluded from permitted recipients |
| Affiliates | Subsidiaries and parent companies | Affiliates excluded (may need cross-entity sharing) |
| Need-to-Know | Requirement that recipients have a need-to-know | No need-to-know filter |
| Downstream Obligations | Recipients bound by confidentiality | No downstream binding requirement |

---

## Criterion 6: Term and Duration

### What to Check

| Sub-Item | Standard | Red Flag |
|----------|----------|----------|
| Agreement Term | 2-5 years | Perpetual or >10 years |
| Survival Period | 2-3 years after termination | No survival or perpetual survival |
| Termination Right | Either party with 30-60 day notice | No termination right |
| Early Termination | For cause or convenience | No early termination option |

### Term Ranges

| Duration | Classification | Typical Context |
|----------|---------------|-----------------|
| 1-2 years | GREEN | Short-term project evaluations |
| 2-5 years | GREEN | Standard business relationships |
| 5-7 years | YELLOW | Long-term partnerships; acceptable with justification |
| 7+ years | YELLOW/RED | Unusual; requires justification |
| Perpetual | RED | Unacceptable unless trade secret protection with termination right |

### Survival Period Ranges

| Survival | Classification | Notes |
|----------|---------------|-------|
| 1-2 years | GREEN | Minimum acceptable |
| 2-3 years | GREEN | Market standard |
| 3-5 years | GREEN | Common for sensitive information |
| 5+ years | YELLOW | May be appropriate for trade secrets |
| Perpetual | YELLOW/RED | Acceptable only for trade secrets with clear definition |

---

## Criterion 7: Return and Destruction

### What to Check

| Sub-Item | Standard | Red Flag |
|----------|----------|----------|
| Trigger | Upon request or termination | No trigger specified |
| Options | Return or destroy, at receiving party's election | Only return (may be impractical for electronic data) |
| Timeline | Within 30 days of request | No timeline or unreasonably short (e.g., 24 hours) |
| Certification | Written certification of destruction | No certification required |
| Retention Exception | May retain copies required by law or internal backup policy | No retention exception (impractical for automated backups) |

---

## Criterion 8: Remedies

### What to Check

| Sub-Item | Standard | Red Flag |
|----------|----------|----------|
| Injunctive Relief | Available without bond | No mention of equitable remedies |
| Damages | Standard breach-of-contract damages | Liquidated damages or penalty clauses |
| Indemnification | Not standard in NDAs | Broad indemnification obligation |
| Limitation of Liability | Not standard in NDAs | Unlimited liability for breach |
| Prevailing Party Fees | Optional; acceptable either way | Mandatory fee-shifting in one direction only |

### Remedy Red Flags

| Provision | Severity | Why Problematic |
|-----------|----------|-----------------|
| Liquidated damages ($X per breach) | RED | Transforms NDA into penalty contract; disproportionate to actual harm |
| Unlimited liability for breach | YELLOW | Standard NDAs rely on actual damages; uncapped exposure is excessive |
| One-way indemnification | YELLOW | Shifts all risk to one party; inappropriate for a confidentiality agreement |
| Specific performance mandated | GREEN | Standard and appropriate for confidentiality obligations |

---

## Criterion 9: Problematic Provisions

These provisions are NOT standard in NDAs and should trigger escalation.

### Provision Risk Classification

| Provision | Severity | Description | Standard Position |
|-----------|----------|-------------|-------------------|
| Non-Solicitation | RED | Restricts hiring or soliciting employees/customers | Remove entirely; not appropriate for NDA |
| Non-Compete | RED | Restricts competitive business activities | Remove entirely; requires separate agreement |
| Exclusivity | RED | Limits engagement with other parties | Remove entirely; NDA is not an exclusivity agreement |
| IP Assignment | RED | Transfers intellectual property rights | Remove entirely; NDA protects information, not transfers IP |
| Broad License Grant | RED | Grants license to use confidential information | Remove entirely; conflicts with purpose of NDA |
| Liquidated Damages | RED | Pre-determined penalty for breach | Remove; rely on standard breach remedies |
| Residuals Clause | YELLOW | Allows use of ideas retained in unaided memory | Remove or narrow to exclude trade secrets explicitly |
| Audit Rights | YELLOW | Allows inspection of premises or systems | Remove or limit to annual with notice |
| Standstill Provision | YELLOW | Restricts acquisition activities | Flag for M&A counsel; may be appropriate in some contexts |

### Residuals Clause Deep Dive

A residuals clause typically allows a party to use "general ideas, concepts, know-how, and techniques" retained in the "unaided memory" of individuals who had access to confidential information.

**Why it is problematic:**
- Effectively creates a carveout that swallows the NDA protection
- Difficult to prove what was "retained in unaided memory" vs. what was memorized deliberately
- Can be used to justify use of trade secrets

**Standard position:** Remove the residuals clause entirely. If counterparty insists, narrow it to:
- Exclude trade secrets explicitly
- Require that individuals did not intentionally memorize information
- Limit to general concepts, not specific data points or algorithms

---

## Criterion 10: Governing Law

### What to Check

| Sub-Item | Standard | Red Flag |
|----------|----------|----------|
| Governing Law | Specified and acceptable | No governing law or hostile jurisdiction |
| Jurisdiction | Courts identified | No jurisdiction specified |
| Dispute Resolution | Litigation or arbitration specified | No dispute resolution mechanism |
| Venue | Specific venue identified | Inconvenient venue |

### Jurisdiction Preference Tiers

| Tier | Jurisdictions | Notes |
|------|---------------|-------|
| Preferred | Home state/country of your entity | Best: familiar law, local counsel, convenient |
| Acceptable | Delaware, New York, England, Singapore | Neutral, well-developed commercial law |
| Review Required | Other US states, EU member states | May be acceptable; requires counsel assessment |
| Escalate | Non-Western jurisdictions, unfamiliar legal systems | Requires senior counsel review |

---

## Common NDA Issues and Redline Approaches

| Issue | Detection Signal | Redline Approach | Fallback |
|-------|-----------------|------------------|----------|
| Overbroad definition | "All information of any kind" | Narrow to information marked or identified as confidential | Add marking requirement with 10-day oral confirmation window |
| Missing independent development carveout | Absent from exclusions section | Add standard carveout language | At minimum: "independently developed without use of Confidential Information as demonstrated by documentary evidence" |
| Non-solicitation clause | "Shall not solicit" employees or customers | Delete entire provision | If counterparty insists: limit to direct solicitation of specific named individuals for 12 months |
| Broad residuals clause | "Unaided memory" with no limitations | Delete entirely | Narrow: exclude trade secrets, require non-intentional retention, limit to general concepts |
| Perpetual obligations | "In perpetuity" or no term specified | Add 3-year term with 2-year survival | Accept 5-year term with 3-year survival |
| No return/destruction | Absent from agreement | Add return or destroy within 30 days of request/termination | Accept retention exception for legal and backup copies with continued confidentiality |
| IP assignment in NDA | "Assigns all right, title, interest" | Delete entirely; NDA is not an IP agreement | If counterparty insists: this is a fundamental scope issue requiring separate negotiation |
| One-sided obligations in "mutual" NDA | Mutual header but only one party obligated | Revise to make obligations truly mutual | Accept one-way structure if appropriate, but relabel accurately |
| No legal compulsion notice | Legal compulsion carveout without notice requirement | Add: "Shall provide prompt written notice prior to disclosure" | Add: "Shall provide notice to the extent legally permitted" |
| Missing effective date | No date on agreement | Add effective date provision | Use "date of last signature" as effective date |
