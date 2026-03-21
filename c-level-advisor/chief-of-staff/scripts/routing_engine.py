#!/usr/bin/env python3
"""
Advisory Routing Engine - Route questions to the right C-suite advisor(s).

Analyzes topics, scores complexity, and determines optimal routing path
(single advisor, dual, multi-advisor, or full board meeting).
"""

import argparse
import json
import sys
from datetime import datetime

ROUTING_TABLE = {
    "fundraising": {"primary": "CFO", "secondary": "CEO", "tertiary": None},
    "financial_model": {"primary": "CFO", "secondary": "CEO", "tertiary": None},
    "burn_rate": {"primary": "CFO", "secondary": "COO", "tertiary": None},
    "hiring": {"primary": "CHRO", "secondary": "COO", "tertiary": "CEO"},
    "org_structure": {"primary": "CHRO", "secondary": "COO", "tertiary": "CEO"},
    "performance": {"primary": "CHRO", "secondary": "CEO", "tertiary": None},
    "product_roadmap": {"primary": "CPO", "secondary": "CTO", "tertiary": None},
    "prioritization": {"primary": "CPO", "secondary": "CTO", "tertiary": None},
    "architecture": {"primary": "CTO", "secondary": "CPO", "tertiary": None},
    "tech_debt": {"primary": "CTO", "secondary": "CFO", "tertiary": None},
    "revenue": {"primary": "CRO", "secondary": "CFO", "tertiary": "CMO"},
    "pricing": {"primary": "CMO", "secondary": "CFO", "tertiary": "CRO"},
    "process": {"primary": "COO", "secondary": "CFO", "tertiary": None},
    "okrs": {"primary": "COO", "secondary": "CEO", "tertiary": None},
    "security": {"primary": "CISO", "secondary": "COO", "tertiary": "CTO"},
    "compliance": {"primary": "CISO", "secondary": "CFO", "tertiary": None},
    "direction": {"primary": "CEO", "secondary": None, "tertiary": None},
    "investors": {"primary": "CEO", "secondary": "CFO", "tertiary": None},
    "market_strategy": {"primary": "CMO", "secondary": "CRO", "tertiary": "CPO"},
    "m_and_a": {"primary": "CEO", "secondary": "CFO", "tertiary": "CTO"},
    "culture": {"primary": "CHRO", "secondary": "CEO", "tertiary": None},
    "international": {"primary": "CEO", "secondary": "CFO", "tertiary": "CRO"},
    "competitive": {"primary": "CMO", "secondary": "CPO", "tertiary": "CRO"},
    "change_management": {"primary": "COO", "secondary": "CHRO", "tertiary": None},
    "board_prep": {"primary": "CEO", "secondary": "CFO", "tertiary": None},
}

TOPIC_KEYWORDS = {
    "fundraising": ["fundraise", "raise", "series", "investors", "term sheet", "valuation"],
    "financial_model": ["financial model", "forecast", "projections", "budget"],
    "burn_rate": ["burn", "runway", "cash", "extend runway"],
    "hiring": ["hire", "recruiting", "headcount", "talent", "candidate"],
    "org_structure": ["reorg", "restructure", "org design", "reporting"],
    "performance": ["performance review", "pip", "underperformer", "promotion"],
    "product_roadmap": ["roadmap", "features", "backlog", "product strategy"],
    "architecture": ["architecture", "tech stack", "infrastructure", "platform"],
    "tech_debt": ["tech debt", "technical debt", "refactor", "legacy"],
    "revenue": ["revenue", "sales", "pipeline", "quota", "deals"],
    "pricing": ["pricing", "price", "packaging", "monetization"],
    "security": ["security", "breach", "vulnerability", "zero trust"],
    "compliance": ["compliance", "soc 2", "iso", "gdpr", "hipaa", "audit"],
    "m_and_a": ["acquisition", "merger", "m&a", "buy", "acquire"],
    "market_strategy": ["positioning", "brand", "marketing strategy", "go to market"],
    "culture": ["culture", "values", "engagement", "morale"],
    "direction": ["vision", "strategy", "direction", "pivot"],
}


def detect_topic(question: str) -> str:
    """Detect topic from question text."""
    question_lower = question.lower()
    best_match = "direction"
    best_score = 0

    for topic, keywords in TOPIC_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in question_lower)
        if score > best_score:
            best_score = score
            best_match = topic

    return best_match


