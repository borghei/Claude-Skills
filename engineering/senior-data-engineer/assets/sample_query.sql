SELECT *
FROM orders o, customers c
WHERE o.customer_id = c.id
  AND LOWER(c.email) LIKE '%@example.com'
ORDER BY o.created_at DESC;
