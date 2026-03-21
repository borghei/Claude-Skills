#!/usr/bin/env python3
"""
Decision Quality Scorer - Score decision quality across 6 dimensions.

Evaluates framing, alternatives, information, reasoning, commitment, and metacognition.
Generates quality profiles, identifies improvement areas, and tracks quality over time.

Usage:
    python decision_quality_scorer.py --input decision_assessments.json
    python decision_quality_scorer.py --input decision_assessments.json --json
"""

import argparse
import json
import sys
from datetime import datetime


QUALITY_DIMENSIONS = {
    "framing": {
        "label": "Framing",
        "description": "Problem definition clarity and scope",
        "weight": 0.20,
        "improvement_tips": {
            "low": "Spend more time defining the problem before jumping to solutions",
            "medium": "Validate the problem framing with stakeholders before proceeding",
            "high": "Strong framing -- ensure it is revisited if new information emerges",
        },
    },
    "alternatives": {
        "label": "Alternatives",
        "description": "Number and quality of options considered",
        "weight": 0.20,
        "improvement_tips": {
            "low": "Require minimum 3 alternatives before deciding -- avoid anchoring on first option",
            "medium": "Include creative or contrarian options -- not just obvious choices",
            "high": "Excellent option generation -- document why rejected alternatives were dropped",
        },
    },
    "information": {
        "label": "Information",
        "description": "Quality and completeness of evidence used",
        "weight": 0.15,
        "improvement_tips": {
            "low": "Decision made with insufficient data -- identify what data would change the decision",
            "medium": "Adequate data but gaps remain -- document known unknowns",
            "high": "Strong evidence base -- ensure data is current and unbiased",
        },
    },
    "reasoning": {
        "label": "Reasoning",
        "description": "Logic soundness and bias awareness",
        "weight": 0.15,
        "improvement_tips": {
            "low": "Check for common biases: confirmation bias, sunk cost, anchoring, recency",
            "medium": "Logic is sound but may benefit from devil's advocate review",
            "high": "Rigorous reasoning -- ensure it is documented for future reference",
        },
    },
    "commitment": {
        "label": "Commitment",
        "description": "Action clarity, ownership, and deadlines",
        "weight": 0.15,
        "improvement_tips": {
            "low": "Decision made but no clear actions, owners, or deadlines -- add them immediately",
            "medium": "Actions defined but may lack specific deadlines or success criteria",
            "high": "Clear actions with owners and deadlines -- ensure follow-up is scheduled",
        },
    },
    "metacognition": {
        "label": "Metacognition",
        "description": "Awareness of uncertainty and reversibility",
        "weight": 0.15,
        "improvement_tips": {
            "low": "Overconfident -- explicitly state what could go wrong and how you would know",
            "medium": "Some uncertainty acknowledged -- add specific triggers for re-evaluation",
            "high": "Excellent self-awareness -- review date set and contingency plan documented",
        },
    },
}


def load_data(path):
    with open(path, "r") as f:
        return json.load(f)


def get_quality_level(score):
    if score >= 8:
        return "high"
    elif score >= 5:
        return "medium"
    else:
        return "low"


def get_overall_label(score):
    if score >= 8:
        return "Excellent"
    elif score >= 6:
        return "Good"
    elif score >= 4:
        return "Adequate"
    else:
        return "Poor"


def score_decision(assessment):
    """Score a single decision across all dimensions."""
    title = assessment.get("title", "Unnamed Decision")
    scores = assessment.get("scores", {})
    outcome = assessment.get("outcome", {})

    dimension_results = {}
    weighted_total = 0

    for dim_key, dim_config in QUALITY_DIMENSIONS.items():
        score = scores.get(dim_key, 5)  # Default to 5 if not provided
        score = max(1, min(10, score))  # Clamp 1-10
        level = get_quality_level(score)
        weighted = score * dim_config["weight"]
        weighted_total += weighted

        dimension_results[dim_key] = {
            "label": dim_config["label"],
            "score": score,
            "level": level,
            "weighted_score": round(weighted, 2),
            "improvement_tip": dim_config["improvement_tips"][level],
        }

    overall = round(weighted_total, 1)

    result = {
        "title": title,
        "date": assessment.get("date", "Unknown"),
        "overall_quality_score": overall,
        "overall_label": get_overall_label(overall),
        "dimensions": dimension_results,
        "weakest_dimension": min(dimension_results, key=lambda k: dimension_results[k]["score"]),
        "strongest_dimension": max(dimension_results, key=lambda k: dimension_results[k]["score"]),
    }

    # Outcome correlation (if available)
    if outcome:
        result["outcome"] = {
            "success": outcome.get("success", None),
            "outcome_score": outcome.get("outcome_score", None),
            "notes": outcome.get("notes", ""),
        }

    return result


