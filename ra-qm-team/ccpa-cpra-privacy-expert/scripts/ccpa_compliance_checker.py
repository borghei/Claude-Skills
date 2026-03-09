#!/usr/bin/env python3
"""
CCPA/CPRA Compliance Checker

Evaluates organizational readiness against all CCPA/CPRA requirements.
Validates privacy policies, consumer rights handling, technical safeguards,
opt-out mechanisms, and sensitive personal information controls.

Usage:
    python ccpa_compliance_checker.py --template > profile.json
    python ccpa_compliance_checker.py --input profile.json
    python ccpa_compliance_checker.py --input profile.json --json
    python ccpa_compliance_checker.py --input profile.json --output report.json
"""

import argparse
import json
import sys
from datetime import datetime
from typing import Any, Dict, List, Tuple


TEMPLATE = {
    "organization": {
        "name": "",
        "annual_revenue_usd": 0,
        "consumers_or_households_count": 0,
        "percent_revenue_from_selling_sharing_pi": 0,
        "is_hipaa_covered_entity": False,
        "is_glba_covered": False,
        "processes_employee_data_only": False,
        "processes_b2b_data_only": False
    },
    "privacy_policy": {
        "exists": False,
        "last_updated": "",
        "available_online": False,
        "accessible_format": False,
        "languages": [],
        "discloses_pi_categories_collected": False,
        "discloses_pi_sources": False,
        "discloses_business_purposes": False,
        "discloses_commercial_purposes": False,
        "discloses_third_party_categories": False,
        "discloses_consumer_rights": False,
        "discloses_right_to_know": False,
        "discloses_right_to_delete": False,
        "discloses_right_to_opt_out": False,
        "discloses_right_to_correct": False,
        "discloses_right_to_limit_spi": False,
        "discloses_right_to_portability": False,
        "discloses_right_to_non_discrimination": False,
        "discloses_retention_periods": False,
        "discloses_sale_sharing_categories": False,
        "discloses_spi_categories": False,
        "updated_annually": False,
        "prior_versions_archived": False
    },
    "consumer_rights": {
        "request_intake_mechanism": False,
        "toll_free_number": False,
        "online_request_form": False,
        "email_request_option": False,
        "identity_verification_process": False,
        "two_data_point_verification": False,
        "three_data_point_for_sensitive": False,
        "authorized_agent_process": False,
        "acknowledgment_within_10_days": False,
        "fulfillment_within_45_days": False,
        "extension_process_with_notice": False,
        "right_to_know_implemented": False,
        "right_to_delete_implemented": False,
        "right_to_opt_out_implemented": False,
        "right_to_correct_implemented": False,
        "right_to_limit_spi_implemented": False,
        "right_to_portability_implemented": False,
        "non_discrimination_policy": False,
        "appeal_process": False,
        "request_tracking_system": False,
        "response_templates": False,
        "staff_trained_on_handling": False
    },
    "opt_out_mechanisms": {
        "do_not_sell_or_share_link": False,
        "link_on_homepage": False,
        "link_clear_and_conspicuous": False,
        "limit_use_of_spi_link": False,
        "spi_link_on_homepage": False,
        "global_privacy_control_honored": False,
        "gpc_technical_detection": False,
        "cookie_consent_banner": False,
        "cookie_categories_defined": False,
        "opt_out_preference_signal_respected": False,
        "no_dark_patterns": False,
        "opt_out_easy_as_opt_in": False,
        "minor_opt_in_required_under_16": False,
        "parental_consent_under_13": False
    },
    "sensitive_personal_information": {
        "spi_categories_identified": False,
        "ssn_protected": False,
        "financial_accounts_protected": False,
        "precise_geolocation_controlled": False,
        "racial_ethnic_data_controlled": False,
        "biometric_data_controlled": False,
        "health_data_controlled": False,
        "sexual_orientation_data_controlled": False,
        "email_text_content_controlled": False,
        "login_credentials_protected": False,
        "genetic_data_controlled": False,
        "spi_use_limited_to_disclosed_purposes": False,
        "spi_processing_minimized": False
    },
    "technical_safeguards": {
        "encryption_at_rest": False,
        "encryption_in_transit": False,
        "access_controls_implemented": False,
        "role_based_access": False,
        "mfa_for_pi_access": False,
        "audit_logging": False,
        "data_loss_prevention": False,
        "incident_response_plan": False,
        "breach_notification_process": False,
        "vulnerability_management": False,
        "penetration_testing": False,
        "security_awareness_training": False,
        "vendor_security_assessments": False,
        "data_backup_and_recovery": False
    },
    "service_providers": {
        "sp_agreements_in_place": False,
        "agreements_restrict_pi_use": False,
        "agreements_require_deletion": False,
        "agreements_allow_audits": False,
        "contractor_agreements_in_place": False,
        "contractor_certification_obtained": False,
        "third_party_data_sharing_documented": False,
        "third_party_opt_out_honored": False,
        "data_processing_agreements": False,
        "sp_security_requirements": False,
        "sp_breach_notification_clause": False,
        "subprocessor_management": False
    },
    "risk_assessments": {
        "annual_cybersecurity_audit_planned": False,
        "risk_assessment_for_processing": False,
        "data_inventory_maintained": False,
        "data_flow_mapping_current": False,
        "retention_schedule_documented": False,
        "cross_border_transfers_documented": False,
        "automated_decision_making_disclosed": False,
        "data_minimization_practiced": False,
        "purpose_limitation_enforced": False
    }
}


CATEGORY_WEIGHTS = {
    "applicability": 5,
    "privacy_policy": 20,
    "consumer_rights": 25,
    "opt_out_mechanisms": 15,
    "sensitive_personal_information": 10,
    "technical_safeguards": 10,
    "service_providers": 10,
    "risk_assessments": 5
}


