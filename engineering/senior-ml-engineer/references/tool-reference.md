# Tool Reference

Read this when you need the full flag detail, input formats and output of the three ML engineering scripts. All three use the Python standard library only, make no network calls and are deterministic. Each one has `--example` to print a sample input and `--format text|json` for the report. Generated files are written only under `--output`, and existing files are never overwritten unless you pass `--force`.

Sample inputs live in `assets/`: `deployment_spec.json`, `rag_spec.json`, `monitoring_baseline.csv` and `monitoring_current.csv`. The outputs below are real runs on those files.

---

## model_deployment_pipeline.py

**Purpose:** Turns a model-service spec into deployment artifacts and checks the spec for common production mistakes.

**Usage:**

```bash
python scripts/model_deployment_pipeline.py --input assets/deployment_spec.json --output deploy/
python scripts/model_deployment_pipeline.py --example > my_spec.json
```

| Flag | Short | Required | Description |
|------|-------|----------|-------------|
| `--input` | `-i` | Yes | Model-service spec JSON |
| `--output` | `-o` | Yes | Directory to write the artifacts into |
| `--force` | | No | Overwrite files that already exist in `--output` |
| `--format` | | No | `text` (default) or `json` report |
| `--example` | | No | Print a sample spec and exit |

**Spec fields:** `name` and `model_file` are required. Optional: `framework` (sklearn, pytorch, tensorflow, onnx, xgboost, lightgbm, custom), `image`, `base_image`, `port` (default 8080), `replicas` (a number or `{"min", "max"}`), `resources` (`cpu_request`, `cpu_limit`, `memory_request`, `memory_limit`), `health` (`liveness_path`, `readiness_path`), `env`, `gpu`, `gpu_count`, `target_cpu_utilization` (default 70), `run_as_root`.

**Input validation:** every value that reaches a generated file is checked against a whitelist, and anything else stops the run with a one-line error before a file is written. `name` must be a Kubernetes name. `model_file` must be a relative path of letters, digits, `.`, `_`, `-` and `/` (no `..`, quotes or whitespace). `image` and `base_image` must be plain image references (`registry[:port]/repo[:tag][@sha256:digest]`, lowercase repository). Health paths must start with `/` and use only letters, digits, `.`, `_`, `-`, `~` and `/`. Resource values must be Kubernetes quantities such as `500m`, `2` or `1Gi`. Env names must match `[A-Za-z_][A-Za-z0-9_]*` and values must be strings or numbers. `port`, replica counts, `gpu_count` and `target_cpu_utilization` must be integers in range, `gpu` must be a boolean, and `replicas`, `resources`, `health` and `env` must have the right JSON type.

**Files written:**

| File | Contents |
|------|----------|
| `Dockerfile` | Pinned slim base (`python:3.11-slim`, or a CUDA runtime image when `gpu` is true), non-root user uid 10001, `HEALTHCHECK` that calls the liveness path with Python's urllib (slim images have no curl) |
| `k8s.yaml` | Deployment (rolling update with `maxUnavailable: 0`, startup, liveness and readiness probes, requests and limits, `runAsNonRoot`, no privilege escalation, all capabilities dropped), ClusterIP Service, and an `autoscaling/v2` HorizontalPodAutoscaler on CPU |
| `serve.py` | Standard-library HTTP stub: liveness returns 200 while the process is up, readiness returns 503 until the model file is loaded, `/predict` returns 501 until you implement it |
| `requirements.txt` | The framework packages to pin, commented out until you add the versions you trained with |

Environment variables are treated as secrets when a whole name segment (split on `_` or `-`) is PASSWORD, PASSWD, PWD, SECRET, TOKEN, APIKEY, CREDENTIAL or CREDENTIALS, or two adjacent segments form API_KEY, ACCESS_KEY, PRIVATE_KEY, SECRET_KEY, SIGNING_KEY or ENCRYPTION_KEY. So `HF_TOKEN` and `DB_PASSWORD` are secrets while `TOKENIZER_PATH` and `PRIMARY_KEYSPACE` are not. Secrets are mapped to a `secretKeyRef` on `<name>-secrets` (which you create), the report lists which variables were treated that way, and a literal value in the spec is dropped with a warning.

