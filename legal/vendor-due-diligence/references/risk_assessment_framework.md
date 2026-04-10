# Vendor Risk Assessment Framework

Complete 6-dimension risk scoring system with detailed scoring criteria, weighting methodology, composite score interpretation, and gap analysis severity classification.

## Table of Contents

- [Framework Overview](#framework-overview)
- [Dimension 1: Financial Risk](#dimension-1-financial-risk)
- [Dimension 2: Operational Risk](#dimension-2-operational-risk)
- [Dimension 3: Compliance Risk](#dimension-3-compliance-risk)
- [Dimension 4: Security Risk](#dimension-4-security-risk)
- [Dimension 5: Reputational Risk](#dimension-5-reputational-risk)
- [Dimension 6: Strategic Risk](#dimension-6-strategic-risk)
- [Weighting Methodology](#weighting-methodology)
- [Composite Score Interpretation](#composite-score-interpretation)
- [Gap Analysis](#gap-analysis)

## Framework Overview

The framework assesses vendors across 6 risk dimensions on a 1-5 scale. Lower scores indicate lower risk.

| Score | Label | Meaning |
|-------|-------|---------|
| 1 | Low Risk | Strong position; minimal concerns; exceeds expectations |
| 2 | Moderate-Low Risk | Acceptable position; minor gaps easily addressed |
| 3 | Moderate Risk | Some concerns; mitigation recommended; monitor closely |
| 4 | High Risk | Significant concerns; remediation required before or during engagement |
| 5 | Critical Risk | Fundamental gaps; engagement not recommended without major remediation |

## Dimension 1: Financial Risk

Assesses the vendor's financial stability, sustainability, and ability to fulfill contractual obligations.

### Scoring Criteria

| Score | Indicators |
|-------|-----------|
| 1 | Annual revenue > $100M; profitable for 5+ years; investment-grade credit; audited financials; comprehensive insurance; public company or well-funded private |
| 2 | Annual revenue $25M-$100M; profitable for 2+ years; adequate cash reserves; audited financials available; standard insurance coverage |
| 3 | Annual revenue $5M-$25M; break-even or recently profitable; funded with 18+ months runway; financial statements available but not audited; basic insurance |
| 4 | Annual revenue < $5M; not yet profitable; funded with < 18 months runway; limited financial transparency; minimal insurance |
| 5 | Revenue declining; significant losses; funding uncertain; no financial statements available; no insurance; key dependencies on single revenue source |

### Key Indicators to Verify

| Indicator | Source | Red Flag |
|-----------|--------|----------|
| Revenue trend | Financial statements, D&B, Crunchbase | Declining revenue for 2+ consecutive quarters |
| Profitability | Income statement, management accounts | Increasing losses without clear path to profitability |
| Cash position | Balance sheet, funding announcements | Less than 12 months runway at current burn rate |
| Customer concentration | Client list, revenue breakdown | Single client > 30% of revenue |
| Insurance | Certificate of insurance | No professional liability or cyber insurance |
| Audit status | Audit reports | No external audit for companies > $10M revenue |

## Dimension 2: Operational Risk

Assesses the vendor's operational maturity, resilience, and ability to deliver services consistently.

### Scoring Criteria

| Score | Indicators |
|-------|-----------|
| 1 | 200+ employees; documented processes (ISO 9001 or equivalent); tested DR/BCP; geographic redundancy; no key-person dependency; 24/7 support; mature ITSM |
| 2 | 50-200 employees; documented key processes; DR plan in place and tested annually; dedicated support team; limited key-person risk |
| 3 | 20-50 employees; some documented processes; DR plan exists but testing is irregular; support during business hours; moderate key-person dependency |
| 4 | 10-20 employees; ad hoc processes; DR plan not documented or tested; limited support; significant key-person dependency |
| 5 | < 10 employees; no documented processes; no DR/BCP; single point of failure for critical functions; founder-dependent |

### Key Indicators to Verify

| Indicator | Source | Red Flag |
|-----------|--------|----------|
| Employee count and growth | LinkedIn, company filings | Headcount declining; high turnover |
| DR/BCP maturity | DR plan document, test results | Never tested or tested > 12 months ago |
| Support model | SLA documentation, reference checks | No dedicated support for your contract size |
| Process maturity | ISO 9001, ITIL, internal documentation | No documented processes for service delivery |
| Geographic distribution | Infrastructure documentation | Single data center; single office location |
| Key-person risk | Organizational chart, team bios | Critical knowledge held by 1-2 individuals |

## Dimension 3: Compliance Risk

Assesses the vendor's regulatory compliance posture and ability to meet your compliance requirements.

### Scoring Criteria

| Score | Indicators |
|-------|-----------|
| 1 | Multiple relevant certifications (ISO 27001, SOC 2 Type II, etc.); dedicated compliance team; quarterly audit cycle; clean compliance history; proactive regulatory monitoring |
| 2 | Key certifications in place; compliance function exists; annual audit cycle; no material compliance findings in last 3 years |
| 3 | Some certifications; compliance responsibility assigned (not dedicated team); annual or irregular audit; minor compliance findings addressed |
| 4 | Limited certifications; no dedicated compliance role; infrequent audits; open compliance findings; reactive approach to regulation |
| 5 | No certifications; no compliance function; no audit history; known compliance violations; no awareness of applicable regulations |

### Key Indicators to Verify

| Indicator | Source | Red Flag |
|-----------|--------|----------|
| Certifications | Certificate copies, certification body registries | Claims certifications but cannot produce current certificates |
| Compliance team | Organizational structure, LinkedIn | No one with compliance/risk in title or job description |
| Audit history | SOC 2 reports, ISO audit reports | No audit in last 24 months; material findings unresolved |
| Breach history | Public records, regulatory databases, news | Regulatory enforcement action in last 3 years |
| Regulatory awareness | Questionnaire responses | Cannot identify which regulations apply to their services |

## Dimension 4: Security Risk

Assesses the vendor's information security posture and ability to protect your data.

### Scoring Criteria

| Score | Indicators |
|-------|-----------|
| 1 | SOC 2 Type II + ISO 27001; zero-trust architecture; quarterly pen testing; bug bounty program; SIEM/SOC; encryption everywhere; MFA enforced; mature vulnerability management |
| 2 | SOC 2 Type II or ISO 27001; annual pen testing; encryption at rest and in transit; MFA enforced; incident response plan tested; vulnerability scanning |
| 3 | SOC 2 Type I or working toward certification; annual pen testing; encryption in transit; MFA available but not enforced; incident response plan exists |
| 4 | No security certifications; irregular pen testing; partial encryption; no MFA; incident response plan not documented; limited vulnerability management |
| 5 | No security program; no pen testing; no encryption; no access controls beyond passwords; no incident response capability; known unpatched vulnerabilities |

### Key Indicators to Verify

| Indicator | Source | Red Flag |
|-----------|--------|----------|
| Security certifications | SOC 2 report, ISO certificate | No certification and no plan to obtain |
| Penetration testing | Pen test executive summary | No pen test in last 12 months; critical findings open |
| Encryption | Technical documentation, architecture diagrams | No encryption at rest; TLS 1.0/1.1 still in use |
| Access controls | Security policy documentation | No MFA; shared admin accounts; no access reviews |
| Incident response | IR plan, tabletop exercise results | No IR plan; never tested; no designated IR team |
| Vulnerability management | Scan reports, patch policy | Mean time to patch critical vulnerabilities > 30 days |

## Dimension 5: Reputational Risk

Assesses risks to your organization's reputation from association with this vendor.

### Scoring Criteria

| Score | Indicators |
|-------|-----------|
| 1 | Strong brand reputation; industry awards; high employee satisfaction (Glassdoor 4.0+); no public breaches; strong client references; positive media coverage |
| 2 | Positive reputation; good employee reviews; no significant public incidents; client references available; neutral-to-positive media |
| 3 | Average reputation; mixed employee reviews; minor public incidents resolved; limited client references; limited media presence |
| 4 | Below-average reputation; poor employee reviews (Glassdoor < 3.0); public incidents with ongoing impact; client references difficult to obtain; negative media |
| 5 | Poor reputation; active litigation; major data breaches; regulatory sanctions; significant negative media; high employee turnover and negative reviews |

### Key Indicators to Verify

| Indicator | Source | Red Flag |
|-----------|--------|----------|
| Public breaches | Have I Been Pwned, news archives | Multiple breaches; poor breach response; delayed notification |
| Litigation | Court records, legal databases | Active lawsuits related to service quality or data handling |
| Employee satisfaction | Glassdoor, LinkedIn attrition data | Rating < 3.0; mass layoffs; senior leadership exodus |
| Client references | Direct reference calls | Cannot provide references; references express concerns |
| Media coverage | News search, industry publications | Sustained negative coverage; investigative journalism pieces |

## Dimension 6: Strategic Risk

Assesses alignment with your strategic objectives and long-term viability of the relationship.

### Scoring Criteria

| Score | Indicators |
|-------|-----------|
| 1 | Market leader; strong roadmap alignment; excellent integration capabilities; low lock-in risk; viable exit strategy; active innovation |
| 2 | Established player; good roadmap alignment; standard API integration; moderate lock-in with clear exit path; regular product updates |
| 3 | Mid-market player; partial roadmap alignment; integration possible with effort; moderate lock-in risk; exit feasible with planning |
| 4 | Niche player; limited roadmap alignment; custom integration required; high lock-in; exit difficult and expensive; limited innovation |
| 5 | Declining market position; no roadmap alignment; no integration capabilities; extreme lock-in (proprietary formats, no data export); no viable exit; stagnant product |

### Key Indicators to Verify

| Indicator | Source | Red Flag |
|-----------|--------|----------|
| Market position | Analyst reports (Gartner, Forrester), market share data | Declining market share; losing to competitors |
| Product roadmap | Vendor presentations, release notes | No meaningful updates in 12+ months |
| Integration | API documentation, developer portal | No API; custom integration only; proprietary protocols |
| Lock-in risk | Contract terms, data export capabilities | No data export; proprietary data formats; long notice periods |
| Exit feasibility | Migration assessment, alternative vendor analysis | No migration tools; data extraction requires vendor assistance |

## Weighting Methodology

### Standard Weighting

All dimensions start with equal weight (1.0), with slight reduction for reputational and strategic (0.8) as they are less directly operational.

| Dimension | Standard Weight |
|-----------|----------------|
| Financial | 1.0 |
| Operational | 1.0 |
| Compliance | 1.0 |
| Security | 1.0 |
| Reputational | 0.8 |
| Strategic | 0.8 |

### Critical Service Weighting

For services classified as critical or essential (e.g., core infrastructure, payment processing, data hosting), apply a 2x multiplier to Security and Compliance dimensions.

| Dimension | Critical Weight |
|-----------|----------------|
| Financial | 1.0 |
| Operational | 1.0 |
| Compliance | **2.0** |
| Security | **2.0** |
| Reputational | 0.8 |
| Strategic | 0.8 |

### Composite Score Calculation

```
Composite = Sum(dimension_score * weight) / Sum(weights)
```

**Example (Standard):**
- Financial: 2, Operational: 3, Compliance: 2, Security: 3, Reputational: 1, Strategic: 2
- Weighted sum: (2*1.0) + (3*1.0) + (2*1.0) + (3*1.0) + (1*0.8) + (2*0.8) = 12.4
- Total weight: 1.0 + 1.0 + 1.0 + 1.0 + 0.8 + 0.8 = 5.6
- Composite: 12.4 / 5.6 = 2.21

## Composite Score Interpretation

| Range | Risk Level | Recommendation | Action |
|-------|-----------|----------------|--------|
| 1.0 - 1.5 | Low Risk | Approve | Proceed with standard monitoring |
| 1.6 - 2.5 | Moderate Risk | Approve with Conditions | Proceed with documented mitigations and enhanced monitoring |
| 2.6 - 3.5 | High Risk | Enhanced Due Diligence | Require remediation plan with timelines; consider alternatives; escalate to risk committee |
| 3.6 - 5.0 | Critical Risk | Reject or Require Remediation | Do not proceed without fundamental changes; require executive risk acceptance if proceeding |

### Conditional Approval Requirements

When approving with conditions, document:

| Element | Requirement |
|---------|------------|
| Specific conditions | List each condition with measurable acceptance criteria |
| Timeline | Deadline for each condition to be met |
| Monitoring plan | How compliance with conditions will be verified |
| Escalation path | What happens if conditions are not met by deadline |
| Risk owner | Named individual accountable for monitoring |

## Gap Analysis

### Severity Classification

| Severity | Definition | Action Required | Timeline |
|----------|-----------|----------------|----------|
| Blocker | Fundamental gap that prevents engagement; unacceptable risk | Must be resolved before contract execution | Before signing |
| Major Concern | Significant gap that materially increases risk | Remediation plan required; contractual commitment to resolve | Within 90 days of contract start |
| Minor Gap | Notable gap with available mitigations | Document mitigation; include in monitoring plan | Within 6 months |
| Acceptable with Mitigation | Small gap that can be managed through contractual or operational controls | Apply mitigation; note in risk register | Ongoing |

### Gap-to-Mitigation Mapping

| Gap Type | Example | Mitigation Options |
|----------|---------|-------------------|
| No SOC 2 certification | Vendor cannot demonstrate security controls independently | Require certification within 12 months; enhanced audit rights; increased insurance |
| No DR testing | Disaster recovery plan exists but never tested | Contractual requirement to test within 6 months; participate in test; backup vendor |
| Key-person dependency | Critical knowledge held by single individual | Knowledge transfer plan; documentation requirements; key-person insurance |
| Limited financial transparency | Privately held; no audited financials | Parent company guarantee; performance bond; escrow; quarterly financial updates |
| No incident response plan | No documented IR capability | Require IR plan within 90 days; tabletop exercise within 6 months; enhanced breach notification |
| High lock-in risk | Proprietary data formats; no export capability | Contractual data portability; regular export testing; maximum term with exit assistance |
