#!/usr/bin/env python3
"""
Extraction Aggregator

Takes multiple extraction result JSONs (from parallel processing agents)
and aggregates into a unified comparison matrix with conflict detection,
confidence scoring, and summary statistics.

Usage:
    python extraction_aggregator.py --results extract_1.json extract_2.json
    python extraction_aggregator.py --results-dir ./results/ --json
    python extraction_aggregator.py --results-dir ./results/ --format markdown --output matrix.md
"""

import argparse
import glob
import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


# Expected extraction result JSON schema:
# {
#   "agent_id": "agent_1",
#   "documents": [
#     {
#       "filename": "contract_a.pdf",
#       "extractions": {
#         "Column Name": {
#           "value": "extracted value",
#           "citation": "p.3, Section 2.1",
#           "confidence": "HIGH"  // HIGH, MEDIUM, LOW
#         }
#       }
#     }
#   ]
# }


CONFIDENCE_LEVELS = {"HIGH": 3, "MEDIUM": 2, "LOW": 1, "NOT_FOUND": 0}


def load_result_file(filepath: str) -> Optional[Dict[str, Any]]:
    """Load a single extraction result JSON file."""
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        return None


def load_results(file_paths: List[str] = None,
                 results_dir: str = None) -> Tuple[List[Dict], List[str]]:
    """Load all extraction results from files or directory."""
    results: List[Dict] = []
    errors: List[str] = []

    paths_to_load: List[str] = []

    if file_paths:
        paths_to_load.extend(file_paths)

    if results_dir:
        if os.path.isdir(results_dir):
            json_files = sorted(glob.glob(os.path.join(results_dir, "*.json")))
            paths_to_load.extend(json_files)
        else:
            errors.append(f"Directory not found: {results_dir}")

    for path in paths_to_load:
        data = load_result_file(path)
        if data is None:
            errors.append(f"Failed to load: {path}")
        else:
            # Handle both single-document and multi-document formats
            if "documents" in data:
                results.append(data)
            elif "filename" in data and "extractions" in data:
                # Single document wrapped in expected format
                results.append({
                    "agent_id": os.path.basename(path),
                    "documents": [data],
                })
            else:
                errors.append(f"Unexpected format: {path}")

    return results, errors


