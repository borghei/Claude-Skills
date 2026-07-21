#!/usr/bin/env python3
"""Report bidirectional coverage between spec requirements and the code that implements them.

Scans a source tree for requirement-ID annotations and reports both directions:
requirements with no implementation or no test, and annotations pointing at IDs the
spec no longer contains.

Usage:
  python3 trace_coverage.py --requirements assets/sample_requirements.json --code .
  python3 trace_coverage.py --requirements assets/sample_requirements.json \\
      --index assets/sample_trace_index.json --format json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Set

REQ_RE = re.compile(r"\bREQ-[A-Z0-9-]+-\d{2}\b")
TEST_HINTS = ("test", "spec", "_test.", ".test.", "__tests__")
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build", ".mypy_cache"}
SOURCE_SUFFIXES = {".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rb", ".java", ".rs", ".sql", ".md"}


def is_test_path(path: Path) -> bool:
    """Return True when a path looks like test code rather than production code."""
    lowered = str(path).lower()
    return any(hint in lowered for hint in TEST_HINTS)


def scan_code(root: str, max_files: int) -> Dict[str, Any]:
    """Scan a source tree for requirement-ID annotations, split by test and source."""
    base = Path(root)
    if not base.is_dir():
        raise SystemExit(f"error: not a directory: {root}")
    source_refs: Dict[str, List[str]] = {}
    test_refs: Dict[str, List[str]] = {}
    scanned = 0
    for path in sorted(base.rglob("*")):
        if scanned >= max_files:
            break
        if not path.is_file() or path.suffix not in SOURCE_SUFFIXES:
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        scanned += 1
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        target = test_refs if is_test_path(path) else source_refs
        for req_id in set(REQ_RE.findall(text)):
            target.setdefault(req_id, []).append(str(path))
    return {"source": source_refs, "tests": test_refs, "files_scanned": scanned}


def load_index(path: str) -> Dict[str, Any]:
    """Load a prebuilt trace index instead of scanning a tree."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"error: index file not found: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"error: index is not valid JSON ({path}): {exc}")
    if not isinstance(data, dict) or "source" not in data or "tests" not in data:
        raise SystemExit("error: index must be an object with 'source' and 'tests' mappings")
    data.setdefault("files_scanned", 0)
    return data


def load_requirements(path: str) -> List[Dict[str, Any]]:
    """Load requirement records emitted by spec_parse.py."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"error: requirements file not found: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"error: requirements file is not valid JSON ({path}): {exc}")
    records = data.get("requirements") if isinstance(data, dict) else data
    if not isinstance(records, list) or not records:
        raise SystemExit("error: requirements file contains no requirement records")
    for record in records:
        if not isinstance(record, dict) or not record.get("id"):
            raise SystemExit("error: every requirement record needs an 'id' field")
    return records


def compute_coverage(requirements: List[Dict[str, Any]], index: Dict[str, Any]) -> Dict[str, Any]:
    """Compare requirements against annotations in both directions."""
    source: Dict[str, List[str]] = index["source"]
    tests: Dict[str, List[str]] = index["tests"]
    known: Set[str] = {str(r["id"]) for r in requirements}

    rows: List[Dict[str, Any]] = []
    for record in requirements:
        req_id = str(record["id"])
        impl, test = source.get(req_id, []), tests.get(req_id, [])
        if impl and test:
            status = "covered"
        elif impl:
            status = "untested"
        elif test:
            status = "test-only"
        else:
            status = "unimplemented"
        rows.append({
            "id": req_id,
            "modality": record.get("modality", "unknown"),
            "status": status,
            "implementation": sorted(impl),
            "tests": sorted(test),
            "text": str(record.get("text", ""))[:100],
        })

    orphans = sorted((set(source) | set(tests)) - known)
    mandatory = [r for r in rows if r["modality"] == "mandatory"]
    covered_mandatory = [r for r in mandatory if r["status"] == "covered"]
    counts: Dict[str, int] = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    return {
        "total_requirements": len(rows),
        "files_scanned": index.get("files_scanned", 0),
        "status_counts": counts,
        "coverage_ratio": round(counts.get("covered", 0) / len(rows), 2) if rows else 0.0,
        "mandatory_coverage_ratio": round(len(covered_mandatory) / len(mandatory), 2) if mandatory else 1.0,
        "orphan_annotations": [{"id": o, "locations": sorted(source.get(o, []) + tests.get(o, []))}
                               for o in orphans],
        "requirements": rows,
    }


def output(report: Dict[str, Any], fmt: str) -> None:
    """Print the bidirectional coverage report as text or JSON."""
    if fmt == "json":
        print(json.dumps(report, indent=2))
        return
    counts = report["status_counts"]
    print(f"{report['total_requirements']} requirements across {report['files_scanned']} scanned files")
    print(f"  coverage {report['coverage_ratio']:.0%}  |  mandatory coverage "
          f"{report['mandatory_coverage_ratio']:.0%}")
    print("  " + ", ".join(f"{count} {status}" for status, count in sorted(counts.items())) + "\n")
    for row in report["requirements"]:
        if row["status"] == "covered":
            continue
        print(f"{row['status']:<14} {row['id']:<22} [{row['modality']}] {row['text'][:60]}")
        if row["implementation"]:
            print(f"               code: {', '.join(row['implementation'][:3])}")
        if row["tests"]:
            print(f"               test: {', '.join(row['tests'][:3])}")
    if report["orphan_annotations"]:
        print("\nOrphan annotations — code references requirements the spec no longer contains:")
        for orphan in report["orphan_annotations"]:
            print(f"  {orphan['id']}  {', '.join(orphan['locations'][:3])}")


def main() -> None:
    """Parse arguments, compute coverage, and exit non-zero below the coverage floor."""
    parser = argparse.ArgumentParser(description="Report spec-to-code coverage in both directions.")
    parser.add_argument("--requirements", required=True, help="requirements JSON emitted by spec_parse.py")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--code", help="source tree to scan for REQ-* annotations")
    source.add_argument("--index", help="prebuilt trace index JSON with 'source' and 'tests' mappings")
    parser.add_argument("--min-coverage", type=float, default=1.0,
                        help="required mandatory-requirement coverage ratio (default: 1.0)")
    parser.add_argument("--max-files", type=int, default=5000, help="file scan cap (default: 5000)")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="output format (default: text)")
    args = parser.parse_args()
    try:
        requirements = load_requirements(args.requirements)
        index = load_index(args.index) if args.index else scan_code(args.code, args.max_files)
        report = compute_coverage(requirements, index)
        output(report, args.format)
    except SystemExit:
        raise
    except OSError as exc:
        print(f"error: could not read inputs: {exc}", file=sys.stderr)
        sys.exit(1)
    failed = report["mandatory_coverage_ratio"] < args.min_coverage or report["orphan_annotations"]
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
