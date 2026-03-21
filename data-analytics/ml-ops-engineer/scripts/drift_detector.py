#!/usr/bin/env python3
"""Detect data and model drift by comparing reference and current distributions.

Reads two CSV files (reference/baseline and current/production) and
computes distribution shift per feature using statistical tests.  Reports
drift scores, flags drifted features, and suggests remediation.

Usage:
    python drift_detector.py --reference train_data.csv --current prod_data.csv
    python drift_detector.py --reference baseline.csv --current latest.csv --threshold 0.1 --json
    python drift_detector.py --reference ref.csv --current cur.csv --columns feature_1 feature_2 feature_3
"""

import argparse
import csv
import json
import math
import os
import sys
from collections import Counter


# ---------------------------------------------------------------------------
# Statistical helpers (standard library only)
# ---------------------------------------------------------------------------

def _is_numeric(value: str) -> bool:
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False


def _to_floats(values: list) -> list:
    return [float(v) for v in values if _is_numeric(str(v)) and str(v).strip()]


def _mean(vals: list) -> float:
    return sum(vals) / len(vals) if vals else 0.0


def _std(vals: list) -> float:
    if len(vals) < 2:
        return 0.0
    m = _mean(vals)
    return math.sqrt(sum((x - m) ** 2 for x in vals) / (len(vals) - 1))


def _ks_statistic(ref: list, cur: list) -> float:
    """Approximate Kolmogorov-Smirnov statistic for two samples."""
    all_vals = sorted(set(ref + cur))
    if not all_vals:
        return 0.0

    n_ref, n_cur = len(ref), len(cur)
    if n_ref == 0 or n_cur == 0:
        return 0.0

    ref_sorted = sorted(ref)
    cur_sorted = sorted(cur)

    max_diff = 0.0
    i, j = 0, 0
    for val in all_vals:
        while i < n_ref and ref_sorted[i] <= val:
            i += 1
        while j < n_cur and cur_sorted[j] <= val:
            j += 1
        diff = abs(i / n_ref - j / n_cur)
        if diff > max_diff:
            max_diff = diff

    return max_diff


def _psi(ref: list, cur: list, bins: int = 10) -> float:
    """Population Stability Index for numeric features."""
    if not ref or not cur:
        return 0.0

    all_vals = ref + cur
    mn, mx = min(all_vals), max(all_vals)
    if mn == mx:
        return 0.0

    step = (mx - mn) / bins
    epsilon = 1e-6

    def _bin_counts(vals):
        counts = [0] * bins
        for v in vals:
            idx = min(int((v - mn) / step), bins - 1)
            counts[idx] += 1
        total = len(vals)
        return [(c / total) + epsilon for c in counts]

    ref_pcts = _bin_counts(ref)
    cur_pcts = _bin_counts(cur)

    psi_val = 0.0
    for r, c in zip(ref_pcts, cur_pcts):
        psi_val += (c - r) * math.log(c / r)

    return psi_val


def _chi_square_categorical(ref: list, cur: list) -> float:
    """Chi-square divergence for categorical features."""
    ref_counts = Counter(ref)
    cur_counts = Counter(cur)
    all_keys = set(ref_counts.keys()) | set(cur_counts.keys())

    n_ref, n_cur = len(ref), len(cur)
    if n_ref == 0 or n_cur == 0:
        return 0.0

    chi2 = 0.0
    for key in all_keys:
        expected = ref_counts.get(key, 0) / n_ref
        observed = cur_counts.get(key, 0) / n_cur
        if expected > 0:
            chi2 += (observed - expected) ** 2 / expected

    return chi2


# ---------------------------------------------------------------------------
# Drift analysis
# ---------------------------------------------------------------------------

