#!/usr/bin/env python3
"""Size an A/B test: sample size per arm, power, and test duration.

Covers a two-proportion test (conversion-style metrics) and a difference in
means (revenue, time on page). Uses the normal approximation with the inverse
normal from statistics.NormalDist, so it needs nothing beyond the standard
library. With more than two arms each treatment is compared with control and
alpha is Bonferroni-adjusted.

Usage:
    python3 experiment_designer.py --metric proportion --baseline 0.10 --mde 0.02
    python3 experiment_designer.py --input ../assets/experiment_design.json
    python3 experiment_designer.py --metric mean --baseline 42 --std-dev 30 \
        --mde 0.05 --mde-type relative --daily-traffic 8000 --format json
"""

import argparse
import json
import math
import sys
from pathlib import Path
from statistics import NormalDist
from typing import Any, Dict, List, Optional

Z = NormalDist()
DEFAULTS: Dict[str, Any] = {
    "metric": "proportion", "baseline": None, "mde": None, "mde_type": "absolute",
    "std_dev": None, "alpha": 0.05, "power": 0.80, "sides": 2, "variants": 2,
    "sample_size": None, "daily_traffic": None, "allocation": 1.0,
}
EXAMPLE = {
    "name": "checkout-button-color", "metric": "proportion", "baseline": 0.05,
    "mde": 0.10, "mde_type": "relative", "alpha": 0.05, "power": 0.80,
    "sides": 2, "variants": 3, "daily_traffic": 20000, "allocation": 0.5,
}
MAX_DAYS = 28
MIN_DAYS = 7


def number(d: Dict[str, Any], key: str, positive: bool = False) -> Optional[float]:
    """Read one numeric field, raising a ValueError that names it."""
    v = d.get(key)
    if v is None:
        return None
    if isinstance(v, bool) or not isinstance(v, (int, float, str)):
        raise ValueError(f"{key} must be a number, got {v!r}")
    try:
        x = float(v)
    except ValueError:
        raise ValueError(f"{key} must be a number, got {v!r}") from None
    if not math.isfinite(x) or (positive and x <= 0):
        raise ValueError(f"{key} must be a {'positive ' if positive else ''}finite number, got {v!r}")
    return x


def resolve(design: Dict[str, Any]) -> Dict[str, Any]:
    """Validate the design and add the treatment value and effect size."""
    d = {**DEFAULTS, **{k: v for k, v in design.items() if v is not None}}
    for key in ("baseline", "mde", "alpha", "power", "allocation"):
        d[key] = number(d, key)
    for key in ("std_dev", "daily_traffic", "sample_size", "variants", "sides"):
        d[key] = number(d, key, positive=True)
    if d["baseline"] is None or d["mde"] is None:
        raise ValueError("baseline and mde are required")
    if d["sample_size"] is not None and d["sample_size"] != int(d["sample_size"]):
        raise ValueError("sample_size must be a whole number")
    if d["metric"] not in ("proportion", "mean"):
        raise ValueError("metric must be 'proportion' or 'mean'")
    if d["mde_type"] not in ("absolute", "relative"):
        raise ValueError("mde_type must be 'absolute' or 'relative'")
    if not 0 < d["alpha"] < 1 or not 0 < d["power"] < 1:
        raise ValueError("alpha and power must be between 0 and 1")
    if d["sides"] not in (1, 2) or d["variants"] != int(d["variants"]) or d["variants"] < 2:
        raise ValueError("sides must be 1 or 2 and variants at least 2")
    if not 0 < d["allocation"] <= 1:
        raise ValueError("allocation must be in (0, 1]")
    base, mde = float(d["baseline"]), float(d["mde"])
    delta = mde * base if d["mde_type"] == "relative" else mde
    if delta == 0:
        raise ValueError("the minimum detectable effect works out to zero")
    if d["metric"] == "proportion":
        if not 0 < base < 1 or not 0 < base + delta < 1:
            raise ValueError("baseline and baseline + effect must be rates in (0, 1)")
    elif d["std_dev"] is None:
        raise ValueError("a mean metric needs a positive std_dev")
    d.update(baseline=base, mde=mde, delta=delta, treatment=base + delta, sides=int(d["sides"]),
             variants=int(d["variants"]), comparisons=int(d["variants"]) - 1)
    d["alpha_adjusted"] = d["alpha"] / d["comparisons"]
    return d


def z_alpha(alpha: float, sides: int) -> float:
    """Critical value for the given significance level and sidedness."""
    return Z.inv_cdf(1 - alpha / sides)


