WITH totals AS (
 SELECT COALESCE(SUM(total_amount), CAST(0 AS DECIMAL(38,2))) AS revenue FROM fcj_sales_db.sales_cleaned
), grouped AS (
 SELECT 'date' AS dimension, SUM(revenue) AS revenue FROM (SELECT order_date, SUM(total_amount) revenue FROM fcj_sales_db.sales_cleaned GROUP BY order_date)
 UNION ALL SELECT 'product', SUM(revenue) FROM (SELECT product, SUM(total_amount) revenue FROM fcj_sales_db.sales_cleaned GROUP BY product)
 UNION ALL SELECT 'category', SUM(revenue) FROM (SELECT category, SUM(total_amount) revenue FROM fcj_sales_db.sales_cleaned GROUP BY category)
 UNION ALL SELECT 'city', SUM(revenue) FROM (SELECT city, SUM(total_amount) revenue FROM fcj_sales_db.sales_cleaned GROUP BY city)
)
SELECT dimension, grouped.revenue, grouped.revenue - totals.revenue AS difference
FROM grouped CROSS JOIN totals ORDER BY dimension;
