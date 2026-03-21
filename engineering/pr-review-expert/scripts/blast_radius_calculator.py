#!/usr/bin/env python3
"""Calculate PR blast radius by analyzing import chains and dependency trees.

Given a set of changed files and a source root, walks the file system to build
an import/dependency graph, then computes how many files are directly and
transitively affected by the changes. Supports Python, JavaScript/TypeScript,
Go, and generic import patterns.

Usage:
    python blast_radius_calculator.py --changed src/lib/auth.ts src/utils/hash.py --root ./src
    git diff --name-only main...HEAD | python blast_radius_calculator.py --root .
    python blast_radius_calculator.py --changed api/models.py --root . --json --depth 5
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


# --- Import pattern extractors ---

# Python: import foo, from foo import bar, from . import bar
PY_IMPORT_RE = [
    re.compile(r"^\s*import\s+([\w.]+)", re.MULTILINE),
    re.compile(r"^\s*from\s+([\w.]+)\s+import", re.MULTILINE),
]

# JavaScript/TypeScript: import ... from '...', require('...')
JS_IMPORT_RE = [
    re.compile(r"""(?:import|export)\s+.*?from\s+['"](\.[\w./\\-]+)['"]""", re.MULTILINE),
    re.compile(r"""require\(\s*['"](\.[\w./\\-]+)['"]\s*\)""", re.MULTILINE),
]

# Go: import "path" or import ( "path" )
GO_IMPORT_RE = [
    re.compile(r"""(?:import\s+)?"([\w./\\-]+)"$""", re.MULTILINE),
]

SUPPORTED_EXTENSIONS = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".jsx": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".go": "go",
}

SKIP_DIRS = {
    "node_modules", ".git", "__pycache__", ".venv", "venv",
    "dist", "build", ".next", ".nuxt", "vendor", ".tox",
    "coverage", ".pytest_cache", ".mypy_cache",
}


def discover_files(root: str) -> List[str]:
    """Walk the source tree and collect supported source files."""
    files = []
    root_path = Path(root).resolve()
    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fname in filenames:
            ext = os.path.splitext(fname)[1]
            if ext in SUPPORTED_EXTENSIONS:
                full = os.path.join(dirpath, fname)
                files.append(full)
    return files


def normalize_path(path: str, root: str) -> str:
    """Convert absolute path to root-relative with forward slashes."""
    try:
        return str(Path(path).resolve().relative_to(Path(root).resolve()))
    except ValueError:
        return path


def extract_imports_python(content: str, file_path: str, root: str) -> List[str]:
    """Extract import targets from Python source."""
    imports = []
    for pattern in PY_IMPORT_RE:
        for match in pattern.finditer(content):
            module = match.group(1)
            # Convert dotted module to path
            module_path = module.replace(".", "/")
            imports.append(module_path)
    return imports


def extract_imports_js(content: str, file_path: str, root: str) -> List[str]:
    """Extract import targets from JS/TS source."""
    imports = []
    for pattern in JS_IMPORT_RE:
        for match in pattern.finditer(content):
            rel_path = match.group(1)
            # Resolve relative to file's directory
            file_dir = os.path.dirname(file_path)
            resolved = os.path.normpath(os.path.join(file_dir, rel_path))
            imports.append(normalize_path(resolved, root))
    return imports


def extract_imports_go(content: str, file_path: str, root: str) -> List[str]:
    """Extract import targets from Go source."""
    imports = []
    for pattern in GO_IMPORT_RE:
        for match in pattern.finditer(content):
            imports.append(match.group(1))
    return imports


EXTRACTORS = {
    "python": extract_imports_python,
    "javascript": extract_imports_js,
    "typescript": extract_imports_js,
    "go": extract_imports_go,
}


def resolve_import_to_file(imp: str, known_files: Set[str]) -> Optional[str]:
    """Try to resolve an import string to a known file path."""
    # Direct match
    if imp in known_files:
        return imp

    # Try common extensions and index files
    candidates = [
        imp,
        imp + ".py",
        imp + ".ts",
        imp + ".tsx",
        imp + ".js",
        imp + ".jsx",
        imp + ".mjs",
        imp + ".go",
        os.path.join(imp, "index.ts"),
        os.path.join(imp, "index.tsx"),
        os.path.join(imp, "index.js"),
        os.path.join(imp, "__init__.py"),
        os.path.join(imp, "mod.go"),
    ]
    for c in candidates:
        normalized = os.path.normpath(c)
        if normalized in known_files:
            return normalized
    return None


