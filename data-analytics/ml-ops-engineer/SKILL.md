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
python scripts/deploy_model.py --model fraud_detector --version v2.3 --env prod
python scripts/drift_analyzer.py --model fraud_detector --window 7d
python scripts/materialize_features.py --feature-view customer_stats
python scripts/run_pipeline.py --pipeline training --params config.yaml
```
