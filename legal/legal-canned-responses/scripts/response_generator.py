#!/usr/bin/env python3
"""
Legal Canned Response Generator

Generates templated responses for common legal inquiries with variable
substitution and escalation detection.

Usage:
    python response_generator.py --category dsr --sub-type acknowledgment --var requestor_name="Jane Doe"
    python response_generator.py --category nda --sub-type standard-form --var counterparty="Acme Corp" --json
    python response_generator.py --category discovery --sub-type initial-notice --var matter_name="Smith v. Corp"
"""

import argparse
import json
import re
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


# Template definitions: category -> sub-type -> {subject, body, variables, follow_up, privileged}
TEMPLATES: Dict[str, Dict[str, Dict[str, Any]]] = {
    "dsr": {
        "acknowledgment": {
            "subject": "Acknowledgment of Your Data Subject Request",
            "body": (
                "Dear {requestor_name},\n\n"
                "We acknowledge receipt of your data subject request submitted on {request_date}. "
                "Your request for {request_type} has been logged and assigned reference number {ref_number}.\n\n"
                "We will respond to your request within the timeframe required by applicable data "
                "protection law (generally 30 days from receipt). If we require additional time, "
                "we will notify you of any extension and the reasons for it.\n\n"
                "Before we can process your request, we may need to verify your identity. If so, "
                "we will contact you with further instructions.\n\n"
                "If you have questions about the status of your request, please reference {ref_number} "
                "in any correspondence.\n\n"
                "Regards,\n{sender_name}\n{sender_title}"
            ),
            "variables": ["requestor_name", "request_date", "request_type", "ref_number",
                          "sender_name", "sender_title"],
            "follow_up": ["Verify identity within 5 business days", "Set 30-day response deadline"],
            "privileged": False,
        },
        "verification": {
            "subject": "Identity Verification Required for Your Data Subject Request",
            "body": (
                "Dear {requestor_name},\n\n"
                "Thank you for your data subject request (Reference: {ref_number}). "
                "Before we can process your request, we are required to verify your identity.\n\n"
                "Please provide the following:\n"
                "- {verification_method}\n\n"
                "Please submit your verification documents within 14 days. "
                "The response timeline for your request will be paused until identity verification "
                "is complete.\n\n"
                "Regards,\n{sender_name}\n{sender_title}"
            ),
            "variables": ["requestor_name", "ref_number", "verification_method",
                          "sender_name", "sender_title"],
            "follow_up": ["Track verification deadline (14 days)", "Resume timeline upon verification"],
            "privileged": False,
        },
        "fulfillment": {
            "subject": "Response to Your Data Subject Request",
            "body": (
                "Dear {requestor_name},\n\n"
                "We have completed processing your {request_type} request (Reference: {ref_number}).\n\n"
                "{data_description}\n\n"
                "If you believe this response is incomplete or inaccurate, you have the right to "
                "submit a complaint to the relevant supervisory authority.\n\n"
                "Regards,\n{sender_name}\n{sender_title}"
            ),
            "variables": ["requestor_name", "request_type", "ref_number", "data_description",
                          "sender_name", "sender_title"],
            "follow_up": ["Close request in tracking system", "Archive response for audit trail"],
            "privileged": False,
        },
        "denial": {
            "subject": "Response to Your Data Subject Request",
            "body": (
                "Dear {requestor_name},\n\n"
                "We have reviewed your {request_type} request (Reference: {ref_number}). "
                "After careful consideration, we are unable to fulfill your request for the "
                "following reason:\n\n{denial_reason}\n\n"
                "You have the right to submit a complaint to the relevant supervisory authority "
                "if you disagree with this decision.\n\n"
                "Regards,\n{sender_name}\n{sender_title}"
            ),
            "variables": ["requestor_name", "request_type", "ref_number", "denial_reason",
                          "sender_name", "sender_title"],
            "follow_up": ["Document denial rationale", "Prepare for potential complaint"],
            "privileged": False,
        },
        "extension": {
            "subject": "Extension Notice for Your Data Subject Request",
            "body": (
                "Dear {requestor_name},\n\n"
                "We are writing regarding your {request_type} request (Reference: {ref_number}). "
                "Due to {extension_reason}, we require additional time to complete your request.\n\n"
                "We will provide a full response by {new_deadline}.\n\n"
                "We apologize for any inconvenience.\n\n"
                "Regards,\n{sender_name}\n{sender_title}"
            ),
            "variables": ["requestor_name", "request_type", "ref_number", "extension_reason",
                          "new_deadline", "sender_name", "sender_title"],
            "follow_up": ["Update tracking system deadline", "Set reminder for new deadline"],
            "privileged": False,
        },
    },
    "discovery": {
        "initial-notice": {
            "subject": "LITIGATION HOLD NOTICE - {matter_name}",
            "body": (
                "PRIVILEGED AND CONFIDENTIAL\n"
                "ATTORNEY-CLIENT COMMUNICATION\n\n"
                "TO: {custodians}\n"
                "RE: Litigation Hold - {matter_name}\n"
                "DATE: {notice_date}\n\n"
                "This notice requires you to preserve all documents, communications, and data "
                "related to {matter_name}. This includes:\n\n"
                "- Emails, text messages, and instant messages\n"
                "- Documents, spreadsheets, and presentations\n"
                "- Calendar entries and meeting notes\n"
                "- Voicemails and call logs\n"
                "- Any other electronically stored information (ESI)\n\n"
                "Relevant data types: {data_types}\n\n"
                "YOU MUST:\n"
                "1. Immediately cease any routine deletion of potentially relevant documents\n"
                "2. Suspend auto-delete policies for relevant systems\n"
                "3. Preserve all relevant documents in their current form\n"
                "4. Notify your team members who may have relevant information\n\n"
                "DO NOT delete, modify, or move any potentially relevant documents. "
                "Failure to comply may result in serious legal consequences.\n\n"
                "Contact {sender_name} with questions.\n\n"
                "{sender_name}\n{sender_title}"
            ),
            "variables": ["matter_name", "custodians", "notice_date", "data_types",
                          "sender_name", "sender_title"],
            "follow_up": ["Track custodian acknowledgments", "Set 7-day reminder follow-up",
                          "Document preservation scope"],
            "privileged": True,
        },
        "reminder": {
            "subject": "LITIGATION HOLD REMINDER #{reminder_number} - {matter_name}",
            "body": (
                "PRIVILEGED AND CONFIDENTIAL\n\n"
                "This is reminder #{reminder_number} regarding the litigation hold for {matter_name}.\n\n"
                "Your obligation to preserve all relevant documents, communications, and data "
                "remains in effect. Please confirm your continued compliance by replying to this "
                "message.\n\n"
                "If you have discovered additional relevant information since the last notice, "
                "please contact {sender_name} immediately.\n\n"
                "{sender_name}\n{sender_title}"
            ),
            "variables": ["matter_name", "reminder_number", "sender_name", "sender_title"],
            "follow_up": ["Log reminder sent", "Track acknowledgments", "Schedule next reminder"],
            "privileged": True,
        },
        "modification": {
            "subject": "LITIGATION HOLD MODIFICATION - {matter_name}",
            "body": (
                "PRIVILEGED AND CONFIDENTIAL\n\n"
                "The scope of the litigation hold for {matter_name} has been modified as follows:\n\n"
                "{modification_description}\n\n"
                "All other terms of the original hold notice remain in effect. "
                "Please confirm your understanding of this modification.\n\n"
                "{sender_name}\n{sender_title}"
            ),
            "variables": ["matter_name", "modification_description", "sender_name", "sender_title"],
            "follow_up": ["Update hold scope documentation", "Track custodian acknowledgments"],
            "privileged": True,
        },
        "release": {
            "subject": "LITIGATION HOLD RELEASE - {matter_name}",
            "body": (
                "PRIVILEGED AND CONFIDENTIAL\n\n"
                "The litigation hold for {matter_name} is hereby released effective {release_date}.\n\n"
                "You may resume normal document retention and deletion policies for materials "
                "that were subject to this hold. However, do not delete any documents that may "
                "be subject to other active holds or retention policies.\n\n"
                "{sender_name}\n{sender_title}"
            ),
            "variables": ["matter_name", "release_date", "sender_name", "sender_title"],
            "follow_up": ["Close hold in tracking system", "Resume normal retention policies"],
            "privileged": True,
        },
    },
    "privacy": {
        "cookies": {
            "subject": "Re: Cookie Policy Inquiry",
            "body": (
                "Dear {requestor_name},\n\n"
                "Thank you for your inquiry about our cookie practices.\n\n"
                "Our website uses cookies as described in our Cookie Policy. "
                "You can manage your cookie preferences at any time through our consent "
                "management platform available on our website.\n\n"
                "For more information, please visit: {cookie_policy_url}\n\n"
                "Regards,\n{sender_name}\n{sender_title}"
            ),
            "variables": ["requestor_name", "cookie_policy_url", "sender_name", "sender_title"],
            "follow_up": ["Log inquiry for privacy metrics"],
            "privileged": False,
        },
        "data-sharing": {
            "subject": "Re: Data Sharing Inquiry",
            "body": (
                "Dear {requestor_name},\n\n"
                "Thank you for your question about our data sharing practices.\n\n"
                "We share personal data only as described in our Privacy Notice and "
                "in accordance with applicable data protection laws. {sharing_details}\n\n"
                "For complete details, please review our Privacy Notice: {privacy_notice_url}\n\n"
                "Regards,\n{sender_name}\n{sender_title}"
            ),
            "variables": ["requestor_name", "sharing_details", "privacy_notice_url",
                          "sender_name", "sender_title"],
            "follow_up": ["Log inquiry", "Review if inquiry suggests process gap"],
            "privileged": False,
        },
        "children": {
            "subject": "Re: Children's Privacy Inquiry",
            "body": (
                "Dear {requestor_name},\n\n"
                "Thank you for your concern regarding children's privacy.\n\n"
                "Our services are not directed at children under {age_threshold}. "
                "We do not knowingly collect personal data from children. "
                "If you believe a child's data has been collected, please contact us "
                "immediately at {privacy_email} so we can investigate and take appropriate action.\n\n"
                "Regards,\n{sender_name}\n{sender_title}"
            ),
            "variables": ["requestor_name", "age_threshold", "privacy_email",
                          "sender_name", "sender_title"],
            "follow_up": ["Investigate if specific child data concern raised", "Log inquiry"],
            "privileged": False,
        },
        "transfers": {
            "subject": "Re: International Data Transfer Inquiry",
            "body": (
                "Dear {requestor_name},\n\n"
                "Thank you for your inquiry about international data transfers.\n\n"
                "When we transfer personal data outside {origin_jurisdiction}, we implement "
                "appropriate safeguards including {transfer_mechanism}. "
                "These measures ensure your data receives an adequate level of protection.\n\n"
                "Regards,\n{sender_name}\n{sender_title}"
            ),
            "variables": ["requestor_name", "origin_jurisdiction", "transfer_mechanism",
                          "sender_name", "sender_title"],
            "follow_up": ["Log inquiry", "Verify transfer mechanisms are current"],
            "privileged": False,
        },
    },
    "vendor": {
        "contract-status": {
            "subject": "Re: Contract Status Inquiry - {vendor_name}",
            "body": (
                "Dear {requestor_name},\n\n"
                "Regarding your inquiry about the contract with {vendor_name}:\n\n"
                "Contract Status: {contract_status}\n"
                "Contract Reference: {contract_ref}\n\n"
                "{additional_details}\n\n"
                "Regards,\n{sender_name}\n{sender_title}"
            ),
            "variables": ["requestor_name", "vendor_name", "contract_status", "contract_ref",
                          "additional_details", "sender_name", "sender_title"],
            "follow_up": ["Update contract tracking system if needed"],
            "privileged": False,
        },
        "amendments": {
            "subject": "Re: Contract Amendment Request - {vendor_name}",
            "body": (
                "Dear {requestor_name},\n\n"
                "We have received your request to amend the agreement with {vendor_name} "
                "(Reference: {contract_ref}).\n\n"
                "Proposed amendment: {amendment_description}\n\n"
                "This request is under review by our legal team. We will provide an update "
                "within {review_timeline}.\n\n"
                "Regards,\n{sender_name}\n{sender_title}"
            ),
            "variables": ["requestor_name", "vendor_name", "contract_ref",
                          "amendment_description", "review_timeline", "sender_name", "sender_title"],
            "follow_up": ["Assign to contract attorney", "Set review deadline"],
            "privileged": False,
        },
        "certifications": {
            "subject": "Re: Vendor Certification Request - {vendor_name}",
            "body": (
                "Dear {requestor_name},\n\n"
                "Regarding the certification request for {vendor_name}:\n\n"
                "{certification_details}\n\n"
                "Please submit the required documentation to {submission_email} "
                "by {deadline}.\n\n"
                "Regards,\n{sender_name}\n{sender_title}"
            ),
            "variables": ["requestor_name", "vendor_name", "certification_details",
                          "submission_email", "deadline", "sender_name", "sender_title"],
            "follow_up": ["Track submission deadline", "Verify certifications upon receipt"],
            "privileged": False,
        },
        "audit": {
            "subject": "Re: Vendor Audit Request - {vendor_name}",
            "body": (
                "Dear {requestor_name},\n\n"
                "We are scheduling an audit of {vendor_name} in accordance with our "
                "contractual audit rights (Reference: {contract_ref}).\n\n"
                "Audit scope: {audit_scope}\n"
                "Proposed dates: {audit_dates}\n\n"
                "Please confirm availability and prepare relevant documentation.\n\n"
                "Regards,\n{sender_name}\n{sender_title}"
            ),
            "variables": ["requestor_name", "vendor_name", "contract_ref", "audit_scope",
                          "audit_dates", "sender_name", "sender_title"],
            "follow_up": ["Confirm audit dates", "Prepare audit checklist"],
            "privileged": False,
        },
    },
    "nda": {
        "standard-form": {
            "subject": "Non-Disclosure Agreement - {counterparty}",
            "body": (
                "Dear {requestor_name},\n\n"
                "Please find attached our standard form Non-Disclosure Agreement for execution "
                "in connection with {purpose}.\n\n"
                "NDA Type: {nda_type}\n"
                "Counterparty: {counterparty}\n"
                "Term: {term}\n\n"
                "Please review, sign, and return at your earliest convenience. "
                "If you have questions or require modifications, please contact us.\n\n"
                "Regards,\n{sender_name}\n{sender_title}"
            ),
            "variables": ["requestor_name", "counterparty", "purpose", "nda_type", "term",
                          "sender_name", "sender_title"],
            "follow_up": ["Track NDA execution", "Set signature deadline"],
            "privileged": False,
        },
        "counterparty-markup": {
            "subject": "Re: NDA Markup Review - {counterparty}",
            "body": (
                "Dear {requestor_name},\n\n"
                "We have reviewed the markup provided by {counterparty} to our NDA. "
                "Our comments are as follows:\n\n"
                "{markup_comments}\n\n"
                "Please advise on next steps.\n\n"
                "Regards,\n{sender_name}\n{sender_title}"
            ),
            "variables": ["requestor_name", "counterparty", "markup_comments",
                          "sender_name", "sender_title"],
            "follow_up": ["Schedule negotiation call if needed", "Track markup versions"],
            "privileged": False,
        },
        "decline": {
            "subject": "Re: NDA Request - {counterparty}",
            "body": (
                "Dear {requestor_name},\n\n"
                "After review, we are unable to enter into an NDA with {counterparty} "
                "at this time. {decline_reason}\n\n"
                "Regards,\n{sender_name}\n{sender_title}"
            ),
            "variables": ["requestor_name", "counterparty", "decline_reason",
                          "sender_name", "sender_title"],
            "follow_up": ["Document decline reason", "Notify business stakeholder"],
            "privileged": False,
        },
        "renewal": {
            "subject": "NDA Renewal Notice - {counterparty}",
            "body": (
                "Dear {requestor_name},\n\n"
                "The NDA with {counterparty} (Reference: {nda_ref}) is approaching its "
                "expiration date of {expiry_date}.\n\n"
                "Please confirm whether renewal is required. If so, we will prepare "
                "the renewal documentation.\n\n"
                "Regards,\n{sender_name}\n{sender_title}"
            ),
            "variables": ["requestor_name", "counterparty", "nda_ref", "expiry_date",
                          "sender_name", "sender_title"],
            "follow_up": ["Track renewal decision", "Set expiry reminder"],
            "privileged": False,
        },
    },
    "subpoena": {
        "acknowledgment": {
            "subject": "FOR COUNSEL REVIEW - Subpoena Acknowledgment - {matter_name}",
            "body": (
                "FOR COUNSEL REVIEW ONLY\n\n"
                "Dear {requestor_name},\n\n"
                "We acknowledge receipt of the subpoena related to {matter_name} "
                "served on {service_date}.\n\n"
                "Response deadline: {response_deadline}\n"
                "Issuing party: {issuing_party}\n\n"
                "This matter has been referred to legal counsel for review.\n\n"
                "Regards,\n{sender_name}\n{sender_title}"
            ),
            "variables": ["requestor_name", "matter_name", "service_date",
                          "response_deadline", "issuing_party", "sender_name", "sender_title"],
            "follow_up": ["IMMEDIATE: Route to counsel", "Calendar response deadline",
                          "Identify responsive documents"],
            "privileged": True,
        },
        "objection": {
            "subject": "FOR COUNSEL REVIEW - Objection to Subpoena - {matter_name}",
            "body": (
                "FOR COUNSEL REVIEW ONLY\n\n"
                "The following objections are raised to the subpoena in {matter_name}:\n\n"
                "{objection_grounds}\n\n"
                "This response must be reviewed and approved by counsel before submission.\n\n"
                "{sender_name}\n{sender_title}"
            ),
            "variables": ["matter_name", "objection_grounds", "sender_name", "sender_title"],
            "follow_up": ["Counsel review required", "File objection by deadline"],
            "privileged": True,
        },
        "extension": {
            "subject": "FOR COUNSEL REVIEW - Extension Request - {matter_name}",
            "body": (
                "FOR COUNSEL REVIEW ONLY\n\n"
                "We respectfully request an extension of time to respond to the subpoena "
                "in {matter_name}.\n\n"
                "Current deadline: {current_deadline}\n"
                "Requested deadline: {requested_deadline}\n"
                "Reason: {extension_reason}\n\n"
                "{sender_name}\n{sender_title}"
            ),
            "variables": ["matter_name", "current_deadline", "requested_deadline",
                          "extension_reason", "sender_name", "sender_title"],
            "follow_up": ["Counsel approval required", "Track extension response"],
            "privileged": True,
        },
        "compliance": {
            "subject": "FOR COUNSEL REVIEW - Subpoena Compliance - {matter_name}",
            "body": (
                "FOR COUNSEL REVIEW ONLY\n\n"
                "The following responsive documents are prepared for production in "
                "response to the subpoena in {matter_name}:\n\n"
                "{production_summary}\n\n"
                "Privilege review status: {privilege_status}\n\n"
                "This production must be reviewed and approved by counsel before submission.\n\n"
                "{sender_name}\n{sender_title}"
            ),
            "variables": ["matter_name", "production_summary", "privilege_status",
                          "sender_name", "sender_title"],
            "follow_up": ["Counsel approval required", "Prepare privilege log if applicable"],
            "privileged": True,
        },
    },
    "insurance": {
        "initial-claim": {
            "subject": "Insurance Claim Notification - {claim_type}",
            "body": (
                "Dear {requestor_name},\n\n"
                "This notice is to inform our insurance carrier of a potential claim.\n\n"
                "Claim Type: {claim_type}\n"
                "Date of Occurrence: {occurrence_date}\n"
                "Description: {claim_description}\n"
                "Policy Number: {policy_number}\n\n"
                "We will provide additional information as it becomes available.\n\n"
                "Regards,\n{sender_name}\n{sender_title}"
            ),
            "variables": ["requestor_name", "claim_type", "occurrence_date",
                          "claim_description", "policy_number", "sender_name", "sender_title"],
            "follow_up": ["Track claim acknowledgment", "Gather supporting documentation"],
            "privileged": False,
        },
        "supplemental-info": {
            "subject": "Supplemental Information - Claim #{claim_number}",
            "body": (
                "Dear {requestor_name},\n\n"
                "Please find below supplemental information regarding Claim #{claim_number}:\n\n"
                "{supplemental_details}\n\n"
                "Please confirm receipt and advise if additional information is needed.\n\n"
                "Regards,\n{sender_name}\n{sender_title}"
            ),
            "variables": ["requestor_name", "claim_number", "supplemental_details",
                          "sender_name", "sender_title"],
            "follow_up": ["Log supplemental submission", "Track carrier response"],
            "privileged": False,
        },
        "reservation-of-rights": {
            "subject": "Re: Reservation of Rights - Claim #{claim_number}",
            "body": (
                "Dear {requestor_name},\n\n"
                "We acknowledge receipt of the reservation of rights letter for "
                "Claim #{claim_number} dated {ror_date}.\n\n"
                "We have noted the carrier's position and will respond as appropriate. "
                "This matter has been referred to counsel for review.\n\n"
                "Regards,\n{sender_name}\n{sender_title}"
            ),
            "variables": ["requestor_name", "claim_number", "ror_date",
                          "sender_name", "sender_title"],
            "follow_up": ["Route to counsel immediately", "Review coverage position"],
            "privileged": False,
        },
    },
}

