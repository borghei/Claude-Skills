#!/usr/bin/env python3
"""
Pitch Deck Structure Scorer — score a deck summary against required slides
for the given fundraise stage.

Usage:
    python deck_structure_scorer.py deck_summary.md
    python deck_structure_scorer.py deck_summary.md --stage series-a
    python deck_structure_scorer.py deck_summary.md --json
"""

import argparse
import json
import re
import sys
from pathlib import Path


REQUIRED_SLIDES = {
    "seed": [
        {
            "label": "Title / vision slide",
            "patterns": [r"\b(title|vision|company name|tagline|mission)\b"],
            "weight": 5,
            "hint": "Slide 1 should be company name + 1-line vision.",
        },
        {
            "label": "Problem framing",
            "patterns": [r"\bproblem\b", r"\bpain\b", r"\bbroken\b", r"\bwhy (?:now|today|this)\b"],
            "weight": 12,
            "hint": "Frame the problem in customer language. Most missed slide.",
        },
        {
            "label": "Why now",
            "patterns": [r"\bwhy now\b", r"\btiming\b", r"\bshift\b", r"\bunlock\b", r"\bnewly possible\b"],
            "weight": 10,
            "hint": "What changed in the world that makes this newly possible / urgent?",
        },
        {
            "label": "Solution / product",
            "patterns": [r"\b(solution|product|how it works|how we (?:solve|do))\b"],
            "weight": 10,
            "hint": "Show, don't describe. Screenshots > prose.",
        },
        {
            "label": "Market size (TAM / SAM / SOM or bottoms-up)",
            "patterns": [r"\bTAM\b|\bSAM\b|\bSOM\b", r"\bmarket size\b", r"\baddressable\b", r"\$\s*\d+\s*[BMb]"],
            "weight": 10,
            "hint": "Bottoms-up market sizing beats top-down. Show your math.",
        },
        {
            "label": "Business model / how you make money",
            "patterns": [r"\b(business model|monetization|pricing|how we (?:charge|make money)|revenue model)\b"],
            "weight": 8,
            "hint": "Pricing structure + unit economics teaser.",
        },
        {
            "label": "Traction / proof",
            "patterns": [r"\b(traction|growth|users|customers|MRR|ARR|usage|metric|month[- ]over[- ]month)\b"],
            "weight": 12,
            "hint": "Numbers. Even pre-revenue: usage, signups, waitlist, LOIs.",
        },
        {
            "label": "Competition / differentiation",
            "patterns": [r"\b(competition|competitor|alternative|landscape|differentiation|vs\b)\b"],
            "weight": 10,
            "hint": "Don't pretend you have no competition. Position honestly.",
        },
        {
            "label": "Team",
            "patterns": [r"\b(team|founders?|who we are|our background)\b"],
            "weight": 10,
            "hint": "Why are you the team to solve this? Background relevance.",
        },
        {
            "label": "Ask / round",
            "patterns": [r"\b(raising|round|ask|use of (?:funds|proceeds))\b", r"\$\s*\d+\s*[Kk]?\s*(?:seed|round|raise)"],
            "weight": 8,
            "hint": "How much, at what stage, for what milestones?",
        },
    ],
    "series-a": [
        {
            "label": "Title / vision slide",
            "patterns": [r"\b(title|vision|company name|tagline|mission)\b"],
            "weight": 5,
            "hint": "Slide 1.",
        },
        {
            "label": "What we do (one-liner clarity)",
            "patterns": [r"\bwhat we do\b", r"\bwhat (?:is|are)\b.*(?:company|product|platform)\b"],
            "weight": 5,
            "hint": "Series A audience often doesn't know your category. Be clear.",
        },
        {
            "label": "Traction (deep)",
            "patterns": [r"\b(traction|growth|MRR|ARR|net retention|NRR|growth rate|MoM|YoY)\b"],
            "weight": 18,
            "hint": "Series A is bought on traction. Show 12-24 month metric history.",
        },
        {
            "label": "Unit economics / business model",
            "patterns": [r"\b(unit economics|CAC|LTV|payback|gross margin|contribution margin)\b"],
            "weight": 12,
            "hint": "Investors buying Series A model unit economics carefully.",
        },
        {
            "label": "Customer evidence (case studies / quotes)",
            "patterns": [r"\b(case stud|customer quote|testimonial|customer logo)\b"],
            "weight": 8,
            "hint": "Specific customer outcomes; named customers if possible.",
        },
        {
            "label": "Market size (validated bottoms-up)",
            "patterns": [r"\bTAM\b|\bSAM\b|\bSOM\b", r"\bmarket size\b"],
            "weight": 8,
            "hint": "Bottoms-up sizing — by now you have data on average customer value.",
        },
        {
            "label": "Competitive position",
            "patterns": [r"\b(competition|competitor|alternative|landscape|differentiation)\b"],
            "weight": 10,
            "hint": "Map showing position; honest about competitor strengths.",
        },
        {
            "label": "Roadmap / next 12-18 months",
            "patterns": [r"\b(roadmap|next 12|next 18|product roadmap|milestones)\b"],
            "weight": 8,
            "hint": "What does the round buy?",
        },
        {
            "label": "Team (with hires planned)",
            "patterns": [r"\b(team|hires?|hiring plan|key hires|leadership)\b"],
            "weight": 10,
            "hint": "Founders + key hires + planned next hires.",
        },
        {
            "label": "Ask / round / use of funds",
            "patterns": [r"\b(raising|round|ask|use of (?:funds|proceeds))\b"],
            "weight": 10,
            "hint": "Specific amount, specific milestones the round buys.",
        },
        {
            "label": "Why us / founder advantage",
            "patterns": [r"\b(why us|founder.?market fit|why we|unfair advantage|insight)\b"],
            "weight": 6,
            "hint": "What's your unfair advantage / insight?",
        },
    ],
}


