---
name: migration-architect
description: >
  Plans zero-downtime migrations with compatibility validation, rollback
  strategies, and phased execution plans. Use when migrating databases, APIs,
  infrastructure, or services between platforms or versions.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: infrastructure
  tier: POWERFUL
  updated: 2026-03-31
---
# Migration Architect

The agent generates phased migration plans with risk assessment, compatibility analysis, and rollback runbooks for database, service, infrastructure, and API migrations. It validates schema compatibility, detects breaking changes, and produces rollback procedures with trigger conditions and communication templates.

## Quick Start

```bash
# Generate a phased migration plan
python scripts/migration_planner.py --input migration_spec.json --output plan.json --format both

# Check schema compatibility between versions
python scripts/compatibility_checker.py --before v1_schema.json --after v2_schema.json --type database

# Generate rollback runbook from a migration plan
python scripts/rollback_generator.py --input plan.json --output runbook.json --format both
```

---

## Core Workflows

### Workflow 1: Plan a Database Migration

1. Create migration spec JSON with `type: "database"`, source, target, constraints (data volume, max downtime, dependencies)
2. Run `migration_planner.py` to generate phased plan with risk assessment
3. Run `compatibility_checker.py` to detect breaking schema changes
4. Review generated phases -- each should have validation criteria and rollback triggers
5. **Validation checkpoint:** Zero unaddressed breaking changes; every phase has rollback steps; downtime within `max_downtime_minutes` constraint

```bash
python scripts/compatibility_checker.py --before v1.json --after v2.json --type database --format json
python scripts/migration_planner.py --input spec.json --output plan.json
python scripts/rollback_generator.py --input plan.json --output runbook.json
```

### Workflow 2: Plan a Service Migration (Strangler Fig)

1. Define spec with `type: "service"`, `pattern: "strangler_fig"`, source/target services, and dependencies
2. Generate migration plan with traffic routing phases (10% -> 50% -> 100%)
3. Review rollback triggers at each traffic percentage gate
4. **Validation checkpoint:** Circuit breaker thresholds defined; monitoring configured; feature flags lock rollout percentage between phases

### Workflow 3: Validate Migration Compatibility

1. Export before/after schemas as JSON (database or OpenAPI format)
2. Run `compatibility_checker.py` to identify breaking changes, type mismatches, and constraint violations
3. Review generated migration scripts and their rollback counterparts
4. **Validation checkpoint:** All breaking changes have migration scripts; rollback scripts verified; validation queries pass

---

## Migration Patterns

| Pattern | Type | Best For |
|---------|------|----------|
| Expand-Contract | Database | Zero-downtime schema evolution with backfill |
| Dual-Write | Database | Maintaining consistency during transition |
| Change Data Capture | Database | Large dataset migration with eventual consistency |
| Strangler Fig | Service | Incremental service replacement via gateway routing |
| Parallel Run | Service | Shadow traffic for correctness validation |
| Canary Deployment | Service | Gradual traffic shift with metric monitoring |
| Blue-Green | Infrastructure | Instant cutover with full rollback capability |

---

## Anti-Patterns

