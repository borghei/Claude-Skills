#!/usr/bin/env python3
"""Audit an internal knowledge base for staleness, ownership gaps, and duplication.

Usage:
    python3 kb_health_auditor.py --input kb.json --as-of 2026-07-21 [--format text|json]
    python3 kb_health_auditor.py --root ./docs --as-of 2026-07-21 [--format text|json]

Input JSON shape:
    {"docs": [{"path": "...", "title": "...", "owner": "...",
               "updated": "2026-06-30", "tier": "critical",
               "word_count": 1250, "views_90d": 940}]}

With --root, each markdown file's YAML frontmatter supplies owner, updated, and tier.
"""

import argparse
import json
import re
import sys
from collections import Counter
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# tier -> (review SLA days, stale threshold days)
TIER_SLA: Dict[str, Any] = {
    "critical": (90, 120),
    "core": (180, 270),
    "reference": (365, 540),
    "archive": (None, None),
}

TIER_WEIGHT = {"critical": 4.0, "core": 2.0, "reference": 1.0, "archive": 0.0}

THIN_WORD_COUNT = 250

# Owner values that are technically present but operationally absent.
ALIAS_PATTERN = re.compile(r"(team|group|squad|helpdesk|support|ops|desk|alias|@)", re.I)


def parse_date(value: str, field: str) -> date:
    """Parse an ISO-8601 date string, raising a clear error on bad input."""
    try:
        return datetime.strptime(str(value).strip(), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        raise ValueError(f"{field} must be an ISO date (YYYY-MM-DD), got: {value!r}")


def read_frontmatter(path: Path) -> Dict[str, str]:
    """Extract simple key: value pairs from a markdown file's YAML frontmatter."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    fields: Dict[str, str] = {}
    for line in text[3:end].splitlines():
        if ":" in line and not line.startswith((" ", "\t", "-")):
            key, _, val = line.partition(":")
            fields[key.strip().lower()] = val.strip().strip("\"'")
    return fields


def load_from_root(root: Path) -> List[Dict[str, Any]]:
    """Build a doc inventory by scanning a directory tree of markdown files."""
    if not root.is_dir():
        raise ValueError(f"--root is not a directory: {root}")
    docs: List[Dict[str, Any]] = []
    for path in sorted(root.rglob("*.md")):
        fm = read_frontmatter(path)
        try:
            words = len(path.read_text(encoding="utf-8", errors="replace").split())
        except OSError:
            words = 0
        docs.append({
            "path": str(path.relative_to(root)),
            "title": fm.get("title") or path.stem.replace("-", " ").replace("_", " "),
            "owner": fm.get("owner", ""),
            "updated": fm.get("updated", ""),
            "tier": (fm.get("tier") or "reference").lower(),
            "word_count": words,
            "views_90d": 0,
        })
    if not docs:
        raise ValueError(f"no markdown files found under {root}")
    return docs


def audit_doc(doc: Dict[str, Any], as_of: date) -> Dict[str, Any]:
    """Evaluate one document against its tier SLA and return its findings."""
    tier = str(doc.get("tier", "reference")).lower()
    if tier not in TIER_SLA:
        tier = "reference"
    sla_days, stale_days = TIER_SLA[tier]
    owner = str(doc.get("owner", "")).strip()
    issues: List[str] = []

    age: Optional[int] = None
    raw_updated = str(doc.get("updated", "")).strip()
    if not raw_updated:
        issues.append("no last-updated date")
    else:
        age = (as_of - parse_date(raw_updated, f"{doc.get('path')} updated")).days
        if age < 0:
            issues.append("last-updated date is in the future")
        elif stale_days is not None:
            if age > stale_days:
                issues.append(f"stale: {age}d old, {tier} threshold is {stale_days}d")
            elif age > sla_days:
                issues.append(f"review overdue: {age}d old, {tier} SLA is {sla_days}d")

    if not owner:
        issues.append("no owner")
    elif ALIAS_PATTERN.search(owner):
        issues.append(f"owner '{owner}' looks like a team alias, not a person")

    if int(doc.get("word_count", 0)) < THIN_WORD_COUNT and tier != "archive":
        issues.append(f"thin: {doc.get('word_count', 0)} words")

    return {
        "path": doc.get("path", "(no path)"),
        "title": doc.get("title", ""),
        "tier": tier,
        "owner": owner,
        "age_days": age,
        "views_90d": int(doc.get("views_90d", 0) or 0),
        "issues": issues,
        "severity": "critical" if tier == "critical" and any(
            i.startswith("stale") or i == "no owner" for i in issues) else (
            "high" if issues and tier in ("critical", "core") else
            ("medium" if issues else "none")),
    }


def audit(docs: List[Dict[str, Any]], as_of: date) -> Dict[str, Any]:
    """Audit the full inventory and compute a 0-100 health score."""
    if not docs:
        raise ValueError("inventory contains no documents")
    results = [audit_doc(d, as_of) for d in docs]
    scored = [r for r in results if r["tier"] != "archive"]
    total = len(scored) or 1

    titles = Counter(str(d.get("title", "")).strip().lower() for d in docs
                     if str(d.get("title", "")).strip())
    duplicates = {t: c for t, c in titles.items() if c > 1}
    dup_paths = {
        t: sorted(d.get("path", "") for d in docs
                  if str(d.get("title", "")).strip().lower() == t)
        for t in duplicates
    }

    stale = [r for r in scored if any(i.startswith("stale") for i in r["issues"])]
    overdue = [r for r in scored if any(i.startswith("review overdue") for i in r["issues"])]
    unowned = [r for r in scored if any(i.startswith("no owner") or "alias" in i
                                        for i in r["issues"])]
    thin = [r for r in scored if any(i.startswith("thin") for i in r["issues"])]

    score = 100.0
    score -= 45.0 * (len(stale) / total)
    score -= 15.0 * (len(overdue) / total)
    score -= 25.0 * (len(unowned) / total)
    score -= 8.0 * (len(thin) / total)
    score -= 7.0 * min(len(duplicates) / total * 3, 1.0)
    score = round(max(score, 0.0), 1)

    if score >= 80:
        band = "healthy - maintenance mode"
    elif score >= 60:
        band = "degrading - run one debt sprint on critical-tier staleness"
    elif score >= 40:
        band = "distrusted - assign owners before writing anything"
    else:
        band = "failed - rebuild the top 20 pages by traffic, archive the rest"

    return {
        "as_of": as_of.isoformat(),
        "total_docs": len(docs),
        "scored_docs": len(scored),
        "archived_docs": len(docs) - len(scored),
        "health_score": score,
        "band": band,
        "counts": {
            "stale": len(stale), "review_overdue": len(overdue),
            "unowned_or_alias": len(unowned), "thin": len(thin),
            "duplicate_titles": len(duplicates),
        },
        "duplicate_titles": dup_paths,
        "findings": sorted(
            [r for r in results if r["issues"]],
            key=lambda r: ({"critical": 0, "high": 1, "medium": 2, "none": 3}[r["severity"]],
                           -(r["views_90d"]), r["path"])),
    }


def output(result: Dict[str, Any], fmt: str) -> None:
    """Print the audit as JSON or human-readable text."""
    if fmt == "json":
        print(json.dumps(result, indent=2))
        return

    print(f"KB health audit as of {result['as_of']}")
    print(f"  {result['total_docs']} docs ({result['archived_docs']} archived, "
          f"{result['scored_docs']} scored)")
    counts = result["counts"]
    print(f"  stale={counts['stale']}  review_overdue={counts['review_overdue']}  "
          f"unowned/alias={counts['unowned_or_alias']}  thin={counts['thin']}  "
          f"duplicate_titles={counts['duplicate_titles']}")
    print(f"\nHealth score: {result['health_score']}/100 - {result['band']}")

    if result["duplicate_titles"]:
        print("\nDuplicate titles (merge into the most-linked path):")
        for title, paths in sorted(result["duplicate_titles"].items()):
            print(f"  '{title}': {', '.join(paths)}")

    print(f"\nFindings ({len(result['findings'])} docs with issues):")
    for f in result["findings"]:
        age = f"{f['age_days']}d" if f["age_days"] is not None else "unknown age"
        print(f"  [{f['severity'].upper():>8}] {f['path']}  ({f['tier']}, {age}, "
              f"{f['views_90d']} views)")
        for issue in f["issues"]:
            print(f"             - {issue}")


def main() -> None:
    """Parse arguments, run the audit, and emit the report."""
    parser = argparse.ArgumentParser(
        description="Audit a knowledge base for staleness, ownership gaps, and duplication.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", help="Path to a JSON inventory with a 'docs' array")
    source.add_argument("--root", help="Directory of markdown files to scan for frontmatter")
    parser.add_argument("--as-of", required=True,
                        help="Audit date as YYYY-MM-DD; required so runs are reproducible")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text)")
    args = parser.parse_args()

    try:
        as_of = parse_date(args.as_of, "--as-of")
        if args.root:
            docs = load_from_root(Path(args.root))
        else:
            with open(args.input, "r", encoding="utf-8") as fh:
                payload = json.load(fh)
            docs = payload.get("docs")
            if not isinstance(docs, list):
                raise ValueError("input JSON must contain a 'docs' array")
        result = audit(docs, as_of)
    except FileNotFoundError:
        print(f"Error: input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"Error: {args.input} is not valid JSON ({exc})", file=sys.stderr)
        sys.exit(1)
    except (ValueError, TypeError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    output(result, args.format)


if __name__ == "__main__":
    main()
