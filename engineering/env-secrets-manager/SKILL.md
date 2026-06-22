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
  updated: 2026-06-17
  frameworks: vault, aws-ssm, 1password-cli, doppler
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

Before running, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Task** — scaffold/validate a `.env`, scan for leaked secrets, or check env drift (selects `env_validator.py` vs `secret_scanner.py` vs `env_sync_checker.py`)
- [ ] **Target paths** — the `.env`/`.env.example` files or directory to scan (the input the tools read)
- [ ] **Secret manager** — Vault, AWS SSM, 1Password, or Doppler (determines the integration and rotation commands generated)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `env_validator.py` | Validate a `.env` against `.env.example`: missing/extra vars, empty secrets, leaked credentials | `python scripts/env_validator.py .env.example .env --strict --check-secrets` |
| `secret_scanner.py` | Scan a directory/file for hardcoded secrets via pattern matching | `python scripts/secret_scanner.py ./src --severity high --json` |
| `env_sync_checker.py` | Compare env configs across dev/staging/prod and report drift | `python scripts/env_sync_checker.py .env.* --baseline .env.example` |

## References

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
| `ra-qm-team/soc2-compliance-auditor` | Demonstrate secret management controls for SOC 2 CC6.1 and CC6.6 criteria | Rotation audit logs and access policies serve as SOC 2 evidence artifacts |
