#!/usr/bin/env python3
"""
PCI DSS v4.0 Scope Analyzer

Determines SAQ type based on business model, maps CDE boundaries,
identifies connected and security-impacting systems, and generates
a comprehensive scoping worksheet.

Usage:
    python pci_scope_analyzer.py --input business_model.json --output scope_report.json
    python pci_scope_analyzer.py --input business_model.json --format markdown --output scope.md
"""

import argparse
import json
import sys
from datetime import datetime
from typing import Any

# ---------------------------------------------------------------------------
# SAQ Type Definitions
# ---------------------------------------------------------------------------

SAQ_TYPES: dict[str, dict[str, Any]] = {
    "SAQ_A": {
        "name": "SAQ A",
        "title": "Card-not-present — Fully Outsourced",
        "description": (
            "E-commerce or mail/telephone-order merchants that have fully outsourced "
            "all cardholder data functions to PCI DSS validated third parties. "
            "No electronic storage, processing, or transmission of CHD on merchant systems."
        ),
        "eligible": (
            "E-commerce merchants using fully hosted payment page (iFrame/redirect) "
            "with no scripts affecting payment transactions. "
            "MOTO merchants with no electronic CHD storage."
        ),
        "question_count": "~30 questions",
        "scope_impact": "Minimal — only policies and third-party management",
    },
    "SAQ_A-EP": {
        "name": "SAQ A-EP",
        "title": "E-commerce — Partial Outsource",
        "description": (
            "E-commerce merchants that partially outsource payment processing but whose "
            "website impacts the security of the payment transaction. "
            "Payment page served by third party but merchant has scripts or APIs that could affect payment data."
        ),
        "eligible": (
            "E-commerce merchants with payment page elements from third party, "
            "but merchant website could impact payment transaction security "
            "(e.g., JavaScript on payment page, API calls to processor)."
        ),
        "question_count": "~140 questions",
        "scope_impact": "Moderate — web servers, APIs, and supporting infrastructure",
    },
    "SAQ_B": {
        "name": "SAQ B",
        "title": "Standalone Terminals — Dial-Out",
        "description": (
            "Merchants using standalone, dial-out terminals (no IP connectivity). "
            "Imprint machines or standalone dial-out terminals. No electronic CHD storage."
        ),
        "eligible": (
            "Merchants with only imprint machines or standalone terminals "
            "that connect via phone line (not IP). No electronic CHD storage."
        ),
        "question_count": "~40 questions",
        "scope_impact": "Minimal — physical terminal security only",
    },
    "SAQ_B-IP": {
        "name": "SAQ B-IP",
        "title": "Standalone Terminals — IP Connected",
        "description": (
            "Merchants using standalone, IP-connected payment terminals. "
            "Terminals are PTS-approved and connected to processor via IP. No electronic CHD storage."
        ),
        "eligible": (
            "Merchants with standalone PTS-approved terminals connected via IP. "
            "No electronic CHD storage. Terminals are the only devices in CDE."
        ),
        "question_count": "~80 questions",
        "scope_impact": "Moderate — terminal network and supporting infrastructure",
    },
    "SAQ_C": {
        "name": "SAQ C",
        "title": "Payment Application Systems",
        "description": (
            "Merchants with payment application systems connected to the Internet. "
            "No electronic CHD storage."
        ),
        "eligible": (
            "Merchants with payment application (e.g., POS system) connected to Internet. "
            "No electronic CHD storage. Payment application is the only system in CDE."
        ),
        "question_count": "~160 questions",
        "scope_impact": "Significant — payment application and supporting infrastructure",
    },
    "SAQ_C-VT": {
        "name": "SAQ C-VT",
        "title": "Virtual Terminal — Web-Based",
        "description": (
            "Merchants manually entering CHD via a virtual terminal provided by the payment processor. "
            "No electronic CHD storage."
        ),
        "eligible": (
            "Merchants that manually enter card data one transaction at a time "
            "via a processor-provided web-based virtual terminal. "
            "No electronic CHD storage."
        ),
        "question_count": "~80 questions",
        "scope_impact": "Moderate — workstations accessing virtual terminal",
    },
    "SAQ_D_MERCHANT": {
        "name": "SAQ D (Merchant)",
        "title": "All Other Merchants",
        "description": (
            "All merchants that do not qualify for any other SAQ type. "
            "Includes merchants that store CHD electronically."
        ),
        "eligible": "Any merchant not qualifying for SAQ A, A-EP, B, B-IP, C, C-VT, or P2PE.",
        "question_count": "~330 questions",
        "scope_impact": "Full — all systems storing, processing, transmitting CHD and connected systems",
    },
    "SAQ_D_SP": {
        "name": "SAQ D (Service Provider)",
        "title": "Service Providers",
        "description": "Service providers eligible to complete an SAQ.",
        "eligible": "Service providers that handle fewer than 300,000 transactions annually.",
        "question_count": "~330 questions",
        "scope_impact": "Full — all systems and additional service provider requirements",
    },
    "SAQ_P2PE": {
        "name": "SAQ P2PE",
        "title": "Hardware Terminals with Validated P2PE",
        "description": (
            "Merchants using validated Point-to-Point Encryption solutions. "
            "No electronic CHD storage. PCI-listed P2PE solution."
        ),
        "eligible": (
            "Merchants using PCI SSC-validated P2PE hardware terminals. "
            "No electronic CHD storage. P2PE solution manages all decryption."
        ),
        "question_count": "~30 questions",
        "scope_impact": "Minimal — terminal physical security and P2PE management only",
    },
}

