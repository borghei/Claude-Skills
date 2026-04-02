---
name: database-designer
description: >
  Provides expert-level database design with schema analysis, index
  optimization, and migration generation. Supports PostgreSQL, MySQL, MongoDB,
  and DynamoDB. Use when designing schemas, optimizing queries, planning
  migrations, or analyzing database performance.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: databases
  tier: POWERFUL
  updated: 2026-03-31
---
# Database Designer

The agent analyzes SQL schemas for normalization compliance, recommends optimal indexes based on query patterns, and generates safe migration scripts with rollback procedures. It produces Mermaid ERDs, detects redundant indexes, and implements zero-downtime expand-contract migration patterns for PostgreSQL and MySQL.

## Quick Start

```bash
# Analyze a schema for normalization issues and generate ERD
python schema_analyzer.py --input schema.sql --generate-erd --output-format json

# Recommend indexes based on query patterns
python index_optimizer.py --schema schema.json --queries queries.json --analyze-existing

# Generate migration scripts between schema versions
python migration_generator.py --current current.json --target target.json --zero-downtime
```

---

## Core Workflows

### Workflow 1: Analyze and Optimize a Schema

1. Provide DDL (SQL) or JSON schema definition
2. Run `schema_analyzer.py` to detect normalization violations (1NF-BCNF), missing constraints, and naming issues
3. Review generated Mermaid ERD for relationship visualization
4. Run `index_optimizer.py` with query patterns to get index recommendations
5. **Validation checkpoint:** All 1NF-3NF violations addressed; foreign keys declared; no redundant indexes

```bash
python schema_analyzer.py -i schema.sql -f json -e -o report.json
python index_optimizer.py -s schema.json -q queries.json -e -p 2 -o index_report.json
```

### Workflow 2: Generate a Safe Migration

1. Export current and target schemas as JSON
2. Run `migration_generator.py` to produce forward and rollback SQL
3. For large tables (10M+ rows), add `--zero-downtime` for expand-contract pattern
4. Review validation queries that confirm migration success
5. **Validation checkpoint:** Every forward step has a rollback counterpart; validation queries pass on test data

```bash
python migration_generator.py -c current.json -t target.json -z --include-validations -f json -o plan.json
```

### Workflow 3: Index Optimization for Query Patterns

1. Document top 10 query patterns as JSON (WHERE clauses, JOINs, ORDER BY)
2. Run `index_optimizer.py` with `--analyze-existing` to find redundancies
3. Review composite index column ordering (most selective first)
4. Check for covering index opportunities
5. **Validation checkpoint:** Query patterns covered; no overlapping indexes; estimated 40%+ query time reduction

---

## Index Type Selection

| Index Type | Best For | Example |
|------------|----------|---------|
| B-tree | Range queries, sorting, equality | `CREATE INDEX idx ON tasks (status, created_date)` |
| Partial | Subset queries on hot data | `CREATE INDEX idx ON users (email) WHERE status = 'active'` |
| Covering | Avoiding table lookups | `CREATE INDEX idx ON users (email) INCLUDE (name, status)` |
| Hash | Exact match only | Primary keys, cache keys |
| GIN | JSONB, array, full-text | `CREATE INDEX idx ON docs USING GIN (data)` |

---

## Anti-Patterns

- **Over-indexing** -- every column indexed wastes write performance and storage; index only columns appearing in WHERE, JOIN, and ORDER BY
- **Missing foreign keys** -- relying on application-layer referential integrity leads to orphaned records; always declare FK constraints
- **VARCHAR(255) everywhere** -- oversized columns waste memory in indexes; right-size columns based on actual data
- **Premature denormalization** -- denormalize only when EXPLAIN ANALYZE shows join-related bottlenecks, not preemptively
- **Direct ALTER on large tables** -- `ALTER TABLE ... SET NOT NULL` on a 100M-row table locks the table; use expand-contract pattern
- **No validation queries in migrations** -- migrations without post-step validation risk silent data corruption

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