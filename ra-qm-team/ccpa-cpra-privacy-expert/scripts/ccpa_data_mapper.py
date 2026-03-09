#!/usr/bin/env python3
"""
CCPA Data Mapper

Maps personal information categories, identifies sensitive personal information,
tracks data flows (collection, use, sharing, selling), and generates data
inventory reports for CCPA/CPRA compliance.

Usage:
    python ccpa_data_mapper.py --template > inventory.json
    python ccpa_data_mapper.py --input inventory.json
    python ccpa_data_mapper.py --input inventory.json --output report.json
    python ccpa_data_mapper.py --input inventory.json --flow-diagram
"""

import argparse
import json
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional


PI_CATEGORIES = {
    "identifiers": {
        "section": "§1798.140(v)(1)(A)",
        "description": "Identifiers such as real name, alias, postal address, unique personal "
                       "identifier, online identifier, IP address, email address, account name, "
                       "SSN, driver's license number, passport number, or other similar identifiers.",
        "examples": ["name", "email", "IP address", "SSN", "driver's license", "passport",
                      "account name", "online identifier", "postal address"],
        "sensitive_subtypes": ["ssn", "driver_license", "passport", "state_id"]
    },
    "customer_records": {
        "section": "§1798.140(v)(1)(B)",
        "description": "Personal information described in Cal. Civ. Code §1798.80(e): name, "
                       "signature, SSN, physical characteristics, address, telephone, passport, "
                       "driver's license, state ID, insurance policy, education, employment, "
                       "employment history, bank account, credit/debit card, financial information, "
                       "medical information, health insurance information.",
        "examples": ["bank account", "credit card", "medical info", "insurance", "employment history",
                      "education", "telephone", "signature"],
        "sensitive_subtypes": ["bank_account", "credit_card", "medical_info"]
    },
    "protected_classifications": {
        "section": "§1798.140(v)(1)(C)",
        "description": "Characteristics of protected classifications under California or federal law: "
                       "race, color, religion, sex/gender, gender identity/expression, sexual orientation, "
                       "marital status, medical condition, military/veteran status, national origin, "
                       "ancestry, disability, genetic information, citizenship, age.",
        "examples": ["race", "sex", "age", "disability", "gender identity", "marital status",
                      "national origin", "religion", "veteran status"],
        "sensitive_subtypes": ["race_ethnicity", "religion", "sexual_orientation"]
    },
    "commercial_information": {
        "section": "§1798.140(v)(1)(D)",
        "description": "Records of personal property, products or services purchased, obtained, "
                       "or considered, or other purchasing or consuming histories or tendencies.",
        "examples": ["purchase history", "product preferences", "shopping cart", "wishlists",
                      "consumption tendencies"],
        "sensitive_subtypes": []
    },
    "biometric_information": {
        "section": "§1798.140(v)(1)(E)",
        "description": "Physiological, biological, or behavioral characteristics that can be used "
                       "to establish individual identity: fingerprints, face, voice, iris, retina, "
                       "keystroke, gait, or other physical patterns, sleep, health, or exercise data.",
        "examples": ["fingerprint", "facial geometry", "voiceprint", "iris scan", "retina scan",
                      "keystroke patterns", "gait", "sleep data"],
        "sensitive_subtypes": ["fingerprint", "facial_geometry", "voiceprint", "iris_scan"]
    },
    "internet_activity": {
        "section": "§1798.140(v)(1)(F)",
        "description": "Internet or other electronic network activity: browsing history, search "
                       "history, information regarding a consumer's interaction with a website, "
                       "application, or advertisement.",
        "examples": ["browsing history", "search history", "page views", "clicks",
                      "app usage", "ad interactions"],
        "sensitive_subtypes": []
    },
    "geolocation_data": {
        "section": "§1798.140(v)(1)(G)",
        "description": "Geolocation data.",
        "examples": ["GPS coordinates", "cell tower location", "WiFi location",
                      "IP-based location"],
        "sensitive_subtypes": ["precise_geolocation"]
    },
    "sensory_data": {
        "section": "§1798.140(v)(1)(H)",
        "description": "Audio, electronic, visual, thermal, olfactory, or similar information.",
        "examples": ["voice recordings", "photos", "video", "thermal imaging",
                      "CCTV footage"],
        "sensitive_subtypes": []
    },
    "professional_info": {
        "section": "§1798.140(v)(1)(I)",
        "description": "Professional or employment-related information.",
        "examples": ["job title", "employer", "work history", "performance reviews",
                      "professional licenses"],
        "sensitive_subtypes": []
    },
    "education_info": {
        "section": "§1798.140(v)(1)(J)",
        "description": "Education information that is not publicly available personally "
                       "identifiable information as defined in FERPA (20 U.S.C. §1232g).",
        "examples": ["grades", "transcripts", "student records", "disciplinary records",
                      "financial aid"],
        "sensitive_subtypes": []
    },
    "inferences": {
        "section": "§1798.140(v)(1)(K)",
        "description": "Inferences drawn from any PI to create a profile reflecting preferences, "
                       "characteristics, psychological trends, predispositions, behavior, "
                       "attitudes, intelligence, abilities, and aptitudes.",
        "examples": ["consumer profiles", "preference predictions", "behavior models",
                      "risk scores", "propensity scores"],
        "sensitive_subtypes": []
    }
}


