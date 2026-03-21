---
name: regulatory-affairs-head
description: >
  Senior Regulatory Affairs Manager for HealthTech and MedTech companies. Use when
  developing regulatory strategy, preparing FDA 510(k)/PMA/De Novo submissions,
  planning EU MDR CE marking, coordinating global market access, or monitoring
  regulatory intelligence. Provides pathway analysis, submission management,
  timeline planning, and cross-functional regulatory leadership.
triggers:
  - regulatory strategy
  - FDA submission
  - EU MDR
  - 510(k)
  - PMA approval
  - CE marking
  - regulatory pathway
  - market access
  - clinical evidence
  - regulatory intelligence
  - submission planning
  - notified body
---

# Head of Regulatory Affairs

Regulatory strategy development, submission management, and global market access for medical device organizations.

---

## Regulatory Strategy Workflow

The agent develops regulatory strategy aligned with business objectives and product characteristics.

### Workflow: New Product Regulatory Strategy

1. **Gather product information** -- collect intended use, device classification (risk level), technology platform, target markets, and timeline from stakeholders.
2. **Identify applicable regulations** per target market:
   - FDA (US): 21 CFR Part 820, 510(k)/PMA/De Novo
   - EU: MDR 2017/745, Notified Body requirements
   - Other markets: Health Canada, PMDA, NMPA, TGA
3. **Determine optimal regulatory pathway** using the pathway selection matrix below -- compare submission types, assess predicate device availability, evaluate clinical evidence requirements.
4. **Develop regulatory timeline** with milestones and critical path dependencies.
5. **Estimate resource requirements** -- budget, personnel (FTEs), external consultants/CRO.
6. **Identify regulatory risks** and define mitigation strategies for each.
7. **Obtain stakeholder alignment** -- present strategy for executive approval.
8. **Validation checkpoint:** Strategy document approved; timeline accepted by all stakeholders; resources allocated and confirmed.

### Regulatory Pathway Selection Matrix

| Factor | 510(k) | De Novo | PMA |
|--------|--------|---------|-----|
| Predicate Available | Yes | No | N/A |
| Risk Level | Low-Moderate | Low-Moderate | High |
| Clinical Data | Usually not required | May be required | Required |
| Review Time | 90 days (MDUFA) | 150 days | 180 days |
| User Fee | ~$22K (2024) | ~$135K | ~$440K |
| Best For | Me-too devices | Novel low-risk | High-risk, novel |

### Example: Regulatory Strategy Output

```
REGULATORY STRATEGY

Product: CardioSense Wearable ECG Monitor
Version: 1.0
Date: 2026-03-12

1. PRODUCT OVERVIEW
   - Intended use: Continuous ECG monitoring for arrhythmia detection
   - Device classification: Class II (FDA), Class IIa (EU MDR)
   - Technology: Single-lead ECG with ML-based AF detection

2. TARGET MARKETS
   | Market | Priority | Timeline    |
   |--------|----------|-------------|
   | USA    | 1        | Q3 2026     |
   | EU     | 2        | Q1 2027     |
   | Canada | 3        | Q2 2027     |

3. REGULATORY PATHWAY
   - FDA: 510(k) — Predicate: AliveCor KardiaMobile (K142743)
   - EU: Class IIa via Annex IX (QMS) + Annex XI Part A (Product)
   - Rationale: Established predicate supports SE argument;
     MDR IIa classification per Rule 10 (active diagnostic)

4. CLINICAL EVIDENCE STRATEGY
   - Requirements: SE comparison + analytical performance data
   - Approach: Literature review for AF detection + bench study

5. RISKS AND MITIGATION
   | Risk                     | Probability | Impact | Mitigation                    |
   |--------------------------|-------------|--------|-------------------------------|
   | FDA requests clinical    | Medium      | High   | Pre-Sub meeting to align      |
   | NB capacity delay        | High        | Medium | Engage NB by Q4 2025         |
   | ML algorithm as SaMD     | Medium      | High   | Follow FDA AI/ML SaMD guidance|
```

