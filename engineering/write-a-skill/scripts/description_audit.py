#!/usr/bin/env python3
"""Audit skill descriptions for activation quality, token budget, and collisions.

Scores each description on budget, trigger presence, filler, and specificity, then
flags pairs of skills whose triggers overlap enough that an assistant would pick
the wrong one.

Usage:
  python3 description_audit.py --input assets/sample_descriptions.json
  python3 description_audit.py --input assets/sample_descriptions.json --format json
  python3 description_audit.py --domain engineering --min-score 70
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

MAX_CHARS = 240
CHARS_PER_TOKEN = 4.0

FILLER_WORDS = (
    "comprehensive", "powerful", "robust", "seamless", "cutting-edge", "world-class",
    "best-in-class", "state-of-the-art", "advanced", "leverage", "utilize", "holistic",
    "revolutionary", "next-generation", "enterprise-grade",
)
STOPWORDS = {
    "the", "and", "for", "with", "use", "when", "a", "an", "of", "to", "or", "in", "on",
    "your", "you", "that", "this", "it", "is", "are", "from", "into", "by", "as", "at",
}


def estimate_tokens(text: str) -> int:
    """Estimate the resident token cost of a description (4 chars per token)."""
    return int(round(len(text) / CHARS_PER_TOKEN))


def trigger_terms(description: str) -> List[str]:
    """Extract the distinctive trigger words that drive skill discovery."""
    tail = description.lower()
    match = re.search(r"use when(.*)", tail, re.DOTALL)
    if match:
        tail = match.group(1)
    words = re.findall(r"[a-z][a-z0-9-]{2,}", tail)
    return sorted({w for w in words if w not in STOPWORDS})


def score_description(name: str, description: str) -> Dict[str, Any]:
    """Score one description and return its findings, score, and trigger terms."""
    description = " ".join(description.split())
    findings: List[str] = []
    score = 100

    chars = len(description)
    if chars > MAX_CHARS:
        over = chars - MAX_CHARS
        penalty = min(40, 10 + over // 10)
        score -= penalty
        findings.append(f"{chars} chars — {over} over the {MAX_CHARS}-char budget")
    elif chars < 60:
        score -= 15
        findings.append(f"{chars} chars — too thin to distinguish this skill from neighbours")

    if "use when" not in description.lower():
        score -= 25
        findings.append("no 'Use when ...' clause — assistants have nothing to match against")

    triggers = trigger_terms(description)
    if len(triggers) < 5:
        score -= 15
        findings.append(f"only {len(triggers)} distinctive trigger terms (aim for 6+)")

    hits = [w for w in FILLER_WORDS if w in description.lower()]
    if hits:
        score -= 5 * len(hits)
        findings.append(f"marketing filler: {', '.join(hits)}")

    readable = name.replace("-", " ").lower()
    if "-" in name and readable in description.lower():
        score -= 10
        findings.append("restates the skill name — the name is already in context")

    if re.search(r"\b(pairs with|distinct from|see also|complements)\b", description.lower()):
        score -= 10
        findings.append("cross-skill routing prose belongs in the body, not the description")

    return {
        "name": name,
        "chars": chars,
        "tokens": estimate_tokens(description),
        "score": max(0, score),
        "triggers": triggers,
        "findings": findings,
    }


def find_collisions(scored: List[Dict[str, Any]], threshold: float) -> List[Dict[str, Any]]:
    """Flag skill pairs whose trigger vocabularies overlap above the threshold."""
    collisions: List[Dict[str, Any]] = []
    for i, left in enumerate(scored):
        for right in scored[i + 1:]:
            a, b = set(left["triggers"]), set(right["triggers"])
            if not a or not b:
                continue
            overlap = len(a & b) / len(a | b)
            if overlap >= threshold:
                collisions.append({
                    "skills": [left["name"], right["name"]],
                    "overlap": round(overlap, 2),
                    "shared_terms": sorted(a & b)[:8],
                })
    return sorted(collisions, key=lambda c: -c["overlap"])


def read_input(input_path: str) -> List[Tuple[str, str]]:
    """Load name/description pairs from a JSON file."""
    try:
        data = json.loads(Path(input_path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"error: input file not found: {input_path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"error: input is not valid JSON ({input_path}): {exc}")
    records = data.get("skills") if isinstance(data, dict) else data
    if not isinstance(records, list):
        raise SystemExit("error: input must be a list of {name, description} objects")
    pairs: List[Tuple[str, str]] = []
    for record in records:
        if not isinstance(record, dict) or "description" not in record:
            raise SystemExit("error: every record needs 'name' and 'description' keys")
        pairs.append((str(record.get("name", "unnamed")), str(record["description"])))
    return pairs


def read_domain(domain_path: str) -> List[Tuple[str, str]]:
    """Extract name/description pairs from every SKILL.md under a domain directory."""
    root = Path(domain_path)
    if not root.is_dir():
        raise SystemExit(f"error: not a directory: {domain_path}")
    pairs: List[Tuple[str, str]] = []
    for doc in sorted(root.glob("*/SKILL.md")):
        text = doc.read_text(encoding="utf-8", errors="replace")
        match = re.search(r"^description:\s*>?\s*\n?((?:.*\n)*?)^[a-z]", text, re.MULTILINE)
        inline = re.search(r"^description:\s*(?!>)(.+)$", text, re.MULTILINE)
        raw = inline.group(1) if inline else (match.group(1) if match else "")
        pairs.append((doc.parent.name, " ".join(raw.split())))
    if not pairs:
        raise SystemExit(f"error: no */SKILL.md found under {domain_path}")
    return pairs


def output(report: Dict[str, Any], fmt: str) -> None:
    """Print the audit report as text or JSON."""
    if fmt == "json":
        print(json.dumps(report, indent=2))
        return
    print(f"Audited {len(report['skills'])} descriptions — {report['failing']} below the bar")
    print(f"Resident cost: {report['total_tokens']} tokens across all descriptions\n")
    for item in report["skills"]:
        flag = "OK  " if item["score"] >= report["min_score"] else "FAIL"
        print(f"{flag} {item['score']:3}/100  {item['name']}  ({item['chars']} chars, ~{item['tokens']} tok)")
        for finding in item["findings"]:
            print(f"       - {finding}")
    if report["collisions"]:
        print("\nTrigger collisions (assistants may activate the wrong skill):")
        for collision in report["collisions"]:
            skills = " <-> ".join(collision["skills"])
            print(f"  {collision['overlap']:.2f}  {skills}  shared: {', '.join(collision['shared_terms'])}")


def main() -> None:
    """Parse arguments, audit every description, and exit non-zero on failures."""
    parser = argparse.ArgumentParser(description="Audit skill descriptions for activation quality.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", help="JSON file of {name, description} records")
    source.add_argument("--domain", help="domain directory to scan for */SKILL.md descriptions")
    parser.add_argument("--min-score", type=int, default=70, help="passing score per description (default: 70)")
    parser.add_argument("--collision-threshold", type=float, default=0.5,
                        help="Jaccard overlap at which two skills are flagged as colliding (default: 0.5)")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="output format (default: text)")
    args = parser.parse_args()
    try:
        pairs = read_input(args.input) if args.input else read_domain(args.domain)
        scored = [score_description(name, desc) for name, desc in pairs]
        report = {
            "min_score": args.min_score,
            "total_tokens": sum(item["tokens"] for item in scored),
            "failing": sum(1 for item in scored if item["score"] < args.min_score),
            "skills": sorted(scored, key=lambda item: item["score"]),
            "collisions": find_collisions(scored, args.collision_threshold),
        }
        output(report, args.format)
    except SystemExit:
        raise
    except OSError as exc:
        print(f"error: could not read descriptions: {exc}", file=sys.stderr)
        sys.exit(1)
    sys.exit(1 if report["failing"] else 0)


if __name__ == "__main__":
    main()
