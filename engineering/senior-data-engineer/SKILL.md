---
name: senior-data-engineer
description: >
  Data engineering for batch and streaming pipelines with Airflow, dbt, Spark, and Kafka. Use
  when designing data architectures, building pipelines, adding data-quality checks,
  optimizing ETL/ELT, or troubleshooting pipeline failures.
license: MIT + Commons Clause
metadata:
  version: 1.2.0
  author: borghei
  category: engineering
  domain: data-engineering
  updated: 2026-11-08
  tags: [airflow, spark, data-pipelines, warehousing, etl]
  python-tools: pipeline_orchestrator.py, data_quality_validator.py, etl_performance_optimizer.py
  tech-stack: python, sql, spark, airflow, dbt, kafka
---
# Senior Data Engineer

Generate pipeline configurations (Airflow, Prefect, Dagster), validate data quality with profiling and anomaly detection, and optimize SQL/Spark performance with actionable recommendations.

## Core Capabilities

- **Pipeline generation** — Airflow/Prefect/Dagster DAG code for batch and incremental loads, with DAG validation.
- **Data quality** — schema validation, profiling, anomaly detection, data contracts, and Great Expectations suite generation.
- **ETL/ELT optimization** — SQL and Spark analysis, partition strategy, and query cost estimation per warehouse.
- **Architecture decisions** — batch vs streaming and warehouse vs lakehouse trade-off frameworks.
- **Reliability patterns** — incremental watermarks, dead letter queues, freshness checks, and schema-drift detection.

## When to Use

- Designing a data architecture or choosing batch vs streaming / warehouse vs lakehouse.
- Building or generating Airflow/Spark/dbt pipelines.
- Adding data-quality checks or data contracts.
- Optimizing slow ETL/ELT queries or troubleshooting pipeline failures.

## Clarify First

Before generating pipelines, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Orchestrator:** Airflow / Prefect / Dagster (`--type`; changes the generated DAG code).
- **Source, destination & load mode:** systems involved and batch vs incremental (`--source`/`--destination`/`--mode`; shapes the pipeline).
- **Data-quality expectations:** the schema and contracts to enforce (drives the Great Expectations suite generation).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

```bash
# Generate an Airflow DAG for incremental PostgreSQL -> Snowflake. Targets Airflow 3 (`airflow.sdk`,
# current 3.4) with import fallbacks for 2.7+; --output creates missing parent folders
python scripts/pipeline_orchestrator.py generate \
  --type airflow --source postgres --destination snowflake \
  --tables orders,customers --mode incremental --schedule "0 5 * * *" --output dags/orders_etl.py

# Validate data against a schema (sample schema and data ship in assets/)
python scripts/data_quality_validator.py validate assets/sample_orders_flawed.csv \
  --schema assets/sample_schema.json --detect-anomalies

# Draft a schema from existing data, then tighten it by hand
python scripts/data_quality_validator.py schema assets/sample_orders_clean.csv --output schema.json

# Review a SQL query (static analysis; read the warehouse's query profile for ground truth)
python scripts/etl_performance_optimizer.py analyze-sql assets/sample_query.sql --warehouse snowflake
```

Schema file format (`--schema`): a JSON object with `name`, `version`, optional
`primary_key` (list of columns), `row_count_min`/`row_count_max`, and `columns`, each with
`name`, `type` (`string`, `integer`, `float`, `boolean`, `date`, `datetime`, `email`, `uuid`),
and optional `nullable`, `unique`, `min_value`, `max_value`, `min_length`, `max_length`,
`pattern` (regex) and `allowed_values`. See `assets/sample_schema.json`. A schema generated
by the `schema` subcommand only records types and observed ranges, so validating the same
data against it finds nothing by construction; add the real business rules before using it
as a gate. The report's check counts list failed checks, so a clean run shows 0.

Exit codes: `0` ok; `1` `validate`/`contract` found error-severity failures, or
`pipeline_orchestrator.py validate` found issues; `2` bad input (missing file, invalid JSON
or schema). `assets/sample_orders_clean.csv` validates clean (exit 0);
`assets/sample_orders_flawed.csv` has a duplicate key, a null and a malformed email, a
negative amount, an unknown status and a bad date (exit 1).

## Tools

| Tool | Subcommands | Purpose |
|------|-------------|---------|
| `pipeline_orchestrator.py` | `generate`, `validate`, `template` | Generate Airflow/Prefect/Dagster pipeline code, validate DAGs |
| `data_quality_validator.py` | `validate`, `profile`, `generate-suite`, `contract`, `schema` | Schema validation, profiling, anomaly detection, Great Expectations |
| `etl_performance_optimizer.py` | `analyze-sql`, `analyze-spark`, `optimize-partition`, `estimate-cost`, `template` | SQL/Spark optimization, partition strategy, cost estimation |

