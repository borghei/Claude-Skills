---
name: senior-data-engineer
description: Expert data engineering covering data pipelines, ETL/ELT, data warehousing, streaming, and data quality.
version: 1.0.0
author: Claude Skills
category: engineering
tags: [data, etl, spark, airflow, snowflake, streaming]
---

# Senior Data Engineer

Expert-level data engineering for scalable data systems.

## Core Competencies

- Data pipeline development
- ETL/ELT design
- Data warehousing
- Stream processing
- Data quality and governance
- Data modeling
- Performance optimization
- Cloud data platforms

## Data Pipeline Architecture

### Batch Pipeline

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Sources   │────▶│  Transform  │────▶│   Target    │
│  (S3, API)  │     │  (Spark)    │     │  (Snowflake)│
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │
       │                   ▼                   │
       │           ┌─────────────┐             │
       └──────────▶│   Quality   │◀────────────┘
                   │   Checks    │
                   └─────────────┘
```

### Streaming Pipeline

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Kafka     │────▶│  Processor  │────▶│  Real-time  │
│   Topics    │     │  (Flink)    │     │    Store    │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   Batch     │
                    │   Layer     │
                    └─────────────┘
```

## Apache Airflow

### DAG Structure

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'email_on_failure': True,
    'email': ['data-alerts@company.com'],
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='daily_etl_pipeline',
    default_args=default_args,
    description='Daily ETL for analytics',
    schedule_interval='0 6 * * *',
    start_date=days_ago(1),
    catchup=False,
    tags=['etl', 'daily'],
) as dag:

    extract_task = PythonOperator(
        task_id='extract_data',
        python_callable=extract_from_source,
        op_kwargs={'date': '{{ ds }}'},
    )

    transform_task = PythonOperator(
        task_id='transform_data',
        python_callable=transform_data,
    )

    quality_check = PythonOperator(
        task_id='quality_check',
        python_callable=run_quality_checks,
    )

    load_task = SnowflakeOperator(
        task_id='load_to_snowflake',
        sql='sql/load_data.sql',
        snowflake_conn_id='snowflake_default',
        params={'date': '{{ ds }}'},
    )

    extract_task >> transform_task >> quality_check >> load_task
```

### Dynamic DAG Generation

```python
from airflow.decorators import dag, task
from datetime import datetime

@dag(
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
)
def dynamic_etl():

    @task
    def get_sources():
        return ['source_a', 'source_b', 'source_c']

    @task
    def extract(source: str):
        print(f'Extracting from {source}')
        return f'{source}_data'

    @task
    def transform(data: str):
        print(f'Transforming {data}')
        return f'{data}_transformed'

    @task
    def load(data: list):
        print(f'Loading {len(data)} datasets')

    sources = get_sources()
    extracted = extract.expand(source=sources)
    transformed = transform.expand(data=extracted)
    load(transformed)

dag = dynamic_etl()
```

## Apache Spark

### Spark ETL Job

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, lit, current_timestamp
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

spark = SparkSession.builder \
    .appName("ETL Pipeline") \
    .config("spark.sql.adaptive.enabled", "true") \
    .config("spark.sql.shuffle.partitions", "200") \
    .getOrCreate()


def read_source_data(path: str, date: str):
    return spark.read \
        .option("header", "true") \
        .option("inferSchema", "true") \
        .csv(f"{path}/date={date}/*.csv")


def transform_data(df):
    return df \
        .withColumn("amount_clean",
            when(col("amount").isNull(), 0).otherwise(col("amount"))) \
        .withColumn("category_normalized",
            when(col("category").isin(["A", "B"]), col("category"))
            .otherwise("OTHER")) \
        .withColumn("processed_at", current_timestamp()) \
        .filter(col("status") == "active") \
        .dropDuplicates(["id"])


def aggregate_metrics(df):
    return df.groupBy("date", "category") \
        .agg(
            F.count("*").alias("total_count"),
            F.sum("amount").alias("total_amount"),
            F.avg("amount").alias("avg_amount"),
            F.countDistinct("user_id").alias("unique_users")
        )


def write_to_warehouse(df, table_name: str, partition_cols: list):
    df.write \
        .mode("overwrite") \
        .partitionBy(partition_cols) \
        .format("delta") \
        .saveAsTable(table_name)


# Main pipeline
raw_df = read_source_data("s3://bucket/raw/", "2024-01-15")
clean_df = transform_data(raw_df)
metrics_df = aggregate_metrics(clean_df)

write_to_warehouse(clean_df, "clean.transactions", ["date"])
write_to_warehouse(metrics_df, "analytics.daily_metrics", ["date"])
```

