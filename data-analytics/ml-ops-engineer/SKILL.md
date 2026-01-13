---
name: ml-ops-engineer
description: Expert MLOps engineering covering model deployment, ML pipelines, model monitoring, feature stores, and infrastructure automation.
version: 1.0.0
author: Claude Skills
category: data-analytics
tags: [mlops, deployment, pipelines, monitoring, feature-store]
---

# MLOps Engineer

Expert-level MLOps for production machine learning systems.

## Core Competencies

- Model deployment
- ML pipeline orchestration
- Model monitoring
- Feature engineering
- Infrastructure automation
- Experiment tracking
- Model versioning
- A/B testing

## MLOps Architecture

### ML Platform Stack

```
┌─────────────────────────────────────────────────────────────────┐
│                        SERVING LAYER                             │
│  API Gateway → Load Balancer → Model Servers → Cache            │
├─────────────────────────────────────────────────────────────────┤
│                      DEPLOYMENT LAYER                            │
│  CI/CD → Container Registry → Kubernetes → Canary/A-B           │
├─────────────────────────────────────────────────────────────────┤
│                       TRAINING LAYER                             │
│  Experiment Tracking → Model Registry → Training Pipelines      │
├─────────────────────────────────────────────────────────────────┤
│                        DATA LAYER                                │
│  Feature Store → Data Validation → Training Data → Batch/Stream │
├─────────────────────────────────────────────────────────────────┤
│                     INFRASTRUCTURE                               │
│  GPU Clusters → Object Storage → Metadata Store → Monitoring    │
└─────────────────────────────────────────────────────────────────┘
```

### MLOps Maturity Model

```
LEVEL 0: Manual ML
├── Jupyter notebooks
├── Manual deployment
└── No monitoring

LEVEL 1: ML Pipeline Automation
├── Automated training
├── Versioned models
└── Basic monitoring

LEVEL 2: CI/CD for ML
├── Continuous training
├── Automated testing
└── Feature store

LEVEL 3: Full MLOps
├── Automated retraining
├── A/B testing
└── Advanced monitoring
```

## Model Deployment

### Deployment Patterns

**Real-time Serving:**
```python
# FastAPI model server
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mlflow.pyfunc

app = FastAPI()

# Load model at startup
model = mlflow.pyfunc.load_model("models:/production-model/Production")

class PredictionRequest(BaseModel):
    features: list[float]

class PredictionResponse(BaseModel):
    prediction: float
    model_version: str
    latency_ms: float

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    import time
    start = time.time()

    try:
        prediction = model.predict([request.features])[0]
        latency = (time.time() - start) * 1000

        return PredictionResponse(
            prediction=prediction,
            model_version=model.metadata.run_id,
            latency_ms=latency
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy", "model_loaded": model is not None}
```

**Batch Inference:**
```python
# Batch prediction pipeline
import pandas as pd
from datetime import datetime

def batch_predict(
    model_uri: str,
    input_path: str,
    output_path: str,
    batch_size: int = 10000
):
    """
    Run batch predictions on large datasets
    """
    import mlflow.pyfunc

    model = mlflow.pyfunc.load_model(model_uri)

    # Process in chunks
    chunks = pd.read_csv(input_path, chunksize=batch_size)
    results = []

    for i, chunk in enumerate(chunks):
        predictions = model.predict(chunk)
        chunk['prediction'] = predictions
        chunk['predicted_at'] = datetime.utcnow()
        chunk['model_version'] = model_uri
        results.append(chunk)

        print(f"Processed batch {i+1}: {len(chunk)} records")

    # Save results
    output_df = pd.concat(results)
    output_df.to_parquet(output_path)

    return len(output_df)
```

### Kubernetes Deployment

```yaml
# k8s/model-deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: model-server
  labels:
    app: model-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: model-server
  template:
    metadata:
      labels:
        app: model-server
    spec:
      containers:
      - name: model-server
        image: gcr.io/project/model-server:v1.2.3
        ports:
        - containerPort: 8080
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
            nvidia.com/gpu: 1
        env:
        - name: MODEL_URI
          value: "s3://models/production/v1.2.3"
        - name: WORKERS
          value: "4"
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 60
          periodSeconds: 30
---
apiVersion: v1
kind: Service
metadata:
  name: model-server-service
spec:
  selector:
    app: model-server
  ports:
  - port: 80
    targetPort: 8080
  type: LoadBalancer
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
      target:
        type: Utilization
        averageUtilization: 70
```

