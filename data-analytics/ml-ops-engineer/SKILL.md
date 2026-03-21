---
name: ml-ops-engineer
description: >
  Expert MLOps engineering covering model deployment, ML pipelines, model
  monitoring, feature stores, and infrastructure automation. Use when deploying
  models to production, building training pipelines, setting up drift detection,
  configuring feature stores, or automating ML CI/CD workflows.
version: 1.0.0
author: borghei
category: data-analytics
tags: [mlops, deployment, pipelines, monitoring, feature-store]
---

# MLOps Engineer

The agent operates as a senior MLOps engineer, deploying models to production, orchestrating training pipelines, monitoring model health, managing feature stores, and automating ML CI/CD.

## Workflow

1. **Assess ML maturity** -- Determine the current level (manual notebooks vs. automated pipelines vs. full CI/CD). Identify the highest-impact gap to close first.
2. **Build or extend training pipeline** -- Define fetch-data, validate, preprocess, train, evaluate stages. Use Kubeflow, Airflow, or equivalent. Gate deployment on an accuracy threshold (e.g., > 0.85).
3. **Deploy model for serving** -- Choose real-time (FastAPI + K8s) or batch (Spark/Parquet) based on latency requirements. Configure health checks, autoscaling, and resource limits.
4. **Register in model registry** -- Log parameters, metrics, and artifacts in MLflow. Transition the winning version to Production stage; archive the previous version.
5. **Instrument monitoring** -- Set up latency (P50/P95/P99), error rate, prediction-distribution, and feature-drift dashboards. Configure alerting thresholds.
6. **Validate end-to-end** -- Run smoke tests against the serving endpoint. Confirm monitoring dashboards populate. Verify rollback procedure works.

## MLOps Maturity Model

| Level | Capabilities | Key signals |
|-------|-------------|------------|
| 0 - Manual | Jupyter notebooks, manual deploy | No version control on models |
| 1 - Pipeline | Automated training, versioned models | MLflow tracking in use |
| 2 - CI/CD | Continuous training, automated tests | Feature store operational |
| 3 - Full MLOps | Auto-retraining on drift, A/B testing | SLA-backed monitoring |

## Real-Time Serving Example

```python
# model_server.py -- FastAPI model serving
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mlflow.pyfunc, time

app = FastAPI()
model = mlflow.pyfunc.load_model("models:/fraud_detector/Production")

class PredictionRequest(BaseModel):
    features: list[float]

class PredictionResponse(BaseModel):
    prediction: float
    model_version: str
    latency_ms: float

@app.post("/predict", response_model=PredictionResponse)
async def predict(req: PredictionRequest):
    start = time.time()
    try:
        pred = model.predict([req.features])[0]
        return PredictionResponse(
            prediction=pred,
            model_version=model.metadata.run_id,
            latency_ms=(time.time() - start) * 1000,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy", "model_loaded": model is not None}
```

## Kubernetes Deployment

```yaml
# k8s/model-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: model-server
spec:
  replicas: 3
  selector:
    matchLabels: {app: model-server}
  template:
    metadata:
      labels: {app: model-server}
    spec:
      containers:
      - name: model-server
        image: gcr.io/project/model-server:v1.2.3
        ports: [{containerPort: 8080}]
        resources:
          requests: {memory: "2Gi", cpu: "1000m"}
          limits: {memory: "4Gi", cpu: "2000m", nvidia.com/gpu: 1}
        env:
        - {name: MODEL_URI, value: "s3://models/production/v1.2.3"}
        readinessProbe:
          httpGet: {path: /health, port: 8080}
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: model-server-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: model-server
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target: {type: Utilization, averageUtilization: 70}
```

## Drift Detection

```python
# monitoring/drift_detector.py
import numpy as np
from scipy import stats
from dataclasses import dataclass

@dataclass
class DriftResult:
    feature: str
    drift_score: float
    is_drifted: bool
    p_value: float

def detect_drift(reference: np.ndarray, current: np.ndarray, threshold: float = 0.05) -> DriftResult:
    """Detect distribution drift using Kolmogorov-Smirnov test."""
    statistic, p_value = stats.ks_2samp(reference, current)
    return DriftResult(feature="", drift_score=statistic, is_drifted=p_value < threshold, p_value=p_value)

def monitor_all_features(reference: dict, current: dict, threshold: float = 0.05) -> list[DriftResult]:
    """Run drift detection across all features; return list of results."""
    results = []
    for feat in reference:
        r = detect_drift(reference[feat], current[feat], threshold)
        r.feature = feat
        results.append(r)
    return results
```

