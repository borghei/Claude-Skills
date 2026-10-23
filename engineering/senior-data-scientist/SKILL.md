---
name: senior-data-scientist
description: >
  Use when the user asks to "design an experiment", "build a predictive model",
  "run A/B test analysis", "perform causal inference", "engineer features",
  "evaluate model performance", "set up MLOps pipeline", "analyze time series",
  "calculate sample size", or "deploy a model to production".
  Expert data science covering statistical modeling, experimentation, causal inference,
  feature engineering, ML deployment, and advanced analytics with Python, R, and SQL.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: data-science
  updated: 2026-06-17
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

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `senior-data-engineer` | Feature pipeline ingests data from ETL outputs; shares data quality validation patterns | Raw data stores --> feature engineering pipeline --> feature store |
| `senior-ml-engineer` | Trained models handed off for MLOps deployment; shares model registry and serving configs | Evaluated model artifacts --> deployment pipeline --> production serving |
| `senior-prompt-engineer` | Embedding features from LLMs feed into ML pipelines; experiment frameworks apply to prompt A/B tests | LLM embeddings --> feature vectors; experiment designs --> prompt evaluation |
| `senior-architect` | Model serving architecture reviewed for scalability; data platform design aligned with training infrastructure | Architecture specs --> deployment topology --> monitoring dashboards |
| `senior-backend` | Model inference endpoints integrated into backend services; API contracts defined for prediction requests | REST/gRPC model API --> backend service layer --> client applications |
| `senior-devops` | CI/CD pipelines extended for model retraining triggers; containerized model images deployed via infrastructure-as-code | Docker images --> Kubernetes manifests --> production clusters |
