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
python scripts/experiment_tracker.py log --name "xgb_v2" --params '{"lr":0.1,"depth":6}' --metrics '{"f1":0.87,"auc":0.92}'
python scripts/experiment_tracker.py list --sort-by f1 --top 5
python scripts/experiment_tracker.py compare --ids 1 3 5 --json
python scripts/hypothesis_tester.py ttest --file data.csv --col-a group_a --col-b group_b
python scripts/hypothesis_tester.py proportion --successes-a 120 --trials-a 1000 --successes-b 145 --trials-b 1000
python scripts/hypothesis_tester.py chi-square --file contingency.csv --json
python scripts/feature_selector.py --file dataset.csv --target churn --top 10
python scripts/feature_selector.py --file dataset.csv --target revenue --method correlation --json
```

## Tool Reference

| Tool | Purpose | Key Flags |
|------|---------|-----------|
| `experiment_tracker.py` | Log, list, and compare experiments with parameters, metrics, and tags in a local JSON file | `log --name --params --metrics --tags`, `list --sort-by --top`, `compare --ids`, `--json` |
| `hypothesis_tester.py` | Run statistical tests: Welch's t-test, paired t-test, proportion z-test, chi-square independence | `ttest --file --col-a --col-b [--paired]`, `proportion --successes-a --trials-a ...`, `chi-square --file`, `--json` |
| `feature_selector.py` | Rank features by composite score (variance, correlation, mutual information, null rate) for a target column | `--file <csv>`, `--target <col>`, `--top <n>`, `--method all/correlation/mutual_info`, `--json` |

## Troubleshooting

| Problem | Likely Cause | Resolution |
|---------|-------------|------------|
| Model overfits (large train-test gap in metrics) | Too many features, insufficient regularization, or data leakage | Reduce feature count with `feature_selector.py`, add regularization, and audit feature engineering for temporal leakage |
| A/B test shows significant result but tiny effect size | Large sample size makes small differences statistically significant | Always report effect size (Cohen's d) alongside p-value; use practical significance thresholds |
| `hypothesis_tester.py` p-value differs from scipy | The tool uses normal/t-distribution approximations (standard library only) | For publication-grade analysis, validate with scipy.stats; the tool is designed for fast directional estimates |
| Feature importance scores are near-zero for all features | Target variable has extremely low variance or the feature set lacks predictive signal | Check target distribution; consider feature engineering or collecting additional data sources |
| `experiment_tracker.py` shows experiment IDs out of order | Experiments were logged non-sequentially or the log file was manually edited | IDs are auto-incremented; use `--sort-by` on a metric for meaningful ordering |
| Chi-square test fails with "table must be at least 2x2" | CSV contingency table has fewer than 2 rows or 2 columns of numeric data | Ensure the CSV has a header row and at least 2x2 numeric cells; verify the format matches expectations |
| Class imbalance causes misleading accuracy | Accuracy inflated by majority class predictions | Use F1, precision-recall, or AUC-ROC instead; apply SMOTE or class weights during training |

## Success Criteria

- Every ML project follows the Define-Collect-Engineer-Train-Evaluate-Communicate workflow before deployment.
- Feature selection is documented: `feature_selector.py` output is saved with the experiment record.
- All experiments are tracked with `experiment_tracker.py` including parameters, metrics, and a descriptive name.
- Model evaluation reports include at least 3 metrics (e.g., F1, AUC-ROC, precision) and comparison against a baseline.
- A/B tests pre-register the hypothesis, sample size calculation, and primary metric before data collection begins.
- Statistical tests report effect size and confidence intervals, not just p-values.
- Business impact is quantified in dollar terms or user-metric terms (e.g., "reduces false positives by 30%, saving $500K/yr").

## Scope & Limitations

**In scope:** Machine learning algorithm selection, feature engineering, model training and evaluation, A/B test design and analysis, statistical hypothesis testing, experiment tracking, and communicating results to stakeholders.

**Out of scope:** Model deployment to production (see ml-ops-engineer), data pipeline infrastructure, dashboard development, and real-time serving architecture.

**Limitations:** The Python tools use only the Python standard library. `hypothesis_tester.py` uses normal and t-distribution approximations that are accurate for moderate sample sizes but should be validated with scipy for edge cases (very small n, extreme skew). `feature_selector.py` computes approximate mutual information using binned discretization -- for high-precision feature selection, use sklearn's mutual_info_classif or permutation importance. All tools process local files and do not integrate with MLflow, W&B, or other tracking platforms.

## Integration Points

- **MLOps Engineer** (`data-analytics/ml-ops-engineer`): Trained models are handed off for production deployment, monitoring, and registry management.
- **Data Analyst** (`data-analytics/data-analyst`): Complex analytical questions requiring predictive modeling are escalated from the analyst to the data scientist.
- **Analytics Engineer** (`data-analytics/analytics-engineer`): Feature engineering pipelines may depend on mart models as upstream data sources.
- **Product Team** (`product-team/`): Experiment results inform product decisions; A/B test designs are co-created with product managers.
- **Engineering** (`engineering/senior-ml-engineer`): Algorithm implementation details and model architecture decisions bridge data science and ML engineering.