## Alert Rules

```python
ALERT_RULES = {
    "latency_p99":    {"threshold": 200,  "severity": "warning",  "msg": "P99 latency exceeded 200 ms"},
    "error_rate":     {"threshold": 0.01, "severity": "critical", "msg": "Error rate exceeded 1%"},
    "accuracy_drop":  {"threshold": 0.05, "severity": "critical", "msg": "Accuracy dropped > 5%"},
    "drift_score":    {"threshold": 0.15, "severity": "warning",  "msg": "Feature drift detected"},
}
```

## Feature Store (Feast)

```python
# features/customer_features.py
from feast import Entity, Feature, FeatureView, FileSource, ValueType
from datetime import timedelta

customer = Entity(name="customer_id", value_type=ValueType.INT64)

customer_stats = FeatureView(
    name="customer_stats",
    entities=["customer_id"],
    ttl=timedelta(days=1),
    features=[
        Feature(name="total_purchases",       dtype=ValueType.FLOAT),
        Feature(name="avg_order_value",        dtype=ValueType.FLOAT),
        Feature(name="days_since_last_order",  dtype=ValueType.INT32),
        Feature(name="lifetime_value",         dtype=ValueType.FLOAT),
    ],
    online=True,
    source=FileSource(
        path="gs://features/customer_stats.parquet",
        timestamp_field="event_timestamp",
    ),
)
```

**Online retrieval at serving time:**
```python
from feast import FeatureStore
store = FeatureStore(repo_path=".")
features = store.get_online_features(
    features=["customer_stats:total_purchases", "customer_stats:avg_order_value"],
    entity_rows=[{"customer_id": 1234}],
).to_dict()
```

## Experiment Tracking (MLflow)

```python
import mlflow

mlflow.set_tracking_uri("http://mlflow.company.com")
mlflow.set_experiment("fraud_detection")

with mlflow.start_run(run_name="xgboost_v2"):
    mlflow.log_params({"n_estimators": 100, "max_depth": 6, "learning_rate": 0.1})
    model = train_model(X_train, y_train)
    mlflow.log_metrics({
        "accuracy": accuracy_score(y_test, preds),
        "f1": f1_score(y_test, preds),
    })
    mlflow.sklearn.log_model(model, "model", registered_model_name="fraud_detector")
```

For extended pipeline examples (Kubeflow, Airflow DAGs, full CI/CD workflows), see `REFERENCE.md`.

## Reference Materials

- `REFERENCE.md` -- Extended patterns: Kubeflow pipelines, Airflow DAGs, CI/CD workflows, model registry operations
- `references/deployment_patterns.md` -- Model deployment strategies
- `references/monitoring_guide.md` -- ML monitoring best practices
- `references/feature_store.md` -- Feature store patterns
- `references/pipeline_design.md` -- ML pipeline architecture

## Scripts

```bash
python scripts/model_registry.py register --name fraud_detector --version v2.3 --metrics '{"f1":0.91,"auc":0.95}' --params '{"n_estimators":200}'
python scripts/model_registry.py promote --name fraud_detector --version v2.3 --stage production
python scripts/model_registry.py list --stage production --json
python scripts/model_registry.py compare --name fraud_detector --versions v2.2 v2.3
python scripts/drift_detector.py --reference train_data.csv --current prod_data.csv
python scripts/drift_detector.py --reference baseline.csv --current latest.csv --threshold 0.1 --json
python scripts/pipeline_validator.py --pipeline pipeline.json --strict
python scripts/pipeline_validator.py --pipeline pipeline.json --json
```

## Tool Reference