SPI_CATEGORIES = {
    "ssn_gov_id": {
        "section": "§1798.140(ae)(1)",
        "description": "Social Security, driver's license, state ID, or passport number",
        "risk_level": "critical"
    },
    "login_credentials": {
        "section": "§1798.140(ae)(2)",
        "description": "Account log-in, financial account, debit card, or credit card number "
                       "in combination with any required security or access code, password, "
                       "or credentials allowing access to an account",
        "risk_level": "critical"
    },
    "financial_accounts": {
        "section": "§1798.140(ae)(3)",
        "description": "Financial account information with access credentials",
        "risk_level": "critical"
    },
    "precise_geolocation": {
        "section": "§1798.140(ae)(4)",
        "description": "Precise geolocation (within a radius of 1,850 feet)",
        "risk_level": "high"
    },
    "racial_ethnic_origin": {
        "section": "§1798.140(ae)(5)",
        "description": "Racial or ethnic origin",
        "risk_level": "high"
    },
    "religious_beliefs": {
        "section": "§1798.140(ae)(5)",
        "description": "Religious or philosophical beliefs",
        "risk_level": "high"
    },
    "union_membership": {
        "section": "§1798.140(ae)(5)",
        "description": "Union membership",
        "risk_level": "high"
    },
    "genetic_data": {
        "section": "§1798.140(ae)(6)",
        "description": "Genetic data",
        "risk_level": "high"
    },
    "mail_email_text_content": {
        "section": "§1798.140(ae)(7)",
        "description": "Contents of a consumer's mail, email, and text messages "
                       "(unless the business is the intended recipient)",
        "risk_level": "high"
    },
    "biometric_data": {
        "section": "§1798.140(ae)(8)",
        "description": "Processing of biometric information for the purpose of uniquely "
                       "identifying a consumer",
        "risk_level": "high"
    },
    "health_data": {
        "section": "§1798.140(ae)(9)",
        "description": "Health information",
        "risk_level": "high"
    },
    "sex_life_orientation": {
        "section": "§1798.140(ae)(10)",
        "description": "Information concerning a consumer's sex life or sexual orientation",
        "risk_level": "high"
    }
}


TEMPLATE = {
    "organization": {
        "name": "",
        "assessment_date": ""
    },
    "data_systems": [
        {
            "system_name": "",
            "system_type": "",
            "description": "",
            "pi_categories": [],
            "spi_categories": [],
            "collection_sources": [],
            "business_purposes": [],
            "commercial_purposes": [],
            "shared_with": [],
            "sold_to": [],
            "service_providers": [],
            "contractors": [],
            "third_parties": [],
            "retention_period": "",
            "cross_border_transfer": False,
            "transfer_destinations": [],
            "encryption_at_rest": False,
            "encryption_in_transit": False,
            "access_controls": False,
            "consumer_count_estimate": 0
        }
    ]
}


