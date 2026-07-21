#!/usr/bin/env python3
"""Scoring internals for calibration_scorer.py — loading, statistics, reading.

Everything here turns raw prediction records into numbers, plus the thresholds
that say when a number means something. The companion CLI (calibration_scorer.py)
orchestrates these, renders them, and verifies them. Helper module: imported by
its sibling, not run directly.
Deterministic: no clock reads, no network, no randomness.
"""

import json
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
