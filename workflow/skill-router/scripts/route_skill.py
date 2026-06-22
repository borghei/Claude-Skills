#!/usr/bin/env python3
"""Route a free-text intent to the best-fit skill(s) in the library.

Scores every skill in the generated catalog (cli/skills.json) by term overlap
between the user's query and the skill's name, tags, domain, and description,
weighting exact name/tag matches highest. Standard library only; no network or
LLM calls — the ranking is deterministic.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

# Tokens too common to carry routing signal.
STOPWORDS = {
    "a", "an", "the", "to", "for", "of", "and", "or", "in", "on", "with", "my",
    "me", "i", "we", "our", "this", "that", "it", "is", "are", "do", "does",
    "how", "what", "which", "need", "want", "help", "should", "use", "using",
    "new", "create", "make", "get", "find", "skill",
}

WEIGHTS = {"name": 5.0, "tags": 3.0, "domain": 2.0, "description": 1.0}
# A verbatim multi-word phrase match is far stronger signal than scattered tokens.
PHRASE_BONUS = 6.0


def tokenize(text: str) -> set[str]:
    return {t for t in re.split(r"[^a-z0-9]+", text.lower()) if t and t not in STOPWORDS}


def normalize(text: str) -> str:
    """Lowercase and reduce to space-separated alphanumerics so phrase matching is
    robust to hyphen/slash/space differences (e.g. 'go-to-market' == 'go to market')."""
    return " ".join(re.split(r"[^a-z0-9]+", text.lower())).strip()


def query_phrases(query_text: str, max_n: int = 4) -> list[str]:
    """Contiguous 2..max_n word shingles of the raw query (stopwords kept, since
    they matter inside a phrase like 'go to market')."""
    words = [w for w in re.split(r"[^a-z0-9]+", query_text.lower()) if w]
    phrases = []
    for n in range(2, max_n + 1):
        for i in range(len(words) - n + 1):
            shingle = words[i:i + n]
            # Skip phrases with no content word (e.g. "for a", "a new") — pure noise.
            if all(w in STOPWORDS for w in shingle):
                continue
            phrases.append(" ".join(shingle))
    return phrases


def find_catalog(explicit: str | None) -> str:
    if explicit:
        return explicit
    here = os.path.dirname(os.path.abspath(__file__))
    # Walk up to a repo root that contains cli/skills.json.
    d = here
    for _ in range(8):
        cand = os.path.join(d, "cli", "skills.json")
        if os.path.isfile(cand):
            return cand
        d = os.path.dirname(d)
    return os.path.join(os.getcwd(), "cli", "skills.json")


def score_skill(query: set[str], phrases: list[str], skill: dict) -> tuple[float, list[str]]:
    fields = {
        "name": skill.get("name", "").replace("-", " "),
        "tags": " ".join(skill.get("tags", [])),
        "domain": skill.get("domain", "").replace("-", " "),
        "description": skill.get("description", ""),
    }
    total = 0.0
    hits: list[str] = []
    for field, text in fields.items():
        overlap = query & tokenize(text)
        if overlap:
            total += WEIGHTS[field] * len(overlap)
            hits.extend(sorted(overlap))
    # Phrase bonus: a verbatim multi-word phrase in name/tags/description is a strong hit.
    blob = normalize(" ".join(fields.values()))
    for ph in phrases:
        if ph in blob:
            total += PHRASE_BONUS * len(ph.split())
            hits.append(f'"{ph}"')
    # De-dup the reason terms, preserve a stable order.
    seen, reasons = set(), []
    for h in hits:
        if h not in seen:
            seen.add(h)
            reasons.append(h)
    return total, reasons


def route(query_text: str, catalog_path: str, top: int, domain: str | None) -> list[dict]:
    with open(catalog_path, encoding="utf-8") as fh:
        data = json.load(fh)
    skills = data["skills"] if isinstance(data, dict) else data
    query = tokenize(query_text)
    phrases = query_phrases(query_text)

    ranked = []
    for s in skills:
        if domain and s.get("domain") != domain:
            continue
        score, reasons = score_skill(query, phrases, s)
        if score > 0:
            ranked.append({
                "name": s.get("name"),
                "domain": s.get("domain"),
                "path": s.get("path"),
                "score": round(score, 1),
                "matched": reasons,
                "description": s.get("description", ""),
            })
    ranked.sort(key=lambda r: (-r["score"], r["name"] or ""))
    return ranked[:top]


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Recommend the best-fit skill(s) for an intent.")
    p.add_argument("query", help="The user's goal, in plain language (quote it).")
    p.add_argument("--top", type=int, default=3, help="How many candidates to return (default: 3).")
    p.add_argument("--domain", help="Restrict matches to one domain (e.g. finance).")
    p.add_argument("--catalog", help="Path to skills.json (default: auto-discover cli/skills.json).")
    p.add_argument("--format", choices=["text", "json"], default="text")
    args = p.parse_args(argv)

    catalog = find_catalog(args.catalog)
    if not os.path.isfile(catalog):
        print(f"error: catalog not found at '{catalog}'. "
              f"Pass --catalog or run scripts/build_manifest.py.", file=sys.stderr)
        return 2

    results = route(args.query, catalog, args.top, args.domain)

    if args.format == "json":
        print(json.dumps(results, indent=2))
        return 0

    if not results:
        print(f'No strong match for: "{args.query}"')
        print("Consider rephrasing the goal, or browse domains in CLAUDE.md.")
        return 0

    if results[0]["score"] < PHRASE_BONUS:
        print('Note: no strong match — these are weak, keyword-only hits. '
              'Consider rephrasing the goal or browsing CLAUDE.md.\n')
    print(f'Top {len(results)} skill(s) for: "{args.query}"\n')
    for i, r in enumerate(results, 1):
        print(f"{i}. {r['name']}  ({r['domain']})  score={r['score']}")
        print(f"   path: {r['path']}")
        print(f"   matched on: {', '.join(r['matched'])}")
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
