-- Sample queries for snowflake_query_helper.py (several deliberate problems)
SELECT *
FROM analytics.orders o
JOIN analytics.customers c ON 1 = 1
WHERE LOWER(c.email) LIKE '%@example.com';

SELECT order_date, SUM(amount) AS revenue
FROM analytics.orders
WHERE order_date >= DATEADD(day, -30, CURRENT_DATE())
GROUP BY order_date
ORDER BY order_date;
