---
name: senior-data-engineer
description: >
  Use when designing data architectures, building batch or streaming pipelines,
  implementing data quality frameworks, optimizing ETL/ELT performance, working
  with Airflow/dbt/Spark/Kafka, or troubleshooting data pipeline failures.
  Provides pipeline generation, data quality validation, and SQL/Spark
  performance optimization.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: data-engineering
  updated: 2026-04-02
  tags: [airflow, spark, data-pipelines, warehousing, etl]
  python-tools: pipeline_orchestrator.py, data_quality_validator.py, etl_performance_optimizer.py
  tech-stack: python, sql, spark, airflow, dbt, kafka
---
# Senior Data Engineer

The agent generates pipeline configurations (Airflow, Prefect, Dagster), validates data quality with profiling and anomaly detection, and optimizes SQL/Spark performance with actionable recommendations.

---

## Quick Start

```bash
# Generate an Airflow DAG for incremental PostgreSQL -> Snowflake
python scripts/pipeline_orchestrator.py generate \
  --type airflow --source postgres --destination snowflake \
  --tables orders,customers --mode incremental --schedule "0 5 * * *"

# Validate data quality against a schema
python scripts/data_quality_validator.py validate data.csv \
  --schema schema.json --detect-anomalies --json

# Profile a dataset
python scripts/data_quality_validator.py profile data.csv --json

# Optimize a slow SQL query
python scripts/etl_performance_optimizer.py analyze-sql query.sql \
  --warehouse snowflake --json

# Estimate query cost
python scripts/etl_performance_optimizer.py estimate-cost query.sql \
  --warehouse bigquery --stats data_stats.json --json
```

## Tools Overview

| Tool | Subcommands | Purpose |
|------|-------------|---------|
| `pipeline_orchestrator.py` | `generate`, `validate`, `template` | Generate Airflow/Prefect/Dagster pipeline code, validate DAGs |
| `data_quality_validator.py` | `validate`, `profile`, `generate-suite`, `contract`, `schema` | Schema validation, profiling, anomaly detection, Great Expectations |
| `etl_performance_optimizer.py` | `analyze-sql`, `analyze-spark`, `optimize-partition`, `estimate-cost`, `template` | SQL/Spark optimization, partition strategy, cost estimation |

All subcommands support `--json` for machine-readable output and `--output` for file writing.

---

## Workflow 1: Batch ETL Pipeline (PostgreSQL -> dbt -> Snowflake)

**Step 1 -- Generate extraction config.**

```bash
python scripts/pipeline_orchestrator.py generate \
  --type airflow --source postgres --tables orders,customers,products \
  --mode incremental --watermark updated_at --output dags/extract_source.py
```

**Step 2 -- Create dbt staging model.**

```sql
-- models/staging/stg_orders.sql
WITH source AS (
    SELECT * FROM {{ source('postgres', 'orders') }}
)
SELECT order_id, customer_id, order_date, total_amount, status, _extracted_at
FROM source
WHERE order_date >= DATEADD(day, -3, CURRENT_DATE)
```

**Step 3 -- Create incremental mart model.**

```sql
-- models/marts/fct_orders.sql
{{ config(materialized='incremental', unique_key='order_id', cluster_by=['order_date']) }}

SELECT o.order_id, o.customer_id, c.customer_segment, o.order_date, o.total_amount, o.status
FROM {{ ref('stg_orders') }} o
LEFT JOIN {{ ref('dim_customers') }} c ON o.customer_id = c.customer_id
{% if is_incremental() %}
WHERE o._extracted_at > (SELECT MAX(_extracted_at) FROM {{ this }})
{% endif %}
```

**Step 4 -- Wire into Airflow DAG.**

```python
with DAG('daily_etl', schedule_interval='0 5 * * *', catchup=False, tags=['etl']) as dag:
    extract = BashOperator(task_id='extract', bash_command='python scripts/extract.py --date {{ ds }}')
    transform = BashOperator(task_id='dbt_run', bash_command='dbt run --select marts.*')
    test = BashOperator(task_id='dbt_test', bash_command='dbt test --select marts.*')
    extract >> transform >> test
```

**Step 5 -- Validate.**

```bash
python scripts/data_quality_validator.py validate --table fct_orders --checks all --output report.json
```

**Validation checkpoint:** DAG runs end-to-end. Data quality report shows 0 failures on uniqueness, completeness, and freshness.

---

## Workflow 2: Real-Time Streaming (Kafka -> Spark -> Delta Lake)

**Step 1 -- Define event schema and Kafka topic.**

```bash
kafka-topics.sh --create --bootstrap-server localhost:9092 \
  --topic user-events --partitions 12 --replication-factor 3 \
  --config retention.ms=604800000
```

**Step 2 -- Implement Spark Structured Streaming.**

```python
events_df = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "user-events") \
    .option("startingOffsets", "latest").load()

parsed_df = events_df.select(from_json(col("value").cast("string"), schema).alias("data")).select("data.*")

aggregated_df = parsed_df \
    .withWatermark("event_timestamp", "10 minutes") \
    .groupBy(window(col("event_timestamp"), "5 minutes"), col("event_type")) \
    .agg(count("*").alias("event_count"), approx_count_distinct("user_id").alias("unique_users"))

aggregated_df.writeStream.format("delta").outputMode("append") \
    .option("checkpointLocation", "/checkpoints/user-events") \
    .trigger(processingTime="1 minute").start()
```

