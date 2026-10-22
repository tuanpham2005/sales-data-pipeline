SELECT order_id, line_id, order_date, product, category, quantity,
 unit_price, city, currency, total_amount, source_path
FROM fcj_sales_db.sales_cleaned
ORDER BY order_date, order_id, line_id;
