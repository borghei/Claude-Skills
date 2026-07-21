#!/usr/bin/env python3
"""Propose candidate tour stops for an unfamiliar repository.

Ranks files by entry-point signals, fan-in from the internal import graph, and
boundary/config roles. Python fan-in uses AST imports; other languages fall back to
filename-reference heuristics.

Usage:
  python3 tour_propose.py --repo .
  python3 tour_propose.py --repo . --max-stops 8 --format json
  python3 tour_propose.py --repo . --exclude vendor --exclude generated
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
import warnings
from pathlib import Path
from typing import Any, Dict, List, Set

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build",
             ".mypy_cache", ".pytest_cache", "target", "vendor", ".next"}
CODE_SUFFIXES = {".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rb", ".java", ".rs"}
ENTRY_NAMES = {"main.py", "__main__.py", "app.py", "cli.py", "manage.py", "server.py",
               "index.js", "index.ts", "main.go", "main.rs", "app.ts", "wsgi.py", "asgi.py"}
CONFIG_NAMES = {"settings.py", "config.py", "conf.py", "dockerfile", "docker-compose.yml",
                "makefile", "pyproject.toml", "package.json", "go.mod", "cargo.toml",
                "requirements.txt", ".env.example", "alembic.ini"}
BOUNDARY_HINTS = ("routes", "router", "api", "handler", "controller", "schema", "models",
                  "migration", "client", "adapter", "gateway", "middleware", "auth")
TEST_DIRS = {"test", "tests", "spec", "specs", "__tests__", "fixtures", "e2e", "testing"}
TEST_FILE_RE = re.compile(r"(^test_|_test\.|\.test\.|\.spec\.|^conftest\.)")

ROLE_WEIGHTS = {"entry-point": 40, "config": 22, "boundary": 18, "hub": 0}


def walk_files(root: Path, excludes: Set[str], max_files: int) -> List[Path]:
    """Return code and config files under root, skipping vendored and excluded paths."""
    found: List[Path] = []
    for path in sorted(root.rglob("*")):
        if len(found) >= max_files:
            break
        if not path.is_file():
            continue
        parts = {p.lower() for p in path.parts}
        if parts & SKIP_DIRS or parts & excludes:
            continue
        if path.suffix in CODE_SUFFIXES or path.name.lower() in CONFIG_NAMES:
            found.append(path)
    if not found:
        raise SystemExit(f"error: no source files found under {root} (all excluded or empty?)")
    return found


def python_fan_in(root: Path, files: List[Path]) -> Dict[str, int]:
    """Count how many modules import each Python file, using AST import analysis."""
    by_stem: Dict[str, List[str]] = {}
    for path in files:
        if path.suffix == ".py":
            by_stem.setdefault(path.stem, []).append(str(path))
    counts: Dict[str, int] = {}
    for path in files:
        if path.suffix != ".py":
            continue
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        except (SyntaxError, OSError, ValueError):
            continue
        imported: Set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[-1] for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imported.add(node.module.split(".")[-1])
                imported.update(alias.name for alias in node.names)
        for stem in imported:
            for target in by_stem.get(stem, []):
                if target != str(path):
                    counts[target] = counts.get(target, 0) + 1
    return counts


def textual_fan_in(files: List[Path]) -> Dict[str, int]:
    """Approximate fan-in for non-Python files by counting references to their stem."""
    stems = {path.stem: str(path) for path in files if path.suffix in CODE_SUFFIXES and path.suffix != ".py"}
    counts: Dict[str, int] = {}
    if not stems:
        return counts
    pattern = re.compile(r"[\"'./]([A-Za-z0-9_-]+)[\"'.]")
    for path in files:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for stem in set(pattern.findall(text)):
            target = stems.get(stem)
            if target and target != str(path):
                counts[target] = counts.get(target, 0) + 1
    return counts


def classify(path: Path, root: Path) -> str:
    """Assign a file the tour role that best describes why it matters."""
    rel = path.relative_to(root)
    name = path.name.lower()
    parts = {part.lower() for part in rel.parts[:-1]}
    if parts & TEST_DIRS or TEST_FILE_RE.search(name):
        return "test"
    if name in ENTRY_NAMES:
        return "entry-point"
    if name in CONFIG_NAMES:
        return "config"
    tokens = parts | set(re.split(r"[_.-]", path.stem.lower()))
    if tokens & set(BOUNDARY_HINTS):
        return "boundary"
    return "hub"


def rationale(role: str, fan_in: int, lines: int) -> str:
    """Explain in one sentence why a candidate earned its place on the tour."""
    if role == "entry-point":
        return "execution starts here — the tour's first stop should be reachable from this file"
    if role == "config":
        return "declares dependencies and runtime shape; explains what the system assumes"
    if role == "boundary":
        return f"crosses a system boundary; {fan_in} internal references depend on its contract"
    if fan_in >= 5:
        return f"high fan-in ({fan_in} modules import it) — changing it moves the whole system"
    return f"{lines} lines with {fan_in} inbound references; carries local logic worth a stop"


def propose(repo: str, excludes: Set[str], max_stops: int, max_files: int) -> Dict[str, Any]:
    """Score every candidate file and return an ordered tour proposal."""
    root = Path(repo)
    if not root.is_dir():
        raise SystemExit(f"error: not a directory: {repo}")
    files = walk_files(root, excludes, max_files)
    fan_in = python_fan_in(root, files)
    fan_in.update({k: fan_in.get(k, 0) + v for k, v in textual_fan_in(files).items()})

    candidates: List[Dict[str, Any]] = []
    for path in files:
        role = classify(path, root)
        if role == "test":
            continue
        try:
            lines = len(path.read_text(encoding="utf-8", errors="replace").splitlines())
        except OSError:
            continue
        inbound = fan_in.get(str(path), 0)
        score = ROLE_WEIGHTS.get(role, 0) + inbound * 6 + min(lines // 40, 10)
        candidates.append({
            "path": str(path.relative_to(root)),
            "role": role,
            "fan_in": inbound,
            "lines": lines,
            "score": score,
            "why": rationale(role, inbound, lines),
        })

    order = {"entry-point": 0, "config": 1, "boundary": 2, "hub": 3}
    top = sorted(candidates, key=lambda c: -c["score"])[:max_stops]
    stops = sorted(top, key=lambda c: (order[c["role"]], -c["score"]))
    for index, stop in enumerate(stops, start=1):
        stop["stop"] = index
    roles: Dict[str, int] = {}
    for candidate in candidates:
        roles[candidate["role"]] = roles.get(candidate["role"], 0) + 1
    return {
        "repo": str(root),
        "files_analyzed": len(files),
        "candidates": len(candidates),
        "role_counts": roles,
        "stops": stops,
    }


def output(report: Dict[str, Any], fmt: str) -> None:
    """Print the proposed tour as text or JSON."""
    if fmt == "json":
        print(json.dumps(report, indent=2))
        return
    print(f"{report['repo']}: {report['files_analyzed']} files analyzed, "
          f"{report['candidates']} candidates")
    print("  roles: " + ", ".join(f"{count} {role}" for role, count in sorted(report["role_counts"].items())))
    print(f"\nProposed tour ({len(report['stops'])} stops, ordered entry -> boundary -> internals):\n")
    for stop in report["stops"]:
        print(f"{stop['stop']:>2}. {stop['path']}")
        print(f"    role={stop['role']:<12} fan-in={stop['fan_in']:<3} lines={stop['lines']:<5} score={stop['score']}")
        print(f"    {stop['why']}")
    print("\nThese are candidates, not a tour. Cut any stop you cannot write a "
          "'why it is this way' note for.")


def main() -> None:
    """Parse arguments, analyze the repository, and print the tour proposal."""
    parser = argparse.ArgumentParser(description="Propose candidate code-tour stops for a repository.")
    parser.add_argument("--repo", required=True, help="repository root to analyze")
    parser.add_argument("--max-stops", type=int, default=7, help="stops to propose (default: 7)")
    parser.add_argument("--max-files", type=int, default=4000, help="file scan cap (default: 4000)")
    parser.add_argument("--exclude", action="append", default=[],
                        help="directory name to skip; repeatable")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="output format (default: text)")
    args = parser.parse_args()
    if args.max_stops < 1:
        raise SystemExit("error: --max-stops must be at least 1")
    try:
        report = propose(args.repo, {e.lower() for e in args.exclude}, args.max_stops, args.max_files)
        output(report, args.format)
    except SystemExit:
        raise
    except OSError as exc:
        print(f"error: could not analyze repository: {exc}", file=sys.stderr)
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
