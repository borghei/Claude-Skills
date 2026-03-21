#!/usr/bin/env python3
"""Context Pruner - Intelligently prune context by removing low-relevance content.

Removes blank lines, comment blocks, redundant sections, verbose patterns,
and boilerplate to compress context while preserving high-signal code.
Implements the Adaptive Compression pattern from the Context Engine skill.

Usage:
    python context_pruner.py path/to/file.py
    python context_pruner.py path/to/file.py --aggressive --json
    python context_pruner.py path/to/dir --output pruned_output/
    cat context.txt | python context_pruner.py --stdin
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


# Pruning levels control how aggressively we strip content
PRUNING_LEVELS = {
    "light": {
        "strip_blank_runs": 2,       # Collapse runs of blanks to max N
        "strip_comments": False,     # Keep all comments
        "strip_docstrings": False,   # Keep all docstrings
        "strip_imports": False,      # Keep all imports
        "strip_decorative": True,    # Remove decorative dividers
        "collapse_braces": False,    # Keep closing brace lines
    },
    "moderate": {
        "strip_blank_runs": 1,
        "strip_comments": True,      # Remove standalone comment lines
        "strip_docstrings": False,
        "strip_imports": False,
        "strip_decorative": True,
        "collapse_braces": True,
    },
    "aggressive": {
        "strip_blank_runs": 0,       # Remove ALL blank lines
        "strip_comments": True,
        "strip_docstrings": True,    # Trim long docstrings to first line
        "strip_imports": True,       # Collapse import blocks to summary
        "strip_decorative": True,
        "collapse_braces": True,
    },
}


def collapse_blank_runs(lines, max_consecutive):
    """Collapse consecutive blank lines to at most max_consecutive."""
    result = []
    blank_count = 0
    for line in lines:
        if line.strip() == "":
            blank_count += 1
            if blank_count <= max_consecutive:
                result.append(line)
        else:
            blank_count = 0
            result.append(line)
    return result


def strip_comment_lines(lines):
    """Remove standalone comment lines (preserving inline comments and shebangs)."""
    result = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        # Keep shebangs, keep inline comments (code before #)
        if stripped.startswith("#") and not stripped.startswith("#!"):
            # Keep type: ignore, noqa, pragma, and encoding comments
            if any(kw in stripped.lower() for kw in ["type:", "noqa", "pragma", "coding", "pylint", "fmt:"]):
                result.append(line)
                continue
            continue
        # Strip // comments for JS/TS/Go/Java/C etc.
        if stripped.startswith("//") and not stripped.startswith("///"):
            continue
        result.append(line)
    return result


def trim_docstrings(lines):
    """Trim multi-line docstrings to just the first summary line."""
    result = []
    in_docstring = False
    docstring_quote = None
    docstring_indent = ""
    first_line_added = False

    for line in lines:
        stripped = line.strip()

        if not in_docstring:
            # Detect docstring opening
            for quote in ['"""', "'''"]:
                if quote in stripped:
                    idx = stripped.index(quote)
                    after_quote = stripped[idx + 3:]
                    # Single-line docstring — keep as is
                    if quote in after_quote:
                        result.append(line)
                        break
                    # Multi-line docstring starts
                    in_docstring = True
                    docstring_quote = quote
                    docstring_indent = line[: len(line) - len(line.lstrip())]
                    # Keep the opening line
                    result.append(line)
                    first_line_added = True
                    break
            else:
                result.append(line)
        else:
            # Inside a docstring — look for closing quote
            if docstring_quote in stripped:
                # Close the docstring with just the closing quotes
                result.append(docstring_indent + docstring_quote)
                in_docstring = False
                docstring_quote = None
                first_line_added = False
            # Skip intermediate docstring lines (they are pruned)

    return result


def collapse_imports(lines):
    """Collapse consecutive import lines into a summary comment."""
    result = []
    import_block = []
    import_modules = set()

    def flush_imports():
        if import_block:
            count = len(import_block)
            # Extract module names
            for imp_line in import_block:
                m = re.match(r"^\s*(?:from\s+(\S+)|import\s+(\S+))", imp_line)
                if m:
                    import_modules.add(m.group(1) or m.group(2))
            modules_str = ", ".join(sorted(import_modules)[:8])
            if len(import_modules) > 8:
                modules_str += f", ... (+{len(import_modules) - 8} more)"
            result.append(f"# [{count} imports: {modules_str}]")
            import_block.clear()
            import_modules.clear()

    for line in lines:
        stripped = line.strip()
        if re.match(r"^(import |from \S+ import )", stripped):
            import_block.append(line)
        else:
            flush_imports()
            result.append(line)

    flush_imports()
    return result


