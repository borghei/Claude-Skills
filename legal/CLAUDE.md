# Legal Domain Skills — Claude Code Guidance

> **⚠️ EXPERIMENTAL — USE AT YOUR OWN RISK**
> 
> All legal skills in this domain are **experimental** and provided for educational and informational purposes only. They do **NOT** constitute legal advice. The entire responsibility for any use of these skills, their outputs, or any decisions made based on them rests solely with the user. Always consult qualified legal professionals before acting on any output from these tools.

This guide covers the **17 production-ready legal skills** spanning contract analysis, privacy compliance, risk assessment, dispute resolution, and legal operations. These skills provide structured frameworks, scoring tools, and document generation for legal workflows.

## Legal Skills Overview (17 Skills)

### Contract Analysis (4 skills)
- **contract-review** — Analyze agreements against playbooks with GREEN/YELLOW/RED severity and redline suggestions
- **nda-triage** — Rapid NDA screening with 10-point checklist, GREEN/YELLOW/RED classification
- **nda-review** — Deep clause-by-clause NDA review from Recipient or Discloser perspective with issue logs
- **tech-contract-negotiation** — Three-Position Framework for technology services agreements and B2B contracts

### Privacy & Data Protection (4 skills)
- **privacy-compliance** — Multi-regulation privacy navigator across 9 global frameworks (GDPR, CCPA, LGPD, POPIA, PIPEDA, PDPA, Privacy Act, PIPL, UK GDPR)
- **privacy-notice-generator** — Draft GDPR-compliant privacy notices for 9 EU/EEA jurisdictions with multi-layer verification
- **dpia-assessment** — GDPR Art. 35 Data Protection Impact Assessment with threshold checking and EDPB criteria scoring
- **data-breach-response** — Incident response with ENISA severity scoring, notification timelines, and multi-regulation compliance

### Risk & Compliance (4 skills)
- **legal-risk-assessment** — Structured 5x5 Severity x Likelihood matrix with risk registers and escalation guidance
- **vendor-due-diligence** — Multi-factor risk scoring for IT vendors across 6 dimensions and 8 compliance frameworks
- **whistleblower-compliance** — Audit whistleblower systems and draft compliant policies (EU Directive, SOX, Dodd-Frank, UK PIDA)
- **statute-analysis** — Statute and regulation interpretation framework with canons of construction and obligation mapping

### Legal Operations (3 skills)
- **legal-canned-responses** — Templated responses for 7 categories of common legal inquiries with escalation detection
- **legal-meeting-briefing** — Structured briefings for 8 meeting types with action item tracking
- **tabular-document-review** — Extract structured data from multiple documents into comparison matrices with citations

### Quality & Strategy (2 skills)
- **legal-red-team** — Adversarial verification for AI-generated legal content with hallucination detection and quality scoring
- **mediation-analysis** — Dispute analysis with settlement calculation, interest mapping, and BATNA assessment

**Total:** 17 specialized legal skills | 34 Python tools | 30+ reference guides

## Quick Reference

| Skill | Primary Use | When to Use |
|-------|-------------|-------------|
| **contract-review** | Agreement analysis | Reviewing vendor contracts, SaaS agreements, service agreements |
| **nda-triage** | NDA screening | Triaging incoming NDAs, routing for approval |
| **nda-review** | NDA deep review | Clause-by-clause negotiation prep with redlines |
| **tech-contract-negotiation** | Tech deal negotiation | Negotiating technology services, B2B contracts ($100K-$10M+) |
| **privacy-compliance** | Privacy regulation | GDPR/CCPA/LGPD assessments, DPA reviews, DSR management |
| **privacy-notice-generator** | Privacy notice drafting | Creating GDPR-compliant notices for EU/EEA jurisdictions |
| **dpia-assessment** | DPIA evaluation | Determining DPIA necessity, managing privacy risk registers |
| **data-breach-response** | Breach response | Breach severity scoring, notification timeline tracking |
| **legal-risk-assessment** | Risk scoring | Building risk registers, escalation decisions, risk memos |
| **vendor-due-diligence** | Vendor assessment | Evaluating technology vendors and third-party partners |
| **whistleblower-compliance** | Whistleblower programs | Auditing reporting systems, drafting compliant policies |
| **statute-analysis** | Statutory interpretation | Reading statutes, classifying requirements, mapping obligations |
| **legal-canned-responses** | Legal intake responses | Handling high-volume recurring legal inquiries |
| **legal-meeting-briefing** | Meeting preparation | Prepping legal meetings, tracking action items |
| **tabular-document-review** | Bulk document review | Comparing contracts, NDA sets, employment agreements |
| **legal-red-team** | Content verification | Fact-checking AI-generated legal content, citation validation |
| **mediation-analysis** | Dispute preparation | Mediation prep, settlement range calculation, BATNA analysis |

## Legal Workflows

### Workflow 1: Contract Lifecycle
```
1. NDA Screening → nda-triage
2. NDA Deep Review → nda-review
3. Contract Review → contract-review
4. Tech Deal Negotiation → tech-contract-negotiation
5. Vendor Assessment → vendor-due-diligence
6. Risk Scoring → legal-risk-assessment
```

### Workflow 2: Privacy Program
```
1. Regulation Mapping → privacy-compliance
2. DPIA Evaluation → dpia-assessment
3. Privacy Notice Drafting → privacy-notice-generator
4. Breach Response Planning → data-breach-response
5. Vendor Privacy Assessment → vendor-due-diligence
```

### Workflow 3: Bulk Document Review
```
1. Document Extraction → tabular-document-review
2. Risk Assessment → legal-risk-assessment
3. Quality Verification → legal-red-team
4. Meeting Briefing → legal-meeting-briefing
```

## Cross-Domain Integration

- **Legal <-> Engineering:** Contract review for SaaS/technology agreements; statute analysis for software compliance requirements
- **Legal <-> RA/QM Compliance:** Privacy compliance aligns with GDPR skills; vendor due diligence maps to ISO 27001 supplier controls; whistleblower compliance supports SOX and EU directive requirements
- **Legal <-> Product:** Privacy notices and DPIAs inform product feature design; data breach response plans integrate with incident management
- **Legal <-> C-Level:** Legal risk assessments feed strategic decision-making; mediation analysis supports dispute resolution at executive level

## Quick Start by Scenario

| Your Scenario | Start With | Then Add |
|---------------|-----------|----------|
| **Reviewing Contracts** | contract-review | legal-risk-assessment, tech-contract-negotiation |
| **NDA Volume** | nda-triage | nda-review (for flagged NDAs) |
| **Privacy Program** | privacy-compliance | dpia-assessment, privacy-notice-generator |
| **Data Breach** | data-breach-response | privacy-compliance, legal-risk-assessment |
| **Vendor Onboarding** | vendor-due-diligence | contract-review, legal-risk-assessment |
| **AI-Generated Content** | legal-red-team | statute-analysis |
| **Dispute Resolution** | mediation-analysis | legal-risk-assessment |
| **Legal Ops Efficiency** | legal-canned-responses | legal-meeting-briefing, tabular-document-review |
| **Regulatory Research** | statute-analysis | privacy-compliance, whistleblower-compliance |

## Additional Resources

- **Main Documentation:** `../CLAUDE.md`
- **RA/QM Compliance (related):** `../ra-qm-team/CLAUDE.md`
- **Standards Library:** `../standards/`

---

**Last Updated:** 2026-04-10
**Skills Deployed:** 17/17 legal skills production-ready
**Tools:** 34 Python automation tools
**References:** 30+ reference guides
**Focus:** Legal operations — from contract analysis to privacy compliance, from risk assessment to dispute resolution
