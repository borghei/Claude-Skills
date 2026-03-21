#!/usr/bin/env python3
"""Regulatory Mapper - Map regulatory requirements by region for international expansion.

Maps data privacy, tax, employment law, and industry-specific regulatory requirements
for target regions. Provides compliance checklist with estimated cost and timeline.

Usage:
    python regulatory_mapper.py --region eu --industry saas --data-processing yes
    python regulatory_mapper.py --region apac --industry healthtech --data-processing yes --json
"""

import argparse
import json
import sys
from datetime import datetime

REGULATIONS = {
    "eu": {
        "region_name": "European Union",
        "data_privacy": {
            "regulation": "GDPR (General Data Protection Regulation)",
            "key_requirements": [
                "Lawful basis for processing (consent, legitimate interest, contract, etc.)",
                "Data Protection Officer (DPO) required if processing at scale",
                "72-hour breach notification to supervisory authority",
                "Data Protection Impact Assessment for high-risk processing",
                "Right to erasure, portability, and access for data subjects",
                "Cross-border transfer rules (SCCs or adequacy decisions)",
                "Data minimization and purpose limitation",
                "Records of processing activities"
            ],
            "penalty": "Up to 4% of annual global revenue or EUR 20M (whichever is greater)",
            "timeline_to_comply": "3-6 months for initial compliance",
            "estimated_cost": "$50K-200K initial; $20K-50K annual maintenance"
        },
        "tax": {
            "requirements": [
                "VAT registration required (threshold varies by country)",
                "OSS (One-Stop Shop) for B2C digital services",
                "Transfer pricing documentation for intercompany transactions",
                "Permanent establishment risk assessment",
                "Country-by-country reporting if revenue > EUR 750M"
            ],
            "vat_rate_range": "17-27% (varies by country)",
            "estimated_cost": "$20K-50K setup; $10K-30K annual compliance"
        },
        "employment": {
            "key_rules": [
                "Strong employee protections (notice periods 1-6 months)",
                "Works council requirements in some countries (Germany, France, Netherlands)",
                "Mandatory benefits (pension, health, vacation minimum 20-25 days)",
                "Anti-discrimination and equal pay regulations",
                "Remote work regulations vary by country",
                "Probation period limitations (typically 3-6 months)"
            ],
            "hiring_options": ["Direct employment (requires entity)", "EOR (Employer of Record)", "Contractor (limited, risk of misclassification)"],
            "estimated_cost": "30-50% on top of salary for mandatory benefits"
        },
        "entity": {
            "common_types": ["GmbH (Germany)", "SAS (France)", "BV (Netherlands)", "Ltd (Ireland)"],
            "timeline": "4-12 weeks depending on country",
            "estimated_cost": "$15K-50K setup; $10K-30K annual maintenance"
        }
    },
    "uk": {
        "region_name": "United Kingdom",
        "data_privacy": {
            "regulation": "UK GDPR + Data Protection Act 2018",
            "key_requirements": [
                "Similar to EU GDPR with UK-specific adaptations",
                "ICO registration required",
                "UK representative required if no UK establishment",
                "International data transfer mechanisms (UK SCCs, adequacy)",
                "Breach notification within 72 hours to ICO"
            ],
            "penalty": "Up to 4% of annual global revenue or GBP 17.5M",
            "timeline_to_comply": "2-4 months (faster if already GDPR compliant)",
            "estimated_cost": "$20K-80K initial; $10K-25K annual"
        },
        "tax": {
            "requirements": [
                "VAT registration (threshold GBP 85K for UK establishments)",
                "Corporation tax on UK-sourced profits",
                "Transfer pricing documentation",
                "Digital Services Tax (2%) on UK-derived revenue > GBP 25M"
            ],
            "vat_rate_range": "20% standard rate",
            "estimated_cost": "$15K-30K setup; $10K-20K annual"
        },
        "employment": {
            "key_rules": [
                "Statutory notice periods (1 week per year of service, up to 12 weeks)",
                "28 days minimum holiday (including bank holidays)",
                "Statutory sick pay requirements",
                "Auto-enrollment pension contribution",
                "National Insurance contributions",
                "IR35 rules for contractor engagement"
            ],
            "hiring_options": ["Direct employment (entity required)", "EOR", "Contractor (IR35 compliance critical)"],
            "estimated_cost": "15-25% on top of salary for mandatory benefits"
        },
        "entity": {
            "common_types": ["Ltd (Private Limited Company)"],
            "timeline": "1-2 weeks (very fast)",
            "estimated_cost": "$5K-15K setup; $5K-15K annual maintenance"
        }
    },
    "apac": {
        "region_name": "Asia-Pacific (General)",
        "data_privacy": {
            "regulation": "Varies: APPI (Japan), PDPA (Singapore), Privacy Act (Australia), PIPA (South Korea), DPDP (India)",
            "key_requirements": [
                "Consent requirements vary significantly by country",
                "Data localization requirements in some jurisdictions (China, India partial)",
                "Cross-border transfer restrictions vary",
                "Breach notification requirements vary (24hrs-72hrs depending on country)",
                "Data Protection Officer requirements vary",
                "Japan: APPI requires purpose specification and consent for third-party sharing",
                "Singapore: PDPA requires consent with business contact exception",
                "Australia: APPs with mandatory breach notification"
            ],
            "penalty": "Varies significantly: Japan (criminal penalties possible), Singapore (up to S$1M), Australia (increasing penalties)",
            "timeline_to_comply": "3-9 months depending on country",
            "estimated_cost": "$30K-150K initial; $15K-50K annual per country"
        },
        "tax": {
            "requirements": [
                "GST/Consumption tax registration varies by country",
                "Withholding tax on cross-border payments common",
                "Transfer pricing documentation required in most jurisdictions",
                "Permanent establishment rules vary significantly",
                "Japan: Consumption tax 10%, complex compliance",
                "Singapore: GST 9%, relatively straightforward",
                "Australia: GST 10%, BAS quarterly reporting"
            ],
            "vat_rate_range": "5-10% (varies by country)",
            "estimated_cost": "$20K-60K setup per country; $15K-40K annual"
        },
        "employment": {
            "key_rules": [
                "Employee protections vary: strong in Japan/Korea, moderate in Singapore/Australia",
                "Notice periods: Japan (30 days), Singapore (1-3 months), Australia (1-5 weeks)",
                "Mandatory benefits vary significantly by country",
                "Japan: lifetime employment culture, termination extremely difficult",
                "Singapore: flexible labor laws, Central Provident Fund contributions",
                "Australia: Fair Work Act, modern awards system, superannuation (11.5%)"
            ],
            "hiring_options": ["Direct employment (entity required)", "EOR (recommended for first hires)", "Contractor (rules vary by country)"],
            "estimated_cost": "15-40% on top of salary depending on country"
        },
        "entity": {
            "common_types": ["KK/GK (Japan)", "Pte Ltd (Singapore)", "Pty Ltd (Australia)"],
            "timeline": "2-16 weeks depending on country (Japan longest)",
            "estimated_cost": "$10K-100K setup; $10K-50K annual depending on country"
        }
    },
    "latam": {
        "region_name": "Latin America",
        "data_privacy": {
            "regulation": "LGPD (Brazil), various others developing",
            "key_requirements": [
                "Brazil LGPD: similar to GDPR, DPO required",
                "Consent as primary legal basis (Brazil)",
                "Data subject rights: access, correction, deletion, portability",
                "Cross-border transfer restrictions",
                "Breach notification to ANPD (Brazil)",
                "Mexico: LFPDPPP for private sector data protection",
                "Argentina: Personal Data Protection Law (EU adequacy)"
            ],
            "penalty": "Brazil: up to 2% of revenue, capped at R$50M per violation",
            "timeline_to_comply": "3-6 months",
            "estimated_cost": "$30K-100K initial; $15K-40K annual"
        },
        "tax": {
            "requirements": [
                "Brazil: extremely complex tax system (Nota Fiscal, ICMS, ISS, PIS/COFINS)",
                "Withholding taxes on cross-border service payments (15-25%)",
                "Transfer pricing rules in most countries",
                "Brazil: requires local tax representative for foreign companies",
                "Mexico: VAT 16%, withholding on digital services",
                "Argentina: complex FX controls and tax regulations"
            ],
            "vat_rate_range": "16-21% (varies by country)",
            "estimated_cost": "$30K-80K setup; $20K-50K annual (Brazil highest)"
        },
        "employment": {
            "key_rules": [
                "Strong employee protections across the region",
                "Brazil: CLT (labor code), 13th salary, FGTS, extensive termination costs",
                "Mexico: profit sharing (10%), severance (3 months + 20 days per year)",
                "Mandatory benefits typically 60-100% on top of salary",
                "Termination extremely costly in Brazil and Mexico"
            ],
            "hiring_options": ["EOR (strongly recommended for first hires)", "Direct employment (entity required)", "Contractor (high misclassification risk)"],
            "estimated_cost": "60-100% on top of salary for mandatory benefits (Brazil/Mexico)"
        },
        "entity": {
            "common_types": ["Ltda (Brazil)", "S de RL de CV (Mexico)", "SAS (Colombia)"],
            "timeline": "8-20 weeks (Brazil and Mexico longest)",
            "estimated_cost": "$20K-80K setup; $15K-40K annual"
        }
    }
}