def score(text, stage):
    rules = REQUIRED_SLIDES.get(stage, REQUIRED_SLIDES["seed"])
    matched = []
    missing = []
    total_score = 0
    for rule in rules:
        if any(re.search(p, text, re.IGNORECASE | re.MULTILINE) for p in rule["patterns"]):
            total_score += rule["weight"]
            matched.append(rule["label"])
        else:
            missing.append({"label": rule["label"], "hint": rule["hint"], "weight": rule["weight"]})

    # Slide count check (rough — count headings or numbered lines)
    slide_lines = re.findall(r"^\s*(?:#+\s|[0-9]+[.)]\s|slide\s*\d+\s*[:\-])", text, re.IGNORECASE | re.MULTILINE)
    slide_count_estimate = len(slide_lines)

    notes = []
    if stage == "seed" and slide_count_estimate > 14:
        notes.append("Slide count looks high for a seed deck (target 10-12).")
    if stage == "seed" and slide_count_estimate < 8:
        notes.append("Slide count looks low — consider adding traction or competition detail.")
    if stage == "series-a" and slide_count_estimate > 18:
        notes.append("Slide count looks high for a Series A deck (target 12-15).")

    return {
        "stage": stage,
        "score": min(100, total_score),
        "estimated_slide_count": slide_count_estimate,
        "matched": matched,
        "missing": missing,
        "notes": notes,
    }


def render_human(result):
    lines = [f"Pitch Deck Structure — {result['stage']} stage"]
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Score: {result['score']} / 100")
    lines.append(f"Estimated slide count: {result['estimated_slide_count']}")
    lines.append("")
    if result["matched"]:
        lines.append(f"Slides covered ({len(result['matched'])}):")
        for m in result["matched"]:
            lines.append(f"  PASS  {m}")
        lines.append("")
    if result["missing"]:
        lines.append(f"Missing or weak slides ({len(result['missing'])}):")
        for m in result["missing"]:
            lines.append(f"  FAIL  {m['label']} (-{m['weight']})")
            lines.append(f"        Hint: {m['hint']}")
        lines.append("")
    if result["notes"]:
        lines.append("Notes:")
        for n in result["notes"]:
            lines.append(f"  - {n}")
        lines.append("")
    if result["score"] >= 80:
        lines.append("Verdict: strong structure. Iterate on content quality and design.")
    elif result["score"] >= 60:
        lines.append("Verdict: solid structure with 1-2 missing pieces. Close gaps and re-test.")
    else:
        lines.append("Verdict: significant structural gaps. Address before sending.")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Score a pitch deck summary against stage rubric.")
    parser.add_argument("deck_summary", help="Path to deck_summary.md (slide-by-slide markdown)")
    parser.add_argument("--stage", choices=["seed", "series-a"], default="seed", help="Fundraise stage")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    path = Path(args.deck_summary)
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        return 1

    text = path.read_text(encoding="utf-8")
    result = score(text, args.stage)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(render_human(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
