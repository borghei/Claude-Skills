---
name: people-analytics
description: Expert people analytics covering workforce analytics, HR metrics, predictive modeling, employee insights, and data-driven HR decisions.
version: 1.0.0
author: Claude Skills
category: hr-operations
tags: [people-analytics, hr-metrics, workforce, insights, predictive]
---

# People Analytics

Expert-level people analytics for data-driven HR decisions.

## Core Competencies

- Workforce analytics
- HR metrics development
- Predictive modeling
- Survey analysis
- Reporting and visualization
- Statistical analysis
- Data governance
- Storytelling with data

## People Analytics Framework

### Analytics Maturity

```
LEVEL 1: Operational Reporting
├── Headcount reports
├── Basic HR metrics
├── Compliance reporting
└── Ad-hoc queries

LEVEL 2: Advanced Reporting
├── Dashboards
├── Trend analysis
├── Benchmarking
└── Segmentation

LEVEL 3: Analytics
├── Statistical analysis
├── Correlation analysis
├── Root cause analysis
└── What-if modeling

LEVEL 4: Predictive
├── Turnover prediction
├── Performance modeling
├── Workforce planning
└── Risk assessment

LEVEL 5: Prescriptive
├── Automated recommendations
├── Real-time insights
├── AI-driven decisions
└── Continuous optimization
```

### Analytics Domains

```
PEOPLE ANALYTICS DOMAINS

WORKFORCE PLANNING
├── Headcount planning
├── Capacity modeling
├── Skills gap analysis
└── Succession planning

TALENT ACQUISITION
├── Sourcing effectiveness
├── Time to fill
├── Quality of hire
├── Diversity hiring

PERFORMANCE & DEVELOPMENT
├── Performance distribution
├── Learning effectiveness
├── Career progression
└── High-potential identification

ENGAGEMENT & RETENTION
├── Employee satisfaction
├── Turnover analysis
├── Engagement drivers
└── Flight risk prediction

COMPENSATION & REWARDS
├── Pay equity analysis
├── Compensation benchmarking
├── Benefits utilization
└── Total rewards optimization

DIVERSITY & INCLUSION
├── Representation metrics
├── Pay gap analysis
├── Promotion equity
└── Inclusion sentiment
```

## HR Metrics

### Core Metrics Framework

**Workforce Metrics:**
| Metric | Formula | Benchmark |
|--------|---------|-----------|
| Headcount | Total employees | - |
| FTE | Full-time equivalents | - |
| Turnover Rate | (Separations / Avg HC) × 100 | 10-15% |
| Retention Rate | (Retained / Starting HC) × 100 | 85-90% |
| Time to Fill | Days req open to offer accept | 30-45 days |
| Cost per Hire | Total recruiting cost / Hires | $3-5K |

**Performance Metrics:**
| Metric | Formula | Benchmark |
|--------|---------|-----------|
| High Performers | % rated top tier | 15-20% |
| Performance Distribution | Rating distribution | Normal curve |
| Goal Completion | Goals achieved / Goals set | 80%+ |
| Promotion Rate | Promotions / Headcount | 8-12% |

**Engagement Metrics:**
| Metric | Formula | Benchmark |
|--------|---------|-----------|
| eNPS | Promoters - Detractors | 20-40 |
| Engagement Score | Survey composite | 70%+ |
| Absenteeism | Absent days / Work days | <3% |
| Regrettable Turnover | Regrettable exits / Total exits | <30% |

### Metrics Dashboard

```
┌─────────────────────────────────────────────────────────────────┐
│              PEOPLE ANALYTICS DASHBOARD                          │
├─────────────────────────────────────────────────────────────────┤
│  Headcount       Turnover        Engagement      Diversity       │
│  2,847           12.5%           78%             42% women       │
│  +124 YTD        -2% vs LY       +3% vs LY       +5% vs LY      │
├─────────────────────────────────────────────────────────────────┤
│  TURNOVER BY DEPARTMENT                                          │
│  Engineering: 8%    Sales: 18%    Support: 15%    Ops: 10%      │
├─────────────────────────────────────────────────────────────────┤
│  ENGAGEMENT DRIVERS                                              │
│  Career Growth: 72%    Manager: 81%    Culture: 85%    Pay: 68% │
├─────────────────────────────────────────────────────────────────┤
│  TENURE DISTRIBUTION                                             │
│  <1yr: 25%    1-3yr: 35%    3-5yr: 22%    5+yr: 18%            │
└─────────────────────────────────────────────────────────────────┘
```

