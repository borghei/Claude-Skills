#!/usr/bin/env python3
"""Context Analyzer - Analyze files and prompts for token usage, relevance scoring, and optimization.

Estimates token counts, scores context relevance across segments, identifies waste,
and provides actionable optimization suggestions based on the Context Engine's
Token Budget Allocation Framework.

Usage:
    python context_analyzer.py path/to/file_or_dir
    python context_analyzer.py --prompt "Fix the auth middleware bug"
    python context_analyzer.py path/to/dir --budget 128000 --json
"""

import argparse
import json
import math
import os
import re
import sys
from collections import Counter
from pathlib import Path


# Approximate token estimation: ~4 chars per token for English/code (GPT-family heuristic)
CHARS_PER_TOKEN = 4

# Token Budget Allocation Framework (from SKILL.md)
BUDGET_SEGMENTS = {
    "system_instructions": {"min": 0.05, "max": 0.10, "priority": "fixed"},
    "task_context": {"min": 0.20, "max": 0.30, "priority": "high"},
    "relevant_code": {"min": 0.25, "max": 0.40, "priority": "dynamic"},
    "conversation_history": {"min": 0.10, "max": 0.20, "priority": "sliding"},
    "tool_results": {"min": 0.05, "max": 0.15, "priority": "ephemeral"},
    "reserved_buffer": {"min": 0.05, "max": 0.10, "priority": "protected"},
}

# Patterns indicating low-signal content
LOW_SIGNAL_PATTERNS = [
    (r"^\s*#.*$", "comment_lines"),
    (r"^\s*$", "blank_lines"),
    (r"^\s*(import|from)\s+", "import_lines"),
    (r"^\s*\}\s*$", "closing_braces"),
    (r"^\s*pass\s*$", "pass_statements"),
    (r"^\s*\.{3}\s*$", "ellipsis"),
]

# Patterns indicating high-signal content
HIGH_SIGNAL_PATTERNS = [
    (r"^\s*(def|async def)\s+\w+", "function_definitions"),
    (r"^\s*class\s+\w+", "class_definitions"),
    (r"^\s*(return|yield)\s+", "return_statements"),
    (r"(raise|except|try|finally)\s+", "error_handling"),
    (r"^\s*@\w+", "decorators"),
]

VERBOSE_PATTERNS = [
    (r"#{3,}\s*-+\s*$", "decorative_dividers"),
    (r"^\s*#\s*={3,}", "decorative_headers"),
    (r"^\s*\"\"\"[\s\S]{200,}\"\"\"", "long_docstrings"),
    (r"(TODO|FIXME|HACK|XXX|NOQA)", "todo_markers"),
]