def check_applicability(data: Dict) -> Tuple[float, List[Dict]]:
    """Check if the organization is subject to CCPA/CPRA."""
    org = data.get("organization", {})
    findings = []
    triggers = 0
    total_triggers = 3

    revenue = org.get("annual_revenue_usd", 0)
    if revenue >= 25_000_000:
        triggers += 1
        findings.append({
            "check": "Revenue threshold",
            "status": "triggered",
            "detail": f"Revenue ${revenue:,.0f} exceeds $25M threshold",
            "reference": "Cal. Civ. Code §1798.140(d)(1)(A)"
        })
    else:
        findings.append({
            "check": "Revenue threshold",
            "status": "not_triggered",
            "detail": f"Revenue ${revenue:,.0f} below $25M threshold",
            "reference": "Cal. Civ. Code §1798.140(d)(1)(A)"
        })

    consumers = org.get("consumers_or_households_count", 0)
    if consumers >= 100_000:
        triggers += 1
        findings.append({
            "check": "Consumer count threshold",
            "status": "triggered",
            "detail": f"{consumers:,} consumers/households exceeds 100K threshold",
            "reference": "Cal. Civ. Code §1798.140(d)(1)(B)"
        })
    else:
        findings.append({
            "check": "Consumer count threshold",
            "status": "not_triggered",
            "detail": f"{consumers:,} consumers/households below 100K threshold",
            "reference": "Cal. Civ. Code §1798.140(d)(1)(B)"
        })

    pct_revenue = org.get("percent_revenue_from_selling_sharing_pi", 0)
    if pct_revenue >= 50:
        triggers += 1
        findings.append({
            "check": "PI revenue threshold",
            "status": "triggered",
            "detail": f"{pct_revenue}% revenue from selling/sharing PI exceeds 50% threshold",
            "reference": "Cal. Civ. Code §1798.140(d)(1)(C)"
        })
    else:
        findings.append({
            "check": "PI revenue threshold",
            "status": "not_triggered",
            "detail": f"{pct_revenue}% revenue from selling/sharing PI below 50% threshold",
            "reference": "Cal. Civ. Code §1798.140(d)(1)(C)"
        })

    # Check exemptions
    exemptions = []
    if org.get("is_hipaa_covered_entity"):
        exemptions.append("HIPAA-covered entity (§1798.145(c))")
    if org.get("is_glba_covered"):
        exemptions.append("GLBA-covered (§1798.145(e))")
    if org.get("processes_employee_data_only"):
        exemptions.append("Employee data exemption (under review through 2026)")
    if org.get("processes_b2b_data_only"):
        exemptions.append("B2B data exemption (under review through 2026)")

    if exemptions:
        for ex in exemptions:
            findings.append({
                "check": "Exemption",
                "status": "info",
                "detail": ex,
                "reference": "Cal. Civ. Code §1798.145"
            })

    is_subject = triggers >= 1 and not (
        org.get("is_hipaa_covered_entity") or org.get("is_glba_covered")
    )

    score = 100.0 if is_subject else (0.0 if triggers == 0 else 50.0)

    findings.insert(0, {
        "check": "CCPA/CPRA applicability",
        "status": "subject" if is_subject else "not_subject",
        "detail": f"{triggers} of {total_triggers} thresholds triggered",
        "reference": "Cal. Civ. Code §1798.140(d)"
    })

    return score, findings


def check_boolean_section(data: Dict, section_key: str,
                          checks: List[Dict]) -> Tuple[float, List[Dict]]:
    """Evaluate a section of boolean compliance checks."""
    section = data.get(section_key, {})
    findings = []
    passed = 0
    total = len(checks)

    for check in checks:
        key = check["key"]
        value = section.get(key, False)
        status = "pass" if value else "fail"
        if value:
            passed += 1
        findings.append({
            "check": check["name"],
            "status": status,
            "detail": check.get("detail_pass" if value else "detail_fail", ""),
            "reference": check.get("reference", ""),
            "severity": check.get("severity", "medium")
        })

    score = (passed / total * 100) if total > 0 else 0
    return score, findings


