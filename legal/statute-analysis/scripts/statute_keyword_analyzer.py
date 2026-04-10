#!/usr/bin/env python3
"""
Statute Keyword Analyzer

Scans statute or regulation text for operative keywords and classifies them
into obligations, permissions, conditions, exemptions, definitions, and
cross-references. Produces a structured map of legal requirements.

Usage:
    python statute_keyword_analyzer.py --input statute.txt
    python statute_keyword_analyzer.py --text "The controller shall implement..."
    python statute_keyword_analyzer.py --input statute.txt --json
    python statute_keyword_analyzer.py --input statute.txt --output report.json
"""

import argparse
import json
import re
import sys
from collections import Counter
from typing import Any, Dict, List, Tuple


# Keyword classification patterns
KEYWORD_PATTERNS: Dict[str, List[Dict[str, Any]]] = {
    "mandatory": [
        {"pattern": r"\bshall\b", "keyword": "shall", "description": "Creates an obligation"},
        {"pattern": r"\bmust\b", "keyword": "must", "description": "Creates an obligation"},
        {"pattern": r"\bis required to\b", "keyword": "is required to", "description": "Creates an obligation"},
        {"pattern": r"\bis obliged to\b", "keyword": "is obliged to", "description": "Creates an obligation"},
    ],
    "permissive": [
        {"pattern": r"\bmay\b(?!\s+not\b)", "keyword": "may", "description": "Creates permission"},
        {"pattern": r"\bis entitled to\b", "keyword": "is entitled to", "description": "Creates an entitlement"},
        {"pattern": r"\bhas the right to\b", "keyword": "has the right to", "description": "Creates a right"},
    ],
    "prohibitive": [
        {"pattern": r"\bmay not\b", "keyword": "may not", "description": "Creates a prohibition"},
        {"pattern": r"\bshall not\b", "keyword": "shall not", "description": "Creates a prohibition"},
        {"pattern": r"\bmust not\b", "keyword": "must not", "description": "Creates a prohibition"},
        {"pattern": r"\bis prohibited\b", "keyword": "is prohibited", "description": "Creates a prohibition"},
        {"pattern": r"\bno\s+\w+\s+shall\b", "keyword": "no...shall", "description": "Negative obligation"},
    ],
    "exception": [
        {"pattern": r"\bunless\b", "keyword": "unless", "description": "Negates rule when condition met"},
        {"pattern": r"\bexcept\b", "keyword": "except", "description": "Carves out specific items"},
        {"pattern": r"\bprovided that\b", "keyword": "provided that", "description": "Adds a condition"},
        {"pattern": r"\bexempt(?:ed|ion)?\b", "keyword": "exempt/exemption", "description": "Carves out from scope"},
        {"pattern": r"\bexclud(?:e[ds]?|ing)\b", "keyword": "exclude", "description": "Removes from scope"},
    ],
    "conditional": [
        {"pattern": r"\bsubject to\b", "keyword": "subject to", "description": "Another provision modifies this"},
        {"pattern": r"\bif\b", "keyword": "if", "description": "Trigger condition"},
        {"pattern": r"\bwhere\b", "keyword": "where", "description": "Conditional clause"},
        {"pattern": r"\bupon\b", "keyword": "upon", "description": "Temporal trigger"},
        {"pattern": r"\bprovided that\b", "keyword": "provided that", "description": "Conditional requirement"},
        {"pattern": r"\bin the event\b", "keyword": "in the event", "description": "Contingency trigger"},
    ],
    "override": [
        {"pattern": r"\bnotwithstanding\b", "keyword": "notwithstanding", "description": "This prevails over conflicting provisions"},
        {"pattern": r"\bprevail[s]?\s+over\b", "keyword": "prevails over", "description": "Priority clause"},
        {"pattern": r"\bwithout prejudice to\b", "keyword": "without prejudice to", "description": "Preserves another provision's effect"},
    ],
    "definition": [
        {"pattern": r"['\u2018]\w[^'\u2019]*['\u2019]\s+means\b", "keyword": "'X' means", "description": "Exhaustive definition"},
        {"pattern": r"['\u2018]\w[^'\u2019]*['\u2019]\s+includes\b", "keyword": "'X' includes", "description": "Illustrative definition"},
        {"pattern": r"['\u2018]\w[^'\u2019]*['\u2019]\s+refers to\b", "keyword": "'X' refers to", "description": "Pointer definition"},
        {"pattern": r"\bfor the purposes of\b", "keyword": "for the purposes of", "description": "Scoped definition"},
        {"pattern": r"\bas defined in\b", "keyword": "as defined in", "description": "Cross-reference definition"},
    ],
    "conjunctive_disjunctive": [
        {"pattern": r"\band/or\b", "keyword": "and/or", "description": "Ambiguous conjunctive/disjunctive"},
        {"pattern": r"\bboth\s+\w+\s+and\b", "keyword": "both...and", "description": "Explicitly conjunctive"},
        {"pattern": r"\beither\s+\w+\s+or\b", "keyword": "either...or", "description": "Explicitly disjunctive"},
    ],
}

