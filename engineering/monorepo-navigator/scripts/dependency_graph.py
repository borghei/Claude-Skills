#!/usr/bin/env python3
"""
Dependency Graph Generator - Generate Mermaid diagrams of monorepo package dependencies.

Scans a monorepo for internal cross-package dependencies and outputs a Mermaid
flowchart showing the dependency structure. Supports filtering by package,
direction control, depth limits, and multiple layout orientations.

Author: Claude Skills Engineering Team
License: MIT
"""

import argparse
import glob
import json
import os
import sys
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class PackageNode:
    """Represents a package in the dependency graph."""
    name: str
    path: str
    category: str  # apps, packages, libs, etc.
    internal_deps: List[str] = field(default_factory=list)
    dep_count: int = 0
    dependent_count: int = 0


@dataclass
class GraphResult:
    """Result containing the generated graph data."""
    mermaid: str
    node_count: int
    edge_count: int
    packages: List[Dict[str, Any]]
    categories: Dict[str, int]
    circular_deps: List[List[str]]
    warnings: List[str]


class DependencyGraphBuilder:
    """Builds a dependency graph from monorepo package structure."""

    def __init__(self, root_path: str):
        self.root_path = Path(root_path).resolve()
        self.nodes: Dict[str, PackageNode] = {}
        self.edges: List[Tuple[str, str]] = []
        self.reverse_deps: Dict[str, Set[str]] = {}
        self.warnings: List[str] = []

    def build(self) -> None:
        """Discover packages and build the graph."""
        workspace_globs = self._detect_workspaces()
        if not workspace_globs:
            workspace_globs = ["packages/*", "apps/*", "libs/*", "modules/*"]
            self.warnings.append("No workspace config found; using default patterns.")

        self._discover_packages(workspace_globs)
        self._resolve_edges()

    def _detect_workspaces(self) -> List[str]:
        """Detect workspace globs from config files."""
        pnpm_ws = self.root_path / "pnpm-workspace.yaml"
        if pnpm_ws.exists():
            return self._parse_pnpm_workspace(pnpm_ws)

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

        lerna_cfg = self.root_path / "lerna.json"
        if lerna_cfg.exists():
            try:
                with open(lerna_cfg, "r") as f:
                    return json.load(f).get("packages", ["packages/*"])
            except (json.JSONDecodeError, OSError):
                pass

        return []

    def _parse_pnpm_workspace(self, filepath: Path) -> List[str]:
        """Parse pnpm-workspace.yaml without PyYAML."""
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
                category = rel_path.split("/")[0] if "/" in rel_path else "root"
                self.nodes[name] = PackageNode(
                    name=name,
                    path=rel_path,
                    category=category,
                )

    def _resolve_edges(self) -> None:
        """Resolve internal dependency edges."""
        internal_names = set(self.nodes.keys())
        for name, node in self.nodes.items():
            pkg_json = self.root_path / node.path / "package.json"
            try:
                with open(pkg_json, "r") as f:
                    data = json.load(f)
            except (json.JSONDecodeError, OSError):
                continue

            dep_sections = [
                data.get("dependencies", {}),
                data.get("devDependencies", {}),
                data.get("peerDependencies", {}),
            ]
            deps = set()
            for section in dep_sections:
                for dep_name in section:
                    if dep_name in internal_names and dep_name != name:
                        deps.add(dep_name)

            node.internal_deps = sorted(deps)
            node.dep_count = len(deps)
            for dep in deps:
                self.edges.append((name, dep))
                self.reverse_deps.setdefault(dep, set()).add(name)

        # Count dependents
        for name in self.nodes:
            self.nodes[name].dependent_count = len(self.reverse_deps.get(name, set()))

    def detect_circular_deps(self) -> List[List[str]]:
        """Detect circular dependencies using DFS."""
        cycles: List[List[str]] = []
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        path: List[str] = []

        def dfs(node: str) -> None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for dep in self.nodes.get(node, PackageNode("", "", "")).internal_deps:
                if dep not in visited:
                    dfs(dep)
                elif dep in rec_stack:
                    cycle_start = path.index(dep)
                    cycle = path[cycle_start:] + [dep]
                    normalized = self._normalize_cycle(cycle)
                    if normalized not in [self._normalize_cycle(c) for c in cycles]:
                        cycles.append(cycle)

            path.pop()
            rec_stack.discard(node)

        for name in sorted(self.nodes.keys()):
            if name not in visited:
                dfs(name)

        return cycles

    @staticmethod
    def _normalize_cycle(cycle: List[str]) -> Tuple[str, ...]:
        """Normalize a cycle for deduplication."""
        if len(cycle) <= 1:
            return tuple(cycle)
        min_idx = cycle.index(min(cycle[:-1]))
        normalized = cycle[min_idx:-1] + cycle[:min_idx]
        return tuple(normalized)

    def filter_by_package(
        self, focus: str, depth: int = -1, direction: str = "both"
    ) -> "DependencyGraphBuilder":
        """Create a filtered graph centered on a specific package."""
        if focus not in self.nodes:
            self.warnings.append(f"Package '{focus}' not found in graph.")
            return self

        relevant: Set[str] = {focus}

        if direction in ("deps", "both"):
            self._collect_deps(focus, relevant, depth)
        if direction in ("dependents", "both"):
            self._collect_dependents(focus, relevant, depth)

        # Filter nodes and edges
        filtered = DependencyGraphBuilder(str(self.root_path))
        filtered.nodes = {k: v for k, v in self.nodes.items() if k in relevant}
        filtered.edges = [(a, b) for a, b in self.edges if a in relevant and b in relevant]
        filtered.reverse_deps = {
            k: v & relevant for k, v in self.reverse_deps.items() if k in relevant
        }
        filtered.warnings = self.warnings
        return filtered

    def _collect_deps(self, start: str, result: Set[str], max_depth: int) -> None:
        """BFS to collect dependencies down to max_depth."""
        queue: deque = deque([(start, 0)])
        while queue:
            current, depth = queue.popleft()
            if max_depth >= 0 and depth >= max_depth:
                continue
            for dep in self.nodes.get(current, PackageNode("", "", "")).internal_deps:
                if dep not in result:
                    result.add(dep)
                    queue.append((dep, depth + 1))

    def _collect_dependents(self, start: str, result: Set[str], max_depth: int) -> None:
        """BFS to collect dependents up to max_depth."""
        queue: deque = deque([(start, 0)])
        while queue:
            current, depth = queue.popleft()
            if max_depth >= 0 and depth >= max_depth:
                continue
            for dep in self.reverse_deps.get(current, set()):
                if dep not in result:
                    result.add(dep)
                    queue.append((dep, depth + 1))

    def generate_mermaid(self, orientation: str = "TD", show_categories: bool = True) -> str:
        """Generate Mermaid flowchart syntax."""
        lines = [f"graph {orientation}"]

        # Sanitize node names for Mermaid (replace special chars)
        def node_id(name: str) -> str:
            return name.replace("@", "").replace("/", "_").replace("-", "_")

        def node_label(name: str) -> str:
            return name

        # Group by category with subgraphs
        if show_categories and len(set(n.category for n in self.nodes.values())) > 1:
            categories: Dict[str, List[PackageNode]] = {}
            for node in self.nodes.values():
                categories.setdefault(node.category, []).append(node)

            for category, nodes in sorted(categories.items()):
                lines.append(f"    subgraph {category}")
                for node in sorted(nodes, key=lambda n: n.name):
                    nid = node_id(node.name)
                    label = node_label(node.name)
                    if node.dependent_count == 0:
                        lines.append(f"        {nid}[{label}]")
                    elif node.dep_count == 0:
                        lines.append(f"        {nid}({label})")
                    else:
                        lines.append(f"        {nid}[{label}]")
                lines.append("    end")
        else:
            for node in sorted(self.nodes.values(), key=lambda n: n.name):
                nid = node_id(node.name)
                label = node_label(node.name)
                if node.dependent_count == 0:
                    lines.append(f"    {nid}[{label}]")
                elif node.dep_count == 0:
                    lines.append(f"    {nid}({label})")
                else:
                    lines.append(f"    {nid}[{label}]")

        # Add edges
        lines.append("")
        for source, target in sorted(self.edges):
            lines.append(f"    {node_id(source)} --> {node_id(target)}")

        return "\n".join(lines)


