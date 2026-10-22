SELECT COUNT(*) AS valid_line_items,
 COUNT(DISTINCT order_id) AS distinct_orders,
 COALESCE(SUM(quantity), 0) AS total_quantity,
 COALESCE(SUM(total_amount), CAST(0 AS DECIMAL(38,2))) AS total_revenue
FROM fcj_sales_db.sales_cleaned;
