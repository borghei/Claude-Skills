---
name: senior-data-scientist
description: >-
  Use when the user asks to "design an experiment", "build a predictive model",
  "run A/B test analysis", "perform causal inference", "engineer features",
  "evaluate model performance", "set up MLOps pipeline", "analyze time series",
  "calculate sample size", or "deploy a model to production".
  Expert data science covering statistical modeling, experimentation, causal inference,
  feature engineering, ML deployment, and advanced analytics with Python, R, and SQL.
version: 1.0.0
author: borghei
category: engineering
tags: [data-science, ml, statistics, experimentation, python, mlops]
---

# Senior Data Scientist

Expert data science for statistical modeling, experimentation, ML deployment,
and data-driven decision making.

## Keywords

data-science, machine-learning, statistics, a-b-testing, causal-inference,
feature-engineering, mlops, experiment-design, model-deployment, python,
scikit-learn, pytorch, tensorflow, spark, airflow

---

## Quick Start

```bash
# Design an experiment with power analysis
python scripts/experiment_designer.py --input data/ --output results/

# Run feature engineering pipeline
python scripts/feature_engineering_pipeline.py --target project/ --analyze

# Evaluate model performance
python scripts/model_evaluation_suite.py --config config.yaml --deploy

# Statistical analysis
python scripts/statistical_analyzer.py --data input.csv --test ttest --output report.json
```

---

## Tools

| Script | Purpose |
|--------|---------|
| `scripts/experiment_designer.py` | A/B test design, power analysis, sample size calculation |
| `scripts/feature_engineering_pipeline.py` | Automated feature generation, correlation analysis, feature selection |
| `scripts/statistical_analyzer.py` | Hypothesis testing, causal inference, regression analysis |
| `scripts/model_evaluation_suite.py` | Model comparison, cross-validation, deployment readiness checks |

---

## Tech Stack

| Category | Tools |
|----------|-------|
| Languages | Python, SQL, R, Scala |
| ML Frameworks | PyTorch, TensorFlow, Scikit-learn, XGBoost |
| Data Processing | Spark, Airflow, dbt, Kafka, Databricks |
| Deployment | Docker, Kubernetes, AWS SageMaker, GCP Vertex AI |
| Experiment Tracking | MLflow, Weights & Biases |
| Databases | PostgreSQL, BigQuery, Snowflake, Pinecone |

---

## Workflow 1: Design and Analyze an A/B Test

1. **Define hypothesis** -- State the null and alternative hypotheses. Identify the primary metric (e.g., conversion rate, revenue per user).
2. **Calculate sample size** -- `python scripts/experiment_designer.py --input data/ --output results/`
   - Specify minimum detectable effect (MDE), significance level (alpha=0.05), and power (0.80).
   - Example: For baseline conversion 5%, MDE 10% relative lift, need ~31,000 users per variant.
3. **Randomize assignment** -- Use hash-based assignment on user ID for deterministic, reproducible splits.
4. **Run experiment** -- Monitor for sample ratio mismatch (SRM) daily. Flag if observed ratio deviates >1% from expected.
5. **Analyze results:**
   ```python
   from scipy import stats

   # Two-proportion z-test for conversion rates
   control_conv = control_successes / control_total
   treatment_conv = treatment_successes / treatment_total
   z_stat, p_value = stats.proportions_ztest(
       [treatment_successes, control_successes],
       [treatment_total, control_total],
       alternative='two-sided'
   )
   # Reject H0 if p_value < 0.05
   ```
6. **Validate** -- Check for novelty effects, Simpson's paradox across segments, and pre-experiment balance on covariates.

## Workflow 2: Build a Feature Engineering Pipeline

1. **Profile raw data** -- `python scripts/feature_engineering_pipeline.py --target project/ --analyze`
   - Identify null rates, cardinality, distributions, and data types.
