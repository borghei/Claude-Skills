---
name: senior-ml-engineer
description: Expert ML engineering covering model development, MLOps, feature engineering, model deployment, and production ML systems.
version: 1.0.0
author: Claude Skills
category: engineering
tags: [ml, mlops, pytorch, tensorflow, deployment, feature-engineering]
---

# Senior ML Engineer

Expert-level machine learning engineering for production systems.

## Core Competencies

- Model development and training
- Feature engineering
- MLOps and pipelines
- Model deployment and serving
- Monitoring and drift detection
- A/B testing and experimentation
- Performance optimization
- Data pipelines

## ML Development Lifecycle

### Project Structure

```
ml-project/
├── data/
│   ├── raw/
│   ├── processed/
│   └── features/
├── notebooks/
│   ├── 01_exploration.ipynb
│   ├── 02_feature_engineering.ipynb
│   └── 03_modeling.ipynb
├── src/
│   ├── data/
│   │   ├── ingestion.py
│   │   └── preprocessing.py
│   ├── features/
│   │   ├── engineering.py
│   │   └── store.py
│   ├── models/
│   │   ├── train.py
│   │   ├── evaluate.py
│   │   └── predict.py
│   └── serving/
│       ├── api.py
│       └── batch.py
├── tests/
├── configs/
├── mlruns/
└── requirements.txt
```

## Feature Engineering

### Feature Types

**Numerical Features:**
```python
def engineer_numerical_features(df: pd.DataFrame) -> pd.DataFrame:
    # Scaling
    df['amount_scaled'] = StandardScaler().fit_transform(df[['amount']])

    # Log transform for skewed data
    df['amount_log'] = np.log1p(df['amount'])

    # Binning
    df['amount_bucket'] = pd.cut(df['amount'],
                                  bins=[0, 100, 500, 1000, np.inf],
                                  labels=['low', 'medium', 'high', 'very_high'])

    # Interactions
    df['amount_per_transaction'] = df['total_amount'] / df['transaction_count']

    return df
```

**Categorical Features:**
```python
def engineer_categorical_features(df: pd.DataFrame) -> pd.DataFrame:
    # One-hot encoding
    df = pd.get_dummies(df, columns=['category'], prefix='cat')

    # Target encoding
    target_means = df.groupby('category')['target'].mean()
    df['category_target_enc'] = df['category'].map(target_means)

    # Frequency encoding
    freq = df['category'].value_counts(normalize=True)
    df['category_freq'] = df['category'].map(freq)

    return df
```

**Temporal Features:**
```python
def engineer_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Basic components
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['month'] = df['timestamp'].dt.month
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)

    # Cyclical encoding
    df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)

    # Lag features
    df['amount_lag_1'] = df.groupby('user_id')['amount'].shift(1)
    df['amount_rolling_mean_7'] = df.groupby('user_id')['amount'].transform(
        lambda x: x.rolling(7, min_periods=1).mean()
    )

    return df
```

### Feature Store

```python
from feast import FeatureStore, Entity, Feature, FeatureView, FileSource

# Define entity
user = Entity(
    name="user_id",
    value_type=ValueType.STRING,
    description="User identifier"
)

# Define feature view
user_features = FeatureView(
    name="user_features",
    entities=["user_id"],
    ttl=timedelta(days=1),
    features=[
        Feature(name="total_purchases", dtype=ValueType.FLOAT),
        Feature(name="avg_order_value", dtype=ValueType.FLOAT),
        Feature(name="days_since_last_order", dtype=ValueType.INT32),
    ],
    source=FileSource(
        path="data/user_features.parquet",
        timestamp_field="event_timestamp",
    )
)

# Retrieve features for training
store = FeatureStore(repo_path=".")
training_df = store.get_historical_features(
    entity_df=entity_df,
    features=[
        "user_features:total_purchases",
        "user_features:avg_order_value",
    ]
).to_df()

# Retrieve features for inference
online_features = store.get_online_features(
    features=[
        "user_features:total_purchases",
        "user_features:avg_order_value",
    ],
    entity_rows=[{"user_id": "user_123"}]
).to_dict()
```

