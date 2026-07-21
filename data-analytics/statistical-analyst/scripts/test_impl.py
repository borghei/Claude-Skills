#!/usr/bin/env python3
"""Statistical test implementations used by run_test.py.

Holds the four core tests — two-proportion z, Welch's t, chi-square of
independence, and Mann-Whitney U — plus the effect-size magnitude readings.
Each returns a plain result dict; the significance verdict, formatting, and CLI
live in run_test.py. Distributions come from stats_core.py in this directory.

Usage:
    python3 test_impl.py --selftest
"""

import argparse
import json
import math
import statistics
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stats_core import chi2_sf, norm_sf, t_crit, t_sf, wilson  # noqa: E402

Z_CRIT = {0.10: 1.644854, 0.05: 1.959964, 0.01: 2.575829}

# Cutoffs separating negligible / small / medium / large, per effect-size family.
COHEN_CUTS = (0.2, 0.5, 0.8)          # Cohen's h and d (and Hedges' g)
CORRELATION_CUTS = (0.1, 0.3, 0.5)    # Cramer's V and rank-biserial r


def magnitude(value: float, cuts: Tuple[float, float, float]) -> str:
    """Translate an effect size into a plain-language magnitude for its family."""
    if value < cuts[0]:
        return "negligible"
    return "small" if value < cuts[1] else ("medium" if value < cuts[2] else "large")


def two_proportion(data: Dict[str, Any], alpha: float) -> Dict[str, Any]:
    """Two-proportion z test with Cohen's h and a Newcombe difference interval."""
    groups = data["groups"]
    (n1_label, g1), (n2_label, g2) = list(groups.items())[:2]
    x1, n1 = int(g1["successes"]), int(g1["trials"])
    x2, n2 = int(g2["successes"]), int(g2["trials"])
    if min(n1, n2) == 0:
        raise ValueError("both groups need trials > 0")
    p1, p2 = x1 / n1, x2 / n2
    pooled = (x1 + x2) / (n1 + n2)
    se = math.sqrt(pooled * (1 - pooled) * (1 / n1 + 1 / n2))
    z = (p2 - p1) / se if se else 0.0
    p_value = 2 * norm_sf(abs(z))
    zc = Z_CRIT.get(alpha, 1.959964)
    l1, u1 = wilson(x1, n1, zc)
    l2, u2 = wilson(x2, n2, zc)
    lower = (p2 - p1) - math.sqrt((p2 - l2) ** 2 + (u1 - p1) ** 2)
    upper = (p2 - p1) + math.sqrt((u2 - p2) ** 2 + (p1 - l1) ** 2)
    h = 2 * math.asin(math.sqrt(p2)) - 2 * math.asin(math.sqrt(p1))
    warnings: List[str] = []
    for label, succ, n in ((n1_label, x1, n1), (n2_label, x2, n2)):
        if succ < 5 or n - succ < 5:
            warnings.append(
                f"{label} has fewer than 5 events or non-events; the normal "
                "approximation is unreliable — use an exact test.")
    return {
        "test": "two-proportion z", "groups": [n1_label, n2_label],
        "rate_baseline": round(p1, 6), "rate_variant": round(p2, 6),
        "absolute_difference": round(p2 - p1, 6),
        "relative_lift": round((p2 - p1) / p1, 6) if p1 else None,
        "statistic": round(z, 4), "p_value": round(p_value, 6),
        "effect_size": {"name": "Cohen's h", "value": round(h, 4),
                        "reading": magnitude(abs(h), COHEN_CUTS)},
        "ci": [round(lower, 6), round(upper, 6)],
        "ci_method": "Newcombe hybrid score",
        "warnings": warnings,
    }


