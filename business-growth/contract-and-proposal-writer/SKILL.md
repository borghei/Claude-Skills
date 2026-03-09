---
name: contract-and-proposal-writer
description: Generate production-ready business documents including freelance contracts, project proposals, SOWs, NDAs, and MSAs with jurisdiction-aware clauses. Covers US (Delaware), EU (GDPR), UK, and DACH (German law) legal frameworks. Includes contract templates, clause libraries, and DOCX conversion. Use when starting client engagements, writing proposals, drafting partnership agreements, or needing GDPR-compliant data processing addenda.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: business-growth
  domain: legal-documents
  tier: POWERFUL
  updated: 2026-03-09
  frameworks: contract-templates, jurisdiction-compliance, proposal-writing
---

# Contract & Proposal Writer

**Tier:** POWERFUL
**Category:** Business Growth
**Tags:** contracts, proposals, SOW, NDA, MSA, GDPR, legal templates, freelance

## Overview

Generate professional, jurisdiction-aware business documents: freelance contracts, project proposals, statements of work, NDAs, and master service agreements. Outputs structured Markdown with conversion instructions for DOCX and PDF. Covers US (Delaware), EU (GDPR), UK, and DACH (German law) jurisdictions with clause libraries for each.

**This is not a substitute for legal counsel.** Use these templates as strong starting points. Review with an attorney for engagements over $50K or involving complex IP, equity, or regulatory requirements.

---

## Core Capabilities

- Fixed-price and hourly development contracts
- Monthly consulting retainer agreements
- Project proposals with timeline and budget breakdown
- Statements of Work (SOW) with deliverables matrix and acceptance criteria
- NDAs (mutual and one-way)
- Master Service Agreements (MSA) with SOW attachment framework
- SaaS partnership agreements (reseller, referral, white-label, integration)
- GDPR Data Processing Addenda (Art. 28) for EU/DACH
- Jurisdiction-specific clause library (US, EU, UK, DACH)
- Change order and scope management clauses

---

## Workflow

### Step 1: Requirements Gathering

Gather before drafting:

| Question | Why It Matters |
|----------|---------------|
| Document type? | Contract, proposal, SOW, NDA, MSA |
| Jurisdiction? | US-Delaware, EU, UK, DACH |
| Engagement model? | Fixed-price, hourly, retainer, revenue-share |
| Parties? | Legal names, roles, registered addresses |
| Scope summary? | 1-3 sentences describing the work |
| Total value or rate? | Drives payment terms and liability caps |
| Timeline? | Start date, end date or duration, milestones |
| Special requirements? | IP assignment, white-label, subcontractors, non-compete |
| Personal data involved? | Triggers GDPR DPA requirement in EU/DACH |

### Step 2: Template Selection

| Document Type | Engagement Model | Template |
|--------------|-----------------|----------|
| Dev contract | Fixed-price | Template A: Fixed-Price Development |
| Dev contract | Hourly/Retainer | Template B: Consulting Retainer |
| Partnership | Revenue-share | Template C: SaaS Partnership |
| NDA | Mutual | Template NDA-M |
| NDA | One-way (discloser/recipient) | Template NDA-OW |
| SOW | Any | Template SOW (attaches to MSA or standalone) |
| Proposal | Any | Template P: Project Proposal |

### Step 3: Generate & Fill

Fill all `[BRACKETED]` placeholders. Flag missing information as `[REQUIRED - description]`. Never leave blanks -- an incomplete contract is more dangerous than no contract.

### Step 4: Review Checklist

Before sending any generated document:

- [ ] All `[BRACKETED]` placeholders filled
- [ ] Correct jurisdiction selected and consistent throughout
- [ ] Payment terms match engagement model
- [ ] IP clause matches jurisdiction requirements
- [ ] Liability cap is reasonable (typically 1x-3x contract value)
- [ ] Termination clauses include both for-cause and for-convenience
- [ ] DPA included if personal data is processed (EU/DACH mandatory)
- [ ] Force majeure clause included for engagements over 3 months
- [ ] Change order process defined for fixed-price contracts
- [ ] Acceptance criteria defined for each deliverable

---

## Clause Library

### Payment Terms

| Model | Standard Terms | Risk Notes |
|-------|---------------|------------|
| Fixed-price | 50% upfront, 25% at beta, 25% at acceptance | Best for defined scope |
| Hourly | Net-30, monthly invoicing | Requires time tracking |
| Retainer | Monthly prepaid, 1st of month | Include overflow rate |
| Milestone | Per-milestone invoicing | Define milestones precisely |
| Revenue-share | Net-30 after month close, minimum threshold | Requires audit rights |

