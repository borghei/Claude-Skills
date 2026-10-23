# Troubleshooting, Success Criteria & Tool Reference

Read this when diagnosing experiment/model/pipeline problems, defining the quality bar, or needing full CLI flag references for the data-science scripts.

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Sample size calculation returns unreasonably large numbers | Minimum detectable effect (MDE) is set too small relative to baseline variance | Increase MDE to a practically meaningful threshold or accept longer experiment duration |
| Feature profile shows high null rates across many columns | Source data contains upstream ingestion gaps or schema drift | Validate raw data completeness before running the pipeline; check ETL logs for failed loads |
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

All three tools use the Python standard library only, make no network calls, and are deterministic. Run them from the skill folder. Each prints a sample input with `--example`, prints JSON with `--format json`, and writes a JSON file only when given `--output DIR`. If that file already exists the tool stops with an error before doing any work, unless you pass `--force`. A missing or unreadable input file, a CSV row whose field count differs from the header (the error names the line), a missing column or an invalid value gives a one-line `ERROR:` message and exit code 1 (argparse usage errors exit 2). A successful run exits 0, whatever the verdict.

### experiment_designer.py

**Purpose:** Size an A/B test. For a two-proportion test (conversion-style metric) or a difference in means, it computes the per-arm sample size for the target power, the power a fixed sample size buys, the total sample, and the test duration from daily traffic. It uses the normal approximation with the inverse normal from `statistics.NormalDist`. With more than two arms each treatment is compared with control and alpha is Bonferroni-adjusted. Numeric fields must be finite numbers, and `std_dev`, `daily_traffic`, `sample_size` and `variants` must be positive; a bad value is rejected with an error that names the field. A design whose sample size is too large to compute (an MDE near zero) is rejected the same way. It warns when a design is underpowered, needs more than 28 days, needs less than 7 days, or has a baseline rate below 1%.

**Usage:**
```bash
python scripts/experiment_designer.py --baseline 0.10 --mde 0.02
python scripts/experiment_designer.py --input assets/experiment_design.json
python scripts/experiment_designer.py --metric mean --baseline 42 --std-dev 30 --mde 0.05 --mde-type relative --daily-traffic 8000
```

**Flags/Parameters:**

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--input` | `-i` | none | Design JSON file (see `--example`). Flags given on the command line override its values |
| `--metric` | | `proportion` | `proportion` (two-proportion test) or `mean` (difference in means) |
| `--baseline` | | required | Control conversion rate (0 to 1) or control mean |
| `--mde` | | required | Minimum detectable effect |
| `--mde-type` | | `absolute` | `absolute` (0.02 means 2 percentage points) or `relative` (0.10 means +10% of baseline) |
| `--std-dev` | | none | Standard deviation of the metric. Required for `--metric mean` |
| `--alpha` | | `0.05` | Significance level |
| `--power` | | `0.80` | Target power |
| `--sides` | | `2` | `1` or `2`-sided test |
| `--variants` | | `2` | Number of arms including control. More than 2 triggers the Bonferroni adjustment |
| `--sample-size` | | none | Fixed per-arm size. The report then shows the power it buys |
| `--daily-traffic` | | none | Eligible units per day. Enables the duration estimate |
| `--allocation` | | `1.0` | Share of daily traffic entering the test |
| `--output` | `-o` | none | Directory to write `experiment_design.json` into |
| `--force` | | off | Overwrite an existing `experiment_design.json` in `--output` |
| `--format` | | `text` | `text` or `json` |
| `--example` | | | Print a sample design JSON and exit |

**Hand check:** baseline 10%, MDE 2 points absolute, alpha 0.05 two-sided, power 0.80 gives 3,841 per arm, the textbook pooled-variance answer. Baseline 5% with a 10% relative lift gives 31,234 per arm.

**Example output** (`--input assets/experiment_design.json`, three arms at 20,000 visitors a day with 50% allocation):
```text
Experiment design - checkout-button-color
  Metric:             proportion (two-sided)
  Baseline rate:      0.05
  Treatment rate:     0.055 (effect +0.005, +10.0% relative)
  Alpha / power:      0.05 / 0.8 (alpha per comparison 0.025)
  Arms:               3 (2 vs control)
  Required per arm:   37,824 (unadjusted 31,234)
  Planned per arm:    37,824 -> power 80.0%
  Total sample:       113,472
  Duration:           12 day(s) (1.7 weeks) at 20,000/day x 50% allocation
  WARNING: Bonferroni: 2 comparisons against control, so each is tested at alpha 0.0250. Per-arm size rises from 31,234 to 37,824.
