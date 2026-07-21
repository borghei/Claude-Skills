#!/usr/bin/env python3
"""
sample_size_calculator.py — Sample size and power for the three parallel-group
designs covering most clinical study planning: two proportions, two means, and
time-to-event compared by log-rank.

Computes required n from a target power, or achieved power from a planned n, and
inflates for dropout, using standard normal-approximation formulas. Stdlib only
(statistics.NormalDist for quantiles).

Supports study operations planning; does not replace a qualified biostatistician.
Assumes a simple parallel design with no interim analyses, multiplicity
adjustment, covariate adjustment, or clustering. Any protocol departing from
those assumptions needs a statistician's sign-off.

Usage:
    python3 sample_size_calculator.py --input power_spec.json [--format json]

Input schema (see assets/sample_power_spec.json for a complete example):
{
  "study": str,
  "design": "two_proportion" | "two_mean" | "survival",
  "alpha": 0.05, "sided": 1|2, "power": 0.80,
  "allocation_ratio": n_treatment / n_control,
  "dropout_rate": 0.15, "planned_n_per_group": int | null,
  "two_proportion": {"p_control", "p_treatment"},
  "two_mean":       {"mean_difference", "std_dev"},
  "survival":       {"hazard_ratio", "median_survival_control_months",
                     "accrual_months", "followup_months"}
                    # or "probability_of_event" directly
}
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from statistics import NormalDist
from typing import Any

ND = NormalDist()
VALID_DESIGNS = ("two_proportion", "two_mean", "survival")
NOTE_PROP = ("Normal approximation with pooled variance under the null. For "
             "expected cell counts below 5, use an exact method instead.")
NOTE_MEAN = ("Assumes equal variance and a known SD. If the SD comes from a small "
             "pilot, add roughly 10-15% to n to absorb its uncertainty.")
NOTE_SURV = ("Event-driven design: the analysis triggers on the event count, not on "
             "the enrolment target. Exponential survival assumed; if hazards are "
             "non-proportional, log-rank is the wrong test.")
DISCLAIMER = ("Operational planning only. Assumes a parallel design with no interim "
              "analysis, multiplicity adjustment, covariate adjustment, or clustering. "
              "Requires biostatistician sign-off before it enters a protocol.")


def _z(alpha: float, sided: int, power: float) -> tuple[float, float]:
    """Return the critical value for alpha and the quantile for the target power."""
    if not 0 < alpha < 1:
        raise ValueError("alpha must be between 0 and 1")
    if not 0 < power < 1:
        raise ValueError("power must be between 0 and 1")
    if sided not in (1, 2):
        raise ValueError("sided must be 1 or 2")
    return ND.inv_cdf(1 - alpha / sided), ND.inv_cdf(power)


def two_proportion(spec: dict[str, Any], alpha: float, sided: int, power: float,
                   k: float) -> dict[str, Any]:
    """Sample size per group for a difference in two independent proportions."""
    p1, p2 = float(spec["p_control"]), float(spec["p_treatment"])
    for name, p in (("p_control", p1), ("p_treatment", p2)):
        if not 0 < p < 1:
            raise ValueError(f"{name} must be strictly between 0 and 1")
    delta = abs(p1 - p2)
    if delta == 0:
        raise ValueError("p_control and p_treatment are equal; no effect to power for")
    z_a, z_b = _z(alpha, sided, power)
    p_bar = (p1 + k * p2) / (1 + k)
    q_bar = 1 - p_bar
    term_null = z_a * math.sqrt((1 + 1 / k) * p_bar * q_bar)
    term_alt = z_b * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2) / k)
    n_control = ((term_null + term_alt) ** 2) / (delta ** 2)

    return {
        "n_control": math.ceil(n_control), "n_treatment": math.ceil(n_control * k),
        "effect": {"p_control": p1, "p_treatment": p2,
                   "absolute_difference": round(delta, 4),
                   "relative_difference": round(delta / p1, 4)},
        "note": NOTE_PROP,
    }


def two_mean(spec: dict[str, Any], alpha: float, sided: int, power: float,
             k: float) -> dict[str, Any]:
    """Sample size per group for a difference in two independent means."""
    delta = abs(float(spec["mean_difference"]))
    sd = float(spec["std_dev"])
    if delta == 0:
        raise ValueError("mean_difference is 0; no effect to power for")
    if sd <= 0:
        raise ValueError("std_dev must be positive")
    z_a, z_b = _z(alpha, sided, power)
    n_control = (1 + 1 / k) * ((z_a + z_b) ** 2) * (sd ** 2) / (delta ** 2)

    return {
        "n_control": math.ceil(n_control), "n_treatment": math.ceil(n_control * k),
        "effect": {"mean_difference": delta, "std_dev": sd,
                   "standardised_effect_size": round(delta / sd, 4)},
        "note": NOTE_MEAN,
    }


def _event_probability(median_months: float, accrual: float, followup: float) -> float:
    """Probability of an event under exponential survival with uniform accrual."""
    lam = math.log(2) / median_months
    if accrual <= 0:
        return 1 - math.exp(-lam * followup)
    # Standard result for uniform accrual over `accrual` plus `followup` of
    # additional observation.
    return 1 - (math.exp(-lam * followup)
                - math.exp(-lam * (followup + accrual))) / (lam * accrual)


def survival(spec: dict[str, Any], alpha: float, sided: int, power: float,
             k: float) -> dict[str, Any]:
    """Required events and enrolment for a log-rank comparison of two arms."""
    hr = float(spec["hazard_ratio"])
    if hr <= 0 or hr == 1:
        raise ValueError("hazard_ratio must be positive and not equal to 1")
    z_a, z_b = _z(alpha, sided, power)
    prop_c, prop_t = 1 / (1 + k), k / (1 + k)

    # Schoenfeld: the design is driven by the number of events, not by n.
    events_schoenfeld = ((z_a + z_b) ** 2) / (prop_c * prop_t * (math.log(hr) ** 2))
    # Freedman, reported alongside because it is the more conservative of the two.
    events_freedman = (((1 + hr) / (1 - hr)) ** 2) * ((z_a + z_b) ** 2)
    events = math.ceil(events_schoenfeld)

    median_c = spec.get("median_survival_control_months")
    prob = spec.get("probability_of_event")
    detail: dict[str, Any] = {}
    if prob is None and median_c:
        accrual = float(spec.get("accrual_months", 0))
        followup = float(spec.get("followup_months", 0))
        if accrual <= 0 and followup <= 0:
            raise ValueError("survival needs accrual_months or followup_months to "
                             "convert events into enrolment")
        median_t = float(median_c) / hr
        p_c = _event_probability(float(median_c), accrual, followup)
        p_t = _event_probability(median_t, accrual, followup)
        prob = prop_c * p_c + prop_t * p_t
        detail = {"median_survival_control_months": float(median_c),
                  "implied_median_treatment_months": round(median_t, 2),
                  "event_probability_control": round(p_c, 4),
                  "event_probability_treatment": round(p_t, 4)}
    if not prob:
        raise ValueError("survival needs probability_of_event, or "
                         "median_survival_control_months with accrual/followup")
    prob = float(prob)
    if not 0 < prob <= 1:
        raise ValueError("probability_of_event must be in (0, 1]")
    total_n = math.ceil(events / prob)
    n_control = math.ceil(total_n * prop_c)
    return {
        "n_control": n_control,
        "n_treatment": total_n - n_control,
        "required_events": events,
        "required_events_freedman": math.ceil(events_freedman),
        "overall_event_probability": round(prob, 4),
        "effect": {"hazard_ratio": hr, **detail},
        "note": NOTE_SURV,
    }


def achieved_power(design: str, spec: dict[str, Any], n_control: int, k: float,
                   alpha: float, sided: int) -> float:
    """Return the power actually achieved by a given per-group sample size."""
    z_a = ND.inv_cdf(1 - alpha / sided)
    n_treat = n_control * k
    if design == "two_mean":
        delta, sd = abs(float(spec["mean_difference"])), float(spec["std_dev"])
        return ND.cdf(delta / (sd * math.sqrt(1 / n_control + 1 / n_treat)) - z_a)
    if design == "two_proportion":
        p1, p2 = float(spec["p_control"]), float(spec["p_treatment"])
        p_bar = (n_control * p1 + n_treat * p2) / (n_control + n_treat)
        se_null = math.sqrt(p_bar * (1 - p_bar) * (1 / n_control + 1 / n_treat))
        se_alt = math.sqrt(p1 * (1 - p1) / n_control + p2 * (1 - p2) / n_treat)
        return ND.cdf((abs(p1 - p2) - z_a * se_null) / se_alt)
    hr = float(spec["hazard_ratio"])
    prob = float(spec.get("probability_of_event") or 0.5)
    events = (n_control + n_treat) * prob
    prop_c, prop_t = 1 / (1 + k), k / (1 + k)
    return ND.cdf(abs(math.log(hr)) * math.sqrt(events * prop_c * prop_t) - z_a)


def analyse(payload: dict[str, Any]) -> dict[str, Any]:
    """Run the requested design calculation and apply dropout inflation."""
    design = payload.get("design")
    if design not in VALID_DESIGNS:
        raise ValueError(f"design is '{design}'; expected one of {list(VALID_DESIGNS)}")
    spec = payload.get(design)
    if not spec:
        raise ValueError(f"payload has design '{design}' but no '{design}' block")
    alpha = float(payload.get("alpha", 0.05))
    sided = int(payload.get("sided", 2))
    power = float(payload.get("power", 0.80))
    k = float(payload.get("allocation_ratio", 1.0))
    dropout = float(payload.get("dropout_rate", 0.0))
    if k <= 0:
        raise ValueError("allocation_ratio must be positive")
    if not 0 <= dropout < 1:
        raise ValueError("dropout_rate must be in [0, 1)")

    handler = {"two_proportion": two_proportion, "two_mean": two_mean,
               "survival": survival}[design]
    result = handler(spec, alpha, sided, power, k)
    analysed = result["n_control"] + result["n_treatment"]
    enrol = math.ceil(analysed / (1 - dropout)) if dropout else analysed

    planned = payload.get("planned_n_per_group")
    planned_power = (round(achieved_power(design, spec, int(planned), k, alpha, sided), 4)
                     if planned else None)

    warnings: list[str] = []
    if power < 0.80:
        warnings.append(f"target power {power:.0%} is below the 80% convention — "
                        "under-powered studies produce uninterpretable negatives")
    if sided == 1:
        warnings.append("one-sided test — regulators generally expect two-sided testing "
                        "unless the protocol justifies otherwise")
    if dropout == 0:
        warnings.append("dropout_rate is 0 — no trial retains every participant; inflate "
                        "by the rate observed in comparable studies")
    if planned_power is not None and planned_power < power:
        warnings.append(f"planned n of {planned}/group gives {planned_power:.0%} power, "
                        f"below the {power:.0%} target")

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
        "warnings": warnings, "disclaimer": DISCLAIMER,
    }


def render_text(r: dict[str, Any]) -> str:
    """Render the calculation as human-readable text."""
    lines = [f"Sample size — {r['study']}",
             f"Design: {r['design']} | alpha {r['alpha']} ({r['sided']}-sided) | "
             f"target power {r['target_power']:.0%}", "", "Effect:"]
    lines += [f"  {key}: {val}" for key, val in r["effect"].items()]
    lines += ["", "Sample:",
              f"  control            {r['n_control']:,}",
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
    lines += ["", f"Method: {r['method_note']}"]
    if r["warnings"]:
        lines += ["", "Warnings:"] + [f"  - {w}" for w in r["warnings"]]
    lines += ["", f"NOTE: {r['disclaimer']}"]
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Sample size and power for two-proportion, two-mean, and log-rank designs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--input", required=True, help="Path to the JSON power spec")
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
        out = json.dumps(report, indent=2) if args.format == "json" else render_text(report)
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
