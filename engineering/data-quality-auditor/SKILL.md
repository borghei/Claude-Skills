---
name: data-quality-auditor
description: >
  Audit data quality across pipelines, warehouses, and stores. Use when designing a DQ
  program, defining DQ dimensions, building rule-based checks, detecting schema drift,
  monitoring freshness SLAs, or responding to a DQ incident.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: engineering
  updated: 2026-06-17
  tags: [data-quality, dq, freshness, schema-drift, great-expectations, dbt-tests, soda, data-observability, data-engineering]
---

# Data Quality Auditor

End-to-end data quality (DQ) practice: define DQ dimensions, write rule-based checks, detect schema drift, monitor freshness SLAs, respond to DQ incidents, build a maturity-graded program. Tool-agnostic — works whether you use Great Expectations, dbt tests, Soda Core, Monte Carlo, custom SQL, or hand-rolled scripts.

This skill is audit-focused, not pipeline-focused. For pipeline design, ETL, Spark/dbt, see `engineering/senior-data-engineer`.

## Core Capabilities

- **Six DQ dimensions** — completeness, accuracy, consistency, timeliness/freshness, validity, uniqueness (plus integrity, conformity, reasonableness); at least one check per dimension at production stage.
- **DQ check catalog** — five categories (volume, freshness, schema, values, distribution) of ~50 specific check patterns applied per dataset.
- **Schema drift detection** — snapshot baseline schemas and diff added/removed/changed columns, types, and ordinals with severity.
- **Freshness SLA monitoring** — per-table max-age budgets with alerting-ready output.
- **Incident response** — severity classification (Sev1-4) and a 7-step playbook (acknowledge → quarantine → triage → contain → fix-forward → notify → post-incident) with recovery patterns.
- **Maturity & governance** — a five-level maturity model and anti-pattern catalog to grade and improve a DQ program.

## When to Use

| Situation | Skill applies |
|-----------|---------------|
| Setting up DQ from scratch on a new pipeline | Yes — start with **DQ dimensions** + **check catalog** |
| Auditing existing pipelines for missing DQ | Yes — `dq_check_runner.py` |
| Detecting schema drift in upstream sources | Yes — `schema_drift_detector.py` |
| Monitoring freshness / SLA on data assets | Yes — `freshness_monitor.py` |
| Responding to a DQ incident (bad data in prod) | Yes — **incident response playbook** |
| Designing a DQ governance model | Yes — **DQ maturity model** |
| Compliance evidence (SOC 2 PI1, GDPR, ISO 27001) | Yes — checks produce auditable artifacts |
| Building data pipelines for the first time | Use `engineering/senior-data-engineer` first |

## Clarify First

Before running the audit, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Dataset & target** — which table, pipeline, or store to audit (the data the scripts read via `--data`)
- [ ] **Which check** — DQ rule checks, schema drift, or freshness SLA (selects `dq_check_runner.py` vs `schema_drift_detector.py` vs `freshness_monitor.py`)
- [ ] **Thresholds & SLAs** — per-dimension pass thresholds and the freshness max-age budget (sets the pass/fail line and `--max-age-min`)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## The six DQ dimensions

Industry-standard taxonomy. Every dataset should have at least one check per dimension when at production stage.

| Dimension | Question | Example check |
|-----------|----------|---------------|
| **Completeness** | Are required fields populated? | `users.email IS NOT NULL` — fail if > 0.1% nulls |
| **Accuracy** | Do values match reality? | Reconciliation against source-of-truth system; sample-based human review |
| **Consistency** | Do values agree across systems / time? | `users.email` in DB matches Salesforce; row count today within 5% of yesterday |
| **Timeliness / Freshness** | Is data current to expectation? | `events_table.max(event_time)` is < 1h old; pipeline runs SLA |
| **Validity** | Do values conform to format / schema / business rules? | Email regex matches; country code in ISO 3166-1; status in known enum |
| **Uniqueness** | Are entities not duplicated? | `users.user_id` is unique; no two rows with same `(user_id, day)` |

