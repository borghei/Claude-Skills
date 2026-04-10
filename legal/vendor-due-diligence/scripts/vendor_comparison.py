#!/usr/bin/env python3
"""
Vendor Comparison Tool

Takes multiple vendor risk assessment JSONs and generates a side-by-side
comparison matrix. Ranks vendors by composite score, highlights strengths
and weaknesses per dimension, and recommends preferred vendor with rationale.

Usage:
    python vendor_comparison.py vendor_a.json vendor_b.json
    python vendor_comparison.py vendor_a.json vendor_b.json vendor_c.json --json
    python vendor_comparison.py vendor_a.json vendor_b.json --critical
"""

import argparse
import json
import sys
from typing import Any, Dict, List, Tuple

# Dimension weights
STANDARD_WEIGHTS: Dict[str, float] = {
    "financial": 1.0, "operational": 1.0, "compliance": 1.0,
    "security": 1.0, "reputational": 0.8, "strategic": 0.8,
}

CRITICAL_WEIGHTS: Dict[str, float] = {
    "financial": 1.0, "operational": 1.0, "compliance": 2.0,
    "security": 2.0, "reputational": 0.8, "strategic": 0.8,
}

DIMENSIONS = ["financial", "operational", "compliance", "security", "reputational", "strategic"]

RISK_LEVELS: List[Tuple[float, str, str]] = [
    (1.5, "Low Risk", "Approve"),
    (2.5, "Moderate Risk", "Approve with Conditions"),
    (3.5, "High Risk", "Enhanced Due Diligence"),
    (5.0, "Critical Risk", "Reject or Remediate"),
]