---

## FDA Submission Workflow

The agent prepares and submits FDA regulatory applications following established pathways.

### Workflow: 510(k) Submission

1. **Confirm 510(k) pathway suitability** -- verify predicate device identified, substantial equivalence supportable, no new intended use or technology concerns.
2. **Schedule Pre-Submission (Q-Sub) meeting** if novel technology, uncertain predicate, or complex testing is involved.
3. **Compile submission package:**
   - Cover letter and administrative information
   - Device description and intended use
   - Substantial equivalence comparison
   - Performance testing data
   - Biocompatibility (if patient contact, per ISO 10993)
   - Software documentation (if applicable, per IEC 62304)
   - Labeling and IFU
4. **Conduct internal review** -- quality check all sections against FDA checklist.
5. **Prepare eCopy** per current FDA format requirements.
6. **Submit via FDA ESG portal** with user fee payment.
7. **Monitor MDUFA clock** and respond to AI/RTA requests within deadline.
8. **Validation checkpoint:** Submission accepted (RTA complete); MDUFA goal date received; tracking system updated.

### Workflow: PMA Submission

1. **Confirm PMA pathway** -- Class III device or no suitable predicate; clinical data strategy defined.
2. **Complete IDE clinical study** if required -- IDE approval, protocol execution, study report.
3. **Conduct Pre-Submission meeting** with FDA.
4. **Compile PMA submission** -- administrative/device information, manufacturing information, nonclinical studies, clinical studies, labeling.
5. **Submit original PMA** application.
6. **Address FDA questions** and deficiency letters within specified timeframes.
7. **Prepare for FDA facility inspection** -- coordinate with Quality team.
8. **Validation checkpoint:** PMA approved; approval letter received; post-approval requirements documented.

### FDA Submission Timeline

| Milestone | 510(k) | De Novo | PMA |
|-----------|--------|---------|-----|
| Pre-Sub Meeting | Day -90 | Day -90 | Day -120 |
| Submission | Day 0 | Day 0 | Day 0 |
| RTA Review | Day 15 | Day 15 | Day 45 |
| Substantive Review | Days 15-90 | Days 15-150 | Days 45-180 |
| Decision | Day 90 | Day 150 | Day 180 |

### Common FDA Deficiencies

| Category | Common Issues | Prevention |
|----------|---------------|------------|
| Substantial Equivalence | Weak predicate comparison | Strong SE argument upfront |
| Performance Testing | Incomplete test protocols | Follow recognized standards |
| Biocompatibility | Missing endpoints | ISO 10993 risk assessment |
| Software | Inadequate documentation | IEC 62304 compliance |
| Labeling | Inconsistent claims | Early labeling review |

See: [references/fda-submission-guide.md](references/fda-submission-guide.md)

---

## EU MDR Submission Workflow

The agent achieves CE marking under EU MDR 2017/745.

### Workflow: MDR Technical Documentation

1. **Confirm device classification** per MDR Annex VIII rules.
2. **Select conformity assessment route** based on class:
   - Class I: Self-declaration
   - Class IIa/IIb: Notified Body involvement
   - Class III: Full NB assessment
3. **Select and engage Notified Body** (for Class IIa+) -- evaluate scope, capacity, experience, and timeline.
4. **Compile Technical Documentation** per Annex II:
   - Device description and specifications
   - Design and manufacturing information
   - GSPR checklist (General Safety and Performance Requirements)
   - Benefit-risk analysis and risk management (ISO 14971)
   - Clinical evaluation per Annex XIV
   - Post-market surveillance plan
5. **Establish and document QMS** per ISO 13485.
6. **Submit application to Notified Body.**
7. **Address NB questions** and coordinate audit logistics.
8. **Validation checkpoint:** CE certificate issued; Declaration of Conformity signed; EUDAMED registration complete.

### Clinical Evidence Requirements by Class

