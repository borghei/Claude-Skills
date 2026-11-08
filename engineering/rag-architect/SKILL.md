---
name: rag-architect
description: >
  Designs and evaluates RAG pipelines: chunking analysis, retrieval metrics on your
  queries, first-pass designs with costs. Use when building a RAG system, choosing
  chunking, embeddings or a vector store, or fixing poor retrieval.
license: MIT + Commons Clause
metadata:
  version: 1.2.0
  author: borghei
  category: engineering
  domain: ai-ml
  tier: POWERFUL
  updated: 2026-11-08
  tags:
    - rag
    - retrieval
    - chunking
    - vector-database
    - embeddings
---
# RAG Architect

The agent designs, implements and tunes retrieval-augmented generation pipelines from chunking through evaluation, and makes every choice (chunking, embedding model, vector store, retrieval mode, reranking) answer to a measured retrieval score on the user's own queries.

## Core Capabilities

- **Chunking strategy selection:** fixed-size, sentence, paragraph, semantic, recursive or document-aware chunking, sized to the corpus.
- **Embedding and vector-store choice:** local vs API models and Pinecone, Weaviate, Qdrant, Chroma or pgvector by scale, latency, cost and data residency.
- **Retrieval design:** dense, sparse (BM25) or hybrid retrieval with Reciprocal Rank Fusion, plus cross-encoder reranking when precision matters most.
- **Query transformations:** HyDE, multi-query and step-back for style mismatch and ambiguous queries.
- **Guardrails and evaluation:** source attribution, groundedness checks, injection defences; IR metrics (Precision@K, Recall@K, MRR, NDCG) and RAGAS-style generation metrics.

## When to Use

- Building a RAG system end to end, or replacing one component.
- Selecting a chunking strategy, embedding model or vector database.
- Diagnosing poor answers: deciding whether retrieval or generation is at fault.
- Setting up a retrieval regression test before changing the pipeline.

## Clarify First

Before designing the pipeline, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Corpus characteristics:** size, structure, languages and domain (drive chunking and the embedding shortlist).
- **Scale, latency and cost constraints:** query volume, budget, and whether data may leave the infrastructure.
- **Retrieval quality target:** the bar to meet (a high precision target usually means hybrid retrieval plus reranking).
- **Query types:** ambiguous, multi-hop or style-mismatched (decides which query transforms to try).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Workflow

1. **Build the ground truth first:** 50 or more real queries with the documents that answer them. Without it no choice below can be verified.
2. **Draft the design** with `rag_pipeline_designer.py` from a requirements file; treat its picks as a starting point.
3. **Choose chunking** with `chunking_optimizer.py` on a sample of the real corpus.
4. **Shortlist embedding models** using [references/embedding_model_benchmark.md](references/embedding_model_benchmark.md), embed the same chunks with each, and compare.
5. **Measure** with `retrieval_evaluator.py`. Validation checkpoint: the chosen configuration beats the TF-IDF baseline and meets the agreed target on Recall@k and MRR; read the worst queries by hand.
6. Done when the design, model ids and versions, chunk parameters and the evaluation scores are written down, and the evaluation runs as a regression test before any pipeline change.

## Quick Start

```bash
# from engineering/rag-architect/ (the tools live at the skill root)
python3 rag_pipeline_designer.py assets/sample_requirements.json
python3 chunking_optimizer.py assets/corpus
python3 retrieval_evaluator.py assets/sample_queries.json assets/corpus assets/sample_ground_truth.json
```

```bash
python3 rag_pipeline_designer.py assets/flawed_requirements.json   # exit 2: accuracy_priority must be a number
```

The evaluator's built-in TF-IDF baseline gets Precision@1 of 0.50 on the sample: two of four plain-language queries miss on wording, which is the gap dense or hybrid retrieval should close.

## Tools Overview

