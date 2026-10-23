---
name: google-workspace-cli
description: >
  This skill should be used when the user asks to "audit Google Workspace",
  "check GWS security settings", "set up Google Workspace authentication",
  "diagnose Workspace issues", or "review Google admin configurations".
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: google-workspace
  updated: 2026-04-02
  tags: [google-workspace, gws, admin, security, audit]
---
# Google Workspace CLI

> **Category:** Engineering
> **Domain:** Google Workspace Administration

## Overview

The **Google Workspace CLI** skill provides tools for auditing Google Workspace configurations, generating authentication setup documentation, and diagnosing common GWS issues. It helps IT administrators maintain secure, well-configured Workspace environments without needing to navigate complex admin consoles.

## Clarify First

Before running, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Task:** security audit, auth setup guide, or diagnostics (selects `workspace_audit.py` vs `auth_setup_guide.py` vs `gws_doctor.py`).
- **Config export or auth method:** the GWS config JSON to audit, or the auth method and scopes for a setup guide (sets `--config` or `--method`/`--scopes`).
- **Output mode:** human-readable vs JSON for automation (sets `--format json`).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

```bash
# Audit Workspace security configuration
python scripts/workspace_audit.py --config gws-config.json

# Generate auth setup guide
python scripts/auth_setup_guide.py --method oauth --scopes admin,drive

# Run diagnostics on a config JSON (try --sample first to see the output)
python scripts/gws_doctor.py --config gws-doctor.json --check all
python scripts/gws_doctor.py --sample --check all

# JSON output for automation
python scripts/workspace_audit.py --config gws-config.json --format json
```

## Tools Overview

### workspace_audit.py

Audits Google Workspace configuration exports for security best practices.

| Feature | Description |
|---------|-------------|
| 2FA enforcement | Checks if 2-step verification is required |
| Password policy | Validates password strength requirements |
| Sharing settings | Reviews external sharing configurations |
| App access | Checks third-party app access policies |
| Admin roles | Reviews admin role assignments |
| Mobile management | Checks device management policies |
| Drive settings | Validates Drive sharing and access controls |

### auth_setup_guide.py

Generates step-by-step authentication setup documentation for GWS API access.

| Feature | Description |
|---------|-------------|
| OAuth setup | Generates OAuth 2.0 configuration guide |
| Service account | Creates service account setup documentation |
| API scopes | Lists required scopes for each API |
| Domain delegation | Documents domain-wide delegation setup |
| Testing guide | Provides verification steps |

### gws_doctor.py

Diagnostic tool for common Google Workspace configuration issues. It needs `--config <file>` or `--sample`, and every check reads values from that JSON. Nothing is looked up live. `--generate-sample` prints the doctor's config schema, which differs from the `workspace_audit.py` schema. The tool exits 1 when any check fails.

| `--check` | Description |
|---------|-------------|
| `dns` | Checks the MX, SPF, DKIM and DMARC record values written in the config |
| `email` | Reviews the email routing and spam filtering settings |
| `security` | Checks 2-step verification enforcement and session duration |
| `integration` | Reviews SSO and directory sync settings |
| `consistency` | Flags conflicting settings, such as external sharing without 2-step verification |

## Workflows

### Security Audit Workflow

1. **Prepare config** - Write your settings into a JSON file in the tool's schema; `workspace_audit.py --generate-sample` prints a template to fill in. No tool in this skill exports settings
2. **Audit** - Run workspace_audit.py against the config file
3. **Review findings** - Prioritize critical security gaps
4. **Remediate** - Apply recommended settings in Admin Console
5. **Re-audit** - Verify changes resolved findings

### API Setup Workflow

1. **Plan** - Determine which APIs and scopes are needed
2. **Generate guide** - Run auth_setup_guide.py with desired method
3. **Follow steps** - Create credentials in Google Cloud Console
4. **Configure** - Set up domain delegation if needed
5. **Verify** - Test API access with provided verification steps

### Health Check Workflow