INDUSTRY_OVERLAYS = {
    "saas": {
        "additional_requirements": [
            "Digital services tax applicability assessment",
            "SaaS-specific data processing agreements",
            "Service availability SLA commitments",
            "Data portability on contract termination"
        ]
    },
    "healthtech": {
        "additional_requirements": [
            "Health data classification and special category data rules",
            "Medical device regulation assessment (EU MDR if applicable)",
            "HIPAA-equivalent local health data regulations",
            "Clinical data storage and processing requirements",
            "Health authority registration if applicable"
        ]
    },
    "fintech": {
        "additional_requirements": [
            "Financial services licensing requirements",
            "Anti-money laundering (AML) and KYC compliance",
            "Payment services regulation (PSD2 in EU)",
            "Capital adequacy requirements if applicable",
            "Regulatory sandbox availability"
        ]
    },
    "edtech": {
        "additional_requirements": [
            "Student data protection (COPPA equivalent)",
            "Educational content localization requirements",
            "Accessibility compliance (WCAG)",
            "Institutional procurement requirements"
        ]
    }
}


def map_regulations(region, industry, data_processing):
    region_key = region.lower()
    if region_key not in REGULATIONS:
        print(f"Error: Unknown region '{region}'. Available: {', '.join(REGULATIONS.keys())}", file=sys.stderr)
        sys.exit(1)

    reg = REGULATIONS[region_key]
    industry_overlay = INDUSTRY_OVERLAYS.get(industry.lower(), {"additional_requirements": []})

    # Build compliance checklist
    checklist = []
    checklist.append({"category": "Data Privacy", "items": reg["data_privacy"]["key_requirements"], "regulation": reg["data_privacy"]["regulation"], "penalty": reg["data_privacy"]["penalty"], "timeline": reg["data_privacy"]["timeline_to_comply"], "cost": reg["data_privacy"]["estimated_cost"]})
    checklist.append({"category": "Tax Compliance", "items": reg["tax"]["requirements"], "cost": reg["tax"]["estimated_cost"]})
    checklist.append({"category": "Employment Law", "items": reg["employment"]["key_rules"], "hiring_options": reg["employment"]["hiring_options"], "cost": reg["employment"]["estimated_cost"]})
    checklist.append({"category": "Entity Formation", "items": [f"Entity types: {', '.join(reg['entity']['common_types'])}", f"Timeline: {reg['entity']['timeline']}"], "cost": reg["entity"]["estimated_cost"]})

    if industry_overlay["additional_requirements"]:
        checklist.append({"category": f"Industry-Specific ({industry.title()})", "items": industry_overlay["additional_requirements"]})

    return {
        "map_date": datetime.now().strftime("%Y-%m-%d"),
        "region": reg["region_name"],
        "region_key": region_key,
        "industry": industry,
        "data_processing": data_processing,
        "regulatory_summary": {
            "data_privacy": reg["data_privacy"]["regulation"],
            "max_penalty": reg["data_privacy"]["penalty"],
            "entity_complexity": reg["entity"]["timeline"],
            "employment_cost_overhead": reg["employment"]["estimated_cost"]
        },
        "compliance_checklist": checklist,
        "risk_assessment": {
            "data_privacy_risk": "HIGH" if data_processing else "MEDIUM",
            "employment_risk": "HIGH" if region_key in ["latam", "eu"] else "MEDIUM",
            "tax_complexity": "VERY HIGH" if region_key == "latam" else "HIGH" if region_key in ["eu", "apac"] else "MEDIUM",
            "entity_timeline": reg["entity"]["timeline"]
        },
        "recommendations": [
            f"Engage local legal counsel in {reg['region_name']} before committing resources",
            f"Budget for {reg['data_privacy']['estimated_cost']} for data privacy compliance",
            f"Consider EOR for first hires to avoid entity setup delay",
            f"Start regulatory assessment at T-90 days before planned launch"
        ]
    }