**Checks reported:** image or base image with an implicit or `latest` tag, `run_as_root` requested, privileged port below 1024, fewer than 2 minimum replicas, each missing request or limit, missing CPU request (the HPA needs it), liveness and readiness sharing a path, secret-looking env values, GPU requested for a CPU framework. Checks are advisory: the tool still writes the files and exits 0.

**Example output:**

```
Deployment artifacts for churn-classifier -> deploy
  wrote Dockerfile
  wrote k8s.yaml
  wrote requirements.txt
  wrote serve.py
Image registry.example.com/ml/churn-classifier:1.4.0 on python:3.11-slim, port 8080, replicas 2-6, gpu no
Checks (0 warnings):
  [INFO] treated as secrets (secretKeyRef churn-classifier-secrets): FEATURE_STORE_TOKEN
```

**Exit codes:** 0 success, 1 bad input or files already present without `--force`, 2 usage error.

---

## rag_system_builder.py

**Purpose:** Produces a rule-based RAG pipeline plan from a spec and explains every choice. It does not ingest documents or call any embedding model or vector store.

**Usage:**

```bash
python scripts/rag_system_builder.py --input assets/rag_spec.json --output rag-plan/
python scripts/rag_system_builder.py --input assets/rag_spec.json --format json
```

| Flag | Short | Required | Description |
|------|-------|----------|-------------|
| `--input` | `-i` | Yes | RAG spec JSON |
| `--output` | `-o` | No | Directory for `rag_config.json` and `pipeline_plan.md`; omit to print the plan only |
| `--force` | | No | Overwrite files that already exist in `--output` |
| `--format` | | No | `text` (default) or `json` report |
| `--example` | | No | Print a sample spec and exit |

**Spec fields:** `corpus.documents` is required. Optional: `corpus.avg_doc_tokens` (default 800), `corpus.doc_types` (one type name, a list of names with equal shares, or a map of name to positive share; types are text, markdown, html, pdf, code, legal, faq, scientific, chat, table), `queries_per_day`, `peak_to_average` (default 3), `latency_budget_ms` (retrieval stage, default 500), `embedding_dim` (default 768), `update_frequency` (realtime, hourly, daily, weekly, static), `exact_match_terms`, `context_tokens` (default 4000), `memory_budget_gb` (default 32). Counts, budgets and shares must be positive numbers and `exact_match_terms` a boolean; anything else is a one-line error.

**Rules applied:**

| Decision | Rule |
|----------|------|
| Chunking | One profile per document type (strategy, size, overlap). Documents no longer than 1.2 times the chunk size are embedded whole. Chunk count is estimated per type from its share of the corpus |
| Index | Under 50,000 vectors: flat exact search. Otherwise HNSW if its memory estimate plus 20% headroom fits the budget, then HNSW with int8 quantization, then IVF-PQ or a disk-based graph index. Memory is estimated from vector count and dimension, not from any vendor's pricing |
| Retrieval mode | Hybrid (BM25 plus dense with reciprocal rank fusion) when `exact_match_terms` is set or the corpus has code, legal or table content; dense otherwise |
| Reranking and top-k | Budget under 150 ms: no cross-encoder, top-k 5. Up to 400 ms: rerank 20 to 30 candidates down to 5. Above 400 ms: rerank 50 down to 8. Top-k is then capped so the chunks fit `context_tokens` |
| Scaling | Peak QPS = queries per day / 86,400 times `peak_to_average`. Under 50: one replica; under 500: replicas plus a query cache; above: shard and replicate |
| Evaluation | Golden set of sqrt(documents) queries, clamped to 50 to 500. Recall at the candidate depth and at top-k, MRR, nDCG, sampled context precision and faithfulness review, p95 latency against the budget, and three ablations |

**Example output:**

