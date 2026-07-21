#!/usr/bin/env python3
"""Recommend a statistical test from data shape and question type.

Takes a description of the question, the outcome variable, the group structure,
and the sample, then recommends one test with its assumptions, the fallback if
those assumptions fail, and the sample size required to detect the stated
minimum effect. Standard library only; distributions come from stats_core.py.

Usage:
    python3 test_selector.py --input question.json
    python3 test_selector.py --input question.json --power 0.9 --format json
"""

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


sys.path.insert(0, str(Path(__file__).resolve().parent))
from stats_core import norm_ppf  # noqa: E402


def recommend(spec: Dict[str, Any]) -> Dict[str, Any]:
    """Select a test from the question shape and return it with its assumptions."""
    outcome = str(spec.get("outcome_type", "continuous")).lower()
    groups = int(spec.get("groups", 2))
    paired = bool(spec.get("paired", False))
    qtype = str(spec.get("question_type", "comparison")).lower()
    n = spec.get("sample_size_per_group")
    distribution = str(spec.get("distribution", "unknown")).lower()
    outliers = bool(spec.get("outliers", False))
    small = isinstance(n, int) and n < 15
    heavy_tailed = distribution in {"skewed", "heavy-tailed", "lognormal"} or outliers

    if qtype in {"trend", "time_series"}:
        return {
            "test": "interrupted time series / segmented regression",
            "why": "The observations are ordered in time, so they are not "
                   "independent. A t test on before/after periods treats "
                   "autocorrelated data as independent samples and produces "
                   "p-values that are far too small.",
            "assumptions": ["model the pre-period trend explicitly",
                            "check residual autocorrelation (Durbin-Watson)",
                            "at least 8-12 pre-period points"],
            "fallback": "difference-in-differences against an unaffected control series",
            "runnable_here": False,
        }
    if qtype in {"association", "correlation"} and outcome in {"continuous", "ordinal"}:
        return {
            "test": "Spearman rank correlation" if heavy_tailed or outcome == "ordinal"
                    else "Pearson correlation",
            "why": "The question is about co-movement of two measured variables, "
                   "not a difference between groups."
                   + (" Ranks are used because the data are skewed or ordinal."
                      if heavy_tailed or outcome == "ordinal" else ""),
            "assumptions": ["a scatter plot was actually looked at",
                            "the relationship is monotonic",
                            "no influential outliers driving the coefficient"],
            "fallback": "report the scatter plot and a robust regression slope",
            "runnable_here": False,
        }
    if outcome in {"binary", "proportion", "rate"}:
        if paired:
            return {
                "test": "McNemar's test",
                "why": "Each unit contributes a before/after pair, so only the "
                       "discordant pairs carry information. Treating the pairs "
                       "as independent samples discards that and loses power.",
                "assumptions": ["pairs are genuinely matched",
                                "at least ~10 discordant pairs, else use the exact version"],
                "fallback": "exact binomial test on the discordant pairs",
                "runnable_here": False,
            }
        if groups > 2:
            return {
                "test": "chi-square of independence",
                "why": f"{groups} groups with a categorical outcome. Run the "
                       "omnibus test first; only then do pairwise comparisons, "
                       "with a multiple-comparison correction.",
                "assumptions": ["every expected cell count is at least 5",
                                "observations are independent — one row per unit"],
                "fallback": "Fisher's exact test when expected counts are small",
                "runnable_here": True, "input_test": "chi_square",
            }
        return {
            "test": "two-proportion z test",
            "why": "Two independent groups with a binary outcome. This is the "
                   "standard conversion-rate comparison.",
            "assumptions": ["at least 5 events and 5 non-events per group",
                            "units are independent — no repeated users across arms",
                            "the assignment was randomized, or confounding is modelled"],
            "fallback": "Fisher's exact test when event counts are small",
            "runnable_here": True, "input_test": "two_proportion",
        }
    if outcome in {"count", "rate_per_exposure"}:
        return {
            "test": "Poisson rate-ratio test (or negative binomial if overdispersed)",
            "why": "Counts over exposure time are bounded below at zero and "
                   "heteroskedastic; a t test on raw counts understates the "
                   "uncertainty in the low-count arm.",
            "assumptions": ["check variance vs mean — if variance >> mean, use "
                            "negative binomial", "exposure time is recorded per unit"],
            "fallback": "Mann-Whitney on per-unit rates",
            "runnable_here": False,
        }
    if outcome == "ordinal" or heavy_tailed or small:
        reason = ("The outcome is ordinal, so means are not meaningful."
                  if outcome == "ordinal" else
                  ("The distribution is skewed or contains outliers, so the mean "
                   "is not a good summary and the t test's normality assumption "
                   "is doing real work." if heavy_tailed else
                   f"n={n} per group is too small for the central limit theorem "
                   "to rescue a non-normal distribution."))
        if groups > 2:
            return {"test": "Kruskal-Wallis", "why": reason + " With more than "
                    "two groups, use the rank-based omnibus test.",
                    "assumptions": ["groups have similar distribution shapes",
                                    "observations independent"],
                    "fallback": "Dunn's test for pairwise follow-up, corrected",
                    "runnable_here": False}
        return {"test": "Mann-Whitney U", "why": reason,
                "assumptions": ["the two distributions have similar shape if you "
                                "want to read it as a median difference",
                                "roughly 8+ observations per group for the normal "
                                "approximation"],
                "fallback": "report medians with bootstrap intervals and skip the test",
                "runnable_here": True, "input_test": "mann_whitney"}
    if paired:
        return {
            "test": "paired t test",
            "why": "Each unit is measured twice, so the pairing removes "
                   "between-unit variance and materially increases power.",
            "assumptions": ["the differences are roughly symmetric",
                            "no unit appears twice in the same arm"],
            "fallback": "Wilcoxon signed-rank when the differences are skewed",
            "runnable_here": False,
        }
    if groups > 2:
        return {
            "test": "one-way ANOVA",
            "why": f"{groups} independent groups with a continuous outcome. Run "
                   "the omnibus test first, then corrected pairwise comparisons.",
            "assumptions": ["residuals roughly normal", "similar group variances",
                            "independent observations"],
            "fallback": "Kruskal-Wallis when variances or shapes differ badly",
            "runnable_here": False,
        }
    return {
        "test": "Welch's t test",
        "why": "Two independent groups with a continuous outcome. Welch is the "
               "default rather than Student's t because it does not assume equal "
               "variances and costs almost nothing when they are equal.",
        "assumptions": ["roughly symmetric distributions, or n >= 15 per group",
                        "independent observations",
                        "outliers inspected rather than silently included"],
        "fallback": "Mann-Whitney U when the data are skewed or outlier-heavy",
        "runnable_here": True, "input_test": "welch_t",
    }


