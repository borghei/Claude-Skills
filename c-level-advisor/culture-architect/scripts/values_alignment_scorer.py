#!/usr/bin/env python3
"""
Values Alignment Scorer - Score alignment between stated values and observed behaviors.

Uses Competing Values Framework (CVF) quadrants (Clan, Adhocracy, Market, Hierarchy).
Detects gaps between current and desired culture, identifies value-washing risks,
and recommends alignment actions.

Usage:
    python values_alignment_scorer.py --input values_data.json
    python values_alignment_scorer.py --input values_data.json --json
"""

import argparse
import json
import sys
from datetime import datetime


CVF_QUADRANTS = {
    "clan": {
        "label": "Clan (Collaborate)",
        "focus": "Internal focus + Flexibility",
        "traits": ["teamwork", "mentoring", "participation", "loyalty", "morale"],
    },
    "adhocracy": {
        "label": "Adhocracy (Create)",
        "focus": "External focus + Flexibility",
        "traits": ["innovation", "risk-taking", "agility", "experimentation", "entrepreneurship"],
    },
    "market": {
        "label": "Market (Compete)",
        "focus": "External focus + Stability",
        "traits": ["competition", "results", "achievement", "market_share", "goal_setting"],
    },
    "hierarchy": {
        "label": "Hierarchy (Control)",
        "focus": "Internal focus + Stability",
        "traits": ["efficiency", "consistency", "process", "compliance", "predictability"],
    },
}


def load_data(path):
    with open(path, "r") as f:
        return json.load(f)


def score_value_alignment(stated, observed):
    """Score alignment between stated and observed behavioral evidence."""
    if observed >= stated * 0.9:
        return {"score": round((observed / max(stated, 1)) * 100, 1), "status": "Aligned"}
    elif observed >= stated * 0.6:
        gap = round(stated - observed, 1)
        return {"score": round((observed / max(stated, 1)) * 100, 1), "status": "Gap", "gap": gap}
    else:
        gap = round(stated - observed, 1)
        return {"score": round((observed / max(stated, 1)) * 100, 1), "status": "Value-washing risk", "gap": gap}


def analyze_cvf(cvf_data):
    """Analyze Competing Values Framework quadrant distribution."""
    if not cvf_data:
        return None

    current = cvf_data.get("current", {})
    desired = cvf_data.get("desired", {})

    # Validate totals should be ~100
    current_total = sum(current.values())
    desired_total = sum(desired.values())

    quadrant_analysis = {}
    for q_key, q_info in CVF_QUADRANTS.items():
        curr = current.get(q_key, 0)
        des = desired.get(q_key, 0)
        shift = round(des - curr, 1)

        quadrant_analysis[q_key] = {
            "label": q_info["label"],
            "current_pct": curr,
            "desired_pct": des,
            "shift_needed": shift,
            "direction": "increase" if shift > 0 else ("decrease" if shift < 0 else "maintain"),
        }

    # Dominant culture
    dominant_current = max(current, key=current.get) if current else None
    dominant_desired = max(desired, key=desired.get) if desired else None

    return {
        "quadrants": quadrant_analysis,
        "dominant_current": CVF_QUADRANTS.get(dominant_current, {}).get("label", "Unknown"),
        "dominant_desired": CVF_QUADRANTS.get(dominant_desired, {}).get("label", "Unknown"),
        "culture_shift_needed": dominant_current != dominant_desired,
    }


