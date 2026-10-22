CREATE EXTERNAL TABLE IF NOT EXISTS fcj_sales_db.sales_cleaned_raw (
  order_id STRING, line_id STRING, order_date STRING, product STRING,
  category STRING, quantity STRING, unit_price STRING, city STRING,
  currency STRING, total_amount STRING
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES ('separatorChar' = ',', 'quoteChar' = '"', 'escapeChar' = '\\')
STORED AS TEXTFILE
LOCATION 's3://tuan-fcj-sales-pipeline-20261006-a7k9/processed/cleaned/'
TBLPROPERTIES ('skip.header.line.count' = '1', 'classification' = 'csv');