- **Big bang migration** -- migrating everything at once maximizes blast radius; always use phased execution with validation gates
- **Stale backups** -- taking backups at plan creation instead of immediately before execution; always create fresh backup as first execution task
- **Skipping staging** -- production-only migration attempts have no safety net; run the full process in a staging environment first
- **No data reconciliation** -- row counts match but data differs; use checksum validation and business logic queries on critical tables
- **Ignoring dependent systems** -- breaking downstream consumers during cutover; map all dependencies and coordinate migration windows
- **Feature flag drift** -- changing rollout percentage mid-phase causes inconsistent user experience; lock flags during each phase

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Compatibility checker reports false positives on type changes | Source and target schemas use vendor-specific type aliases (e.g., `serial` vs `int`) that are not in the built-in type compatibility matrix | Normalize type aliases to canonical SQL/JSON types in both schema files before running the checker |
| Migration planner generates unrealistic duration estimates | Complexity multiplier does not account for organizational factors like change-board approvals or cross-team coordination | Adjust the `constraints` block in your input spec to include `special_requirements` entries for each non-technical blocker |
| Rollback generator produces empty rollback steps for a phase | The phase name in the migration plan does not match any of the recognized keywords (`migration`, `cutover`, `preparation`) | Use standard phase names from the planner output, or ensure custom phase names contain one of the recognized keywords |
| Data validation fails after migration but row counts match | Soft deletes, filtered records, or computed columns cause hash/checksum mismatches even when primary data is intact | Use business logic validation (aggregate queries on key columns) instead of full-row checksums for tables with soft deletes or generated columns |
| Dual-write pattern causes write conflicts during cutover | Race conditions between source and target systems when replication lag exceeds the write interval | Implement idempotent writes with conflict-resolution timestamps, and increase the delta-sync frequency before the cutover window |
| Rollback triggered but legacy database backup is stale | Backup was taken at plan creation time rather than immediately before the migration execution phase | Always create a fresh backup as the first task of the migration execution phase; reference `migration_planner.py` preparation-phase tasks |
| Feature flag rollout causes inconsistent user experience | Hash-based routing sends the same user to different paths across sessions when the flag name or rollout percentage changes mid-migration | Lock the flag name and rollout percentage during each migration phase; only adjust between validated phase gates |

## Success Criteria

- **Data Integrity:** 100% of records pass post-migration checksum and referential-integrity validation with zero data loss or corruption.
- **Downtime Within Budget:** Actual service unavailability stays within the `max_downtime_minutes` constraint defined in the migration spec (target: zero-downtime for critical systems).
- **Performance Parity:** P95 latency and throughput on the target system are within 10% of pre-migration baseline measurements during the first 72 hours after cutover.
- **Rollback Readiness:** Every migration phase has a tested rollback procedure that can restore the previous state within 25% of the original phase duration.
- **Stakeholder Sign-off:** All stakeholders listed in the migration plan confirm acceptance criteria are met before legacy decommission begins.
- **Zero Critical Defects:** No severity-critical or severity-high issues remain unresolved 48 hours after cutover; all issues are tracked with owners and ETAs.
- **Compliance Continuity:** All regulatory and compliance controls (audit logging, access controls, encryption) remain fully operational throughout the migration and are validated in the target environment.

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

## Tool Reference

### migration_planner.py

**Purpose:** Generates comprehensive, phased migration plans with risk assessment, rollback strategies, timeline estimates, and stakeholder communication structures from a JSON migration specification.

**Usage:**
```bash
python scripts/migration_planner.py --input <spec.json> [--output <plan.json>] [--format <format>] [--validate]
```

