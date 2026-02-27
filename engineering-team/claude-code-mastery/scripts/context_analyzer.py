#!/usr/bin/env python3
"""
Context Analyzer - Estimate context window usage across a project

Scans a project directory to estimate how much of Claude Code's context window
is consumed by CLAUDE.md files, skill definitions, source code, and configuration.
Helps users understand and manage their token budget.

Usage:
    python context_analyzer.py /path/to/project
    python context_analyzer.py . --max-depth 3
    python context_analyzer.py /project --context-window 200000 --json
"""

import argparse
import json
import os
import sys
import textwrap
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# Approximate characters per token for Claude models
CHARS_PER_TOKEN = 4

# File categories for analysis
FILE_CATEGORIES = {
    "claude_config": {
        "label": "Claude Configuration",
        "patterns": ["CLAUDE.md", "claude.md", ".claude/settings.json", ".claude/agents/*.yaml", ".claude/agents/*.yml"],
        "description": "CLAUDE.md files and .claude/ configuration (loaded automatically)",
    },
    "skill_files": {
        "label": "Skill Definitions",
        "patterns": ["SKILL.md", "skill.md"],
        "description": "Skill master documents (loaded when skills are triggered)",
    },
    "reference_docs": {
        "label": "Reference Documents",
        "patterns": ["references/*.md", "references/**/*.md"],
        "description": "Deep-dive reference guides (loaded on demand)",
    },
    "source_code": {
        "label": "Source Code",
        "extensions": [".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java", ".rb", ".php", ".c", ".cpp", ".h", ".cs", ".swift", ".kt"],
        "description": "Source files Claude reads during work",
    },
    "config_files": {
        "label": "Config & Build",
        "extensions": [".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".env.example", ".gitignore"],
        "names": ["Makefile", "Dockerfile", "docker-compose.yml", "package.json", "tsconfig.json", "pyproject.toml", "Cargo.toml", "go.mod"],
        "description": "Configuration and build files",
    },
    "documentation": {
        "label": "Documentation",
        "extensions": [".md", ".rst", ".txt"],
        "description": "Markdown and text documentation",
    },
}

# Directories to always skip
SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "env",
    ".tox", ".mypy_cache", ".pytest_cache", "dist", "build",
    ".next", ".nuxt", "coverage", ".coverage", "target",
    ".terraform", ".serverless", "vendor",
}

# Files to always skip
SKIP_FILES = {
    ".DS_Store", "Thumbs.db", "package-lock.json", "yarn.lock",
    "pnpm-lock.yaml", "poetry.lock", "Gemfile.lock", "Cargo.lock",
    "composer.lock",
}

# Max file size to analyze (skip very large files)
MAX_FILE_SIZE = 1_000_000  # 1 MB


def estimate_tokens(text: str) -> int:
    """Estimate token count from text."""
    return int(len(text) / CHARS_PER_TOKEN)


def estimate_tokens_from_size(byte_size: int) -> int:
    """Estimate tokens from file size in bytes (assumes UTF-8)."""
    return int(byte_size / CHARS_PER_TOKEN)


def categorize_file(filepath: Path, project_root: Path) -> str:
    """Categorize a file into one of the analysis categories."""
    name = filepath.name
    relative = filepath.relative_to(project_root)
    relative_str = str(relative)

    # Claude configuration files
    if name.upper() == "CLAUDE.MD":
        return "claude_config"
    if ".claude/" in relative_str or ".claude\\" in relative_str:
        return "claude_config"

    # Skill files
    if name.upper() == "SKILL.MD":
        return "skill_files"

    # Reference documents
    parts = relative.parts
    if "references" in parts:
        return "reference_docs"

    # Source code
    suffix = filepath.suffix.lower()
    source_extensions = FILE_CATEGORIES["source_code"]["extensions"]
    if suffix in source_extensions:
        return "source_code"

    # Config files
    config_extensions = FILE_CATEGORIES["config_files"]["extensions"]
    config_names = FILE_CATEGORIES["config_files"].get("names", [])
    if suffix in config_extensions or name in config_names:
        return "config_files"

    # Documentation
    doc_extensions = FILE_CATEGORIES["documentation"]["extensions"]
    if suffix in doc_extensions:
        return "documentation"

    return "other"


