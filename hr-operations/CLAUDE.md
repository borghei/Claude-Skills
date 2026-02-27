# HR Operations Skills - Claude Code Guidance

This guide covers the 4 HR operations skills and planned Python automation tools for the domain.

## HR Operations Skills Overview

**Available Skills:**
1. **operations-manager/** - Workforce planning, process optimization, compliance management, facilities coordination, and operational efficiency
2. **talent-acquisition/** - Recruiting strategy, candidate sourcing, interview design, offer management, employer branding, and hiring analytics
3. **hr-business-partner/** - Strategic HR advisory, organizational development, change management, employee relations, and performance management
4. **people-analytics/** - Workforce analytics, attrition modeling, engagement analysis, compensation benchmarking, and DEI metrics

**Current Status:** 4 SKILL.md knowledge bases deployed. Python automation tools planned for next phase.

## Skill Selection Guide

| Need | Use This Skill |
|------|---------------|
| Day-to-day operational processes and compliance | operations-manager |
| Hiring pipeline management and recruiting strategy | talent-acquisition |
| Strategic workforce decisions and organizational design | hr-business-partner |
| Data-driven workforce insights and HR metrics | people-analytics |

**Overlap Guidance:**
- operations-manager vs hr-business-partner: Use operations-manager for process execution and compliance; use hr-business-partner for strategic advisory and organizational change.
- talent-acquisition vs people-analytics: Use talent-acquisition for active recruiting workflows; use people-analytics when analyzing hiring funnel efficiency, quality-of-hire metrics, or sourcing channel ROI.
- people-analytics supports all three other skills by providing the data foundation for workforce decisions.

## Recommended Python Tools (Planned)

### Organizational Analysis
- **Org Chart Analyzer** (`operations-manager/scripts/org_chart_analyzer.py`) - Analyze reporting structures for span of control, layers of management, and organizational bottlenecks
- **Headcount Planner** (`operations-manager/scripts/headcount_planner.py`) - Model hiring plans against budget, attrition rates, and growth targets

### Talent Acquisition
- **Hiring Funnel Analyzer** (`talent-acquisition/scripts/hiring_funnel_analyzer.py`) - Stage-by-stage conversion rates, time-to-fill analysis, bottleneck identification, and sourcing channel comparison
- **Interview Scorecard Generator** (`talent-acquisition/scripts/interview_scorecard_generator.py`) - Generate structured interview scorecards based on role competencies and leveling criteria

### Compensation and Benchmarking
- **Compensation Benchmarker** (`people-analytics/scripts/compensation_benchmarker.py`) - Compare compensation data against market bands, flag outliers, and calculate compa-ratios
- **Pay Equity Analyzer** (`people-analytics/scripts/pay_equity_analyzer.py`) - Statistical analysis of pay gaps across demographic groups with confidence intervals

### Workforce Analytics
- **Attrition Risk Scorer** (`people-analytics/scripts/attrition_risk_scorer.py`) - Score employees on flight risk based on tenure, engagement signals, and historical patterns
- **Engagement Survey Analyzer** (`people-analytics/scripts/engagement_survey_analyzer.py`) - Aggregate survey responses, identify themes, and benchmark against prior periods

## Integration with Other Domains

### Project Management Integration
| HR Operations Skill | PM Skill | Integration Pattern |
|---------------------|----------|-------------------|
| operations-manager | resource-planning | Align headcount plans with project resource requirements |
| talent-acquisition | sprint-planning | Coordinate new hire onboarding timelines with team capacity |
| hr-business-partner | stakeholder-management | Organizational change communication and stakeholder alignment |

### Business & Growth Integration
| HR Operations Skill | Business & Growth Skill | Integration Pattern |
|---------------------|------------------------|-------------------|
| people-analytics | revenue-operations | Correlate team staffing levels with revenue performance |
| talent-acquisition | customer-success-manager | Align hiring for CS teams with customer portfolio growth |
| operations-manager | sales-engineer | Coordinate technical hiring with sales capacity planning |

**Cross-Domain Workflow:**
```bash
# 1. Analyze current organizational structure
python operations-manager/scripts/org_chart_analyzer.py org_data.json

# 2. Model headcount needs for next quarter
python operations-manager/scripts/headcount_planner.py plan_data.json

# 3. Evaluate hiring funnel health
python talent-acquisition/scripts/hiring_funnel_analyzer.py funnel_data.json

# 4. Benchmark compensation for open roles
python people-analytics/scripts/compensation_benchmarker.py comp_data.json
```

## Quality Standards

**All HR operations Python tools must:**
- Use standard library only (no external dependencies)
- Support both JSON and human-readable output via `--format` flag
- Provide clear error messages for invalid input
- Return appropriate exit codes (0 success, 1 error)
- Process files locally with no API calls or network access
- Include argparse CLI with `--help` support
- Handle sensitive data assumptions (tools process anonymized or aggregated data only)

**Skill documentation must:**
- Reference established HR methodologies (SHRM, Bersin, Mercer frameworks)
- Include compliance considerations (EEOC, GDPR, local labor law awareness)
- Provide realistic examples with sample data structures
- Address confidentiality and data governance for workforce data

## Related Skills

- **Project Management:** Resource planning, capacity management -> `../project-management/`
- **Business & Growth:** Revenue operations, GTM efficiency -> `../business-growth/`
- **Finance:** Compensation budgeting, workforce cost modeling -> `../finance/`
- **C-Level:** Strategic workforce planning, organizational design -> `../c-level-advisor/`

## Additional Resources

- **Main Documentation:** `../CLAUDE.md`
- **Standards Library:** `../standards/`

---

**Last Updated:** February 2026
**Skills Deployed:** 4/4 HR operations skills (SKILL.md knowledge bases)
**Python Tools:** Planned for next development phase