def build_dependency_graph(root: str) -> Tuple[Dict[str, Set[str]], Dict[str, Set[str]], Set[str]]:
    """Build forward (imports) and reverse (imported-by) dependency graphs.

    Returns:
        imports_graph: file -> set of files it imports
        reverse_graph: file -> set of files that import it
        all_files: set of all discovered file paths (root-relative)
    """
    all_abs_files = discover_files(root)
    all_files = set()
    file_abs_map = {}

    for abs_path in all_abs_files:
        rel = normalize_path(abs_path, root)
        all_files.add(rel)
        file_abs_map[rel] = abs_path

    imports_graph: Dict[str, Set[str]] = defaultdict(set)
    reverse_graph: Dict[str, Set[str]] = defaultdict(set)

    for rel_path, abs_path in file_abs_map.items():
        ext = os.path.splitext(abs_path)[1]
        lang = SUPPORTED_EXTENSIONS.get(ext)
        if not lang or lang not in EXTRACTORS:
            continue

        try:
            with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except (OSError, IOError):
            continue

        extractor = EXTRACTORS[lang]
        raw_imports = extractor(content, rel_path, root)

        for imp in raw_imports:
            resolved = resolve_import_to_file(imp, all_files)
            if resolved and resolved != rel_path:
                imports_graph[rel_path].add(resolved)
                reverse_graph[resolved].add(rel_path)

    return dict(imports_graph), dict(reverse_graph), all_files


def compute_blast_radius(
    changed_files: List[str],
    reverse_graph: Dict[str, Set[str]],
    max_depth: int,
) -> Dict[str, Dict]:
    """BFS from changed files through reverse dependency graph.

    Returns per-changed-file impact analysis with depth tracking.
    """
    results = {}

    for changed in changed_files:
        visited: Dict[str, int] = {}
        queue: deque = deque()

        # Seed with direct dependents
        if changed in reverse_graph:
            for dep in reverse_graph[changed]:
                if dep not in changed_files:
                    queue.append((dep, 1))
                    visited[dep] = 1

        # BFS
        while queue:
            current, depth = queue.popleft()
            if depth >= max_depth:
                continue
            if current in reverse_graph:
                for dep in reverse_graph[current]:
                    if dep not in visited and dep not in changed_files:
                        visited[dep] = depth + 1
                        queue.append((dep, depth + 1))

        direct = [f for f, d in visited.items() if d == 1]
        transitive = [f for f, d in visited.items() if d > 1]

        results[changed] = {
            "direct_dependents": sorted(direct),
            "transitive_dependents": sorted(transitive),
            "direct_count": len(direct),
            "transitive_count": len(transitive),
            "total_affected": len(visited),
            "max_chain_depth": max(visited.values()) if visited else 0,
        }

    return results


def classify_severity(total_affected: int) -> str:
    """Classify blast radius severity based on total affected files."""
    if total_affected >= 20:
        return "CRITICAL"
    elif total_affected >= 10:
        return "HIGH"
    elif total_affected >= 3:
        return "MEDIUM"
    else:
        return "LOW"


def generate_report(
    changed_files: List[str],
    root: str,
    max_depth: int,
) -> Dict:
    """Full blast radius analysis report."""
    imports_graph, reverse_graph, all_files = build_dependency_graph(root)

    # Normalize changed file paths
    normalized_changed = []
    for cf in changed_files:
        norm = normalize_path(cf, root)
        if norm in all_files:
            normalized_changed.append(norm)
        else:
            # Try without leading path components
            basename = os.path.basename(cf)
            matches = [f for f in all_files if f.endswith(cf) or os.path.basename(f) == basename]
            if matches:
                normalized_changed.extend(matches)
            else:
                normalized_changed.append(norm)

    per_file = compute_blast_radius(normalized_changed, reverse_graph, max_depth)

    # Aggregate
    all_affected: Set[str] = set()
    for info in per_file.values():
        all_affected.update(info["direct_dependents"])
        all_affected.update(info["transitive_dependents"])

    total_affected = len(all_affected)
    overall_severity = classify_severity(total_affected)

    # Hotspots: most-imported files among the changed set
    hotspots = []
    for cf in normalized_changed:
        dep_count = len(reverse_graph.get(cf, set()))
        if dep_count > 0:
            hotspots.append({"file": cf, "dependent_count": dep_count})
    hotspots.sort(key=lambda x: x["dependent_count"], reverse=True)

    return {
        "overall_severity": overall_severity,
        "total_files_in_project": len(all_files),
        "changed_files": normalized_changed,
        "changed_file_count": len(normalized_changed),
        "total_affected_files": total_affected,
        "impact_percentage": round(total_affected / max(len(all_files), 1) * 100, 1),
        "max_depth_searched": max_depth,
        "hotspots": hotspots[:10],
        "per_file_analysis": per_file,
        "all_affected_files": sorted(all_affected),
    }


