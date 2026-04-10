# Vendor Monitoring Framework

Ongoing vendor monitoring including quarterly reviews, annual re-assessments, event-triggered reviews, Early Warning Indicators, KPI metrics, risk mitigation strategies, and onboarding checklists.

## Table of Contents

- [Monitoring Overview](#monitoring-overview)
- [Quarterly Review Template](#quarterly-review-template)
- [Annual Re-Assessment Framework](#annual-re-assessment-framework)
- [Event-Triggered Reviews](#event-triggered-reviews)
- [Early Warning Indicators](#early-warning-indicators)
- [KPI Dashboard Metrics](#kpi-dashboard-metrics)
- [Risk Mitigation Strategies](#risk-mitigation-strategies)
- [Onboarding Checklist](#onboarding-checklist)

## Monitoring Overview

Vendor monitoring operates on three cycles with escalating depth of review.

| Cycle | Frequency | Depth | Trigger |
|-------|-----------|-------|---------|
| Quarterly Review | Every 3 months | Operational metrics, SLA performance, incident review | Calendar-based |
| Annual Re-Assessment | Every 12 months | Full 6-dimension risk re-scoring with updated questionnaire | Calendar-based |
| Event-Triggered Review | As needed | Targeted assessment of impacted dimensions | Specific event occurs |

### Risk-Based Monitoring Intensity

| Vendor Risk Level | Quarterly Review | Annual Re-Assessment | Monitoring Intensity |
|-------------------|-----------------|----------------------|---------------------|
| Low Risk (1.0-1.5) | Abbreviated (metrics only) | Standard questionnaire | Routine |
| Moderate Risk (1.6-2.5) | Standard (metrics + discussion) | Full questionnaire + evidence review | Enhanced |
| High Risk (2.6-3.5) | Extended (deep-dive + remediation tracking) | Full questionnaire + on-site/virtual audit | Active |
| Critical Risk (3.6-5.0) | Monthly review | Quarterly re-assessment | Intensive |

## Quarterly Review Template

### Review Agenda

| # | Item | Time | Owner |
|---|------|------|-------|
| 1 | SLA performance review | 15 min | Vendor |
| 2 | Incident summary (count, severity, resolution time) | 10 min | Vendor |
| 3 | Change and release summary | 10 min | Vendor |
| 4 | Compliance and certification updates | 5 min | Vendor |
| 5 | Upcoming changes or risks | 5 min | Vendor |
| 6 | Client feedback and escalations | 10 min | Client |
| 7 | Action items and next steps | 5 min | Both |

### Metrics to Review

| Category | Metric | Target | Red Flag |
|----------|--------|--------|----------|
| Availability | Uptime % | Per SLA (e.g., 99.9%) | Below SLA for 2+ months |
| Performance | Response time (P95) | Per SLA | Degrading trend over 3 months |
| Incidents | P1/P2 count | Decreasing trend | Increasing P1s; recurring issues |
| Incidents | Mean time to resolve (MTTR) | Per SLA | MTTR increasing; SLA breaches |
| Security | Vulnerability count (critical/high) | Zero critical open > 30 days | Any critical open > 30 days |
| Security | Security incidents | Zero | Any data-related security incident |
| Compliance | Certification status | Current | Certification lapsed or expiring < 90 days |
| Financial | Invoice accuracy | > 99% | Recurring billing disputes |
| Support | Ticket resolution rate | > 95% within SLA | Below 90%; escalations increasing |

### Review Output

Document the following after each quarterly review:

| Output | Content |
|--------|---------|
| Performance summary | SLA compliance, incident trends, key metrics |
| Issues log | Open issues with severity, owner, and target resolution date |
| Risk update | Any changes to the vendor's risk profile |
| Action items | Specific actions with owners and due dates |
| Next review date | Confirmed date for next quarterly review |

## Annual Re-Assessment Framework

### Process

| Step | Activity | Timeline |
|------|----------|----------|
| 1 | Issue updated vendor questionnaire (all 6 dimensions) | 4 weeks before review |
| 2 | Collect and review evidence (certifications, audit reports, financials) | 3 weeks before review |
| 3 | Re-score using vendor risk scoring tool | 2 weeks before review |
| 4 | Compare scores against prior year baseline | 2 weeks before review |
| 5 | Conduct annual review meeting | Review date |
| 6 | Document findings and update risk register | 1 week after review |
| 7 | Issue remediation requirements if applicable | 1 week after review |

### Year-over-Year Comparison

| Dimension | Prior Year Score | Current Score | Change | Trend |
|-----------|-----------------|---------------|--------|-------|
| Financial | - | - | - | Improving / Stable / Deteriorating |
| Operational | - | - | - | Improving / Stable / Deteriorating |
| Compliance | - | - | - | Improving / Stable / Deteriorating |
| Security | - | - | - | Improving / Stable / Deteriorating |
| Reputational | - | - | - | Improving / Stable / Deteriorating |
| Strategic | - | - | - | Improving / Stable / Deteriorating |
| **Composite** | - | - | - | - |

### Escalation Criteria

| Condition | Action |
|-----------|--------|
| Composite score increased by > 0.5 | Escalate to risk committee; increase monitoring frequency |
| Any dimension increased to 4 or 5 | Require remediation plan within 30 days |
| Composite score now > 3.5 | Activate exit planning; engage alternative vendors |
| Compliance dimension increased by 2+ | Immediate regulatory impact assessment |

## Event-Triggered Reviews

### Trigger Events

| Event | Review Scope | Timeline | Escalation |
|-------|-------------|----------|------------|
| Data breach at vendor | Security, Compliance, Reputational | Within 48 hours | Immediate executive notification |
| Vendor M&A announcement | All dimensions (full re-assessment) | Within 2 weeks | Risk committee review |
| Regulatory violation or sanction | Compliance, Reputational | Within 1 week | Legal and compliance team engagement |
| Key leadership change (CEO, CTO, CISO) | Operational, Strategic | Within 2 weeks | Relationship manager assessment |
| Financial deterioration (downgrade, layoffs, losses) | Financial, Operational, Strategic | Within 1 week | Financial analysis; exit readiness check |
| Major service outage (> SLA threshold) | Operational, Security | Within 48 hours | SLA remediation process |
| Vendor loses certification | Compliance, Security | Within 1 week | Impact assessment; remediation timeline |
| Significant negative press | Reputational | Within 1 week | Communications and legal review |
| Sub-processor change for critical service | Compliance, Security, Operational | Within 2 weeks | Sub-processor assessment |
| Your own regulatory change | Compliance | Within 4 weeks | Gap analysis against new requirements |

### Event Response Process

1. **Identify** -- Capture the event through monitoring channels, news alerts, or vendor notification
2. **Assess** -- Determine which risk dimensions are impacted and the potential severity
3. **Investigate** -- Gather information from vendor and independent sources
4. **Score** -- Re-score impacted dimensions using the risk assessment framework
5. **Decide** -- Determine action: continue monitoring, require remediation, escalate, or activate exit
6. **Document** -- Record the event, assessment, decision, and rationale in the vendor risk register

## Early Warning Indicators

Indicators that suggest vendor risk may be increasing before a formal trigger event occurs.

### Financial Early Warnings

| Indicator | Detection Method | Severity |
|-----------|-----------------|----------|
| Late payments to their own suppliers | Industry intelligence, credit monitoring | Moderate |
| Cost-cutting announcements (layoffs > 10%) | News monitoring, LinkedIn | High |
| Failed funding round or down round | Crunchbase, news | High |
| Credit rating downgrade | Credit monitoring services | High |
| Loss of major client (> 10% revenue) | News, industry contacts | Moderate |
| Delayed financial reporting | Quarterly check-in; SEC filings | Moderate |

### Operational Early Warnings

| Indicator | Detection Method | Severity |
|-----------|-----------------|----------|
| Key personnel departures (CISO, CTO, VP Eng) | LinkedIn monitoring, vendor notification | High |
| Increasing support ticket volume | Quarterly metrics review | Moderate |
| Degrading SLA performance (trend, not one-off) | Monthly SLA dashboards | Moderate |
| Delayed product releases or roadmap changes | Vendor communications, product updates | Low |
| Increased employee turnover (Glassdoor, LinkedIn) | External monitoring | Moderate |

### Security Early Warnings

| Indicator | Detection Method | Severity |
|-----------|-----------------|----------|
| Certification expiring without renewal plans | Certificate monitoring; quarterly review | High |
| Increased vulnerability disclosures in vendor product | CVE monitoring, security advisories | Moderate-High |
| Vendor appears in breach databases or threat intelligence | Threat intelligence feeds | Critical |
| Delayed patch releases for known vulnerabilities | Security advisory monitoring | High |
| Changes to vendor security team (reductions) | LinkedIn monitoring | Moderate |

### Escalation Path

| Severity | Response Time | Escalation To | Action |
|----------|--------------|--------------|--------|
| Low | Next quarterly review | Relationship manager | Note and monitor |
| Moderate | Within 2 weeks | Vendor risk owner | Investigate; request vendor response |
| High | Within 1 week | Risk committee / management | Formal assessment; remediation demand |
| Critical | Within 48 hours | Executive leadership; legal | Incident response; potential exit activation |

## KPI Dashboard Metrics

### Vendor Performance KPIs

| KPI | Formula | Target | Frequency |
|-----|---------|--------|-----------|
| SLA Compliance Rate | Months meeting SLA / Total months | > 95% | Monthly |
| Incident Rate | P1+P2 incidents / Month | Decreasing trend | Monthly |
| Mean Time to Resolve (P1) | Average P1 resolution time | Per SLA | Monthly |
| Service Credit Utilization | Credits claimed / Credits available | < 20% | Quarterly |
| Vendor Responsiveness | Requests responded within SLA / Total requests | > 95% | Monthly |

### Vendor Risk KPIs

| KPI | Formula | Target | Frequency |
|-----|---------|--------|-----------|
| Composite Risk Score | Weighted average of 6 dimensions | < 2.5 | Quarterly |
| Risk Trend | Current score - Prior quarter score | Stable or improving | Quarterly |
| Open Gaps Count | Active gaps from gap analysis | Decreasing | Quarterly |
| Gap Closure Rate | Gaps closed on time / Gaps due | > 90% | Quarterly |
| Early Warning Count | Active early warning indicators | Zero High/Critical | Monthly |

### Portfolio-Level KPIs

| KPI | Formula | Target | Frequency |
|-----|---------|--------|-----------|
| Vendor Portfolio Risk | Average composite score across all vendors | < 2.0 | Quarterly |
| High-Risk Vendor % | Vendors scoring > 3.0 / Total vendors | < 10% | Quarterly |
| Assessment Completion Rate | Assessments completed on time / Assessments due | 100% | Quarterly |
| Monitoring Compliance | Reviews completed on schedule / Reviews due | 100% | Quarterly |

## Risk Mitigation Strategies

Specific mitigation strategies organized by risk dimension.

### Financial Risk Mitigations

| Mitigation | When to Apply | Implementation |
|-----------|---------------|----------------|
| Parent company guarantee | Vendor is subsidiary; financial risk is moderate+ | Require parent guarantee in contract |
| Performance bond | High-value contract; vendor financial risk is high | Bond covering 6-12 months of fees |
| Insurance requirements | All vendors; scale with risk level | Minimum coverage amounts in contract |
| Escrow (fees) | Vendor financial risk is high; critical service | Escrow 3-6 months of fees |
| Shorter contract terms | Financial uncertainty; limit exposure | 12-month terms with renewal option |
| Payment milestones | Project-based work; financial risk is moderate+ | Pay on delivery/acceptance, not upfront |

### Security Risk Mitigations

| Mitigation | When to Apply | Implementation |
|-----------|---------------|----------------|
| Mandatory security controls | All vendors processing your data | Contractual security schedule |
| Annual penetration testing | Moderate+ security risk | Contractual requirement; share results |
| Enhanced monitoring | High security risk | Real-time alerting; dedicated security contact |
| Data minimization | All vendors; reduce blast radius | Limit data shared to minimum necessary |
| Encryption requirements | All vendors handling sensitive data | Contractual encryption standards |
| Incident response SLA | All vendors; stricter for higher risk | 24-hour notification; joint IR exercises |

### Compliance Risk Mitigations

| Mitigation | When to Apply | Implementation |
|-----------|---------------|----------------|
| Certification timeline | Vendor lacks required certifications | Contractual commitment with milestone dates |
| Audit rights | All vendors; frequency based on risk | Annual audit right; accept SOC 2 as alternative |
| Breach termination clause | All vendors | Right to terminate for material compliance breach |
| Regulatory change clause | Regulated industries | Vendor must accommodate new regulatory requirements |
| Compliance reporting | Moderate+ compliance risk | Quarterly compliance status reports |
| Sub-processor controls | GDPR/DORA applicable vendors | Approval rights for sub-processor changes |

### Operational Risk Mitigations

| Mitigation | When to Apply | Implementation |
|-----------|---------------|----------------|
| SLAs with financial consequences | All vendors with availability requirements | Service credits; termination rights |
| Redundancy requirements | Critical services | Contractual geographic/infrastructure redundancy |
| IP escrow | Vendor-dependent technology; high operational risk | Source code escrow with release triggers |
| Backup vendor identification | Critical services; high operational risk | Identify and pre-qualify alternative vendor |
| Knowledge transfer | Key-person dependency identified | Documented knowledge transfer plan |
| Transition assistance | All vendors | Contractual transition assistance obligation on termination |

### Strategic Risk Mitigations

| Mitigation | When to Apply | Implementation |
|-----------|---------------|----------------|
| Limited contract terms | High lock-in risk | Maximum 2-3 year terms with exit provisions |
| Data portability testing | All vendors | Annual data export test |
| Dual-source strategy | Critical services; high strategic risk | Maintain qualified alternative vendor |
| Exit provisions | All vendors | Documented exit plan with timeline and vendor obligations |
| API/integration standards | Technology vendors | Require open standards; avoid proprietary lock-in |
| Innovation requirements | Strategic vendors; long-term relationships | Contractual innovation/roadmap sharing commitments |

## Onboarding Checklist

Post-approval vendor onboarding tasks, scaled by risk level.

### All Vendors (Baseline)

| # | Task | Owner | Timeline |
|---|------|-------|----------|
| 1 | Execute contract with all required provisions | Legal | Before start |
| 2 | Add vendor to vendor register/inventory | Procurement | Day 1 |
| 3 | Set up access and credentials (least privilege) | IT Security | Day 1-3 |
| 4 | Confirm data handling procedures | Data Protection | Week 1 |
| 5 | Establish communication channels and escalation contacts | Relationship Mgr | Week 1 |
| 6 | Schedule first quarterly review | Relationship Mgr | Week 1 |
| 7 | Document vendor in risk register with baseline score | Risk/Compliance | Week 1 |
| 8 | Configure monitoring alerts (SLA, incidents) | Operations | Week 1-2 |

### Moderate Risk Vendors (Additional)

| # | Task | Owner | Timeline |
|---|------|-------|----------|
| 9 | Document gap remediation plan with milestones | Risk/Compliance | Week 2 |
| 10 | Set up enhanced SLA monitoring dashboard | Operations | Week 2 |
| 11 | Confirm insurance certificates on file | Procurement | Week 1 |
| 12 | Brief internal stakeholders on vendor risk profile | Relationship Mgr | Week 2 |

### High/Critical Risk Vendors (Additional)

| # | Task | Owner | Timeline |
|---|------|-------|----------|
| 13 | Assign dedicated vendor risk owner | Risk Committee | Before start |
| 14 | Execute detailed exit/transition plan | Legal + Operations | Month 1 |
| 15 | Set up monthly (not quarterly) review cadence | Relationship Mgr | Week 1 |
| 16 | Identify and pre-qualify backup vendor | Procurement | Month 1-2 |
| 17 | Configure Early Warning Indicator monitoring | Risk/Compliance | Week 2 |
| 18 | Schedule tabletop incident response exercise with vendor | Security | Quarter 1 |
| 19 | Obtain executive risk acceptance sign-off | Risk Committee | Before start |
| 20 | Set up financial health monitoring for vendor | Finance | Week 2 |
