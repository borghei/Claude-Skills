---
name: ms365-tenant-manager
description: >
  Microsoft 365 tenant administration for Global Administrators. Use for tenant setup, Azure
  AD user management, Exchange Online and Teams config, Conditional Access policies, license
  management, and PowerShell bulk-operation scripts.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: cloud-administration
  updated: 2026-06-17
  tags: [microsoft-365, azure-ad, office-365, administration]
---
# Microsoft 365 Tenant Manager

The agent generates production-ready PowerShell scripts for M365 tenant setup, bulk user provisioning, Conditional Access policies, security audits, and license management. It automates user lifecycle operations (onboarding, offboarding), recommends license SKUs by role, and produces 7-category security audit reports via Microsoft Graph.

## Core Capabilities

- **Tenant lifecycle** — setup checklists, domain verification, DNS record generation, security baseline, and PowerShell setup scripts for Exchange, SharePoint, Teams.
- **User lifecycle automation** — bulk provisioning from CSV, secure 11-step offboarding, license recommendations by role/department, group membership suggestions, data validation.
- **Security & compliance** — Conditional Access policy generation (report-only first), MFA enforcement, and 7-category security audits (MFA, admin roles, inactive users, guests, licenses, mailbox delegations, CA policies).
- **License management** — SKU recommendations and distribution/cost estimates adjusted for GDPR/HIPAA compliance requirements.
- **PowerShell generation** — Microsoft Graph-based scripts with error handling, logging, and `-WhatIf` support.

## When to Use

- New tenant setup — generate phased checklist, DNS records, and baseline scripts.
- Security hardening — run audits and stand up Conditional Access / MFA policies.
- Bulk user provisioning or secure offboarding.
- License planning and quarterly utilization review.

## Clarify First

Before generating scripts, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Task** — tenant setup, security audit/hardening, bulk provisioning, or offboarding (selects `tenant_setup.py` vs `powershell_generator.py` vs `user_management.py`)
- [ ] **Tenant inputs** — the domain, the user CSV, or the role/department data (the input the modules consume)
- [ ] **Compliance regime** — GDPR/HIPAA or none (adjusts license SKU recommendations and the security baseline)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

The scripts are importable Python modules (instantiate a class, not a CLI). Full API, parameters, and worked examples are in [references/tools-and-workflows.md](references/tools-and-workflows.md).

| Tool | Purpose | Entry point |
|------|---------|-------------|
| `powershell_generator.py` | Security audit, Conditional Access, and bulk license scripts | `from powershell_generator import PowerShellScriptGenerator` |
| `user_management.py` | Provisioning, offboarding, license/group recommendations, validation | `from user_management import UserLifecycleManager` |
| `tenant_setup.py` | Setup checklist, DNS records, setup script, license distribution | `from tenant_setup import TenantSetupManager` |

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/tools-and-workflows.md](references/tools-and-workflows.md)** — Quick Start commands, per-tool usage/parameters, the 3 end-to-end workflows (setup, hardening, offboarding), and the full Python module API for all three scripts. Read when running the tools or wiring up the API.
- **[references/operations-and-best-practices.md](references/operations-and-best-practices.md)** — best practices, limitations, required modules/permissions, anti-patterns, the troubleshooting table, and success criteria. Read before hardening a tenant or shipping scripts.
- **[references/powershell-templates.md](references/powershell-templates.md)** — ready-to-use script templates: Conditional Access policy examples, bulk user provisioning, and security audit scripts.
- **[references/security-policies.md](references/security-policies.md)** — Conditional Access configuration, MFA enforcement strategies, DLP/retention policies, and security baseline settings.
- **[references/troubleshooting.md](references/troubleshooting.md)** — common error resolutions, PowerShell module issues, permission troubleshooting, and DNS propagation problems.

## Scope & Limitations

**What This Skill Covers**

- **Tenant lifecycle management** -- initial setup, domain verification, DNS configuration, security baseline, and service provisioning for Exchange Online, SharePoint, Teams, and OneDrive
- **User lifecycle automation** -- bulk provisioning from CSV, license assignment by role/department, group membership recommendations, secure offboarding with mailbox preservation
- **Security and compliance** -- Conditional Access policy generation, MFA enforcement, comprehensive 7-category security audits, and audit log enablement
- **PowerShell script generation** -- production-ready scripts with error handling, logging, `-WhatIf` support, and Microsoft Graph best practices

**What This Skill Does NOT Cover**

- **Hybrid identity (AD Connect)** -- on-premises Active Directory synchronization and pass-through authentication require the `senior-devops` skill and Microsoft AD Connect tooling
- **Intune device management** -- endpoint compliance policies, app deployment, and mobile device management are outside scope; see `senior-secops` for device security posture
- **Power Platform administration** -- Power Apps, Power Automate, and Power BI tenant-level governance fall under separate platform administration
- **Third-party SSO and SCIM provisioning** -- integration with non-Microsoft identity providers (Okta, Ping, Auth0) requires dedicated identity engineering

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `senior-secops` | Security audit findings feed into SecOps incident response and threat remediation workflows | Audit CSV reports (MFA status, admin roles, inactive users) → SecOps triage and hardening actions |
| `senior-devops` | Tenant setup scripts integrate with infrastructure-as-code pipelines for repeatable deployments | Generated PowerShell scripts → CI/CD pipeline execution → tenant configuration state |
| `senior-architect` | License distribution recommendations and tenant topology inform enterprise architecture decisions | License cost analysis and user count projections → architecture capacity planning |
| `code-reviewer` | Generated PowerShell scripts can be reviewed for security anti-patterns and credential handling | PowerShell script output → code review for hardcoded secrets, missing error handling |
| `aws-solution-architect` | Multi-cloud identity federation between Azure AD and AWS IAM for organizations using both platforms | Azure AD tenant configuration → cross-cloud SSO and role mapping |
| `senior-security` | Conditional Access policies and MFA enforcement align with broader organizational security posture | CA policy configurations and security audit results → security policy compliance validation |