def sample_size(spec: Dict[str, Any], alpha: float, power: float) -> Optional[Dict[str, Any]]:
    """Compute required n per group for the stated minimum detectable effect."""
    z_a = norm_ppf(1 - alpha / 2)
    z_b = norm_ppf(power)
    outcome = str(spec.get("outcome_type", "continuous")).lower()
    if outcome in {"binary", "proportion", "rate"}:
        p1 = spec.get("baseline_rate")
        rel = spec.get("mde_relative")
        if p1 is None or rel is None:
            return None
        p2 = p1 * (1 + rel)
        if not 0 < p2 < 1:
            return None
        delta = abs(p2 - p1)
        n = (z_a + z_b) ** 2 * (p1 * (1 - p1) + p2 * (1 - p2)) / delta ** 2
        return {"per_group": math.ceil(n), "total": 2 * math.ceil(n),
                "basis": f"baseline {p1:.4f} -> {p2:.4f} "
                         f"({rel * 100:+.1f}% relative)",
                "alpha": alpha, "power": power}
    sd = spec.get("sd")
    mde_abs = spec.get("mde_absolute")
    if sd in (None, 0) or mde_abs in (None, 0):
        return None
    d = abs(mde_abs) / sd
    n = 2 * (z_a + z_b) ** 2 / d ** 2
    return {"per_group": math.ceil(n), "total": 2 * math.ceil(n),
            "basis": f"standardized effect d={d:.3f} (MDE {mde_abs} / SD {sd})",
            "alpha": alpha, "power": power}