PRIVACY_POLICY_CHECKS = [
    {"key": "exists", "name": "Privacy policy exists",
     "detail_pass": "Privacy policy documented",
     "detail_fail": "No privacy policy found — required under §1798.100(b)",
     "reference": "§1798.100(b)", "severity": "critical"},
    {"key": "available_online", "name": "Available online",
     "detail_pass": "Policy accessible on website",
     "detail_fail": "Policy not available online — must be posted conspicuously",
     "reference": "§1798.130(a)(5)", "severity": "critical"},
    {"key": "accessible_format", "name": "Accessible format",
     "detail_pass": "Policy in accessible format",
     "detail_fail": "Policy not in accessible format for consumers with disabilities",
     "reference": "§1798.130(a)(5)", "severity": "medium"},
    {"key": "discloses_pi_categories_collected", "name": "PI categories disclosed",
     "detail_pass": "Categories of PI collected are disclosed",
     "detail_fail": "Must disclose categories of PI collected in past 12 months",
     "reference": "§1798.100(a)", "severity": "critical"},
    {"key": "discloses_pi_sources", "name": "PI sources disclosed",
     "detail_pass": "Sources of PI are disclosed",
     "detail_fail": "Must disclose categories of sources from which PI is collected",
     "reference": "§1798.110(c)(2)", "severity": "high"},
    {"key": "discloses_business_purposes", "name": "Business purposes disclosed",
     "detail_pass": "Business purposes for collection are disclosed",
     "detail_fail": "Must disclose business or commercial purposes for collecting PI",
     "reference": "§1798.110(c)(3)", "severity": "high"},
    {"key": "discloses_third_party_categories", "name": "Third party categories disclosed",
     "detail_pass": "Categories of third parties are disclosed",
     "detail_fail": "Must disclose categories of third parties to whom PI is disclosed",
     "reference": "§1798.110(c)(4)", "severity": "high"},
    {"key": "discloses_consumer_rights", "name": "Consumer rights described",
     "detail_pass": "Consumer rights are described in policy",
     "detail_fail": "Must describe consumer rights and how to exercise them",
     "reference": "§1798.130(a)(2)", "severity": "critical"},
    {"key": "discloses_right_to_know", "name": "Right to Know disclosed",
     "detail_pass": "Right to Know is described",
     "detail_fail": "Must disclose Right to Know categories and specific pieces of PI",
     "reference": "§1798.100, §1798.110", "severity": "high"},
    {"key": "discloses_right_to_delete", "name": "Right to Delete disclosed",
     "detail_pass": "Right to Delete is described",
     "detail_fail": "Must disclose Right to Delete PI",
     "reference": "§1798.105", "severity": "high"},
    {"key": "discloses_right_to_opt_out", "name": "Right to Opt-Out disclosed",
     "detail_pass": "Right to Opt-Out of sale/sharing is described",
     "detail_fail": "Must disclose Right to Opt-Out of sale or sharing",
     "reference": "§1798.120", "severity": "high"},
    {"key": "discloses_right_to_correct", "name": "Right to Correct disclosed",
     "detail_pass": "Right to Correct is described (CPRA)",
     "detail_fail": "Must disclose Right to Correct inaccurate PI (CPRA requirement)",
     "reference": "§1798.106", "severity": "high"},
    {"key": "discloses_right_to_limit_spi", "name": "Right to Limit SPI Use disclosed",
     "detail_pass": "Right to Limit Use of SPI is described (CPRA)",
     "detail_fail": "Must disclose Right to Limit Use of Sensitive PI",
     "reference": "§1798.121", "severity": "high"},
    {"key": "discloses_right_to_portability", "name": "Right to Portability disclosed",
     "detail_pass": "Right to Data Portability is described (CPRA)",
     "detail_fail": "Must disclose Right to Data Portability",
     "reference": "§1798.130", "severity": "medium"},
    {"key": "discloses_right_to_non_discrimination", "name": "Non-discrimination disclosed",
     "detail_pass": "Right to Non-Discrimination is described",
     "detail_fail": "Must disclose Right to Non-Discrimination for exercising rights",
     "reference": "§1798.125", "severity": "high"},
    {"key": "discloses_retention_periods", "name": "Retention periods disclosed",
     "detail_pass": "Retention periods are disclosed (CPRA)",
     "detail_fail": "Must disclose retention periods for each PI category (CPRA)",
     "reference": "§1798.100(a)(3)", "severity": "medium"},
    {"key": "discloses_sale_sharing_categories", "name": "Sale/sharing categories disclosed",
     "detail_pass": "Categories of PI sold or shared are disclosed",
     "detail_fail": "Must disclose categories of PI sold or shared in past 12 months",
     "reference": "§1798.115(c)", "severity": "high"},
    {"key": "discloses_spi_categories", "name": "SPI categories disclosed",
     "detail_pass": "Sensitive PI categories collected are disclosed",
     "detail_fail": "Must disclose categories of SPI collected (CPRA)",
     "reference": "§1798.100(a)(2)", "severity": "high"},
    {"key": "updated_annually", "name": "Updated annually",
     "detail_pass": "Policy updated at least annually",
     "detail_fail": "Policy must be updated at least every 12 months",
     "reference": "§1798.130(a)(5)", "severity": "medium"},
    {"key": "prior_versions_archived", "name": "Prior versions archived",
     "detail_pass": "Prior policy versions are archived",
     "detail_fail": "Best practice to maintain archive of prior policy versions",
     "reference": "Best practice", "severity": "low"}
]