1. **Prepare config** - Fill in the template from `gws_doctor.py --generate-sample` with the values from your Admin Console and DNS zone
2. **Run diagnostics** - Execute `gws_doctor.py --config <file> --check all`
3. **Review results** - Check DNS, email, and integration health. DNS results reflect the values in the file, so confirm them against the live zone
4. **Fix issues** - Address failures in priority order
5. **Re-check** - Update the file and verify fixes pass diagnostics

### Regular Maintenance

```bash
# Monthly security audit
python scripts/workspace_audit.py --config gws-export.json --format json > audit_$(date +%Y%m).json

# Weekly health check
python scripts/gws_doctor.py --config gws-doctor.json --check dns,email --format json
```

## Scope & Limitations

**In Scope:**
- Security audits of a Workspace configuration JSON with `workspace_audit.py`: 2-step verification, password policy, external sharing, third-party app access, admin roles, mobile management and Drive settings
- Diagnostics with `gws_doctor.py` on the same kind of JSON: MX, SPF, DKIM and DMARC record format, email and security settings, integrations and conflicting settings
- Auth setup guides from `auth_setup_guide.py` for OAuth or service accounts, with scopes for Admin SDK, Drive, Gmail, Calendar, Sheets and Reports, and optional domain-wide delegation steps
- Sample configs (`--generate-sample`, `--sample`) and an admin reference for security settings, API configuration and DNS requirements

**Out of Scope:**
- Calling the Admin SDK or any Google API, exporting settings, or changing settings in the Admin Console
- Microsoft 365 tenant administration (see `engineering/ms365-tenant-manager/`)
- Privacy law and data-protection compliance for Workspace data (see `ra-qm-team/gdpr-dsgvo-expert/`)
- General cloud IAM and posture outside Workspace (see `engineering/cloud-security/`)

**Important Caveats:**
- All three tools work offline. The audit and diagnostics read a JSON file the user prepares in the tool's own schema, and there is no export tool in this skill.
- DNS checks look at the record values in that file. They do not query live DNS, so a record that is correct in the file can still be missing or wrong in the real zone.
- Findings compare settings with the skill's recommended values. They are not a Google security review or a compliance certification.
- Google changes Admin Console settings, API scopes and auth requirements over time. Confirm generated setup steps against current Google documentation.

## Reference Documentation

- [GWS Admin Guide](references/gws-admin-guide.md) - Security settings, API configuration, DNS requirements

## Common Patterns Quick Reference

### Security Priorities
| Setting | Priority | Impact |
|---------|----------|--------|
| 2FA enforcement | Critical | Prevents account takeover |
| Password policy | Critical | Reduces credential attacks |
| External sharing | High | Prevents data leakage |
| App access control | High | Limits third-party risk |
| Mobile management | Medium | Secures device access |
| Admin role review | Medium | Limits privilege exposure |

### DNS Records for Email
| Record | Purpose | Example |
|--------|---------|---------|
| MX | Email routing | `ASPMX.L.GOOGLE.COM` |
| SPF | Sender verification | `v=spf1 include:_spf.google.com ~all` |
| DKIM | Email signing | Domain-specific CNAME |
| DMARC | Policy enforcement | `v=DMARC1; p=reject; rua=mailto:...` |

### API Scopes
| API | Scope | Purpose |
|-----|-------|---------|
| Admin SDK | `admin.directory.user` | User management |
| Drive | `drive.readonly` | File listing |
| Gmail | `gmail.settings.basic` | Email settings |
| Calendar | `calendar.readonly` | Calendar access |

### Common Issues
| Issue | Symptom | Fix |
|-------|---------|-----|
| No 2FA | Account takeover risk | Enable 2FA enforcement |
| Weak passwords | Credential stuffing | Set 12+ char minimum |
| Open sharing | Data leakage | Restrict external sharing |
| No DMARC | Email spoofing | Add DMARC DNS record |
| Stale admins | Excessive privileges | Review admin roles quarterly |
