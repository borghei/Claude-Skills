#!/usr/bin/env python3
"""
answer_adjacent_copy_linter.py — Lint ad copy written for placements next to AI answers
(ChatGPT Ads, Google ads in AI Overviews / AI Mode, ads in Microsoft Copilot).

Checks: platform length limits (hard limits = error, recommended ranges = warning),
claims that need substantiation, copy that impersonates or implies endorsement by the
assistant, restricted/sensitive categories per platform, pressure tactics, missing CTA,
landing URL hygiene (https, UTM), unverified price/discount claims, testimonial and
AI-media disclosure gaps, and editorial style (all caps, repeated punctuation).

Length and category facts reflect official platform help pages as of September 2026
(see references/platform-specs.md). Deterministic, standard library only.

Exit codes:
    0  no errors (warnings allowed)
    1  tool error (bad path, malformed JSON, missing fields)
    2  gate failed: one or more errors (or warnings with --strict)

Usage:
    python3 answer_adjacent_copy_linter.py assets/sample_ad_copy.json
    python3 answer_adjacent_copy_linter.py ads.json --format json --strict
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

# (field, min, max, severity) — severity "error" = hard platform limit, "warning" = recommended range
LENGTHS = {
    "chatgpt": [("headline", 16, 24, "warning"), ("body", 32, 48, "warning")],   # OpenAI Help Center guidance
    "google": [("headline", 1, 30, "error"), ("body", 1, 90, "error")],         # RSA headline / description
    "microsoft": [("headline", 1, 30, "error"), ("body", 1, 90, "error")],      # RSA headline / description
}
CLAIM_RE = re.compile(r"(?:#1\b)|\b(best|number one|no\.? ?1|leading|top[- ]rated|cheapest|lowest price|fastest|"
                      r"guaranteed?|clinically (proven|tested)|doctor[- ]recommended|proven|100%|risk[- ]free|"
                      r"cures?|award[- ]winning|most (popular|trusted))\b", re.IGNORECASE)
IMPERSONATION_RE = re.compile(r"\b(chatgpt|gpt|copilot|gemini|ai mode|ai overview|the ai|this assistant)\b.{0,25}"
                              r"\b(recommends?|says|picks?|chose|choice|approved|verified|suggests?|ranks?)\b|"
                              r"\b(recommended|verified|approved|picked|ranked) by (chatgpt|copilot|gemini|ai)\b|"
                              r"\bas an ai\b|\bthe (best )?answer is\b|\bai[- ]verified\b", re.IGNORECASE)
CATEGORY_TERMS = {
    "gambling": r"\b(casino|betting|bet now|sportsbook|poker|slots)\b",
    "dating": r"\b(dating|singles near|hook ?up)\b",
    "alcohol": r"\b(beer|wine|vodka|whisk(e)?y|spirits|cocktail)\b",
    "drugs": r"\b(cbd|cannabis|thc|kratom)\b",
    "health_claims": r"\b(weight loss|lose \d+ ?(lbs|kg|pounds)|cure|treats?|symptoms?|supplement)\b",
    "finance": r"\b(loan|credit card|apr|mortgage|crypto|invest(ment)?s?|debt relief)\b",
    "legal": r"\b(lawyer|attorney|lawsuit|legal advice)\b",
    "political": r"\b(vote|election|candidate|ballot|campaign for)\b",
}
# Platform treatment of category hits (September 2026): chatgpt = not allowed / manual approval;
# google = not shown in AI Overviews (may still serve elsewhere); microsoft = Bing policy applies.
CATEGORY_SEVERITY = {
    "chatgpt": {"finance": "warning", "legal": "warning", "health_claims": "error", "_default": "error"},
    "google": {"_default": "warning"},
    "microsoft": {"political": "error", "_default": "warning"},
}
PRESSURE_RE = re.compile(r"\b(act now|hurry|last chance|only today|ends tonight|don'?t miss|limited time only|"
                         r"before it'?s too late)\b", re.IGNORECASE)
CTA_RE = re.compile(r"\b(shop|buy|compare|see|get|book|try|learn|explore|find|start|order|view|check)\b",
                    re.IGNORECASE)
PRICE_RE = re.compile(r"([$€£]\s?\d|\d+\s?%\s?off|\bfree shipping\b|\bsave \d)", re.IGNORECASE)
TESTIMONIAL_RE = re.compile(r"(customers say|reviewers say|\"[^\"]{8,}\"\s*[-—]\s*\w+|\d(\.\d)?\s?stars?)",
                            re.IGNORECASE)
CAPS_RE = re.compile(r"\b[A-Z]{4,}\b")
PUNCT_RE = re.compile(r"[!?]{2,}")


def issue(ad_id: str, sev: str, rule: str, msg: str) -> dict[str, str]:
    """Build one lint issue."""
    return {"ad_id": ad_id, "severity": sev, "rule": rule, "message": msg}


def lint_ad(ad: dict[str, Any]) -> list[dict[str, str]]:
    """Apply every rule to one ad."""
    aid, plat = str(ad.get("id", "?")), str(ad.get("platform", "")).lower()
    if plat not in LENGTHS:
        raise ValueError(f"ad {aid}: platform must be one of {sorted(LENGTHS)}")
    head, body, cta = str(ad.get("headline", "")), str(ad.get("body", "")), str(ad.get("cta", ""))
    text = f"{head} {body} {cta}"
    out: list[dict[str, str]] = []
    for field, lo, hi, sev in LENGTHS[plat]:
        n = len(str(ad.get(field, "")))
        if n < lo or n > hi:
            out.append(issue(aid, sev, "length", f"{field} is {n} chars; {plat} {'limit' if sev == 'error' else 'recommended'} "
                             f"range {lo}-{hi}"))
    substantiated = {s.lower() for s in ad.get("substantiated_claims", [])}
    for m in sorted({m.group(0).lower() for m in CLAIM_RE.finditer(text)}):
        if m not in substantiated:
            out.append(issue(aid, "error", "unsubstantiated-claim", f"'{m}' needs evidence on file; add it to "
                             "substantiated_claims only if you hold that evidence"))
    if IMPERSONATION_RE.search(text):
        out.append(issue(aid, "error", "assistant-endorsement", "Copy implies the AI assistant recommends or "
                         "verified the product; ads are separate from answers and must not borrow their authority"))
    for cat, pat in CATEGORY_TERMS.items():
        if re.search(pat, text, re.IGNORECASE):
            sev_map = CATEGORY_SEVERITY[plat]
            sev = sev_map.get(cat, sev_map["_default"])
            out.append(issue(aid, sev, f"category-{cat}", f"Copy touches '{cat}' - restricted or not shown next "
                             f"to AI answers on {plat}; confirm eligibility in the platform policy"))
    if PRESSURE_RE.search(text):
        out.append(issue(aid, "warning", "pressure-tactic", "Urgency phrasing reads as manipulative next to a "
                         "neutral answer; lead with a useful fact instead"))
    if not CTA_RE.search(cta or body):
        out.append(issue(aid, "warning", "missing-cta", "No clear action verb (compare, see, get, book...)"))
    url = str(ad.get("landing_url", ""))
    if not url.startswith("https://"):
        out.append(issue(aid, "error", "landing-url", "landing_url missing or not https"))
    elif "utm_source=" not in url and not ad.get("uses_auto_tagging"):
        out.append(issue(aid, "warning", "utm", "No utm_source; GA4 will not separate this from organic AI "
                         "assistant referrals"))
    if PRICE_RE.search(text) and not ad.get("price_matches_landing_and_feed"):
        out.append(issue(aid, "warning", "price-claim", "Price/discount in copy: confirm it matches the landing "
                         "page and product feed at serve time"))
    if TESTIMONIAL_RE.search(text) and not ad.get("testimonial_verified"):
        out.append(issue(aid, "error", "testimonial", "Testimonial or rating in copy without a verified, "
                         "disclosed source (FTC 16 CFR 465 / 255)"))
    if ad.get("ai_generated_media") and not ad.get("ai_label"):
        out.append(issue(aid, "warning", "ai-media-label", "AI-generated image: add an AI label where required "
                         "(EU, India, New York audiences; platform AI label settings)"))
    if CAPS_RE.search(text) or PUNCT_RE.search(text):
        out.append(issue(aid, "warning", "editorial-style", "All-caps words or repeated !/? - commonly "
                         "disapproved by ad editorial policies"))
    return out


def lint(data: Any) -> dict[str, Any]:
    """Validate the input file and lint every ad."""
    ads = data.get("ads") if isinstance(data, dict) else data
    if not isinstance(ads, list) or not ads:
        raise ValueError("input must be a list of ads or an object with a non-empty 'ads' list")
    issues: list[dict[str, str]] = []
    for ad in ads:
        if not isinstance(ad, dict) or "headline" not in ad or "platform" not in ad:
            raise ValueError(f"each ad needs 'id', 'platform', 'headline', 'body': {ad}")
        issues += lint_ad(ad)
    errors = sum(1 for i in issues if i["severity"] == "error")
    clean = [a.get("id") for a in ads if not any(i["ad_id"] == str(a.get("id")) for i in issues)]
    return {"ads_checked": len(ads), "errors": errors, "warnings": len(issues) - errors,
            "clean_ads": clean, "issues": issues}


def render_text(res: dict[str, Any]) -> str:
    """Human-readable report grouped by ad."""
    lines = ["Answer-Adjacent Ad Copy Lint",
             f"Ads: {res['ads_checked']}  |  Errors: {res['errors']}  |  Warnings: {res['warnings']}  |  "
             f"Clean: {', '.join(map(str, res['clean_ads'])) or 'none'}", ""]
    current = None
    for i in sorted(res["issues"], key=lambda x: (x["ad_id"], x["severity"] != "error")):
        if i["ad_id"] != current:
            current = i["ad_id"]
            lines.append(f"[{current}]")
        lines.append(f"  {i['severity'].upper():7} {i['rule']}: {i['message']}")
    return "\n".join(lines)


def main() -> None:
    """CLI entry point."""
    ap = argparse.ArgumentParser(description="Lint ad copy for AI-assistant and AI-search placements.")
    ap.add_argument("ads", help="Path to ads JSON (list, or object with 'ads')")
    ap.add_argument("--format", choices=["text", "json"], default="text", help="Output format (default: text)")
    ap.add_argument("--strict", action="store_true", help="Fail (exit 2) on warnings as well as errors")
    args = ap.parse_args()
    try:
        res = lint(json.loads(Path(args.ads).read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
    failing = res["errors"] + (res["warnings"] if args.strict else 0)
    res["gate"] = {"strict": args.strict, "failing_issues": failing, "passed": failing == 0}
    print(json.dumps(res, indent=2) if args.format == "json" else render_text(res))
    sys.exit(2 if failing else 0)


if __name__ == "__main__":
    main()