def print_human(result):
    print(f"\n{'='*70}")
    print(f"REGULATORY MAP: {result['region']}")
    print(f"Industry: {result['industry']}  |  Data Processing: {result['data_processing']}")
    print(f"Date: {result['map_date']}")
    print(f"{'='*70}\n")

    rs = result["regulatory_summary"]
    print(f"SUMMARY:")
    print(f"  Data Privacy: {rs['data_privacy']}")
    print(f"  Max Penalty: {rs['max_penalty']}")
    print(f"  Entity Timeline: {rs['entity_complexity']}")
    print(f"  Employment Overhead: {rs['employment_cost_overhead']}\n")

    for section in result["compliance_checklist"]:
        print(f"\n--- {section['category'].upper()} ---")
        if "regulation" in section:
            print(f"  Regulation: {section['regulation']}")
        if "penalty" in section:
            print(f"  Penalty: {section['penalty']}")
        for item in section["items"]:
            print(f"  [ ] {item}")
        if "cost" in section:
            print(f"  Estimated Cost: {section['cost']}")

    ra = result["risk_assessment"]
    print(f"\nRISK ASSESSMENT:")
    print(f"  Data Privacy: {ra['data_privacy_risk']}")
    print(f"  Employment: {ra['employment_risk']}")
    print(f"  Tax Complexity: {ra['tax_complexity']}")

    print(f"\nRECOMMENDATIONS:")
    for r in result["recommendations"]:
        print(f"  -> {r}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Map regulatory requirements by region")
    parser.add_argument("--region", required=True, choices=list(REGULATIONS.keys()), help="Target region")
    parser.add_argument("--industry", default="saas", choices=list(INDUSTRY_OVERLAYS.keys()) + ["other"], help="Industry")
    parser.add_argument("--data-processing", default="yes", choices=["yes", "no"], help="Does the product process personal data?")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    result = map_regulations(args.region, args.industry, args.data_processing == "yes")

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_human(result)


if __name__ == "__main__":
    main()