### Performance Optimization

```python
# Partition tuning
df = spark.read.parquet("s3://bucket/data/") \
    .repartition(100, "date")  # Repartition by key

# Broadcast join for small tables
from pyspark.sql.functions import broadcast

small_df = spark.table("lookup_table")
large_df = spark.table("fact_table")

result = large_df.join(broadcast(small_df), "key")

# Cache intermediate results
cleaned_df = transform(raw_df)
cleaned_df.cache()

metrics_1 = cleaned_df.groupBy("category").count()
metrics_2 = cleaned_df.groupBy("region").sum("amount")

cleaned_df.unpersist()

# Predicate pushdown
df = spark.read.parquet("s3://bucket/data/") \
    .filter(col("date") >= "2024-01-01")  # Pushed to storage layer
```

## Data Modeling

### Dimensional Modeling

**Star Schema:**
```sql
-- Fact Table
CREATE TABLE fact_sales (
    sale_id BIGINT PRIMARY KEY,
    date_key INT REFERENCES dim_date(date_key),
    product_key INT REFERENCES dim_product(product_key),
    customer_key INT REFERENCES dim_customer(customer_key),
    store_key INT REFERENCES dim_store(store_key),
    quantity INT,
    unit_price DECIMAL(10,2),
    total_amount DECIMAL(10,2),
    discount_amount DECIMAL(10,2)
);

-- Dimension Tables
CREATE TABLE dim_date (
    date_key INT PRIMARY KEY,
    full_date DATE,
    year INT,
    quarter INT,
    month INT,
    week INT,
    day_of_week INT,
    is_weekend BOOLEAN,
    is_holiday BOOLEAN
);

CREATE TABLE dim_product (
    product_key INT PRIMARY KEY,
    product_id VARCHAR(50),
    product_name VARCHAR(200),
    category VARCHAR(100),
    subcategory VARCHAR(100),
    brand VARCHAR(100),
    -- SCD Type 2 columns
    effective_date DATE,
    end_date DATE,
    is_current BOOLEAN
);
```

### dbt Models

**staging/stg_orders.sql:**
```sql
{{ config(materialized='view') }}

with source as (
    select * from {{ source('raw', 'orders') }}
),

renamed as (
    select
        order_id,
        customer_id,
        order_date,
        cast(total_amount as decimal(10,2)) as total_amount,
        status,
        _loaded_at
    from source
    where order_date >= '2023-01-01'
)

select * from renamed
```

**marts/fct_orders.sql:**
```sql
{{ config(
    materialized='incremental',
    unique_key='order_id',
    incremental_strategy='merge'
) }}

with orders as (
    select * from {{ ref('stg_orders') }}
),

customers as (
    select * from {{ ref('dim_customers') }}
),

final as (
    select
        o.order_id,
        o.customer_id,
        c.customer_segment,
        o.order_date,
        o.total_amount,
        o.status,
        current_timestamp() as processed_at
    from orders o
    left join customers c on o.customer_id = c.customer_id
    {% if is_incremental() %}
    where o._loaded_at > (select max(processed_at) from {{ this }})
    {% endif %}
)

select * from final
```

## Data Quality

### Great Expectations