def validate_inventory(data: Dict) -> List[str]:
    """Validate the data inventory structure and content."""
    warnings = []
    systems = data.get("data_systems", [])

    if not systems:
        warnings.append("No data systems defined in inventory")
        return warnings

    for i, system in enumerate(systems):
        name = system.get("system_name", f"System {i+1}")

        if not system.get("system_name"):
            warnings.append(f"System {i+1}: Missing system name")

        if not system.get("pi_categories"):
            warnings.append(f"{name}: No PI categories specified")

        if not system.get("collection_sources"):
            warnings.append(f"{name}: No collection sources specified")

        if not system.get("business_purposes"):
            warnings.append(f"{name}: No business purposes specified")

        if not system.get("retention_period"):
            warnings.append(f"{name}: No retention period specified (required under CPRA §1798.100(a)(3))")

        # Validate PI category names
        for cat in system.get("pi_categories", []):
            if cat not in PI_CATEGORIES:
                warnings.append(
                    f"{name}: Unknown PI category '{cat}'. "
                    f"Valid categories: {', '.join(PI_CATEGORIES.keys())}"
                )

        # Validate SPI category names
        for spi in system.get("spi_categories", []):
            if spi not in SPI_CATEGORIES:
                warnings.append(
                    f"{name}: Unknown SPI category '{spi}'. "
                    f"Valid categories: {', '.join(SPI_CATEGORIES.keys())}"
                )

        # Check security controls for SPI
        if system.get("spi_categories") and not system.get("encryption_at_rest"):
            warnings.append(f"{name}: Contains SPI but encryption at rest not enabled")

        if system.get("spi_categories") and not system.get("access_controls"):
            warnings.append(f"{name}: Contains SPI but access controls not implemented")

        # Check cross-border transfers
        if system.get("cross_border_transfer") and not system.get("transfer_destinations"):
            warnings.append(f"{name}: Cross-border transfer enabled but no destinations specified")

    return warnings


def map_pi_categories(data: Dict) -> Dict:
    """Map all PI categories across data systems."""
    category_map = {}

    for cat_id, cat_info in PI_CATEGORIES.items():
        category_map[cat_id] = {
            "category": cat_id,
            "section": cat_info["section"],
            "description": cat_info["description"],
            "systems": [],
            "collection_sources": set(),
            "business_purposes": set(),
            "shared_with": set(),
            "sold_to": set(),
            "service_providers": set(),
            "total_consumers": 0,
            "is_sensitive": bool(cat_info.get("sensitive_subtypes"))
        }

    for system in data.get("data_systems", []):
        name = system.get("system_name", "Unknown")
        for cat in system.get("pi_categories", []):
            if cat in category_map:
                entry = category_map[cat]
                entry["systems"].append(name)
                entry["collection_sources"].update(system.get("collection_sources", []))
                entry["business_purposes"].update(system.get("business_purposes", []))
                entry["shared_with"].update(system.get("shared_with", []))
                entry["sold_to"].update(system.get("sold_to", []))
                entry["service_providers"].update(system.get("service_providers", []))
                entry["total_consumers"] += system.get("consumer_count_estimate", 0)

    # Convert sets to sorted lists for JSON serialization
    for cat_id in category_map:
        for field in ["collection_sources", "business_purposes", "shared_with",
                       "sold_to", "service_providers"]:
            category_map[cat_id][field] = sorted(category_map[cat_id][field])

    return category_map


