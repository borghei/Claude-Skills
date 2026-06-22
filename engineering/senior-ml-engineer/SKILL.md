---
name: senior-ml-engineer
description: >
  ML engineering skill for productionizing models, building MLOps pipelines, and
  integrating LLMs. Covers model deployment, feature stores, drift monitoring,
  RAG systems, and cost optimization.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: machine-learning
  updated: 2026-06-17
  tags: [ml-pipelines, model-deployment, mlops, rag]
---
# Senior ML Engineer

Production ML engineering patterns for model deployment, MLOps infrastructure, and LLM integration.

## Core Capabilities

- **Model deployment** — export to ONNX/TorchScript/SavedModel, containerize, canary rollout, and serve via FastAPI, Triton, TF Serving, TorchServe, or Ray Serve with p95<100ms / error<0.1% gates.
- **MLOps pipelines** — feature stores (Feast/Tecton), experiment tracking (MLflow/W&B), model registry, A/B testing, and drift-triggered retraining.
- **LLM integration** — provider abstraction, retry/fallback with exponential backoff, token counting, response caching, cost tracking, and Pydantic output validation.
- **RAG systems** — vector database selection, chunking strategies, ingestion, retrieval, and reranking.
- **Model monitoring** — latency/error tracking, input drift detection (KS test, PSI), prediction-shift alerts, and automated retraining triggers.

## When to Use

- Deploying a trained model to production with canary rollout and monitoring.
- Standing up MLOps infrastructure (feature store, registry, retraining).
- Integrating LLM APIs with provider abstraction and cost control.
- Building a RAG pipeline (vector DB + chunking + retrieval + reranking).
- Setting up drift detection and model-health alerting.

## Clarify First

Before generating artifacts, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Task** — model deployment / RAG pipeline build / monitoring setup (selects the script and workflow)
- [ ] **Serving target & rollout** — container vs K8s and canary vs direct (drives the generated Dockerfile/manifests and health gates)
- [ ] **Model or data interface** — the input/output contract, and for RAG the corpus + vector store (shapes the scaffold)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `model_deployment_pipeline.py` | Generate deployment artifacts (Dockerfile, K8s manifests, health checks) | `python scripts/model_deployment_pipeline.py --input <path> --output <path> [--config <file>]` |
| `rag_system_builder.py` | Scaffold a RAG pipeline with vector store + retrieval logic | `python scripts/rag_system_builder.py --input <path> --output <path> [--config <file>]` |
| `ml_monitoring_suite.py` | Set up drift detection, alerting, and dashboards | `python scripts/ml_monitoring_suite.py --input <path> --output <path> [--config <file>]` |

All tools support `--verbose`/`-v` and emit JSON (`status`, `start_time`, `end_time`, `processed_items`) to stdout. See [references/tool-reference.md](references/tool-reference.md) for full flag detail.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/production-ml-workflows.md](references/production-ml-workflows.md)** — the five step-by-step workflows (model deployment, MLOps setup, LLM integration, RAG, monitoring) with all code templates, serving/vector-DB/chunking/cost tables, the troubleshooting matrix, and success criteria. Read when executing any workflow.
- **[references/tool-reference.md](references/tool-reference.md)** — full flag/parameter tables and output formats for the three scripts. Read when scripting the tools.
- **[references/mlops_production_patterns.md](references/mlops_production_patterns.md)** — model deployment pipeline with Kubernetes manifests, feature store architecture with Feast examples, model monitoring with drift detection code, A/B testing with traffic splitting, automated retraining with MLflow. Read when building MLOps infra.
- **[references/llm_integration_guide.md](references/llm_integration_guide.md)** — provider abstraction layer, retry/fallback with tenacity, prompt templates (few-shot, CoT), token optimization with tiktoken, cost calculation and tracking. Read when integrating an LLM.
- **[references/rag_system_architecture.md](references/rag_system_architecture.md)** — RAG pipeline implementation code, vector database comparison/integration, chunking strategies, embedding model selection, hybrid search and reranking. Read when building a RAG system.

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

**Last Updated:** June 2026
**Version:** 1.1.0
