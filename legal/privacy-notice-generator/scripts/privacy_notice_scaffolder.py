#!/usr/bin/env python3
"""
Privacy Notice Scaffolder

Generates a privacy notice skeleton based on notice type, jurisdiction, and
processing parameters. Outputs structured markdown with all required sections
pre-populated with jurisdiction-specific placeholders and legal references.

Usage:
    python privacy_notice_scaffolder.py --notice-type website --jurisdiction DE --data-categories personal,contact,usage --legal-bases consent,contract
    python privacy_notice_scaffolder.py --notice-type employee --jurisdiction FR --data-categories personal,employment --legal-bases contract,legal_obligation --has-ai
    python privacy_notice_scaffolder.py --notice-type b2c --jurisdiction UK --data-categories personal,financial --legal-bases consent,contract --has-cookies --json
"""

import argparse
import json
import sys
from datetime import datetime
from typing import Dict, List, Optional

NOTICE_TYPES = ["website", "applicant", "employee", "b2b", "b2c", "combined"]

JURISDICTIONS: Dict[str, Dict] = {
    "DE": {
        "name": "Germany",
        "regulation": "DSGVO (GDPR) + BDSG + TDDDG",
        "sa_name": "Relevant Landesbeauftragte or BfDI",
        "sa_url": "https://www.bfdi.bund.de",
        "language": "German",
        "notes": [
            "Art. 21 DSGVO right to object must be prominently displayed (separate from other rights)",
            "TDDDG (formerly TTDSG) applies to telecom and telemedia services",
            "§26 BDSG governs employee data processing (employment context)",
            "DSK (Datenschutzkonferenz) guidance should be followed for cookie consent",
        ],
        "dpo_note": "DPO mandatory if 20+ employees regularly engaged in automated processing (§38 BDSG)",
    },
    "FR": {
        "name": "France",
        "regulation": "RGPD (GDPR) + Loi Informatique et Libertés (LIL) + LCEN",
        "sa_name": "CNIL (Commission Nationale de l'Informatique et des Libertés)",
        "sa_url": "https://www.cnil.fr",
        "language": "French",
        "notes": [
            "CNIL recommends specific cookie consent wording and mechanism",
            "LIL contains supplementary provisions for research and health data",
            "LCEN imposes hosting provider identification requirements",
            "French language version required for FR-targeted services",
        ],
        "dpo_note": "DPO appointment follows GDPR Art. 37 criteria",
    },
    "AT": {
        "name": "Austria",
        "regulation": "DSGVO (GDPR) + DSG (Datenschutzgesetz)",
        "sa_name": "DSB (Datenschutzbehörde)",
        "sa_url": "https://www.dsb.gv.at",
        "language": "German",
        "notes": [
            "DSG supplements GDPR with Austrian-specific provisions",
            "Employee data subject to works council involvement (ArbVG)",
            "DSB has specific guidance on video surveillance",
        ],
        "dpo_note": "DPO appointment follows GDPR Art. 37 criteria",
    },
    "IT": {
        "name": "Italy",
        "regulation": "GDPR + Codice Privacy (D.Lgs. 196/2003 as amended)",
        "sa_name": "Garante per la protezione dei dati personali",
        "sa_url": "https://www.garanteprivacy.it",
        "language": "Italian",
        "notes": [
            "Garante has issued simplified notice guidelines for minors",
            "Specific cookie guidelines (Garante Cookie Guidelines 2021)",
            "Marketing consent requires granular opt-in (no bundled consent)",
            "Simplified notice format available for straightforward processing",
        ],
        "dpo_note": "DPO appointment follows GDPR Art. 37 criteria; Garante recommends broader adoption",
    },
    "ES": {
        "name": "Spain",
        "regulation": "GDPR + LOPDGDD (Ley Orgánica 3/2018)",
        "sa_name": "AEPD (Agencia Española de Protección de Datos)",
        "sa_url": "https://www.aepd.es",
        "language": "Spanish",
        "notes": [
            "LOPDGDD supplements GDPR with Spanish-specific provisions",
            "Digital rights provisions (Title X LOPDGDD) including digital disconnection",
            "AEPD guidance on employee monitoring and digital rights",
            "Deceased persons' data rights (Art. 3 LOPDGDD)",
        ],
        "dpo_note": "Art. 34 LOPDGDD mandates DPO for additional categories beyond GDPR Art. 37",
    },
    "NL": {
        "name": "Netherlands",
        "regulation": "GDPR + UAVG (Uitvoeringswet AVG)",
        "sa_name": "AP (Autoriteit Persoonsgegevens)",
        "sa_url": "https://www.autoriteitpersoonsgegevens.nl",
        "language": "Dutch",
        "notes": [
            "AP has prohibited cookie walls (no access = no consent model)",
            "UAVG supplements GDPR for Dutch implementation",
            "Specific guidance on BSN (citizen service number) processing",
            "AP enforcement active on cookie compliance",
        ],
        "dpo_note": "DPO appointment follows GDPR Art. 37 criteria",
    },
    "BE": {
        "name": "Belgium",
        "regulation": "GDPR + Belgian Data Protection Act (30 July 2018)",
        "sa_name": "APD/GBA (Autorité de protection des données / Gegevensbeschermingsautoriteit)",
        "sa_url": "https://www.gegevensbeschermingsautoriteit.be",
        "language": "French / Dutch",
        "notes": [
            "APD has specific guidance on direct marketing consent",
            "Belgian DPA Act supplements GDPR with national provisions",
            "Bilingual requirements for notices in bilingual regions",
        ],
        "dpo_note": "DPO appointment follows GDPR Art. 37 criteria",
    },
    "IE": {
        "name": "Ireland",
        "regulation": "GDPR + Data Protection Act 2018",
        "sa_name": "DPC (Data Protection Commission)",
        "sa_url": "https://www.dataprotection.ie",
        "language": "English",
        "notes": [
            "DPC is lead supervisory authority for many US tech companies (one-stop-shop)",
            "Specific guidance on cross-border processing under Art. 56",
            "DPC enforcement decisions often have EU-wide impact",
            "Irish DPA supplements GDPR with national provisions",
        ],
        "dpo_note": "DPO appointment follows GDPR Art. 37 criteria",
    },
    "UK": {
        "name": "United Kingdom",
        "regulation": "UK GDPR + Data Protection Act 2018 (UK DPA)",
        "sa_name": "ICO (Information Commissioner's Office)",
        "sa_url": "https://ico.org.uk",
        "language": "English",
        "notes": [
            "UK GDPR applies post-Brexit (retained EU law)",
            "UK International Data Transfer Agreement (IDTA) or UK Addendum to EU SCCs",
            "ICO guidance on privacy notices and transparency",
            "PECR (Privacy and Electronic Communications Regulations) for cookies and direct marketing",
            "ICO registration and data protection fee required",
        ],
        "dpo_note": "DPO appointment follows UK GDPR Art. 37 criteria",
    },
}

