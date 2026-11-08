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
  updated: 2026-11-08
  tags: [data-quality, freshness, schema-drift, great-expectations, dbt-tests, soda, data-observability, data-engineering]
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

Before running the audit, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Dataset & target:** which table, pipeline, or store to audit (the data the scripts read via `--data`).
- **Which check:** DQ rule checks, schema drift, or freshness SLA (selects `dq_check_runner.py` vs `schema_drift_detector.py` vs `freshness_monitor.py`).
- **Thresholds & SLAs:** per-dimension pass thresholds and the freshness max-age budget (sets the pass/fail line and `--max-age-min`).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

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

| Tool | Purpose | Exit codes |
|------|---------|------------|
| `dq_check_runner.py` | Run a checks file (YAML or JSON, top-level `checks:` list) against CSV/JSON rows; `--profile` adds per-column null rate, distinct count, min/max | 0 all pass, 1 a check failed/errored, 2 bad input or zero checks loaded |
| `schema_drift_detector.py` | Diff a current schema against a baseline (added/removed columns, type, nullability, ordinal); `--snapshot` infers a baseline from data; `--fail-on` sets the gate severity (default `critical`) | 0 no drift at/above `--fail-on`, 1 drift, 2 bad input |
| `freshness_monitor.py` | Age of the newest timestamp vs a max-age budget; `--now` pins the clock | 0 within SLA, 1 breach, 2 bad input |

Supported check types: `not_null` (`threshold` = max null rate), `unique`, `accepted_values` (`values`), `matches_regex` (`regex`), `between` (`min`/`max`), `row_count_between`, `freshness` (`max_age_min`, optional `now`), `length_between` (`min_len`/`max_len`), `reference_exists` (`reference_values`). The YAML reader handles block maps, block lists and flow lists (`[a, b]`); anything fancier, use JSON.

## Workflow

Run from the skill folder. The samples pin `now` so the demo gives the same result on any date.

```bash
# 1. Profile, then run the suite: sound data passes (exit 0), flawed data fails 7 of 8 checks (exit 1)
python3 scripts/dq_check_runner.py --profile --data assets/sample_orders.json
python3 scripts/dq_check_runner.py --data assets/sample_orders.json --checks assets/checks.yaml
python3 scripts/dq_check_runner.py --data assets/sample_orders_flawed.json --checks assets/checks.yaml --format json

# 2. Snapshot a baseline, then diff: the drifted schema has a type change and a NOT NULL tightening (exit 1)
python3 scripts/schema_drift_detector.py --snapshot assets/sample_orders.json --output "$(mktemp -d)/baseline.json"
python3 scripts/schema_drift_detector.py --baseline assets/baseline_schema.json --current assets/current_schema_drifted.json

# 3. Freshness SLA: newest row 30 min old against a 60 min budget (exit 0)
python3 scripts/freshness_monitor.py --data assets/sample_orders.json --column updated_at --max-age-min 60 --now 2026-06-01T12:30:00Z --table-name orders
```

The tools read exported rows or schema JSON; they do not query a database. To audit a live table, export a sample (`SELECT ... LIMIT n` to JSON/CSV) or the `information_schema.columns` rows, then run the same commands. A result is only as good as the export: say what was sampled.

Done means: every production-critical table has at least one check per relevant dimension, the suite exits 0 on current data, and any failure has an owner and a ticket.

## Anti-Patterns

**Mistake:** Treating a run that loaded zero checks as a pass.
**Why it happens:** A typo in the checks file or the wrong format silently produces an empty suite.
**Instead:** The runner exits 2 when no checks load. In CI, gate on the exit code, not on the absence of failures in the report.

**Mistake:** Checks that alert but never block.
**Why it happens:** Wiring the exit code into the pipeline feels risky, so failures only post to a channel.
**Instead:** Fail the load on exit 1 for critical checks and route warnings by severity. Unenforced checks let bad data reach consumers anyway.

**Mistake:** `not_null` on every column of a wide table.
**Why it happens:** Coverage looks good on a dashboard.
**Instead:** Check the columns the business needs, with thresholds tuned from the profile. Noise trains people to ignore the real alerts.

More in [references/dq-anti-patterns.md](references/dq-anti-patterns.md).

## Files

- `scripts/dq_check_runner.py`, `scripts/schema_drift_detector.py`, `scripts/freshness_monitor.py` — the three tools above.
- `assets/sample_orders.json` (sound), `assets/sample_orders_flawed.json` (duplicate key, empty and malformed email, unknown status, negative amount, orphan customer, stale), `assets/checks.yaml`, `assets/baseline_schema.json`, `assets/current_schema_drifted.json`.

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
- Live database querying; the scripts read exported CSV/JSON rows and schema JSON. Export first, or run the same checks in your warehouse tool (dbt tests, Great Expectations, Soda).

## Related skills

- `engineering/senior-data-engineer` — pipeline design, ETL, dbt, Spark
- `engineering/observability-designer` — observability for data infrastructure (adjacent to DQ)
- `engineering/chaos-engineering` — DQ checks benefit from chaos testing
- `ra-qm-team/gdpr-dsgvo-expert` — DQ underpins GDPR Art. 5(1)(d) "accuracy"
- `ra-qm-team/soc2-compliance-expert` — SOC 2 PI1 (Processing Integrity) requires DQ controls