| Tool | Purpose | Key flags | Exit codes |
|------|---------|-----------|------------|
| `chunking_optimizer.py` | Runs 12 chunking configurations over a document directory and recommends one with parameters | `directory`, `--config`, `--extensions`, `--output`, `--verbose` | 0 report; 2 missing directory or unreadable input |
| `retrieval_evaluator.py` | Precision@K, Recall@K, MRR, NDCG and failure analysis for a query set against a corpus (TF-IDF baseline retriever) | `queries corpus ground_truth`, `--k-values 1 5 10`, `--output`, `--verbose` | 0 report; 2 unreadable input |
| `rag_pipeline_designer.py` | Component picks, monthly cost estimate, Mermaid diagram and config templates from requirements | `requirements`, `--output`, `--verbose` | 0 design; 2 invalid requirements |

Requirements fields: `document_types` (list), `document_count`, `avg_document_size` (characters), `queries_per_day` (integers), `query_patterns` (list), `latency_requirement`, `budget_monthly` (number), `accuracy_priority` and `cost_priority` (numbers from 0 to 1), `maintenance_complexity` (`low`, `medium` or `high`). Embedding prices in the designer are OpenAI's published rates as of 2026-11 ($0.02 per 1M tokens for `text-embedding-3-small`, $0.13 per 1M for `text-embedding-3-large`); check the provider's pricing page before quoting a cost. Full flags: [references/tool-cli-reference.md](references/tool-cli-reference.md).

## Anti-Patterns

**Mistake:** Choosing the embedding model from a leaderboard.
**Why it matters:** Generic benchmark rank often does not hold on a specific corpus, and a wrong pick means re-embedding everything later.
**Instead:** Shortlist from the leaderboard, then decide with `retrieval_evaluator.py` on your own queries.

**Mistake:** Tuning prompts when answers are wrong, before checking retrieval.
**Why it matters:** If the right chunk is not in the context, no prompt can recover it.
**Instead:** Check Recall@k first; fix retrieval, then generation.

**Mistake:** Changing chunking or the model without re-running the evaluation.
**Why it matters:** Retrieval quality regresses silently, and users notice before the team does.
**Instead:** Keep the ground truth in the repo and gate pipeline changes on the evaluator's scores.

## Reference Documentation

- **[references/rag-design-guide.md](references/rag-design-guide.md)**: the design workflow, selection matrices (chunking, embedding, vector DB, retrieval, query transforms), context-window optimization and production patterns.
- **[references/embedding_model_benchmark.md](references/embedding_model_benchmark.md)**: embedding model families, selection criteria, and how to decide on your own data.
- **[references/chunking_strategies_comparison.md](references/chunking_strategies_comparison.md)**: the chunking strategies compared, with domain recommendations.
- **[references/rag_evaluation_framework.md](references/rag_evaluation_framework.md)**: retrieval, generation and end-to-end evaluation methods.
- **[references/tool-cli-reference.md](references/tool-cli-reference.md)**: full flag tables and output formats for the three tools.

## Files

| File | Purpose |
|------|---------|
| `chunking_optimizer.py`, `retrieval_evaluator.py`, `rag_pipeline_designer.py` | Stdlib CLIs at the skill root |
| `assets/corpus/` | Four short help-center articles |
| `assets/sample_queries.json`, `assets/sample_ground_truth.json` | Four queries and their relevant documents |
| `assets/sample_requirements.json` | Valid requirements for a 12,000-document help center |
| `assets/flawed_requirements.json` | `accuracy_priority` given as text; the designer exits 2 |

## Scope & Limitations

**Covers:** RAG architecture from chunking to evaluation; quantitative chunking analysis; IR-metric evaluation with a TF-IDF baseline; automated first-pass designs with cost estimates.

**Does not cover:**
- Prompt design for the generation step (see `engineering/prompt-engineer-toolkit`).
- Metadata store schema design (see `engineering/database-designer`).
- Production monitoring (see `engineering/observability-designer`).
- Agent workflows built on retrieval (see `engineering/agent-workflow-designer`).
- Running embeddings: the tools make no model or network calls, so dense retrieval must be evaluated with your own embedding code.
