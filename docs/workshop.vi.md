# Pipeline dữ liệu bán hàng nhỏ trên AWS — bản nháp workshop

## Bài toán và mục tiêu

CSV bán hàng có thể sai ngày, thiếu dữ liệu, sai giá và trùng dòng hàng. Workshop xây pipeline nhận CSV, làm sạch, tách lỗi, tính doanh thu và cho truy vấn SQL. Dataset là giả lập. Mục tiêu nghiệm thu: 6 dòng sạch, 4 dòng lỗi, 5 đơn, quantity 17 và doanh thu 670000.00 VND. Không mô tả đây là dữ liệu doanh nghiệp hoặc hệ thống dữ liệu lớn.

## Điều kiện tiên quyết

Python 3.10+, Windows/PowerShell, AWS project có quyền trên S3/Lambda/Glue/Athena/CloudWatch; phiên login profile codex-aws. Selected Region ap-southeast-2. Power BI Desktop phục vụ dựng dashboard ở máy. Đọc deployment.md và iam/README.md trước khi thao tác. Project được kiểm tra là FREE plan; kiểm tra khả năng sử dụng dịch vụ và chi phí theo trạng thái thật của mình.

## Kiến trúc cần tự vẽ và giải thích

S3 raw phát event tới Lambda; Lambda ghi cleaned/rejected/aggregates/summary. Glue Data Catalog cung cấp metadata cho Athena đọc cleaned trên S3. Query results nằm ở prefix riêng; CSV export sang Power BI. CloudWatch theo dõi Lambda. Theo architecture-and-data.md để tự vẽ bằng AWS icons chính thức. Glue không chạy ETL trong thiết kế này; dashboard không realtime.

## Các bước thực hành

1. Chạy local tests và sample; xem cleaned, rejected, summary, bốn aggregate.
2. Đối chiếu Lambda handler/env/runtime/role, bucket notification và source constraints; không tạo lại tài nguyên đã có.
3. Build ZIP, lưu backup/revision, cập nhật code đúng hàm. Upload sample cùng raw key.
4. Đợi log Processed, kiểm tra S3 có 7 output files và summary đúng bộ mẫu.
5. Tạo workgroup với output athena-results/; chạy SQL 00/01/02. Table chỉ trỏ processed/cleaned/; raw columns STRING, view CAST đúng kiểu.
6. Chạy quality gate rồi SQL KPI/date/product/category/city/top/reconciliation/duplicates. Không export nếu chất lượng không đạt.
7. Export CSV thật, dùng dashboard/Sales.pq và measures.dax để dựng Power BI theo dashboard/README.md; Refresh thủ công rồi kiểm tra slicer.
8. Upload lại cùng raw key, đối chiếu file keys và KPI không tăng; xem log/metric/alarm.
9. Lưu ảnh/video và Pricing Calculator estimate của chính mình. Khi kết thúc lab, làm cleanup.md.

## Kết quả đã quan sát 22/10/2026

30 test local đạt; AWS S3/Lambda upload + repeat thành công; Athena KPI 6/5/17/670000.00, daily totals đúng và reconciliation difference=0. CSV comma/quote/Unicode được xác minh trong bảng validation riêng. Hai alarm đã được cấu hình nhưng chưa fault-inject để kiểm tra chuyển ALARM; không có email action. Query IDs và API status nằm trong docs/evidence/2026-10-22.

Power BI hiện là gói hướng dẫn, dữ liệu thật xuất từ Athena, Power Query và DAX; chưa có PBIX/ảnh dashboard hoàn tất. Sơ đồ tự vẽ, video demo và Calculator share link là phần người dùng cần hoàn thiện, không được ghi là đã làm.

## Chi phí và giới hạn

Mô hình giả định nhỏ, giá Sydney tra ngày triển khai: 0.273488 USD/tháng trước allowances/credit/thuế, xem costs.md và cost-estimate.csv. Không phải hóa đơn. File <=5 MiB, xử lý trong bộ nhớ; không cross-file dedup hoặc exactly-once/transaction đa object. Newline trong field không được hỗ trợ do định dạng CSV cho Athena. Cập nhật cùng key đồng thời vẫn có race. Nêu giới hạn này khi demo và trình bày hướng phát triển, không thêm dịch vụ mới chỉ để tăng số dịch vụ.

Tham khảo: [OpenCSVSerde](https://docs.aws.amazon.com/athena/latest/ug/csv-serde.html), [S3/Lambda](https://docs.aws.amazon.com/lambda/latest/dg/with-s3.html), [Lambda Python ZIP](https://docs.aws.amazon.com/lambda/latest/dg/python-package.html).
