#!/usr/bin/env python3
"""
A/B Test Results Analyzer

Analyzes A/B test results with statistical significance testing, confidence
intervals, effect size calculation, and actionable recommendations.

Supports two-proportion z-tests for conversion rate experiments.

Expected JSON input: {"test_name", "variants": {"control": {"visitors", "conversions"},
  "treatment": {"visitors", "conversions"}}, "significance_level"}

Usage:
    python results_analyzer.py results.json
    python results_analyzer.py results.json --format json
    python results_analyzer.py results.json --batch
    python results_analyzer.py results.json --bayesian
"""

import argparse
import json
import math
import sys
from typing import Any, Dict, List, Optional, Tuple


def norm_ppf(p: float) -> float:
    """Inverse normal CDF using rational approximation."""
    if p <= 0 or p >= 1:
        raise ValueError("p must be between 0 and 1")
    if p < 0.5:
        return -norm_ppf(1 - p)
    t = math.sqrt(-2 * math.log(1 - p))
    c0, c1, c2 = 2.515517, 0.802853, 0.010328
    d1, d2, d3 = 1.432788, 0.189269, 0.001308
    return t - (c0 + c1 * t + c2 * t**2) / (1 + d1 * t + d2 * t**2 + d3 * t**3)


def norm_cdf(x: float) -> float:
    """Standard normal CDF."""
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def two_proportion_z_test(
    n1: int, x1: int, n2: int, x2: int
) -> Dict[str, float]:
    """
    Perform a two-proportion z-test.

    Args:
        n1: Sample size of control
        x1: Conversions in control
        n2: Sample size of treatment
        x2: Conversions in treatment

    Returns:
        z_statistic, p_value (two-sided)
    """
    p1 = x1 / n1 if n1 > 0 else 0
    p2 = x2 / n2 if n2 > 0 else 0
    p_pooled = (x1 + x2) / (n1 + n2) if (n1 + n2) > 0 else 0

    se = math.sqrt(p_pooled * (1 - p_pooled) * (1/n1 + 1/n2)) if n1 > 0 and n2 > 0 else 0

    if se == 0:
        return {"z_statistic": 0, "p_value": 1.0, "se": 0}

    z = (p2 - p1) / se
    p_value = 2 * (1 - norm_cdf(abs(z)))

    return {"z_statistic": round(z, 4), "p_value": round(p_value, 6), "se": round(se, 6)}


def confidence_interval(
    n1: int, x1: int, n2: int, x2: int, alpha: float = 0.05
) -> Dict[str, float]:
    """Calculate confidence interval for difference in proportions."""
    p1 = x1 / n1 if n1 > 0 else 0
    p2 = x2 / n2 if n2 > 0 else 0
    diff = p2 - p1

    se = math.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2) if n1 > 0 and n2 > 0 else 0
    z = norm_ppf(1 - alpha / 2)

    margin = z * se
    return {
        "point_estimate": round(diff, 6),
        "lower_bound": round(diff - margin, 6),
        "upper_bound": round(diff + margin, 6),
        "margin_of_error": round(margin, 6),
        "confidence_level": round((1 - alpha) * 100, 0),
    }


def cohens_h(p1: float, p2: float) -> float:
    """Calculate Cohen's h effect size for proportions."""
    return 2 * math.asin(math.sqrt(p2)) - 2 * math.asin(math.sqrt(p1))


