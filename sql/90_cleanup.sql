-- Manual end-of-lab cleanup only. Save evidence first; run one statement at a time.
-- These statements remove metadata, NOT S3 data. No CASCADE is intentional.
DROP VIEW IF EXISTS fcj_sales_db.sales_cleaned;
DROP TABLE IF EXISTS fcj_sales_db.sales_cleaned_raw;
DROP TABLE IF EXISTS fcj_sales_db.sales_csv_validation;
DROP DATABASE IF EXISTS fcj_sales_db;