def scan_project(
    project_path: str,
    max_depth: int = 5,
    context_window: int = 200_000,
) -> Dict:
    """Scan a project directory and analyze context window usage."""
    root = Path(project_path).resolve()

    if not root.exists():
        return {"success": False, "error": f"Path does not exist: {project_path}"}
    if not root.is_dir():
        return {"success": False, "error": f"Not a directory: {project_path}"}

    # Collect files by category
    category_files: Dict[str, List[Dict]] = {
        "claude_config": [],
        "skill_files": [],
        "reference_docs": [],
        "source_code": [],
        "config_files": [],
        "documentation": [],
        "other": [],
    }

    total_files = 0
    skipped_files = 0

    for dirpath, dirnames, filenames in os.walk(root):
        # Compute current depth
        rel_dir = Path(dirpath).relative_to(root)
        depth = len(rel_dir.parts)
        if depth > max_depth:
            dirnames.clear()
            continue

        # Skip ignored directories
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]

        for filename in filenames:
            if filename in SKIP_FILES:
                skipped_files += 1
                continue

            filepath = Path(dirpath) / filename

            # Skip very large files
            try:
                file_size = filepath.stat().st_size
            except OSError:
                skipped_files += 1
                continue

            if file_size > MAX_FILE_SIZE:
                skipped_files += 1
                continue

            if file_size == 0:
                continue

            total_files += 1
            category = categorize_file(filepath, root)
            token_estimate = estimate_tokens_from_size(file_size)

            category_files[category].append({
                "path": str(filepath.relative_to(root)),
                "size_bytes": file_size,
                "token_estimate": token_estimate,
            })

    # Compute category totals
    category_summaries = {}
    total_tokens = 0

    for cat_key, files in category_files.items():
        cat_tokens = sum(f["token_estimate"] for f in files)
        total_tokens += cat_tokens
        label = FILE_CATEGORIES.get(cat_key, {}).get("label", cat_key.replace("_", " ").title())
        description = FILE_CATEGORIES.get(cat_key, {}).get("description", "")

        # Sort files by token count descending
        sorted_files = sorted(files, key=lambda f: f["token_estimate"], reverse=True)

        category_summaries[cat_key] = {
            "label": label,
            "description": description,
            "file_count": len(files),
            "total_tokens": cat_tokens,
            "percentage_of_window": round(cat_tokens / context_window * 100, 1) if context_window > 0 else 0,
            "largest_files": sorted_files[:10],
        }

    # Compute auto-loaded tokens (CLAUDE.md files load automatically)
    auto_loaded_tokens = category_summaries.get("claude_config", {}).get("total_tokens", 0)

    # Compute the recommended budget breakdown
    budget = {
        "system_prompt": {"tokens": 3000, "label": "System Prompt (fixed)"},
        "claude_config": {"tokens": auto_loaded_tokens, "label": "CLAUDE.md Configuration (auto-loaded)"},
        "active_skills": {"tokens": category_summaries.get("skill_files", {}).get("total_tokens", 0), "label": "Skill Definitions (on trigger)"},
        "available_for_work": {
            "tokens": context_window - 3000 - auto_loaded_tokens,
            "label": "Available for Source Code + Conversation + Reasoning",
        },
    }

    # Find top 20 largest files across all categories
    all_files = []
    for files in category_files.values():
        all_files.extend(files)
    largest_files = sorted(all_files, key=lambda f: f["token_estimate"], reverse=True)[:20]

    # Generate recommendations
    recommendations = []

    if auto_loaded_tokens > context_window * 0.1:
        recommendations.append({
            "priority": "high",
            "message": f"CLAUDE.md configuration uses {auto_loaded_tokens} tokens "
                       f"({round(auto_loaded_tokens / context_window * 100, 1)}% of context window). "
                       f"Target under 10%. Use hierarchical loading.",
        })

    if auto_loaded_tokens > 8000:
        recommendations.append({
            "priority": "high",
            "message": "Root CLAUDE.md files exceed 8K tokens total. "
                       "Move domain-specific instructions to subdirectory CLAUDE.md files.",
        })

    skill_tokens = category_summaries.get("skill_files", {}).get("total_tokens", 0)
    if skill_tokens > context_window * 0.15:
        recommendations.append({
            "priority": "medium",
            "message": f"Skill definitions total {skill_tokens} tokens. "
                       f"Consider splitting large skills or using progressive disclosure.",
        })

    large_source_files = [
        f for f in category_files.get("source_code", [])
        if f["token_estimate"] > 5000
    ]
    if large_source_files:
        recommendations.append({
            "priority": "medium",
            "message": f"{len(large_source_files)} source files exceed 5K tokens. "
                       f"When reading these files, use line ranges instead of full reads.",
        })

    available = budget["available_for_work"]["tokens"]
    if available < context_window * 0.5:
        recommendations.append({
            "priority": "high",
            "message": f"Only {available} tokens ({round(available / context_window * 100, 1)}%) "
                       f"available for actual work. Reduce configuration overhead.",
        })

    claude_config_count = category_summaries.get("claude_config", {}).get("file_count", 0)
    if claude_config_count == 0:
        recommendations.append({
            "priority": "medium",
            "message": "No CLAUDE.md found. Create one to give Claude project-specific context.",
        })

    return {
        "success": True,
        "project_path": str(root),
        "context_window": context_window,
        "summary": {
            "total_files_scanned": total_files,
            "files_skipped": skipped_files,
            "total_project_tokens": total_tokens,
            "auto_loaded_tokens": auto_loaded_tokens,
            "project_as_percentage_of_window": round(total_tokens / context_window * 100, 1) if context_window > 0 else 0,
        },
        "categories": category_summaries,
        "budget": budget,
        "largest_files": largest_files,
        "recommendations": recommendations,
    }