def bayesian_analysis(n1: int, x1: int, n2: int, x2: int,
                      n_samples: int = 100000) -> Dict[str, Any]:
    """Simple Bayesian analysis using Beta-Binomial model with grid approximation.
    Uses a uniform Beta(1,1) prior."""
    # Beta posterior parameters
    alpha1, beta1 = x1 + 1, n1 - x1 + 1
    alpha2, beta2 = x2 + 1, n2 - x2 + 1

    # Compute probability that treatment > control using numerical integration
    # Grid-based approximation
    grid_size = 1000
    prob_b_better = 0.0
    step = 1.0 / grid_size

    for i in range(grid_size):
        p = (i + 0.5) * step
        # Beta PDF approximation using Stirling's for large factorials
        # Use log-space for numerical stability
        # For simplicity, use the analytical result for Beta distributions
        pass

    # Simpler approximation: normal approximation to beta posterior
    mean1 = alpha1 / (alpha1 + beta1)
    var1 = (alpha1 * beta1) / ((alpha1 + beta1) ** 2 * (alpha1 + beta1 + 1))
    mean2 = alpha2 / (alpha2 + beta2)
    var2 = (alpha2 * beta2) / ((alpha2 + beta2) ** 2 * (alpha2 + beta2 + 1))

    diff_mean = mean2 - mean1
    diff_std = math.sqrt(var1 + var2)

    if diff_std > 0:
        prob_b_better = norm_cdf(diff_mean / diff_std)
    else:
        prob_b_better = 0.5

    # Credible interval for the difference
    z95 = 1.96
    ci_lower = diff_mean - z95 * diff_std
    ci_upper = diff_mean + z95 * diff_std

    return {
        "probability_treatment_better": round(prob_b_better, 4),
        "expected_difference": round(diff_mean, 6),
        "credible_interval_95": {
            "lower": round(ci_lower, 6),
            "upper": round(ci_upper, 6),
        },
        "control_posterior_mean": round(mean1, 6),
        "treatment_posterior_mean": round(mean2, 6),
    }


def analyze_test(data: Dict[str, Any], include_bayesian: bool = False) -> Dict[str, Any]:
    """Analyze a single A/B test."""
    test_name = data.get("test_name", "Unnamed Test")
    metric = data.get("metric", "conversion_rate")
    alpha = data.get("significance_level", 0.05)
    variants = data.get("variants", {})

    # Support both dict and list format for variants
    if isinstance(variants, list):
        if len(variants) >= 2:
            control = variants[0]
            treatment = variants[1]
        else:
            return {"error": "Need at least 2 variants"}
    else:
        control = variants.get("control", {})
        treatment = variants.get("treatment", {})

    n1 = control.get("visitors", 0)
    x1 = control.get("conversions", 0)
    n2 = treatment.get("visitors", 0)
    x2 = treatment.get("conversions", 0)

    if n1 == 0 or n2 == 0:
        return {"error": "Both variants must have visitors > 0", "test_name": test_name}

    p1 = x1 / n1
    p2 = x2 / n2
    relative_change = (p2 - p1) / p1 if p1 > 0 else 0

    # Statistical test
    z_test = two_proportion_z_test(n1, x1, n2, x2)
    ci = confidence_interval(n1, x1, n2, x2, alpha)
    effect_size = cohens_h(p1, p2)

    # Significance determination
    is_significant = z_test["p_value"] < alpha
    direction = "positive" if p2 > p1 else "negative" if p2 < p1 else "neutral"

    # Effect size interpretation
    abs_h = abs(effect_size)
    if abs_h < 0.2:
        effect_label = "negligible"
    elif abs_h < 0.5:
        effect_label = "small"
    elif abs_h < 0.8:
        effect_label = "medium"
    else:
        effect_label = "large"

    # Recommendation
    if is_significant and direction == "positive":
        recommendation = "SHIP - Statistically significant positive result"
        confidence = "high"
    elif is_significant and direction == "negative":
        recommendation = "REVERT - Statistically significant negative result"
        confidence = "high"
    elif not is_significant and abs(relative_change) > 0.05:
        recommendation = "EXTEND - Trending but not yet significant. Consider running longer."
        confidence = "low"
    else:
        recommendation = "NO EFFECT - No meaningful difference detected"
        confidence = "medium"

    result = {
        "test_name": test_name,
        "metric": metric,
        "control": {
            "visitors": n1,
            "conversions": x1,
            "rate": round(p1, 6),
            "rate_pct": round(p1 * 100, 3),
        },
        "treatment": {
            "visitors": n2,
            "conversions": x2,
            "rate": round(p2, 6),
            "rate_pct": round(p2 * 100, 3),
        },
        "difference": {
            "absolute": round(p2 - p1, 6),
            "absolute_pct": round((p2 - p1) * 100, 3),
            "relative_pct": round(relative_change * 100, 2),
            "direction": direction,
        },
        "statistical_test": {
            "method": "Two-proportion z-test (two-sided)",
            "z_statistic": z_test["z_statistic"],
            "p_value": z_test["p_value"],
            "significance_level": alpha,
            "is_significant": is_significant,
        },
        "confidence_interval": ci,
        "effect_size": {
            "cohens_h": round(effect_size, 4),
            "interpretation": effect_label,
        },
        "recommendation": recommendation,
        "confidence": confidence,
    }

    if include_bayesian:
        result["bayesian"] = bayesian_analysis(n1, x1, n2, x2)

    return result


