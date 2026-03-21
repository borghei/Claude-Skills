#!/usr/bin/env python3
"""
Package Analyzer - Analyze monorepo package structure and dependencies.

Detects packages in a monorepo by scanning workspace configuration files
(pnpm-workspace.yaml, package.json workspaces, lerna.json), resolves
internal cross-package dependencies, identifies shared external dependencies,
and reports on package health metrics.

Author: Claude Skills Engineering Team
License: MIT
"""

import argparse
import glob
import json
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class Package:
    """Represents a monorepo package."""
    name: str
    path: str
    version: str
    private: bool
    internal_deps: List[str] = field(default_factory=list)
    external_deps: Dict[str, str] = field(default_factory=dict)
    dev_deps: Dict[str, str] = field(default_factory=dict)
    peer_deps: Dict[str, str] = field(default_factory=dict)
    scripts: List[str] = field(default_factory=list)
    has_tests: bool = False
    has_build: bool = False
    entry_point: Optional[str] = None


@dataclass
class AnalysisResult:
    """Full analysis result for the monorepo."""
    root_path: str
    workspace_tool: str
    total_packages: int
    packages: List[Dict[str, Any]]
    internal_dependency_count: int
    shared_external_deps: List[Dict[str, Any]]
    orphan_packages: List[str]
    leaf_packages: List[str]
    root_packages: List[str]
    warnings: List[str]


