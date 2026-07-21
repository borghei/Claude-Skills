#!/usr/bin/env python3
"""Score forecast calibration from a log of resolved predictions.

Computes the Brier score, its Murphy decomposition (reliability, resolution,
uncertainty), a bucketed calibration table, and a skill score against the
always-guess-the-base-rate baseline. Answers the only question that matters for
reflection: were you right as often as you thought you would be?
Deterministic: no clock reads, no network, no randomness.

Usage:
    python3 calibration_scorer.py --input assets/sample_predictions.json
    python3 calibration_scorer.py --input preds.json --buckets 5 --format json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# A gap this large between stated confidence and observed hit rate is a real bias,
# not sampling noise, once a bucket holds enough predictions.
MEANINGFUL_GAP = 0.10
MIN_BUCKET_N = 5
# Below this many resolved predictions, calibration estimates are too noisy to act on.
MIN_TOTAL_N = 20


def load_predictions(path: Path) -> List[Dict[str, Any]]:
    """Load prediction records from a JSON list or an object with a 'predictions' key."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        if "predictions" not in data:
            raise ValueError(
                f"{path.name} is a JSON object with no 'predictions' key "
                f"(found: {', '.join(sorted(data)) or 'nothing'}) — expected a prediction log")
        preds = data["predictions"]
    else:
        preds = data
    if not isinstance(preds, list):
        raise ValueError("log must be a JSON list or an object with a 'predictions' list")
    if not preds:
        raise ValueError("prediction log is empty — nothing to score")
    return preds