# ---------------------------------------------------------------------------
# Merchant Level Definitions
# ---------------------------------------------------------------------------

MERCHANT_LEVELS = {
    1: {
        "name": "Level 1",
        "criteria": "Over 6 million annual Visa/Mastercard transactions",
        "assessment": "Annual ROC by QSA + quarterly ASV scans",
        "threshold": 6_000_000,
    },
    2: {
        "name": "Level 2",
        "criteria": "1 million to 6 million annual transactions",
        "assessment": "Annual SAQ + quarterly ASV scans",
        "threshold": 1_000_000,
    },
    3: {
        "name": "Level 3",
        "criteria": "20,000 to 1 million annual e-commerce transactions",
        "assessment": "Annual SAQ + quarterly ASV scans",
        "threshold": 20_000,
    },
    4: {
        "name": "Level 4",
        "criteria": "Under 20,000 e-commerce or up to 1 million other transactions",
        "assessment": "Annual SAQ recommended + quarterly ASV scan recommended",
        "threshold": 0,
    },
}


def load_input(path: str) -> dict:
    """Load business model from JSON file."""
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)


def determine_merchant_level(annual_transactions: int, is_ecommerce: bool) -> dict:
    """Determine merchant level based on transaction volume."""
    if annual_transactions > 6_000_000:
        return {**MERCHANT_LEVELS[1], "level": 1}
    elif annual_transactions > 1_000_000:
        return {**MERCHANT_LEVELS[2], "level": 2}
    elif is_ecommerce and annual_transactions > 20_000:
        return {**MERCHANT_LEVELS[3], "level": 3}
    else:
        return {**MERCHANT_LEVELS[4], "level": 4}


