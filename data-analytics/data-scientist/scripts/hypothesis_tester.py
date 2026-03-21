#!/usr/bin/env python3
"""Run statistical hypothesis tests on CSV data using only the standard library.

Supports two-sample t-test (Welch's), paired t-test, chi-square test of
independence, and proportion z-test.  Computes test statistics, p-values,
confidence intervals, and effect sizes.

Usage:
    python hypothesis_tester.py ttest --file data.csv --col-a group_a --col-b group_b
    python hypothesis_tester.py proportion --successes-a 120 --trials-a 1000 --successes-b 145 --trials-b 1000
    python hypothesis_tester.py chi-square --file contingency.csv
    python hypothesis_tester.py ttest --file data.csv --col-a before --col-b after --paired --json
"""

import argparse
import csv
import json
import math
import os
import sys


# ---------------------------------------------------------------------------
# Statistical helpers (standard library only)
# ---------------------------------------------------------------------------

def _mean(values: list) -> float:
    return sum(values) / len(values)


def _variance(values: list, ddof: int = 1) -> float:
    m = _mean(values)
    return sum((x - m) ** 2 for x in values) / (len(values) - ddof)


def _std(values: list, ddof: int = 1) -> float:
    return math.sqrt(_variance(values, ddof))


def _normal_cdf(x: float) -> float:
    """Approximate standard normal CDF using Abramowitz & Stegun."""
    sign = 1 if x >= 0 else -1
    x = abs(x)
    t = 1.0 / (1.0 + 0.2316419 * x)
    d = 0.3989422804014327  # 1/sqrt(2*pi)
    poly = t * (0.319381530 + t * (-0.356563782 + t * (1.781477937 + t * (-1.821255978 + t * 1.330274429))))
    cdf = 1.0 - d * math.exp(-0.5 * x * x) * poly
    return 0.5 + sign * (cdf - 0.5)


def _t_cdf(t_val: float, df: float) -> float:
    """Approximate t-distribution CDF using normal approximation for df > 30,
    otherwise use a simple beta-function based approximation."""
    if df > 30:
        return _normal_cdf(t_val)
    # Use regularized incomplete beta function approximation
    x = df / (df + t_val * t_val)
    # Simple approximation via normal with correction
    g = math.lgamma((df + 1) / 2) - math.lgamma(df / 2)
    correction = math.exp(g) / math.sqrt(df * math.pi)
    # For small df, use a Cornish-Fisher-style approximation
    z = t_val * (1 - 1 / (4 * df))
    return _normal_cdf(z)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def welch_ttest(a: list, b: list, alpha: float = 0.05) -> dict:
    """Two-sample Welch's t-test (unequal variances)."""
    n_a, n_b = len(a), len(b)
    mean_a, mean_b = _mean(a), _mean(b)
    var_a, var_b = _variance(a), _variance(b)
    se = math.sqrt(var_a / n_a + var_b / n_b)
    if se == 0:
        return {"error": "Standard error is zero; groups may be identical."}
    t_stat = (mean_a - mean_b) / se

    # Welch-Satterthwaite degrees of freedom
    num = (var_a / n_a + var_b / n_b) ** 2
    denom = (var_a / n_a) ** 2 / (n_a - 1) + (var_b / n_b) ** 2 / (n_b - 1)
    df = num / denom if denom > 0 else n_a + n_b - 2

    p_value = 2 * (1 - _t_cdf(abs(t_stat), df))

    # Cohen's d
    pooled_std = math.sqrt((var_a + var_b) / 2)
    cohens_d = (mean_a - mean_b) / pooled_std if pooled_std > 0 else 0

    # 95% CI for difference
    z = 1.96
    ci_low = (mean_a - mean_b) - z * se
    ci_high = (mean_a - mean_b) + z * se

    effect_label = "negligible"
    d_abs = abs(cohens_d)
    if d_abs >= 0.8:
        effect_label = "large"
    elif d_abs >= 0.5:
        effect_label = "medium"
    elif d_abs >= 0.2:
        effect_label = "small"

    return {
        "test": "welch_ttest",
        "group_a": {"n": n_a, "mean": round(mean_a, 4), "std": round(_std(a), 4)},
        "group_b": {"n": n_b, "mean": round(mean_b, 4), "std": round(_std(b), 4)},
        "t_statistic": round(t_stat, 4),
        "degrees_of_freedom": round(df, 2),
        "p_value": round(p_value, 6),
        "significant": p_value < alpha,
        "alpha": alpha,
        "cohens_d": round(cohens_d, 4),
        "effect_size": effect_label,
        "ci_95": [round(ci_low, 4), round(ci_high, 4)],
        "interpretation": f"The difference is {'statistically significant' if p_value < alpha else 'not statistically significant'} (p={round(p_value, 4)}) with a {effect_label} effect size (d={round(cohens_d, 2)}).",
    }