| Class | Clinical Requirement | Documentation |
|-------|---------------------|---------------|
| I | Clinical evaluation (CE) | CE report |
| IIa | CE with literature focus | CE report + PMCF plan |
| IIb | CE with clinical data | CE report + PMCF + clinical study (some) |
| III | CE with clinical investigation | CE report + PMCF + clinical investigation |

### Notified Body Selection Criteria

| Criterion | Consideration |
|-----------|---------------|
| Scope | Device category expertise |
| Capacity | Availability and review timeline |
| Experience | Track record in your technology |
| Geography | Proximity for audits |
| Cost | Fee structure transparency |
| Communication | Responsiveness and clarity |

See: [references/eu-mdr-submission-guide.md](references/eu-mdr-submission-guide.md)

---

## Global Market Access Workflow

The agent coordinates regulatory approvals across international markets.

### Workflow: Multi-Market Submission Strategy

1. **Define target markets** based on business priorities and revenue projections.
2. **Sequence markets** for efficient evidence leverage:
   - Phase 1: FDA + EU (reference markets)
   - Phase 2: Recognition markets (Canada via MDSAP, Australia via TGA)
   - Phase 3: Major markets (Japan PMDA, China NMPA)
   - Phase 4: Emerging markets
3. **Identify local requirements** per market -- clinical data acceptability, local agent/representative needs, language and labeling requirements.
4. **Develop master technical file** with localization plan.
5. **Establish in-country regulatory support.**
6. **Execute parallel or sequential submissions** per sequencing strategy.
7. **Track approvals** and coordinate product launches.
8. **Validation checkpoint:** All target market approvals obtained; registration database updated; launch dates confirmed.

### Market Priority Matrix

| Market | Size | Complexity | Recognition | Priority |
|--------|------|------------|-------------|----------|
| USA | Large | High | N/A | 1 |
| EU | Large | High | N/A | 1-2 |
| Canada | Medium | Medium | MDSAP | 2 |
| Australia | Medium | Low | EU accepted | 2 |
| Japan | Large | High | Local clinical | 3 |
| China | Large | Very High | Local testing | 3 |
| Brazil | Medium | High | GMP inspection | 3-4 |

See: [references/global-regulatory-pathways.md](references/global-regulatory-pathways.md)

---

## Regulatory Intelligence Workflow

The agent monitors and responds to regulatory changes affecting the product portfolio.

### Workflow: Regulatory Change Management

1. **Monitor regulatory sources** -- FDA Federal Register, EU Official Journal, MDCG guidance, Notified Body communications, industry associations (AdvaMed, MedTech Europe).
2. **Assess relevance** to current product portfolio and pipeline.
3. **Evaluate impact** -- timeline to compliance, resource requirements, product changes needed.
4. **Develop compliance action plan** with owners and deadlines.
5. **Communicate to affected stakeholders** across functions.
6. **Implement required changes** within established timelines.
7. **Document compliance status** for management review and audit readiness.
8. **Validation checkpoint:** Compliance action plan approved; changes implemented on schedule; no gaps at next audit.

### Regulatory Monitoring Sources

| Source | Type | Frequency |
|--------|------|-----------|
| FDA Federal Register | Regulations, guidance | Daily |
| FDA Device Database | 510(k), PMA, recalls | Weekly |
| EU Official Journal | MDR/IVDR updates | Weekly |
| MDCG Guidance | EU implementation | As published |
| ISO/IEC | Standards updates | Quarterly |
| Notified Body | Audit findings, trends | Per interaction |

---

## Decision Frameworks

### Pathway Selection Decision Tree

```
Is predicate device available?
            |
        Yes-+-No
         |     |
         v     v
    Is device   Is risk level
    substantially  Low-Moderate?
    equivalent?       |
         |        Yes-+-No
     Yes-+-No      |     |
      |     |      v     v
      v     v   De Novo  PMA
    510(k)  Consider      required
           De Novo
           or PMA
```

### Pre-Submission Meeting Decision