def determine_saq_type(data: dict) -> dict:
    """Determine the appropriate SAQ type based on business model."""
    business_type = data.get("business_type", "").lower()
    stores_pan = data.get("stores_pan", False)
    processes_pan = data.get("processes_pan", False)
    transmits_pan = data.get("transmits_pan", False)
    card_present = data.get("card_present", False)
    card_not_present = data.get("card_not_present", False)
    uses_iframe_redirect = data.get("uses_iframe_redirect", False)
    uses_p2pe = data.get("uses_p2pe", False)
    payment_channels = data.get("payment_channels", [])

    reasons: list[str] = []

    # Service provider check
    if business_type == "service_provider":
        return {
            "saq_type": "SAQ_D_SP",
            **SAQ_TYPES["SAQ_D_SP"],
            "determination_reasons": ["Organization is a service provider"],
        }

    # If stores CHD electronically → SAQ D
    if stores_pan:
        reasons.append("Organization stores PAN electronically")
        return {
            "saq_type": "SAQ_D_MERCHANT",
            **SAQ_TYPES["SAQ_D_MERCHANT"],
            "determination_reasons": reasons,
        }

    # P2PE
    if uses_p2pe and card_present and not card_not_present:
        reasons.append("Uses validated P2PE solution")
        reasons.append("Card-present transactions only")
        reasons.append("No electronic CHD storage")
        return {
            "saq_type": "SAQ_P2PE",
            **SAQ_TYPES["SAQ_P2PE"],
            "determination_reasons": reasons,
        }

    # E-commerce only
    is_ecommerce = "web" in payment_channels or "e-commerce" in business_type or "ecommerce" in business_type
    is_moto = "moto" in business_type or "mail" in payment_channels or "telephone" in payment_channels

    if (is_ecommerce or is_moto) and not card_present:
        if uses_iframe_redirect and not processes_pan and not transmits_pan:
            reasons.append("E-commerce/MOTO with fully outsourced payment processing")
            reasons.append("Uses iFrame or redirect to processor-hosted payment page")
            reasons.append("No processing or transmission of CHD")
            return {
                "saq_type": "SAQ_A",
                **SAQ_TYPES["SAQ_A"],
                "determination_reasons": reasons,
            }
        elif is_ecommerce:
            reasons.append("E-commerce merchant with website impacting payment security")
            reasons.append("Payment elements from third party but merchant site affects transaction")
            return {
                "saq_type": "SAQ_A-EP",
                **SAQ_TYPES["SAQ_A-EP"],
                "determination_reasons": reasons,
            }

    # Virtual terminal
    if "virtual_terminal" in payment_channels:
        reasons.append("Uses web-based virtual terminal from payment processor")
        reasons.append("Manual card entry, one transaction at a time")
        return {
            "saq_type": "SAQ_C-VT",
            **SAQ_TYPES["SAQ_C-VT"],
            "determination_reasons": reasons,
        }

    # Card-present (POS)
    if card_present:
        pos_channels = [c for c in payment_channels if c in ("pos", "terminal", "in_store")]
        if pos_channels:
            # Check terminal type
            terminal_type = data.get("terminal_type", "ip")
            if terminal_type == "dial_out":
                reasons.append("Standalone dial-out terminal (phone line)")
                return {
                    "saq_type": "SAQ_B",
                    **SAQ_TYPES["SAQ_B"],
                    "determination_reasons": reasons,
                }
            elif terminal_type == "ip_standalone":
                reasons.append("Standalone IP-connected PTS-approved terminal")
                return {
                    "saq_type": "SAQ_B-IP",
                    **SAQ_TYPES["SAQ_B-IP"],
                    "determination_reasons": reasons,
                }
            else:
                reasons.append("Payment application system connected to Internet")
                return {
                    "saq_type": "SAQ_C",
                    **SAQ_TYPES["SAQ_C"],
                    "determination_reasons": reasons,
                }

    # Default: SAQ D
    reasons.append("Does not qualify for a specific SAQ type")
    return {
        "saq_type": "SAQ_D_MERCHANT",
        **SAQ_TYPES["SAQ_D_MERCHANT"],
        "determination_reasons": reasons,
    }


def classify_systems(systems: list[dict]) -> dict:
    """Classify systems into CDE, connected-to, security-impacting, and out-of-scope."""
    classified = {
        "cde_systems": [],
        "connected_to_systems": [],
        "security_impacting_systems": [],
        "out_of_scope_systems": [],
    }

    for system in systems:
        handles_chd = system.get("handles_cardholder_data", False)
        connected = system.get("connected_to_cde", False)
        security_impact = system.get("security_impacting", False)

        entry = {
            "name": system.get("name", "Unknown"),
            "type": system.get("type", "Unknown"),
            "description": system.get("description", ""),
        }

        if handles_chd:
            entry["classification"] = "CDE"
            entry["scope_rationale"] = "Stores, processes, or transmits cardholder data"
            classified["cde_systems"].append(entry)
        elif connected:
            entry["classification"] = "Connected-to"
            entry["scope_rationale"] = "Direct connectivity to CDE systems"
            classified["connected_to_systems"].append(entry)
        elif security_impact:
            entry["classification"] = "Security-Impacting"
            entry["scope_rationale"] = "Provides security services to CDE"
            classified["security_impacting_systems"].append(entry)
        else:
            entry["classification"] = "Out of Scope"
            entry["scope_rationale"] = "No connectivity to CDE, no CHD handling, no security impact"
            classified["out_of_scope_systems"].append(entry)

    return classified


