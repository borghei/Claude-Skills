---
name: runbook-generator
description: >
  Generate operational runbooks from codebase analysis covering deployment, incident response,
  scaling, and monitoring, with copy-paste commands and rollback steps. Use when bootstrapping
  ops docs, preparing for on-call, or post-incident.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: site-reliability
  tier: POWERFUL
  updated: 2026-06-17
  frameworks: github-actions, vercel, aws, kubernetes, postgresql
---
# Runbook Generator

Analyze a codebase and generate production-grade operational runbooks with copy-paste commands, verification checks after every step, rollback procedures for every destructive action, escalation paths with contact information, and time estimates for capacity planning. Detects the stack (CI/CD, database, hosting, containers) and produces runbooks tailored to the actual infrastructure. Includes staleness detection to flag runbooks when referenced config files change.

**Keywords:** runbook, operational procedures, incident response, deployment, rollback, database maintenance, scaling, monitoring, on-call, SRE, postmortem

## Core Capabilities

- **Stack detection** — identify CI/CD platform, database, hosting, and orchestration from repo files; map to runbook templates; extract connection strings, deploy commands, and infra details.
- **Runbook types** — deployment (pre-checks, deploy, smoke tests, rollback), incident response (triage→diagnose→mitigate→resolve→postmortem), database maintenance (backup, migration, vacuum, reindex), scaling (horizontal/vertical), and monitoring (alerts, dashboards, on-call rotation).
- **Format discipline** — numbered steps with copy-paste commands, a VERIFY check after EVERY step, time estimates, a rollback procedure for every destructive action, and escalation paths with decision criteria.
- **Maintenance** — staleness detection linked to config file modification dates, quarterly review cadence, and a staging dry-run validation framework.

## When to Use

- Codebase has no runbooks and you need to bootstrap them.
- Existing runbooks are outdated or incomplete.
- Onboarding a new engineer for on-call rotation.
- Preparing for an incident response drill.
- Post-incident improvement: updating runbooks with lessons learned.

## Clarify First

Before generating the runbook, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Runbook type** — deployment / incident response / database maintenance / scaling / monitoring (selects the template and step structure)
- [ ] **Actual stack** — CI/CD platform, database, hosting, and orchestration (every copy-paste command and rollback step is stack-specific)
- [ ] **Escalation contacts & severity routing** — who is paged at each level (fills the escalation table; a runbook without it is unusable on-call)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `runbook_scaffolder.py` | Generate runbook markdown templates from a JSON service definition | `python scripts/runbook_scaffolder.py -i service.json --type deployment -o runbook.md` |
| `runbook_validator.py` | Validate runbook markdown for completeness and quality (required sections, VERIFY blocks, hardcoded creds, escalation table) | `python scripts/runbook_validator.py --dir docs/runbooks --strict` |
| `staleness_checker.py` | Check runbook freshness against configurable staleness thresholds | `python scripts/staleness_checker.py docs/runbooks --threshold 90 --json` |

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/runbook-templates.md](references/runbook-templates.md)** — the stack-detection shell commands plus full deployment, incident response, and database maintenance runbook templates with copy-paste commands, VERIFY blocks, rollback, and escalation tables. Read when scanning a repo or writing a runbook.
- **[references/staleness-and-maintenance.md](references/staleness-and-maintenance.md)** — the staleness-detection CI script and the 7-step quarterly review process. Read when automating freshness checks or running a quarterly review.
- **[references/quality-and-troubleshooting.md](references/quality-and-troubleshooting.md)** — common pitfalls, the best-practice checklist, the troubleshooting table, and the success-criteria bar. Read before shipping a runbook.

## Scope & Limitations

**This skill covers:**
- Generating deployment, incident response, database maintenance, scaling, and monitoring runbooks from codebase analysis
- Stack detection for common CI/CD platforms (GitHub Actions, GitLab CI, Jenkins), databases (PostgreSQL, MySQL, MongoDB), and hosting providers (Vercel, Fly.io, Kubernetes, AWS)
- Staleness detection automation and quarterly review processes
- Escalation path templates with severity-based routing

**This skill does NOT cover:**
- Automated execution of runbook steps — it generates documentation, not orchestration (see `ci-cd-pipeline-builder` for automated pipelines)
- Infrastructure provisioning or Terraform/Pulumi code generation (see `migration-architect` for schema migration tooling)
- Observability stack setup such as Prometheus rules, Grafana dashboards, or alert definitions (see `observability-designer` for monitoring infrastructure)
- Security incident response or vulnerability remediation playbooks (see `skill-security-auditor` for security-focused analysis)

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `ci-cd-pipeline-builder` | Runbook deployment steps align with pipeline stages | Pipeline config feeds into deployment runbook generation; runbook rollback steps reference pipeline rollback triggers |
| `observability-designer` | Monitoring runbook references alert rules and dashboards | Observability outputs (alert names, dashboard URLs) are embedded in runbook VERIFY and Monitor steps |
| `migration-architect` | Database maintenance runbook uses migration tooling conventions | Migration file paths and commands flow into the database runbook template; rollback steps mirror migration rollback commands |
| `release-manager` | Release process triggers runbook execution checkpoints | Release tags and changelogs feed into runbook staleness checks; release gates reference runbook pre-deployment checklists |
| `env-secrets-manager` | Runbook commands reference env vars managed by secrets tooling | Secret names and vault paths flow into runbook env var references; rotation schedules inform runbook update cadence |
| `changelog-generator` | Post-deployment runbook steps cross-reference changelog entries | Changelog diffs help identify which runbook steps need re-verification after a release |
