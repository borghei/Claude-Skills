---
name: env-secrets-manager
description: >
  Complete environment and secrets management lifecycle. Covers .env file
  scaffolding, validation scripts, secret leak detection in git history,
  credential rotation playbooks, and integration with HashiCorp Vault, AWS SSM,
  1Password CLI, and Doppler. Use when setting up projects, scanning for leaked
  secrets, or rotating credentials after an incident.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: security-devops
  tier: POWERFUL
  updated: 2026-03-09
  frameworks: vault, aws-ssm, 1password-cli, doppler
---
# Env & Secrets Manager

**Tier:** POWERFUL
**Category:** Engineering / Security
**Maintainer:** Claude Skills Team

## Overview

Complete environment variable and secrets management lifecycle: .env file structure across dev/staging/production, .env.example auto-generation that strips sensitive values, required-variable validation at startup, secret leak detection in git history, credential rotation playbooks, environment drift detection, and integration with HashiCorp Vault, AWS SSM, 1Password CLI, and Doppler.

## Keywords

secrets management, environment variables, .env, secret rotation, HashiCorp Vault, AWS SSM, 1Password, Doppler, secret leak detection, credential rotation, environment drift

## Core Capabilities

### 1. .env Lifecycle Management
- Structured .env layout with categorized sections
- Auto-generation of .env.example from .env (strips sensitive values)
- Environment-specific files (.env.local, .env.staging, .env.production)
- Validation scripts that fail fast on missing required variables

### 2. Secret Leak Detection
- Regex scan of git history for exposed credentials
- Pre-commit hook integration to block secret commits
- Pattern matching for API keys, tokens, passwords, private keys
- Working tree and staged file scanning

### 3. Credential Rotation
- Step-by-step rotation playbooks per secret type
- Scope analysis (find everywhere a secret is used)
- Zero-downtime rotation with dual-read period
- Post-rotation verification and monitoring

### 4. Secret Manager Integration
- HashiCorp Vault KV v2 with OIDC authentication
- AWS SSM Parameter Store with KMS encryption
- 1Password CLI with template injection
- Doppler with project/config management

## When to Use

- Setting up a new project — scaffold .env.example and validation
- Before every commit — scan for accidentally staged secrets
- Post-incident — rotate leaked credentials systematically
- Onboarding developers — provide complete environment setup
- Auditing — detect environment drift between staging and production
- Compliance — demonstrate secret management practices

## .env File Structure

### Canonical Layout

```bash
# ─── Application ───────────────────────────────────
APP_NAME=myapp
APP_ENV=development              # development | staging | production
APP_PORT=3000
APP_URL=http://localhost:3000    # REQUIRED: public base URL
APP_SECRET=                      # REQUIRED: min 32 chars, used for signing

# ─── Database ──────────────────────────────────────
DATABASE_URL=                    # REQUIRED: full connection string
DATABASE_POOL_MIN=2
DATABASE_POOL_MAX=10
DATABASE_SSL=false               # true in staging/production

# ─── Authentication ────────────────────────────────
AUTH_JWT_SECRET=                  # REQUIRED: min 32 chars
AUTH_JWT_EXPIRY=3600             # seconds
AUTH_REFRESH_SECRET=             # REQUIRED: min 32 chars
AUTH_REFRESH_EXPIRY=604800       # 7 days in seconds

# ─── Third-Party Services ─────────────────────────
STRIPE_SECRET_KEY=               # REQUIRED in production
STRIPE_WEBHOOK_SECRET=           # REQUIRED in production
STRIPE_PUBLISHABLE_KEY=          # REQUIRED (public, safe to expose)
SENDGRID_API_KEY=                # REQUIRED for email features
SENTRY_DSN=                      # Optional: error tracking

# ─── Storage ───────────────────────────────────────
AWS_ACCESS_KEY_ID=               # Prefer IAM roles in production
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1
S3_BUCKET=

# ─── Monitoring ────────────────────────────────────
DD_API_KEY=
LOG_LEVEL=debug                  # debug | info | warn | error
```