Some teams add: **Integrity** (referential — FKs resolve), **Conformity** (matches a published standard), **Reasonableness** (passes basic sanity checks beyond strict validity).

## The DQ check catalog

Checks group into five categories applied per dataset — **Volume**, **Freshness**, **Schema**, **Values**, and **Distribution**. See the category summary and the full ~50-pattern catalog in [references/dq-check-catalog.md](references/dq-check-catalog.md).

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `dq_check_runner.py` | Run/profile DQ checks against tabular data; per-table pass/fail/warning with value vs threshold | `python scripts/dq_check_runner.py --data t.json --checks checks.json --format json` |
| `schema_drift_detector.py` | Diff a current schema against a baseline snapshot (added/removed/changed columns, types, ordinals) | `python scripts/schema_drift_detector.py --baseline base.json --current cur.json` |
| `freshness_monitor.py` | Check a freshness SLA: current age vs max-age budget, alerting-ready output | `python scripts/freshness_monitor.py --data t.json --column updated_at --max-age-min 60` |

All scripts: stdlib only, argparse CLI, JSON or human-readable output (see Scope re: live DB integration).

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/data-quality-dimensions.md](references/data-quality-dimensions.md)** — the 6 dimensions in depth: how to measure, threshold guidance, alerting strategy, and common pitfalls per dimension. Read when defining checks for a specific dimension.
- **[references/dq-check-catalog.md](references/dq-check-catalog.md)** — the full catalog of ~50 specific check patterns with detection heuristics and tool snippets (Great Expectations / dbt / Soda / SQL). Read when writing concrete checks.
- **[references/dq-incident-response.md](references/dq-incident-response.md)** — the full incident playbook: severity classification, the 7-step response loop, recovery patterns (backfill, quarantine, DLQ, idempotent reprocessing, rollback), and post-incident writeup/notification templates. Read when responding to a DQ incident.
- **[references/dq-maturity-model.md](references/dq-maturity-model.md)** — the five-level DQ maturity model (L0 reactive → L4 data-as-product) and what to invest in at each level. Read when grading or planning a DQ program.
- **[references/dq-workflows.md](references/dq-workflows.md)** — the five end-to-end workflows (new dataset, schema drift, freshness SLA, auditing existing pipelines, post-incident improvement) with the exact script commands. Read when executing a concrete DQ task.
- **[references/dq-anti-patterns.md](references/dq-anti-patterns.md)** — the catalog of DQ anti-patterns to avoid. Read when reviewing an existing DQ program for smells.

## Scope & Limitations

**This skill covers:**
- Auditing data quality across pipelines, warehouses, and stores against the six DQ dimensions.
- Rule-based check design, schema drift detection, and freshness SLA monitoring (tool-agnostic).
- DQ incident response and a maturity-graded governance program.
- Producing auditable DQ artifacts for compliance evidence (SOC 2 PI1, GDPR accuracy, ISO 27001).

**This skill does NOT cover:**
- Pipeline design, ETL, dbt/Spark implementation — use `engineering/senior-data-engineer`.
- Live database querying; scripts are stdlib-only and read JSON inputs or simulate. For production, integrate your DB driver of choice (psycopg / mysqlclient / google-cloud-bigquery / etc.).

## Related skills

- `engineering/senior-data-engineer` — pipeline design, ETL, dbt, Spark
- `engineering/observability-designer` — observability for data infrastructure (adjacent to DQ)
- `engineering/chaos-engineering` — DQ checks benefit from chaos testing
- `ra-qm-team/gdpr-dsgvo-expert` — DQ underpins GDPR Art. 5(1)(d) "accuracy"
- `ra-qm-team/soc2-compliance-expert` — SOC 2 PI1 (Processing Integrity) requires DQ controls
