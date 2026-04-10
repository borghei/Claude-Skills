#!/usr/bin/env python3
"""
Document Discovery Tool

Scans a directory for legal documents (PDF, DOCX, TXT, MD, etc.) and
generates an inventory manifest with metadata for pipeline processing.

Usage:
    python document_discovery.py /path/to/contracts
    python document_discovery.py /path/to/ndas --types pdf,docx --json
    python document_discovery.py /path/to/leases --min-size 1024
"""

import argparse
import json
import math
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


DEFAULT_TYPES = ["pdf", "docx", "doc", "txt", "md", "rtf"]

# Estimated processing time per document (seconds) by file type
PROCESSING_ESTIMATES: Dict[str, float] = {
    "pdf": 30.0,
    "docx": 20.0,
    "doc": 25.0,
    "txt": 10.0,
    "md": 10.0,
    "rtf": 20.0,
}

MAX_AGENTS = 10


def format_size(size_bytes: int) -> str:
    """Format file size in human-readable form."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def get_file_extension(filename: str) -> str:
    """Get lowercase file extension without dot."""
    _, ext = os.path.splitext(filename)
    return ext.lower().lstrip(".")


def scan_directory(
    directory: str,
    file_types: List[str],
    min_size: int = 0,
    max_size: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Scan directory recursively for matching documents."""
    documents: List[Dict[str, Any]] = []

    if not os.path.isdir(directory):
        return documents

    for root, dirs, files in os.walk(directory):
        # Skip hidden directories
        dirs[:] = [d for d in dirs if not d.startswith(".")]

        for filename in sorted(files):
            if filename.startswith("."):
                continue

            ext = get_file_extension(filename)
            if ext not in file_types:
                continue

            filepath = os.path.join(root, filename)
            try:
                stat = os.stat(filepath)
                size = stat.st_size
            except OSError:
                continue

            # Size filters
            if size < min_size:
                continue
            if max_size is not None and size > max_size:
                continue

            rel_path = os.path.relpath(filepath, directory)
            mod_time = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")

            documents.append({
                "filename": filename,
                "relative_path": rel_path,
                "absolute_path": filepath,
                "extension": ext,
                "size_bytes": size,
                "size_human": format_size(size),
                "modified": mod_time,
            })

    return documents


