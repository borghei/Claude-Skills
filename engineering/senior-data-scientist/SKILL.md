---
name: senior-data-scientist
description: >
  Experiment sizing, feature profiling with leakage checks, and model evaluation from saved
  predictions, plus causal-inference workflows. Use when sizing an A/B test, vetting features,
  or scoring a model before release.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: data-science
  updated: 2026-11-08
  tags: [data-science, ml, statistics, experimentation, python, mlops]
---
# Senior Data Scientist

Expert data science for statistical modeling, experimentation, ML deployment, and data-driven decision making — A/B test design and analysis, feature engineering, model training/evaluation, production deployment, and causal inference.

## Keywords

data-science, machine-learning, statistics, a-b-testing, causal-inference,
feature-engineering, mlops, experiment-design, model-deployment, python,
scikit-learn, pytorch, tensorflow, spark, airflow

## Core Capabilities

- **Experiment design & analysis** — hypothesis framing, power analysis and sample sizing, randomization, SRM monitoring, and post-hoc significance testing.
- **Feature engineering** — profiling, candidate generation (temporal/aggregation/interaction/text), selection (variance, correlation, SHAP/RFE), and leakage validation.
- **Model training & evaluation** — stratified/temporal splits, baselines, hyperparameter tuning, cross-validation, calibration, and fairness checks.
- **Production deployment** — containerized serving, input/output drift monitoring (KS/PSI), canary rollouts, and latency/error SLAs.
- **Causal inference** — propensity score matching, difference-in-differences, regression discontinuity, instrumental variables, and assumption/placebo testing.

## When to Use

- Designing or analyzing an A/B test.
- Building a feature engineering pipeline.
- Training, evaluating, or deploying an ML model.
- Estimating treatment effects from observational data.

## Clarify First

Before running an analysis or pipeline, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Task:** A/B test design / feature engineering / model evaluation / causal inference (selects the script and workflow).
- **Dataset & target variable:** what you are modeling or measuring (drives feature generation and leakage validation).
- **Decision metric & minimum effect:** the metric and the smallest effect worth detecting (drives power analysis and sample size).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Tools

Three standard-library Python tools. Each takes `--format text|json`, prints a sample input with `--example`, and writes a JSON file only when you pass `--output DIR` (it will not overwrite an existing one without `--force`). Sample inputs live in `assets/`.

| Script | Purpose | Example |
|--------|---------|---------|
| `scripts/experiment_designer.py` | Per-arm sample size, power and test duration for a two-proportion or difference-in-means A/B test, with Bonferroni adjustment for extra arms and warnings for underpowered or very long designs | `python scripts/experiment_designer.py --baseline 0.10 --mde 0.02 --daily-traffic 5000` |
| `scripts/feature_engineering_pipeline.py` | Profiles a CSV (types, nulls, cardinality, quantiles, skew), flags constant, ID-like and highly correlated columns, scores features against a target, flags leakage suspects, and drafts a keep/transform/drop plan | `python scripts/feature_engineering_pipeline.py --input assets/customers_sample.csv --target churned` |
| `scripts/model_evaluation_suite.py` | Scores saved predictions: classification (confusion matrix, precision, recall, F1, ROC AUC, log loss, Brier) or regression (MAE, RMSE, R², MAPE), side by side, with a fold stability check and pass/fail against thresholds | `python scripts/model_evaluation_suite.py --input assets/predictions_sample.csv --folds 5 --config assets/eval_thresholds.json` |

Exit codes: `0` the run completed (a NOT READY verdict or an underpowered warning is still exit 0; read the verdict); `2` bad input (missing or malformed file, unknown column, invalid value, existing output without `--force`).

> For hypothesis testing, causal inference, and regression analysis, use inline scipy/statsmodels — see [references/statistical_methods_advanced.md](references/statistical_methods_advanced.md).

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/ds-workflows.md](references/ds-workflows.md)** — quick-start commands, tech stack, the five end-to-end workflows (A/B testing, feature pipeline, train/evaluate, deploy, causal inference) with Python snippets, performance targets, and common commands. Read when executing any data-science task.
- **[references/ds-operations.md](references/ds-operations.md)** — troubleshooting table, success criteria, and the full CLI flag reference for each script. Read when diagnosing issues or running the tools.
- **[references/statistical_methods_advanced.md](references/statistical_methods_advanced.md)** — advanced statistical methods reference (hypothesis testing, causal inference, regression). Read for statistical depth.
- **[references/experiment_design_frameworks.md](references/experiment_design_frameworks.md)** — experiment design frameworks and power-analysis foundations. Read when designing rigorous experiments.
- **[references/feature_engineering_patterns.md](references/feature_engineering_patterns.md)** — feature engineering patterns and selection techniques. Read when building features.