```

---

### feature_engineering_pipeline.py

**Purpose:** Profile a CSV and draft a feature plan. For each column it infers the type (numeric, binary, datetime, categorical), measures null rate and cardinality, and for numeric columns reports min, max, mean, standard deviation, the 5th to 95th percentiles and skew. It flags constant and near-constant columns (95% or more one value), ID-like columns (nearly all values unique, or unique consecutive integers), and numeric pairs whose Pearson |r| reaches `--corr-threshold`. With `--target` it scores each feature against the target (Pearson r for numeric and binary features, the correlation ratio eta for categorical ones) and flags any feature at 0.90 or above as a leakage suspect. Each column ends with an action (keep, transform, drop) and the reasons: log1p for right skew, one-hot up to `--max-onehot` levels and out-of-fold target encoding above it, impute plus a missing indicator for nulls, date part extraction for datetimes, and dropping constants, ID-like columns, columns over 95% null, and the weaker member of a redundant pair. Null tokens are empty, `NA`, `N/A`, `null`, `None` and `NaN`. Values so large that their statistics overflow are rejected with an error asking you to rescale them.

**Usage:**
```bash
python scripts/feature_engineering_pipeline.py --input assets/customers_sample.csv
python scripts/feature_engineering_pipeline.py --input assets/customers_sample.csv --target churned --output features/
```

**Flags/Parameters:**

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--input` | `-i` | required | CSV file with a header row |
| `--target` | `-t` | none | Target column. Enables target association and leakage checks. A text target needs exactly two classes |
| `--corr-threshold` | | `0.95` | Flag numeric pairs whose absolute Pearson r is at or above this |
| `--max-onehot` | | `10` | One-hot encode categoricals with up to this many levels; target-encode above it |
| `--output` | `-o` | none | Directory to write `feature_plan.json` (full profile, pairs, target section and plan) into |
| `--force` | | off | Overwrite an existing `feature_plan.json` in `--output` |
| `--format` | | `text` | `text` or `json` |
| `--example` | | | Print a small sample CSV and exit |

**Example output** (`--input assets/customers_sample.csv --target churned`, 60 synthetic customers with a planted leak, `refund_issued`, and a redundant column, `annual_spend` = 12 x `monthly_spend`):
```text
Feature profile: assets/customers_sample.csv (60 rows, 12 columns)

  column            type         null% distinct  summary
  customer_id       categorical     0%       60  top 'C1000' 2%
  signup_date       datetime        0%       60  2025-01-01 to 2025-12-24
  plan              categorical     0%        3  top 'basic' 47%
  country           categorical     0%        6  top 'ES' 20%
  age               numeric        23%       30  min 19, p50 47.5, max 69, mean 44.3, sd 13.83, skew -0.13
  tenure_months     numeric         0%       34  min 2, p50 30.5, max 48, mean 27.38, sd 12.66, skew -0.44
  monthly_spend     numeric         0%       60  min 3.67, p50 57.58, max 157.9, mean 61.38, sd 37.63, skew +0.74
  annual_spend      numeric         0%       60  min 44.04, p50 690.9, max 1895, mean 736.5, sd 451.6, skew +0.74
  support_tickets   numeric         0%        6  min 0, p50 1.5, max 8, mean 2.267, sd 2.401, skew +1.23
  region            categorical     0%        1  top 'EU' 100%
  refund_issued     binary          0%        2  top '0' 75%
  churned           binary          0%        2  top '0' 75%

Correlated pairs (|r| >= 0.95):
  monthly_spend ~ annual_spend  r = 1.0

Association with target 'churned':
  refund_issued     r = +1.000
  support_tickets   r = +0.529
  country           eta = +0.315
  tenure_months     r = -0.245
  age               r = +0.095
  plan              eta = +0.093
  monthly_spend     r = -0.059
  annual_spend      r = -0.059
  Leakage suspects: refund_issued

Feature plan:
  customer_id       drop      ID-like: nearly every value is unique
  signup_date       transform extract day-of-week, month and recency; drop the raw date
  plan              transform one-hot encode
  country           transform one-hot encode
  age               transform impute (median or mode) and add a was-missing indicator
  tenure_months     keep      
  monthly_spend     keep      
  annual_spend      drop      redundant with monthly_spend (r = 1.0)
  support_tickets   transform log1p transform (right skew)
  region            drop      constant
  refund_issued     drop      leakage suspect: |association| >= 0.9 with target. confirm it is known before the outcome
  churned           target    
```

