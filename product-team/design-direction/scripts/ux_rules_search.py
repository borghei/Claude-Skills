#!/usr/bin/env python3
"""Search the bundled design knowledge: UX rules, chart choices, stack notes, directions,
palettes, type pairings, product types, page patterns and motion by interaction.

Usage:
  python3 ux_rules_search.py --query "form errors"
  python3 ux_rules_search.py --domain rules --category accessibility --min-severity high
  python3 ux_rules_search.py --domain charts --query "share of revenue by plan"
  python3 ux_rules_search.py --domain palettes --query "dark fintech" --format json
  python3 ux_rules_search.py --domain patterns --query "pricing page"
  python3 ux_rules_search.py --domain motion --query "modal"
  python3 ux_rules_search.py --list

Exit codes: 0 results found, 1 no matches, 2 bad arguments or unreadable data.
"""
import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

REF = Path(__file__).resolve().parent.parent / "references"
FILES = {"rules": "ux-rules.json", "charts": "charts.json", "stacks": "stacks.json", "directions": "directions.json",
         "palettes": "palettes.json", "pairings": "type-pairings.json", "products": "product-types.json",
         "patterns": "page-patterns.json", "motion": "motion.json"}
STOP = {"a", "an", "and", "the", "for", "of", "to", "in", "on", "with", "or", "is", "our", "we", "app", "that", "by", "at",
        "how", "what", "do", "does", "my", "vs"}


class SearchError(Exception):
    """Bad arguments or unreadable bundled data; exits 2."""


class _Data:
    """Bundled reference data, loaded on first use and cached."""

    def __init__(self) -> None:
        self.SEVERITY_RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        self.DataError = SearchError
        self._cache: Dict[str, List[Dict[str, Any]]] = {}

    def load(self, kind: str) -> List[Dict[str, Any]]:
        """Rows of one bundled reference file."""
        if kind not in self._cache:
            try:
                self._cache[kind] = json.loads((REF / FILES[kind]).read_text(encoding="utf-8"))[kind]
            except (OSError, ValueError, KeyError) as exc:
                raise SearchError(f"bundled data {FILES[kind]} unreadable: {exc}") from exc
        return self._cache[kind]

    @staticmethod
    def words(text: str) -> List[str]:
        """Lower-case word stems without stopwords."""
        out = []
        for w in re.findall(r"[a-z0-9]+", text.lower().replace("color", "colour").replace("gray", "grey")):  # UK/US spelling
            if w in STOP:
                continue
            w = w[:-3] + "y" if len(w) > 4 and w.endswith("ies") else w
            w = w[:-2] if len(w) > 4 and re.search(r"(ch|sh|x|ss)es$", w) else w
            out.append(w[:-3] if len(w) > 5 and w.endswith("ing") else
                       (w[:-1] if len(w) > 4 and w.endswith("s") and not w.endswith("ss") else w))
        return out

    def match_score(self, query: str, phrases: List[str], extra: str = "") -> int:
        """+3 per whole phrase found in the query, +1 per shared word stem."""
        q = " " + " ".join(re.findall(r"[a-z0-9]+", query.lower())) + " "
        hits = sum(3 for p in phrases if " " + " ".join(re.findall(r"[a-z0-9]+", p.lower())) + " " in q)
        return hits + len(set(self.words(query)) & set(self.words(" ".join(phrases) + " " + extra)))

    @staticmethod
    def contrast(a: str, b: str) -> float:
        """WCAG 2.x contrast ratio between two #RRGGBB colours."""
        def lum(v: str) -> float:
            c = [int(v.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4)]
            c = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
            return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
        return round((max(lum(a), lum(b)) + 0.05) / (min(lum(a), lum(b)) + 0.05), 2)


dd = _Data()
DOMAINS = ("rules", "charts", "stacks", "directions", "palettes", "pairings", "products", "patterns", "motion")
# Fields that carry each domain's searchable text, and the keyword-like field used for phrase hits.
TEXT_FIELDS = {
    "rules": (["rule", "why", "check", "category", "id"], None),
    "charts": (["question", "best", "avoid_when", "a11y", "id"], "keywords"),
    "stacks": (["name", "notes", "id"], "keywords"),
    "directions": (["name", "summary", "signatures", "best_for", "pitfalls", "id"], "best_for"),
    "palettes": (["name", "summary", "id"], "tags"),
    "pairings": (["display", "body", "why", "best_for", "kind", "id"], "moods"),
    "products": (["name", "risks", "avoid", "id"], "keywords"),
    "patterns": (["name", "kind", "sections", "cta", "id"], "keywords"),
    "motion": (["name", "animate", "rule", "id"], "keywords"),
}


def flatten(row: Dict[str, Any], fields: List[str]) -> str:
    """Join the searchable fields of a row into one string."""
    parts = []
    for f in fields:
        v = row.get(f, "")
        parts.append(" ".join(v) if isinstance(v, list) else str(v))
    return " ".join(parts)


