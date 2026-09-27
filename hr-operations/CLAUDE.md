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
- **Org Health Scorer** (`hr-business-partner/scripts/org_health_scorer.py`) - Score department health across retention, engagement, performance, development, compensation, and structure (span of control, open roles)
- **Headcount Planner** (`people-analytics/scripts/headcount_planner.py`) - Model hiring plans against attrition rates, growth targets, and hiring capacity

### Talent Acquisition
- **Candidate Pipeline Tracker** (`talent-acquisition/scripts/candidate_pipeline_tracker.py`) - Stage-by-stage conversion rates, time-to-fill analysis, bottleneck identification, and sourcing channel comparison
- **Interview Scorecard** (`talent-acquisition/scripts/interview_scorecard.py`) - Generate structured interview scorecards based on role competencies and leveling criteria

### Compensation and Benchmarking
- **Compensation Analyzer** (`hr-business-partner/scripts/compensation_analyzer.py`) - Compare compensation data against bands, flag outliers, calculate compa-ratios, and measure pay gaps across demographic groups

### Workforce Analytics
- **Attrition Predictor** (`people-analytics/scripts/attrition_predictor.py`) - Score employees on flight risk based on tenure, engagement signals, and historical patterns
- **Survey Analyzer** (`people-analytics/scripts/survey_analyzer.py`) - Aggregate survey responses, identify themes, and benchmark against prior periods

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
# 1. Score current organizational health
python hr-business-partner/scripts/org_health_scorer.py --file org_metrics.csv

# 2. Model headcount needs for next quarter
python people-analytics/scripts/headcount_planner.py --file workforce.csv --growth 0.15 --attrition 0.12

# 3. Evaluate hiring funnel health
python talent-acquisition/scripts/candidate_pipeline_tracker.py --file pipeline.csv

# 4. Benchmark compensation for open roles
python hr-business-partner/scripts/compensation_analyzer.py --file comp_data.csv
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
