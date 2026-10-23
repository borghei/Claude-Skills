#!/usr/bin/env python3
"""Plan a RAG pipeline from a JSON spec with rule-based, explained choices.

From corpus size and document types, query volume, latency budget, embedding
dimension and update frequency it decides chunking (strategy, size, overlap
per document type), index type with a memory estimate, retrieval settings
(dense or hybrid, candidates, reranking, final top-k), the update strategy and
an evaluation plan. Writes rag_config.json and pipeline_plan.md into --output.

Usage:
    python rag_system_builder.py --input rag_spec.json --output rag-plan/
    python rag_system_builder.py --example > rag_spec.json
"""

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

EXAMPLE_SPEC: Dict[str, Any] = {
    "name": "support-kb",
    "corpus": {"documents": 120000, "avg_doc_tokens": 1800,
               "doc_types": {"markdown": 0.6, "pdf": 0.3, "faq": 0.1}},
    "queries_per_day": 40000, "peak_to_average": 4, "latency_budget_ms": 600,
    "embedding_dim": 1024, "update_frequency": "daily", "exact_match_terms": True,
    "context_tokens": 4000, "memory_budget_gb": 16,
}
# type: (strategy, size_tokens, overlap_tokens, reason)
PROFILES: Dict[str, Tuple[str, int, int, str]] = {
    "text": ("recursive (paragraph, then sentence)", 512, 64, "keeps paragraphs whole; general default"),
    "markdown": ("structure-aware on headings", 512, 64, "headings are natural topic boundaries; keep the heading path as metadata"),
    "html": ("structure-aware on headings after boilerplate removal", 512, 64, "nav and footer text pollutes embeddings"),
    "pdf": ("recursive after layout extraction", 768, 96, "strip page headers and footers first; larger chunks absorb broken lines"),
    "code": ("syntax-aware (function or class)", 384, 0, "split on definitions; overlap would duplicate code"),
    "legal": ("section or clause", 1024, 128, "clauses cross-reference each other; keep numbered sections whole"),
    "faq": ("one question-answer pair per chunk", 256, 0, "each answer is a self-contained unit"),
    "scientific": ("section-aware with semantic splits", 768, 96, "methods and results need surrounding context"),
    "chat": ("thread window of consecutive turns", 384, 64, "single turns lack context; whole threads mix topics"),
    "table": ("row groups with the header repeated", 512, 0, "rows without headers are meaningless"),
}
ALIASES = {"docs": "markdown", "md": "markdown", "txt": "text", "contracts": "legal", "papers": "scientific",
           "tickets": "chat", "csv": "table", "source": "code", "web": "html"}
UPDATES = {
    "realtime": "streaming upserts from a change queue; ids are doc_id#chunk_n so a document is replaced or deleted as a unit",
    "hourly": "incremental batch: hash each document, re-chunk and re-embed only changed ones, delete removed ids",
    "daily": "incremental batch: hash each document, re-chunk and re-embed only changed ones, delete removed ids",
    "weekly": "full rebuild into a new index, validate with the eval set, then swap an alias (blue/green)",
    "static": "build once; rebuild only when the chunking or embedding model changes",
}


def pos_number(v: Any, field: str, integer: bool = False) -> Any:
    """Return v if it is a positive number (an integer when integer=True), else raise ValueError."""
    ok = not isinstance(v, bool) and isinstance(v, (int, float)) and v > 0 and (not integer or v == int(v))
    if not ok:
        raise ValueError(f"{field} must be a positive {'integer' if integer else 'number'}, got {v!r}")
    return int(v) if integer else v


def chunking(corpus: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], int]:
    """Choose a chunking profile per document type and estimate the chunk count."""
    types = corpus.get("doc_types") or ["text"]
    if isinstance(types, str):
        types = [types]
    if isinstance(types, list):
        if not all(isinstance(t, str) for t in types):
            raise ValueError("corpus.doc_types list must contain type names (strings)")
        types = {t: 1.0 for t in types}
    if not isinstance(types, dict):
        raise ValueError("corpus.doc_types must be a type name, a list of names or a map of name to share")
    for t, v in types.items():
        if isinstance(v, bool) or not isinstance(v, (int, float)) or v <= 0:
            raise ValueError(f"corpus.doc_types share for '{t}' must be a positive number, got {v!r}")
    shares, total = types, sum(types.values())
    docs = pos_number(corpus["documents"], "corpus.documents", integer=True)
    avg = pos_number(corpus.get("avg_doc_tokens", 800), "corpus.avg_doc_tokens", integer=True)
    plan, chunks = [], 0
    for raw, share in shares.items():
        t = ALIASES.get(str(raw).lower(), str(raw).lower())
        if t not in PROFILES:
            raise ValueError(f"unknown doc type '{raw}' (known: {', '.join(sorted(PROFILES))})")
        strategy, size, overlap, why = PROFILES[t]
        whole = avg <= size * 1.2
        per_doc = 1 if whole else math.ceil((avg - overlap) / (size - overlap))
        n = round(docs * share / total)
        chunks += n * per_doc
        plan.append({"doc_type": t, "share": round(share / total, 3), "strategy": strategy,
                     "chunk_tokens": avg if whole else size, "overlap_tokens": 0 if whole else overlap,
                     "chunks_per_doc": per_doc, "reason": why + ("; documents are short enough to embed whole"
                                                                if whole else "")})
    return plan, chunks


