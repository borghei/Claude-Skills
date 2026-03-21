---
name: database-designer
description: Provides expert-level database design with schema analysis, index optimization, and migration generation. Supports PostgreSQL, MySQL, MongoDB, and DynamoDB. Use when designing schemas, optimizing queries, planning migrations, or analyzing database performance.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  category: engineering
  domain: databases
  tier: POWERFUL
---

# Database Designer - POWERFUL Tier Skill

## Overview

A comprehensive database design skill that provides expert-level analysis, optimization, and migration capabilities for modern database systems. This skill combines theoretical principles with practical tools to help architects and developers create scalable, performant, and maintainable database schemas.

## Core Competencies

### Schema Design & Analysis
- **Normalization Analysis**: Automated detection of normalization levels (1NF through BCNF)
- **Denormalization Strategy**: Smart recommendations for performance optimization
- **Data Type Optimization**: Identification of inappropriate types and size issues
- **Constraint Analysis**: Missing foreign keys, unique constraints, and null checks
- **Naming Convention Validation**: Consistent table and column naming patterns
- **ERD Generation**: Automatic Mermaid diagram creation from DDL

### Index Optimization
- **Index Gap Analysis**: Identification of missing indexes on foreign keys and query patterns
- **Composite Index Strategy**: Optimal column ordering for multi-column indexes
- **Index Redundancy Detection**: Elimination of overlapping and unused indexes
- **Performance Impact Modeling**: Selectivity estimation and query cost analysis
- **Index Type Selection**: B-tree, hash, partial, covering, and specialized indexes

### Migration Management
- **Zero-Downtime Migrations**: Expand-contract pattern implementation
- **Schema Evolution**: Safe column additions, deletions, and type changes
- **Data Migration Scripts**: Automated data transformation and validation
- **Rollback Strategy**: Complete reversal capabilities with validation
- **Execution Planning**: Ordered migration steps with dependency resolution

## Database Design Principles

### Normalization Forms

#### First Normal Form (1NF)
- **Atomic Values**: Each column contains indivisible values
- **Unique Column Names**: No duplicate column names within a table
- **Uniform Data Types**: Each column contains the same type of data
- **Row Uniqueness**: No duplicate rows in the table

**Example Violation:**
```sql
-- BAD: Multiple phone numbers in one column
CREATE TABLE contacts (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    phones VARCHAR(200)  -- "123-456-7890, 098-765-4321"
);

-- GOOD: Separate table for phone numbers
CREATE TABLE contacts (
    id INT PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE contact_phones (
    id INT PRIMARY KEY,
    contact_id INT REFERENCES contacts(id),
    phone_number VARCHAR(20),
    phone_type VARCHAR(10)
);
```

#### Second Normal Form (2NF)
- **1NF Compliance**: Must satisfy First Normal Form
- **Full Functional Dependency**: Non-key attributes depend on the entire primary key
- **Partial Dependency Elimination**: Remove attributes that depend on part of a composite key

**Example Violation:**
```sql
-- BAD: Student course table with partial dependencies
CREATE TABLE student_courses (
    student_id INT,
    course_id INT,
    student_name VARCHAR(100),  -- Depends only on student_id
    course_name VARCHAR(100),   -- Depends only on course_id
    grade CHAR(1),
    PRIMARY KEY (student_id, course_id)
);

-- GOOD: Separate tables eliminate partial dependencies
CREATE TABLE students (
    id INT PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE courses (
    id INT PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE enrollments (
    student_id INT REFERENCES students(id),
    course_id INT REFERENCES courses(id),
    grade CHAR(1),
    PRIMARY KEY (student_id, course_id)
);
```

#### Third Normal Form (3NF)
- **2NF Compliance**: Must satisfy Second Normal Form
- **Transitive Dependency Elimination**: Non-key attributes should not depend on other non-key attributes
- **Direct Dependency**: Non-key attributes depend directly on the primary key

**Example Violation:**
```sql
-- BAD: Employee table with transitive dependency
CREATE TABLE employees (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    department_id INT,
    department_name VARCHAR(100),  -- Depends on department_id, not employee id
    department_budget DECIMAL(10,2) -- Transitive dependency
);

-- GOOD: Separate department information
CREATE TABLE departments (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    budget DECIMAL(10,2)
);

CREATE TABLE employees (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    department_id INT REFERENCES departments(id)
);
```