def format_human(result: Dict) -> str:
    """Format blast radius report for human reading."""
    lines = []
    lines.append("=" * 60)
    lines.append("  BLAST RADIUS ANALYSIS")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Overall Severity:    {result['overall_severity']}")
    lines.append(f"Project Files:       {result['total_files_in_project']}")
    lines.append(f"Changed Files:       {result['changed_file_count']}")
    lines.append(f"Affected Files:      {result['total_affected_files']}")
    lines.append(f"Impact:              {result['impact_percentage']}% of project")
    lines.append(f"Max Depth Searched:  {result['max_depth_searched']}")
    lines.append("")

    # Hotspots
    if result["hotspots"]:
        lines.append("Dependency Hotspots (most imported changed files):")
        for hs in result["hotspots"]:
            lines.append(f"  {hs['file']} <- {hs['dependent_count']} dependents")
        lines.append("")

    # Per-file breakdown
    lines.append("-" * 60)
    lines.append("PER-FILE IMPACT")
    lines.append("-" * 60)

    for changed_file, info in result["per_file_analysis"].items():
        sev = classify_severity(info["total_affected"])
        lines.append("")
        lines.append(f"[{sev}] {changed_file}")
        lines.append(f"  Direct dependents:     {info['direct_count']}")
        lines.append(f"  Transitive dependents: {info['transitive_count']}")
        lines.append(f"  Total affected:        {info['total_affected']}")
        if info["max_chain_depth"] > 0:
            lines.append(f"  Longest chain depth:   {info['max_chain_depth']}")

        if info["direct_dependents"]:
            lines.append("  Direct:")
            for dep in info["direct_dependents"][:10]:
                lines.append(f"    -> {dep}")
            if len(info["direct_dependents"]) > 10:
                lines.append(f"    ... and {len(info['direct_dependents']) - 10} more")

        if info["transitive_dependents"]:
            lines.append("  Transitive:")
            for dep in info["transitive_dependents"][:10]:
                lines.append(f"    ~> {dep}")
            if len(info["transitive_dependents"]) > 10:
                lines.append(f"    ... and {len(info['transitive_dependents']) - 10} more")

    # Summary
    lines.append("")
    lines.append("-" * 60)
    lines.append("AFFECTED FILE LIST")
    lines.append("-" * 60)
    if result["all_affected_files"]:
        for af in result["all_affected_files"]:
            lines.append(f"  {af}")
    else:
        lines.append("  No downstream dependencies found.")

    lines.append("")
    lines.append("=" * 60)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Calculate PR blast radius by analyzing import chains and "
                    "dependency trees from changed files.",
        epilog="Example: git diff --name-only main...HEAD | python blast_radius_calculator.py --root .",
    )
    parser.add_argument(
        "--changed", "-c",
        nargs="+",
        help="List of changed file paths. If omitted, reads from stdin.",
    )
    parser.add_argument(
        "--root", "-r",
        default=".",
        help="Source root directory to scan for dependencies (default: current directory).",
    )
    parser.add_argument(
        "--depth", "-d",
        type=int,
        default=5,
        help="Maximum transitive dependency depth to traverse (default: 5).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as JSON.",
    )
    args = parser.parse_args()

    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        print(f"Error: Root directory not found: {root}", file=sys.stderr)
        sys.exit(1)

    if args.changed:
        changed_files = args.changed
    else:
        if sys.stdin.isatty():
            print("Reading changed file paths from stdin (one per line)...", file=sys.stderr)
        changed_files = [line.strip() for line in sys.stdin if line.strip()]

    if not changed_files:
        print("Error: No changed files provided.", file=sys.stderr)
        sys.exit(1)

    result = generate_report(changed_files, root, args.depth)

    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print(format_human(result))


if __name__ == "__main__":
    main()