def analyze_values(data):
    """Run full values alignment analysis."""
    org_name = data.get("organization", "Organization")
    values = data.get("values", [])
    cvf_data = data.get("cvf_assessment", {})

    results = {
        "timestamp": datetime.now().isoformat(),
        "organization": org_name,
        "values_count": len(values),
        "overall_alignment_score": 0,
        "overall_alignment_label": "",
        "value_assessments": [],
        "aligned_values": [],
        "gap_values": [],
        "washing_risks": [],
        "cvf_analysis": None,
        "recommendations": [],
    }

    alignment_scores = []

    for val in values:
        name = val.get("name", "Unnamed")
        stated_importance = val.get("stated_importance", 10)  # 1-10
        behavioral_evidence = val.get("behavioral_evidence_score", 0)  # 1-10
        behaviors = val.get("observable_behaviors", [])
        violations = val.get("observed_violations", [])
        trade_off = val.get("trade_off", "Not defined")

        alignment = score_value_alignment(stated_importance, behavioral_evidence)
        has_trade_off = trade_off != "Not defined" and trade_off != ""

        assessment = {
            "name": name,
            "stated_importance": stated_importance,
            "behavioral_evidence": behavioral_evidence,
            "alignment_score": alignment["score"],
            "alignment_status": alignment["status"],
            "gap": alignment.get("gap", 0),
            "observable_behaviors": behaviors,
            "violations_observed": violations,
            "trade_off_defined": has_trade_off,
            "trade_off": trade_off,
        }

        # Flag platitudes (no trade-off defined)
        if not has_trade_off:
            assessment["warning"] = "No trade-off defined -- may be a platitude, not a real value"

        results["value_assessments"].append(assessment)
        alignment_scores.append(alignment["score"])

        if alignment["status"] == "Aligned":
            results["aligned_values"].append(name)
        elif alignment["status"] == "Gap":
            results["gap_values"].append({"name": name, "gap": alignment.get("gap", 0)})
        elif alignment["status"] == "Value-washing risk":
            results["washing_risks"].append({"name": name, "gap": alignment.get("gap", 0)})

    # Overall alignment
    if alignment_scores:
        results["overall_alignment_score"] = round(sum(alignment_scores) / len(alignment_scores), 1)
        score = results["overall_alignment_score"]
        if score >= 80:
            results["overall_alignment_label"] = "Strong alignment"
        elif score >= 60:
            results["overall_alignment_label"] = "Moderate alignment -- gaps to address"
        elif score >= 40:
            results["overall_alignment_label"] = "Weak alignment -- significant gaps"
        else:
            results["overall_alignment_label"] = "Values are performative -- rebuild from reality"

    # CVF analysis
    if cvf_data:
        results["cvf_analysis"] = analyze_cvf(cvf_data)

    # Recommendations
    recs = results["recommendations"]
    if results["washing_risks"]:
        names = ", ".join(w["name"] for w in results["washing_risks"])
        recs.append(f"VALUE-WASHING RISK: {names} -- stated importance far exceeds behavioral evidence")
        recs.append("Either invest in making these values real or rewrite values to match actual culture")

    platitudes = [a for a in results["value_assessments"] if not a["trade_off_defined"]]
    if platitudes:
        recs.append(f"{len(platitudes)} values have no defined trade-off -- run values-to-behaviors workshop")

    if len(values) > 5:
        recs.append(f"{len(values)} values defined -- reduce to 3-5 maximum for memorability")

    if results["cvf_analysis"] and results["cvf_analysis"]["culture_shift_needed"]:
        recs.append(
            f"Culture shift needed: {results['cvf_analysis']['dominant_current']} -> "
            f"{results['cvf_analysis']['dominant_desired']} -- plan for 12-24 month transition"
        )

    return results


def format_text(results):
    lines = [
        "=" * 60,
        "VALUES ALIGNMENT SCORECARD",
        "=" * 60,
        f"Organization: {results['organization']}",
        f"Values Assessed: {results['values_count']}",
        f"Analysis Date: {results['timestamp'][:10]}",
        "",
        f"OVERALL ALIGNMENT: {results['overall_alignment_score']}% ({results['overall_alignment_label']})",
        "",
        "VALUE ASSESSMENTS",
    ]

    for v in results["value_assessments"]:
        status_icon = {"Aligned": "+", "Gap": "~", "Value-washing risk": "!!"}.get(v["alignment_status"], "?")
        lines.append(f"\n  [{status_icon}] {v['name']}")
        lines.append(f"      Stated: {v['stated_importance']}/10 | Evidence: {v['behavioral_evidence']}/10 | Alignment: {v['alignment_score']}%")
        lines.append(f"      Status: {v['alignment_status']}")
        if v.get("trade_off_defined"):
            lines.append(f"      Trade-off: {v['trade_off']}")
        else:
            lines.append(f"      Trade-off: NOT DEFINED (may be a platitude)")
        if v.get("warning"):
            lines.append(f"      WARNING: {v['warning']}")

    if results["aligned_values"]:
        lines.append("")
        lines.append(f"ALIGNED VALUES: {', '.join(results['aligned_values'])}")

    if results["washing_risks"]:
        lines.append("")
        lines.append("VALUE-WASHING RISKS")
        for w in results["washing_risks"]:
            lines.append(f"  !! {w['name']} (gap: {w['gap']})")

    if results["cvf_analysis"]:
        cvf = results["cvf_analysis"]
        lines.append("")
        lines.append("COMPETING VALUES FRAMEWORK")
        lines.append(f"  Dominant Culture: {cvf['dominant_current']}")
        lines.append(f"  Desired Culture: {cvf['dominant_desired']}")
        lines.append(f"  Shift Needed: {'Yes' if cvf['culture_shift_needed'] else 'No'}")
        for q, info in cvf["quadrants"].items():
            lines.append(f"    {info['label']}: {info['current_pct']}% -> {info['desired_pct']}% ({info['direction']})")

    if results["recommendations"]:
        lines.append("")
        lines.append("RECOMMENDATIONS")
        for rec in results["recommendations"]:
            lines.append(f"  * {rec}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Score values alignment using CVF and behavioral evidence")
    parser.add_argument("--input", required=True, help="Path to JSON values data file")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    args = parser.parse_args()

    try:
        data = load_data(args.input)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading input file: {e}", file=sys.stderr)
        sys.exit(1)

    results = analyze_values(data)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_text(results))


if __name__ == "__main__":
    main()