def analyze_decisions(data):
    """Analyze all decision quality assessments."""
    assessments = data.get("assessments", [])
    org_name = data.get("organization", "Organization")

    results = {
        "timestamp": datetime.now().isoformat(),
        "organization": org_name,
        "decisions_assessed": len(assessments),
        "decision_results": [],
        "aggregate_scores": {},
        "dimension_averages": {},
        "patterns": [],
        "recommendations": [],
    }

    all_dimension_scores = {dim: [] for dim in QUALITY_DIMENSIONS}
    all_overall_scores = []

    for assessment in assessments:
        result = score_decision(assessment)
        results["decision_results"].append(result)
        all_overall_scores.append(result["overall_quality_score"])

        for dim_key, dim_data in result["dimensions"].items():
            all_dimension_scores[dim_key].append(dim_data["score"])

    # Aggregate scores
    if all_overall_scores:
        results["aggregate_scores"] = {
            "avg_quality": round(sum(all_overall_scores) / len(all_overall_scores), 1),
            "min_quality": min(all_overall_scores),
            "max_quality": max(all_overall_scores),
            "quality_label": get_overall_label(sum(all_overall_scores) / len(all_overall_scores)),
        }

    # Dimension averages
    for dim_key, scores in all_dimension_scores.items():
        if scores:
            avg = round(sum(scores) / len(scores), 1)
            results["dimension_averages"][dim_key] = {
                "label": QUALITY_DIMENSIONS[dim_key]["label"],
                "average": avg,
                "level": get_quality_level(avg),
            }

    # Patterns
    if results["dimension_averages"]:
        weakest = min(results["dimension_averages"], key=lambda k: results["dimension_averages"][k]["average"])
        strongest = max(results["dimension_averages"], key=lambda k: results["dimension_averages"][k]["average"])
        results["patterns"].append(f"Consistently weakest: {QUALITY_DIMENSIONS[weakest]['label']} (avg: {results['dimension_averages'][weakest]['average']}/10)")
        results["patterns"].append(f"Consistently strongest: {QUALITY_DIMENSIONS[strongest]['label']} (avg: {results['dimension_averages'][strongest]['average']}/10)")

    # Check for low-alternatives pattern
    alt_avg = results["dimension_averages"].get("alternatives", {}).get("average", 5)
    if alt_avg < 5:
        results["patterns"].append("Pattern: decisions consistently lack sufficient alternatives -- anchoring risk")

    # Recommendations
    recs = results["recommendations"]
    if results["aggregate_scores"].get("avg_quality", 0) < 5:
        recs.append("Overall decision quality is low -- implement structured decision-making process")

    for dim_key, dim_info in results["dimension_averages"].items():
        if dim_info["level"] == "low":
            tip = QUALITY_DIMENSIONS[dim_key]["improvement_tips"]["low"]
            recs.append(f"Improve {dim_info['label']}: {tip}")

    # Outcome correlation
    decisions_with_outcomes = [d for d in results["decision_results"] if d.get("outcome", {}).get("success") is not None]
    if len(decisions_with_outcomes) >= 3:
        high_q_success = sum(1 for d in decisions_with_outcomes if d["overall_quality_score"] >= 7 and d["outcome"]["success"])
        high_q_total = sum(1 for d in decisions_with_outcomes if d["overall_quality_score"] >= 7)
        if high_q_total > 0:
            success_rate = round((high_q_success / high_q_total) * 100, 0)
            recs.append(f"High-quality decisions (score >= 7) have {success_rate}% success rate")

    return results


def format_text(results):
    lines = [
        "=" * 60,
        "DECISION QUALITY REPORT",
        "=" * 60,
        f"Organization: {results['organization']}",
        f"Decisions Assessed: {results['decisions_assessed']}",
        f"Report Date: {results['timestamp'][:10]}",
    ]

    agg = results["aggregate_scores"]
    if agg:
        lines.extend([
            "",
            f"AGGREGATE QUALITY: {agg['avg_quality']}/10 ({agg['quality_label']})",
            f"  Range: {agg['min_quality']} - {agg['max_quality']}",
        ])

    if results["dimension_averages"]:
        lines.append("")
        lines.append("DIMENSION AVERAGES")
        sorted_dims = sorted(results["dimension_averages"].items(), key=lambda x: x[1]["average"])
        for dim_key, info in sorted_dims:
            lines.append(f"  {info['label']}: {info['average']}/10 ({info['level']})")

    lines.append("")
    lines.append("INDIVIDUAL DECISIONS")
    for d in results["decision_results"]:
        lines.append(f"\n  {d['title']} ({d['date']})")
        lines.append(f"    Quality: {d['overall_quality_score']}/10 ({d['overall_label']})")
        lines.append(f"    Weakest: {QUALITY_DIMENSIONS[d['weakest_dimension']]['label']} | "
                      f"Strongest: {QUALITY_DIMENSIONS[d['strongest_dimension']]['label']}")
        for dim_key, dim_data in d["dimensions"].items():
            lines.append(f"      {dim_data['label']}: {dim_data['score']}/10")
        if d.get("outcome", {}).get("success") is not None:
            lines.append(f"    Outcome: {'Success' if d['outcome']['success'] else 'Failed'}")

    if results["patterns"]:
        lines.append("")
        lines.append("PATTERNS")
        for p in results["patterns"]:
            lines.append(f"  * {p}")

    if results["recommendations"]:
        lines.append("")
        lines.append("RECOMMENDATIONS")
        for rec in results["recommendations"]:
            lines.append(f"  * {rec}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Score decision quality across 6 dimensions")
    parser.add_argument("--input", required=True, help="Path to JSON decision assessments file")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    args = parser.parse_args()

    try:
        data = load_data(args.input)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading input file: {e}", file=sys.stderr)
        sys.exit(1)

    results = analyze_decisions(data)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_text(results))


if __name__ == "__main__":
    main()
