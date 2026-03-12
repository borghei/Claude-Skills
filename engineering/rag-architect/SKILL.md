---
name: rag-architect
description: >
  Designs production-grade RAG pipelines with chunking optimization, retrieval
  evaluation, and pipeline architecture. Use when building a RAG system,
  selecting a chunking strategy, choosing a vector database, optimizing
  retrieval quality, designing embedding pipelines, or evaluating RAG
  performance with RAGAS metrics.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  category: engineering
  domain: ai-ml
  tier: POWERFUL
---

# RAG Architect

The agent designs, implements, and optimizes production-grade Retrieval-Augmented Generation pipelines, covering the full lifecycle from document chunking through evaluation.

## Workflow

1. **Analyse corpus** -- Profile the document collection: count, average length, format mix (PDF, HTML, Markdown), language(s), and domain. Validate that sample documents are accessible before proceeding.
2. **Select chunking strategy** -- Choose from the Chunking Strategy Matrix based on corpus characteristics. Set chunk size, overlap, and boundary rules. Run a test split on 100 sample documents.
3. **Choose embedding model** -- Select an embedding model from the Embedding Model table based on domain, latency budget, and cost constraints. Verify dimension compatibility with the target vector database.
4. **Select vector database** -- Pick a vector store from the Vector Database Comparison based on scale, query patterns, and operational requirements.
5. **Design retrieval pipeline** -- Configure retrieval strategy (dense, sparse, or hybrid). Add reranking if precision requirements exceed 0.85. Set the top-K parameter and similarity threshold.
6. **Implement query transformations** -- If query-document style mismatch exists, enable HyDE. If queries are ambiguous, enable multi-query generation. Validate each transformation improves retrieval metrics on a held-out set.
7. **Configure guardrails** -- Enable PII detection, toxicity filtering, hallucination detection, and source attribution. Set confidence score thresholds.
8. **Evaluate end-to-end** -- Run the RAGAS evaluation framework. Verify faithfulness > 0.90, context relevance > 0.80, answer relevance > 0.85. Iterate on weak components.

## Chunking Strategy Matrix

| Strategy | Best For | Chunk Size | Overlap | Pros | Cons |
|----------|----------|-----------|---------|------|------|
| Fixed-size (token) | Uniform docs, consistent sizing | 512-2048 tokens | 10-20% | Predictable, simple | Breaks semantic units |
| Sentence-based | Narrative text, articles | 3-8 sentences | 1 sentence | Preserves language boundaries | Variable sizes |
| Paragraph-based | Structured docs, technical manuals | 1-3 paragraphs | 0-1 paragraph | Preserves topic coherence | Highly variable sizes |
| Semantic | Long-form, research papers | Dynamic | Topic-shift detection | Best coherence | Computationally expensive |
| Recursive | Mixed content types | Dynamic, multi-level | Per-level | Optimal utilization | Complex implementation |
| Document-aware | Multi-format collections | Format-specific | Section-level | Preserves metadata | Format-specific code required |

## Embedding Model Comparison

| Model | Dimensions | Speed | Quality | Cost | Best For |
|-------|-----------|-------|---------|------|----------|
| all-MiniLM-L6-v2 | 384 | ~14K tok/s | Good | Free (local) | Prototyping, low-latency |
| all-mpnet-base-v2 | 768 | ~2.8K tok/s | Better | Free (local) | Balanced production use |
| text-embedding-3-small | 1536 | API | High | $0.02/1M tokens | Cost-effective production |
| text-embedding-3-large | 3072 | API | Highest | $0.13/1M tokens | Maximum quality |
| Domain fine-tuned | Varies | Varies | Domain-best | Training cost | Specialized domains (legal, medical) |

## Vector Database Comparison

| Database | Type | Scaling | Key Feature | Best For |
|----------|------|---------|-------------|----------|
| Pinecone | Managed | Auto-scaling | Metadata filtering, hybrid search | Production, managed preference |
| Weaviate | Open source | Horizontal | GraphQL API, multi-modal | Complex data types |
| Qdrant | Open source | Distributed | High perf, low memory (Rust) | Performance-critical |
| Chroma | Embedded | Limited | Simple API, SQLite-backed | Prototyping, small-scale |
| pgvector | PostgreSQL ext | PostgreSQL scaling | ACID, SQL joins | Existing PostgreSQL infra |

## Retrieval Strategies

