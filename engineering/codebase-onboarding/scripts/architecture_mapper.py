#!/usr/bin/env python3
"""Analyze project structure and generate a high-level architecture map.

Scans directories, detects architectural patterns, maps dependencies,
identifies layers, and produces a structured architecture overview
with Mermaid diagram markup.
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

IGNORE_DIRS = {
    "node_modules", ".git", "__pycache__", ".next", "dist", "build",
    ".venv", "venv", "env", ".tox", ".mypy_cache", ".pytest_cache",
    "vendor", "target", "bin", "obj", ".idea", ".vscode", "coverage",
    ".nyc_output", ".cache", ".turbo", ".svelte-kit",
}

LAYER_PATTERNS = {
    "api": {"patterns": ["api", "routes", "endpoints", "controllers", "handlers", "views"],
            "label": "API Layer", "description": "HTTP handlers and route definitions"},
    "service": {"patterns": ["services", "service", "usecases", "use-cases", "interactors", "domain"],
                "label": "Service/Business Logic", "description": "Core business rules and orchestration"},
    "data": {"patterns": ["models", "entities", "schema", "db", "database", "repositories", "repo",
                          "dal", "prisma", "migrations", "drizzle"],
             "label": "Data Layer", "description": "Database models, schemas, and data access"},
    "ui": {"patterns": ["components", "pages", "views", "screens", "layouts", "templates", "ui"],
           "label": "UI Layer", "description": "User interface components and page layouts"},
    "config": {"patterns": ["config", "configuration", "settings", "constants"],
               "label": "Configuration", "description": "Application settings and constants"},
    "infrastructure": {"patterns": ["infra", "infrastructure", "deploy", "k8s", "terraform",
                                     "docker", "ci", "scripts"],
                        "label": "Infrastructure", "description": "Deployment, CI/CD, and infrastructure"},
    "shared": {"patterns": ["lib", "utils", "helpers", "common", "shared", "core", "pkg"],
               "label": "Shared/Utilities", "description": "Reusable utilities and shared code"},
    "tests": {"patterns": ["tests", "test", "__tests__", "spec", "specs", "e2e", "integration"],
              "label": "Tests", "description": "Test suites and test utilities"},
    "docs": {"patterns": ["docs", "documentation", "doc", "wiki"],
             "label": "Documentation", "description": "Project documentation and guides"},
    "assets": {"patterns": ["assets", "static", "public", "media", "images", "fonts", "styles"],
               "label": "Static Assets", "description": "Images, fonts, stylesheets, and static files"},
}

ARCHITECTURE_PATTERNS = {
    "monorepo": {
        "signals": ["packages", "apps", "libs", "modules"],
        "description": "Monorepo with multiple packages or applications",
    },
    "microservices": {
        "signals": ["services", "microservices"],
        "description": "Microservices architecture with independent services",
    },
    "mvc": {
        "signals": ["controllers", "models", "views"],
        "description": "Model-View-Controller pattern",
    },
    "layered": {
        "signals": ["api", "services", "repositories"],
        "description": "Layered architecture with clear separation of concerns",
    },
    "feature-based": {
        "signals": ["features", "modules"],
        "description": "Feature-based module organization",
    },
    "nextjs-app": {
        "signals": ["app"],
        "description": "Next.js App Router with file-based routing",
    },
}


def should_ignore(name):
    """Check if a directory name should be ignored."""
    return name in IGNORE_DIRS or name.startswith(".")


def scan_top_dirs(root):
    """Get top-level directories with metadata."""
    root_path = Path(root).resolve()
    dirs = []
    for item in sorted(root_path.iterdir()):
        if item.is_dir() and not should_ignore(item.name):
            file_count = 0
            extensions = defaultdict(int)
            for dirpath, dirnames, filenames in os.walk(item):
                dirnames[:] = [d for d in dirnames if not should_ignore(d)]
                for f in filenames:
                    ext = Path(f).suffix.lower()
                    if ext:
                        extensions[ext] += 1
                    file_count += 1
                if len(Path(dirpath).relative_to(item).parts) > 4:
                    dirnames.clear()
            top_ext = sorted(extensions.items(), key=lambda x: -x[1])[:5]
            dirs.append({
                "name": item.name,
                "file_count": file_count,
                "top_extensions": dict(top_ext),
                "subdirs": sorted([
                    d.name for d in item.iterdir()
                    if d.is_dir() and not should_ignore(d.name)
                ])[:10],
            })
    return dirs


def classify_layers(top_dirs):
    """Map top-level directories to architectural layers."""
    classified = {}
    unclassified = []
    for d in top_dirs:
        name_lower = d["name"].lower()
        matched = False
        for layer_id, layer_info in LAYER_PATTERNS.items():
            if name_lower in layer_info["patterns"]:
                classified[d["name"]] = {
                    "layer": layer_id,
                    "label": layer_info["label"],
                    "description": layer_info["description"],
                    "file_count": d["file_count"],
                }
                matched = True
                break
        if not matched:
            unclassified.append(d["name"])
    return classified, unclassified


def detect_architecture_pattern(top_dirs):
    """Detect the dominant architecture pattern."""
    dir_names = {d["name"].lower() for d in top_dirs}
    detected = []
    for pattern_id, pattern_info in ARCHITECTURE_PATTERNS.items():
        matches = [s for s in pattern_info["signals"] if s in dir_names]
        if matches:
            detected.append({
                "pattern": pattern_id,
                "description": pattern_info["description"],
                "signals": matches,
                "confidence": len(matches) / len(pattern_info["signals"]),
            })
    detected.sort(key=lambda x: -x["confidence"])
    return detected


def parse_dependencies(root):
    """Extract dependency names from common manifest files."""
    root_path = Path(root).resolve()
    deps = {"runtime": [], "dev": []}

    # package.json
    pkg_path = root_path / "package.json"
    if pkg_path.exists():
        try:
            data = json.loads(pkg_path.read_text(errors="ignore"))
            deps["runtime"].extend(sorted(data.get("dependencies", {}).keys()))
            deps["dev"].extend(sorted(data.get("devDependencies", {}).keys()))
        except (ValueError, OSError):
            pass

    # requirements.txt
    req_path = root_path / "requirements.txt"
    if req_path.exists():
        try:
            for line in req_path.read_text(errors="ignore").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and not line.startswith("-"):
                    pkg = re.split(r"[>=<!\[\];]", line)[0].strip()
                    if pkg:
                        deps["runtime"].append(pkg)
        except OSError:
            pass

    # go.mod
    gomod_path = root_path / "go.mod"
    if gomod_path.exists():
        try:
            in_require = False
            for line in gomod_path.read_text(errors="ignore").splitlines():
                line = line.strip()
                if line.startswith("require ("):
                    in_require = True
                    continue
                if in_require and line == ")":
                    in_require = False
                    continue
                if in_require and line:
                    parts = line.split()
                    if parts:
                        deps["runtime"].append(parts[0])
        except OSError:
            pass

    # Cargo.toml
    cargo_path = root_path / "Cargo.toml"
    if cargo_path.exists():
        try:
            in_deps = False
            for line in cargo_path.read_text(errors="ignore").splitlines():
                if re.match(r"\[dependencies\]", line):
                    in_deps = True
                    continue
                if re.match(r"\[dev-dependencies\]", line):
                    in_deps = True
                    continue
                if line.startswith("[") and in_deps:
                    in_deps = False
                    continue
                if in_deps:
                    match = re.match(r"^(\w[\w-]*)\s*=", line)
                    if match:
                        deps["runtime"].append(match.group(1))
        except OSError:
            pass

    return deps


def generate_mermaid_diagram(layers, pattern):
    """Generate a Mermaid diagram of the architecture."""
    lines = ["graph TD"]
    layer_order = ["ui", "api", "service", "data", "shared", "config", "infrastructure", "tests"]

    nodes = {}
    for dir_name, info in layers.items():
        layer = info["layer"]
        node_id = f"{layer}_{dir_name}".replace("-", "_")
        label = f"{dir_name}/ ({info['file_count']} files)"
        nodes[layer] = nodes.get(layer, [])
        nodes[layer].append((node_id, label))
        lines.append(f"    {node_id}[\"{label}\"]")

    # Add edges based on typical flow
    flow_edges = [
        ("ui", "api"), ("api", "service"), ("service", "data"),
        ("api", "shared"), ("service", "shared"),
    ]
    added_edges = set()
    for from_layer, to_layer in flow_edges:
        if from_layer in nodes and to_layer in nodes:
            f_id = nodes[from_layer][0][0]
            t_id = nodes[to_layer][0][0]
            edge_key = (f_id, t_id)
            if edge_key not in added_edges:
                lines.append(f"    {f_id} --> {t_id}")
                added_edges.add(edge_key)

    return "\n".join(lines)


def generate_report(root):
    """Generate the full architecture analysis report."""
    root_path = Path(root).resolve()
    top_dirs = scan_top_dirs(root)
    layers, unclassified = classify_layers(top_dirs)
    patterns = detect_architecture_pattern(top_dirs)
    deps = parse_dependencies(root)
    mermaid = generate_mermaid_diagram(layers, patterns[0] if patterns else None)

    # Count root-level files
    root_files = sorted([
        f.name for f in root_path.iterdir()
        if f.is_file() and not f.name.startswith(".")
    ])

    return {
        "project_name": root_path.name,
        "project_path": str(root_path),
        "architecture_patterns": patterns,
        "layers": layers,
        "unclassified_directories": unclassified,
        "directory_details": top_dirs,
        "dependencies": {
            "runtime_count": len(deps["runtime"]),
            "dev_count": len(deps["dev"]),
            "runtime": deps["runtime"][:30],
            "dev": deps["dev"][:20],
        },
        "root_files": root_files,
        "mermaid_diagram": mermaid,
    }


def format_human(report):
    """Format report as human-readable text."""
    lines = []
    lines.append(f"{'=' * 60}")
    lines.append(f"  ARCHITECTURE MAP: {report['project_name']}")
    lines.append(f"{'=' * 60}")
    lines.append(f"\nProject: {report['project_path']}")

    # Architecture patterns
    lines.append(f"\n--- Detected Architecture Patterns ---")
    if report["architecture_patterns"]:
        for p in report["architecture_patterns"]:
            conf = f"{p['confidence']:.0%}"
            lines.append(f"  {p['pattern'].upper()} ({conf} confidence)")
            lines.append(f"    {p['description']}")
            lines.append(f"    Signals: {', '.join(p['signals'])}")
    else:
        lines.append("  No standard architecture pattern detected.")

    # Layers
    lines.append(f"\n--- Architectural Layers ---")
    if report["layers"]:
        for dir_name, info in sorted(report["layers"].items(),
                                      key=lambda x: x[1]["layer"]):
            lines.append(f"  {dir_name}/")
            lines.append(f"    Layer: {info['label']}")
            lines.append(f"    Purpose: {info['description']}")
            lines.append(f"    Files: {info['file_count']}")
    else:
        lines.append("  No directories matched known layer patterns.")

    if report["unclassified_directories"]:
        lines.append(f"\n  Unclassified directories: {', '.join(report['unclassified_directories'])}")

    # Directory details
    lines.append(f"\n--- Directory Breakdown ---")
    for d in report["directory_details"]:
        lines.append(f"\n  {d['name']}/ ({d['file_count']} files)")
        if d["top_extensions"]:
            ext_str = ", ".join(f"{ext}({cnt})" for ext, cnt in d["top_extensions"].items())
            lines.append(f"    File types: {ext_str}")
        if d["subdirs"]:
            lines.append(f"    Subdirs: {', '.join(d['subdirs'])}")

    # Dependencies
    deps = report["dependencies"]
    lines.append(f"\n--- Dependencies ---")
    lines.append(f"  Runtime: {deps['runtime_count']}  |  Dev: {deps['dev_count']}")
    if deps["runtime"]:
        lines.append(f"\n  Key runtime dependencies:")
        for dep in deps["runtime"][:15]:
            lines.append(f"    - {dep}")
    if deps["dev"]:
        lines.append(f"\n  Key dev dependencies:")
        for dep in deps["dev"][:10]:
            lines.append(f"    - {dep}")

    # Root files
    if report["root_files"]:
        lines.append(f"\n--- Root-Level Files ---")
        for f in report["root_files"]:
            lines.append(f"  {f}")

    # Mermaid diagram
    lines.append(f"\n--- Mermaid Architecture Diagram ---")
    lines.append("  (Copy into a Mermaid-compatible renderer)\n")
    lines.append("```mermaid")
    lines.append(report["mermaid_diagram"])
    lines.append("```")

    lines.append(f"\n{'=' * 60}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze project structure and generate a high-level architecture map.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  %(prog)s /path/to/project\n"
            "  %(prog)s . --json\n"
            "  %(prog)s ~/my-app --json > architecture.json\n"
        ),
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Project directory to analyze (default: current directory)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as JSON instead of human-readable format",
    )
    args = parser.parse_args()

    target = Path(args.directory).resolve()
    if not target.is_dir():
        print(f"Error: '{args.directory}' is not a valid directory.", file=sys.stderr)
        sys.exit(1)

    report = generate_report(str(target))

    if args.json_output:
        print(json.dumps(report, indent=2))
    else:
        print(format_human(report))


if __name__ == "__main__":
    main()
