#!/usr/bin/env python3
"""
A/B Test Experiment Analyzer

Analyzes A/B test results for statistical significance using the
normal approximation to the two-proportion z-test.

Reads experiment data from CSV and produces analysis with confidence
intervals, p-values, and segment breakdowns.

Uses ONLY Python standard library.

Usage:
    python experiment_analyzer.py results.csv
    python experiment_analyzer.py results.csv --alpha 0.01
    python experiment_analyzer.py results.csv --json
"""

import argparse
import csv
import json
import math
import sys
from typing import Dict, List, Tuple


def z_score(p: float) -> float:
    """Approximate inverse normal CDF using Abramowitz & Stegun 26.2.23."""
    if p <= 0 or p >= 1:
        raise ValueError("p must be between 0 and 1 exclusive")
    if p > 0.5:
        return -z_score(1 - p)
    t = math.sqrt(-2 * math.log(p))
    c0, c1, c2 = 2.515517, 0.802853, 0.010328
    d1, d2, d3 = 1.432788, 0.189269, 0.001308
    return t - (c0 + c1 * t + c2 * t * t) / (1 + d1 * t + d2 * t * t + d3 * t * t * t)


def normal_cdf(x: float) -> float:
    """Approximate normal CDF using error function approximation."""
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def two_proportion_z_test(
    n_control: int, conv_control: int, n_variant: int, conv_variant: int
) -> Dict:
    """Perform two-proportion z-test.

    Returns dict with z-statistic, p-value, confidence interval, and lift.
    """
    if n_control == 0 or n_variant == 0:
        return {"error": "Zero sample size in one or more groups"}

    p_c = conv_control / n_control
    p_v = conv_variant / n_variant
    p_pooled = (conv_control + conv_variant) / (n_control + n_variant)

    se_pooled = math.sqrt(p_pooled * (1 - p_pooled) * (1 / n_control + 1 / n_variant))

    if se_pooled == 0:
        return {"error": "Zero standard error - no variance in data"}

    z = (p_v - p_c) / se_pooled
    p_value = 2 * (1 - normal_cdf(abs(z)))

    # Confidence interval for the difference (unpooled SE)
    se_diff = math.sqrt(p_c * (1 - p_c) / n_control + p_v * (1 - p_v) / n_variant)
    diff = p_v - p_c
    z_crit = z_score(0.025)  # 95% CI
    ci_lower = diff - z_crit * se_diff
    ci_upper = diff + z_crit * se_diff

    lift = ((p_v - p_c) / p_c) * 100 if p_c > 0 else 0

    return {
        "control_rate": round(p_c, 6),
        "variant_rate": round(p_v, 6),
        "absolute_difference": round(diff, 6),
        "relative_lift": round(lift, 2),
        "z_statistic": round(z, 4),
        "p_value": round(p_value, 6),
        "confidence_interval": {
            "lower": round(ci_lower, 6),
            "upper": round(ci_upper, 6),
        },
    }


def interpret_result(result: Dict, alpha: float) -> Dict:
    """Interpret statistical test result."""
    if "error" in result:
        return {"verdict": "ERROR", "explanation": result["error"]}

    p = result["p_value"]
    lift = result["relative_lift"]

    if p < alpha:
        if lift > 0:
            verdict = "WINNER"
            explanation = f"Variant wins with {lift:+.2f}% lift (p={p:.4f}). Statistically significant."
        else:
            verdict = "LOSER"
            explanation = f"Variant loses with {lift:+.2f}% change (p={p:.4f}). Keep control."
    elif p < alpha * 2:
        verdict = "INCONCLUSIVE"
        explanation = f"Trending ({lift:+.2f}% lift, p={p:.4f}). Consider running longer."
    else:
        if abs(lift) < 2:
            verdict = "FLAT"
            explanation = f"No meaningful difference ({lift:+.2f}%, p={p:.4f}). Test bolder changes."
        else:
            verdict = "INCONCLUSIVE"
            explanation = f"Direction unclear ({lift:+.2f}%, p={p:.4f}). Need more traffic."

    return {"verdict": verdict, "explanation": explanation}