CROSS_REF_PATTERNS = [
    r"(?:Article|Art\.?)\s+\d+(?:\(\d+\))?(?:\([a-z]\))?",
    r"(?:Section|Sec\.?|§)\s*\d+(?:\.\d+)?(?:\([a-z]\))?",
    r"(?:Regulation|Directive)\s+\(?(?:EU|EC)\)?\s*(?:No\s*)?\d{4}/\d+",
    r"(?:paragraph|para\.?)\s+\d+(?:\([a-z]\))?",
    r"(?:Annex|Schedule|Appendix)\s+[IVXLCDM]+(?:\s+\w+)?",
    r"(?:Chapter|Title|Part)\s+[IVXLCDM\d]+",
]


def extract_sentences(text: str) -> List[str]:
    """Split text into sentences, handling common legal abbreviations."""
    # Protect common abbreviations from sentence splitting
    protected = text
    abbrevs = ["Art.", "Sec.", "No.", "para.", "e.g.", "i.e.", "et al.", "cf.", "v."]
    for abbr in abbrevs:
        protected = protected.replace(abbr, abbr.replace(".", "<DOT>"))
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z\d(])', protected)
    return [s.replace("<DOT>", ".").strip() for s in sentences if s.strip()]


def find_keyword_matches(text: str) -> Dict[str, List[Dict[str, Any]]]:
    """Find all keyword matches in text, organized by classification."""
    sentences = extract_sentences(text)
    results: Dict[str, List[Dict[str, Any]]] = {}

    for category, patterns in KEYWORD_PATTERNS.items():
        matches = []
        for pat_info in patterns:
            pattern = re.compile(pat_info["pattern"], re.IGNORECASE)
            for i, sentence in enumerate(sentences):
                for match in pattern.finditer(sentence):
                    matches.append({
                        "keyword": pat_info["keyword"],
                        "description": pat_info["description"],
                        "sentence_index": i,
                        "sentence": sentence.strip(),
                        "position": match.start(),
                        "matched_text": match.group(),
                    })
        if matches:
            results[category] = matches

    return results


def find_cross_references(text: str) -> List[Dict[str, str]]:
    """Extract all cross-references from text."""
    refs = []
    sentences = extract_sentences(text)
    for i, sentence in enumerate(sentences):
        for pattern in CROSS_REF_PATTERNS:
            for match in re.finditer(pattern, sentence):
                refs.append({
                    "reference": match.group(),
                    "sentence_index": i,
                    "context": sentence.strip(),
                })
    # Deduplicate by reference text
    seen = set()
    unique_refs = []
    for ref in refs:
        key = ref["reference"]
        if key not in seen:
            seen.add(key)
            unique_refs.append(ref)
    return unique_refs


def compute_statistics(matches: Dict[str, List], cross_refs: List, text: str) -> Dict[str, Any]:
    """Compute summary statistics for the analysis."""
    sentences = extract_sentences(text)
    total_keywords = sum(len(v) for v in matches.values())
    keyword_counts: Dict[str, int] = {}
    for category, items in matches.items():
        for item in items:
            kw = item["keyword"]
            keyword_counts[kw] = keyword_counts.get(kw, 0) + 1

    # Sort by frequency
    sorted_keywords = sorted(keyword_counts.items(), key=lambda x: -x[1])

    return {
        "total_sentences": len(sentences),
        "total_keywords_found": total_keywords,
        "total_cross_references": len(cross_refs),
        "keywords_by_category": {cat: len(items) for cat, items in matches.items()},
        "keyword_frequency": dict(sorted_keywords[:20]),
        "obligation_density": round(
            matches.get("mandatory", []).__len__() / max(len(sentences), 1) * 100, 1
        ),
        "exception_density": round(
            matches.get("exception", []).__len__() / max(len(sentences), 1) * 100, 1
        ),
    }


def build_obligation_map(matches: Dict[str, List]) -> List[Dict[str, str]]:
    """Build a deduplicated map of obligations from mandatory matches."""
    obligations = []
    seen = set()
    for item in matches.get("mandatory", []):
        key = item["sentence"]
        if key not in seen:
            seen.add(key)
            obligations.append({
                "type": "obligation",
                "keyword": item["keyword"],
                "text": item["sentence"],
            })
    for item in matches.get("prohibitive", []):
        key = item["sentence"]
        if key not in seen:
            seen.add(key)
            obligations.append({
                "type": "prohibition",
                "keyword": item["keyword"],
                "text": item["sentence"],
            })
    return obligations


