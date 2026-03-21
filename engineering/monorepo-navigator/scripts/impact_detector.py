#!/usr/bin/env python3
"""
Impact Detector - Determine which monorepo packages are affected by file changes.

Given a list of changed files (or a git ref to diff against), this tool resolves
which packages are directly affected, then computes transitive dependents to
show the full blast radius. Useful for selective CI builds and PR impact summaries.

Author: Claude Skills Engineering Team
License: MIT
"""

import argparse
import glob
import json
import os
import subprocess
import sys
from collections import deque
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class ImpactResult:
    """Result of impact analysis."""
    changed_files: List[str]
    directly_affected: List[str]
    transitively_affected: List[str]
    total_affected: List[str]
    unaffected: List[str]
    blast_radius_percent: float
    impact_chains: Dict[str, List[str]]
    root_config_changed: bool
    warnings: List[str]


class MonorepoGraph:
    """Builds and queries the internal dependency graph."""

    def __init__(self, root_path: str):
        self.root_path = Path(root_path).resolve()
        self.packages: Dict[str, str] = {}  # name -> relative path
        self.paths_to_names: Dict[str, str] = {}  # relative path -> name
        self.deps: Dict[str, Set[str]] = {}  # name -> set of internal deps
        self.reverse_deps: Dict[str, Set[str]] = {}  # name -> set of dependents
        self.warnings: List[str] = []

    def build(self) -> None:
        """Discover packages and build the dependency graph."""
        workspace_globs = self._detect_workspaces()
        if not workspace_globs:
            workspace_globs = ["packages/*", "apps/*", "libs/*", "modules/*"]
            self.warnings.append("No workspace config found; using default glob patterns.")

        self._discover_packages(workspace_globs)
        self._build_graph()

    def _detect_workspaces(self) -> List[str]:
        """Detect workspace globs from config files."""
        # pnpm-workspace.yaml
        pnpm_ws = self.root_path / "pnpm-workspace.yaml"
        if pnpm_ws.exists():
            return self._parse_pnpm_workspace(pnpm_ws)

        # package.json workspaces
        root_pkg = self.root_path / "package.json"
        if root_pkg.exists():
            try:
                with open(root_pkg, "r") as f:
                    data = json.load(f)
                ws = data.get("workspaces")
                if isinstance(ws, list):
                    return ws
                if isinstance(ws, dict) and "packages" in ws:
                    return ws["packages"]
            except (json.JSONDecodeError, OSError):
                pass

        # lerna.json
        lerna_cfg = self.root_path / "lerna.json"
        if lerna_cfg.exists():
            try:
                with open(lerna_cfg, "r") as f:
                    return json.load(f).get("packages", ["packages/*"])
            except (json.JSONDecodeError, OSError):
                pass

        return []

    def _parse_pnpm_workspace(self, filepath: Path) -> List[str]:
        """Parse pnpm-workspace.yaml without external YAML library."""
        globs = []
        try:
            with open(filepath, "r") as f:
                in_packages = False
                for line in f:
                    stripped = line.strip()
                    if stripped == "packages:":
                        in_packages = True
                        continue
                    if in_packages:
                        if stripped.startswith("- "):
                            globs.append(stripped[2:].strip().strip("'\""))
                        elif stripped and not stripped.startswith("#"):
                            break
        except OSError:
            pass
        return globs

    def _discover_packages(self, workspace_globs: List[str]) -> None:
        """Find all packages matching workspace globs."""
        for ws_glob in workspace_globs:
            if ws_glob.startswith("!"):
                continue
            pattern = str(self.root_path / ws_glob / "package.json")
            for pkg_path in sorted(glob.glob(pattern)):
                pkg_json = Path(pkg_path)
                try:
                    with open(pkg_json, "r") as f:
                        data = json.load(f)
                except (json.JSONDecodeError, OSError):
                    continue
                name = data.get("name")
                if not name:
                    continue
                rel_path = str(pkg_json.parent.relative_to(self.root_path))
                self.packages[name] = rel_path
                self.paths_to_names[rel_path] = name

    def _build_graph(self) -> None:
        """Build dependency and reverse-dependency maps."""
        internal_names = set(self.packages.keys())
        for name, rel_path in self.packages.items():
            pkg_json = self.root_path / rel_path / "package.json"
            try:
                with open(pkg_json, "r") as f:
                    data = json.load(f)
            except (json.JSONDecodeError, OSError):
                continue

            all_dep_sections = [
                data.get("dependencies", {}),
                data.get("devDependencies", {}),
                data.get("peerDependencies", {}),
            ]
            internal_deps = set()
            for section in all_dep_sections:
                for dep_name in section:
                    if dep_name in internal_names:
                        internal_deps.add(dep_name)

            self.deps[name] = internal_deps
            for dep in internal_deps:
                self.reverse_deps.setdefault(dep, set()).add(name)

    def get_package_for_file(self, filepath: str) -> Optional[str]:
        """Determine which package a file belongs to based on path prefix."""
        # Normalize path
        normalized = filepath.replace("\\", "/").lstrip("./")

        # Sort paths longest first for most specific match
        sorted_paths = sorted(self.paths_to_names.keys(), key=len, reverse=True)
        for pkg_path in sorted_paths:
            if normalized.startswith(pkg_path + "/") or normalized == pkg_path:
                return self.paths_to_names[pkg_path]
        return None

    def get_transitive_dependents(self, package_name: str) -> List[str]:
        """BFS to find all transitive dependents of a package."""
        visited: Set[str] = set()
        queue = deque([package_name])
        result = []

        while queue:
            current = queue.popleft()
            for dependent in self.reverse_deps.get(current, set()):
                if dependent not in visited:
                    visited.add(dependent)
                    result.append(dependent)
                    queue.append(dependent)

        return sorted(result)

    def get_impact_chain(self, source: str, target: str) -> List[str]:
        """Find the shortest dependency chain from source to target (via reverse deps)."""
        if source == target:
            return [source]
        visited: Set[str] = {source}
        queue: deque = deque([(source, [source])])
        while queue:
            current, path = queue.popleft()
            for dep in self.reverse_deps.get(current, set()):
                if dep == target:
                    return path + [dep]
                if dep not in visited:
                    visited.add(dep)
                    queue.append((dep, path + [dep]))
        return []


