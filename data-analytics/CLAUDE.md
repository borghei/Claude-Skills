# Data Analytics Skills - Claude Code Guidance

This guide covers the 5 data analytics skills and planned Python automation tools for the domain.

## Data Analytics Skills Overview

**Available Skills:**
1. **data-analyst/** - SQL querying, data visualization, statistical analysis, business reporting, and data storytelling
2. **data-scientist/** - Hypothesis testing, predictive modeling, experiment design, feature engineering, and causal inference
3. **business-intelligence/** - Dashboard design, KPI frameworks, data modeling, self-service analytics, and executive reporting
4. **analytics-engineer/** - Data pipeline design, dbt modeling, data warehouse architecture, testing, and documentation
5. **ml-ops-engineer/** - Model deployment, ML pipelines, model monitoring, feature stores, and infrastructure automation

**Current Status:** 5 SKILL.md knowledge bases deployed. Python automation tools planned for next phase.

## Skill Selection Guide

| Need | Use This Skill |
|------|---------------|
| Ad-hoc SQL queries and business reporting | data-analyst |
| Statistical modeling and experiment design | data-scientist |
| Dashboard creation and KPI tracking | business-intelligence |
| Data pipeline and warehouse architecture | analytics-engineer |
| Production ML deployment and monitoring | ml-ops-engineer |

**Overlap Guidance:**
- data-analyst vs business-intelligence: Use data-analyst for exploratory analysis; use business-intelligence for repeatable dashboards and KPI systems.
- data-scientist vs ml-ops-engineer: Use data-scientist for model development and experimentation; use ml-ops-engineer for production deployment and monitoring.
- analytics-engineer bridges data-analyst and business-intelligence by building the reliable data models both depend on.

## Recommended Python Tools (Planned)

### SQL and Query Tools
- **SQL Generator** (`data-analyst/scripts/sql_generator.py`) - Generate common query patterns (aggregation, window functions, CTEs) from natural-language descriptions
- **Query Optimizer** (`data-analyst/scripts/query_optimizer.py`) - Analyze SQL for performance issues, suggest indexes, and rewrite inefficient patterns

### Visualization Helpers
- **Chart Recommender** (`business-intelligence/scripts/chart_recommender.py`) - Recommend chart types based on data shape, cardinality, and analysis goal
- **Dashboard Spec Generator** (`business-intelligence/scripts/dashboard_spec_generator.py`) - Generate dashboard layout specifications from KPI definitions

### Data Quality and Testing
- **Data Quality Validator** (`analytics-engineer/scripts/data_quality_validator.py`) - Schema validation, null checks, uniqueness constraints, freshness monitoring
- **Data Profiler** (`analytics-engineer/scripts/data_profiler.py`) - Automated column profiling with distribution analysis, outlier detection, and completeness scores

### ML Operations
- **Model Health Monitor** (`ml-ops-engineer/scripts/model_health_monitor.py`) - Track prediction drift, data drift, and model performance degradation
- **Experiment Tracker** (`data-scientist/scripts/experiment_tracker.py`) - Log experiment parameters, metrics, and artifacts in structured JSON format

## Integration with Engineering Team

The data-analytics domain connects closely with engineering-team skills:

| Data Analytics Skill | Engineering Skill | Integration Pattern |
|---------------------|-------------------|-------------------|
| analytics-engineer | senior-data-engineer | Shared pipeline orchestration patterns; analytics-engineer focuses on transformation layer, data-engineer on ingestion and infrastructure |
| data-scientist | senior-data-scientist | Complementary scopes; data-analytics version emphasizes business context, engineering version emphasizes algorithm implementation |
| ml-ops-engineer | senior-ml-engineer | ml-ops-engineer handles deployment and monitoring; ml-engineer handles model architecture and training |
| business-intelligence | senior-fullstack | BI dashboards may embed in fullstack applications; use fullstack scaffolder for custom analytics UIs |

**Cross-Domain Workflow:**
```bash
# 1. Profile raw data quality
python analytics-engineer/scripts/data_profiler.py raw_data.csv

# 2. Validate transformation output
python analytics-engineer/scripts/data_quality_validator.py transformed_data.json

# 3. Generate dashboard specification
python business-intelligence/scripts/dashboard_spec_generator.py kpi_definitions.json

# 4. Monitor deployed ML model
python ml-ops-engineer/scripts/model_health_monitor.py model_metrics.json
```

## Quality Standards

**All data analytics Python tools must:**
- Use standard library only (no pandas, numpy, or external dependencies)
- Support both JSON and human-readable output via `--format` flag
- Provide clear error messages for malformed input data
- Return appropriate exit codes (0 success, 1 error)
- Process files locally with no API calls or network access
- Include argparse CLI with `--help` support
- Handle CSV and JSON input formats where applicable

**Skill documentation must:**
- Include realistic SQL examples with expected output shapes
- Provide industry-specific KPI definitions where relevant
- Reference authoritative methodologies (Kimball, Inmon, dbt best practices)
- Include data governance and privacy considerations

## Related Skills

- **Engineering:** Data engineering, ML engineering -> `../engineering-team/`
- **Product Team:** User analytics, metrics-driven product decisions -> `../product-team/`
- **Finance:** Financial data analysis, forecasting -> `../finance/`
- **Business & Growth:** Revenue analytics, customer health scoring -> `../business-growth/`

## Additional Resources

- **Main Documentation:** `../CLAUDE.md`
- **Standards Library:** `../standards/`

---

**Last Updated:** February 2026
**Skills Deployed:** 5/5 data analytics skills (SKILL.md knowledge bases)
**Python Tools:** Planned for next development phase