`--json` is available on `data_quality_validator.py` `validate`, `profile` and `contract` and on the four `etl_performance_optimizer.py` analysis subcommands (`analyze-sql`, `analyze-spark`, `optimize-partition`, `estimate-cost`). `pipeline_orchestrator.py` has no `--json` flag: `generate` and `template` print pipeline code, and `validate` always prints its result as JSON. Every subcommand except `pipeline_orchestrator.py validate` takes `--output` to write to a file.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/pipeline-workflows.md](references/pipeline-workflows.md)** — the three end-to-end worked pipelines with code: batch ETL (PostgreSQL → dbt → Snowflake), real-time streaming (Kafka → Spark → Delta Lake), and the data-quality framework. Read when building a concrete pipeline.
- **[references/decisions-and-troubleshooting.md](references/decisions-and-troubleshooting.md)** — the batch-vs-streaming and warehouse-vs-lakehouse decision frameworks, anti-patterns, and the troubleshooting table. Read when choosing an architecture or diagnosing a failure.
- **[references/data_pipeline_architecture.md](references/data_pipeline_architecture.md)** — deep reference on pipeline architecture patterns. Read for architecture design depth.
- **[references/data_modeling_patterns.md](references/data_modeling_patterns.md)** — dimensional modeling and data-modeling patterns. Read when modeling marts and dimensions.
- **[references/dataops_best_practices.md](references/dataops_best_practices.md)** — DataOps practices for CI/CD, testing, and operating pipelines. Read when operationalizing pipelines.

## Scope & Limitations

**In Scope:**
- Pipeline code generation for Airflow, Prefect and Dagster with `pipeline_orchestrator.py` (`generate`, `validate`, `template`), including incremental and full load modes.
- Data quality checks on CSV, JSON or JSONL files with `data_quality_validator.py`: schema validation, profiling, anomaly detection, data contracts, schema inference and Great Expectations suite generation.
- SQL and Spark analysis with `etl_performance_optimizer.py`: query recommendations, Spark job metrics review, partition strategy and query cost estimates for BigQuery, Snowflake, Redshift and Databricks.
- Batch versus streaming and warehouse versus lakehouse decision frameworks, worked pipelines and troubleshooting in `references/`.

**Out of Scope:**
- Running pipelines or connecting to sources, warehouses, Kafka or Spark clusters. The scripts work on local files.
- Snowflake-specific query tuning and warehouse sizing (see `engineering/snowflake-development/`).
- An organization-wide data quality program (see `engineering/data-quality-auditor/`).
- Model training and feature pipelines for ML (see `engineering/senior-ml-engineer/`).

**Important Caveats:**
- Generated DAG and flow code is a scaffold. It imports Airflow, Prefect, Dagster or pandas, which are not installed by the skill, and it needs real connections, credentials and testing before use.
- SQL analysis is pattern-based on query text. It does not read execution plans or table statistics unless a stats file is provided.
- Cost estimates use per-credit and per-TB prices built into the script. Warehouse pricing changes and varies by contract and region, so estimates are for comparison, not budgeting.
- The YAML used for configs and contracts is read with a small stdlib parser, so complex YAML may not load as expected.

## Anti-Patterns

### Validating Against an Inferred Schema
**Mistake:** Generating a schema from today's data with `schema`, then gating tomorrow's loads on it.
**Why it happens:** It is one command and the first run passes.
**Instead:** An inferred schema encodes whatever the data already is, including its errors. Add the business rules (keys, allowed values, ranges) by hand and review them with the data owner.

### Non-Idempotent Loads
**Mistake:** Appending each run's rows without a merge key, so retries and backfills duplicate data.
**Why it happens:** Appends are simpler and work on the happy path.
**Instead:** Load by partition or `MERGE` on a business key so re-running any date gives the same result; test by running the same date twice.

### Relative Start Dates in DAGs
**Mistake:** `start_date=days_ago(1)` or `datetime.now()` in a DAG.
**Why it happens:** Older tutorials used it.
**Instead:** A fixed, timezone-aware `start_date` with `catchup` set deliberately. Relative dates shift every parse, break backfills, and the helper is gone in Airflow 3.

## Files

| File | Purpose |
|------|---------|
| `scripts/pipeline_orchestrator.py` | Airflow / Prefect / Dagster code generation and DAG validation |
| `scripts/data_quality_validator.py` | Schema validation, profiling, anomalies, contracts, schema inference, GE suites |
| `scripts/etl_performance_optimizer.py` | SQL and Spark analysis, partition strategy, cost estimates |
| `assets/sample_schema.json` | Schema with keys, types, ranges and allowed values |
| `assets/sample_orders_clean.csv` | Data that passes the schema (exit 0) |
| `assets/sample_orders_flawed.csv` | Data with six rule violations (exit 1) |
| `assets/sample_query.sql` | Query for `analyze-sql` (SELECT *, function on a filter column, ORDER BY without LIMIT) |
| `references/*.md` | Worked pipelines, decisions and troubleshooting, architecture, modeling, DataOps |