```python
import great_expectations as gx

context = gx.get_context()

# Define expectations
expectation_suite = context.add_expectation_suite("orders_suite")

expectations = [
    gx.expectations.ExpectColumnValuesToNotBeNull(column="order_id"),
    gx.expectations.ExpectColumnValuesToBeUnique(column="order_id"),
    gx.expectations.ExpectColumnValuesToBeBetween(
        column="amount",
        min_value=0,
        max_value=100000
    ),
    gx.expectations.ExpectColumnValuesToMatchRegex(
        column="email",
        regex=r"^[\w\.-]+@[\w\.-]+\.\w+$"
    ),
    gx.expectations.ExpectTableRowCountToBeBetween(
        min_value=1000,
        max_value=1000000
    ),
]

for exp in expectations:
    expectation_suite.add_expectation(exp)

# Run validation
batch = context.get_batch(datasource_name="orders", data_asset_name="daily")
results = context.run_validation_operator(
    "action_list_operator",
    assets_to_validate=[batch],
    expectation_suite_name="orders_suite"
)

if not results["success"]:
    raise DataQualityError("Validation failed")
```

### Custom Quality Checks

```python
from dataclasses import dataclass
from typing import Callable

@dataclass
class QualityCheck:
    name: str
    check_fn: Callable
    severity: str  # 'error' or 'warning'


def check_no_nulls(df, column: str) -> bool:
    null_count = df.filter(col(column).isNull()).count()
    return null_count == 0


def check_referential_integrity(df, ref_df, key: str) -> bool:
    orphans = df.join(ref_df, key, "left_anti")
    return orphans.count() == 0


def check_freshness(df, timestamp_col: str, max_hours: int) -> bool:
    from pyspark.sql.functions import max as spark_max, current_timestamp
    max_ts = df.agg(spark_max(timestamp_col)).collect()[0][0]
    hours_old = (datetime.now() - max_ts).total_seconds() / 3600
    return hours_old <= max_hours


def run_quality_checks(df, checks: list[QualityCheck]):
    results = []
    for check in checks:
        passed = check.check_fn(df)
        results.append({
            'check': check.name,
            'passed': passed,
            'severity': check.severity
        })

    errors = [r for r in results if not r['passed'] and r['severity'] == 'error']
    if errors:
        raise DataQualityError(f"Quality checks failed: {errors}")

    return results
```

## Stream Processing

### Kafka + Flink

```python
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment

env = StreamExecutionEnvironment.get_execution_environment()
t_env = StreamTableEnvironment.create(env)

# Define Kafka source
t_env.execute_sql("""
    CREATE TABLE orders (
        order_id STRING,
        customer_id STRING,
        amount DECIMAL(10,2),
        order_time TIMESTAMP(3),
        WATERMARK FOR order_time AS order_time - INTERVAL '5' SECOND
    ) WITH (
        'connector' = 'kafka',
        'topic' = 'orders',
        'properties.bootstrap.servers' = 'kafka:9092',
        'properties.group.id' = 'order-processor',
        'format' = 'json',
        'scan.startup.mode' = 'latest-offset'
    )
""")

# Windowed aggregation
t_env.execute_sql("""
    CREATE TABLE order_metrics (
        window_start TIMESTAMP(3),
        window_end TIMESTAMP(3),
        total_orders BIGINT,
        total_amount DECIMAL(10,2)
    ) WITH (
        'connector' = 'kafka',
        'topic' = 'order-metrics',
        'properties.bootstrap.servers' = 'kafka:9092',
        'format' = 'json'
    )
""")

t_env.execute_sql("""
    INSERT INTO order_metrics
    SELECT
        TUMBLE_START(order_time, INTERVAL '1' MINUTE) as window_start,
        TUMBLE_END(order_time, INTERVAL '1' MINUTE) as window_end,
        COUNT(*) as total_orders,
        SUM(amount) as total_amount
    FROM orders
    GROUP BY TUMBLE(order_time, INTERVAL '1' MINUTE)
""")
```

## Reference Materials

- `references/pipeline_patterns.md` - Pipeline architecture patterns
- `references/data_modeling.md` - Dimensional modeling guide
- `references/quality_framework.md` - Data quality practices
- `references/streaming_guide.md` - Stream processing patterns

## Scripts

```bash
# Pipeline scaffolder
python scripts/pipeline_scaffold.py --name daily_etl --schedule daily

# Data quality runner
python scripts/quality_check.py --suite orders_suite --data s3://bucket/orders/

# Schema migration
python scripts/schema_migrate.py --target snowflake --version v2

# Backfill runner
python scripts/backfill.py --dag daily_etl --start 2024-01-01 --end 2024-01-31
```
