#!/usr/bin/env python3
"""Analyze API test coverage by comparing spec endpoints vs existing test files.

Parses an OpenAPI/Swagger JSON spec to extract all defined endpoints, then
scans test files in a given directory to detect which endpoints have test
coverage. Reports missing coverage, coverage percentage, and gaps by
HTTP method and tag.

Usage:
    python coverage_analyzer.py spec.json tests/
    python coverage_analyzer.py spec.json tests/ --json
    python coverage_analyzer.py spec.json tests/ --threshold 90
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


def load_spec(spec_path: str) -> dict:
    """Load and validate an OpenAPI/Swagger spec file."""
    path = Path(spec_path)
    if not path.exists():
        print(f"Error: spec file not found: {spec_path}", file=sys.stderr)
        sys.exit(2)
    try:
        with open(path, "r", encoding="utf-8") as f:
            spec = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON in spec file: {e}", file=sys.stderr)
        sys.exit(2)
    if not isinstance(spec, dict) or ("openapi" not in spec and "swagger" not in spec):
        print("Error: file does not appear to be an OpenAPI or Swagger spec", file=sys.stderr)
        sys.exit(2)
    return spec


def extract_spec_endpoints(spec: dict) -> list:
    """Extract all endpoint definitions from the spec."""
    endpoints = []
    paths = spec.get("paths", {})
    for path, path_item in paths.items():
        for method in ("get", "post", "put", "patch", "delete", "head", "options"):
            if method not in path_item:
                continue
            operation = path_item[method]
            endpoints.append({
                "path": path,
                "method": method.upper(),
                "operation_id": operation.get("operationId", ""),
                "tags": operation.get("tags", []),
                "summary": operation.get("summary", ""),
                "deprecated": operation.get("deprecated", False),
            })
    return endpoints


def scan_test_files(test_dir: str) -> list:
    """Recursively find test files in the given directory."""
    test_files = []
    test_dir_path = Path(test_dir)
    if not test_dir_path.exists():
        print(f"Error: test directory not found: {test_dir}", file=sys.stderr)
        sys.exit(2)

    # Common test file patterns
    patterns = ["test_*.py", "*_test.py", "*.test.ts", "*.test.js", "*.spec.ts", "*.spec.js"]
    for pattern in patterns:
        test_files.extend(test_dir_path.rglob(pattern))
    return sorted(set(test_files))


CALL_RE = re.compile(
    r'\.(get|post|put|patch|delete)\(\s*f?["\'](?:\{\w+\})?(/[^"\'\s]*)', re.IGNORECASE)
# Assertions on the response body, not just its status code
BODY_ASSERT_RE = re.compile(
    r'\.json\(\)\s*[\[.=!]|\.body\b|toMatchObject|toHaveProperty|toEqual\(|matchesSchema|\.headers\[',
    re.IGNORECASE)
COMMENT_RE = re.compile(r'(?m)^\s*(#|//).*$')
TEST_START_RE = re.compile(r'^\s*(?:async\s+)?def test_|^\s*(?:it|test)\(', re.MULTILINE)


def extract_tested_endpoints(test_files: list) -> list:
    """Find each HTTP call in test files, with its method, path and body-assertion flag.

    A call counts only when a method and a literal path appear together, so a file
    calling GET /a and DELETE /b never credits DELETE /a. A call is "asserted" when
    the test that contains it also checks the response body or headers.
    """
    tested = []
    for test_file in test_files:
        try:
            content = test_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        starts = [m.start() for m in TEST_START_RE.finditer(content)] + [len(content)]
        for match in CALL_RE.finditer(content):
            path = re.sub(r'\?.*$', '', match.group(2))
            begin = max([0] + [x for x in starts if x <= match.start()])
            end = min(x for x in starts if x > match.start())
            if "skip(" in content[begin:end] or "pass\n" in content[begin:end]:
                continue
            tested.append({
                "path": path,
                "method": match.group(1).upper(),
                "test_file": str(test_file),
                "asserted": bool(BODY_ASSERT_RE.search(COMMENT_RE.sub("", content[match.end():end]))),
            })
    return tested


def _path_regex(spec_path: str):
    """Regex matching concrete paths for a spec path: {id} or :id matches one segment."""
    parts = re.split(r'(\{[^}]+\}|:[A-Za-z_]+)', spec_path.rstrip("/").lower())
    body = "".join("[^/]+" if (x.startswith("{") or x.startswith(":")) else re.escape(x) for x in parts)
    return re.compile("^" + body + "/?$")


def _normalize_path(path: str) -> str:
    """Normalize an API path for comparison.

    Converts path parameters like {userId}, :userId to a canonical {param} form.
    """
    # OpenAPI style: /users/{userId} -> /users/{param}
    normalized = re.sub(r'\{[^}]+\}', '{param}', path)
    # Express style: /users/:userId -> /users/{param}
    normalized = re.sub(r':[a-zA-Z_]+', '{param}', normalized)
    return normalized.rstrip("/").lower()


def compute_coverage(spec_endpoints: list, tested_endpoints: list) -> dict:
    """Compare spec endpoints against tested calls to find gaps."""
    covered = []
    uncovered = []
    deprecated_skipped = 0
    asserted = 0
    for ep in spec_endpoints:
        if ep["deprecated"]:
            deprecated_skipped += 1
            continue
        rx = _path_regex(ep["path"])
        hits = [te for te in tested_endpoints
                if te["method"] == ep["method"] and rx.match(te["path"].rstrip("/").lower() or "/")]
        if hits:
            deep = any(te["asserted"] for te in hits)
            asserted += deep
            covered.append({**ep, "asserted": deep,
                            "test_files": sorted({te["test_file"] for te in hits})})
        else:
            uncovered.append(ep)

    active_total = len(spec_endpoints) - deprecated_skipped
    coverage_pct = (len(covered) / active_total * 100) if active_total > 0 else 0.0
    asserted_pct = (asserted / active_total * 100) if active_total > 0 else 0.0

    # Coverage by method
    method_stats = {}
    for ep in spec_endpoints:
        if ep["deprecated"]:
            continue
        m = ep["method"]
        method_stats.setdefault(m, {"total": 0, "covered": 0})
        method_stats[m]["total"] += 1
    for ep in covered:
        m = ep["method"]
        method_stats[m]["covered"] += 1

    # Coverage by tag
    tag_stats = {}
    for ep in spec_endpoints:
        if ep["deprecated"]:
            continue
        tags = ep["tags"] or ["untagged"]
        for tag in tags:
            tag_stats.setdefault(tag, {"total": 0, "covered": 0})
            tag_stats[tag]["total"] += 1
    for ep in covered:
        tags = ep["tags"] or ["untagged"]
        for tag in tags:
            tag_stats[tag]["covered"] += 1

    return {
        "total_endpoints": len(spec_endpoints),
        "deprecated_skipped": deprecated_skipped,
        "active_endpoints": active_total,
        "covered": len(covered),
        "uncovered_count": len(uncovered),
        "coverage_percent": round(coverage_pct, 1),
        "asserted": asserted,
        "asserted_percent": round(asserted_pct, 1),
        "covered_endpoints": covered,
        "uncovered_endpoints": uncovered,
        "by_method": method_stats,
        "by_tag": tag_stats,
        "test_files_scanned": len(set(te["test_file"] for te in tested_endpoints)),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Analyze API test coverage by comparing spec endpoints vs test files.",
        epilog="Example: python coverage_analyzer.py openapi.json tests/ --threshold 90",
    )
    parser.add_argument("spec", help="Path to OpenAPI/Swagger JSON spec file")
    parser.add_argument("test_dir", help="Directory containing test files to scan")
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.0,
        help="Minimum %% of endpoints whose tests assert on the response body "
             "(exit 1 if below; default 0 = no gate)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--show-covered",
        action="store_true",
        help="Also list covered endpoints (default: only show gaps)",
    )
    args = parser.parse_args()

    spec = load_spec(args.spec)
    spec_endpoints = extract_spec_endpoints(spec)

    if not spec_endpoints:
        print("Error: no endpoints found in spec.", file=sys.stderr)
        sys.exit(2)

    test_files = scan_test_files(args.test_dir)
    tested_endpoints = extract_tested_endpoints(test_files)
    report = compute_coverage(spec_endpoints, tested_endpoints)

    if args.json_output:
        output = {
            "coverage_percent": report["coverage_percent"],
            "asserted_percent": report["asserted_percent"],
            "status_only": [f'{e["method"]} {e["path"]}' for e in report["covered_endpoints"] if not e["asserted"]],
            "total_endpoints": report["active_endpoints"],
            "covered": report["covered"],
            "uncovered_count": report["uncovered_count"],
            "deprecated_skipped": report["deprecated_skipped"],
            "test_files_scanned": report["test_files_scanned"],
            "by_method": report["by_method"],
            "by_tag": report["by_tag"],
            "uncovered_endpoints": [
                {"method": ep["method"], "path": ep["path"], "summary": ep["summary"]}
                for ep in report["uncovered_endpoints"]
            ],
        }
        if args.show_covered:
            output["covered_endpoints"] = [
                {"method": ep["method"], "path": ep["path"], "test_files": ep["test_files"]}
                for ep in report["covered_endpoints"]
            ]
        print(json.dumps(output, indent=2))
    else:
        pct = report["coverage_percent"]
        bar_len = 40
        filled = int(bar_len * pct / 100)
        bar = "#" * filled + "-" * (bar_len - filled)

        print("=== API Test Coverage Report ===")
        print()
        print(f"Coverage: [{bar}] {pct}%")
        print(f"  {report['covered']}/{report['active_endpoints']} endpoints called by a test")
        print(f"  {report['asserted']}/{report['active_endpoints']} endpoints with a body/header assertion "
              f"({report['asserted_percent']}%) <- gated by --threshold")
        if report["deprecated_skipped"]:
            print(f"  {report['deprecated_skipped']} deprecated endpoints skipped")
        print(f"  {report['test_files_scanned']} test files scanned")
        print()

        # By method
        print("Coverage by HTTP method:")
        for method in sorted(report["by_method"].keys()):
            stats = report["by_method"][method]
            m_pct = (stats["covered"] / stats["total"] * 100) if stats["total"] else 0
            print(f"  {method:7s} {stats['covered']}/{stats['total']} ({m_pct:.0f}%)")
        print()

        # By tag
        if report["by_tag"]:
            print("Coverage by tag:")
            for tag in sorted(report["by_tag"].keys()):
                stats = report["by_tag"][tag]
                t_pct = (stats["covered"] / stats["total"] * 100) if stats["total"] else 0
                print(f"  {tag:20s} {stats['covered']}/{stats['total']} ({t_pct:.0f}%)")
            print()

        # Uncovered endpoints
        if report["uncovered_endpoints"]:
            print("UNCOVERED endpoints:")
            for ep in report["uncovered_endpoints"]:
                summary = f" - {ep['summary']}" if ep["summary"] else ""
                print(f"  {ep['method']:7s} {ep['path']}{summary}")
            print()

        # Covered endpoints (optional)
        if args.show_covered and report["covered_endpoints"]:
            print("COVERED endpoints:")
            for ep in report["covered_endpoints"]:
                files = ", ".join(ep["test_files"][:3])
                more = f" (+{len(ep['test_files'])-3} more)" if len(ep["test_files"]) > 3 else ""
                print(f"  {ep['method']:7s} {ep['path']}  <- {files}{more}")
            print()

    # Threshold check
    if args.threshold > 0 and report["asserted_percent"] < args.threshold:
        msg = f"Asserted coverage {report['asserted_percent']}% is below threshold {args.threshold}%"
        if not args.json_output:
            print(f"FAIL: {msg}")
        sys.exit(1)


if __name__ == "__main__":
    main()
