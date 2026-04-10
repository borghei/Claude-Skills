# Privacy Notice Types Guide

Detailed guidance for 6 privacy notice types with audience-specific requirements, data categories, and jurisdiction notes.

---

## Table of Contents

- [Website/App Notice](#websiteapp-notice)
- [Applicant/Recruiting Notice](#applicantrecruiting-notice)
- [Employee Notice](#employee-notice)
- [Business Partner (B2B) Notice](#business-partner-b2b-notice)
- [B2C Customer Notice](#b2c-customer-notice)
- [Combined Notice](#combined-notice)

---

## Website/App Notice

### Platform Sub-Types

| Sub-Type | Specific Sections Needed | Additional Considerations |
|----------|------------------------|--------------------------|
| **Brochure website** | Cookie notice, contact form data, analytics | Minimal processing; often consent + legitimate interests basis |
| **E-commerce** | Payment processing, order fulfillment, account data, marketing | Contract basis for orders; separate consent for marketing; payment processor disclosure |
| **SaaS platform** | Account data, usage data, API data, customer content | Processor/controller distinction for customer data; sub-processor list |
| **Mobile app** | Device data, location, push notifications, app analytics | Device permissions disclosure; SDK/third-party library data sharing; app store requirements |
| **Marketplace** | Seller data, buyer data, transaction data, reviews | Multiple data subject categories; dual-role processing (buyers and sellers) |
| **AI platform** | Training data, inference data, model outputs, user prompts | EU AI Act Art. 50 transparency; Art. 22 automated decisions; data retention for training |

### Required Sections for Website/App

| Section | Required | Notes |
|---------|----------|-------|
| Controller identity | Yes | Legal entity, not just brand name |
| DPO contact | Yes (if appointed) | Separate from general contact |
| Data categories collected | Yes | Include automatically collected data |
| Purposes and legal bases | Yes | Per-purpose legal basis mapping |
| Recipients | Yes | Analytics providers, CDN, hosting, payment |
| International transfers | Yes (if applicable) | Cloud providers often transfer data |
| Retention periods | Yes | Per-category; session vs. persistent cookies |
| Data subject rights | Yes | All 8 rights with exercise method |
| Cookies and tracking | Yes | Category table; consent mechanism reference |
| Third-party integrations | Recommended | Social media plugins, embedded content |
| Children's data | If applicable | Age verification; parental consent mechanisms |

### Typical Data Categories

| Category | Examples | Legal Basis (Typical) |
|----------|---------|----------------------|
| Identity | Name, email (registration) | Contract |
| Contact form | Name, email, message | Legitimate interests or consent |
| Usage data | Pages visited, session duration, clicks | Legitimate interests or consent |
| Device data | IP address, browser, OS, screen resolution | Legitimate interests |
| Cookies (necessary) | Session, CSRF, preferences | Legitimate interests (strictly necessary) |
| Cookies (analytics) | Google Analytics, Hotjar | Consent |
| Cookies (marketing) | Facebook Pixel, Google Ads | Consent |
| Payment data | Card details, billing address | Contract |
| Account data | Username, password hash, preferences | Contract |

---

## Applicant/Recruiting Notice

### Hiring-Specific Data Categories

| Category | Examples | Legal Basis | Retention |
|----------|---------|-------------|-----------|
| Application materials | CV, cover letter, portfolio | Pre-contractual measures (Art. 6(1)(b)) | 6 months post-decision (default) |
| Contact details | Email, phone, address | Pre-contractual measures | 6 months post-decision |
| Qualifications | Degrees, certifications, licenses | Pre-contractual measures | 6 months post-decision |
| Interview notes | Assessment records, panel feedback | Legitimate interests (Art. 6(1)(f)) | 6 months post-decision |
| Reference checks | Previous employer feedback | Consent (Art. 6(1)(a)) | 6 months post-decision |
| Background checks | Criminal record, credit check (if applicable) | Legal obligation or consent | 6 months post-decision |
| Right to work | Passport, visa, work permit | Legal obligation (Art. 6(1)(c)) | Duration of employment + statutory retention |
| Diversity data | Gender, ethnicity, disability (voluntary) | Consent; Art. 9(2)(b) employment law | Anonymized after use; aggregate statistics retained |
| Salary expectations | Current/expected compensation | Legitimate interests | 6 months post-decision |

### Retention Defaults

| Scenario | Default Retention | Basis |
|----------|-------------------|-------|
| Unsuccessful application | 6 months from decision | Defense of legal claims (discrimination, unfair hiring) |
| Talent pool (with consent) | 12 months (renewable) | Consent — must be freely given, not bundled with application |
| Successful application | Transfer to employee file | Contract basis |
| Withdrawn application | Delete within 30 days of withdrawal | No further basis for processing |

### Talent Pool Consent Requirements

- Consent must be separate from application submission
- Must be freely given — refusal must not affect application
- Must specify retention period and review frequency
- Easy withdrawal mechanism (email or portal)
- Re-consent before expiry if extending retention

### DE-Specific (§26 BDSG)

- Employee data processing (including applicants) governed by §26 BDSG
- Processing must be necessary for employment relationship decisions
- Works council (Betriebsrat) may have co-determination rights in hiring process
- Discriminatory questioning restrictions (AGG — Allgemeines Gleichbehandlungsgesetz)

---

## Employee Notice

### Employee-Specific Data Categories

| Category | Examples | Legal Basis | Special Handling |
|----------|---------|-------------|-----------------|
| Employment contract data | Role, start date, salary, benefits | Contract (Art. 6(1)(b)) | — |
| Payroll data | Bank details, tax code, NI/social security | Legal obligation (Art. 6(1)(c)) | Financial data protection |
| Performance data | Reviews, objectives, development plans | Legitimate interests (Art. 6(1)(f)) | Transparency required |
| IT system data | Login records, email usage, internet usage | Legitimate interests | Works council agreement |
| Health data | Sick leave, occupational health, disability | Art. 9(2)(b) employment law | Special category — additional safeguards |
| CCTV footage | Workplace video surveillance | Legitimate interests (security) | Signage, retention limits, access restrictions |
| Location data | Company vehicle GPS, field worker tracking | Legitimate interests or consent | Proportionality assessment required |
| Biometric data | Access control fingerprint/face | Consent or employment law | Special category — DPIA recommended |

### Works Council Notification (DE/AT)

| Topic | Works Council Involvement | Legal Basis |
|-------|--------------------------|-------------|
| IT systems monitoring | Co-determination right (§87(1)(6) BetrVG) | Must agree before implementation |
| CCTV installation | Co-determination right | Must agree on scope, retention, access |
| Performance monitoring tools | Co-determination right | Must agree on metrics and use |
| Employee data processing agreements | Information right | Must be informed of DPA terms |
| BYOD policies | Co-determination right | Must agree on scope of employer access |
| HR information systems | Co-determination right | Must agree on data collected and access |

### IT Monitoring Disclosure

| Monitoring Type | Disclosure Required | Key Points |
|----------------|-------------------|------------|
| Email monitoring | Yes — scope and purpose | Whether content or metadata only; personal use policy |
| Internet usage logging | Yes — scope and purpose | Categories logged; personal use allowance |
| Device management (MDM) | Yes — capabilities | What data employer can access/wipe; BYOD boundaries |
| Keylogger/screenshot | Highly restricted; requires strong justification | Generally disproportionate; exceptional circumstances only |
| DLP (Data Loss Prevention) | Yes — triggers and scope | What triggers alert; who reviews; false positive handling |

### BYOD Policy Disclosure

- What data employer can access on personal device
- Remote wipe scope (company data only vs. full device)
- App installation requirements and restrictions
- Employee's right to refuse BYOD participation
- Data segregation measures (containerization)

---

## Business Partner (B2B) Notice

### Art. 14 Requirements (Indirect Collection)

When personal data is not collected directly from the data subject (common in B2B), Art. 14 GDPR applies:

| Requirement | Art. 14 Reference | B2B Context |
|-------------|-------------------|-------------|
| Source of data | Art. 14(2)(f) | "We received your data from your employer" or "from public business registers" |
| Categories of data obtained | Art. 14(1)(d) | Name, business email, job title, business phone |
| Timing of notice | Art. 14(3) | Within reasonable period, max 1 month; or at first communication |
| Whether from publicly available source | Art. 14(2)(f) | LinkedIn, company websites, business directories |

### Typical B2B Data Categories

| Category | Examples | Source | Legal Basis |
|----------|---------|--------|-------------|
| Business contact details | Name, title, email, phone | Counterparty company, business cards | Legitimate interests (Art. 6(1)(f)) |
| Company information | Company name, address, registration | Public registers, company website | Legitimate interests |
| Transaction data | Orders, invoices, payment history | Business relationship | Contract (Art. 6(1)(b)) |
| Communication records | Emails, meeting notes, correspondence | Business relationship | Legitimate interests |
| Due diligence data | Credit checks, sanctions screening | Credit agencies, sanctions lists | Legal obligation or legitimate interests |

### Source Disclosure Template

> We obtained your business contact details from [source: your employer / public business register / industry event / your company website / your business card provided at [event]]. We process your data for the purpose of [managing our business relationship / contract performance / business development]. This notice is provided in accordance with Art. 14 GDPR.

---

## B2C Customer Notice

### Soft Opt-In Rules

The "soft opt-in" allows marketing to existing customers about similar products without prior consent, subject to conditions:

| Condition | Requirement |
|-----------|-------------|
| Existing customer | Data subject purchased or negotiated purchase of a product/service |
| Similar products/services | Marketing relates to similar products/services to those already purchased |
| Opt-out at collection | Clear opportunity to opt-out at point of data collection |
| Opt-out in every message | Easy unsubscribe mechanism in every marketing communication |
| No consent required | Soft opt-in replaces consent requirement for email marketing |

**Jurisdiction notes:**
- DE: §7(3) UWG implements soft opt-in; strictly limited to direct electronic marketing
- FR: Art. L34-5 CPCE implements soft opt-in; CNIL guidance applies
- UK: Regulation 22 PECR implements soft opt-in; ICO guidance
- IT: Garante guidance on soft opt-in scope and limitations

### Payment Processor Disclosure

| Disclosure Element | Details |
|-------------------|---------|
| Processor identity | Name of payment processor (e.g., Stripe, Adyen, PayPal) |
| Data shared | Card details, billing address, transaction amount |
| Controller/processor role | Payment processor typically acts as independent controller for fraud prevention |
| PCI-DSS compliance | Note payment data handling meets PCI-DSS standards |
| Data location | Where payment data is processed and stored |
| Retention | Transaction records per tax/accounting legal obligation |

### Loyalty Program Disclosure

| Element | Requirement |
|---------|-------------|
| Purpose | Points accumulation, rewards, personalized offers |
| Data collected | Purchase history, preferences, engagement data |
| Legal basis | Consent (for profiling) or contract (for points calculation) |
| Profiling | If loyalty data used for profiling, Art. 22 disclosure required |
| Third-party sharing | Partners in loyalty network |
| Retention | Duration of membership + statutory period |

---

## Combined Notice

### When to Use Combined Notices

Use a combined notice when:
- Organization processes data of multiple audience types (customers + website visitors)
- Audiences overlap significantly
- Maintaining multiple notices creates inconsistency risk

### Merge Strategies

| Strategy | Approach | Best For |
|----------|---------|----------|
| **Layered sections** | Universal sections (controller, DPO, rights) + audience-specific sections clearly labeled | Organizations with 2-3 distinct audiences |
| **Tabbed/accordion** | Digital notice with expandable sections per audience | Web-based notices; good UX |
| **Appendix model** | Core notice + audience-specific appendices | Complex processing with many audiences |
| **Unified with callouts** | Single flowing notice with "If you are a [customer/employee/visitor]..." callouts | Simple processing, overlapping categories |

### Combined Notice Structure

| Section | Universal | Audience-Specific Notes |
|---------|-----------|------------------------|
| Controller identity | Yes | — |
| DPO contact | Yes | — |
| Data categories | Partial | List all; mark which audiences each applies to |
| Purposes and legal bases | Partial | Some purposes universal; others audience-specific |
| Recipients | Partial | Some recipients universal (hosting); others audience-specific |
| International transfers | Yes | — |
| Retention periods | Audience-specific | Different retention per audience and purpose |
| Data subject rights | Yes | Exercise mechanism may differ per audience |
| Cookies | Website visitors only | Not applicable to employees/B2B |
| Employee-specific | Employees only | Works council, monitoring, BYOD |
| B2B source disclosure | B2B only | Art. 14 requirements |

### Risks of Combined Notices

| Risk | Mitigation |
|------|-----------|
| Information overload | Use clear headings and audience markers; layered approach |
| Missing audience-specific requirements | Checklist per audience type before publishing |
| Confusion about which sections apply | "This section applies to you if..." intro per section |
| Maintenance burden | Version control; designated owner per audience section |
