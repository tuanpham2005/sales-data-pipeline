SELECT order_id, product, city, CAST(quantity AS BIGINT) AS quantity, CAST(total_amount AS DECIMAL(38,2)) AS total_amount FROM fcj_sales_db.sales_csv_validation ORDER BY order_id;