def map_spi_categories(data: Dict) -> Dict:
    """Map sensitive personal information across data systems."""
    spi_map = {}

    for spi_id, spi_info in SPI_CATEGORIES.items():
        spi_map[spi_id] = {
            "category": spi_id,
            "section": spi_info["section"],
            "description": spi_info["description"],
            "risk_level": spi_info["risk_level"],
            "systems": [],
            "has_encryption": True,
            "has_access_controls": True,
            "total_consumers": 0
        }

    for system in data.get("data_systems", []):
        name = system.get("system_name", "Unknown")
        for spi in system.get("spi_categories", []):
            if spi in spi_map:
                entry = spi_map[spi]
                entry["systems"].append(name)
                entry["total_consumers"] += system.get("consumer_count_estimate", 0)
                if not system.get("encryption_at_rest"):
                    entry["has_encryption"] = False
                if not system.get("access_controls"):
                    entry["has_access_controls"] = False

    return spi_map


def map_data_flows(data: Dict) -> Dict:
    """Map data flows across the organization."""
    flows = {
        "collection": [],
        "internal_use": [],
        "sharing": [],
        "selling": [],
        "service_provider_processing": [],
        "cross_border": []
    }

    for system in data.get("data_systems", []):
        name = system.get("system_name", "Unknown")
        pi_cats = system.get("pi_categories", [])

        # Collection flows
        for source in system.get("collection_sources", []):
            flows["collection"].append({
                "source": source,
                "destination": name,
                "pi_categories": pi_cats,
                "purposes": system.get("business_purposes", [])
            })

        # Internal use flows
        for purpose in system.get("business_purposes", []):
            flows["internal_use"].append({
                "system": name,
                "purpose": purpose,
                "pi_categories": pi_cats
            })

        # Sharing flows
        for recipient in system.get("shared_with", []):
            flows["sharing"].append({
                "source": name,
                "recipient": recipient,
                "pi_categories": pi_cats,
                "type": "sharing"
            })

        # Selling flows
        for buyer in system.get("sold_to", []):
            flows["selling"].append({
                "source": name,
                "recipient": buyer,
                "pi_categories": pi_cats,
                "type": "selling"
            })

        # Service provider flows
        for sp in system.get("service_providers", []):
            flows["service_provider_processing"].append({
                "source": name,
                "service_provider": sp,
                "pi_categories": pi_cats
            })

        # Cross-border flows
        if system.get("cross_border_transfer"):
            flows["cross_border"].append({
                "source": name,
                "destinations": system.get("transfer_destinations", []),
                "pi_categories": pi_cats
            })

    return flows


def map_recipients(data: Dict) -> Dict:
    """Map all data recipients (service providers, contractors, third parties)."""
    recipients = {
        "service_providers": {},
        "contractors": {},
        "third_parties": {}
    }

    for system in data.get("data_systems", []):
        name = system.get("system_name", "Unknown")

        for sp in system.get("service_providers", []):
            if sp not in recipients["service_providers"]:
                recipients["service_providers"][sp] = {
                    "systems": [], "pi_categories": set()
                }
            recipients["service_providers"][sp]["systems"].append(name)
            recipients["service_providers"][sp]["pi_categories"].update(
                system.get("pi_categories", [])
            )

        for contractor in system.get("contractors", []):
            if contractor not in recipients["contractors"]:
                recipients["contractors"][contractor] = {
                    "systems": [], "pi_categories": set()
                }
            recipients["contractors"][contractor]["systems"].append(name)
            recipients["contractors"][contractor]["pi_categories"].update(
                system.get("pi_categories", [])
            )

        for tp in system.get("third_parties", []):
            if tp not in recipients["third_parties"]:
                recipients["third_parties"][tp] = {
                    "systems": [], "pi_categories": set()
                }
            recipients["third_parties"][tp]["systems"].append(name)
            recipients["third_parties"][tp]["pi_categories"].update(
                system.get("pi_categories", [])
            )

    # Convert sets to sorted lists
    for rtype in recipients:
        for name in recipients[rtype]:
            recipients[rtype][name]["pi_categories"] = sorted(
                recipients[rtype][name]["pi_categories"]
            )

    return recipients


