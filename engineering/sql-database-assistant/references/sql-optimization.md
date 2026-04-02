# SQL Optimization Reference

## Index Strategies

### B-Tree Indexes (Default)
Best for: equality checks, range queries, sorting, prefix LIKE.

```sql
-- Single column index
CREATE INDEX idx_users_email ON users (email);

-- Composite index (column order matters)
CREATE INDEX idx_orders_user_date ON orders (user_id, created_at);

-- Partial index (PostgreSQL)
CREATE INDEX idx_active_users ON users (email) WHERE active = true;
```

### Index Selection Rules
1. Index columns used in WHERE, JOIN ON, ORDER BY
2. Put equality columns first in composite indexes
3. Put range columns last
4. Don't over-index (each index slows writes)
5. Monitor unused indexes and remove them

### Covering Indexes
Include all columns a query needs to avoid table lookup:
```sql
CREATE INDEX idx_covering ON orders (user_id, status) INCLUDE (total, created_at);
```

## Query Anti-Patterns

### SELECT *
```sql
-- Bad: fetches all columns
SELECT * FROM users WHERE active = true;

-- Good: fetch only needed columns
SELECT id, name, email FROM users WHERE active = true;
```

### Leading Wildcard LIKE
```sql
-- Bad: full table scan, cannot use index
SELECT * FROM users WHERE name LIKE '%smith%';

-- Better: use full-text search
SELECT * FROM users WHERE to_tsvector(name) @@ to_tsquery('smith');
```

### Functions on Indexed Columns
```sql
-- Bad: prevents index usage
SELECT * FROM orders WHERE YEAR(created_at) = 2024;

-- Good: use range instead
SELECT * FROM orders WHERE created_at >= '2024-01-01' AND created_at < '2025-01-01';
```

### N+1 Queries
```sql
-- Bad: correlated subquery (runs once per row)
SELECT u.name,
  (SELECT COUNT(*) FROM orders WHERE user_id = u.id) AS order_count
FROM users u;

-- Good: single JOIN
SELECT u.name, COUNT(o.id) AS order_count
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
GROUP BY u.id, u.name;
```

### Large OFFSET Pagination
```sql
-- Bad: scans and discards 10000 rows
SELECT * FROM products ORDER BY id LIMIT 20 OFFSET 10000;

-- Good: keyset pagination
SELECT * FROM products WHERE id > 10000 ORDER BY id LIMIT 20;
```

## JOIN Optimization

### JOIN Types Performance
1. **INNER JOIN** - Most efficient, only matching rows
2. **LEFT JOIN** - Returns all left rows, matching right
3. **CROSS JOIN** - Cartesian product (avoid unless intentional)
4. **Subquery** - Often slower than equivalent JOIN

### JOIN Best Practices
- Always have indexes on JOIN columns
- Join on integer PKs/FKs when possible
- Filter early (WHERE before JOIN when possible)
- Use EXPLAIN to verify join order

## EXPLAIN Analysis

### Key Metrics
| Metric | Good | Bad |
|--------|------|-----|
| Scan type | Index Scan, Index Only Scan | Seq Scan on large table |
| Rows estimated | Close to actual | Off by 10x+ |
| Sort method | Index | External merge/disk |
| Join type | Nested Loop (small), Hash (medium) | Nested Loop on large tables |

### Reading EXPLAIN Output
```sql
EXPLAIN ANALYZE SELECT * FROM orders WHERE user_id = 123;
-- Look for:
-- 1. Scan type (Index Scan vs Seq Scan)
-- 2. Actual rows vs estimated rows
-- 3. Execution time
-- 4. Sort operations
```

## Migration Best Practices

### Safe Column Addition
```sql
-- Step 1: Add nullable column
ALTER TABLE users ADD COLUMN phone VARCHAR(20);

-- Step 2: Backfill data
UPDATE users SET phone = '' WHERE phone IS NULL;

-- Step 3: Add constraint (if needed)
ALTER TABLE users ALTER COLUMN phone SET NOT NULL;
```

### Safe Column Rename
```sql
-- Never: ALTER TABLE users RENAME COLUMN name TO full_name;
-- Instead:
-- Step 1: Add new column
ALTER TABLE users ADD COLUMN full_name VARCHAR(255);
-- Step 2: Migrate data
UPDATE users SET full_name = name;
-- Step 3: Update application to use new column
-- Step 4: Drop old column (after deployment)
ALTER TABLE users DROP COLUMN name;
```

### Zero-Downtime Migrations
1. Add columns as nullable (no lock)
2. Create indexes CONCURRENTLY (PostgreSQL)
3. Backfill in batches, not all at once
4. Apply NOT NULL after backfill is complete
5. Drop columns only after code no longer references them
