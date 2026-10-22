CREATE OR REPLACE VIEW fcj_sales_db.sales_cleaned AS
SELECT order_id, line_id, CAST(order_date AS DATE) AS order_date,
       product, category, CAST(quantity AS BIGINT) AS quantity,
       CAST(unit_price AS DECIMAL(38,2)) AS unit_price, city, currency,
       CAST(total_amount AS DECIMAL(38,2)) AS total_amount,
       "$path" AS source_path
FROM fcj_sales_db.sales_cleaned_raw;