## ML Pipelines

### Training Pipeline (Kubeflow)

```python
# pipelines/training_pipeline.py

from kfp import dsl
from kfp.dsl import Dataset, Model, Metrics

@dsl.component
def fetch_data(
    data_path: str,
    output_dataset: dsl.Output[Dataset]
):
    import pandas as pd
    df = pd.read_parquet(data_path)
    df.to_parquet(output_dataset.path)

@dsl.component
def preprocess(
    input_dataset: dsl.Input[Dataset],
    output_dataset: dsl.Output[Dataset]
):
    import pandas as pd
    df = pd.read_parquet(input_dataset.path)
    # Preprocessing logic
    df_processed = preprocess_features(df)
    df_processed.to_parquet(output_dataset.path)

@dsl.component
def train_model(
    input_dataset: dsl.Input[Dataset],
    hyperparameters: dict,
    output_model: dsl.Output[Model],
    metrics: dsl.Output[Metrics]
):
    import pandas as pd
    import xgboost as xgb
    import mlflow

    df = pd.read_parquet(input_dataset.path)
    X = df.drop('target', axis=1)
    y = df['target']

    model = xgb.XGBClassifier(**hyperparameters)
    model.fit(X, y)

    # Log metrics
    metrics.log_metric('accuracy', model.score(X, y))

    # Save model
    model.save_model(output_model.path)

@dsl.component
def evaluate_model(
    model: dsl.Input[Model],
    test_data: dsl.Input[Dataset],
    metrics: dsl.Output[Metrics]
) -> bool:
    import pandas as pd
    import xgboost as xgb

    model = xgb.XGBClassifier()
    model.load_model(model.path)

    df = pd.read_parquet(test_data.path)
    X = df.drop('target', axis=1)
    y = df['target']

    accuracy = model.score(X, y)
    metrics.log_metric('test_accuracy', accuracy)

    return accuracy > 0.85  # Threshold for deployment

@dsl.pipeline(name='training-pipeline')
def training_pipeline(
    data_path: str,
    hyperparameters: dict
):
    fetch_task = fetch_data(data_path=data_path)
    preprocess_task = preprocess(input_dataset=fetch_task.output)
    train_task = train_model(
        input_dataset=preprocess_task.output,
        hyperparameters=hyperparameters
    )
    evaluate_task = evaluate_model(
        model=train_task.outputs['output_model'],
        test_data=preprocess_task.output
    )
```

### Airflow DAG

```python
# dags/ml_training_dag.py

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'mlops',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'ml_training_pipeline',
    default_args=default_args,
    schedule_interval='0 2 * * *',  # Daily at 2 AM
    catchup=False
) as dag:

    fetch_data = KubernetesPodOperator(
        task_id='fetch_data',
        name='fetch-data',
        namespace='ml-pipelines',
        image='gcr.io/project/data-fetcher:latest',
        arguments=['--date', '{{ ds }}'],
    )

    validate_data = KubernetesPodOperator(
        task_id='validate_data',
        name='validate-data',
        namespace='ml-pipelines',
        image='gcr.io/project/data-validator:latest',
    )

    train_model = KubernetesPodOperator(
        task_id='train_model',
        name='train-model',
        namespace='ml-pipelines',
        image='gcr.io/project/model-trainer:latest',
        resources={
            'request_memory': '8Gi',
            'request_cpu': '4',
            'limit_gpu': '1'
        },
    )

    evaluate_model = KubernetesPodOperator(
        task_id='evaluate_model',
        name='evaluate-model',
        namespace='ml-pipelines',
        image='gcr.io/project/model-evaluator:latest',
    )

    deploy_model = KubernetesPodOperator(
        task_id='deploy_model',
        name='deploy-model',
        namespace='ml-pipelines',
        image='gcr.io/project/model-deployer:latest',
        trigger_rule='all_success',
    )

    fetch_data >> validate_data >> train_model >> evaluate_model >> deploy_model
```

## Feature Store

### Feast Configuration