def strip_decorative(lines):
    """Remove decorative dividers and banner comments."""
    result = []
    for line in lines:
        stripped = line.strip()
        # Lines that are purely decorative: ####, -----, ====, /****/
        if re.match(r"^[#\-=*\/\\]{4,}\s*$", stripped):
            continue
        # Banner-style comments like # ========== SECTION ==========
        if re.match(r"^#\s*[=\-*]{3,}.*[=\-*]{3,}\s*$", stripped):
            # Keep the text, strip the decoration
            text = re.sub(r"[=\-*]+", "", stripped.lstrip("#")).strip()
            if text:
                indent = line[: len(line) - len(line.lstrip())]
                result.append(f"{indent}# {text}")
            continue
        result.append(line)
    return result


def collapse_closing_braces(lines):
    """Remove lines that are only closing braces/brackets with optional whitespace."""
    result = []
    for line in lines:
        stripped = line.strip()
        if stripped in ("}", "},", ");", "});", "]", "],"):
            # Keep it but strip trailing whitespace
            result.append(line.rstrip())
        else:
            result.append(line)
    # Remove consecutive closing-only lines (keep just one)
    final = []
    prev_closing = False
    for line in result:
        stripped = line.strip()
        is_closing = stripped in ("}", "},", ");", "});", "]", "],")
        if is_closing and prev_closing:
            # Merge onto previous line
            if final:
                final[-1] = final[-1] + " " + stripped
            continue
        final.append(line)
        prev_closing = is_closing
    return final


def detect_redundant_blocks(lines, min_block_size=3):
    """Detect and remove repeated blocks of identical lines."""
    result = []
    seen_blocks = {}
    i = 0
    removed = 0

    while i < len(lines):
        if i + min_block_size <= len(lines):
            block = tuple(l.strip() for l in lines[i : i + min_block_size])
            # Skip blocks that are all empty
            if any(l for l in block):
                if block in seen_blocks:
                    result.append(f"# [duplicate block removed, first seen line {seen_blocks[block] + 1}]")
                    i += min_block_size
                    removed += min_block_size
                    continue
                seen_blocks[block] = i
        result.append(lines[i])
        i += 1

    return result, removed


