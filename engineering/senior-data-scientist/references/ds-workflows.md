# Data Science Workflows

Read this when running an A/B test, building a feature pipeline, training/evaluating a model, deploying to production, or doing causal inference — includes the quick-start commands, tech stack, the five end-to-end workflows, performance targets, and common commands.

## Quick Start

Run these from the skill folder. Each command works on the sample inputs in `assets/`; swap in your own values or files.

```bash
# Size an A/B test: per-arm sample size, power and duration
python scripts/experiment_designer.py --baseline 0.10 --mde 0.02 --daily-traffic 5000
python scripts/experiment_designer.py --input assets/experiment_design.json --output results/

# Profile a dataset and draft a feature plan
python scripts/feature_engineering_pipeline.py --input assets/customers_sample.csv --target churned --output features/

# Compare saved model predictions and check them against thresholds
python scripts/model_evaluation_suite.py --input assets/predictions_sample.csv --folds 5 --config assets/eval_thresholds.json
```

A rerun into an `--output` folder that already holds the report stops with an error unless you add `--force`. Full flags and example output for each tool are in [ds-operations.md](ds-operations.md).

For a single statistical test, use inline Python (scipy, statsmodels) as in Workflows 1 and 5, or `run_test.py` in `data-analytics/statistical-analyst/` (Welch's t, Mann-Whitney, chi-square, two-proportion).

## Tech Stack

| Category | Tools |
|----------|-------|
| Languages | Python, SQL, R, Scala |
| ML Frameworks | PyTorch, TensorFlow, Scikit-learn, XGBoost |
| Data Processing | Spark, Airflow, dbt, Kafka, Databricks |
| Deployment | Docker, Kubernetes, AWS SageMaker, GCP Vertex AI |
| Experiment Tracking | MLflow, Weights & Biases |
| Databases | PostgreSQL, BigQuery, Snowflake, Pinecone |

## Workflow 1: Design and Analyze an A/B Test

1. **Define hypothesis** -- State the null and alternative hypotheses. Identify the primary metric (e.g., conversion rate, revenue per user).
2. **Calculate sample size** -- `python scripts/experiment_designer.py --baseline 0.05 --mde 0.10 --mde-type relative --daily-traffic 20000`
   - Specify minimum detectable effect (MDE), significance level (`--alpha`, default 0.05), and power (`--power`, default 0.80). Use `--metric mean --std-dev ...` for a revenue-style metric and `--variants 3` or more for multi-arm tests (alpha is Bonferroni-adjusted).
   - Example: for baseline conversion 5% and a 10% relative lift the tool returns 31,234 users per variant. With three arms the per-arm figure rises to 37,824.
   - Act on its warnings: an underpowered design, a test longer than 28 days, or one shorter than a full week.
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

1. **Profile raw data** -- `python scripts/feature_engineering_pipeline.py --input data.csv --target <target> --output features/`
   - Reports type, null rate, cardinality, quantiles and skew per column, highly correlated numeric pairs, and each feature's association with the target. `features/feature_plan.json` holds a keep/transform/drop decision per column.
2. **Generate candidate features:**
   - Temporal: day-of-week, hour, recency, frequency, monetary (RFM)
   - Aggregation: rolling means/sums over 7d/30d/90d windows
   - Interaction: ratio features, polynomial combinations
   - Text: TF-IDF, embedding vectors
3. **Select features** -- Remove features with >95% null rate, near-zero variance, or >0.95 pairwise correlation (the feature plan already marks these). Use recursive feature elimination or SHAP importance in your own training code.
4. **Validate** -- Confirm no target leakage (no features derived from post-outcome data). The profiler lists features with an association of 0.90 or more as leakage suspects; check when each suspect becomes known. Check train/test distribution alignment.
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
   To compare candidates without sklearn, save one prediction column per model next to the actuals and run `python scripts/model_evaluation_suite.py --input test_predictions.csv --target actual --folds 5 --config thresholds.json`. It reports the metrics side by side, the fold spread of the primary metric, and a READY or NOT READY verdict per model against the thresholds.
5. **Validate** -- Check calibration (predicted probabilities match observed rates; the evaluation suite's Brier score is a single-number check). Evaluate fairness metrics across protected groups. Confirm no overfitting (train vs test gap <5%).

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
5. **Validate** -- From serving metrics, confirm latency, error rate <0.1%, and that model outputs match the offline evaluation.

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

## Performance Targets

| Metric | Target |
|--------|--------|
| P50 latency | < 50ms |
| P95 latency | < 100ms |
| P99 latency | < 200ms |
| Throughput | > 1,000 req/s |
| Availability | 99.9% |
| Error rate | < 0.1% |

## Common Commands

These are commands for your own ML project (its tests, `train.py`, `evaluate.py`, deployment), not tools this skill ships:

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
