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
| `audit_log_analyzer.py` | Analyze vault audit logs for anomalies | `--log-file`, `--time-range`, `--format` |

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

## Reference Documentation

- [Secrets Management Guide](references/secrets-management-guide.md) - Best practices, rotation policies, and compliance requirements

## Common Patterns

### Secret Classification
- **Critical**: Database credentials, API master keys, encryption keys
- **High**: Service account tokens, OAuth secrets, TLS certificates
- **Medium**: Third-party API keys, webhook secrets
- **Low**: Public API keys, non-sensitive configuration