# Default variable values
DEFAULTS: Dict[str, str] = {
    "ref_number": "[REF-XXXX]",
    "sender_name": "[SENDER NAME]",
    "sender_title": "[SENDER TITLE]",
    "notice_date": datetime.now().strftime("%Y-%m-%d"),
    "nda_type": "Mutual",
    "term": "2 years",
    "age_threshold": "13",
    "review_timeline": "10 business days",
}


def get_template(category: str, sub_type: str) -> Optional[Dict[str, Any]]:
    """Retrieve template by category and sub-type."""
    cat_templates = TEMPLATES.get(category)
    if not cat_templates:
        return None
    return cat_templates.get(sub_type)


def substitute_variables(text: str, variables: Dict[str, str]) -> Tuple[str, List[str]]:
    """Substitute variables in template text. Returns (text, missing_vars)."""
    missing = []
    pattern = re.compile(r'\{(\w+)\}')
    found_vars = pattern.findall(text)

    for var in found_vars:
        if var in variables:
            text = text.replace(f"{{{var}}}", variables[var])
        elif var in DEFAULTS:
            text = text.replace(f"{{{var}}}", DEFAULTS[var])
        else:
            missing.append(var)
            text = text.replace(f"{{{var}}}", f"[{var.upper().replace('_', ' ')}]")

    return text, missing