def analyze_feature(name: str, ref_values: list, cur_values: list, threshold: float) -> dict:
    ref_non_null = [v for v in ref_values if v is not None and str(v).strip()]
    cur_non_null = [v for v in cur_values if v is not None and str(v).strip()]

    ref_numeric = _to_floats(ref_non_null)
    cur_numeric = _to_floats(cur_non_null)
    is_numeric = (len(ref_numeric) > len(ref_non_null) * 0.8) if ref_non_null else False

    result = {
        "feature": name,
        "data_type": "numeric" if is_numeric else "categorical",
        "ref_count": len(ref_non_null),
        "cur_count": len(cur_non_null),
    }

    if is_numeric and ref_numeric and cur_numeric:
        result["ref_mean"] = round(_mean(ref_numeric), 4)
        result["cur_mean"] = round(_mean(cur_numeric), 4)
        result["ref_std"] = round(_std(ref_numeric), 4)
        result["cur_std"] = round(_std(cur_numeric), 4)
        result["mean_shift"] = round(result["cur_mean"] - result["ref_mean"], 4)

        ks = _ks_statistic(ref_numeric, cur_numeric)
        psi = _psi(ref_numeric, cur_numeric)

        result["ks_statistic"] = round(ks, 4)
        result["psi"] = round(psi, 4)
        result["drift_score"] = round(max(ks, psi), 4)
        result["is_drifted"] = result["drift_score"] > threshold

        # PSI interpretation
        if psi < 0.1:
            result["psi_interpretation"] = "stable"
        elif psi < 0.2:
            result["psi_interpretation"] = "moderate_shift"
        else:
            result["psi_interpretation"] = "significant_shift"
    else:
        chi2 = _chi_square_categorical(ref_non_null, cur_non_null)
        result["chi_square"] = round(chi2, 4)
        result["drift_score"] = round(chi2, 4)
        result["is_drifted"] = chi2 > threshold

        # Check for new categories
        ref_cats = set(ref_non_null)
        cur_cats = set(cur_non_null)
        new_cats = cur_cats - ref_cats
        missing_cats = ref_cats - cur_cats
        if new_cats:
            result["new_categories"] = list(new_cats)[:10]
        if missing_cats:
            result["missing_categories"] = list(missing_cats)[:10]

    if result["is_drifted"]:
        if is_numeric:
            result["recommendation"] = "Investigate distribution shift; consider retraining if model performance degrades."
        else:
            result["recommendation"] = "New/missing categories detected; update encoding and retrain."

    return result


def detect_drift(ref_data: list, cur_data: list, columns: list = None, threshold: float = 0.1) -> dict:
    if columns is None:
        columns = list(ref_data[0].keys()) if ref_data else []

    results = []
    for col in columns:
        ref_vals = [row.get(col) for row in ref_data]
        cur_vals = [row.get(col) for row in cur_data]
        results.append(analyze_feature(col, ref_vals, cur_vals, threshold))

    drifted = [r for r in results if r["is_drifted"]]
    results.sort(key=lambda x: x["drift_score"], reverse=True)

    return {
        "total_features": len(results),
        "drifted_features": len(drifted),
        "drift_rate": round(len(drifted) / len(results) * 100, 1) if results else 0,
        "threshold": threshold,
        "alert": len(drifted) > len(results) * 0.3,
        "alert_message": f"{len(drifted)}/{len(results)} features drifted (>{threshold} threshold). Consider model retraining." if len(drifted) > len(results) * 0.3 else "",
        "features": results,
    }


def main():
    parser = argparse.ArgumentParser(description="Detect data and model drift between reference and current datasets.")
    parser.add_argument("--reference", required=True, help="Path to reference/baseline CSV file")
    parser.add_argument("--current", required=True, help="Path to current/production CSV file")
    parser.add_argument("--columns", nargs="*", help="Specific columns to check (default: all)")
    parser.add_argument("--threshold", type=float, default=0.1, help="Drift threshold (default: 0.1)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    for path, label in [(args.reference, "Reference"), (args.current, "Current")]:
        if not os.path.exists(path):
            print(f"Error: {label} file not found: {path}", file=sys.stderr)
            sys.exit(1)

    with open(args.reference, "r", newline="") as f:
        ref_data = list(csv.DictReader(f))
    with open(args.current, "r", newline="") as f:
        cur_data = list(csv.DictReader(f))

    if not ref_data or not cur_data:
        print("Error: Both files must contain data rows.", file=sys.stderr)
        sys.exit(1)

    result = detect_drift(ref_data, cur_data, args.columns, args.threshold)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("Drift Detection Report")
        print("=" * 65)
        alert_str = " [ALERT]" if result["alert"] else ""
        print(f"Features: {result['total_features']}  |  Drifted: {result['drifted_features']} ({result['drift_rate']}%)  |  Threshold: {result['threshold']}{alert_str}")
        if result["alert_message"]:
            print(f"\n  {result['alert_message']}")
        print()
        print(f"{'Feature':<25} {'Type':<12} {'Drift Score':>12} {'Drifted':<8}")
        print("-" * 65)
        for f in result["features"]:
            marker = "[!!]" if f["is_drifted"] else "[ ]"
            print(f"  {f['feature']:<23} {f['data_type']:<12} {f['drift_score']:>12.4f} {marker}")
            if f.get("recommendation"):
                print(f"    -> {f['recommendation']}")

    sys.exit(1 if result["alert"] else 0)


if __name__ == "__main__":
    main()
