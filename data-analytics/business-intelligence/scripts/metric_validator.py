#!/usr/bin/env python3
"""Validate metric definitions for consistency, completeness, and correctness.

Reads a metric definitions file (JSON) and checks for common issues:
missing fields, conflicting aggregations, naming violations, undefined
dimensions, and threshold logic errors.

Usage:
    python metric_validator.py --definitions metrics.json
    python metric_validator.py --definitions metrics.json --strict --json

Metric definition format:
[
    {
        "name": "Monthly Revenue",
        "formula": "SUM(amount)",
        "data_source": "orders",
        "column": "amount",
        "aggregation": "sum",
        "owner": "Finance",
        "dimensions": ["region", "product_line"],
        "target": 100000,
        "warning_pct": 0.9,
        "critical_pct": 0.8,
        "higher_is_better": true,
        "granularity": "monthly"
    }
]
"""

import argparse
import json
import os
import re
import sys


# ---------------------------------------------------------------------------
# Validation rules
# ---------------------------------------------------------------------------

REQUIRED_FIELDS = ["name", "aggregation", "data_source"]
RECOMMENDED_FIELDS = ["owner", "formula", "granularity", "dimensions"]
VALID_AGGREGATIONS = {"sum", "mean", "average", "count", "count_distinct", "min", "max", "median", "ratio", "rate"}
VALID_GRANULARITIES = {"daily", "weekly", "monthly", "quarterly", "yearly", "hourly", "real_time"}
NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9 _-]{2,60}$")


def _validate_metric(metric: dict, index: int, strict: bool = False) -> list:
    issues = []
    prefix = f"Metric #{index + 1}"
    name = metric.get("name", f"(unnamed #{index + 1})")

    # Required fields
    for field in REQUIRED_FIELDS:
        if not metric.get(field):
            issues.append({
                "metric": name,
                "severity": "error",
                "rule": "MISSING_REQUIRED_FIELD",
                "message": f"Missing required field '{field}'.",
            })

    # Recommended fields
    if strict:
        for field in RECOMMENDED_FIELDS:
            if not metric.get(field):
                issues.append({
                    "metric": name,
                    "severity": "warning",
                    "rule": "MISSING_RECOMMENDED_FIELD",
                    "message": f"Missing recommended field '{field}'.",
                })

    # Name format
    if metric.get("name") and not NAME_PATTERN.match(metric["name"]):
        issues.append({
            "metric": name,
            "severity": "warning",
            "rule": "INVALID_NAME_FORMAT",
            "message": "Metric name should be 3-60 chars, start with a letter, and use only alphanumeric, spaces, hyphens, or underscores.",
        })

    # Aggregation
    agg = metric.get("aggregation", "").lower()
    if agg and agg not in VALID_AGGREGATIONS:
        issues.append({
            "metric": name,
            "severity": "error",
            "rule": "INVALID_AGGREGATION",
            "message": f"Aggregation '{agg}' is not recognized. Valid: {', '.join(sorted(VALID_AGGREGATIONS))}.",
        })

    # Granularity
    gran = metric.get("granularity", "").lower()
    if gran and gran not in VALID_GRANULARITIES:
        issues.append({
            "metric": name,
            "severity": "warning",
            "rule": "INVALID_GRANULARITY",
            "message": f"Granularity '{gran}' is not standard. Valid: {', '.join(sorted(VALID_GRANULARITIES))}.",
        })

    # Threshold logic
    target = metric.get("target")
    warning_pct = metric.get("warning_pct")
    critical_pct = metric.get("critical_pct")
    higher = metric.get("higher_is_better", True)

    if target is not None:
        if warning_pct is not None and critical_pct is not None:
            if higher:
                if warning_pct <= critical_pct:
                    issues.append({
                        "metric": name,
                        "severity": "error",
                        "rule": "THRESHOLD_ORDER",
                        "message": f"warning_pct ({warning_pct}) should be > critical_pct ({critical_pct}) when higher_is_better=true.",
                    })
            if warning_pct is not None and (warning_pct <= 0 or warning_pct > 1):
                issues.append({
                    "metric": name,
                    "severity": "error",
                    "rule": "THRESHOLD_RANGE",
                    "message": f"warning_pct ({warning_pct}) must be between 0 and 1.",
                })
            if critical_pct is not None and (critical_pct <= 0 or critical_pct > 1):
                issues.append({
                    "metric": name,
                    "severity": "error",
                    "rule": "THRESHOLD_RANGE",
                    "message": f"critical_pct ({critical_pct}) must be between 0 and 1.",
                })

    # Dimensions validation
    dims = metric.get("dimensions", [])
    if not isinstance(dims, list):
        issues.append({
            "metric": name,
            "severity": "error",
            "rule": "INVALID_DIMENSIONS",
            "message": "Dimensions must be a list.",
        })
    elif len(dims) > 10:
        issues.append({
            "metric": name,
            "severity": "warning",
            "rule": "EXCESSIVE_DIMENSIONS",
            "message": f"Metric has {len(dims)} dimensions; consider limiting to <=10 for dashboard usability.",
        })

    # Formula vs aggregation consistency
    formula = metric.get("formula", "").upper()
    if formula and agg:
        expected_agg = None
        if formula.startswith("SUM("):
            expected_agg = "sum"
        elif formula.startswith("AVG(") or formula.startswith("AVERAGE("):
            expected_agg = "mean"
        elif formula.startswith("COUNT(DISTINCT"):
            expected_agg = "count_distinct"
        elif formula.startswith("COUNT("):
            expected_agg = "count"
        if expected_agg and expected_agg != agg:
            issues.append({
                "metric": name,
                "severity": "warning",
                "rule": "FORMULA_AGG_MISMATCH",
                "message": f"Formula suggests '{expected_agg}' but aggregation is set to '{agg}'.",
            })

    return issues


