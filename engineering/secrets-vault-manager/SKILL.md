---
name: secrets-vault-manager
description: >
  Generates HashiCorp Vault configs, plans secret rotation from an inventory, and flags
  suspicious access in Vault audit logs. Use when setting up Vault, scheduling rotation,
  or investigating secret access.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: secrets-management
  updated: 2026-11-08
  tags: [secrets, vault, hashicorp, rotation, audit, security]
---

# Secrets Vault Manager

The agent generates reviewed HashiCorp Vault configuration, turns a secrets inventory into a rotation schedule, and screens Vault audit logs for root-token use, off-hours access, bulk reads, failed authentication and sensitive paths. Nothing here talks to a live Vault: the tools read local files and print or write files.

## When to Use

- Setting up Vault for an environment: server config, secrets engines, auth methods and a policy.
- Building or reviewing a rotation schedule for an inventory of secrets.
- Investigating an exported audit log after an alert or as a periodic review.

## Clarify First

Before generating configs or plans, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Task:** config generation / rotation planning / audit-log analysis (selects the script and the entire workflow).
- **Environment & secrets engines:** e.g. production + kv/database/transit (`--env`, `--secrets-engines`; shapes the generated HCL).
- **Secrets inventory & classification:** Critical/High/Medium/Low per secret (drives rotation frequencies and the schedule).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

```bash
# Generate Vault configuration
python3 scripts/vault_config_generator.py --env production --secrets-engines kv,database,transit

# Plan secret rotation schedule (the sample's dates are relative to today, so the plan always mixes states)
INV="$(mktemp -d)/inventory.json"
python3 scripts/rotation_planner.py --generate-sample > "$INV"
python3 scripts/rotation_planner.py --inventory "$INV"          # exit 1: two secrets overdue

# Analyze vault audit logs
python3 scripts/audit_log_analyzer.py --log-file assets/sample_audit_sound.log    # exit 0: no alerts
python3 scripts/audit_log_analyzer.py --log-file assets/sample_audit_flawed.log   # exit 1: root token at 03:00, policy change
```

## Tools Overview

| Tool | Purpose | Key Flags |
|------|---------|-----------|
| `vault_config_generator.py` | Generate HashiCorp Vault configurations | `--env`, `--secrets-engines`, `--auth-methods` |
| `rotation_planner.py` | Plan and schedule secret rotation cycles | `--inventory`, `--generate-sample`, `--policy`, `--filter-priority`, `--filter-owner`, `--format` |
| `audit_log_analyzer.py` | Analyze vault audit logs for anomalies | `--log-file`, `--bulk-threshold`, `--auth-threshold`, `--format` |

**Exit codes:** `vault_config_generator.py` 0 written, 2 bad option. `rotation_planner.py` 0 nothing overdue, 1 overdue secrets, 2 unreadable or malformed inventory. `audit_log_analyzer.py` 0 no alerts, 1 alerts (critical ones are marked in the report), 2 missing file or no parseable audit entries. A log with nothing parseable is an error, not a clean result; skipped lines are counted on stderr.

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
1. Export the file audit device log (one JSON entry per line).
2. Run `audit_log_analyzer.py`; read the skipped-line count on stderr, because skipped lines are events nobody screened.
3. Review each alert against change records and on-call notes.
4. Validation checkpoint: every high alert is explained or escalated; root-token use outside a documented break-glass event is an incident.

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

## Anti-Patterns

**Mistake:** Treating a quiet analyzer report as proof nothing happened.
**Why it matters:** The rules are fixed thresholds; misuse below them, or in lines the parser skipped, does not raise an alert.
**Instead:** Check the skipped-line count and the event totals, and sample the raw log for the paths that matter.

**Mistake:** Using the root token for routine work.
**Why it matters:** Root bypasses every policy and its use cannot be scoped or easily attributed.
**Instead:** Generate a root token only for break-glass tasks, revoke it straight after, and alert on any root-policy event.

**Mistake:** Applying generated HCL as is.
**Why it matters:** Storage, TLS, network and policy paths are placeholders for your environment; `--no-tls` configs leak secrets in transit.
**Instead:** Review every block against the deployed Vault version's documentation and apply through code review.

## Files

| File | Purpose |
|------|---------|
| `scripts/vault_config_generator.py` | Vault server, engine, auth and policy HCL per environment |
| `scripts/rotation_planner.py` | Rotation schedule from a JSON inventory |
| `scripts/audit_log_analyzer.py` | Rule-based screening of Vault audit logs |
| `assets/sample_audit_sound.log` | Ten business-hours reads by a service token; no alerts |
| `assets/sample_audit_flawed.log` | Root-token reads at 03:00, failed logins, a policy change; exits 1 |
