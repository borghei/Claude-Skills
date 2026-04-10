---
name: vendor-due-diligence
description: >
  Assess IT vendors and third-party partners with multi-factor risk scoring
  and regulatory compliance checklists. Use when evaluating technology vendors.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: The Glass Room
  category: legal
  domain: vendor-assessment
  updated: 2026-04-10
  tags: [vendor-assessment, due-diligence, risk-scoring, compliance, third-party-risk]
---
> **⚠️ EXPERIMENTAL** — This skill is provided for educational and informational purposes only. It does NOT constitute legal advice. All responsibility for usage rests with the user. Consult qualified legal professionals before acting on any output.

# Vendor Due Diligence Skill

## Overview

Production-ready framework for assessing IT service providers, technology vendors, and third-party partners. Provides a Three-Phase Assessment (Initial Screening, Detailed Assessment, Final Evaluation), Multi-Factor Risk Scoring across 6 dimensions with critical-service weighting, regulatory compliance checklists for 8 frameworks, vendor comparison matrices, and ongoing monitoring with Early Warning Indicators. Designed for procurement teams, legal counsel, IT security, and compliance officers evaluating technology vendors.

## Table of Contents

- [Tools](#tools)
- [Reference Guides](#reference-guides)
- [Workflows](#workflows)
- [Troubleshooting](#troubleshooting)
- [Success Criteria](#success-criteria)
- [Scope & Limitations](#scope--limitations)
- [Anti-Patterns](#anti-patterns)
- [Tool Reference](#tool-reference)

## Tools

### 1. Vendor Risk Scorer (`scripts/vendor_risk_scorer.py`)

Scores a vendor across 6 risk dimensions based on questionnaire responses. Calculates weighted composite score with 2x multiplier for critical services. Generates risk heat map and overall recommendation.

```bash
# Score a vendor from questionnaire responses
python scripts/vendor_risk_scorer.py vendor_responses.json

# JSON output for dashboards
python scripts/vendor_risk_scorer.py vendor_responses.json --json

# Flag as critical service (2x weight on security + compliance)
python scripts/vendor_risk_scorer.py vendor_responses.json --critical
```

### 2. Vendor Comparison (`scripts/vendor_comparison.py`)

Takes multiple vendor risk assessment JSONs and generates a side-by-side comparison matrix. Ranks vendors by composite score and recommends preferred vendor with rationale.

```bash
# Compare two vendors
python scripts/vendor_comparison.py vendor_a.json vendor_b.json

# Compare multiple vendors with JSON output
python scripts/vendor_comparison.py vendor_a.json vendor_b.json vendor_c.json --json

# Compare with critical service weighting
python scripts/vendor_comparison.py vendor_a.json vendor_b.json --critical
```

## Reference Guides

| Reference | Purpose |
|-----------|---------|
| `references/risk_assessment_framework.md` | 6-dimension scoring system, weighting methodology, composite score interpretation |
| `references/regulatory_checklists.md` | Pre-built compliance checklists for GDPR, DORA, NIS2, SOX, PCI DSS, ISO 27001/SOC 2, HIPAA, FedRAMP |
| `references/monitoring_framework.md` | Quarterly reviews, Early Warning Indicators, KPI metrics, risk mitigation strategies, onboarding checklists |

## Workflows

### Workflow 1: Three-Phase Vendor Assessment

**Phase 1: Initial Screening (Days 1-5)**
1. Gather basic vendor information (company profile, financial health, certifications)
2. Run `vendor_risk_scorer.py` with preliminary data for initial risk classification
3. Check applicable regulatory frameworks from `regulatory_checklists.md`
4. Decision gate: Proceed to detailed assessment or reject early

**Phase 2: Detailed Assessment (Days 5-15)**
1. Issue comprehensive vendor questionnaire covering all 6 risk dimensions
2. Run `vendor_risk_scorer.py` with complete questionnaire responses
3. Execute regulatory compliance checklists for all applicable frameworks
4. Request supporting documentation (SOC 2 reports, pen test results, financials)
5. Conduct reference checks and public record searches

**Phase 3: Final Evaluation (Days 15-20)**
1. Run `vendor_comparison.py` if evaluating multiple vendors
2. Compile Vendor Risk Report with dimension breakdowns
3. Document gaps and required mitigations from `risk_assessment_framework.md`
4. Present recommendation (Approve / Approve with Conditions / Reject)
5. If approved, generate onboarding checklist from `monitoring_framework.md`

### Workflow 2: Competitive Vendor Selection

1. **Define requirements** -- Document must-have and nice-to-have criteria mapped to risk dimensions
2. **Screen candidates** -- Run initial scoring on all candidates; eliminate any with Critical risk
3. **Deep-dive finalists** -- Full 6-dimension assessment on top 2-3 vendors
4. **Compare** -- Run `vendor_comparison.py` on finalist assessments
5. **Negotiate** -- Use risk findings as leverage in contract negotiations (integrates with `tech-contract-negotiation` skill)
6. **Select and onboard** -- Approve preferred vendor; set up monitoring per `monitoring_framework.md`

### Workflow 3: Ongoing Vendor Monitoring

1. **Quarterly review** -- Re-score vendor using updated data; compare against baseline
2. **Event-triggered review** -- Re-assess on M&A, breaches, regulatory changes, or leadership turnover
3. **Annual re-assessment** -- Full 6-dimension re-evaluation with updated questionnaire
4. **Early Warning response** -- Monitor indicators from `monitoring_framework.md`; escalate per defined paths
5. **Exit planning** -- If risk exceeds threshold, activate exit provisions and dual-source strategy

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| All dimensions score 1 (Low Risk) | Vendor self-reported optimistically on questionnaire | Cross-reference with SOC 2 reports, pen test results, and financial filings; adjust scores based on evidence |
| Composite score doesn't reflect known security issues | Security dimension not weighted for critical service | Re-run with `--critical` flag to apply 2x multiplier on security and compliance dimensions |
| Comparison matrix shows all vendors tied | Scoring inputs are too similar or too coarse | Request more granular data; use the 5-level scoring criteria from the risk framework to differentiate |
| Regulatory checklist seems incomplete for your industry | Only 8 frameworks are pre-built | Customize checklists by adding industry-specific requirements as additional items |
| Vendor refuses to complete questionnaire | Vendor sees assessment as overly burdensome | Share only the dimensions relevant to their service scope; offer to accept SOC 2/ISO 27001 reports as partial substitutes |
| Risk score changed dramatically between quarters | Major event occurred (breach, M&A, leadership change) | This is expected behavior; document the trigger event and follow the event-triggered review process |

## Success Criteria

- **Assessment Completeness**: 100% of vendor assessments cover all 6 risk dimensions with evidence-backed scores
- **Timeline Adherence**: Three-phase assessment completed within 20 business days for 90% of evaluations
- **Risk Prediction Accuracy**: Vendors flagged as High/Critical risk experience 3x more incidents than Low risk vendors over 12 months
- **Regulatory Coverage**: All applicable regulatory checklists completed with zero missed frameworks for 95% of assessments
- **Comparison Consistency**: Vendor comparison rankings remain stable when re-scored by different assessors (inter-rater reliability > 85%)
- **Monitoring Compliance**: 100% of quarterly reviews completed on schedule with documented findings
- **Early Warning Detection**: 80%+ of vendor incidents preceded by at least one Early Warning Indicator flagged in monitoring

## Scope & Limitations

**This skill covers:**
- Multi-factor risk scoring across 6 dimensions (Financial, Operational, Compliance, Security, Reputational, Strategic) with critical-service weighting
- Regulatory compliance checklists for GDPR, DORA, NIS2, SOX, PCI DSS, ISO 27001/SOC 2, HIPAA, and FedRAMP
- Side-by-side vendor comparison with composite ranking and dimension-level analysis
- Ongoing monitoring framework with quarterly reviews, Early Warning Indicators, and escalation paths
- Risk mitigation strategies and onboarding checklists by risk level

**This skill does NOT cover:**
- Real-time vendor monitoring dashboards, automated data feeds, or integration with GRC platforms (all input is via JSON files)
- Financial auditing, forensic accounting, or detailed financial statement analysis of vendors (use the `finance/financial-analyst` skill)
- Physical security assessments, on-site facility audits, or hardware supply chain verification
- Legal review of vendor contracts or negotiation of terms (use the `legal/tech-contract-negotiation` skill)
- Vendor relationship management, performance optimization, or strategic partnership development beyond risk assessment

## Anti-Patterns

| Anti-Pattern | Why It Fails | Better Approach |
|--------------|-------------|-----------------|
| Relying solely on vendor self-assessment questionnaires | Vendors underreport risks; no independent verification | Cross-reference questionnaire responses with SOC 2/ISO 27001 reports, pen test results, and public records |
| Applying the same weight to all dimensions regardless of service type | A payroll vendor and a marketing tool have different risk profiles | Use `--critical` flag for critical services; adjust dimension weights based on service classification |
| Completing due diligence once and never revisiting | Vendor risk changes over time due to M&A, breaches, market shifts | Implement quarterly monitoring with annual re-assessment per the monitoring framework |
| Rejecting vendors for a single high-risk dimension without considering mitigations | Eliminates potentially strong vendors with addressable gaps | Use the gap analysis severity classification; require remediation plans for major concerns before final decision |
| Skipping the comparison matrix for sole-source procurements | Misses opportunity to benchmark the vendor against market standards | Run comparison against industry benchmarks or previous vendor assessments to establish a risk baseline |

## Tool Reference

### `scripts/vendor_risk_scorer.py`

Score a vendor across 6 risk dimensions and generate an overall recommendation.

```
usage: vendor_risk_scorer.py [-h] [--json] [--critical]
                              input_file

positional arguments:
  input_file            Path to JSON file with vendor questionnaire responses

options:
  -h, --help            Show help message and exit
  --json                Output results as JSON
  --critical            Apply 2x weight to security and compliance
                        dimensions (for critical/essential services)
```

**Outputs:** 6-dimension risk scores (1-5 each), weighted composite score, risk level classification (Low/Moderate/High/Critical), overall recommendation (Approve/Approve with Conditions/Reject), dimension-level findings, and gap analysis.

### `scripts/vendor_comparison.py`

Compare multiple vendors side-by-side and recommend preferred vendor.

```
usage: vendor_comparison.py [-h] [--json] [--critical]
                             input_files [input_files ...]

positional arguments:
  input_files           Paths to vendor assessment JSON files (minimum 2)

options:
  -h, --help            Show help message and exit
  --json                Output results as JSON
  --critical            Apply 2x weight to security and compliance
                        dimensions (for critical/essential services)
```

**Outputs:** Side-by-side comparison matrix, composite score ranking, per-dimension strength/weakness analysis, preferred vendor recommendation with rationale, and risk delta highlights.
