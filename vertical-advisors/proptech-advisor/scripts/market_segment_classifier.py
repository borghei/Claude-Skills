#!/usr/bin/env python3
"""
Proptech Market Segment Classifier — classify a proptech business description
into one or more segments and surface regulatory considerations.

Usage:
    python market_segment_classifier.py description.txt
    python market_segment_classifier.py description.txt --json
"""

import argparse
import json
import re
import sys
from pathlib import Path


SEGMENTS = [
    {
        "name": "Transaction",
        "patterns": [
            r"\b(iBuyer|instant buy|cash offer|cash buyer|sell my home|home buying|home buyer)\b",
            r"\b(brokerage|broker|listing agent|buyer's agent|buying agent|selling agent)\b",
            r"\b(transaction coordinator|escrow|closing|closing process)\b",
            r"\b(marketplace for (?:homes|properties|real estate))\b",
        ],
        "regulatory": "Real estate brokerage license required (state-by-state). Antitrust scrutiny on commission structures. RESPA on settlement-service kickbacks. Fair housing compliance.",
        "business_model": "Commission-based, take-rate, or markup on iBuyer transactions. Capital-intensive at iBuyer scale.",
    },
    {
        "name": "Listings & Search",
        "patterns": [
            r"\b(MLS|listing|listings|home search|property search|find a home)\b",
            r"\b(valuation|AVM|automated valuation|comparable|comp|comps|home value)\b",
            r"\b(Zillow|Redfin|Trulia|Realtor\.com)\b",
        ],
        "regulatory": "MLS access requires broker membership or syndication agreement (IDX/VOW/RESO Web API). State display rules. Fair housing on ranking and recommendations.",
        "business_model": "Lead-gen to agents (per-lead or referral fees), advertising, premium listings, brokerage adjacent.",
    },
    {
        "name": "Financing",
        "patterns": [
            r"\b(mortgage|mortgage tech|home loan|home financing|origination|originator)\b",
            r"\b(refinanc(?:e|ing)|HELOC|home equity)\b",
            r"\b(rent[- ]to[- ]own|alternative financing|fractional ownership|home equity (?:investment|sharing))\b",
            r"\b(down payment assistance|DPA)\b",
        ],
        "regulatory": "Mortgage origination requires NMLS license + state lender licenses. CFPB oversight. RESPA for settlement services. State-by-state lending rules. Fair lending (ECOA / HMDA).",
        "business_model": "Origination fees, broker fees, interest rate spread, or fee-for-service.",
    },
    {
        "name": "Property Management",
        "patterns": [
            r"\b(property management|property manager|landlord|rental property)\b",
            r"\b(multifamily|apartment|tenant|lease|leasing)\b",
            r"\b(short[- ]term rental|STR|vacation rental|Airbnb host)\b",
            r"\b(operating expense|opex|maintenance|work order)\b",
        ],
        "regulatory": "Property management licenses (varies by state — some require, some don't). Fair housing in screening. State landlord-tenant laws on screening, deposits, evictions. Local STR regulations.",
        "business_model": "% of rent collected, SaaS per-unit/month, transaction fees on services.",
    },
    {
        "name": "Services (Insurance, Title, Escrow, Inspection)",
        "patterns": [
            r"\b(title insurance|title|escrow|escrow services)\b",
            r"\b(home inspection|inspection|inspector)\b",
            r"\b(home insurance|homeowners insurance|landlord insurance)\b",
            r"\b(home warranty|home warranties)\b",
            r"\b(moving services|movers)\b",
        ],
        "regulatory": "Title and escrow are licensed services in most states. Insurance requires producer/agency licenses (state-by-state). RESPA Section 8 prohibits kickbacks for referrals to settlement services.",
        "business_model": "Fee per transaction, commission on insurance premiums, referral fees (subject to RESPA).",
    },
    {
        "name": "Data & Infrastructure (B2B SaaS)",
        "patterns": [
            r"\b(CRM for (?:agents|brokers|real estate))\b",
            r"\b(MLS data|property data|real estate data)\b",
            r"\b(SaaS for (?:brokerages|agents|landlords|property managers))\b",
            r"\b(API|developer|integration)\b",
        ],
        "regulatory": "Lower direct regulatory exposure, but customers (brokerages, lenders) face their own; product must support their compliance. Fair lending / fair housing implications if your data feeds decision-making.",
        "business_model": "SaaS subscription, per-seat, per-user, per-transaction.",
    },
    {
        "name": "Commercial Real Estate (CRE)",
        "patterns": [
            r"\b(commercial real estate|CRE|office space|industrial real estate|warehouse|logistics real estate)\b",
            r"\b(REIT|real estate investment trust|institutional investor)\b",
            r"\b(net lease|triple net|NNN|cap rate|capitalization rate)\b",
        ],
        "regulatory": "Different from residential — sophisticated parties, fewer consumer-protection rules, but securities (REITs, syndications) apply.",
        "business_model": "Subscription, transaction, advisory fees, asset management fees.",
    },
]


def classify(text):
    text_lower = text.lower()
    matched = []
    for segment in SEGMENTS:
        terms = []
        for pattern in segment["patterns"]:
            for m in re.finditer(pattern, text_lower, re.IGNORECASE):
                terms.append(m.group(0))
        if terms:
            matched.append({
                "segment": segment["name"],
                "matched_terms": list(set(terms))[:5],
                "regulatory_considerations": segment["regulatory"],
                "business_model_pattern": segment["business_model"],
            })
    return matched


def render_human(segments):
    lines = []
    lines.append("Proptech Market Segment Classification")
    lines.append("=" * 60)
    if not segments:
        lines.append("No clear proptech segment detected from the description.")
        return "\n".join(lines)
    lines.append(f"Detected {len(segments)} segment(s):")
    lines.append("")
    for i, s in enumerate(segments, 1):
        lines.append(f"{i}. {s['segment']}")
        lines.append(f"   Matched terms: {', '.join(s['matched_terms'])}")
        lines.append(f"   Regulatory: {s['regulatory_considerations']}")
        lines.append(f"   Business model pattern: {s['business_model_pattern']}")
        lines.append("")
    if len(segments) > 1:
        lines.append("Note: matching multiple segments is common but doing all at once almost always under-performs picking one.")
    lines.append("=" * 60)
    lines.append("REMINDER: Keyword scan, not legal advice. Real estate is regulated state-by-state.")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Classify a proptech business description.")
    parser.add_argument("description", help="Path to a text file describing the product")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    path = Path(args.description)
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        return 1

    text = path.read_text(encoding="utf-8")
    segments = classify(text)

    if args.json:
        print(json.dumps({
            "description_excerpt": text[:200].strip(),
            "segments": segments,
            "disclaimer": "Keyword scan only. Not legal advice.",
        }, indent=2))
    else:
        print(render_human(segments))
    return 0


if __name__ == "__main__":
    sys.exit(main())
