-- queries.sql — SQL queries with common anti-patterns
--
-- These queries contain deliberate issues for the sql-database-assistant
-- skill to detect and suggest improvements:
--   - SELECT * usage
--   - Missing indexes (queries on unindexed columns)
--   - N+1 query patterns
--   - Inefficient subqueries that could be JOINs
--   - Cartesian joins
--   - Non-sargable WHERE clauses
--   - ORDER BY without index support


-- ANTI-PATTERN: SELECT * pulls all columns including large TEXT fields
-- Should select only needed columns
SELECT *
FROM orders
WHERE user_id = 4821;


-- ANTI-PATTERN: function on indexed column prevents index usage (non-sargable)
-- Should use: WHERE created_at >= '2026-01-01' AND created_at < '2027-01-01'
SELECT id, email, full_name
FROM users
WHERE EXTRACT(YEAR FROM created_at) = 2026;


-- ANTI-PATTERN: N+1 query — this runs once per order in application code
-- A loop in the app calls this for every order returned by a parent query.
-- Should be a single JOIN query instead.
SELECT *
FROM order_items
WHERE order_id = ?;  -- called in a loop for each order


-- ANTI-PATTERN: correlated subquery is re-evaluated for every row
-- Should be rewritten as a JOIN with GROUP BY
SELECT
    p.id,
    p.name,
    p.price_cents,
    (SELECT AVG(r.rating) FROM reviews r WHERE r.product_id = p.id) AS avg_rating,
    (SELECT COUNT(*)       FROM reviews r WHERE r.product_id = p.id) AS review_count
FROM products p
WHERE p.is_published = TRUE
ORDER BY avg_rating DESC;


-- ANTI-PATTERN: implicit cartesian join (missing JOIN condition)
-- This produces a cross product of all users and all orders
SELECT u.full_name, o.id, o.total_cents
FROM users u, orders o
WHERE o.status = 'shipped';


-- ANTI-PATTERN: LIKE with leading wildcard prevents index usage
-- Also uses SELECT * unnecessarily
SELECT *
FROM products
WHERE name LIKE '%wireless%'
ORDER BY created_at DESC;


-- ANTI-PATTERN: querying unindexed column (reviews.product_id has no index)
-- and using ORDER BY on unindexed column
SELECT
    r.rating,
    r.title,
    r.body,
    u.full_name AS reviewer_name
FROM reviews r
JOIN users u ON u.id = r.user_id
WHERE r.product_id = 1042
ORDER BY r.created_at DESC;


-- ANTI-PATTERN: DISTINCT used to mask a bad join that produces duplicates
SELECT DISTINCT
    u.id,
    u.email,
    u.full_name
FROM users u
JOIN orders o ON o.user_id = u.id
JOIN order_items oi ON oi.order_id = o.id
JOIN products p ON p.id = oi.product_id
WHERE p.category = 'Electronics';


-- ANTI-PATTERN: OR conditions on different columns prevent index usage
-- Should be rewritten as UNION of two indexed queries
SELECT id, email, full_name, phone
FROM users
WHERE email LIKE '%@example.com'
   OR phone LIKE '+1-555%';


-- ANTI-PATTERN: counting with SELECT COUNT(*) in a subquery + no limit
-- Heavy query with no pagination
SELECT
    p.id,
    p.name,
    p.category,
    p.stock_quantity,
    p.price_cents,
    il.total_changes
FROM products p
LEFT JOIN (
    SELECT product_id, SUM(ABS(change_qty)) AS total_changes
    FROM inventory_log
    GROUP BY product_id
) il ON il.product_id = p.id
ORDER BY il.total_changes DESC;
-- MISSING: LIMIT clause — returns entire catalog
