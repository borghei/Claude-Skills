#!/usr/bin/env python3
"""Run a core statistical test with effect size and confidence interval.

Supports two-proportion z, Welch's t, chi-square of independence, and
Mann-Whitney U. Distributions come from stats_core.py in this directory — no
scipy. Every result reports an effect size and an interval, because a bare
p-value answers a question nobody asked.

Usage:
    python3 run_test.py --input data.json
    python3 run_test.py --input data.json --test welch_t --alpha 0.05 \
        --comparisons 4 --format json
"""

import argparse
import json
import math
import statistics
import sys
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parent))
from stats_core import chi2_sf, norm_sf, t_crit, t_sf, wilson  # noqa: E402

Z_CRIT = {0.10: 1.644854, 0.05: 1.959964, 0.01: 2.575829}


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
                        "reading": cohen_h_reading(abs(h))},
        "ci": [round(lower, 6), round(upper, 6)],
        "ci_method": "Newcombe hybrid score",
        "warnings": warnings,
    }


def cohen_h_reading(h: float) -> str:
    """Translate |Cohen's h| into a plain-language magnitude."""
    if h < 0.2:
        return "negligible"
    return "small" if h < 0.5 else ("medium" if h < 0.8 else "large")


def cohen_d_reading(d: float) -> str:
    """Translate |Cohen's d| into a plain-language magnitude."""
    if d < 0.2:
        return "negligible"
    return "small" if d < 0.5 else ("medium" if d < 0.8 else "large")


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
                        "reading": cohen_d_reading(abs(g))},
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
                        "reading": "negligible" if v < 0.1 else
                                   ("small" if v < 0.3 else
                                    ("medium" if v < 0.5 else "large"))},
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
                        "reading": "negligible" if abs(rb) < 0.1 else
                                   ("small" if abs(rb) < 0.3 else
                                    ("medium" if abs(rb) < 0.5 else "large"))},
        "ci": None,
        "ci_method": "distribution-free; report the Hodges-Lehmann shift if an "
                     "interval is required",
        "warnings": warnings,
    }


TESTS = {"two_proportion": two_proportion, "welch_t": welch_t,
         "chi_square": chi_square, "mann_whitney": mann_whitney}


def interpret(result: Dict[str, Any], alpha: float, comparisons: int) -> Dict[str, Any]:
    """Attach the significance verdict and a plain-language reading."""
    adjusted = alpha / comparisons
    significant = result["p_value"] < adjusted
    effect = result.get("effect_size", {})
    reading = effect.get("reading", "unknown")
    if significant and reading in {"negligible", "small"}:
        verdict = ("Statistically significant but the effect is "
                   f"{reading}. Decide on the effect size and its interval, not "
                   "on the p-value — at this sample size trivial differences "
                   "reach significance.")
    elif significant:
        verdict = f"Significant with a {reading} effect. Act on it."
    elif result.get("ci") and result["ci"][0] < 0 < result["ci"][1]:
        verdict = ("Not significant. The interval spans zero and includes "
                   f"effects as large as {max(abs(result['ci'][0]), abs(result['ci'][1])):.4f} "
                   "— this is an inconclusive result, not evidence of no effect.")
    else:
        verdict = ("Not significant at the adjusted threshold. Absence of "
                   "evidence is not evidence of absence — report the interval.")
    return {**result, "alpha": alpha, "comparisons": comparisons,
            "adjusted_alpha": round(adjusted, 6), "significant": significant,
            "verdict": verdict}


def output(result: Dict[str, Any], fmt: str) -> None:
    """Print the test result as JSON or human-readable text."""
    if fmt == "json":
        print(json.dumps(result, indent=2))
        return
    print(f"Test: {result['test']}")
    print("=" * 66)
    for key in ("rate_baseline", "rate_variant", "absolute_difference",
                "relative_lift", "mean_baseline", "mean_variant",
                "mean_difference", "median_baseline", "median_variant", "n"):
        if result.get(key) is not None:
            print(f"  {key.replace('_', ' '):<22} {result[key]}")
    print(f"  {'statistic':<22} {result['statistic']}"
          + (f" (df={result['df']})" if "df" in result else ""))
    p_shown = "<0.000001" if 0 <= result["p_value"] < 1e-6 else result["p_value"]
    print(f"  {'p-value':<22} {p_shown}")
    print(f"  {'alpha (adjusted)':<22} {result['adjusted_alpha']} "
          f"({result['comparisons']} comparison(s))")
    effect = result["effect_size"]
    print(f"  {effect['name']:<22} {effect['value']} ({effect['reading']})")
    if result.get("ci"):
        print(f"  {'95% CI':<22} [{result['ci'][0]}, {result['ci'][1]}] "
              f"via {result['ci_method']}")
    else:
        print(f"  {'interval':<22} {result['ci_method']}")
    print("-" * 66)
    print(f"Verdict: {result['verdict']}")
    for warning in result.get("warnings", []):
        print(f"WARNING: {warning}")


def main() -> None:
    """Parse arguments, run the requested test, and emit the result."""
    parser = argparse.ArgumentParser(
        description="Run a core statistical test with effect size and CI.")
    parser.add_argument("--input", required=True,
                        help="Path to the test-data JSON file.")
    parser.add_argument("--test", choices=sorted(TESTS),
                        help="Override the 'test' field in the input file.")
    parser.add_argument("--alpha", type=float, default=0.05,
                        help="Significance threshold before correction (default: 0.05).")
    parser.add_argument("--comparisons", type=int, default=1,
                        help="Number of comparisons in the family; applies a "
                             "Bonferroni-adjusted alpha (default: 1).")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text).")
    args = parser.parse_args()

    if args.comparisons < 1:
        print("ERROR: --comparisons must be at least 1.", file=sys.stderr)
        sys.exit(1)
    try:
        with Path(args.input).open(encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError:
        print(f"ERROR: file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"ERROR: {args.input} is not valid JSON (line {exc.lineno}): "
              f"{exc.msg}", file=sys.stderr)
        sys.exit(1)

    name = args.test or data.get("test")
    if name not in TESTS:
        print(f"ERROR: unknown test {name!r}. Choose one of: "
              f"{', '.join(sorted(TESTS))}.", file=sys.stderr)
        sys.exit(1)
    try:
        result = TESTS[name](data, args.alpha)
    except (KeyError, ValueError, TypeError, IndexError) as exc:
        print(f"ERROR: could not run {name}: {exc}. Check the input shape "
              "against assets/sample_experiment.json.", file=sys.stderr)
        sys.exit(1)

    output(interpret(result, args.alpha, args.comparisons), args.format)


if __name__ == "__main__":
    main()