## Scope & Limitations

**This skill covers:**
- End-to-end experiment design including power analysis, randomization, and post-hoc analysis
- Feature engineering pipelines with profiling, generation, selection, and validation
- Model training evaluation including cross-validation, calibration, and fairness checks
- Production model deployment with monitoring, drift detection, and canary rollouts

**What the tools do and do not do:**
- `experiment_designer.py` sizes a test with the normal approximation. It does not analyze results, check for sample ratio mismatch, or size tests for ratio metrics, CUPED or sequential designs. Below a 1% baseline treat its numbers as a lower bound.
- `feature_engineering_pipeline.py` profiles and recommends. It does not generate or write transformed features, and its leakage check is statistical (|association| of 0.90 or more with the target), so a leak that is only weakly correlated still needs a timing review.
- `model_evaluation_suite.py` evaluates predictions you already have. It does not train or retrain models, so its fold check shows how stable a metric is across subsets of the same predictions, not cross-validated generalization. Classification is binary only, and rows with a missing actual are skipped. Readiness verdicts use only the thresholds a model can be measured on; the others are listed as not applicable. Latency, error rate and drift need serving metrics; config keys for them are reported as ignored.
- Hypothesis tests on finished experiments and causal inference are done with inline scipy/statsmodels, as in the workflows.

**This skill does NOT cover:**
- Data engineering infrastructure (ETL orchestration, pipeline scheduling, data lake management) -- see `senior-data-engineer`
- Deep learning model architecture design and training at scale (distributed GPU training, custom layers) -- see `senior-ml-engineer`
- Prompt engineering, RAG systems, and LLM fine-tuning workflows -- see `senior-prompt-engineer`
- Computer vision pipelines (object detection, segmentation, video processing) -- see `senior-computer-vision`

## Integration Points

| Skill | Use for |
|-------|---------|
| `senior-data-engineer` | Upstream data pipelines and data-quality checks |
| `senior-ml-engineer` | Serving, monitoring and retraining after evaluation |

## Anti-Patterns

### Peeking and Stopping Early
**Mistake:** Checking an A/B test daily and stopping the first time p < 0.05.
**Why it happens:** Early wins are exciting and traffic is expensive.
**Instead:** Fix the sample size with `experiment_designer.py` before launch and analyse once it is reached, or use a sequential design built for interim looks. Repeated peeking inflates the false-positive rate far above the nominal 5%.

### Features That Know the Answer
**Mistake:** Training on columns recorded after the outcome (refund issued, account closed date).
**Why it happens:** They correlate strongly, so models built on them look excellent offline.
**Instead:** Check every feature's timestamp against the prediction time. `feature_engineering_pipeline.py` flags statistical suspects; the timing review is still yours.

### One Metric on One Split
**Mistake:** Shipping on a single AUC from one random split.
**Why it happens:** It is the default output of most tutorials.
**Instead:** Evaluate on a temporal holdout that mirrors production, report calibration and the business threshold metrics, and check stability across folds (`--folds`).

## Files

| File | Purpose |
|------|---------|
| `scripts/experiment_designer.py` | Sample size, power and duration for two-arm or multi-arm tests |
| `scripts/feature_engineering_pipeline.py` | CSV profiling, leakage suspects and a keep/transform/drop plan |
| `scripts/model_evaluation_suite.py` | Classification/regression metrics, fold stability, readiness verdict |
| `assets/customers_sample.csv` | Features with a planted leak (`refund_issued`) and a duplicate column |
| `assets/predictions_sample.csv`, `regression_sample.csv` | Saved predictions for the evaluation suite |
| `assets/eval_thresholds.json`, `experiment_design.json` | Threshold config and experiment input |
| `references/*.md` | Workflows, operations and CLI reference, statistics, experiment design, feature patterns |