DATA_CATEGORY_LABELS = {
    "personal": "Identity Data (name, date of birth, gender, nationality)",
    "contact": "Contact Data (email address, telephone number, postal address)",
    "usage": "Usage Data (browsing history, page views, session data, device information)",
    "cookies": "Cookie and Tracking Data (cookie identifiers, analytics data, advertising IDs)",
    "financial": "Financial Data (payment details, bank account, transaction history)",
    "health": "Health Data (medical records, health conditions, disability information)",
    "employment": "Employment Data (role, salary, performance, work history, benefits)",
    "marketing": "Marketing Data (preferences, consent records, campaign interactions)",
    "biometric": "Biometric Data (fingerprints, facial recognition, voice patterns)",
}

LEGAL_BASIS_LABELS = {
    "consent": "Art. 6(1)(a) GDPR — Consent",
    "contract": "Art. 6(1)(b) GDPR — Performance of a contract",
    "legal_obligation": "Art. 6(1)(c) GDPR — Compliance with a legal obligation",
    "vital_interests": "Art. 6(1)(d) GDPR — Protection of vital interests",
    "public_task": "Art. 6(1)(e) GDPR — Public interest or official authority",
    "legitimate_interests": "Art. 6(1)(f) GDPR — Legitimate interests",
}

NOTICE_TYPE_EXTRAS: Dict[str, Dict] = {
    "website": {
        "title_suffix": "Website/Application",
        "extra_sections": ["cookies_tracking"],
        "typical_categories": ["personal", "contact", "usage", "cookies", "marketing"],
    },
    "applicant": {
        "title_suffix": "Job Applicants (Recruiting)",
        "extra_sections": ["talent_pool"],
        "typical_categories": ["personal", "contact", "employment"],
    },
    "employee": {
        "title_suffix": "Employees",
        "extra_sections": ["employee_monitoring", "works_council"],
        "typical_categories": ["personal", "contact", "employment", "financial", "health"],
    },
    "b2b": {
        "title_suffix": "Business Partners",
        "extra_sections": ["art14_source"],
        "typical_categories": ["personal", "contact"],
    },
    "b2c": {
        "title_suffix": "Customers",
        "extra_sections": ["soft_optin", "payment_processing"],
        "typical_categories": ["personal", "contact", "financial", "usage", "marketing"],
    },
    "combined": {
        "title_suffix": "Data Processing",
        "extra_sections": [],
        "typical_categories": ["personal", "contact", "usage", "financial"],
    },
}


