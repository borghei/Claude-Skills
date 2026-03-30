---
name: senior-ml-engineer
description: >
  ML engineering skill for productionizing models, building MLOps pipelines, and
  integrating LLMs. Covers model deployment, feature stores, drift monitoring,
  RAG systems, and cost optimization.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: machine-learning
  updated: 2026-03-31
  tags: [ml-pipelines, model-deployment, mlops, rag]
---
# Senior ML Engineer

Production ML engineering patterns for model deployment, MLOps infrastructure, and LLM integration.

---

## Table of Contents

- [Model Deployment Workflow](#model-deployment-workflow)
- [MLOps Pipeline Setup](#mlops-pipeline-setup)
- [LLM Integration Workflow](#llm-integration-workflow)
- [RAG System Implementation](#rag-system-implementation)
- [Model Monitoring](#model-monitoring)
- [Reference Documentation](#reference-documentation)
- [Tools](#tools)

---

## Model Deployment Workflow

Deploy a trained model to production with monitoring:

1. Export model to standardized format (ONNX, TorchScript, SavedModel)
2. Package model with dependencies in Docker container
3. Deploy to staging environment
4. Run integration tests against staging
5. Deploy canary (5% traffic) to production
6. Monitor latency and error rates for 1 hour
7. Promote to full production if metrics pass
8. **Validation:** p95 latency < 100ms, error rate < 0.1%

### Container Template

```dockerfile
FROM python:3.11-slim

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY model/ /app/model/
COPY src/ /app/src/

HEALTHCHECK CMD curl -f http://localhost:8080/health || exit 1

EXPOSE 8080
CMD ["uvicorn", "src.server:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Serving Options

| Option | Latency | Throughput | Use Case |
|--------|---------|------------|----------|
| FastAPI + Uvicorn | Low | Medium | REST APIs, small models |
| Triton Inference Server | Very Low | Very High | GPU inference, batching |
| TensorFlow Serving | Low | High | TensorFlow models |
| TorchServe | Low | High | PyTorch models |
| Ray Serve | Medium | High | Complex pipelines, multi-model |

---

## MLOps Pipeline Setup

Establish automated training and deployment:

1. Configure feature store (Feast, Tecton) for training data
2. Set up experiment tracking (MLflow, Weights & Biases)
3. Create training pipeline with hyperparameter logging
4. Register model in model registry with version metadata
5. Configure staging deployment triggered by registry events
6. Set up A/B testing infrastructure for model comparison
7. Enable drift monitoring with alerting
8. **Validation:** New models automatically evaluated against baseline

### Feature Store Pattern

```python
from feast import Entity, Feature, FeatureView, FileSource

user = Entity(name="user_id", value_type=ValueType.INT64)

user_features = FeatureView(
    name="user_features",
    entities=["user_id"],
    ttl=timedelta(days=1),
    features=[
        Feature(name="purchase_count_30d", dtype=ValueType.INT64),
        Feature(name="avg_order_value", dtype=ValueType.FLOAT),
    ],
    online=True,
    source=FileSource(path="data/user_features.parquet"),
)
```

### Retraining Triggers

| Trigger | Detection | Action |
|---------|-----------|--------|
| Scheduled | Cron (weekly/monthly) | Full retrain |
| Performance drop | Accuracy < threshold | Immediate retrain |
| Data drift | PSI > 0.2 | Evaluate, then retrain |
| New data volume | X new samples | Incremental update |

---

## LLM Integration Workflow

Integrate LLM APIs into production applications:

1. Create provider abstraction layer for vendor flexibility
2. Implement retry logic with exponential backoff
3. Configure fallback to secondary provider
4. Set up token counting and context truncation
5. Add response caching for repeated queries
6. Implement cost tracking per request
7. Add structured output validation with Pydantic
8. **Validation:** Response parses correctly, cost within budget

### Provider Abstraction

```python
from abc import ABC, abstractmethod
from tenacity import retry, stop_after_attempt, wait_exponential

class LLMProvider(ABC):
    @abstractmethod
    def complete(self, prompt: str, **kwargs) -> str:
        pass

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
def call_llm_with_retry(provider: LLMProvider, prompt: str) -> str:
    return provider.complete(prompt)
```

### Cost Management

| Provider | Input Cost | Output Cost |
|----------|------------|-------------|
| GPT-4 | $0.03/1K | $0.06/1K |
| GPT-3.5 | $0.0005/1K | $0.0015/1K |
| Claude 3 Opus | $0.015/1K | $0.075/1K |
| Claude 3 Haiku | $0.00025/1K | $0.00125/1K |

---

## RAG System Implementation

Build retrieval-augmented generation pipeline:

1. Choose vector database (Pinecone, Qdrant, Weaviate)
2. Select embedding model based on quality/cost tradeoff
3. Implement document chunking strategy
4. Create ingestion pipeline with metadata extraction
5. Build retrieval with query embedding
6. Add reranking for relevance improvement
7. Format context and send to LLM
8. **Validation:** Response references retrieved context, no hallucinations

### Vector Database Selection

| Database | Hosting | Scale | Latency | Best For |
|----------|---------|-------|---------|----------|
| Pinecone | Managed | High | Low | Production, managed |
| Qdrant | Both | High | Very Low | Performance-critical |
| Weaviate | Both | High | Low | Hybrid search |
| Chroma | Self-hosted | Medium | Low | Prototyping |
| pgvector | Self-hosted | Medium | Medium | Existing Postgres |

### Chunking Strategies

| Strategy | Chunk Size | Overlap | Best For |
|----------|------------|---------|----------|
| Fixed | 500-1000 tokens | 50-100 | General text |
| Sentence | 3-5 sentences | 1 sentence | Structured text |
| Semantic | Variable | Based on meaning | Research papers |
| Recursive | Hierarchical | Parent-child | Long documents |

---

## Model Monitoring

Monitor production models for drift and degradation:

1. Set up latency tracking (p50, p95, p99)
2. Configure error rate alerting
3. Implement input data drift detection
4. Track prediction distribution shifts
5. Log ground truth when available
6. Compare model versions with A/B metrics
7. Set up automated retraining triggers
8. **Validation:** Alerts fire before user-visible degradation

### Drift Detection

```python
from scipy.stats import ks_2samp

def detect_drift(reference, current, threshold=0.05):
    statistic, p_value = ks_2samp(reference, current)
    return {
        "drift_detected": p_value < threshold,
        "ks_statistic": statistic,
        "p_value": p_value
    }
```

### Alert Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| p95 latency | > 100ms | > 200ms |
| Error rate | > 0.1% | > 1% |
| PSI (drift) | > 0.1 | > 0.2 |
| Accuracy drop | > 2% | > 5% |

---

## Reference Documentation

### MLOps Production Patterns

`references/mlops_production_patterns.md` contains:

- Model deployment pipeline with Kubernetes manifests
- Feature store architecture with Feast examples
- Model monitoring with drift detection code
- A/B testing infrastructure with traffic splitting
- Automated retraining pipeline with MLflow

### LLM Integration Guide

`references/llm_integration_guide.md` contains:

- Provider abstraction layer pattern
- Retry and fallback strategies with tenacity
- Prompt engineering templates (few-shot, CoT)
- Token optimization with tiktoken
- Cost calculation and tracking

### RAG System Architecture

`references/rag_system_architecture.md` contains:

- RAG pipeline implementation with code
- Vector database comparison and integration
- Chunking strategies (fixed, semantic, recursive)
- Embedding model selection guide
- Hybrid search and reranking patterns

---

## Tools

### Model Deployment Pipeline

```bash
python scripts/model_deployment_pipeline.py --model model.pkl --target staging
```

Generates deployment artifacts: Dockerfile, Kubernetes manifests, health checks.

### RAG System Builder

```bash
python scripts/rag_system_builder.py --config rag_config.yaml --analyze
```

Scaffolds RAG pipeline with vector store integration and retrieval logic.

### ML Monitoring Suite

```bash
python scripts/ml_monitoring_suite.py --config monitoring.yaml --deploy
```

Sets up drift detection, alerting, and performance dashboards.

---

## Tech Stack

| Category | Tools |
|----------|-------|
| ML Frameworks | PyTorch, TensorFlow, Scikit-learn, XGBoost |
| LLM Frameworks | LangChain, LlamaIndex, DSPy |
| MLOps | MLflow, Weights & Biases, Kubeflow |
| Data | Spark, Airflow, dbt, Kafka |
| Deployment | Docker, Kubernetes, Triton |
| Databases | PostgreSQL, BigQuery, Pinecone, Redis |

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Model latency spikes after deployment | Container resource limits too low or cold starts on serverless | Pre-warm instances, increase CPU/memory limits, enable GPU request batching |
| Data drift alerts firing constantly | Reference distribution outdated or threshold too sensitive | Recalibrate reference window to recent 30 days, raise PSI warning threshold to 0.15 |
| Feature store serving stale features | TTL misconfigured or materialization job failing silently | Verify TTL matches data freshness SLA, add alerting on materialization job status |
| RAG retrieval returns irrelevant chunks | Chunk size too large or embedding model mismatch | Reduce chunk size to 300-500 tokens, switch to domain-tuned embedding model, add reranker |
| LLM provider rate limits hit in production | No request queuing or burst traffic exceeds quota | Implement token bucket rate limiter, add request queue with backpressure, configure fallback provider |
| Model accuracy degrades gradually | Concept drift in underlying data distribution | Enable automated retraining triggers on accuracy drop > 2%, schedule weekly evaluation jobs |
| A/B test results inconclusive after weeks | Insufficient traffic split or high-variance metric chosen | Increase treatment allocation to 10-20%, switch to lower-variance proxy metric, extend test duration |

---

## Success Criteria

- Model serving latency p99 under 100ms for real-time inference endpoints
- Zero data drift alerts unresolved for more than 48 hours
- Automated retraining pipeline triggers within 1 hour of performance threshold breach
- RAG system retrieval accuracy (hit rate at k=5) above 90% on evaluation set
- LLM integration uptime at 99.9% with provider fallback activating in under 2 seconds
- Feature store materialization freshness within defined TTL for all online features
- Model deployment rollback completes in under 5 minutes with zero dropped requests

---

## Scope & Limitations

**This skill covers:**
- End-to-end model deployment pipelines (packaging, containerization, serving, canary rollout)
- MLOps infrastructure setup (feature stores, experiment tracking, model registries, retraining)
- LLM integration patterns (provider abstraction, retries, caching, cost tracking)
- RAG system architecture (vector databases, chunking, retrieval, reranking)

**This skill does NOT cover:**
- Model training algorithms or hyperparameter tuning (see `senior-data-scientist`)
- Raw data pipeline construction and ETL orchestration (see `senior-data-engineer`)
- Prompt engineering techniques, few-shot design, or prompt optimization (see `senior-prompt-engineer`)
- Image/video model architectures or computer vision inference optimization (see `senior-computer-vision`)

---

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `senior-data-scientist` | Receives trained models and evaluation metrics for deployment | Data Scientist exports model artifacts and baseline metrics; ML Engineer packages and deploys |
| `senior-data-engineer` | Consumes feature pipelines and data quality outputs | Data Engineer builds ETL and feature pipelines; ML Engineer reads from feature store for serving |
| `senior-prompt-engineer` | Provides LLM serving infrastructure for prompt workflows | Prompt Engineer designs prompts; ML Engineer deploys provider abstraction and manages cost/latency |
| `senior-devops` | Leverages CI/CD and Kubernetes infrastructure for model serving | DevOps manages cluster and pipelines; ML Engineer defines deployment manifests and health checks |
| `senior-computer-vision` | Deploys vision models through shared serving infrastructure | CV Engineer trains and exports models; ML Engineer handles Triton/TorchServe deployment and monitoring |
| `senior-security` | Applies security scanning to model containers and API endpoints | Security reviews container images and endpoint auth; ML Engineer remediates findings before promotion |

---

## Tool Reference

### model_deployment_pipeline.py

**Purpose:** Generates deployment artifacts for productionizing ML models, including Dockerfiles, Kubernetes manifests, and health check configurations.

**Usage:**

```bash
python scripts/model_deployment_pipeline.py --input <path> --output <path> [--config <file>] [--verbose]
```

**Flags/Parameters:**

| Flag | Short | Required | Description |
|------|-------|----------|-------------|
| `--input` | `-i` | Yes | Input path (model artifact or directory) |
| `--output` | `-o` | Yes | Output path for generated deployment artifacts |
| `--config` | `-c` | No | Configuration file for deployment settings |
| `--verbose` | `-v` | No | Enable debug-level logging output |

**Example:**

```bash
python scripts/model_deployment_pipeline.py -i ./models/classifier.pkl -o ./deploy/
```

**Output Formats:** JSON to stdout containing `status`, `start_time`, `end_time`, and `processed_items`. Logs progress to stderr.

---

### rag_system_builder.py

**Purpose:** Scaffolds a RAG pipeline with vector store integration, retrieval logic, and ingestion configuration.

**Usage:**

```bash
python scripts/rag_system_builder.py --input <path> --output <path> [--config <file>] [--verbose]
```

**Flags/Parameters:**

| Flag | Short | Required | Description |
|------|-------|----------|-------------|
| `--input` | `-i` | Yes | Input path (document corpus or configuration directory) |
| `--output` | `-o` | Yes | Output path for generated RAG pipeline artifacts |
| `--config` | `-c` | No | Configuration file for RAG settings (vector DB, chunking, embedding) |
| `--verbose` | `-v` | No | Enable debug-level logging output |

**Example:**

```bash
python scripts/rag_system_builder.py -i ./documents/ -o ./rag-pipeline/ -c rag_config.yaml
```

**Output Formats:** JSON to stdout containing `status`, `start_time`, `end_time`, and `processed_items`. Logs progress to stderr.

---

### ml_monitoring_suite.py

**Purpose:** Sets up drift detection, performance alerting, and monitoring dashboards for production ML models.

**Usage:**

```bash
python scripts/ml_monitoring_suite.py --input <path> --output <path> [--config <file>] [--verbose]
```

**Flags/Parameters:**

| Flag | Short | Required | Description |
|------|-------|----------|-------------|
| `--input` | `-i` | Yes | Input path (model metrics, reference data, or monitoring config) |
| `--output` | `-o` | Yes | Output path for generated monitoring configuration and dashboards |
| `--config` | `-c` | No | Configuration file for monitoring thresholds and alert rules |
| `--verbose` | `-v` | No | Enable debug-level logging output |

**Example:**

```bash
python scripts/ml_monitoring_suite.py -i ./model-metrics/ -o ./monitoring/ -c monitoring.yaml -v
```

**Output Formats:** JSON to stdout containing `status`, `start_time`, `end_time`, and `processed_items`. Logs progress to stderr.