#### Boyce-Codd Normal Form (BCNF)
- **3NF Compliance**: Must satisfy Third Normal Form
- **Determinant Key Rule**: Every determinant must be a candidate key
- **Stricter 3NF**: Handles anomalies not covered by 3NF

### Denormalization Strategies

#### When to Denormalize
1. **Read-Heavy Workloads**: High query frequency with acceptable write trade-offs
2. **Performance Bottlenecks**: Join operations causing significant latency
3. **Aggregation Needs**: Frequent calculation of derived values
4. **Caching Requirements**: Pre-computed results for common queries

#### Common Denormalization Patterns

**Redundant Storage**
```sql
-- Store calculated values to avoid expensive joins
CREATE TABLE orders (
    id INT PRIMARY KEY,
    customer_id INT REFERENCES customers(id),
    customer_name VARCHAR(100), -- Denormalized from customers table
    order_total DECIMAL(10,2),  -- Denormalized calculation
    created_at TIMESTAMP
);
```

**Materialized Aggregates**
```sql
-- Pre-computed summary tables
CREATE TABLE customer_statistics (
    customer_id INT PRIMARY KEY,
    total_orders INT,
    lifetime_value DECIMAL(12,2),
    last_order_date DATE,
    updated_at TIMESTAMP
);
```

## Index Optimization Strategies

### B-Tree Indexes
- **Default Choice**: Best for range queries, sorting, and equality matches
- **Column Order**: Most selective columns first for composite indexes
- **Prefix Matching**: Supports leading column subset queries
- **Maintenance Cost**: Balanced tree structure with logarithmic operations

### Hash Indexes
- **Equality Queries**: Optimal for exact match lookups
- **Memory Efficiency**: Constant-time access for single-value queries
- **Range Limitations**: Cannot support range or partial matches
- **Use Cases**: Primary keys, unique constraints, cache keys

### Composite Indexes
```sql
-- Query pattern determines optimal column order
-- Query: WHERE status = 'active' AND created_date > '2023-01-01' ORDER BY priority DESC
CREATE INDEX idx_task_status_date_priority 
ON tasks (status, created_date, priority DESC);

-- Query: WHERE user_id = 123 AND category IN ('A', 'B') AND date_field BETWEEN '...' AND '...'
CREATE INDEX idx_user_category_date 
ON user_activities (user_id, category, date_field);
```

### Covering Indexes
```sql
-- Include additional columns to avoid table lookups
CREATE INDEX idx_user_email_covering 
ON users (email) 
INCLUDE (first_name, last_name, status);

-- Query can be satisfied entirely from the index
-- SELECT first_name, last_name, status FROM users WHERE email = 'user@example.com';
```

### Partial Indexes
```sql
-- Index only relevant subset of data
CREATE INDEX idx_active_users_email 
ON users (email) 
WHERE status = 'active';

-- Index for recent orders only
CREATE INDEX idx_recent_orders_customer 
ON orders (customer_id, created_at) 
WHERE created_at > CURRENT_DATE - INTERVAL '30 days';
```

## Query Analysis & Optimization

### Query Patterns Recognition
1. **Equality Filters**: Single-column B-tree indexes
2. **Range Queries**: B-tree with proper column ordering
3. **Text Search**: Full-text indexes or trigram indexes
4. **Join Operations**: Foreign key indexes on both sides
5. **Sorting Requirements**: Indexes matching ORDER BY clauses

### Index Selection Algorithm
```
1. Identify WHERE clause columns
2. Determine most selective columns first
3. Consider JOIN conditions
4. Include ORDER BY columns if possible
5. Evaluate covering index opportunities
6. Check for existing overlapping indexes
```

## Data Modeling Patterns

### Star Schema (Data Warehousing)
```sql
-- Central fact table
CREATE TABLE sales_facts (
    sale_id BIGINT PRIMARY KEY,
    product_id INT REFERENCES products(id),
    customer_id INT REFERENCES customers(id),
    date_id INT REFERENCES date_dimension(id),
    store_id INT REFERENCES stores(id),
    quantity INT,
    unit_price DECIMAL(8,2),
    total_amount DECIMAL(10,2)
);

-- Dimension tables
CREATE TABLE date_dimension (
    id INT PRIMARY KEY,
    date_value DATE,
    year INT,
    quarter INT,
    month INT,
    day_of_week INT,
    is_weekend BOOLEAN
);
```