def generate_flow_diagram(data: Dict) -> str:
    """Generate a text-based data flow diagram."""
    flows = map_data_flows(data)
    lines = []

    lines.append("=" * 60)
    lines.append("DATA FLOW DIAGRAM")
    lines.append("=" * 60)
    lines.append("")

    # Collection
    lines.append("COLLECTION SOURCES")
    lines.append("-" * 40)
    seen_sources = set()
    for flow in flows["collection"]:
        key = f"{flow['source']} -> {flow['destination']}"
        if key not in seen_sources:
            seen_sources.add(key)
            cats = ", ".join(flow["pi_categories"][:3])
            if len(flow["pi_categories"]) > 3:
                cats += f" (+{len(flow['pi_categories']) - 3} more)"
            lines.append(f"  [{flow['source']}] --> [{flow['destination']}]")
            lines.append(f"    PI: {cats}")
    lines.append("")

    # Internal use
    lines.append("INTERNAL PROCESSING")
    lines.append("-" * 40)
    seen_purposes = set()
    for flow in flows["internal_use"]:
        key = f"{flow['system']}:{flow['purpose']}"
        if key not in seen_purposes:
            seen_purposes.add(key)
            lines.append(f"  [{flow['system']}] -- {flow['purpose']}")
    lines.append("")

    # Sharing
    if flows["sharing"]:
        lines.append("SHARING (requires opt-out)")
        lines.append("-" * 40)
        for flow in flows["sharing"]:
            lines.append(f"  [{flow['source']}] ==> [{flow['recipient']}]")
        lines.append("")

    # Selling
    if flows["selling"]:
        lines.append("SELLING (requires opt-out)")
        lines.append("-" * 40)
        for flow in flows["selling"]:
            lines.append(f"  [{flow['source']}] ==$==> [{flow['recipient']}]")
        lines.append("")

    # Service providers
    if flows["service_provider_processing"]:
        lines.append("SERVICE PROVIDER PROCESSING")
        lines.append("-" * 40)
        for flow in flows["service_provider_processing"]:
            lines.append(f"  [{flow['source']}] --SP--> [{flow['service_provider']}]")
        lines.append("")

    # Cross-border
    if flows["cross_border"]:
        lines.append("CROSS-BORDER TRANSFERS")
        lines.append("-" * 40)
        for flow in flows["cross_border"]:
            dests = ", ".join(flow["destinations"])
            lines.append(f"  [{flow['source']}] --XBORDER--> [{dests}]")
        lines.append("")

    lines.append("=" * 60)
    lines.append("LEGEND")
    lines.append("  -->     Data collection")
    lines.append("  ==>     Data sharing")
    lines.append("  ==$==>  Data selling")
    lines.append("  --SP--> Service provider")
    lines.append("  --XBORDER--> Cross-border transfer")
    lines.append("=" * 60)

    return "\n".join(lines)