def prune_content(content, level="moderate"):
    """Apply pruning strategies to content string. Returns (pruned_content, stats)."""
    config = PRUNING_LEVELS.get(level, PRUNING_LEVELS["moderate"])
    lines = content.splitlines()
    original_lines = len(lines)
    original_tokens = max(1, len(content) // 4)
    stats = {"original_lines": original_lines, "original_tokens": original_tokens, "operations": []}

    # 1. Strip decorative elements
    if config["strip_decorative"]:
        before = len(lines)
        lines = strip_decorative(lines)
        removed = before - len(lines)
        if removed > 0:
            stats["operations"].append({"op": "strip_decorative", "lines_removed": removed})

    # 2. Strip comments
    if config["strip_comments"]:
        before = len(lines)
        lines = strip_comment_lines(lines)
        removed = before - len(lines)
        if removed > 0:
            stats["operations"].append({"op": "strip_comments", "lines_removed": removed})

    # 3. Trim docstrings
    if config["strip_docstrings"]:
        before = len(lines)
        lines = trim_docstrings(lines)
        removed = before - len(lines)
        if removed > 0:
            stats["operations"].append({"op": "trim_docstrings", "lines_removed": removed})

    # 4. Collapse imports
    if config["strip_imports"]:
        before = len(lines)
        lines = collapse_imports(lines)
        removed = before - len(lines)
        if removed > 0:
            stats["operations"].append({"op": "collapse_imports", "lines_removed": removed})

    # 5. Collapse closing braces
    if config["collapse_braces"]:
        before = len(lines)
        lines = collapse_closing_braces(lines)
        removed = before - len(lines)
        if removed > 0:
            stats["operations"].append({"op": "collapse_braces", "lines_removed": removed})

    # 6. Remove redundant blocks
    before = len(lines)
    lines, dup_removed = detect_redundant_blocks(lines)
    if dup_removed > 0:
        stats["operations"].append({"op": "remove_duplicates", "lines_removed": dup_removed})

    # 7. Collapse blank lines (always, last step)
    before = len(lines)
    lines = collapse_blank_runs(lines, config["strip_blank_runs"])
    removed = before - len(lines)
    if removed > 0:
        stats["operations"].append({"op": "collapse_blanks", "lines_removed": removed})

    pruned_content = "\n".join(lines)
    pruned_tokens = max(1, len(pruned_content) // 4)

    stats["pruned_lines"] = len(lines)
    stats["pruned_tokens"] = pruned_tokens
    stats["lines_removed"] = original_lines - len(lines)
    stats["tokens_saved"] = original_tokens - pruned_tokens
    stats["compression_ratio"] = round(pruned_tokens / original_tokens, 3) if original_tokens > 0 else 1.0

    return pruned_content, stats


def prune_file(file_path, level, output_dir=None):
    """Prune a single file and optionally write output."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except (OSError, IOError) as e:
        return {"path": str(file_path), "error": str(e)}

    pruned, stats = prune_content(content, level)
    stats["path"] = str(file_path)

    if output_dir:
        out_path = Path(output_dir) / Path(file_path).name
        os.makedirs(output_dir, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(pruned)
        stats["output_path"] = str(out_path)

    stats["pruned_content"] = pruned
    return stats


def collect_files(path, max_files=50):
    """Collect prunable files from a path."""
    p = Path(path)
    if p.is_file():
        return [p]
    if p.is_dir():
        files = []
        skip = {".git", "__pycache__", "node_modules", ".venv", "venv"}
        exts = {".py", ".js", ".ts", ".tsx", ".jsx", ".md", ".yaml", ".yml",
                ".go", ".rs", ".java", ".rb", ".c", ".cpp", ".h", ".sh"}
        for root, dirs, fnames in os.walk(p):
            dirs[:] = [d for d in dirs if d not in skip]
            for fn in fnames:
                fp = Path(root) / fn
                if fp.suffix.lower() in exts:
                    files.append(fp)
                    if len(files) >= max_files:
                        return files
        return files
    return []


def format_human(results):
    """Format results for human-readable output."""
    lines = []
    lines.append("=" * 60)
    lines.append("  CONTEXT PRUNER REPORT")
    lines.append("=" * 60)

    total_saved = 0
    total_original = 0

    for r in results:
        if "error" in r:
            lines.append(f"\n  {r['path']}: ERROR - {r['error']}")
            continue

        lines.append(f"\n  File: {r['path']}")
        lines.append(f"    Lines: {r['original_lines']} -> {r['pruned_lines']} ({r['lines_removed']} removed)")
        lines.append(f"    Tokens: ~{r['original_tokens']:,} -> ~{r['pruned_tokens']:,} ({r['tokens_saved']:,} saved)")
        lines.append(f"    Compression: {r['compression_ratio'] * 100:.1f}%")

        if r.get("operations"):
            lines.append("    Operations:")
            for op in r["operations"]:
                lines.append(f"      - {op['op']}: {op['lines_removed']} lines removed")

        if "output_path" in r:
            lines.append(f"    Written to: {r['output_path']}")

        total_saved += r.get("tokens_saved", 0)
        total_original += r.get("original_tokens", 0)

    lines.append("\n" + "-" * 60)
    lines.append(f"  Total tokens saved: ~{total_saved:,}")
    if total_original > 0:
        lines.append(f"  Overall compression: {(total_original - total_saved) / total_original * 100:.1f}%")
    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Prune context by removing low-relevance content, redundancy, and verbose patterns.",
        epilog="Example: python context_pruner.py src/main.py --aggressive --json",
    )
    parser.add_argument("path", nargs="?", help="File or directory to prune")
    parser.add_argument("--stdin", action="store_true", help="Read content from stdin")
    parser.add_argument("--level", choices=["light", "moderate", "aggressive"], default="moderate",
                        help="Pruning aggressiveness (default: moderate)")
    parser.add_argument("--aggressive", action="store_true", help="Shortcut for --level aggressive")
    parser.add_argument("--output", type=str, help="Output directory for pruned files")
    parser.add_argument("--max-files", type=int, default=50, help="Max files to process (default: 50)")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output results as JSON")

    args = parser.parse_args()
    level = "aggressive" if args.aggressive else args.level

    if not args.path and not args.stdin:
        parser.print_help()
        sys.exit(1)

    results = []

    if args.stdin:
        content = sys.stdin.read()
        pruned, stats = prune_content(content, level)
        stats["path"] = "<stdin>"
        if not args.json_output:
            print(pruned)
            return
        stats.pop("pruned_content", None)
        results.append(stats)
    elif args.path:
        files = collect_files(args.path, max_files=args.max_files)
        if not files:
            print(f"Error: No files found at '{args.path}'", file=sys.stderr)
            sys.exit(1)
        for f in files:
            r = prune_file(f, level, output_dir=args.output)
            r.pop("pruned_content", None)
            results.append(r)

    if args.json_output:
        print(json.dumps(results, indent=2))
    else:
        print(format_human(results))


if __name__ == "__main__":
    main()
