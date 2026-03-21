#!/usr/bin/env python3
"""Scan a project directory and generate an onboarding guide.

Detects tech stack, key files, directory structure, entry points,
and produces a structured onboarding document for new developers.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from collections import defaultdict

IGNORE_DIRS = {
    "node_modules", ".git", "__pycache__", ".next", "dist", "build",
    ".venv", "venv", "env", ".tox", ".mypy_cache", ".pytest_cache",
    ".eggs", "*.egg-info", "vendor", "target", "bin", "obj",
    ".idea", ".vscode", ".DS_Store", "coverage", ".nyc_output",
}

STACK_INDICATORS = {
    "package.json": "Node.js",
    "requirements.txt": "Python",
    "pyproject.toml": "Python",
    "setup.py": "Python",
    "Pipfile": "Python (Pipenv)",
    "go.mod": "Go",
    "Cargo.toml": "Rust",
    "pom.xml": "Java (Maven)",
    "build.gradle": "Java (Gradle)",
    "Gemfile": "Ruby",
    "composer.json": "PHP",
    "mix.exs": "Elixir",
    "Package.swift": "Swift",
    "CMakeLists.txt": "C/C++ (CMake)",
    "Makefile": "Make-based build",
}

FRAMEWORK_INDICATORS = {
    "next.config": "Next.js",
    "nuxt.config": "Nuxt.js",
    "angular.json": "Angular",
    "vue.config": "Vue.js",
    "svelte.config": "SvelteKit",
    "astro.config": "Astro",
    "vite.config": "Vite",
    "webpack.config": "Webpack",
    "tailwind.config": "Tailwind CSS",
    "tsconfig.json": "TypeScript",
    "docker-compose": "Docker Compose",
    "Dockerfile": "Docker",
    ".github/workflows": "GitHub Actions CI/CD",
    ".gitlab-ci.yml": "GitLab CI/CD",
    "Jenkinsfile": "Jenkins CI/CD",
    "terraform": "Terraform",
    "prisma/schema.prisma": "Prisma ORM",
    "drizzle.config": "Drizzle ORM",
    "alembic.ini": "Alembic (SQLAlchemy migrations)",
}

ENTRY_POINT_PATTERNS = [
    "main.py", "app.py", "manage.py", "wsgi.py", "asgi.py",
    "main.go", "main.rs", "Main.java",
    "index.ts", "index.js", "server.ts", "server.js",
    "app.ts", "app.js", "index.tsx", "index.jsx",
    "src/main.ts", "src/main.js", "src/index.ts", "src/index.js",
    "cmd/main.go",
]

KEY_FILE_NAMES = [
    "README.md", "README", "CONTRIBUTING.md", "CHANGELOG.md",
    "LICENSE", ".env.example", ".env.sample", "Makefile",
    "docker-compose.yml", "docker-compose.yaml",
    "Dockerfile", ".gitignore", ".editorconfig",
]


def should_ignore(path_part):
    """Check if a path component should be ignored."""
    return path_part in IGNORE_DIRS or path_part.startswith(".")


def scan_directory_tree(root, max_depth=3):
    """Walk the directory tree up to max_depth, skipping ignored dirs."""
    tree = []
    root_path = Path(root).resolve()
    for dirpath, dirnames, filenames in os.walk(root_path):
        rel = Path(dirpath).relative_to(root_path)
        depth = len(rel.parts)
        if depth > max_depth:
            dirnames.clear()
            continue
        dirnames[:] = sorted(d for d in dirnames if not should_ignore(d))
        for d in dirnames:
            tree.append({"type": "dir", "path": str(rel / d), "depth": depth + 1})
        for f in sorted(filenames):
            if not f.startswith(".") or f in KEY_FILE_NAMES or f.startswith(".env"):
                tree.append({"type": "file", "path": str(rel / f), "depth": depth + 1})
    return tree


def detect_stack(root):
    """Identify tech stack from manifest and config files."""
    root_path = Path(root).resolve()
    detected = []
    for indicator, stack in STACK_INDICATORS.items():
        if (root_path / indicator).exists():
            detected.append({"file": indicator, "stack": stack})
    return detected


def detect_frameworks(root):
    """Identify frameworks from config files."""
    root_path = Path(root).resolve()
    detected = []
    for pattern, framework in FRAMEWORK_INDICATORS.items():
        matches = list(root_path.glob(pattern + "*"))
        if matches or (root_path / pattern).exists():
            detected.append({"pattern": pattern, "framework": framework})
    return detected


def find_entry_points(root):
    """Locate likely entry point files."""
    root_path = Path(root).resolve()
    found = []
    for pattern in ENTRY_POINT_PATTERNS:
        target = root_path / pattern
        if target.exists():
            found.append(str(pattern))
        for match in root_path.glob(f"**/{pattern}"):
            rel = str(match.relative_to(root_path))
            if rel not in found and not any(should_ignore(p) for p in Path(rel).parts):
                found.append(rel)
    return list(dict.fromkeys(found))[:15]


def find_key_files(root):
    """Find important project files."""
    root_path = Path(root).resolve()
    found = []
    for name in KEY_FILE_NAMES:
        target = root_path / name
        if target.exists():
            found.append(name)
    return found


def count_file_types(root, max_depth=5):
    """Count files by extension."""
    root_path = Path(root).resolve()
    counts = defaultdict(int)
    for dirpath, dirnames, filenames in os.walk(root_path):
        rel = Path(dirpath).relative_to(root_path)
        if len(rel.parts) > max_depth:
            dirnames.clear()
            continue
        dirnames[:] = [d for d in dirnames if not should_ignore(d)]
        for f in filenames:
            ext = Path(f).suffix.lower()
            if ext:
                counts[ext] += 1
    return dict(sorted(counts.items(), key=lambda x: -x[1])[:20])


def count_source_lines(root, extensions=None):
    """Count total lines across source files."""
    if extensions is None:
        extensions = {".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs", ".java", ".rb", ".php"}
    root_path = Path(root).resolve()
    total = 0
    file_count = 0
    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames[:] = [d for d in dirnames if not should_ignore(d)]
        for f in filenames:
            if Path(f).suffix.lower() in extensions:
                try:
                    filepath = Path(dirpath) / f
                    total += sum(1 for _ in open(filepath, errors="ignore"))
                    file_count += 1
                except (OSError, PermissionError):
                    pass
    return {"total_lines": total, "source_files": file_count}


def generate_report(root):
    """Generate the full onboarding analysis report."""
    root_path = Path(root).resolve()
    project_name = root_path.name

    stack = detect_stack(root)
    frameworks = detect_frameworks(root)
    entry_points = find_entry_points(root)
    key_files = find_key_files(root)
    file_types = count_file_types(root)
    source_stats = count_source_lines(root)
    tree = scan_directory_tree(root, max_depth=2)

    top_dirs = [item["path"] for item in tree if item["type"] == "dir" and item["depth"] == 1]

    return {
        "project_name": project_name,
        "project_path": str(root_path),
        "tech_stack": stack,
        "frameworks": frameworks,
        "entry_points": entry_points,
        "key_files": key_files,
        "top_level_directories": top_dirs,
        "file_type_distribution": file_types,
        "source_code_stats": source_stats,
        "directory_tree_sample": tree[:60],
    }


def format_human(report):
    """Format report as human-readable text."""
    lines = []
    lines.append(f"{'=' * 60}")
    lines.append(f"  ONBOARDING GUIDE: {report['project_name']}")
    lines.append(f"{'=' * 60}")
    lines.append(f"\nProject Path: {report['project_path']}")

    lines.append(f"\n--- Tech Stack ---")
    if report["tech_stack"]:
        for item in report["tech_stack"]:
            lines.append(f"  [{item['file']}] -> {item['stack']}")
    else:
        lines.append("  No stack indicators detected.")

    lines.append(f"\n--- Frameworks & Tools ---")
    if report["frameworks"]:
        for item in report["frameworks"]:
            lines.append(f"  {item['framework']} (detected via {item['pattern']})")
    else:
        lines.append("  No framework configs detected.")

    lines.append(f"\n--- Entry Points ---")
    if report["entry_points"]:
        for ep in report["entry_points"]:
            lines.append(f"  -> {ep}")
    else:
        lines.append("  No standard entry points found.")

    lines.append(f"\n--- Key Project Files ---")
    for kf in report["key_files"]:
        lines.append(f"  * {kf}")

    lines.append(f"\n--- Top-Level Directories ---")
    for d in report["top_level_directories"]:
        lines.append(f"  {d}/")

    lines.append(f"\n--- File Type Distribution ---")
    for ext, count in report["file_type_distribution"].items():
        lines.append(f"  {ext:12s}  {count:5d} files")

    stats = report["source_code_stats"]
    lines.append(f"\n--- Source Code Stats ---")
    lines.append(f"  Source files: {stats['source_files']}")
    lines.append(f"  Total lines:  {stats['total_lines']}")

    lines.append(f"\n--- Directory Structure (depth 2) ---")
    for item in report["directory_tree_sample"]:
        indent = "  " * item["depth"]
        suffix = "/" if item["type"] == "dir" else ""
        name = Path(item["path"]).name
        lines.append(f"  {indent}{name}{suffix}")

    lines.append(f"\n{'=' * 60}")
    lines.append("  Next steps:")
    lines.append("  1. Read the key files listed above")
    lines.append("  2. Follow the setup guide (README or CONTRIBUTING)")
    lines.append("  3. Explore entry points to understand the main flow")
    lines.append("  4. Run the test suite to verify your local setup")
    lines.append(f"{'=' * 60}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Scan a project directory and generate an onboarding guide.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  %(prog)s /path/to/project\n"
            "  %(prog)s /path/to/project --json\n"
            "  %(prog)s . --json > onboarding.json\n"
        ),
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Project directory to scan (default: current directory)",
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