| Tool | Purpose | Key Flags |
|------|---------|-----------|
| `model_registry.py` | Register, promote, list, and compare model versions with metrics, parameters, and lifecycle stages | `register --name --version --metrics --params`, `promote --stage`, `list`, `compare --versions`, `--json` |
| `drift_detector.py` | Detect data/model drift between reference and current datasets using KS statistic, PSI, and chi-square | `--reference <csv>`, `--current <csv>`, `--columns`, `--threshold`, `--json` |
| `pipeline_validator.py` | Validate ML pipeline definitions for completeness, stage ordering, evaluation gates, and rollback config | `--pipeline <json>`, `--strict`, `--json` |

## Troubleshooting

| Problem | Likely Cause | Resolution |
|---------|-------------|------------|
| Model latency exceeds P99 SLA (> 200 ms) | Model is too large, input preprocessing is slow, or pod resources are undersized | Profile the serving endpoint; consider model distillation, input caching, or increasing CPU/memory limits |
| `drift_detector.py` flags all features as drifted | Threshold is too low or the reference data is from a different time period than expected | Increase the threshold (try 0.15-0.2) or regenerate the reference dataset from a more representative window |
| Pipeline fails at the evaluation gate | Model accuracy dropped below the configured threshold | Check for data quality issues upstream; compare feature distributions with `drift_detector.py`; retrain with fresh data |
| Model registry shows "already registered" error | The exact name + version combination was previously registered | Use a new version string (e.g., v2.3.1) or remove the old entry if it was a test |
| Kubernetes pods crash-loop on model server | OOM kill due to model size exceeding memory limits, or health check timeout too short | Increase `resources.limits.memory`; extend `initialDelaySeconds` on readiness probe for large models |
| Feature store returns stale features | Materialization job failed or ran outside the TTL window | Check materialization logs; re-run `materialize_features`; consider reducing TTL or adding freshness alerts |
| `pipeline_validator.py` reports STAGE_ORDER error | Pipeline stages are defined out of the expected sequence (data -> transform -> train -> evaluate -> deploy) | Reorder stages to follow the canonical sequence; the validator expects data stages before training stages |

## Success Criteria

- All production models are registered in the model registry with version, metrics, and parameters before serving traffic.
- Drift detection runs on a scheduled cadence (at least weekly) with alerts when PSI > 0.2 or KS > 0.15.
- ML pipelines pass `pipeline_validator.py --strict` with zero errors before deployment.
- Model serving latency stays within SLA: P50 < 50 ms, P95 < 100 ms, P99 < 200 ms.
- Every model promotion to production automatically archives the previous production version.
- Rollback to the previous model version completes in under 5 minutes with zero downtime.
- Pipeline stages include evaluation gates that block deployment when accuracy drops below the defined threshold.

## Scope & Limitations

**In scope:** Model deployment (real-time and batch), ML pipeline orchestration, model registry management, drift detection (data drift, concept drift, prediction drift), feature store patterns, monitoring and alerting, Kubernetes deployment configurations, and CI/CD for ML.

**Out of scope:** Model architecture design and algorithm selection (see data-scientist), raw data ingestion pipelines, BI dashboard development, and business strategy.

**Limitations:** The Python tools use only the Python standard library. `drift_detector.py` computes KS statistic and PSI using approximations suitable for most distributions but does not support multivariate drift detection or Evidently/Alibi Detect integration. `model_registry.py` stores state in a local JSON file -- for production use, integrate with MLflow Model Registry or a similar platform. `pipeline_validator.py` validates structure and conventions but does not execute pipeline stages.

## Integration Points

- **Data Scientist** (`data-analytics/data-scientist`): Receives trained models with experiment metadata; promotes winning experiments to the registry for deployment.
- **Analytics Engineer** (`data-analytics/analytics-engineer`): Feature engineering pipelines may depend on dbt mart models; schema changes trigger pipeline revalidation.
- **Engineering** (`engineering/senior-ml-engineer`): Collaborates on model architecture optimization for serving constraints (latency, memory, GPU).
- **Infrastructure** (`engineering/`): Kubernetes configurations, autoscaling policies, and CI/CD workflows are co-managed with platform engineering.
- **Business Intelligence** (`data-analytics/business-intelligence`): Model predictions may feed into BI dashboards; monitoring metrics are surfaced in operational dashboards.
