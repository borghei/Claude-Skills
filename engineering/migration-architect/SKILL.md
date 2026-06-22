---
name: migration-architect
description: >
  Plans zero-downtime migrations with compatibility validation, rollback
  strategies, and phased execution plans. Use when migrating databases, APIs,
  infrastructure, or services between platforms or versions.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: infrastructure
  tier: POWERFUL
  updated: 2026-06-17
---
# Migration Architect

Generates phased migration plans with risk assessment, compatibility analysis, and rollback runbooks for database, service, infrastructure, and API migrations. Validates schema compatibility, detects breaking changes, and produces rollback procedures with trigger conditions and communication templates.

## Core Capabilities

- **Phased planning** — generate risk-assessed, multi-phase migration plans with validation gates, timelines, and stakeholder structures from a JSON spec.
- **Compatibility analysis** — diff before/after database or REST/JSON schemas to detect breaking changes, type mismatches, and constraint violations, with migration + rollback scripts.
- **Rollback runbooks** — phase-by-phase reversal steps, automated trigger conditions, data-recovery plans, escalation matrices, and communication templates.
- **Pattern catalog** — Expand-Contract, Dual-Write, CDC, Strangler Fig, Parallel Run, Canary, Blue-Green.
- **Risk frameworks** — technical, business, operational, and compliance risk categories.

## When to Use

- Migrating databases, APIs, infrastructure, or services between platforms or versions.
- Validating schema/API compatibility and detecting breaking changes before cutover.
- Building rollback runbooks and zero-downtime execution plans.

## Clarify First

Before planning the migration, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **What's migrating** — database, API, infrastructure, or service (sets `--type` and which pattern catalog applies)
- [ ] **Deliverable** — phased plan, compatibility diff, or rollback runbook (selects `migration_planner.py` vs `compatibility_checker.py` vs `rollback_generator.py`)
- [ ] **Downtime budget & pattern** — zero-downtime requirement and which pattern (expand-contract, dual-write, strangler fig, blue-green) (drives the phases and cutover technique)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `migration_planner.py` | Generate a phased migration plan with risk assessment | `python scripts/migration_planner.py --input spec.json --output plan.json --format both` |
| `compatibility_checker.py` | Diff schemas/APIs and flag breaking changes | `python scripts/compatibility_checker.py --before v1.json --after v2.json --type database` |
| `rollback_generator.py` | Generate a rollback runbook from a plan | `python scripts/rollback_generator.py --input plan.json --output runbook.json --format both` |

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/workflows-patterns-and-quality.md](references/workflows-patterns-and-quality.md)** — quick-start commands, the three core workflows with validation checkpoints, the migration-pattern catalog table, anti-patterns, troubleshooting, and success criteria. Read when planning a migration.
- **[references/tool-reference.md](references/tool-reference.md)** — full per-tool purpose, usage, flag tables, input formats, and output structures for all three scripts. Read before running or debugging the scripts.
- **[references/migration_patterns_catalog.md](references/migration_patterns_catalog.md)** — deep catalog of migration patterns with mechanics and trade-offs. Read when choosing a pattern.
- **[references/zero_downtime_techniques.md](references/zero_downtime_techniques.md)** — techniques for cutover without downtime (expand-contract, dual-write, traffic shifting). Read when downtime budget is near zero.
- **[references/data_reconciliation_strategies.md](references/data_reconciliation_strategies.md)** — checksum/business-logic validation strategies to confirm data integrity post-migration. Read when verifying migrated data.

## Scope & Limitations

**This skill covers:**
- End-to-end migration planning for databases, services, infrastructure, and APIs with phased execution and validation gates.
- Automated compatibility analysis between schema versions (SQL and REST/JSON) including breaking-change detection and migration script generation.
- Rollback runbook generation with trigger conditions, data recovery plans, escalation matrices, and communication templates.
- Risk assessment frameworks covering technical, business, operational, and compliance risk categories.

**This skill does NOT cover:**
- Actual execution of migrations against live systems -- the tools generate plans, reports, and scripts but do not connect to databases or cloud APIs.
- Application-level code refactoring required to support new schemas or APIs; see `engineering/api-design-reviewer` for API contract changes and `engineering/database-designer` for schema design.
- Real-time monitoring, alerting, or dashboard provisioning during migration execution; see `engineering/observability-designer` for observability setup.
- Cloud cost optimization or capacity planning for target infrastructure; see `engineering/ci-cd-pipeline-builder` for deployment pipeline configuration.

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `engineering/database-designer` | Design target schema before migration planning | Target schema JSON feeds into `compatibility_checker.py --after` |
| `engineering/api-design-reviewer` | Validate API contract changes for service migrations | OpenAPI spec diffs feed into `compatibility_checker.py --type api` |
| `engineering/observability-designer` | Set up monitoring dashboards referenced in migration runbooks | Migration plan success metrics inform alerting rule definitions |
| `engineering/ci-cd-pipeline-builder` | Embed migration validation in CI/CD stages | `compatibility_checker.py` runs as a pipeline stage; `migration_planner.py --validate` gates deployments |
| `engineering/runbook-generator` | Extend rollback runbooks with operational procedures | `rollback_generator.py` output serves as input for detailed operational runbooks |
| `engineering/release-manager` | Coordinate migration cutover with release schedules | Migration plan phases and timelines align with release windows and feature-flag rollout stages |