## Model Training

### PyTorch Training Loop

```python
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from tqdm import tqdm
import mlflow

class Model(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim // 2, output_dim)
        )

    def forward(self, x):
        return self.layers(x)


def train_model(
    model: nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    epochs: int,
    learning_rate: float
):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=3)

    best_val_loss = float('inf')

    with mlflow.start_run():
        mlflow.log_params({
            'epochs': epochs,
            'learning_rate': learning_rate,
            'batch_size': train_loader.batch_size
        })

        for epoch in range(epochs):
            # Training
            model.train()
            train_loss = 0
            for batch_x, batch_y in tqdm(train_loader, desc=f'Epoch {epoch+1}'):
                batch_x, batch_y = batch_x.to(device), batch_y.to(device)

                optimizer.zero_grad()
                outputs = model(batch_x)
                loss = criterion(outputs, batch_y)
                loss.backward()
                optimizer.step()

                train_loss += loss.item()

            # Validation
            model.eval()
            val_loss = 0
            correct = 0
            total = 0
            with torch.no_grad():
                for batch_x, batch_y in val_loader:
                    batch_x, batch_y = batch_x.to(device), batch_y.to(device)
                    outputs = model(batch_x)
                    loss = criterion(outputs, batch_y)
                    val_loss += loss.item()

                    _, predicted = outputs.max(1)
                    total += batch_y.size(0)
                    correct += predicted.eq(batch_y).sum().item()

            val_accuracy = correct / total
            scheduler.step(val_loss)

            mlflow.log_metrics({
                'train_loss': train_loss / len(train_loader),
                'val_loss': val_loss / len(val_loader),
                'val_accuracy': val_accuracy
            }, step=epoch)

            if val_loss < best_val_loss:
                best_val_loss = val_loss
                torch.save(model.state_dict(), 'best_model.pt')
                mlflow.pytorch.log_model(model, 'model')

    return model
```

### Hyperparameter Tuning

```python
import optuna
from sklearn.model_selection import cross_val_score

def objective(trial):
    params = {
        'n_estimators': trial.suggest_int('n_estimators', 100, 1000),
        'max_depth': trial.suggest_int('max_depth', 3, 10),
        'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
        'min_child_weight': trial.suggest_int('min_child_weight', 1, 10),
        'subsample': trial.suggest_float('subsample', 0.6, 1.0),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
    }

    model = XGBClassifier(**params, random_state=42)
    scores = cross_val_score(model, X_train, y_train, cv=5, scoring='roc_auc')

    return scores.mean()


study = optuna.create_study(direction='maximize')
study.optimize(objective, n_trials=100, timeout=3600)

print(f"Best params: {study.best_params}")
print(f"Best score: {study.best_value}")
```

## Model Deployment

### FastAPI Model Serving

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import torch
import numpy as np

app = FastAPI()

# Load model at startup
model = None

@app.on_event("startup")
async def load_model():
    global model
    model = Model(input_dim=10, hidden_dim=64, output_dim=2)
    model.load_state_dict(torch.load('best_model.pt'))
    model.eval()


class PredictionRequest(BaseModel):
    features: list[float]


class PredictionResponse(BaseModel):
    prediction: int
    probability: float
    class_probabilities: list[float]


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        features = torch.tensor([request.features], dtype=torch.float32)

        with torch.no_grad():
            logits = model(features)
            probabilities = torch.softmax(logits, dim=1)
            prediction = probabilities.argmax(dim=1).item()

        return PredictionResponse(
            prediction=prediction,
            probability=probabilities[0][prediction].item(),
            class_probabilities=probabilities[0].tolist()
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "healthy", "model_loaded": model is not None}
```

### Batch Inference

```python
import ray
from typing import Iterator

