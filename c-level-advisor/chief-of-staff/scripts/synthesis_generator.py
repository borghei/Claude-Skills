#!/usr/bin/env python3
"""
Synthesis Generator - Merge multi-advisor outputs into decision-ready format.

Takes independent advisor contributions, identifies consensus and conflicts,
maps dependencies, and frames the decision for founder review.
"""

import argparse
import json
import sys
from datetime import datetime


def synthesize(data: dict) -> dict:
    """Synthesize multiple advisor contributions."""
    topic = data.get("topic", "")
    contributions = data.get("contributions", {})
    complexity = data.get("complexity_score", 5)

    results = {
        "timestamp": datetime.now().isoformat(),
        "topic": topic,
        "complexity_score": complexity,
        "advisors_consulted": list(contributions.keys()),
        "consensus_points": [],
        "disagreements": [],
        "dependencies": [],
        "action_items": [],
        "decision_frame": {},
        "risk_note": "",
    }

    # Extract all recommendations and key points
    all_recommendations = {}
    all_key_points = {}
    all_concerns = {}
    confidence_map = {}

    for role, contrib in contributions.items():
        recommendation = contrib.get("recommendation", "")
        all_recommendations[role] = recommendation
        all_key_points[role] = contrib.get("key_points", [])
        all_concerns[role] = contrib.get("key_concern", "")
        confidence_map[role] = contrib.get("confidence", "Medium")

    # Find consensus (themes mentioned by 2+ advisors)
    point_themes = {}
    for role, points in all_key_points.items():
        for point in points:
            # Simple theme matching by first 3 words
            theme = " ".join(point.lower().split()[:4])
            if theme not in point_themes:
                point_themes[theme] = []
            point_themes[theme].append({"role": role, "point": point})

    for theme, entries in point_themes.items():
        if len(entries) >= 2:
            roles = [e["role"] for e in entries]
            results["consensus_points"].append({
                "point": entries[0]["point"],
                "agreed_by": roles,
                "strength": "Strong" if len(roles) >= 3 else "Moderate",
            })

    # Find disagreements
    rec_clusters = {}
    for role, rec in all_recommendations.items():
        direction = "proceed" if any(w in rec.lower() for w in ["proceed", "go", "invest", "yes", "approve", "recommend"]) else "wait" if any(w in rec.lower() for w in ["wait", "delay", "defer", "pause"]) else "modify" if any(w in rec.lower() for w in ["modify", "adjust", "change", "alternative"]) else "neutral"
        if direction not in rec_clusters:
            rec_clusters[direction] = []
        rec_clusters[direction].append({"role": role, "recommendation": rec, "confidence": confidence_map.get(role, "Medium")})

    if len(rec_clusters) > 1:
        for direction, members in rec_clusters.items():
            if direction != "neutral":
                results["disagreements"].append({
                    "position": direction,
                    "advisors": [m["role"] for m in members],
                    "reasoning": [m["recommendation"] for m in members],
                })

    # Dependencies
    for role, points in all_key_points.items():
        for point in points:
            if any(w in point.lower() for w in ["depends on", "requires", "contingent", "assuming", "if"]):
                results["dependencies"].append({
                    "from_advisor": role,
                    "dependency": point,
                })

    # Action items (max 5)
    action_count = 0
    for role, contrib in contributions.items():
        for action in contrib.get("action_items", []):
            if action_count < 5:
                results["action_items"].append({
                    "action": action.get("action", ""),
                    "owner": action.get("owner", role),
                    "deadline": action.get("deadline", "TBD"),
                    "success_criteria": action.get("success_criteria", ""),
                })
                action_count += 1

    # Decision frame
    if results["disagreements"]:
        option_a = results["disagreements"][0] if len(results["disagreements"]) > 0 else {}
        option_b = results["disagreements"][1] if len(results["disagreements"]) > 1 else {}
        results["decision_frame"] = {
            "question": f"Regarding {topic}: should we {option_a.get('position', 'proceed')} or {option_b.get('position', 'wait')}?",
            "option_a": {
                "position": option_a.get("position", ""),
                "supported_by": option_a.get("advisors", []),
                "trade_off": f"Gain: execution speed. Risk: {all_concerns.get(option_a.get('advisors', [''])[0], 'unknown')}",
            },
            "option_b": {
                "position": option_b.get("position", ""),
                "supported_by": option_b.get("advisors", []),
                "trade_off": f"Gain: reduced risk. Risk: {all_concerns.get(option_b.get('advisors', [''])[0], 'missed opportunity')}",
            },
        }
    else:
        majority_rec = max(all_recommendations.items(), key=lambda x: confidence_map.get(x[0], "Medium") == "High") if all_recommendations else ("", "")
        results["decision_frame"] = {
            "question": f"Regarding {topic}: advisors are aligned on approach.",
            "recommendation": majority_rec[1] if majority_rec else "No recommendation",
            "confidence": "High" if len(results["consensus_points"]) >= 2 else "Medium",
        }

    # Risk note
    low_confidence = [role for role, conf in confidence_map.items() if conf == "Low"]
    if low_confidence:
        results["risk_note"] = f"Low confidence from {', '.join(low_confidence)}. Key assumption may be unvalidated."
    elif results["disagreements"]:
        results["risk_note"] = f"Fundamental disagreement exists ({len(results['disagreements'])} positions). Founder judgment required."
    else:
        results["risk_note"] = "Advisors aligned. Verify assumptions match current market conditions."

    return results