| Factor | Schedule Pre-Sub | Skip Pre-Sub |
|--------|------------------|--------------|
| Novel Technology | Yes | |
| New Intended Use | Yes | |
| Complex Testing | Yes | |
| Uncertain Predicate | Yes | |
| Clinical Data Needed | Yes | |
| Well-established | | Yes |
| Clear Predicate | | Yes |
| Standard Testing | | Yes |

### Regulatory Escalation Criteria

| Situation | Escalation Level | Action |
|-----------|------------------|--------|
| Submission rejection | VP Regulatory | Root cause analysis, strategy revision |
| Major deficiency | Director | Cross-functional response team |
| Timeline at risk | Management | Resource reallocation review |
| Regulatory change | VP Regulatory | Portfolio impact assessment |
| Safety signal | Executive | Immediate containment and reporting |

---

## Tools and References

### Scripts

| Tool | Purpose | Usage |
|------|---------|-------|
| [regulatory_tracker.py](scripts/regulatory_tracker.py) | Track submission status and timelines | `python regulatory_tracker.py --help` |

```bash
# Example: Track active submissions
python scripts/regulatory_tracker.py --status active --format markdown

# Example: Check overdue submissions
python scripts/regulatory_tracker.py --overdue --notify
```

### References

| Document | Content |
|----------|---------|
| [fda-submission-guide.md](references/fda-submission-guide.md) | FDA pathways, requirements, review process |
| [eu-mdr-submission-guide.md](references/eu-mdr-submission-guide.md) | MDR classification, technical documentation, clinical evidence |
| [global-regulatory-pathways.md](references/global-regulatory-pathways.md) | Canada, Japan, China, Australia, Brazil requirements |
| [iso-regulatory-requirements.md](references/iso-regulatory-requirements.md) | ISO 13485, 14971, 10993, IEC 62304, 62366 requirements |

### Key Performance Indicators

| KPI | Target | Calculation |
|-----|--------|-------------|
| First-time approval rate | >85% | (Approved without major deficiency / Total submitted) x 100 |
| On-time submission | >90% | (Submitted by target date / Total submissions) x 100 |
| Review cycle compliance | >95% | (Responses within deadline / Total requests) x 100 |
| Regulatory hold time | <20% | (Days on hold / Total review days) x 100 |

---

## Related Skills

| Skill | Integration Point |
|-------|-------------------|
| [mdr-745-specialist](../mdr-745-specialist/) | Detailed EU MDR technical requirements |
| [fda-consultant-specialist](../fda-consultant-specialist/) | FDA submission deep expertise |
| [quality-manager-qms-iso13485](../quality-manager-qms-iso13485/) | QMS for regulatory compliance |
| [risk-management-specialist](../risk-management-specialist/) | ISO 14971 risk management |

---

## Troubleshooting

| Problem | Likely Cause | Resolution |
|---------|-------------|------------|
| Regulatory tracker shows "No existing data file found" | Data file does not exist at the expected path | Create an initial submissions JSON file or use the tracker to add a first submission. The tool creates the file on first save. |
| Submission status shows as PLANNING when it should be SUBMITTED | Status not updated after submission | Update the submission record with `submission_status: SUBMITTED` and `submission_date`. The tracker does not auto-detect FDA ESG submission status. |
| Overdue notification fires for approved submission | `actual_approval_date` field not populated | Update the record with the actual approval date. The tracker compares `target_approval_date` against today when `actual_approval_date` is null. |
| 510(k) pathway selected but clinical data still needed | Novel technology or uncertain predicate | Schedule a Pre-Submission (Q-Sub) meeting with FDA. Novel technologies or complex testing may require clinical evidence even under the 510(k) pathway. |
| Notified Body timeline exceeds plan | NB capacity constraints (common in 2025-2026) | Engage the NB as early as possible (6+ months before target submission). The number of designated MDR NBs has grown to ~50 as of 2024, but capacity remains tight for complex device classes. |
| EUDAMED registration blocked | EUDAMED modules not yet mandatory or data upload issues | Develop a secure process for uploading device data into EUDAMED. Certain modules become mandatory in 2026. Prepare data structures proactively. |
| Multi-market submission timeline keeps slipping | Sequential submissions creating cascading delays | Where possible, shift to parallel submission strategy. Use FDA + EU as reference markets and leverage MDSAP for recognition markets (Canada, Australia, Japan, Brazil). |

