#!/usr/bin/env python3
"""Generate summary reports from CSV or JSON data files.

Produces a structured summary report with key statistics, trends, and
highlights.  Supports markdown and plain-text output.

Usage:
    python report_generator.py --file sales.csv --title "Monthly Sales Report"
    python report_generator.py --file data.json --format markdown --json
    python report_generator.py --file data.csv --group-by region
"""

import argparse
import csv
import json
import math
import os
import sys
from collections import defaultdict
from datetime import datetime


def _is_numeric(value: str) -> bool:
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False


def _median(values: list) -> float:
    s = sorted(values)
    n = len(s)
    if n == 0:
        return 0.0
    mid = n // 2
    return (s[mid - 1] + s[mid]) / 2.0 if n % 2 == 0 else s[mid]


def load_data(file_path: str) -> list:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        with open(file_path, "r", newline="") as f:
            return list(csv.DictReader(f))
    elif ext == ".json":
        with open(file_path, "r") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            raise ValueError("JSON must contain an array of objects.")
    else:
        print(f"Error: Unsupported file type '{ext}'.", file=sys.stderr)
        sys.exit(1)


def _detect_numeric_columns(data: list) -> list:
    if not data:
        return []
    cols = []
    for col in data[0].keys():
        sample = [row.get(col) for row in data[:100] if row.get(col) is not None and str(row.get(col)).strip()]
        if sample and sum(1 for v in sample if _is_numeric(str(v))) > len(sample) * 0.8:
            cols.append(col)
    return cols


def _compute_numeric_summary(data: list, col: str) -> dict:
    values = []
    for row in data:
        v = row.get(col)
        if v is not None and _is_numeric(str(v)):
            values.append(float(str(v)))
    if not values:
        return {}
    total = sum(values)
    mean = total / len(values)
    return {
        "column": col,
        "count": len(values),
        "sum": round(total, 2),
        "mean": round(mean, 2),
        "median": round(_median(values), 2),
        "min": round(min(values), 2),
        "max": round(max(values), 2),
    }


def _compute_group_summary(data: list, group_col: str, numeric_cols: list) -> list:
    groups = defaultdict(list)
    for row in data:
        key = str(row.get(group_col, "Unknown"))
        groups[key].append(row)

    summaries = []
    for group_name, rows in sorted(groups.items()):
        entry = {"group": group_name, "count": len(rows)}
        for col in numeric_cols:
            values = []
            for row in rows:
                v = row.get(col)
                if v is not None and _is_numeric(str(v)):
                    values.append(float(str(v)))
            if values:
                entry[f"{col}_sum"] = round(sum(values), 2)
                entry[f"{col}_mean"] = round(sum(values) / len(values), 2)
        summaries.append(entry)
    return summaries


def generate_report(data: list, title: str, group_by: str = None) -> dict:
    numeric_cols = _detect_numeric_columns(data)

    report = {
        "title": title,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_rows": len(data),
        "total_columns": len(data[0].keys()) if data else 0,
        "numeric_columns": len(numeric_cols),
    }

    # Numeric summaries
    summaries = []
    for col in numeric_cols:
        s = _compute_numeric_summary(data, col)
        if s:
            summaries.append(s)
    report["numeric_summaries"] = summaries

    # Group-by breakdown
    if group_by and data:
        if group_by not in data[0]:
            print(f"Warning: Column '{group_by}' not found. Skipping group-by.", file=sys.stderr)
        else:
            report["group_by"] = group_by
            report["group_summaries"] = _compute_group_summary(data, group_by, numeric_cols)

    # Highlights
    highlights = []
    for s in summaries:
        if s["max"] > s["mean"] * 3 and s["count"] > 10:
            highlights.append(f"{s['column']}: max ({s['max']}) is >3x the mean ({s['mean']}), indicating outliers.")
    if len(data) > 0 and numeric_cols:
        highlights.append(f"Dataset contains {len(data)} rows across {len(data[0].keys())} columns with {len(numeric_cols)} numeric fields.")
    report["highlights"] = highlights

    return report


def format_markdown(report: dict) -> str:
    lines = [f"# {report['title']}", ""]
    lines.append(f"*Generated: {report['generated_at']}*\n")
    lines.append(f"**Rows:** {report['total_rows']} | **Columns:** {report['total_columns']} | **Numeric:** {report['numeric_columns']}\n")

    if report.get("numeric_summaries"):
        lines.append("## Numeric Summaries\n")
        lines.append("| Column | Count | Sum | Mean | Median | Min | Max |")
        lines.append("|--------|-------|-----|------|--------|-----|-----|")
        for s in report["numeric_summaries"]:
            lines.append(f"| {s['column']} | {s['count']} | {s['sum']} | {s['mean']} | {s['median']} | {s['min']} | {s['max']} |")
        lines.append("")

    if report.get("group_summaries"):
        lines.append(f"## Breakdown by {report['group_by']}\n")
        if report["group_summaries"]:
            headers = list(report["group_summaries"][0].keys())
            lines.append("| " + " | ".join(headers) + " |")
            lines.append("|" + "|".join(["---"] * len(headers)) + "|")
            for row in report["group_summaries"]:
                lines.append("| " + " | ".join(str(row.get(h, "")) for h in headers) + " |")
        lines.append("")

    if report.get("highlights"):
        lines.append("## Highlights\n")
        for h in report["highlights"]:
            lines.append(f"- {h}")

    return "\n".join(lines)


def format_text(report: dict) -> str:
    lines = [report["title"], "=" * len(report["title"])]
    lines.append(f"Generated: {report['generated_at']}")
    lines.append(f"Rows: {report['total_rows']}  Columns: {report['total_columns']}  Numeric: {report['numeric_columns']}")
    lines.append("")

    if report.get("numeric_summaries"):
        lines.append("Numeric Summaries:")
        lines.append("-" * 40)
        for s in report["numeric_summaries"]:
            lines.append(f"  {s['column']}: sum={s['sum']}, mean={s['mean']}, median={s['median']}, range=[{s['min']}, {s['max']}]")
        lines.append("")

    if report.get("group_summaries"):
        lines.append(f"Breakdown by {report['group_by']}:")
        lines.append("-" * 40)
        for row in report["group_summaries"]:
            parts = [f"{k}={v}" for k, v in row.items()]
            lines.append(f"  {', '.join(parts)}")
        lines.append("")

    if report.get("highlights"):
        lines.append("Highlights:")
        for h in report["highlights"]:
            lines.append(f"  * {h}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate summary reports from CSV or JSON data.")
    parser.add_argument("--file", required=True, help="Path to CSV or JSON data file")
    parser.add_argument("--title", default="Data Summary Report", help="Report title")
    parser.add_argument("--group-by", help="Column name to group results by")
    parser.add_argument("--format", choices=["text", "markdown"], default="text", help="Output format (default: text)")
    parser.add_argument("--json", action="store_true", help="Output raw report data as JSON")
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    data = load_data(args.file)
    if not data:
        print("Error: No data rows found in file.", file=sys.stderr)
        sys.exit(1)

    report = generate_report(data, args.title, args.group_by)

    if args.json:
        print(json.dumps(report, indent=2))
    elif args.format == "markdown":
        print(format_markdown(report))
    else:
        print(format_text(report))

    sys.exit(0)


if __name__ == "__main__":
    main()
