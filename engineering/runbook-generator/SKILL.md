---
name: runbook-generator
description: >
  Drafts, validates and ages operational runbooks (deploy, incident, database, scaling,
  monitoring) with stack-specific commands, VERIFY steps and rollback. Use when bootstrapping
  ops docs, preparing on-call, or after an incident.
license: MIT + Commons Clause
metadata:
  version: 1.2.0
  author: borghei
  category: engineering
  domain: site-reliability
  tier: POWERFUL
  updated: 2026-11-08
  frameworks: github-actions, vercel, aws, kubernetes, postgresql
  tags:
    - runbooks
    - incident-response
    - sre
    - operations
    - rollback
---
# Runbook Generator

The agent writes runbooks an on-call engineer can follow at 3 a.m.: numbered steps with copy-paste commands, a VERIFY line after every step, a rollback for every destructive action, an escalation table, and an owner plus a last-verified date so staleness can be measured.

## When to Use

- A service has no runbooks and you need a first set.
- Existing runbooks are outdated, incomplete or fail review.
- Onboarding someone onto the on-call rotation, or preparing an incident drill.
- After an incident: fold the lessons into the runbook and re-date it.

## Clarify First

Before generating the runbook, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Runbook type:** deployment / incident / database / scaling / monitoring (selects the template).
- **Actual stack:** hosting, database, CI/CD, framework and migration command (every command and rollback is stack-specific).
- **Escalation contacts:** who is paged at L1, L2 and L3 (a runbook without them is unusable on-call).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Workflow

1. **Detect the stack yourself.** The tools do not read the repo. Look for CI files, `docker-compose*.yml`, `k8s/`, `fly.toml`, `vercel.json`, ORM config (`alembic.ini`, `prisma/schema.prisma`, `manage.py`). The detection commands are in [references/runbook-templates.md](references/runbook-templates.md).
2. **Write the service definition JSON** (shape: `assets/sample_service.json`). Set `stack.migrate_command` when the framework default would be wrong, and list `config_files` so drift can be checked.
3. **Scaffold** each runbook type you need with `runbook_scaffolder.py`.
4. **Replace every FILL IN** with real values and tailor the steps; the scaffold is a draft, not a verified procedure.
5. **Validate** with `runbook_validator.py --strict`. Fix every finding; `--strict` also fails on leftover FILL IN placeholders in commands.
6. **Dry-run in staging**, then set Last verified to the dry-run date. Done when the validator passes in strict mode and someone other than the author has run the steps.
7. **Keep it fresh:** run `staleness_checker.py` in CI so a runbook goes stale loudly, not silently.

## Quick Start

```bash
# from engineering/runbook-generator/; write output outside the repo
OUT=$(mktemp -d)
python3 scripts/runbook_scaffolder.py -i assets/sample_service.json --type deployment -o "$OUT/deploy.md"
python3 scripts/runbook_validator.py "$OUT/deploy.md" --strict        # exit 0: the draft is structurally complete
python3 scripts/runbook_validator.py assets/flawed_runbook.md       # exit 1: 7 errors (no rollback, hardcoded DB URL, ...)
```

```bash
python3 scripts/staleness_checker.py assets/flawed_runbook.md --as-of 2026-03-01   # exit 1: critical, 415 days
```

## Tools Overview

| Tool | Purpose | Key flags | Exit codes |
|------|---------|-----------|------------|
| `scripts/runbook_scaffolder.py` | Runbook draft from a service JSON; commands derived from hosting, database, CI and framework | `-i FILE\|-`, `--type deployment\|incident\|database\|scaling\|monitoring`, `-o FILE`, `--format markdown\|json` | 0 written; 2 bad input |
| `scripts/runbook_validator.py` | Required sections per type, VERIFY lines, time estimates, Owner / Last verified, escalation table, hardcoded DB credentials, placeholders in commands | `FILES...`, `--dir DIR`, `--strict`, `--format json` | 0 valid; 1 findings; 2 missing file or no input |
| `scripts/staleness_checker.py` | Age of each runbook's Last verified date, plus config files changed since then (via `git log`) | `PATHS...`, `--threshold 90`, `--warning 60`, `--critical 180`, `--as-of YYYY-MM-DD`, `--repo-root`, `--json` | 0 fresh or warning; 1 stale or critical; 2 bad input |

Pass `--as-of` to the staleness checker when you need a reproducible result; without it, age is measured from today.

## Anti-Patterns

**Mistake:** Shipping the scaffold as the runbook.
**Why it matters:** The scaffold's Last verified date is the generation date, and its steps have never been run; on-call will trust both.
**Instead:** Replace FILL IN values, dry-run in staging, then re-date it.

**Mistake:** A deploy step with no rollback, or a rollback that only reverts the code.
**Why it matters:** Schema migrations and data changes outlive a code rollback; the incident gets worse when the old code meets the new schema.
**Instead:** Pair each migration with its down path or a restore-from-backup step, and say which steps cannot be undone.

**Mistake:** Hardcoding connection strings or tokens in commands.
**Why it matters:** Runbooks are copied into tickets and chat; credentials leak and go stale.
**Instead:** Use environment variables (`$PROD_DB_URL`); the validator flags inline database URLs as errors.

## Reference Documentation

- **[references/runbook-templates.md](references/runbook-templates.md)**: stack-detection commands plus full deployment, incident and database templates. Read when scanning a repo or writing a runbook by hand.
- **[references/staleness-and-maintenance.md](references/staleness-and-maintenance.md)**: the staleness CI job and the quarterly review process. Read when automating freshness checks.
- **[references/quality-and-troubleshooting.md](references/quality-and-troubleshooting.md)**: pitfalls, best-practice checklist, troubleshooting and the success bar. Read before shipping a runbook.

## Files

| File | Purpose |
|------|---------|
| `scripts/runbook_scaffolder.py` | Draft generator (stdlib only) |
| `scripts/runbook_validator.py` | Completeness and quality gate |
| `scripts/staleness_checker.py` | Freshness and config-drift gate |
| `assets/sample_service.json` | FastAPI + PostgreSQL + Kubernetes service; all five types pass `--strict` |
| `assets/flawed_runbook.md` | Deliberately incomplete runbook; validator exits 1 |

## Scope & Limitations

**Covers:** drafting deployment, incident, database, scaling and monitoring runbooks; validating structure and safety markers; staleness and config-drift checks.

**Does not cover:**
- Running runbook steps; it writes documentation, not automation (see `engineering/ci-cd-pipeline-builder`).
- Infrastructure provisioning (see `engineering/terraform-patterns`).
- Alert rules and dashboards (see `engineering/observability-designer`).
- Live incident coordination (see `engineering/incident-commander`) and security incident playbooks (see `engineering/security-audit`).
- The validator checks structure, not truth: it cannot tell whether a command works on your system.
