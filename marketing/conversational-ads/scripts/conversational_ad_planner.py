#!/usr/bin/env python3
"""
conversational_ad_planner.py — Plan a first test of ads in AI assistants and AI search
(ChatGPT Ads, Google ads in AI Overviews / AI Mode, ads in Microsoft Copilot).

Input: a JSON brief (product, category, regions, language, monthly budget, target CPA,
intent prompts with funnel stage, readiness flags). Output: platform eligibility with
reasons, placement mix, a holdout-based incrementality test plan, KPI targets and a
readiness checklist. Platform facts are encoded as of September 2026 from official help
pages (see references/platform-specs.md) — re-verify before spending.

Deterministic, standard library only.

Exit codes:
    0  plan produced, no blockers
    1  tool error (bad path, malformed JSON, missing fields)
    2  plan produced but blocked: no eligible platform, or budget too small for a
       readable holdout test at the target CPA

Usage:
    python3 conversational_ad_planner.py assets/sample_plan_input.json
    python3 conversational_ad_planner.py brief.json --format json --min-conversions 50
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Categories each platform excludes or gates (as of September 2026, official help pages).
CHATGPT_BLOCKED = {"political", "gambling", "adult", "dating", "alcohol", "drugs"}
CHATGPT_GATED = {"finance", "healthcare", "legal"}  # manual, case-by-case approval
GOOGLE_AIO_EXCLUDED = {"adult", "alcohol", "gambling", "finance", "healthcare", "political"}
GOOGLE_AIO_COUNTRIES = {"AU", "CA", "IN", "ID", "KE", "MY", "NZ", "NG", "PK", "PH", "SG", "US"}
# ChatGPT Ads markets named in OpenAI announcements through Aug 2026 (verify at ads.openai.com).
CHATGPT_MARKETS = {"US", "UK", "EU", "IN", "MX", "BR", "JP", "KR", "MENA"}
STAGE_WEIGHTS = {  # relative fit of each platform to each conversational stage
    "research": {"chatgpt_ads": 0.45, "google_ai_overviews": 0.35, "microsoft_copilot": 0.20},
    "compare": {"chatgpt_ads": 0.40, "google_ai_overviews": 0.35, "microsoft_copilot": 0.25},
    "purchase": {"chatgpt_ads": 0.25, "google_ai_overviews": 0.50, "microsoft_copilot": 0.25},
    "support": {"chatgpt_ads": 0.20, "google_ai_overviews": 0.50, "microsoft_copilot": 0.30},
}
SENSITIVE_WORDS = ("symptom", "diagnos", "depress", "anxiety", "loan", "debt", "lawyer", "election",
                   "vote", "medication", "therapy", "bet ", "casino")


def eligibility(brief: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Return per-platform eligibility with human-readable reasons."""
    cat, regions = brief.get("category", "").lower(), set(brief.get("regions", []))
    lang = brief.get("language", "en").lower()
    out: dict[str, dict[str, Any]] = {}
    reasons: list[str] = []
    ok = True
    if cat in CHATGPT_BLOCKED:
        ok, reasons = False, [f"category '{cat}' not allowed in ChatGPT Ads"]
    elif cat in CHATGPT_GATED:
        reasons.append(f"category '{cat}' needs manual approval; plan a fallback")
    if not regions & CHATGPT_MARKETS:
        ok = False
        reasons.append("no target region in announced ChatGPT Ads markets")
    reasons.append("ads not shown to under-18s, in Temporary Chats, or on Plus/Pro/Business/Enterprise/Edu")
    out["chatgpt_ads"] = {"eligible": ok, "reasons": reasons,
                          "buy": "direct: ChatGPT Ads Manager campaign (CPC or outcome bidding)"}

    reasons, ok = [], True
    if cat in GOOGLE_AIO_EXCLUDED:
        ok = False
        reasons.append(f"sensitive vertical '{cat}' excluded from ads in AI Overviews")
    if not regions & GOOGLE_AIO_COUNTRIES:
        ok = False
        reasons.append("no target country in the AI Overviews ads country list")
    if lang != "en":
        ok = False
        reasons.append("AI Overviews ads currently English only")
    if not brief.get("uses_broad_match_pmax_or_shopping", False):
        reasons.append("needs Search with broad match / AI Max, Shopping or PMax to be matched")
    reasons.append("no opt-out, no direct targeting, no segmented reporting (reported as Top ads)")
    out["google_ai_overviews"] = {"eligible": ok, "reasons": reasons,
                                  "buy": "indirect: fund Search broad/AI Max, Shopping or PMax; placement not buyable"}

    reasons, ok = [], True
    if cat in {"political"}:
        ok = False
        reasons.append("political ads not served")
    if not brief.get("has_logo_asset", False):
        reasons.append("Search ads need a logo (extension) to be eligible in Copilot")
    reasons.append("auto opt-in, no opt-out, no Copilot-specific metrics; negative keywords apply")
    out["microsoft_copilot"] = {"eligible": ok, "reasons": reasons,
                                "buy": "indirect: fund PMax / Search (with logo) / Shopping; placement not buyable"}
    return out