```
RAG plan for support-kb: ~492,000 chunks, peak 1.85 QPS
  chunk markdown   structure-aware on headings, 512 tokens / 64 overlap
  chunk pdf        recursive after layout extraction, 768 tokens / 96 overlap
  chunk faq        one question-answer pair per chunk, 256 tokens / 0 overlap
Index: HNSW {"M": 16, "ef_construction": 200}
  why: graph index fits in memory (1.94 GB of 16.0 GB with 20% headroom); best recall/latency tradeoff and supports incremental inserts
Retrieval: hybrid (BM25 + dense, reciprocal rank fusion, k=60); 50 candidates, rerank yes, top-k 7
  why: the spec says queries carry exact identifiers; BM25 catches exact tokens that embeddings blur
  note: budget allows reranking a wide candidate list, which usually gives the largest precision gain
  note: final top-k cut from 8 to 7 so chunks fit the 4000-token context budget
  note: pin the embedding model version; changing it means re-embedding everything into a new index
Scaling: single index replica is enough
Updates (daily): incremental batch: hash each document, re-chunk and re-embed only changed ones, delete removed ids
Evaluation: 347 golden queries; Recall@50 (retriever ceiling before rerank), Recall@7, MRR@7, nDCG@7
wrote rag-plan/rag_config.json
wrote rag-plan/pipeline_plan.md
```

`pipeline_plan.md` lists the nine pipeline stages (ingest, parse, chunk, embed, index, retrieve, rerank, assemble context, update) with the chosen settings, the chunking table with reasons, memory estimates and the evaluation plan. `rag_config.json` holds the same plan as data.

**Exit codes:** 0 success, 1 bad input or files already present without `--force`, 2 usage error.

---

## ml_monitoring_suite.py

**Purpose:** Compares a baseline CSV (training data or a stable production window) with a current CSV and reports data, prediction and performance drift.

**Usage:**

```bash
python scripts/ml_monitoring_suite.py \
  --baseline assets/monitoring_baseline.csv --current assets/monitoring_current.csv \
  --prediction-col prediction --label-col label --exclude customer_id \
  --model-name churn-classifier --output monitoring/
```

| Flag | Short | Required | Description |
|------|-------|----------|-------------|
| `--baseline` | `-b` | Yes | Reference CSV with a header row |
| `--current` | `-c` | Yes | CSV to compare against the baseline |
| `--prediction-col` | | No | Model output column; it is also checked for prediction drift like any feature |
| `--label-col` | | No | Ground-truth column; with `--prediction-col` it enables performance drift. Excluded from feature checks |
| `--exclude` | | No | Comma-separated columns to skip, such as ids and timestamps |
| `--bins` | | No | Quantile bins for numeric PSI (default 10) |
| `--config` | | No | JSON file that overrides thresholds; `--example` prints every key with its default |
| `--output` | `-o` | No | Directory for `drift_report.json` and `alert_rules.yaml` |
| `--model-name` | | No | Model label used in the alert rules (default `model`) |
| `--force` | | No | Overwrite files that already exist in `--output` |
| `--fail-on` | | No | `alert` (default), `warn` or `never`: the level that makes the tool exit 1 |
| `--format` | | No | `text` (default) or `json` report |
| `--example` | | No | Print the default threshold config and exit |

**What it computes per column:**

