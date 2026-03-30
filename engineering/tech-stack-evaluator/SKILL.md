---
name: tech-stack-evaluator
description: >
  Technology stack evaluation and comparison with TCO analysis, security
  assessment, and ecosystem health scoring. Use when comparing frameworks,
  evaluating technology stacks, calculating total cost of ownership, assessing
  migration paths, or analyzing ecosystem viability.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: technology-evaluation
  updated: 2026-03-31
  tags: [framework-comparison, tco-analysis, technology-evaluation]
---
# Technology Stack Evaluator

Evaluate and compare technologies, frameworks, and cloud providers with data-driven analysis and actionable recommendations.

## Table of Contents

- [Capabilities](#capabilities)
- [Quick Start](#quick-start)
- [Input Formats](#input-formats)
- [Analysis Types](#analysis-types)
- [Scripts](#scripts)
- [References](#references)

---

## Capabilities

| Capability | Description |
|------------|-------------|
| Technology Comparison | Compare frameworks and libraries with weighted scoring |
| TCO Analysis | Calculate 5-year total cost including hidden costs |
| Ecosystem Health | Assess GitHub metrics, npm adoption, community strength |
| Security Assessment | Evaluate vulnerabilities and compliance readiness |
| Migration Analysis | Estimate effort, risks, and timeline for migrations |
| Cloud Comparison | Compare AWS, Azure, GCP for specific workloads |

---

## Quick Start

### Compare Two Technologies

```
Compare React vs Vue for a SaaS dashboard.
Priorities: developer productivity (40%), ecosystem (30%), performance (30%).
```

### Calculate TCO

```
Calculate 5-year TCO for Next.js on Vercel.
Team: 8 developers. Hosting: $2500/month. Growth: 40%/year.
```

### Assess Migration

```
Evaluate migrating from Angular.js to React.
Codebase: 50,000 lines, 200 components. Team: 6 developers.
```

---

## Input Formats

The evaluator accepts three input formats:

**Text** - Natural language queries
```
Compare PostgreSQL vs MongoDB for our e-commerce platform.
```

**YAML** - Structured input for automation
```yaml
comparison:
  technologies: ["React", "Vue"]
  use_case: "SaaS dashboard"
  weights:
    ecosystem: 30
    performance: 25
    developer_experience: 45
```

**JSON** - Programmatic integration
```json
{
  "technologies": ["React", "Vue"],
  "use_case": "SaaS dashboard"
}
```

---

## Analysis Types

### Quick Comparison (200-300 tokens)
- Weighted scores and recommendation
- Top 3 decision factors
- Confidence level

### Standard Analysis (500-800 tokens)
- Comparison matrix
- TCO overview
- Security summary

### Full Report (1200-1500 tokens)
- All metrics and calculations
- Migration analysis
- Detailed recommendations

---

## Scripts

### stack_comparator.py

Compare technologies with customizable weighted criteria.

```bash
python scripts/stack_comparator.py --help
```

### tco_calculator.py

Calculate total cost of ownership over multi-year projections.

```bash
python scripts/tco_calculator.py --input assets/sample_input_tco.json
```

### ecosystem_analyzer.py

Analyze ecosystem health from GitHub, npm, and community metrics.

```bash
python scripts/ecosystem_analyzer.py --technology react
```

### security_assessor.py

Evaluate security posture and compliance readiness.

```bash
python scripts/security_assessor.py --technology express --compliance soc2,gdpr
```

### migration_analyzer.py

Estimate migration complexity, effort, and risks.

```bash
python scripts/migration_analyzer.py --from angular-1.x --to react
```

---

## References

| Document | Content |
|----------|---------|
| `references/metrics.md` | Detailed scoring algorithms and calculation formulas |
| `references/examples.md` | Input/output examples for all analysis types |
| `references/workflows.md` | Step-by-step evaluation workflows |

---

## Confidence Levels

| Level | Score | Interpretation |
|-------|-------|----------------|
| High | 80-100% | Clear winner, strong data |
| Medium | 50-79% | Trade-offs present, moderate uncertainty |
| Low | < 50% | Close call, limited data |

---

## When to Use

- Comparing frontend/backend frameworks for new projects
- Evaluating cloud providers for specific workloads
- Planning technology migrations with risk assessment
- Calculating build vs. buy decisions with TCO
- Assessing open-source library viability

## When NOT to Use

- Trivial decisions between similar tools (use team preference)
- Mandated technology choices (decision already made)
- Emergency production issues (use monitoring tools)

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Weighted scores all return 50.0 | Technology data dictionaries missing `score` keys under each category | Ensure each category dict contains a `score` key on a 0-100 scale (e.g., `{"performance": {"score": 85}}`) |
| TCO projections look unrealistically low | Default cost parameters used when `operational_costs` or `initial_costs` are empty | Populate `monthly_hosting`, `annual_licensing`, `developer_hourly_rate`, and `maintenance_hours_per_dev_monthly` with real figures |
| Ecosystem health score stuck at 50 for npm | `npm_data` dict is empty or not provided | Pass npm metrics (`weekly_downloads`, `version`, `dependencies_count`, `days_since_last_publish`); 50 is the neutral fallback when npm data is absent |
| Security compliance returns "Unknown standard" | Unsupported standard name passed to `assess_compliance()` | Use one of the supported keys: `GDPR`, `SOC2`, `HIPAA`, `PCI_DSS` (case-sensitive) |
| Migration complexity always shows moderate | `architecture_change_level` defaults to `moderate` when not specified | Set `architecture_change_level` explicitly to `minimal`, `moderate`, `significant`, or `complete` in `codebase_stats` |
| Report renders ASCII tables instead of markdown | `ReportGenerator` auto-detects CLI context when stdout is a TTY | Pass `output_context='desktop'` to force rich markdown output |
| Format detector misclassifies YAML as text | Fewer than 50% of lines match YAML key-value patterns | Ensure input uses standard YAML syntax with `key: value` pairs and proper indentation |

---

## Success Criteria

- **TCO variance under 15%**: Calculated TCO deviates less than 15% from actual costs when validated against real-world spending data over the projection period.
- **Security score above 80/100**: Technologies recommended for production use achieve a minimum overall security score of 80, corresponding to grade B or higher.
- **Ecosystem health score above 65/100**: Recommended technologies demonstrate viable long-term ecosystem health with a risk level no worse than "Low-Medium."
- **Migration effort estimate within 20%**: Person-hours and timeline estimates land within 20% of actual migration effort when measured post-completion.
- **Comparison confidence above 70%**: Final technology recommendations carry a confidence score of 70% or higher, indicating a meaningful score gap between top candidates.
- **Compliance readiness at "Mostly Ready" or above**: Technologies targeting regulated environments achieve at least 70% feature coverage against required compliance standards (GDPR, SOC2, HIPAA, PCI-DSS).
- **Report generation under 5 seconds**: All report types (executive summary, full report) render within 5 seconds for evaluations comparing up to 5 technologies.

---

## Scope & Limitations

**Covers:**
- Weighted multi-criteria comparison of frameworks, libraries, and cloud providers
- Multi-year TCO projections including hidden costs (technical debt, vendor lock-in, turnover)
- Ecosystem viability assessment using GitHub, npm, and community metrics
- Security posture scoring and compliance readiness for GDPR, SOC2, HIPAA, PCI-DSS

**Does NOT cover:**
- Live data fetching from GitHub API, npm registry, or vulnerability databases (all data must be provided as input dictionaries)
- Performance benchmarking or load testing (use `engineering/senior-qa` for test execution)
- Licensing legal review or contract negotiation (use `ra-qm-team` compliance skills for regulatory guidance)
- Team hiring or organizational design decisions (use `hr-operations/talent-acquisition` for staffing analysis)

---

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `engineering/senior-security` | Feed security assessor output into deeper vulnerability analysis | `SecurityAssessor` results → security review input |
| `engineering/senior-devops` | Use TCO hosting projections to inform infrastructure planning | `TCOCalculator` hosting/scaling data → DevOps capacity models |
| `engineering/senior-qa` | Migration test coverage scores inform QA test planning | `MigrationAnalyzer` testing_requirements → QA test strategy |
| `ra-qm-team/compliance-auditor` | Compliance readiness gaps feed into formal audit preparation | `SecurityAssessor.assess_compliance()` missing features → audit checklist |
| `c-level-advisor/cto-advisor` | Executive summaries and TCO reports support CTO decision-making | `ReportGenerator` executive summary → strategic technology decisions |
| `product-team/product-manager` | Ecosystem viability and migration timelines inform product roadmaps | `EcosystemAnalyzer` + `MigrationAnalyzer` → roadmap planning |

---

## Tool Reference

### stack_comparator.py

**Purpose:** Compare technologies with customizable weighted criteria across 8 evaluation categories: performance, scalability, developer experience, ecosystem, learning curve, documentation, community support, and enterprise readiness.

**Usage:**
```python
from stack_comparator import StackComparator

comparator = StackComparator({
    "technologies": ["React", "Vue"],
    "use_case": "SaaS dashboard",
    "weights": {"developer_experience": 40, "performance": 30, "ecosystem": 30}
})

results = comparator.compare_technologies(tech_data_list)
```

**Constructor Parameters (`comparison_data` dict):**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `technologies` | list | `[]` | Names of technologies to compare |
| `use_case` | str | `"general"` | Use case context (supports `real-time`, `enterprise`, `startup` bonuses) |
| `priorities` | dict | `{}` | Priority overrides |
| `weights` | dict | `DEFAULT_WEIGHTS` | Category weights (auto-normalized to 100) |

**Default Weights:** performance 15, scalability 15, developer_experience 20, ecosystem 15, learning_curve 10, documentation 10, community_support 10, enterprise_readiness 5.

**Key Methods:**
- `compare_technologies(tech_data_list)` -- Full comparison with scores, recommendation, confidence, and decision factors
- `score_technology(tech_name, tech_data)` -- Score a single technology across all categories
- `calculate_weighted_score(category_scores)` -- Calculate weighted total from category scores
- `generate_pros_cons(tech_name, tech_scores)` -- Generate pros/cons lists from scores

**Example Output:**
```json
{
  "technologies": {"React": {"weighted_total": 78.5, "strengths": [...], "weaknesses": [...]}},
  "recommendation": "React",
  "confidence": 72.0,
  "decision_factors": [{"category": "developer_experience", "importance": "40.0%", "best_performer": "React"}],
  "comparison_matrix": [{"category": "performance", "weight": "15.0%", "scores": {"React": "82.0", "Vue": "79.0"}}]
}
```

**Output Format:** Python dictionary (serialize with `json.dumps()` for JSON output).

---

### tco_calculator.py

**Purpose:** Calculate comprehensive Total Cost of Ownership over multi-year projections, including initial costs, operational costs, scaling costs, hidden costs (technical debt, vendor lock-in, security incidents, downtime, turnover), and developer productivity impact.

**Usage:**
```python
from tco_calculator import TCOCalculator

calculator = TCOCalculator({
    "technology": "Next.js",
    "team_size": 8,
    "timeline_years": 5,
    "initial_costs": {"licensing": 0, "migration": 15000, "developer_hourly_rate": 100},
    "operational_costs": {"monthly_hosting": 2500, "annual_licensing": 0, "maintenance_hours_per_dev_monthly": 20},
    "scaling_params": {"annual_growth_rate": 0.40, "initial_users": 5000}
})

tco = calculator.calculate_total_tco()
summary = calculator.generate_tco_summary()
```

**Constructor Parameters (`tco_data` dict):**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `technology` | str | `"Unknown"` | Technology name |
| `team_size` | int | `5` | Number of developers |
| `timeline_years` | int | `5` | Projection period in years |
| `initial_costs` | dict | `{}` | One-time costs: `licensing`, `migration`, `setup`, `tooling`, `training_hours_per_dev`, `developer_hourly_rate`, `training_materials` |
| `operational_costs` | dict | `{}` | Recurring costs: `monthly_hosting`, `annual_licensing`, `annual_support`, `maintenance_hours_per_dev_monthly` |
| `scaling_params` | dict | `{}` | Growth params: `annual_growth_rate`, `initial_users`, `initial_servers`, `cost_per_server_monthly` |
| `productivity_factors` | dict | `{}` | Productivity: `productivity_multiplier`, `time_to_market_reduction_days`, `avg_feature_time_days`, `avg_feature_value`, `technical_debt_percentage`, `vendor_lock_in_risk`, `security_incidents_per_year`, `avg_security_incident_cost`, `downtime_hours_per_year`, `downtime_cost_per_hour`, `annual_turnover_rate`, `cost_per_new_hire` |

**Key Methods:**
- `calculate_total_tco()` -- Complete TCO with all cost components
- `generate_tco_summary()` -- Executive summary with formatted dollar amounts
- `calculate_initial_costs()` -- One-time cost breakdown
- `calculate_operational_costs()` -- Year-by-year operational costs
- `calculate_scaling_costs()` -- User projections and cost-per-user analysis
- `calculate_hidden_costs()` -- Technical debt, vendor lock-in, security, downtime, turnover
- `calculate_productivity_impact()` -- Productivity gains and feature velocity

**Output Format:** Python dictionary (all monetary values as floats; `generate_tco_summary()` returns pre-formatted dollar strings).

---

### ecosystem_analyzer.py

**Purpose:** Analyze technology ecosystem health and long-term viability by scoring GitHub activity, npm adoption, community strength, corporate backing, and maintenance responsiveness on a 0-100 scale.

**Usage:**
```python
from ecosystem_analyzer import EcosystemAnalyzer

analyzer = EcosystemAnalyzer({
    "technology": "React",
    "github": {"stars": 220000, "forks": 45000, "contributors": 1500, "commits_last_month": 120},
    "npm": {"weekly_downloads": 20000000, "version": "18.2.0", "dependencies_count": 3},
    "community": {"stackoverflow_questions": 400000, "job_postings": 15000},
    "corporate_backing": {"type": "major_tech_company"}
})

report = analyzer.generate_ecosystem_report()
viability = analyzer.assess_viability()
```

**Constructor Parameters (`ecosystem_data` dict):**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `technology` | str | `"Unknown"` | Technology name |
| `github` | dict | `{}` | GitHub metrics: `stars`, `forks`, `contributors`, `commits_last_month`, `avg_issue_response_hours`, `issue_resolution_rate`, `releases_per_year`, `active_maintainers`, `open_issues` |
| `npm` | dict | `{}` | npm metrics: `weekly_downloads`, `version`, `dependencies_count`, `days_since_last_publish` |
| `community` | dict | `{}` | Community metrics: `stackoverflow_questions`, `job_postings`, `tutorials_count`, `forum_members` |
| `corporate_backing` | dict | `{}` | Backing info: `type` (one of `major_tech_company`, `established_company`, `startup_backed`, `community_led`, `none`), `funding_millions` |

**Health Score Weights:** github_health 25%, npm_health 20%, community_health 20%, corporate_backing 15%, maintenance_health 20%.

**Key Methods:**
- `generate_ecosystem_report()` -- Complete report with health scores, viability, and formatted metrics
- `calculate_health_score()` -- Component scores and weighted overall score
- `assess_viability()` -- Viability level, risk assessment, strengths, and recommendation

**Output Format:** Python dictionary with nested health scores, viability assessment, and formatted metrics.

---

### security_assessor.py

**Purpose:** Evaluate security posture and compliance readiness for technology stacks. Scores vulnerabilities, patch responsiveness, built-in security features, and track record. Assesses compliance against GDPR, SOC2, HIPAA, and PCI-DSS.

**Usage:**
```python
from security_assessor import SecurityAssessor

assessor = SecurityAssessor({
    "technology": "Express",
    "vulnerabilities": {
        "critical_last_12m": 0, "high_last_12m": 2,
        "avg_critical_patch_days": 7, "has_security_team": True
    },
    "security_features": {
        "encryption_in_transit": True, "authentication": True,
        "input_validation": True, "csrf_protection": True
    },
    "compliance_requirements": ["SOC2", "GDPR"]
})

report = assessor.generate_security_report()
compliance = assessor.assess_compliance(["SOC2", "GDPR"])
```

**Constructor Parameters (`security_data` dict):**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `technology` | str | `"Unknown"` | Technology name |
| `vulnerabilities` | dict | `{}` | Vulnerability data: `critical_last_12m`, `high_last_12m`, `medium_last_12m`, `low_last_12m`, `critical_last_3y`, `high_last_3y`, `medium_last_3y`, `low_last_3y`, `avg_critical_patch_days`, `avg_high_patch_days`, `has_security_team`, `years_since_major_incident`, `has_security_certifications`, `has_bug_bounty_program`, `security_audits_per_year`, `common_vulnerability_types` |
| `security_features` | dict | `{}` | Boolean feature flags: `encryption_at_rest`, `encryption_in_transit`, `authentication`, `authorization`, `input_validation`, `rate_limiting`, `csrf_protection`, `xss_protection`, `sql_injection_protection`, `audit_logging`, `mfa_support`, `rbac`, `secrets_management`, `security_headers`, `cors_configuration` |
| `compliance_requirements` | list | `[]` | Standards to assess: `GDPR`, `SOC2`, `HIPAA`, `PCI_DSS` |

**Security Score Weights:** vulnerability_score 30%, patch_responsiveness 25%, security_features 30%, track_record 15%.

**Key Methods:**
- `generate_security_report()` -- Full report with score, compliance, vulnerabilities, and recommendations
- `calculate_security_score()` -- Component scores with letter grade (A-F)
- `assess_compliance(standards)` -- Per-standard readiness with missing features list
- `identify_vulnerabilities()` -- Categorized vulnerability report with trend analysis

**Output Format:** Python dictionary with security scores, compliance assessments, and risk level.

---

### migration_analyzer.py

**Purpose:** Analyze migration complexity, estimate effort in person-hours and calendar months, assess technical/business/team risks, and recommend a migration approach (direct, phased, or strangler pattern) based on complexity scoring.

**Usage:**
```python
from migration_analyzer import MigrationAnalyzer

analyzer = MigrationAnalyzer({
    "source_technology": "Angular 1.x",
    "target_technology": "React",
    "codebase_stats": {
        "lines_of_code": 50000, "num_components": 200,
        "architecture_change_level": "significant",
        "current_test_coverage": 0.6
    },
    "team": {"team_size": 6, "target_tech_experience": "low"},
    "constraints": {"downtime_tolerance": "low"}
})

plan = analyzer.generate_migration_plan()
effort = analyzer.estimate_effort()
risks = analyzer.assess_risks()
```

**Constructor Parameters (`migration_data` dict):**

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `source_technology` | str | `"Unknown"` | Current technology |
| `target_technology` | str | `"Unknown"` | Target technology |
| `codebase_stats` | dict | `{}` | Codebase metrics: `lines_of_code`, `num_files`, `num_components`, `architecture_change_level` (`minimal`/`moderate`/`significant`/`complete`), `has_database`, `database_size_gb`, `schema_changes_required`, `data_transformation_required`, `breaking_api_changes` (`none`/`minimal`/`some`/`many`/`complete`), `num_dependencies`, `dependencies_to_replace`, `current_test_coverage` (0-1), `num_tests` |
| `team` | dict | `{}` | Team info: `team_size`, `hours_per_week`, `target_tech_experience` (`none`/`low`/`medium`/`high`) |
| `constraints` | dict | `{}` | Constraints: `downtime_tolerance` (`none`/`low`/`medium`/`high`) |

**Complexity Score Weights:** code_volume 20%, architecture_changes 25%, data_migration 20%, api_compatibility 15%, dependency_changes 10%, testing_requirements 10%.

**Key Methods:**
- `generate_migration_plan()` -- Complete plan with complexity, effort, risks, approach, and success criteria
- `calculate_complexity_score()` -- Per-factor complexity scores (1-10 scale)
- `estimate_effort()` -- Person-hours, person-months, phase breakdown, and calendar timeline
- `assess_risks()` -- Technical, business, and team risks with severity and mitigation strategies

**Output Format:** Python dictionary with nested complexity analysis, effort estimation, risk assessment, and recommended approach.

---

### report_generator.py

**Purpose:** Generate context-aware evaluation reports with progressive disclosure. Auto-detects output context (Claude Desktop vs CLI) and renders rich markdown tables or ASCII-formatted output accordingly. Supports selective section generation.

**Usage:**
```python
from report_generator import ReportGenerator

generator = ReportGenerator(report_data, output_context="desktop")

executive_summary = generator.generate_executive_summary(max_tokens=300)
full_report = generator.generate_full_report(sections=["executive_summary", "comparison_matrix", "tco_analysis"])
generator.export_to_file("evaluation_report.md")
```

**Constructor Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `report_data` | dict | (required) | Complete evaluation data containing any combination of: `technologies`, `recommendation`, `decision_factors`, `comparison_matrix`, `tco_analysis`, `ecosystem_health`, `security_assessment`, `migration_analysis`, `performance_benchmarks`, `use_case` |
| `output_context` | str | `None` (auto-detect) | Output format: `"desktop"` for rich markdown, `"cli"` for ASCII tables. Auto-detects via `CLAUDE_DESKTOP` env var and TTY check |

**Available Report Sections:** `executive_summary`, `comparison_matrix`, `tco_analysis`, `ecosystem_health`, `security_assessment`, `migration_analysis`, `performance_benchmarks`.

**Key Methods:**
- `generate_executive_summary(max_tokens=300)` -- Concise summary with recommendation, strengths, concerns, and decision factors
- `generate_full_report(sections=None)` -- Complete report with selected sections (all if None)
- `export_to_file(filename, sections=None)` -- Write report to file, returns file path

**Output Format:** Markdown string (desktop context) or ASCII-formatted string (CLI context).

---

### format_detector.py

**Purpose:** Automatically detect and parse input format (JSON, YAML, URL, or natural language text) for technology evaluation requests. Extracts technology names, use cases, priorities, and analysis types from unstructured text input.

**Usage:**
```python
from format_detector import FormatDetector

detector = FormatDetector('Compare React vs Vue for a SaaS dashboard. Priorities: performance, ecosystem.')

format_type = detector.detect_format()   # Returns: "text"
parsed = detector.parse()                # Returns normalized dict
info = detector.get_format_info()        # Returns detection metadata
```

**Constructor Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `input_data` | str | (required) | Raw input string in any supported format |

**Supported Formats:**
- **JSON** -- Valid JSON objects are detected and parsed directly
- **YAML** -- Detected when >50% of lines match key-value or list patterns (simplified parser, no PyYAML dependency)
- **URL** -- Detected when input contains `http://` or `https://` URLs; categorizes GitHub, npm, and other URLs
- **Text** -- Natural language fallback; extracts technologies from 30+ known keywords, identifies use cases, priorities, and analysis types

**Key Methods:**
- `detect_format()` -- Returns format string: `"json"`, `"yaml"`, `"url"`, or `"text"`
- `parse()` -- Parse input and return normalized dictionary with standard keys: `technologies`, `use_case`, `priorities`, `analysis_type`, `format`
- `get_format_info()` -- Detection metadata: `detected_format`, `input_length`, `line_count`, `parsing_successful`

**Output Format:** Python dictionary normalized to a standard structure with keys: `technologies` (list), `use_case` (str), `priorities` (list), `analysis_type` (str), `format` (str).