CONSUMER_RIGHTS_CHECKS = [
    {"key": "request_intake_mechanism", "name": "Request intake mechanism",
     "detail_pass": "Consumer request intake mechanism exists",
     "detail_fail": "Must provide at least two methods for submitting requests",
     "reference": "§1798.130(a)(1)", "severity": "critical"},
    {"key": "toll_free_number", "name": "Toll-free number",
     "detail_pass": "Toll-free number available for requests",
     "detail_fail": "Must provide toll-free number (unless online-only business)",
     "reference": "§1798.130(a)(1)(A)", "severity": "high"},
    {"key": "online_request_form", "name": "Online request form",
     "detail_pass": "Online request form available",
     "detail_fail": "Should provide online request submission mechanism",
     "reference": "§1798.130(a)(1)", "severity": "high"},
    {"key": "identity_verification_process", "name": "Identity verification",
     "detail_pass": "Identity verification process established",
     "detail_fail": "Must verify identity of consumers making requests",
     "reference": "§1798.140(ak)", "severity": "critical"},
    {"key": "two_data_point_verification", "name": "Two-point verification",
     "detail_pass": "Two data point verification for standard requests",
     "detail_fail": "Standard requests require matching 2+ data points",
     "reference": "CCPA Regulations §999.325", "severity": "high"},
    {"key": "three_data_point_for_sensitive", "name": "Three-point for sensitive",
     "detail_pass": "Three data point verification for specific PI requests",
     "detail_fail": "Requests for specific pieces of PI require 3+ data point match",
     "reference": "CCPA Regulations §999.325", "severity": "high"},
    {"key": "authorized_agent_process", "name": "Authorized agent process",
     "detail_pass": "Authorized agent request process exists",
     "detail_fail": "Must allow authorized agents to submit requests on consumer behalf",
     "reference": "§1798.135(c)", "severity": "medium"},
    {"key": "acknowledgment_within_10_days", "name": "10-day acknowledgment",
     "detail_pass": "Requests acknowledged within 10 business days",
     "detail_fail": "Must confirm receipt within 10 business days",
     "reference": "§1798.130(a)(1)", "severity": "high"},
    {"key": "fulfillment_within_45_days", "name": "45-day fulfillment",
     "detail_pass": "Requests fulfilled within 45 calendar days",
     "detail_fail": "Must fulfill requests within 45 calendar days of receipt",
     "reference": "§1798.130(a)(2)", "severity": "critical"},
    {"key": "extension_process_with_notice", "name": "Extension process",
     "detail_pass": "Extension process with consumer notice exists",
     "detail_fail": "May extend 45 additional days with notice to consumer",
     "reference": "§1798.130(a)(2)", "severity": "medium"},
    {"key": "right_to_know_implemented", "name": "Right to Know operational",
     "detail_pass": "Right to Know request fulfillment operational",
     "detail_fail": "Must implement Right to Know (categories and specific pieces)",
     "reference": "§1798.100, §1798.110", "severity": "critical"},
    {"key": "right_to_delete_implemented", "name": "Right to Delete operational",
     "detail_pass": "Right to Delete request fulfillment operational",
     "detail_fail": "Must implement Right to Delete and notify service providers",
     "reference": "§1798.105", "severity": "critical"},
    {"key": "right_to_opt_out_implemented", "name": "Right to Opt-Out operational",
     "detail_pass": "Right to Opt-Out of sale/sharing operational",
     "detail_fail": "Must implement opt-out of sale and sharing of PI",
     "reference": "§1798.120", "severity": "critical"},
    {"key": "right_to_correct_implemented", "name": "Right to Correct operational",
     "detail_pass": "Right to Correct inaccurate PI operational (CPRA)",
     "detail_fail": "Must implement Right to Correct (CPRA requirement)",
     "reference": "§1798.106", "severity": "high"},
    {"key": "right_to_limit_spi_implemented", "name": "Right to Limit SPI operational",
     "detail_pass": "Right to Limit SPI Use operational (CPRA)",
     "detail_fail": "Must implement Right to Limit Use of SPI (CPRA)",
     "reference": "§1798.121", "severity": "high"},
    {"key": "right_to_portability_implemented", "name": "Right to Portability operational",
     "detail_pass": "Right to Data Portability operational (CPRA)",
     "detail_fail": "Must implement Right to Data Portability in machine-readable format",
     "reference": "§1798.130", "severity": "medium"},
    {"key": "non_discrimination_policy", "name": "Non-discrimination enforced",
     "detail_pass": "Non-discrimination policy for rights exercise enforced",
     "detail_fail": "Must not discriminate against consumers who exercise rights",
     "reference": "§1798.125", "severity": "high"},
    {"key": "appeal_process", "name": "Appeal process",
     "detail_pass": "Appeal process for denied requests exists",
     "detail_fail": "Should provide appeal mechanism for denied or partial requests",
     "reference": "Best practice", "severity": "low"},
    {"key": "request_tracking_system", "name": "Request tracking system",
     "detail_pass": "Request tracking system in place",
     "detail_fail": "Should implement tracking for request SLAs and compliance reporting",
     "reference": "Best practice", "severity": "medium"},
    {"key": "staff_trained_on_handling", "name": "Staff trained",
     "detail_pass": "Staff trained on consumer request handling",
     "detail_fail": "Staff handling requests must be informed of CCPA requirements",
     "reference": "§1798.130(a)(6)", "severity": "high"}
]

