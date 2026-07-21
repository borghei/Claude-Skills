#!/usr/bin/env python3
"""
Carbon Impact Estimator — classify a climate-tech business description into
climate categories and provide order-of-magnitude impact ranges and verification
considerations.

Usage:
    python carbon_impact_estimator.py description.txt
    python carbon_impact_estimator.py description.txt --json

This is a CATEGORIZATION tool, not a verified carbon-accounting calculator.
Real GHG accounting requires methodology selection, data collection, and
(for credit issuance) third-party verification.
"""

import argparse
import json
import re
import sys
from pathlib import Path


CATEGORIES = [
    {
        "name": "Energy generation",
        "patterns": [
            r"\b(solar|wind|geothermal|hydroelectric|hydropower|nuclear|fission|fusion)\b",
            r"\b(renewable energy|clean energy|grid scale|utility scale)\b",
            r"\b(power plant|generation|electricity (?:generation|production))\b",
        ],
        "scope_typically_affected": "Scope 2 (purchased electricity) for end users; Scope 1 for grid operators; large absolute Mt CO2e potential",
        "verification": "Verra VCS, Gold Standard, ACR, CAR for credits. IRA Section 45 / 48 tax credits in US. CSRD eligibility.",
        "magnitude_intuition": "Utility-scale projects: 100k-10M+ tons CO2e/year displaceable. Distributed: smaller per-asset, larger in aggregate.",
    },
    {
        "name": "Energy storage",
        "patterns": [
            r"\b(battery|batteries|storage|grid storage|energy storage|long[- ]duration|LDES)\b",
            r"\b(hydrogen|electrolyzer|electrolysis)\b",
            r"\b(thermal storage|pumped hydro)\b",
        ],
        "scope_typically_affected": "Indirect — enables higher renewable penetration; impact via avoided fossil generation",
        "verification": "Difficult to credit directly (additionality challenges); usually monetized via grid services + IRA credits.",
        "magnitude_intuition": "GWh-scale storage projects shift millions of tons CO2e/year by enabling renewables.",
    },
    {
        "name": "Transport (vehicles, fuels, mobility)",
        "patterns": [
            r"\b(electric vehicle|EV|EVs|battery electric|fuel cell vehicle)\b",
            r"\b(SAF|sustainable aviation fuel|hydrogen aviation|biofuel|biodiesel|renewable diesel|e[- ]fuel)\b",
            r"\b(charging infrastructure|EV charging|charging network)\b",
            r"\b(electric fleet|fleet electrification|electric truck)\b",
        ],
        "scope_typically_affected": "Scope 1 for fleet operators (direct fuel emissions); Scope 3 for OEMs and supply chain",
        "verification": "EU/UK/CA fuel programs (LCFS), CORSIA for aviation, IRA credits, carbon credits via 'fuel switching' methodologies",
        "magnitude_intuition": "Transport is ~25% of US emissions. Even niche transport solutions can target Mt-CO2e categories.",
    },
    {
        "name": "Industry (cement, steel, chemicals, manufacturing)",
        "patterns": [
            r"\b(cement|concrete|steel|iron|aluminum|chemicals|fertilizer|ammonia|glass)\b",
            r"\b(industrial decarbonization|hard[- ]to[- ]abate|process emissions|heat decarbonization)\b",
            r"\b(green steel|green hydrogen|CCUS|carbon capture|industrial heat)\b",
        ],
        "scope_typically_affected": "Scope 1 for the producer (process and combustion emissions); Scope 3 for downstream users",
        "verification": "Industry-specific protocols (ISO standards), product environmental declarations (EPDs), tax credits (45Q for sequestration in US)",
        "magnitude_intuition": "Industry is ~30% of global emissions. Single facility decarbonization can shift Mt-scale CO2e.",
    },
    {
        "name": "Buildings (efficiency, HVAC, materials)",
        "patterns": [
            r"\b(building efficiency|building decarbonization|heat pump|HVAC|insulation)\b",
            r"\b(green building|net zero building|passive house|LEED)\b",
            r"\b(retrofit|electrification of buildings)\b",
        ],
        "scope_typically_affected": "Scope 1 for buildings burning fossil fuels (gas heating); Scope 2 for electricity",
        "verification": "Building certifications (LEED, Passive House), utility programs, IRA Section 25C / 25D for residential efficiency",
        "magnitude_intuition": "Buildings are ~30% of US emissions. Per-building impact small; aggregated, very large.",
    },
    {
        "name": "Food and agriculture",
        "patterns": [
            r"\b(alternative protein|alt protein|plant[- ]based|cultivated meat|cellular agriculture|fermentation)\b",
            r"\b(regenerative agriculture|cover crop|no[- ]till|soil carbon)\b",
            r"\b(precision (?:agriculture|farming)|methane reduction|enteric fermentation)\b",
            r"\b(food waste|food loss|supply chain emissions)\b",
        ],
        "scope_typically_affected": "Scope 1 (livestock methane, fertilizer), Scope 3 (food supply chain emissions)",
        "verification": "Soil carbon protocols (Verra, CAR, others), enteric fermentation methodologies, dietary-shift modeling",
        "magnitude_intuition": "Food systems ~30% of global emissions. Verification of soil-sequestration is contested.",
    },
    {
        "name": "Carbon removal (CDR)",
        "patterns": [
            r"\b(carbon removal|CDR|direct air capture|DAC|negative emissions|engineered removal)\b",
            r"\b(biochar|enhanced weathering|ERW|ocean alkalinity|mineralization)\b",
            r"\b(reforestation|afforestation|forest carbon|nature[- ]based)\b",
        ],
        "scope_typically_affected": "Generates removal credits (durability matters: nature-based often <100yr; engineered 1000+yr)",
        "verification": "Specialized registries (Puro.earth, Isometric, CarbonPlan rated). 45Q tax credit in US for engineered removal. Durability and additionality contested for nature-based.",
        "magnitude_intuition": "Per-project: 1k-100k+ tons CO2/year. Industry needs to scale to gigaton/year by 2050 per IPCC.",
    },
    {
        "name": "Software / data / measurement (climate-tech B2B SaaS)",
        "patterns": [
            r"\b(carbon accounting|GHG accounting|emissions tracking|sustainability software)\b",
            r"\b(MRV|measurement reporting verification|ESG reporting|CSRD reporting)\b",
            r"\b(climate data|emissions data|supply chain emissions|scope 3)\b",
            r"\b(net zero (?:roadmap|planning|software))\b",
        ],
        "scope_typically_affected": "Indirect — enables others to measure and reduce their emissions",
        "verification": "Aligns to GHG Protocol, ISO 14064, sector-specific frameworks. Customer-side reporting drives requirements.",
        "magnitude_intuition": "Direct impact small; leverage via large customers' reduction targets.",
    },
]