def generate_section(num: int, title: str, content: str) -> str:
    """Generate a numbered section."""
    return f"## {num}. {title}\n\n{content}\n"


def build_notice(notice_type: str, jurisdiction: str, data_categories: List[str],
                 legal_bases: List[str], has_cookies: bool, has_ai: bool,
                 has_transfers: bool) -> str:
    """Build the complete privacy notice skeleton."""
    jur = JURISDICTIONS[jurisdiction]
    nt = NOTICE_TYPE_EXTRAS[notice_type]
    lines = []

    # Header
    lines.append(f"# Privacy Notice — {nt['title_suffix']}")
    lines.append(f"\n**Jurisdiction:** {jur['name']} ({jur['regulation']})")
    lines.append(f"**Last Updated:** {datetime.now().strftime('%d %B %Y')}")
    lines.append(f"**Version:** 1.0\n")
    lines.append("---\n")

    sec = 1

    # Section 1: Controller Identity
    content = ("| Field | Details |\n|-------|--------|\n"
               "| Controller | [PLACEHOLDER: Legal entity name and registered address] |\n"
               "| Registration | [PLACEHOLDER: Commercial register number] |\n"
               "| Contact | [PLACEHOLDER: Email, phone, postal address] |\n"
               f"| Supervisory Authority | {jur['sa_name']} — {jur['sa_url']} |\n")
    lines.append(generate_section(sec, "Who We Are (Controller Identity)", content))
    sec += 1

    # Section 2: DPO
    content = (f"> {jur['dpo_note']}\n\n"
               "| Field | Details |\n|-------|--------|\n"
               "| DPO Name | [PLACEHOLDER: DPO name or title] |\n"
               "| DPO Contact | [PLACEHOLDER: dpo@company.com] |\n"
               "| DPO Address | [PLACEHOLDER: Postal address if different from controller] |\n")
    lines.append(generate_section(sec, "Data Protection Officer", content))
    sec += 1

    # Section 3: Data Categories
    content = "We collect and process the following categories of your personal data:\n\n"
    content += "| Category | Description | Source |\n|----------|-------------|--------|\n"
    for cat in data_categories:
        label = DATA_CATEGORY_LABELS.get(cat, cat)
        source = "Directly from you" if cat not in ("usage", "cookies") else "Automatically collected"
        if notice_type == "b2b":
            source = "[PLACEHOLDER: Specify source — directly, from employer, from public sources]"
        content += f"| {label} | [PLACEHOLDER: Specific data elements] | {source} |\n"
    lines.append(generate_section(sec, "What Data We Collect", content))
    sec += 1

    # Section 4: Purposes and Legal Bases
    content = "| Purpose | Legal Basis | Details |\n|---------|------------|--------|\n"
    for basis in legal_bases:
        label = LEGAL_BASIS_LABELS.get(basis, basis)
        content += f"| [PLACEHOLDER: Specific purpose] | {label} | [PLACEHOLDER: Why this basis applies] |\n"
    if "health" in data_categories or "biometric" in data_categories:
        content += "\n> **Special Category Data:** Processing of health or biometric data requires an additional legal basis under Art. 9(2) GDPR. [PLACEHOLDER: Specify Art. 9(2) basis — e.g., explicit consent, employment law, vital interests]\n"
    lines.append(generate_section(sec, "Why We Process Your Data (Purposes and Legal Bases)", content))
    sec += 1

    # Section 5: Recipients
    content = ("| Recipient Category | Purpose | Location |\n"
               "|-------------------|---------|----------|\n"
               "| [PLACEHOLDER: IT service providers] | [PLACEHOLDER: Hosting, maintenance] | [PLACEHOLDER: EU/EEA or specify] |\n"
               "| [PLACEHOLDER: Payment processors] | [PLACEHOLDER: Payment handling] | [PLACEHOLDER: Country] |\n"
               "| [PLACEHOLDER: Analytics providers] | [PLACEHOLDER: Usage analysis] | [PLACEHOLDER: Country] |\n"
               "| [PLACEHOLDER: Other recipients] | [PLACEHOLDER: Purpose] | [PLACEHOLDER: Country] |\n")
    lines.append(generate_section(sec, "Who Receives Your Data", content))
    sec += 1

    # Section 6: International Transfers
    if has_transfers:
        content = ("> We transfer your personal data to recipients outside the EU/EEA. "
                   "We ensure appropriate safeguards are in place.\n\n"
                   "| Recipient | Country | Transfer Mechanism | Further Information |\n"
                   "|-----------|---------|-------------------|--------------------|\n"
                   "| [PLACEHOLDER] | [PLACEHOLDER] | [PLACEHOLDER: Adequacy decision / SCCs / BCRs] | [PLACEHOLDER: Link to SCCs or further info] |\n")
        if jurisdiction == "UK":
            content += "\n> **UK Transfers:** Transfers from the UK use the UK International Data Transfer Agreement (IDTA) or UK Addendum to EU SCCs.\n"
    else:
        content = "Your personal data is processed within the EU/EEA. If transfers outside the EU/EEA become necessary, we will update this notice and ensure appropriate safeguards per Chapter V GDPR.\n"
    lines.append(generate_section(sec, "International Data Transfers", content))
    sec += 1

    # Section 7: Retention
    content = ("| Data Category | Retention Period | Basis |\n"
               "|--------------|-----------------|-------|\n")
    for cat in data_categories:
        label = DATA_CATEGORY_LABELS.get(cat, cat).split("(")[0].strip()
        content += f"| {label} | [PLACEHOLDER: Specific period or criteria] | [PLACEHOLDER: Legal basis for retention] |\n"
    if notice_type == "applicant":
        content += "\n> **Applicant Data Default:** Application data is retained for 6 months after the recruitment process concludes, unless you consent to inclusion in our talent pool.\n"
    if notice_type == "employee":
        content += "\n> **Employee Data:** Retention periods are subject to statutory requirements (e.g., tax records, social security). Specific retention schedules are available from HR.\n"
    lines.append(generate_section(sec, "How Long We Keep Your Data", content))
    sec += 1

    # Section 8: Data Subject Rights
    rights_table = ("You have the following rights under GDPR:\n\n"
                    "| Right | Description | Reference |\n"
                    "|-------|------------|----------|\n"
                    "| Access | Request a copy of your personal data | Art. 15 GDPR |\n"
                    "| Rectification | Request correction of inaccurate data | Art. 16 GDPR |\n"
                    "| Erasure | Request deletion of your data | Art. 17 GDPR |\n"
                    "| Restriction | Request limitation of processing | Art. 18 GDPR |\n"
                    "| Data Portability | Receive your data in a structured format | Art. 20 GDPR |\n"
                    "| Objection | Object to processing based on legitimate interests | Art. 21 GDPR |\n"
                    "| Automated Decisions | Right not to be subject to solely automated decisions | Art. 22 GDPR |\n"
                    "| Withdraw Consent | Withdraw consent at any time without affecting prior processing | Art. 7(3) GDPR |\n"
                    "\nTo exercise your rights, contact us at [PLACEHOLDER: privacy@company.com].\n")

    # Art. 21 prominence for DE
    if jurisdiction == "DE":
        rights_table += ("\n---\n\n### Right to Object (Widerspruchsrecht) — Art. 21 DSGVO\n\n"
                         "**You have the right to object at any time, on grounds relating to your particular situation, "
                         "to the processing of your personal data based on Art. 6(1)(e) or (f) DSGVO. "
                         "If you object, we will no longer process your data unless we can demonstrate compelling "
                         "legitimate grounds that override your interests, rights, and freedoms, or the processing "
                         "serves the establishment, exercise, or defense of legal claims.**\n\n"
                         "**If we process your personal data for direct marketing purposes, you have the right to "
                         "object at any time. If you object to processing for direct marketing, we will no longer "
                         "process your data for these purposes.**\n")
    lines.append(generate_section(sec, "Your Rights", rights_table))
    sec += 1

    # Section 9: Consent Withdrawal
    if "consent" in legal_bases:
        content = ("Where we process your personal data based on your consent, you have the right to withdraw "
                   "that consent at any time. Withdrawal does not affect the lawfulness of processing carried "
                   "out before the withdrawal.\n\n"
                   "**How to withdraw consent:** [PLACEHOLDER: Describe method — email, settings page, unsubscribe link]\n")
        lines.append(generate_section(sec, "Withdrawing Your Consent", content))
        sec += 1

    # Section 10: Right to Complain
    content = (f"You have the right to lodge a complaint with a supervisory authority, in particular in the "
               f"Member State of your habitual residence, place of work, or place of the alleged infringement.\n\n"
               f"**Your supervisory authority:**\n"
               f"- **Name:** {jur['sa_name']}\n"
               f"- **Website:** {jur['sa_url']}\n"
               f"- **Contact:** [PLACEHOLDER: SA postal address and phone]\n")
    lines.append(generate_section(sec, "Right to Complain", content))
    sec += 1

    # Section 11: Automated Decision-Making
    content = ("[PLACEHOLDER: Describe any automated decision-making including profiling per Art. 22 GDPR. "
               "If no automated decision-making with legal/significant effects, state: "
               "\"We do not use your personal data for automated decision-making that produces legal or similarly significant effects.\"]\n\n"
               "If automated decisions are used:\n"
               "- Logic involved: [PLACEHOLDER]\n"
               "- Significance and consequences: [PLACEHOLDER]\n"
               "- Right to human review: [PLACEHOLDER]\n")
    lines.append(generate_section(sec, "Automated Decision-Making", content))
    sec += 1

    # Section 12: Cookies (if applicable)
    if has_cookies or "cookies" in data_categories or notice_type == "website":
        content = ("| Cookie Category | Examples | Purpose | Consent Required |\n"
                   "|----------------|---------|---------|------------------|\n"
                   "| Strictly Necessary | Session, CSRF, load balancer | Essential website function | No |\n"
                   "| Functional | Language, UI preferences | Enhanced user experience | Yes |\n"
                   "| Analytics | [PLACEHOLDER: e.g., Google Analytics] | Usage analysis | Yes |\n"
                   "| Marketing | [PLACEHOLDER: e.g., Facebook Pixel] | Targeted advertising | Yes |\n"
                   "\nYou can manage your cookie preferences at any time via [PLACEHOLDER: cookie settings link/button].\n")
        if jurisdiction == "DE":
            content += "\n> **DE Note:** Cookie consent must comply with DSK guidance and TDDDG. Non-essential cookies require prior opt-in consent.\n"
        if jurisdiction == "FR":
            content += "\n> **FR Note:** Cookie consent must comply with CNIL guidelines. \"Continue browsing\" does not constitute valid consent.\n"
        if jurisdiction == "NL":
            content += "\n> **NL Note:** Cookie walls are prohibited per AP guidance. Users must be able to access the service without accepting non-essential cookies.\n"
        lines.append(generate_section(sec, "Cookies and Tracking Technologies", content))
        sec += 1

    # Section 13: AI Processing (if applicable)
    if has_ai:
        content = ("> **EU AI Act (Regulation 2024/1689) Art. 50 Transparency Obligations**\n\n"
                   "| AI System | Purpose | Risk Level | Human Oversight |\n"
                   "|-----------|---------|-----------|----------------|\n"
                   "| [PLACEHOLDER: AI system name] | [PLACEHOLDER: Purpose] | [PLACEHOLDER: High/Limited/Minimal] | [PLACEHOLDER: Description] |\n"
                   "\n**How AI affects you:**\n"
                   "- [PLACEHOLDER: What decisions or outputs AI influences]\n"
                   "- [PLACEHOLDER: Your rights regarding AI processing]\n"
                   "- [PLACEHOLDER: How to request human review]\n")
        lines.append(generate_section(sec, "AI and Automated Processing", content))
        sec += 1

    # Type-specific sections
    if notice_type == "applicant":
        content = ("If your application is unsuccessful, we may ask for your consent to retain your data "
                   "in our talent pool for future opportunities.\n\n"
                   "- **Retention in talent pool:** [PLACEHOLDER: Period, e.g., 12 months]\n"
                   "- **Consent mechanism:** [PLACEHOLDER: How consent is obtained]\n"
                   "- **Withdrawal:** You can request removal from the talent pool at any time.\n")
        lines.append(generate_section(sec, "Talent Pool", content))
        sec += 1

    if notice_type == "employee":
        if jurisdiction in ("DE", "AT"):
            content = ("Your employer may be required to inform the works council (Betriebsrat) about "
                       "certain data processing activities in accordance with the Works Constitution Act "
                       "(Betriebsverfassungsgesetz).\n\n"
                       "- [PLACEHOLDER: Describe works council notification scope]\n"
                       "- [PLACEHOLDER: IT monitoring arrangements agreed with works council]\n"
                       "- [PLACEHOLDER: BYOD policy if applicable]\n")
        else:
            content = ("- [PLACEHOLDER: Employee representative body notification if applicable]\n"
                       "- [PLACEHOLDER: IT monitoring policy and scope]\n"
                       "- [PLACEHOLDER: BYOD policy if applicable]\n")
        lines.append(generate_section(sec, "Employee-Specific Information", content))
        sec += 1

    if notice_type == "b2b":
        content = ("Where we have not collected your personal data directly from you, we are required "
                   "under Art. 14 GDPR to inform you of the source.\n\n"
                   "| Source Category | Data Obtained | Publicly Available |\n"
                   "|----------------|--------------|-------------------|\n"
                   "| [PLACEHOLDER: Your employer] | Contact details, role | [PLACEHOLDER: Yes/No] |\n"
                   "| [PLACEHOLDER: Business registers] | Company details | Yes |\n"
                   "| [PLACEHOLDER: Industry databases] | Professional contact details | [PLACEHOLDER: Yes/No] |\n")
        lines.append(generate_section(sec, "Source of Your Data (Art. 14 GDPR)", content))
        sec += 1

    # Jurisdiction notes
    if jur["notes"]:
        lines.append(f"## Jurisdiction-Specific Notes ({jur['name']})\n")
        for note in jur["notes"]:
            lines.append(f"- {note}")
        lines.append("")

    # Footer
    lines.append("---\n")
    lines.append(f"*This privacy notice was generated on {datetime.now().strftime('%Y-%m-%d')} "
                 f"for {jur['name']} jurisdiction. All [PLACEHOLDER] markers must be replaced "
                 f"with actual information before publication. Legal review is required.*\n")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate a privacy notice skeleton with jurisdiction-specific placeholders"
    )
    parser.add_argument("--notice-type", required=True, choices=NOTICE_TYPES,
                        help="Notice type: website, applicant, employee, b2b, b2c, combined")
    parser.add_argument("--jurisdiction", required=True, choices=list(JURISDICTIONS.keys()),
                        help="Jurisdiction code: DE, FR, AT, IT, ES, NL, BE, IE, UK")
    parser.add_argument("--data-categories", required=True,
                        help="Comma-separated data categories: personal,contact,usage,cookies,financial,health,employment,marketing,biometric")
    parser.add_argument("--legal-bases", required=True,
                        help="Comma-separated legal bases: consent,contract,legal_obligation,legitimate_interests,vital_interests,public_task")
    parser.add_argument("--has-cookies", action="store_true", help="Include cookies and tracking section")
    parser.add_argument("--has-ai", action="store_true", help="Include AI and automated processing section")
    parser.add_argument("--has-international-transfers", action="store_true",
                        help="Include international transfers section")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")

    args = parser.parse_args()

    try:
        categories = [c.strip() for c in args.data_categories.split(",")]
        bases = [b.strip() for b in args.legal_bases.split(",")]

        # Validate categories
        valid_cats = set(DATA_CATEGORY_LABELS.keys())
        for cat in categories:
            if cat not in valid_cats:
                print(f"Warning: Unknown data category '{cat}'. Valid: {', '.join(sorted(valid_cats))}", file=sys.stderr)

        # Validate bases
        valid_bases = set(LEGAL_BASIS_LABELS.keys())
        for basis in bases:
            if basis not in valid_bases:
                print(f"Warning: Unknown legal basis '{basis}'. Valid: {', '.join(sorted(valid_bases))}", file=sys.stderr)

        notice = build_notice(
            args.notice_type, args.jurisdiction, categories, bases,
            args.has_cookies, args.has_ai, args.has_international_transfers
        )

        if args.json:
            output = {
                "generated": datetime.now().isoformat(),
                "parameters": {
                    "notice_type": args.notice_type,
                    "jurisdiction": args.jurisdiction,
                    "data_categories": categories,
                    "legal_bases": bases,
                    "has_cookies": args.has_cookies,
                    "has_ai": args.has_ai,
                    "has_international_transfers": args.has_international_transfers,
                },
                "notice_markdown": notice,
                "placeholder_count": notice.count("[PLACEHOLDER"),
                "jurisdiction_info": JURISDICTIONS[args.jurisdiction],
            }
            print(json.dumps(output, indent=2))
        else:
            print(notice)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