def index_choice(n: int, dim: int, budget_gb: float, update: str) -> Dict[str, Any]:
    """Pick flat, HNSW, quantized HNSW or IVF-PQ from vector count and memory."""
    gb = lambda b: round(b / 1024 ** 3, 2)
    raw = n * dim * 4
    m = 16 if n < 1_000_000 else 32
    hnsw = raw + n * m * 2 * 4
    hnsw_int8 = n * dim + n * m * 2 * 4
    est = {"float32_vectors_gb": gb(raw), "hnsw_gb": gb(hnsw), "hnsw_int8_gb": gb(hnsw_int8),
           "ivf_pq_gb": gb(n * (dim // 8 + 8))}
    budget = budget_gb * 1024 ** 3
    if n < 50_000:
        choice = {"type": "flat (exact)", "params": {},
                  "reason": f"{n:,} vectors is small enough for exact search: perfect recall and no index to tune"}
    elif hnsw * 1.2 <= budget:
        choice = {"type": "HNSW", "params": {"M": m, "ef_construction": 200},
                  "reason": f"graph index fits in memory ({est['hnsw_gb']} GB of {budget_gb} GB with 20% headroom); "
                            "best recall/latency tradeoff and supports incremental inserts"}
    elif hnsw_int8 * 1.2 <= budget:
        choice = {"type": "HNSW with int8 scalar quantization", "params": {"M": m, "ef_construction": 200},
                  "reason": f"float32 HNSW needs {est['hnsw_gb']} GB, over the {budget_gb} GB budget; int8 cuts "
                            "vector memory 4x for a small recall loss (rescore top candidates with full vectors)"}
    else:
        nlist = 2 ** round(math.log2(max(4 * math.sqrt(n), 64)))
        choice = {"type": "IVF-PQ (or a disk-based graph index)",
                  "params": {"nlist": nlist, "nprobe": max(8, nlist // 64), "pq_bytes": dim // 8},
                  "reason": f"even int8 HNSW ({est['hnsw_int8_gb']} GB) exceeds {budget_gb} GB; product quantization "
                            "trades recall for memory, so tune nprobe against the eval set"}
        if update in ("realtime", "hourly"):
            choice["reason"] += "; frequent updates drift from the trained centroids, so retrain them on a schedule"
    choice["memory_estimate"] = est
    return choice


def retrieval_settings(budget_ms: int, plan: List[Dict[str, Any]], exact: bool, ctx: int, peak_qps: float) -> Dict[str, Any]:
    """Decide dense vs hybrid, candidate count, reranking and final top-k."""
    types = {p["doc_type"] for p in plan}
    structured = sorted(types & {"code", "legal", "table"})
    hybrid = exact or bool(structured)
    why = (["the spec says queries carry exact identifiers"] if exact else []) + \
          [f"{t} content needs lexical match" for t in structured]
    avg_chunk = sum(p["chunk_tokens"] * p["share"] for p in plan)
    notes = []
    if budget_ms < 150:
        rerank, cand, k = False, 20, 5
        notes.append(f"{budget_ms} ms leaves no room for a cross-encoder; first-stage ranking and chunking carry precision")
    elif budget_ms <= 400:
        rerank, cand, k = True, 20 if avg_chunk > 700 else 30, 5
        notes.append("rerank a short candidate list; cross-encoder cost grows with candidates times chunk length")
    else:
        rerank, cand, k = True, 50, 8
        notes.append("budget allows reranking a wide candidate list, which usually gives the largest precision gain")
    fit = max(3, int(ctx // max(avg_chunk, 1)))
    if k > fit:
        notes.append(f"final top-k cut from {k} to {fit} so chunks fit the {ctx}-token context budget")
        k = fit
    if not rerank and not hybrid:
        cand = k
    if rerank and peak_qps > 100:
        notes.append(f"peak {peak_qps:.0f} QPS with reranking: batch the reranker on GPU or lower candidates")
    return {"mode": "hybrid (BM25 + dense, reciprocal rank fusion, k=60)" if hybrid else "dense",
            "mode_reason": ("; ".join(why) + "; BM25 catches exact tokens that embeddings blur"
                            if hybrid else "natural-language queries over prose; dense retrieval alone is enough"),
            "candidates": cand, "rerank": rerank, "final_top_k": k, "ef_search": max(64, 2 * cand), "notes": notes}


def build(spec: Dict[str, Any]) -> Dict[str, Any]:
    """Validate the spec and assemble the full plan."""
    corpus = spec.get("corpus")
    if not isinstance(corpus, dict) or not corpus.get("documents"):
        raise ValueError("spec needs corpus.documents (number of documents)")
    dim = pos_number(spec.get("embedding_dim", 768), "embedding_dim", integer=True)
    budget = pos_number(spec.get("latency_budget_ms", 500), "latency_budget_ms", integer=True)
    update = spec.get("update_frequency", "daily")
    if not isinstance(update, str) or update.lower() not in UPDATES:
        raise ValueError(f"update_frequency must be one of {', '.join(UPDATES)}")
    update = update.lower()
    qpd = pos_number(spec.get("queries_per_day", 1000), "queries_per_day")
    peak = qpd / 86400 * pos_number(spec.get("peak_to_average", 3), "peak_to_average")
    mem = pos_number(spec.get("memory_budget_gb", 32), "memory_budget_gb")
    ctx = pos_number(spec.get("context_tokens", 4000), "context_tokens", integer=True)
    exact = spec.get("exact_match_terms", False)
    if not isinstance(exact, bool):
        raise ValueError("exact_match_terms must be true or false")
    plan, n_chunks = chunking(corpus)
    index = index_choice(n_chunks, dim, float(mem), update)
    ret = retrieval_settings(budget, plan, exact, ctx, peak)
    emb_notes = []
    if dim > 1024 and n_chunks > 5_000_000:
        emb_notes.append(f"{dim} dims at {n_chunks:,} chunks is memory-heavy; prefer a model that supports "
                         "truncated (Matryoshka) embeddings or quantize")
    if dim < 384:
        emb_notes.append(f"{dim} dims is compact but usually loses recall on nuanced queries; validate on the eval set")
    emb_notes.append("pin the embedding model version; changing it means re-embedding everything into a new index")
    scaling = ("single index replica is enough" if peak < 50 else
               "run 2+ index replicas behind a load balancer and cache embeddings of repeated queries" if peak < 500
               else "shard the index and replicate each shard; cache hot queries")
    golden = max(50, min(500, math.ceil(math.sqrt(int(corpus["documents"])))))
    k = ret["final_top_k"]
    return {"name": spec.get("name", "rag-system"), "estimated_chunks": n_chunks,
            "peak_qps": round(peak, 2), "chunking": plan, "embedding": {"dimension": dim, "notes": emb_notes},
            "index": index, "retrieval": ret, "scaling": scaling,
            "updates": {"frequency": update, "strategy": UPDATES[update]},
            "evaluation": {"golden_queries": golden,
                           "sampling": "real queries from logs, stratified by doc type, each labelled with relevant chunk ids",
                           "metrics": [f"Recall@{ret['candidates']} (retriever ceiling before rerank)", f"Recall@{k}",
                                       f"MRR@{k}", f"nDCG@{k}", "context precision (sampled review)",
                                       "answer faithfulness (sampled review)", f"p95 retrieval latency vs {budget} ms"],
                           "starting_targets": {f"recall_at_{k}": 0.8, f"mrr_at_{k}": 0.6},
                           "when": "before launch and on every change to chunking, embedding model, index params or top-k",
                           "ablations": ["dense vs hybrid", "with vs without rerank", "chunk size -25% / +25%"]}}


def plan_markdown(p: Dict[str, Any]) -> str:
    """Render the pipeline skeleton as a readable markdown plan."""
    r, ix, ev = p["retrieval"], p["index"], p["evaluation"]
    lines = [f"# RAG pipeline plan: {p['name']}", "",
             f"Estimated chunks: {p['estimated_chunks']:,}. Peak load: {p['peak_qps']} QPS.", "",
             "## Pipeline stages", "",
             "1. Ingest: pull source documents and record doc_id, source, updated_at, content hash.",
             "2. Parse: extract text per type (layout extraction for PDF, boilerplate removal for HTML).",
             "3. Chunk: route each document to its chunker (table below); store the parent doc_id and heading path.",
             f"4. Embed: {p['embedding']['dimension']}-dim model, batch requests, store model version with each vector.",
             f"5. Index: {ix['type']} {json.dumps(ix['params'])}.",
             f"6. Retrieve: {r['mode']}, {r['candidates']} candidates.",
             f"7. Rerank: {'cross-encoder over the candidates' if r['rerank'] else 'skipped (latency budget)'}.",
             f"8. Assemble context: top {r['final_top_k']} chunks with source citations.",
             f"9. Update: {p['updates']['strategy']}.", "",
             "## Chunking", "", "| Doc type | Share | Strategy | Tokens | Overlap | Why |", "|---|---|---|---|---|---|"]
    lines += [f"| {c['doc_type']} | {c['share']} | {c['strategy']} | {c['chunk_tokens']} | {c['overlap_tokens']} "
              f"| {c['reason']} |" for c in p["chunking"]]
    lines += ["", "## Index", "", ix["reason"] + ".", "",
              "Memory estimate (GB): " + ", ".join(f"{k} {v}" for k, v in ix["memory_estimate"].items()) + ".",
              "", "## Retrieval", "", r["mode_reason"] + "."] + [f"- {n}" for n in r["notes"]]
    lines += ["", "## Embedding", ""] + [f"- {n}" for n in p["embedding"]["notes"]]
    lines += ["", "## Scaling", "", p["scaling"] + ".", "", "## Evaluation", "",
              f"Golden set: {ev['golden_queries']} queries, {ev['sampling']}.", ""] + [f"- {m}" for m in ev["metrics"]]
    lines += ["", f"Starting targets (calibrate on your data): {json.dumps(ev['starting_targets'])}.",
              f"Run {ev['when']}.", "Ablations: " + "; ".join(ev["ablations"]) + "."]
    return "\n".join(lines) + "\n"


def output(p: Dict[str, Any], fmt: str) -> None:
    """Print the plan as JSON or as a readable summary."""
    if fmt == "json":
        print(json.dumps(p, indent=2))
        return
    r, ix = p["retrieval"], p["index"]
    print(f"RAG plan for {p['name']}: ~{p['estimated_chunks']:,} chunks, peak {p['peak_qps']} QPS")
    for c in p["chunking"]:
        print(f"  chunk {c['doc_type']:<10} {c['strategy']}, {c['chunk_tokens']} tokens / {c['overlap_tokens']} overlap")
    print(f"Index: {ix['type']} {json.dumps(ix['params'])}\n  why: {ix['reason']}")
    print(f"Retrieval: {r['mode']}; {r['candidates']} candidates, rerank {'yes' if r['rerank'] else 'no'}, "
          f"top-k {r['final_top_k']}\n  why: {r['mode_reason']}")
    for n in r["notes"] + p["embedding"]["notes"]:
        print(f"  note: {n}")
    print(f"Scaling: {p['scaling']}\nUpdates ({p['updates']['frequency']}): {p['updates']['strategy']}")
    print(f"Evaluation: {p['evaluation']['golden_queries']} golden queries; " + ", ".join(p["evaluation"]["metrics"][:4]))
    for path in p.get("written", []):
        print(f"wrote {path}")


def main() -> None:
    """Parse arguments, build the plan and write files."""
    ap = argparse.ArgumentParser(description="Rule-based RAG pipeline plan (chunking, index, retrieval, updates, "
                                 "evaluation) from a JSON spec; writes rag_config.json and pipeline_plan.md.")
    ap.add_argument("--input", "-i", help="RAG spec JSON (see --example)")
    ap.add_argument("--output", "-o", help="directory for rag_config.json and pipeline_plan.md (omit to print only)")
    ap.add_argument("--force", action="store_true", help="overwrite existing files in --output")
    ap.add_argument("--format", choices=["text", "json"], default="text", help="report format (default text)")
    ap.add_argument("--example", action="store_true", help="print a sample spec and exit")
    args = ap.parse_args()
    if args.example:
        print(json.dumps(EXAMPLE_SPEC, indent=2))
        return
    if not args.input:
        ap.error("--input is required (or use --example)")
    try:
        spec = json.loads(Path(args.input).read_text(encoding="utf-8"))
        if not isinstance(spec, dict):
            raise ValueError("spec must be a JSON object")
        plan = build(spec)
        if args.output:
            out = Path(args.output)
            files = {"rag_config.json": json.dumps(plan, indent=2) + "\n", "pipeline_plan.md": plan_markdown(plan)}
            existing = [n for n in files if (out / n).exists()]
            if existing and not args.force:
                raise FileExistsError(f"{out} already has {', '.join(existing)}; pass --force to overwrite")
            out.mkdir(parents=True, exist_ok=True)
            for name, text in files.items():
                (out / name).write_text(text, encoding="utf-8")
            plan["written"] = [str(out / n) for n in files]
        output(plan, args.format)
    except FileNotFoundError:
        sys.exit(f"error: input file not found: {args.input}")
    except json.JSONDecodeError as exc:
        sys.exit(f"error: {args.input} is not valid JSON ({exc.msg} at line {exc.lineno})")
    except (ValueError, TypeError, AttributeError, KeyError, FileExistsError, OSError) as exc:
        sys.exit(f"error: {exc}")


if __name__ == "__main__":
    main()
