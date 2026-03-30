---
name: ms365-tenant-manager
description: >
  Microsoft 365 tenant administration for Global Administrators. Automate M365
  tenant setup, Office 365 admin tasks, Azure AD user management, Exchange
  Online configuration, Teams administration, and security policies. Generate
  PowerShell scripts for bulk operations, Conditional Access policies, license
  management, and compliance reporting. Use for M365 tenant manager, Office 365
  admin, Azure AD users, Global Administrator, tenant configuration, or
  Microsoft 365 automation.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: cloud-administration
  updated: 2026-03-31
  tags: [microsoft-365, azure-ad, office-365, administration]
---
# Microsoft 365 Tenant Manager

Expert guidance and automation for Microsoft 365 Global Administrators managing tenant setup, user lifecycle, security policies, and organizational optimization.

---

## Table of Contents

- [Trigger Phrases](#trigger-phrases)
- [Quick Start](#quick-start)
- [Tools](#tools)
- [Workflows](#workflows)
- [Best Practices](#best-practices)
- [Reference Guides](#reference-guides)
- [Limitations](#limitations)

---

## Trigger Phrases

Use this skill when you hear:
- "set up Microsoft 365 tenant"
- "create Office 365 users"
- "configure Azure AD"
- "generate PowerShell script for M365"
- "set up Conditional Access"
- "bulk user provisioning"
- "M365 security audit"
- "license management"
- "Exchange Online configuration"
- "Teams administration"

---

## Quick Start

### Generate Security Audit Script

```bash
python scripts/powershell_generator.py --action audit --output audit_script.ps1
```

### Create Bulk User Provisioning Script

```bash
python scripts/user_management.py --action provision --csv users.csv --license E3
```

### Configure Conditional Access Policy

```bash
python scripts/powershell_generator.py --action conditional-access --require-mfa --include-admins
```

---

## Tools

### powershell_generator.py

Generates ready-to-use PowerShell scripts for Microsoft 365 administration.

**Usage:**

```bash
# Generate security audit script
python scripts/powershell_generator.py --action audit

# Generate Conditional Access policy script
python scripts/powershell_generator.py --action conditional-access \
  --policy-name "Require MFA for Admins" \
  --require-mfa \
  --include-users "All"

# Generate bulk license assignment script
python scripts/powershell_generator.py --action license \
  --csv users.csv \
  --sku "ENTERPRISEPACK"
```

**Parameters:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--action` | Yes | Script type: `audit`, `conditional-access`, `license`, `users` |
| `--policy-name` | No | Name for Conditional Access policy |
| `--require-mfa` | No | Require MFA in policy |
| `--include-users` | No | Users to include: `All` or specific UPNs |
| `--csv` | No | CSV file path for bulk operations |
| `--sku` | No | License SKU for assignment |
| `--output` | No | Output file path (default: stdout) |

**Output:** Complete PowerShell scripts with error handling, logging, and best practices.

### user_management.py

Automates user lifecycle operations and bulk provisioning.

**Usage:**

```bash
# Provision users from CSV
python scripts/user_management.py --action provision --csv new_users.csv

# Offboard user securely
python scripts/user_management.py --action offboard --user john.doe@company.com

# Generate inactive users report
python scripts/user_management.py --action report-inactive --days 90
```

**Parameters:**

| Parameter | Required | Description |
|-----------|----------|-------------|
| `--action` | Yes | Operation: `provision`, `offboard`, `report-inactive`, `sync` |
| `--csv` | No | CSV file for bulk operations |
| `--user` | No | Single user UPN |
| `--days` | No | Days for inactivity threshold (default: 90) |
| `--license` | No | License SKU to assign |

### tenant_setup.py

Initial tenant configuration and service provisioning automation.

**Usage:**

```bash
# Generate tenant setup checklist
python scripts/tenant_setup.py --action checklist --company "Acme Inc" --users 50

# Generate DNS records configuration
python scripts/tenant_setup.py --action dns --domain acme.com

# Generate security baseline script
python scripts/tenant_setup.py --action security-baseline
```

---

## Workflows

### Workflow 1: New Tenant Setup

**Step 1: Generate Setup Checklist**

```bash
python scripts/tenant_setup.py --action checklist --company "Company Name" --users 100
```

**Step 2: Configure DNS Records**

```bash
python scripts/tenant_setup.py --action dns --domain company.com
```

**Step 3: Apply Security Baseline**

```bash
python scripts/powershell_generator.py --action audit > initial_audit.ps1
```

**Step 4: Provision Users**

```bash
python scripts/user_management.py --action provision --csv employees.csv --license E3
```

### Workflow 2: Security Hardening

**Step 1: Run Security Audit**

```bash
python scripts/powershell_generator.py --action audit --output security_audit.ps1
```

**Step 2: Create MFA Policy**

```bash
python scripts/powershell_generator.py --action conditional-access \
  --policy-name "Require MFA All Users" \
  --require-mfa \
  --include-users "All"
```

**Step 3: Review Results**

Execute generated scripts and review CSV reports in output directory.

### Workflow 3: User Offboarding

**Step 1: Generate Offboarding Script**

```bash
python scripts/user_management.py --action offboard --user departing.user@company.com
```

**Step 2: Execute Script with -WhatIf**

```powershell
.\offboard_user.ps1 -WhatIf
```

**Step 3: Execute for Real**

```powershell
.\offboard_user.ps1 -Confirm:$false
```

---

## Best Practices

### Tenant Setup

1. Enable MFA before adding users
2. Configure named locations for Conditional Access
3. Use separate admin accounts with PIM
4. Verify custom domains before bulk user creation
5. Apply Microsoft Secure Score recommendations

### Security Operations

1. Start Conditional Access policies in report-only mode
2. Use `-WhatIf` parameter before executing scripts
3. Never hardcode credentials in scripts
4. Enable audit logging for all operations
5. Regular quarterly security reviews

### PowerShell Automation

1. Prefer Microsoft Graph over legacy MSOnline modules
2. Include try/catch blocks for error handling
3. Implement logging for audit trails
4. Use Azure Key Vault for credential management
5. Test in non-production tenant first

---

## Reference Guides

### When to Use Each Reference

**references/powershell-templates.md**

- Ready-to-use script templates
- Conditional Access policy examples
- Bulk user provisioning scripts
- Security audit scripts

**references/security-policies.md**

- Conditional Access configuration
- MFA enforcement strategies
- DLP and retention policies
- Security baseline settings

**references/troubleshooting.md**

- Common error resolutions
- PowerShell module issues
- Permission troubleshooting
- DNS propagation problems

---

## Limitations

| Constraint | Impact |
|------------|--------|
| Global Admin required | Full tenant setup needs highest privilege |
| API rate limits | Bulk operations may be throttled |
| License dependencies | E3/E5 required for advanced features |
| Hybrid scenarios | On-premises AD needs additional configuration |
| PowerShell prerequisites | Microsoft.Graph module required |

### Required PowerShell Modules

```powershell
Install-Module Microsoft.Graph -Scope CurrentUser
Install-Module ExchangeOnlineManagement -Scope CurrentUser
Install-Module MicrosoftTeams -Scope CurrentUser
```

### Required Permissions

- **Global Administrator** - Full tenant setup
- **User Administrator** - User management
- **Security Administrator** - Security policies
- **Exchange Administrator** - Mailbox management

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| `Connect-MgGraph` fails with "Insufficient privileges" | App registration missing required API permissions | Grant `Directory.ReadWrite.All`, `User.ReadWrite.All`, and `Policy.ReadWrite.ConditionalAccess` in Azure AD > App Registrations > API Permissions, then admin-consent |
| Bulk user creation silently skips users | CSV `UserPrincipalName` column missing or domain not verified in tenant | Verify custom domain is added and set as default; ensure CSV header matches exactly `UserPrincipalName` |
| License assignment returns "No available licenses" | All purchased seats consumed or SKU part number misspelled | Run `Get-MgSubscribedSku -All` to confirm `SkuPartNumber` and check `PrepaidUnits.Enabled - ConsumedUnits > 0` |
| Conditional Access policy created but not enforcing MFA | Policy state defaults to `enabledForReportingButNotEnforced` (report-only) | After validating sign-in logs, update policy state to `enabled` in Azure AD > Security > Conditional Access |
| Offboarding script fails at mailbox conversion | Exchange Online Management module not connected or mailbox already shared | Run `Connect-ExchangeOnline` before executing; check mailbox type with `Get-Mailbox -Identity user@domain.com` |
| DNS records configured but mail not flowing | MX record DNS propagation incomplete or SPF record missing `-all` suffix | Wait up to 48 hours for propagation; validate with `nslookup -type=MX domain.com` and confirm SPF ends with `-all` |
| Security audit reports empty CSV files | Microsoft Graph scopes not consented or audit log ingestion not enabled | Run `Set-AdminAuditLogConfig -UnifiedAuditLogIngestionEnabled $true` and re-consent scopes with `Connect-MgGraph -Scopes "AuditLog.Read.All"` |

---

## Success Criteria

- 100% of provisioned users have correct license SKU assigned matching their role and department
- Zero orphaned accounts: every disabled user has licenses removed, mailbox converted to shared, and sessions revoked within 24 hours of offboarding
- MFA enforcement covers 100% of enabled user accounts, verified by security audit script output showing zero users without MFA
- DNS records pass validation for all five service types (MX, SPF, DKIM, autodiscover, device registration) with zero propagation errors
- Conditional Access policies achieve report-only validation with less than 1% false-positive block rate before enforcement
- License utilization stays above 90% across all SKUs, with unused licenses identified and reclaimed quarterly
- Security audit generates complete CSV reports for all 7 audit categories (MFA, admin roles, inactive users, guests, licenses, mailbox delegations, Conditional Access) with zero script errors

---

## Scope & Limitations

### What This Skill Covers

- **Tenant lifecycle management** -- initial setup, domain verification, DNS configuration, security baseline, and service provisioning for Exchange Online, SharePoint, Teams, and OneDrive
- **User lifecycle automation** -- bulk provisioning from CSV, license assignment by role/department, group membership recommendations, secure offboarding with mailbox preservation
- **Security and compliance** -- Conditional Access policy generation, MFA enforcement, comprehensive 7-category security audits, and audit log enablement
- **PowerShell script generation** -- production-ready scripts with error handling, logging, `-WhatIf` support, and Microsoft Graph best practices

### What This Skill Does NOT Cover

- **Hybrid identity (AD Connect)** -- on-premises Active Directory synchronization and pass-through authentication require the `senior-devops` skill and Microsoft AD Connect tooling
- **Intune device management** -- endpoint compliance policies, app deployment, and mobile device management are outside scope; see `senior-secops` for device security posture
- **Power Platform administration** -- Power Apps, Power Automate, and Power BI tenant-level governance fall under separate platform administration
- **Third-party SSO and SCIM provisioning** -- integration with non-Microsoft identity providers (Okta, Ping, Auth0) requires dedicated identity engineering

---

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `senior-secops` | Security audit findings feed into SecOps incident response and threat remediation workflows | Audit CSV reports (MFA status, admin roles, inactive users) → SecOps triage and hardening actions |
| `senior-devops` | Tenant setup scripts integrate with infrastructure-as-code pipelines for repeatable deployments | Generated PowerShell scripts → CI/CD pipeline execution → tenant configuration state |
| `senior-architect` | License distribution recommendations and tenant topology inform enterprise architecture decisions | License cost analysis and user count projections → architecture capacity planning |
| `code-reviewer` | Generated PowerShell scripts can be reviewed for security anti-patterns and credential handling | PowerShell script output → code review for hardcoded secrets, missing error handling |
| `aws-solution-architect` | Multi-cloud identity federation between Azure AD and AWS IAM for organizations using both platforms | Azure AD tenant configuration → cross-cloud SSO and role mapping |
| `senior-security` | Conditional Access policies and MFA enforcement align with broader organizational security posture | CA policy configurations and security audit results → security policy compliance validation |

---

## Tool Reference

### powershell_generator.py

**Purpose:** Generates production-ready PowerShell scripts for Microsoft 365 administration including security audits, Conditional Access policies, and bulk license assignment.

**Module:** `PowerShellScriptGenerator` class (import and instantiate, not a CLI tool)

**Initialization:**

```python
from powershell_generator import PowerShellScriptGenerator

generator = PowerShellScriptGenerator(tenant_domain="company.com")
```

**Methods:**

#### `generate_security_audit_script()`

Generates a comprehensive 7-category security audit PowerShell script that checks MFA status, admin role assignments, inactive users, guest users, license usage, mailbox delegations, and Conditional Access policies.

| Parameter | Required | Type | Description |
|-----------|----------|------|-------------|
| *(none)* | -- | -- | Uses `tenant_domain` from constructor |

**Example:**

```python
generator = PowerShellScriptGenerator("company.com")
script = generator.generate_security_audit_script()
print(script)  # Complete PowerShell script with Connect-MgGraph, 7 audit checks, CSV export
```

**Output:** PowerShell script string that produces CSV reports in a timestamped `SecurityAudit_` directory: `MFA_Status.csv`, `Admin_Roles.csv`, `Inactive_Users.csv`, `Guest_Users.csv`, `License_Usage.csv`, `Mailbox_Delegations.csv`, `ConditionalAccess_Policies.csv`.

#### `generate_conditional_access_policy_script(policy_config)`

Generates a PowerShell script to create a Conditional Access policy in report-only mode.

| Parameter | Required | Type | Description |
|-----------|----------|------|-------------|
| `policy_config` | Yes | `Dict[str, Any]` | Policy configuration dictionary |
| `policy_config["name"]` | No | `str` | Policy display name (default: `"MFA Policy"`) |
| `policy_config["require_mfa"]` | No | `bool` | Whether to require MFA (default: `True`) |
| `policy_config["include_users"]` | No | `str` | Users to include (default: `"All"`) |
| `policy_config["exclude_users"]` | No | `List[str]` | UPNs to exclude (default: `[]`) |

**Example:**

```python
script = generator.generate_conditional_access_policy_script({
    "name": "Require MFA for Admins",
    "require_mfa": True,
    "include_users": "All",
    "exclude_users": ["breakglass@company.com"]
})
```

**Output:** PowerShell script string that creates a Conditional Access policy via `New-MgIdentityConditionalAccessPolicy` in `enabledForReportingButNotEnforced` state.

#### `generate_bulk_license_assignment_script(users_csv_path, license_sku)`

Generates a PowerShell script for assigning a license SKU to users listed in a CSV file.

| Parameter | Required | Type | Description |
|-----------|----------|------|-------------|
| `users_csv_path` | Yes | `str` | Path to CSV file (must contain `UserPrincipalName` column) |
| `license_sku` | Yes | `str` | License SKU part number (e.g., `"ENTERPRISEPACK"` for E3) |

**Example:**

```python
script = generator.generate_bulk_license_assignment_script("users.csv", "ENTERPRISEPACK")
```

**Output:** PowerShell script string that imports the CSV, checks for existing licenses, assigns the specified SKU, and exports results to `LicenseAssignment_Results_<timestamp>.csv` with `Status` and `Message` columns.

---

### user_management.py

**Purpose:** Manages user lifecycle operations including bulk provisioning, secure offboarding, license recommendations, group membership, and data validation.

**Module:** `UserLifecycleManager` class (import and instantiate, not a CLI tool)

**Initialization:**

```python
from user_management import UserLifecycleManager

manager = UserLifecycleManager(domain="company.com")
```

**Methods:**

#### `generate_user_creation_script(users)`

Generates a PowerShell script for bulk user provisioning with license assignment.

| Parameter | Required | Type | Description |
|-----------|----------|------|-------------|
| `users` | Yes | `List[Dict[str, Any]]` | List of user dictionaries |
| `users[].username` | Yes | `str` | Username (without domain) |
| `users[].display_name` | Yes | `str` | Full display name |
| `users[].first_name` | Yes | `str` | Given name |
| `users[].last_name` | Yes | `str` | Surname |
| `users[].job_title` | No | `str` | Job title |
| `users[].department` | No | `str` | Department name |
| `users[].license_sku` | No | `str` | License SKU (default: `"Microsoft_365_Business_Standard"`) |

**Example:**

```python
script = manager.generate_user_creation_script([
    {"username": "jdoe", "display_name": "Jane Doe", "first_name": "Jane",
     "last_name": "Doe", "job_title": "Engineer", "department": "Engineering",
     "license_sku": "ENTERPRISEPACK"}
])
```

**Output:** PowerShell script string that creates users via `New-MgUser`, assigns licenses, and exports results to `UserCreation_Results_<timestamp>.csv`.

#### `generate_user_offboarding_script(user_email)`

Generates a comprehensive 11-step secure offboarding PowerShell script.

| Parameter | Required | Type | Description |
|-----------|----------|------|-------------|
| `user_email` | Yes | `str` | UPN of the user to offboard |

**Example:**

```python
script = manager.generate_user_offboarding_script("john.doe@company.com")
```

**Output:** PowerShell script string that disables sign-in, revokes sessions, removes group memberships, removes devices, converts mailbox to shared, sets auto-reply, removes licenses, hides from GAL, and exports an offboarding report CSV.

#### `generate_license_assignment_recommendations(user_role, department)`

Returns license recommendation based on role and department matching.

| Parameter | Required | Type | Description |
|-----------|----------|------|-------------|
| `user_role` | Yes | `str` | Job title or role (matched against keywords: CEO, CTO, admin, manager, contractor, etc.) |
| `department` | Yes | `str` | Department name (matched against: legal, finance, hr, accounting) |

**Example:**

```python
rec = manager.generate_license_assignment_recommendations("Security Analyst", "IT")
# Returns: {"recommended_license": "Microsoft 365 E5", "justification": "...", "features_needed": [...], "monthly_cost": 57.00}
```

**Output:** Dictionary with `recommended_license`, `justification`, `features_needed` (list), and `monthly_cost` (float).

#### `generate_group_membership_recommendations(user)`

Recommends security and distribution groups based on user attributes.

| Parameter | Required | Type | Description |
|-----------|----------|------|-------------|
| `user` | Yes | `Dict[str, Any]` | User dictionary with `department`, `location`, `job_title`, `needs_sharepoint_access`, `needs_project_access` |

**Example:**

```python
groups = manager.generate_group_membership_recommendations({
    "department": "Engineering", "location": "NYC", "job_title": "Director of Engineering"
})
# Returns: ["DL-Engineering", "SG-Engineering", "SG-Location-Nyc", "SG-Management"]
```

**Output:** List of recommended group name strings using naming conventions `DL-` (distribution list), `SG-` (security group).

#### `validate_user_data(user_data)`

Validates user data before provisioning, checking required fields, username format, and email format.

| Parameter | Required | Type | Description |
|-----------|----------|------|-------------|
| `user_data` | Yes | `Dict[str, Any]` | Dictionary with `first_name`, `last_name`, `username` (required); `email`, `display_name`, `license_sku` (optional) |

**Example:**

```python
result = manager.validate_user_data({"first_name": "Jane", "last_name": "Doe", "username": "jdoe"})
# Returns: {"is_valid": True, "errors": [], "warnings": ["Display name not provided, will use: Jane Doe", ...]}
```

**Output:** Dictionary with `is_valid` (bool), `errors` (list of strings), and `warnings` (list of strings).

---

### tenant_setup.py

**Purpose:** Manages initial Microsoft 365 tenant configuration including setup checklists, DNS record generation, PowerShell setup scripts, and license distribution recommendations.

**Module:** `TenantSetupManager` class (import and instantiate, not a CLI tool)

**Initialization:**

```python
from tenant_setup import TenantSetupManager

manager = TenantSetupManager(tenant_config={
    "company_name": "Acme Inc",
    "domain_name": "acme.com",
    "user_count": 50,
    "industry": "technology",
    "compliance_requirements": ["GDPR"],  # optional: "GDPR", "HIPAA"
    "licenses": {}
})
```

| Config Key | Required | Type | Description |
|------------|----------|------|-------------|
| `company_name` | Yes | `str` | Organization display name |
| `domain_name` | Yes | `str` | Primary custom domain |
| `user_count` | Yes | `int` | Total expected user count |
| `industry` | No | `str` | Industry vertical (default: `"general"`) |
| `compliance_requirements` | No | `List[str]` | Compliance frameworks: `"GDPR"`, `"HIPAA"` |
| `licenses` | No | `Dict` | Existing license inventory |

**Methods:**

#### `generate_setup_checklist()`

Generates a phased tenant setup checklist (4-5 phases depending on compliance requirements).

| Parameter | Required | Type | Description |
|-----------|----------|------|-------------|
| *(none)* | -- | -- | Uses constructor config |

**Example:**

```python
checklist = manager.generate_setup_checklist()
# Returns list of phase dicts, each with "phase", "name", "priority", "tasks"
```

**Output:** List of dictionaries. Each phase contains `phase` (int), `name` (str), `priority` (`"critical"` or `"high"`), and `tasks` (list of dicts with `task`, `details`, `estimated_time`). Phases: Initial Configuration, Custom Domain, Security Baseline, Service Configuration, and optionally Compliance Configuration.

#### `generate_dns_records()`

Generates all required DNS records for Microsoft 365 services.

| Parameter | Required | Type | Description |
|-----------|----------|------|-------------|
| *(none)* | -- | -- | Uses `domain_name` from constructor |

**Example:**

```python
records = manager.generate_dns_records()
# Keys: "mx_records", "txt_records", "cname_records", "srv_records"
```

**Output:** Dictionary with four keys, each containing a list of record dictionaries with `type`, `name`, `value`, `ttl`, `purpose`, and record-type-specific fields (`priority` for MX/SRV, `port`/`weight` for SRV).

#### `generate_powershell_setup_script()`

Generates a complete PowerShell script for initial tenant configuration covering Graph, Exchange Online, SharePoint, and Teams.

| Parameter | Required | Type | Description |
|-----------|----------|------|-------------|
| *(none)* | -- | -- | Uses constructor config |

**Example:**

```python
script = manager.generate_powershell_setup_script()
print(script)  # PowerShell script connecting to Graph, Exchange, Teams with 7 setup steps
```

**Output:** PowerShell script string that connects to Microsoft Graph, Exchange Online, and Teams; configures organization settings, security defaults, audit logging, Exchange policies, and Teams messaging policies.

#### `get_license_recommendations()`

Calculates license distribution recommendations and cost estimates based on user count and compliance requirements.

| Parameter | Required | Type | Description |
|-----------|----------|------|-------------|
| *(none)* | -- | -- | Uses `user_count` and `compliance_requirements` from constructor |

**Example:**

```python
recs = manager.get_license_recommendations()
# Returns: {"recommendations": {...}, "suggested_distribution": {"E5": 5, "E3": 10, ...},
#           "estimated_monthly_cost": 1234.50, "estimated_annual_cost": 14814.00}
```

**Output:** Dictionary with `recommendations` (license tier details), `suggested_distribution` (dict mapping SKU tier to user count), `estimated_monthly_cost` (float), and `estimated_annual_cost` (float). Distribution adjusts automatically when compliance requirements are specified.