def load_vendor_data(file_path: str) -> Dict[str, Any]:
    """Load and validate a vendor assessment JSON file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {file_path}: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate required structure
    vendor_name = data.get("vendor_name", file_path.split("/")[-1].replace(".json", ""))
    scores: Dict[str, int] = {}

    for dim in DIMENSIONS:
        dim_data = data.get(dim, {})
        if isinstance(dim_data, dict) and "score" in dim_data:
            # Pre-scored format (output from vendor_risk_scorer.py)
            scores[dim] = dim_data["score"]
        elif isinstance(dim_data, dict):
            # Raw questionnaire format -- apply basic scoring
            scores[dim] = _quick_score(dim, dim_data)
        else:
            scores[dim] = 3  # default moderate if missing

    return {"vendor_name": vendor_name, "scores": scores, "raw_data": data}


def _quick_score(dimension: str, data: Dict[str, Any]) -> int:
    """Quick-score a dimension from raw questionnaire data (simplified)."""
    score = 3  # baseline
    positive_keys = [
        "audited_financials", "disaster_recovery_plan", "business_continuity_tested",
        "geographic_redundancy", "dedicated_support", "compliance_team_exists",
        "encryption_at_rest", "encryption_in_transit", "mfa_enforced",
        "incident_response_plan", "soc2_type2", "vulnerability_management",
        "client_references_available", "industry_recognition",
        "exit_strategy_feasible", "innovation_track_record",
    ]
    negative_keys = [
        "key_person_dependency", "breach_history", "litigation_history",
        "negative_press",
    ]

    for key in positive_keys:
        if data.get(key, False) is True:
            score -= 0.3

    for key in negative_keys:
        if data.get(key, False) is True:
            score += 0.5

    certs = data.get("certifications", [])
    score -= min(1.5, len(certs) * 0.5)

    return max(1, min(5, round(score)))


def calculate_composite(scores: Dict[str, int], weights: Dict[str, float]) -> float:
    """Calculate weighted composite score."""
    weighted_sum = sum(scores[d] * weights[d] for d in DIMENSIONS)
    total_weight = sum(weights[d] for d in DIMENSIONS)
    return round(weighted_sum / total_weight, 2)


def get_risk_level(composite: float) -> Tuple[str, str]:
    """Get risk level and recommendation from composite score."""
    for threshold, level, rec in RISK_LEVELS:
        if composite <= threshold:
            return level, rec
    return "Critical Risk", "Reject or Remediate"


def analyze_strengths_weaknesses(
    vendors: List[Dict[str, Any]]
) -> Dict[str, Dict[str, List[str]]]:
    """Identify per-vendor strengths and weaknesses relative to the group."""
    analysis: Dict[str, Dict[str, List[str]]] = {}

    for vendor in vendors:
        name = vendor["vendor_name"]
        strengths: List[str] = []
        weaknesses: List[str] = []

        for dim in DIMENSIONS:
            vendor_score = vendor["scores"][dim]
            other_scores = [v["scores"][dim] for v in vendors if v["vendor_name"] != name]

            if not other_scores:
                continue

            avg_other = sum(other_scores) / len(other_scores)

            if vendor_score < avg_other - 0.5:
                strengths.append(f"{dim.title()} ({vendor_score}/5 vs avg {avg_other:.1f})")
            elif vendor_score > avg_other + 0.5:
                weaknesses.append(f"{dim.title()} ({vendor_score}/5 vs avg {avg_other:.1f})")

        analysis[name] = {"strengths": strengths, "weaknesses": weaknesses}

    return analysis


def generate_recommendation(
    vendors: List[Dict[str, Any]], weights: Dict[str, float]
) -> Dict[str, Any]:
    """Generate preferred vendor recommendation with rationale."""
    ranked = sorted(
        vendors,
        key=lambda v: calculate_composite(v["scores"], weights),
    )

    preferred = ranked[0]
    preferred_composite = calculate_composite(preferred["scores"], weights)
    risk_level, rec = get_risk_level(preferred_composite)

    rationale_parts: List[str] = []
    rationale_parts.append(
        f"Lowest composite risk score ({preferred_composite:.2f})"
    )

    # Find dimensions where preferred vendor leads
    for dim in DIMENSIONS:
        is_best = all(
            preferred["scores"][dim] <= v["scores"][dim]
            for v in vendors if v["vendor_name"] != preferred["vendor_name"]
        )
        if is_best and preferred["scores"][dim] <= 2:
            rationale_parts.append(f"Best-in-class {dim} risk ({preferred['scores'][dim]}/5)")

    # Note any concerns
    concerns: List[str] = []
    for dim in DIMENSIONS:
        if preferred["scores"][dim] >= 4:
            concerns.append(f"{dim.title()} dimension scores {preferred['scores'][dim]}/5 -- requires mitigation")

    return {
        "preferred_vendor": preferred["vendor_name"],
        "composite_score": preferred_composite,
        "risk_level": risk_level,
        "recommendation": rec,
        "rationale": rationale_parts,
        "concerns": concerns,
    }


def build_comparison_matrix(
    vendors: List[Dict[str, Any]], weights: Dict[str, float]
) -> Dict[str, Any]:
    """Build the full comparison result."""
    # Calculate composites
    vendor_results: List[Dict[str, Any]] = []
    for v in vendors:
        composite = calculate_composite(v["scores"], weights)
        risk_level, rec = get_risk_level(composite)
        vendor_results.append({
            "vendor_name": v["vendor_name"],
            "scores": v["scores"],
            "composite_score": composite,
            "risk_level": risk_level,
            "recommendation": rec,
        })

    # Sort by composite (lower is better)
    vendor_results.sort(key=lambda x: x["composite_score"])

    # Rank
    for i, vr in enumerate(vendor_results, 1):
        vr["rank"] = i

    # Analysis
    sw_analysis = analyze_strengths_weaknesses(vendors)
    recommendation = generate_recommendation(vendors, weights)

    # Risk deltas
    if len(vendor_results) >= 2:
        best = vendor_results[0]["composite_score"]
        worst = vendor_results[-1]["composite_score"]
        delta = round(worst - best, 2)
    else:
        delta = 0.0

    return {
        "vendor_count": len(vendors),
        "ranking": vendor_results,
        "strengths_weaknesses": sw_analysis,
        "recommendation": recommendation,
        "risk_delta": delta,
    }


def format_text_output(result: Dict[str, Any], critical: bool) -> str:
    """Format comparison results as human-readable text."""
    lines: List[str] = []
    lines.append("=" * 78)
    lines.append("VENDOR COMPARISON MATRIX")
    lines.append(f"Vendors Compared: {result['vendor_count']}")
    lines.append(f"Weighting: {'Critical Service (2x Security & Compliance)' if critical else 'Standard'}")
    lines.append("=" * 78)
    lines.append("")

    # Ranking table
    lines.append("-" * 78)
    lines.append(f"{'Rank':<6} {'Vendor':<25} {'Composite':>10} {'Risk Level':<18} {'Recommendation'}")
    lines.append("-" * 78)
    for vr in result["ranking"]:
        lines.append(
            f"  {vr['rank']:<4} {vr['vendor_name']:<25} {vr['composite_score']:>8.2f}   "
            f"{vr['risk_level']:<18} {vr['recommendation']}"
        )
    lines.append("")

    # Dimension comparison
    lines.append("-" * 78)
    lines.append("DIMENSION COMPARISON (1=Low Risk, 5=Critical Risk)")
    lines.append("-" * 78)

    header = f"{'Dimension':<16}"
    for vr in result["ranking"]:
        header += f" {vr['vendor_name'][:15]:>15}"
    lines.append(header)
    lines.append("-" * 78)

    for dim in DIMENSIONS:
        row = f"  {dim.title():<14}"
        scores_for_dim = []
        for vr in result["ranking"]:
            score = vr["scores"][dim]
            scores_for_dim.append(score)
            bar = "█" * score + "░" * (5 - score)
            row += f" {bar} {score:<3}"
        # Mark best
        best_score = min(scores_for_dim)
        lines.append(row)
    lines.append("")

    # Strengths and weaknesses
    lines.append("-" * 78)
    lines.append("STRENGTHS & WEAKNESSES")
    lines.append("-" * 78)
    for vendor_name, sw in result["strengths_weaknesses"].items():
        lines.append(f"\n  {vendor_name}:")
        if sw["strengths"]:
            lines.append("    Strengths:")
            for s in sw["strengths"]:
                lines.append(f"      + {s}")
        if sw["weaknesses"]:
            lines.append("    Weaknesses:")
            for w in sw["weaknesses"]:
                lines.append(f"      - {w}")
        if not sw["strengths"] and not sw["weaknesses"]:
            lines.append("    No significant differentiators vs. other vendors")
    lines.append("")

    # Recommendation
    rec = result["recommendation"]
    lines.append("-" * 78)
    lines.append("RECOMMENDATION")
    lines.append("-" * 78)
    lines.append(f"  Preferred Vendor: {rec['preferred_vendor']}")
    lines.append(f"  Composite Score:  {rec['composite_score']:.2f}")
    lines.append(f"  Risk Level:       {rec['risk_level']}")
    lines.append(f"  Action:           {rec['recommendation']}")
    lines.append("")
    lines.append("  Rationale:")
    for r in rec["rationale"]:
        lines.append(f"    - {r}")
    if rec["concerns"]:
        lines.append("  Concerns:")
        for c in rec["concerns"]:
            lines.append(f"    ! {c}")

    lines.append("")
    lines.append(f"  Risk Delta (best to worst): {result['risk_delta']:.2f}")
    lines.append("")

    return "\n".join(lines)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Compare multiple vendors side-by-side and recommend preferred vendor."
    )
    parser.add_argument(
        "input_files", nargs="+",
        help="Paths to vendor assessment JSON files (minimum 2)"
    )
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--critical", action="store_true",
                        help="Apply 2x weight to security and compliance")
    args = parser.parse_args()

    if len(args.input_files) < 2:
        print("Error: At least 2 vendor files required for comparison.", file=sys.stderr)
        sys.exit(1)

    vendors: List[Dict[str, Any]] = []
    for fp in args.input_files:
        vendors.append(load_vendor_data(fp))

    # Check for duplicate vendor names
    names = [v["vendor_name"] for v in vendors]
    if len(names) != len(set(names)):
        print("Warning: Duplicate vendor names detected. Results may be ambiguous.", file=sys.stderr)

    weights = CRITICAL_WEIGHTS if args.critical else STANDARD_WEIGHTS
    result = build_comparison_matrix(vendors, weights)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_text_output(result, args.critical))


if __name__ == "__main__":
    main()
