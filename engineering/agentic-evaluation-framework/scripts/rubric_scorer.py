#!/usr/bin/env python3
"""
rubric_scorer.py — score LLM/agent outputs against a weighted rubric.

Reads a JSON file of per-criterion scores that you (or your judges) already
collected, then computes:
  * per-item weighted totals and per-criterion means across graders
  * pass/fail vs per-criterion thresholds and an overall pass threshold
  * a simple inter-rater agreement metric (exact-agreement rate and a
    deviation-based normalized agreement) so you can tell whether your
    graders — human or model — actually agree.

This tool does NOT call any model. It only aggregates scores you provide.

Input JSON shape:
{
  "criteria": [
    {"name": "accuracy",    "weight": 0.5, "threshold": 3.0, "scale_max": 5},
    {"name": "helpfulness", "weight": 0.3, "threshold": 3.0, "scale_max": 5},
    {"name": "safety",      "weight": 0.2, "threshold": 4.0, "scale_max": 5}
  ],
  "pass_threshold": 3.5,
  "items": [
    {
      "id": "item-1",
      "scores": {
        "accuracy":    {"judgeA": 4, "judgeB": 5},
        "helpfulness": {"judgeA": 3, "judgeB": 4},
        "safety":      {"judgeA": 5, "judgeB": 5}
      }
    }
  ]
}

Notes:
  * weights are normalized automatically if they do not sum to 1.0.
  * a criterion may carry a single score (one grader) or many (panel).
  * "scale_max" is per-criterion and only used to normalize the agreement
    metric; defaults to the max observed score for that criterion.
"""
import argparse
import json
import sys
from statistics import mean


def _load(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _grader_values(cell):
    """Accept either a dict {grader: score} or a bare number / list."""
    if isinstance(cell, dict):
        return [float(v) for v in cell.values()]
    if isinstance(cell, (list, tuple)):
        return [float(v) for v in cell]
    return [float(cell)]


def _cell_mean(cell):
    vals = _grader_values(cell)
    return mean(vals) if vals else 0.0


def score(data):
    criteria = data["criteria"]
    names = [c["name"] for c in criteria]
    raw_weights = {c["name"]: float(c.get("weight", 1.0)) for c in criteria}
    wsum = sum(raw_weights.values()) or 1.0
    weights = {k: v / wsum for k, v in raw_weights.items()}
    thresholds = {c["name"]: c.get("threshold") for c in criteria}
    pass_threshold = data.get("pass_threshold")

    # scale_max per criterion (for agreement normalization)
    scale_max = {}
    for c in criteria:
        if c.get("scale_max") is not None:
            scale_max[c["name"]] = float(c["scale_max"])

    items_out = []
    # accumulators for inter-rater agreement
    agree_cells = 0          # multi-grader cells total
    exact_cells = 0          # cells where all graders identical
    dev_norm_sum = 0.0       # sum of normalized within-cell deviation
    dev_cells = 0
    # per-criterion accumulators
    crit_means = {n: [] for n in names}

    for item in data["items"]:
        scores = item.get("scores", {})
        per_crit = {}
        weighted = 0.0
        crit_pass = {}
        for n in names:
            if n not in scores:
                continue
            cell = scores[n]
            vals = _grader_values(cell)
            m = mean(vals)
            per_crit[n] = round(m, 4)
            crit_means[n].append(m)
            weighted += weights[n] * m
            thr = thresholds[n]
            if thr is not None:
                crit_pass[n] = m >= float(thr)
            # agreement bookkeeping (only meaningful with >=2 graders)
            if len(vals) >= 2:
                agree_cells += 1
                if max(vals) == min(vals):
                    exact_cells += 1
                rng = scale_max.get(n, max(vals) if max(vals) > 0 else 1.0)
                rng = rng or 1.0
                cell_dev = mean(abs(v - m) for v in vals)
                dev_norm_sum += cell_dev / rng
                dev_cells += 1

        overall_pass = None
        if pass_threshold is not None:
            overall_pass = weighted >= float(pass_threshold)
        # a failed mandatory criterion fails the item too
        if any(v is False for v in crit_pass.values()):
            overall_pass = False

        items_out.append({
            "id": item.get("id"),
            "weighted_total": round(weighted, 4),
            "per_criterion": per_crit,
            "criterion_pass": crit_pass,
            "pass": overall_pass,
        })

    exact_rate = (exact_cells / agree_cells) if agree_cells else None
    norm_agreement = (1.0 - dev_norm_sum / dev_cells) if dev_cells else None

    summary = {
        "n_items": len(items_out),
        "weights_normalized": {k: round(v, 4) for k, v in weights.items()},
        "mean_weighted_total": round(mean(i["weighted_total"] for i in items_out), 4) if items_out else None,
        "per_criterion_mean": {n: round(mean(v), 4) for n, v in crit_means.items() if v},
        "pass_rate": round(mean(1.0 if i["pass"] else 0.0 for i in items_out if i["pass"] is not None), 4)
        if any(i["pass"] is not None for i in items_out) else None,
        "inter_rater_agreement": {
            "multi_grader_cells": agree_cells,
            "exact_agreement_rate": round(exact_rate, 4) if exact_rate is not None else None,
            "normalized_agreement": round(norm_agreement, 4) if norm_agreement is not None else None,
        },
    }
    return {"summary": summary, "items": items_out}


def _print_human(result):
    s = result["summary"]
    print("== Rubric Scoring ==")
    print(f"items scored        : {s['n_items']}")
    print(f"mean weighted total : {s['mean_weighted_total']}")
    if s["pass_rate"] is not None:
        print(f"pass rate           : {s['pass_rate'] * 100:.1f}%")
    print("weights (normalized):")
    for k, v in s["weights_normalized"].items():
        print(f"    {k:<16} {v}")
    print("per-criterion mean  :")
    for k, v in s["per_criterion_mean"].items():
        print(f"    {k:<16} {v}")
    ira = s["inter_rater_agreement"]
    print("inter-rater agreement:")
    if ira["multi_grader_cells"]:
        print(f"    multi-grader cells   {ira['multi_grader_cells']}")
        print(f"    exact-agreement rate {ira['exact_agreement_rate']}")
        print(f"    normalized agreement {ira['normalized_agreement']}  (1.0 = perfect)")
    else:
        print("    n/a (need >=2 graders per cell)")
    print("\nper-item:")
    for it in result["items"]:
        flag = "" if it["pass"] is None else ("PASS" if it["pass"] else "FAIL")
        print(f"    {str(it['id']):<14} total={it['weighted_total']:<8} {flag}")


def main(argv=None):
    p = argparse.ArgumentParser(description="Score outputs against a weighted rubric.")
    p.add_argument("--data", required=True, help="path to rubric scores JSON")
    p.add_argument("--json", action="store_true", help="emit JSON instead of human-readable")
    args = p.parse_args(argv)

    try:
        data = _load(args.data)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: could not read --data: {exc}", file=sys.stderr)
        return 2

    if "criteria" not in data or "items" not in data:
        print("error: input JSON must contain 'criteria' and 'items'", file=sys.stderr)
        return 2

    result = score(data)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        _print_human(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