def aggregate_results(
    results: List[Dict[str, Any]],
    column_filter: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Aggregate extraction results into unified matrix."""

    # Collect all documents and columns
    doc_data: Dict[str, Dict[str, Dict[str, Any]]] = {}  # filename -> column -> extraction
    all_columns: List[str] = []
    column_set: set = set()
    conflicts: List[Dict[str, Any]] = []
    total_extractions = 0
    confidence_counts: Dict[str, int] = {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "NOT_FOUND": 0}

    for result in results:
        agent_id = result.get("agent_id", "unknown")
        for doc in result.get("documents", []):
            filename = doc.get("filename", "unknown")

            if filename not in doc_data:
                doc_data[filename] = {}

            for col_name, extraction in doc.get("extractions", {}).items():
                # Apply column filter
                if column_filter and col_name not in column_filter:
                    continue

                if col_name not in column_set:
                    column_set.add(col_name)
                    all_columns.append(col_name)

                total_extractions += 1

                value = extraction.get("value", "NOT FOUND")
                citation = extraction.get("citation", "")
                confidence = extraction.get("confidence", "LOW").upper()

                if confidence not in CONFIDENCE_LEVELS:
                    confidence = "LOW"

                confidence_counts[confidence] = confidence_counts.get(confidence, 0) + 1

                # Check for conflicts (same document, same column, different value)
                if col_name in doc_data[filename]:
                    existing = doc_data[filename][col_name]
                    if existing["value"] != value and value != "NOT FOUND":
                        conflicts.append({
                            "document": filename,
                            "column": col_name,
                            "existing_value": existing["value"],
                            "new_value": value,
                            "existing_agent": existing.get("agent_id", "unknown"),
                            "new_agent": agent_id,
                        })
                        # Keep higher confidence value
                        if CONFIDENCE_LEVELS.get(confidence, 0) > CONFIDENCE_LEVELS.get(
                                existing["confidence"], 0):
                            doc_data[filename][col_name] = {
                                "value": value,
                                "citation": citation,
                                "confidence": confidence,
                                "agent_id": agent_id,
                                "conflict": True,
                            }
                    continue

                doc_data[filename][col_name] = {
                    "value": value,
                    "citation": citation,
                    "confidence": confidence,
                    "agent_id": agent_id,
                    "conflict": False,
                }

    # Apply column filter ordering if specified
    if column_filter:
        all_columns = [c for c in column_filter if c in column_set]

    # Build matrix rows
    matrix_rows: List[Dict[str, Any]] = []
    not_found_count = 0
    total_cells = 0

    for filename in sorted(doc_data.keys()):
        row: Dict[str, Any] = {"document": filename, "columns": {}}
        for col in all_columns:
            total_cells += 1
            if col in doc_data[filename]:
                extraction = doc_data[filename][col]
                row["columns"][col] = extraction
                if extraction["value"] == "NOT FOUND":
                    not_found_count += 1
            else:
                row["columns"][col] = {
                    "value": "NOT FOUND",
                    "citation": "",
                    "confidence": "NOT_FOUND",
                    "conflict": False,
                }
                not_found_count += 1

        matrix_rows.append(row)

    # Summary statistics
    extraction_coverage = {}
    for col in all_columns:
        found = sum(1 for row in matrix_rows
                    if row["columns"].get(col, {}).get("value", "NOT FOUND") != "NOT FOUND")
        extraction_coverage[col] = {
            "found": found,
            "total": len(matrix_rows),
            "coverage_pct": round((found / len(matrix_rows)) * 100, 1) if matrix_rows else 0,
        }

    high_count = confidence_counts.get("HIGH", 0)
    med_count = confidence_counts.get("MEDIUM", 0)
    total_with_value = high_count + med_count + confidence_counts.get("LOW", 0)
    avg_confidence_pct = round(
        ((high_count * 100 + med_count * 66 + confidence_counts.get("LOW", 0) * 33)
         / total_with_value) if total_with_value > 0 else 0, 1
    )

    return {
        "aggregation_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "documents_processed": len(matrix_rows),
        "columns": all_columns,
        "column_count": len(all_columns),
        "total_cells": total_cells,
        "total_extractions": total_extractions,
        "not_found_count": not_found_count,
        "not_found_rate_pct": round((not_found_count / total_cells) * 100, 1) if total_cells else 0,
        "average_confidence_pct": avg_confidence_pct,
        "confidence_distribution": confidence_counts,
        "conflicts": conflicts,
        "conflict_count": len(conflicts),
        "extraction_coverage": extraction_coverage,
        "matrix": matrix_rows,
    }


def format_markdown(result: Dict[str, Any]) -> str:
    """Format aggregated result as markdown table."""
    lines = []
    lines.append("# Document Review Matrix")
    lines.append("")
    lines.append(f"Generated: {result['aggregation_date']}")
    lines.append(f"Documents: {result['documents_processed']} | "
                 f"Columns: {result['column_count']} | "
                 f"Avg Confidence: {result['average_confidence_pct']}%")
    lines.append("")

    columns = result["columns"]
    if not columns or not result["matrix"]:
        lines.append("*No data to display.*")
        return "\n".join(lines)

    # Header
    header = "| Document |"
    separator = "|----------|"
    for col in columns:
        col_display = col[:20] if len(col) > 20 else col
        header += f" {col_display} |"
        separator += f"{'---' * max(1, len(col_display) // 3 + 1)}|"
    lines.append(header)
    lines.append(separator)

    # Rows
    for row in result["matrix"]:
        doc_name = row["document"]
        if len(doc_name) > 25:
            doc_name = doc_name[:22] + "..."
        line = f"| {doc_name} |"
        for col in columns:
            cell = row["columns"].get(col, {})
            value = cell.get("value", "NOT FOUND")
            citation = cell.get("citation", "")
            confidence = cell.get("confidence", "NOT_FOUND")

            if value == "NOT FOUND":
                display = "*Not found*"
            else:
                # Truncate long values
                if len(str(value)) > 30:
                    value = str(value)[:27] + "..."
                if citation:
                    display = f"{value} [{citation}]"
                else:
                    display = str(value)

            line += f" {display} |"
        lines.append(line)

    # Summary section
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Documents processed | {result['documents_processed']} |")
    lines.append(f"| Columns extracted | {result['column_count']} |")
    lines.append(f"| Average confidence | {result['average_confidence_pct']}% |")
    lines.append(f"| Not found rate | {result['not_found_rate_pct']}% |")
    lines.append(f"| Conflicts detected | {result['conflict_count']} |")

    # Coverage per column
    lines.append("")
    lines.append("## Column Coverage")
    lines.append("")
    lines.append("| Column | Found | Total | Coverage |")
    lines.append("|--------|-------|-------|----------|")
    for col, cov in result["extraction_coverage"].items():
        lines.append(f"| {col} | {cov['found']} | {cov['total']} | {cov['coverage_pct']}% |")

    # Conflicts
    if result["conflicts"]:
        lines.append("")
        lines.append("## Conflicts (Requires Manual Review)")
        lines.append("")
        lines.append("| Document | Column | Value 1 | Value 2 |")
        lines.append("|----------|--------|---------|---------|")
        for conflict in result["conflicts"]:
            lines.append(f"| {conflict['document']} | {conflict['column']} | "
                         f"{conflict['existing_value']} | {conflict['new_value']} |")

    return "\n".join(lines)


def format_text(result: Dict[str, Any]) -> str:
    """Format as plain text summary."""
    lines = []
    lines.append("=" * 70)
    lines.append("EXTRACTION AGGREGATION REPORT")
    lines.append("=" * 70)
    lines.append(f"Date:               {result['aggregation_date']}")
    lines.append(f"Documents:          {result['documents_processed']}")
    lines.append(f"Columns:            {result['column_count']}")
    lines.append(f"Total cells:        {result['total_cells']}")
    lines.append(f"Avg confidence:     {result['average_confidence_pct']}%")
    lines.append(f"Not found rate:     {result['not_found_rate_pct']}%")
    lines.append(f"Conflicts:          {result['conflict_count']}")
    lines.append("")

    dist = result["confidence_distribution"]
    lines.append("CONFIDENCE DISTRIBUTION:")
    lines.append(f"  HIGH:      {dist.get('HIGH', 0)}")
    lines.append(f"  MEDIUM:    {dist.get('MEDIUM', 0)}")
    lines.append(f"  LOW:       {dist.get('LOW', 0)}")
    lines.append(f"  NOT FOUND: {dist.get('NOT_FOUND', 0)}")

    if result.get("conflicts"):
        lines.append("")
        lines.append("CONFLICTS (Requires Manual Review):")
        for c in result["conflicts"]:
            lines.append(f"  {c['document']} / {c['column']}: "
                         f"'{c['existing_value']}' vs '{c['new_value']}'")

    lines.append("")
    lines.append("=" * 70)
    lines.append("Use --format markdown for full matrix output.")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Aggregate extraction results into unified comparison matrix."
    )
    parser.add_argument("--json", action="store_true",
                        help="Output in JSON format")
    parser.add_argument("--results", nargs="+", default=None,
                        help="One or more extraction result JSON files")
    parser.add_argument("--results-dir", default=None,
                        help="Directory containing extraction result JSON files")
    parser.add_argument("--format", choices=["markdown", "json"], default=None,
                        help="Output format (default: text summary)")
    parser.add_argument("--columns", default=None,
                        help="Comma-separated column names to include")
    parser.add_argument("--output", default=None,
                        help="Write output to file instead of stdout")

    args = parser.parse_args()

    if not args.results and not args.results_dir:
        parser.error("Must specify --results or --results-dir")

    try:
        results, errors = load_results(args.results, args.results_dir)

        if errors:
            for err in errors:
                print(f"Warning: {err}", file=sys.stderr)

        if not results:
            print("Error: No valid extraction results loaded.", file=sys.stderr)
            sys.exit(1)

        column_filter = None
        if args.columns:
            column_filter = [c.strip() for c in args.columns.split(",")]

        aggregated = aggregate_results(results, column_filter)

        # Determine output format
        output_format = args.format
        if args.json:
            output_format = "json"

        if output_format == "json":
            output_text = json.dumps(aggregated, indent=2)
        elif output_format == "markdown":
            output_text = format_markdown(aggregated)
        else:
            output_text = format_text(aggregated)

        if args.output:
            with open(args.output, "w") as f:
                f.write(output_text)
            print(f"Output written to {args.output} "
                  f"({aggregated['documents_processed']} documents, "
                  f"{aggregated['column_count']} columns)")
        else:
            print(output_text)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
