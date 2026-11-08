---
name: google-workspace-cli
description: >
  Offline audit of an exported Google Workspace config: 2SV, passwords, sharing, apps,
  admins, email DNS. Writes API auth setup guides. Use when asked to audit Workspace
  security, check SPF/DKIM/DMARC, or set up Admin SDK access.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: google-workspace
  updated: 2026-11-08
  tags: [google-workspace, gws, admin, security, audit]
---
# Google Workspace CLI

Audit a Google Workspace tenant's security settings and email DNS against recommended values, and generate setup guides for Admin SDK / API access. The tools are offline: they read a JSON file built from an export, so the agent's first job is always getting real data into that file.

## Quick Start

```bash
python3 scripts/workspace_audit.py --generate-sample          # schema to fill in
python3 scripts/workspace_audit.py --config assets/sample_workspace_config.json
python3 scripts/auth_setup_guide.py --list-scopes
```

## When to Use

- "Audit our Google Workspace security" or "review our Admin console settings".
- Checking MX, SPF, DKIM and DMARC for a Workspace domain.
- Setting up OAuth or a service account with domain-wide delegation for Workspace APIs.
- Re-checking settings after remediation.

Not for: Microsoft 365 (`engineering/ms365-tenant-manager`), cloud IAM outside Workspace (`engineering/cloud-security`), privacy-law questions (`ra-qm-team/gdpr-dsgvo-expert`).

## Clarify First

Before running, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Task:** security audit, email/DNS diagnostics, or an auth setup guide.
- **Data access:** can the user run GAM (or another Admin SDK client) and `dig`, or will they read values off the Admin console by hand? This decides how the config file gets filled.
- **Output mode:** human-readable or JSON for automation.

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Workflow

### 1. Export the data

No tool here calls Google. The agent collects the values (or asks the user to run the commands), then writes them into the tool's schema. Useful sources:

| Setting | Where it comes from |
|---------|---------------------|
| 2SV enforcement | `gam print users fields primaryemail,isenrolledin2sv,isenforcedin2sv` — set `security.2fa_enforcement` to true only if every user is enforced |
| Super admins | `gam print admins` — list the Super Admin role holders in `admin.super_admins` |
| Third-party app grants | `gam all users print tokens` — summarise into `security.api_clients` (name + scopes) |
| Mobile management | `gam print mobile` plus Admin console > Devices > Settings |
| Password, session, Drive sharing | Admin console (Security > Password management, Google session control; Apps > Drive > Sharing settings), or the Cloud Identity Policy API where your edition exposes it |
| MX / SPF / DKIM / DMARC | `dig +short MX example.com`, `dig +short TXT example.com`, `dig +short TXT google._domainkey.example.com`, `dig +short TXT _dmarc.example.com` |

Leave a key out rather than guessing. Missing settings are reported as **not provided** and never counted as failures, so the report shows exactly what was and was not assessed.

### 2. Run the checks

```bash
# Security audit: the flawed sample fails 2SV, password, sharing and app checks (exit 1); the sound one passes (exit 0)
python3 scripts/workspace_audit.py --config assets/sample_workspace_config.json
python3 scripts/workspace_audit.py --config assets/sample_workspace_config_sound.json --format json

# Diagnostics on DNS, email, security, integrations and conflicting settings
python3 scripts/gws_doctor.py --config assets/sample_doctor_config.json --check all
python3 scripts/gws_doctor.py --config assets/sample_doctor_config.json --check dns,email --format json

# Auth setup guide for API access
python3 scripts/auth_setup_guide.py --method service-account --scopes admin,drive --domain-delegation
```

### 3. Report and remediate

1. Lead with critical and high findings and give the Admin console path for each fix.
2. List the settings that were not provided so the user knows the audit's coverage.
3. Re-export and re-run after changes, and verify that the audit exits 0 with nothing critical or high and nothing important left "not provided".

## Tools Overview

| Tool | What it checks | Exit codes |
|------|----------------|------------|
| `workspace_audit.py` | 2SV enforcement, password length/complexity, Drive external and link sharing, third-party app access, mobile management, admin recovery, session length, super admin count (2-5), API client scope count, spoofing protection, DMARC policy | 0 no critical/high finding, 1 critical or high finding, 2 bad input or nothing auditable |
| `gws_doctor.py` | `--check dns` (record values in the file: Google MX, SPF include, DKIM, DMARC policy), `email`, `security`, `integration` (SSO, directory sync), `consistency` (e.g. external sharing without 2SV) | 0 no failures, 1 a check failed, 2 bad input, unknown `--check`, or no checkable section |
| `auth_setup_guide.py` | Step-by-step OAuth or service-account setup, scopes per API, domain-wide delegation, test steps (`--method oauth|service-account`, `--scopes admin,drive,gmail,calendar,sheets,reports`, `--domain-delegation`, `--list-scopes`) | 0, 2 on unknown scope or missing flags |

The two config schemas differ: `workspace_audit.py --generate-sample` and `gws_doctor.py --generate-sample` each print their own.

## Anti-Patterns

**Mistake:** Running the audit on a hand-typed config full of guesses.
**Why it happens:** Exporting takes effort and the tool accepts any JSON.
**Instead:** Export with GAM, `dig` and the Admin console, and omit what you could not confirm. A guessed `true` hides a real gap.

**Mistake:** Reading DNS results as proof the live zone is right.
**Why it happens:** The doctor reports "pass" on the record values in the file.
**Instead:** Paste the `dig` output into the file on the day of the audit, and say in the report when it was taken.

**Mistake:** Requesting broad scopes in the auth guide "to be safe".
**Why it happens:** It avoids a second consent round later.
**Instead:** Request the narrowest scopes per API (`--list-scopes`), use read-only scopes for audits, and limit domain-wide delegation to the service account that needs it.

## Files

- `scripts/workspace_audit.py`, `scripts/gws_doctor.py`, `scripts/auth_setup_guide.py` — the three tools above.
- `assets/sample_workspace_config.json` (flawed), `assets/sample_workspace_config_sound.json` (passes), `assets/sample_doctor_config.json` (doctor schema, fails 2SV and DMARC).

## Reference Documentation

- [references/gws-admin-guide.md](references/gws-admin-guide.md) — security settings, API configuration and DNS requirements in depth.

## Scope & Limitations

- Offline only: no Admin SDK calls, no live DNS lookups, no changes to settings.
- Findings compare settings with this skill's recommended values; they are not a Google security review or a compliance certification.
- Google changes Admin console paths, API scopes and auth requirements over time. Confirm generated setup steps against current Google documentation.