def assess(spec: Dict[str, Any], alpha: float, power: float) -> Dict[str, Any]:
    """Build the full recommendation, including sizing and design warnings."""
    rec = recommend(spec)
    sizing = sample_size(spec, alpha, power)
    warnings: List[str] = []
    n = spec.get("sample_size_per_group")
    if sizing and isinstance(n, int) and n < sizing["per_group"]:
        warnings.append(
            f"Planned n={n} per group is below the {sizing['per_group']} needed "
            f"for {power:.0%} power. This study can only detect effects larger "
            "than the one you said matters — a null result will be uninformative.")
    if sizing is None:
        warnings.append(
            "No sample size computed: supply baseline_rate + mde_relative for a "
            "binary outcome, or sd + mde_absolute for a continuous one. Running "
            "a test without knowing your detectable effect is how underpowered "
            "studies get published as 'no difference'.")
    if int(spec.get("comparisons", 1)) > 1:
        adjusted = alpha / int(spec["comparisons"])
        warnings.append(
            f"{spec['comparisons']} comparisons in this family: use "
            f"alpha={adjusted:.4f} (Bonferroni) or Benjamini-Hochberg if the "
            "comparisons are exploratory. Uncorrected, the chance of at least "
            f"one false positive is {1 - (1 - alpha) ** int(spec['comparisons']):.1%}.")
    if not spec.get("randomized", True):
        warnings.append(
            "Assignment was not randomized. Any test here measures association, "
            "not causal effect — name the confounders you are not controlling for.")
    if spec.get("peeked", False):
        warnings.append(
            "The data have already been looked at while collecting. A fixed-"
            "horizon test is no longer valid; use a sequential method or fix a "
            "new horizon and collect fresh data.")
    return {"question": spec.get("question", ""), "recommendation": rec,
            "sample_size": sizing, "warnings": warnings}


def output(report: Dict[str, Any], fmt: str) -> None:
    """Print the recommendation as JSON or human-readable text."""
    if fmt == "json":
        print(json.dumps(report, indent=2))
        return
    rec = report["recommendation"]
    if report["question"]:
        print(f"Question: {report['question']}")
    print("=" * 68)
    print(f"Recommended test: {rec['test']}")
    print(f"Why: {rec['why']}")
    print("Assumptions to check before trusting the result:")
    for item in rec["assumptions"]:
        print(f"  - {item}")
    print(f"If those fail: {rec['fallback']}")
    if rec.get("runnable_here"):
        print(f"Runnable with run_test.py using \"test\": \"{rec['input_test']}\"")
    else:
        print("Not implemented in run_test.py — this one needs a modelling tool.")
    sizing = report["sample_size"]
    if sizing:
        print("-" * 68)
        print(f"Sample size for {sizing['power']:.0%} power at alpha="
              f"{sizing['alpha']}: {sizing['per_group']} per group "
              f"({sizing['total']} total)")
        print(f"  basis: {sizing['basis']}")
    for warning in report["warnings"]:
        print(f"WARNING: {warning}")


def main() -> None:
    """Parse arguments, build the recommendation, and emit it."""
    parser = argparse.ArgumentParser(
        description="Recommend a statistical test from data shape and question type.")
    parser.add_argument("--input", required=True,
                        help="Path to the question-spec JSON file.")
    parser.add_argument("--alpha", type=float, default=0.05,
                        help="Significance threshold for sizing (default: 0.05).")
    parser.add_argument("--power", type=float, default=0.8,
                        help="Target statistical power for sizing (default: 0.8).")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text).")
    args = parser.parse_args()

    if not 0 < args.alpha < 1 or not 0 < args.power < 1:
        print("ERROR: --alpha and --power must be between 0 and 1.", file=sys.stderr)
        sys.exit(1)
    try:
        with Path(args.input).open(encoding="utf-8") as handle:
            spec = json.load(handle)
    except FileNotFoundError:
        print(f"ERROR: file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"ERROR: {args.input} is not valid JSON (line {exc.lineno}): "
              f"{exc.msg}", file=sys.stderr)
        sys.exit(1)

    try:
        report = assess(spec, args.alpha, args.power)
    except (ValueError, TypeError, KeyError) as exc:
        print(f"ERROR: could not build a recommendation: {exc}. Check the input "
              "against assets/sample_question.json.", file=sys.stderr)
        sys.exit(1)
    output(report, args.format)


if __name__ == "__main__":
    main()