def format_text(results: dict) -> str:
    """Format synthesis as structured output."""
    lines = [
        "=" * 60,
        f"SYNTHESIS: {results['topic']}",
        "=" * 60,
        f"Date: {results['timestamp'][:10]}",
        f"Advisors Consulted: {', '.join(results['advisors_consulted'])}",
        f"Complexity Score: {results['complexity_score']}/10",
        "",
    ]

    if results["consensus_points"]:
        lines.append("CONSENSUS:")
        for cp in results["consensus_points"]:
            lines.append(f"  [{cp['strength']}] {cp['point']} (agreed: {', '.join(cp['agreed_by'])})")
        lines.append("")

    if results["disagreements"]:
        lines.append("DISAGREEMENTS:")
        for d in results["disagreements"]:
            lines.append(f"  Position '{d['position']}': {', '.join(d['advisors'])}")
            for r in d["reasoning"][:1]:
                lines.append(f"    Reasoning: {r}")
        lines.append("")

    if results["action_items"]:
        lines.append("RECOMMENDED ACTIONS:")
        for i, ai in enumerate(results["action_items"], 1):
            lines.append(f"  {i}. {ai['action']} -- Owner: {ai['owner']} -- By: {ai['deadline']}")
        lines.append("")

    df = results["decision_frame"]
    lines.extend(["YOUR DECISION POINT:", f"  {df.get('question', '')}"])
    if "option_a" in df:
        lines.append(f"  Option A ({df['option_a']['position']}): Supported by {', '.join(df['option_a']['supported_by'])}")
        lines.append(f"    Trade-off: {df['option_a']['trade_off']}")
    if "option_b" in df:
        lines.append(f"  Option B ({df['option_b']['position']}): Supported by {', '.join(df['option_b']['supported_by'])}")
        lines.append(f"    Trade-off: {df['option_b']['trade_off']}")
    if "recommendation" in df:
        lines.append(f"  Recommendation: {df['recommendation']} (Confidence: {df.get('confidence', 'Medium')})")

    lines.extend(["", f"RISK NOTE: {results['risk_note']}", "", "=" * 60])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Synthesize multi-advisor contributions")
    parser.add_argument("--input", "-i", help="JSON file with advisor contributions")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if args.input:
        with open(args.input) as f:
            data = json.load(f)
    else:
        data = {
            "topic": "Series B timing",
            "complexity_score": 8,
            "contributions": {
                "CFO": {
                    "recommendation": "Proceed with fundraising in Q2. Metrics are strong enough.",
                    "confidence": "High",
                    "key_points": ["Burn multiple at 1.8x is fundable", "Runway covers 15 months", "NRR at 115% is above median"],
                    "key_concern": "Market window may close if we wait",
                    "action_items": [{"action": "Engage 3 investment banks", "owner": "CFO", "deadline": "2 weeks"}],
                },
                "CEO": {
                    "recommendation": "Proceed but improve burn multiple to 1.5x first for better terms.",
                    "confidence": "Medium",
                    "key_points": ["Burn multiple at 1.8x is fundable but not ideal", "Board relationships are warm", "Market conditions favorable"],
                    "key_concern": "Valuation expectations may not match current metrics",
                    "action_items": [{"action": "Schedule board member pre-conversations", "owner": "CEO", "deadline": "1 week"}],
                },
                "CRO": {
                    "recommendation": "Wait until Q3. Pipeline needs one more quarter to show sustained growth.",
                    "confidence": "Medium",
                    "key_points": ["Pipeline is building but not yet mature", "Q2 pipeline depends on new SDR team ramping"],
                    "key_concern": "Pipeline story may not be convincing enough yet",
                    "action_items": [{"action": "Deliver Q1 pipeline targets", "owner": "CRO", "deadline": "End of Q1"}],
                },
            },
        }

    results = synthesize(data)
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_text(results))


if __name__ == "__main__":
    main()
