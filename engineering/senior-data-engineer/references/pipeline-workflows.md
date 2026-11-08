# Pipeline Workflows

Read this for the end-to-end worked pipelines with copy-pasteable code: batch ETL (PostgreSQL → dbt → Snowflake), real-time streaming (Kafka → Spark → Delta Lake), and the data-quality framework.

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
with DAG('daily_etl', schedule='0 5 * * *', catchup=False, tags=['etl']) as dag:
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
