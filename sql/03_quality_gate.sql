SELECT COUNT(*) AS line_count,
 COUNT(DISTINCT "$path") AS source_files,
 COALESCE(SUM(CASE WHEN
   order_id IS NULL OR TRIM(order_id) = '' OR line_id IS NULL OR TRIM(line_id) = ''
   OR product IS NULL OR TRIM(product) = '' OR category IS NULL OR TRIM(category) = ''
   OR city IS NULL OR TRIM(city) = '' OR currency IS NULL OR currency <> 'VND'
   OR TRY_CAST(order_date AS DATE) IS NULL
   OR NOT REGEXP_LIKE(COALESCE(order_date, ''), '^[0-9]{4}-[0-9]{2}-[0-9]{2}$')
   OR TRY_CAST(quantity AS BIGINT) IS NULL OR TRY_CAST(quantity AS BIGINT) NOT BETWEEN 1 AND 1000000
   OR NOT REGEXP_LIKE(COALESCE(quantity, ''), '^[0-9]+$')
   OR TRY_CAST(unit_price AS DECIMAL(38,2)) IS NULL
   OR TRY_CAST(unit_price AS DECIMAL(38,2)) NOT BETWEEN 0 AND 1000000000000
   OR NOT REGEXP_LIKE(COALESCE(unit_price, ''), '^[0-9]+([.][0-9]{1,2})?$')
   OR TRY_CAST(total_amount AS DECIMAL(38,2)) IS NULL
   OR NOT REGEXP_LIKE(COALESCE(total_amount, ''), '^[0-9]+([.][0-9]{1,2})?$')
   OR TRY_CAST(total_amount AS DECIMAL(38,2)) <>
      TRY_CAST(quantity AS BIGINT) * TRY_CAST(unit_price AS DECIMAL(38,2))
 THEN 1 ELSE 0 END), 0) AS invalid_rows,
 COUNT(*) - COUNT(DISTINCT ROW(order_id, line_id)) AS duplicate_line_keys
FROM fcj_sales_db.sales_cleaned_raw;
