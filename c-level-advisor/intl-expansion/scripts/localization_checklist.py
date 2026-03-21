#!/usr/bin/env python3
"""Localization Checklist - Generate a phased localization checklist for a target market.

Creates a prioritized, phased checklist covering product, GTM, operations, and
compliance localization requirements for a specific target market.

Usage:
    python localization_checklist.py --market "Japan" --product-type saas --current-languages en
    python localization_checklist.py --market "Germany" --product-type saas --current-languages en,de --has-entity --json
"""

import argparse
import json
import sys
from datetime import datetime

MARKET_PROFILES = {
    "germany": {"region": "eu", "language": "German", "currency": "EUR", "data_privacy": "GDPR", "payment_methods": ["SEPA", "Giropay", "Credit Card"], "cultural_notes": "Enterprise-heavy, formal business culture, strong data privacy expectations", "entity_complexity": "medium", "timezone": "CET (UTC+1)"},
    "france": {"region": "eu", "language": "French", "currency": "EUR", "data_privacy": "GDPR", "payment_methods": ["Carte Bancaire", "SEPA", "Credit Card"], "cultural_notes": "Language required in business, strong labor laws, relationship-driven", "entity_complexity": "high", "timezone": "CET (UTC+1)"},
    "uk": {"region": "europe", "language": "English", "currency": "GBP", "data_privacy": "UK GDPR", "payment_methods": ["Direct Debit", "Credit Card"], "cultural_notes": "English-speaking, strong tech ecosystem, post-Brexit regulations", "entity_complexity": "low", "timezone": "GMT (UTC+0)"},
    "japan": {"region": "apac", "language": "Japanese", "currency": "JPY", "data_privacy": "APPI", "payment_methods": ["Konbini", "Bank Transfer", "Credit Card"], "cultural_notes": "Requires local partner, long sales cycles, relationship-heavy, high quality expectations", "entity_complexity": "very_high", "timezone": "JST (UTC+9)"},
    "singapore": {"region": "apac", "language": "English", "currency": "SGD", "data_privacy": "PDPA", "payment_methods": ["PayNow", "Credit Card", "Bank Transfer"], "cultural_notes": "Regional hub, English common, diverse market gateway to SEA", "entity_complexity": "low", "timezone": "SGT (UTC+8)"},
    "australia": {"region": "apac", "language": "English", "currency": "AUD", "data_privacy": "Privacy Act", "payment_methods": ["BPAY", "Direct Debit", "Credit Card"], "cultural_notes": "English-speaking, similar business culture, timezone challenge with US/EU", "entity_complexity": "low", "timezone": "AEST (UTC+10)"},
    "brazil": {"region": "latam", "language": "Portuguese", "currency": "BRL", "data_privacy": "LGPD", "payment_methods": ["Pix", "Boleto", "Credit Card"], "cultural_notes": "Portuguese required, complex tax system (Nota Fiscal), large opportunity", "entity_complexity": "very_high", "timezone": "BRT (UTC-3)"},
    "india": {"region": "apac", "language": "English/Hindi", "currency": "INR", "data_privacy": "DPDP Act", "payment_methods": ["UPI", "Net Banking", "Credit Card"], "cultural_notes": "Price-sensitive, English common in business, massive scale potential", "entity_complexity": "high", "timezone": "IST (UTC+5:30)"},
    "netherlands": {"region": "eu", "language": "Dutch/English", "currency": "EUR", "data_privacy": "GDPR", "payment_methods": ["iDEAL", "SEPA", "Credit Card"], "cultural_notes": "Multilingual, hub for European operations, direct communication style", "entity_complexity": "low", "timezone": "CET (UTC+1)"},
    "south_korea": {"region": "apac", "language": "Korean", "currency": "KRW", "data_privacy": "PIPA", "payment_methods": ["KakaoPay", "Bank Transfer", "Credit Card"], "cultural_notes": "Tech-savvy, relationship-important, hierarchical business culture", "entity_complexity": "high", "timezone": "KST (UTC+9)"},
}