def classify(text):
    text_lower = text.lower()
    matched = []
    for category in CATEGORIES:
        terms = []
        for pattern in category["patterns"]:
            for m in re.finditer(pattern, text_lower, re.IGNORECASE):
                terms.append(m.group(0))
        if terms:
            matched.append({
                "category": category["name"],
                "matched_terms": list(set(terms))[:5],
                "scope_affected": category["scope_typically_affected"],
                "verification_landscape": category["verification"],
                "magnitude_intuition": category["magnitude_intuition"],
            })
    return matched


def render_human(categories):
    lines = []
    lines.append("Climate-Tech Category Classification")
    lines.append("=" * 60)
    if not categories:
        lines.append("No clear climate-tech category detected from the description.")
        lines.append("Re-describe with explicit category language and re-run.")
        return "\n".join(lines)
    lines.append(f"Detected {len(categories)} category(ies):")
    lines.append("")
    for i, c in enumerate(categories, 1):
        lines.append(f"{i}. {c['category']}")
        lines.append(f"   Matched terms: {', '.join(c['matched_terms'])}")
        lines.append(f"   Scope affected: {c['scope_affected']}")
        lines.append(f"   Verification: {c['verification_landscape']}")
        lines.append(f"   Magnitude intuition: {c['magnitude_intuition']}")
        lines.append("")
    lines.append("=" * 60)
    lines.append("REMINDER: Categorization tool, not a carbon-accounting calculator.")
    lines.append("Real GHG accounting requires qualified methodology and verification.")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Classify a climate-tech business description.")
    parser.add_argument("description", help="Path to a text file describing the business")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    path = Path(args.description)
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        return 1

    text = path.read_text(encoding="utf-8")
    cats = classify(text)

    if args.json:
        print(json.dumps({
            "description_excerpt": text[:200].strip(),
            "categories": cats,
            "disclaimer": "Categorization only. Not verified GHG accounting.",
        }, indent=2))
    else:
        print(render_human(cats))
    return 0


if __name__ == "__main__":
    sys.exit(main())
