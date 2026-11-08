# Tools, Quick Start & Workflows

Read this when running the generator, wiring up the import-based Python API, or executing an end-to-end tenant operation (setup, hardening, offboarding).

All commands run from the skill folder. `scripts/ms365_cli.py` is the command-line entry point; the three modules behind it are importable libraries (see Tool Reference below). Nothing here connects to a tenant: the output is PowerShell for an administrator to review and run.

## Quick Start

```bash
python3 scripts/ms365_cli.py audit --domain contoso.com -o audit.ps1
python3 scripts/ms365_cli.py provision --domain contoso.com --users assets/sample_users.csv -o provision.ps1
python3 scripts/ms365_cli.py conditional-access --domain contoso.com --exclude breakglass@contoso.com -o ca-mfa.ps1
```

## CLI

| Subcommand | Output | Key flags |
|------------|--------|-----------|
| `audit` | Security audit script: MFA, admin roles, inactive users, guests, licenses, mailbox delegation, CA policies | `--domain`, `-o` |
| `conditional-access` | CA policy script, created as `enabledForReportingButNotEnforced` | `--domain`, `--name`, `--include`, `--exclude ...`, `--no-mfa` |
| `bulk-license` | License assignment script for a CSV with a `UserPrincipalName` column | `--domain`, `--csv`, `--sku` |
| `provision` | Validates every user, then writes the creation script; random 20-character temporary passwords, forced change at first sign-in | `--domain`, `--users CSV\|JSON` |
| `offboard` | Offboarding script (disable sign-in, revoke sessions, remove groups and devices, convert mailbox to shared, remove licenses); supports `-WhatIf` | `--domain`, `--user` |
| `recommend-license` | License recommendation with justification and list price | `--role`, `--department`, `--format json` |
| `setup` | Checklist, DNS records, setup script or license distribution from a tenant config | `--config`, `--part checklist\|dns\|script\|licenses`, `--format json` |

Users CSV columns: `first_name,last_name,username,display_name,job_title,department,license_sku` (the first three are required).

Exit codes: 0 output written; 1 `provision` found invalid users and wrote nothing; 2 unusable input (missing file, bad JSON or CSV, invalid domain or UPN).

Prices printed by `recommend-license` and `setup --part licenses` are list prices embedded in the module; check current Microsoft pricing before quoting them.

---

## Workflows

### Workflow 1: New Tenant Setup

```bash
python3 scripts/ms365_cli.py setup --config sample_input.json --part checklist
python3 scripts/ms365_cli.py setup --config sample_input.json --part dns        # records to create at the registrar
python3 scripts/ms365_cli.py setup --config sample_input.json --part script -o setup.ps1
python3 scripts/ms365_cli.py provision --domain acme.com --users employees.csv -o provision.ps1
```

Replace the `MS=msXXXXXXXX` verification value with the one the admin center shows. Teams-only tenants do not need the legacy Skype for Business SRV and `lyncdiscover` records; check Microsoft's current DNS list for your services.

### Workflow 2: Security Hardening

```bash
python3 scripts/ms365_cli.py audit --domain company.com -o security_audit.ps1
python3 scripts/ms365_cli.py conditional-access --domain company.com \
  --name "Require MFA All Users" --exclude <break-glass-object-id> -o ca-mfa.ps1
```

Run the audit, review its CSV reports, then create the policy. It starts in report-only mode; watch sign-in logs for a week before switching it to enabled.

### Workflow 3: User Offboarding

```bash
python3 scripts/ms365_cli.py offboard --domain company.com --user departing.user@company.com -o offboard_user.ps1
```

```powershell
.\offboard_user.ps1 -WhatIf     # preview
.\offboard_user.ps1             # run after the preview and any legal-hold check
```

---

## Tool Reference

### powershell_generator.py

**Purpose:** Generates production-ready PowerShell scripts for Microsoft 365 administration including security audits, Conditional Access policies, and bulk license assignment.

**Module:** `PowerShellScriptGenerator` class (library; the command-line entry point is `ms365_cli.py`)

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

**Module:** `UserLifecycleManager` class (library; the command-line entry point is `ms365_cli.py`)

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

**Module:** `TenantSetupManager` class (library; the command-line entry point is `ms365_cli.py`)

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