def normalise(pred: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Validate one prediction; return None when it is not yet resolved."""
    if "confidence" not in pred:
        raise KeyError(f"prediction missing 'confidence': {pred}")
    confidence = float(pred["confidence"])
    if confidence > 1:
        confidence /= 100.0
    if not 0.0 <= confidence <= 1.0:
        raise ValueError(f"confidence must be 0-1 or 0-100: {pred}")
    outcome = pred.get("outcome")
    if outcome is None or (isinstance(outcome, str) and outcome.lower() in {"unresolved", "pending", ""}):
        return None
    if isinstance(outcome, str):
        outcome = outcome.lower() in {"true", "yes", "hit", "correct", "1"}
    return {
        "id": str(pred.get("id", "?")),
        "statement": str(pred.get("statement", "")),
        "domain": str(pred.get("domain", "general")),
        "confidence": confidence,
        "outcome": 1.0 if outcome else 0.0,
        # Unrounded: this feeds the aggregate Brier and therefore the identity.
        "brier": (confidence - (1.0 if outcome else 0.0)) ** 2,
    }


def bucket_index(confidence: float, buckets: int) -> int:
    """Map a confidence value to a bucket index, clamping the top edge."""
    return min(int(confidence * buckets), buckets - 1)


def calibration_table(preds: List[Dict[str, Any]], buckets: int) -> List[Dict[str, Any]]:
    """Group predictions by stated confidence and compare to observed hit rate."""
    grouped: Dict[int, List[Dict[str, Any]]] = {}
    for pred in preds:
        grouped.setdefault(bucket_index(pred["confidence"], buckets), []).append(pred)

    rows: List[Dict[str, Any]] = []
    width = 1.0 / buckets
    for index in sorted(grouped):
        group = grouped[index]
        mean_conf = sum(p["confidence"] for p in group) / len(group)
        observed = sum(p["outcome"] for p in group) / len(group)
        gap = mean_conf - observed
        rows.append({
            "range": f"{index * width:.0%}-{(index + 1) * width:.0%}",
            "n": len(group),
            "mean_confidence": round(mean_conf, 3),
            "observed_rate": round(observed, 3),
            "gap": round(gap, 3),
            "verdict": bucket_verdict(gap, len(group)),
        })
    return rows


def bucket_verdict(gap: float, n: int) -> str:
    """Label a bucket as over/under-confident, calibrated, or too small to judge."""
    if n < MIN_BUCKET_N:
        return "too-few"
    if gap > MEANINGFUL_GAP:
        return "overconfident"
    if gap < -MEANINGFUL_GAP:
        return "underconfident"
    return "calibrated"


def murphy_decomposition(preds: List[Dict[str, Any]]) -> Tuple[float, float, float]:
    """Split the Brier score into reliability, resolution, and uncertainty.

    Groups by distinct forecast value, not by display bucket. The identity
    BS = REL - RES + UNC holds exactly only under a partition by distinct
    confidence; coarser bins discard within-bin variance and the identity
    stops closing. This is deliberately independent of --buckets, so a
    readability setting cannot perturb the statistics.
    """
    total = len(preds)
    base_rate = sum(p["outcome"] for p in preds) / total
    grouped: Dict[float, List[float]] = {}
    for pred in preds:
        grouped.setdefault(pred["confidence"], []).append(pred["outcome"])

    reliability = 0.0
    resolution = 0.0
    for confidence, outcomes in grouped.items():
        weight = len(outcomes) / total
        observed = sum(outcomes) / len(outcomes)
        reliability += weight * (confidence - observed) ** 2
        resolution += weight * (observed - base_rate) ** 2
    return reliability, resolution, base_rate * (1 - base_rate)


def domain_breakdown(preds: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Brier score and confidence gap per prediction domain."""
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for pred in preds:
        grouped.setdefault(pred["domain"], []).append(pred)
    rows = []
    for domain, group in grouped.items():
        mean_conf = sum(p["confidence"] for p in group) / len(group)
        observed = sum(p["outcome"] for p in group) / len(group)
        rows.append({
            "domain": domain,
            "n": len(group),
            "brier": round(sum(p["brier"] for p in group) / len(group), 4),
            "gap": round(mean_conf - observed, 3),
        })
    return sorted(rows, key=lambda r: -r["brier"])


def interpret(brier: float, gap: float, total: int, skill: float) -> List[str]:
    """Turn the numbers into statements about what to change."""
    notes: List[str] = []
    if total < MIN_TOTAL_N:
        notes.append(
            f"Only {total} resolved predictions — below {MIN_TOTAL_N}, calibration estimates are "
            "too noisy to act on. Keep logging before drawing conclusions.")
    if gap > MEANINGFUL_GAP:
        notes.append(
            f"Overconfident by {gap:.0%} overall. The standard correction is to shade every stated "
            "confidence toward 50% by roughly that margin, then re-measure in a quarter.")
    elif gap < -MEANINGFUL_GAP:
        notes.append(
            f"Underconfident by {abs(gap):.0%} overall — you know more than you claim. This costs "
            "you decisiveness; state the confidence you actually hold.")
    else:
        notes.append(f"Well calibrated overall (gap {gap:+.0%}). Stated confidence can be trusted as an input to decisions.")
    if skill <= 0:
        notes.append(
            "Skill score at or below zero: these forecasts carry no more information than always "
            "predicting the base rate. Check whether the predictions are specific enough to be wrong.")
    elif skill < 0.15:
        notes.append(f"Skill score {skill:.2f} — barely beating the base rate. Predictions may be too safe to be useful.")
    if brier < 0.15:
        notes.append(f"Brier {brier:.3f} is strong; the main gains left are in resolution, not reliability.")
    return notes


def analyse(raw: List[Dict[str, Any]], buckets: int) -> Dict[str, Any]:
    """Score the prediction log end to end."""
    resolved = [p for p in (normalise(r) for r in raw) if p is not None]
    if not resolved:
        raise ValueError("no resolved predictions found — every entry is still pending")
    total = len(resolved)
    brier = sum(p["brier"] for p in resolved) / total
    rows = calibration_table(resolved, buckets)
    reliability, resolution, uncertainty = murphy_decomposition(resolved)
    base_rate = sum(p["outcome"] for p in resolved) / total
    baseline = base_rate * (1 - base_rate)
    skill = (baseline - brier) / baseline if baseline else 0.0
    gap = sum(p["confidence"] for p in resolved) / total - base_rate

    return {
        "resolved": total,
        "unresolved": len(raw) - total,
        # The four identity participants keep full precision so that
        # BS = REL - RES + UNC verifies exactly in the emitted JSON.
        "brier_score": brier,
        "reliability": reliability,
        "resolution": resolution,
        "uncertainty": uncertainty,
        "identity_residual": brier - (reliability - resolution + uncertainty),
        "base_rate": round(base_rate, 3),
        "mean_confidence": round(sum(p["confidence"] for p in resolved) / total, 3),
        "overall_gap": round(gap, 3),
        "skill_score": round(skill, 3),
        "calibration": rows,
        "by_domain": domain_breakdown(resolved),
        "worst_calls": sorted(resolved, key=lambda p: -p["brier"])[:5],
        "interpretation": interpret(brier, gap, total, skill),
    }


def output(report: Dict[str, Any], fmt: str) -> None:
    """Print the calibration report as text or JSON."""
    if fmt == "json":
        print(json.dumps(report, indent=2))
        return
    print(f"Calibration — {report['resolved']} resolved, {report['unresolved']} pending")
    print(f"Brier {report['brier_score']:.3f} (lower is better; 0.25 = coin flip) | "
          f"skill vs base rate {report['skill_score']:+.2f}")
    print(f"Mean confidence {report['mean_confidence']:.0%} vs actual hit rate "
          f"{report['base_rate']:.0%} — gap {report['overall_gap']:+.0%}")
    print(f"Decomposition: reliability {report['reliability']:.3f} (miscalibration, lower better) | "
          f"resolution {report['resolution']:.3f} (discrimination, higher better)")
    print("-" * 64)
    print(f"{'stated':<12}{'n':>4}{'said':>8}{'actual':>9}{'gap':>8}  verdict")
    for row in report["calibration"]:
        print(f"{row['range']:<12}{row['n']:>4}{row['mean_confidence']:>8.0%}"
              f"{row['observed_rate']:>9.0%}{row['gap']:>+8.0%}  {row['verdict']}")
    print("\nBy domain:")
    for row in report["by_domain"]:
        print(f"  {row['domain']:<18} n={row['n']:<4} brier={row['brier']:.3f}  gap={row['gap']:+.0%}")
    print("\nWorst calls:")
    for pred in report["worst_calls"]:
        said = "yes" if pred["confidence"] >= 0.5 else "no"
        happened = "yes" if pred["outcome"] else "no"
        print(f"  [{pred['id']}] {pred['confidence']:.0%} ({said}) -> {happened}: {pred['statement']}")
    print("\nInterpretation:")
    for note in report["interpretation"]:
        print(f"  - {note}")


def residual_of(report: Dict[str, Any]) -> float:
    """Absolute departure from the identity BS = REL - RES + UNC."""
    return abs(report["brier_score"] - (report["reliability"]
               - report["resolution"] + report["uncertainty"]))


def selftest(sample: Path) -> int:
    """Verify scoring invariants against the shipped sample. Returns an exit code."""
    r = analyse(load_predictions(sample), 5)
    bs, rel, res, unc = (r["brier_score"], r["reliability"], r["resolution"], r["uncertainty"])
    at10 = analyse(load_predictions(sample), 10)
    perfect = analyse([{"id": "a", "confidence": 1.0, "outcome": True},
                       {"id": "b", "confidence": 0.0, "outcome": False}], 5)
    pct = analyse([{"id": "a", "confidence": 80, "outcome": True}], 5)
    # Confidences off the 5% grid: guards against any value feeding the identity being rounded.
    odd = analyse([{"id": "a", "confidence": 1 / 3, "outcome": True},
                   {"id": "b", "confidence": 1 / 3, "outcome": False},
                   {"id": "c", "confidence": 0.777, "outcome": True}], 5)

    checks: List[Tuple[str, bool, str]] = [
        ("Murphy identity BS = REL - RES + UNC", residual_of(r) < 1e-9, f"residual={residual_of(r):.2e}"),
        ("identity holds off the 5% grid", residual_of(odd) < 1e-9, f"residual={residual_of(odd):.2e}"),
        ("decomposition invariant to --buckets",
         abs(rel - at10["reliability"]) < 1e-12 and abs(res - at10["resolution"]) < 1e-12,
         f"rel {rel:.6f} vs {at10['reliability']:.6f}"),
        ("reliability non-negative", rel >= 0, f"rel={rel:.6f}"),
        ("resolution non-negative", res >= 0, f"res={res:.6f}"),
        ("Brier within [0,1]", 0.0 <= bs <= 1.0, f"brier={bs:.6f}"),
        ("uncertainty = p(1-p)", abs(unc - r["base_rate"] * (1 - r["base_rate"])) < 1e-3, ""),
        ("unresolved excluded from scoring", r["resolved"] == 27 and r["unresolved"] == 3,
         f"{r['resolved']} resolved / {r['unresolved']} pending"),
        ("calibration rows sum to resolved",
         sum(x["n"] for x in r["calibration"]) == r["resolved"], ""),
        ("skill score = (UNC - BS) / UNC",
         abs(r["skill_score"] - round((unc - bs) / unc, 3)) < 1e-9, ""),
        ("perfect forecaster scores 0",
         abs(perfect["brier_score"]) < 1e-12 and abs(perfect["reliability"]) < 1e-12, ""),
        ("percentage confidence normalised", abs(pct["brier_score"] - 0.04) < 1e-12,
         f"brier={pct['brier_score']:.6f}"),
    ]

    failed = [c for c in checks if not c[1]]
    for name, passed, detail in checks:
        print(f"  {'PASS' if passed else 'FAIL'}  {name}" + (f"  ({detail})" if detail else ""))
    print(f"\n{len(checks) - len(failed)}/{len(checks)} invariants hold")
    if failed:
        sys.stdout.flush()  # keep the failure line ordered after the check list
        print(f"SELFTEST FAILED — {len(failed)} invariant(s) broken", file=sys.stderr)
        return 1
    print(f"Reference values: brier={bs:.6f} reliability={rel:.6f} "
          f"resolution={res:.6f} uncertainty={unc:.6f}")
    return 0


def main() -> None:
    """Parse arguments, score the prediction log, and emit the report."""
    parser = argparse.ArgumentParser(
        description="Score prediction calibration with Brier score and a bucketed table.",
    )
    parser.add_argument("--input", help="Path to the JSON prediction log (required unless --selftest)")
    parser.add_argument("--selftest", action="store_true",
                        help="Verify scoring invariants against the shipped sample and exit")
    parser.add_argument("--buckets", type=int, default=10, help="Number of confidence buckets (default: 10)")
    parser.add_argument("--domain", help="Score only predictions in this domain")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format (default: text)")
    args = parser.parse_args()

    try:
        if args.selftest:
            sample = Path(__file__).resolve().parent.parent / "assets" / "sample_predictions.json"
            if not sample.exists():
                raise FileNotFoundError(f"shipped sample missing: {sample}")
            sys.exit(selftest(sample))
        if not args.input:
            raise ValueError("--input is required (or pass --selftest)")
        path = Path(args.input)
        if not path.exists():
            raise FileNotFoundError(f"prediction log not found: {path}")
        if not 2 <= args.buckets <= 20:
            raise ValueError("--buckets must be between 2 and 20")
        preds = load_predictions(path)
        if args.domain:
            preds = [p for p in preds if str(p.get("domain", "general")) == args.domain]
            if not preds:
                raise ValueError(f"no predictions found in domain {args.domain!r}")
        output(analyse(preds, args.buckets), args.format)
    except (OSError, ValueError, KeyError, TypeError, ZeroDivisionError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