2. **Generate candidate features:**
   - Temporal: day-of-week, hour, recency, frequency, monetary (RFM)
   - Aggregation: rolling means/sums over 7d/30d/90d windows
   - Interaction: ratio features, polynomial combinations
   - Text: TF-IDF, embedding vectors
3. **Select features** -- Remove features with >95% null rate, near-zero variance, or >0.95 pairwise correlation. Use recursive feature elimination or SHAP importance.
4. **Validate** -- Confirm no target leakage (no features derived from post-outcome data). Check train/test distribution alignment.
5. **Register** -- Store features in feature store with versioning and lineage metadata.

## Workflow 3: Train and Evaluate a Model

1. **Split data** -- Stratified train/validation/test split (70/15/15). For time series, use temporal split (no future leakage).
2. **Train baseline** -- Start with a simple model (logistic regression, gradient boosted trees) to establish a benchmark.
3. **Tune hyperparameters** -- Use Optuna or cross-validated grid search. Log all runs to MLflow.
4. **Evaluate on held-out test set:**
   ```python
   from sklearn.metrics import classification_report, roc_auc_score

   y_pred = model.predict(X_test)
   y_prob = model.predict_proba(X_test)[:, 1]

   print(classification_report(y_test, y_pred))
   print(f"AUC-ROC: {roc_auc_score(y_test, y_prob):.4f}")
   ```
5. **Validate** -- Check calibration (predicted probabilities match observed rates). Evaluate fairness metrics across protected groups. Confirm no overfitting (train vs test gap <5%).

## Workflow 4: Deploy a Model to Production

1. **Containerize** -- Package model with inference dependencies in Docker:
   ```bash
   docker build -t model-service:v1 .
   ```
2. **Set up serving** -- Deploy behind a REST API with health check, input validation, and structured error responses.
3. **Configure monitoring:**
   - Input drift: compare incoming feature distributions to training baseline (KS test, PSI)
   - Output drift: monitor prediction distribution shifts
   - Performance: track latency P50/P95/P99 targets (<50ms / <100ms / <200ms)
4. **Enable canary deployment** -- Route 5% traffic to new model, compare metrics against baseline for 24-48 hours.
5. **Validate** -- `python scripts/model_evaluation_suite.py --config config.yaml --deploy` confirms serving latency, error rate <0.1%, and model outputs match offline evaluation.

## Workflow 5: Perform Causal Inference

1. **Assess assignment mechanism** -- Determine if treatment was randomized (use experiment analysis) or observational (use causal methods below).
2. **Select method** based on data structure:
   - **Propensity Score Matching**: when treatment is binary, many covariates available
   - **Difference-in-Differences**: when pre/post data available for treatment and control groups
   - **Regression Discontinuity**: when treatment assigned by threshold on running variable
   - **Instrumental Variables**: when unobserved confounding present but valid instrument exists
3. **Check assumptions** -- Parallel trends (DiD), overlap/positivity (PSM), continuity (RDD).
4. **Estimate treatment effect** and compute confidence intervals.
5. **Validate** -- Run placebo tests (apply method to pre-treatment period, expect null effect). Sensitivity analysis for unobserved confounding.

---

## Performance Targets

| Metric | Target |
|--------|--------|
| P50 latency | < 50ms |
| P95 latency | < 100ms |
| P99 latency | < 200ms |
| Throughput | > 1,000 req/s |
| Availability | 99.9% |
| Error rate | < 0.1% |

---

## Common Commands

```bash
# Development
python -m pytest tests/ -v --cov
python -m black src/
python -m pylint src/

# Training
python scripts/train.py --config prod.yaml
python scripts/evaluate.py --model best.pth

# Deployment
docker build -t service:v1 .
kubectl apply -f k8s/
helm upgrade service ./charts/

# Monitoring
kubectl logs -f deployment/service
python scripts/health_check.py
```

---

## Reference Documentation