## Predictive Analytics

### Turnover Prediction

```python
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

def build_turnover_model(employee_data):
    """
    Build a turnover prediction model
    """
    # Feature engineering
    features = [
        'tenure_months',
        'salary_ratio_to_market',
        'performance_rating',
        'promotion_wait_months',
        'manager_tenure',
        'team_size',
        'commute_distance',
        'engagement_score',
        'training_hours_ytd',
        'projects_completed'
    ]

    X = employee_data[features]
    y = employee_data['left_company']

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Feature importance
    importance = pd.DataFrame({
        'feature': features,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)

    return model, importance

def predict_flight_risk(model, current_employees):
    """
    Score current employees for flight risk
    """
    probabilities = model.predict_proba(current_employees)[:, 1]

    risk_levels = pd.cut(
        probabilities,
        bins=[0, 0.25, 0.5, 0.75, 1.0],
        labels=['Low', 'Medium', 'High', 'Critical']
    )

    return pd.DataFrame({
        'employee_id': current_employees['employee_id'],
        'flight_risk_score': probabilities,
        'risk_level': risk_levels
    })
```

### Flight Risk Dashboard

```
┌─────────────────────────────────────────────────────────────────┐
│              FLIGHT RISK ANALYSIS                                │
├─────────────────────────────────────────────────────────────────┤
│  RISK DISTRIBUTION                                               │
│  Critical: 45 (3%)   High: 128 (9%)   Medium: 312 (22%)        │
│  Low: 934 (66%)                                                  │
├─────────────────────────────────────────────────────────────────┤
│  TOP RISK FACTORS                                                │
│  1. Time since last promotion: 0.28                             │
│  2. Salary vs market: 0.22                                      │
│  3. Manager tenure: 0.18                                        │
│  4. Engagement score: 0.15                                      │
│  5. Commute distance: 0.08                                      │
├─────────────────────────────────────────────────────────────────┤
│  HIGH RISK BY DEPARTMENT                                         │
│  Sales: 42 (15%)    Engineering: 28 (8%)    Support: 18 (12%)  │
├─────────────────────────────────────────────────────────────────┤
│  RECOMMENDED INTERVENTIONS                                       │
│  • 23 employees: Compensation review                            │
│  • 18 employees: Career conversation                            │
│  • 12 employees: Manager change                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Survey Analytics

### Survey Design

```markdown
# Employee Engagement Survey

## Survey Structure

### Section 1: Overall Engagement (5 questions)
- I would recommend this company as a great place to work
- I am proud to work for this company
- I see myself working here in 2 years
- This company motivates me to do my best work
- I rarely think about looking for a job elsewhere

### Section 2: Manager (6 questions)
- My manager cares about me as a person
- My manager provides clear expectations
- My manager gives regular feedback
- My manager supports my development
- My manager recognizes my contributions
- I trust my manager

### Section 3: Growth & Development (5 questions)
- I have opportunities to learn and grow
- I understand my career path here
- I receive training I need to do my job
- My work is challenging and interesting
- I can use my strengths every day

### Section 4: Culture & Values (5 questions)
- Company values align with my personal values
- Leaders model company values
- I feel included and belong here
- People are treated fairly regardless of background
- Open and honest communication is encouraged

### Section 5: Compensation & Benefits (4 questions)
- I am paid fairly for my work
- Benefits meet my needs
- Recognition is meaningful here
- Total rewards are competitive

## Response Scale
1 = Strongly Disagree
2 = Disagree
3 = Neutral
4 = Agree
5 = Strongly Agree
```

### Survey Analysis

```python
def analyze_survey_results(responses):
    """
    Comprehensive survey analysis
    """
    analysis = {}

    # Overall scores
    analysis['engagement_score'] = responses['engagement_items'].mean()
    analysis['response_rate'] = len(responses) / total_employees

    # Calculate eNPS
    promoters = (responses['recommend'] >= 9).sum()
    detractors = (responses['recommend'] <= 6).sum()
    analysis['enps'] = (promoters - detractors) / len(responses) * 100

    # Category scores
    categories = ['manager', 'growth', 'culture', 'compensation']
    for cat in categories:
        cat_items = [c for c in responses.columns if c.startswith(cat)]
        analysis[f'{cat}_score'] = responses[cat_items].mean().mean()

    # Segment analysis
    segments = ['department', 'level', 'tenure_band', 'location']
    for seg in segments:
        analysis[f'{seg}_breakdown'] = responses.groupby(seg).mean()

    # Driver analysis
    analysis['drivers'] = calculate_driver_importance(responses)

    # Trending
    analysis['vs_prior'] = compare_to_prior_survey(responses)

    return analysis