def welch_t(data: Dict[str, Any], alpha: float) -> Dict[str, Any]:
    """Welch's unequal-variance t test with Hedges' g and a mean-difference CI."""
    groups = data["groups"]
    (a_label, a), (b_label, b) = list(groups.items())[:2]
    a, b = [float(v) for v in a], [float(v) for v in b]
    if len(a) < 2 or len(b) < 2:
        raise ValueError("each group needs at least 2 observations")
    n1, n2 = len(a), len(b)
    m1, m2 = statistics.fmean(a), statistics.fmean(b)
    v1, v2 = statistics.variance(a), statistics.variance(b)
    se = math.sqrt(v1 / n1 + v2 / n2)
    if se == 0:
        raise ValueError("zero variance in both groups; a t test is undefined")
    t = (m2 - m1) / se
    df = (v1 / n1 + v2 / n2) ** 2 / (
        (v1 / n1) ** 2 / (n1 - 1) + (v2 / n2) ** 2 / (n2 - 1))
    p_value = 2 * t_sf(abs(t), df)
    tc = t_crit(df, alpha)
    pooled_sd = math.sqrt(((n1 - 1) * v1 + (n2 - 1) * v2) / (n1 + n2 - 2))
    d = (m2 - m1) / pooled_sd if pooled_sd else 0.0
    g = d * (1 - 3 / (4 * (n1 + n2) - 9))
    warnings = []
    if min(n1, n2) < 15:
        warnings.append(
            f"smallest group has n={min(n1, n2)}; with fewer than ~15 observations "
            "the t test is sensitive to non-normality — check a plot or use "
            "Mann-Whitney.")
    if max(v1, v2) > 0 and min(v1, v2) > 0 and max(v1, v2) / min(v1, v2) > 4:
        warnings.append("group variances differ by more than 4x; Welch handles "
                        "this, but confirm the groups are comparable at all.")
    return {
        "test": "Welch's t", "groups": [a_label, b_label],
        "mean_baseline": round(m1, 6), "mean_variant": round(m2, 6),
        "mean_difference": round(m2 - m1, 6),
        "statistic": round(t, 4), "df": round(df, 2), "p_value": round(p_value, 6),
        "effect_size": {"name": "Hedges' g", "value": round(g, 4),
                        "reading": magnitude(abs(g), COHEN_CUTS)},
        "ci": [round((m2 - m1) - tc * se, 6), round((m2 - m1) + tc * se, 6)],
        "ci_method": "Welch t interval",
        "warnings": warnings,
    }


def chi_square(data: Dict[str, Any], alpha: float) -> Dict[str, Any]:
    """Chi-square test of independence with Cramer's V."""
    table = [[float(v) for v in row] for row in data["table"]]
    rows, cols = len(table), len(table[0])
    total = sum(sum(r) for r in table)
    if total == 0:
        raise ValueError("contingency table is empty")
    row_sums = [sum(r) for r in table]
    col_sums = [sum(table[i][j] for i in range(rows)) for j in range(cols)]
    stat, small = 0.0, 0
    for i in range(rows):
        for j in range(cols):
            expected = row_sums[i] * col_sums[j] / total
            if expected < 5:
                small += 1
            if expected > 0:
                stat += (table[i][j] - expected) ** 2 / expected
    df = (rows - 1) * (cols - 1)
    p_value = chi2_sf(stat, df)
    v = math.sqrt(stat / (total * min(rows - 1, cols - 1))) if total else 0.0
    warnings = []
    if small:
        warnings.append(
            f"{small} cell(s) have an expected count below 5; the chi-square "
            "approximation degrades — collapse categories or use Fisher's exact test.")
    return {
        "test": "chi-square of independence",
        "statistic": round(stat, 4), "df": df, "p_value": round(p_value, 6),
        "n": int(total),
        "effect_size": {"name": "Cramer's V", "value": round(v, 4),
                        "reading": magnitude(v, CORRELATION_CUTS)},
        "ci": None,
        "ci_method": "not defined for the omnibus chi-square; report per-cell "
                     "proportion intervals instead",
        "warnings": warnings,
    }


def mann_whitney(data: Dict[str, Any], alpha: float) -> Dict[str, Any]:
    """Mann-Whitney U test (normal approximation, tie-corrected) with rank-biserial r."""
    groups = data["groups"]
    (a_label, a), (b_label, b) = list(groups.items())[:2]
    a, b = [float(v) for v in a], [float(v) for v in b]
    n1, n2 = len(a), len(b)
    if n1 == 0 or n2 == 0:
        raise ValueError("both groups need at least one observation")
    combined = sorted([(v, 0) for v in a] + [(v, 1) for v in b])
    ranks: List[float] = [0.0] * len(combined)
    i, tie_term = 0, 0.0
    while i < len(combined):
        j = i
        while j + 1 < len(combined) and combined[j + 1][0] == combined[i][0]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[k] = avg
        size = j - i + 1
        tie_term += size ** 3 - size
        i = j + 1
    r1 = sum(ranks[k] for k in range(len(combined)) if combined[k][1] == 0)
    u1 = r1 - n1 * (n1 + 1) / 2.0
    u2 = n1 * n2 - u1
    u = min(u1, u2)
    n = n1 + n2
    mu = n1 * n2 / 2.0
    sigma = math.sqrt(n1 * n2 / 12.0 * ((n + 1) - tie_term / (n * (n - 1))))
    z = (u - mu) / sigma if sigma else 0.0
    p_value = 2 * norm_sf(abs(z))
    # Positive rb means the second group ranks higher than the first.
    rb = 1.0 - 2.0 * u1 / (n1 * n2)
    warnings = []
    if min(n1, n2) < 8:
        warnings.append(
            f"smallest group has n={min(n1, n2)}; the normal approximation needs "
            "roughly 8+ per group — treat the p-value as indicative only.")
    return {
        "test": "Mann-Whitney U", "groups": [a_label, b_label],
        "u_statistic": round(u, 2), "statistic": round(z, 4),
        "p_value": round(p_value, 6),
        "median_baseline": round(statistics.median(a), 6),
        "median_variant": round(statistics.median(b), 6),
        "effect_size": {"name": "rank-biserial r", "value": round(rb, 4),
                        "reading": magnitude(abs(rb), CORRELATION_CUTS)},
        "ci": None,
        "ci_method": "distribution-free; report the Hodges-Lehmann shift if an "
                     "interval is required",
        "warnings": warnings,
    }


