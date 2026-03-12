---
name: people-analytics
description: >
  Expert people analytics covering workforce analytics, HR metrics, predictive modeling,
  employee insights, and data-driven HR decisions. Use when building turnover prediction
  models, analyzing engagement surveys, running pay equity regressions, designing
  people dashboards, scoring flight risk, or advising HR leaders with workforce data.
version: 1.0.0
author: borghei
category: hr-operations
tags: [people-analytics, hr-metrics, workforce, insights, predictive]
---

# People Analytics

The agent operates as a senior people analytics partner, translating workforce data into actionable insights using statistical modeling, segmentation analysis, and data governance best practices.

## Workflow

1. **Frame the question** -- Clarify the business question with the HR or business stakeholder. Examples: "Why is Sales attrition 2x the company average?" or "Are we paying equitably across gender?" Define the success metric for the analysis.
2. **Assess data readiness** -- Identify required data sources (HRIS, ATS, survey platform, payroll). Check for completeness, recency, and quality. Flag any gaps before proceeding.
3. **Analyze** -- Apply the appropriate method from the analytics toolkit (descriptive stats, regression, classification, segmentation). Document assumptions and limitations.
4. **Validate findings** -- Sense-check results with domain experts (HRBPs, managers). Test for statistical significance and practical significance. Check predictive models for bias across protected groups.
5. **Recommend** -- Translate findings into 2-3 specific, actionable recommendations with expected impact and cost.
6. **Deliver and monitor** -- Present insights using the dashboard framework. Set up ongoing monitoring for key metrics with alert thresholds.

> Checkpoint: After step 2, confirm that all data has been anonymized or aggregated to comply with privacy policy before analysis begins.

## Analytics Maturity Model

| Level | Name | Capabilities | Typical Questions Answered |
|-------|------|-------------|---------------------------|
| 1 | Operational Reporting | Headcount, compliance, ad-hoc queries | "How many people do we have?" |
| 2 | Advanced Reporting | Dashboards, trends, benchmarking, segmentation | "How has attrition changed by quarter?" |
| 3 | Analytics | Statistical analysis, correlation, root cause | "What drives attrition in Sales?" |
| 4 | Predictive | Turnover prediction, performance modeling, risk scoring | "Who is likely to leave in the next 6 months?" |
| 5 | Prescriptive | Automated recommendations, real-time interventions | "What should we do to retain this person?" |

## Core HR Metrics

### Workforce Metrics

| Metric | Formula | Benchmark |
|--------|---------|-----------|
| Turnover Rate | (Separations / Avg HC) x 100 | 10-15% |
| Retention Rate | (Retained / Starting HC) x 100 | 85-90% |
| Time to Fill | Days from req open to offer accept | 30-45 days |
| Cost per Hire | Total recruiting cost / Hires | $3-5K |
| Regrettable Turnover | Regrettable exits / Total exits | < 30% |

### Performance Metrics

| Metric | Formula | Benchmark |
|--------|---------|-----------|
| High Performers | % rated top tier | 15-20% |
| Goal Completion | Goals achieved / Goals set | 80%+ |
| Promotion Rate | Promotions / Headcount | 8-12% |

### Engagement Metrics

| Metric | Formula | Benchmark |
|--------|---------|-----------|
| eNPS | Promoters % - Detractors % | 20-40 |
| Engagement Score | Survey composite (1-100) | 70%+ |
| Absenteeism | Absent days / Work days | < 3% |

## Turnover Prediction Model

```python
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

def build_turnover_model(employee_data: pd.DataFrame) -> dict:
    """
    Build and evaluate a turnover prediction model.

    Input: DataFrame with columns for features + 'left_company' (0/1).
    Output: dict with model, feature importance, and evaluation metrics.
    """
    features = [
        'tenure_months', 'salary_ratio_to_market', 'performance_rating',
        'months_since_last_promotion', 'manager_tenure', 'team_size',
        'engagement_score', 'training_hours_ytd', 'projects_completed'
    ]

    X = employee_data[features]
    y = employee_data['left_company']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    report = classification_report(y_test, y_pred, output_dict=True)

    importance = (
        pd.DataFrame({'feature': features, 'importance': model.feature_importances_})
        .sort_values('importance', ascending=False)
    )

    return {'model': model, 'importance': importance, 'evaluation': report}


def score_flight_risk(model, current_employees: pd.DataFrame) -> pd.DataFrame:
    """
    Score current employees for flight risk.

    Returns DataFrame with employee_id, flight_risk_score (0-1), and risk_level.
    """
    probabilities = model.predict_proba(current_employees[model.feature_names_in_])[:, 1]

    risk_levels = pd.cut(
        probabilities,
        bins=[0, 0.25, 0.50, 0.75, 1.0],
        labels=['Low', 'Medium', 'High', 'Critical']
    )

    return pd.DataFrame({
        'employee_id': current_employees['employee_id'],
        'flight_risk_score': probabilities.round(3),
        'risk_level': risk_levels
    }).sort_values('flight_risk_score', ascending=False)
```

