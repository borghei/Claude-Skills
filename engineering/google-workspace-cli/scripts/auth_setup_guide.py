#!/usr/bin/env python3
"""
Auth Setup Guide - Generate Google Workspace API authentication setup documentation.

Creates step-by-step setup guides for OAuth 2.0, service accounts, and
domain-wide delegation for Google Workspace API access.

Author: Claude Skills Engineering Team
License: MIT
"""

import argparse
import json
import sys
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional


API_SCOPES = {
    "admin": {
        "name": "Admin SDK Directory API",
        "scopes": [
            "https://www.googleapis.com/auth/admin.directory.user",
            "https://www.googleapis.com/auth/admin.directory.user.readonly",
            "https://www.googleapis.com/auth/admin.directory.group",
            "https://www.googleapis.com/auth/admin.directory.orgunit",
        ],
        "description": "Manage users, groups, and organizational units.",
    },
    "drive": {
        "name": "Google Drive API",
        "scopes": [
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/drive.readonly",
            "https://www.googleapis.com/auth/drive.file",
            "https://www.googleapis.com/auth/drive.metadata.readonly",
        ],
        "description": "Access and manage Google Drive files and folders.",
    },
    "gmail": {
        "name": "Gmail API",
        "scopes": [
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.send",
            "https://www.googleapis.com/auth/gmail.settings.basic",
            "https://www.googleapis.com/auth/gmail.labels",
        ],
        "description": "Read, send, and manage Gmail messages and settings.",
    },
    "calendar": {
        "name": "Google Calendar API",
        "scopes": [
            "https://www.googleapis.com/auth/calendar",
            "https://www.googleapis.com/auth/calendar.readonly",
            "https://www.googleapis.com/auth/calendar.events",
        ],
        "description": "Access and manage Google Calendar events.",
    },
    "sheets": {
        "name": "Google Sheets API",
        "scopes": [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/spreadsheets.readonly",
        ],
        "description": "Read and write Google Sheets data.",
    },
    "reports": {
        "name": "Admin Reports API",
        "scopes": [
            "https://www.googleapis.com/auth/admin.reports.audit.readonly",
            "https://www.googleapis.com/auth/admin.reports.usage.readonly",
        ],
        "description": "Access audit logs and usage reports.",
    },
}


@dataclass
class SetupStep:
    """A setup step."""
    number: int
    title: str
    instructions: List[str]
    notes: List[str]


def generate_oauth_guide(scope_keys: List[str], project_name: str) -> List[SetupStep]:
    """Generate OAuth 2.0 setup guide."""
    selected_scopes = []
    for key in scope_keys:
        if key in API_SCOPES:
            selected_scopes.extend(API_SCOPES[key]["scopes"])

    steps = [
        SetupStep(
            number=1,
            title="Create Google Cloud Project",
            instructions=[
                "Go to https://console.cloud.google.com/",
                "Click 'Select a project' > 'New Project'",
                f"Enter project name: '{project_name}'",
                "Click 'Create'",
                "Wait for project creation to complete",
            ],
            notes=["Use a descriptive name that identifies this integration."],
        ),
        SetupStep(
            number=2,
            title="Enable Required APIs",
            instructions=[
                "Go to APIs & Services > Library",
            ] + [f"Search for and enable: {API_SCOPES[k]['name']}" for k in scope_keys if k in API_SCOPES],
            notes=["Each API must be explicitly enabled before use."],
        ),
        SetupStep(
            number=3,
            title="Configure OAuth Consent Screen",
            instructions=[
                "Go to APIs & Services > OAuth consent screen",
                "Select 'Internal' (for Workspace users only) or 'External'",
                f"App name: '{project_name}'",
                "Add support email and developer contact",
                "Click 'Save and Continue'",
                "Add scopes:",
            ] + [f"  - {scope}" for scope in selected_scopes],
            notes=[
                "Internal type limits access to your organization only (recommended).",
                "External type requires verification for production use.",
            ],
        ),
        SetupStep(
            number=4,
            title="Create OAuth Client ID",
            instructions=[
                "Go to APIs & Services > Credentials",
                "Click '+ Create Credentials' > 'OAuth client ID'",
                "Application type: 'Desktop app' (for CLI) or 'Web application'",
                f"Name: '{project_name} OAuth Client'",
                "Click 'Create'",
                "Download the JSON credentials file",
                "Save as 'credentials.json' in your project directory",
            ],
            notes=[
                "IMPORTANT: Never commit credentials.json to version control.",
                "Add credentials.json to .gitignore immediately.",
            ],
        ),
        SetupStep(
            number=5,
            title="Test Authentication",
            instructions=[
                "Install the Google client library:",
                "  pip install google-auth google-auth-oauthlib google-api-python-client",
                "Run your first API call to trigger the OAuth flow",
                "Complete the browser-based authorization",
                "Token will be saved locally for future use",
            ],
            notes=["First run will open a browser for authorization."],
        ),
    ]

    return steps