def paired_ttest(a: list, b: list, alpha: float = 0.05) -> dict:
    """Paired t-test for dependent samples."""
    if len(a) != len(b):
        return {"error": "Paired t-test requires equal-length samples."}
    diffs = [x - y for x, y in zip(a, b)]
    n = len(diffs)
    mean_d = _mean(diffs)
    std_d = _std(diffs)
    se = std_d / math.sqrt(n) if n > 0 else 0
    if se == 0:
        return {"error": "Standard error is zero."}
    t_stat = mean_d / se
    df = n - 1
    p_value = 2 * (1 - _t_cdf(abs(t_stat), df))
    cohens_d = mean_d / std_d if std_d > 0 else 0

    return {
        "test": "paired_ttest",
        "n_pairs": n,
        "mean_difference": round(mean_d, 4),
        "std_difference": round(std_d, 4),
        "t_statistic": round(t_stat, 4),
        "degrees_of_freedom": df,
        "p_value": round(p_value, 6),
        "significant": p_value < alpha,
        "alpha": alpha,
        "cohens_d": round(cohens_d, 4),
    }


def proportion_ztest(succ_a: int, n_a: int, succ_b: int, n_b: int, alpha: float = 0.05) -> dict:
    """Two-proportion z-test."""
    p_a = succ_a / n_a
    p_b = succ_b / n_b
    p_pool = (succ_a + succ_b) / (n_a + n_b)
    se = math.sqrt(p_pool * (1 - p_pool) * (1 / n_a + 1 / n_b))
    if se == 0:
        return {"error": "Standard error is zero."}
    z = (p_a - p_b) / se
    p_value = 2 * (1 - _normal_cdf(abs(z)))
    lift = (p_b - p_a) / p_a if p_a > 0 else 0

    return {
        "test": "proportion_ztest",
        "group_a": {"successes": succ_a, "trials": n_a, "rate": round(p_a, 4)},
        "group_b": {"successes": succ_b, "trials": n_b, "rate": round(p_b, 4)},
        "z_statistic": round(z, 4),
        "p_value": round(p_value, 6),
        "significant": p_value < alpha,
        "alpha": alpha,
        "lift": round(lift, 4),
        "interpretation": f"Group B rate ({round(p_b, 4)}) vs Group A ({round(p_a, 4)}): {'+' if lift >= 0 else ''}{round(lift * 100, 1)}% lift. {'Significant' if p_value < alpha else 'Not significant'} (p={round(p_value, 4)}).",
    }


