#!/usr/bin/env python3
"""Parse a markdown specification into discrete requirements with stable IDs.

Assigns each normative statement an ID derived from its section and ordinal, plus
a content fingerprint so silent edits to an already-implemented requirement are
detectable on the next parse.

Usage:
  python3 spec_parse.py --spec assets/sample_spec.md
  python3 spec_parse.py --spec assets/sample_spec.md --format json > requirements.json
  python3 spec_parse.py --spec assets/sample_spec.md --baseline requirements.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

MODALITIES = {
    "must": "mandatory", "must not": "mandatory", "shall": "mandatory",
    "should": "recommended", "should not": "recommended",
    "may": "optional", "can": "optional",
}
MODALITY_RE = re.compile(r"\b(must not|must|shall|should not|should|may|can)\b", re.IGNORECASE)
ACCEPTANCE_RE = re.compile(r"^\s*[-*]\s*(?:AC|acceptance|given|when|then)\b", re.IGNORECASE)
STOPWORDS = {"the", "a", "an", "and", "or", "of", "to", "for", "in", "on", "with", "system"}


def slugify(heading: str) -> str:
    """Reduce a heading to a short uppercase slug used in requirement IDs."""
    words = [w for w in re.findall(r"[A-Za-z0-9]+", heading.lower()) if w not in STOPWORDS]
    return "-".join(words[:2]).upper() or "GEN"


def fingerprint(text: str) -> str:
    """Return a stable 8-character fingerprint of a requirement's normalized text."""
    normalized = " ".join(text.lower().split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:8]


def parse_spec(path: str) -> List[Dict[str, Any]]:
    """Extract every normative statement from a markdown spec as a requirement record."""
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        raise SystemExit(f"error: spec file not found: {path}")
    except UnicodeDecodeError:
        raise SystemExit(f"error: spec file is not valid UTF-8 text: {path}")

    requirements: List[Dict[str, Any]] = []
    section, slug, counters = "General", "GEN", {}
    in_code = False

    for number, raw in enumerate(lines, start=1):
        stripped = raw.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code or not stripped:
            continue
        if stripped.startswith("#"):
            section = stripped.lstrip("#").strip()
            slug = slugify(section)
            continue
        if ACCEPTANCE_RE.match(raw) and requirements:
            requirements[-1]["acceptance_criteria"].append(stripped.lstrip("-* ").strip())
            continue

        match = MODALITY_RE.search(stripped)
        if not match:
            continue
        text = stripped.lstrip("-*0123456789. ").strip()
        counters[slug] = counters.get(slug, 0) + 1
        keyword = match.group(1).lower()
        requirements.append({
            "id": f"REQ-{slug}-{counters[slug]:02d}",
            "section": section,
            "line": number,
            "modality": MODALITIES[keyword],
            "keyword": keyword,
            "text": text,
            "fingerprint": fingerprint(text),
            "acceptance_criteria": [],
        })
    if not requirements:
        raise SystemExit(f"error: no normative statements (must/shall/should/may) found in {path}")
    return requirements


def load_baseline(path: Optional[str]) -> Dict[str, Dict[str, Any]]:
    """Load a previously emitted requirements file, keyed by requirement ID."""
    if not path:
        return {}
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"error: baseline file not found: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"error: baseline is not valid JSON ({path}): {exc}")
    records = data.get("requirements") if isinstance(data, dict) else data
    if not isinstance(records, list):
        raise SystemExit("error: baseline must be a list of requirement objects")
    return {str(r.get("id")): r for r in records if isinstance(r, dict) and r.get("id")}


def diff_baseline(current: List[Dict[str, Any]], baseline: Dict[str, Dict[str, Any]]) -> Dict[str, List[str]]:
    """Compare parsed requirements to a baseline, reporting added, removed, and drifted IDs."""
    now = {r["id"]: r for r in current}
    drifted = [rid for rid, rec in now.items()
               if rid in baseline and baseline[rid].get("fingerprint") != rec["fingerprint"]]
    return {
        "added": sorted(set(now) - set(baseline)),
        "removed": sorted(set(baseline) - set(now)),
        "drifted": sorted(drifted),
    }


def summarize(requirements: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Summarize counts by modality and acceptance-criteria coverage."""
    by_modality: Dict[str, int] = {}
    for req in requirements:
        by_modality[req["modality"]] = by_modality.get(req["modality"], 0) + 1
    without_ac = [r["id"] for r in requirements if not r["acceptance_criteria"]]
    mandatory_without_ac = [r["id"] for r in requirements
                            if r["modality"] == "mandatory" and not r["acceptance_criteria"]]
    return {
        "total": len(requirements),
        "by_modality": by_modality,
        "without_acceptance_criteria": without_ac,
        "mandatory_without_acceptance_criteria": mandatory_without_ac,
    }


def output(report: Dict[str, Any], fmt: str) -> None:
    """Print the parsed requirement set as text or JSON."""
    if fmt == "json":
        print(json.dumps(report, indent=2))
        return
    summary = report["summary"]
    print(f"Parsed {summary['total']} requirements from {report['spec']}")
    modality = ", ".join(f"{count} {name}" for name, count in sorted(summary["by_modality"].items()))
    print(f"  {modality}\n")
    for req in report["requirements"]:
        criteria = len(req["acceptance_criteria"])
        marker = " " if criteria else "!"
        print(f"{marker} {req['id']:<22} L{req['line']:<4} [{req['keyword']}] {req['text'][:70]}")
        if not criteria:
            print(f"    no acceptance criteria — this requirement is not verifiable as written")
    if report.get("diff"):
        diff = report["diff"]
        print(f"\nAgainst baseline: {len(diff['added'])} added, {len(diff['removed'])} removed, "
              f"{len(diff['drifted'])} drifted")
        for rid in diff["drifted"]:
            print(f"  DRIFT {rid} — text changed since baseline; re-verify its tests")
        for rid in diff["removed"]:
            print(f"  GONE  {rid} — removed from spec; delete or re-point its tests")


def main() -> None:
    """Parse arguments, extract requirements, and emit the report."""
    parser = argparse.ArgumentParser(description="Parse a markdown spec into requirements with stable IDs.")
    parser.add_argument("--spec", required=True, help="path to the markdown specification")
    parser.add_argument("--baseline", help="previously emitted requirements JSON to diff against")
    parser.add_argument("--require-acceptance", action="store_true",
                        help="exit 1 if any mandatory requirement lacks acceptance criteria")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="output format (default: text)")
    args = parser.parse_args()
    try:
        requirements = parse_spec(args.spec)
        summary = summarize(requirements)
        report: Dict[str, Any] = {"spec": args.spec, "summary": summary, "requirements": requirements}
        baseline = load_baseline(args.baseline)
        if baseline:
            report["diff"] = diff_baseline(requirements, baseline)
        output(report, args.format)
    except SystemExit:
        raise
    except OSError as exc:
        print(f"error: could not read spec: {exc}", file=sys.stderr)
        sys.exit(1)
    gaps = summary["mandatory_without_acceptance_criteria"]
    drift = report.get("diff", {}).get("drifted") or []
    sys.exit(1 if (args.require_acceptance and gaps) or drift else 0)


if __name__ == "__main__":
    main()