| Document | Path |
|----------|------|
| Statistical Methods | [references/statistical_methods_advanced.md](references/statistical_methods_advanced.md) |
| Experiment Design Frameworks | [references/experiment_design_frameworks.md](references/experiment_design_frameworks.md) |
| Feature Engineering Patterns | [references/feature_engineering_patterns.md](references/feature_engineering_patterns.md) |
| Automation Scripts | `scripts/` directory |

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Sample size calculation returns unreasonably large numbers | Minimum detectable effect (MDE) is set too small relative to baseline variance | Increase MDE to a practically meaningful threshold or accept longer experiment duration |
| Feature pipeline reports high null rates across all generated features | Source data contains upstream ingestion gaps or schema drift | Validate raw data completeness before running the pipeline; check ETL logs for failed loads |
| Model AUC drops significantly on validation vs. training set | Overfitting due to high-cardinality features or insufficient regularization | Apply stronger regularization, reduce feature set, or increase training data volume |
| Experiment shows significant results but large confidence intervals | Insufficient sample size or high metric variance | Extend experiment runtime, increase traffic allocation, or switch to a variance-reduction technique (CUPED) |
| Deployed model latency exceeds P95 targets | Model complexity too high for serving infrastructure or missing batching | Quantize the model, reduce input feature count, or enable request batching on the serving layer |
| Feature importance scores are unstable across cross-validation folds | Correlated features cause importance to shift between redundant predictors | Remove highly correlated features (>0.95) before training or use permutation importance with repeated runs |
| Causal inference estimates show implausible treatment effects | Violation of parallel trends assumption (DiD) or poor covariate overlap (PSM) | Run diagnostic tests (placebo checks, overlap histograms) and consider alternative identification strategies |

---

## Success Criteria

- **Model discrimination**: AUC-ROC above 0.85 on held-out test set for classification tasks
- **Calibration quality**: Brier score below 0.15; predicted probabilities within 5% of observed rates across decile bins
- **Feature coverage**: Feature importance analysis accounts for at least 90% of cumulative model importance
- **Experiment power**: All A/B tests designed with statistical power of 0.80 or higher at the specified MDE
- **Deployment readiness**: Model serving latency under 100ms at P95; error rate below 0.1%
- **Reproducibility**: All experiments and training runs logged with full parameter tracking; results reproducible from logged artifacts
- **Data quality**: Input feature pipelines maintain less than 2% null rate on critical features after imputation

---

## Scope & Limitations

**This skill covers:**
- End-to-end experiment design including power analysis, randomization, and post-hoc analysis
- Feature engineering pipelines with profiling, generation, selection, and validation
- Model training evaluation including cross-validation, calibration, and fairness checks
- Production model deployment with monitoring, drift detection, and canary rollouts

**This skill does NOT cover:**
- Data engineering infrastructure (ETL orchestration, pipeline scheduling, data lake management) -- see `senior-data-engineer`
- Deep learning model architecture design and training at scale (distributed GPU training, custom layers) -- see `senior-ml-engineer`
- Prompt engineering, RAG systems, and LLM fine-tuning workflows -- see `senior-prompt-engineer`
- Computer vision pipelines (object detection, segmentation, video processing) -- see `senior-computer-vision`

---

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `senior-data-engineer` | Feature pipeline ingests data from ETL outputs; shares data quality validation patterns | Raw data stores --> feature engineering pipeline --> feature store |
| `senior-ml-engineer` | Trained models handed off for MLOps deployment; shares model registry and serving configs | Evaluated model artifacts --> deployment pipeline --> production serving |
| `senior-prompt-engineer` | Embedding features from LLMs feed into ML pipelines; experiment frameworks apply to prompt A/B tests | LLM embeddings --> feature vectors; experiment designs --> prompt evaluation |
| `senior-architect` | Model serving architecture reviewed for scalability; data platform design aligned with training infrastructure | Architecture specs --> deployment topology --> monitoring dashboards |
| `senior-backend` | Model inference endpoints integrated into backend services; API contracts defined for prediction requests | REST/gRPC model API --> backend service layer --> client applications |
| `senior-devops` | CI/CD pipelines extended for model retraining triggers; containerized model images deployed via infrastructure-as-code | Docker images --> Kubernetes manifests --> production clusters |

