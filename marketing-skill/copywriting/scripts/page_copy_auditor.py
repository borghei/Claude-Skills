#!/usr/bin/env python3
"""
Page Copy Auditor

Audits marketing page copy for conversion principles:
benefit clarity, specificity, customer focus, CTA strength,
objection handling, and social proof.

Usage:
    python page_copy_auditor.py page.txt
    python page_copy_auditor.py page.html --json
"""

import argparse
import json
import re
import sys
from pathlib import Path

HTML_TAG = re.compile(r"<[^>]+>")


def audit_copy(text: str) -> dict:
    # Strip HTML if present
    plain = HTML_TAG.sub(" ", text)
    plain = re.sub(r"\s+", " ", plain).strip()

    sentences = [s.strip() for s in re.split(r"[.!?]+", plain) if s.strip()]
    words = plain.split()
    word_count = len(words)

    result = {
        "word_count": word_count,
        "sentence_count": len(sentences),
        "scores": {},
        "checks": [],
        "issues": [],
        "suggestions": [],
    }

    # 1. Customer focus (you vs we)
    you_count = len(re.findall(r"\b(you|your|you're|yourself)\b", plain, re.IGNORECASE))
    we_count = len(re.findall(r"\b(we|our|we're|us)\b", plain, re.IGNORECASE))
    ratio = you_count / max(we_count, 1)

    if ratio >= 2:
        result["checks"].append({"name": "Customer Focus", "status": "PASS", "detail": f"You/Your: {you_count}, We/Our: {we_count} (ratio: {ratio:.1f}:1)"})
        result["scores"]["customer_focus"] = 90
    elif ratio >= 1:
        result["checks"].append({"name": "Customer Focus", "status": "OK", "detail": f"You: {you_count}, We: {we_count}"})
        result["scores"]["customer_focus"] = 65
    else:
        result["checks"].append({"name": "Customer Focus", "status": "FAIL", "detail": f"We/Our ({we_count}) outnumbers You/Your ({you_count})"})
        result["scores"]["customer_focus"] = 35
        result["issues"].append("Copy is company-focused. Rewrite to lead with 'you' and the customer's world.")

    # 2. Specificity
    numbers = re.findall(r"\d+", plain)
    specific_metrics = re.findall(r"\d+%|\d+x|\$\d+|\d+ (hours|minutes|days|teams|customers|companies)", plain, re.IGNORECASE)
    has_named_companies = bool(re.search(r"(Stripe|Notion|Slack|Linear|Figma|Shopify|HubSpot|\w+\.com)", plain))

    specificity = 30
    if len(specific_metrics) >= 3:
        specificity = 90
    elif len(specific_metrics) >= 1:
        specificity = 65
    if has_named_companies:
        specificity += 10
    if len(numbers) == 0:
        result["issues"].append("No numbers or metrics found. Add specific data for credibility.")

    result["scores"]["specificity"] = min(100, specificity)
    result["checks"].append({"name": "Specificity", "status": "PASS" if specificity >= 70 else "WARN", "detail": f"{len(specific_metrics)} specific metrics, {len(numbers)} numbers total"})

    # 3. Social proof
    social_proof_patterns = [
        re.compile(r"(trusted by|used by|join|loved by)\s+\d+", re.IGNORECASE),
        re.compile(r"\d+\s*(teams|companies|customers|users|businesses)", re.IGNORECASE),
        re.compile(r"(testimonial|review|rating|stars?|4\.\d|5\.0)", re.IGNORECASE),
        re.compile(r'".+"\s*[-—]\s*\w+', re.IGNORECASE),  # quoted testimonial
    ]
    proof_found = sum(1 for p in social_proof_patterns if p.search(plain))

    if proof_found >= 2:
        result["scores"]["social_proof"] = 85
        result["checks"].append({"name": "Social Proof", "status": "PASS", "detail": f"{proof_found} social proof elements found"})
    elif proof_found == 1:
        result["scores"]["social_proof"] = 55
        result["checks"].append({"name": "Social Proof", "status": "WARN", "detail": "Limited social proof"})
        result["suggestions"].append("Add more social proof: testimonials with names, metrics, and specific outcomes.")
    else:
        result["scores"]["social_proof"] = 20
        result["checks"].append({"name": "Social Proof", "status": "FAIL", "detail": "No social proof detected"})
        result["issues"].append("No social proof found. Add testimonials, customer counts, or review scores.")

    # 4. CTA presence
    cta_patterns = [
        re.compile(r"(start|get|try|book|sign up|create|download|claim|unlock|begin|join)\b", re.IGNORECASE),
    ]
    cta_found = sum(1 for p in cta_patterns if p.search(plain))
    cta_mentions = len(re.findall(r"(start|get started|try free|book|sign up|free trial)", plain, re.IGNORECASE))

    if cta_mentions >= 2:
        result["scores"]["cta_presence"] = 85
        result["checks"].append({"name": "CTA Presence", "status": "PASS", "detail": f"{cta_mentions} CTA mentions"})
    elif cta_mentions >= 1:
        result["scores"]["cta_presence"] = 60
        result["checks"].append({"name": "CTA Presence", "status": "WARN", "detail": "Single CTA -- add 2-3 throughout page"})
    else:
        result["scores"]["cta_presence"] = 25
        result["checks"].append({"name": "CTA Presence", "status": "FAIL", "detail": "No clear CTA found"})
        result["issues"].append("No clear CTA detected. Add action-oriented CTAs throughout the page.")

    # 5. Objection handling
    objection_patterns = [
        re.compile(r"(no credit card|cancel anytime|money.back|guarantee|refund|free trial|risk.free)", re.IGNORECASE),
        re.compile(r"(faq|frequently asked|common questions)", re.IGNORECASE),
        re.compile(r"(secure|encrypted|privacy|gdpr|soc 2|iso|compliant)", re.IGNORECASE),
    ]
    objection_count = sum(1 for p in objection_patterns if p.search(plain))

    if objection_count >= 2:
        result["scores"]["objection_handling"] = 85
    elif objection_count == 1:
        result["scores"]["objection_handling"] = 55
        result["suggestions"].append("Add risk reversal near CTAs: 'No credit card required' or 'Cancel anytime'.")
    else:
        result["scores"]["objection_handling"] = 20
        result["issues"].append("No objection handling found. Add FAQs, guarantees, or risk reversal copy.")

    result["checks"].append({"name": "Objection Handling", "status": "PASS" if objection_count >= 2 else "WARN" if objection_count == 1 else "FAIL", "detail": f"{objection_count} objection-handling elements"})

    # 6. Readability
    avg_words_per_sentence = word_count / max(len(sentences), 1)
    if avg_words_per_sentence <= 15:
        result["scores"]["readability"] = 90
    elif avg_words_per_sentence <= 20:
        result["scores"]["readability"] = 70
    else:
        result["scores"]["readability"] = 45
        result["suggestions"].append("Sentences are too long. Break into shorter, punchier sentences.")

    # Overall
    weights = {"customer_focus": 0.20, "specificity": 0.20, "social_proof": 0.20, "cta_presence": 0.15, "objection_handling": 0.15, "readability": 0.10}
    overall = sum(result["scores"].get(k, 50) * w for k, w in weights.items())
    result["overall_score"] = round(overall)
    result["grade"] = "A" if overall >= 85 else "B" if overall >= 70 else "C" if overall >= 55 else "D" if overall >= 40 else "F"

    return result