def get_market_profile(market_name):
    key = market_name.lower().replace(" ", "_")
    if key in MARKET_PROFILES:
        return MARKET_PROFILES[key]
    # Default profile for unknown markets
    return {
        "region": "unknown", "language": "Local language", "currency": "Local currency",
        "data_privacy": "Research required", "payment_methods": ["Credit Card", "Local methods TBD"],
        "cultural_notes": "Research local business culture before entry",
        "entity_complexity": "unknown", "timezone": "Research required"
    }


def generate_checklist(market_name, product_type, current_languages, has_entity, arr_from_market):
    profile = get_market_profile(market_name)
    needs_translation = profile["language"].split("/")[0].lower() not in [l.lower() for l in current_languages]

    checklist = {
        "generated_date": datetime.now().strftime("%Y-%m-%d"),
        "market": market_name,
        "market_profile": profile,
        "product_type": product_type,
        "current_languages": current_languages,
        "has_entity": has_entity,
        "translation_needed": needs_translation,
        "phases": []
    }

    # Phase 1: Must Have (Pre-Launch)
    phase1_items = []
    if needs_translation:
        phase1_items.append({"item": f"Translate core product UI to {profile['language']}", "category": "product", "priority": "must-have", "est_cost": "$20-50K", "timeline": "4-8 weeks"})
    phase1_items.append({"item": f"Support {profile['currency']} currency display and charging", "category": "product", "priority": "must-have", "est_cost": "$10-30K", "timeline": "2-4 weeks"})
    phase1_items.append({"item": f"Integrate local payment method: {profile['payment_methods'][0]}", "category": "product", "priority": "must-have", "est_cost": "$5-20K", "timeline": "2-4 weeks"})
    phase1_items.append({"item": "Localize date, time, number, and address formats", "category": "product", "priority": "must-have", "est_cost": "$5-15K", "timeline": "1-2 weeks"})
    phase1_items.append({"item": f"Ensure {profile['data_privacy']} compliance for data handling", "category": "compliance", "priority": "must-have", "est_cost": "$10-50K", "timeline": "4-8 weeks"})
    phase1_items.append({"item": "Review and adapt contracts for local legal requirements", "category": "legal", "priority": "must-have", "est_cost": "$10-30K", "timeline": "3-6 weeks"})
    phase1_items.append({"item": f"Adapt value proposition for {market_name} market pain points", "category": "gtm", "priority": "must-have", "est_cost": "$5-15K", "timeline": "2-4 weeks"})
    phase1_items.append({"item": f"Research and document local ICP definition for {market_name}", "category": "gtm", "priority": "must-have", "est_cost": "$5-10K", "timeline": "2-3 weeks"})
    phase1_items.append({"item": f"Set market-specific pricing based on local willingness to pay", "category": "gtm", "priority": "must-have", "est_cost": "Internal effort", "timeline": "2-3 weeks"})

    if not has_entity and arr_from_market >= 500000:
        phase1_items.append({"item": f"Establish legal entity in {market_name}", "category": "legal", "priority": "must-have", "est_cost": "$50-200K", "timeline": "8-16 weeks"})
    elif not has_entity and arr_from_market >= 200000:
        phase1_items.append({"item": f"Hire first local person via EOR (Employer of Record)", "category": "people", "priority": "must-have", "est_cost": "$100-300K/year", "timeline": "4-8 weeks"})

    checklist["phases"].append({"phase": 1, "name": "Must Have (Pre-Launch)", "items": phase1_items})

    # Phase 2: Nice to Have (Post-Launch, Revenue-Gated)
    phase2_items = []
    if needs_translation:
        phase2_items.append({"item": f"Translate marketing website to {profile['language']}", "category": "gtm", "priority": "nice-to-have", "est_cost": "$10-25K", "timeline": "3-6 weeks"})
    phase2_items.append({"item": f"Integrate additional payment methods: {', '.join(profile['payment_methods'][1:])}", "category": "product", "priority": "nice-to-have", "est_cost": "$5-20K per method", "timeline": "2-4 weeks each"})
    phase2_items.append({"item": "Create local customer case studies and references", "category": "gtm", "priority": "nice-to-have", "est_cost": "$5-10K", "timeline": "4-8 weeks"})
    phase2_items.append({"item": f"Build local SEO content in {profile['language']}", "category": "gtm", "priority": "nice-to-have", "est_cost": "$10-20K", "timeline": "Ongoing"})
    phase2_items.append({"item": "Establish local partner/integration ecosystem", "category": "gtm", "priority": "nice-to-have", "est_cost": "Partnership effort", "timeline": "3-6 months"})
    phase2_items.append({"item": f"Set up customer support coverage for {profile['timezone']}", "category": "operations", "priority": "nice-to-have", "est_cost": "$50-100K/year", "timeline": "4-8 weeks"})

    checklist["phases"].append({"phase": 2, "name": "Nice to Have (Revenue-Gated)", "items": phase2_items})

    # Phase 3: Scale (After proven market)
    phase3_items = []
    if profile.get("entity_complexity") in ["high", "very_high"] and not has_entity:
        phase3_items.append({"item": f"Establish full legal entity with local banking", "category": "legal", "priority": "scale", "est_cost": "$100K-500K", "timeline": "8-20 weeks"})
    phase3_items.append({"item": "Hire regional leadership (Country Manager or Regional VP)", "category": "people", "priority": "scale", "est_cost": "$150-250K/year", "timeline": "8-12 weeks"})
    phase3_items.append({"item": "Build local team (3-8 people across sales, CS, marketing)", "category": "people", "priority": "scale", "est_cost": "$500K-1.5M/year", "timeline": "3-6 months"})
    phase3_items.append({"item": "Develop market-specific product features based on local feedback", "category": "product", "priority": "scale", "est_cost": "Engineering allocation", "timeline": "Ongoing"})
    phase3_items.append({"item": "Attend regional conferences and events", "category": "gtm", "priority": "scale", "est_cost": "$20-50K/year", "timeline": "Ongoing"})

    checklist["phases"].append({"phase": 3, "name": "Scale (After Market Validation)", "items": phase3_items})

    # Calculate totals
    total_must_have = len(phase1_items)
    total_items = sum(len(p["items"]) for p in checklist["phases"])

    checklist["summary"] = {
        "total_items": total_items,
        "must_have_items": total_must_have,
        "translation_needed": needs_translation,
        "entity_needed": not has_entity and arr_from_market >= 500000,
        "cultural_notes": profile["cultural_notes"]
    }

    return checklist


