# Trạng thái bàn giao — 22/10/2026

Người thực hiện thao tác trong lượt triển khai: **Codex**, theo dàn ý A–F của người dùng. Kiro đã hoàn tất kiểm tra sẵn sàng trước đó; không ghi nhận Kiro sửa code trong lượt triển khai này. Mức hướng dẫn HIGH. Người dùng đã chọn **giữ tài nguyên để tiếp tục demo**.

## Kết quả nghiệm thu đã đo

| Chỉ số | Kỳ vọng | Thực tế AWS |
| --- | ---: | ---: |
| Dòng sạch | 6 | 6 |
| Dòng bị loại | 4 | 4 |
| Đơn hàng phân biệt | 5 | 5 |
| Tổng quantity | 17 | 17 |
| Doanh thu VND | 670000.00 | 670000.00 |
| Ngày 01/09/2026 | 150000.00 | 150000.00 |
| Ngày 02/09/2026 | 340000.00 | 340000.00 |
| Ngày 03/09/2026 | 180000.00 | 180000.00 |
| SQL lỗi kiểu/giá trị | 0 | 0 |
| Khóa dòng hàng trùng | 0 | 0 |

Hai lần upload cùng raw/sales_sample.csv kích hoạt Lambda thành công. Có đúng **7 data output files**; key và ETag giống nhau giữa hai lần. Athena sau chạy lặp vẫn trả 670000.00. Tổng theo date/product/category/city đều khớp và không có duplicate keys. File CSV dành cho Power BI đã được so với S3 cleaned: khớp từng dòng/cột. Dữ liệu giả lập được giữ nguyên làm golden sample.

## Bảng trạng thái A–F

| Giai đoạn | Đã hoàn thành | Còn thiếu / bị chặn |
| --- | --- | --- |
| A — Rà soát | Đọc source/tests; đối chiếu deployed ZIP; cấu hình Lambda/role/env/handler/trigger và dữ liệu S3 thực tế | Không có lỗi quyền chặn phần này |
| B — Catalog/Athena | fcj_sales_db, sales_cleaned_raw, sales_cleaned, workgroup/output/SSE-S3/10 MiB scan cap; kiểm tra SerDe/schema bằng GetTable | Không có ETL job hoặc crawler; không cần cho phạm vi này |
| C — SQL phân tích | KPI, date/product/category/city, top products, reconciliation, duplicate detection; chạy và lưu query IDs/results | Không có phần SQL đang bị chặn |
| D — Dashboard | CSV thật từ Athena, Power Query, DAX, theme, hướng dẫn 3 KPI/4 chart/3 slicer và refresh/đối chiếu | **PBIX và kiểm thử visual trong Power BI Desktop chưa thực hiện**; người dùng làm theo dashboard/README.md |
| E — Kiểm thử/vận hành | 30/30 test local; live upload/repeat; CSV comma/quote/Unicode qua Athena; log/metric và 2 alarm | Chưa fault-inject cloud, test concurrent updates hoặc kiểm tra email (không có action); không có exactly-once/global dedup |
| F — Tài liệu | Local/deployment/data dictionary/IAM/operations/cost/cleanup, danh sách ảnh, workshop VI/EN, worklog thực tế | Sơ đồ do sinh viên tự vẽ, ảnh/video demo và share link/PDF Pricing Calculator chưa có; website Hugo không được viết đè |

Chưa có blocker về quyền/kết nối AWS trong các thao tác đã thực hiện. Các bước Desktop/nội dung cá nhân còn lại là việc chưa làm, không được tính là đã hoàn tất.

## Tài nguyên AWS đang giữ

- Giữ bucket private `tuan-fcj-sales-pipeline-20261006-a7k9`, Lambda `fcj-sales-processor`, role `fcj-sales-lambda-role`; không tạo lại hoặc xóa chúng.
- Cập nhật code của chính Lambda cũ: SHA256 `CmiZEuJSnUmScQJqHvGRhIqA0o8VP2JPLEnbqOdWCtc=`, Python 3.13, 256 MB, timeout 30s, handler và SALES_BUCKET giữ đúng cấu hình đã xác minh.
- Thêm category aggregate và các kiểm tra CSV; không mở rộng quyền IAM của Lambda.
- Mới: Glue database `fcj_sales_db`; external table `sales_cleaned_raw`; view `sales_cleaned`; table fixture `sales_csv_validation`.
- Mới: Athena workgroup `fcj-sales-workgroup`; giữ primary nguyên cấu hình. Kết quả ở athena-results/.
- Mới: alarms `fcj-sales-lambda-errors` và `fcj-sales-lambda-duration-high`. Cả hai đã đọc lại là **OK**, không có notification actions.
- Artifact ZIP ở `artifacts/lambda/fcj-sales-processor-20261022.zip`; fixture ở `validation/serde-special/`. Không thuộc cleaned table nên không làm nhiễu tổng mẫu.
- Không tạo Glue ETL/crawler, SNS, QuickSight, capacity reservation hoặc nâng plan. Project được quan sát là FREE/ACTIVE. Tất cả tài nguyên regional của lab ở Sydney.

## Evidence và giới hạn

- `evidence/2026-10-22/initial-aws-*.json`: baseline cấu hình/policy/source trước thay đổi.
- `lambda-before.zip`: backup code cũ; `lambda_update.json`: kết quả cập nhật và hash.
- `s3_repeat_first.json`, `s3_repeat_second.json`, `data-acceptance.json`: so sánh output và golden dataset.
- `athena_ddl.json`, `athena_initial_selects.json`, `athena_analyses.json`, `after_repeat_and_csv_validation.json`: API status, query IDs, scanned bytes và row values.
- `aws_final_verification.json`: cấu hình cuối; CloudWatch ghi 2 invocations, 0 errors; maximum duration 3471.92 ms và hai Processed log events.
- `local-tests.txt`, `security-scan.json`: 30 test đạt; không phát hiện access-key IDs hoặc literal secret/token theo pattern scan trong deliverable text. Đây không phải security audit đầy đủ.
- `pricing*.json`, `cost-estimate.csv`: giá Sydney đã tra và mô hình **0.273488 USD/tháng** với giả định ở costs.md; không phải hóa đơn.

IAM candidate do Autopilot sinh **không được apply** vì rộng hơn phạm vi lab và cần review. Bản inline S3 policy quan sát thực tế được xuất trong iam/. Danh tính query hiện có quyền quản lý của project; chưa tạo một analyst identity riêng để triển khai quyền hẹp hơn.

## Bước tiếp theo

1. Dùng dashboard/README.md, Sales.pq và measures.dax để tạo PBIX; kiểm tra KPI và slicer rồi lưu/chụp màn hình.
2. Tự vẽ/giải thích kiến trúc theo architecture-and-data.md; quay demo theo screenshots.md.
3. Lưu estimate trong AWS Pricing Calculator theo costs.md; cập nhật bài báo cáo Hugo từ các bản nháp workshop VI/EN sau khi người dùng đã hiểu và thực hiện.
4. Chỉ cleanup khi người dùng quyết định kết thúc lab; hiện đã chọn giữ để demo.
