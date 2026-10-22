SELECT category, COUNT(*) AS valid_lines, COUNT(DISTINCT order_id) AS distinct_orders,
 SUM(quantity) AS total_quantity, SUM(total_amount) AS revenue
FROM fcj_sales_db.sales_cleaned
GROUP BY category ORDER BY category;