**Late payment:** 1.5% per month (US standard), up to statutory maximum in EU/DACH.

### Intellectual Property

| Jurisdiction | Default IP Ownership | Key Requirement |
|-------------|---------------------|-----------------|
| US (Delaware) | Work-for-hire doctrine | Must be in writing, 9 qualifying categories |
| EU | Author retains moral rights | Separate written assignment needed |
| UK | Employer owns (if employee) | Contractor: explicit assignment required |
| DACH (Germany) | Author retains Urheberrecht permanently | Must transfer Nutzungsrechte (usage rights) explicitly |

**Pre-existing IP:** Always carve out pre-existing tools, libraries, and frameworks. Grant client a perpetual, royalty-free license to use pre-existing IP as embedded in deliverables.

**Portfolio rights:** Developer retains right to display work in portfolio unless client requests confidentiality in writing within 30 days.

### Liability

| Risk Level | Cap | When to Use |
|-----------|-----|-------------|
| Standard | 1x total fees paid | Most projects |
| High-risk | 3x total fees paid | Critical infrastructure, regulated industries |
| Uncapped (mutual) | No cap, mutual indemnification | Enterprise partnerships |

**Always exclude:** Indirect, incidental, and consequential damages (both parties).

### Termination

| Type | Notice Period | Financial Treatment |
|------|-------------|-------------------|
| For cause | 14-day cure period | Pay for work completed |
| For convenience (client) | 30 days written notice | Pay for work completed + 10-20% of remaining value |
| For convenience (either) | 30-60 days | Pay for work completed |
| Immediate (material breach uncured) | 7 days post-notice | Pro-rata payment |

### Confidentiality

- Standard term: 3 years post-termination
- Trade secrets: Perpetual (as long as information remains a trade secret)
- Return/destruction: All confidential materials returned or certified destroyed within 30 days of termination
- Exceptions: Publicly known, independently developed, received from third party, required by law

### Dispute Resolution

| Jurisdiction | Recommended Forum | Rules |
|-------------|-------------------|-------|
| US | Binding arbitration | AAA Commercial Rules, Delaware venue |
| EU | ICC arbitration or local courts | ICC Rules, venue in capital of governing law |
| UK | LCIA arbitration, London | LCIA Rules, English law |
| DACH | DIS arbitration or Landgericht | DIS Rules, German law |

---

## Jurisdiction-Specific Requirements

### US (Delaware)
- Governing law: State of Delaware (most business-friendly)
- Work-for-hire doctrine applies (Copyright Act 101)
- Non-compete: Enforceable with reasonable scope/duration/geography
- Electronic signatures: Valid under ESIGN Act and UETA

### EU (GDPR)
- Data Processing Addendum required if handling personal data
- IP assignment may require separate written deed in some member states
- Consumer protection laws may override contract terms for B2C
- Right to withdraw within 14 days for distance contracts (B2C)

### UK (Post-Brexit)
- Governed by English law (most common choice)
- IP: Patents Act 1977, CDPA 1988
- UK GDPR (post-Brexit equivalent) applies for data processing
- Electronic signatures: Valid under Electronic Communications Act 2000

### DACH (Germany / Austria / Switzerland)
- BGB (Buergerliches Gesetzbuch) governs contracts
- Schriftform (written form) required for certain clauses (para 126 BGB)
- Author always retains moral rights (Urheberpersoernlichkeitsrecht) -- cannot be transferred
- Must explicitly transfer Nutzungsrechte (usage rights) with scope and duration
- Non-competes: Maximum 2 years, compensation required (para 74 HGB)
- DSGVO (German GDPR implementation) mandatory for personal data
- Kuendigungsfristen: Statutory notice periods apply and cannot be shortened below minimum

---

## GDPR Data Processing Addendum (Template Block)

Required for any EU/DACH engagement involving personal data:

```markdown
## DATA PROCESSING ADDENDUM (Art. 28 GDPR/DSGVO)

Controller: [CLIENT LEGAL NAME]
Processor: [SERVICE PROVIDER LEGAL NAME]

### Processing Scope
Processor processes personal data solely to perform services under the Agreement.

### Categories of Data Subjects
[End users / Employees / Customers of Controller]

### Categories of Personal Data
[Names, email addresses, usage data, IP addresses, payment information]

### Processing Duration
Term of the Agreement. Deletion within [30] days of termination.

### Processor Obligations
1. Process only on Controller's documented instructions
2. Ensure authorized persons committed to confidentiality
3. Implement Art. 32 technical and organizational measures
4. Assist with data subject rights requests within [10] business days
5. Notify Controller of personal data breach within [72] hours
6. No sub-processors without prior written consent
7. Delete or return all personal data upon termination
8. Make available information to demonstrate compliance

### Current Sub-Processors
| Sub-Processor | Location | Purpose |
|--------------|----------|---------|
| [AWS/GCP/Azure] | [Region] | Cloud infrastructure |
| [Stripe] | [US/EU] | Payment processing |

### Cross-Border Transfers
Transfers outside EEA: [ ] Standard Contractual Clauses [ ] Adequacy Decision [ ] BCRs
```

