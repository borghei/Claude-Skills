---
name: privacy-compliance
description: >
  Multi-regulation privacy compliance navigator. Use for GDPR, CCPA, LGPD,
  POPIA, PIPEDA, PDPA, Privacy Act, PIPL, UK GDPR compliance assessments,
  DPA reviews, and data subject request management.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: The Glass Room
  category: legal
  domain: privacy-compliance
  updated: 2026-04-10
  tags: [privacy, gdpr, ccpa, data-protection, compliance]
---
> **⚠️ EXPERIMENTAL** — This skill is provided for educational and informational purposes only. It does NOT constitute legal advice. All responsibility for usage rests with the user. Consult qualified legal professionals before acting on any output.

# Privacy Compliance Navigator

Tools and guidance for multi-regulation privacy compliance across 9 major global privacy frameworks, DPA review, and data subject request lifecycle management.

---

## Table of Contents

- [Tools](#tools)
  - [Privacy Regulation Checker](#privacy-regulation-checker)
  - [DSR Tracker](#dsr-tracker)
- [Reference Guides](#reference-guides)
- [Workflows](#workflows)
- [Troubleshooting](#troubleshooting)
- [Success Criteria](#success-criteria)
- [Scope & Limitations](#scope--limitations)
- [Anti-Patterns](#anti-patterns)
- [Tool Reference](#tool-reference)

---

## Tools

### Privacy Regulation Checker

Determines which privacy regulations apply to an organization based on its location, data subjects, data types, and processing activities. Generates a compliance obligations matrix and flags gaps.

```bash
# Basic check — organization in Germany processing EU and US data
python scripts/privacy_regulation_checker.py \
  --org-location DE \
  --data-subjects EU,US \
  --data-types personal,sensitive,financial \
  --processing-activities marketing,analytics,hr

# JSON output for integration
python scripts/privacy_regulation_checker.py \
  --org-location SG \
  --data-subjects SG,AU,CN \
  --data-types personal,health \
  --processing-activities healthcare,research \
  --json

# Include gap analysis against current practices
python scripts/privacy_regulation_checker.py \
  --org-location US-CA \
  --data-subjects EU,US,BR \
  --data-types personal,biometric \
  --processing-activities ecommerce,profiling \
  --current-practices consent_mechanism,breach_process,retention_policy
```

**Determines:**
- Which of 9 regulations apply based on territorial scope rules
- Key obligations per applicable regulation
- Data subject rights required per regulation
- Response timelines per regulation
- Gap analysis when current practices are provided

**Output:**
- Applicable regulations list with confidence level
- Per-regulation obligations matrix
- Gap analysis with risk ratings
- Recommended priority actions

---

### DSR Tracker

Manages Data Subject Request lifecycle across multiple regulations with deadline calculation, status tracking, and overdue alerts.

```bash
# Add a new GDPR access request
python scripts/dsr_tracker.py add \
  --type access --regulation gdpr \
  --subject "Jane Smith" --email "jane@example.com"

# Add CCPA deletion request
python scripts/dsr_tracker.py add \
  --type deletion --regulation ccpa \
  --subject "John Doe" --email "john@example.com"

# List all open requests
python scripts/dsr_tracker.py list

# List overdue requests only
python scripts/dsr_tracker.py list --overdue

# Update request status
python scripts/dsr_tracker.py update --id DSR-0001 --status verified

# Dashboard view with time remaining
python scripts/dsr_tracker.py dashboard

# Export as JSON
python scripts/dsr_tracker.py dashboard --json
```

**Supported Request Types:**

| Type | GDPR Art. | CCPA Section | LGPD Art. |
|------|-----------|-------------|-----------|
| Access | Art. 15 | §1798.100 | Art. 18 |
| Deletion/Erasure | Art. 17 | §1798.105 | Art. 18(VI) |
| Correction/Rectification | Art. 16 | §1798.106 | Art. 18(III) |
| Portability | Art. 20 | §1798.130 | Art. 18(V) |
| Restriction | Art. 18 | — | Art. 18(IV) |
| Objection | Art. 21 | §1798.120 | Art. 18(IV) |
| Automated Decision Opt-Out | Art. 22 | §1798.185 | Art. 20 |
| Withdraw Consent | Art. 7(3) | — | Art. 18(IX) |

**Deadline Calculation:**

| Regulation | Initial Deadline | Extension | Extension Deadline |
|-----------|-----------------|-----------|-------------------|
| GDPR | 30 calendar days | +60 days (complex) | 90 calendar days |
| CCPA | 10 business days (ack) + 45 calendar days | +45 days | 90 calendar days |
| LGPD | 15 calendar days | — | — |
| POPIA | 30 calendar days | — | — |
| PIPEDA | 30 calendar days | +30 days | 60 calendar days |
| PDPA (SG) | 30 calendar days | — | — |
| Privacy Act (AU) | 30 calendar days | +30 days | 60 calendar days |
| PIPL | 15 calendar days | +15 days | 30 calendar days |
| UK GDPR | 30 calendar days | +60 days | 90 calendar days |

**Statuses:** received → verified → processing → completed | denied | extended

---

## Reference Guides

### Global Privacy Regulations
`references/global_privacy_regulations.md`

Comprehensive comparison of 9 major privacy regulations covering:
- Territorial scope and applicability criteria
- Legal bases for processing
- Data subject rights comparison matrix
- Breach notification requirements and timelines
- Cross-border transfer mechanisms
- DPO requirements
- Penalty structures

### DPA Review Checklist
`references/dpa_review_checklist.md`

Complete Data Processing Agreement review guide:
- Art. 28 GDPR required elements
- 10 processor obligations with analysis points
- International transfer mechanisms (SCCs June 2021, module selection)
- Transfer impact assessment requirements
- Common DPA issues with risk levels
- Practical negotiation considerations

### DSR Handling Guide
`references/dsr_handling_guide.md`

Data Subject Request handling reference:
- 8 request types with intake procedures
- Identity verification methods
- Response timelines per regulation
- Exemptions by regulation
- 6-step response process
- Regulatory monitoring approach

---

## Workflows

### Workflow 1: Regulation Applicability Assessment

```
Step 1: Identify organization parameters
        → Location, data subjects, data types, processing activities

Step 2: Run regulation checker
        → python scripts/privacy_regulation_checker.py --org-location [LOC] ...

Step 3: Review applicable regulations and obligations
        → Prioritize by risk (penalties, data volume, enforcement activity)

Step 4: Gap analysis against current practices
        → Re-run with --current-practices flag

Step 5: Build remediation roadmap
        → Address critical gaps first (missing legal basis, no breach process)
```

### Workflow 2: Data Subject Request Handling

```
Step 1: Receive and log request
        → python scripts/dsr_tracker.py add --type [type] --regulation [reg] ...

Step 2: Verify identity (proportionate to sensitivity)
        → See references/dsr_handling_guide.md for methods
        → python scripts/dsr_tracker.py update --id [ID] --status verified

Step 3: Gather data from all systems
        → python scripts/dsr_tracker.py update --id [ID] --status processing

Step 4: Apply exemptions if applicable
        → Check references/dsr_handling_guide.md exemptions table

Step 5: Prepare and send response within deadline
        → python scripts/dsr_tracker.py update --id [ID] --status completed

Step 6: Monitor dashboard for overdue requests
        → python scripts/dsr_tracker.py dashboard
```

### Workflow 3: DPA Review

```
Step 1: Check DPA against Art. 28 required elements
        → Use references/dpa_review_checklist.md

Step 2: Verify processor obligations (10 items)
        → Sub-processing, deletion, audit rights, etc.

Step 3: Assess international transfer provisions
        → SCC module selection (C2P, C2C, P2P, P2C)
        → Transfer impact assessment
        → Supplementary measures

Step 4: Review practical considerations
        → Liability caps, insurance, termination, data locations

Step 5: Document findings and negotiate amendments
```

### Workflow 4: Multi-Regulation Compliance Program

```
Step 1: Run regulation checker for full scope
        → python scripts/privacy_regulation_checker.py [params]

Step 2: Map overlapping obligations across regulations
        → Use references/global_privacy_regulations.md comparison matrix

Step 3: Build unified controls (satisfy strictest requirement)
        → GDPR-first approach covers most other regulations

Step 4: Layer regulation-specific requirements
        → CCPA opt-out mechanisms, LGPD DPO, PIPL localization

Step 5: Monitor regulatory changes
        → See references/dsr_handling_guide.md monitoring approach
```

---

## Troubleshooting

| Problem | Possible Cause | Resolution |
|---------|---------------|------------|
| Regulation checker flags unexpected regulation | Data subjects in jurisdiction not considered | Review data flow maps; even indirect data collection (analytics, cookies) can trigger territorial scope |
| DSR deadline missed | Request not logged promptly or status not updated | Implement intake SLA (log within 24 hours); use dashboard daily for overdue alerts |
| DPA missing Art. 28 elements | Template from processor is incomplete | Use DPA review checklist to identify gaps; require amendments before signing |
| Cross-border transfer mechanism unclear | Multiple transfer layers (controller → processor → sub-processor) | Map full data flow chain; each transfer leg needs its own mechanism |
| Conflicting obligations across regulations | Retention vs. deletion requirements differ | Document conflicts; apply strictest obligation unless local law mandates otherwise; seek legal counsel |
| Identity verification proportionality unclear | Over-verification deters legitimate requests | Match verification to risk: low-risk data = email confirmation; high-risk = ID verification |

---

## Success Criteria

- **All applicable regulations identified and mapped** — regulation checker confirms coverage with zero unaddressed jurisdictions where data subjects reside
- **100% of DSRs responded within statutory deadlines** — dashboard shows zero overdue requests; extension documented where used
- **DPAs reviewed against Art. 28 checklist before signing** — all 10 processor obligations addressed; international transfer mechanisms validated
- **Compliance matrix maintained and current** — quarterly review of obligations per regulation with change log
- **Regulatory monitoring active** — escalation criteria defined; new regulation applicability assessed within 30 days of enactment

---

## Scope & Limitations

**In Scope:**
- Applicability assessment for 9 major privacy regulations
- Data subject request tracking with multi-regulation deadline calculation
- DPA review against Art. 28 GDPR requirements
- Cross-regulation obligation mapping
- Gap analysis against current practices
- International transfer mechanism assessment

**Out of Scope:**
- Legal advice on specific legal basis selection — consult qualified privacy counsel
- Supervisory authority filings or breach notifications
- Cookie consent implementation or consent management platform configuration
- Binding Corporate Rules (BCR) application process
- Sector-specific regulations (HIPAA, FERPA, GLBA) beyond the 9 covered frameworks
- Data Protection Impact Assessments (see `dpia-assessment` skill)

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Better Approach |
|-------------|-------------|-----------------|
| **GDPR-only compliance** | Organizations assume GDPR covers all obligations; miss CCPA opt-out requirements, LGPD DPO mandate, PIPL data localization | Run regulation checker against all jurisdictions where data subjects reside; layer regulation-specific controls |
| **One-size-fits-all DSR process** | Applying GDPR 30-day timeline to all regulations misses CCPA 10-business-day acknowledgment or PIPL 15-day deadline | Configure per-regulation deadlines; use DSR tracker with regulation parameter for accurate deadline calculation |
| **Ignoring sub-processor chains in DPA review** | DPA covers direct processor but sub-processors transfer data to third countries without TIA | Map full processing chain in DPA review; require Art. 28(2) sub-processor obligations; validate each transfer leg |
| **Treating privacy as a one-time project** | Regulations evolve; new laws enacted; enforcement priorities shift | Implement regulatory monitoring with escalation criteria; quarterly compliance reviews |

---

## Tool Reference

### privacy_regulation_checker.py

Determines applicable privacy regulations and maps obligations based on organization parameters.

| Flag | Required | Description |
|------|----------|-------------|
| `--org-location <code>` | Yes | Organization headquarters (ISO country code, e.g., DE, US-CA, SG) |
| `--data-subjects <list>` | Yes | Comma-separated locations of data subjects (EU, US, BR, ZA, CA, SG, AU, CN, UK) |
| `--data-types <list>` | Yes | Comma-separated data types (personal, sensitive, financial, health, biometric, children) |
| `--processing-activities <list>` | Yes | Comma-separated activities (marketing, analytics, hr, ecommerce, profiling, healthcare, research) |
| `--current-practices <list>` | No | Comma-separated current practices for gap analysis |
| `--json` | No | Output in JSON format |

### dsr_tracker.py

Tracks Data Subject Request lifecycle with multi-regulation deadline calculation.

| Subcommand | Description |
|------------|-------------|
| `add` | Add new DSR (`--type`, `--regulation`, `--subject`, `--email` required) |
| `list` | List all requests (`--overdue` for overdue only) |
| `update` | Update request status (`--id`, `--status` required) |
| `dashboard` | Show dashboard with time remaining and alerts |

| Flag | Description |
|------|-------------|
| `--type <type>` | Request type: access, deletion, correction, portability, restriction, objection, automated_decision, withdraw_consent |
| `--regulation <reg>` | Regulation: gdpr, ccpa, lgpd, popia, pipeda, pdpa, privacy_act_au, pipl, uk_gdpr |
| `--subject <name>` | Data subject name |
| `--email <email>` | Data subject email |
| `--id <id>` | Request ID (e.g., DSR-0001) |
| `--status <status>` | Status: received, verified, processing, completed, denied, extended |
| `--overdue` | Filter to overdue requests only |
| `--json` | Output in JSON format |
| `--data-file <path>` | Custom data file path (default: dsr_requests.json) |
