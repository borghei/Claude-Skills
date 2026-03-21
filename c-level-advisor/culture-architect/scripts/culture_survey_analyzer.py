#!/usr/bin/env python3
"""
Culture Survey Analyzer - Analyze culture health survey results across 8 dimensions.

Calculates dimension scores, overall health rating, identifies strengths and risks,
segments by department/tenure, and generates action recommendations.

Usage:
    python culture_survey_analyzer.py --input survey_data.json
    python culture_survey_analyzer.py --input survey_data.json --json
"""

import argparse
import json
import sys
from datetime import datetime
from statistics import mean, stdev


DIMENSIONS = [
    "psychological_safety", "clarity", "fairness", "growth",
    "trust_in_leadership", "recognition", "belonging", "autonomy"
]

DIMENSION_LABELS = {
    "psychological_safety": "Psychological Safety",
    "clarity": "Clarity",
    "fairness": "Fairness",
    "growth": "Growth",
    "trust_in_leadership": "Trust in Leadership",
    "recognition": "Recognition",
    "belonging": "Belonging",
    "autonomy": "Autonomy",
}


def load_data(path):
    with open(path, "r") as f:
        return json.load(f)


def get_health_label(score):
    if score >= 80:
        return "Healthy"
    elif score >= 65:
        return "Warning"
    elif score >= 50:
        return "Damaged"
    else:
        return "Crisis"


def get_action_timeline(label):
    return {"Healthy": "Maintain", "Warning": "30 days", "Damaged": "14 days", "Crisis": "Immediate"}.get(label, "Review")


def analyze_dimension(responses, dimension):
    """Analyze a single dimension across all responses."""
    scores = []
    for r in responses:
        val = r.get("scores", {}).get(dimension)
        if val is not None:
            scores.append(val)

    if not scores:
        return {"score": 0, "label": "No data", "responses": 0}

    avg = round(mean(scores), 1)
    label = get_health_label(avg)

    result = {
        "score": avg,
        "label": label,
        "action_timeline": get_action_timeline(label),
        "responses": len(scores),
        "min": min(scores),
        "max": max(scores),
    }

    if len(scores) >= 3:
        result["stdev"] = round(stdev(scores), 1)

    return result


def segment_analysis(responses, segment_key):
    """Analyze scores segmented by a key (department, tenure, etc.)."""
    segments = {}
    for r in responses:
        seg = r.get(segment_key, "unknown")
        if seg not in segments:
            segments[seg] = []
        segments[seg].append(r)

    results = {}
    for seg_name, seg_responses in segments.items():
        dim_scores = {}
        for dim in DIMENSIONS:
            scores = [r.get("scores", {}).get(dim, 0) for r in seg_responses if r.get("scores", {}).get(dim) is not None]
            if scores:
                dim_scores[dim] = round(mean(scores), 1)

        overall = round(mean(dim_scores.values()), 1) if dim_scores else 0
        results[seg_name] = {
            "respondents": len(seg_responses),
            "overall_score": overall,
            "health": get_health_label(overall),
            "dimension_scores": dim_scores,
        }

    return results


def calculate_enps(responses):
    """Calculate eNPS from responses."""
    enps_scores = [r.get("enps_score") for r in responses if r.get("enps_score") is not None]
    if not enps_scores:
        return None

    promoters = sum(1 for s in enps_scores if s >= 9) / len(enps_scores) * 100
    detractors = sum(1 for s in enps_scores if s <= 6) / len(enps_scores) * 100
    enps = round(promoters - detractors, 1)

    if enps > 50:
        label = "Exceptional"
    elif enps > 30:
        label = "Good"
    elif enps > 10:
        label = "Acceptable"
    elif enps > 0:
        label = "Concerning"
    else:
        label = "Crisis"

    return {
        "score": enps,
        "label": label,
        "promoters_pct": round(promoters, 1),
        "detractors_pct": round(detractors, 1),
        "passives_pct": round(100 - promoters - detractors, 1),
        "total_responses": len(enps_scores),
    }