def build_exception_map(matches: Dict[str, List]) -> List[Dict[str, str]]:
    """Build a map of exceptions and conditions."""
    exceptions = []
    seen = set()
    for item in matches.get("exception", []):
        key = item["sentence"]
        if key not in seen:
            seen.add(key)
            exceptions.append({
                "type": "exception",
                "keyword": item["keyword"],
                "text": item["sentence"],
            })
    for item in matches.get("conditional", []):
        key = item["sentence"]
        if key not in seen:
            seen.add(key)
            exceptions.append({
                "type": "condition",
                "keyword": item["keyword"],
                "text": item["sentence"],
            })
    return exceptions


def format_human_report(
    matches: Dict[str, List],
    cross_refs: List,
    stats: Dict[str, Any],
    obligations: List,
    exceptions: List,
) -> str:
    """Format results as human-readable report."""
    lines = []
    lines.append("=" * 72)
    lines.append("STATUTE KEYWORD ANALYSIS REPORT")
    lines.append("=" * 72)

    lines.append("\n--- SUMMARY ---")
    lines.append(f"Total sentences analyzed: {stats['total_sentences']}")
    lines.append(f"Total operative keywords found: {stats['total_keywords_found']}")
    lines.append(f"Total cross-references found: {stats['total_cross_references']}")
    lines.append(f"Obligation density: {stats['obligation_density']}% of sentences")
    lines.append(f"Exception density: {stats['exception_density']}% of sentences")

    lines.append("\n--- KEYWORD FREQUENCY ---")
    for kw, count in stats.get("keyword_frequency", {}).items():
        lines.append(f"  {kw:25s} {count:4d}")

    lines.append("\n--- KEYWORDS BY CATEGORY ---")
    for cat, count in stats.get("keywords_by_category", {}).items():
        lines.append(f"  {cat:30s} {count:4d}")

    lines.append(f"\n--- OBLIGATIONS ({len(obligations)}) ---")
    for i, ob in enumerate(obligations, 1):
        lines.append(f"\n  [{i}] ({ob['type'].upper()}) [{ob['keyword']}]")
        lines.append(f"      {ob['text'][:200]}")

    lines.append(f"\n--- EXCEPTIONS AND CONDITIONS ({len(exceptions)}) ---")
    for i, ex in enumerate(exceptions, 1):
        lines.append(f"\n  [{i}] ({ex['type'].upper()}) [{ex['keyword']}]")
        lines.append(f"      {ex['text'][:200]}")

    lines.append(f"\n--- CROSS-REFERENCES ({len(cross_refs)}) ---")
    for ref in cross_refs:
        lines.append(f"  {ref['reference']}")

    if matches.get("conjunctive_disjunctive"):
        lines.append(f"\n--- AMBIGUITY FLAGS ({len(matches['conjunctive_disjunctive'])}) ---")
        for item in matches["conjunctive_disjunctive"]:
            lines.append(f"  [{item['keyword']}] {item['sentence'][:150]}")

    if matches.get("definition"):
        lines.append(f"\n--- DEFINITIONS ({len(matches['definition'])}) ---")
        for item in matches["definition"]:
            lines.append(f"  [{item['keyword']}] {item['sentence'][:150]}")

    lines.append("\n" + "=" * 72)
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze statute text for operative keywords and classify obligations."
    )
    parser.add_argument("--input", "-i", type=str, help="Path to statute text file")
    parser.add_argument("--text", "-t", type=str, help="Inline statute text to analyze")
    parser.add_argument("--output", "-o", type=str, help="Path to save output (JSON)")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    args = parser.parse_args()

    if not args.input and not args.text:
        parser.print_help()
        sys.exit(1)

    try:
        if args.input:
            with open(args.input, "r", encoding="utf-8") as f:
                text = f.read()
        else:
            text = args.text

        if not text or not text.strip():
            print("Error: Empty input text.", file=sys.stderr)
            sys.exit(1)

        matches = find_keyword_matches(text)
        cross_refs = find_cross_references(text)
        stats = compute_statistics(matches, cross_refs, text)
        obligations = build_obligation_map(matches)
        exceptions = build_exception_map(matches)

        result = {
            "statistics": stats,
            "obligations": obligations,
            "exceptions_and_conditions": exceptions,
            "cross_references": cross_refs,
            "definitions": [
                {"keyword": m["keyword"], "text": m["sentence"]}
                for m in matches.get("definition", [])
            ],
            "ambiguity_flags": [
                {"keyword": m["keyword"], "text": m["sentence"]}
                for m in matches.get("conjunctive_disjunctive", [])
            ],
            "overrides": [
                {"keyword": m["keyword"], "text": m["sentence"]}
                for m in matches.get("override", [])
            ],
        }

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"Report saved to {args.output}")
        elif args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(format_human_report(matches, cross_refs, stats, obligations, exceptions))

    except FileNotFoundError:
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
