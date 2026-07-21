#!/usr/bin/env python3
"""Compare two agent eval runs and surface regressions.

Consumes two JSON reports produced by scenario_runner.py --format json and
reports fixed / regressed / stable scenarios, pass-rate movement with a
Wilson interval, an exact McNemar test on the paired discordant scenarios,
and cost / latency drift per scenario.

Usage:
    python3 eval_diff.py --baseline before.json --candidate after.json
    python3 eval_diff.py --baseline before.json --candidate after.json \
        --format json --drift-threshold 0.15
"""

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

Z_95 = 1.959963985


def load_report(path: Path) -> Dict[str, Any]:
    """Load a scenario_runner JSON report, exiting on malformed input."""
    try:
        with path.open(encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError:
        print(f"ERROR: file not found: {path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"ERROR: {path} is not valid JSON (line {exc.lineno}): {exc.msg}",
              file=sys.stderr)
        sys.exit(1)
    if "results" not in data:
        print(f"ERROR: {path} has no 'results' key — expected the JSON output of "
              "scenario_runner.py --format json.", file=sys.stderr)
        sys.exit(1)
    return data


def wilson_interval(successes: int, total: int) -> Tuple[float, float]:
    """Return the 95% Wilson score interval for a binomial proportion."""
    if total == 0:
        return (0.0, 0.0)
    phat = successes / total
    denom = 1 + Z_95 ** 2 / total
    centre = (phat + Z_95 ** 2 / (2 * total)) / denom
    margin = Z_95 * math.sqrt(
        phat * (1 - phat) / total + Z_95 ** 2 / (4 * total ** 2)) / denom
    return (max(0.0, centre - margin), min(1.0, centre + margin))


def mcnemar_exact(regressions: int, fixes: int) -> float:
    """Exact two-sided McNemar p-value over the discordant scenario pairs.

    Uses the binomial(n, 0.5) distribution on the b+c discordant pairs, which
    is the correct test at the sample sizes typical of agent eval suites.
    """
    n = regressions + fixes
    if n == 0:
        return 1.0
    k = min(regressions, fixes)
    tail = sum(math.comb(n, i) for i in range(0, k + 1)) / (2 ** n)
    return min(1.0, 2 * tail)


def index_results(report: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Index a report's scenario results by scenario_id."""
    return {str(r.get("scenario_id")): r for r in report.get("results", [])}


def classify(baseline: Dict[str, Any], candidate: Dict[str, Any],
             drift_threshold: float) -> Dict[str, Any]:
    """Diff two indexed runs into per-scenario transitions and drift."""
    before = index_results(baseline)
    after = index_results(candidate)
    all_ids = sorted(set(before) | set(after))

    transitions: List[Dict[str, Any]] = []
    for scenario_id in all_ids:
        was = before.get(scenario_id)
        now = after.get(scenario_id)
        if was is None:
            label = "new"
        elif now is None:
            label = "dropped"
        elif was["status"] == "pass" and now["status"] != "pass":
            label = "regressed"
        elif was["status"] != "pass" and now["status"] == "pass":
            label = "fixed"
        elif now["status"] == "pass":
            label = "stable-pass"
        else:
            label = "stable-fail"

        cost_delta = latency_delta = 0.0
        cost_pct = latency_pct = 0.0
        if was and now:
            cost_delta = now.get("cost_usd", 0.0) - was.get("cost_usd", 0.0)
            latency_delta = now.get("latency_ms", 0.0) - was.get("latency_ms", 0.0)
            if was.get("cost_usd"):
                cost_pct = cost_delta / was["cost_usd"]
            if was.get("latency_ms"):
                latency_pct = latency_delta / was["latency_ms"]

        failing_now = []
        if now:
            failing_now = [a["type"] for a in now.get("assertions", [])
                           if not a.get("passed")]

        transitions.append({
            "scenario_id": scenario_id,
            "transition": label,
            "failing_assertions": failing_now,
            "cost_delta_usd": round(cost_delta, 5),
            "cost_drift_pct": round(cost_pct, 4),
            "latency_delta_ms": round(latency_delta, 1),
            "latency_drift_pct": round(latency_pct, 4),
            "budget_drift": abs(cost_pct) >= drift_threshold
            or abs(latency_pct) >= drift_threshold,
        })

    return {"transitions": transitions}


def summarize(baseline: Dict[str, Any], candidate: Dict[str, Any],
              diff: Dict[str, Any]) -> Dict[str, Any]:
    """Build the aggregate verdict, including the paired significance test."""
    transitions = diff["transitions"]
    regressed = [t for t in transitions if t["transition"] == "regressed"]
    fixed = [t for t in transitions if t["transition"] == "fixed"]

    b_pass = baseline.get("scenarios_passed", 0)
    b_total = baseline.get("scenarios_total", 0)
    c_pass = candidate.get("scenarios_passed", 0)
    c_total = candidate.get("scenarios_total", 0)

    p_value = mcnemar_exact(len(regressed), len(fixed))
    discordant = len(regressed) + len(fixed)

    if discordant == 0:
        guidance = "No scenario changed status. Nothing to test."
    elif discordant < 6:
        guidance = (f"Only {discordant} scenarios changed status. At this size no "
                    "p-value is informative — read the individual regressions "
                    "rather than the aggregate.")
    elif p_value < 0.05:
        guidance = (f"p={p_value:.3f} over {discordant} discordant scenarios: the "
                    "shift is unlikely to be run-to-run noise.")
    else:
        guidance = (f"p={p_value:.3f} over {discordant} discordant scenarios: "
                    "consistent with noise. Re-run both arms before concluding.")

    verdict = "regression" if regressed else ("improvement" if fixed else "no-change")
    return {
        "baseline_run": baseline.get("run_id"),
        "candidate_run": candidate.get("run_id"),
        "baseline_model": baseline.get("model"),
        "candidate_model": candidate.get("model"),
        "baseline_pass_rate": round(b_pass / b_total, 4) if b_total else 0.0,
        "candidate_pass_rate": round(c_pass / c_total, 4) if c_total else 0.0,
        "baseline_ci95": [round(v, 4) for v in wilson_interval(b_pass, b_total)],
        "candidate_ci95": [round(v, 4) for v in wilson_interval(c_pass, c_total)],
        "regressed": len(regressed),
        "fixed": len(fixed),
        "mcnemar_p": round(p_value, 5),
        "significance_guidance": guidance,
        "cost_delta_usd": round(candidate.get("total_cost_usd", 0.0)
                                - baseline.get("total_cost_usd", 0.0), 5),
        "latency_delta_ms": round(candidate.get("mean_latency_ms", 0.0)
                                  - baseline.get("mean_latency_ms", 0.0), 1),
        "verdict": verdict,
        "transitions": transitions,
    }


def output(report: Dict[str, Any], fmt: str) -> None:
    """Print the diff as JSON or human-readable text."""
    if fmt == "json":
        print(json.dumps(report, indent=2))
        return
    print(f"Baseline : {report['baseline_run']} ({report['baseline_model']})  "
          f"pass {report['baseline_pass_rate'] * 100:.1f}% "
          f"CI[{report['baseline_ci95'][0] * 100:.0f}-{report['baseline_ci95'][1] * 100:.0f}%]")
    print(f"Candidate: {report['candidate_run']} ({report['candidate_model']})  "
          f"pass {report['candidate_pass_rate'] * 100:.1f}% "
          f"CI[{report['candidate_ci95'][0] * 100:.0f}-{report['candidate_ci95'][1] * 100:.0f}%]")
    print("=" * 68)
    for label, header in (("regressed", "REGRESSED"), ("fixed", "FIXED"),
                          ("new", "NEW"), ("dropped", "DROPPED")):
        rows = [t for t in report["transitions"] if t["transition"] == label]
        if not rows:
            continue
        print(f"{header} ({len(rows)})")
        for row in rows:
            failing = ", ".join(row["failing_assertions"][:3]) or "-"
            print(f"  - {row['scenario_id']}: {failing}")
    drift = [t for t in report["transitions"] if t["budget_drift"]]
    if drift:
        print(f"BUDGET DRIFT ({len(drift)})")
        for row in drift:
            print(f"  - {row['scenario_id']}: cost {row['cost_drift_pct'] * 100:+.1f}%, "
                  f"latency {row['latency_drift_pct'] * 100:+.1f}%")
    print("-" * 68)
    print(f"Verdict: {report['verdict']}  "
          f"(+{report['fixed']} fixed / -{report['regressed']} regressed)")
    print(f"Cost delta: ${report['cost_delta_usd']:+.4f}   "
          f"Mean latency delta: {report['latency_delta_ms']:+.0f}ms")
    print(f"Significance: {report['significance_guidance']}")


def main() -> None:
    """Parse arguments, diff the two runs, and emit the report."""
    parser = argparse.ArgumentParser(
        description="Compare two agent eval runs and surface regressions.")
    parser.add_argument("--baseline", required=True,
                        help="Path to the baseline scenario_runner JSON report.")
    parser.add_argument("--candidate", required=True,
                        help="Path to the candidate scenario_runner JSON report.")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text).")
    parser.add_argument("--drift-threshold", type=float, default=0.20,
                        help="Relative cost/latency change that counts as drift "
                             "(default: 0.20 = 20%%).")
    parser.add_argument("--fail-on-regression", action="store_true",
                        help="Exit 2 if any scenario regressed.")
    args = parser.parse_args()

    baseline = load_report(Path(args.baseline))
    candidate = load_report(Path(args.candidate))
    diff = classify(baseline, candidate, args.drift_threshold)
    report = summarize(baseline, candidate, diff)
    output(report, args.format)

    if args.fail_on_regression and report["regressed"]:
        sys.exit(2)


if __name__ == "__main__":
    main()