def generate_response(category: str, sub_type: str,
                      variables: Dict[str, str]) -> Dict[str, Any]:
    """Generate a response from template with variables."""
    template = get_template(category, sub_type)
    if not template:
        available = list(TEMPLATES.get(category, {}).keys()) if category in TEMPLATES else []
        return {
            "error": True,
            "message": f"Template not found: {category}/{sub_type}",
            "available_sub_types": available,
            "available_categories": list(TEMPLATES.keys()),
        }

    subject, subj_missing = substitute_variables(template["subject"], variables)
    body, body_missing = substitute_variables(template["body"], variables)
    all_missing = list(set(subj_missing + body_missing))

    return {
        "error": False,
        "generated_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "category": category,
        "sub_type": sub_type,
        "privileged": template.get("privileged", False),
        "subject": subject,
        "body": body,
        "follow_up_actions": template.get("follow_up", []),
        "required_variables": template.get("variables", []),
        "missing_variables": all_missing,
        "escalation_note": "ALWAYS ESCALATE" if category == "subpoena" else None,
    }


def format_text(result: Dict[str, Any]) -> str:
    """Format response as human-readable text."""
    if result.get("error"):
        lines = [f"ERROR: {result['message']}"]
        if result.get("available_categories"):
            lines.append(f"Available categories: {', '.join(result['available_categories'])}")
        if result.get("available_sub_types"):
            lines.append(f"Available sub-types: {', '.join(result['available_sub_types'])}")
        return "\n".join(lines)

    lines = []
    lines.append("=" * 70)
    lines.append("GENERATED LEGAL RESPONSE")
    lines.append("=" * 70)
    lines.append(f"Category:  {result['category']}")
    lines.append(f"Sub-Type:  {result['sub_type']}")
    lines.append(f"Date:      {result['generated_date']}")
    if result.get("privileged"):
        lines.append("Status:    PRIVILEGED AND CONFIDENTIAL")
    if result.get("escalation_note"):
        lines.append(f"WARNING:   {result['escalation_note']}")
    lines.append("")
    lines.append(f"Subject: {result['subject']}")
    lines.append("-" * 70)
    lines.append(result["body"])
    lines.append("-" * 70)

    if result.get("missing_variables"):
        lines.append("")
        lines.append(f"MISSING VARIABLES: {', '.join(result['missing_variables'])}")
        lines.append("(Shown as [PLACEHOLDER] in response)")

    if result.get("follow_up_actions"):
        lines.append("")
        lines.append("FOLLOW-UP ACTIONS:")
        for action in result["follow_up_actions"]:
            lines.append(f"  - {action}")

    lines.append("")
    lines.append("=" * 70)
    return "\n".join(lines)


def parse_var(var_str: str) -> Tuple[str, str]:
    """Parse a KEY=VALUE variable string."""
    if "=" not in var_str:
        return var_str, ""
    key, value = var_str.split("=", 1)
    return key.strip(), value.strip()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate templated responses for common legal inquiries."
    )
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--category", required=True,
                        choices=list(TEMPLATES.keys()),
                        help="Response category")
    parser.add_argument("--sub-type", required=True,
                        help="Response sub-type within category")
    parser.add_argument("--var", action="append", default=[],
                        help="Variable substitution as KEY=VALUE (repeatable)")

    args = parser.parse_args()

    try:
        variables = dict(parse_var(v) for v in args.var)
        result = generate_response(args.category, args.sub_type, variables)

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(format_text(result))

        if result.get("error"):
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
