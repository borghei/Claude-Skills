#!/usr/bin/env python3
"""
review_authenticity_linter.py — Lint a set of reviews/testimonials before they are
published or used in marketing, against the FTC Consumer Reviews and Testimonials Rule
(16 CFR Part 465), the FTC Endorsement Guides (16 CFR Part 255), the EU Unfair
Commercial Practices Directive review provisions and the UK DMCC Act fake-review ban.

Flags: AI-written or fabricated reviews presented as customer reviews, insider reviews
without disclosure, incentivised reviews without disclosure, incentives conditioned on
sentiment, suppressed negative reviews, substantive business edits, near-duplicate text
and posting bursts. Deterministic heuristics only (no ML, no network). Not legal advice.

Exit codes:
    0  no findings at or above --fail-on
    1  tool error (bad path, malformed JSON)
    2  gate failed: findings at or above --fail-on (default: high)

Usage:
    python3 review_authenticity_linter.py assets/sample_reviews.json
    python3 review_authenticity_linter.py reviews.json --format json --fail-on medium
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

RISK_ORDER = {"low": 1, "medium": 2, "high": 3}
INSIDER_SOURCES = {"employee", "officer", "agent", "agency", "family", "owner"}
NON_CONSUMER_SOURCES = {"ai_tool", "agency_written", "purchased", "unknown_vendor"}
DISCLOSURE_RE = re.compile(
    r"(#ad\b|#sponsored|\bsponsored\b|\bpaid partnership\b|\breceived (this|a|the)? ?"
    r"(product|item|sample)? ?(for )?free\b|\bfree (product|sample)\b|\bin exchange for\b|"
    r"\bdiscount(ed)? (for|in exchange)\b|\bi work (at|for)\b|\bemployee of\b|\bincentivi[sz]ed\b|"
    r"\bgifted\b|\bcommission\b)", re.IGNORECASE)
AI_TELL_RE = re.compile(
    r"(as an ai\b|as a language model|i don't have personal experience|i do not have personal "
    r"experience|\[insert|\[product name\]|\[your name\]|regenerate response)", re.IGNORECASE)
SOURCE = {
    "465": "https://www.ecfr.gov/current/title-16/chapter-I/subchapter-D/part-465",
    "255": "https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255",
    "FAQ": "https://www.ftc.gov/business-guidance/resources/consumer-reviews-testimonials-rule-questions-answers",
    "UCPD": "https://eur-lex.europa.eu/eli/dir/2005/29/oj",
    "CMA": "https://assets.publishing.service.gov.uk/media/67eeb64fe9c76fa33048c790/CMA208_-_Fake_reviews_guidance.pdf",
}


def flag(rid: str, rule: str, risk: str, msg: str, fix: str, src: str) -> dict[str, Any]:
    """Build one finding."""
    return {"review_id": rid, "rule": rule, "risk": risk, "message": msg, "fix": fix, "source": SOURCE[src]}


def shingles(text: str, k: int = 3) -> set[str]:
    """Word k-shingles for near-duplicate detection."""
    words = re.findall(r"[a-z0-9']+", text.lower())
    return {" ".join(words[i:i + k]) for i in range(max(0, len(words) - k + 1))}


def jaccard(a: set[str], b: set[str]) -> float:
    """Jaccard similarity of two sets (0 when both empty)."""
    return len(a & b) / len(a | b) if a and b else 0.0


def lint_review(r: dict[str, Any]) -> list[dict[str, Any]]:
    """Per-review rules."""
    out: list[dict[str, Any]] = []
    rid, text = str(r.get("id", "?")), str(r.get("text", ""))
    src, incentive = r.get("source", "customer"), r.get("incentive", "none")
    disclosed = bool(DISCLOSURE_RE.search(text)) or bool(r.get("disclosure_text"))
    presented_as_consumer = r.get("presented_as", "customer_review") == "customer_review"
    if presented_as_consumer and (r.get("generated_by_ai") or src in NON_CONSUMER_SOURCES):
        out.append(flag(rid, "fake-or-ai-review", "high", "Review not written by a real customer about a real "
                        "experience is presented as a customer review (FTC 465.2; EU UCPD Annex I 23c; UK DMCC)",
                        "Remove it. AI may help a real customer phrase their own review only if the content is "
                        "theirs.", "465"))
    if presented_as_consumer and AI_TELL_RE.search(text):
        out.append(flag(rid, "ai-template-artifact", "medium", "Text contains AI or template artefacts",
                        "Verify the reviewer and the experience; remove if it cannot be verified.", "465"))
    if src in INSIDER_SOURCES and not disclosed:
        out.append(flag(rid, "undisclosed-insider", "high", f"Insider review (source={src}) without a clear "
                        "relationship disclosure (FTC 465.5; Endorsement Guides)",
                        "Add 'I work at [Brand]' (or the actual relationship) inside the review itself.", "465"))
    if incentive != "none" and r.get("incentive_conditioned_on_sentiment"):
        out.append(flag(rid, "sentiment-conditioned-incentive", "high", "Incentive conditioned, expressly or "
                        "by implication, on positive (or negative) sentiment (FTC 465.4)",
                        "Offer incentives for honest reviews only; remove affected reviews.", "465"))
    if incentive != "none" and not disclosed:
        out.append(flag(rid, "undisclosed-incentive", "high", f"Incentivised review (incentive={incentive}) with "
                        "no disclosure (FTC Act s.5 / Endorsement Guides; UK DMCC concealed incentivised review)",
                        "Add a clear disclosure, e.g. 'I received a free sample for this review.'", "255"))
    if r.get("edited_by_business") == "substantive":
        out.append(flag(rid, "business-edited", "medium", "Business substantively edited the review text",
                        "Publish the reviewer's words; limit edits to profanity/PII redaction and say so.", "255"))
    if r.get("suppressed"):
        out.append(flag(rid, "review-suppression", "high", "Review withheld because it was negative while "
                        "displayed reviews imply they are all or most reviews (FTC 465.7; EU/UK also require an "
                        "accurate overall picture)", "Publish all genuine reviews under a neutral moderation "
                        "policy.", "FAQ"))
    if r.get("reused_from_other_product"):
        out.append(flag(rid, "review-hijacking", "high", "Review written for a different product is displayed "
                        "for this one (FTC 465.3)", "Only show reviews of substantially the same product.", "465"))
    return out


def lint_set(reviews: list[dict[str, Any]], dup_threshold: float, burst_share: float) -> list[dict[str, Any]]:
    """Set-level rules: near duplicates and posting bursts."""
    out: list[dict[str, Any]] = []
    sh = [(str(r.get("id", i)), shingles(str(r.get("text", "")))) for i, r in enumerate(reviews)]
    for i in range(len(sh)):
        for j in range(i + 1, len(sh)):
            score = jaccard(sh[i][1], sh[j][1])
            if score >= dup_threshold:
                out.append(flag(f"{sh[i][0]}+{sh[j][0]}", "near-duplicate", "medium", f"Texts are {score:.0%} "
                                "similar - common signature of templated or fabricated reviews",
                                "Verify both reviewers and purchases before publishing.", "465"))
    days = Counter(str(r.get("date", ""))[:10] for r in reviews if r.get("date"))
    if days and len(reviews) >= 5:
        day, n = days.most_common(1)[0]
        if n / len(reviews) >= burst_share:
            out.append(flag("(set)", "posting-burst", "low", f"{n} of {len(reviews)} reviews dated {day}",
                            "Check whether a campaign or vendor produced them; label any solicited batch.", "CMA"))
    return out


def lint(data: Any, dup_threshold: float, burst_share: float) -> dict[str, Any]:
    """Validate input and run all rules."""
    reviews = data.get("reviews") if isinstance(data, dict) else data
    if not isinstance(reviews, list) or not reviews:
        raise ValueError("input must be a list of reviews or an object with a non-empty 'reviews' list")
    findings: list[dict[str, Any]] = []
    for r in reviews:
        if not isinstance(r, dict) or "text" not in r:
            raise ValueError(f"each review needs at least 'id' and 'text': {r}")
        findings += lint_review(r)
    findings += lint_set(reviews, dup_threshold, burst_share)
    counts = {k: sum(1 for f in findings if f["risk"] == k) for k in RISK_ORDER}
    flagged = {f["review_id"] for f in findings if "+" not in f["review_id"] and f["review_id"] != "(set)"}
    return {"reviews_checked": len(reviews), "reviews_flagged": len(flagged), "findings_by_risk": counts,
            "findings": findings,
            "disclaimer": "Heuristic decision support, not legal advice or proof of fraud."}


def render_text(res: dict[str, Any]) -> str:
    """Human-readable report."""
    lines = ["Review Authenticity Lint",
             f"Reviews checked: {res['reviews_checked']}  |  Flagged: {res['reviews_flagged']}  |  "
             + ", ".join(f"{k}={v}" for k, v in res["findings_by_risk"].items()), ""]
    for f in sorted(res["findings"], key=lambda x: (-RISK_ORDER[x["risk"]], x["review_id"])):
        lines += [f"{f['risk'].upper():6} [{f['review_id']}] {f['rule']}", f"       {f['message']}",
                  f"       Fix: {f['fix']}"]
    if not res["findings"]:
        lines.append("No findings.")
    lines += ["", res["disclaimer"]]
    return "\n".join(lines)


def main() -> None:
    """CLI entry point."""
    p = argparse.ArgumentParser(description="Lint reviews/testimonials for authenticity and disclosure issues.")
    p.add_argument("reviews", help="Path to reviews JSON (list, or object with 'reviews')")
    p.add_argument("--format", choices=["text", "json"], default="text", help="Output format (default: text)")
    p.add_argument("--fail-on", choices=["high", "medium", "low"], default="high",
                   help="Lowest risk level that fails the gate with exit 2 (default: high)")
    p.add_argument("--dup-threshold", type=float, default=0.6,
                   help="Jaccard similarity (0-1) of 3-word shingles that counts as near-duplicate (default 0.6)")
    p.add_argument("--burst-share", type=float, default=0.4,
                   help="Share of reviews on a single date that counts as a burst (default 0.4)")
    args = p.parse_args()
    try:
        data = json.loads(Path(args.reviews).read_text(encoding="utf-8"))
        res = lint(data, args.dup_threshold, args.burst_share)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
    threshold = RISK_ORDER[args.fail_on]
    failing = sum(v for k, v in res["findings_by_risk"].items() if RISK_ORDER[k] >= threshold)
    res["gate"] = {"fail_on": args.fail_on, "failing_findings": failing, "passed": failing == 0}
    print(json.dumps(res, indent=2) if args.format == "json" else render_text(res))
    sys.exit(2 if failing else 0)


if __name__ == "__main__":
    main()