**Step 3 -- Handle errors with dead letter queue.**

```python
def process_with_dlq(batch_df, batch_id):
    valid_df = batch_df.filter(col("event_id").isNotNull())
    invalid_df = batch_df.filter(col("event_id").isNull())
    valid_df.write.format("delta").mode("append").save("/data/lake/user_events")
    if invalid_df.count() > 0:
        invalid_df.withColumn("error_reason", lit("missing_event_id")) \
            .write.format("delta").mode("append").save("/data/lake/dlq/user_events")
```

**Validation checkpoint:** Consumer lag stays under threshold. DLQ table has < 0.1% of total events.

---

## Workflow 3: Data Quality Framework

**Step 1 -- Generate a Great Expectations suite from data.**

```bash
python scripts/data_quality_validator.py generate-suite data.csv --output expectations.json
```

**Step 2 -- Validate against a data contract.**

```yaml
# contracts/orders_contract.yaml
contract:
  name: orders_data_contract
  version: "1.0.0"
schema:
  properties:
    order_id: { type: string, format: uuid }
    total_amount: { type: decimal, minimum: 0 }
    status: { type: string, enum: [pending, confirmed, shipped, delivered, cancelled] }
sla:
  freshness: { max_delay_hours: 1 }
  completeness: { min_percentage: 99.9 }
  accuracy: { duplicate_tolerance: 0.01 }
```

```bash
python scripts/data_quality_validator.py contract data.csv --contract orders_contract.yaml --json
```

**Step 3 -- Add dbt tests for ongoing validation.**

```yaml
models:
  - name: fct_orders
    columns:
      - name: order_id
        tests: [unique, not_null]
      - name: total_amount
        tests:
          - not_null
          - dbt_utils.accepted_range: { min_value: 0, max_value: 1000000 }
```

**Validation checkpoint:** Quality score >= 95%. Zero duplicates. Freshness under SLA threshold.

---

## Architecture Decision Framework

| Question | Batch | Streaming |
|----------|-------|-----------|
| Latency requirement | Hours to days | Seconds to minutes |
| Processing complexity | Complex transforms, ML | Simple aggregations |
| Cost sensitivity | More cost-effective | Higher infra cost |
| Error handling | Easy reprocessing | Requires careful DLQ design |

**Decision tree:**
```
Real-time insight needed?
  Yes -> Exactly-once needed?
    Yes -> Kafka + Flink/Spark Structured Streaming
    No  -> Kafka + consumer groups
  No  -> Daily volume > 1TB?
    Yes -> Spark/Databricks
    No  -> dbt + warehouse compute
```

| Feature | Warehouse (Snowflake/BigQuery) | Lakehouse (Delta/Iceberg) |
|---------|-------------------------------|---------------------------|
| Best for | BI, SQL analytics | ML, unstructured data |
| Storage cost | Higher (proprietary) | Lower (open formats) |
| Flexibility | Schema-on-write | Schema-on-read |

---

## Anti-Patterns

1. **Full table reload on every run** -- use incremental loads with watermark columns.
2. **No dead letter queue** -- failed records silently dropped. Always route failures to a DLQ.
3. **Timezone mismatch** -- normalize all timestamps to UTC at extraction.
4. **Missing freshness checks** -- add `dbt source freshness` before transforms start.
5. **Skipping schema drift detection** -- use `mergeSchema` option or data contracts to catch new columns.

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Pipeline silently produces zero rows | Timezone mismatch on watermark column | Normalize to UTC; add row-count assertion |
| Spark shuffle 10x slower than expected | Data skew on join key | Salt the key or broadcast the smaller table |
| Airflow shows "no tasks to run" | Circular dependency or import error | `airflow dags list-import-errors`; fix import |
| dbt succeeds but dashboards stale | Source freshness not checked | Add `dbt source freshness` as prerequisite task |
| Kafka consumer lag grows unbounded | Throughput < producer rate | Increase partitions, scale consumers, batch `max.poll.records` |
| Quality validator false-positive anomalies | Z-score threshold too tight | Raise threshold or switch to IQR mode |

---

## References

| Guide | Path |
|-------|------|
| Pipeline Architecture | `references/data_pipeline_architecture.md` |
| Data Modeling Patterns | `references/data_modeling_patterns.md` |
| DataOps Best Practices | `references/dataops_best_practices.md` |

---

## Integration Points

| Skill | Integration |
|-------|-------------|
| `senior-data-scientist` | Feature engineering consumes curated mart data |
| `senior-ml-engineer` | ML pipelines depend on feature store tables |
| `senior-devops` | CI/CD for dbt, Airflow deployment, container orchestration |
| `senior-architect` | Architecture reviews for lakehouse vs warehouse decisions |
| `code-reviewer` | Pipeline code reviews for DAGs, dbt models, Spark jobs |

---

**Last Updated:** April 2026
**Version:** 1.1.0