def estimate_tokens(text):
    """Estimate token count from text using character-based heuristic."""
    return max(1, len(text) // CHARS_PER_TOKEN)


def analyze_file(file_path):
    """Analyze a single file for token usage and content signals."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except (OSError, IOError) as e:
        return {"path": str(file_path), "error": str(e)}

    lines = content.splitlines()
    total_tokens = estimate_tokens(content)
    total_lines = len(lines)

    low_signal_counts = Counter()
    high_signal_counts = Counter()
    low_signal_lines = 0
    high_signal_lines = 0

    for line in lines:
        matched_low = False
        for pattern, name in LOW_SIGNAL_PATTERNS:
            if re.match(pattern, line):
                low_signal_counts[name] += 1
                low_signal_lines += 1
                matched_low = True
                break
        if not matched_low:
            for pattern, name in HIGH_SIGNAL_PATTERNS:
                if re.search(pattern, line):
                    high_signal_counts[name] += 1
                    high_signal_lines += 1
                    break

    verbose_counts = Counter()
    for pattern, name in VERBOSE_PATTERNS:
        matches = re.findall(pattern, content, re.MULTILINE)
        if matches:
            verbose_counts[name] = len(matches)

    neutral_lines = total_lines - low_signal_lines - high_signal_lines
    if total_lines > 0:
        relevance_score = round(
            (high_signal_lines * 1.0 + neutral_lines * 0.5) / total_lines, 3
        )
    else:
        relevance_score = 0.0

    # Detect duplicate/redundant blocks (repeated sequences of 3+ identical lines)
    redundant_blocks = 0
    if total_lines > 6:
        seen_blocks = set()
        for i in range(len(lines) - 2):
            block = tuple(lines[i : i + 3])
            if block in seen_blocks and any(l.strip() for l in block):
                redundant_blocks += 1
            seen_blocks.add(block)

    ext = Path(file_path).suffix.lower()
    size_bytes = os.path.getsize(file_path)

    return {
        "path": str(file_path),
        "extension": ext,
        "size_bytes": size_bytes,
        "total_lines": total_lines,
        "estimated_tokens": total_tokens,
        "relevance_score": relevance_score,
        "high_signal_lines": high_signal_lines,
        "low_signal_lines": low_signal_lines,
        "neutral_lines": neutral_lines,
        "high_signal_breakdown": dict(high_signal_counts),
        "low_signal_breakdown": dict(low_signal_counts),
        "verbose_patterns": dict(verbose_counts),
        "redundant_blocks": redundant_blocks,
    }


def compute_budget_analysis(total_tokens, budget):
    """Compute how the analyzed tokens fit within a context budget."""
    segments = {}
    for name, config in BUDGET_SEGMENTS.items():
        min_tokens = int(budget * config["min"])
        max_tokens = int(budget * config["max"])
        segments[name] = {
            "min_tokens": min_tokens,
            "max_tokens": max_tokens,
            "priority": config["priority"],
        }

    utilization = round(total_tokens / budget, 3) if budget > 0 else 0.0
    remaining = max(0, budget - total_tokens)

    return {
        "budget_tokens": budget,
        "used_tokens": total_tokens,
        "remaining_tokens": remaining,
        "utilization": utilization,
        "segments": segments,
        "over_budget": total_tokens > budget,
    }


def generate_suggestions(file_results, budget_analysis):
    """Generate optimization suggestions from analysis results."""
    suggestions = []

    total_low = sum(r.get("low_signal_lines", 0) for r in file_results if "error" not in r)
    total_lines = sum(r.get("total_lines", 0) for r in file_results if "error" not in r)

    if total_lines > 0 and total_low / total_lines > 0.35:
        suggestions.append({
            "type": "reduce_low_signal",
            "severity": "high",
            "message": (
                f"{total_low}/{total_lines} lines ({total_low * 100 // total_lines}%) are low-signal "
                "(blanks, comments, closing braces). Consider pruning or summarizing."
            ),
        })

    total_redundant = sum(r.get("redundant_blocks", 0) for r in file_results if "error" not in r)
    if total_redundant > 3:
        suggestions.append({
            "type": "remove_redundancy",
            "severity": "medium",
            "message": f"Detected {total_redundant} redundant 3-line blocks. Deduplicate repeated code sections.",
        })

    if budget_analysis and budget_analysis["over_budget"]:
        overage = budget_analysis["used_tokens"] - budget_analysis["budget_tokens"]
        suggestions.append({
            "type": "over_budget",
            "severity": "critical",
            "message": (
                f"Context exceeds budget by {overage:,} tokens. "
                "Apply tiered loading: keep Tier 0/1, summarize Tier 2, drop Tier 3."
            ),
        })
    elif budget_analysis and budget_analysis["utilization"] < 0.5:
        suggestions.append({
            "type": "under_utilized",
            "severity": "info",
            "message": (
                f"Only {budget_analysis['utilization'] * 100:.0f}% of budget used. "
                "You can load additional dependency or test files for better coverage."
            ),
        })

    # Check for very large individual files
    for r in file_results:
        if "error" in r:
            continue
        if r["estimated_tokens"] > 8000:
            suggestions.append({
                "type": "large_file",
                "severity": "medium",
                "message": (
                    f"{r['path']} is ~{r['estimated_tokens']:,} tokens. "
                    "Consider loading only relevant functions instead of the full file."
                ),
            })

    if not suggestions:
        suggestions.append({
            "type": "ok",
            "severity": "info",
            "message": "Context looks well-optimized. No major issues detected.",
        })

    return suggestions


def collect_files(path, max_files=100):
    """Collect files from a path (file or directory)."""
    p = Path(path)
    if p.is_file():
        return [p]

    if p.is_dir():
        files = []
        skip_dirs = {".git", "__pycache__", "node_modules", ".venv", "venv", ".tox"}
        for root, dirs, filenames in os.walk(p):
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            for fname in filenames:
                fp = Path(root) / fname
                if fp.suffix.lower() in {
                    ".py", ".js", ".ts", ".tsx", ".jsx", ".md", ".yaml", ".yml",
                    ".json", ".toml", ".cfg", ".ini", ".sh", ".go", ".rs", ".java",
                    ".rb", ".c", ".cpp", ".h", ".hpp", ".cs", ".swift", ".kt",
                }:
                    files.append(fp)
                    if len(files) >= max_files:
                        return files
        return files

    return []


def format_human(file_results, budget_analysis, suggestions):
    """Format results for human-readable terminal output."""
    lines = []
    lines.append("=" * 64)
    lines.append("  CONTEXT ANALYZER REPORT")
    lines.append("=" * 64)

    total_tokens = sum(r.get("estimated_tokens", 0) for r in file_results if "error" not in r)
    total_files = sum(1 for r in file_results if "error" not in r)
    lines.append(f"\n  Files analyzed: {total_files}")
    lines.append(f"  Total estimated tokens: {total_tokens:,}")

    if budget_analysis:
        lines.append(f"  Budget: {budget_analysis['budget_tokens']:,} tokens")
        lines.append(f"  Utilization: {budget_analysis['utilization'] * 100:.1f}%")
        if budget_analysis["over_budget"]:
            lines.append(f"  ** OVER BUDGET by {total_tokens - budget_analysis['budget_tokens']:,} tokens **")

    lines.append(f"\n{'  File':<45} {'Tokens':>8} {'Relevance':>10}")
    lines.append("  " + "-" * 62)
    for r in sorted(file_results, key=lambda x: x.get("estimated_tokens", 0), reverse=True):
        if "error" in r:
            lines.append(f"  {r['path']:<45} ERROR: {r['error']}")
            continue
        name = r["path"]
        if len(name) > 43:
            name = "..." + name[-40:]
        lines.append(f"  {name:<45} {r['estimated_tokens']:>8,} {r['relevance_score']:>10.2f}")

    lines.append(f"\n  OPTIMIZATION SUGGESTIONS")
    lines.append("  " + "-" * 40)
    for s in suggestions:
        marker = {"critical": "!!!", "high": "!!", "medium": "!", "info": " "}
        icon = marker.get(s["severity"], " ")
        lines.append(f"  [{icon}] {s['message']}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze files/prompts for token usage, context relevance, and optimization suggestions.",
        epilog="Example: python context_analyzer.py src/ --budget 128000 --json",
    )
    parser.add_argument("path", nargs="?", help="File or directory to analyze")
    parser.add_argument("--prompt", type=str, help="Analyze a prompt string for token estimation")
    parser.add_argument("--budget", type=int, default=128000, help="Context window budget in tokens (default: 128000)")
    parser.add_argument("--max-files", type=int, default=100, help="Max files to analyze in a directory (default: 100)")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output results as JSON")

    args = parser.parse_args()

    if not args.path and not args.prompt:
        parser.print_help()
        sys.exit(1)

    file_results = []

    if args.prompt:
        tokens = estimate_tokens(args.prompt)
        file_results.append({
            "path": "<prompt>",
            "extension": "",
            "size_bytes": len(args.prompt.encode("utf-8")),
            "total_lines": args.prompt.count("\n") + 1,
            "estimated_tokens": tokens,
            "relevance_score": 1.0,
            "high_signal_lines": args.prompt.count("\n") + 1,
            "low_signal_lines": 0,
            "neutral_lines": 0,
            "high_signal_breakdown": {},
            "low_signal_breakdown": {},
            "verbose_patterns": {},
            "redundant_blocks": 0,
        })

    if args.path:
        files = collect_files(args.path, max_files=args.max_files)
        if not files:
            print(f"Error: No analyzable files found at '{args.path}'", file=sys.stderr)
            sys.exit(1)
        for f in files:
            file_results.append(analyze_file(f))

    total_tokens = sum(r.get("estimated_tokens", 0) for r in file_results if "error" not in r)
    budget_analysis = compute_budget_analysis(total_tokens, args.budget)
    suggestions = generate_suggestions(file_results, budget_analysis)

    result = {
        "summary": {
            "files_analyzed": sum(1 for r in file_results if "error" not in r),
            "total_estimated_tokens": total_tokens,
            "budget": args.budget,
        },
        "files": file_results,
        "budget_analysis": budget_analysis,
        "suggestions": suggestions,
    }

    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print(format_human(file_results, budget_analysis, suggestions))


if __name__ == "__main__":
    main()