def format_tokens(tokens: int) -> str:
    """Format token count with K suffix for readability."""
    if tokens >= 1000:
        return f"{tokens / 1000:.1f}K"
    return str(tokens)


def print_human_readable(result: Dict) -> None:
    """Print analysis in human-readable format."""
    if not result["success"]:
        print(f"ERROR: {result['error']}")
        sys.exit(1)

    s = result["summary"]
    cw = result["context_window"]

    print("=" * 64)
    print("  Context Window Analysis")
    print("=" * 64)
    print(f"  Project:           {result['project_path']}")
    print(f"  Context window:    {format_tokens(cw)} tokens")
    print(f"  Files scanned:     {s['total_files_scanned']} ({s['files_skipped']} skipped)")
    print(f"  Total project:     ~{format_tokens(s['total_project_tokens'])} tokens ({s['project_as_percentage_of_window']}% of window)")
    print(f"  Auto-loaded:       ~{format_tokens(s['auto_loaded_tokens'])} tokens (CLAUDE.md config)")
    print()

    # Budget breakdown
    print("--- Context Budget Breakdown ---")
    budget = result["budget"]
    for key, info in budget.items():
        tokens = info["tokens"]
        pct = round(tokens / cw * 100, 1) if cw > 0 else 0
        bar_len = int(pct / 2)
        bar = "#" * bar_len + "." * (50 - bar_len)
        print(f"  {info['label']}")
        print(f"    {format_tokens(tokens):>8} tokens ({pct:>5.1f}%)  [{bar}]")
    print()

    # Category breakdown
    print("--- Category Breakdown ---")
    for cat_key, cat_info in result["categories"].items():
        if cat_info["file_count"] == 0:
            continue
        print(f"  {cat_info['label']} ({cat_info['file_count']} files)")
        print(f"    ~{format_tokens(cat_info['total_tokens'])} tokens ({cat_info['percentage_of_window']}% of window)")
        if cat_info["largest_files"]:
            top_count = min(5, len(cat_info["largest_files"]))
            for f in cat_info["largest_files"][:top_count]:
                print(f"      {f['path']}  (~{format_tokens(f['token_estimate'])} tokens)")
        print()

    # Largest files
    print("--- Largest Files (Top 20) ---")
    for i, f in enumerate(result["largest_files"], 1):
        print(f"  {i:>2}. {f['path']}  (~{format_tokens(f['token_estimate'])} tokens)")
    print()

    # Recommendations
    if result["recommendations"]:
        print("--- Recommendations ---")
        priority_order = {"high": 0, "medium": 1, "low": 2}
        sorted_recs = sorted(result["recommendations"], key=lambda r: priority_order.get(r["priority"], 3))
        for rec in sorted_recs:
            print(f"  [{rec['priority'].upper()}] {rec['message']}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Analyze a project to estimate Claude Code context window usage",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
Examples:
    python context_analyzer.py /path/to/project
    python context_analyzer.py . --max-depth 3
    python context_analyzer.py /project --context-window 200000 --json
        """),
    )
    parser.add_argument(
        "project_path",
        help="Path to the project directory to analyze",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=5,
        help="Maximum directory traversal depth (default: 5)",
    )
    parser.add_argument(
        "--context-window",
        type=int,
        default=200_000,
        help="Total context window size in tokens (default: 200000)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format",
    )

    args = parser.parse_args()

    result = scan_project(
        project_path=args.project_path,
        max_depth=args.max_depth,
        context_window=args.context_window,
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_human_readable(result)

    if not result["success"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