## Example: Sales Attrition Root-Cause Analysis

```
QUESTION
  Sales voluntary turnover is 22% vs 12% company average. Why?

DATA
  Source: HRIS + engagement survey + exit interviews (n=45 exits, trailing 12 mo)

ANALYSIS
  Segmentation by tenure band:
    < 1 yr: 35% of exits (onboarding/ramp issues)
    1-2 yr: 40% of exits (comp dissatisfaction + career path)
    2+ yr: 25% of exits (manager relationship)

  Regression on exit survey scores (n=38 respondents):
    Top drivers of intent-to-leave:
      1. "I am paid fairly" (beta = -0.42, p < 0.01)
      2. "I see a career path here" (beta = -0.31, p < 0.01)
      3. "My manager supports my development" (beta = -0.28, p < 0.05)

  Compensation benchmark:
    Sales IC3 compa-ratio: 0.88 (12% below midpoint)
    Sales IC2 compa-ratio: 0.91 (9% below midpoint)
    Rest of company average: 0.98

FINDINGS
  1. Sales comp is significantly below market, especially at IC2-IC3
  2. No defined career ladder for Sales ICs beyond IC3
  3. New hires (< 1 yr) leaving due to unrealistic ramp expectations

RECOMMENDATIONS
  1. Market adjustment: Bring Sales IC2-IC3 to 95th percentile compa-ratio ($180K budget)
  2. Publish a Sales career ladder through IC5 with clear promotion criteria
  3. Redesign onboarding: extend ramp period from 30 to 90 days with milestone targets

EXPECTED IMPACT
  Reduce Sales attrition from 22% to 14-16% within 12 months
  ROI: $180K adjustment saves ~$450K in replacement costs (10 fewer exits x $45K/hire)
```

## Pay Equity Analysis

```python
import pandas as pd
import statsmodels.api as sm

def analyze_pay_equity(employee_data: pd.DataFrame) -> dict:
    """
    Conduct pay equity analysis controlling for legitimate pay factors.

    Returns raw gap, adjusted gap, model fit, and employees flagged for review.
    """
    # Raw gap
    avg_by_gender = employee_data.groupby('gender')['salary'].mean()
    raw_gap = (avg_by_gender['Female'] - avg_by_gender['Male']) / avg_by_gender['Male']

    # Adjusted gap (control for level, tenure, performance, location)
    controls = pd.get_dummies(
        employee_data[['job_level', 'tenure_years', 'performance_rating', 'department', 'location']],
        drop_first=True
    )
    controls = sm.add_constant(controls)
    controls['is_female'] = (employee_data['gender'] == 'Female').astype(int)

    model = sm.OLS(employee_data['salary'], controls).fit()
    adjusted_gap = model.params['is_female']

    # Flag outliers (residual > 2 std dev)
    employee_data['predicted'] = model.predict(controls)
    employee_data['residual'] = employee_data['salary'] - employee_data['predicted']
    threshold = 2 * employee_data['residual'].std()
    flagged = employee_data[abs(employee_data['residual']) > threshold]

    return {
        'raw_gap_pct': round(raw_gap * 100, 1),
        'adjusted_gap_usd': round(adjusted_gap, 0),
        'model_r_squared': round(model.rsquared, 3),
        'employees_flagged': len(flagged),
        'flagged_details': flagged[['employee_id', 'salary', 'predicted', 'residual']]
    }
```

## Engagement Survey Analysis

1. **Calculate response rate** -- Target 80%+ for statistical validity. Flag departments below 60%.
2. **Compute category scores** -- Average Likert responses by category (Manager, Growth, Culture, Compensation). Compare to prior period.
3. **Run driver analysis** -- Regress category scores against overall engagement to identify which categories have the highest impact on engagement.
4. **Segment** -- Break results by department, level, tenure band, and location. Identify where scores diverge most from company average.
5. **Prioritize** -- Plot categories on a 2x2 matrix (Impact vs Score). "High impact, low score" quadrant = priority action areas.

> Checkpoint: Suppress results for any segment with fewer than 5 respondents to protect anonymity.

## DEI Metrics Framework

| Domain | Metrics | Data Source |
|--------|---------|-------------|
| Representation | Gender / ethnicity distribution by level | HRIS |
| Pay equity | Raw gap, adjusted gap (controlled regression) | Payroll + HRIS |
| Progression | Promotion rates by demographic group | HRIS |
| Hiring | Offer and accept rates by demographic group | ATS |
| Inclusion | Inclusion index, belonging score, psychological safety | Survey |

## Data Governance Checklist

Before starting any people analytics project:

- [ ] Business question and purpose clearly documented
- [ ] Data minimization applied (only collect what is needed)
- [ ] Privacy impact assessment completed
- [ ] Anonymization or aggregation applied where possible
- [ ] Predictive models tested for bias across protected groups
- [ ] Role-based access controls implemented
- [ ] Data retention policy defined
- [ ] Employee communication planned (transparency principle)

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
