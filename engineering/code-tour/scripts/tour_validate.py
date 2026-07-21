#!/usr/bin/env python3
"""Validate a tour definition against the current state of a repository.

Resolves every stop's file and anchor symbol, reports deleted files, moved symbols,
line drift, and changed anchor bodies, and suggests relocations by searching for the
anchor elsewhere in the tree.

Usage:
  python3 tour_validate.py --tour assets/sample_tour.json --repo .
  python3 tour_validate.py --tour assets/sample_tour.json --repo . --format json
  python3 tour_validate.py --tour assets/sample_tour.json --repo . --update > fixed.json
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import sys
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build", "target"}
STATUS_ORDER = {"deleted": 0, "moved": 1, "missing-anchor": 2, "drifted": 3, "shifted": 4, "ok": 5}


def load_tour(path: str) -> Dict[str, Any]:
    """Load and validate a tour definition file."""
    try:
        tour = json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"error: tour file not found: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"error: tour file is not valid JSON ({path}): {exc}")
    stops = tour.get("stops") if isinstance(tour, dict) else None
    if not isinstance(stops, list) or not stops:
        raise SystemExit("error: tour must be an object with a non-empty 'stops' list")
    for index, stop in enumerate(stops, start=1):
        if not isinstance(stop, dict) or not stop.get("path"):
            raise SystemExit(f"error: stop {index} is missing a 'path' field")
    return tour


def anchor_span(path: Path, anchor: str) -> Optional[Tuple[int, int, str]]:
    """Locate an anchor in a file, returning its start line, end line, and body text.

    Python files are searched by AST for a matching function or class definition;
    other files fall back to the first line containing the anchor text.
    """
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    lines = text.splitlines()
    if path.suffix == ".py":
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                tree = ast.parse(text)
        except (SyntaxError, ValueError):
            tree = None
        if tree is not None:
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) \
                        and node.name == anchor:
                    end = getattr(node, "end_lineno", node.lineno) or node.lineno
                    return node.lineno, end, "\n".join(lines[node.lineno - 1:end])
    for number, line in enumerate(lines, start=1):
        if anchor in line:
            end = min(number + 20, len(lines))
            return number, end, "\n".join(lines[number - 1:end])
    return None


def fingerprint(body: str) -> str:
    """Return a stable 8-character fingerprint of an anchor body, ignoring whitespace."""
    normalized = " ".join(body.split())
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:8]


def search_relocation(root: Path, anchor: str, original: str, max_files: int) -> List[str]:
    """Search the tree for files containing the anchor, to suggest where a stop moved to."""
    hits: List[str] = []
    basename = Path(original).name
    scanned = 0
    for path in sorted(root.rglob("*")):
        if scanned >= max_files or len(hits) >= 5:
            break
        if not path.is_file() or set(p.lower() for p in path.parts) & SKIP_DIRS:
            continue
        if path.suffix not in {".py", ".js", ".ts", ".tsx", ".go", ".rb", ".java", ".rs"}:
            continue
        scanned += 1
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if (anchor and anchor in text) or path.name == basename:
            hits.append(str(path.relative_to(root)))
    return hits


def validate_stop(stop: Dict[str, Any], root: Path, max_files: int) -> Dict[str, Any]:
    """Resolve one stop against the tree and classify its health."""
    rel = str(stop["path"])
    anchor = str(stop.get("anchor") or "")
    target = root / rel
    result: Dict[str, Any] = {
        "stop": stop.get("stop"),
        "title": stop.get("title", rel),
        "path": rel,
        "anchor": anchor,
        "recorded_line": stop.get("line"),
        "status": "ok",
        "detail": "",
        "current_line": None,
        "fingerprint": stop.get("fingerprint"),
        "suggestions": [],
    }
    if not target.is_file():
        result["status"] = "deleted"
        result["detail"] = "file does not exist at the recorded path"
        result["suggestions"] = search_relocation(root, anchor, rel, max_files)
        return result
    if not anchor:
        result["detail"] = "file exists; no anchor recorded, so drift cannot be detected"
        return result

    span = anchor_span(target, anchor)
    if span is None:
        result["status"] = "moved"
        result["detail"] = f"anchor '{anchor}' is no longer in this file"
        result["suggestions"] = [s for s in search_relocation(root, anchor, rel, max_files) if s != rel]
        if not result["suggestions"]:
            result["status"] = "missing-anchor"
            result["detail"] = f"anchor '{anchor}' not found anywhere in the tree — renamed or deleted"
        return result

    start, _, body = span
    result["current_line"] = start
    current = fingerprint(body)
    recorded = stop.get("fingerprint")
    if recorded and recorded != current:
        result["status"] = "drifted"
        result["detail"] = "anchor body changed since the tour was written — re-read the note"
    elif stop.get("line") and abs(int(stop["line"]) - start) > 0:
        result["status"] = "shifted"
        result["detail"] = f"anchor moved from line {stop['line']} to {start} (content unchanged)"
    result["fingerprint"] = current
    return result


def validate_tour(tour: Dict[str, Any], repo: str, max_files: int) -> Dict[str, Any]:
    """Validate every stop and summarize the tour's health."""
    root = Path(repo)
    if not root.is_dir():
        raise SystemExit(f"error: not a directory: {repo}")
    results = [validate_stop(stop, root, max_files) for stop in tour["stops"]]
    counts: Dict[str, int] = {}
    for item in results:
        counts[item["status"]] = counts.get(item["status"], 0) + 1
    broken = sum(count for status, count in counts.items() if status not in ("ok", "shifted"))
    return {
        "tour": tour.get("title", "untitled tour"),
        "repo": str(root),
        "total_stops": len(results),
        "status_counts": counts,
        "broken_stops": broken,
        "health": round(counts.get("ok", 0) / len(results), 2) if results else 0.0,
        "stops": sorted(results, key=lambda r: STATUS_ORDER[r["status"]]),
    }


