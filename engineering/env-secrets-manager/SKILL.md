---
name: env-secrets-manager
description: >
  Environment and secrets management lifecycle: .env scaffolding, validation, leak detection,
  and rotation across Vault, AWS SSM, 1Password, and Doppler. Use when setting up projects,
  scanning for leaked secrets, or rotating credentials.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: security-devops
  tier: POWERFUL
  updated: 2026-11-08
  frameworks: vault, aws-ssm, 1password-cli, doppler
  tags:
    - secrets
    - env-files
    - vault
    - secret-rotation
    - leak-detection
---
# Env & Secrets Manager

Complete environment variable and secrets management lifecycle: .env file structure across dev/staging/production, .env.example auto-generation that strips sensitive values, required-variable validation at startup, secret leak detection in git history, credential rotation playbooks, environment drift detection, and integration with HashiCorp Vault, AWS SSM, 1Password CLI, and Doppler.

## Core Capabilities

- **.env lifecycle** — structured layout with categorized sections, auto-generated `.env.example` (strips secrets), environment-specific files, and fail-fast startup validation.
- **Secret leak detection** — regex scan of git history, working tree, and staged files; pre-commit hooks; patterns for API keys, tokens, passwords, private keys.
- **Credential rotation** — per-secret playbooks, scope analysis, zero-downtime dual-read rotation, post-rotation verification and monitoring.
- **Secret manager integration** — HashiCorp Vault (KV v2 + OIDC), AWS SSM Parameter Store (KMS), 1Password CLI (template injection), Doppler (project/config).
- **Drift detection** — compare variable key sets between staging and production and report missing/extra keys.

## When to Use

- Setting up a new project — scaffold .env.example and validation.
- Before every commit — scan for accidentally staged secrets.
- Post-incident — rotate leaked credentials systematically.
- Onboarding developers — provide complete environment setup.
- Auditing — detect environment drift between staging and production.
- Compliance — demonstrate secret management practices.

## Clarify First

Before running, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Task:** scaffold/validate a `.env`, scan for leaked secrets, or check env drift (selects `env_validator.py` vs `secret_scanner.py` vs `env_sync_checker.py`).
- **Target paths:** the `.env`/`.env.example` files or directory to scan (the input the tools read).
- **Secret manager:** Vault, AWS SSM, 1Password, or Doppler (determines the integration and rotation commands generated).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Workflow

1. **Scan first.** Run `secret_scanner.py` over the repository (and `git log -p` output or a history scanner such as gitleaks for past commits). Any high-severity hit is treated as leaked: rotate it before cleaning history, because the old value is already exposed.
2. **Validate each environment** against `.env.example` with `env_validator.py`; missing required variables fail, extras fail under `--strict`.
3. **Check drift** between environments with `env_sync_checker.py`. By default only missing and extra keys count; values are expected to differ between staging and production. Add `--compare-values` for environments that should be identical (blue and green, two regions).
4. **Move secrets to a manager** (Vault, AWS SSM, 1Password, Doppler) using `references/secret-manager-integration.md`, and leave only `${VAR}` references or placeholders in files.
5. **Verify**: the scanner reports nothing at high severity, every environment validates, drift is within the target, and rotated credentials are confirmed working.

## Quick Start

```bash
python3 scripts/secret_scanner.py assets/sample_leaky_config.py                       # 2 high, 1 medium (exit 1); all values fake
python3 scripts/env_validator.py assets/sample.env.example assets/sample.env.staging --check-secrets   # passes with warnings (exit 0)
python3 scripts/env_validator.py assets/sample.env.example assets/sample.env.production --strict       # missing + extra key (exit 1)
python3 scripts/env_sync_checker.py assets/sample.env.staging assets/sample.env.production --baseline assets/sample.env.example  # key drift (exit 1)
```

## Tools Overview

| Tool | What it does | Key flags | Exit codes |
|------|--------------|-----------|------------|
| `secret_scanner.py <path>` | Regex scan for AWS/Google/Stripe/GitHub/GitLab/Slack/SendGrid keys, private keys, JWTs, password assignments and credentialed connection strings; values are redacted in output | `--severity low|medium|high`, `--include`, `--exclude`, `--json` | 0 none found, 1 findings, 2 bad path |
| `env_validator.py <reference> <target>` | Missing and extra variables, empty or placeholder secrets; `--check-secrets` also checks the reference file for real-looking values | `--strict`, `--check-secrets`, `--json` | 0 valid, 1 errors, 2 bad input |
| `env_sync_checker.py <files...>` | Missing/extra keys per environment pair and against a baseline; differing values listed (redacted) | `--baseline`, `--compare-values`, `--show-values`, `--json` | 0 drift within 5%, 1 drift or baseline gaps, 2 a file not found |

## Anti-Patterns

**Mistake:** Deleting a leaked secret from the latest commit and calling it fixed.
**Why it happens:** The scanner goes quiet once the line is gone.
**Instead:** The value is in history, forks and CI logs. Rotate it first, then purge history if policy requires.

**Mistake:** Real values in `.env.example`.
**Why it happens:** Copying the working `.env` is the fastest way to create the example.
**Instead:** Placeholders only; run `env_validator.py --check-secrets` on the example in CI.

**Mistake:** Counting every differing value as configuration drift.
**Why it happens:** A diff of two files shows every line that changed.
**Instead:** Hosts and credentials should differ between environments. Track key drift by default and compare values only where environments must match.

## Files

- `scripts/secret_scanner.py`, `scripts/env_validator.py`, `scripts/env_sync_checker.py` — the tools above.
- `assets/sample.env.example`, `assets/sample.env.staging`, `assets/sample.env.production` — environments with deliberate key drift; `assets/sample_leaky_config.py` — scanner demo with fake credentials (the AWS key is AWS's documented example).

## Reference Documentation

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/env-file-structure.md](references/env-file-structure.md)** — canonical `.env` layout, the `.env.*` file hierarchy, required `.gitignore` patterns, and the full Python startup-validation script. Read when scaffolding a project or wiring validation.
- **[references/leak-detection-and-rotation.md](references/leak-detection-and-rotation.md)** — the git-history secret scanner, pre-commit hook, the 4-step credential rotation playbook (scope, generate, dual-write, verify), and the environment-drift detection script. Read when scanning for leaks or rotating credentials.
- **[references/secret-manager-integration.md](references/secret-manager-integration.md)** — concrete Vault, AWS SSM, and Doppler commands for storing, reading, and rotating secrets. Read when integrating a secret manager.
- **[references/best-practices-and-troubleshooting.md](references/best-practices-and-troubleshooting.md)** — common pitfalls, the 8 best practices, the troubleshooting table, and the success-criteria bar. Read when reviewing a setup or debugging.

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
| `ra-qm-team/soc2-compliance-expert` | Demonstrate secret management controls for SOC 2 CC6.1 and CC6.6 criteria | Rotation audit logs and access policies serve as SOC 2 evidence artifacts |
