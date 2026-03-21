#!/usr/bin/env python3
"""Profile CSV or JSON datasets: column statistics, null rates, cardinality, and outliers.

Reads a data file and computes per-column statistics including count, null
rate, unique values, min/max, mean, median, standard deviation, and
quartiles for numeric columns.  Flags potential quality issues.

Usage:
    python data_profiler.py --file data.csv
    python data_profiler.py --file data.json --json
    python data_profiler.py --file data.csv --top 5
"""

import argparse
import csv
import json
import math
import os
import sys
from collections import Counter


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
    if n % 2 == 0:
        return (s[mid - 1] + s[mid]) / 2.0
    return s[mid]


def _percentile(values: list, p: float) -> float:
    s = sorted(values)
    n = len(s)
    if n == 0:
        return 0.0
    k = (n - 1) * p
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return s[int(k)]
    return s[f] * (c - k) + s[c] * (k - f)


def _std_dev(values: list, mean: float) -> float:
    if len(values) < 2:
        return 0.0
    variance = sum((v - mean) ** 2 for v in values) / (len(values) - 1)
    return math.sqrt(variance)


def load_data(file_path: str) -> list:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        with open(file_path, "r", newline="") as f:
            reader = csv.DictReader(f)
            return list(reader)
    elif ext == ".json":
        with open(file_path, "r") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            raise ValueError("JSON file must contain an array of objects.")
    else:
        print(f"Error: Unsupported file type '{ext}'. Use .csv or .json.", file=sys.stderr)
        sys.exit(1)


def profile_column(name: str, values: list, top_n: int = 5) -> dict:
    total = len(values)
    nulls = sum(1 for v in values if v is None or str(v).strip() == "")
    non_null = [v for v in values if v is not None and str(v).strip() != ""]
    unique = len(set(str(v) for v in non_null))

    profile = {
        "column": name,
        "total_rows": total,
        "null_count": nulls,
        "null_pct": round(nulls / total * 100, 2) if total > 0 else 0.0,
        "unique_values": unique,
        "cardinality_pct": round(unique / total * 100, 2) if total > 0 else 0.0,
    }

    # Check if numeric
    numeric_vals = []
    for v in non_null:
        if _is_numeric(str(v)):
            numeric_vals.append(float(str(v)))

    if len(numeric_vals) > len(non_null) * 0.8 and numeric_vals:
        mean = sum(numeric_vals) / len(numeric_vals)
        std = _std_dev(numeric_vals, mean)
        profile["data_type"] = "numeric"
        profile["min"] = min(numeric_vals)
        profile["max"] = max(numeric_vals)
        profile["mean"] = round(mean, 4)
        profile["median"] = round(_median(numeric_vals), 4)
        profile["std_dev"] = round(std, 4)
        profile["q25"] = round(_percentile(numeric_vals, 0.25), 4)
        profile["q75"] = round(_percentile(numeric_vals, 0.75), 4)
        # Outlier detection (IQR method)
        iqr = profile["q75"] - profile["q25"]
        lower_bound = profile["q25"] - 1.5 * iqr
        upper_bound = profile["q75"] + 1.5 * iqr
        outliers = sum(1 for v in numeric_vals if v < lower_bound or v > upper_bound)
        profile["outlier_count"] = outliers
        profile["outlier_pct"] = round(outliers / len(numeric_vals) * 100, 2)
    else:
        profile["data_type"] = "text"
        str_vals = [str(v) for v in non_null]
        if str_vals:
            lengths = [len(s) for s in str_vals]
            profile["min_length"] = min(lengths)
            profile["max_length"] = max(lengths)
            profile["avg_length"] = round(sum(lengths) / len(lengths), 1)
        # Top values
        counter = Counter(str(v) for v in non_null)
        profile["top_values"] = [
            {"value": val, "count": cnt}
            for val, cnt in counter.most_common(top_n)
        ]

    # Quality flags
    flags = []
    if profile["null_pct"] > 50:
        flags.append("HIGH_NULL_RATE")
    if profile["null_pct"] > 0 and profile["null_pct"] <= 50:
        flags.append("HAS_NULLS")
    if unique == total and total > 1:
        flags.append("POTENTIALLY_UNIQUE_KEY")
    if unique == 1 and total > 1:
        flags.append("CONSTANT_VALUE")
    if profile["data_type"] == "numeric" and profile.get("outlier_pct", 0) > 5:
        flags.append("HIGH_OUTLIER_RATE")
    profile["quality_flags"] = flags

    return profile


def profile_dataset(data: list, top_n: int = 5) -> dict:
    if not data:
        return {"row_count": 0, "column_count": 0, "columns": []}

    columns = list(data[0].keys())
    col_profiles = []
    for col in columns:
        values = [row.get(col) for row in data]
        col_profiles.append(profile_column(col, values, top_n))

    quality_issues = sum(
        1 for p in col_profiles if p["quality_flags"]
    )

    return {
        "row_count": len(data),
        "column_count": len(columns),
        "columns_with_issues": quality_issues,
        "columns": col_profiles,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Profile CSV or JSON datasets with column-level statistics."
    )
    parser.add_argument("--file", required=True, help="Path to CSV or JSON file")
    parser.add_argument("--top", type=int, default=5, help="Number of top values to show for text columns (default: 5)")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    data = load_data(args.file)
    result = profile_dataset(data, args.top)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("Data Profile Report")
        print("=" * 60)
        print(f"Rows: {result['row_count']}  |  Columns: {result['column_count']}  |  Columns with issues: {result['columns_with_issues']}")
        print()
        for col in result["columns"]:
            print(f"--- {col['column']} ({col['data_type']}) ---")
            print(f"  Nulls: {col['null_count']} ({col['null_pct']}%)  |  Unique: {col['unique_values']} ({col['cardinality_pct']}%)")
            if col["data_type"] == "numeric":
                print(f"  Min: {col['min']}  Max: {col['max']}  Mean: {col['mean']}  Median: {col['median']}")
                print(f"  Std: {col['std_dev']}  Q25: {col['q25']}  Q75: {col['q75']}")
                if col.get("outlier_count", 0) > 0:
                    print(f"  Outliers: {col['outlier_count']} ({col['outlier_pct']}%)")
            else:
                if "min_length" in col:
                    print(f"  Length: min={col['min_length']}  max={col['max_length']}  avg={col['avg_length']}")
                if col.get("top_values"):
                    top_str = ", ".join(f"{t['value']} ({t['count']})" for t in col["top_values"][:3])
                    print(f"  Top: {top_str}")
            if col["quality_flags"]:
                print(f"  Flags: {', '.join(col['quality_flags'])}")
            print()

    sys.exit(0)


if __name__ == "__main__":
    main()
