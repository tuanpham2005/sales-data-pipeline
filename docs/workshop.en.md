# Small-file sales data pipeline on AWS — workshop draft

## Problem and acceptance criteria

Sales CSV files can contain invalid dates, missing values, invalid prices and duplicate order lines. This workshop ingests a CSV, validates and separates records, calculates revenue and exposes cleaned data to SQL. The dataset is **synthetic**. The golden sample must produce 6 valid line items, 4 rejected rows, 5 distinct orders, 17 units and VND 670000.00. This is not a business production dataset or a large-scale processing system.

## Prerequisites

Python 3.10+, Windows/PowerShell and an AWS project with the required S3/Lambda/Glue/Athena/CloudWatch permissions. The local browser-login profile is codex-aws; the selected Region is ap-southeast-2. Use Power BI Desktop for the local dashboard. Review deployment.md and iam/README.md. The project was observed on the FREE plan; service availability, credits and costs must be checked against its current status.

## Architecture to draw and explain yourself

S3 raw object events invoke Lambda. Lambda writes cleaned and rejected records, four revenue aggregations and a summary. Glue Data Catalog supplies metadata to Athena, which reads cleaned files directly from S3. Query outputs have a separate prefix. A verified CSV export is imported into Power BI with manual refresh. CloudWatch receives Lambda logs and metrics. Follow architecture-and-data.md and draw your own diagram with official AWS icons. There is no Glue ETL job/crawler or realtime dashboard in this implementation.

## Lab procedure

1. Run local tests and the golden sample; inspect the cleaned/rejected/summary and four aggregations.
2. Verify the existing Lambda runtime, handler, environment and execution role; inspect the scoped bucket notification and invoke policy. Do not recreate working resources.
3. Build the ZIP, preserve a backup and revision ID, then update the same function. Upload the sample using the same raw key.
4. Wait for the Processed log and inspect all seven output files and the summary.
5. Configure the dedicated Athena workgroup and athena-results/ output. Execute SQL 00/01/02. The external table reads only processed/cleaned/, with STRING columns and a typed CAST view.
6. Run the quality gate, then KPI, daily/product/category/city, top-product, reconciliation and duplicate queries. Stop export on invalid data or duplicate keys.
7. Export actual Athena results, import dashboard/Sales.pq, add measures.dax and build visuals/slicers following dashboard/README.md. Refresh is manual.
8. Upload the same raw key again; verify stable output keys and unchanged revenue. Review logs, metrics and alarm configuration.
9. Capture your own evidence/video and Pricing Calculator estimate. Follow cleanup.md when ending the lab.

## Observed results on 22 October 2026

All 30 local tests passed. The live S3/Lambda upload and repeat checks passed. Athena returned 6 line items, 5 orders, 17 units and VND 670000.00; daily amounts matched the reference and all dimension reconciliation differences were zero. Commas, quoted strings and Vietnamese Unicode were verified against an isolated validation table. Two alarms were configured without notification actions; an intentional cloud fault has not been injected to validate ALARM transitions. Query IDs and API status are recorded under docs/evidence/2026-10-22.

The Power BI deliverable currently consists of actual exported data, Power Query, DAX, a theme and reproducible instructions. A completed PBIX, dashboard screenshots, the student's own architecture diagram, demo recording and Calculator share link are still pending and must not be reported as completed.

## Cost and limitations

The documented small monthly scenario is estimated at USD 0.273488 before allowances, credits and tax, using Sydney price snapshots from the implementation date. It is not a bill. Processing is in memory and limited to 5 MiB inputs. Cross-file business deduplication, exactly-once execution and atomic multi-object commits are not implemented. Embedded field newlines are rejected for Athena CSV compatibility. Concurrent updates of the same source key can still race. Explain these limits and future improvements without adding services solely to increase the service count.

References: [OpenCSVSerde](https://docs.aws.amazon.com/athena/latest/ug/csv-serde.html), [S3/Lambda integration](https://docs.aws.amazon.com/lambda/latest/dg/with-s3.html), [Python deployment ZIPs](https://docs.aws.amazon.com/lambda/latest/dg/python-package.html).