class PackageAnalyzer:
    """Analyzes monorepo package structure and dependencies."""

    def __init__(self, root_path: str):
        self.root_path = Path(root_path).resolve()
        self.packages: Dict[str, Package] = {}
        self.workspace_tool = "unknown"
        self.warnings: List[str] = []

    def analyze(self) -> AnalysisResult:
        """Run full analysis on the monorepo."""
        workspace_globs = self._detect_workspace_config()
        if not workspace_globs:
            self.warnings.append("No workspace configuration found. Scanning for package.json files.")
            workspace_globs = ["packages/*", "apps/*", "libs/*", "modules/*"]

        self._discover_packages(workspace_globs)
        self._resolve_internal_deps()
        self._detect_package_features()

        shared_deps = self._find_shared_external_deps()
        orphans = self._find_orphan_packages()
        leaves = self._find_leaf_packages()
        roots = self._find_root_packages()

        return AnalysisResult(
            root_path=str(self.root_path),
            workspace_tool=self.workspace_tool,
            total_packages=len(self.packages),
            packages=[asdict(p) for p in self.packages.values()],
            internal_dependency_count=sum(len(p.internal_deps) for p in self.packages.values()),
            shared_external_deps=shared_deps,
            orphan_packages=orphans,
            leaf_packages=leaves,
            root_packages=roots,
            warnings=self.warnings,
        )

    def _detect_workspace_config(self) -> List[str]:
        """Detect workspace configuration and return package globs."""
        # Try pnpm-workspace.yaml
        pnpm_ws = self.root_path / "pnpm-workspace.yaml"
        if pnpm_ws.exists():
            self.workspace_tool = "pnpm"
            return self._parse_pnpm_workspace(pnpm_ws)

        # Try root package.json workspaces field
        root_pkg = self.root_path / "package.json"
        if root_pkg.exists():
            try:
                with open(root_pkg, "r") as f:
                    data = json.load(f)
                workspaces = data.get("workspaces", None)
                if isinstance(workspaces, list):
                    self.workspace_tool = "npm/yarn"
                    return workspaces
                if isinstance(workspaces, dict) and "packages" in workspaces:
                    self.workspace_tool = "yarn"
                    return workspaces["packages"]
            except (json.JSONDecodeError, OSError):
                pass

        # Try lerna.json
        lerna_cfg = self.root_path / "lerna.json"
        if lerna_cfg.exists():
            self.workspace_tool = "lerna"
            try:
                with open(lerna_cfg, "r") as f:
                    data = json.load(f)
                return data.get("packages", ["packages/*"])
            except (json.JSONDecodeError, OSError):
                return ["packages/*"]

        return []

    def _parse_pnpm_workspace(self, filepath: Path) -> List[str]:
        """Parse pnpm-workspace.yaml without PyYAML (stdlib only)."""
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
                            val = stripped[2:].strip().strip("'\"")
                            globs.append(val)
                        elif stripped and not stripped.startswith("#"):
                            break
        except OSError:
            self.warnings.append(f"Could not read {filepath}")
        return globs

    def _discover_packages(self, workspace_globs: List[str]) -> None:
        """Find all packages matching workspace globs."""
        for ws_glob in workspace_globs:
            # Skip negation patterns
            if ws_glob.startswith("!"):
                continue
            pattern = str(self.root_path / ws_glob / "package.json")
            for pkg_path in sorted(glob.glob(pattern)):
                self._load_package(Path(pkg_path))

    def _load_package(self, pkg_json_path: Path) -> None:
        """Load a single package from its package.json."""
        try:
            with open(pkg_json_path, "r") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            self.warnings.append(f"Could not parse {pkg_json_path}: {e}")
            return

        name = data.get("name")
        if not name:
            self.warnings.append(f"Package at {pkg_json_path.parent} has no name field")
            return

        pkg = Package(
            name=name,
            path=str(pkg_json_path.parent.relative_to(self.root_path)),
            version=data.get("version", "0.0.0"),
            private=data.get("private", False),
            external_deps=dict(data.get("dependencies", {})),
            dev_deps=dict(data.get("devDependencies", {})),
            peer_deps=dict(data.get("peerDependencies", {})),
            scripts=list(data.get("scripts", {}).keys()),
            entry_point=data.get("main") or data.get("module") or data.get("exports"),
        )
        self.packages[name] = pkg

    def _resolve_internal_deps(self) -> None:
        """Separate internal workspace deps from external deps."""
        internal_names = set(self.packages.keys())
        for pkg in self.packages.values():
            internal = []
            external_only = {}
            for dep_name, dep_version in pkg.external_deps.items():
                if dep_name in internal_names:
                    internal.append(dep_name)
                else:
                    external_only[dep_name] = dep_version
            pkg.internal_deps = sorted(internal)
            pkg.external_deps = external_only

            # Also check devDependencies for internal refs
            dev_external = {}
            for dep_name, dep_version in pkg.dev_deps.items():
                if dep_name in internal_names and dep_name not in pkg.internal_deps:
                    pkg.internal_deps.append(dep_name)
                else:
                    dev_external[dep_name] = dep_version
            pkg.dev_deps = dev_external
            pkg.internal_deps = sorted(set(pkg.internal_deps))

    def _detect_package_features(self) -> None:
        """Detect if packages have tests, build scripts, etc."""
        for pkg in self.packages.values():
            pkg.has_tests = any(s in pkg.scripts for s in ("test", "test:unit", "test:e2e", "vitest"))
            pkg.has_build = any(s in pkg.scripts for s in ("build", "compile", "bundle"))

    def _find_shared_external_deps(self) -> List[Dict[str, Any]]:
        """Find external dependencies shared across multiple packages."""
        dep_usage: Dict[str, List[Tuple[str, str]]] = {}
        for pkg in self.packages.values():
            for dep_name, dep_version in pkg.external_deps.items():
                dep_usage.setdefault(dep_name, []).append((pkg.name, dep_version))

        shared = []
        for dep_name, users in sorted(dep_usage.items()):
            if len(users) < 2:
                continue
            versions = list(set(v for _, v in users))
            entry = {
                "name": dep_name,
                "used_by_count": len(users),
                "packages": [u[0] for u in users],
                "versions": versions,
                "version_mismatch": len(versions) > 1,
            }
            shared.append(entry)

        shared.sort(key=lambda x: x["used_by_count"], reverse=True)
        return shared

    def _find_orphan_packages(self) -> List[str]:
        """Find packages that nobody depends on and that depend on nothing internal."""
        all_depended_on: Set[str] = set()
        for pkg in self.packages.values():
            all_depended_on.update(pkg.internal_deps)

        orphans = []
        for name, pkg in self.packages.items():
            if name not in all_depended_on and not pkg.internal_deps:
                orphans.append(name)
        return sorted(orphans)

    def _find_leaf_packages(self) -> List[str]:
        """Find packages with no internal dependencies (leaves of the dep tree)."""
        return sorted(name for name, pkg in self.packages.items() if not pkg.internal_deps)

    def _find_root_packages(self) -> List[str]:
        """Find packages that nothing else depends on (roots/apps)."""
        all_depended_on: Set[str] = set()
        for pkg in self.packages.values():
            all_depended_on.update(pkg.internal_deps)
        return sorted(name for name in self.packages if name not in all_depended_on)


