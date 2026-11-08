---
name: migration-architect
description: >
  Plans zero-downtime migrations with compatibility validation, rollback
  strategies, and phased execution plans. Use when migrating databases, APIs,
  infrastructure, or services between platforms or versions.
license: MIT + Commons Clause
metadata:
  version: 1.2.0
  author: borghei
  category: engineering
  domain: infrastructure
  tier: POWERFUL
  updated: 2026-11-08
  tags:
    - migrations
    - zero-downtime
    - rollback
    - database-migration
    - infrastructure
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

Before planning the migration, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **What's migrating:** database, API, infrastructure, or service (sets `--type` and which pattern catalog applies).
- **Deliverable:** phased plan, compatibility diff, or rollback runbook (selects `migration_planner.py` vs `compatibility_checker.py` vs `rollback_generator.py`).
- **Downtime budget & pattern:** zero-downtime requirement and which pattern (expand-contract, dual-write, strangler fig, blue-green) (drives the phases and cutover technique).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Tools Overview

| Tool | Purpose | Command |
|------|---------|---------|
| `migration_planner.py` | Phased migration plan with risk assessment from a migration spec | `python3 scripts/migration_planner.py --input spec.json --output plan.json --format both` |
| `compatibility_checker.py` | Diff schemas or APIs and flag breaking changes | `python3 scripts/compatibility_checker.py --before v1.json --after v2.json --type database` |
| `rollback_generator.py` | Rollback runbook from the planner's plan JSON (not from the spec) | `python3 scripts/rollback_generator.py --input plan.json --output runbook.json --format both` |

**Exit codes:** 0 done (compatibility checker: no breaking changes); 1 compatibility checker found potentially breaking changes; 2 unusable input (missing file, invalid JSON, missing required fields). A CI gate can therefore tell a real finding from a typo in a path.

## Quick Start

The tools chain: spec, then plan, then runbook. Run from `engineering/migration-architect/` and write outputs outside the repo.

```bash
OUT=$(mktemp -d)
python3 scripts/migration_planner.py --input assets/sample_database_migration.json --output "$OUT/plan.json" --format json
python3 scripts/rollback_generator.py --input "$OUT/plan.json" --format text
python3 scripts/compatibility_checker.py --before assets/database_schema_before.json --after assets/database_schema_after.json --type database
```

## Reference Documentation

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/workflows-patterns-and-quality.md](references/workflows-patterns-and-quality.md)** — quick-start commands, the three core workflows with validation checkpoints, the migration-pattern catalog table, anti-patterns, troubleshooting, and success criteria. Read when planning a migration.
- **[references/tool-reference.md](references/tool-reference.md)** — full per-tool purpose, usage, flag tables, input formats, and output structures for all three scripts. Read before running or debugging the scripts.
- **[references/migration_patterns_catalog.md](references/migration_patterns_catalog.md)** — deep catalog of migration patterns with mechanics and trade-offs. Read when choosing a pattern.
- **[references/zero_downtime_techniques.md](references/zero_downtime_techniques.md)** — techniques for cutover without downtime (expand-contract, dual-write, traffic shifting). Read when downtime budget is near zero.
- **[references/data_reconciliation_strategies.md](references/data_reconciliation_strategies.md)** — checksum/business-logic validation strategies to confirm data integrity post-migration. Read when verifying migrated data.

## Anti-Patterns

**Mistake:** A migration plan without a tested rollback.
**Why it matters:** The moment you need the rollback is the worst moment to discover it does not work.
**Instead:** Generate the runbook from the plan and rehearse it in staging before cutover.

**Mistake:** Contract changes in one step (rename or drop in the same release that stops writing the old shape).
**Why it matters:** Old and new code run side by side during a deploy; a one-step change breaks whichever version is still live.
**Instead:** Expand, migrate, contract: add the new shape, dual-write and backfill, switch reads, then remove the old shape in a later release.

**Mistake:** Treating a passing compatibility check as proof of safety.
**Why it matters:** The checker compares declared schemas; it cannot see data volume, lock time or consumers it was not told about.
**Instead:** Pair it with a dry run on production-sized data and a consumer inventory.

## Files

| File | Purpose |
|------|---------|
| `scripts/migration_planner.py`, `scripts/compatibility_checker.py`, `scripts/rollback_generator.py` | Stdlib CLIs |
| `assets/sample_database_migration.json`, `assets/sample_service_migration.json` | Migration specs for the planner |
| `assets/database_schema_before.json`, `assets/database_schema_after.json` | Schema pair for the compatibility checker (breaking changes, exit 1) |
| `expected_outputs/` | Example outputs |

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