def calculate_driver_importance(responses):
    """
    Identify which factors most impact engagement
    """
    from sklearn.linear_model import LinearRegression

    X = responses[category_columns]
    y = responses['overall_engagement']

    model = LinearRegression()
    model.fit(X, y)

    return pd.DataFrame({
        'driver': category_columns,
        'impact': model.coef_
    }).sort_values('impact', ascending=False)
```

### Survey Results Report

```
┌─────────────────────────────────────────────────────────────────┐
│              ENGAGEMENT SURVEY RESULTS                           │
├─────────────────────────────────────────────────────────────────┤
│  Response Rate: 87%    Engagement Score: 78%    eNPS: +32      │
│  vs Prior: +3%                                                   │
├─────────────────────────────────────────────────────────────────┤
│  CATEGORY SCORES                                                 │
│  Culture: 85% (+5)    Manager: 81% (+2)    Growth: 72% (+4)    │
│  Recognition: 75% (0)  Compensation: 68% (-2)                   │
├─────────────────────────────────────────────────────────────────┤
│  TOP DRIVERS OF ENGAGEMENT                                       │
│  1. Career growth opportunities (r=0.72)                        │
│  2. Manager relationship (r=0.68)                               │
│  3. Meaningful work (r=0.65)                                    │
│  4. Recognition (r=0.58)                                        │
├─────────────────────────────────────────────────────────────────┤
│  PRIORITY AREAS (Low score, High impact)                        │
│  • Career path clarity (Score: 65%, Impact: High)               │
│  • Compensation fairness (Score: 62%, Impact: Medium)           │
│  • Learning opportunities (Score: 70%, Impact: High)            │
└─────────────────────────────────────────────────────────────────┘
```

## Diversity Analytics

### DEI Metrics

```
DEI METRICS FRAMEWORK

REPRESENTATION
├── Gender distribution
├── Ethnicity distribution
├── Age distribution
├── Disability status
└── Veteran status

PAY EQUITY
├── Gender pay gap
├── Ethnicity pay gap
├── Adjusted pay gap (controlling for factors)
└── Pay ratio analysis

PROGRESSION
├── Promotion rates by group
├── Hiring rates by group
├── Attrition rates by group
└── Leadership representation

INCLUSION
├── Inclusion index (survey)
├── Belonging score
├── Psychological safety
└── ERG participation
```

### Pay Equity Analysis

```python
def analyze_pay_equity(employee_data):
    """
    Conduct comprehensive pay equity analysis
    """
    import statsmodels.api as sm

    # Raw pay gap
    raw_gap = calculate_raw_gap(employee_data, 'gender')

    # Adjusted pay gap (controlling for legitimate factors)
    X = employee_data[[
        'job_level',
        'tenure_years',
        'performance_rating',
        'education',
        'department',
        'location'
    ]]
    X = pd.get_dummies(X, drop_first=True)
    X = sm.add_constant(X)

    y = employee_data['salary']
    gender = employee_data['gender']

    # Add gender as predictor
    X['gender_female'] = (gender == 'Female').astype(int)

    model = sm.OLS(y, X).fit()
    adjusted_gap = model.params['gender_female']

    # Identify outliers needing review
    employee_data['predicted_salary'] = model.predict(X)
    employee_data['residual'] = y - employee_data['predicted_salary']
    employee_data['needs_review'] = abs(employee_data['residual']) > 2 * employee_data['residual'].std()

    return {
        'raw_gap': raw_gap,
        'adjusted_gap': adjusted_gap,
        'model_r2': model.rsquared,
        'employees_for_review': employee_data[employee_data['needs_review']]
    }