def format_human(result: AnalysisResult) -> str:
    """Format analysis result for human-readable output."""
    lines = []
    lines.append("=" * 60)
    lines.append("MONOREPO PACKAGE ANALYSIS")
    lines.append("=" * 60)
    lines.append(f"Root:            {result.root_path}")
    lines.append(f"Workspace Tool:  {result.workspace_tool}")
    lines.append(f"Total Packages:  {result.total_packages}")
    lines.append(f"Internal Deps:   {result.internal_dependency_count}")
    lines.append("")

    # Package summary table
    lines.append("-" * 60)
    lines.append("PACKAGES")
    lines.append("-" * 60)
    for pkg in result.packages:
        private_tag = " [private]" if pkg["private"] else ""
        lines.append(f"  {pkg['name']}@{pkg['version']}{private_tag}")
        lines.append(f"    Path: {pkg['path']}")
        if pkg["internal_deps"]:
            lines.append(f"    Internal deps: {', '.join(pkg['internal_deps'])}")
        ext_count = len(pkg["external_deps"])
        dev_count = len(pkg["dev_deps"])
        lines.append(f"    External deps: {ext_count}  Dev deps: {dev_count}")
        features = []
        if pkg["has_build"]:
            features.append("build")
        if pkg["has_tests"]:
            features.append("tests")
        if features:
            lines.append(f"    Features: {', '.join(features)}")
        lines.append("")

    # Leaf packages
    if result.leaf_packages:
        lines.append("-" * 60)
        lines.append("LEAF PACKAGES (no internal deps)")
        lines.append("-" * 60)
        for name in result.leaf_packages:
            lines.append(f"  - {name}")
        lines.append("")

    # Root packages
    if result.root_packages:
        lines.append("-" * 60)
        lines.append("ROOT PACKAGES (nothing depends on them)")
        lines.append("-" * 60)
        for name in result.root_packages:
            lines.append(f"  - {name}")
        lines.append("")

    # Orphan packages
    if result.orphan_packages:
        lines.append("-" * 60)
        lines.append("ORPHAN PACKAGES (isolated - no internal connections)")
        lines.append("-" * 60)
        for name in result.orphan_packages:
            lines.append(f"  - {name}")
        lines.append("")

    # Shared deps
    if result.shared_external_deps:
        lines.append("-" * 60)
        lines.append("SHARED EXTERNAL DEPENDENCIES")
        lines.append("-" * 60)
        for dep in result.shared_external_deps[:15]:
            mismatch = " [VERSION MISMATCH]" if dep["version_mismatch"] else ""
            lines.append(f"  {dep['name']} (used by {dep['used_by_count']} packages){mismatch}")
            if dep["version_mismatch"]:
                lines.append(f"    Versions: {', '.join(dep['versions'])}")
        lines.append("")

    # Warnings
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
        description="Analyze monorepo package structure, dependencies, and health.",
        epilog="Example: python package_analyzer.py /path/to/monorepo --json",
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
        "--only-shared",
        action="store_true",
        help="Only show shared external dependencies",
    )
    parser.add_argument(
        "--only-orphans",
        action="store_true",
        help="Only show orphan packages",
    )

    args = parser.parse_args()

    root = Path(args.path).resolve()
    if not root.is_dir():
        print(f"Error: {root} is not a valid directory", file=sys.stderr)
        sys.exit(1)

    analyzer = PackageAnalyzer(str(root))
    result = analyzer.analyze()

    if result.total_packages == 0:
        print("No packages found. Is this a monorepo with workspace configuration?", file=sys.stderr)
        sys.exit(1)

    if args.json_output:
        print(json.dumps(asdict(result), indent=2))
    elif args.only_shared:
        if not result.shared_external_deps:
            print("No shared external dependencies found.")
        else:
            for dep in result.shared_external_deps:
                mismatch = " [MISMATCH]" if dep["version_mismatch"] else ""
                print(f"{dep['name']} ({dep['used_by_count']} packages){mismatch}")
    elif args.only_orphans:
        if not result.orphan_packages:
            print("No orphan packages found.")
        else:
            for name in result.orphan_packages:
                print(name)
    else:
        print(format_human(result))


if __name__ == "__main__":
    main()