ROOT_CONFIG_FILES = {
    "turbo.json", "pnpm-workspace.yaml", "lerna.json", "nx.json",
    "tsconfig.json", "tsconfig.base.json", ".eslintrc.js", ".eslintrc.json",
    "jest.config.js", "vitest.config.ts", "pnpm-lock.yaml", "yarn.lock",
    "package-lock.json",
}


def get_changed_files_from_git(root_path: str, ref: str) -> List[str]:
    """Get list of changed files compared to a git ref."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", ref],
            capture_output=True,
            text=True,
            cwd=root_path,
            timeout=30,
        )
        if result.returncode != 0:
            # Try with merge-base
            merge_base = subprocess.run(
                ["git", "merge-base", ref, "HEAD"],
                capture_output=True,
                text=True,
                cwd=root_path,
                timeout=15,
            )
            if merge_base.returncode == 0:
                base = merge_base.stdout.strip()
                result = subprocess.run(
                    ["git", "diff", "--name-only", base],
                    capture_output=True,
                    text=True,
                    cwd=root_path,
                    timeout=30,
                )
        return [f for f in result.stdout.strip().split("\n") if f]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []


def detect_impact(
    root_path: str,
    changed_files: List[str],
) -> ImpactResult:
    """Run impact detection on the given changed files."""
    graph = MonorepoGraph(root_path)
    graph.build()

    all_package_names = set(graph.packages.keys())
    directly_affected: Set[str] = set()
    root_config_changed = False

    for filepath in changed_files:
        basename = os.path.basename(filepath)
        if basename in ROOT_CONFIG_FILES or filepath.startswith(".github/"):
            root_config_changed = True

        pkg_name = graph.get_package_for_file(filepath)
        if pkg_name:
            directly_affected.add(pkg_name)

    # Compute transitive dependents
    transitively_affected: Set[str] = set()
    for pkg in directly_affected:
        for dep in graph.get_transitive_dependents(pkg):
            if dep not in directly_affected:
                transitively_affected.add(dep)

    total_affected = directly_affected | transitively_affected

    # If root config changed, all packages are affected
    if root_config_changed:
        total_affected = all_package_names
        transitively_affected = all_package_names - directly_affected

    unaffected = sorted(all_package_names - total_affected)

    # Build impact chains for transitively affected packages
    impact_chains: Dict[str, List[str]] = {}
    for target in sorted(transitively_affected):
        for source in sorted(directly_affected):
            chain = graph.get_impact_chain(source, target)
            if chain:
                impact_chains[target] = chain
                break

    total_count = len(all_package_names) if all_package_names else 1
    blast_pct = round(len(total_affected) / total_count * 100, 1)

    return ImpactResult(
        changed_files=changed_files,
        directly_affected=sorted(directly_affected),
        transitively_affected=sorted(transitively_affected),
        total_affected=sorted(total_affected),
        unaffected=unaffected,
        blast_radius_percent=blast_pct,
        impact_chains=impact_chains,
        root_config_changed=root_config_changed,
        warnings=graph.warnings,
    )


def format_human(result: ImpactResult) -> str:
    """Format impact result for human-readable output."""
    lines = []
    lines.append("=" * 60)
    lines.append("IMPACT ANALYSIS")
    lines.append("=" * 60)
    lines.append(f"Changed files:     {len(result.changed_files)}")
    lines.append(f"Blast radius:      {result.blast_radius_percent}%")
    if result.root_config_changed:
        lines.append("Root config changed: YES (all packages affected)")
    lines.append("")

    lines.append("-" * 60)
    lines.append(f"DIRECTLY AFFECTED ({len(result.directly_affected)})")
    lines.append("-" * 60)
    for pkg in result.directly_affected:
        lines.append(f"  * {pkg}")
    lines.append("")

    if result.transitively_affected:
        lines.append("-" * 60)
        lines.append(f"TRANSITIVELY AFFECTED ({len(result.transitively_affected)})")
        lines.append("-" * 60)
        for pkg in result.transitively_affected:
            chain = result.impact_chains.get(pkg, [])
            chain_str = f"  (via {' -> '.join(chain)})" if chain else ""
            lines.append(f"  ~ {pkg}{chain_str}")
        lines.append("")

    if result.unaffected:
        lines.append("-" * 60)
        lines.append(f"UNAFFECTED ({len(result.unaffected)})")
        lines.append("-" * 60)
        for pkg in result.unaffected:
            lines.append(f"    {pkg}")
        lines.append("")

    if result.warnings:
        lines.append("-" * 60)
        lines.append("WARNINGS")
        lines.append("-" * 60)
        for w in result.warnings:
            lines.append(f"  ! {w}")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Detect which monorepo packages are affected by file changes.",
        epilog="Example: python impact_detector.py --ref origin/main --json",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to monorepo root (default: current directory)",
    )
    parser.add_argument(
        "--files",
        nargs="+",
        help="Explicit list of changed file paths (relative to monorepo root)",
    )
    parser.add_argument(
        "--ref",
        default=None,
        help="Git ref to diff against (e.g., origin/main, HEAD~3)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--affected-only",
        action="store_true",
        help="Only print names of affected packages (one per line)",
    )

    args = parser.parse_args()

    root = Path(args.path).resolve()
    if not root.is_dir():
        print(f"Error: {root} is not a valid directory", file=sys.stderr)
        sys.exit(1)

    # Determine changed files
    changed_files: List[str] = []
    if args.files:
        changed_files = args.files
    elif args.ref:
        changed_files = get_changed_files_from_git(str(root), args.ref)
        if not changed_files:
            print(f"No changed files found compared to {args.ref}", file=sys.stderr)
            sys.exit(0)
    else:
        # Read from stdin
        if not sys.stdin.isatty():
            changed_files = [line.strip() for line in sys.stdin if line.strip()]
        else:
            print("Error: Provide --files, --ref, or pipe file list via stdin", file=sys.stderr)
            parser.print_help(sys.stderr)
            sys.exit(1)

    result = detect_impact(str(root), changed_files)

    if args.json_output:
        print(json.dumps(asdict(result), indent=2))
    elif args.affected_only:
        for pkg in result.total_affected:
            print(pkg)
    else:
        print(format_human(result))


if __name__ == "__main__":
    main()