---

### model_evaluation_suite.py

**Purpose:** Evaluate predictions you already have. The input CSV holds an actual column and one or more prediction columns. Rows with a missing actual (empty, `NA`, `null` and similar) are skipped and counted in the report, never treated as a class. A target with only one distinct value is rejected, because no metric can be computed from it. For binary classification each prediction column is read as hard labels (only 0 and 1), probabilities (all values in 0 to 1) or raw scores (anything else). Labels and probabilities get a confusion matrix, accuracy, precision, recall, F1 and specificity (probabilities are cut at `--threshold`). Probabilities and scores get ROC AUC by the rank method, with tied scores given average ranks. Probabilities also get log loss and Brier score. Regression gets MAE, RMSE, R², MAPE (rows where the actual is zero are skipped and counted) and bias. Models are shown side by side and the best one is named by its primary metric (AUC, F1 for label-only columns, RMSE for regression). `--folds k` deals the rows round-robin into k folds and reports the primary metric's mean and standard deviation, which shows how stable the metric is across subsets. It is not retraining cross-validation. A readiness verdict compares each model with thresholds from `--config`. Without a config, classification uses `min_auc` 0.85 and `max_brier` 0.15 from the success criteria above, and regression has no default thresholds.

**Usage:**
```bash
python scripts/model_evaluation_suite.py --input assets/predictions_sample.csv
python scripts/model_evaluation_suite.py --input assets/predictions_sample.csv --target actual --folds 5 --config assets/eval_thresholds.json
python scripts/model_evaluation_suite.py --input assets/regression_sample.csv --task regression
```