def validate_all(metrics: list, strict: bool = False) -> dict:
    all_issues = []
    for i, m in enumerate(metrics):
        all_issues.extend(_validate_metric(m, i, strict))

    # Cross-metric checks: duplicate names
    names = [m.get("name", "") for m in metrics]
    seen = set()
    for n in names:
        if n in seen:
            all_issues.append({
                "metric": n,
                "severity": "error",
                "rule": "DUPLICATE_NAME",
                "message": f"Metric name '{n}' appears more than once.",
            })
        seen.add(n)

    errors = sum(1 for i in all_issues if i["severity"] == "error")
    warnings = sum(1 for i in all_issues if i["severity"] == "warning")

    return {
        "total_metrics": len(metrics),
        "total_issues": len(all_issues),
        "errors": errors,
        "warnings": warnings,
        "valid": errors == 0,
        "issues": all_issues,
    }


def main():
    parser = argparse.ArgumentParser(description="Validate metric definitions for consistency and completeness.")
    parser.add_argument("--definitions", required=True, help="Path to metric definitions JSON file")
    parser.add_argument("--strict", action="store_true", help="Enable strict mode (flag missing recommended fields)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if not os.path.exists(args.definitions):
        print(f"Error: File not found: {args.definitions}", file=sys.stderr)
        sys.exit(1)

    with open(args.definitions, "r") as f:
        metrics = json.load(f)

    if not isinstance(metrics, list):
        print("Error: Definitions must be a JSON array.", file=sys.stderr)
        sys.exit(1)

    result = validate_all(metrics, args.strict)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("Metric Validation Report")
        print("=" * 55)
        status = "PASS" if result["valid"] else "FAIL"
        print(f"Status: [{status}]  |  Metrics: {result['total_metrics']}  |  Errors: {result['errors']}  Warnings: {result['warnings']}")
        print()

        if not result["issues"]:
            print("All metric definitions are valid.")
        else:
            for issue in result["issues"]:
                sev = issue["severity"].upper()
                print(f"  [{sev}] {issue['metric']}: {issue['rule']}")
                print(f"    {issue['message']}")

    sys.exit(1 if result["errors"] > 0 else 0)


if __name__ == "__main__":
    main()
