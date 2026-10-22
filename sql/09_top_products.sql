SELECT product, SUM(total_amount) AS revenue,
 SUM(quantity) AS total_quantity, COUNT(*) AS valid_lines
FROM fcj_sales_db.sales_cleaned
GROUP BY product ORDER BY revenue DESC, product LIMIT 10;