def compute_statistics(documents: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compute summary statistics for discovered documents."""
    if not documents:
        return {
            "total_documents": 0,
            "total_size_bytes": 0,
            "total_size_human": "0 B",
            "by_type": {},
            "size_range": {"min": "0 B", "max": "0 B", "avg": "0 B"},
        }

    total_size = sum(d["size_bytes"] for d in documents)
    sizes = [d["size_bytes"] for d in documents]

    by_type: Dict[str, Dict[str, Any]] = {}
    for doc in documents:
        ext = doc["extension"]
        if ext not in by_type:
            by_type[ext] = {"count": 0, "total_size_bytes": 0}
        by_type[ext]["count"] += 1
        by_type[ext]["total_size_bytes"] += doc["size_bytes"]

    for ext_data in by_type.values():
        ext_data["total_size_human"] = format_size(ext_data["total_size_bytes"])

    avg_size = total_size // len(documents) if documents else 0

    return {
        "total_documents": len(documents),
        "total_size_bytes": total_size,
        "total_size_human": format_size(total_size),
        "by_type": by_type,
        "size_range": {
            "min": format_size(min(sizes)),
            "max": format_size(max(sizes)),
            "avg": format_size(avg_size),
        },
    }


def estimate_processing(documents: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Estimate processing time and recommend agent allocation."""
    if not documents:
        return {
            "estimated_seconds": 0,
            "estimated_human": "0 seconds",
            "recommended_agents": 1,
            "documents_per_agent": 0,
        }

    total_seconds = 0.0
    for doc in documents:
        ext = doc["extension"]
        est = PROCESSING_ESTIMATES.get(ext, 20.0)
        # Scale by file size (larger files take longer)
        size_factor = max(1.0, doc["size_bytes"] / (100 * 1024))  # Baseline 100KB
        total_seconds += est * min(size_factor, 5.0)  # Cap at 5x

    doc_count = len(documents)
    if doc_count <= 5:
        recommended_agents = 1
    elif doc_count <= 15:
        recommended_agents = min(3, doc_count)
    elif doc_count <= 40:
        recommended_agents = min(6, doc_count)
    else:
        recommended_agents = min(MAX_AGENTS, doc_count)

    docs_per_agent = math.ceil(doc_count / recommended_agents)

    # Parallel processing reduces total time
    parallel_seconds = total_seconds / recommended_agents

    if parallel_seconds < 60:
        time_human = f"{parallel_seconds:.0f} seconds"
    elif parallel_seconds < 3600:
        time_human = f"{parallel_seconds / 60:.1f} minutes"
    else:
        time_human = f"{parallel_seconds / 3600:.1f} hours"

    # Build agent assignments
    agent_assignments: List[Dict[str, Any]] = []
    for i in range(recommended_agents):
        start = i * docs_per_agent
        end = min(start + docs_per_agent, doc_count)
        if start >= doc_count:
            break
        assigned_docs = [d["filename"] for d in documents[start:end]]
        agent_assignments.append({
            "agent_number": i + 1,
            "document_count": len(assigned_docs),
            "documents": assigned_docs,
        })

    return {
        "estimated_total_seconds": round(total_seconds, 1),
        "estimated_parallel_seconds": round(parallel_seconds, 1),
        "estimated_human": time_human,
        "recommended_agents": recommended_agents,
        "documents_per_agent": docs_per_agent,
        "agent_assignments": agent_assignments,
    }


def run_discovery(args: argparse.Namespace) -> Dict[str, Any]:
    """Run document discovery on the specified directory."""
    directory = os.path.abspath(args.directory)
    file_types = [t.strip().lower().lstrip(".")
                  for t in args.types.split(",")]
    min_size = args.min_size
    max_size = args.max_size if args.max_size and args.max_size > 0 else None

    if not os.path.isdir(directory):
        return {
            "error": True,
            "message": f"Directory not found: {directory}",
        }

    documents = scan_directory(directory, file_types, min_size, max_size)
    statistics = compute_statistics(documents)
    processing = estimate_processing(documents)

    return {
        "discovery_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "directory": directory,
        "file_types": file_types,
        "filters": {
            "min_size": min_size,
            "max_size": max_size,
        },
        "statistics": statistics,
        "processing_estimate": processing,
        "documents": documents,
    }


def format_text(result: Dict[str, Any]) -> str:
    """Format discovery result as human-readable text."""
    if result.get("error"):
        return f"Error: {result['message']}"

    lines = []
    lines.append("=" * 70)
    lines.append("DOCUMENT DISCOVERY REPORT")
    lines.append("=" * 70)
    lines.append(f"Directory:  {result['directory']}")
    lines.append(f"Date:       {result['discovery_date']}")
    lines.append(f"File types: {', '.join(result['file_types'])}")
    lines.append("")

    stats = result["statistics"]
    lines.append(f"Total documents: {stats['total_documents']}")
    lines.append(f"Total size:      {stats['total_size_human']}")
    lines.append(f"Size range:      {stats['size_range']['min']} - {stats['size_range']['max']} "
                 f"(avg: {stats['size_range']['avg']})")
    lines.append("")

    # By type
    if stats["by_type"]:
        lines.append("BY FILE TYPE:")
        lines.append(f"{'Type':<10} {'Count':>8} {'Total Size':>12}")
        lines.append("-" * 32)
        for ext, data in sorted(stats["by_type"].items()):
            lines.append(f".{ext:<9} {data['count']:>8} {data['total_size_human']:>12}")

    # Processing estimate
    proc = result["processing_estimate"]
    lines.append("")
    lines.append("-" * 70)
    lines.append("PROCESSING ESTIMATE")
    lines.append("-" * 70)
    lines.append(f"Estimated time (parallel): {proc['estimated_human']}")
    lines.append(f"Recommended agents:        {proc['recommended_agents']}")
    lines.append(f"Documents per agent:        {proc['documents_per_agent']}")

    if proc.get("agent_assignments"):
        lines.append("")
        lines.append("AGENT ASSIGNMENTS:")
        for assignment in proc["agent_assignments"]:
            lines.append(f"  Agent {assignment['agent_number']}: "
                         f"{assignment['document_count']} documents")
            for doc in assignment["documents"][:5]:
                lines.append(f"    - {doc}")
            if len(assignment["documents"]) > 5:
                lines.append(f"    ... and {len(assignment['documents']) - 5} more")

    # Document list
    lines.append("")
    lines.append("-" * 70)
    lines.append("DOCUMENTS FOUND:")
    lines.append("-" * 70)
    lines.append(f"{'#':<5} {'Filename':<40} {'Type':<6} {'Size':>10} {'Modified'}")
    lines.append("-" * 70)

    for i, doc in enumerate(result["documents"], 1):
        name = doc["filename"]
        if len(name) > 38:
            name = name[:35] + "..."
        lines.append(f"{i:<5} {name:<40} .{doc['extension']:<5} "
                     f"{doc['size_human']:>10} {doc['modified']}")

    lines.append("")
    lines.append("=" * 70)
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scan directory for legal documents and generate inventory manifest."
    )
    parser.add_argument("directory", help="Path to directory containing documents")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--types", default=",".join(DEFAULT_TYPES),
                        help=f"Comma-separated file extensions (default: {','.join(DEFAULT_TYPES)})")
    parser.add_argument("--min-size", type=int, default=0,
                        help="Minimum file size in bytes (default: 0)")
    parser.add_argument("--max-size", type=int, default=0,
                        help="Maximum file size in bytes (default: no limit)")

    args = parser.parse_args()

    try:
        result = run_discovery(args)

        if result.get("error"):
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(f"Error: {result['message']}", file=sys.stderr)
            sys.exit(1)

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(format_text(result))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
