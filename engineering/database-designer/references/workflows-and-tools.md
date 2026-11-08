# Database Designer — Workflows & Tool Reference

Read this when running the end-to-end analyze/optimize/migrate process, or when you need
the full CLI flags, usage, and output formats for the three scripts.

## Quick Start

```bash
# Analyze a schema for normalization issues and generate ERD
python3 scripts/schema_analyzer.py --input schema.sql --generate-erd --output-format json

# Recommend indexes based on query patterns
python3 scripts/index_optimizer.py --schema schema.json --queries queries.json --analyze-existing

# Generate migration scripts between schema versions
python3 scripts/migration_generator.py --current current.json --target target.json --zero-downtime
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
python3 scripts/schema_analyzer.py -i schema.sql -f json -e -o report.json
python3 scripts/index_optimizer.py -s schema.json -q queries.json -e -p 2 -o index_report.json
```

### Workflow 2: Generate a Safe Migration

1. Export current and target schemas as JSON
2. Run `migration_generator.py` to produce forward and rollback SQL
3. For large tables (10M+ rows), add `--zero-downtime` for expand-contract pattern
4. Review validation queries that confirm migration success
5. **Validation checkpoint:** Every forward step has a rollback counterpart; validation queries pass on test data

```bash
python3 scripts/migration_generator.py -c current.json -t target.json -z --include-validations -f json -o plan.json
```

### Workflow 3: Index Optimization for Query Patterns

1. Document top 10 query patterns as JSON (WHERE clauses, JOINs, ORDER BY)
2. Run `index_optimizer.py` with `--analyze-existing` to find redundancies
3. Review composite index column ordering (most selective first)
4. Check for covering index opportunities
5. **Validation checkpoint:** Query patterns covered; no overlapping indexes; estimated 40%+ query time reduction

---

## Tool Reference

### schema_analyzer.py

**Purpose:** Analyzes SQL DDL statements and JSON schema definitions for normalization compliance, missing constraints, data type issues, naming convention violations, and relationship mapping. Generates Mermaid ERD diagrams.

**Usage:**
```bash
python3 scripts/schema_analyzer.py --input schema.sql --output-format json
python3 scripts/schema_analyzer.py --input schema.json --output-format text
python3 scripts/schema_analyzer.py --input schema.sql --generate-erd --output analysis.json
python3 scripts/schema_analyzer.py --input schema.sql --erd-only
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
python3 scripts/schema_analyzer.py -i my_schema.sql -f json -e -o report.json
```

**Output Formats:**
- `text` -- Human-readable report with normalization findings, constraint issues, data type recommendations, and naming violations
- `json` -- Structured JSON with `normalization_issues`, `constraint_issues`, `data_type_issues`, `naming_issues`, `relationships`, and optional `erd_diagram` fields

---

### index_optimizer.py

**Purpose:** Analyzes schema definitions and query patterns to recommend optimal indexes. Identifies missing indexes, detects redundant and overlapping indexes, suggests composite index column ordering, estimates selectivity, and generates CREATE INDEX statements.

**Usage:**
```bash
python3 scripts/index_optimizer.py --schema schema.json --queries queries.json --format text
python3 scripts/index_optimizer.py --schema schema.json --queries queries.json --output recommendations.json --format json
python3 scripts/index_optimizer.py --schema schema.json --queries queries.json --analyze-existing
python3 scripts/index_optimizer.py --schema schema.json --queries queries.json --min-priority 2
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
python3 scripts/index_optimizer.py -s schema.json -q queries.json -f json -e -p 2 -o index_report.json
```

**Output Formats:**
- `text` -- Human-readable report with analysis summary, high-priority recommendations, redundancy issues, performance impact analysis, and CREATE INDEX statements
- `json` -- Structured JSON with `analysis_summary`, `index_recommendations` (by priority), `redundancy_analysis`, `size_estimates`, `sql_statements`, and `performance_impact` fields

---

### migration_generator.py

**Purpose:** Generates safe migration scripts between schema versions. Compares current and target schemas, produces ALTER TABLE statements, implements zero-downtime expand-contract patterns, creates rollback scripts, and generates validation queries.

**Usage:**
```bash
python3 scripts/migration_generator.py --current current.json --target target.json --format text
python3 scripts/migration_generator.py --current current.json --target target.json --output migration.sql --format sql
python3 scripts/migration_generator.py --current current.json --target target.json --zero-downtime --format json
python3 scripts/migration_generator.py --current current.json --target target.json --validate-only
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
python3 scripts/migration_generator.py -c current.json -t target.json -z --include-validations -f json -o migration_plan.json
```

**Output Formats:**
- `text` -- Human-readable migration plan with ordered steps, forward SQL, rollback SQL, risk levels, and execution timeline
- `json` -- Structured JSON with `migration_id`, `steps` (each with `sql_forward`, `sql_rollback`, `validation_sql`, `risk_level`, `zero_downtime_phase`), `summary`, `execution_order`, and `rollback_order`
- `sql` -- Raw SQL output with forward migration statements, suitable for direct execution or piping into a database client
