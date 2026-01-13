---
name: data-scientist
description: Expert data science covering machine learning, statistical modeling, experimentation, predictive analytics, and advanced analytics.
version: 1.0.0
author: Claude Skills
category: data-analytics
tags: [data-science, machine-learning, statistics, modeling, analytics]
---

# Data Scientist

Expert-level data science for business impact.

## Core Competencies

- Machine learning
- Statistical modeling
- Experimentation design
- Predictive analytics
- Feature engineering
- Model evaluation
- Data storytelling
- Production ML

## Machine Learning Workflow

```
PROBLEM DEFINITION → DATA → FEATURES → MODEL → EVALUATION → DEPLOYMENT

1. Problem Definition
   - Business objective
   - Success metrics
   - Constraints

2. Data Collection
   - Data sources
   - Data quality
   - Sample size

3. Feature Engineering
   - Feature creation
   - Feature selection
   - Transformation

4. Model Development
   - Algorithm selection
   - Training
   - Tuning

5. Evaluation
   - Metrics
   - Validation
   - Business impact

6. Deployment
   - Production pipeline
   - Monitoring
   - Iteration
```

## Model Selection

### Algorithm Comparison

| Algorithm | Use Case | Pros | Cons |
|-----------|----------|------|------|
| Linear Regression | Continuous prediction | Interpretable, fast | Linear relationships only |
| Logistic Regression | Binary classification | Interpretable, probabilistic | Linear boundaries |
| Random Forest | Classification/Regression | Handles non-linearity | Less interpretable |
| XGBoost | Classification/Regression | High accuracy | Overfitting risk |
| Neural Networks | Complex patterns | Flexible | Requires lots of data |

### Model Selection Framework

```python
def select_model(problem_type, data_size, interpretability_need, accuracy_need):
    """
    problem_type: 'classification' or 'regression'
    data_size: 'small' (<10K), 'medium' (10K-1M), 'large' (>1M)
    interpretability_need: 'high', 'medium', 'low'
    accuracy_need: 'high', 'medium', 'low'
    """

    if interpretability_need == 'high':
        if problem_type == 'classification':
            return 'Logistic Regression'
        else:
            return 'Linear Regression'

    if data_size == 'small':
        return 'Random Forest'

    if accuracy_need == 'high':
        if data_size == 'large':
            return 'Neural Network'
        else:
            return 'XGBoost'

    return 'Random Forest'
```

## Feature Engineering

### Feature Types

```python
# Numerical Features
def engineer_numerical(df, col):
    features = {
        f'{col}_log': np.log1p(df[col]),
        f'{col}_sqrt': np.sqrt(df[col]),
        f'{col}_squared': df[col] ** 2,
        f'{col}_binned': pd.cut(df[col], bins=5, labels=False)
    }
    return pd.DataFrame(features)

# Categorical Features
def engineer_categorical(df, col):
    # One-hot encoding
    dummies = pd.get_dummies(df[col], prefix=col)

    # Target encoding
    target_mean = df.groupby(col)['target'].mean()
    target_encoded = df[col].map(target_mean)

    # Frequency encoding
    freq = df[col].value_counts(normalize=True)
    freq_encoded = df[col].map(freq)

    return dummies, target_encoded, freq_encoded

# Time Features
def engineer_time(df, col):
    df[col] = pd.to_datetime(df[col])
    features = {
        f'{col}_hour': df[col].dt.hour,
        f'{col}_day': df[col].dt.day,
        f'{col}_dayofweek': df[col].dt.dayofweek,
        f'{col}_month': df[col].dt.month,
        f'{col}_is_weekend': df[col].dt.dayofweek.isin([5, 6]).astype(int),
        f'{col}_hour_sin': np.sin(2 * np.pi * df[col].dt.hour / 24),
        f'{col}_hour_cos': np.cos(2 * np.pi * df[col].dt.hour / 24)
    }
    return pd.DataFrame(features)
```

### Feature Selection

```python
from sklearn.feature_selection import mutual_info_classif, RFE
from sklearn.ensemble import RandomForestClassifier

def select_features(X, y, method='importance', n_features=20):
    if method == 'importance':
        model = RandomForestClassifier(n_estimators=100)
        model.fit(X, y)
        importance = pd.Series(model.feature_importances_, index=X.columns)
        return importance.nlargest(n_features).index.tolist()

    elif method == 'mutual_info':
        mi_scores = mutual_info_classif(X, y)
        mi_series = pd.Series(mi_scores, index=X.columns)
        return mi_series.nlargest(n_features).index.tolist()

    elif method == 'rfe':
        model = RandomForestClassifier(n_estimators=100)
        rfe = RFE(model, n_features_to_select=n_features)
        rfe.fit(X, y)
        return X.columns[rfe.support_].tolist()
```

## Model Evaluation

### Classification Metrics