def generate_service_account_guide(scope_keys: List[str], project_name: str,
                                     domain_delegation: bool = False) -> List[SetupStep]:
    """Generate service account setup guide."""
    selected_scopes = []
    for key in scope_keys:
        if key in API_SCOPES:
            selected_scopes.extend(API_SCOPES[key]["scopes"])

    steps = [
        SetupStep(
            number=1,
            title="Create Google Cloud Project",
            instructions=[
                "Go to https://console.cloud.google.com/",
                "Click 'Select a project' > 'New Project'",
                f"Enter project name: '{project_name}'",
                "Click 'Create'",
            ],
            notes=[],
        ),
        SetupStep(
            number=2,
            title="Enable Required APIs",
            instructions=[
                "Go to APIs & Services > Library",
            ] + [f"Enable: {API_SCOPES[k]['name']}" for k in scope_keys if k in API_SCOPES],
            notes=[],
        ),
        SetupStep(
            number=3,
            title="Create Service Account",
            instructions=[
                "Go to IAM & Admin > Service Accounts",
                "Click '+ Create Service Account'",
                f"Name: '{project_name}-service-account'",
                "Click 'Create and Continue'",
                "Grant role: 'Project > Editor' (or more restrictive)",
                "Click 'Continue' then 'Done'",
            ],
            notes=["Use the most restrictive role that satisfies your requirements."],
        ),
        SetupStep(
            number=4,
            title="Create Service Account Key",
            instructions=[
                "Click on the service account you just created",
                "Go to 'Keys' tab",
                "Click 'Add Key' > 'Create new key'",
                "Select JSON format",
                "Click 'Create'",
                "Save the downloaded JSON key file securely",
            ],
            notes=[
                "CRITICAL: This key grants full service account access. Store securely.",
                "Never commit key files to version control.",
                "Rotate keys regularly (every 90 days recommended).",
            ],
        ),
    ]

    if domain_delegation:
        steps.append(SetupStep(
            number=5,
            title="Configure Domain-Wide Delegation",
            instructions=[
                "Copy the service account's Client ID (numeric)",
                "Go to Google Workspace Admin Console > Security > API Controls",
                "Click 'Manage Domain Wide Delegation'",
                "Click 'Add New'",
                "Enter the Client ID",
                "Add the following OAuth scopes:",
            ] + [f"  {scope}" for scope in selected_scopes] + [
                "Click 'Authorize'",
            ],
            notes=[
                "Domain-wide delegation allows the service account to impersonate any user.",
                "Only grant the minimum scopes required.",
                "This requires super admin access to the Admin Console.",
            ],
        ))

        steps.append(SetupStep(
            number=6,
            title="Test Domain-Wide Delegation",
            instructions=[
                "Install dependencies:",
                "  pip install google-auth google-api-python-client",
                "Create a test script that impersonates a user:",
                "  from google.oauth2 import service_account",
                "  credentials = service_account.Credentials.from_service_account_file(",
                "      'key.json',",
                f"      scopes={selected_scopes[:2]},",
                "      subject='admin@yourdomain.com'",
                "  )",
                "Run the test script to verify delegation works",
            ],
            notes=["Replace 'admin@yourdomain.com' with a real user in your domain."],
        ))
    else:
        steps.append(SetupStep(
            number=5,
            title="Test Service Account",
            instructions=[
                "Install dependencies:",
                "  pip install google-auth google-api-python-client",
                "Test authentication with the key file",
                "Verify API calls succeed",
            ],
            notes=[],
        ))

    return steps


