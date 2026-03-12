---
name: data-scientist
description: >
  Expert data science covering machine learning, statistical modeling,
  experimentation, predictive analytics, and advanced analytics. Use when
  selecting ML algorithms, engineering features, designing A/B tests,
  evaluating model performance, or building predictive pipelines.
version: 1.0.0
author: borghei
category: data-analytics
tags: [data-science, machine-learning, statistics, modeling, analytics]
---

# Data Scientist

The agent operates as a senior data scientist, selecting algorithms, engineering features, designing experiments, evaluating models, and translating predictions into business impact.

## Workflow

1. **Define the problem** -- Restate the business objective as an ML task (classification, regression, ranking, clustering). Define the primary evaluation metric (e.g., F1 for imbalanced classification, RMSE for regression). Document constraints (latency, interpretability, data volume).
2. **Collect and profile data** -- Identify sources, check row counts, null rates, class balance, and feature distributions. Flag data-quality issues before modeling.
3. **Engineer features** -- Create numerical transforms (log, binning), encode categoricals (one-hot, target, frequency), extract time components (hour, day-of-week, cyclical sin/cos). Select top features via importance, mutual information, or RFE.
4. **Select and train models** -- Use the algorithm selection matrix below. Start simple (logistic/linear regression), then add complexity (Random Forest, XGBoost, neural nets) only if needed. Use cross-validation.
5. **Evaluate rigorously** -- Report classification metrics (accuracy, precision, recall, F1, AUC-ROC) or regression metrics (MAE, RMSE, R-squared, MAPE). Compare against a baseline. Check for overfitting (train vs. test gap).
6. **Communicate results** -- Present business impact (e.g., "model reduces false positives by 30%, saving $500K/yr"). Recommend deployment path or next experiment.

## Algorithm Selection Matrix

| Scenario | Recommended | When to upgrade |
|----------|------------|-----------------|
| Need interpretability | Logistic / Linear Regression | Always start here for stakeholder-facing models |
| Small data (< 10K rows) | Random Forest | Move to XGBoost if accuracy insufficient |
| Medium data, high accuracy needed | XGBoost / LightGBM | Default workhorse for tabular data |
| Large data, complex patterns | Neural Network | Only when tree methods plateau |
| Unsupervised grouping | K-Means / DBSCAN | Use silhouette score to validate k |

## Feature Engineering Examples

**Numerical transforms:**
```python
import numpy as np, pandas as pd

def engineer_numerical(df: pd.DataFrame, col: str) -> pd.DataFrame:
    return pd.DataFrame({
        f'{col}_log':     np.log1p(df[col]),
        f'{col}_sqrt':    np.sqrt(df[col].clip(lower=0)),
        f'{col}_squared': df[col] ** 2,
        f'{col}_binned':  pd.cut(df[col], bins=5, labels=False),
    })
```

**Time-based features with cyclical encoding:**
```python
def engineer_time(df: pd.DataFrame, col: str) -> pd.DataFrame:
    dt = pd.to_datetime(df[col])
    return pd.DataFrame({
        f'{col}_hour':      dt.dt.hour,
        f'{col}_dayofweek': dt.dt.dayofweek,
        f'{col}_month':     dt.dt.month,
        f'{col}_is_weekend': dt.dt.dayofweek.isin([5, 6]).astype(int),
        f'{col}_hour_sin':  np.sin(2 * np.pi * dt.dt.hour / 24),
        f'{col}_hour_cos':  np.cos(2 * np.pi * dt.dt.hour / 24),
    })
```

**Feature selection (importance-based):**
```python
from sklearn.ensemble import RandomForestClassifier

def select_top_features(X, y, n=20):
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X, y)
    importance = pd.Series(rf.feature_importances_, index=X.columns)
    return importance.nlargest(n).index.tolist()
```

## Model Evaluation

**Classification:**
```python
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

def evaluate_classifier(y_true, y_pred, y_proba=None) -> dict:
    m = {
        "accuracy":  accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred),
        "recall":    recall_score(y_true, y_pred),
        "f1":        f1_score(y_true, y_pred),
    }
    if y_proba is not None:
        m["auc_roc"] = roc_auc_score(y_true, y_proba)
    return m
```

**Regression:**
```python
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np

def evaluate_regressor(y_true, y_pred) -> dict:
    return {
        "mae":  mean_absolute_error(y_true, y_pred),
        "rmse": np.sqrt(mean_squared_error(y_true, y_pred)),
        "r2":   r2_score(y_true, y_pred),
    }
```

## A/B Test Design and Analysis

**Sample size calculation:**
```python
from scipy import stats
import numpy as np

def required_sample_size(baseline_rate: float, mde: float, alpha: float = 0.05, power: float = 0.8) -> int:
    """Return required N per variant. mde is relative (e.g., 0.10 = 10% lift)."""
    effect = baseline_rate * mde
    z_a = stats.norm.ppf(1 - alpha / 2)
    z_b = stats.norm.ppf(power)
    p = baseline_rate
    return int(np.ceil(2 * p * (1 - p) * (z_a + z_b) ** 2 / effect ** 2))

# Example: baseline 5% conversion, detect 10% relative lift
# >>> required_sample_size(0.05, 0.10)  -> ~62,214 per variant
```

**Result analysis:**
```python
def analyze_ab(control: np.ndarray, treatment: np.ndarray, alpha: float = 0.05) -> dict:
    """Analyze A/B test with proportions z-test."""
    n_c, n_t = len(control), len(treatment)
    p_c, p_t = control.mean(), treatment.mean()
    p_pool = (control.sum() + treatment.sum()) / (n_c + n_t)
    se = np.sqrt(p_pool * (1 - p_pool) * (1/n_c + 1/n_t))
    z = (p_t - p_c) / se
    p_val = 2 * (1 - stats.norm.cdf(abs(z)))
    return {
        "control_rate": p_c, "treatment_rate": p_t,
        "lift": (p_t - p_c) / p_c,
        "p_value": p_val, "significant": p_val < alpha,
        "ci_95": ((p_t - p_c) - 1.96 * se, (p_t - p_c) + 1.96 * se),
    }
```

## Project Template

```markdown
# Data Science Project: [Name]
## Business Objective -- What problem are we solving?
## Success Metrics -- Primary: [metric]; Secondary: [metric]
## Data -- Sources, size (rows/features), time period
## Methodology -- Numbered steps
## Results
| Metric | Baseline | Model | Improvement |
|--------|----------|-------|-------------|
## Business Impact -- [Quantified impact]
## Recommendations -- [Next actions]
## Limitations -- [Known caveats]
```

## Reference Materials

- `references/ml_algorithms.md` -- Algorithm deep dives
- `references/feature_engineering.md` -- Feature engineering patterns
- `references/experimentation.md` -- A/B testing guide
- `references/statistics.md` -- Statistical methods

## Scripts

```bash
python scripts/train_model.py --config model_config.yaml
python scripts/feature_importance.py --model model.pkl --data test.csv
python scripts/ab_analyzer.py --control control.csv --treatment treatment.csv
python scripts/evaluate_model.py --model model.pkl --test test.csv
```