```

### DEI Dashboard

```
┌─────────────────────────────────────────────────────────────────┐
│              DIVERSITY & INCLUSION DASHBOARD                     │
├─────────────────────────────────────────────────────────────────┤
│  REPRESENTATION                                                  │
│  Women: 42% (+3% YoY)    URG: 28% (+2% YoY)    Veterans: 5%    │
├─────────────────────────────────────────────────────────────────┤
│  REPRESENTATION BY LEVEL                                         │
│  Level       Women    URG      vs Target                        │
│  IC          45%      30%      ✓ On track                       │
│  Manager     38%      22%      ↑ Improving                      │
│  Director    32%      18%      ↗ Progress needed                │
│  VP+         28%      15%      ⚠ Gap to close                   │
├─────────────────────────────────────────────────────────────────┤
│  PAY EQUITY                                                      │
│  Gender Gap (Raw): -5.2%    Gender Gap (Adjusted): -1.8%        │
│  Ethnicity Gap (Raw): -4.8%  Ethnicity Gap (Adjusted): -0.9%   │
├─────────────────────────────────────────────────────────────────┤
│  INCLUSION INDEX                                                 │
│  Overall: 78%    Belonging: 82%    Safety: 75%    Voice: 72%   │
└─────────────────────────────────────────────────────────────────┘
```

## Workforce Planning

### Workforce Model

```python
def build_workforce_plan(current_state, business_plan):
    """
    Build strategic workforce plan
    """
    # Calculate future demand
    demand = calculate_demand(business_plan)

    # Project supply (current + expected changes)
    supply = project_supply(
        current_headcount=current_state['headcount'],
        turnover_rate=current_state['turnover'],
        retirement_rate=current_state['retirement_eligible']
    )

    # Calculate gap
    gap = demand - supply

    # Build plan to close gap
    plan = {
        'external_hiring': max(0, gap * 0.6),
        'internal_development': gap * 0.3,
        'contingent_workforce': gap * 0.1,
        'cost_estimate': estimate_costs(gap)
    }

    return plan

def calculate_demand(business_plan):
    """
    Calculate headcount demand from business projections
    """
    base_headcount = business_plan['revenue'] / business_plan['revenue_per_head']

    # Adjust for productivity improvements
    productivity_factor = 1 + business_plan['productivity_improvement']
    adjusted_demand = base_headcount / productivity_factor

    return adjusted_demand
```

### Workforce Dashboard

```
┌─────────────────────────────────────────────────────────────────┐
│              WORKFORCE PLANNING                                  │
├─────────────────────────────────────────────────────────────────┤
│  Current HC       Projected Need      Gap          Timeline     │
│  2,847            3,200               +353         12 months    │
├─────────────────────────────────────────────────────────────────┤
│  GAP BY FUNCTION                                                 │
│  Engineering: +120    Sales: +85    Product: +45    Other: +103 │
├─────────────────────────────────────────────────────────────────┤
│  FILL STRATEGY                                                   │
│  External Hire: 212 (60%)    Internal Move: 106 (30%)          │
│  Contractors: 35 (10%)                                          │
├─────────────────────────────────────────────────────────────────┤
│  SKILLS GAPS                                                     │
│  ML Engineering: Critical    Cloud Architecture: High           │
│  Data Science: Medium        Product Management: Low            │
├─────────────────────────────────────────────────────────────────┤
│  SUCCESSION READINESS                                            │
│  Key Roles: 85    Ready Now: 42 (49%)    Ready 1-2yr: 28 (33%) │
└─────────────────────────────────────────────────────────────────┘
```

## Data Governance

### Data Ethics

```markdown
# People Analytics Data Ethics Framework

## Principles

### 1. Transparency
- Employees know what data is collected
- Purpose of analysis is communicated
- Results are shared appropriately

### 2. Consent
- Data collection with consent where required
- Opt-out options for non-essential analytics
- Clear data usage policies

### 3. Fairness
- Models tested for bias
- Protected attributes handled appropriately
- Outcomes reviewed for disparate impact

### 4. Privacy
- Data minimization
- Anonymization where possible
- Access controls

### 5. Security
- Encryption at rest and in transit
- Role-based access
- Audit logging

## Governance Checklist

- [ ] Purpose clearly defined and documented
- [ ] Data minimization applied
- [ ] Privacy impact assessment completed
- [ ] Bias testing performed
- [ ] Access controls implemented
- [ ] Retention policy defined
- [ ] Employee communication planned
```

## Reference Materials

- `references/hr_metrics.md` - Complete HR metrics guide
- `references/predictive_models.md` - Predictive modeling approaches
- `references/survey_design.md` - Survey methodology
- `references/data_ethics.md` - Ethical analytics practices

## Scripts

```bash
# Turnover analysis
python scripts/turnover_analyzer.py --data employees.csv

# Flight risk scorer
python scripts/flight_risk.py --model model.pkl --employees current.csv

# Survey analyzer
python scripts/survey_analyzer.py --responses survey.csv --prior prior.csv

# DEI metrics generator
python scripts/dei_metrics.py --data workforce.csv

# Workforce planner
python scripts/workforce_planner.py --current state.csv --plan business_plan.yaml
```
