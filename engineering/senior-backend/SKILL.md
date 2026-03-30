---
name: senior-backend
description: >
  This skill should be used when the user asks to "design REST APIs", "optimize
  database queries", "implement authentication", "build microservices", "review
  backend code", "set up GraphQL", "handle database migrations", or "load test
  APIs". Use for Node.js/Express/Fastify development, PostgreSQL optimization,
  API security, and backend architecture patterns.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: backend
  updated: 2026-03-31
  tags: [api-design, microservices, databases, caching, queues]
---
# Senior Backend Engineer

Backend development patterns, API design, database optimization, and security practices.

## Table of Contents

- [Quick Start](#quick-start)
- [Tools Overview](#tools-overview)
  - [API Scaffolder](#1-api-scaffolder)
  - [Database Migration Tool](#2-database-migration-tool)
  - [API Load Tester](#3-api-load-tester)
- [Backend Development Workflows](#backend-development-workflows)
  - [API Design Workflow](#api-design-workflow)
  - [Database Optimization Workflow](#database-optimization-workflow)
  - [Security Hardening Workflow](#security-hardening-workflow)
- [Reference Documentation](#reference-documentation)
- [Common Patterns Quick Reference](#common-patterns-quick-reference)

---

## Quick Start

```bash
# Generate API routes from OpenAPI spec
python scripts/api_scaffolder.py openapi.yaml --framework express --output src/routes/

# Analyze database schema and generate migrations
python scripts/database_migration_tool.py --connection postgres://localhost/mydb --analyze

# Load test an API endpoint
python scripts/api_load_tester.py https://api.example.com/users --concurrency 50 --duration 30
```

---

## Tools Overview

### 1. API Scaffolder

Generates API route handlers, middleware, and OpenAPI specifications from schema definitions.

**Input:** OpenAPI spec (YAML/JSON) or database schema
**Output:** Route handlers, validation middleware, TypeScript types

**Usage:**
```bash
# Generate Express routes from OpenAPI spec
python scripts/api_scaffolder.py openapi.yaml --framework express --output src/routes/

# Output:
# Generated 12 route handlers in src/routes/
# - GET /users (listUsers)
# - POST /users (createUser)
# - GET /users/{id} (getUser)
# - PUT /users/{id} (updateUser)
# - DELETE /users/{id} (deleteUser)
# ...
# Created validation middleware: src/middleware/validators.ts
# Created TypeScript types: src/types/api.ts

# Generate from database schema
python scripts/api_scaffolder.py --from-db postgres://localhost/mydb --output src/routes/

# Generate OpenAPI spec from existing routes
python scripts/api_scaffolder.py src/routes/ --generate-spec --output openapi.yaml
```

**Supported Frameworks:**
- Express.js (`--framework express`)
- Fastify (`--framework fastify`)
- Koa (`--framework koa`)

---

### 2. Database Migration Tool

Analyzes database schemas, detects changes, and generates migration files with rollback support.

**Input:** Database connection string or schema files
**Output:** Migration files, schema diff report, optimization suggestions

**Usage:**
```bash
# Analyze current schema and suggest optimizations
python scripts/database_migration_tool.py --connection postgres://localhost/mydb --analyze

# Output:
# === Database Analysis Report ===
# Tables: 24
# Total rows: 1,247,832
#
# MISSING INDEXES (5 found):
#   orders.user_id - 847ms avg query time, ADD INDEX recommended
#   products.category_id - 234ms avg query time, ADD INDEX recommended
#
# N+1 QUERY RISKS (3 found):
#   users -> orders relationship (no eager loading)
#
# SUGGESTED MIGRATIONS:
#   1. Add index on orders(user_id)
#   2. Add index on products(category_id)
#   3. Add composite index on order_items(order_id, product_id)

# Generate migration from schema diff
python scripts/database_migration_tool.py --connection postgres://localhost/mydb \
  --compare schema/v2.sql --output migrations/

# Output:
# Generated migration: migrations/20240115_add_user_indexes.sql
# Generated rollback: migrations/20240115_add_user_indexes_rollback.sql

# Dry-run a migration
python scripts/database_migration_tool.py --connection postgres://localhost/mydb \
  --migrate migrations/20240115_add_user_indexes.sql --dry-run
```

---

### 3. API Load Tester

Performs HTTP load testing with configurable concurrency, measuring latency percentiles and throughput.

**Input:** API endpoint URL and test configuration
**Output:** Performance report with latency distribution, error rates, throughput metrics

**Usage:**
```bash
# Basic load test
python scripts/api_load_tester.py https://api.example.com/users --concurrency 50 --duration 30

# Output:
# === Load Test Results ===
# Target: https://api.example.com/users
# Duration: 30s | Concurrency: 50
#
# THROUGHPUT:
#   Total requests: 15,247
#   Requests/sec: 508.2
#   Successful: 15,102 (99.0%)
#   Failed: 145 (1.0%)
#
# LATENCY (ms):
#   Min: 12
#   Avg: 89
#   P50: 67
#   P95: 198
#   P99: 423
#   Max: 1,247
#
# ERRORS:
#   Connection timeout: 89
#   HTTP 503: 56
#
# RECOMMENDATION: P99 latency (423ms) exceeds 200ms target.
# Consider: connection pooling, query optimization, or horizontal scaling.

# Test with custom headers and body
python scripts/api_load_tester.py https://api.example.com/orders \
  --method POST \
  --header "Authorization: Bearer token123" \
  --body '{"product_id": 1, "quantity": 2}' \
  --concurrency 100 \
  --duration 60

# Compare two endpoints
python scripts/api_load_tester.py https://api.example.com/v1/users https://api.example.com/v2/users \
  --compare --concurrency 50 --duration 30
```

---

## Backend Development Workflows

### API Design Workflow

Use when designing a new API or refactoring existing endpoints.

**Step 1: Define resources and operations**
```yaml
# openapi.yaml
openapi: 3.0.3
info:
  title: User Service API
  version: 1.0.0
paths:
  /users:
    get:
      summary: List users
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
            default: 20
    post:
      summary: Create user
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateUser'
```

**Step 2: Generate route scaffolding**
```bash
python scripts/api_scaffolder.py openapi.yaml --framework express --output src/routes/
```

**Step 3: Implement business logic**
```typescript
// src/routes/users.ts (generated, then customized)
export const createUser = async (req: Request, res: Response) => {
  const { email, name } = req.body;

  // Add business logic
  const user = await userService.create({ email, name });

  res.status(201).json(user);
};
```

**Step 4: Add validation middleware**
```bash
# Validation is auto-generated from OpenAPI schema
# src/middleware/validators.ts includes:
# - Request body validation
# - Query parameter validation
# - Path parameter validation
```

**Step 5: Generate updated OpenAPI spec**
```bash
python scripts/api_scaffolder.py src/routes/ --generate-spec --output openapi.yaml
```

---

### Database Optimization Workflow

Use when queries are slow or database performance needs improvement.

**Step 1: Analyze current performance**
```bash
python scripts/database_migration_tool.py --connection $DATABASE_URL --analyze
```

**Step 2: Identify slow queries**
```sql
-- Check query execution plans
EXPLAIN ANALYZE SELECT * FROM orders
WHERE user_id = 123
ORDER BY created_at DESC
LIMIT 10;

-- Look for: Seq Scan (bad), Index Scan (good)
```

**Step 3: Generate index migrations**
```bash
python scripts/database_migration_tool.py --connection $DATABASE_URL \
  --suggest-indexes --output migrations/
```

**Step 4: Test migration (dry-run)**
```bash
python scripts/database_migration_tool.py --connection $DATABASE_URL \
  --migrate migrations/add_indexes.sql --dry-run
```

**Step 5: Apply and verify**
```bash
# Apply migration
python scripts/database_migration_tool.py --connection $DATABASE_URL \
  --migrate migrations/add_indexes.sql

# Verify improvement
python scripts/database_migration_tool.py --connection $DATABASE_URL --analyze
```

---

### Security Hardening Workflow

Use when preparing an API for production or after a security review.

**Step 1: Review authentication setup**
```typescript
// Verify JWT configuration
const jwtConfig = {
  secret: process.env.JWT_SECRET,  // Must be from env, never hardcoded
  expiresIn: '1h',                 // Short-lived tokens
  algorithm: 'RS256'               // Prefer asymmetric
};
```

**Step 2: Add rate limiting**
```typescript
import rateLimit from 'express-rate-limit';

const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,  // 15 minutes
  max: 100,                   // 100 requests per window
  standardHeaders: true,
  legacyHeaders: false,
});

app.use('/api/', apiLimiter);
```

**Step 3: Validate all inputs**
```typescript
import { z } from 'zod';

const CreateUserSchema = z.object({
  email: z.string().email().max(255),
  name: z.string().min(1).max(100),
  age: z.number().int().positive().optional()
});

// Use in route handler
const data = CreateUserSchema.parse(req.body);
```

**Step 4: Load test with attack patterns**
```bash
# Test rate limiting
python scripts/api_load_tester.py https://api.example.com/login \
  --concurrency 200 --duration 10 --expect-rate-limit

# Test input validation
python scripts/api_load_tester.py https://api.example.com/users \
  --method POST \
  --body '{"email": "not-an-email"}' \
  --expect-status 400
```

**Step 5: Review security headers**
```typescript
import helmet from 'helmet';

app.use(helmet({
  contentSecurityPolicy: true,
  crossOriginEmbedderPolicy: true,
  crossOriginOpenerPolicy: true,
  crossOriginResourcePolicy: true,
  hsts: { maxAge: 31536000, includeSubDomains: true },
}));
```

---

## Reference Documentation

| File | Contains | Use When |
|------|----------|----------|
| `references/api_design_patterns.md` | REST vs GraphQL, versioning, error handling, pagination | Designing new APIs |
| `references/database_optimization_guide.md` | Indexing strategies, query optimization, N+1 solutions | Fixing slow queries |
| `references/backend_security_practices.md` | OWASP Top 10, auth patterns, input validation | Security hardening |

---

## Common Patterns Quick Reference

### REST API Response Format
```json
{
  "data": { "id": 1, "name": "John" },
  "meta": { "requestId": "abc-123" }
}
```

### Error Response Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid email format",
    "details": [{ "field": "email", "message": "must be valid email" }]
  },
  "meta": { "requestId": "abc-123" }
}
```

### HTTP Status Codes
| Code | Use Case |
|------|----------|
| 200 | Success (GET, PUT, PATCH) |
| 201 | Created (POST) |
| 204 | No Content (DELETE) |
| 400 | Validation error |
| 401 | Authentication required |
| 403 | Permission denied |
| 404 | Resource not found |
| 429 | Rate limit exceeded |
| 500 | Internal server error |

### Database Index Strategy
```sql
-- Single column (equality lookups)
CREATE INDEX idx_users_email ON users(email);

-- Composite (multi-column queries)
CREATE INDEX idx_orders_user_status ON orders(user_id, status);

-- Partial (filtered queries)
CREATE INDEX idx_orders_active ON orders(created_at) WHERE status = 'active';

-- Covering (avoid table lookup)
CREATE INDEX idx_users_email_name ON users(email) INCLUDE (name);
```

---

## Common Commands

```bash
# API Development
python scripts/api_scaffolder.py openapi.yaml --framework express
python scripts/api_scaffolder.py src/routes/ --generate-spec

# Database Operations
python scripts/database_migration_tool.py --connection $DATABASE_URL --analyze
python scripts/database_migration_tool.py --connection $DATABASE_URL --migrate file.sql

# Performance Testing
python scripts/api_load_tester.py https://api.example.com/endpoint --concurrency 50
python scripts/api_load_tester.py https://api.example.com/endpoint --compare baseline.json
```

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| `api_scaffolder.py` generates empty route files | OpenAPI spec missing `operationId` fields or paths use unsupported HTTP methods | Add `operationId` to each operation; verify methods are GET, POST, PUT, PATCH, or DELETE |
| `database_migration_tool.py` parses zero tables | SQL file uses non-standard DDL syntax or multi-line comments break regex parsing | Ensure `CREATE TABLE` statements end with `;` and remove block comments (`/* ... */`) before analysis |
| Load tester reports 100% failure rate | Target URL unreachable, SSL verification failing, or firewall blocking concurrent connections | Verify URL manually with `curl`; try `--no-verify-ssl` for self-signed certs; reduce `--concurrency` |
| Generated TypeScript types show `unknown` for all fields | OpenAPI schema uses `$ref` references to external files or missing `components/schemas` section | Inline referenced schemas or ensure all `$ref` targets exist within the same spec file |
| Migration diff reports "No changes" when changes exist | Column type differences are case-sensitive; `VARCHAR(255)` vs `varchar(255)` treated as different | Normalize casing in schema files; the parser converts types to uppercase internally |
| Load tester hangs after duration expires | Worker threads blocked on slow connections that exceed the default 30s timeout | Set `--timeout` lower than `--duration` (e.g., `--timeout 5 --duration 30`) to prevent thread starvation |
| Zod validators missing for nested objects | Deeply nested `$ref` chains not fully resolved by the scaffolder | Flatten nested schemas in the OpenAPI spec or manually extend the generated validators |

---

## Success Criteria

- **API p99 latency under 200ms** at production concurrency levels, verified by `api_load_tester.py`
- **Zero N+1 query patterns detected** in schema analysis via `database_migration_tool.py --analyze`
- **All foreign key columns indexed** with no "missing index" warnings from the migration tool
- **100% of generated routes include input validation** middleware (Zod schemas auto-generated from OpenAPI spec)
- **Success rate above 99.5%** during sustained load tests at target concurrency for 60+ seconds
- **Every migration paired with a rollback script** to enable zero-downtime deployment reversals
- **API response format consistency** across all endpoints following the standardized `data`/`error`/`meta` envelope pattern

---

## Scope & Limitations

**What this skill covers:**
- REST API design, scaffolding, and OpenAPI-driven code generation for Express, Fastify, and Koa
- PostgreSQL schema analysis, index optimization, migration generation with rollback support
- HTTP load testing with latency percentile analysis, throughput measurement, and endpoint comparison
- Backend security patterns including JWT configuration, rate limiting, input validation, and security headers

**What this skill does NOT cover:**
- Frontend development, UI components, or client-side state management -- see `senior-frontend`
- Infrastructure provisioning, container orchestration, or CI/CD pipeline setup -- see `senior-devops`
- GraphQL schema design, resolvers, or subscriptions -- see `senior-fullstack`
- Application performance monitoring (APM), distributed tracing, or log aggregation -- see `senior-secops`

---

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `senior-fullstack` | API routes generated here feed into fullstack project scaffolding | OpenAPI spec &rarr; fullstack scaffolder consumes as API contract |
| `senior-devops` | Migration scripts output here are consumed by CI/CD deployment pipelines | `migrations/` directory &rarr; deployment workflow applies and verifies |
| `senior-security` | Load test results and security hardening output feed into security review | Load test JSON &rarr; security audit validates rate limiting and error handling |
| `senior-qa` | Generated route handlers and validators provide test surface for QA automation | Route files + Zod schemas &rarr; QA generates integration test suites |
| `senior-frontend` | TypeScript types generated by the scaffolder are shared with frontend consumers | `types.ts` &rarr; frontend imports API types for type-safe client code |
| `code-reviewer` | Schema analysis issues and migration diffs feed into code review checklists | Analysis report &rarr; reviewer validates index coverage and naming conventions |

---

## Tool Reference

### api_scaffolder.py

**Purpose:** Generate Express.js/Fastify/Koa route handlers, Zod validators, and TypeScript types from an OpenAPI specification.

**Usage:**
```bash
python scripts/api_scaffolder.py <spec> [flags]
```

**Flags:**

| Flag | Short | Type | Default | Description |
|------|-------|------|---------|-------------|
| `spec` | | positional | *(required)* | Path to OpenAPI specification file (YAML or JSON) |
| `--output` | `-o` | string | `./generated` | Output directory for generated files |
| `--framework` | `-f` | choice | `express` | Target framework: `express`, `fastify`, or `koa` |
| `--types-only` | | flag | `false` | Generate only TypeScript type definitions, skip routes and validators |
| `--verbose` | `-v` | flag | `false` | Enable verbose output (shows spec title/version) |
| `--json` | | flag | `false` | Output results summary as JSON |

**Example:**
```bash
python scripts/api_scaffolder.py openapi.yaml --framework express --output src/routes/ --verbose
```
```
API Scaffolder - Express
Spec: openapi.yaml
Output: src/routes/
--------------------------------------------------
Loaded: User Service API v1.0.0
  Generated: src/routes/types.ts
  Generated: src/routes/validators.ts
  Generated: src/routes/users.routes.ts (5 handlers)
  Generated: src/routes/index.ts
--------------------------------------------------
Generated 5 route handlers
Generated 3 type definitions
Output: src/routes/
```

**Output Formats:** Human-readable console output by default. Add `--json` for machine-readable JSON with `status`, `generated_files`, `routes_count`, and `types_count` fields.

---

### database_migration_tool.py

**Purpose:** Analyze SQL schema files for issues, compare schemas to generate migrations with rollback scripts, and suggest missing indexes.

**Usage:**
```bash
python scripts/database_migration_tool.py <schema> [flags]
```

**Flags:**

| Flag | Short | Type | Default | Description |
|------|-------|------|---------|-------------|
| `schema` | | positional | *(required)* | Path to SQL schema file |
| `--analyze` | | flag | `false` | Analyze schema for issues and optimizations (default mode if no other mode specified) |
| `--compare` | | string | | Path to a second schema file to compare against and generate migration |
| `--suggest-indexes` | | flag | `false` | Generate index suggestions for foreign keys, filter columns, and timestamps |
| `--output` | `-o` | string | | Output directory for generated migration files |
| `--verbose` | `-v` | flag | `false` | Enable verbose output (shows parsed table count and info-level suggestions) |
| `--json` | | flag | `false` | Output results as JSON |

**Example:**
```bash
python scripts/database_migration_tool.py schema.sql --analyze --verbose
```
```
Database Migration Tool
Schema: schema.sql
--------------------------------------------------
Parsed 8 tables

Analysis Results:
  Tables: 8
  Errors: 1
  Warnings: 3
  Suggestions: 7

ERRORS:
  [audit_log] Table 'audit_log' has no primary key
    Suggestion: Add a primary key column (e.g., 'id SERIAL PRIMARY KEY')

WARNINGS:
  [orders] Foreign key column 'user_id' is not indexed
    Suggestion: CREATE INDEX idx_orders_user_id ON orders(user_id);
```

**Output Formats:** Human-readable console output by default. Add `--json` for structured JSON with `issues_detail` array containing severity, category, table, message, and suggestion for each finding. When using `--compare --output`, generates timestamped `_migration.sql` and `_migration_rollback.sql` files.

---

### api_load_tester.py

**Purpose:** Perform HTTP load testing with configurable concurrency, measuring latency percentiles (p50/p90/p95/p99), throughput, error rates, and optional endpoint comparison.

**Usage:**
```bash
python scripts/api_load_tester.py <urls...> [flags]
```

**Flags:**

| Flag | Short | Type | Default | Description |
|------|-------|------|---------|-------------|
| `urls` | | positional | *(required)* | One or more URLs to test |
| `--method` | `-m` | choice | `GET` | HTTP method: `GET`, `POST`, `PUT`, `PATCH`, or `DELETE` |
| `--body` | `-b` | string | | Request body as a JSON string |
| `--header` | `-H` | string (repeatable) | | HTTP header in `"Name: Value"` format; can be specified multiple times |
| `--concurrency` | `-c` | int | `10` | Number of concurrent request threads |
| `--duration` | `-d` | float | `10.0` | Test duration in seconds |
| `--timeout` | `-t` | float | `30.0` | Per-request timeout in seconds |
| `--compare` | | flag | `false` | Compare two endpoints side-by-side (requires two URLs) |
| `--no-verify-ssl` | | flag | `false` | Disable SSL certificate verification |
| `--verbose` | `-v` | flag | `false` | Enable verbose output (shows transfer bytes and throughput Mbps) |
| `--json` | | flag | `false` | Output results as JSON |
| `--output` | `-o` | string | | File path to write JSON results |

**Example:**
```bash
python scripts/api_load_tester.py https://api.example.com/users \
  --method GET \
  --header "Authorization: Bearer tok_abc123" \
  --concurrency 50 \
  --duration 30 \
  --verbose
```
```
============================================================
LOAD TEST RESULTS
============================================================

Target: https://api.example.com/users
Method: GET
Duration: 30.2s
Concurrency: 50

THROUGHPUT:
  Total requests: 14,832
  Requests/sec: 491.1
  Successful: 14,710 (99.2%)
  Failed: 122

LATENCY (ms):
  Min: 11.3
  Avg: 92.4
  P50: 71.2
  P90: 165.8
  P95: 201.3
  P99: 387.6
  Max: 1,102.5
  StdDev: 89.2

TRANSFER:
  Total bytes: 45,291,520
  Throughput: 12.01 Mbps

RECOMMENDATIONS:
  Warning: P99 latency (388ms) exceeds 500ms
    Consider: Connection pooling, query optimization, caching
  Performance looks good for this load level
============================================================
```

**Output Formats:** Human-readable console report by default with latency distribution and recommendations. Add `--json` for structured JSON output. Use `--output results.json` to write results to a file. When using `--compare` with two URLs, outputs a side-by-side metric comparison table.