TESTS: Dict[str, Callable[[Dict[str, Any], float], Dict[str, Any]]] = {
    "two_proportion": two_proportion, "welch_t": welch_t,
    "chi_square": chi_square, "mann_whitney": mann_whitney}

# Each case: test, input, field to check, expected value, tolerance. Values are
# from worked examples computed independently of this implementation.
SELFTEST_CASES: List[Dict[str, Any]] = [
    # z = (0.13-0.10)/sqrt(0.115*0.885*(1/1000+1/1000)) = 0.03/0.0142671
    {"test": "two_proportion", "field": "statistic", "expected": 2.1027, "tol": 5e-4,
     "data": {"groups": {"control": {"successes": 100, "trials": 1000},
                         "variant": {"successes": 130, "trials": 1000}}}},
    # 2 * (1 - PHI(2.1027)); standard normal table gives PHI(2.10) = 0.98214
    {"test": "two_proportion", "field": "p_value", "expected": 0.0355, "tol": 5e-4,
     "data": {"groups": {"control": {"successes": 100, "trials": 1000},
                         "variant": {"successes": 130, "trials": 1000}}}},
    # equal variances (2.5 each, n=5): t = (6-3)/sqrt(0.5+0.5) = 3, df = 8
    {"test": "welch_t", "field": "statistic", "expected": 3.0, "tol": 5e-4,
     "data": {"groups": {"a": [1, 2, 3, 4, 5], "b": [4, 5, 6, 7, 8]}}},
    {"test": "welch_t", "field": "df", "expected": 8.0, "tol": 5e-3,
     "data": {"groups": {"a": [1, 2, 3, 4, 5], "b": [4, 5, 6, 7, 8]}}},
    # expected 12.857/17.143/17.143/22.857; sum (O-E)^2/E = 1.94444
    {"test": "chi_square", "field": "statistic", "expected": 1.9444, "tol": 5e-4,
     "data": {"table": [[10, 20], [20, 20]]}},
    # ranks with one tie at 3: R1 = 1+2+3.5+5 = 11.5, U1 = 11.5 - 10 = 1.5
    {"test": "mann_whitney", "field": "u_statistic", "expected": 1.5, "tol": 5e-3,
     "data": {"groups": {"a": [1, 2, 3, 4], "b": [3, 5, 6, 7]}}},
]


def selftest() -> Dict[str, Any]:
    """Run every test against known values; returns a pass/fail report."""
    results: List[Dict[str, Any]] = []
    for case in SELFTEST_CASES:
        actual = TESTS[case["test"]](case["data"], 0.05)[case["field"]]
        ok = abs(float(actual) - case["expected"]) <= case["tol"]
        results.append({"test": case["test"], "field": case["field"],
                        "expected": case["expected"], "actual": actual,
                        "passed": ok})
    passed = sum(1 for r in results if r["passed"])
    return {"total": len(results), "passed": passed,
            "failed": len(results) - passed, "results": results}


def output(report: Dict[str, Any], fmt: str) -> None:
    """Print the self-test report as JSON or human-readable text."""
    if fmt == "json":
        print(json.dumps(report, indent=2))
        return
    print("test_impl self-test")
    print("-" * 70)
    for row in report["results"]:
        mark = "PASS" if row["passed"] else "FAIL"
        print(f"  [{mark}] {row['test']:<16} {row['field']:<12} "
              f"expected {row['expected']}  got {row['actual']}")
    print("-" * 70)
    print(f"{report['passed']}/{report['total']} passed")


def main() -> None:
    """Parse arguments and run the self-test."""
    parser = argparse.ArgumentParser(
        description="Statistical test implementations for run_test.py; run "
                    "--selftest to verify them against worked examples.")
    parser.add_argument("--selftest", action="store_true",
                        help="Verify every test against known values.")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text).")
    args = parser.parse_args()

    if not args.selftest:
        parser.print_help()
        sys.exit(0)
    try:
        report = selftest()
    except (ValueError, OverflowError, ZeroDivisionError) as exc:
        print(f"ERROR: self-test could not complete: {exc}", file=sys.stderr)
        sys.exit(1)
    output(report, args.format)
    if report["failed"]:
        sys.exit(2)


if __name__ == "__main__":
    main()