OPT_OUT_CHECKS = [
    {"key": "do_not_sell_or_share_link", "name": "Do Not Sell/Share link",
     "detail_pass": "'Do Not Sell or Share My Personal Information' link exists",
     "detail_fail": "Must provide 'Do Not Sell or Share My Personal Information' link",
     "reference": "§1798.135(a)(1)", "severity": "critical"},
    {"key": "link_on_homepage", "name": "Link on homepage",
     "detail_pass": "Opt-out link on homepage",
     "detail_fail": "Link must be on homepage or clearly accessible",
     "reference": "§1798.135(a)(1)", "severity": "critical"},
    {"key": "link_clear_and_conspicuous", "name": "Link clear and conspicuous",
     "detail_pass": "Opt-out link is clear and conspicuous",
     "detail_fail": "Link must be clear, conspicuous, and not buried in footer",
     "reference": "§1798.135(a)(1)", "severity": "high"},
    {"key": "limit_use_of_spi_link", "name": "Limit SPI Use link",
     "detail_pass": "'Limit the Use of My Sensitive Personal Information' link exists",
     "detail_fail": "Must provide 'Limit the Use of My Sensitive Personal Information' link (CPRA)",
     "reference": "§1798.135(a)(2)", "severity": "critical"},
    {"key": "spi_link_on_homepage", "name": "SPI link on homepage",
     "detail_pass": "SPI limit link on homepage",
     "detail_fail": "SPI limit link must be on homepage (CPRA)",
     "reference": "§1798.135(a)(2)", "severity": "high"},
    {"key": "global_privacy_control_honored", "name": "GPC honored",
     "detail_pass": "Global Privacy Control browser signal is honored",
     "detail_fail": "Must treat GPC signal as valid opt-out request",
     "reference": "§1798.135(b)(1)", "severity": "critical"},
    {"key": "gpc_technical_detection", "name": "GPC technical detection",
     "detail_pass": "GPC signal technically detected (Sec-GPC header / JS API)",
     "detail_fail": "Must detect Sec-GPC:1 header or navigator.globalPrivacyControl",
     "reference": "§1798.135(b)(1)", "severity": "high"},
    {"key": "cookie_consent_banner", "name": "Cookie consent banner",
     "detail_pass": "Cookie consent banner implemented",
     "detail_fail": "Should implement cookie consent for non-essential cookies",
     "reference": "Best practice / §1798.135", "severity": "medium"},
    {"key": "cookie_categories_defined", "name": "Cookie categories defined",
     "detail_pass": "Cookie categories (necessary, functional, analytics, ads) defined",
     "detail_fail": "Should categorize cookies for granular consent",
     "reference": "Best practice", "severity": "low"},
    {"key": "opt_out_preference_signal_respected", "name": "Opt-out preference signals",
     "detail_pass": "Opt-out preference signals respected",
     "detail_fail": "Must respect opt-out preference signals per CPPA regulations",
     "reference": "§1798.135(b)", "severity": "high"},
    {"key": "no_dark_patterns", "name": "No dark patterns",
     "detail_pass": "No dark patterns in opt-out UX",
     "detail_fail": "Must not use dark patterns that subvert consumer opt-out choices",
     "reference": "§1798.140(l)", "severity": "high"},
    {"key": "opt_out_easy_as_opt_in", "name": "Opt-out ease parity",
     "detail_pass": "Opt-out process as easy as opt-in",
     "detail_fail": "Opt-out must be as easy as opting in (symmetric choice)",
     "reference": "§1798.135(b)(1)", "severity": "medium"},
    {"key": "minor_opt_in_required_under_16", "name": "Minor opt-in (under 16)",
     "detail_pass": "Opt-in required for consumers under 16 before selling PI",
     "detail_fail": "Must obtain opt-in consent before selling PI of minors under 16",
     "reference": "§1798.120(c)", "severity": "high"},
    {"key": "parental_consent_under_13", "name": "Parental consent (under 13)",
     "detail_pass": "Parental consent obtained for consumers under 13",
     "detail_fail": "Must obtain parental/guardian consent for children under 13",
     "reference": "§1798.120(c)", "severity": "high"}
]

SPI_CHECKS = [
    {"key": "spi_categories_identified", "name": "SPI categories identified",
     "detail_pass": "Sensitive PI categories identified and documented",
     "detail_fail": "Must identify all SPI categories per §1798.140(ae)",
     "reference": "§1798.140(ae)", "severity": "critical"},
    {"key": "ssn_protected", "name": "SSN protected",
     "detail_pass": "Social Security numbers protected with enhanced controls",
     "detail_fail": "SSN is SPI — requires enhanced protection and use limitation",
     "reference": "§1798.140(ae)(1)", "severity": "critical"},
    {"key": "financial_accounts_protected", "name": "Financial accounts protected",
     "detail_pass": "Financial account information protected",
     "detail_fail": "Financial account numbers with access credentials are SPI",
     "reference": "§1798.140(ae)(3)", "severity": "critical"},
    {"key": "precise_geolocation_controlled", "name": "Precise geolocation controlled",
     "detail_pass": "Precise geolocation data controlled",
     "detail_fail": "Precise geolocation (within 1,850 ft) is SPI requiring controls",
     "reference": "§1798.140(ae)(4)", "severity": "high"},
    {"key": "racial_ethnic_data_controlled", "name": "Racial/ethnic data controlled",
     "detail_pass": "Racial or ethnic origin data controlled",
     "detail_fail": "Racial or ethnic origin is SPI under CPRA",
     "reference": "§1798.140(ae)(5)", "severity": "high"},
    {"key": "biometric_data_controlled", "name": "Biometric data controlled",
     "detail_pass": "Biometric data for identification controlled",
     "detail_fail": "Biometric data used for identification is SPI",
     "reference": "§1798.140(ae)(8)", "severity": "high"},
    {"key": "health_data_controlled", "name": "Health data controlled",
     "detail_pass": "Health information controlled",
     "detail_fail": "Health information is SPI requiring enhanced controls",
     "reference": "§1798.140(ae)(9)", "severity": "high"},
    {"key": "sexual_orientation_data_controlled", "name": "Sex life/orientation controlled",
     "detail_pass": "Sex life or sexual orientation data controlled",
     "detail_fail": "Sex life or sexual orientation data is SPI",
     "reference": "§1798.140(ae)(10)", "severity": "high"},
    {"key": "email_text_content_controlled", "name": "Email/text content controlled",
     "detail_pass": "Email and text message content controlled",
     "detail_fail": "Contents of mail, email, text messages are SPI (unless intended recipient)",
     "reference": "§1798.140(ae)(7)", "severity": "medium"},
    {"key": "login_credentials_protected", "name": "Login credentials protected",
     "detail_pass": "Account login credentials protected",
     "detail_fail": "Username with password or security question/answer is SPI",
     "reference": "§1798.140(ae)(2)", "severity": "critical"},
    {"key": "genetic_data_controlled", "name": "Genetic data controlled",
     "detail_pass": "Genetic data controlled",
     "detail_fail": "Genetic data is SPI under CPRA",
     "reference": "§1798.140(ae)(6)", "severity": "high"},
    {"key": "spi_use_limited_to_disclosed_purposes", "name": "SPI use limited",
     "detail_pass": "SPI use limited to disclosed purposes",
     "detail_fail": "Must limit SPI use to purposes disclosed at collection or consumer-directed",
     "reference": "§1798.121(a)", "severity": "critical"},
    {"key": "spi_processing_minimized", "name": "SPI processing minimized",
     "detail_pass": "SPI processing minimized to what is necessary",
     "detail_fail": "Must minimize SPI processing to what is reasonably necessary",
     "reference": "§1798.100(c)", "severity": "high"}
]

