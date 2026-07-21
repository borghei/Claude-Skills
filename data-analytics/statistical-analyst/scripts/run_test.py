#!/usr/bin/env python3
"""Run a core statistical test with effect size and confidence interval.

Supports two-proportion z, Welch's t, chi-square of independence, and
Mann-Whitney U. The tests themselves live in test_impl.py and their
distributions in stats_core.py, both in this directory — no scipy. Every result
reports an effect size and an interval, because a bare p-value answers a
question nobody asked.

Usage:
    python3 run_test.py --input data.json
    python3 run_test.py --input data.json --test welch_t --alpha 0.05 \
        --comparisons 4 --format json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_impl import TESTS  # noqa: E402


def load_data(path: str) -> Dict[str, Any]:
    """Load the test-data JSON, exiting with guidance on failure."""
    try:
        with Path(path).open(encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"ERROR: {path} is not valid JSON (line {exc.lineno}): "
              f"{exc.msg}", file=sys.stderr)
        sys.exit(1)


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
    data = load_data(args.input)

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