### File Hierarchy

```
.env.example        → Committed to git. Keys only, no values. Safe defaults noted.
.env                → Local development. NEVER committed. In .gitignore.
.env.local          → Local overrides. NEVER committed.
.env.test           → Test environment. May be committed if no secrets.
.env.staging        → Reference only. Actual values in secret manager.
.env.production     → NEVER exists on disk. Pulled from secret manager at runtime.
```

## .gitignore Patterns (Required)

```gitignore
# Environment files
.env
.env.local
.env.*.local
.env.development
.env.staging
.env.production

# Secret files
*.pem
*.key
*.p12
*.pfx
secrets.json
secrets.yaml
credentials.json
service-account*.json

# Cloud credentials
.aws/credentials
.gcloud/

# Terraform state (may contain secrets)
*.tfstate
*.tfstate.backup
```

## Startup Validation Script

```python
#!/usr/bin/env python3
"""Validate required environment variables at application startup."""

import os
import sys
import re

REQUIRED_VARS = {
    "APP_SECRET": {"min_length": 32, "description": "Application signing secret"},
    "DATABASE_URL": {"pattern": r"^postgres(ql)?://", "description": "PostgreSQL connection string"},
    "AUTH_JWT_SECRET": {"min_length": 32, "description": "JWT signing secret"},
}

REQUIRED_IN_PRODUCTION = {
    "STRIPE_SECRET_KEY": {"pattern": r"^sk_(live|test)_", "description": "Stripe secret key"},
    "STRIPE_WEBHOOK_SECRET": {"pattern": r"^whsec_", "description": "Stripe webhook secret"},
    "SENDGRID_API_KEY": {"pattern": r"^SG\.", "description": "SendGrid API key"},
    "SENTRY_DSN": {"pattern": r"^https://", "description": "Sentry DSN"},
}

def validate() -> list[str]:
    errors = []
    env = os.environ.get("APP_ENV", "development")

    vars_to_check = dict(REQUIRED_VARS)
    if env == "production":
        vars_to_check.update(REQUIRED_IN_PRODUCTION)

    for var_name, rules in vars_to_check.items():
        value = os.environ.get(var_name, "")

        if not value:
            errors.append(f"MISSING: {var_name} — {rules['description']}")
            continue

        if "min_length" in rules and len(value) < rules["min_length"]:
            errors.append(
                f"TOO SHORT: {var_name} is {len(value)} chars, need {rules['min_length']}+"
            )

        if "pattern" in rules and not re.match(rules["pattern"], value):
            errors.append(
                f"INVALID FORMAT: {var_name} does not match expected pattern"
            )

    return errors

if __name__ == "__main__":
    errors = validate()
    if errors:
        print("Environment validation FAILED:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        sys.exit(1)
    print("Environment validation passed.")
```

## Secret Leak Detection

### Git History Scanner

```bash
#!/bin/bash
# Scan git history for leaked secrets

echo "Scanning git history for potential secrets..."

PATTERNS=(
  'AKIA[0-9A-Z]{16}'                          # AWS Access Key
  'AIza[0-9A-Za-z\-_]{35}'                    # Google API Key
  'sk_(live|test)_[0-9a-zA-Z]{24,}'           # Stripe Secret Key
  'ghp_[0-9a-zA-Z]{36}'                       # GitHub Personal Access Token
  'glpat-[0-9a-zA-Z\-]{20,}'                  # GitLab Personal Access Token
  'xoxb-[0-9]{10,}-[0-9]{10,}-[a-zA-Z0-9]{24}' # Slack Bot Token
  'SG\.[0-9A-Za-z\-_]{22}\.[0-9A-Za-z\-_]{43}' # SendGrid API Key
  '-----BEGIN (RSA |EC )?PRIVATE KEY-----'      # Private Keys
  'password\s*=\s*["\x27][^"\x27]{8,}["\x27]'  # Hardcoded passwords
)

FOUND=0
for pattern in "${PATTERNS[@]}"; do
  MATCHES=$(git log -p --all -S "$pattern" --format="%H %an %ad %s" 2>/dev/null | head -20)
  if [ -n "$MATCHES" ]; then
    echo ""
    echo "FOUND pattern: $pattern"
    echo "$MATCHES"
    FOUND=$((FOUND + 1))
  fi
done

if [ "$FOUND" -gt 0 ]; then
  echo ""
  echo "WARNING: Found $FOUND potential secret patterns in git history."
  echo "Run 'git filter-repo' or BFG Repo-Cleaner to remove them."
  exit 1
else
  echo "No secrets detected in git history."
fi
```