TECHNICAL_SAFEGUARD_CHECKS = [
    {"key": "encryption_at_rest", "name": "Encryption at rest",
     "detail_pass": "PI encrypted at rest",
     "detail_fail": "Must implement reasonable security including encryption at rest",
     "reference": "§1798.150(a)(1)", "severity": "critical"},
    {"key": "encryption_in_transit", "name": "Encryption in transit",
     "detail_pass": "PI encrypted in transit",
     "detail_fail": "Must encrypt PI in transit (TLS/HTTPS)",
     "reference": "§1798.150(a)(1)", "severity": "critical"},
    {"key": "access_controls_implemented", "name": "Access controls",
     "detail_pass": "Access controls for PI implemented",
     "detail_fail": "Must implement access controls to limit PI access",
     "reference": "§1798.150(a)(1)", "severity": "critical"},
    {"key": "role_based_access", "name": "Role-based access",
     "detail_pass": "Role-based access control for PI",
     "detail_fail": "Should implement RBAC for PI access based on need-to-know",
     "reference": "Best practice", "severity": "high"},
    {"key": "mfa_for_pi_access", "name": "MFA for PI access",
     "detail_pass": "Multi-factor authentication for PI system access",
     "detail_fail": "Should require MFA for accessing PI systems",
     "reference": "Best practice", "severity": "medium"},
    {"key": "audit_logging", "name": "Audit logging",
     "detail_pass": "Audit logging for PI access and modifications",
     "detail_fail": "Should log access and modifications to PI for accountability",
     "reference": "Best practice", "severity": "high"},
    {"key": "data_loss_prevention", "name": "Data loss prevention",
     "detail_pass": "Data loss prevention measures in place",
     "detail_fail": "Should implement DLP to prevent unauthorized PI disclosure",
     "reference": "Best practice", "severity": "medium"},
    {"key": "incident_response_plan", "name": "Incident response plan",
     "detail_pass": "Incident response plan documented",
     "detail_fail": "Must have incident response plan for data breaches",
     "reference": "§1798.150", "severity": "critical"},
    {"key": "breach_notification_process", "name": "Breach notification",
     "detail_pass": "Breach notification process established",
     "detail_fail": "Must notify AG and consumers of breaches per Cal. Civ. Code §1798.82",
     "reference": "Cal. Civ. Code §1798.82", "severity": "critical"},
    {"key": "vulnerability_management", "name": "Vulnerability management",
     "detail_pass": "Vulnerability management program in place",
     "detail_fail": "Should implement vulnerability scanning and patching program",
     "reference": "Best practice", "severity": "high"},
    {"key": "penetration_testing", "name": "Penetration testing",
     "detail_pass": "Regular penetration testing conducted",
     "detail_fail": "Should conduct regular penetration testing of PI systems",
     "reference": "Best practice", "severity": "medium"},
    {"key": "security_awareness_training", "name": "Security training",
     "detail_pass": "Security awareness training for PI handlers",
     "detail_fail": "Should train staff on security practices for handling PI",
     "reference": "§1798.130(a)(6)", "severity": "high"},
    {"key": "vendor_security_assessments", "name": "Vendor security assessments",
     "detail_pass": "Vendor security assessments conducted",
     "detail_fail": "Should assess security practices of vendors processing PI",
     "reference": "Best practice", "severity": "medium"},
    {"key": "data_backup_and_recovery", "name": "Backup and recovery",
     "detail_pass": "Data backup and recovery procedures in place",
     "detail_fail": "Should implement backup and recovery for PI systems",
     "reference": "Best practice", "severity": "medium"}
]

SERVICE_PROVIDER_CHECKS = [
    {"key": "sp_agreements_in_place", "name": "SP agreements in place",
     "detail_pass": "Service provider agreements executed",
     "detail_fail": "Must have written agreements with all service providers",
     "reference": "§1798.140(ag)", "severity": "critical"},
    {"key": "agreements_restrict_pi_use", "name": "PI use restricted in agreements",
     "detail_pass": "Agreements restrict PI use to specified purposes",
     "detail_fail": "SP agreements must restrict PI use to contracted purposes",
     "reference": "§1798.140(ag)(1)(A)", "severity": "critical"},
    {"key": "agreements_require_deletion", "name": "Deletion clause",
     "detail_pass": "Agreements require PI deletion upon request or contract end",
     "detail_fail": "SP agreements must include PI deletion obligations",
     "reference": "§1798.105(c)", "severity": "high"},
    {"key": "agreements_allow_audits", "name": "Audit rights",
     "detail_pass": "Agreements include audit rights",
     "detail_fail": "Agreements should allow compliance audits of service providers",
     "reference": "Best practice / CPRA", "severity": "medium"},
    {"key": "contractor_agreements_in_place", "name": "Contractor agreements",
     "detail_pass": "Contractor agreements in place (CPRA)",
     "detail_fail": "Must have written agreements with contractors (CPRA distinction)",
     "reference": "§1798.140(j)", "severity": "high"},
    {"key": "contractor_certification_obtained", "name": "Contractor certification",
     "detail_pass": "Contractors certify understanding of CCPA obligations",
     "detail_fail": "Contractors must certify they understand and will comply with CCPA",
     "reference": "§1798.140(j)(1)", "severity": "high"},
    {"key": "third_party_data_sharing_documented", "name": "Third-party sharing documented",
     "detail_pass": "Third-party data sharing documented",
     "detail_fail": "Must document all third-party PI sharing arrangements",
     "reference": "§1798.115", "severity": "high"},
    {"key": "third_party_opt_out_honored", "name": "Third-party opt-out honored",
     "detail_pass": "Consumer opt-outs communicated to third parties",
     "detail_fail": "Must communicate opt-out requests to third parties receiving PI",
     "reference": "§1798.120(b)", "severity": "critical"},
    {"key": "data_processing_agreements", "name": "DPAs in place",
     "detail_pass": "Data processing agreements executed",
     "detail_fail": "Should have DPAs covering CCPA requirements",
     "reference": "Best practice", "severity": "medium"},
    {"key": "sp_security_requirements", "name": "SP security requirements",
     "detail_pass": "Security requirements specified for service providers",
     "detail_fail": "Agreements should specify security requirements for PI",
     "reference": "Best practice", "severity": "medium"},
    {"key": "sp_breach_notification_clause", "name": "SP breach notification",
     "detail_pass": "Breach notification clauses in SP agreements",
     "detail_fail": "SP agreements should require prompt breach notification",
     "reference": "Best practice", "severity": "high"},
    {"key": "subprocessor_management", "name": "Subprocessor management",
     "detail_pass": "Subprocessor management process in place",
     "detail_fail": "Should manage and approve subprocessors of service providers",
     "reference": "Best practice", "severity": "medium"}
]