**Flags/Parameters:**

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--input`, `-i` | Yes | -- | Input migration specification file (JSON). Must contain `type`, `source`, and `target` fields. |
| `--output`, `-o` | No | stdout | Output file path for the migration plan (JSON). Text output saved to same path with `.txt` extension when format includes text. |
| `--format`, `-f` | No | `both` | Output format. Choices: `json`, `text`, `both`. |
| `--validate` | No | false | Validate the migration specification without generating a plan. Exits with 0 if valid. |

**Input Specification Fields:**
- `type` (required): Migration type -- `database`, `service`, `infrastructure`, `data`, or `api`.
- `source` (required): Source system identifier.
- `target` (required): Target system identifier.
- `pattern`: Migration pattern (e.g., `schema_change`, `data_migration`, `strangler_fig`, `parallel_run`, `cloud_migration`, `on_prem_to_cloud`).
- `constraints.data_volume_gb`: Data volume in GB (affects complexity scoring).
- `constraints.dependencies`: List of dependent systems.
- `constraints.max_downtime_minutes`: Maximum allowed downtime in minutes.
- `constraints.special_requirements`: List of additional requirements that increase complexity.
- `constraints.compliance_requirements`: List of compliance frameworks that apply.

**Example:**
```bash
python scripts/migration_planner.py --input migration_spec.json --output plan.json --format both
```

**Output Formats:**
- **JSON:** Complete `MigrationPlan` object with `migration_id`, `phases` (each with tasks, validation criteria, rollback triggers), `risks` (categorized by severity), `rollback_plan`, `success_criteria`, and `stakeholders`.
- **Text:** Human-readable report with sections for phases, risk assessment, rollback strategy, success criteria, and stakeholders.

---

### compatibility_checker.py

**Purpose:** Analyzes schema and API compatibility between two versions, identifies breaking changes, data type mismatches, constraint violations, and generates migration script suggestions with rollback counterparts.

**Usage:**
```bash
python scripts/compatibility_checker.py --before <old.json> --after <new.json> [--type <schema_type>] [--output <report.json>] [--format <format>]
```

**Flags/Parameters:**

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--before` | Yes | -- | Path to the before/old schema file (JSON). |
| `--after` | Yes | -- | Path to the after/new schema file (JSON). |
| `--type` | No | `database` | Schema type to analyze. Choices: `database`, `api`. |
| `--output`, `-o` | No | stdout | Output file path for the compatibility report (JSON). |
| `--format`, `-f` | No | `both` | Output format. Choices: `json`, `text`, `both`. |

**Input Schema Format (database):** JSON with a `tables` object where each key is a table name containing `columns` (with `type`, `nullable`, `length`, `default` per column) and `constraints` (with `primary_key`, `foreign_key`, `unique`, `check`, `index` arrays).

**Input Schema Format (api):** OpenAPI-style JSON with `paths` (keyed by route, containing HTTP methods) and `components.schemas` (keyed by model name with `properties`, `required` arrays, and field `type` definitions).

**Example:**
```bash
python scripts/compatibility_checker.py --before v1_schema.json --after v2_schema.json --type database --format json
```

**Output Formats:**
- **JSON:** `CompatibilityReport` with `overall_compatibility` level, counts by change type (`breaking_changes_count`, `potentially_breaking_count`, `non_breaking_changes_count`, `additive_changes_count`), detailed `issues` list (each with severity, impact, suggested migration), `migration_scripts` (with rollback scripts and validation queries), `risk_assessment`, and `recommendations`.
- **Text:** Human-readable report with color-coded severity sections, issue details, and migration script listings.

---

### rollback_generator.py

**Purpose:** Takes a migration plan (typically the JSON output of `migration_planner.py`) and generates a comprehensive rollback runbook with phase-by-phase reversal steps, automated trigger conditions, data recovery plans, escalation matrices, and communication templates.

**Usage:**
```bash
python scripts/rollback_generator.py --input <plan.json> [--output <runbook.json>] [--format <format>]
```

**Flags/Parameters:**

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--input`, `-i` | Yes | -- | Input migration plan file (JSON). Expects output from `migration_planner.py` or any JSON with `migration_id`, `migration_type`, and `phases` fields. |
| `--output`, `-o` | No | stdout | Output file path for the rollback runbook (JSON). |
| `--format`, `-f` | No | `both` | Output format. Choices: `json`, `text`, `both`. |

**Example:**
```bash
python scripts/migration_planner.py --input spec.json --output plan.json --format json
python scripts/rollback_generator.py --input plan.json --output runbook.json --format both
```

**Output Formats:**
- **JSON:** `RollbackRunbook` object with `runbook_id`, `rollback_phases` (each containing ordered `steps` with script content, validation commands, success criteria, and failure escalation), `trigger_conditions` (with metric thresholds and auto-execute flags), `data_recovery_plan` (backup location, recovery scripts, estimated recovery time), `communication_templates` (for technical, business, and executive audiences), `escalation_matrix`, `validation_checklist`, `post_rollback_procedures`, and `emergency_contacts`.
- **Text:** Human-readable runbook with phase-by-phase rollback instructions, trigger condition summaries, communication templates, and a post-rollback checklist.