---
name: rag-architect
description: >
  Design RAG pipelines: chunking, retrieval evaluation, and architecture. Use when building a
  RAG system, selecting a chunking strategy, choosing a vector database, optimizing retrieval
  quality, or evaluating with RAGAS metrics.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: ai-ml
  tier: POWERFUL
  updated: 2026-06-17
---
# RAG Architect

The agent designs, implements, and optimizes production-grade RAG pipelines, from document chunking through evaluation.

## Core Capabilities

- **Chunking strategy selection** — match corpus characteristics to fixed-size, sentence, paragraph, semantic, recursive, or document-aware chunking with sized parameters.
- **Embedding & vector-DB choice** — pick an embedding model (local vs API) and vector store (Pinecone, Weaviate, Qdrant, Chroma, pgvector) by scale, latency, and cost.
- **Retrieval design** — dense, sparse (BM25), or hybrid retrieval with Reciprocal Rank Fusion plus cross-encoder reranking when precision must exceed 0.85.
- **Query transformations** — HyDE, multi-query, and step-back techniques for style mismatch and ambiguous queries.
- **Guardrails** — PII detection, hallucination/NLI checks, source attribution, confidence scoring, and injection prevention.
- **Evaluation** — RAGAS faithfulness/relevance plus IR metrics (Precision@K, Recall@K, MRR, NDCG) with failure analysis.
- **Production patterns** — caching, streaming, fallbacks, incremental re-indexing, and cost control.

## When to Use

- Building a RAG system end to end.
- Selecting a chunking strategy or choosing a vector database.
- Optimizing retrieval quality or adding reranking.
- Evaluating a pipeline with RAGAS or IR metrics.

## Clarify First

Before designing the pipeline, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Corpus characteristics** — size, document structure, and domain (drives the chunking-strategy selection and parameters)
- [ ] **Scale / latency / cost constraints** — query volume and budget (selects the embedding model and vector DB)
- [ ] **Retrieval precision target** — the accuracy bar (precision >0.85 forces hybrid retrieval + cross-encoder reranking)
- [ ] **Query types** — ambiguous, multi-hop, or style-mismatched (decides which query transforms: HyDE / multi-query / step-back)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

Python tools live at the skill root (no `scripts/` dir). Full flags/output formats: [references/tool-cli-reference.md](references/tool-cli-reference.md).

| Tool | Purpose | Command |
|------|---------|---------|
| `chunking_optimizer.py` | Analyze a corpus and recommend the optimal chunking strategy with parameters | `python chunking_optimizer.py ./docs --output results.json` |
| `retrieval_evaluator.py` | Evaluate retrieval with Precision@K, Recall@K, MRR, NDCG + failure analysis | `python retrieval_evaluator.py queries.json ./corpus ground_truth.json` |
| `rag_pipeline_designer.py` | Generate a full pipeline design, cost projection, and Mermaid diagram from requirements | `python rag_pipeline_designer.py requirements.json --output pipeline_design.json` |

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/rag-design-guide.md](references/rag-design-guide.md)** — the 8-step workflow, every selection matrix (chunking, embedding, vector DB, retrieval, query transforms), context-window optimization, RAGAS targets, guardrails, a worked YAML pipeline example, production patterns, common pitfalls, troubleshooting table, and success criteria. Read when designing or debugging a pipeline.
- **[references/tool-cli-reference.md](references/tool-cli-reference.md)** — full flag/parameter tables, examples, and output formats for `chunking_optimizer.py`, `retrieval_evaluator.py`, and `rag_pipeline_designer.py`. Read before running the scripts.
- **[references/chunking_strategies_comparison.md](references/chunking_strategies_comparison.md)** — deep comparison of the five chunking strategies with size distributions, quality metrics, and domain recommendations. Read when choosing a chunking strategy.
- **[references/embedding_model_benchmark.md](references/embedding_model_benchmark.md)** — benchmark of OpenAI, open-source, specialized, and domain-specific embedding models. Read when selecting an embedding model.
- **[references/rag_evaluation_framework.md](references/rag_evaluation_framework.md)** — full evaluation framework: retrieval/generation/end-to-end dimensions, offline/online/human methodologies, metric implementations. Read when building an evaluation harness.

## Scope & Limitations

**This skill covers:**
- End-to-end RAG pipeline architecture design: chunking, embedding, vector storage, retrieval, reranking, and evaluation.
- Quantitative chunking analysis across four strategy families (fixed-size, sentence, paragraph, semantic).
- Retrieval quality evaluation using standard IR metrics (Precision@K, Recall@K, MRR, NDCG) with a built-in TF-IDF baseline.
- Automated pipeline design with component selection, cost projection, and Mermaid architecture diagrams.

**This skill does NOT cover:**
- LLM prompt engineering or generation-side optimization -- see `engineering/prompt-engineer-toolkit`.
- Database schema design for metadata stores alongside vector databases -- see `engineering/database-designer`.
- Production observability, alerting, and SLO dashboards for deployed pipelines -- see `engineering/observability-designer`.
- Agent orchestration or multi-step reasoning workflows that sit on top of RAG retrieval -- see `engineering/agent-workflow-designer`.

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `engineering/prompt-engineer-toolkit` | Optimize system prompts and few-shot examples fed alongside retrieved chunks | Pipeline design output --> prompt templates that reference chunk format and metadata |
| `engineering/database-designer` | Design relational metadata stores (tags, access control, source tracking) paired with the vector database | Vector DB recommendation --> metadata schema for hybrid storage |
| `engineering/observability-designer` | Set up latency, throughput, and accuracy monitoring for the deployed RAG pipeline | Evaluation metrics and SLO targets --> dashboards and alerting rules |
| `engineering/agent-workflow-designer` | Embed the RAG retrieval step inside multi-agent reasoning workflows | Retrieval config --> agent tool definition with top-K and threshold parameters |
| `engineering/ci-cd-pipeline-builder` | Automate embedding re-indexing, evaluation regression tests, and deployment on document changes | Evaluation thresholds --> CI gate that blocks deploys when metrics regress |
| `engineering/api-design-reviewer` | Review the query and ingestion API surface exposed by the RAG service | Pipeline config --> OpenAPI spec review for search and ingest endpoints |
