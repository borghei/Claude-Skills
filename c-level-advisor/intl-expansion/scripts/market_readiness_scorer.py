#!/usr/bin/env python3
"""Market Readiness Scorer - Score and rank target markets using 6-factor weighted framework.

Evaluates international markets on market size, competitive intensity, regulatory
complexity, cultural distance, existing traction, and operational complexity.
Produces a weighted score with go/no-go recommendation.

Usage:
    python market_readiness_scorer.py --market "Germany" --market-size 4 --competition 3 --regulatory 2 --cultural-distance 3 --traction 4 --operational 3
    python market_readiness_scorer.py --market "Japan" --market-size 5 --competition 2 --regulatory 1 --cultural-distance 1 --traction 2 --operational 2 --json
    python market_readiness_scorer.py compare --markets markets.csv --json
"""

import argparse
import json
import sys
from datetime import datetime

FACTORS = {
    "market_size": {
        "name": "Market Size (Addressable)",
        "weight": 0.25,
        "description": "TAM in target segment, willingness to pay, growth rate",
        "scoring_guide": {
            5: "Very large addressable market with proven willingness to pay",
            4: "Large market with good growth rate",
            3: "Medium market, adequate for regional presence",
            2: "Small market, niche opportunity only",
            1: "Minimal addressable market"
        }
    },
    "competition": {
        "name": "Competitive Intensity",
        "weight": 0.20,
        "description": "Incumbent strength, number of alternatives, market gaps",
        "scoring_guide": {
            5: "Few competitors, clear market gap for your offering",
            4: "Moderate competition with differentiable positioning",
            3: "Several competitors but room for new entrants",
            2: "Strong incumbents with established market share",
            1: "Dominant incumbents, extremely hard to penetrate"
        }
    },
    "regulatory": {
        "name": "Regulatory Complexity",
        "weight": 0.20,
        "description": "Barriers to entry, compliance cost, timeline to launch",
        "scoring_guide": {
            5: "Minimal regulatory barriers, fast to launch",
            4: "Light regulation, manageable compliance",
            3: "Moderate regulation, requires legal counsel",
            2: "Heavy regulation, significant compliance investment",
            1: "Extreme regulation, data localization required, long timeline"
        }
    },
    "cultural_distance": {
        "name": "Cultural Distance",
        "weight": 0.15,
        "description": "Language, business practices, buying behavior, sales cycle",
        "scoring_guide": {
            5: "Very similar culture, English-speaking, familiar business practices",
            4: "Low cultural distance, English common in business",
            3: "Moderate cultural adaptation needed, local language helpful",
            2: "Significant cultural differences, local language required",
            1: "Very high cultural distance, local partner essential"
        }
    },
    "traction": {
        "name": "Existing Traction",
        "weight": 0.10,
        "description": "Inbound demand, existing customers, partnership signals",
        "scoring_guide": {
            5: "Strong inbound demand, multiple existing customers",
            4: "Some inbound interest, 1-2 existing customers",
            3: "Partnership signals or adjacent market success",
            2: "Minimal traction, mostly push-driven interest",
            1: "No existing traction or signals"
        }
    },
    "operational": {
        "name": "Operational Complexity",
        "weight": 0.10,
        "description": "Time zones, infrastructure, payment systems, talent pool",
        "scoring_guide": {
            5: "Easy operations: good timezone overlap, strong infrastructure",
            4: "Manageable operations with minor adjustments",
            3: "Moderate complexity: timezone gaps, some infrastructure needs",
            2: "Significant operational challenges",
            1: "Very challenging: extreme timezone, poor infrastructure, limited talent"
        }
    }
}

ENTRY_RECOMMENDATIONS = {
    "strong_go": {"min_score": 4.0, "label": "STRONG GO", "recommendation": "Market shows strong signals. Proceed with entry planning. Consider Local Hire or Full Entity based on existing revenue."},
    "go": {"min_score": 3.2, "label": "GO", "recommendation": "Market is viable. Start with Remote Sales to validate demand before committing resources."},
    "conditional": {"min_score": 2.5, "label": "CONDITIONAL", "recommendation": "Market has potential but significant risks. Validate with 20+ discovery calls before any investment. Define strict exit criteria."},
    "no_go": {"min_score": 0, "label": "NO GO", "recommendation": "Market does not score high enough to justify investment. Focus resources on stronger markets."}
}


