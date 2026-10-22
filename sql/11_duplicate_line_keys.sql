SELECT order_id, line_id, COUNT(*) AS occurrences,
 ARRAY_AGG(DISTINCT source_path) AS source_files
FROM fcj_sales_db.sales_cleaned
GROUP BY order_id, line_id HAVING COUNT(*) > 1
ORDER BY order_id, line_id;