def generate_scope_reduction_recommendations(data: dict) -> list[dict]:
    """Generate recommendations for reducing PCI DSS scope."""
    recommendations: list[dict] = []

    if data.get("stores_pan"):
        recommendations.append({
            "strategy": "Tokenization",
            "description": "Replace stored PANs with non-reversible tokens to remove systems from CDE scope",
            "impact": "HIGH — can eliminate PAN storage entirely",
            "effort": "Medium — requires payment processor tokenization service",
        })

    if data.get("card_present") and not data.get("uses_p2pe"):
        recommendations.append({
            "strategy": "P2PE (Point-to-Point Encryption)",
            "description": "Deploy PCI SSC-validated P2PE terminals to encrypt CHD at the point of interaction",
            "impact": "HIGH — significantly reduces CDE scope, may qualify for SAQ P2PE",
            "effort": "Medium — requires validated P2PE solution from PCI SSC list",
        })

    payment_channels = data.get("payment_channels", [])
    if "web" in payment_channels and not data.get("uses_iframe_redirect"):
        recommendations.append({
            "strategy": "iFrame/Redirect",
            "description": "Use payment processor's hosted payment page (iFrame or redirect) instead of handling CHD on your servers",
            "impact": "HIGH — may qualify for SAQ A instead of SAQ A-EP or D",
            "effort": "Low-Medium — requires integration with processor's hosted solution",
        })

    if not data.get("network_segmentation_implemented", True):
        recommendations.append({
            "strategy": "Network Segmentation",
            "description": "Isolate CDE on a dedicated network segment with strict firewall rules",
            "impact": "MEDIUM — reduces number of in-scope systems",
            "effort": "Medium — requires network architecture changes",
        })

    recommendations.append({
        "strategy": "Outsource to PCI-Compliant Processor",
        "description": "Shift CHD handling to a PCI DSS compliant third-party processor",
        "impact": "HIGH — reduces scope proportional to outsourced functions",
        "effort": "Medium-High — may require payment architecture redesign",
    })

    return recommendations


def analyze_scope(data: dict) -> dict:
    """Perform full scope analysis."""
    annual_tx = data.get("annual_transactions", 0)
    is_ecommerce = "web" in data.get("payment_channels", [])

    merchant_level = determine_merchant_level(annual_tx, is_ecommerce)
    saq_type = determine_saq_type(data)
    systems = classify_systems(data.get("systems", []))
    scope_reductions = generate_scope_reduction_recommendations(data)

    in_scope_count = (
        len(systems["cde_systems"])
        + len(systems["connected_to_systems"])
        + len(systems["security_impacting_systems"])
    )

    return {
        "metadata": {
            "organization": data.get("organization", "Unknown"),
            "analysis_date": datetime.now().strftime("%Y-%m-%d"),
            "business_type": data.get("business_type", "Unknown"),
            "payment_channels": data.get("payment_channels", []),
            "payment_processor": data.get("payment_processor", "Unknown"),
            "annual_transactions": annual_tx,
            "card_brands": data.get("card_brands", []),
        },
        "merchant_level": merchant_level,
        "saq_determination": saq_type,
        "system_classification": systems,
        "scope_summary": {
            "total_systems_analyzed": len(data.get("systems", [])),
            "cde_systems": len(systems["cde_systems"]),
            "connected_to_systems": len(systems["connected_to_systems"]),
            "security_impacting_systems": len(systems["security_impacting_systems"]),
            "out_of_scope_systems": len(systems["out_of_scope_systems"]),
            "total_in_scope": in_scope_count,
        },
        "data_handling": {
            "stores_pan": data.get("stores_pan", False),
            "processes_pan": data.get("processes_pan", False),
            "transmits_pan": data.get("transmits_pan", False),
            "uses_tokenization": data.get("tokenization_implemented", False),
            "uses_p2pe": data.get("uses_p2pe", False),
            "uses_iframe_redirect": data.get("uses_iframe_redirect", False),
        },
        "scope_reduction_recommendations": scope_reductions,
    }