def score_market(market_name, scores):
    weighted_total = 0.0
    factor_results = []

    for factor_key, factor_info in FACTORS.items():
        score = scores.get(factor_key, 3)
        weighted = score * factor_info["weight"]
        weighted_total += weighted

        factor_results.append({
            "factor": factor_info["name"],
            "key": factor_key,
            "score": score,
            "weight": factor_info["weight"],
            "weighted_score": round(weighted, 2),
            "description": factor_info["scoring_guide"].get(score, "")
        })

    overall = round(weighted_total, 2)

    # Determine recommendation
    recommendation = ENTRY_RECOMMENDATIONS["no_go"]
    for rec_key in ["strong_go", "go", "conditional", "no_go"]:
        if overall >= ENTRY_RECOMMENDATIONS[rec_key]["min_score"]:
            recommendation = ENTRY_RECOMMENDATIONS[rec_key]
            break

    # Identify risks (scores 1-2)
    risks = [f for f in factor_results if f["score"] <= 2]

    # Identify strengths (scores 4-5)
    strengths = [f for f in factor_results if f["score"] >= 4]

    # Entry mode recommendation based on traction
    traction_score = scores.get("traction", 3)
    if traction_score >= 4:
        entry_mode = "Local Hire (EOR) or Full Entity -- existing traction justifies investment"
    elif traction_score >= 3:
        entry_mode = "Remote Sales for 3-6 months, then evaluate Local Hire"
    else:
        entry_mode = "Remote Sales only -- prove demand before any local investment"

    return {
        "assessment_date": datetime.now().strftime("%Y-%m-%d"),
        "market": market_name,
        "overall_score": overall,
        "max_possible": 5.0,
        "recommendation": recommendation["label"],
        "recommendation_detail": recommendation["recommendation"],
        "entry_mode_suggestion": entry_mode,
        "factor_scores": factor_results,
        "strengths": [{"factor": s["factor"], "score": s["score"]} for s in strengths],
        "risks": [{"factor": r["factor"], "score": r["score"], "description": r["description"]} for r in risks],
        "next_steps": [
            f"Validate traction with 20+ discovery calls in {market_name}",
            f"Engage local legal counsel for regulatory assessment" if scores.get("regulatory", 3) <= 3 else f"Regulatory environment is manageable",
            f"Research local competitors and positioning gaps",
            f"Define 12-month exit criteria: pipeline > $500K, revenue > $200K ARR"
        ]
    }


def print_human(result):
    print(f"\n{'='*70}")
    print(f"MARKET READINESS SCORE: {result['market']}")
    print(f"Date: {result['assessment_date']}")
    print(f"{'='*70}\n")

    print(f"OVERALL SCORE: {result['overall_score']}/{result['max_possible']}")
    print(f"RECOMMENDATION: {result['recommendation']}")
    print(f"  {result['recommendation_detail']}\n")

    print(f"ENTRY MODE: {result['entry_mode_suggestion']}\n")

    print("FACTOR SCORES:")
    print("-" * 60)
    for f in result["factor_scores"]:
        bar = "#" * f["score"] + "." * (5 - f["score"])
        print(f"  {f['factor']:<30s} {f['score']}/5  [{bar}]  (weight: {f['weight']})")

    if result["strengths"]:
        print(f"\nSTRENGTHS:")
        for s in result["strengths"]:
            print(f"  [+] {s['factor']}: {s['score']}/5")

    if result["risks"]:
        print(f"\nRISKS:")
        for r in result["risks"]:
            print(f"  [!] {r['factor']}: {r['score']}/5 -- {r['description']}")

    print(f"\nNEXT STEPS:")
    for n in result["next_steps"]:
        print(f"  -> {n}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Score and rank target markets for international expansion")
    parser.add_argument("--market", required=True, help="Market name (e.g., 'Germany', 'Japan')")
    parser.add_argument("--market-size", type=int, required=True, choices=[1,2,3,4,5], help="Market size score (1-5)")
    parser.add_argument("--competition", type=int, required=True, choices=[1,2,3,4,5], help="Competitive intensity score (1-5, 5=favorable)")
    parser.add_argument("--regulatory", type=int, required=True, choices=[1,2,3,4,5], help="Regulatory complexity (1-5, 5=easy)")
    parser.add_argument("--cultural-distance", type=int, required=True, choices=[1,2,3,4,5], help="Cultural distance (1-5, 5=close)")
    parser.add_argument("--traction", type=int, required=True, choices=[1,2,3,4,5], help="Existing traction (1-5)")
    parser.add_argument("--operational", type=int, required=True, choices=[1,2,3,4,5], help="Operational complexity (1-5, 5=easy)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    scores = {
        "market_size": args.market_size,
        "competition": args.competition,
        "regulatory": args.regulatory,
        "cultural_distance": args.cultural_distance,
        "traction": args.traction,
        "operational": args.operational
    }

    result = score_market(args.market, scores)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_human(result)


if __name__ == "__main__":
    main()
