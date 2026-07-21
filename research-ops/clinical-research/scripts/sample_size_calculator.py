#!/usr/bin/env python3
"""
sample_size_calculator.py — Sample size and power for the three parallel-group
designs covering most clinical study planning: two proportions, two means, and
time-to-event compared by log-rank.

Computes required n from a target power, or achieved power from a planned n, and
inflates for dropout. Stdlib only. The design formulas live in the sibling
module power_formulas.py; this file handles input validation, dropout inflation,
warnings, reporting, and the CLI. Every result reports the approximation that
produced it in `method_note`.

Supports study operations planning; it does not replace a qualified
biostatistician. It assumes a simple parallel design with no interim analyses,
no multiplicity adjustment, no covariate adjustment, and no clustering. Any
protocol departing from those assumptions needs a statistician's sign-off.

Usage:
    python3 sample_size_calculator.py --input power_spec.json
    python3 sample_size_calculator.py --input power_spec.json --format json

Input schema (see assets/sample_power_spec.json for a complete example):
{
  "study": str,
  "design": "two_proportion" | "two_mean" | "survival",
  "alpha": 0.05,
  "sided": 1 | 2,
  "power": 0.80,
  "allocation_ratio": n_treatment / n_control,     # 1.0 for equal allocation
  "dropout_rate": 0.15,
  "planned_n_per_group": int | null,               # report power at this n

  "two_proportion": {"p_control", "p_treatment"},
  "two_mean":       {"mean_difference", "std_dev"},
  "survival":       {"hazard_ratio", "probability_of_event"}
                    # or, instead of probability_of_event:
                    #   "median_survival_control_months" together with
                    #   "accrual_months" and "followup_months"
}

Only the block matching `design` is read; the others may be present and are
ignored, so one spec file can carry all three.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

# The statistics live in their own module so a biostatistician can review and
# revise the formulas without touching validation, reporting, or the CLI.
# Same-skill sibling import.
from power_formulas import DESIGNS, DISCLAIMER, achieved_power

VALID_DESIGNS = tuple(DESIGNS)


def analyse(payload: dict[str, Any]) -> dict[str, Any]:
    """Run the requested design calculation and apply dropout inflation."""
    design = payload.get("design")
    if design not in VALID_DESIGNS:
        raise ValueError(f"design is '{design}'; expected one of {list(VALID_DESIGNS)}")
    spec = payload.get(design)
    if not spec:
        raise ValueError(f"design is '{design}' but no '{design}' block is present")

    alpha = float(payload.get("alpha", 0.05))
    sided = int(payload.get("sided", 2))
    power = float(payload.get("power", 0.80))
    k = float(payload.get("allocation_ratio", 1.0))
    dropout = float(payload.get("dropout_rate", 0.0))
    if k <= 0:
        raise ValueError(f"allocation_ratio is {k}; must be positive")
    if not 0 <= dropout < 1:
        raise ValueError(f"dropout_rate is {dropout}; must be in [0, 1)")

    result = DESIGNS[design](spec, alpha, sided, power, k)
    analysed = result["n_control"] + result["n_treatment"]
    enrol = math.ceil(analysed / (1 - dropout)) if dropout else analysed

    planned = payload.get("planned_n_per_group")
    planned_power = (round(achieved_power(design, spec, int(planned), k, alpha, sided), 4)
                     if planned else None)

    return {
        "study": payload.get("study", ""), "design": design,
        "alpha": alpha, "sided": sided, "target_power": power,
        "allocation_ratio": k, "dropout_rate": dropout,
        "n_control": result["n_control"], "n_treatment": result["n_treatment"],
        "n_analysed_total": analysed, "n_to_enrol_total": enrol,
        "required_events": result.get("required_events"),
        "required_events_freedman": result.get("required_events_freedman"),
        "overall_event_probability": result.get("overall_event_probability"),
        "effect": result["effect"], "planned_n_per_group": planned,
        "power_at_planned_n": planned_power, "method_note": result["note"],
        "warnings": build_warnings(power, sided, dropout, planned, planned_power),
        "disclaimer": DISCLAIMER,
    }


def build_warnings(power: float, sided: int, dropout: float,
                   planned: int | None, planned_power: float | None) -> list[str]:
    """Flag inputs that are legal but that usually indicate a planning mistake."""
    warnings: list[str] = []
    if power < 0.80:
        warnings.append(f"target power {power:.0%} is below the 80% convention — "
                        "under-powered studies produce uninterpretable negatives")
    if sided == 1:
        warnings.append("one-sided test — regulators generally expect two-sided "
                        "testing unless the protocol justifies otherwise")
    if dropout == 0:
        warnings.append("dropout_rate is 0 — no trial retains every participant; "
                        "inflate by the rate seen in comparable studies")
    if planned_power is not None and planned_power < power:
        warnings.append(f"planned n of {planned}/group gives {planned_power:.0%} "
                        f"power, below the {power:.0%} target")
    return warnings


def render_text(r: dict[str, Any]) -> str:
    """Render the calculation as human-readable text."""
    lines = [f"Sample size — {r['study']}",
             f"Design: {r['design']} | alpha {r['alpha']} ({r['sided']}-sided) | "
             f"target power {r['target_power']:.0%}", "", "Effect:"] + [
             f"  {key}: {val}" for key, val in r["effect"].items()]
    lines += ["", "Sample:", f"  control            {r['n_control']:,}",
              f"  treatment          {r['n_treatment']:,}",
              f"  analysed total     {r['n_analysed_total']:,}",
              f"  to enrol (dropout {r['dropout_rate']:.0%})  {r['n_to_enrol_total']:,}"]
    if r.get("required_events"):
        lines += [f"  required events    {r['required_events']:,} "
                  f"(Freedman: {r['required_events_freedman']:,})",
                  f"  event probability  {r['overall_event_probability']:.3f}"]
    if r["planned_n_per_group"]:
        lines += ["", f"Planned {r['planned_n_per_group']}/group gives "
                      f"{r['power_at_planned_n']:.1%} power"]
    if r["warnings"]:
        lines += ["", "Warnings:"] + [f"  - {w}" for w in r["warnings"]]
    return "\n".join(lines + ["", f"Method: {r['method_note']}",
                              "", f"NOTE: {r['disclaimer']}"])


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Sample size and power for two-proportion, two-mean, and "
                    "log-rank designs.",
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    parser.add_argument("--input", required=True, help="Path to JSON power spec")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format; text is the default")
    parser.add_argument("--output", help="Write output file instead of stdout")
    return parser.parse_args()


def main() -> int:
    """CLI entry point."""
    args = parse_args()
    try:
        payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
        report = analyse(payload)
        out = (json.dumps(report, indent=2) if args.format == "json"
               else render_text(report))
        if args.output:
            Path(args.output).write_text(out, encoding="utf-8")
            print(f"wrote {args.output}", file=sys.stderr)
        else:
            print(out)
    except OSError as exc:
        print(f"error: cannot read or write file: {exc}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"error: --input is not valid JSON: {exc}", file=sys.stderr)
        return 1
    except (ValueError, KeyError, TypeError, ZeroDivisionError) as exc:
        print(f"error: invalid power spec: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
