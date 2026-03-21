---
name: ccpa-cpra-privacy-expert
description: CCPA and CPRA privacy compliance automation. Audits organizations for California privacy law compliance, maps personal information flows, validates consumer rights readiness, and checks technical safeguards. Use for CCPA compliance assessments, CPRA readiness checks, privacy policy review, consumer rights handling, data mapping, and California privacy audits.
triggers:
  - CCPA
  - CPRA
  - California privacy
  - California Consumer Privacy Act
  - consumer privacy rights
  - data privacy California
  - privacy compliance
  - personal information
  - CCPA audit
  - data broker registration
---

# CCPA/CPRA Privacy Expert

Tools and guidance for California Consumer Privacy Act (CCPA) and California Privacy Rights Act (CPRA) compliance.

---

## Table of Contents

- [Tools](#tools)
  - [CCPA Compliance Checker](#ccpa-compliance-checker)
  - [CCPA Data Mapper](#ccpa-data-mapper)
- [Reference Guides](#reference-guides)
- [Workflows](#workflows)
- [Regulatory Overview](#regulatory-overview)

---

## Tools

### CCPA Compliance Checker

Evaluates organizational readiness against all CCPA/CPRA requirements. Validates privacy policies, consumer rights handling, technical safeguards, and opt-out mechanisms.

```bash
# Check compliance from a JSON profile
python scripts/ccpa_compliance_checker.py --input company_profile.json

# Generate a blank input template
python scripts/ccpa_compliance_checker.py --template > company_profile.json

# JSON output for automation
python scripts/ccpa_compliance_checker.py --input company_profile.json --json

# Export report to file
python scripts/ccpa_compliance_checker.py --input company_profile.json --output report.json
```

**Assessment Categories:**

| Category | Key Checks |
|----------|-----------|
| Applicability | Revenue threshold, consumer count, data selling revenue |
| Privacy Policy | Required disclosures, update cadence, accessibility |
| Consumer Rights | Request handling, verification, timelines |
| Opt-Out Mechanisms | "Do Not Sell" link, GPC signal, cookie consent |
| Sensitive PI | SPI categories, use limitation link, handling controls |
| Technical Safeguards | Encryption, access controls, security measures |
| Service Providers | Agreement requirements, data processing terms |
| Risk Assessments | Annual audits, processing risk evaluations |

**Output:**
- Overall compliance score (0-100)
- Per-category scores with pass/fail/partial status
- Prioritized findings with regulatory references
- Remediation recommendations

---

### CCPA Data Mapper

Maps personal information categories, identifies sensitive personal information, tracks data flows across collection, use, sharing, and selling. Generates data inventory reports.

```bash
# Map data from a JSON data inventory
python scripts/ccpa_data_mapper.py --input data_inventory.json

# Generate a blank inventory template
python scripts/ccpa_data_mapper.py --template > data_inventory.json

# Export mapping report
python scripts/ccpa_data_mapper.py --input data_inventory.json --output mapping_report.json

# Generate data flow diagram (text-based)
python scripts/ccpa_data_mapper.py --input data_inventory.json --flow-diagram
```

**Features:**
- Maps all 11 CCPA personal information categories
- Identifies sensitive personal information (SPI) per CPRA definitions
- Tracks data flows: collection sources, business purposes, sharing/selling recipients
- Maps data to service providers, contractors, and third parties
- Generates CCPA-compliant data inventory for privacy policy disclosures
- Flags cross-border data transfers
- Detects data retention gaps

**Personal Information Categories Tracked:**

| Category | CCPA Section | Examples |
|----------|-------------|---------|
| Identifiers | 1798.140(v)(1)(A) | Name, SSN, IP address, email |
| Customer Records | 1798.140(v)(1)(B) | Financial info, medical info |
| Protected Classifications | 1798.140(v)(1)(C) | Race, sex, age, disability |
| Commercial Information | 1798.140(v)(1)(D) | Purchase history, tendencies |
| Biometric Information | 1798.140(v)(1)(E) | Fingerprints, face geometry |
| Internet Activity | 1798.140(v)(1)(F) | Browsing, search, interaction |
| Geolocation Data | 1798.140(v)(1)(G) | Precise location |
| Sensory Data | 1798.140(v)(1)(H) | Audio, visual, thermal |
| Professional Info | 1798.140(v)(1)(I) | Employment, education |
| Education Info | 1798.140(v)(1)(J) | Non-public education records |
| Inferences | 1798.140(v)(1)(K) | Profiles, preferences |

---

## Reference Guides

### CCPA/CPRA Requirements Guide
`references/ccpa-cpra-requirements-guide.md`

Complete regulatory requirements covering:
- Full CCPA/CPRA text analysis with section references
- Consumer rights implementation guidance (Right to Know, Delete, Opt-Out, Correct, Portability, Limit SPI Use)
- Privacy policy content requirements and templates
- Service provider and contractor agreement requirements
- Comparison with Virginia VCDPA, Colorado CPA, Connecticut CTDPA, and GDPR
- Enforcement and penalty structure

### CCPA Implementation Playbook
`references/ccpa-implementation-playbook.md`

Step-by-step implementation guidance:
- 6-month implementation roadmap
- Data mapping methodology and templates
- Privacy policy drafting guide
- Opt-out mechanism implementation (website, GPC, universal opt-out)
- Consumer request workflow design with SLA tracking
- Employee and vendor training program outline
- Annual cybersecurity audit planning
- Ongoing compliance monitoring

---

## Workflows

### Workflow 1: Initial CCPA/CPRA Compliance Assessment

```
Step 1: Determine applicability
        → Check $25M revenue, 100K+ consumers, 50%+ PI revenue thresholds
        → Review exemptions (HIPAA, GLBA, employment data)

Step 2: Generate compliance profile template
        → python scripts/ccpa_compliance_checker.py --template > profile.json
        → Fill in organizational details

Step 3: Run compliance assessment
        → python scripts/ccpa_compliance_checker.py --input profile.json

Step 4: Review scores and findings
        → Address critical gaps first (opt-out link, privacy policy)
        → Plan remediation by category

Step 5: Create data inventory
        → python scripts/ccpa_data_mapper.py --template > inventory.json
        → Document all PI categories collected
        → python scripts/ccpa_data_mapper.py --input inventory.json

Step 6: Develop implementation plan
        → See references/ccpa-implementation-playbook.md
```

### Workflow 2: Consumer Rights Request Handling

```
Step 1: Receive consumer request
        → Identify request type (Know, Delete, Opt-Out, Correct, Portability, Limit SPI)

Step 2: Acknowledge within 10 business days (confirm receipt)
        → Document request in tracking system

Step 3: Verify consumer identity
        → Match 2+ data points for standard requests
        → Match 3+ data points for sensitive data requests
        → No verification needed for opt-out requests

Step 4: Fulfill request within 45 calendar days
        → Extension: up to 45 additional days with notice
        → Search all systems using data inventory
        → python scripts/ccpa_data_mapper.py --input inventory.json

Step 5: Deliver response
        → Provide information in portable format if requested
        → Document completion and response

Step 6: Monitor compliance
        → Track response times and completion rates
        → Generate quarterly compliance reports
```

### Workflow 3: Privacy Policy Update Cycle

```
Step 1: Review current privacy policy against requirements
        → python scripts/ccpa_compliance_checker.py --input profile.json
        → Check privacy_policy category score

Step 2: Update data inventory
        → python scripts/ccpa_data_mapper.py --input inventory.json
        → Verify all PI categories are disclosed

Step 3: Verify required disclosures
        → Categories of PI collected (past 12 months)
        → Sources of PI
        → Business/commercial purposes
        → Categories of third parties
        → Consumer rights description
        → "Do Not Sell or Share" link
        → "Limit the Use of My Sensitive PI" link

Step 4: Update and publish
        → Annual update at minimum
        → Update within 30 days of material changes
        → Maintain prior version archive
```

---

## Regulatory Overview

### CCPA/CPRA Timeline

| Date | Milestone |
|------|-----------|
| Jan 1, 2020 | CCPA effective |
| Jul 1, 2020 | AG enforcement begins |
| Nov 3, 2020 | CPRA passed (Proposition 24) |
| Jan 1, 2023 | CPRA amendments effective |
| Jul 1, 2023 | CPPA enforcement of CPRA begins |
| 2026 | Employment and B2B data exemptions status review |

### Scope and Applicability

A **business** is subject to CCPA/CPRA if it:
- Has annual gross revenue exceeding **$25 million**
- Buys, sells, or shares PI of **100,000+ consumers or households** annually
- Derives **50% or more** of annual revenue from selling or sharing consumers' PI

**Entity Types:**

| Entity | Definition | Obligations |
|--------|-----------|------------|
| Business | Determines purposes and means of processing | Full CCPA/CPRA compliance |
| Service Provider | Processes PI on behalf of a business (contractual) | Limited use, deletion obligations |
| Contractor | Processes PI via written contract (CPRA addition) | Certification, limited use, audit rights |
| Third Party | Receives PI not as service provider/contractor | Subject to opt-out rights |

**Exemptions:**
- **HIPAA-covered entities**: Health data governed by HIPAA exempt
- **GLBA**: Financial data subject to GLBA exempt
- **Employment data**: Employee/applicant PI (subject to review through 2026)
- **B2B data**: Business contact PI in B2B transactions (subject to review through 2026)
- **FCRA**: Data subject to Fair Credit Reporting Act

### Consumer Rights

| Right | CCPA Section | Description | Timeline |
|-------|-------------|-------------|----------|
| Right to Know | §1798.100, §1798.110 | Categories and specific pieces of PI collected | 45 days |
| Right to Delete | §1798.105 | Delete PI collected from the consumer | 45 days |
| Right to Opt-Out | §1798.120 | Opt out of sale or sharing of PI | Immediate |
| Right to Non-Discrimination | §1798.125 | No retaliation for exercising rights | Ongoing |
| Right to Correct | §1798.106 | Correct inaccurate PI (CPRA) | 45 days |
| Right to Limit SPI Use | §1798.121 | Limit use of sensitive PI (CPRA) | Immediate |
| Right to Data Portability | §1798.130 | Receive PI in portable format (CPRA) | 45 days |

### Sensitive Personal Information (CPRA)

SPI categories requiring enhanced protections under CPRA §1798.140(ae):
- Social Security number, driver's license, state ID, passport number
- Account log-in credentials (username + password/security question)
- Financial account number with access credentials
- Precise geolocation (within 1,850 feet / radius)
- Racial or ethnic origin
- Religious or philosophical beliefs
- Union membership
- Contents of mail, email, and text messages (unless business is intended recipient)
- Genetic data
- Biometric data for identification
- Health information
- Sex life or sexual orientation data

### Enforcement and Penalties

| Violation Type | Penalty | Enforcer |
|---------------|---------|----------|
| Unintentional violation | $2,500 per violation | CPPA / AG |
| Intentional violation | $7,500 per violation | CPPA / AG |
| Violations involving minors (under 16) | $7,500 per violation | CPPA / AG |
| Data breach (private action) | $100-$750 per consumer per incident | Consumer (court) |

**Enforcement Bodies:**
- **California Privacy Protection Agency (CPPA)**: Primary enforcer under CPRA (operational 2023)
- **California Attorney General**: Retains enforcement authority
- **Private right of action**: Limited to data breaches from failure to maintain reasonable security

### CCPA vs GDPR Comparison

| Aspect | CCPA/CPRA | GDPR |
|--------|----------|------|
| Scope | California consumers | EU/EEA data subjects |
| Legal basis | Opt-out model | Opt-in (consent or legal basis) |
| Data covered | Personal information | Personal data |
| Sensitive data | SPI with limit-use right | Special category with explicit consent |
| Breach notification | AG notification, private action | 72-hour DPA notification |
| DPO requirement | None | Required for certain processing |
| Penalties | $2,500-$7,500 per violation | Up to 4% global revenue or €20M |
| Private right of action | Data breaches only | Varies by member state |
| Cross-border transfers | No restrictions | Adequacy decisions, SCCs, BCRs |
| Children's data | Opt-in for under 16, parental for under 13 | Parental consent for under 16 (variable) |

### Infrastructure Privacy Controls

**Cookie Consent Management:**
- Implement cookie consent banner for non-essential cookies
- Honor Global Privacy Control (GPC) browser signals (legally required)
- Maintain cookie inventory with retention periods
- Categorize cookies: strictly necessary, functional, analytics, advertising

**Global Privacy Control (GPC):**
- Businesses must treat GPC signal as valid opt-out request (§1798.135)
- Technical implementation: detect `Sec-GPC: 1` header or `navigator.globalPrivacyControl`
- Apply opt-out to sale AND sharing of PI
- No re-authentication required for GPC

**Privacy by Design:**
- Data minimization: collect only PI necessary for disclosed purposes
- Purpose limitation: use PI only for purposes disclosed at collection
- Storage limitation: retain PI only as long as necessary
- Security by default: encrypt PI at rest and in transit

**Data Inventory and Mapping:**
- Maintain comprehensive PI inventory across all systems
- Map data flows: collection → processing → sharing → deletion
- Document retention schedules per PI category
- Track cross-border data transfers

**Automated Decision-Making:**
- Disclose use of automated decision-making technology
- Provide opt-out for profiling that produces legal or significant effects
- CPRA regulations may require access to logic of automated decisions

### Compliance Roadmap

**Month 1-2: Discovery and Assessment**
- Determine CCPA/CPRA applicability
- Conduct data inventory and mapping
- Gap analysis against requirements
- Assign compliance ownership

**Month 3-4: Implementation**
- Draft/update privacy policy
- Implement "Do Not Sell or Share" link
- Implement "Limit Use of SPI" link
- Deploy GPC signal detection
- Build consumer request intake and fulfillment workflows
- Draft service provider/contractor agreements

**Month 5-6: Operationalization**
- Train employees on privacy obligations
- Test consumer request workflows end-to-end
- Conduct initial risk assessment
- Plan annual cybersecurity audit
- Establish ongoing monitoring and metrics
- Document compliance program for regulatory defense

---

## Troubleshooting

| Problem | Possible Cause | Resolution |
|---------|---------------|------------|
| Compliance score unexpectedly low despite privacy policy updates | Policy disclosures incomplete -- missing SPI categories, retention periods, or sale/sharing categories | Run `ccpa_compliance_checker.py --input profile.json` and review per-category scores; cross-reference privacy policy against the 17+ required disclosure elements |
| Data mapper flags cross-border transfers but organization operates only in US | Data inventory includes cloud services with non-US processing locations | Review data inventory entries for cloud provider data processing locations; document all sub-processor locations per service provider agreements |
| Consumer rights requests consistently exceed 45-day response deadline | Manual fulfillment process without tracking system or unclear ownership | Implement `ccpa_data_mapper.py` to map PI across all systems; deploy request tracking with automated deadline alerts; assign per-system data stewards |
| GPC signal detection not working | Application does not check `Sec-GPC: 1` header or `navigator.globalPrivacyControl` | Implement server-side header detection and client-side JavaScript check; test with browsers that support GPC (Firefox, Brave); log detection events |
| CPPA enforcement inquiry received | Potential compliance gap discovered during regulatory sweep or consumer complaint | Immediately run full compliance assessment; prioritize critical gaps (opt-out link, GPC, privacy policy); engage privacy counsel; document remediation timeline |
| Vendor contracts missing CCPA-required provisions | Service provider agreements predate CPRA amendments | Audit all vendor agreements against CCPA service provider/contractor requirements; update contracts to include certification, limited use, audit rights, and data deletion obligations |
| Risk assessment requirements unclear | New CPRA regulations (effective January 1, 2026) mandate risk assessments for six processing categories | Review processing activities against the six "significant risk" categories; document risk assessments per CPPA regulatory template; plan for April 2028 attestation deadline |

---

## Success Criteria

- **Overall compliance score of 80+ on initial assessment** -- indicating foundational CCPA/CPRA controls are in place, with per-category scores identifying targeted remediation areas
- **All consumer rights requests fulfilled within 45 calendar days** -- with 10-business-day acknowledgment, tracked through a request management system with automated deadline alerts
- **Privacy policy updated at least annually** -- with documented reviews quarterly, disclosing all 11 PI categories collected, sources, purposes, third-party sharing, and all seven consumer rights
- **GPC signal honored automatically** -- detected via `Sec-GPC: 1` header and `navigator.globalPrivacyControl`, applied to both sale and sharing of PI, with no re-authentication required
- **Complete data inventory maintained** -- all PI categories mapped to collection sources, business purposes, sharing recipients, and retention schedules using `ccpa_data_mapper.py`
- **Service provider and contractor agreements include all CCPA-required provisions** -- including certification of limited use, deletion obligations, audit rights, and sub-contractor chain documentation
- **Risk assessments completed for all applicable processing activities** -- covering the six CPRA significant-risk categories, with attestation readiness by the April 2028 deadline

---

## Scope & Limitations

**In Scope:**
- CCPA/CPRA applicability determination (revenue, consumer count, PI revenue thresholds)
- Privacy policy compliance assessment against all required disclosures
- Consumer rights readiness validation (Know, Delete, Opt-Out, Correct, Portability, Limit SPI Use)
- Data inventory mapping across all 11 CCPA personal information categories
- Sensitive personal information identification per CPRA definitions
- Technical safeguard assessment (encryption, access controls, opt-out mechanisms)
- Service provider and contractor agreement requirements

**Out of Scope:**
- Legal advice or determination of exemption applicability (HIPAA, GLBA, FCRA, employment data) -- consult privacy counsel for exemption analysis
- Implementation of cookie consent management platforms or GPC signal handling code
- CCPA private right of action defense (data breach litigation) -- consult legal counsel
- Other state privacy laws (Virginia VCDPA, Colorado CPA, Connecticut CTDPA) beyond the comparison tables provided -- use jurisdiction-specific guidance
- Automated decision-making technology (ADMT) compliance under CPRA regulations effective January 2027 -- monitor CPPA rulemaking for final requirements

**Important Notes:**
- CPPA enforcement is escalating significantly in 2025-2026, with fines exceeding $1.3M in individual cases and joint multi-state enforcement sweeps targeting GPC non-compliance
- New CPRA regulations effective January 1, 2026 add risk assessment, cybersecurity audit, and updated compliance requirements -- plan implementation accordingly

---

## Integration Points

| Skill | Integration | When to Use |
|-------|-------------|-------------|
| `gdpr-dsgvo-expert` | Unified privacy program satisfying both GDPR and CCPA; cross-framework privacy mapping | When organization operates in both EU and California markets |
| `infrastructure-compliance-auditor` | Technical safeguard validation (encryption, access controls, logging) for CCPA reasonable security | When assessing infrastructure controls supporting CCPA compliance |
| `information-security-manager-iso27001` | Security controls supporting CCPA "reasonable security" requirement | When building security program that satisfies both ISO 27001 and CCPA |
| `soc2-compliance-expert` | SOC 2 controls mapped to CCPA technical safeguard requirements | When SOC 2 audit evidence supports CCPA security compliance |

---

## Tool Reference

### ccpa_compliance_checker.py

Evaluates organizational readiness against all CCPA/CPRA requirements across 8 assessment categories.

| Flag | Required | Description |
|------|----------|-------------|
| `--input <file>` | Yes (unless `--template`) | Path to JSON company profile for assessment |
| `--template` | No | Generate blank input template to stdout |
| `--json` | No | Output results in JSON format for automation |
| `--output <file>` | No | Export report to specified file path |

**Output:** Overall compliance score (0-100), per-category scores with pass/fail/partial status, prioritized findings with regulatory references, and remediation recommendations.

### ccpa_data_mapper.py

Maps personal information categories, tracks data flows, and generates data inventory reports.

| Flag | Required | Description |
|------|----------|-------------|
| `--input <file>` | Yes (unless `--template`) | Path to JSON data inventory for mapping |
| `--template` | No | Generate blank inventory template to stdout |
| `--output <file>` | No | Export mapping report to specified file path |
| `--flow-diagram` | No | Generate text-based data flow diagram showing collection, use, sharing, and selling paths |

**Output:** PI category mapping across all 11 CCPA categories, SPI identification, data flow analysis (sources, purposes, recipients), cross-border transfer flags, and data retention gap detection.