### Snowflake Schema
```sql
-- Normalized dimension tables
CREATE TABLE products (
    id INT PRIMARY KEY,
    name VARCHAR(200),
    category_id INT REFERENCES product_categories(id),
    brand_id INT REFERENCES brands(id)
);

CREATE TABLE product_categories (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    parent_category_id INT REFERENCES product_categories(id)
);
```

### Document Model (JSON Storage)
```sql
-- Flexible document storage with indexing
CREATE TABLE documents (
    id UUID PRIMARY KEY,
    document_type VARCHAR(50),
    data JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Index on JSON properties
CREATE INDEX idx_documents_user_id 
ON documents USING GIN ((data->>'user_id'));

CREATE INDEX idx_documents_status 
ON documents ((data->>'status')) 
WHERE document_type = 'order';
```

### Graph Data Patterns
```sql
-- Adjacency list for hierarchical data
CREATE TABLE categories (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    parent_id INT REFERENCES categories(id),
    level INT,
    path VARCHAR(500)  -- Materialized path: "/1/5/12/"
);

-- Many-to-many relationships
CREATE TABLE relationships (
    id UUID PRIMARY KEY,
    from_entity_id UUID,
    to_entity_id UUID,
    relationship_type VARCHAR(50),
    created_at TIMESTAMP,
    INDEX (from_entity_id, relationship_type),
    INDEX (to_entity_id, relationship_type)
);
```

## Migration Strategies

### Zero-Downtime Migration (Expand-Contract Pattern)

**Phase 1: Expand**
```sql
-- Add new column without constraints
ALTER TABLE users ADD COLUMN new_email VARCHAR(255);

-- Backfill data in batches
UPDATE users SET new_email = email WHERE id BETWEEN 1 AND 1000;
-- Continue in batches...

-- Add constraints after backfill
ALTER TABLE users ADD CONSTRAINT users_new_email_unique UNIQUE (new_email);
ALTER TABLE users ALTER COLUMN new_email SET NOT NULL;
```

**Phase 2: Contract**
```sql
-- Update application to use new column
-- Deploy application changes
-- Verify new column is being used

-- Remove old column
ALTER TABLE users DROP COLUMN email;
-- Rename new column
ALTER TABLE users RENAME COLUMN new_email TO email;
```

### Data Type Changes
```sql
-- Safe string to integer conversion
ALTER TABLE products ADD COLUMN sku_number INTEGER;
UPDATE products SET sku_number = CAST(sku AS INTEGER) WHERE sku ~ '^[0-9]+$';
-- Validate conversion success before dropping old column
```

## Partitioning Strategies

### Horizontal Partitioning (Sharding)
```sql
-- Range partitioning by date
CREATE TABLE sales_2023 PARTITION OF sales
FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');

CREATE TABLE sales_2024 PARTITION OF sales
FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

-- Hash partitioning by user_id
CREATE TABLE user_data_0 PARTITION OF user_data
FOR VALUES WITH (MODULUS 4, REMAINDER 0);

CREATE TABLE user_data_1 PARTITION OF user_data
FOR VALUES WITH (MODULUS 4, REMAINDER 1);
```

### Vertical Partitioning
```sql
-- Separate frequently accessed columns
CREATE TABLE users_core (
    id INT PRIMARY KEY,
    email VARCHAR(255),
    status VARCHAR(20),
    created_at TIMESTAMP
);

-- Less frequently accessed profile data
CREATE TABLE users_profile (
    user_id INT PRIMARY KEY REFERENCES users_core(id),
    bio TEXT,
    preferences JSONB,
    last_login TIMESTAMP
);
```

## Connection Management

### Connection Pooling
- **Pool Size**: CPU cores × 2 + effective spindle count
- **Connection Lifetime**: Rotate connections to prevent resource leaks
- **Timeout Settings**: Connection, idle, and query timeouts
- **Health Checks**: Regular connection validation

### Read Replicas Strategy
```sql
-- Write queries to primary
INSERT INTO users (email, name) VALUES ('user@example.com', 'John Doe');

-- Read queries to replicas (with appropriate read preference)
SELECT * FROM users WHERE status = 'active';  -- Route to read replica

-- Consistent reads when required
SELECT * FROM users WHERE id = LAST_INSERT_ID();  -- Route to primary
```

## Caching Layers

### Cache-Aside Pattern
```python
def get_user(user_id):
    # Try cache first
    user = cache.get(f"user:{user_id}")
    if user is None:
        # Cache miss - query database
        user = db.query("SELECT * FROM users WHERE id = %s", user_id)
        # Store in cache
        cache.set(f"user:{user_id}", user, ttl=3600)
    return user
```