| Strategy | When to Use | Implementation |
|----------|-------------|---------------|
| Dense (vector similarity) | Default for semantic search | Cosine similarity with k-NN/ANN |
| Sparse (BM25/TF-IDF) | Exact keyword matching needed | Elasticsearch or inverted index |
| Hybrid (dense + sparse) | Best of both needed | Reciprocal Rank Fusion (RRF) with tuned weights |
| + Reranking | Precision must exceed 0.85 | Cross-encoder reranker after initial retrieval |

## Query Transformation Techniques

| Technique | When to Use | How It Works |
|-----------|-------------|-------------|
| HyDE | Query/document style mismatch | LLM generates hypothetical answer; embed that instead of query |
| Multi-query | Ambiguous queries | Generate 3-5 query variations; retrieve for each; deduplicate |
| Step-back | Specific questions needing general context | Transform to broader query; retrieve general + specific |

## Context Window Optimization

- **Relevance ordering**: Most relevant chunks first in the context window
- **Diversity**: Deduplicate semantically similar chunks
- **Token budget**: Fit within model context limit; reserve tokens for system prompt and answer
- **Hierarchical inclusion**: Include section summary before detailed chunks when available
- **Compression**: Summarize low-relevance chunks; extract key facts from verbose passages

## Evaluation Metrics (RAGAS Framework)

| Metric | Target | What It Measures |
|--------|--------|-----------------|
| Faithfulness | > 0.90 | Answers grounded in retrieved context |
| Context Relevance | > 0.80 | Retrieved chunks relevant to query |
| Answer Relevance | > 0.85 | Answer addresses the original question |
| Precision@K | > 0.70 | % of top-K results that are relevant |
| Recall@K | > 0.80 | % of relevant docs found in top-K |
| MRR | > 0.75 | Reciprocal rank of first relevant result |

## Guardrails

- **PII detection**: Scan retrieved chunks and generated responses for PII; redact or block
- **Hallucination detection**: Compare generated claims against source documents via NLI
- **Source attribution**: Every factual claim must cite a retrieved chunk
- **Confidence scoring**: Return confidence level; if below threshold, return "I don't have enough information"
- **Injection prevention**: Sanitize user queries; reject prompt injection attempts

## Example: Internal Knowledge Base RAG Pipeline

```yaml
corpus:
  documents: 12,000 Confluence pages + 3,000 PDFs
  avg_length: 2,400 tokens
  languages: [English]
  domain: internal engineering docs

pipeline:
  chunking:
    strategy: recursive
    max_tokens: 512
    overlap: 50 tokens
    boundary: paragraph
  embedding:
    model: text-embedding-3-small
    dimensions: 1536
    batch_size: 100
  vector_db:
    engine: pgvector
    index: HNSW (ef_construction=128, m=16)
    reason: "Existing PostgreSQL infra; ACID compliance for audit"
  retrieval:
    strategy: hybrid
    dense_weight: 0.7
    sparse_weight: 0.3
    top_k: 10
    reranker: cross-encoder/ms-marco-MiniLM-L-12-v2
    final_k: 5

evaluation_results:
  faithfulness: 0.93
  context_relevance: 0.84
  answer_relevance: 0.88
  precision_at_5: 0.76
  recall_at_10: 0.85
```

## Production Patterns

- **Caching**: Query-level (exact match), semantic (similar queries via embedding distance < 0.05), chunk-level (embedding cache)
- **Streaming**: Stream generation tokens while retrieval completes; show sources after generation
- **Fallbacks**: If primary vector DB is unavailable, serve from read-replica; if retrieval returns no results above threshold, say so explicitly
- **Document refresh**: Incremental re-embedding on change detection; full re-index weekly
- **Cost control**: Batch embeddings, cache aggressively, route simple queries to BM25 only

## Common Pitfalls

| Problem | Solution |
|---------|----------|
| Chunks break mid-sentence | Use boundary-aware chunking with sentence/paragraph overlap |
| Low retrieval precision | Add cross-encoder reranker; tune similarity threshold |
| High latency (> 2s) | Cache embeddings; use faster model; reduce top-K |
| Inconsistent quality | Implement RAGAS evaluation in CI; add quality scoring |
| Scalability bottleneck | Shard vector DB; implement auto-scaling; add caching layer |

## Scripts

### Chunking Optimizer
Analyses corpus and recommends optimal chunking strategy with parameters.

### Retrieval Evaluator
Runs evaluation suite (precision, recall, MRR, NDCG) against a test query set.

### Pipeline Benchmarker
Measures end-to-end latency, throughput, and cost per query across configurations.