def spread(d: Dict[str, Any]) -> tuple:
    """Return (sd under H0, sd under H1) for one unit of per-arm sample."""
    if d["metric"] == "mean":
        sd = d["std_dev"] * math.sqrt(2)
        return sd, sd
    p1, p2 = d["baseline"], d["treatment"]
    pbar = (p1 + p2) / 2
    return math.sqrt(2 * pbar * (1 - pbar)), math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))


def sample_size(d: Dict[str, Any], alpha: float) -> int:
    """Per-arm sample size needed to reach the target power."""
    s0, s1 = spread(d)
    za, zb = z_alpha(alpha, d["sides"]), Z.inv_cdf(d["power"])
    return math.ceil(((za * s0 + zb * s1) / abs(d["delta"])) ** 2)


def power_at(d: Dict[str, Any], n: int, alpha: float) -> float:
    """Power of the test with n units per arm."""
    s0, s1 = spread(d)
    return Z.cdf((abs(d["delta"]) * math.sqrt(n) - z_alpha(alpha, d["sides"]) * s0) / s1)


def design_experiment(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Compute the full design: sizes, power, duration and warnings."""
    d = resolve(raw)
    warnings: List[str] = []
    n_unadj = sample_size(d, d["alpha"])
    n_req = sample_size(d, d["alpha_adjusted"])
    n_used = int(d["sample_size"]) if d["sample_size"] else n_req
    achieved = power_at(d, n_used, d["alpha_adjusted"])
    result: Dict[str, Any] = {
        "name": raw.get("name"), "metric": d["metric"],
        "baseline": d["baseline"], "treatment": round(d["treatment"], 6),
        "absolute_effect": round(d["delta"], 6),
        "relative_effect": round(d["delta"] / d["baseline"], 4) if d["baseline"] else None,
        "alpha": d["alpha"], "sides": d["sides"], "target_power": d["power"],
        "variants": d["variants"], "comparisons": d["comparisons"],
        "alpha_per_comparison": round(d["alpha_adjusted"], 6),
        "sample_size_per_arm_unadjusted": n_unadj,
        "sample_size_per_arm_required": n_req,
        "sample_size_per_arm_used": n_used,
        "total_sample_size": n_used * d["variants"],
        "achieved_power": round(achieved, 4),
        "std_dev": d["std_dev"] if d["metric"] == "mean" else None,
    }
    if d["comparisons"] > 1:
        warnings.append(f"Bonferroni: {d['comparisons']} comparisons against control, so each "
                        f"is tested at alpha {d['alpha_adjusted']:.4f}. Per-arm size rises "
                        f"from {n_unadj:,} to {n_req:,}.")
    if achieved < 0.8:
        warnings.append(f"Underpowered: {achieved:.0%} power at {n_used:,} per arm. "
                        f"A real effect of this size would be missed {1 - achieved:.0%} of the time.")
    if d["daily_traffic"]:
        per_day = float(d["daily_traffic"]) * d["allocation"]
        days = math.ceil(result["total_sample_size"] / per_day)
        result.update(daily_traffic=d["daily_traffic"], allocation=d["allocation"],
                      units_per_arm_per_day=round(per_day / d["variants"], 1),
                      duration_days=days, duration_weeks=round(days / 7, 1))
        if days > MAX_DAYS:
            warnings.append(f"Very long test: {days} days. Raise allocation, cut arms, or "
                            "accept a larger MDE. Long tests drift with seasonality and cookie churn.")
        elif days < MIN_DAYS:
            warnings.append(f"Only {days} day(s) of traffic needed. Run at least {MIN_DAYS} days "
                            "to cover a full weekly cycle and dampen novelty effects.")
    if d["metric"] == "proportion" and d["baseline"] < 0.01:
        warnings.append("Baseline below 1%: the normal approximation is rough here. "
                        "Treat the size as a lower bound.")
    result["warnings"] = warnings
    return result


def output(r: Dict[str, Any], fmt: str) -> None:
    """Print the design as JSON or as a readable report."""
    if fmt == "json":
        print(json.dumps(r, indent=2))
        return
    unit = "rate" if r["metric"] == "proportion" else "mean"
    rel = f", {r['relative_effect']:+.1%} relative" if r["relative_effect"] is not None else ""
    rows = [
        ("Metric", f"{r['metric']} ({'two' if r['sides'] == 2 else 'one'}-sided)"),
        (f"Baseline {unit}", f"{r['baseline']:g}"),
        (f"Treatment {unit}", f"{r['treatment']:g} (effect {r['absolute_effect']:+g}{rel})"),
        ("Std dev", f"{r['std_dev']:g}" if r["std_dev"] else None),
        ("Alpha / power", f"{r['alpha']:g} / {r['target_power']:g} "
                          f"(alpha per comparison {r['alpha_per_comparison']:g})"),
        ("Arms", f"{r['variants']} ({r['comparisons']} vs control)"),
        ("Required per arm", f"{r['sample_size_per_arm_required']:,} "
                             f"(unadjusted {r['sample_size_per_arm_unadjusted']:,})"),
        ("Planned per arm", f"{r['sample_size_per_arm_used']:,} -> power {r['achieved_power']:.1%}"),
        ("Total sample", f"{r['total_sample_size']:,}"),
    ]
    if "duration_days" in r:
        rows.append(("Duration", f"{r['duration_days']} day(s) ({r['duration_weeks']} weeks) at "
                                 f"{r['daily_traffic']:,.0f}/day x {r['allocation']:.0%} allocation"))
    print(f"Experiment design{' - ' + r['name'] if r['name'] else ''}")
    for label, value in rows:
        if value is not None:
            print(f"  {label + ':':<19} {value}")
    for w in r["warnings"]:
        print(f"  WARNING: {w}")


def main() -> None:
    """Parse arguments, merge the design file with flags, and report."""
    p = argparse.ArgumentParser(description="Size an A/B test: per-arm sample size, power and "
                                "duration for a two-proportion or difference-in-means test.")
    p.add_argument("--input", "-i", help="design JSON file (see --example); flags override it")
    p.add_argument("--metric", choices=["proportion", "mean"], help="metric type (default proportion)")
    p.add_argument("--baseline", type=float, help="control rate (0-1) or control mean")
    p.add_argument("--mde", type=float, help="minimum detectable effect")
    p.add_argument("--mde-type", choices=["absolute", "relative"],
                   help="absolute (0.02 = 2pp) or relative (0.10 = +10%%); default absolute")
    p.add_argument("--std-dev", type=float, help="standard deviation of the metric (mean only)")
    p.add_argument("--alpha", type=float, help="significance level (default 0.05)")
    p.add_argument("--power", type=float, help="target power (default 0.80)")
    p.add_argument("--sides", type=int, choices=[1, 2], help="one- or two-sided test (default 2)")
    p.add_argument("--variants", type=int, help="number of arms including control (default 2)")
    p.add_argument("--sample-size", type=int, help="fixed per-arm size; reports the power it buys")
    p.add_argument("--daily-traffic", type=float, help="eligible units per day, for duration")
    p.add_argument("--allocation", type=float, help="share of traffic in the test (default 1.0)")
    p.add_argument("--output", "-o", help="directory to write experiment_design.json into")
    p.add_argument("--force", action="store_true", help="overwrite an existing file in --output")
    p.add_argument("--format", choices=["text", "json"], default="text", help="output format")
    p.add_argument("--example", action="store_true", help="print a sample design JSON and exit")
    args = p.parse_args()
    if args.example:
        print(json.dumps(EXAMPLE, indent=2))
        return
    design: Dict[str, Any] = {}
    if args.input:
        try:
            design = json.loads(Path(args.input).read_text(encoding="utf-8"))
        except FileNotFoundError:
            sys.exit(f"ERROR: file not found: {args.input}")
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            sys.exit(f"ERROR: {args.input} is not valid JSON: {exc}")
        if not isinstance(design, dict):
            sys.exit(f"ERROR: {args.input} must hold a JSON object")
    target = Path(args.output) / "experiment_design.json" if args.output else None
    if target and target.exists() and not args.force:
        sys.exit(f"ERROR: {target} already exists; pass --force to overwrite")
    flags = {k: v for k, v in vars(args).items()
             if k not in ("input", "output", "format", "example", "force") and v is not None}
    try:
        result = design_experiment({**design, **flags})
    except (ValueError, TypeError) as exc:
        sys.exit(f"ERROR: {exc}")
    except OverflowError:
        sys.exit("ERROR: the required sample size is too large to compute; "
                 "check that mde is not tiny relative to the baseline or std_dev")
    output(result, args.format)
    if target:
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        except OSError as exc:
            sys.exit(f"ERROR: cannot write {target}: {exc}")
        print(f"Wrote {target}", file=sys.stderr)


if __name__ == "__main__":
    main()