### Write-Through Cache
- **Consistency**: Always keep cache and database in sync
- **Write Latency**: Higher due to dual writes
- **Data Safety**: No data loss on cache failures

### Cache Invalidation Strategies
1. **TTL-Based**: Time-based expiration
2. **Event-Driven**: Invalidate on data changes
3. **Version-Based**: Use version numbers for consistency
4. **Tag-Based**: Group related cache entries

## Database Selection Guide

### SQL Databases
**PostgreSQL**
- **Strengths**: ACID compliance, complex queries, JSON support, extensibility
- **Use Cases**: OLTP applications, data warehousing, geospatial data
- **Scale**: Vertical scaling with read replicas

**MySQL**
- **Strengths**: Performance, replication, wide ecosystem support
- **Use Cases**: Web applications, content management, e-commerce
- **Scale**: Horizontal scaling through sharding

### NoSQL Databases

**Document Stores (MongoDB, CouchDB)**
- **Strengths**: Flexible schema, horizontal scaling, developer productivity
- **Use Cases**: Content management, catalogs, user profiles
- **Trade-offs**: Eventual consistency, complex queries limitations

**Key-Value Stores (Redis, DynamoDB)**
- **Strengths**: High performance, simple model, excellent caching
- **Use Cases**: Session storage, real-time analytics, gaming leaderboards
- **Trade-offs**: Limited query capabilities, data modeling constraints

**Column-Family (Cassandra, HBase)**
- **Strengths**: Write-heavy workloads, linear scalability, fault tolerance
- **Use Cases**: Time-series data, IoT applications, messaging systems
- **Trade-offs**: Query flexibility, consistency model complexity

**Graph Databases (Neo4j, Amazon Neptune)**
- **Strengths**: Relationship queries, pattern matching, recommendation engines
- **Use Cases**: Social networks, fraud detection, knowledge graphs
- **Trade-offs**: Specialized use cases, learning curve

### NewSQL Databases
**Distributed SQL (CockroachDB, TiDB, Spanner)**
- **Strengths**: SQL compatibility with horizontal scaling
- **Use Cases**: Global applications requiring ACID guarantees
- **Trade-offs**: Complexity, latency for distributed transactions

## Tools & Scripts

### Schema Analyzer
- **Input**: SQL DDL files, JSON schema definitions
- **Analysis**: Normalization compliance, constraint validation, naming conventions
- **Output**: Analysis report, Mermaid ERD, improvement recommendations

### Index Optimizer
- **Input**: Schema definition, query patterns
- **Analysis**: Missing indexes, redundancy detection, selectivity estimation
- **Output**: Index recommendations, CREATE INDEX statements, performance projections

### Migration Generator
- **Input**: Current and target schemas
- **Analysis**: Schema differences, dependency resolution, risk assessment
- **Output**: Migration scripts, rollback plans, validation queries

## Best Practices

### Schema Design
1. **Use meaningful names**: Clear, consistent naming conventions
2. **Choose appropriate data types**: Right-sized columns for storage efficiency
3. **Define proper constraints**: Foreign keys, check constraints, unique indexes
4. **Consider future growth**: Plan for scale from the beginning
5. **Document relationships**: Clear foreign key relationships and business rules

### Performance Optimization
1. **Index strategically**: Cover common query patterns without over-indexing
2. **Monitor query performance**: Regular analysis of slow queries
3. **Partition large tables**: Improve query performance and maintenance
4. **Use appropriate isolation levels**: Balance consistency with performance
5. **Implement connection pooling**: Efficient resource utilization

### Security Considerations
1. **Principle of least privilege**: Grant minimal necessary permissions
2. **Encrypt sensitive data**: At rest and in transit
3. **Audit access patterns**: Monitor and log database access
4. **Validate inputs**: Prevent SQL injection attacks
5. **Regular security updates**: Keep database software current

## Conclusion

Effective database design requires balancing multiple competing concerns: performance, scalability, maintainability, and business requirements. This skill provides the tools and knowledge to make informed decisions throughout the database lifecycle, from initial schema design through production optimization and evolution.

