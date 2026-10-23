# Troubleshooting, Success Criteria & Tool Reference

Read this when diagnosing experiment/model/pipeline problems, defining the quality bar, or needing full CLI flag references for the data-science scripts.

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

## Success Criteria

- **Model discrimination**: AUC-ROC above 0.85 on held-out test set for classification tasks
- **Calibration quality**: Brier score below 0.15; predicted probabilities within 5% of observed rates across decile bins
- **Feature coverage**: Feature importance analysis accounts for at least 90% of cumulative model importance
- **Experiment power**: All A/B tests designed with statistical power of 0.80 or higher at the specified MDE
- **Deployment readiness**: Model serving latency under 100ms at P95; error rate below 0.1%
- **Reproducibility**: All experiments and training runs logged with full parameter tracking; results reproducible from logged artifacts
- **Data quality**: Input feature pipelines maintain less than 2% null rate on critical features after imputation

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

> **Note:** This skill has no standalone statistics tool. Run individual tests with inline Python (scipy, statsmodels), as in Workflow 1 and Workflow 5, or with `run_test.py` in `data-analytics/statistical-analyst/`.
