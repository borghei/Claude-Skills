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

Before generating artifacts, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Task:** model deployment / RAG pipeline build / monitoring setup (selects the script and workflow).
- **Serving target & rollout:** container vs K8s and canary vs direct (drives the generated Dockerfile/manifests and health gates; the tool writes a rolling-update Deployment, so canary splitting is configured by hand from the references).
- **Model or data interface:** the input/output contract, and for RAG the corpus + vector store (shapes the scaffold).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Tools

All three tools use the Python standard library only, run offline and give the same output for the same input. Each has `--example` (prints a sample input) and `--format text|json`, writes only under `--output`, and refuses to overwrite existing files unless you pass `--force`. Sample inputs are in `assets/`.

| Tool | Purpose | Command |
|------|---------|---------|
| `model_deployment_pipeline.py` | Generate a Dockerfile (pinned slim base, non-root user, HEALTHCHECK), Kubernetes Deployment, Service and HPA with probes and resource requests/limits, a health/readiness `serve.py` stub and a requirements stub; flags latest tags, missing limits, root, privileged ports and single replicas | `python scripts/model_deployment_pipeline.py --input assets/deployment_spec.json --output deploy/` |
| `rag_system_builder.py` | Plan a RAG pipeline from corpus size, document types, query volume, latency budget, embedding dimension and update frequency: chunking per type, index choice with memory estimate, dense or hybrid retrieval, reranking and top-k, update strategy and evaluation plan, each with its reason; writes `rag_config.json` and `pipeline_plan.md` | `python scripts/rag_system_builder.py --input assets/rag_spec.json --output rag-plan/` |
| `ml_monitoring_suite.py` | Compare a baseline and a current CSV: PSI per feature (quantile bins for numeric, category shares for categorical), two-sample KS for numeric features, missing-rate change, and accuracy or MAE drift from prediction and label columns, mapped to OK/WARN/ALERT; writes `drift_report.json` and Prometheus-style `alert_rules.yaml` | `python scripts/ml_monitoring_suite.py --baseline assets/monitoring_baseline.csv --current assets/monitoring_current.csv --prediction-col prediction --label-col label --exclude customer_id --output monitoring/` |

`ml_monitoring_suite.py` exits 1 when the overall status reaches `--fail-on` (default `alert`), so it can gate a CI or scheduled job; it exits 2 on bad input. The other two exit 0 on success and 1 on bad input. See [references/tool-reference.md](references/tool-reference.md) for every flag, spec field, rule and threshold, with real output from the samples.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/production-ml-workflows.md](references/production-ml-workflows.md)** — the five step-by-step workflows (model deployment, MLOps setup, LLM integration, RAG, monitoring) with all code templates, serving/vector-DB/chunking/cost tables, the troubleshooting matrix, and success criteria. Read when executing any workflow.
- **[references/tool-reference.md](references/tool-reference.md)** — flags, spec fields, decision rules, thresholds, exit codes and sample output for the three scripts. Read when running the tools or interpreting their output.
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

**Tool limits:**
- `model_deployment_pipeline.py` writes artifacts but does not build images, push them or apply manifests, and it does not generate canary or traffic-splitting config. `serve.py` is a stub: model loading and `/predict` are yours to implement, and `requirements.txt` lists packages without versions until you pin them.
- `rag_system_builder.py` plans from a spec; it does not read documents, compute embeddings or measure retrieval. Memory figures are estimates from vector count and dimension, it names no vendor and quotes no prices, and its starting eval targets need calibration on your data.
- `ml_monitoring_suite.py` works on two CSV snapshots in memory. It has no streaming, scheduling or dashboards, and it does not track latency or error rates. The KS p-value is the asymptotic approximation and is loose below about 50 rows per side, and PSI is inflated by sampling noise on small files; the tool notes both. ID-like categorical columns are skipped rather than tested. The alert rules assume metric names you must export or rename.

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