The included tools automate common analysis and optimization tasks, while the comprehensive guides provide the theoretical foundation for making sound architectural decisions. Whether building a new system or optimizing an existing one, these resources provide expert-level guidance for creating robust, scalable database solutions.

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Schema analyzer reports false 1NF violations | JSON or array columns detected as multi-valued fields | Review flagged columns; intentional JSONB/array usage is valid for document-style storage patterns |
| Index optimizer recommends indexes on low-selectivity columns | Boolean or status columns appear in frequent WHERE clauses | Use partial indexes (`WHERE status = 'active'`) instead of full-column indexes to reduce overhead |
| Migration generator produces high-risk steps for column type changes | Direct `ALTER COLUMN ... TYPE` can lock tables and fail on incompatible data | Use the `--zero-downtime` flag to generate expand-contract migration patterns with safe backfill steps |
| ERD output missing relationships | Foreign key constraints not declared in DDL or JSON input | Ensure all FK relationships are explicitly defined; the analyzer only detects declared constraints |
| Composite index column order seems wrong | Optimizer orders by estimated selectivity, not query clause order | Verify cardinality estimates in the schema JSON; provide `cardinality_estimate` per column for accurate ordering |
| Redundancy analysis flags covering indexes as overlapping | Overlap ratio calculation uses Jaccard similarity on column sets | Review flagged pairs manually; covering indexes with INCLUDE columns serve a different purpose than their subsets |
| Validation queries fail after migration | Target schema JSON does not match actual post-migration state | Run `--validate-only` before and after migration; ensure the target JSON reflects all intended changes precisely |

## Success Criteria

- Schema analysis detects 90%+ of normalization violations (1NF through BCNF) when provided complete DDL input
- Index recommendations reduce query execution time by 40%+ for analyzed query patterns (measured via EXPLAIN ANALYZE before/after)
- Migration scripts execute with zero data loss and include verified rollback for every forward step
- ERD generation produces valid Mermaid diagrams that render correctly for schemas with up to 50 tables
- Redundant index detection identifies 95%+ of duplicate and overlapping indexes with less than 5% false positive rate
- Zero-downtime migrations maintain full application availability during schema changes on tables with 10M+ rows
- Generated SQL statements are syntactically valid and compatible with PostgreSQL 14+ and MySQL 8.0+

## Scope & Limitations

**Covers:**
- Schema design analysis for SQL databases (PostgreSQL, MySQL) including normalization, constraints, naming, and data types
- Index optimization with selectivity estimation, composite index ordering, covering indexes, and redundancy detection
- Migration generation with forward/rollback scripts, zero-downtime patterns, and validation queries
- ERD generation in Mermaid format from DDL or JSON schema definitions

**Does NOT cover:**
- Runtime query performance monitoring or live database profiling (see `performance-profiler` skill)
- NoSQL-specific schema design for MongoDB, DynamoDB, or Cassandra (conceptual guidance only in the reference sections)
- Database administration tasks such as backup/restore, replication setup, or user/role management
- Application-level ORM configuration, connection pool tuning, or driver-specific optimizations (see `database-schema-designer` for ORM-adjacent patterns)

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `migration-architect` | Migration strategy and execution planning for large-scale schema changes | Database Designer generates migration SQL; Migration Architect orchestrates multi-service deployment order and rollback coordination |
| `database-schema-designer` | Complementary schema design with focus on application-layer patterns | Database Designer provides normalization analysis; Schema Designer applies ORM mapping and application modeling conventions |
| `performance-profiler` | Runtime validation of index and schema optimization recommendations | Database Designer outputs recommended indexes; Performance Profiler measures actual query plan improvements via EXPLAIN ANALYZE |
| `api-design-reviewer` | Alignment between database schema and API resource contracts | Database Designer defines table structures; API Design Reviewer validates that endpoint schemas match underlying data models |
| `ci-cd-pipeline-builder` | Automated migration execution in deployment pipelines | Database Designer generates migration scripts; CI/CD Pipeline Builder integrates them into deployment stages with validation gates |
| `observability-designer` | Database performance monitoring and alerting post-optimization | Database Designer identifies query patterns; Observability Designer configures slow query alerts and index usage dashboards |

## Tool Reference

### schema_analyzer.py

**Purpose:** Analyzes SQL DDL statements and JSON schema definitions for normalization compliance, missing constraints, data type issues, naming convention violations, and relationship mapping. Generates Mermaid ERD diagrams.

**Usage:**
```bash
python schema_analyzer.py --input schema.sql --output-format json
python schema_analyzer.py --input schema.json --output-format text
python schema_analyzer.py --input schema.sql --generate-erd --output analysis.json
python schema_analyzer.py --input schema.sql --erd-only
```

