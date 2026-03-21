#!/usr/bin/env python3
"""Memory Indexer - Index and search a memory/knowledge base directory.

Scans a directory of markdown/text files, builds a term-frequency index,
and scores entries by relevance to a query using TF-IDF-inspired ranking.
Designed for the Context Engine's Session Memory and Knowledge Base layers.

Usage:
    python memory_indexer.py path/to/knowledge_base --query "authentication flow"
    python memory_indexer.py path/to/memory_dir --query "deployment" --top 5 --json
    python memory_indexer.py path/to/dir --index-only --json
    python memory_indexer.py path/to/dir --stats
"""

import argparse
import json
import math
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


# Stop words to exclude from indexing
STOP_WORDS = frozenset({
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "has", "have", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "can", "this", "that", "these", "those",
    "it", "its", "not", "no", "if", "then", "else", "when", "which",
    "what", "how", "who", "where", "why", "all", "each", "every", "both",
    "as", "so", "up", "out", "about", "into", "over", "after", "before",
    "between", "under", "above", "such", "only", "also", "than", "too",
    "very", "just", "more", "most", "other", "some", "any", "new", "old",
    "use", "used", "using", "see", "e", "g", "i", "we", "you", "they",
})

# File extensions to index
INDEXABLE_EXTENSIONS = {".md", ".txt", ".yaml", ".yml", ".json", ".toml", ".rst", ".org"}

# Boost factors for different content locations
TITLE_BOOST = 3.0
HEADING_BOOST = 2.0
FRONTMATTER_BOOST = 1.5
CODE_BLOCK_PENALTY = 0.5


def tokenize(text):
    """Split text into lowercase tokens, filtering stop words and short tokens."""
    # Split on non-alphanumeric (keep underscores and hyphens for code terms)
    raw_tokens = re.findall(r"[a-zA-Z_][a-zA-Z0-9_-]*", text.lower())
    return [t for t in raw_tokens if t not in STOP_WORDS and len(t) > 1]


def extract_sections(content):
    """Extract structured sections from a markdown file."""
    sections = []
    current_heading = ""
    current_body = []
    in_code_block = False
    in_frontmatter = False
    frontmatter_text = []

    lines = content.splitlines()

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Detect YAML frontmatter
        if i == 0 and stripped == "---":
            in_frontmatter = True
            continue
        if in_frontmatter:
            if stripped == "---":
                in_frontmatter = False
                sections.append({
                    "type": "frontmatter",
                    "heading": "_frontmatter",
                    "content": "\n".join(frontmatter_text),
                    "line": 0,
                })
                continue
            frontmatter_text.append(line)
            continue

        # Track code blocks
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            current_body.append(line)
            continue

        # Detect headings
        if not in_code_block and re.match(r"^#{1,6}\s+", stripped):
            # Flush previous section
            if current_heading or current_body:
                sections.append({
                    "type": "section",
                    "heading": current_heading,
                    "content": "\n".join(current_body),
                    "line": max(0, i - len(current_body)),
                })
            current_heading = re.sub(r"^#{1,6}\s+", "", stripped)
            current_body = []
        else:
            current_body.append(line)

    # Flush last section
    if current_heading or current_body:
        sections.append({
            "type": "section",
            "heading": current_heading,
            "content": "\n".join(current_body),
            "line": max(0, len(lines) - len(current_body)),
        })

    return sections


