# Choosing an Embedding Model

Read this when picking or replacing the embedding model for a RAG pipeline.

Embedding models change faster than this file. Treat any public leaderboard number as a shortlist filter, never as the decision: scores on generic benchmarks often do not carry over to a specific corpus. The decision comes from running your own queries against your own documents with `retrieval_evaluator.py`.

## Model Families (check current versions before choosing)

| Family | Examples | Hosting | Notes |
|--------|----------|---------|-------|
| OpenAI | `text-embedding-3-small` (1536 dims), `text-embedding-3-large` (3072 dims) | API | The 3-series replaced `text-embedding-ada-002`; both support shortening dimensions. Use the current model list and pricing page. |
| Cohere | Embed (multilingual and English variants) | API | Separate input types for queries and documents; strong multilingual options. |
| Voyage | General and domain models (code, legal, finance) | API | Domain-tuned variants are worth testing for specialist corpora. |
| Open-weight | BGE, E5, GTE, Nomic, `all-mpnet-base-v2`, `all-MiniLM-L6-v2` | Self-hosted | No per-token cost, data stays in-house; small models trade quality for speed. |

The MTEB leaderboard (retrieval tasks) is a reasonable place to build a shortlist. Filter by the languages and document lengths you have, and by the dimension count your vector store can afford.

## Selection Criteria

1. **Language and domain:** multilingual corpora need a multilingual model; code, legal or medical text may justify a domain model.
2. **Context length:** the model's maximum input must exceed your chunk size, or chunks are silently truncated.
3. **Dimensions and storage:** vectors cost `count x dimensions x 4 bytes` (float32) before index overhead. Shortened dimensions or quantization cut this, at some recall cost.
4. **Cost:** API price per million tokens times (corpus tokens + monthly query tokens); re-embedding the corpus on a model change is a one-off cost to budget.
5. **Data residency:** if documents may not leave your infrastructure, only self-hosted models qualify.
6. **Latency:** query embedding sits on the request path; measure p95 from your region.

## How to Decide

1. Shortlist two or three models from the table and the leaderboard.
2. Build a ground-truth set: 50 or more real queries with the documents that answer them (shape: `assets/sample_queries.json` and `assets/sample_ground_truth.json`).
3. Embed the same chunked corpus with each candidate and run retrieval for every query.
4. Compare Precision@k, Recall@k, MRR and NDCG with `retrieval_evaluator.py`; also check the worst queries by hand.
5. Pick the cheapest model within a small margin of the best on your metric, then record the model id, version and date in the design so a later change is deliberate.

## Switching Models

Vectors from different models are not comparable. A model change means re-embedding the whole corpus into a new index, running the evaluation on both, and cutting traffic over only when the new index matches or beats the old one.