```yaml
# feature_store.yaml

project: ml_platform
registry: gs://feature-store/registry.db
provider: gcp
online_store:
  type: redis
  connection_string: redis://10.0.0.1:6379
offline_store:
  type: bigquery
```

```python
# features/customer_features.py

from feast import Entity, Feature, FeatureView, FileSource, ValueType
from datetime import timedelta

# Entity definition
customer = Entity(
    name="customer_id",
    value_type=ValueType.INT64,
    description="Customer identifier"
)

# Feature source
customer_stats_source = FileSource(
    path="gs://features/customer_stats.parquet",
    timestamp_field="event_timestamp",
)

# Feature view
customer_stats = FeatureView(
    name="customer_stats",
    entities=["customer_id"],
    ttl=timedelta(days=1),
    features=[
        Feature(name="total_purchases", dtype=ValueType.FLOAT),
        Feature(name="avg_order_value", dtype=ValueType.FLOAT),
        Feature(name="days_since_last_order", dtype=ValueType.INT32),
        Feature(name="lifetime_value", dtype=ValueType.FLOAT),
    ],
    online=True,
    source=customer_stats_source,
)
```

### Feature Retrieval

```python
from feast import FeatureStore

store = FeatureStore(repo_path=".")

# Online serving
features = store.get_online_features(
    features=[
        "customer_stats:total_purchases",
        "customer_stats:avg_order_value",
        "customer_stats:lifetime_value",
    ],
    entity_rows=[
        {"customer_id": 1234},
        {"customer_id": 5678},
    ]
).to_dict()

# Historical features for training
training_df = store.get_historical_features(
    entity_df=entity_df,
    features=[
        "customer_stats:total_purchases",
        "customer_stats:avg_order_value",
    ]
).to_df()
```

## Model Monitoring

### Monitoring Dashboard

```
┌─────────────────────────────────────────────────────────────────┐
│                    MODEL MONITORING                              │
├─────────────────────────────────────────────────────────────────┤
│  Model: fraud_detector_v2.3    Status: ✓ Healthy                │
│  Deployed: 2024-01-15          Uptime: 99.97%                   │
├─────────────────────────────────────────────────────────────────┤
│  PERFORMANCE METRICS                                             │
│  Latency P50: 12ms    P95: 45ms    P99: 120ms                  │
│  Throughput: 1,250 req/s    Errors: 0.02%                       │
├─────────────────────────────────────────────────────────────────┤
│  MODEL QUALITY                                                   │
│  Accuracy: 94.2% (baseline: 93.5%)    ✓ Within threshold        │
│  Precision: 89.1%    Recall: 91.3%    F1: 90.2%                │
├─────────────────────────────────────────────────────────────────┤
│  DATA DRIFT                                                      │
│  Feature Drift Score: 0.08 (threshold: 0.15)    ✓ OK           │
│  Top Drifted: amount (-0.12), time_since_last (+0.09)          │
├─────────────────────────────────────────────────────────────────┤
│  PREDICTION DISTRIBUTION                                         │
│  [Histogram of prediction scores over time]                     │
└─────────────────────────────────────────────────────────────────┘
```

### Drift Detection

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

def detect_drift(
    reference: np.ndarray,
    current: np.ndarray,
    threshold: float = 0.05
) -> DriftResult:
    """
    Detect distribution drift using KS test
    """
    statistic, p_value = stats.ks_2samp(reference, current)

    return DriftResult(
        feature="",
        drift_score=statistic,
        is_drifted=p_value < threshold,
        p_value=p_value
    )

def monitor_features(
    reference_data: dict,
    current_data: dict,
    threshold: float = 0.05
) -> list[DriftResult]:
    """
    Monitor all features for drift
    """
    results = []

    for feature in reference_data.keys():
        result = detect_drift(
            reference_data[feature],
            current_data[feature],
            threshold
        )
        result.feature = feature
        results.append(result)

    return results
```

### Alerting

```python
# monitoring/alerts.py

from dataclasses import dataclass
from enum import Enum

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

@dataclass
class Alert:
    name: str
    severity: AlertSeverity
    message: str
    model_name: str
    metric_value: float
    threshold: float