def build_file_entry(file_path):
    """Build an index entry for a single file."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except (OSError, IOError) as e:
        return None

    stat = os.stat(file_path)
    sections = extract_sections(content)

    # Build term frequency map with positional boosts
    term_freq = Counter()
    section_terms = {}

    # Index file name tokens with title boost
    name_tokens = tokenize(Path(file_path).stem.replace("-", " ").replace("_", " "))
    for t in name_tokens:
        term_freq[t] += TITLE_BOOST

    for section in sections:
        heading_tokens = tokenize(section["heading"])
        body_tokens = tokenize(section["content"])

        # Boost heading terms
        for t in heading_tokens:
            boost = FRONTMATTER_BOOST if section["type"] == "frontmatter" else HEADING_BOOST
            term_freq[t] += boost

        # Body terms at base weight (penalize code blocks slightly)
        in_code = False
        for line in section["content"].splitlines():
            if line.strip().startswith("```"):
                in_code = not in_code
                continue
            line_tokens = tokenize(line)
            weight = CODE_BLOCK_PENALTY if in_code else 1.0
            for t in line_tokens:
                term_freq[t] += weight

        section_key = section["heading"] or f"_section_{section['line']}"
        section_terms[section_key] = set(heading_tokens + body_tokens)

    total_tokens = sum(term_freq.values())

    # Extract title from first heading or filename
    title = Path(file_path).stem
    for s in sections:
        if s["type"] == "section" and s["heading"]:
            title = s["heading"]
            break

    # Detect staleness based on modification time
    mtime = datetime.fromtimestamp(stat.st_mtime)
    days_old = (datetime.now() - mtime).days
    if days_old < 7:
        freshness = "fresh"
    elif days_old < 30:
        freshness = "aging"
    else:
        freshness = "stale"

    return {
        "path": str(file_path),
        "title": title,
        "size_bytes": stat.st_size,
        "modified": mtime.isoformat(),
        "days_since_modified": days_old,
        "freshness": freshness,
        "total_weighted_tokens": round(total_tokens, 1),
        "unique_terms": len(term_freq),
        "sections": [{"heading": s["heading"], "type": s["type"], "line": s["line"]}
                      for s in sections],
        "term_freq": dict(term_freq),
        "section_terms": {k: list(v) for k, v in section_terms.items()},
    }


def build_index(directory, max_files=500):
    """Build a full index of a knowledge base directory."""
    entries = []
    doc_freq = Counter()  # How many documents contain each term
    skip_dirs = {".git", "__pycache__", "node_modules", ".venv", "venv"}

    p = Path(directory)
    if not p.is_dir():
        return [], {}

    file_count = 0
    for root, dirs, fnames in os.walk(p):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for fn in sorted(fnames):
            fp = Path(root) / fn
            if fp.suffix.lower() not in INDEXABLE_EXTENSIONS:
                continue
            entry = build_file_entry(fp)
            if entry:
                entries.append(entry)
                # Track document frequency
                for term in entry["term_freq"]:
                    doc_freq[term] += 1
                file_count += 1
                if file_count >= max_files:
                    break
        if file_count >= max_files:
            break

    return entries, dict(doc_freq)


def score_query(query, entries, doc_freq):
    """Score all entries against a query using TF-IDF-inspired ranking."""
    query_tokens = tokenize(query)
    if not query_tokens:
        return []

    num_docs = max(len(entries), 1)
    results = []

    for entry in entries:
        tf = entry["term_freq"]
        total = max(entry["total_weighted_tokens"], 1)
        score = 0.0
        matched_terms = []

        for qt in query_tokens:
            if qt in tf:
                # TF component: term frequency normalized by document length
                tf_val = tf[qt] / total
                # IDF component: inverse document frequency
                df = doc_freq.get(qt, 1)
                idf_val = math.log(num_docs / df) + 1
                term_score = tf_val * idf_val
                score += term_score
                matched_terms.append(qt)

        # Freshness bonus: fresh docs get a small boost
        if entry["freshness"] == "fresh":
            score *= 1.1
        elif entry["freshness"] == "stale":
            score *= 0.9

        # Coverage bonus: matching more query terms is better
        if len(query_tokens) > 1:
            coverage = len(set(matched_terms)) / len(set(query_tokens))
            score *= (0.5 + 0.5 * coverage)

        if score > 0:
            # Find which sections matched
            matched_sections = []
            query_set = set(query_tokens)
            for sec_name, sec_terms in entry.get("section_terms", {}).items():
                if query_set & set(sec_terms):
                    matched_sections.append(sec_name)

            results.append({
                "path": entry["path"],
                "title": entry["title"],
                "score": round(score, 4),
                "matched_terms": list(set(matched_terms)),
                "matched_sections": matched_sections,
                "freshness": entry["freshness"],
                "days_old": entry["days_since_modified"],
            })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results


def compute_stats(entries):
    """Compute summary statistics for the index."""
    if not entries:
        return {"total_files": 0}

    total_terms = sum(e["unique_terms"] for e in entries)
    total_size = sum(e["size_bytes"] for e in entries)
    freshness_dist = Counter(e["freshness"] for e in entries)

    # Find most common terms across corpus
    global_freq = Counter()
    for e in entries:
        for term, freq in e["term_freq"].items():
            global_freq[term] += freq

    return {
        "total_files": len(entries),
        "total_size_bytes": total_size,
        "total_unique_terms": len(global_freq),
        "avg_terms_per_file": round(total_terms / len(entries), 1),
        "freshness_distribution": dict(freshness_dist),
        "top_terms": [{"term": t, "frequency": round(f, 1)} for t, f in global_freq.most_common(20)],
        "largest_files": sorted(
            [{"path": e["path"], "size": e["size_bytes"], "terms": e["unique_terms"]}
             for e in entries],
            key=lambda x: x["size"], reverse=True,
        )[:10],
    }


def format_search_results(results, query, top_n):
    """Format search results for human-readable output."""
    lines = []
    lines.append("=" * 60)
    lines.append(f"  MEMORY INDEX SEARCH: \"{query}\"")
    lines.append("=" * 60)

    if not results:
        lines.append("\n  No matching entries found.")
        lines.append("")
        return "\n".join(lines)

    shown = results[:top_n]
    lines.append(f"\n  Found {len(results)} matching entries (showing top {len(shown)}):\n")

    for i, r in enumerate(shown, 1):
        freshness_marker = {"fresh": "+", "aging": "~", "stale": "-"}.get(r["freshness"], "?")
        lines.append(f"  {i}. [{freshness_marker}] {r['title']}")
        lines.append(f"     Path: {r['path']}")
        lines.append(f"     Score: {r['score']:.4f}  |  Age: {r['days_old']}d ({r['freshness']})")
        lines.append(f"     Matched: {', '.join(r['matched_terms'])}")
        if r["matched_sections"]:
            lines.append(f"     Sections: {', '.join(r['matched_sections'][:5])}")
        lines.append("")

    lines.append(f"  Legend: [+] fresh (<7d)  [~] aging (7-30d)  [-] stale (>30d)")
    lines.append("")
    return "\n".join(lines)


def format_stats(stats):
    """Format index statistics for human-readable output."""
    lines = []
    lines.append("=" * 60)
    lines.append("  MEMORY INDEX STATISTICS")
    lines.append("=" * 60)

    lines.append(f"\n  Total files indexed: {stats['total_files']}")
    lines.append(f"  Total size: {stats.get('total_size_bytes', 0):,} bytes")
    lines.append(f"  Unique terms: {stats.get('total_unique_terms', 0):,}")
    lines.append(f"  Avg terms/file: {stats.get('avg_terms_per_file', 0)}")

    fd = stats.get("freshness_distribution", {})
    if fd:
        lines.append(f"\n  Freshness: {fd.get('fresh', 0)} fresh, {fd.get('aging', 0)} aging, {fd.get('stale', 0)} stale")

    top = stats.get("top_terms", [])
    if top:
        lines.append("\n  Top terms:")
        for t in top[:15]:
            lines.append(f"    {t['term']:<30} {t['frequency']:>8.0f}")

    largest = stats.get("largest_files", [])
    if largest:
        lines.append("\n  Largest files:")
        for f in largest[:5]:
            name = f["path"]
            if len(name) > 45:
                name = "..." + name[-42:]
            lines.append(f"    {name:<48} {f['size']:>8,} bytes")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Index and search a memory/knowledge base directory with TF-IDF relevance scoring.",
        epilog="Example: python memory_indexer.py docs/ --query 'auth middleware' --top 5",
    )
    parser.add_argument("directory", help="Directory containing knowledge base files to index")
    parser.add_argument("--query", "-q", type=str, help="Search query to score entries against")
    parser.add_argument("--top", "-n", type=int, default=10, help="Number of top results to return (default: 10)")
    parser.add_argument("--index-only", action="store_true", help="Build and display the index without searching")
    parser.add_argument("--stats", action="store_true", help="Show index statistics")
    parser.add_argument("--max-files", type=int, default=500, help="Maximum files to index (default: 500)")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output results as JSON")

    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"Error: '{args.directory}' is not a directory", file=sys.stderr)
        sys.exit(1)

    if not args.query and not args.index_only and not args.stats:
        parser.print_help()
        print("\nError: Provide --query, --index-only, or --stats", file=sys.stderr)
        sys.exit(1)

    entries, doc_freq = build_index(args.directory, max_files=args.max_files)

    if not entries:
        print(f"No indexable files found in '{args.directory}'", file=sys.stderr)
        sys.exit(1)

    if args.stats:
        stats = compute_stats(entries)
        if args.json_output:
            print(json.dumps(stats, indent=2))
        else:
            print(format_stats(stats))
        return

    if args.index_only:
        index_data = {
            "directory": args.directory,
            "total_files": len(entries),
            "entries": [
                {
                    "path": e["path"],
                    "title": e["title"],
                    "freshness": e["freshness"],
                    "unique_terms": e["unique_terms"],
                    "sections": e["sections"],
                }
                for e in entries
            ],
        }
        if args.json_output:
            print(json.dumps(index_data, indent=2))
        else:
            print(f"Indexed {len(entries)} files from '{args.directory}'")
            for e in entries:
                marker = {"fresh": "+", "aging": "~", "stale": "-"}.get(e["freshness"], "?")
                print(f"  [{marker}] {e['title']} ({e['unique_terms']} terms) - {e['path']}")
        return

    if args.query:
        results = score_query(args.query, entries, doc_freq)
        if args.json_output:
            output = {
                "query": args.query,
                "total_matches": len(results),
                "results": results[:args.top],
            }
            print(json.dumps(output, indent=2))
        else:
            print(format_search_results(results, args.query, args.top))


if __name__ == "__main__":
    main()