---

## Success Criteria

- First-time regulatory approval rate exceeds 85% across all submission types (510(k), PMA, De Novo, CE marking)
- Regulatory submission timelines met for 90%+ of submissions (submitted by target date)
- Pre-Submission meetings scheduled and completed for all novel technology, uncertain predicate, or complex testing submissions
- FDA review cycle compliance exceeds 95% (responses to AI/RTA/deficiency requests submitted within deadline)
- EU MDR Technical Documentation complete and accepted by Notified Body with no critical findings on first review
- Global market access strategy documented with phased market sequencing, resource estimates, and risk mitigation for each target jurisdiction
- Regulatory intelligence monitoring active for all applicable jurisdictions with change assessments completed within 30 days of publication

---

## Scope & Limitations

**In Scope:**
- Regulatory strategy development for medical devices across FDA, EU MDR, and global markets
- FDA submission management (510(k), PMA, De Novo, Q-Sub/Pre-Submission)
- EU MDR conformity assessment route selection and Notified Body engagement
- Global market access planning and multi-market submission sequencing
- Regulatory intelligence monitoring and change management
- Submission timeline planning and milestone tracking
- Regulatory pathway selection decision frameworks

**Out of Scope:**
- Clinical trial design, execution, or data analysis (the skill addresses clinical evidence strategy but not clinical operations)
- Detailed technical file content creation (use mdr-745-specialist for GSPR checklists, Annex II documentation)
- Quality system management (use quality-manager-qms-iso13485 for QMS processes)
- Post-market surveillance program execution (the skill defines PMS strategy but execution is managed by PMS teams)
- Reimbursement strategy or health technology assessment (HTA) submissions
- Patent or intellectual property strategy related to regulatory pathways
- In vitro diagnostic (IVD) specific regulatory requirements under IVDR 2017/746

---

## Integration Points

| Skill | Integration |
|-------|------------|
| [mdr-745-specialist](../mdr-745-specialist/) | Detailed EU MDR technical requirements, GSPR checklists, Annex VIII classification rules, and EUDAMED registration |
| [fda-consultant-specialist](../fda-consultant-specialist/) | FDA submission deep expertise including QMSR alignment, HIPAA, cybersecurity guidance, and 510(k)/PMA specifics |
| [quality-manager-qms-iso13485](../quality-manager-qms-iso13485/) | QMS certification is a prerequisite for MDR conformity assessment and supports FDA QMSR compliance |
| [risk-management-specialist](../risk-management-specialist/) | ISO 14971 risk management file is required for both FDA submissions and EU MDR Technical Documentation |
| [quality-manager-qmr](../quality-manager-qmr/) | Regulatory changes affecting the QMS are management review inputs; QMR coordinates compliance across jurisdictions |

---

## Tool Reference

### regulatory_tracker.py

Tracks regulatory submission status, timelines, and overdue notifications across all markets.

| Flag | Required | Description |
|------|----------|-------------|
| `--status` | No | Filter submissions by status: `active`, `planning`, `submitted`, `approved`, `all` |
| `--overdue` | No | Show only submissions past their target approval date without an actual approval date |
| `--notify` | No | Generate notification alerts for overdue or at-risk submissions |
| `--format` | No | Output format: `markdown` for formatted text, omit for default display |

Note: The tracker operates on a `regulatory_submissions.json` data file (default path). Submissions are added and updated programmatically through the `RegulatoryTracker` class API. The tool supports submission types: FDA_510K, FDA_PMA, FDA_DE_NOVO, EU_MDR_CE, ISO_CERTIFICATION, GLOBAL_REGULATORY.