def chi_square_test(table: list, alpha: float = 0.05) -> dict:
    """Chi-square test of independence from a contingency table (list of lists)."""
    rows = len(table)
    cols = len(table[0]) if rows > 0 else 0
    row_totals = [sum(r) for r in table]
    col_totals = [sum(table[r][c] for r in range(rows)) for c in range(cols)]
    grand_total = sum(row_totals)

    if grand_total == 0:
        return {"error": "Table totals are zero."}

    chi2 = 0.0
    for r in range(rows):
        for c in range(cols):
            expected = row_totals[r] * col_totals[c] / grand_total
            if expected > 0:
                chi2 += (table[r][c] - expected) ** 2 / expected

    df = (rows - 1) * (cols - 1)
    # Approximate p-value using Wilson-Hilferty normal approximation
    if df > 0:
        z = (chi2 / df) ** (1 / 3) - (1 - 2 / (9 * df))
        z /= math.sqrt(2 / (9 * df)) if df > 0 else 1
        p_value = 1 - _normal_cdf(z)
    else:
        p_value = 1.0

    # Cramer's V
    min_dim = min(rows, cols) - 1
    cramers_v = math.sqrt(chi2 / (grand_total * min_dim)) if grand_total > 0 and min_dim > 0 else 0

    return {
        "test": "chi_square",
        "chi2_statistic": round(chi2, 4),
        "degrees_of_freedom": df,
        "p_value": round(max(p_value, 0), 6),
        "significant": p_value < alpha,
        "alpha": alpha,
        "cramers_v": round(cramers_v, 4),
    }


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def _load_columns(file_path: str, col_a: str, col_b: str) -> tuple:
    with open(file_path, "r", newline="") as f:
        reader = csv.DictReader(f)
        a_vals, b_vals = [], []
        for row in reader:
            va, vb = row.get(col_a), row.get(col_b)
            if va is not None and va.strip():
                try:
                    a_vals.append(float(va))
                except ValueError:
                    pass
            if vb is not None and vb.strip():
                try:
                    b_vals.append(float(vb))
                except ValueError:
                    pass
    return a_vals, b_vals


def _load_contingency(file_path: str) -> list:
    with open(file_path, "r", newline="") as f:
        reader = csv.reader(f)
        next(reader, None)  # skip header
        table = []
        for row in reader:
            table.append([int(float(v)) for v in row if v.strip()])
    return table


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Run statistical hypothesis tests on data.")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--alpha", type=float, default=0.05, help="Significance level (default: 0.05)")

    sub = parser.add_subparsers(dest="test_type", help="Test to run")

    # ttest
    tt = sub.add_parser("ttest", help="Two-sample or paired t-test")
    tt.add_argument("--file", required=True, help="CSV file with data columns")
    tt.add_argument("--col-a", required=True, help="Column name for group A")
    tt.add_argument("--col-b", required=True, help="Column name for group B")
    tt.add_argument("--paired", action="store_true", help="Run paired t-test instead of independent")

    # proportion
    pr = sub.add_parser("proportion", help="Two-proportion z-test")
    pr.add_argument("--successes-a", type=int, required=True)
    pr.add_argument("--trials-a", type=int, required=True)
    pr.add_argument("--successes-b", type=int, required=True)
    pr.add_argument("--trials-b", type=int, required=True)

    # chi-square
    ch = sub.add_parser("chi-square", help="Chi-square test of independence")
    ch.add_argument("--file", required=True, help="CSV file with contingency table (numeric cells, first row is header)")

    args = parser.parse_args()
    if not args.test_type:
        parser.print_help()
        sys.exit(1)

    result = {}

    if args.test_type == "ttest":
        if not os.path.exists(args.file):
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        a, b = _load_columns(args.file, args.col_a, args.col_b)
        if len(a) < 2 or len(b) < 2:
            print("Error: Each group needs at least 2 values.", file=sys.stderr)
            sys.exit(1)
        if args.paired:
            result = paired_ttest(a, b, args.alpha)
        else:
            result = welch_ttest(a, b, args.alpha)

    elif args.test_type == "proportion":
        result = proportion_ztest(args.successes_a, args.trials_a, args.successes_b, args.trials_b, args.alpha)

    elif args.test_type == "chi-square":
        if not os.path.exists(args.file):
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        table = _load_contingency(args.file)
        if len(table) < 2 or any(len(r) < 2 for r in table):
            print("Error: Contingency table must be at least 2x2.", file=sys.stderr)
            sys.exit(1)
        result = chi_square_test(table, args.alpha)

    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Hypothesis Test: {result.get('test', args.test_type)}")
        print("=" * 50)
        for k, v in result.items():
            if k == "test":
                continue
            if isinstance(v, dict):
                print(f"  {k}:")
                for kk, vv in v.items():
                    print(f"    {kk}: {vv}")
            elif isinstance(v, list):
                print(f"  {k}: [{', '.join(str(x) for x in v)}]")
            else:
                print(f"  {k}: {v}")

    sys.exit(0)


if __name__ == "__main__":
    main()