def placement_mix(intents: list[dict[str, Any]], elig: dict[str, dict[str, Any]]) -> dict[str, float]:
    """Weight platforms by the funnel stages of the supplied intent prompts."""
    score = {p: 0.0 for p in elig}
    for it in intents:
        weights = STAGE_WEIGHTS.get(it.get("stage", "research"), STAGE_WEIGHTS["research"])
        vol = float(it.get("weight", 1.0))
        for p, w in weights.items():
            if elig[p]["eligible"]:
                score[p] += w * vol
    total = sum(score.values())
    return {p: round(v / total, 3) for p, v in score.items()} if total else {p: 0.0 for p in score}


def test_plan(brief: dict[str, Any], mix: dict[str, float], min_conv: int, holdout: float) -> dict[str, Any]:
    """Budget split, holdout design, expected conversions and KPI targets."""
    budget, cpa = float(brief["monthly_budget"]), float(brief["target_cpa"])
    weeks = int(brief.get("test_weeks", 6))
    spend = budget * weeks / 4.33
    arms = []
    for p, share in mix.items():
        if share <= 0:
            continue
        arm_spend = spend * share
        exp_conv = arm_spend / (cpa * 1.3)  # assume 30% CPA premium while platforms learn
        arms.append({"platform": p, "share": share, "test_spend": round(arm_spend, 2),
                     "expected_conversions": round(exp_conv, 1),
                     "readable": exp_conv >= min_conv})
    aov = float(brief.get("avg_order_value", 0) or 0)
    return {
        "test_weeks": weeks, "total_test_spend": round(spend, 2), "arms": arms,
        "holdout": {"design": "geo holdout (matched regions dark on conversational placements)"
                    if brief.get("can_geo_split", True) else "time-based on/off alternation (2-week blocks)",
                    "holdout_share": holdout,
                    "read": "incremental conversions = treated - holdout (scaled); "
                            "compare with platform-reported conversions"},
        "kpi_targets": {"target_cpa": cpa, "max_cpa_during_learning": round(cpa * 1.3, 2),
                        "roas_at_target_cpa": round(aov / cpa, 2) if aov else None,
                        "min_conversions_per_arm": min_conv,
                        "min_ctr_note": "no public benchmark yet; set baseline in weeks 1-2"},
    }