def print_human(results: List[Dict[str, Any]]) -> None:
    """Print analysis in human-readable format."""
    for r in results:
        if "error" in r:
            print(f"\n  Error in {r.get('test_name', 'unknown')}: {r['error']}")
            continue

        print("=" * 65)
        print(f"  A/B Test Results: {r['test_name']}")
        print("=" * 65)

        c = r["control"]
        t = r["treatment"]
        print(f"\n  --- Variant Performance ({r['metric']}) ---")
        print(f"  {'Variant':<12} {'Visitors':>10} {'Conversions':>12} {'Rate':>10}")
        print(f"  {'-'*12} {'-'*10} {'-'*12} {'-'*10}")
        print(f"  {'Control':<12} {c['visitors']:>10,} {c['conversions']:>12,} {c['rate_pct']:>9.3f}%")
        print(f"  {'Treatment':<12} {t['visitors']:>10,} {t['conversions']:>12,} {t['rate_pct']:>9.3f}%")

        d = r["difference"]
        sign = "+" if d["relative_pct"] >= 0 else ""
        print(f"\n  --- Effect ---")
        print(f"  Absolute Change:  {sign}{d['absolute_pct']:.3f}pp")
        print(f"  Relative Change:  {sign}{d['relative_pct']:.2f}%")
        print(f"  Direction:        {d['direction']}")

        s = r["statistical_test"]
        print(f"\n  --- Statistical Significance ---")
        print(f"  Z-statistic:  {s['z_statistic']:.4f}")
        print(f"  P-value:      {s['p_value']:.6f}")
        print(f"  Alpha:        {s['significance_level']}")
        sig_label = "YES - Statistically significant" if s["is_significant"] else "NO - Not statistically significant"
        print(f"  Significant:  {sig_label}")

        ci = r["confidence_interval"]
        print(f"\n  --- {ci['confidence_level']:.0f}% Confidence Interval ---")
        print(f"  [{ci['lower_bound']*100:+.3f}pp, {ci['upper_bound']*100:+.3f}pp]")
        print(f"  Margin of Error: +/-{ci['margin_of_error']*100:.3f}pp")

        e = r["effect_size"]
        print(f"\n  --- Effect Size ---")
        print(f"  Cohen's h: {e['cohens_h']:.4f} ({e['interpretation']})")

        if "bayesian" in r:
            b = r["bayesian"]
            print(f"\n  --- Bayesian Analysis ---")
            print(f"  P(Treatment > Control): {b['probability_treatment_better']*100:.1f}%")
            print(f"  Expected Difference:    {b['expected_difference']*100:.3f}pp")
            ci_b = b["credible_interval_95"]
            print(f"  95% Credible Interval:  [{ci_b['lower']*100:.3f}pp, {ci_b['upper']*100:.3f}pp]")

        print(f"\n  {'=' * 61}")
        print(f"  RECOMMENDATION: {r['recommendation']}")
        print(f"  Confidence: {r['confidence']}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="Analyze A/B test results with statistical significance testing"
    )
    parser.add_argument("file", help="JSON file with test results")
    parser.add_argument("--format", choices=["human", "json"], default="human", help="Output format")
    parser.add_argument("--batch", action="store_true",
                        help="Process multiple tests (expects 'tests' array)")
    parser.add_argument("--bayesian", action="store_true",
                        help="Include Bayesian analysis alongside frequentist")
    args = parser.parse_args()

    with open(args.file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if args.batch:
        tests = data.get("tests", [])
    else:
        tests = [data]

    results = [analyze_test(t, args.bayesian) for t in tests]

    if args.format == "json":
        output = {"results": results} if len(results) > 1 else results[0]
        print(json.dumps(output, indent=2))
    else:
        print_human(results)


if __name__ == "__main__":
    main()