---

## Tool Reference

### experiment_designer.py

**Purpose:** A/B test design, statistical power analysis, and sample size calculation. Validates experiment configuration and produces structured results with timestamps.

**Usage:**
```bash
python scripts/experiment_designer.py --input data/ --output results/
```

**Flags/Parameters:**

| Flag | Short | Required | Description |
|------|-------|----------|-------------|
| `--input` | `-i` | Yes | Input path (directory or file containing experiment data) |
| `--output` | `-o` | Yes | Output path (directory for results) |
| `--config` | `-c` | No | Path to configuration file (YAML or JSON) |
| `--verbose` | `-v` | No | Enable verbose (DEBUG-level) logging output |

**Example:**
```bash
python scripts/experiment_designer.py -i data/experiment_config/ -o results/power_analysis/ -c config.yaml -v
```

**Output Format:** JSON to stdout with the following structure:
```json
{
  "status": "completed",
  "start_time": "2026-03-21T10:00:00.000000",
  "processed_items": 0,
  "end_time": "2026-03-21T10:00:01.000000"
}
```

---

### feature_engineering_pipeline.py

**Purpose:** Automated feature generation, correlation analysis, and feature selection. Profiles raw data, generates candidate features, and validates for target leakage.

**Usage:**
```bash
python scripts/feature_engineering_pipeline.py --input data/ --output features/
```

**Flags/Parameters:**

| Flag | Short | Required | Description |
|------|-------|----------|-------------|
| `--input` | `-i` | Yes | Input path (directory or file containing raw data) |
| `--output` | `-o` | Yes | Output path (directory for generated features) |
| `--config` | `-c` | No | Path to configuration file (YAML or JSON) |
| `--verbose` | `-v` | No | Enable verbose (DEBUG-level) logging output |

**Example:**
```bash
python scripts/feature_engineering_pipeline.py -i data/raw/ -o features/v2/ -v
```

**Output Format:** JSON to stdout with the following structure:
```json
{
  "status": "completed",
  "start_time": "2026-03-21T10:00:00.000000",
  "processed_items": 0,
  "end_time": "2026-03-21T10:00:01.000000"
}
```

---

### model_evaluation_suite.py

**Purpose:** Model comparison, cross-validation, and deployment readiness checks. Validates serving latency, error rates, and confirms model outputs match offline evaluation.

**Usage:**
```bash
python scripts/model_evaluation_suite.py --input models/ --output evaluation/
```

**Flags/Parameters:**

| Flag | Short | Required | Description |
|------|-------|----------|-------------|
| `--input` | `-i` | Yes | Input path (directory or file containing model artifacts) |
| `--output` | `-o` | Yes | Output path (directory for evaluation results) |
| `--config` | `-c` | No | Path to configuration file (YAML or JSON) |
| `--verbose` | `-v` | No | Enable verbose (DEBUG-level) logging output |

**Example:**
```bash
python scripts/model_evaluation_suite.py -i models/xgb_v3/ -o evaluation/report/ -c prod_config.yaml
```

**Output Format:** JSON to stdout with the following structure:
```json
{
  "status": "completed",
  "start_time": "2026-03-21T10:00:00.000000",
  "processed_items": 0,
  "end_time": "2026-03-21T10:00:01.000000"
}
```

> **Note:** The Tools table references `scripts/statistical_analyzer.py` but this script does not yet exist in the repository. Statistical analysis workflows described in the SKILL.md can be performed using inline Python (scipy, statsmodels) as shown in Workflow 1 and Workflow 5.
