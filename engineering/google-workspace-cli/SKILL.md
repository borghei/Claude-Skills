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

## Quick Start

```bash
# Audit Workspace security configuration
python scripts/workspace_audit.py --config gws-config.json

# Generate auth setup guide
python scripts/auth_setup_guide.py --method oauth --scopes admin,drive

# Run diagnostics
python scripts/gws_doctor.py --check all

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

Diagnostic tool for common Google Workspace configuration issues.

| Feature | Description |
|---------|-------------|
| DNS checks | Validates MX, SPF, DKIM, DMARC records format |
| SSL/TLS | Checks certificate and transport security settings |
| Integration health | Validates common integration patterns |
| Config consistency | Checks for conflicting settings |
| Best practices | Compares against GWS recommended settings |

## Workflows

### Security Audit Workflow

1. **Export config** - Export GWS settings to JSON via Admin SDK or manual export
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

1. **Run diagnostics** - Execute gws_doctor.py with all checks
2. **Review results** - Check DNS, email, and integration health
3. **Fix issues** - Address failures in priority order
4. **Re-check** - Verify fixes pass diagnostics

### Regular Maintenance

```bash
# Monthly security audit
python scripts/workspace_audit.py --config gws-export.json --format json > audit_$(date +%Y%m).json

# Weekly health check
python scripts/gws_doctor.py --check dns,email --format json
```

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
