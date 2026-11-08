---
name: ms365-tenant-manager
description: >
  Generates reviewed PowerShell for Microsoft 365 admin: tenant setup and DNS, bulk
  provisioning, offboarding, Conditional Access and security audits. Use when setting up,
  hardening or auditing a tenant, or onboarding and offboarding users.
license: MIT + Commons Clause
metadata:
  version: 1.2.0
  author: borghei
  category: engineering
  domain: cloud-administration
  updated: 2026-11-08
  tags: [microsoft-365, azure-ad, office-365, administration]
---
# Microsoft 365 Tenant Manager

The agent produces reviewed, reversible PowerShell for Microsoft 365 administration: tenant setup plans and DNS records, bulk provisioning, secure offboarding, Conditional Access and 7-category security audits through Microsoft Graph and Exchange Online. The tools generate scripts from local inputs; they never connect to a tenant, so an administrator stays the one who runs every change.

## When to Use

- New tenant setup: phased checklist, DNS records and a baseline setup script.
- Security hardening: an audit first, then Conditional Access and MFA policies.
- Bulk user provisioning from a CSV, or offboarding a departing user.
- License planning by role, and quarterly utilization review.

## Clarify First

Before generating scripts, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Task:** setup, audit and hardening, provisioning, or offboarding (selects the subcommand).
- **Tenant inputs:** the domain, the users CSV, the tenant config JSON, and the break-glass account to exclude from Conditional Access.
- **Compliance regime:** GDPR, HIPAA or none (changes license recommendations and retention steps in offboarding).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Before Applying Any Script

These changes have real blast radius: a bad Conditional Access policy locks everyone out, and offboarding the wrong account cuts off a working employee.

1. **Read the generated script** and confirm the tenant, user and SKU values. The generator fills templates; it cannot see your tenant.
2. **Keep a break-glass account** (cloud-only, excluded from every CA policy, credentials offline). Without one, a policy mistake has no way back in.
3. **Report-only first.** CA policies are created as `enabledForReportingButNotEnforced`; check sign-in logs before enabling.
4. **Preview with `-WhatIf`** where the script supports it (offboarding), and run bulk jobs on a pilot group of two or three users first.
5. **Check legal hold and retention before offboarding.** Mailbox and OneDrive data are converted or archived, not exported; confirm the retention requirement with whoever owns it.
6. **Name the approver.** Write down who approved a tenant-wide change and when, so the audit log has an owner.

## Workflow

1. Gather inputs: domain, users CSV (`assets/sample_users.csv` shows the columns) or tenant config (`sample_input.json`).
2. Generate with `scripts/ms365_cli.py <subcommand> ... -o file.ps1`.
3. Validation checkpoint: `provision` validates every user and writes nothing if any row is invalid (exit 1); fix the CSV and rerun.
4. Apply the checklist above, then hand the script to the administrator to run.
5. Done when the audit script's reports show the intended state (for example zero users without MFA) and the change is recorded with its approver.

## Quick Start

```bash
# from engineering/ms365-tenant-manager/
python3 scripts/ms365_cli.py audit --domain contoso.com -o "$(mktemp -d)/audit.ps1"
python3 scripts/ms365_cli.py provision --domain contoso.com --users assets/sample_users.csv | head -40
python3 scripts/ms365_cli.py provision --domain contoso.com --users assets/flawed_users.csv   # exit 1, 2 invalid users
```

```bash
python3 scripts/ms365_cli.py conditional-access --domain contoso.com --exclude breakglass@contoso.com
python3 scripts/ms365_cli.py offboard --domain contoso.com --user ada.lovelace@contoso.com
python3 scripts/ms365_cli.py setup --config sample_input.json --part dns
python3 scripts/ms365_cli.py recommend-license --role "Finance Director" --department Finance --format json
```

## Tools Overview

| Tool | Purpose |
|------|---------|
| `scripts/ms365_cli.py` | CLI: `audit`, `conditional-access`, `bulk-license`, `provision`, `offboard`, `recommend-license`, `setup`. Writes to stdout or `-o FILE`; `--format json` for data subcommands. |
| `scripts/powershell_generator.py` | Library: audit, Conditional Access and bulk-license script templates (`PowerShellScriptGenerator`) |
| `scripts/user_management.py` | Library: provisioning, offboarding, license and group recommendations, user validation (`UserLifecycleManager`) |
| `scripts/tenant_setup.py` | Library: setup checklist, DNS records, setup script, license distribution (`TenantSetupManager`) |

**Exit codes (`ms365_cli.py`):** 0 output written; 1 `provision` found invalid users (no script written); 2 unusable input (missing file, bad JSON or CSV, invalid domain or user principal name). License prices are list prices baked into the module; check current Microsoft pricing before quoting them.

## Anti-Patterns

**Mistake:** Enforcing a Conditional Access policy on day one.
**Why it matters:** A policy that blocks legitimate sign-ins takes the whole company offline, admins included.
**Instead:** Create it report-only, review a week of sign-in logs, exclude the break-glass account, then enable.

**Mistake:** Running bulk provisioning or license scripts against everyone at once.
**Why it matters:** One wrong column or SKU repeats across hundreds of accounts and is slow to unwind.
**Instead:** Validate the CSV (the CLI refuses invalid rows), run a pilot of two or three users, then the rest.

**Mistake:** Deleting a departing user's account on their last day.
**Why it matters:** Deletion starts the clock on mailbox and OneDrive data and can breach retention or legal-hold duties.
**Instead:** Disable sign-in, revoke sessions, convert the mailbox to shared and keep the account until the retention owner signs off.

## Reference Documentation

- **[references/tools-and-workflows.md](references/tools-and-workflows.md)**: CLI reference, the three end-to-end workflows (setup, hardening, offboarding) and the Python module API. Read when running the tools.
- **[references/operations-and-best-practices.md](references/operations-and-best-practices.md)**: best practices, required modules and roles, troubleshooting and success criteria. Read before hardening a tenant.
- **[references/powershell-templates.md](references/powershell-templates.md)**: hand-written Conditional Access, provisioning and audit templates.
- **[references/security-policies.md](references/security-policies.md)**: Conditional Access design, MFA rollout, DLP and retention, security baseline.
- **[references/troubleshooting.md](references/troubleshooting.md)**: module, permission and DNS propagation problems.

## Files

| File | Purpose |
|------|---------|
| `scripts/ms365_cli.py` | Command-line entry point (stdlib only) |
| `scripts/powershell_generator.py`, `scripts/user_management.py`, `scripts/tenant_setup.py` | Template libraries the CLI imports |
| `sample_input.json` | Tenant config for `setup` (Acme, 75 users, GDPR) |
| `expected_output.json` | Example structured output for the sample config |
| `assets/sample_users.csv` | Three valid users; `provision` writes a script |
| `assets/flawed_users.csv` | Username with spaces, missing first name; `provision` exits 1 |

## Scope & Limitations

**Covers:** tenant setup planning and DNS, user lifecycle (provisioning, offboarding, license and group recommendations), Conditional Access and MFA scripts, security audits, all through Microsoft Graph and Exchange Online PowerShell.

**Does not cover:**
- Hybrid identity (Microsoft Entra Connect sync, pass-through authentication).
- Intune device management and Power Platform governance.
- Third-party SSO and SCIM (Okta, Ping, Auth0).
- Running anything against a tenant: the scripts are generated for an administrator to review and run.
