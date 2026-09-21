#!/usr/bin/env python3
"""
disclosure_checker.py — Map AI-generated/assisted marketing assets to the disclosures
they need, per jurisdiction and platform, with a risk level and a CI-friendly exit code.

Reads a content manifest (JSON; see assets/content_manifest_template.json) and applies
deterministic rules for: EU AI Act Art. 50, US FTC Consumer Reviews and Testimonials
Rule (16 CFR Part 465), FTC Endorsement Guides (16 CFR Part 255), New York synthetic
performer ad disclosure law, India IT Rules synthetic-content labelling, and platform
AI-label policies (YouTube, TikTok, Meta, Google Ads). Rules reflect sources checked
September 2026 — see references/regulation-summaries.md. Not legal advice.

Exit codes:
    0  no unresolved findings at or above the --fail-on level
    1  tool error (bad path, malformed JSON, missing fields)
    2  gate failed: unresolved findings at or above the --fail-on level (default: high)

Usage:
    python3 disclosure_checker.py assets/sample_content_manifest.json
    python3 disclosure_checker.py manifest.json --format json --fail-on medium
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

RISK_ORDER = {"low": 1, "medium": 2, "high": 3}
VISUAL_AUDIO = {"image", "video", "audio"}
AI_MATERIAL = {"partial", "generated"}  # "none" and "assistive" (standard editing) do not trigger AI labels
REVIEW_TYPES = {"review", "testimonial", "endorsement"}
META_CHANNELS = {"meta", "facebook", "instagram", "threads"}
CONNECTION_WORDING = {
    "employee": "I work at [Brand].",
    "paid": "Ad | Paid partnership with [Brand].",
    "free_product": "[Brand] sent me this product for free.",
    "discount": "I received a discount from [Brand] for this review.",
    "affiliate": "I earn a commission if you buy through this link.",
    "family": "[Brand] is owned by a member of my family.",
}

SOURCES = {
    "EU": "https://eur-lex.europa.eu/eli/reg/2024/1689/oj (Art. 50); "
          "https://digital-strategy.ec.europa.eu/en/faqs/transparency-obligations-under-article-50-ai-act",
    "FTC465": "https://www.ecfr.gov/current/title-16/chapter-I/subchapter-D/part-465",
    "FTC255": "https://www.ecfr.gov/current/title-16/chapter-I/subchapter-B/part-255",
    "NY": "https://www.governor.ny.gov/news/governor-hochul-announces-first-nation-law-requiring-disclosure-when-advertisements-include-ai",
    "IN": "https://www.meity.gov.in/static/uploads/2026/02/550681ab908f8afb135b0ad42816a1c9.pdf",
    "UCPD": "https://eur-lex.europa.eu/eli/dir/2005/29/oj (Annex I points 11, 22, 23b, 23c)",
    "UK": "https://assets.publishing.service.gov.uk/media/67eeb64fe9c76fa33048c790/CMA208_-_Fake_reviews_guidance.pdf",
    "YOUTUBE": "https://support.google.com/youtube/answer/14328491",
    "TIKTOK": "https://ads.tiktok.com/help/article/tiktok-ads-policy-misleading-and-false-content",
    "META": "https://transparency.meta.com/policies/ad-standards/SIEP-advertising/SIEP",
    "GADS_POL": "https://support.google.com/adspolicy/answer/6014595",
    "GADS_AI": "https://support.google.com/adspolicy/answer/17257106",
}


def finding(asset: dict[str, Any], rule: str, juris: str, req: str, risk: str,
            needs: list[str], wording: str, src: str, fixable: bool = True) -> dict[str, Any]:
    """Build one finding; resolved when any accepted disclosure is present and the issue is fixable."""
    present = set(asset.get("disclosures_present", []))
    resolved = fixable and (not needs or bool(present.intersection(needs)))
    return {"asset_id": asset.get("id", "?"), "rule": rule, "jurisdiction": juris,
            "requirement": req, "risk": risk, "needs_one_of": needs,
            "status": "resolved" if resolved else "unresolved",
            "suggested_wording": wording, "source": SOURCES[src]}


def eu_rules(a: dict[str, Any]) -> list[dict[str, Any]]:
    """EU AI Act Art. 50 deployer (50(4)) and provider (50(1), 50(2)) duties."""
    out: list[dict[str, Any]] = []
    ai, typ = a.get("ai_involvement", "none"), a.get("type", "")
    if typ == "chatbot":
        out.append(finding(a, "EU-AIA-50(1)", "EU", "Tell people they are interacting with an AI system "
                           "from the first interaction, unless obvious", "high", ["ai_interaction_notice"],
                           "You're chatting with an AI assistant.", "EU"))
    if ai in AI_MATERIAL and typ in VISUAL_AUDIO and a.get("realistic"):
        if a.get("artistic_or_satirical"):
            out.append(finding(a, "EU-AIA-50(4)-deepfake-artistic", "EU", "Disclose deepfake in an "
                               "appropriate manner that does not hamper enjoyment of the work", "medium",
                               ["ai_label", "platform_ai_toggle"], "Contains AI-generated imagery.", "EU"))
        else:
            out.append(finding(a, "EU-AIA-50(4)-deepfake", "EU", "Deployer must disclose that realistic "
                               "image/audio/video content is artificially generated or manipulated", "high",
                               ["ai_label"], "AI-generated. This scene did not take place.", "EU"))
    if ai in AI_MATERIAL and typ == "text" and a.get("public_interest"):
        if a.get("human_review") and a.get("editorial_responsibility"):
            out.append(finding(a, "EU-AIA-50(4)-text-exempt", "EU", "Human review + editorial "
                               "responsibility exception claimed: keep review evidence (who, when, what changed)",
                               "low", [], "", "EU"))
        else:
            out.append(finding(a, "EU-AIA-50(4)-text", "EU", "Label AI-generated text published to inform "
                               "the public on matters of public interest (or put it under documented editorial "
                               "control)", "high", ["ai_label"], "This article was generated with AI.", "EU"))
    if a.get("own_generator_offered_to_others") and ai in AI_MATERIAL:
        out.append(finding(a, "EU-AIA-50(2)-marking", "EU", "Provider duty: machine-readable marking of "
                           "outputs (systems on the market before 2 Aug 2026: from 2 Dec 2026)", "medium",
                           ["machine_readable_marking"], "Embed C2PA/watermark metadata at export.", "EU"))
    return out


def us_rules(a: dict[str, Any], regions: set[str]) -> list[dict[str, Any]]:
    """FTC Part 465 / Part 255 plus New York synthetic performer law."""
    out: list[dict[str, Any]] = []
    typ, ai, conn = a.get("type", ""), a.get("ai_involvement", "none"), a.get("material_connection", "none")
    if typ in REVIEW_TYPES and ai == "generated" and not a.get("virtual_influencer"):
        out.append(finding(a, "FTC-465.2-fake-review", "US", "AI-generated review/testimonial presented as a "
                           "real person's experience is prohibited; a label does not cure it — remove it", "high",
                           [], "", "FTC465", fixable=False))
    if typ in REVIEW_TYPES and conn != "none":
        out.append(finding(a, "FTC-255-material-connection", "US", f"Disclose the material connection "
                           f"({conn}) clearly and conspicuously, in the endorsement itself", "high",
                           ["material_connection"], CONNECTION_WORDING.get(conn, "Ad | Paid partnership with "
                           "[Brand]."), "FTC255"))
    if typ in REVIEW_TYPES and conn == "employee":
        out.append(finding(a, "FTC-465.5-insider", "US", "Insider (officer/manager/employee/agent) reviews need "
                           "a clear and conspicuous relationship disclosure", "high", ["material_connection"],
                           "I work at [Brand].", "FTC465"))
    if a.get("virtual_influencer"):
        out.append(finding(a, "FTC-255-virtual-influencer", "US", "Virtual influencers are endorsers: disclose "
                           "the brand relationship; do not imply real-world use", "medium",
                           ["ad_disclosure", "material_connection"], "#ad — [Name] is a virtual character "
                           "created by [Brand].", "FTC255"))
    if ("US-NY" in regions and a.get("is_paid_ad") and a.get("synthetic_performer")
            and typ in {"image", "video"}):
        out.append(finding(a, "NY-synthetic-performer", "US-NY", "Ad containing an AI synthetic performer must "
                           "conspicuously disclose it (audio-only ads excluded)", "high",
                           ["synthetic_performer_disclosure", "ai_label"],
                           "This ad features an AI-generated performer.", "NY"))
    return out


def other_region_rules(a: dict[str, Any], regions: set[str]) -> list[dict[str, Any]]:
    """EU UCPD review rules, UK DMCC fake-review ban and India synthetic-content labelling."""
    out: list[dict[str, Any]] = []
    typ, ai = a.get("type", ""), a.get("ai_involvement", "none")
    if "UK" in regions and typ in REVIEW_TYPES and a.get("material_connection", "none") != "none":
        out.append(finding(a, "UK-DMCC-incentivised-review", "UK", "Reviews by incentivised or connected reviewers "
                           "must be clearly marked; concealed incentivised reviews are banned (DMCC Act, 6 Apr 2025)", "high",
                           ["material_connection"], CONNECTION_WORDING.get(a.get("material_connection", ""), "Incentivised review."), "UK"))
    if "EU" in regions and typ in REVIEW_TYPES and ai == "generated" and not a.get("virtual_influencer"):
        out.append(finding(a, "EU-UCPD-false-review", "EU", "Submitting or commissioning false consumer reviews "
                           "is a blacklisted unfair commercial practice — remove it", "high", [], "", "UCPD",
                           fixable=False))
    if "EU" in regions and typ in REVIEW_TYPES and a.get("material_connection", "none") != "none":
        out.append(finding(a, "EU-UCPD-hidden-marketing", "EU", "Do not present paid/insider content as a "
                           "consumer's independent opinion; make the commercial intent clear", "high",
                           ["material_connection", "ad_disclosure"], "Sponsored | Werbung | Publicite", "UCPD"))
    if "IN" in regions and ai in AI_MATERIAL and typ in VISUAL_AUDIO and a.get("realistic"):
        out.append(finding(a, "IN-IT-Rules-SGI", "IN", "Synthetically generated content: visible label "
                           "expected by intermediaries under IT Rules amendment (in force 20 Feb 2026)",
                           "medium", ["ai_label", "platform_ai_toggle"], "AI-generated", "IN"))
    return out


def platform_rules(a: dict[str, Any], regions: set[str]) -> list[dict[str, Any]]:
    """Platform AI-label policies; platforms can reject ads or apply labels themselves."""
    out: list[dict[str, Any]] = []
    ch, typ, ai = a.get("channel", ""), a.get("type", ""), a.get("ai_involvement", "none")
    realistic_ai = ai in AI_MATERIAL and typ in VISUAL_AUDIO and a.get("realistic")
    if ch == "youtube" and realistic_ai:
        out.append(finding(a, "YT-altered-synthetic", "YouTube", "Tick 'altered or synthetic content' at upload "
                           "for realistic AI content", "high" if a.get("depicts_real_people") else "medium",
                           ["platform_ai_toggle"], "Use YouTube Studio disclosure toggle.", "YOUTUBE"))
    if ch == "tiktok" and realistic_ai:
        paid = bool(a.get("is_paid_ad"))
        out.append(finding(a, "TT-AIGC-label", "TikTok", "Apply the AIGC label or a clear disclaimer; "
                           "undisclosed AIGC ads are rejected or restricted", "high" if paid else "medium",
                           ["platform_ai_toggle", "ai_label"], "AI-generated", "TIKTOK"))
    if ch in META_CHANNELS and a.get("political") and ai in AI_MATERIAL:
        out.append(finding(a, "META-SIEP-AI", "Meta", "Social issue/electoral/political ads: self-disclose "
                           "AI-created or altered media", "high", ["platform_ai_toggle"],
                           "Use the AI disclosure in Ads Manager.", "META"))
    if ch == "google_ads" and a.get("political") and realistic_ai:
        out.append(finding(a, "GADS-election-synthetic", "Google Ads", "Election ads: tick 'altered or "
                           "synthetic content' checkbox", "high", ["platform_ai_toggle"],
                           "Tick the synthetic content checkbox.", "GADS_POL"))
    if (ch == "google_ads" and ai in AI_MATERIAL and typ in {"image", "video"}
            and regions.intersection({"EU", "IN", "US-NY"})):
        out.append(finding(a, "GADS-ai-label-setting", "Google Ads", "Use the AI label setting or an in-creative "
                           "label for EU/India/New York audiences (setting alone does not guarantee compliance)",
                           "medium", ["platform_ai_toggle", "ai_label"], "AI-generated", "GADS_AI"))
    return out


def check(manifest: dict[str, Any]) -> dict[str, Any]:
    """Run every rule over every asset and aggregate by risk and status."""
    assets = manifest.get("assets")
    if not isinstance(assets, list) or not assets:
        raise ValueError("manifest must contain a non-empty 'assets' list")
    findings: list[dict[str, Any]] = []
    for a in assets:
        if "id" not in a or "type" not in a:
            raise ValueError(f"asset missing 'id' or 'type': {a}")
        regions = set(a.get("regions", []))
        if "US-NY" in regions:
            regions.add("US")
        if "EU" in regions:
            findings += eu_rules(a)
        if "US" in regions:
            findings += us_rules(a, regions)
        findings += other_region_rules(a, regions) + platform_rules(a, regions)
    unresolved = [f for f in findings if f["status"] == "unresolved"]
    counts = {r: sum(1 for f in unresolved if f["risk"] == r) for r in RISK_ORDER}
    return {"campaign": manifest.get("campaign", ""), "assets_checked": len(assets),
            "asset_ids": [a["id"] for a in assets],
            "findings": findings, "unresolved_by_risk": counts,
            "disclaimer": "Decision support, not legal advice. Confirm with counsel for your markets."}


def render_text(result: dict[str, Any]) -> str:
    """Human-readable report grouped by asset."""
    lines = [f"AI Content Disclosure Check — {result['campaign'] or 'unnamed campaign'}",
             f"Assets checked: {result['assets_checked']}  |  Unresolved: "
             + ", ".join(f"{k}={v}" for k, v in result["unresolved_by_risk"].items()), ""]
    by_asset: dict[str, list[dict[str, Any]]] = {}
    for f in result["findings"]:
        by_asset.setdefault(f["asset_id"], []).append(f)
    for aid in result["asset_ids"]:
        items = by_asset.get(aid, [])
        if not items:
            lines += [f"[{aid}]", "  --  no disclosure rule triggered (check ai_involvement/regions are right)", ""]
            continue
        lines.append(f"[{aid}]")
        for f in sorted(items, key=lambda x: -RISK_ORDER[x["risk"]]):
            mark = "OK  " if f["status"] == "resolved" else "FIX "
            lines.append(f"  {mark}{f['risk'].upper():6} {f['rule']} ({f['jurisdiction']})")
            lines.append(f"       {f['requirement']}")
            if f["status"] == "unresolved" and f["suggested_wording"]:
                lines.append(f"       Suggested: \"{f['suggested_wording']}\"")
        lines.append("")
    lines.append(result["disclaimer"])
    return "\n".join(lines)


def main() -> None:
    """CLI entry point."""
    p = argparse.ArgumentParser(description="Check AI-content and endorsement disclosures in a content "
                                "manifest (EU AI Act Art. 50, FTC, NY, UK, India, platform policies).")
    p.add_argument("manifest", help="Path to content manifest JSON")
    p.add_argument("--format", choices=["text", "json"], default="text", help="Output format (default: text)")
    p.add_argument("--fail-on", choices=["high", "medium", "low"], default="high",
                   help="Lowest unresolved risk level that fails the gate with exit 2 (default: high)")
    args = p.parse_args()
    try:
        manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
        result = check(manifest)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
    threshold = RISK_ORDER[args.fail_on]
    failing = sum(v for k, v in result["unresolved_by_risk"].items() if RISK_ORDER[k] >= threshold)
    result["gate"] = {"fail_on": args.fail_on, "failing_findings": failing, "passed": failing == 0}
    print(json.dumps(result, indent=2) if args.format == "json" else render_text(result))
    sys.exit(2 if failing else 0)


if __name__ == "__main__":
    main()
