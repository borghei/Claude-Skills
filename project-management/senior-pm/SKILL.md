---
name: senior-pm
description: >
  Senior Project Manager for enterprise software, SaaS, and digital
  transformation projects. Specializes in portfolio management, quantitative
  risk analysis, resource optimization, stakeholder alignment, and executive
  reporting. Uses advanced methodologies including EMV analysis, Monte Carlo
  simulation, WSJF prioritization, and multi-dimensional health scoring.
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

## Overview

Strategic project management for enterprise software, SaaS, and digital transformation initiatives. This skill provides sophisticated portfolio management capabilities, quantitative analysis tools, and executive-level reporting frameworks for managing complex, multi-million dollar project portfolios.

### Core Expertise Areas

**Portfolio Management & Strategic Alignment**
- Multi-project portfolio optimization using advanced prioritization models (WSJF, RICE, ICE, MoSCoW)
- Strategic roadmap development aligned with business objectives and market conditions
- Resource capacity planning and allocation optimization across portfolio
- Portfolio health monitoring with multi-dimensional scoring frameworks

**Quantitative Risk Management**
- Expected Monetary Value (EMV) analysis for financial risk quantification
- Monte Carlo simulation for schedule risk modeling and confidence intervals
- Risk appetite framework implementation with enterprise-level thresholds
- Portfolio risk correlation analysis and diversification strategies

**Executive Communication & Governance**
- Board-ready executive reports with RAG status and strategic recommendations
- Stakeholder alignment through sophisticated RACI matrices and escalation paths
- Financial performance tracking with risk-adjusted ROI and NPV calculations
- Change management strategies for large-scale digital transformations

## Methodology & Frameworks

### Three-Tier Analysis Approach

**Tier 1: Portfolio Health Assessment**
Uses `project_health_dashboard.py` to provide comprehensive multi-dimensional scoring:

```bash
python3 scripts/project_health_dashboard.py assets/sample_project_data.json
```

**Health Dimensions (Weighted Scoring):**
- **Timeline Performance** (25% weight): Schedule adherence, milestone achievement, critical path analysis
- **Budget Management** (25% weight): Spend variance, forecast accuracy, cost efficiency metrics
- **Scope Delivery** (20% weight): Feature completion rates, requirement satisfaction, change control
- **Quality Metrics** (20% weight): Code coverage, defect density, technical debt, security posture
- **Risk Exposure** (10% weight): Risk score, mitigation effectiveness, exposure trends

**RAG Status Calculation:**
- 🟢 Green: Composite score >80, all dimensions >60
- 🟡 Amber: Composite score 60-80, or any dimension 40-60
- 🔴 Red: Composite score <60, or any dimension <40

**Tier 2: Risk Matrix & Mitigation Strategy**
Leverages `risk_matrix_analyzer.py` for quantitative risk assessment:

```bash
python3 scripts/risk_matrix_analyzer.py assets/sample_project_data.json
```

**Risk Quantification Process:**
1. **Probability Assessment** (1-5 scale): Historical data, expert judgment, Monte Carlo inputs
2. **Impact Analysis** (1-5 scale): Financial, schedule, quality, and strategic impact vectors
3. **Category Weighting**: Technical (1.2x), Resource (1.1x), Financial (1.4x), Schedule (1.0x)
4. **EMV Calculation**: Risk Score = (Probability × Impact × Category Weight)

**Risk Response Strategies:**
- **Avoid** (>18 score): Eliminate through scope/approach changes
- **Mitigate** (12-18 score): Reduce probability or impact through active intervention
- **Transfer** (8-12 score): Insurance, contracts, partnerships
- **Accept** (<8 score): Monitor with contingency planning

**Tier 3: Resource Capacity Optimization**
Employs `resource_capacity_planner.py` for portfolio resource analysis:

```bash
python3 scripts/resource_capacity_planner.py assets/sample_project_data.json
```

**Capacity Analysis Framework:**
- **Utilization Optimization**: Target 70-85% for sustainable productivity
- **Skill Matching**: Algorithm-based resource allocation to maximize efficiency
- **Bottleneck Identification**: Critical path resource constraints across portfolio
- **Scenario Planning**: What-if analysis for resource reallocation strategies

### Advanced Prioritization Models

**Weighted Shortest Job First (WSJF) - For Agile Portfolios**
```
WSJF Score = (User Value + Time Criticality + Risk Reduction) ÷ Job Size

Application Context:
- Resource-constrained environments
- Fast-moving competitive landscapes  
- Agile/SAFe methodology adoption
- Clear cost-of-delay quantification available
```