def generate_report(data: Dict) -> Dict:
    """Generate comprehensive data mapping report."""
    warnings = validate_inventory(data)
    pi_map = map_pi_categories(data)
    spi_map = map_spi_categories(data)
    flows = map_data_flows(data)
    recipients = map_recipients(data)

    # Summary statistics
    active_pi = [cat for cat, info in pi_map.items() if info["systems"]]
    active_spi = [cat for cat, info in spi_map.items() if info["systems"]]
    total_systems = len(data.get("data_systems", []))

    spi_risks = []
    for spi_id, spi_info in spi_map.items():
        if spi_info["systems"]:
            if not spi_info["has_encryption"]:
                spi_risks.append(f"{spi_id}: Missing encryption in {', '.join(spi_info['systems'])}")
            if not spi_info["has_access_controls"]:
                spi_risks.append(f"{spi_id}: Missing access controls in {', '.join(spi_info['systems'])}")

    report = {
        "report_date": datetime.now().isoformat(),
        "organization": data.get("organization", {}).get("name", "Unknown"),
        "summary": {
            "total_data_systems": total_systems,
            "pi_categories_in_use": len(active_pi),
            "pi_categories_list": active_pi,
            "spi_categories_in_use": len(active_spi),
            "spi_categories_list": active_spi,
            "total_service_providers": len(recipients["service_providers"]),
            "total_contractors": len(recipients["contractors"]),
            "total_third_parties": len(recipients["third_parties"]),
            "has_data_selling": len(flows["selling"]) > 0,
            "has_data_sharing": len(flows["sharing"]) > 0,
            "has_cross_border_transfers": len(flows["cross_border"]) > 0,
            "spi_security_risks": spi_risks
        },
        "pi_category_mapping": {
            cat: {
                "section": info["section"],
                "systems": info["systems"],
                "collection_sources": info["collection_sources"],
                "business_purposes": info["business_purposes"],
                "shared_with": info["shared_with"],
                "sold_to": info["sold_to"],
                "service_providers": info["service_providers"],
                "total_consumers": info["total_consumers"]
            }
            for cat, info in pi_map.items() if info["systems"]
        },
        "spi_mapping": {
            cat: {
                "section": info["section"],
                "description": info["description"],
                "risk_level": info["risk_level"],
                "systems": info["systems"],
                "has_encryption": info["has_encryption"],
                "has_access_controls": info["has_access_controls"],
                "total_consumers": info["total_consumers"]
            }
            for cat, info in spi_map.items() if info["systems"]
        },
        "data_flows": {
            "collection_count": len(flows["collection"]),
            "sharing_count": len(flows["sharing"]),
            "selling_count": len(flows["selling"]),
            "service_provider_count": len(flows["service_provider_processing"]),
            "cross_border_count": len(flows["cross_border"]),
            "flows": flows
        },
        "recipients": recipients,
        "validation_warnings": warnings,
        "privacy_policy_disclosures_needed": {
            "pi_categories_collected": active_pi,
            "spi_categories_collected": active_spi,
            "pi_categories_sold_or_shared": list(set(
                cat for flow in flows["selling"] + flows["sharing"]
                for cat in flow.get("pi_categories", [])
            )),
            "third_party_categories": list(recipients["third_parties"].keys()),
            "service_provider_list": list(recipients["service_providers"].keys()),
            "cross_border_destinations": list(set(
                dest for flow in flows["cross_border"]
                for dest in flow.get("destinations", [])
            ))
        }
    }

    return report


