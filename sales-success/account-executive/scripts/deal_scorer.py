#!/usr/bin/env python3
"""Score deal health using MEDDPICC qualification framework.

Reads deal data from CSV or JSON and produces a qualification score
for each opportunity based on MEDDPICC dimensions plus BANT criteria.

Usage:
    python deal_scorer.py --data deals.csv
    python deal_scorer.py --data deals.json --json
    python deal_scorer.py --data deals.csv --threshold 60
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime

MEDDPICC_DIMENSIONS = [
    "metrics",
    "economic_buyer",
    "decision_criteria",
    "decision_process",
    "paper_process",
    "identify_pain",
    "champion",
    "competition",
]

BANT_DIMENSIONS = ["budget", "authority", "need", "timeline"]

SCORE_LABELS = {
    (0, 30): ("Critical", "Needs immediate qualification or disqualification"),
    (30, 50): ("Weak", "Significant gaps; address before advancing"),
    (50, 70): ("Developing", "Viable but requires work on weak dimensions"),
    (70, 85): ("Strong", "Well-qualified; advance with confidence"),
    (85, 101): ("Exceptional", "Top-tier opportunity; prioritize and close"),
}


def load_data(filepath):
    """Load deal data from CSV or JSON file."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".json":
        with open(filepath, "r") as f:
            data = json.load(f)
            return data if isinstance(data, list) else [data]
    elif ext == ".csv":
        with open(filepath, "r") as f:
            reader = csv.DictReader(f)
            return list(reader)
    else:
        print(f"Error: Unsupported file format '{ext}'. Use .csv or .json.", file=sys.stderr)
        sys.exit(1)


def parse_score(value, max_val=5):
    """Parse a score value, clamping to 0-max_val range."""
    try:
        score = float(value)
        return max(0, min(score, max_val))
    except (ValueError, TypeError):
        return 0


def score_deal(deal, mode="meddpicc"):
    """Score a single deal using MEDDPICC or BANT framework.

    Each dimension is scored 0-5. Total is normalized to 0-100.
    """
    if mode == "meddpicc":
        dimensions = MEDDPICC_DIMENSIONS
    else:
        dimensions = BANT_DIMENSIONS

    scores = {}
    for dim in dimensions:
        raw = deal.get(dim, deal.get(dim.replace("_", " "), 0))
        scores[dim] = parse_score(raw, 5)

    max_possible = len(dimensions) * 5
    raw_total = sum(scores.values())
    normalized = (raw_total / max_possible) * 100 if max_possible > 0 else 0

    label = "Unknown"
    advice = ""
    for (lo, hi), (lbl, adv) in SCORE_LABELS.items():
        if lo <= normalized < hi:
            label = lbl
            advice = adv
            break

    weak_dimensions = [dim for dim, score in scores.items() if score < 3]
    strong_dimensions = [dim for dim, score in scores.items() if score >= 4]

    return {
        "deal_name": deal.get("deal_name", deal.get("name", deal.get("opportunity", "Unknown"))),
        "stage": deal.get("stage", "Unknown"),
        "amount": deal.get("amount", deal.get("acv", "N/A")),
        "framework": mode.upper(),
        "dimension_scores": scores,
        "raw_total": round(raw_total, 1),
        "max_possible": max_possible,
        "normalized_score": round(normalized, 1),
        "label": label,
        "advice": advice,
        "weak_dimensions": weak_dimensions,
        "strong_dimensions": strong_dimensions,
    }


def format_human(results, threshold):
    """Format results for human-readable output."""
    lines = []
    lines.append("=" * 70)
    lines.append("DEAL QUALIFICATION SCORECARD")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"Threshold: {threshold}/100")
    lines.append("=" * 70)

    above = [r for r in results if r["normalized_score"] >= threshold]
    below = [r for r in results if r["normalized_score"] < threshold]

    for result in sorted(results, key=lambda x: x["normalized_score"], reverse=True):
        lines.append("")
        lines.append(f"  Deal: {result['deal_name']}")
        lines.append(f"  Stage: {result['stage']}  |  Amount: {result['amount']}")
        lines.append(f"  Framework: {result['framework']}")
        lines.append(f"  Score: {result['normalized_score']}/100 ({result['raw_total']}/{result['max_possible']})")
        lines.append(f"  Rating: {result['label']}")
        lines.append(f"  Assessment: {result['advice']}")
        lines.append("")
        lines.append("  Dimension Scores:")
        for dim, score in result["dimension_scores"].items():
            bar = "#" * int(score) + "." * (5 - int(score))
            flag = " << WEAK" if score < 3 else ""
            lines.append(f"    {dim:20s} [{bar}] {score}/5{flag}")

        if result["weak_dimensions"]:
            lines.append(f"\n  Action Required: Strengthen {', '.join(result['weak_dimensions'])}")
        if result["strong_dimensions"]:
            lines.append(f"  Strengths: {', '.join(result['strong_dimensions'])}")

        status = "ABOVE" if result["normalized_score"] >= threshold else "BELOW"
        lines.append(f"  Threshold Status: {status}")
        lines.append("-" * 70)

    lines.append("")
    lines.append("SUMMARY")
    lines.append(f"  Total deals scored: {len(results)}")
    lines.append(f"  Above threshold ({threshold}): {len(above)}")
    lines.append(f"  Below threshold ({threshold}): {len(below)}")
    if results:
        avg = sum(r["normalized_score"] for r in results) / len(results)
        lines.append(f"  Average score: {avg:.1f}/100")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Score deal health using MEDDPICC or BANT qualification framework."
    )
    parser.add_argument("--data", required=True, help="Path to deals CSV or JSON file")
    parser.add_argument(
        "--mode",
        choices=["meddpicc", "bant"],
        default="meddpicc",
        help="Qualification framework (default: meddpicc)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=60,
        help="Minimum qualification score 0-100 (default: 60)",
    )
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    if not os.path.exists(args.data):
        print(f"Error: File not found: {args.data}", file=sys.stderr)
        sys.exit(1)

    deals = load_data(args.data)
    if not deals:
        print("Error: No deals found in input file.", file=sys.stderr)
        sys.exit(1)

    results = [score_deal(deal, args.mode) for deal in deals]

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_human(results, args.threshold))

    below = [r for r in results if r["normalized_score"] < args.threshold]
    sys.exit(1 if below else 0)


if __name__ == "__main__":
    main()