**Flags/Parameters:**

| Flag | Short | Required | Description |
|------|-------|----------|-------------|
| `--input` | `-i` | Yes | Input file path (SQL DDL or JSON schema) |
| `--output` | `-o` | No | Output file path (default: stdout) |
| `--output-format` | `-f` | No | Output format: `json` or `text` (default: `text`) |
| `--generate-erd` | `-e` | No | Include Mermaid ERD diagram in output |
| `--erd-only` | | No | Output only the Mermaid ERD diagram |

**Example:**
```bash
python schema_analyzer.py -i my_schema.sql -f json -e -o report.json
```

**Output Formats:**
- `text` -- Human-readable report with normalization findings, constraint issues, data type recommendations, and naming violations
- `json` -- Structured JSON with `normalization_issues`, `constraint_issues`, `data_type_issues`, `naming_issues`, `relationships`, and optional `erd_diagram` fields

---

### index_optimizer.py

**Purpose:** Analyzes schema definitions and query patterns to recommend optimal indexes. Identifies missing indexes, detects redundant and overlapping indexes, suggests composite index column ordering, estimates selectivity, and generates CREATE INDEX statements.

**Usage:**
```bash
python index_optimizer.py --schema schema.json --queries queries.json --format text
python index_optimizer.py --schema schema.json --queries queries.json --output recommendations.json --format json
python index_optimizer.py --schema schema.json --queries queries.json --analyze-existing
python index_optimizer.py --schema schema.json --queries queries.json --min-priority 2
```

**Flags/Parameters:**

| Flag | Short | Required | Description |
|------|-------|----------|-------------|
| `--schema` | `-s` | Yes | Schema definition JSON file |
| `--queries` | `-q` | Yes | Query patterns JSON file |
| `--output` | `-o` | No | Output file path (default: stdout) |
| `--format` | `-f` | No | Output format: `json` or `text` (default: `text`) |
| `--analyze-existing` | `-e` | No | Include analysis of existing indexes for redundancy |
| `--min-priority` | `-p` | No | Minimum priority level to include: 1=highest, 4=lowest (default: `4`) |

**Example:**
```bash
python index_optimizer.py -s schema.json -q queries.json -f json -e -p 2 -o index_report.json
```

**Output Formats:**
- `text` -- Human-readable report with analysis summary, high-priority recommendations, redundancy issues, performance impact analysis, and CREATE INDEX statements
- `json` -- Structured JSON with `analysis_summary`, `index_recommendations` (by priority), `redundancy_analysis`, `size_estimates`, `sql_statements`, and `performance_impact` fields

---

### migration_generator.py

**Purpose:** Generates safe migration scripts between schema versions. Compares current and target schemas, produces ALTER TABLE statements, implements zero-downtime expand-contract patterns, creates rollback scripts, and generates validation queries.

**Usage:**
```bash
python migration_generator.py --current current.json --target target.json --format text
python migration_generator.py --current current.json --target target.json --output migration.sql --format sql
python migration_generator.py --current current.json --target target.json --zero-downtime --format json
python migration_generator.py --current current.json --target target.json --validate-only
```

**Flags/Parameters:**

| Flag | Short | Required | Description |
|------|-------|----------|-------------|
| `--current` | `-c` | Yes | Current schema JSON file |
| `--target` | `-t` | Yes | Target schema JSON file |
| `--output` | `-o` | No | Output file path (default: stdout) |
| `--format` | `-f` | No | Output format: `json`, `text`, or `sql` (default: `text`) |
| `--zero-downtime` | `-z` | No | Generate zero-downtime migration using expand-contract pattern |
| `--validate-only` | `-v` | No | Only generate validation queries, skip migration steps |
| `--include-validations` | | No | Include validation queries in migration output |

**Example:**
```bash
python migration_generator.py -c current.json -t target.json -z --include-validations -f json -o migration_plan.json
```

**Output Formats:**
- `text` -- Human-readable migration plan with ordered steps, forward SQL, rollback SQL, risk levels, and execution timeline
- `json` -- Structured JSON with `migration_id`, `steps` (each with `sql_forward`, `sql_rollback`, `validation_sql`, `risk_level`, `zero_downtime_phase`), `summary`, `execution_order`, and `rollback_order`
- `sql` -- Raw SQL output with forward migration statements, suitable for direct execution or piping into a database client