**RICE Framework - For Product Development**
```
RICE Score = (Reach × Impact × Confidence) ÷ Effort

Best for:
- Customer-facing initiatives
- Marketing and growth projects
- When reach metrics are quantifiable
- Data-driven product decisions
```

**ICE Scoring - For Rapid Decision Making**
```  
ICE Score = (Impact + Confidence + Ease) ÷ 3

Optimal when:
- Quick prioritization needed
- Brainstorming and ideation phases
- Limited analysis time available
- Cross-functional team alignment required
```

**Decision Tree for Model Selection:**
Reference: `references/portfolio-prioritization-models.md`

- **Resource Constrained?** → WSJF
- **Customer Impact Focus?** → RICE
- **Need Speed?** → ICE
- **Multiple Stakeholder Groups?** → MoSCoW
- **Complex Trade-offs?** → Multi-Criteria Decision Analysis (MCDA)

### Risk Management Framework

**Quantitative Risk Analysis Process:**
Reference: `references/risk-management-framework.md`

**Step 1: Risk Identification & Classification**
- Technical risks: Architecture, integration, performance
- Resource risks: Availability, skills, retention
- Schedule risks: Dependencies, critical path, external factors
- Financial risks: Budget overruns, currency, economic factors
- Business risks: Market changes, competitive pressure, strategic shifts

**Step 2: Probability/Impact Assessment**
Uses three-point estimation for Monte Carlo simulation:
```
Expected Value = (Optimistic + 4×Most Likely + Pessimistic) ÷ 6
Standard Deviation = (Pessimistic - Optimistic) ÷ 6
```

**Step 3: Expected Monetary Value (EMV) Calculation**
```
EMV = Σ(Probability × Financial Impact) for all risk scenarios

Risk-Adjusted Budget = Base Budget × (1 + Risk Premium)
Risk Premium = Portfolio Risk Score × Risk Tolerance Factor
```

**Step 4: Portfolio Risk Correlation Analysis**
```
Portfolio Risk = √(Σ Individual Risks² + 2Σ Correlation×Risk1×Risk2)
```

**Risk Appetite Framework:**
- **Conservative**: Risk scores 0-8, 25-30% contingency reserves
- **Moderate**: Risk scores 8-15, 15-20% contingency reserves  
- **Aggressive**: Risk scores 15+, 10-15% contingency reserves

## Stakeholder Mapping & Engagement

### Power/Interest Grid (Mendelow's Matrix)

Uses `stakeholder_mapper.py` to classify stakeholders and generate communication plans:

```bash
python3 scripts/stakeholder_mapper.py stakeholders.json
python3 scripts/stakeholder_mapper.py --demo --format json
```

**Classification Quadrants (threshold at 5/10):**
- **Manage Closely** (High Power, High Interest): Weekly 1:1s, steering committee, proactive escalation
- **Keep Satisfied** (High Power, Low Interest): Monthly executive summary, milestone invites
- **Keep Informed** (Low Power, High Interest): Bi-weekly newsletter, demo invites, dashboards
- **Monitor** (Low Power, Low Interest): Quarterly updates, organizational newsletter

**Blocker Engagement Strategy:**
The tool identifies stakeholders with `attitude: blocker` and generates targeted engagement strategies based on their power level — high-power blockers require urgent 1:1 engagement and potential executive sponsor escalation; low-power blockers need transparency and involvement.

**Integration with OKR Brainstorming:**
Stakeholder mapping feeds directly into OKR alignment — high-power/high-interest stakeholders shape strategic objectives, while their feedback validates Key Results. Cross-reference with `execution/brainstorm-okrs/` for OKR development workflows.

Reference: `references/stakeholder-engagement-guide.md`
Template: `assets/stakeholder_map_template.md`

## Assets & Templates

### Project Charter Template
Reference: `assets/project_charter_template.md`

**Comprehensive 12-section charter including:**
- Executive summary with strategic alignment
- Success criteria with KPIs and quality gates
- RACI matrix with decision authority levels
- Risk assessment with mitigation strategies
- Budget breakdown with contingency analysis
- Timeline with critical path dependencies

**Key Features:**
- Production-ready for board presentation
- Integrated stakeholder management framework
- Risk-adjusted financial projections
- Change control and governance processes

### Executive Report Template  
Reference: `assets/executive_report_template.md`