def load_experiment_csv(filepath: str) -> List[Dict]:
    """Load experiment data from CSV.

    Expected columns: variant, visitors, conversions
    Optional columns: segment (for segment analysis)
    """
    rows = []
    with open(filepath, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(
                {
                    "variant": row.get("variant", "unknown"),
                    "visitors": int(row.get("visitors", 0)),
                    "conversions": int(row.get("conversions", 0)),
                    "segment": row.get("segment", "all"),
                }
            )
    return rows


def create_sample_csv(filepath: str):
    """Create sample experiment CSV for testing."""
    rows = [
        ["variant", "visitors", "conversions", "segment"],
        ["control", "5000", "250", "all"],
        ["variant_a", "5000", "290", "all"],
        ["control", "2500", "125", "desktop"],
        ["variant_a", "2500", "155", "desktop"],
        ["control", "2500", "125", "mobile"],
        ["variant_a", "2500", "135", "mobile"],
    ]
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    print(f"Sample CSV created at: {filepath}")


def analyze_experiment(rows: List[Dict], alpha: float) -> Dict:
    """Analyze full experiment with segment breakdown."""
    segments = {}
    for row in rows:
        seg = row["segment"]
        if seg not in segments:
            segments[seg] = {}
        segments[seg][row["variant"]] = row

    analyses = {}
    for seg_name, seg_data in segments.items():
        variants = list(seg_data.keys())
        control_key = next((v for v in variants if "control" in v.lower()), variants[0])
        control = seg_data[control_key]

        seg_results = []
        for variant_key, variant_data in seg_data.items():
            if variant_key == control_key:
                continue

            result = two_proportion_z_test(
                control["visitors"],
                control["conversions"],
                variant_data["visitors"],
                variant_data["conversions"],
            )
            interpretation = interpret_result(result, alpha)
            result.update(interpretation)
            result["variant_name"] = variant_key
            result["control_name"] = control_key
            result["control_visitors"] = control["visitors"]
            result["variant_visitors"] = variant_data["visitors"]
            seg_results.append(result)

        analyses[seg_name] = seg_results

    return analyses


def format_human_output(analyses: Dict, alpha: float) -> str:
    """Format analysis results as human-readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append("A/B TEST EXPERIMENT ANALYSIS")
    lines.append("=" * 60)
    lines.append(f"  Significance level: {alpha:.0%}")

    for seg_name, results in analyses.items():
        lines.append(f"\n{'  SEGMENT: ' + seg_name.upper()}")
        lines.append("  " + "-" * 50)

        for r in results:
            if "error" in r:
                lines.append(f"  Error: {r['error']}")
                continue

            lines.append(f"  {r['control_name']} vs {r['variant_name']}")
            lines.append(f"    Control:  {r['control_rate']:.2%} ({r['control_visitors']:,} visitors)")
            lines.append(f"    Variant:  {r['variant_rate']:.2%} ({r['variant_visitors']:,} visitors)")
            lines.append(f"    Lift:     {r['relative_lift']:+.2f}%")
            lines.append(f"    p-value:  {r['p_value']:.4f}")
            ci = r["confidence_interval"]
            lines.append(f"    95% CI:   [{ci['lower']:+.4f}, {ci['upper']:+.4f}]")
            lines.append(f"    Verdict:  {r['verdict']}")
            lines.append(f"    {r['explanation']}")
            lines.append("")

    # Summary
    if "all" in analyses:
        lines.append("-" * 60)
        lines.append("  RECOMMENDATION")
        lines.append("-" * 60)
        for r in analyses["all"]:
            if r.get("verdict") == "WINNER":
                lines.append(f"  Ship {r['variant_name']}. Check segment results for consistency.")
            elif r.get("verdict") == "LOSER":
                lines.append(f"  Keep {r['control_name']}. Investigate why variant underperformed.")
            elif r.get("verdict") == "FLAT":
                lines.append("  No effect detected. Consider testing a bolder change.")
            else:
                lines.append("  Results inconclusive. Extend the test or increase traffic.")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze A/B test experiment results for statistical significance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create sample data
  python experiment_analyzer.py sample

  # Analyze results
  python experiment_analyzer.py results.csv

  # Stricter significance
  python experiment_analyzer.py results.csv --alpha 0.01

  # JSON output
  python experiment_analyzer.py results.csv --json

CSV format:
  variant,visitors,conversions,segment
  control,5000,250,all
  variant_a,5000,290,all
        """,
    )

    parser.add_argument("input", help='CSV file with experiment results or "sample" to create sample')
    parser.add_argument("--alpha", "-a", type=float, default=0.05, help="Significance level (default: 0.05)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if args.input == "sample":
        create_sample_csv("sample_experiment.csv")
        return

    rows = load_experiment_csv(args.input)
    if not rows:
        print("Error: No data found in CSV", file=sys.stderr)
        sys.exit(1)

    analyses = analyze_experiment(rows, args.alpha)

    if args.json:
        print(json.dumps(analyses, indent=2))
    else:
        print(format_human_output(analyses, args.alpha))


if __name__ == "__main__":
    main()