def build_graph_result(builder: DependencyGraphBuilder, orientation: str, show_categories: bool) -> GraphResult:
    """Build the complete graph result."""
    circular = builder.detect_circular_deps()
    mermaid = builder.generate_mermaid(orientation, show_categories)

    categories: Dict[str, int] = {}
    for node in builder.nodes.values():
        categories[node.category] = categories.get(node.category, 0) + 1

    packages_info = []
    for node in sorted(builder.nodes.values(), key=lambda n: n.name):
        packages_info.append({
            "name": node.name,
            "path": node.path,
            "category": node.category,
            "internal_deps": node.internal_deps,
            "dep_count": node.dep_count,
            "dependent_count": node.dependent_count,
        })

    return GraphResult(
        mermaid=mermaid,
        node_count=len(builder.nodes),
        edge_count=len(builder.edges),
        packages=packages_info,
        categories=categories,
        circular_deps=[cycle for cycle in circular],
        warnings=builder.warnings,
    )


def format_human(result: GraphResult) -> str:
    """Format graph result for human-readable output."""
    lines = []
    lines.append("=" * 60)
    lines.append("DEPENDENCY GRAPH")
    lines.append("=" * 60)
    lines.append(f"Packages: {result.node_count}  Edges: {result.edge_count}")
    lines.append(f"Categories: {', '.join(f'{k}({v})' for k, v in sorted(result.categories.items()))}")
    lines.append("")

    if result.circular_deps:
        lines.append("-" * 60)
        lines.append("CIRCULAR DEPENDENCIES DETECTED")
        lines.append("-" * 60)
        for cycle in result.circular_deps:
            lines.append(f"  ! {' -> '.join(cycle)}")
        lines.append("")

    # Package connectivity summary
    lines.append("-" * 60)
    lines.append("PACKAGE CONNECTIVITY")
    lines.append("-" * 60)
    for pkg in result.packages:
        deps_str = f"deps={pkg['dep_count']}"
        dependents_str = f"dependents={pkg['dependent_count']}"
        lines.append(f"  {pkg['name']:40s} {deps_str:10s} {dependents_str}")
    lines.append("")

    # Mermaid diagram
    lines.append("-" * 60)
    lines.append("MERMAID DIAGRAM")
    lines.append("-" * 60)
    lines.append("")
    lines.append("```mermaid")
    lines.append(result.mermaid)
    lines.append("```")
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
        description="Generate a Mermaid dependency graph of monorepo internal packages.",
        epilog="Example: python dependency_graph.py /path/to/monorepo --focus @repo/ui --depth 2",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to monorepo root (default: current directory)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--mermaid-only",
        action="store_true",
        help="Output only the raw Mermaid diagram (no wrapper)",
    )
    parser.add_argument(
        "--orientation",
        choices=["TD", "LR", "BT", "RL"],
        default="TD",
        help="Graph orientation: TD (top-down), LR (left-right), BT, RL (default: TD)",
    )
    parser.add_argument(
        "--focus",
        default=None,
        help="Focus on a specific package and its connections",
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=-1,
        help="Max depth from focus package (-1 for unlimited, default: -1)",
    )
    parser.add_argument(
        "--direction",
        choices=["deps", "dependents", "both"],
        default="both",
        help="Direction from focus: deps, dependents, or both (default: both)",
    )
    parser.add_argument(
        "--no-categories",
        action="store_true",
        help="Do not group packages into category subgraphs",
    )

    args = parser.parse_args()

    root = Path(args.path).resolve()
    if not root.is_dir():
        print(f"Error: {root} is not a valid directory", file=sys.stderr)
        sys.exit(1)

    builder = DependencyGraphBuilder(str(root))
    builder.build()

    if not builder.nodes:
        print("No packages found. Is this a monorepo with workspace configuration?", file=sys.stderr)
        sys.exit(1)

    if args.focus:
        builder = builder.filter_by_package(args.focus, args.depth, args.direction)

    result = build_graph_result(builder, args.orientation, not args.no_categories)

    if args.json_output:
        output = {
            "mermaid": result.mermaid,
            "node_count": result.node_count,
            "edge_count": result.edge_count,
            "packages": result.packages,
            "categories": result.categories,
            "circular_deps": result.circular_deps,
            "warnings": result.warnings,
        }
        print(json.dumps(output, indent=2))
    elif args.mermaid_only:
        print(result.mermaid)
    else:
        print(format_human(result))


if __name__ == "__main__":
    main()