def format_text_guide(steps: List[SetupStep], method: str, scope_keys: List[str]) -> str:
    """Format guide as text."""
    lines = []
    lines.append("=" * 60)
    lines.append(f"GOOGLE WORKSPACE API SETUP GUIDE")
    lines.append(f"Method: {method.upper()}")
    lines.append("=" * 60)

    lines.append("\nRequired APIs and Scopes:")
    for key in scope_keys:
        if key in API_SCOPES:
            api = API_SCOPES[key]
            lines.append(f"\n  {api['name']}")
            lines.append(f"  {api['description']}")
            for scope in api["scopes"]:
                lines.append(f"    - {scope}")

    lines.append("\n" + "-" * 60)
    lines.append("SETUP STEPS")
    lines.append("-" * 60)

    for step in steps:
        lines.append(f"\n## Step {step.number}: {step.title}")
        for inst in step.instructions:
            lines.append(f"  {inst}")
        if step.notes:
            lines.append("")
            for note in step.notes:
                lines.append(f"  NOTE: {note}")

    lines.append("\n" + "=" * 60)
    return "\n".join(lines)


def format_json_guide(steps: List[SetupStep], method: str, scope_keys: List[str]) -> str:
    """Format guide as JSON."""
    apis = {}
    for key in scope_keys:
        if key in API_SCOPES:
            apis[key] = API_SCOPES[key]

    return json.dumps({
        "method": method,
        "apis": apis,
        "steps": [asdict(s) for s in steps],
        "total_steps": len(steps),
    }, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Generate Google Workspace API authentication setup documentation."
    )
    parser.add_argument("--method", choices=["oauth", "service-account"],
                       required=True, help="Authentication method")
    parser.add_argument("--scopes", required=True,
                       help="Comma-separated API scope keys: admin,drive,gmail,calendar,sheets,reports")
    parser.add_argument("--project", default="my-gws-integration",
                       help="Google Cloud project name")
    parser.add_argument("--domain-delegation", action="store_true",
                       help="Include domain-wide delegation setup (service-account only)")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument("--list-scopes", action="store_true", help="List available API scopes")
    args = parser.parse_args()

    if args.list_scopes:
        for key, api in API_SCOPES.items():
            print(f"\n{key}: {api['name']}")
            print(f"  {api['description']}")
            for scope in api["scopes"]:
                print(f"    {scope}")
        return

    scope_keys = [s.strip() for s in args.scopes.split(",")]
    invalid = [s for s in scope_keys if s not in API_SCOPES]
    if invalid:
        print(f"Error: Unknown scope keys: {', '.join(invalid)}", file=sys.stderr)
        print(f"Valid keys: {', '.join(API_SCOPES.keys())}", file=sys.stderr)
        sys.exit(2)

    if args.method == "oauth":
        steps = generate_oauth_guide(scope_keys, args.project)
    else:
        steps = generate_service_account_guide(scope_keys, args.project, args.domain_delegation)

    if args.format == "json":
        print(format_json_guide(steps, args.method, scope_keys))
    else:
        print(format_text_guide(steps, args.method, scope_keys))


if __name__ == "__main__":
    main()