---

## Project Proposal Template (Template P)

```markdown
# PROJECT PROPOSAL

**Prepared for:** [Client Name]
**Prepared by:** [Your Name / Company]
**Date:** [Date]
**Valid until:** [Date + 30 days]

---

## Executive Summary
[2-3 sentences: what you will build, the business problem it solves, and the expected outcome]

## Understanding of Requirements
[Demonstrate you understand the client's problem. Reference their specific situation, not generic boilerplate]

## Proposed Solution
[Technical approach, architecture overview, technology choices with rationale]

## Scope of Work

### In Scope
- [Deliverable 1: specific description]
- [Deliverable 2: specific description]
- [Deliverable 3: specific description]

### Out of Scope
- [Explicitly list what is NOT included -- prevents scope creep]

### Assumptions
- [Client provides X by Y date]
- [Access to Z system will be available]

## Timeline

| Phase | Deliverables | Duration | Dates |
|-------|-------------|----------|-------|
| Discovery | Requirements document, architecture plan | 1 week | [Dates] |
| Development | Core features, API integration | 4 weeks | [Dates] |
| Testing | QA, UAT, bug fixes | 1 week | [Dates] |
| Launch | Deployment, monitoring, handoff | 1 week | [Dates] |

## Investment

| Item | Cost |
|------|------|
| Discovery & Planning | [Amount] |
| Development | [Amount] |
| Testing & QA | [Amount] |
| Project Management | [Amount] |
| **Total** | **[Amount]** |

### Payment Schedule
- 50% upon contract signing
- 25% at beta delivery
- 25% upon final acceptance

## Why Us
[2-3 concrete differentiators. Reference relevant experience, not just claims]

## Next Steps
1. Review and approve this proposal
2. Sign agreement (attached)
3. Kick-off meeting within [5] business days
```

---

## Document Conversion

```bash
# Markdown to DOCX (basic)
pandoc contract.md -o contract.docx --reference-doc=template.docx

# With numbered sections (legal style)
pandoc contract.md -o contract.docx --number-sections -V fontsize=11pt

# Markdown to PDF (via LaTeX)
pandoc contract.md -o contract.pdf -V geometry:margin=1in -V fontsize=11pt

# Batch convert all contracts
for f in contracts/*.md; do
  pandoc "$f" -o "${f%.md}.docx" --reference-doc=template.docx
done
```

---

## Common Pitfalls

| Pitfall | Consequence | Prevention |
|---------|-------------|------------|
| Missing IP assignment language | Unclear ownership, disputes | Always include explicit IP clause per jurisdiction |
| Vague acceptance criteria | Endless revision cycles | Define "accepted" = written sign-off within X days |
| No change order process | Scope creep on fixed-price | Include change order clause with pricing mechanism |
| Jurisdiction mismatch | Unenforceable clauses | Match governing law to where parties operate |
| Missing liability cap | Unlimited exposure | Always cap liability at 1-3x contract value |
| Oral amendments | Unenforceable modifications | Require written amendments signed by both parties |
| No DPA for EU data | GDPR violation, up to 4% global revenue fine | Always include DPA when processing EU personal data |
| Missing force majeure | No protection against unforeseeable events | Include for engagements over 3 months |

---

## Best Practices

1. Use milestone payments over net-30 for projects over $10K -- reduces cash flow risk for both parties
2. Always include a change order clause in fixed-price contracts
3. For DACH: include Schriftformklausel (written form clause) explicitly
4. Define response time SLAs in retainer agreements (e.g., 4h urgent / 24h normal)
5. Keep templates in version control; review annually as laws change
6. For NDAs: always specify return/destruction of confidential materials on termination
7. Include a survival clause -- specify which clauses survive termination (confidentiality, IP, liability)
8. For EU/DACH: check if consumer protection laws apply (B2C engagements have additional requirements)

---

## Related Skills

| Skill | Use When |
|-------|----------|
| **ceo-advisor** | Strategic decisions about partnerships and business models |
| **cfo-advisor** | Financial terms, pricing strategy, revenue recognition |
| **launch-strategy** | Contract timing around product launches |
