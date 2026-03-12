# MLOps Engineer -- Extended Reference

## Training Pipeline (Kubeflow)

```python
from kfp import dsl
from kfp.dsl import Dataset, Model, Metrics

@dsl.component
def fetch_data(data_path: str, output_dataset: dsl.Output[Dataset]):
    import pandas as pd
    df = pd.read_parquet(data_path)
    df.to_parquet(output_dataset.path)

@dsl.component
def preprocess(input_dataset: dsl.Input[Dataset], output_dataset: dsl.Output[Dataset]):
    import pandas as pd
    df = pd.read_parquet(input_dataset.path)
    df_processed = preprocess_features(df)
    df_processed.to_parquet(output_dataset.path)

@dsl.component
def train_model(
    input_dataset: dsl.Input[Dataset],
    hyperparameters: dict,
    output_model: dsl.Output[Model],
    metrics: dsl.Output[Metrics],
):
    import pandas as pd, xgboost as xgb, mlflow
    df = pd.read_parquet(input_dataset.path)
    X, y = df.drop('target', axis=1), df['target']
    model = xgb.XGBClassifier(**hyperparameters)
    model.fit(X, y)
    metrics.log_metric('accuracy', model.score(X, y))
    model.save_model(output_model.path)

@dsl.component
def evaluate_model(model: dsl.Input[Model], test_data: dsl.Input[Dataset], metrics: dsl.Output[Metrics]) -> bool:
    import pandas as pd, xgboost as xgb
    m = xgb.XGBClassifier()
    m.load_model(model.path)
    df = pd.read_parquet(test_data.path)
    accuracy = m.score(df.drop('target', axis=1), df['target'])
    metrics.log_metric('test_accuracy', accuracy)
    return accuracy > 0.85

@dsl.pipeline(name='training-pipeline')
def training_pipeline(data_path: str, hyperparameters: dict):
    fetch = fetch_data(data_path=data_path)
    prep = preprocess(input_dataset=fetch.output)
    train = train_model(input_dataset=prep.output, hyperparameters=hyperparameters)
    evaluate_model(model=train.outputs['output_model'], test_data=prep.output)
```

## Airflow DAG

```python
from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'mlops',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG('ml_training_pipeline', default_args=default_args, schedule_interval='0 2 * * *', catchup=False) as dag:
    fetch = KubernetesPodOperator(task_id='fetch_data', name='fetch-data', namespace='ml-pipelines', image='gcr.io/project/data-fetcher:latest', arguments=['--date', '{{ ds }}'])
    validate = KubernetesPodOperator(task_id='validate_data', name='validate-data', namespace='ml-pipelines', image='gcr.io/project/data-validator:latest')
    train = KubernetesPodOperator(task_id='train_model', name='train-model', namespace='ml-pipelines', image='gcr.io/project/model-trainer:latest', resources={'request_memory': '8Gi', 'request_cpu': '4', 'limit_gpu': '1'})
    evaluate = KubernetesPodOperator(task_id='evaluate_model', name='evaluate-model', namespace='ml-pipelines', image='gcr.io/project/model-evaluator:latest')
    deploy = KubernetesPodOperator(task_id='deploy_model', name='deploy-model', namespace='ml-pipelines', image='gcr.io/project/model-deployer:latest', trigger_rule='all_success')

    fetch >> validate >> train >> evaluate >> deploy
```

## Batch Inference Pattern

```python
import pandas as pd
from datetime import datetime

def batch_predict(model_uri: str, input_path: str, output_path: str, batch_size: int = 10000):
    """Run batch predictions on large datasets."""
    import mlflow.pyfunc
    model = mlflow.pyfunc.load_model(model_uri)
    chunks = pd.read_csv(input_path, chunksize=batch_size)
    results = []
    for i, chunk in enumerate(chunks):
        chunk['prediction'] = model.predict(chunk)
        chunk['predicted_at'] = datetime.utcnow()
        chunk['model_version'] = model_uri
        results.append(chunk)
    output_df = pd.concat(results)
    output_df.to_parquet(output_path)
    return len(output_df)
```

## Model Registry Operations

```python
from mlflow.tracking import MlflowClient

client = MlflowClient()

# Promote to production
client.transition_model_version_stage(name="fraud_detector", version=3, stage="Production")

# Archive previous version
client.transition_model_version_stage(name="fraud_detector", version=2, stage="Archived")

# Load production model
model = mlflow.pyfunc.load_model("models:/fraud_detector/Production")
```

## Full CI/CD Pipeline

```yaml
# .github/workflows/ml-pipeline.yml
name: ML Pipeline
on:
  push:
    paths: ['models/**', 'features/**']
  schedule:
    - cron: '0 2 * * *'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: pytest tests/unit
      - run: pytest tests/integration
      - run: python scripts/validate_schema.py

  train:
    needs: test
    runs-on: gpu-runner
    steps:
      - uses: actions/checkout@v3
      - run: python scripts/train.py
      - run: python scripts/evaluate.py
      - name: Register model
        if: ${{ env.ACCURACY > 0.85 }}
        run: python scripts/register_model.py

  deploy:
    needs: train
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - run: python scripts/deploy.py --env staging
      - run: python scripts/smoke_test.py
      - run: python scripts/deploy.py --env production
```

## Monitoring Dashboard Layout

```
+------------------------------------------------------------------+
|                    MODEL MONITORING                                |
| Model: fraud_detector_v2.3    Status: Healthy    Uptime: 99.97%   |
+------------------------------------------------------------------+
| Latency  P50: 12ms   P95: 45ms   P99: 120ms                      |
| Throughput: 1,250 req/s    Error rate: 0.02%                      |
+------------------------------------------------------------------+
| Accuracy: 94.2% (baseline 93.5%)   Precision: 89.1%  Recall: 91.3%|
+------------------------------------------------------------------+
| Feature Drift Score: 0.08 (threshold 0.15)   Status: OK           |
| Top drifted: amount (-0.12), time_since_last (+0.09)             |
+------------------------------------------------------------------+
```
