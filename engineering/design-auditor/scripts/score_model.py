#!/usr/bin/env python3
"""
Score Model — validate an audit findings file and compute its weighted design score.

Shared layer of design_scorer.py (which adds the three grades, trend and the report).
Weights and grade bands are read from references/scoring-model.json. Run alone to check
a findings file before scoring it.

Usage:
    python score_model.py --input findings.json
    python score_model.py --input findings.json --format json

Exit codes: 0 valid, 2 missing file, invalid JSON or invalid findings.
"""

import argparse
import json
import os
import sys

_DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "references", "scoring-model.json")
with open(_DATA, "r", encoding="utf-8") as _f:
    MODEL = json.load(_f)

# 12 audit categories with weights (sum to 0.95 — 0.05 is the coherence bonus)
CATEGORIES = MODEL["categories"]
COHERENCE_WEIGHT = MODEL["coherence_weight"]
PRIORITY_ORDER = MODEL["priority_order"]
PRIORITY_LABELS = MODEL["priority_labels"]


def grade_for(score: float, band: str) -> str:
    """Map a score to a letter using the named band in scoring-model.json (first floor met wins)."""
    for floor, letter in MODEL["grade_bands"][band]:
        if score >= floor:
            return letter
    return MODEL["grade_floor"]


def _check_score(obj, missing: str, label: str, errors: list[str]) -> None:
    if "score" not in obj:
        errors.append(missing)
    elif not isinstance(obj["score"], (int, float)):
        errors.append(f"{label} must be a number")
    elif not (0 <= obj["score"] <= 10):
        errors.append(f"{label} must be between 0 and 10")


def validate_findings(data: dict) -> list[str]:
    """Validate the structure of audit findings JSON."""
    if not isinstance(data, dict) or "categories" not in data:
        return ["Missing required 'categories' key"]
    cats = data["categories"]
    if not isinstance(cats, dict):
        return ["'categories' must be an object keyed by category"]

    errors = []
    for key in CATEGORIES:
        if key not in cats:
            errors.append(f"Missing category: {key}")
            continue
        if not isinstance(cats[key], dict):
            errors.append(f"Category '{key}' must be an object with a 'score'")
            continue
        _check_score(cats[key], f"Missing 'score' in category '{key}'", f"Score in '{key}'", errors)

    if "coherence" in data:
        if not isinstance(data["coherence"], dict):
            errors.append("Coherence must be an object with a 'score'")
        else:
            _check_score(data["coherence"], "Missing 'score' in coherence", "Coherence score", errors)

    return errors


def compute_weighted_score(data: dict) -> dict:
    """Compute weighted scores across all categories."""
    cats = data["categories"]
    category_results = {}
    total_weighted = 0.0

    for key, meta in CATEGORIES.items():
        cat = cats[key]
        raw_score = float(cat["score"])
        weighted = raw_score * meta["weight"] * 10  # Convert to 0-100 scale contribution
        category_results[key] = {
            "name": meta["name"],
            "weight": meta["weight"],
            "raw_score": raw_score,
            "weighted_contribution": round(weighted, 2),
            "findings": cat.get("findings", []),
        }
        total_weighted += weighted

    # Coherence bonus
    coherence_score = 5.0  # Default if not provided
    if "coherence" in data:
        coherence_score = float(data["coherence"]["score"])
    coherence_weighted = coherence_score * COHERENCE_WEIGHT * 10
    total_weighted += coherence_weighted

    return {
        "categories": category_results,
        "coherence": {
            "raw_score": coherence_score,
            "weighted_contribution": round(coherence_weighted, 2),
        },
        "total_score": round(total_weighted, 2),
    }


def extract_recommendations(data: dict) -> list[dict]:
    """Extract and prioritize all findings as recommendations."""
    recommendations = []
    cats = data.get("categories", {})

    for key, cat in cats.items():
        category_name = CATEGORIES.get(key, {}).get("name", key)
        for finding in cat.get("findings", []):
            recommendations.append({
                "category": category_name,
                "category_key": key,
                "description": finding.get("description", ""),
                "priority": finding.get("priority", "medium"),
                "fix": finding.get("fix", ""),
                "impact_score": finding.get("impact", 5),
            })

    # Sort by priority order, then by impact score descending
    def sort_key(r):
        pri_idx = PRIORITY_ORDER.index(r["priority"]) if r["priority"] in PRIORITY_ORDER else 99
        return (pri_idx, -r["impact_score"])

    recommendations.sort(key=sort_key)
    return recommendations


def _direction(delta: float) -> str:
    return "improved" if delta > 0 else ("declined" if delta < 0 else "unchanged")


def compute_trend(current: dict, baseline: dict) -> dict:
    """Compare current scores against a baseline for trend tracking."""
    trend = {}
    current_cats = current.get("categories", {})
    baseline_cats = baseline.get("categories", {})

    for key in CATEGORIES:
        current_score = current_cats.get(key, {}).get("raw_score", 0)
        baseline_score = baseline_cats.get(key, {}).get("raw_score", 0)
        delta = round(current_score - baseline_score, 2)
        trend[key] = {
            "name": CATEGORIES[key]["name"],
            "current": current_score,
            "baseline": baseline_score,
            "delta": delta,
            "direction": _direction(delta),
        }

    current_total = current.get("total_score", 0)
    baseline_total = baseline.get("total_score", 0)
    total_delta = round(current_total - baseline_total, 2)
    trend["_overall"] = {
        "current_total": current_total,
        "baseline_total": baseline_total,
        "delta": total_delta,
        "direction": _direction(total_delta),
    }
    return trend


def count_by_priority(recommendations: list[dict]) -> dict:
    """Count findings by priority level."""
    counts = {p: 0 for p in PRIORITY_ORDER}
    for rec in recommendations:
        pri = rec.get("priority", "medium")
        counts[pri] = counts.get(pri, 0) + 1
    return counts


def load_json_file(path: str) -> dict:
    """Load and parse a JSON file (exit 2 on a missing file or invalid JSON)."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(2)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {path}: {e}", file=sys.stderr)
        sys.exit(2)


def main():
    parser = argparse.ArgumentParser(
        description="Score Model — validate a findings file and print its weighted design score",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input findings.json
  %(prog)s --input findings.json --format json
        """,
    )
    parser.add_argument("--input", "-i", required=True, help="Path to audit findings JSON file")
    parser.add_argument("--format", "-f", choices=["json", "text"], default="text",
                        help="Output format (default: text)")
    args = parser.parse_args()

    data = load_json_file(args.input)
    errors = validate_findings(data)
    if errors:
        print("Validation errors:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        sys.exit(2)

    scores = compute_weighted_score(data)
    result = {"valid": True, "total_score": scores["total_score"],
              "design_grade": grade_for(scores["total_score"], "design"),
              "contributions": {k: v["weighted_contribution"] for k, v in scores["categories"].items()},
              "coherence": scores["coherence"]["weighted_contribution"]}
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(f"Valid findings file. Weighted score {result['total_score']}/100 ({result['design_grade']})")
        for key, value in result["contributions"].items():
            print(f"  {key:<20} {value:>6.2f}")
        print(f"  {'coherence':<20} {result['coherence']:>6.2f}")


if __name__ == "__main__":
    main()