RISK_ASSESSMENT_CHECKS = [
    {"key": "annual_cybersecurity_audit_planned", "name": "Annual cybersecurity audit",
     "detail_pass": "Annual cybersecurity audit planned or conducted",
     "detail_fail": "CPRA requires annual cybersecurity audits for significant risk processing",
     "reference": "§1798.185(a)(15)(B)", "severity": "high"},
    {"key": "risk_assessment_for_processing", "name": "Processing risk assessment",
     "detail_pass": "Risk assessments conducted for processing activities",
     "detail_fail": "CPRA requires risk assessments for processing that presents significant risk",
     "reference": "§1798.185(a)(15)(A)", "severity": "high"},
    {"key": "data_inventory_maintained", "name": "Data inventory",
     "detail_pass": "Comprehensive PI data inventory maintained",
     "detail_fail": "Must maintain inventory of all PI categories collected and processed",
     "reference": "§1798.100(a)", "severity": "critical"},
    {"key": "data_flow_mapping_current", "name": "Data flow mapping",
     "detail_pass": "Data flow mapping is current",
     "detail_fail": "Should map PI flows from collection through sharing/deletion",
     "reference": "Best practice", "severity": "high"},
    {"key": "retention_schedule_documented", "name": "Retention schedule",
     "detail_pass": "Data retention schedule documented",
     "detail_fail": "Must document retention periods; must not retain PI longer than necessary (CPRA)",
     "reference": "§1798.100(a)(3)", "severity": "high"},
    {"key": "cross_border_transfers_documented", "name": "Cross-border transfers",
     "detail_pass": "Cross-border data transfers documented",
     "detail_fail": "Should document cross-border PI transfers and safeguards",
     "reference": "Best practice", "severity": "medium"},
    {"key": "automated_decision_making_disclosed", "name": "Automated decisions disclosed",
     "detail_pass": "Automated decision-making technology disclosed",
     "detail_fail": "CPRA may require disclosure of automated decision-making use",
     "reference": "§1798.185(a)(16)", "severity": "medium"},
    {"key": "data_minimization_practiced", "name": "Data minimization",
     "detail_pass": "Data minimization practiced (CPRA)",
     "detail_fail": "Must not collect PI beyond what is reasonably necessary (CPRA)",
     "reference": "§1798.100(c)", "severity": "high"},
    {"key": "purpose_limitation_enforced", "name": "Purpose limitation",
     "detail_pass": "Purpose limitation enforced (CPRA)",
     "detail_fail": "Must not use PI for purposes incompatible with disclosed purposes (CPRA)",
     "reference": "§1798.100(c)", "severity": "high"}
]