def analyze_survey(data):
    """Run full survey analysis."""
    responses = data.get("responses", [])
    org_name = data.get("organization", "Organization")
    survey_date = data.get("survey_date", datetime.now().strftime("%Y-%m-%d"))

    results = {
        "timestamp": datetime.now().isoformat(),
        "organization": org_name,
        "survey_date": survey_date,
        "total_responses": len(responses),
        "participation_rate_pct": data.get("participation_rate_pct", 0),
        "overall_health_score": 0,
        "overall_health_label": "",
        "dimension_results": {},
        "strengths": [],
        "risks": [],
        "enps": None,
        "department_analysis": {},
        "tenure_analysis": {},
        "recommendations": [],
    }

    # Analyze each dimension
    dim_scores = []
    for dim in DIMENSIONS:
        result = analyze_dimension(responses, dim)
        results["dimension_results"][dim] = result
        if result["score"] > 0:
            dim_scores.append(result["score"])

    # Overall score
    if dim_scores:
        results["overall_health_score"] = round(mean(dim_scores), 1)
        results["overall_health_label"] = get_health_label(results["overall_health_score"])

    # Identify strengths and risks
    sorted_dims = sorted(results["dimension_results"].items(), key=lambda x: x[1]["score"], reverse=True)
    results["strengths"] = [
        {"dimension": DIMENSION_LABELS.get(d, d), "score": info["score"]}
        for d, info in sorted_dims[:3] if info["score"] >= 65
    ]
    results["risks"] = [
        {"dimension": DIMENSION_LABELS.get(d, d), "score": info["score"], "action_timeline": info["action_timeline"]}
        for d, info in sorted_dims if info["score"] < 65
    ]

    # eNPS
    results["enps"] = calculate_enps(responses)

    # Segment analysis
    if any(r.get("department") for r in responses):
        results["department_analysis"] = segment_analysis(responses, "department")
    if any(r.get("tenure") for r in responses):
        results["tenure_analysis"] = segment_analysis(responses, "tenure")

    # Recommendations
    recs = results["recommendations"]
    participation = results["participation_rate_pct"]
    if participation > 0 and participation < 50:
        recs.append(f"Low participation ({participation}%) -- results may not be representative; address trust in anonymity")

    for risk in results["risks"][:3]:
        recs.append(f"Address {risk['dimension']} (score: {risk['score']}) within {risk['action_timeline']}")

    if results["enps"] and results["enps"]["score"] < 10:
        recs.append(f"eNPS at {results['enps']['score']} ({results['enps']['label']}) -- investigate detractor feedback")

    # Department-level risks
    for dept, info in results.get("department_analysis", {}).items():
        if info["overall_score"] < 50:
            recs.append(f"Department '{dept}' in crisis (score: {info['overall_score']}) -- targeted intervention needed")

    return results


def format_text(results):
    lines = [
        "=" * 60,
        "CULTURE HEALTH SURVEY ANALYSIS",
        "=" * 60,
        f"Organization: {results['organization']}",
        f"Survey Date: {results['survey_date']}",
        f"Responses: {results['total_responses']} (participation: {results['participation_rate_pct']}%)",
        "",
        f"OVERALL HEALTH: {results['overall_health_score']}/100 ({results['overall_health_label']})",
    ]

    if results["enps"]:
        lines.append(f"eNPS: {results['enps']['score']} ({results['enps']['label']}) -- "
                      f"Promoters: {results['enps']['promoters_pct']}%, Detractors: {results['enps']['detractors_pct']}%")

    lines.append("")
    lines.append("DIMENSION SCORES")
    for dim in DIMENSIONS:
        info = results["dimension_results"].get(dim, {})
        label = DIMENSION_LABELS.get(dim, dim)
        lines.append(f"  {label}: {info.get('score', 0)}/100 ({info.get('label', 'N/A')}) [{info.get('action_timeline', '')}]")

    if results["strengths"]:
        lines.append("")
        lines.append("STRENGTHS")
        for s in results["strengths"]:
            lines.append(f"  + {s['dimension']}: {s['score']}/100")

    if results["risks"]:
        lines.append("")
        lines.append("RISKS")
        for r in results["risks"]:
            lines.append(f"  ! {r['dimension']}: {r['score']}/100 (action: {r['action_timeline']})")

    if results["department_analysis"]:
        lines.append("")
        lines.append("BY DEPARTMENT")
        for dept, info in sorted(results["department_analysis"].items(), key=lambda x: x[1]["overall_score"]):
            lines.append(f"  {dept}: {info['overall_score']}/100 ({info['health']}) -- {info['respondents']} responses")

    if results["recommendations"]:
        lines.append("")
        lines.append("RECOMMENDATIONS")
        for rec in results["recommendations"]:
            lines.append(f"  * {rec}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Analyze culture health survey results across 8 dimensions")
    parser.add_argument("--input", required=True, help="Path to JSON survey data file")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    args = parser.parse_args()

    try:
        data = load_data(args.input)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading input file: {e}", file=sys.stderr)
        sys.exit(1)

    results = analyze_survey(data)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_text(results))


if __name__ == "__main__":
    main()
