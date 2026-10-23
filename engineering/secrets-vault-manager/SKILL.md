---
name: secrets-vault-manager
description: >
  This skill should be used when the user asks to "generate Vault configurations",
  "plan secret rotation", "analyze vault audit logs", "manage secrets lifecycle",
  or "set up HashiCorp Vault".
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: secrets-management
  updated: 2026-04-02
  tags: [secrets, vault, hashicorp, rotation, audit, security]
---

# Secrets Vault Manager

> **Category:** Engineering
> **Domain:** Secrets Management & Security

## Overview

The **Secrets Vault Manager** skill provides tools for generating HashiCorp Vault configurations, planning and scheduling secret rotation cycles, and analyzing vault audit logs for suspicious access patterns. Essential for teams managing secrets at scale.

## Clarify First

Before generating configs or plans, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Task:** config generation / rotation planning / audit-log analysis (selects the script and the entire workflow).
- **Environment & secrets engines:** e.g. production + kv/database/transit (`--env`, `--secrets-engines`; shapes the generated HCL).
- **Secrets inventory & classification:** Critical/High/Medium/Low per secret (drives rotation frequencies and the schedule).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

```bash
# Generate Vault configuration
python scripts/vault_config_generator.py --env production --secrets-engines kv,database,transit

# Plan secret rotation schedule
python scripts/rotation_planner.py --inventory secrets_inventory.json

# Analyze vault audit logs
python scripts/audit_log_analyzer.py --log-file vault_audit.log --format json
```

## Tools Overview

| Tool | Purpose | Key Flags |
|------|---------|-----------|
| `vault_config_generator.py` | Generate HashiCorp Vault configurations | `--env`, `--secrets-engines`, `--auth-methods` |
| `rotation_planner.py` | Plan and schedule secret rotation cycles | `--inventory`, `--policy`, `--format` |
| `audit_log_analyzer.py` | Analyze vault audit logs for anomalies | `--log-file`, `--bulk-threshold`, `--auth-threshold`, `--format` |

## Workflows

### Initial Vault Setup
1. Define environment and required secrets engines
2. Run `vault_config_generator.py` to generate HCL configs
3. Review and customize generated configurations
4. Apply via Terraform or Vault CLI

### Secret Rotation Planning
1. Create secrets inventory (JSON)
2. Run `rotation_planner.py` to generate schedule
3. Review rotation plan and adjust frequencies
4. Implement automated rotation where possible

### Audit Log Investigation
1. Export vault audit logs
2. Run `audit_log_analyzer.py` for anomaly detection
3. Review flagged events
4. Investigate suspicious access patterns

## Scope & Limitations

**In Scope:**
- HashiCorp Vault configuration files from `vault_config_generator.py`: server config, secrets engines (kv, database, transit, pki, aws, ssh), auth methods (approle, kubernetes, oidc, token, userpass) and a policy, per environment, with optional HA.
- Rotation schedules from a JSON secrets inventory with `rotation_planner.py`, including custom policies, priority and owner filters, and a sample inventory generator.
- Anomaly checks on Vault audit logs in JSON format with `audit_log_analyzer.py`: off-hours access, bulk reads, failed authentication, root token use and unusual paths.
- Classification, rotation and audit guidance in `references/secrets-management-guide.md`.

**Out of Scope:**
- Connecting to a running Vault server, applying configuration or rotating any secret. The scripts only read local files and print or write files.
- `.env` scaffolding, leaked-secret scanning and other secret stores (see `engineering/env-secrets-manager/`).
- Cloud KMS, IAM and secret-manager posture in live accounts (see `engineering/cloud-security/`).
- Provisioning Vault infrastructure with Terraform (see `engineering/terraform-patterns/`).

**Important Caveats:**
- Generated HCL is a starting template. It needs review for the real network, storage backend, TLS certificates and policy paths before use, and `--no-tls` is for development only.
- Rotation dates are only as accurate as the inventory. The planner does not discover secrets or check when they were last rotated.
- The log analyzer uses fixed rules and thresholds (`--bulk-threshold`, `--auth-threshold`, a 22:00-06:00 off-hours window applied to the logged timestamps). Alerts need investigation, and a quiet report does not show that no misuse took place.
- Vault features and engine options change between releases, so generated settings need checking against the documentation for the deployed version.

## Reference Documentation

- [Secrets Management Guide](references/secrets-management-guide.md) - Best practices, rotation policies, and compliance requirements

## Common Patterns

### Secret Classification
- **Critical**: Database credentials, API master keys, encryption keys
- **High**: Service account tokens, OAuth secrets, TLS certificates
- **Medium**: Third-party API keys, webhook secrets
- **Low**: Public API keys, non-sensitive configuration