### Pre-Commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit — block commits containing secrets

PATTERNS=(
  'AKIA[0-9A-Z]{16}'
  'sk_(live|test)_[0-9a-zA-Z]{24,}'
  'ghp_[0-9a-zA-Z]{36}'
  '-----BEGIN (RSA |EC )?PRIVATE KEY-----'
)

FILES=$(git diff --cached --name-only --diff-filter=ACM)

for file in $FILES; do
  for pattern in "${PATTERNS[@]}"; do
    if git diff --cached -- "$file" | grep -qE "$pattern"; then
      echo "BLOCKED: Potential secret detected in $file"
      echo "Pattern: $pattern"
      echo "Remove the secret and try again."
      exit 1
    fi
  done
done
```

## Credential Rotation Playbook

### Step 1: Scope the Secret

```bash
# Find everywhere a secret is referenced
SECRET_NAME="STRIPE_SECRET_KEY"

# In code
grep -r "$SECRET_NAME" src/ lib/ app/ --include="*.ts" --include="*.py" -l

# In CI/CD
grep -r "$SECRET_NAME" .github/ .gitlab-ci.yml docker-compose.yml -l

# In infrastructure
grep -r "$SECRET_NAME" terraform/ k8s/ helm/ -l 2>/dev/null

# In secret managers
vault kv get -field=$SECRET_NAME secret/myapp/prod 2>/dev/null
aws ssm get-parameter --name "/myapp/prod/$SECRET_NAME" 2>/dev/null
doppler secrets get $SECRET_NAME --project myapp --config prod 2>/dev/null
```

### Step 2: Generate New Secret

```bash
# Generic secret (32 bytes, base64)
openssl rand -base64 32

# JWT secret (64 bytes for HS256)
openssl rand -base64 64