def rebuild_tour(tour: Dict[str, Any], report: Dict[str, Any]) -> Dict[str, Any]:
    """Return the tour with refreshed line numbers and fingerprints for resolvable stops."""
    by_path = {(r["path"], r["anchor"]): r for r in report["stops"]}
    updated = json.loads(json.dumps(tour))
    for stop in updated["stops"]:
        result = by_path.get((str(stop["path"]), str(stop.get("anchor") or "")))
        if result and result["status"] in ("ok", "shifted", "drifted") and result["current_line"]:
            stop["line"] = result["current_line"]
            stop["fingerprint"] = result["fingerprint"]
    return updated


def output(report: Dict[str, Any], fmt: str) -> None:
    """Print the validation report as text or JSON."""
    if fmt == "json":
        print(json.dumps(report, indent=2))
        return
    print(f"{report['tour']} — {report['total_stops']} stops, health {report['health']:.0%}, "
          f"{report['broken_stops']} broken")
    print("  " + ", ".join(f"{count} {status}" for status, count in sorted(report["status_counts"].items())) + "\n")
    for item in report["stops"]:
        if item["status"] == "ok":
            continue
        print(f"[{item['status']:<14}] stop {item['stop']}: {item['title']}")
        print(f"                 {item['path']}" + (f"::{item['anchor']}" if item["anchor"] else ""))
        print(f"                 {item['detail']}")
        for suggestion in item["suggestions"][:3]:
            print(f"                 -> maybe now at: {suggestion}")
    if report["broken_stops"] == 0:
        print("Every anchor resolves. Line shifts, if any, are cosmetic.")


def main() -> None:
    """Parse arguments, validate the tour, and exit non-zero when stops are broken."""
    parser = argparse.ArgumentParser(description="Validate a code tour against the current tree.")
    parser.add_argument("--tour", required=True, help="tour definition JSON")
    parser.add_argument("--repo", required=True, help="repository root the tour describes")
    parser.add_argument("--max-files", type=int, default=3000, help="relocation search cap (default: 3000)")
    parser.add_argument("--update", action="store_true",
                        help="print the tour with refreshed lines and fingerprints instead of a report")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="output format (default: text)")
    args = parser.parse_args()
    try:
        tour = load_tour(args.tour)
        report = validate_tour(tour, args.repo, args.max_files)
        if args.update:
            print(json.dumps(rebuild_tour(tour, report), indent=2, ensure_ascii=False))
        else:
            output(report, args.format)
    except SystemExit:
        raise
    except OSError as exc:
        print(f"error: could not validate tour: {exc}", file=sys.stderr)
        sys.exit(1)
    sys.exit(1 if report["broken_stops"] else 0)


if __name__ == "__main__":
    main()