- **Type.** A column is numeric when every non-missing baseline value parses as a number and it has more than 10 distinct values (`categorical_max_unique`); otherwise it is categorical, so 0/1 flags and class predictions are treated as categories.
- **PSI.** Numeric columns use bin edges at the baseline quantiles. Categorical columns use the baseline's 20 most frequent values (`categorical_top_n`) plus two buckets: `__other__` for the rest of the baseline's values and `__unseen__` for values the baseline never had. That keeps PSI meaningful for high-cardinality columns: two columns with completely different values put everything in different buckets and give a large PSI (about 18 for fully disjoint data) instead of spreading over thousands of near-empty bins. Empty bins are smoothed to 0.0001. Defaults: WARN at 0.1, ALERT at 0.25. The report also gives `unseen_share` and up to 10 new categories.
- **ID-like columns.** A categorical column with more than `categorical_top_n` distinct values where at least 90% of baseline values are distinct (`id_like_unique_ratio`) is reported as `id-like`. Its distribution checks are skipped with a note, because ids differ between any two samples by design; only its missing rate is checked. Exclude such columns, or bucket them upstream if their distribution matters.
- **PSI noise floor.** With few rows PSI is inflated by sampling noise alone, by about (bins - 1) x (1/n_baseline + 1/n_current). When that floor is above half of `psi_warn` the column gets a note to use fewer bins or more rows before trusting its status.
- **KS (numeric only).** The two-sample Kolmogorov-Smirnov statistic D with an asymptotic p-value. KS raises WARN at D 0.1 and ALERT at D 0.2, but only when p is below 0.05. Below 50 rows on either side (`ks_min_samples`) the column gets a note that the p-value is approximate; at 5 rows per side it can differ from an exact test by up to about 0.18.
- **Missing rate.** WARN when the missing rate moves by 5 points, ALERT at 10 points. Empty, NA, N/A, NaN, null and None count as missing.
- **Performance.** Accuracy when the label is categorical (WARN on a 2-point drop, ALERT on 5), MAE when it is numeric (WARN on a 10% increase, ALERT on 25%).

A column's status is the worst of its checks. A column present in the baseline but absent from the current file is an ALERT. A column missing in every row of both files is reported with a note and stays OK. Columns named in `--exclude` (and the label column) are ignored entirely, even when they are absent from one file. The overall status is the worst of all columns and performance.

**CSV validation:** both files need a header row with unique column names and at least one data row. A row whose field count differs from the header (extra or missing fields) is rejected rather than skipped, because a misaligned row usually means a broken export whose values sit under the wrong columns. The run stops with one line naming the file and physical line, for example `error: current.csv line 3: 3 fields, header has 2`, and exits 2. Blank lines are ignored.

**Config validation:** the config must be a JSON object whose keys are those printed by `--example`; values must be non-negative numbers (integers for `bins`, `categorical_max_unique`, `categorical_top_n` and `ks_min_samples`), and each warn threshold must not exceed its alert threshold. `--model-name` must be 1 to 63 letters, digits, `.`, `_` or `-`. Any of these errors exits 2, never 1, so a CI gate cannot mistake a bad config for drift.

The reference tables elsewhere in this skill set the critical PSI at 0.2. To use that instead of the conventional 0.25, put `{"psi_alert": 0.2}` in a config file.

**Example output:**

```
Drift report: baseline 400 rows, current 400 rows
feature              type             PSI    KS D      KS p  miss chg  status
age                  numeric       0.0084  0.0400    0.9004    +0.000  OK
monthly_spend        numeric       0.4921  0.3025         0    +0.000  ALERT
tenure_months        numeric       0.0554  0.0761    0.2248    +0.102  ALERT
plan                 categorical   0.4130       -         -    +0.000  ALERT
region               categorical   0.0026       -         -    +0.000  OK
prediction           categorical   0.1913       -         -    +0.000  WARN
Performance: accuracy baseline 0.905 -> current 0.82  ALERT
Overall: ALERT (OK 2, WARN 1, ALERT 4)
wrote monitoring/drift_report.json
wrote monitoring/alert_rules.yaml
```

The sample current file was built with a higher spend distribution, a shifted plan mix, more missing tenure values and noisier predictions, so the flagged rows are the intended result. Running the baseline against itself gives PSI 0, KS D 0 and OK for every column.

**Alert rules:** `alert_rules.yaml` is a Prometheus-style rule group with rules only for flagged columns: PSI warning and critical rules when PSI or KS flagged the column, a missing-rate rule when the missing rate rose, and a performance rule when accuracy or MAE moved. The rules assume your serving stack exports gauges named `feature_psi`, `feature_missing_rate` and `model_accuracy` or `model_mae` with `model` and `feature` labels; rename them to match your metrics.

**Exit codes:** 0 when the overall status is below `--fail-on`, 1 when it reaches it (use this as a CI or scheduled-job gate), 2 for bad input such as a missing file, an empty CSV, a row with the wrong field count, an unknown column, an invalid config or an invalid model name.