ALERT_RULES = {
    "latency_p99": {
        "threshold": 200,  # ms
        "severity": AlertSeverity.WARNING,
        "message": "Model latency P99 exceeded threshold"
    },
    "error_rate": {
        "threshold": 0.01,  # 1%
        "severity": AlertSeverity.CRITICAL,
        "message": "Model error rate exceeded threshold"
    },
    "accuracy_drop": {
        "threshold": 0.05,  # 5% drop
        "severity": AlertSeverity.CRITICAL,
        "message": "Model accuracy dropped significantly"
    },
    "drift_score": {
        "threshold": 0.15,
        "severity": AlertSeverity.WARNING,
        "message": "Data drift detected"
    }
}

def evaluate_alerts(metrics: dict, model_name: str) -> list[Alert]:
    """
    Evaluate metrics against alert rules
    """
    alerts = []

    for metric_name, rule in ALERT_RULES.items():
        if metric_name in metrics:
            value = metrics[metric_name]
            if value > rule["threshold"]:
                alerts.append(Alert(
                    name=metric_name,
                    severity=rule["severity"],
                    message=rule["message"],
                    model_name=model_name,
                    metric_value=value,
                    threshold=rule["threshold"]
                ))

    return alerts
```

## Experiment Tracking

### MLflow Integration

```python
import mlflow
from mlflow.tracking import MlflowClient

# Set tracking server
mlflow.set_tracking_uri("http://mlflow.company.com")

# Start experiment
mlflow.set_experiment("fraud_detection")

with mlflow.start_run(run_name="xgboost_v2"):
    # Log parameters
    mlflow.log_params({
        "n_estimators": 100,
        "max_depth": 6,
        "learning_rate": 0.1
    })

    # Train model
    model = train_model(X_train, y_train)

    # Log metrics
    mlflow.log_metrics({
        "accuracy": accuracy_score(y_test, predictions),
        "precision": precision_score(y_test, predictions),
        "recall": recall_score(y_test, predictions),
        "f1": f1_score(y_test, predictions)
    })

    # Log model
    mlflow.sklearn.log_model(
        model,
        "model",
        registered_model_name="fraud_detector"
    )

    # Log artifacts
    mlflow.log_artifact("feature_importance.png")
    mlflow.log_artifact("confusion_matrix.png")
```

### Model Registry

```python
from mlflow.tracking import MlflowClient

client = MlflowClient()

# Transition model to production
client.transition_model_version_stage(
    name="fraud_detector",
    version=3,
    stage="Production"
)

# Archive old version
client.transition_model_version_stage(
    name="fraud_detector",
    version=2,
    stage="Archived"
)

# Get production model
model_uri = "models:/fraud_detector/Production"
model = mlflow.pyfunc.load_model(model_uri)
```

## CI/CD for ML

### GitHub Actions

```yaml
# .github/workflows/ml-pipeline.yml

name: ML Pipeline

on:
  push:
    paths:
      - 'models/**'
      - 'features/**'
  schedule:
    - cron: '0 2 * * *'  # Daily retraining

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run unit tests
        run: pytest tests/unit

      - name: Run integration tests
        run: pytest tests/integration

      - name: Validate data schema
        run: python scripts/validate_schema.py

  train:
    needs: test
    runs-on: gpu-runner
    steps:
      - uses: actions/checkout@v3

      - name: Train model
        run: python scripts/train.py

      - name: Evaluate model
        run: python scripts/evaluate.py

      - name: Register model
        if: ${{ env.ACCURACY > 0.85 }}
        run: python scripts/register_model.py

  deploy:
    needs: train
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to staging
        run: python scripts/deploy.py --env staging

      - name: Run smoke tests
        run: python scripts/smoke_test.py

      - name: Deploy to production
        run: python scripts/deploy.py --env production
```

## Reference Materials

- `references/deployment_patterns.md` - Model deployment strategies
- `references/monitoring_guide.md` - ML monitoring best practices
- `references/feature_store.md` - Feature store patterns
- `references/pipeline_design.md` - ML pipeline architecture

## Scripts

```bash
# Model deployer
python scripts/deploy_model.py --model fraud_detector --version v2.3 --env prod

# Drift analyzer
python scripts/drift_analyzer.py --model fraud_detector --window 7d

# Feature materializer
python scripts/materialize_features.py --feature-view customer_stats

# Pipeline runner
python scripts/run_pipeline.py --pipeline training --params config.yaml
```
