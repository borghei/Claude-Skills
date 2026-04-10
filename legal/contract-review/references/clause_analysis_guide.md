# Clause Analysis Guide

Comprehensive reference for analyzing commercial contract clauses. Covers key elements, common issues, market-standard positions, and risk indicators for each clause type.

---

## Table of Contents

- [Limitation of Liability](#limitation-of-liability)
- [Indemnification](#indemnification)
- [Intellectual Property](#intellectual-property)
- [Data Protection](#data-protection)
- [Term and Termination](#term-and-termination)
- [Governing Law and Dispute Resolution](#governing-law-and-dispute-resolution)
- [Representations and Warranties](#representations-and-warranties)
- [Force Majeure](#force-majeure)
- [Clause Interaction Matrix](#clause-interaction-matrix)

---

## Limitation of Liability

### Key Elements

| Element | Description | Market Standard |
|---------|-------------|-----------------|
| Aggregate Cap | Maximum total liability under the agreement | 12 months of fees paid/payable |
| Cap Type | How the cap is calculated | Fixed dollar amount or fee-based formula |
| Consequential Damages | Exclusion of indirect/special/incidental damages | Mutual exclusion with limited carveouts |
| Carveouts | Obligations excluded from the cap | IP infringement, confidentiality breach, willful misconduct |
| Super-Cap | Higher cap for specific carveout obligations | 2-3x the general cap |
| Per-Incident vs. Aggregate | Whether cap applies per claim or total | Aggregate is more protective for the liable party |

### Cap Types

| Cap Structure | Description | When Appropriate |
|--------------|-------------|------------------|
| Fee-Based (12 months) | Cap equals 12 months of fees paid | Standard SaaS and services agreements |
| Fee-Based (24 months) | Cap equals 24 months of fees paid | Higher-value engagements or vendor-favorable |
| Fixed Dollar Amount | Specific dollar cap (e.g., $1M) | When fees are variable or unpredictable |
| Greater-Of | Greater of fees paid or fixed amount | Balanced approach for medium-value deals |
| Insurance-Based | Cap tied to insurance coverage amount | Professional services, consulting |

### Common Issues

| Issue | Risk Level | Resolution |
|-------|-----------|------------|
| No liability cap at all | RED | Add 12-month fee-based cap immediately |
| Uncapped carveouts that swallow the cap | RED | Limit carveouts to IP infringement and willful misconduct; add super-cap |
| One-sided cap (only limits vendor liability) | YELLOW | Make cap mutual or ensure customer cap is proportionate |
| Cap based on fees "paid" not "paid or payable" | YELLOW | Change to "paid or payable" if early in the agreement term |
| No consequential damages exclusion | YELLOW | Add mutual consequential damages exclusion |
| Consequential damages exclusion does not survive termination | YELLOW | Ensure exclusion survives termination |

### Consequential Damages Deep Dive

Consequential damages include lost profits, lost revenue, loss of data, loss of business opportunity, and reputational harm. These are inherently unpredictable and can far exceed the contract value.

**Standard Exclusion Language:**
> Neither party shall be liable to the other for any indirect, incidental, special, consequential, or punitive damages, including but not limited to loss of profits, data, business opportunity, or goodwill, regardless of whether such party has been advised of the possibility of such damages.

**Common Carveouts from the Exclusion:**
- Breach of confidentiality obligations
- IP infringement indemnification
- Willful misconduct or gross negligence
- Data breach obligations
- Breach of use restrictions

---

## Indemnification

### Key Elements

| Element | Description | Market Standard |
|---------|-------------|-----------------|
| Mutuality | Whether both parties indemnify | Mutual with scope appropriate to each party's risk |
| Scope | What triggers indemnification | Third-party claims arising from breach, negligence, IP infringement |
| Procedure | Notice, control, cooperation requirements | Written notice, indemnifier controls defense, indemnified party cooperates |
| Limitations | Cap, exclusions, conditions | Subject to general liability cap; requires timely notice |
| IP Indemnification | Defense against IP infringement claims | Vendor indemnifies for IP infringement; includes cure options |
| Data Breach | Defense against claims from data incidents | Party causing breach indemnifies the other |

### Indemnification Procedure Checklist

| Step | Requirement | Standard Timeline |
|------|-------------|-------------------|
| Notice | Written notice of claim to indemnifying party | Within 10-15 business days of becoming aware |
| Control | Indemnifying party controls defense | Upon receipt of notice |
| Cooperation | Indemnified party provides reasonable cooperation | Ongoing during defense |
| Settlement | Indemnifying party may not settle without consent if it admits liability | Prior to any settlement |
| Mitigation | Indemnified party must take reasonable steps to mitigate | Ongoing |

### Common Issues

| Issue | Risk Level | Resolution |
|-------|-----------|------------|
| Unilateral indemnification (customer only) | YELLOW | Request mutual indemnification or cap the obligation |
| No indemnification procedure | YELLOW | Add standard notice/control/cooperation procedure |
| Indemnification not subject to liability cap | RED | Ensure indemnification is within or has its own cap |
| No IP indemnification from vendor | YELLOW | Add vendor IP indemnification with cure options |
| Overly broad trigger (any claim, not just third-party) | YELLOW | Limit to third-party claims |

---

## Intellectual Property

### Key Elements

| Element | Description | Market Standard |
|---------|-------------|-----------------|
| Pre-Existing IP | IP owned before the agreement | Remains with originating party |
| Deliverable Ownership | Who owns custom work product | Assigned to customer upon payment, or licensed |
| License Grants | Rights to use pre-existing IP in deliverables | Non-exclusive, perpetual license for use in deliverables |
| Work-for-Hire | IP created as "work made for hire" | Appropriate for employee relationships; complex for contractors |
| Feedback & Improvements | Rights to suggestions and improvements | Vendor typically retains rights to incorporate feedback |
| Background IP | General tools, methodologies, frameworks | Provider retains; grants license for use in deliverables |

### Ownership Models

| Model | Description | Best For |
|-------|-------------|----------|
| Full Assignment | All IP transfers to customer | Custom development with large budget |
| License Model | Provider owns; customer gets exclusive license | SaaS, platform, recurring services |
| Joint Ownership | Both parties own jointly | Collaborative R&D, joint ventures |
| Deliverable Assignment + Background License | Custom work assigned; tools licensed | Professional services, consulting |

### Common Issues

| Issue | Risk Level | Resolution |
|-------|-----------|------------|
| Blanket IP assignment including pre-existing IP | RED | Limit assignment to deliverables; carve out background IP |
| No license to pre-existing IP used in deliverables | YELLOW | Add non-exclusive, perpetual license for embedded pre-existing IP |
| Feedback clause grants vendor ownership of customer ideas | YELLOW | Limit feedback clause to unsolicited suggestions |
| No work product definition | YELLOW | Define deliverables explicitly in SOW |
| IP assignment not conditioned on payment | YELLOW | Condition assignment on full payment |

---

## Data Protection

### Key Elements

| Element | Description | Market Standard |
|---------|-------------|-----------------|
| Roles | Controller vs. Processor designation | Clear designation based on data flow |
| Purpose Limitation | Permitted uses of personal data | Processing only for agreement purposes |
| Sub-Processors | Requirements for downstream processors | Prior written consent or list with objection right |
| Data Breach Notification | Timeline and content of breach notices | 72 hours (GDPR); without undue delay |
| Cross-Border Transfers | Mechanisms for international data transfer | SCCs, adequacy decisions, or binding corporate rules |
| Audit Rights | Right to audit data processing practices | Annual audit with reasonable notice |
| Data Deletion | Obligations upon termination | Delete or return within 30-90 days |
| DPA Requirement | Whether a separate DPA is needed | Required when processing personal data |

### DPA Checklist

| Requirement | Description | Regulatory Basis |
|-------------|-------------|------------------|
| Processing purposes defined | Specific, documented purposes | GDPR Art. 28 |
| Categories of data subjects listed | Employees, customers, etc. | GDPR Art. 28 |
| Types of personal data specified | Names, emails, etc. | GDPR Art. 28 |
| Duration of processing | Aligned with agreement term | GDPR Art. 28 |
| Sub-processor list or consent mechanism | Prior consent or objection right | GDPR Art. 28 |
| Technical and organizational measures | Security standards documented | GDPR Art. 32 |
| Breach notification timeline | 72 hours or without undue delay | GDPR Art. 33 |
| Data subject rights assistance | Cooperation obligations | GDPR Art. 28 |
| Cross-border transfer mechanism | SCCs, adequacy, BCRs | GDPR Ch. V |
| Return/deletion upon termination | Within specified timeframe | GDPR Art. 28 |

### Common Issues

| Issue | Risk Level | Resolution |
|-------|-----------|------------|
| No DPA when processing personal data | RED | Add DPA as exhibit or schedule |
| No breach notification timeline | RED | Add 72-hour notification obligation |
| Unlimited sub-processor rights | YELLOW | Require prior consent or list with objection right |
| No cross-border transfer mechanism | YELLOW | Add SCCs or other approved transfer mechanism |
| No data deletion obligation on termination | YELLOW | Add 30-day deletion/return obligation |
| Unlimited audit rights | YELLOW | Limit to annual with reasonable notice |

---

## Term and Termination

### Key Elements

| Element | Description | Market Standard |
|---------|-------------|-----------------|
| Initial Term | Duration of the initial agreement period | 12-36 months |
| Renewal | How the agreement renews | Auto-renewal with 60-90 day opt-out, or mutual written renewal |
| Termination for Cause | Right to terminate upon breach | 30-day cure period for material breach |
| Termination for Convenience | Right to terminate without cause | 30-90 day written notice |
| Cure Period | Time to fix a breach before termination | 30 days for material breach |
| Transition Assistance | Support during wind-down | 30-90 days of transition support at standard rates |
| Survival | Clauses that survive termination | Confidentiality, liability, IP, indemnification |

### Termination Triggers

| Trigger | Standard Cure Period | Notes |
|---------|---------------------|-------|
| Material breach | 30 days | Must specify breach in written notice |
| Payment default | 15-30 days | Often has shorter cure than other breaches |
| Insolvency/bankruptcy | Immediate | No cure period typically required |
| Change of control | 30 days notice | Right to terminate, not obligation |
| Convenience | 30-90 days notice | No cause required |
| Force majeure (extended) | 90 days of force majeure | Either party may terminate |

### Common Issues

| Issue | Risk Level | Resolution |
|-------|-----------|------------|
| Perpetual term with no termination right | RED | Add termination for convenience with 90-day notice |
| Auto-renewal with no opt-out mechanism | YELLOW | Add 60-day non-renewal notice window |
| Immediate termination without cure | YELLOW | Add 30-day cure period for material breach |
| No transition assistance | YELLOW | Add 30-day transition period at standard rates |
| No survival clause | YELLOW | Add survival for confidentiality, liability, IP, payment |
| Penalty for early termination | YELLOW | Remove or limit to remaining committed fees |

---

## Governing Law and Dispute Resolution

### Key Elements

| Element | Description | Market Standard |
|---------|-------------|-----------------|
| Governing Law | Which jurisdiction's law applies | Home jurisdiction or neutral (Delaware, England) |
| Jurisdiction | Where disputes are litigated | Courts of the governing law jurisdiction |
| Arbitration | Alternative to court litigation | ICC, AAA, or JAMS rules; binding |
| Jury Waiver | Waiver of right to jury trial | Common in B2B; less common in consumer |
| Venue | Specific court or city for disputes | Named city/county in governing law jurisdiction |
| Class Action Waiver | Waiver of class proceedings | Common in B2B agreements |
| Prevailing Party Fees | Attorney fees for the winner | Encourages settlement; may deter smaller party |

### Arbitration vs. Litigation

| Factor | Arbitration | Litigation |
|--------|------------|------------|
| Cost | Lower for smaller disputes | Lower for large, multi-issue disputes |
| Speed | Generally faster | Varies widely by jurisdiction |
| Privacy | Confidential proceedings | Public record |
| Appeal | Very limited appeal rights | Full appellate process |
| Discovery | Limited discovery | Full discovery |
| Expertise | Can select industry-expert arbitrators | Judges may lack domain expertise |
| Enforcement | Easier international enforcement (NY Convention) | May require domestication |

### Common Issues

| Issue | Risk Level | Resolution |
|-------|-----------|------------|
| Foreign jurisdiction with unfamiliar law | YELLOW | Negotiate to home or neutral jurisdiction |
| Mandatory arbitration with no injunctive relief carveout | YELLOW | Add carveout for injunctive relief in courts |
| Jury waiver without arbitration alternative | YELLOW | Either remove waiver or add arbitration clause |
| Exclusive jurisdiction in inconvenient venue | YELLOW | Negotiate to non-exclusive or mutual venue |
| No governing law specified | YELLOW | Add governing law clause |

---

## Representations and Warranties

### Key Elements

| Element | Description | Market Standard |
|---------|-------------|-----------------|
| Authority | Power to enter the agreement | Both parties represent authority |
| Compliance | Compliance with laws | Both parties represent legal compliance |
| Non-Infringement | Services do not infringe third-party IP | Vendor represents non-infringement |
| Conformance | Services meet specifications | Vendor warrants material conformance |
| Workmanship | Professional standard of work | Professional and workmanlike manner |
| Disclaimer | Exclusion of implied warranties | "AS-IS" with limited express warranties |
| Duration | How long warranties last | Term of agreement or specific period (90 days) |

### Common Issues

| Issue | Risk Level | Resolution |
|-------|-----------|------------|
| Complete warranty disclaimer (as-is) | YELLOW | Add minimum warranties: authority, conformance, workmanship |
| No IP non-infringement warranty | YELLOW | Add vendor non-infringement representation |
| Warranties expire too quickly | YELLOW | Extend to term of agreement or minimum 12 months |
| No remedy for warranty breach | YELLOW | Add re-performance obligation and right to terminate |
| One-sided representations | GREEN | Acceptable if scope matches each party's obligations |

---

## Force Majeure

### Key Elements

| Element | Description | Market Standard |
|---------|-------------|-----------------|
| Definition | What events qualify | Natural disasters, pandemics, government actions, war, terrorism |
| Notice | Requirement to notify other party | Written notice within 5-10 business days |
| Mitigation | Obligation to mitigate impact | Commercially reasonable efforts to mitigate |
| Duration Limit | Maximum period before termination right | 90-180 days |
| Termination Right | Right to terminate if force majeure persists | Either party after specified period |
| Payment Obligations | Whether payment obligations are excused | Typically not excused; only performance |
| Pandemic Exclusion | Whether pandemics are explicitly included | Post-COVID, explicitly include or exclude |

### Common Issues

| Issue | Risk Level | Resolution |
|-------|-----------|------------|
| No force majeure clause | YELLOW | Add standard clause with defined events |
| Overly broad definition (includes economic hardship) | YELLOW | Narrow to truly unforeseeable events |
| No duration limit (perpetual excuse) | YELLOW | Add 90-day limit with termination right |
| No mitigation obligation | GREEN | Add commercially reasonable mitigation requirement |
| Payment obligations included in force majeure | YELLOW | Carve out payment obligations |

---

## Clause Interaction Matrix

Understanding how clauses interact is critical for consistent contract review.

| Clause A | Clause B | Interaction |
|----------|----------|-------------|
| Liability Cap | Indemnification | Indemnification should be subject to or have its own cap |
| Liability Cap | Data Protection | Data breach liability may be carved out of general cap |
| Indemnification | IP | IP indemnification is often a specific indemnification obligation |
| Term & Termination | Confidentiality | Confidentiality should survive termination (typically 3-5 years) |
| Term & Termination | Transition | Transition assistance triggers upon termination notice |
| Governing Law | Arbitration | Arbitration clause must be compatible with governing law |
| Reps & Warranties | Indemnification | Warranty breach may trigger indemnification obligation |
| Data Protection | Confidentiality | Personal data protections should exceed general confidentiality |
| Force Majeure | Term & Termination | Extended force majeure should trigger termination right |
| Payment Terms | Liability Cap | Cap is often calculated based on fees from payment terms |

---

## Quick Reference: Severity Classification

| Severity | Criteria | Action Required |
|----------|----------|-----------------|
| RED | Uncapped liability, perpetual term with no exit, broad IP assignment, no data breach notification, missing critical clauses | Must negotiate before signing |
| YELLOW | One-sided indemnification, no cure period, auto-renewal traps, warranty disclaimers, missing recommended clauses, unfavorable jurisdiction | Should negotiate; may accept with mitigation |
| GREEN | Standard terms, balanced obligations, market-standard positions, appropriate caps and carveouts | Acceptable as-is |