**Board-level portfolio reporting with:**
- RAG status dashboard with trend analysis
- Financial performance vs. strategic objectives
- Risk heat map with mitigation status
- Resource utilization and capacity analysis
- Forward-looking recommendations with ROI projections

**Executive Decision Support:**
- Critical issues requiring immediate action
- Investment recommendations with business cases
- Portfolio optimization opportunities
- Market/competitive intelligence integration

### RACI Matrix Template
Reference: `assets/raci_matrix_template.md`

**Enterprise-grade responsibility assignment featuring:**
- Detailed stakeholder roster with decision authority
- Phase-based RACI assignments (initiation through deployment)
- Escalation paths with timeline and authority levels
- Communication protocols and meeting frameworks
- Conflict resolution processes with governance integration

**Advanced Features:**
- Decision-making RACI for strategic vs. operational choices
- Risk and issue management responsibility assignment
- Performance metrics for RACI effectiveness
- Template validation checklist and maintenance procedures

### Sample Portfolio Data
Reference: `assets/sample_project_data.json`

**Realistic multi-project portfolio including:**
- 4 projects across different phases and priorities
- Complete financial data (budgets, actuals, forecasts)
- Resource allocation with utilization metrics
- Risk register with probability/impact scoring
- Quality metrics and stakeholder satisfaction data
- Dependencies and milestone tracking

**Data Completeness:**
- Works with all three analysis scripts
- Demonstrates portfolio balance across strategic priorities
- Includes both successful and at-risk project examples
- Provides historical trend data for analysis

### Expected Output Examples
Reference: `assets/expected_output.json`

**Demonstrates script capabilities with:**
- Portfolio health scores and RAG status
- Risk matrix visualization and mitigation priorities
- Resource capacity analysis with optimization recommendations
- Integration examples showing how outputs complement each other

## Implementation Workflows

### Portfolio Health Review (Weekly)

1. **Data Collection & Validation**
   ```bash
   # Update project data from JIRA, financial systems, team surveys
   python3 scripts/project_health_dashboard.py current_portfolio.json
   ```

2. **Risk Assessment Update**
   ```bash
   # Refresh risk probabilities and impact assessments
   python3 scripts/risk_matrix_analyzer.py current_portfolio.json
   ```

3. **Capacity Analysis**
   ```bash  
   # Review resource utilization and bottlenecks
   python3 scripts/resource_capacity_planner.py current_portfolio.json
   ```

4. **Executive Summary Generation**
   - Synthesize outputs into executive report format
   - Highlight critical issues and recommendations
   - Prepare stakeholder communications

### Monthly Strategic Review

1. **Portfolio Prioritization Review**
   - Apply WSJF/RICE/ICE models to evaluate current priorities
   - Assess strategic alignment with business objectives
   - Identify optimization opportunities

2. **Risk Portfolio Analysis**
   - Update risk appetite and tolerance levels
   - Review portfolio risk correlation and concentration
   - Adjust risk mitigation investments

3. **Resource Optimization Planning**
   - Analyze capacity constraints across upcoming quarter
   - Plan resource reallocation and hiring strategies
   - Identify skill gaps and training needs

4. **Stakeholder Alignment Session**
   - Present portfolio health and strategic recommendations
   - Gather feedback on prioritization and resource allocation
   - Align on upcoming quarter priorities and investments

### Quarterly Portfolio Optimization

1. **Strategic Alignment Assessment**
   - Evaluate portfolio contribution to business objectives
   - Assess market and competitive position changes
   - Update strategic priorities and success criteria

2. **Financial Performance Review**
   - Analyze risk-adjusted ROI across portfolio
   - Review budget performance and forecast accuracy
   - Optimize investment allocation for maximum value

3. **Capability Gap Analysis**
   - Identify emerging technology and skill requirements
   - Plan capability building investments
   - Assess make vs. buy vs. partner decisions

4. **Portfolio Rebalancing**
   - Apply three horizons model for innovation balance
   - Optimize risk-return profile using efficient frontier
   - Plan new initiatives and sunset decisions

## Integration Strategies

### Atlassian Integration
- **Jira**: Portfolio dashboards, cross-project metrics, risk tracking
- **Confluence**: Strategic documentation, executive reports, knowledge management
- Use MCP integrations to automate data collection and report generation

### Financial Systems Integration
- **Budget Tracking**: Real-time spend data for variance analysis
- **Resource Costing**: Hourly rates and utilization for capacity planning
- **ROI Measurement**: Value realization tracking against projections