# API key format (alphanumeric)
openssl rand -hex 32
```

### Step 3: Dual-Write Period

```
Timeline:
─────────────────────────────────────────────────────
T+0:   Generate new secret
T+1:   Deploy code that accepts BOTH old and new secrets
T+2:   Update secret in ALL locations to new value
T+3:   Verify all services work with new secret
T+4:   Deploy code that accepts ONLY new secret
T+5:   Invalidate/revoke old secret
T+6:   Monitor for 24 hours for any auth failures
─────────────────────────────────────────────────────
```

### Step 4: Verify and Monitor

```bash
# Check for auth failures in logs (24 hours after rotation)
# Replace with your actual log query
grep -i "unauthorized\|auth.*fail\|invalid.*token" /var/log/app/*.log | tail -20

# Verify new credentials work
curl -s -o /dev/null -w "%{http_code}" \
  -H "Authorization: Bearer $NEW_TOKEN" \
  https://api.myapp.com/health
```

## Secret Manager Integration

### HashiCorp Vault

```bash
# Authenticate via OIDC
export VAULT_ADDR="https://vault.company.com"
vault login -method=oidc

# Store secrets
vault kv put secret/myapp/prod \
  DATABASE_URL="postgres://user:pass@host/db" \
  APP_SECRET="$(openssl rand -base64 32)" \
  STRIPE_SECRET_KEY="sk_live_..."

# Read secrets into environment
eval $(vault kv get -format=json secret/myapp/prod | \
  jq -r '.data.data | to_entries[] | "export \(.key)=\(.value|@sh)"')

# Rotate a single secret
vault kv patch secret/myapp/prod \
  APP_SECRET="$(openssl rand -base64 32)"
```

### AWS SSM Parameter Store

```bash
# Store as encrypted parameter
aws ssm put-parameter \
  --name "/myapp/prod/DATABASE_URL" \
  --value "postgres://..." \
  --type "SecureString" \
  --key-id "alias/myapp-secrets" \
  --overwrite

# Read all parameters for an environment
aws ssm get-parameters-by-path \
  --path "/myapp/prod/" \
  --with-decryption \
  --query "Parameters[*].[Name,Value]" \
  --output text
```

### Doppler

```bash
# Set up project
doppler setup --project myapp --config prod

# Run with secrets injected (recommended for production)
doppler run -- node server.js

# Download for local dev
doppler secrets download --no-file --format env > .env.local
```

## Environment Drift Detection

```bash
#!/bin/bash
# Compare environment variable keys between staging and production

STAGING_KEYS=$(doppler secrets --project myapp --config staging --format json | \
  jq -r 'keys[]' | sort)
PROD_KEYS=$(doppler secrets --project myapp --config prod --format json | \
  jq -r 'keys[]' | sort)

ONLY_STAGING=$(comm -23 <(echo "$STAGING_KEYS") <(echo "$PROD_KEYS"))
ONLY_PROD=$(comm -13 <(echo "$STAGING_KEYS") <(echo "$PROD_KEYS"))

if [ -n "$ONLY_STAGING" ]; then
  echo "DRIFT: Keys in STAGING but NOT in PROD:"
  echo "$ONLY_STAGING" | sed 's/^/  /'
fi

if [ -n "$ONLY_PROD" ]; then
  echo "DRIFT: Keys in PROD but NOT in STAGING:"
  echo "$ONLY_PROD" | sed 's/^/  /'
fi

[ -z "$ONLY_STAGING" ] && [ -z "$ONLY_PROD" ] && echo "No drift detected."
```

## Common Pitfalls

- **Committing .env to git** — add `.env` to .gitignore on day 1; use pre-commit hooks as a safety net
- **Echoing secrets in CI logs** — never `echo $SECRET`; mask variables in CI settings
- **Rotating in only one location** — secrets exist in CI, hosting, Docker, K8s; update ALL locations
- **Weak secrets** — `APP_SECRET=mysecret` is not a secret; use `openssl rand -base64 32`
- **Shared secrets across environments** — dev and prod must have different secrets, always
- **No monitoring after rotation** — watch for auth failures for 24 hours after rotating credentials
- **.env.example with real values** — example files are public; strip everything sensitive
- **Long-lived credentials** — prefer short-lived tokens (OIDC, instance roles) over permanent API keys

## Best Practices

1. **Secret manager is source of truth** — .env files are for local dev only; never in production
2. **Rotate on a schedule** — quarterly minimum for long-lived keys, not just after incidents
3. **Principle of least privilege** — each service gets its own API key with minimal permissions
4. **Validate at startup** — fail fast on missing required variables before serving traffic
5. **Never log secrets** — add middleware that redacts known secret patterns from log output
6. **Use short-lived credentials** — prefer OIDC/instance roles over long-lived access keys
7. **Audit access** — log every secret read in Vault/SSM; alert on anomalous access patterns
8. **Document rotation playbooks** — write them before an incident, not during one

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Startup validation fails with MISSING for a set variable | Variable is set in `.env` but the app reads from a different file (e.g., `.env.local` overrides it to empty) | Check file hierarchy load order; ensure the correct `.env.*` file is loaded and no override blanks the value |
| Pre-commit hook passes but CI detects a leaked secret | Pre-commit patterns list is out of date or does not cover the token format CI scans for | Sync the regex pattern list between the pre-commit hook and CI scanner; add the missing pattern |
| `vault kv get` returns "permission denied" | OIDC token expired or the Vault policy does not grant read access to the target path | Re-authenticate with `vault login -method=oidc` and verify the policy includes `read` capability on the secret path |
| Environment drift detection shows false positives | One environment uses a prefix convention (e.g., `NEXT_PUBLIC_`) that the other does not | Add an exclusion list of known environment-specific keys to the drift script |
| Secret rotation causes service outage | Code was deployed without the dual-read period; only the new secret is accepted immediately | Always deploy the dual-read code change first, then update the secret value, then remove old-secret support |
| `.env.example` accidentally contains real credentials | Developer copied `.env` to `.env.example` without stripping values | Run the auto-generation script to rebuild `.env.example` from `.env` with values stripped; add a CI check that `.env.example` values match safe defaults only |
| AWS SSM `put-parameter` fails with AccessDeniedException | IAM role lacks `ssm:PutParameter` or `kms:Encrypt` permissions for the target key | Attach the required IAM policy granting `ssm:PutParameter` and `kms:Encrypt` on the KMS key alias used for SecureString |

## Success Criteria

- **Zero secrets in git history** — secret leak scanner reports 0 findings across all branches
- **100% startup validation coverage** — every required variable is declared in the validation script; no production deploy starts with missing vars
- **Rotation completed within SLA** — credential rotation finishes within 4 hours of incident detection, including dual-write period and verification
- **Environment drift below 5%** — staging and production variable key sets differ by no more than 5% (intentional differences documented)
- **Pre-commit hook adoption at 100%** — every contributor has the secret-blocking pre-commit hook installed and active
- **Quarterly rotation compliance** — all long-lived credentials are rotated at least once per quarter with audit trail in the secret manager
- **Post-rotation monitoring green** — zero authentication failures attributed to stale credentials in the 24-hour window after each rotation

## Scope & Limitations

**This skill covers:**
- `.env` file scaffolding, hierarchy, and validation for any language/framework
- Secret leak detection in git history, staged files, and working tree
- Credential rotation playbooks with zero-downtime dual-read strategy
- Integration patterns for HashiCorp Vault, AWS SSM, 1Password CLI, and Doppler

**This skill does NOT cover:**
- Runtime secret injection in Kubernetes (see `engineering/ci-cd-pipeline-builder` for deployment pipeline secrets)
- Infrastructure-as-code for provisioning Vault clusters or SSM policies (see `engineering/ci-cd-pipeline-builder`)
- Application-level encryption at rest or in transit (see `engineering/api-design-reviewer` for API security patterns)
- Identity and access management (IAM) role design or SSO/OIDC provider configuration (see `ra-qm-team/` compliance skills for access control frameworks)

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `engineering/ci-cd-pipeline-builder` | Inject secrets from Vault/SSM/Doppler into CI/CD pipeline stages | Rotation playbook outputs feed pipeline secret-update steps |
| `engineering/dependency-auditor` | Flag dependencies that bundle or require hardcoded credentials | Dependency audit findings trigger secret leak scans on affected repos |
| `engineering/skill-security-auditor` | Validate that no skill packages ship embedded secrets or credentials | Security audit references this skill's regex patterns for detection |
| `engineering/codebase-onboarding` | Include `.env.example` setup and secret-manager access in onboarding checklists | Onboarding workflow consumes the `.env` hierarchy and validation script |
| `engineering/observability-designer` | Monitor authentication failures post-rotation; alert on anomalous secret access | Post-rotation verification metrics flow into observability dashboards |
| `ra-qm-team/soc2-compliance-auditor` | Demonstrate secret management controls for SOC 2 CC6.1 and CC6.6 criteria | Rotation audit logs and access policies serve as SOC 2 evidence artifacts |
