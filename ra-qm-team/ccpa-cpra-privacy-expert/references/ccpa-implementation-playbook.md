# CCPA/CPRA Implementation Playbook

Step-by-step implementation guide for achieving and maintaining CCPA/CPRA compliance, including data mapping methodology, privacy policy drafting, opt-out mechanisms, consumer request workflows, training, and audit planning.

---

## Table of Contents

- [6-Month Implementation Roadmap](#6-month-implementation-roadmap)
- [Data Mapping Methodology](#data-mapping-methodology)
- [Privacy Policy Drafting Guide](#privacy-policy-drafting-guide)
- [Opt-Out Mechanism Implementation](#opt-out-mechanism-implementation)
- [Consumer Request Workflow Design](#consumer-request-workflow-design)
- [Training Program Outline](#training-program-outline)
- [Annual Cybersecurity Audit Planning](#annual-cybersecurity-audit-planning)
- [Ongoing Compliance Monitoring](#ongoing-compliance-monitoring)

---

## 6-Month Implementation Roadmap

### Month 1: Discovery and Scoping

| Week | Activity | Deliverable |
|------|----------|------------|
| 1 | Determine CCPA/CPRA applicability | Applicability determination memo |
| 1 | Assign compliance ownership (DPO / privacy lead) | RACI matrix |
| 2 | Identify all data systems processing PI | System inventory spreadsheet |
| 2 | Identify all PI categories collected | PI category inventory |
| 3 | Map data flows (collection, use, sharing, selling) | Data flow diagrams |
| 3 | Identify all service providers, contractors, third parties | Vendor inventory |
| 4 | Conduct gap analysis against CCPA/CPRA requirements | Gap analysis report |
| 4 | Prioritize remediation actions | Prioritized action plan |

### Month 2: Data Inventory and Mapping

| Week | Activity | Deliverable |
|------|----------|------------|
| 1 | Complete detailed data inventory per system | Data inventory (JSON or spreadsheet) |
| 1 | Identify all SPI categories and systems | SPI inventory |
| 2 | Document collection sources per PI category | Source mapping document |
| 2 | Document business purposes per PI category | Purpose mapping document |
| 3 | Map third-party sharing and selling flows | Third-party data flow map |
| 3 | Document retention periods per PI category | Retention schedule |
| 4 | Validate data inventory with system owners | Signed-off data inventory |
| 4 | Identify cross-border data transfers | Transfer documentation |

### Month 3: Policy and Documentation

| Week | Activity | Deliverable |
|------|----------|------------|
| 1 | Draft privacy policy using requirements checklist | Draft privacy policy |
| 1 | Draft notice at collection | Notice at collection text |
| 2 | Draft service provider agreement addendum | SP agreement template |
| 2 | Draft contractor agreement addendum | Contractor agreement template |
| 3 | Legal review of all documents | Legal review memo |
| 3 | Create privacy policy archive process | Version control procedure |
| 4 | Publish privacy policy on website | Live privacy policy URL |
| 4 | Implement notice at collection across channels | Deployed notices |

### Month 4: Technical Implementation

| Week | Activity | Deliverable |
|------|----------|------------|
| 1 | Implement "Do Not Sell or Share" link on homepage | Live opt-out link |
| 1 | Implement "Limit Use of SPI" link on homepage | Live SPI limit link |
| 2 | Implement GPC signal detection | GPC technical implementation |
| 2 | Deploy cookie consent management platform | Cookie consent banner |
| 3 | Build consumer request intake form | Online request form |
| 3 | Set up toll-free number (or email for online-only) | Request intake channels |
| 4 | Build consumer request fulfillment workflow | Workflow documentation |
| 4 | Implement identity verification process | Verification procedure |

### Month 5: Operationalization

| Week | Activity | Deliverable |
|------|----------|------------|
| 1 | Test consumer request workflow end-to-end | Test results report |
| 1 | Test opt-out mechanisms (website, GPC, cookies) | Test results report |
| 2 | Execute service provider/contractor agreements | Signed agreements |
| 2 | Train customer-facing staff on request handling | Training completion records |
| 3 | Train all employees on privacy obligations | Training completion records |
| 3 | Conduct tabletop exercise for data breach scenario | Exercise report |
| 4 | Document compliance program for regulatory defense | Compliance program documentation |
| 4 | Establish ongoing metrics and monitoring | Dashboard / KPI tracking |

### Month 6: Verification and Audit

| Week | Activity | Deliverable |
|------|----------|------------|
| 1 | Conduct internal compliance assessment | Assessment report |
| 1 | Remediate any remaining gaps | Remediation evidence |
| 2 | Plan annual cybersecurity audit | Audit plan |
| 2 | Conduct risk assessment for high-risk processing | Risk assessment report |
| 3 | Finalize compliance documentation package | Compliance package |
| 3 | Brief executive leadership on compliance status | Executive briefing |
| 4 | Establish quarterly review cadence | Review calendar |
| 4 | Document lessons learned and improvement plan | Improvement plan |

---

## Data Mapping Methodology

### Step 1: Inventory Data Systems

Document every system that collects, stores, processes, or transmits PI:

```
For each system, capture:
- System name and owner
- System type (CRM, ERP, analytics, marketing, HR, etc.)
- Description and business function
- PI categories processed (map to 11 CCPA categories)
- SPI categories processed (map to CPRA SPI categories)
- Data volume (number of consumer records)
- Data retention period
- Geographic location (data center region)
```

### Step 2: Map Collection Sources

For each PI category, document:
- **Direct collection**: Website forms, mobile apps, in-person, phone
- **Indirect collection**: Third-party data purchases, public records, social media
- **Automatic collection**: Cookies, pixels, device fingerprinting, server logs
- **Employee/agent collection**: Customer service interactions, sales interactions

### Step 3: Map Business and Commercial Purposes

Document purposes per CCPA-defined categories:
- **Auditing**: Ad impressions, compliance with regulations
- **Security**: Detecting security incidents, protecting against fraud
- **Debugging**: Identifying and repairing functionality errors
- **Short-lived use**: Contextual ad customization (not profiling)
- **Services**: Performing services, maintaining accounts
- **Quality/safety**: Verifying or maintaining quality, safety
- **Product improvement**: Advancing commercial or economic interests

### Step 4: Map Sharing and Selling

Document all PI flows to external parties:

| PI Category | Recipient | Recipient Type | Purpose | Legal Basis |
|-------------|-----------|---------------|---------|-------------|
| (category) | (name) | SP / Contractor / Third Party | (purpose) | (sale / sharing / business purpose) |

### Step 5: Document Retention

For each PI category:
- Define retention period and justification
- Document deletion/anonymization procedures
- Specify exceptions (legal hold, regulatory requirement)
- Ensure retention is "no longer than reasonably necessary" (CPRA §1798.100(c))

### Step 6: Validate and Maintain

- **Quarterly review**: Validate data inventory accuracy with system owners
- **Trigger-based updates**: New systems, new PI categories, new vendors
- **Annual comprehensive review**: Full data mapping refresh

---

## Privacy Policy Drafting Guide

### Structure Template

```
1. Introduction and Scope
2. Categories of Personal Information Collected
3. Categories of Sensitive Personal Information Collected
4. Sources of Personal Information
5. Purposes for Collecting and Using Personal Information
6. How We Share Personal Information
7. Categories of PI Sold or Shared (past 12 months)
8. Categories of PI Disclosed for Business Purpose (past 12 months)
9. Retention Periods
10. Your Privacy Rights
    a. Right to Know
    b. Right to Delete
    c. Right to Correct
    d. Right to Opt-Out of Sale/Sharing
    e. Right to Limit Use of SPI
    f. Right to Data Portability
    g. Right to Non-Discrimination
11. How to Exercise Your Rights
12. Verification Process
13. Authorized Agents
14. Children's Privacy
15. Do Not Sell or Share My Personal Information
16. Limit the Use of My Sensitive Personal Information
17. Changes to This Policy
18. Contact Information
19. Effective Date
```

### Drafting Best Practices

- Use plain language (8th-grade reading level target)
- Avoid legal jargon where possible
- Use tables for PI category disclosures
- Provide specific examples of PI in each category
- Include clear instructions for exercising rights
- Specify response timelines
- Update the effective date on every revision
- Maintain an archive of all prior versions with dates

---

## Opt-Out Mechanism Implementation

### "Do Not Sell or Share" Link

**Placement:**
- Homepage footer (required)
- All landing pages (recommended)
- Mobile app settings (if applicable)
- Email footer (recommended)

**Technical Implementation:**
1. Create dedicated opt-out page with clear form
2. Associate opt-out preference with consumer identifier (cookie, account, device)
3. Propagate opt-out to all downstream systems (ad tech, analytics, third parties)
4. Persist preference indefinitely (do not reset)
5. Confirm opt-out to consumer

### Global Privacy Control (GPC)

**Detection methods:**
```
HTTP Header: Sec-GPC: 1
JavaScript API: navigator.globalPrivacyControl === true
```

**Implementation requirements:**
- Detect GPC signal on every page load
- Treat GPC as valid opt-out of sale AND sharing
- Do not require additional steps from consumer
- Apply opt-out to the browser or device (not just session)
- Do not serve tracking cookies if GPC detected
- Log GPC detection for compliance records

### "Limit Use of SPI" Link

**Placement:**
- Homepage footer (required under CPRA)
- May combine with "Do Not Sell or Share" link using alternative link labeled "Your Privacy Choices" or similar (per CPPA guidance)

**Implementation:**
1. Create preference center for SPI use limitation
2. Document which SPI uses will be limited
3. Implement technical controls to restrict SPI processing
4. Persist preference and propagate to all systems

### Cookie Consent Management

**Categories to implement:**
- Strictly necessary (no consent required)
- Functional (consent recommended)
- Analytics (consent or opt-out required)
- Advertising (must honor opt-out)

**Platform requirements:**
- Load non-essential cookies only after consent or in absence of opt-out
- Integrate with GPC detection
- Maintain cookie inventory with vendor, purpose, expiration
- Provide granular category controls

---

## Consumer Request Workflow Design

### Request Intake

**Channels:**
- Online form (primary) — accessible from privacy policy and footer
- Toll-free phone number — staffed or IVR with callback
- Email — privacy-specific address (e.g., privacy@company.com)

**Information to capture:**
- Request type (Know, Delete, Correct, Opt-Out, Limit SPI, Portability)
- Consumer name and contact information
- Consumer identifier (email, account number, etc.)
- Specific details (for correction requests)
- Authorized agent documentation (if applicable)

### Identity Verification

**Standard requests (categories of PI):**
- Match 2+ data points against existing records
- Examples: name + email, name + account number, name + phone

**Specific pieces of PI requests:**
- Match 3+ data points against existing records
- Examples: name + email + last 4 SSN, name + account + DOB

**Opt-out requests:**
- No verification required (must be processed immediately)

**Authorized agents:**
- Verify agent's authority (power of attorney or signed authorization)
- May also verify consumer identity directly
- Registered with Secretary of State (if business entity)

### Request Tracking

**SLA tracking:**
- Receipt date and time
- 10-business-day acknowledgment deadline
- 45-calendar-day response deadline
- Extension date (if applicable, up to 90 days total)
- Completion date
- Escalation triggers at 30 days and 40 days

**Status workflow:**
```
Received → Acknowledged → Verification Pending → Verified →
In Progress → Ready for Review → Response Sent → Completed
```

**Metrics to track:**
- Request volume by type (monthly/quarterly)
- Average response time
- On-time completion rate
- Denial rate and reasons
- Appeal rate and outcomes

### Response Templates

Develop standardized response templates for:
- Acknowledgment of receipt (within 10 business days)
- Verification request
- Extension notice (with reason)
- Right to Know response (categories)
- Right to Know response (specific pieces)
- Right to Delete confirmation
- Right to Correct confirmation
- Opt-out confirmation
- Limit SPI confirmation
- Denial with explanation and appeal rights
- Authorized agent response

---

## Training Program Outline

### Tier 1: All Employees (Annual)

**Duration:** 30-45 minutes
**Content:**
- What is CCPA/CPRA and why it matters
- What is personal information (with examples)
- How to recognize a consumer privacy request
- Where to direct consumer requests
- Data handling best practices
- Consequences of non-compliance

### Tier 2: Customer-Facing Staff (Quarterly)

**Duration:** 60-90 minutes
**Content:**
- Detailed consumer rights overview
- How to accept and log requests
- Identity verification procedures
- Escalation procedures
- Scripts for common consumer scenarios
- Handling difficult or complex requests
- Non-discrimination requirements

### Tier 3: Privacy and Compliance Team (Ongoing)

**Duration:** 2-4 hours initial, monthly updates
**Content:**
- Full CCPA/CPRA text analysis
- CPPA regulations and guidance updates
- Request fulfillment procedures
- Data inventory management
- Vendor management and agreements
- Risk assessment methodology
- Audit preparation
- Incident response

### Training Delivery

- Learning management system (LMS) for tracking completion
- Annual certification requirement for all employees
- Role-specific assessments
- New hire orientation inclusion
- Refresher training after regulatory updates

---

## Annual Cybersecurity Audit Planning

### CPRA Audit Requirement (§1798.185(a)(15)(B))

The CPPA is authorized to issue regulations requiring annual cybersecurity audits for businesses whose processing of PI presents "significant risk to consumers' privacy or security."

### Audit Scope

| Area | Key Controls to Audit |
|------|----------------------|
| Access management | RBAC, MFA, privileged access management, access reviews |
| Encryption | At rest, in transit, key management, certificate lifecycle |
| Incident response | IR plan, tabletop exercises, breach notification readiness |
| Vulnerability management | Scanning frequency, patch SLAs, penetration testing |
| Data protection | DLP, backup/recovery, data classification, retention |
| Vendor security | SP assessments, contractual requirements, monitoring |
| Network security | Firewalls, segmentation, monitoring, WAF |
| Employee security | Background checks, training, acceptable use, offboarding |
| Physical security | Data center controls, office access, media disposal |

### Audit Process

1. **Scoping** (Month 1): Define systems and data in scope
2. **Evidence collection** (Month 2-3): Gather policies, configurations, logs
3. **Testing** (Month 3-4): Validate controls through sampling, inspection, testing
4. **Findings** (Month 4): Document findings, assign severity ratings
5. **Remediation** (Month 5-6): Implement corrective actions for findings
6. **Reporting** (Month 6): Final audit report with management attestation

### Risk Assessment for Processing Activities

For each processing activity involving SPI or large-scale PI processing:

- **Describe** the processing activity and purpose
- **Assess** risks to consumers' privacy and security
- **Evaluate** safeguards applied to mitigate risks
- **Determine** whether benefits outweigh risks
- **Document** residual risk and acceptance rationale
- **Review** annually or when processing changes materially

---

## Ongoing Compliance Monitoring

### Quarterly Activities

- [ ] Review consumer request metrics (volume, timing, completions)
- [ ] Validate data inventory accuracy with system owners
- [ ] Review vendor compliance with SP/contractor agreements
- [ ] Test opt-out mechanisms (website, GPC, cookies)
- [ ] Review privacy policy for necessary updates
- [ ] Monitor CPPA enforcement actions and guidance

### Annual Activities

- [ ] Comprehensive data mapping refresh
- [ ] Privacy policy annual update
- [ ] Cybersecurity audit (if required)
- [ ] Risk assessments for processing activities
- [ ] Employee training refresh and certification
- [ ] Vendor agreement review and renewal
- [ ] Board/executive compliance briefing
- [ ] Regulatory landscape scan (new state laws, CPPA rules)

### KPIs to Track

| KPI | Target | Frequency |
|-----|--------|-----------|
| Consumer request on-time completion | > 95% | Monthly |
| Average request response time | < 30 days | Monthly |
| Privacy policy accuracy | 100% current | Quarterly |
| Employee training completion | 100% | Annually |
| SP/contractor agreement coverage | 100% | Quarterly |
| Data inventory freshness | < 90 days old | Quarterly |
| Opt-out mechanism uptime | 99.9% | Monthly |
| GPC signal detection rate | 100% accuracy | Quarterly |
| Open audit findings | 0 critical, < 5 high | Monthly |

### Regulatory Monitoring

Track and respond to:
- CPPA rulemaking and proposed regulations
- CPPA enforcement actions and published decisions
- AG enforcement actions
- Court decisions affecting CCPA/CPRA interpretation
- New state privacy law enactments
- Federal privacy law developments
- Industry-specific guidance