### Stakeholder Management
- **Executive Dashboards**: Real-time portfolio health visualization
- **Team Scorecards**: Individual project performance metrics
- **Risk Registers**: Collaborative risk management with automated escalation

## Handoff Protocols

### TO Scrum Master
**Context Transfer:**
- Strategic priorities and success criteria
- Resource allocation and team composition
- Risk factors requiring sprint-level attention
- Quality standards and acceptance criteria

**Ongoing Collaboration:**
- Weekly velocity and health metrics review
- Sprint retrospective insights for portfolio learning
- Impediment escalation and resolution support
- Team capacity and utilization feedback

### TO Product Owner
**Strategic Context:**
- Market prioritization and competitive analysis
- User value frameworks and measurement criteria
- Feature prioritization aligned with portfolio objectives
- Resource and timeline constraints

**Decision Support:**
- ROI analysis for feature investments
- Risk assessment for product decisions
- Market intelligence and customer feedback integration
- Strategic roadmap alignment and dependencies

### FROM Executive Team
**Strategic Direction:**
- Business objective updates and priority changes
- Budget allocation and resource approval decisions
- Risk appetite and tolerance level adjustments
- Market strategy and competitive response decisions

**Performance Expectations:**
- Portfolio health and value delivery targets
- Timeline and milestone commitment expectations
- Quality standards and compliance requirements
- Stakeholder satisfaction and communication standards

## Success Metrics & KPIs

### Portfolio Performance Indicators
- **On-time Delivery Rate**: >80% projects delivered within 10% of planned timeline
- **Budget Variance**: <5% average variance across portfolio
- **Quality Score**: >85 composite quality rating across all projects
- **Risk Mitigation Effectiveness**: >90% risks with active mitigation plans
- **Resource Utilization**: 75-85% average utilization across teams

### Strategic Value Indicators  
- **ROI Achievement**: >90% projects meeting ROI projections within 12 months
- **Strategic Alignment**: >95% portfolio investment aligned with business priorities
- **Innovation Balance**: 70% operational, 20% growth, 10% transformational projects
- **Stakeholder Satisfaction**: >8.5/10 average satisfaction across executive stakeholders
- **Value Acceleration**: <6 months average time from completion to value realization

### Risk Management Indicators
- **Risk Exposure Level**: Maintain within approved risk appetite ranges
- **Risk Resolution Time**: <30 days average for medium risks, <7 days for high risks
- **Mitigation Cost Efficiency**: Mitigation spend <20% of total portfolio risk EMV
- **Risk Prediction Accuracy**: >70% accuracy in risk probability assessments

## Continuous Improvement Framework

### Portfolio Learning Integration
- Capture lessons learned from completed projects
- Update risk probability assessments based on historical data
- Refine estimation accuracy through retrospective analysis
- Share best practices across project teams

### Methodology Evolution
- Regular review of prioritization model effectiveness
- Update risk frameworks based on industry best practices
- Integrate new tools and technologies for analysis efficiency
- Benchmark against industry portfolio performance standards

### Stakeholder Feedback Integration
- Quarterly stakeholder satisfaction surveys
- Executive interview feedback on decision support quality
- Team feedback on process efficiency and effectiveness
- Customer impact assessment of portfolio decisions

This skill represents the pinnacle of enterprise project management capability, providing both strategic oversight and tactical execution support for complex digital transformation initiatives. The combination of quantitative analysis, sophisticated prioritization, and executive-level communication enables senior project managers to drive significant business value while managing enterprise-level risks and complexities.

## Troubleshooting

| Symptom | Likely Cause | Resolution |
|---------|-------------|------------|
| Portfolio health score does not match stakeholder perception | Dimension weights misaligned with organizational priorities, or data inputs incomplete | Recalibrate HEALTH_DIMENSIONS weights with executive sponsors; ensure all 5 dimensions have data |
| Risk matrix shows all risks clustered in medium zone | Probability/impact scoring lacks granularity or team avoids extreme ratings | Facilitate risk calibration workshop; use three-point estimation and reference past incidents |
| Resource capacity planner shows zero gaps despite team complaints | Utilization data does not account for meeting overhead, context-switching, or unplanned work | Verify CAPACITY_FACTORS config; include 15% meeting overhead and 5% context-switching penalty |
| Stakeholder mapper classifies everyone as "Manage Closely" | Power/interest thresholds too low for your organization, or scores inflated | Adjust POWER_THRESHOLD and INTEREST_THRESHOLD (default: 5); use relative ranking within group |
| RAG status oscillates between green and amber weekly | Thresholds set too tight, or data updates cause noise | Widen amber band (e.g., 55-80 instead of 60-80); use rolling 2-week average instead of point-in-time |
| EMV calculations produce unrealistically high risk exposure | Category weights compounding with high probability/impact scores | Review RISK_CATEGORIES weights; cap financial risk weight at 1.4x; validate probability estimates against historical data |
| Executive reports are too long for stakeholder attention span | Report template includes too many detail sections for the audience | Tailor output to audience using the tone guide; executives need 1-page RAG summary, not full dimension breakdown |