def format_human(result: dict) -> str:
    lines = ["\n" + "=" * 60, "  PAGE COPY AUDITOR", "=" * 60]
    lines.append(f"\n  Score: {result['overall_score']}/100 ({result['grade']}) | {result['word_count']} words, {result['sentence_count']} sentences")

    lines.append(f"\n  Checks:")
    for c in result["checks"]:
        icon = {"PASS": "+", "WARN": "!", "FAIL": "X", "OK": "~"}
        lines.append(f"    [{icon.get(c['status'], '?')}] {c['name']}: {c['detail']}")

    lines.append(f"\n  Scores:")
    for k, v in sorted(result["scores"].items(), key=lambda x: -x[1]):
        lines.append(f"    {k.replace('_', ' ').title():<20} {v}/100")

    if result["issues"]:
        lines.append(f"\n  Issues:")
        for i in result["issues"]:
            lines.append(f"    X {i}")

    if result["suggestions"]:
        lines.append(f"\n  Suggestions:")
        for s in result["suggestions"]:
            lines.append(f"    > {s}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Audit marketing page copy for conversion potential.")
    parser.add_argument("file", help="Text or HTML file to audit")
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()

    try:
        text = Path(args.file).read_text()
    except FileNotFoundError:
        print(f"Error: {args.file} not found", file=sys.stderr)
        sys.exit(1)

    result = audit_copy(text)
    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print(format_human(result))


if __name__ == "__main__":
    main()