def format_text_report(report: Dict) -> str:
    """Format the report as human-readable text."""
    lines = []
    summary = report["summary"]

    lines.append("=" * 60)
    lines.append("CCPA/CPRA DATA MAPPING REPORT")
    lines.append("=" * 60)
    lines.append(f"Organization: {report['organization']}")
    lines.append(f"Report Date: {report['report_date']}")
    lines.append("")

    lines.append("-" * 60)
    lines.append("SUMMARY")
    lines.append("-" * 60)
    lines.append(f"  Data Systems: {summary['total_data_systems']}")
    lines.append(f"  PI Categories in Use: {summary['pi_categories_in_use']}/11")
    lines.append(f"  SPI Categories in Use: {summary['spi_categories_in_use']}/12")
    lines.append(f"  Service Providers: {summary['total_service_providers']}")
    lines.append(f"  Contractors: {summary['total_contractors']}")
    lines.append(f"  Third Parties: {summary['total_third_parties']}")
    lines.append(f"  Data Selling: {'Yes' if summary['has_data_selling'] else 'No'}")
    lines.append(f"  Data Sharing: {'Yes' if summary['has_data_sharing'] else 'No'}")
    lines.append(f"  Cross-Border Transfers: {'Yes' if summary['has_cross_border_transfers'] else 'No'}")
    lines.append("")

    # PI Categories
    pi_mapping = report.get("pi_category_mapping", {})
    if pi_mapping:
        lines.append("-" * 60)
        lines.append("PERSONAL INFORMATION CATEGORIES")
        lines.append("-" * 60)
        for cat, info in pi_mapping.items():
            lines.append(f"  {cat} ({info['section']})")
            lines.append(f"    Systems: {', '.join(info['systems'])}")
            if info['collection_sources']:
                lines.append(f"    Sources: {', '.join(info['collection_sources'])}")
            if info['shared_with']:
                lines.append(f"    Shared with: {', '.join(info['shared_with'])}")
            if info['sold_to']:
                lines.append(f"    Sold to: {', '.join(info['sold_to'])}")
            lines.append("")

    # SPI
    spi_mapping = report.get("spi_mapping", {})
    if spi_mapping:
        lines.append("-" * 60)
        lines.append("SENSITIVE PERSONAL INFORMATION")
        lines.append("-" * 60)
        for cat, info in spi_mapping.items():
            risk_icon = "[!]" if info["risk_level"] == "critical" else "[*]"
            lines.append(f"  {risk_icon} {cat} ({info['section']})")
            lines.append(f"    Risk Level: {info['risk_level']}")
            lines.append(f"    Systems: {', '.join(info['systems'])}")
            lines.append(f"    Encrypted: {'Yes' if info['has_encryption'] else 'NO'}")
            lines.append(f"    Access Controls: {'Yes' if info['has_access_controls'] else 'NO'}")
            lines.append("")

    # SPI Risks
    if summary.get("spi_security_risks"):
        lines.append("-" * 60)
        lines.append("SPI SECURITY RISKS")
        lines.append("-" * 60)
        for risk in summary["spi_security_risks"]:
            lines.append(f"  [RISK] {risk}")
        lines.append("")

    # Privacy policy disclosures
    disclosures = report.get("privacy_policy_disclosures_needed", {})
    lines.append("-" * 60)
    lines.append("PRIVACY POLICY DISCLOSURE REQUIREMENTS")
    lines.append("-" * 60)
    lines.append(f"  PI Categories to Disclose: {', '.join(disclosures.get('pi_categories_collected', []))}")
    lines.append(f"  SPI Categories to Disclose: {', '.join(disclosures.get('spi_categories_collected', []))}")
    lines.append(f"  Categories Sold/Shared: {', '.join(disclosures.get('pi_categories_sold_or_shared', [])) or 'None'}")
    lines.append(f"  Third Parties: {', '.join(disclosures.get('third_party_categories', [])) or 'None'}")
    lines.append("")

    # Warnings
    warnings = report.get("validation_warnings", [])
    if warnings:
        lines.append("-" * 60)
        lines.append("VALIDATION WARNINGS")
        lines.append("-" * 60)
        for w in warnings:
            lines.append(f"  [WARN] {w}")
        lines.append("")

    lines.append("=" * 60)
    lines.append("End of Report")
    lines.append("=" * 60)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="CCPA Data Mapper — maps personal information categories, "
                    "identifies SPI, and tracks data flows for CCPA/CPRA compliance."
    )
    parser.add_argument(
        "--input", "-i",
        help="Path to JSON data inventory file"
    )
    parser.add_argument(
        "--template", "-t",
        action="store_true",
        help="Output a blank data inventory template (JSON)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Path to write the mapping report"
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output results as JSON (default is human-readable text)"
    )
    parser.add_argument(
        "--flow-diagram",
        action="store_true",
        help="Generate text-based data flow diagram"
    )
    args = parser.parse_args()

    if args.template:
        print(json.dumps(TEMPLATE, indent=2))
        return

    if not args.input:
        parser.error("--input is required (or use --template to generate a blank inventory)")

    try:
        with open(args.input, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {args.input}: {e}", file=sys.stderr)
        sys.exit(1)

    if args.flow_diagram:
        output = generate_flow_diagram(data)
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
            print(f"Flow diagram written to {args.output}")
        else:
            print(output)
        return

    report = generate_report(data)

    if args.json:
        output = json.dumps(report, indent=2)
    else:
        output = format_text_report(report)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Report written to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