## Success Criteria

- Portfolio average health score maintained above 75/100 across all active projects
- On-time delivery rate exceeds 80% (within 10% of planned timeline)
- Budget variance maintained below 5% average across the portfolio
- Risk mitigation effectiveness above 90% (all critical/high risks have active mitigation plans)
- Resource utilization consistently in the 70-85% optimal range
- Stakeholder satisfaction above 8.5/10 as measured by quarterly surveys
- All projects in red RAG status have documented intervention plans within 48 hours

## Scope & Limitations

**In Scope:**
- Multi-project portfolio health assessment with weighted composite scoring
- Quantitative risk analysis using EMV, probability/impact matrices, and category weighting
- Resource capacity planning with utilization optimization and skill-matching
- Stakeholder mapping with Mendelow's Matrix and targeted communication plans
- Executive-level reporting with RAG status dashboards and strategic recommendations

**Out of Scope:**
- Sprint-level team management (see `scrum-master/` skill)
- Product backlog management and feature prioritization (see `execution/prioritization-frameworks/`)
- Agile coaching and team maturity assessment (see `agile-coach/` skill)
- Financial modeling beyond project-level ROI (see `finance/` domain skills)
- Contract negotiation and procurement management

**Important Caveats:**
- Health scores use deterministic formulas, not ML predictions. Calibrate thresholds to your portfolio context.
- Risk EMV calculations assume independent risks. Portfolio risk correlation analysis (Step 4) provides a more accurate combined view but requires cross-project dependency data.
- Resource capacity planning models are weekly snapshots; they do not account for intra-week variability or unplanned work spikes.

## Integration Points

| Integration | Direction | Description |
|------------|-----------|-------------|
| `scrum-master/` | Receives from | Sprint velocity and health metrics feed portfolio-level health dashboards |
| `sprint-retrospective/` | Receives from | Retro insights inform stakeholder reports and process improvement tracking |
| `execution/brainstorm-okrs/` | Feeds into | Portfolio priorities and strategic context shape quarterly OKR themes |
| `execution/outcome-roadmap/` | Feeds into | Portfolio health data influences roadmap commitment levels (Now/Next/Later) |
| `discovery/pre-mortem/` | Receives from | Launch-blocking tigers escalate into portfolio risk register |
| `execution/release-notes/` | Complements | Release notes incorporate stakeholder communication plans from mapper |
| Jira via Atlassian MCP | Bidirectional | Pull project data for health analysis; push status reports to Confluence |
| Financial Systems | Receives from | Real-time budget and spend data for variance analysis |

## Tool Reference

### project_health_dashboard.py

Aggregates project metrics across timeline, budget, scope, quality, and risk dimensions. Produces composite health scores and RAG status.

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `data_file` | positional | (required) | Path to JSON file containing project portfolio data |
| `--format` | choice | `text` | Output format: `text` or `json` |

### risk_matrix_analyzer.py

Builds probability/impact matrices, calculates weighted risk scores by category, and suggests mitigation strategies.

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `data_file` | positional | (required) | Path to JSON file containing risk register data |
| `--format` | choice | `text` | Output format: `text` or `json` |

### resource_capacity_planner.py

Models team capacity across projects, identifies utilization imbalances, and provides optimization recommendations.

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `data_file` | positional | (required) | Path to JSON file containing resource and project capacity data |
| `--format` | choice | `text` | Output format: `text` or `json` |

### stakeholder_mapper.py

Classifies stakeholders into Mendelow's Matrix quadrants and generates tailored communication plans with blocker engagement strategies.

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `data_file` | positional | (optional) | Path to JSON file with stakeholder data |
| `--format` | choice | `text` | Output format: `text` or `json` |
| `--demo` | flag | off | Run with built-in sample data (10 stakeholders) |