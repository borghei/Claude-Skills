---
name: senior-pm
description: "Senior Project Manager for enterprise software, SaaS, and digital transformation projects. Provides portfolio health assessment, quantitative risk analysis, resource capacity optimization, stakeholder mapping, and executive reporting using weighted scoring, EMV analysis, and WSJF/RICE/ICE prioritization. Use when the user asks about portfolio health reviews, project risk quantification, resource capacity planning, stakeholder mapping, executive reporting, project prioritization, or managing a multi-project portfolio."
license: MIT + Commons Clause
metadata:
  version: 2.0.0
  author: borghei
  category: project-management
  domain: enterprise-pm
  updated: 2026-03-04
  tags: [project-management, stakeholder-management, risk, planning]
  python-tools: project_health_dashboard.py, risk_matrix_analyzer.py, resource_capacity_planner.py, stakeholder_mapper.py
  tech-stack: portfolio-management, risk-analysis, stakeholder-mapping, executive-reporting
---

# Senior Project Management Expert

Strategic project management for enterprise software, SaaS, and digital transformation initiatives. The agent provides portfolio health assessment, quantitative risk analysis, resource optimization, stakeholder mapping, and executive-level reporting for complex project portfolios.

## Core Workflow

### 1. Assess Portfolio Health

The agent runs the health dashboard to produce composite scores across 5 weighted dimensions:

```bash
python3 scripts/project_health_dashboard.py assets/sample_project_data.json
```

**Health Dimensions (Weighted Scoring):**

| Dimension | Weight | Green (>80) | Amber (60-80) | Red (<40) |
|-----------|--------|-------------|---------------|-----------|
| Timeline | 25% | On schedule | Minor delays | Critical path at risk |
| Budget | 25% | <5% variance | 5-15% variance | >15% overrun |
| Scope | 20% | Features on track | Some scope creep | Major re-scope needed |
| Quality | 20% | Coverage >80% | Moderate debt | Critical defects |
| Risk | 10% | Mitigations active | Gaps identified | Unmitigated critical risks |

**RAG Status:** Green >80 all dims >60; Amber 60-80 or any dim 40-60; Red <60 or any dim <40.

**Validate:** Composite score calculated; any red dimensions have documented intervention plans.

### 2. Quantify Risks

The agent runs risk analysis to calculate Expected Monetary Value and prioritize mitigations:

```bash
python3 scripts/risk_matrix_analyzer.py assets/sample_project_data.json
```

**Risk Quantification:**
```
Risk Score = Probability (1-5) × Impact (1-5) × Category Weight
Category Weights: Technical 1.2x, Resource 1.1x, Financial 1.4x, Schedule 1.0x
```

**Response strategy by score:**
- **Avoid** (>18): Eliminate through scope/approach changes
- **Mitigate** (12-18): Reduce probability or impact actively
- **Transfer** (8-12): Insurance, contracts, partnerships
- **Accept** (<8): Monitor with contingency planning

**Validate:** All risks scored; critical risks (>18) have documented avoidance plans; risk-adjusted budget calculated.

### 3. Optimize Resource Capacity

The agent analyzes resource utilization and identifies bottlenecks:

```bash
python3 scripts/resource_capacity_planner.py assets/sample_project_data.json
```

Target utilization: 70-85% for sustainable productivity. The agent identifies over/under-allocated resources and critical path constraints.

**Validate:** No resources above 90% utilization; bottleneck resources have reallocation plans.

### 4. Map Stakeholders

The agent classifies stakeholders using Mendelow's Matrix and generates communication plans:

```bash
python3 scripts/stakeholder_mapper.py stakeholders.json
python3 scripts/stakeholder_mapper.py --demo --format json
```

**Quadrants (threshold at 5/10):**
- **Manage Closely** (High Power, High Interest): Weekly 1:1s, steering committee
- **Keep Satisfied** (High Power, Low Interest): Monthly executive summary
- **Keep Informed** (Low Power, High Interest): Bi-weekly newsletter, dashboards
- **Monitor** (Low Power, Low Interest): Quarterly updates

The tool identifies blockers and generates targeted engagement strategies based on power level.

**Validate:** All stakeholders classified; high-power blockers have engagement plans; communication cadence defined per quadrant.

### 5. Select Prioritization Model

The agent selects the appropriate model based on context:

- **Resource Constrained?** → WSJF: `(User Value + Time Criticality + Risk Reduction) ÷ Job Size`
- **Customer Impact Focus?** → RICE: `(Reach × Impact × Confidence) ÷ Effort`
- **Need Speed?** → ICE: `(Impact + Confidence + Ease) ÷ 3`
- **Multiple Stakeholder Groups?** → MoSCoW

Reference: `references/portfolio-prioritization-models.md`

**Validate:** Model selection rationale documented; top 5 priorities scored and ranked.

### 6. Generate Executive Report

The agent synthesizes outputs into a board-ready report:
- RAG status dashboard with trend analysis
- Top 3 risks with mitigation status
- Resource utilization summary
- Forward-looking recommendations with ROI projections

Template: `assets/executive_report_template.md`

**Validate:** Report is ≤ 2 pages for executive audience; all red items have action plans with owners and dates.

## Anti-Patterns

1. **Reporting health scores without calibrating weights** — Default dimension weights may not match organizational priorities. The agent recalibrates weights with executive sponsors before first use.
2. **Treating all risks as medium** — Teams avoid extreme ratings. The agent uses three-point estimation and references past incidents to force granularity in probability/impact scoring.
3. **Overloading resources above 85%** — Utilization above 85% does not account for meetings, context-switching, and unplanned work. The agent includes 15% overhead and 5% context-switching penalty.
4. **Presenting full dimension breakdowns to executives** — Executives need a 1-page RAG summary, not 5-page analysis. The agent tailors report depth to audience level.

## Assets & Templates

| Template | Reference |
|----------|-----------|
| Project Charter | `assets/project_charter_template.md` |
| Executive Report | `assets/executive_report_template.md` |
| RACI Matrix | `assets/raci_matrix_template.md` |
| Stakeholder Map | `assets/stakeholder_map_template.md` |
| Sample Portfolio Data | `assets/sample_project_data.json` |

## Tools

### project_health_dashboard.py

Aggregates project metrics across timeline, budget, scope, quality, and risk dimensions. Produces composite health scores and RAG status.

```bash
python3 scripts/project_health_dashboard.py data_file.json
python3 scripts/project_health_dashboard.py data_file.json --format json
```

### risk_matrix_analyzer.py

Builds probability/impact matrices, calculates weighted risk scores by category, and suggests mitigation strategies.

```bash
python3 scripts/risk_matrix_analyzer.py data_file.json
python3 scripts/risk_matrix_analyzer.py data_file.json --format json
```

### resource_capacity_planner.py

Models team capacity across projects, identifies utilization imbalances, and provides optimization recommendations.

```bash
python3 scripts/resource_capacity_planner.py data_file.json
python3 scripts/resource_capacity_planner.py data_file.json --format json
```

### stakeholder_mapper.py

Classifies stakeholders into Mendelow's Matrix quadrants and generates tailored communication plans with blocker engagement strategies.

```bash
python3 scripts/stakeholder_mapper.py stakeholders.json
python3 scripts/stakeholder_mapper.py --demo --format json
```

## Troubleshooting

| Symptom | Resolution |
|---------|------------|
| Health score does not match stakeholder perception | Recalibrate dimension weights with executive sponsors; ensure all 5 dimensions have data |
| All risks clustered in medium zone | Facilitate risk calibration workshop; use three-point estimation and reference past incidents |
| Capacity planner shows zero gaps despite complaints | Verify capacity factors include 15% meeting overhead and 5% context-switching penalty |
| Stakeholder mapper classifies everyone as "Manage Closely" | Adjust power/interest thresholds (default: 5); use relative ranking within group |
| RAG status oscillates weekly | Widen amber band (e.g., 55-80); use rolling 2-week average instead of point-in-time |

## References

- [Portfolio Prioritization Models](references/portfolio-prioritization-models.md) — WSJF, RICE, ICE, MoSCoW decision frameworks
- [Risk Management Framework](references/risk-management-framework.md) — EMV calculation, Monte Carlo simulation, risk appetite framework
- [Stakeholder Engagement Guide](references/stakeholder-engagement-guide.md) — Communication plans, blocker engagement, escalation paths

## Integration Points

| Skill | Direction | Use Case |
|-------|-----------|----------|
| `scrum-master/` | Receives from | Sprint velocity feeds portfolio health |
| `sprint-retrospective/` | Receives from | Retro insights inform process improvement |
| `execution/brainstorm-okrs/` | Feeds into | Portfolio priorities shape OKR themes |
| `discovery/pre-mortem/` | Receives from | Launch risks escalate to portfolio register |
| Jira via Atlassian MCP | Bidirectional | Pull data for health analysis; push reports |
