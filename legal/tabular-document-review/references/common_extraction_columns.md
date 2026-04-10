# Common Extraction Columns

Pre-defined column sets for common legal document review scenarios.

## Table of Contents

- [Contract Review Columns](#contract-review-columns)
- [NDA Review Columns](#nda-review-columns)
- [Employment Agreement Columns](#employment-agreement-columns)
- [Lease Review Columns](#lease-review-columns)
- [Using Column Sets](#using-column-sets)
- [Creating Custom Columns](#creating-custom-columns)

## Contract Review Columns

Standard extraction columns for commercial contract review.

| # | Column | Description | Where to Look | Example Values |
|---|--------|-------------|---------------|----------------|
| 1 | Parties | All contracting parties with full legal names | Preamble, first page, recitals | "Acme Corporation, a Delaware corporation" |
| 2 | Effective Date | Date the agreement becomes effective | Preamble, definitions section, signature page | "January 15, 2026" or "upon mutual execution" |
| 3 | Term | Duration of the agreement | Term section, typically Article/Section 2 or 3 | "3 years from Effective Date" |
| 4 | Renewal | Auto-renewal terms and notice period for non-renewal | Term section, often subsection of Term | "Auto-renews for 1-year periods unless 90 days notice" |
| 5 | Governing Law | Jurisdiction whose laws govern the agreement | Near end; "Governing Law" or "Choice of Law" clause | "State of Delaware" |
| 6 | Liability Cap | Maximum aggregate liability amount or formula | Limitation of Liability section | "$5,000,000" or "12 months of fees paid" |
| 7 | Indemnification | Indemnification obligations and scope | Indemnification section, often a separate article | "Each party indemnifies for third-party claims arising from breach" |
| 8 | IP Ownership | Intellectual property ownership and license grants | IP section, license grants, work product | "All work product owned by Client" |
| 9 | Termination Rights | Events triggering termination and notice requirements | Termination section | "Either party may terminate for material breach with 30 days cure" |
| 10 | Data Protection | Data protection, privacy, or security obligations | Data protection section, exhibit, or DPA | "Processor obligations per GDPR Art. 28" |

### Contract Review: Where to Find Each Column

| Column | Primary Location | Secondary Location | Fallback |
|--------|-----------------|-------------------|----------|
| Parties | Page 1, preamble | Recitals | Signature page |
| Effective Date | Preamble | Definitions | Signature page date |
| Term | "Term" section | "Duration" section | First substantive article |
| Renewal | Sub-section of Term | Separate "Renewal" clause | Termination section |
| Governing Law | End of agreement | "General Provisions" | Signature page |
| Liability Cap | "Limitation of Liability" | "Damages" section | Indemnification cap |
| Indemnification | "Indemnification" article | "Liability" section | Insurance provisions |
| IP Ownership | "Intellectual Property" section | "Work Product" | License grant section |
| Termination Rights | "Termination" section | "Default and Remedies" | "Term" section |
| Data Protection | DPA exhibit | "Data Protection" section | "Confidentiality" section |

## NDA Review Columns

Standard extraction columns for non-disclosure agreement review.

| # | Column | Description | Where to Look | Example Values |
|---|--------|-------------|---------------|----------------|
| 1 | Parties | Disclosing and receiving parties | Preamble, first page | "Disclosing Party: Acme Corp; Receiving Party: Beta Inc" |
| 2 | Type | Mutual or one-way NDA | Preamble, definition of "Confidential Information" | "Mutual" or "One-way (Acme disclosing)" |
| 3 | Definition Scope | How "Confidential Information" is defined | Definitions section, typically Section 1 | "All non-public information disclosed in writing or orally" |
| 4 | Exceptions | Standard exceptions to confidentiality | Typically Section 2 or "Exclusions" subsection | "Publicly known, independently developed, rightfully received from third party" |
| 5 | Term | Duration of confidentiality obligations | Term section | "3 years from date of disclosure" |
| 6 | Survival | How long obligations survive after termination | Term section, survival clause | "Obligations survive for 2 years after termination" |
| 7 | Return/Destruction | Obligations upon termination regarding materials | Termination section, "Return of Materials" | "Return or destroy within 30 days; certify destruction" |
| 8 | Remedies | Available remedies for breach | Remedies section | "Injunctive relief without bond; monetary damages" |
| 9 | Non-Compete | Any non-compete or non-solicitation provisions | Often added as separate section | "None" or "12-month non-solicitation of employees" |
| 10 | Residuals | Residual knowledge/information clause | Often near exceptions or IP section | "Residual knowledge retained in unaided memory is not restricted" |

### NDA Review: Key Distinctions

| Feature | Mutual NDA | One-Way NDA |
|---------|-----------|-------------|
| Parties | Both are Disclosing and Receiving | One Disclosing, one Receiving |
| Definition | Symmetric definition | Asymmetric; only discloser's info protected |
| Obligations | Both parties bound | Only receiving party bound |
| Preferred by | Balanced relationships | Party sharing more sensitive information |
| Risk | May over-protect non-sensitive info | Under-protects receiving party's info |

## Employment Agreement Columns

Standard extraction columns for employment agreement review.

| # | Column | Description | Where to Look | Example Values |
|---|--------|-------------|---------------|----------------|
| 1 | Employee | Employee full name | Preamble, first page | "Jane Smith" |
| 2 | Employer | Employing entity full legal name | Preamble, first page | "Acme Corporation" |
| 3 | Start Date | Employment commencement date | "Commencement" or "Start Date" section | "March 1, 2026" |
| 4 | Compensation | Base salary and any variable compensation | Compensation section | "$150,000 base + 20% target bonus" |
| 5 | Benefits | Key benefits referenced or described | Benefits section | "Standard benefits package per Employee Handbook" |
| 6 | Non-Compete Scope | Geographic and industry scope of non-compete | Restrictive covenants section | "Within 50 miles of any company office; same industry" |
| 7 | Non-Compete Duration | Duration of post-employment non-compete | Restrictive covenants, same section as scope | "12 months following termination" |
| 8 | IP Assignment | Intellectual property assignment provisions | IP section, "Inventions" or "Work Product" | "All inventions during employment assigned to Employer" |
| 9 | Termination Conditions | Conditions and process for termination | Termination section | "At-will; or for Cause as defined" |
| 10 | Notice Period | Required notice period for resignation/termination | Termination section | "30 days written notice" |
| 11 | Severance | Severance terms upon termination | Termination or Severance section | "6 months base salary if terminated without Cause" |

### Employment Agreement: Jurisdiction Considerations

| Jurisdiction | Key Consideration | Impact on Extraction |
|-------------|-------------------|---------------------|
| California | Non-compete generally unenforceable | Note if non-compete exists but may be unenforceable |
| EU/EEA | Maximum probation periods; notice requirements | Extract probation period and statutory minimums |
| UK | Statutory notice minimums; garden leave | Extract garden leave provisions |
| New York | Non-compete must be reasonable in scope | Extract scope details for reasonableness assessment |
| Texas | At-will with consideration requirement | Note consideration for non-compete |

## Lease Review Columns

Standard extraction columns for commercial lease review.

| # | Column | Description | Where to Look | Example Values |
|---|--------|-------------|---------------|----------------|
| 1 | Landlord | Property owner/lessor full legal name | Preamble, first page | "ABC Property Holdings LLC" |
| 2 | Tenant | Lessee full legal name | Preamble, first page | "Acme Corporation" |
| 3 | Premises | Description of leased space | Premises section, exhibits | "Suite 400, 123 Main St, Floor 4, 5,000 sq ft" |
| 4 | Term | Lease duration with start and end dates | Term section | "5 years: Jan 1, 2026 to Dec 31, 2030" |
| 5 | Rent | Base rent amount and payment schedule | Rent section | "$50/sq ft/year, payable monthly" |
| 6 | Escalation | Rent escalation mechanism | Rent section, escalation subsection | "3% annual increase" or "CPI-adjusted" |
| 7 | Maintenance | Maintenance and repair responsibilities | Maintenance section | "Tenant: interior; Landlord: structural, roof, HVAC" |
| 8 | Insurance | Insurance requirements | Insurance section | "CGL $1M/$2M, Property coverage at replacement value" |
| 9 | Assignment/Subletting | Restrictions on assignment and subletting | Assignment section | "Landlord consent required; not unreasonably withheld" |
| 10 | Break Clause | Early termination rights | Break clause or termination section | "Tenant break at Year 3 with 6 months notice" |

### Lease Review: Lease Type Impact

| Lease Type | Rent Covers | Tenant Also Pays | Key Extraction Difference |
|-----------|-------------|-------------------|--------------------------|
| Gross | Base rent includes most costs | Typically nothing additional | Focus on what's included |
| Net | Base rent only | Taxes | Extract tax obligation |
| Double Net (NN) | Base rent only | Taxes + insurance | Extract both obligations |
| Triple Net (NNN) | Base rent only | Taxes + insurance + maintenance | Extract all three obligations |
| Modified Gross | Base rent + some costs | Varies | Extract allocation of costs |

## Using Column Sets

### Selecting a Column Set

1. **Identify document type** -- What kind of documents are you reviewing?
2. **Select pre-defined set** -- Use the matching column set from this reference
3. **Customize** -- Add, remove, or modify columns based on review objectives
4. **Define specifics** -- Add "Where to Look" and "Example Values" for custom columns

### Combining Column Sets

For documents that span multiple types (e.g., a master services agreement with NDA provisions):

1. Start with the primary document type column set
2. Add specific columns from secondary sets
3. Remove duplicates (e.g., "Parties" appears in all sets)
4. Prioritize columns based on review objectives

### Column Count Guidelines

| Review Type | Recommended Columns | Maximum |
|------------|--------------------|---------| 
| Quick triage | 3-5 | 8 |
| Standard review | 6-10 | 15 |
| Comprehensive review | 10-15 | 20 |
| Due diligence | 15-20 | 25 |

More columns means more processing time and lower average confidence. Balance comprehensiveness with efficiency.

## Creating Custom Columns

### Custom Column Template

```
Column: [Specific name]
Description: [Exactly what to extract]
Where to look: [Typical location(s) in the document]
Format: [Expected format of the value]
Example values:
  - [Example 1]
  - [Example 2]
Edge cases:
  - [What if not explicitly stated?]
  - [What if multiple values exist?]
```

### Custom Column Examples

**Revenue Share:**
```
Column: Revenue Share Percentage
Description: The percentage of revenue shared between parties
Where to look: Payment terms, revenue sharing section, commercial terms
Format: Percentage (e.g., "70/30" or "70% to Licensor")
Example values:
  - "70% to Licensor, 30% to Licensee"
  - "Net revenue split 60/40"
Edge cases:
  - If tiered, extract all tiers
  - If different rates for different products, note "varies by product"
```

**Force Majeure:**
```
Column: Force Majeure
Description: Whether force majeure clause exists and what events are covered
Where to look: Force Majeure section, typically in General Provisions
Format: Yes/No + key events listed
Example values:
  - "Yes: natural disasters, war, pandemic, government action"
  - "No force majeure clause"
Edge cases:
  - If referenced in another document (e.g., Master Agreement), note cross-reference
  - If clause exists but is limited, extract the limitations
```

### Custom Column Quality Checklist

- [ ] Name is specific and unambiguous
- [ ] Description tells agent exactly what to look for
- [ ] "Where to look" guidance provided
- [ ] Expected format specified
- [ ] At least 2 example values given
- [ ] Edge cases documented
- [ ] Column is relevant to the review objective