@ray.remote
class BatchPredictor:
    def __init__(self, model_path: str):
        self.model = self._load_model(model_path)

    def _load_model(self, path: str):
        model = Model(input_dim=10, hidden_dim=64, output_dim=2)
        model.load_state_dict(torch.load(path))
        model.eval()
        return model

    def predict_batch(self, features: np.ndarray) -> np.ndarray:
        with torch.no_grad():
            inputs = torch.tensor(features, dtype=torch.float32)
            outputs = self.model(inputs)
            predictions = torch.argmax(outputs, dim=1)
        return predictions.numpy()


def run_batch_inference(data_path: str, output_path: str, batch_size: int = 1000):
    ray.init()

    # Create prediction actors
    num_actors = 4
    actors = [BatchPredictor.remote('best_model.pt') for _ in range(num_actors)]

    # Process in batches
    df = pd.read_parquet(data_path)
    predictions = []

    for i in range(0, len(df), batch_size * num_actors):
        batch_futures = []
        for j, actor in enumerate(actors):
            start = i + j * batch_size
            end = min(start + batch_size, len(df))
            if start < len(df):
                features = df.iloc[start:end][feature_columns].values
                batch_futures.append(actor.predict_batch.remote(features))

        batch_predictions = ray.get(batch_futures)
        predictions.extend(np.concatenate(batch_predictions))

    df['prediction'] = predictions
    df.to_parquet(output_path)

    ray.shutdown()
```

## Model Monitoring

### Drift Detection

```python
from evidently import ColumnMapping
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, TargetDriftPreset

def detect_drift(reference_data: pd.DataFrame, current_data: pd.DataFrame):
    column_mapping = ColumnMapping(
        target='target',
        numerical_features=['feature_1', 'feature_2', 'feature_3'],
        categorical_features=['category_1', 'category_2']
    )

    report = Report(metrics=[
        DataDriftPreset(),
        TargetDriftPreset()
    ])

    report.run(
        reference_data=reference_data,
        current_data=current_data,
        column_mapping=column_mapping
    )

    # Get drift summary
    drift_results = report.as_dict()
    data_drift_detected = drift_results['metrics'][0]['result']['dataset_drift']
    drifted_features = [
        col for col, result in drift_results['metrics'][0]['result']['drift_by_columns'].items()
        if result['drift_detected']
    ]

    return {
        'drift_detected': data_drift_detected,
        'drifted_features': drifted_features,
        'report': report
    }
```

### Performance Monitoring

```python
from prometheus_client import Counter, Histogram, Gauge
import time

# Metrics
prediction_counter = Counter(
    'model_predictions_total',
    'Total predictions made',
    ['model_version', 'prediction_class']
)

prediction_latency = Histogram(
    'model_prediction_latency_seconds',
    'Prediction latency',
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0]
)

model_accuracy = Gauge(
    'model_accuracy',
    'Model accuracy on recent predictions',
    ['model_version']
)


def monitored_predict(features, model_version='v1'):
    start_time = time.time()

    prediction = model.predict(features)

    # Record metrics
    latency = time.time() - start_time
    prediction_latency.observe(latency)
    prediction_counter.labels(
        model_version=model_version,
        prediction_class=str(prediction)
    ).inc()

    return prediction
```

## Reference Materials

- `references/feature_engineering.md` - Feature engineering patterns
- `references/mlops_guide.md` - MLOps best practices
- `references/model_serving.md` - Deployment patterns
- `references/monitoring.md` - ML monitoring setup

## Scripts

```bash
# Feature pipeline
python scripts/feature_pipeline.py --config features.yaml

# Model training
python scripts/train.py --config model_config.yaml --experiment exp_001

# Model deployment
python scripts/deploy.py --model-uri runs:/abc123/model --env production

# Drift detection
python scripts/drift_check.py --reference ref_data.parquet --current current_data.parquet
```