def search(domain: str, query: str, category: str, min_sev: str, platform: str) -> List[Tuple[int, Dict[str, Any]]]:
    """Score and filter one domain; an empty query returns every row passing the filters."""
    fields, phrase_field = TEXT_FIELDS[domain]
    floor = 2 if len(dd.words(query)) >= 2 else 1
    hits = []
    for row in dd.load(domain):
        if domain == "rules":
            if category and row["category"] != category:
                continue
            if min_sev and dd.SEVERITY_RANK[row["severity"]] > dd.SEVERITY_RANK[min_sev]:
                continue
            if platform and row["platform"] not in ("all", platform):
                continue
        if domain == "stacks" and platform and row["platform"] != platform:
            continue
        phrases = row.get(phrase_field, []) if phrase_field else []
        score = dd.match_score(query, phrases, flatten(row, fields)) if query else 1
        if query and row["id"].lower() == query.lower():
            score += 10
        if score >= floor or (not query and score > 0):
            hits.append((score, row))
    hits.sort(key=lambda h: (-h[0], dd.SEVERITY_RANK.get(h[1].get("severity", "low"), 3)))
    return hits


def line(domain: str, row: Dict[str, Any]) -> str:
    """One-row text rendering per domain."""
    if domain == "rules":
        return f"{row['id']:8} {row['severity']:8} {row['platform']:6} {row['rule']}\n{'':24}check: {row['check']}"
    if domain == "charts":
        return f"{row['id']:14} {row['question']}\n{'':15}use: {row['best']}; avoid when {row['avoid_when']}; a11y: {row['a11y']}"
    if domain == "stacks":
        return f"{row['name']} ({row['platform']})\n" + "\n".join(f"{'':4}- {n}" for n in row["notes"])
    if domain == "directions":
        return f"{row['id']:22} {row['summary']}\n{'':23}best for: {', '.join(row['best_for'])}"
    if domain == "palettes":
        light = row["light"]
        return (f"{row['id']:14} {row['summary']}\n{'':15}light bg {light['bg']} fg {light['fg']} primary {light['primary']}; "
                f"fg/bg {dd.contrast(light['fg'], light['bg'])}:1, on-primary {dd.contrast(light['on_primary'], light['primary'])}:1")
    if domain == "pairings":
        return f"{row['id']:18} {row['display']} / {row['body']} / {row['mono']}  ({', '.join(row['moods'])})\n{'':19}{row['why']}"
    if domain == "patterns":
        return (f"{row['id']:20} {row['kind']:8} {row['name']}\n{'':21}sections: {' > '.join(row['sections'])}\n"
                f"{'':21}cta: {row['cta']}; not when {row['avoid_when']}")
    if domain == "motion":
        return (f"{row['id']:16} {row['name']}: calm/standard/expressive {'/'.join(str(x or '-') for x in row['ms'])} ms, {row['easing']}"
                f"\n{'':17}animate {', '.join(row['animate'])}; reduced: {row['reduced']}; {row['rule']}")
    return f"{row['id']:22} {row['name']}: landing {row.get('landing') or '-'}, direction {row['direction']} (alt {row['alt']}), palettes {', '.join(row['palettes'])}"


def main() -> None:
    """Parse arguments, run the search and exit with the contract code."""
    ap = argparse.ArgumentParser(description="Search bundled UX rules, charts, stacks, directions, palettes and type pairings.")
    ap.add_argument("--query", default="", help="free-text query (words and phrases)")
    ap.add_argument("--domain", choices=DOMAINS + ("all",), default="all", help="which data set to search (default all)")
    ap.add_argument("--category", default="", help="rules only: accessibility, touch, forms, motion, ...")
    ap.add_argument("--min-severity", choices=list(dd.SEVERITY_RANK), default="", help="rules only: lowest severity to include")
    ap.add_argument("--platform", choices=["web", "mobile"], default="", help="rules and stacks: platform filter")
    ap.add_argument("--limit", type=int, default=8, help="maximum results per domain (default 8)")
    ap.add_argument("--list", action="store_true", help="list domains, rule categories and counts")
    ap.add_argument("--format", choices=["text", "json"], default="text", help="output format")
    args = ap.parse_args()
    try:
        if args.list:
            cats = sorted({r["category"] for r in dd.load("rules")})
            info = {"domains": {d: len(dd.load(d)) for d in DOMAINS}, "rule_categories": cats}
            print(json.dumps(info, indent=2) if args.format == "json" else
                  "\n".join(f"{d:11} {n}" for d, n in info["domains"].items()) + "\ncategories: " + ", ".join(cats))
            sys.exit(0)
        if args.category and args.category not in {r["category"] for r in dd.load("rules")}:
            raise dd.DataError(f"unknown category {args.category!r}; run --list")
        if args.limit < 1:
            raise dd.DataError("--limit must be at least 1")
        if not args.query and args.domain == "all" and not (args.category or args.min_severity):
            raise dd.DataError("give --query, or a --domain / --category filter")
        domains = DOMAINS if args.domain == "all" else (args.domain,)
        if args.category or args.min_severity:
            domains = ("rules",)
        results = {d: search(d, args.query, args.category, args.min_severity, args.platform)[: args.limit] for d in domains}
    except dd.DataError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)
    results = {d: hits for d, hits in results.items() if hits}
    if args.format == "json":
        print(json.dumps({"query": args.query, "results": {d: [dict(r, score=s) for s, r in hits]
                                                           for d, hits in results.items()}}, indent=2))
    elif not results:
        print(f"no matches for {args.query!r}; try fewer or plainer words, or --list")
    else:
        for d, hits in results.items():
            print(f"== {d} ({len(hits)})")
            for _, row in hits:
                print("  " + line(d, row).replace("\n", "\n  "))
    sys.exit(0 if results else 1)


if __name__ == "__main__":
    main()