**Flags/Parameters:**

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--input` | `-i` | required | CSV with an actual column and prediction columns |
| `--target` | `-t` | `actual` | Actual or label column |
| `--predictions` | `-p` | every other usable column | Comma-separated prediction columns. Without it, every non-target column is tried; columns with missing or non-numeric values are skipped and named with the reason in the report (`skipped_columns`). If none is usable, the tool stops and names each column and its problem. With it, a listed column that has missing or non-numeric values is an error. A numeric ID column would be scored as a model, so list the columns explicitly when the file has one |
| `--task` | | `auto` | `classification`, `regression`, or `auto` (classification when the target has exactly two values) |
| `--positive` | | `1`, else the last sorted label | Positive class label |
| `--threshold` | | `0.5` | Probability cut-off for predicted labels |
| `--folds` | `-k` | `0` (off) | Number of round-robin folds for the stability check |
| `--config` | `-c` | built-in | Thresholds JSON. Keys: `min_accuracy`, `min_precision`, `min_recall`, `min_f1`, `min_auc`, `max_log_loss`, `max_brier`, `min_r2`, `max_rmse`, `max_mae`, `max_mape`, `max_fold_std`. Other keys, such as a latency limit, are listed as ignored because predictions cannot show them |
| `--output` | `-o` | none | Directory to write `evaluation_report.json` into |
| `--force` | | off | Overwrite an existing `evaluation_report.json` in `--output` |
| `--format` | | `text` | `text` or `json` |
| `--example` | | | Print a small sample predictions CSV and exit |

A threshold on a metric the model does not have (AUC or Brier for a label-only column, or `max_fold_std` without `--folds`) is listed as not applicable rather than failed. The verdict uses only the measurable checks: READY when they all pass, NOT READY when any fails, and NO VERDICT when none can be measured. With the default config a label-only column therefore gets NO VERDICT; add a label metric such as `min_f1` or `min_recall` to judge it.

**Hand check:** ten rows with actuals 1,1,1,1,0,0,0,0,0,0 and probabilities 0.9, 0.8, 0.4, 0.6, 0.7, 0.3, 0.2, 0.1, 0.55, 0.05 give TP 3, FP 2, FN 1, TN 4, so accuracy 0.70, precision 0.60, recall 0.75 and F1 0.6667. 21 of the 24 positive-negative pairs are ordered correctly, so AUC is 0.875. The tool reports exactly these values, plus log loss 0.4495 and Brier 0.1505.

**Example output** (`--input assets/predictions_sample.csv --folds 5 --config assets/eval_thresholds.json`, two probability models and a rule that emits hard labels):
```text
Model evaluation: assets/predictions_sample.csv (80 rows, classification, positive class '1')

  metric                    gbm_v2     logreg_v1    rules_flag
  kind                 probability   probability         label
  accuracy                  0.8625        0.8000        0.7500
  precision                 0.8077        0.7037        0.6842
  recall                    0.7778        0.7037        0.4815
  f1                        0.7925        0.7037        0.5652
  specificity               0.9057        0.8491        0.8868
  auc                       0.9672        0.8588           n/a
  log_loss                  0.2930        0.4473           n/a
  brier                     0.0840        0.1429           n/a

  gbm_v2 confusion (threshold 0.5): TP 21  FP 5  FN 6  TN 48
  gbm_v2 5-fold auc: mean 0.9698, std 0.0330 (0.979, 0.937, 1.000, 1.000, 0.933)

  logreg_v1 confusion (threshold 0.5): TP 19  FP 8  FN 8  TN 45
  logreg_v1 5-fold auc: mean 0.8746, std 0.0722 (0.812, 0.794, 0.958, 0.875, 0.933)

  rules_flag confusion (threshold 0.5): TP 13  FP 6  FN 14  TN 47
  rules_flag 5-fold f1: mean 0.5526, std 0.1912 (0.286, 0.500, 0.750, 0.500, 0.727)

  Skipped: 'id' has non-numeric values

Best by primary metric: gbm_v2

Readiness (offline thresholds):
  gbm_v2       READY       min_auc 0.9672 vs 0.85 PASS, min_recall 0.7778 vs 0.7 PASS, max_brier 0.0840 vs 0.15 PASS, max_fold_std 0.0330 vs 0.08 PASS
  logreg_v1    READY       min_auc 0.8588 vs 0.85 PASS, min_recall 0.7037 vs 0.7 PASS, max_brier 0.1429 vs 0.15 PASS, max_fold_std 0.0722 vs 0.08 PASS
  rules_flag   NOT READY   min_recall 0.4815 vs 0.7 FAIL, max_fold_std 0.1912 vs 0.08 FAIL; not applicable: min_auc, max_brier
  Ignored (not measurable from predictions): max_latency_ms
  Verdicts use only the checks a model can be measured on. Offline check only: latency, error rate and drift need serving metrics.
```

Regression (`--input assets/regression_sample.csv`):
```text
Model evaluation: assets/regression_sample.csv (12 rows, regression)

  metric                     ridge        forest
  kind                  regression    regression
  mae                      16.5000        7.8333
  rmse                     18.7661        8.2765
  r2                        0.9823        0.9966
  mape                      0.0526        0.0266
  mape_rows_skipped              1             1
  bias                      2.6667       -2.5000

  Skipped: 'id' has non-numeric values

Best by primary metric: forest

Readiness (offline thresholds):
  ridge        NO VERDICT  no thresholds set (pass --config)
  forest       NO VERDICT  no thresholds set (pass --config)
  Verdicts use only the checks a model can be measured on. Offline check only: latency, error rate and drift need serving metrics.
```

> **Note:** This skill has no standalone statistics tool. Run individual tests with inline Python (scipy, statsmodels), as in Workflow 1 and Workflow 5, or with `run_test.py` in `data-analytics/statistical-analyst/`.