def print_human(result):
    print(f"\n{'='*70}")
    print(f"LOCALIZATION CHECKLIST: {result['market']}")
    print(f"Generated: {result['generated_date']}")
    print(f"{'='*70}\n")

    p = result["market_profile"]
    print(f"MARKET PROFILE:")
    print(f"  Language: {p['language']}  |  Currency: {p['currency']}  |  Timezone: {p['timezone']}")
    print(f"  Data Privacy: {p['data_privacy']}  |  Entity Complexity: {p['entity_complexity']}")
    print(f"  Cultural Notes: {p['cultural_notes']}\n")

    for phase in result["phases"]:
        print(f"\n--- PHASE {phase['phase']}: {phase['name']} ---")
        for item in phase["items"]:
            print(f"  [ ] [{item['category']:<10s}] {item['item']}")
            print(f"       Cost: {item['est_cost']}  |  Timeline: {item['timeline']}")

    s = result["summary"]
    print(f"\nSUMMARY: {s['total_items']} total items, {s['must_have_items']} must-have")
    print(f"  Translation needed: {'Yes' if s['translation_needed'] else 'No'}")
    print(f"  Entity needed: {'Yes' if s['entity_needed'] else 'No'}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Generate phased localization checklist")
    parser.add_argument("--market", required=True, help="Target market name")
    parser.add_argument("--product-type", default="saas", choices=["saas", "marketplace", "hardware", "services"])
    parser.add_argument("--current-languages", default="en", help="Comma-separated current supported languages")
    parser.add_argument("--has-entity", action="store_true", help="Already have legal entity in market")
    parser.add_argument("--arr-from-market", type=float, default=0, help="Current ARR from this market")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    languages = [l.strip() for l in args.current_languages.split(",")]
    result = generate_checklist(args.market, args.product_type, languages, args.has_entity, args.arr_from_market)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_human(result)


if __name__ == "__main__":
    main()