def run_assessment(data: Dict) -> Dict:
    """Run full CCPA/CPRA compliance assessment."""
    results = {
        "assessment_date": datetime.now().isoformat(),
        "framework": "CCPA/CPRA",
        "organization": data.get("organization", {}).get("name", "Unknown"),
        "categories": {},
        "overall_score": 0.0,
        "overall_status": "",
        "summary": {
            "critical_findings": [],
            "high_findings": [],
            "recommendations": []
        }
    }

    # Run all category checks
    app_score, app_findings = check_applicability(data)
    results["categories"]["applicability"] = {
        "score": round(app_score, 1),
        "findings": app_findings
    }

    category_checks = [
        ("privacy_policy", "privacy_policy", PRIVACY_POLICY_CHECKS),
        ("consumer_rights", "consumer_rights", CONSUMER_RIGHTS_CHECKS),
        ("opt_out_mechanisms", "opt_out_mechanisms", OPT_OUT_CHECKS),
        ("sensitive_personal_information", "sensitive_personal_information", SPI_CHECKS),
        ("technical_safeguards", "technical_safeguards", TECHNICAL_SAFEGUARD_CHECKS),
        ("service_providers", "service_providers", SERVICE_PROVIDER_CHECKS),
        ("risk_assessments", "risk_assessments", RISK_ASSESSMENT_CHECKS)
    ]

    for cat_name, section_key, checks in category_checks:
        score, findings = check_boolean_section(data, section_key, checks)
        results["categories"][cat_name] = {
            "score": round(score, 1),
            "findings": findings
        }

    # Calculate weighted overall score
    total_weight = sum(CATEGORY_WEIGHTS.values())
    weighted_sum = 0
    for cat, weight in CATEGORY_WEIGHTS.items():
        cat_score = results["categories"].get(cat, {}).get("score", 0)
        weighted_sum += cat_score * weight
    results["overall_score"] = round(weighted_sum / total_weight, 1)

    # Determine status
    score = results["overall_score"]
    if score >= 90:
        results["overall_status"] = "Compliant"
    elif score >= 70:
        results["overall_status"] = "Substantially Compliant"
    elif score >= 50:
        results["overall_status"] = "Partially Compliant"
    else:
        results["overall_status"] = "Non-Compliant"

    # Collect critical and high findings
    for cat_name, cat_data in results["categories"].items():
        for finding in cat_data.get("findings", []):
            if finding["status"] == "fail":
                entry = {
                    "category": cat_name,
                    "check": finding["check"],
                    "detail": finding["detail"],
                    "reference": finding["reference"]
                }
                if finding.get("severity") == "critical":
                    results["summary"]["critical_findings"].append(entry)
                elif finding.get("severity") == "high":
                    results["summary"]["high_findings"].append(entry)

    # Generate recommendations
    if results["summary"]["critical_findings"]:
        results["summary"]["recommendations"].append(
            "Address all critical findings immediately — these represent direct "
            "regulatory violations exposing the organization to enforcement action "
            "($2,500-$7,500 per violation)."
        )
    if results["categories"].get("opt_out_mechanisms", {}).get("score", 0) < 50:
        results["summary"]["recommendations"].append(
            "Implement 'Do Not Sell or Share My Personal Information' and "
            "'Limit the Use of My Sensitive Personal Information' links on homepage."
        )
    if results["categories"].get("consumer_rights", {}).get("score", 0) < 70:
        results["summary"]["recommendations"].append(
            "Establish consumer rights request intake, verification, and "
            "fulfillment processes with 10-day acknowledgment and 45-day completion SLAs."
        )
    if results["categories"].get("privacy_policy", {}).get("score", 0) < 70:
        results["summary"]["recommendations"].append(
            "Update privacy policy to include all required CCPA/CPRA disclosures "
            "including PI categories, sources, purposes, and consumer rights."
        )
    if results["categories"].get("technical_safeguards", {}).get("score", 0) < 70:
        results["summary"]["recommendations"].append(
            "Implement reasonable security measures (encryption, access controls, "
            "incident response) to reduce private right of action exposure."
        )

    return results


def format_text_report(results: Dict) -> str:
    """Format results as human-readable text report."""
    lines = []
    lines.append("=" * 70)
    lines.append("CCPA/CPRA COMPLIANCE ASSESSMENT REPORT")
    lines.append("=" * 70)
    lines.append(f"Organization: {results['organization']}")
    lines.append(f"Assessment Date: {results['assessment_date']}")
    lines.append(f"Overall Score: {results['overall_score']}/100")
    lines.append(f"Status: {results['overall_status']}")
    lines.append("")

    # Category scores
    lines.append("-" * 70)
    lines.append("CATEGORY SCORES")
    lines.append("-" * 70)
    for cat_name, cat_data in results["categories"].items():
        display_name = cat_name.replace("_", " ").title()
        score = cat_data["score"]
        bar_len = int(score / 5)
        bar = "#" * bar_len + "." * (20 - bar_len)
        lines.append(f"  {display_name:<40} [{bar}] {score:>5.1f}")
    lines.append("")

    # Critical findings
    critical = results["summary"]["critical_findings"]
    if critical:
        lines.append("-" * 70)
        lines.append(f"CRITICAL FINDINGS ({len(critical)})")
        lines.append("-" * 70)
        for f in critical:
            lines.append(f"  [CRITICAL] {f['check']}")
            lines.append(f"    Category: {f['category'].replace('_', ' ').title()}")
            lines.append(f"    Detail:   {f['detail']}")
            lines.append(f"    Ref:      {f['reference']}")
            lines.append("")

    # High findings
    high = results["summary"]["high_findings"]
    if high:
        lines.append("-" * 70)
        lines.append(f"HIGH FINDINGS ({len(high)})")
        lines.append("-" * 70)
        for f in high:
            lines.append(f"  [HIGH] {f['check']}")
            lines.append(f"    Category: {f['category'].replace('_', ' ').title()}")
            lines.append(f"    Detail:   {f['detail']}")
            lines.append(f"    Ref:      {f['reference']}")
            lines.append("")

    # Recommendations
    recs = results["summary"]["recommendations"]
    if recs:
        lines.append("-" * 70)
        lines.append("RECOMMENDATIONS")
        lines.append("-" * 70)
        for i, rec in enumerate(recs, 1):
            lines.append(f"  {i}. {rec}")
        lines.append("")

    lines.append("=" * 70)
    lines.append("End of Report")
    lines.append("=" * 70)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="CCPA/CPRA Compliance Checker — evaluates organizational "
                    "readiness against California privacy law requirements."
    )
    parser.add_argument(
        "--input", "-i",
        help="Path to JSON file with organization compliance profile"
    )
    parser.add_argument(
        "--template", "-t",
        action="store_true",
        help="Output a blank compliance profile template (JSON)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Path to write the assessment report"
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output results as JSON (default is human-readable text)"
    )
    args = parser.parse_args()

    if args.template:
        print(json.dumps(TEMPLATE, indent=2))
        return

    if not args.input:
        parser.error("--input is required (or use --template to generate a blank profile)")

    try:
        with open(args.input, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {args.input}: {e}", file=sys.stderr)
        sys.exit(1)

    results = run_assessment(data)

    if args.json:
        output = json.dumps(results, indent=2)
    else:
        output = format_text_report(results)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Report written to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
