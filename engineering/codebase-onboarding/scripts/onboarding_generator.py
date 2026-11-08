#!/usr/bin/env python3
"""Scan a project directory and generate an onboarding guide.

Detects tech stack, key files, directory structure, entry points,
and produces a structured onboarding document for new developers.
"""

import argparse
import json
import re
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


SOURCE_EXTENSIONS = {".py": "Python", ".js": "JavaScript", ".ts": "TypeScript", ".tsx": "TypeScript",
                     ".go": "Go", ".rs": "Rust", ".java": "Java", ".rb": "Ruby", ".php": "PHP",
                     ".swift": "Swift", ".kt": "Kotlin", ".cs": "C#", ".c": "C", ".cpp": "C++", ".sh": "Shell"}


def detect_stack(root):
    """Identify tech stack from manifests; fall back to counting source files by extension."""
    root_path = Path(root).resolve()
    detected = []
    for indicator, stack in STACK_INDICATORS.items():
        if (root_path / indicator).exists():
            detected.append({"file": indicator, "stack": stack})
    if not detected:
        counts = {}
        for entry in scan_directory_tree(root_path, max_depth=4):
            lang = SOURCE_EXTENSIONS.get(Path(entry["path"]).suffix) if entry["type"] == "file" else None
            if lang:
                counts[lang] = counts.get(lang, 0) + 1
        for lang, n in sorted(counts.items(), key=lambda kv: -kv[1])[:3]:
            detected.append({"file": f"{n} source file(s), no manifest", "stack": lang})
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


def find_run_commands(root):
    """Commands the repo itself declares: package.json scripts, Makefile targets, .env keys."""
    root_path = Path(root).resolve()
    cmds, env_keys, readme_title, readme_summary = [], [], None, None
    try:
        scripts = json.loads((root_path / "package.json").read_text()).get("scripts", {})
        cmds += [f"npm run {name}  # {body}" for name, body in list(scripts.items())[:12]]
    except (OSError, ValueError, AttributeError):
        pass
    try:
        text = (root_path / "Makefile").read_text(errors="ignore")
        cmds += [f"make {t}" for t in re.findall(r"(?m)^([A-Za-z0-9_-]+):(?!=)", text)]
    except OSError:
        pass
    for name in (".env.example", ".env.sample"):
        try:
            env_keys = [l.split("=")[0].strip() for l in (root_path / name).read_text().splitlines()
                        if "=" in l and not l.lstrip().startswith("#")]
            break
        except OSError:
            continue
    for name in ("README.md", "README"):
        try:
            lines = (root_path / name).read_text().splitlines()
            readme_title = next((l.lstrip("# ").strip() for l in lines if l.startswith("#")), None)
            readme_summary = next((l.strip() for l in lines if l.strip() and not l.startswith(("#", "!", "[", "<"))), None)
            break
        except OSError:
            continue
    return {"commands": cmds[:20], "env_keys": env_keys[:30], "readme_title": readme_title,
            "readme_summary": readme_summary}


TODO = "> **TODO (owner):**"


def render_markdown(r):
    """Draft onboarding doc: sections filled from gathered facts, placeholders where facts end."""
    f = r["run_facts"]
    stack = ", ".join(sorted({i["stack"] for i in r["tech_stack"]})) or None
    out = [f"# Onboarding: {f['readme_title'] or r['project_name']}", ""]
    out += ["## What this is", f"From the README: {f['readme_summary']}" if f["readme_summary"] else "",
            f"{TODO} who uses it and what breaks for them if it is down.", ""]
    out += ["## Stack", f"- Languages/build: {stack}" if stack else f"{TODO} no manifest found; name the stack."]
    out += [f"- Tools: {', '.join(x['framework'] for x in r['frameworks'])}"] if r["frameworks"] else []
    st = r["source_code_stats"]
    out += [f"- Size: {st['source_files']} source files, {st['total_lines']} lines", ""]
    out += ["## Run it locally"]
    if f["commands"]:
        out += ["Commands declared in the repo (check which ones a newcomer needs, in order):", "```bash"]
        out += f["commands"] + ["```"]
    else:
        out += [f"{TODO} no package.json scripts or Makefile targets found; write the install, run and test commands."]
    if f["env_keys"]:
        out += ["", "Environment variables from the env template (say where each value comes from):"]
        out += [f"- `{k}`: {TODO.strip('> ')} source" for k in f["env_keys"]]
    out += ["", "## Where to start reading"]
    out += [f"- `{e}`: {TODO.strip('> ')} what starts here" for e in r["entry_points"][:8]] or \
           [f"{TODO} no standard entry point found; name the file where execution starts."]
    out += ["", "## Layout"]
    out += [f"- `{d}/`: {TODO.strip('> ')} purpose" for d in r["top_level_directories"][:15]]
    out += ["", "## Key files"] + [f"- `{k}`" for k in r["key_files"]] or []
    out += ["", "## Not derivable from the code", f"{TODO} deploy process, owners and on-call, "
            "where logs and dashboards live, known traps."]
    return "\n".join(out) + "\n"


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
        "run_facts": find_run_commands(root),
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
    lines.append("  Use --format markdown for a draft guide built from these facts.")
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
    parser.add_argument("--format", choices=["text", "json", "markdown"], default=None,
                        help="text (fact report), json, or markdown (draft onboarding guide with TODOs)")
    args = parser.parse_args()
    fmt = args.format or ("json" if args.json_output else "text")

    target = Path(args.directory).resolve()
    if not target.is_dir():
        print(f"Error: '{args.directory}' is not a valid directory.", file=sys.stderr)
        sys.exit(2)

    report = generate_report(str(target))

    if fmt == "json":
        print(json.dumps(report, indent=2))
    elif fmt == "markdown":
        print(render_markdown(report), end="")
    else:
        print(format_human(report))


if __name__ == "__main__":
    main()