```python
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix,
    classification_report
)

def evaluate_classification(y_true, y_pred, y_proba=None):
    metrics = {
        'accuracy': accuracy_score(y_true, y_pred),
        'precision': precision_score(y_true, y_pred),
        'recall': recall_score(y_true, y_pred),
        'f1': f1_score(y_true, y_pred),
    }

    if y_proba is not None:
        metrics['auc_roc'] = roc_auc_score(y_true, y_proba)

    print(classification_report(y_true, y_pred))
    print(confusion_matrix(y_true, y_pred))

    return metrics
```

### Regression Metrics

```python
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error,
    r2_score, mean_absolute_percentage_error
)

def evaluate_regression(y_true, y_pred):
    metrics = {
        'mae': mean_absolute_error(y_true, y_pred),
        'mse': mean_squared_error(y_true, y_pred),
        'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
        'r2': r2_score(y_true, y_pred),
        'mape': mean_absolute_percentage_error(y_true, y_pred)
    }
    return metrics
```

## Experimentation

### A/B Test Design

```python
from scipy import stats

def calculate_sample_size(baseline_rate, mde, alpha=0.05, power=0.8):
    """
    Calculate required sample size per variant

    baseline_rate: Current conversion rate (e.g., 0.05)
    mde: Minimum detectable effect (e.g., 0.1 for 10% lift)
    alpha: Significance level
    power: Statistical power
    """
    effect_size = baseline_rate * mde
    z_alpha = stats.norm.ppf(1 - alpha / 2)
    z_beta = stats.norm.ppf(power)

    p = baseline_rate
    p_new = p + effect_size

    n = (2 * p * (1 - p) * (z_alpha + z_beta) ** 2) / (effect_size ** 2)

    return int(np.ceil(n))


def analyze_ab_test(control, treatment, alpha=0.05):
    """
    Analyze A/B test results

    control: array of 0/1 outcomes for control
    treatment: array of 0/1 outcomes for treatment
    """
    n_control = len(control)
    n_treatment = len(treatment)

    p_control = control.mean()
    p_treatment = treatment.mean()

    # Pooled proportion
    p_pool = (control.sum() + treatment.sum()) / (n_control + n_treatment)

    # Standard error
    se = np.sqrt(p_pool * (1 - p_pool) * (1/n_control + 1/n_treatment))

    # Z-statistic
    z = (p_treatment - p_control) / se

    # P-value (two-tailed)
    p_value = 2 * (1 - stats.norm.cdf(abs(z)))

    # Confidence interval
    ci_low = (p_treatment - p_control) - 1.96 * se
    ci_high = (p_treatment - p_control) + 1.96 * se

    return {
        'control_rate': p_control,
        'treatment_rate': p_treatment,
        'lift': (p_treatment - p_control) / p_control,
        'z_statistic': z,
        'p_value': p_value,
        'significant': p_value < alpha,
        'confidence_interval': (ci_low, ci_high)
    }
```

## Statistical Analysis

### Hypothesis Testing

```python
from scipy import stats

# T-test
def compare_means(group1, group2):
    stat, p_value = stats.ttest_ind(group1, group2)
    effect_size = (group1.mean() - group2.mean()) / np.sqrt(
        (group1.std()**2 + group2.std()**2) / 2
    )
    return {'t_statistic': stat, 'p_value': p_value, 'cohens_d': effect_size}

# Chi-square
def test_independence(contingency_table):
    chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
    return {'chi2': chi2, 'p_value': p_value, 'degrees_of_freedom': dof}

# Correlation
def analyze_correlation(x, y):
    pearson_r, pearson_p = stats.pearsonr(x, y)
    spearman_r, spearman_p = stats.spearmanr(x, y)
    return {
        'pearson': {'r': pearson_r, 'p_value': pearson_p},
        'spearman': {'r': spearman_r, 'p_value': spearman_p}
    }
```

## Project Template

```markdown
# Data Science Project: [Name]

## Business Objective
[What business problem are we solving?]

## Success Metrics
- Primary: [Metric]
- Secondary: [Metric]

## Data
- Sources: [List]
- Size: [Rows/Features]
- Time period: [Dates]

## Methodology
1. [Step 1]
2. [Step 2]

## Results

### Model Performance
| Metric | Value |
|--------|-------|
| [Metric] | [Value] |

### Business Impact
- [Impact 1]
- [Impact 2]

## Recommendations
1. [Recommendation]

## Next Steps
- [Next step]

## Appendix
[Technical details]
```

## Reference Materials

- `references/ml_algorithms.md` - Algorithm deep dives
- `references/feature_engineering.md` - Feature engineering patterns
- `references/experimentation.md` - A/B testing guide
- `references/statistics.md` - Statistical methods

## Scripts

```bash
# Model trainer
python scripts/train_model.py --config model_config.yaml

# Feature importance analyzer
python scripts/feature_importance.py --model model.pkl --data test.csv

# A/B test analyzer
python scripts/ab_analyzer.py --control control.csv --treatment treatment.csv

# Model evaluator
python scripts/evaluate_model.py --model model.pkl --test test.csv
```