def readiness(brief: dict[str, Any], intents: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Readiness checklist items with status."""
    items = [
        ("conversion_tracking", brief.get("has_conversion_tracking"),
         "Pixel/Conversions API (ChatGPT), Google tag, Microsoft UET live and deduplicated"),
        ("product_feed", brief.get("has_product_feed"),
         "Clean product feed (Merchant Center / Microsoft / ChatGPT product feeds) with price + availability"),
        ("landing_pages_answer_first", brief.get("landing_pages_answer_first"),
         "Landing page answers the prompt in the first screen (specs, price, comparison)"),
        ("utm_convention", brief.get("has_utm_convention"),
         "UTM convention: utm_source=<platform>, utm_medium=cpc, campaign ids via platform macros"),
        ("logo_asset", brief.get("has_logo_asset"), "Logo/image assets for Copilot and ChatGPT image slots"),
    ]
    out = [{"item": k, "status": "ready" if v else "missing", "action": a} for k, v, a in items]
    risky = [i["prompt"] for i in intents if any(w in i.get("prompt", "").lower() for w in SENSITIVE_WORDS)]
    if risky:
        out.append({"item": "sensitive_prompts", "status": "warning",
                    "action": "Sensitive-topic prompts won't carry ads on ChatGPT/AI Overviews: " + "; ".join(risky)})
    return out


def build(brief: dict[str, Any], min_conv: int, holdout: float) -> dict[str, Any]:
    """Validate brief and assemble the plan."""
    for key in ("product", "category", "regions", "monthly_budget", "target_cpa", "intents"):
        if key not in brief:
            raise ValueError(f"brief missing required field '{key}'")
    intents = brief["intents"]
    if not isinstance(intents, list) or not intents:
        raise ValueError("'intents' must be a non-empty list of {prompt, stage}")
    elig = eligibility(brief)
    mix = placement_mix(intents, elig)
    plan = test_plan(brief, mix, min_conv, holdout)
    blockers = []
    if not any(e["eligible"] for e in elig.values()):
        blockers.append("no eligible conversational placement for this category/region/language")
    if not brief.get("has_conversion_tracking"):
        blockers.append("no conversion tracking - the test cannot be read; install pixel/CAPI/tags first")
    unreadable = [a["platform"] for a in plan["arms"] if not a["readable"]]
    if unreadable:
        blockers.append(f"budget too small for >= {min_conv} conversions per arm on: {', '.join(unreadable)} "
                        "- concentrate budget on fewer platforms or extend the test")
    return {"product": brief["product"], "as_of": "2026-09", "eligibility": elig, "placement_mix": mix,
            "test_plan": plan, "readiness": readiness(brief, intents), "blockers": blockers}


def render_text(r: dict[str, Any]) -> str:
    """Human-readable plan."""
    L = [f"Conversational Ads Plan — {r['product']} (platform facts as of {r['as_of']})", "", "ELIGIBILITY"]
    for p, e in r["eligibility"].items():
        L.append(f"  {'YES' if e['eligible'] else 'NO '} {p}")
        L += [f"        buy: {e['buy']}"] + [f"        - {x}" for x in e["reasons"]]
    L += ["", "PLACEMENT MIX"] + [f"  {p:22} {s:6.1%}" for p, s in r["placement_mix"].items()]
    t = r["test_plan"]
    L += ["", f"TEST PLAN ({t['test_weeks']} weeks, spend {t['total_test_spend']:,.2f})"]
    for a in t["arms"]:
        L.append(f"  {a['platform']:22} spend {a['test_spend']:>10,.2f}  exp. conv {a['expected_conversions']:>6}"
                 f"  {'readable' if a['readable'] else 'UNDERPOWERED'}")
    h = t["holdout"]
    L += [f"  Holdout: {h['design']}, {h['holdout_share']:.0%} of eligible regions/time", f"  Read: {h['read']}",
          "", "KPI TARGETS"] + [f"  {k}: {v}" for k, v in t["kpi_targets"].items()]
    L += ["", "READINESS"] + [f"  [{i['status'].upper():7}] {i['item']}: {i['action']}" for i in r["readiness"]]
    L += ["", "BLOCKERS"] + ([f"  ! {b}" for b in r["blockers"]] or ["  none"])
    return "\n".join(L)


def main() -> None:
    """CLI entry point."""
    ap = argparse.ArgumentParser(description="Plan a conversational/AI-search ad test with holdout.")
    ap.add_argument("brief", help="Path to planning brief JSON (see assets/sample_plan_input.json)")
    ap.add_argument("--format", choices=["text", "json"], default="text", help="Output format (default: text)")
    ap.add_argument("--min-conversions", type=int, default=50,
                    help="Minimum expected conversions per platform arm for a readable test (default 50)")
    ap.add_argument("--holdout", type=float, default=0.2, help="Holdout share, 0.1-0.5 (default 0.2)")
    args = ap.parse_args()
    try:
        if not 0.05 <= args.holdout <= 0.5:
            raise ValueError("--holdout must be between 0.05 and 0.5")
        brief = json.loads(Path(args.brief).read_text(encoding="utf-8"))
        result = build(brief, args.min_conversions, args.holdout)
    except (OSError, json.JSONDecodeError, ValueError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(result, indent=2) if args.format == "json" else render_text(result))
    sys.exit(2 if result["blockers"] else 0)


if __name__ == "__main__":
    main()