def format_markdown(result: dict) -> str:
    """Format scope analysis as Markdown."""
    lines: list[str] = []
    meta = result["metadata"]
    ml = result["merchant_level"]
    saq = result["saq_determination"]
    scope = result["scope_summary"]
    dh = result["data_handling"]

    lines.append("# PCI DSS v4.0 Scope Analysis Report")
    lines.append("")
    lines.append(f"**Organization:** {meta['organization']}")
    lines.append(f"**Business Type:** {meta['business_type']}")
    lines.append(f"**Payment Channels:** {', '.join(meta['payment_channels'])}")
    lines.append(f"**Payment Processor:** {meta['payment_processor']}")
    lines.append(f"**Annual Transactions:** {meta['annual_transactions']:,}")
    lines.append(f"**Card Brands:** {', '.join(meta['card_brands'])}")
    lines.append(f"**Analysis Date:** {meta['analysis_date']}")
    lines.append("")

    # Merchant Level
    lines.append("## Merchant Level")
    lines.append("")
    lines.append(f"**Level:** {ml['name']}")
    lines.append(f"**Criteria:** {ml['criteria']}")
    lines.append(f"**Required Assessment:** {ml['assessment']}")
    lines.append("")

    # SAQ Determination
    lines.append("## SAQ Type Determination")
    lines.append("")
    lines.append(f"**Recommended SAQ:** {saq['name']}")
    lines.append(f"**Title:** {saq['title']}")
    lines.append(f"**Questions:** {saq['question_count']}")
    lines.append(f"**Scope Impact:** {saq['scope_impact']}")
    lines.append("")
    lines.append(f"**Description:** {saq['description']}")
    lines.append("")
    lines.append("**Determination Reasons:**")
    for reason in saq["determination_reasons"]:
        lines.append(f"- {reason}")
    lines.append("")

    # Data Handling
    lines.append("## Cardholder Data Handling")
    lines.append("")
    lines.append("| Activity | Status |")
    lines.append("|----------|--------|")
    lines.append(f"| Stores PAN | {'Yes' if dh['stores_pan'] else 'No'} |")
    lines.append(f"| Processes PAN | {'Yes' if dh['processes_pan'] else 'No'} |")
    lines.append(f"| Transmits PAN | {'Yes' if dh['transmits_pan'] else 'No'} |")
    lines.append(f"| Tokenization | {'Yes' if dh['uses_tokenization'] else 'No'} |")
    lines.append(f"| P2PE | {'Yes' if dh['uses_p2pe'] else 'No'} |")
    lines.append(f"| iFrame/Redirect | {'Yes' if dh['uses_iframe_redirect'] else 'No'} |")
    lines.append("")

    # System Classification
    lines.append("## System Classification")
    lines.append("")
    lines.append(f"**Total Systems Analyzed:** {scope['total_systems_analyzed']}")
    lines.append(f"**Total In Scope:** {scope['total_in_scope']}")
    lines.append(f"**Out of Scope:** {scope['out_of_scope_systems']}")
    lines.append("")

    sc = result["system_classification"]
    for category, label in [
        ("cde_systems", "CDE Systems (Store/Process/Transmit CHD)"),
        ("connected_to_systems", "Connected-to Systems"),
        ("security_impacting_systems", "Security-Impacting Systems"),
        ("out_of_scope_systems", "Out-of-Scope Systems"),
    ]:
        systems = sc[category]
        if systems:
            lines.append(f"### {label}")
            lines.append("")
            lines.append("| System | Type | Rationale |")
            lines.append("|--------|------|-----------|")
            for s in systems:
                lines.append(f"| {s['name']} | {s['type']} | {s['scope_rationale']} |")
            lines.append("")

    # Scope Reduction
    if result["scope_reduction_recommendations"]:
        lines.append("## Scope Reduction Recommendations")
        lines.append("")
        for rec in result["scope_reduction_recommendations"]:
            lines.append(f"### {rec['strategy']}")
            lines.append("")
            lines.append(f"**Description:** {rec['description']}")
            lines.append(f"**Impact:** {rec['impact']}")
            lines.append(f"**Effort:** {rec['effort']}")
            lines.append("")

    return "\n".join(lines)


def write_output(result: dict, output_path: str | None, fmt: str) -> None:
    """Write results to file or stdout."""
    if fmt == "markdown":
        content = format_markdown(result)
    else:
        content = json.dumps(result, indent=2)

    if output_path:
        with open(output_path, "w") as f:
            f.write(content)
        print(f"Scope analysis written to {output_path}", file=sys.stderr)
    else:
        print(content)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="PCI DSS v4.0 Scope Analyzer — determine SAQ type and map CDE boundaries"
    )
    parser.add_argument(
        "--input", "-i", required=True,
        help="Path to business model JSON file"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path (stdout if not specified)"
    )
    parser.add_argument(
        "--format", "-f", choices=["json", "markdown"], default="json",
        help="Output format (default: json)"
    )

    args = parser.parse_args()
    data = load_input(args.input)
    result = analyze_scope(data)
    write_output(result, args.output, args.format)


if __name__ == "__main__":
    main()