def route_question(data: dict) -> dict:
    """Route a question to the appropriate advisor(s)."""
    question = data.get("question", "")
    topic = data.get("topic") or detect_topic(question)
    complexity = data.get("complexity_score", 5)

    routing = ROUTING_TABLE.get(topic, ROUTING_TABLE["direction"])

    results = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "detected_topic": topic,
        "complexity_score": complexity,
        "routing_type": "",
        "primary_advisor": routing["primary"],
        "secondary_advisor": routing.get("secondary"),
        "tertiary_advisor": routing.get("tertiary"),
        "activated_advisors": [],
        "routing_rationale": [],
        "loop_prevention": {
            "max_depth": 2,
            "path": [],
            "loop_detected": False,
        },
        "quality_checks": [],
    }

    # Determine routing type based on complexity
    if complexity <= 3:
        results["routing_type"] = "SINGLE ADVISOR"
        results["activated_advisors"] = [routing["primary"]]
        results["routing_rationale"].append(f"Low complexity ({complexity}/10) - single advisor sufficient")
    elif complexity <= 6:
        results["routing_type"] = "DUAL ADVISOR"
        advisors = [routing["primary"]]
        if routing.get("secondary"):
            advisors.append(routing["secondary"])
        results["activated_advisors"] = advisors
        results["routing_rationale"].append(f"Medium complexity ({complexity}/10) - dual advisor with synthesis")
    elif complexity <= 8:
        results["routing_type"] = "MULTI-ADVISOR"
        advisors = [routing["primary"]]
        if routing.get("secondary"):
            advisors.append(routing["secondary"])
        if routing.get("tertiary"):
            advisors.append(routing["tertiary"])
        results["activated_advisors"] = advisors
        results["routing_rationale"].append(f"High complexity ({complexity}/10) - multi-advisor with full synthesis")
    else:
        results["routing_type"] = "FULL BOARD MEETING"
        results["activated_advisors"] = [routing["primary"]]
        if routing.get("secondary"):
            results["activated_advisors"].append(routing["secondary"])
        if routing.get("tertiary"):
            results["activated_advisors"].append(routing["tertiary"])
        results["routing_rationale"].append(f"Very high complexity ({complexity}/10) - invoke board-meeting protocol")

    # Quality checks
    results["quality_checks"] = [
        {"check": "Company context loaded", "required": True},
        {"check": "Decision history checked for conflicts", "required": complexity >= 5},
        {"check": "Bottom line appears first in output", "required": True},
        {"check": "Actions have owners and deadlines", "required": True},
        {"check": "Conflicts named explicitly", "required": complexity >= 6},
        {"check": "Maximum 5 bullets per section", "required": True},
    ]

    return results


def format_text(results: dict) -> str:
    """Format as human-readable report."""
    lines = [
        "=" * 60,
        "ADVISORY ROUTING",
        "=" * 60,
        f"Question: {results['question'][:80]}{'...' if len(results['question']) > 80 else ''}",
        f"Topic: {results['detected_topic']}",
        f"Complexity: {results['complexity_score']}/10",
        f"Routing: {results['routing_type']}",
        "",
        f"ACTIVATED ADVISORS: {' -> '.join(results['activated_advisors'])}",
        f"  Primary:   {results['primary_advisor']}",
    ]
    if results["secondary_advisor"]:
        lines.append(f"  Secondary: {results['secondary_advisor']}")
    if results["tertiary_advisor"]:
        lines.append(f"  Tertiary:  {results['tertiary_advisor']}")

    lines.extend(["", "RATIONALE:"])
    for r in results["routing_rationale"]:
        lines.append(f"  {r}")

    lines.extend(["", "QUALITY CHECKS:"])
    for qc in results["quality_checks"]:
        req = "[Required]" if qc["required"] else "[Optional]"
        lines.append(f"  {req} {qc['check']}")

    lines.extend(["", "=" * 60])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Route advisory questions to appropriate C-suite role(s)")
    parser.add_argument("--question", "-q", help="Question to route")
    parser.add_argument("--topic", help="Pre-classified topic")
    parser.add_argument("--complexity", "-c", type=int, default=5, help="Complexity score (1-10)")
    parser.add_argument("--list-topics", action="store_true", help="List all topic routing")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if args.list_topics:
        print("Topic Routing Table:")
        for topic, route in sorted(ROUTING_TABLE.items()):
            advisors = [route["primary"]]
            if route.get("secondary"):
                advisors.append(route["secondary"])
            if route.get("tertiary"):
                advisors.append(route["tertiary"])
            print(f"  {topic:<22} -> {' -> '.join(advisors)}")
        return

    data = {
        "question": args.question or "Should we raise a Series B now or wait until next quarter?",
        "topic": args.topic,
        "complexity_score": args.complexity,
    }

    results = route_question(data)
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_text(results))


if __name__ == "__main__":
    main()
