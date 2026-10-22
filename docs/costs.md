# Dự toán chi phí và theo dõi

Đã đọc AWS Price List API ngày **22/10/2026**, lọc Sydney ap-southeast-2. JSON giá/SKU nằm trong pricing.json, pricing_extra.json, pricing_final.json. Đây là giá public on-demand; không phải hóa đơn hay cam kết miễn phí.

`python scripts/estimate_costs.py` tính bằng Decimal và xuất cost-estimate.csv. Kịch bản một tháng: 100 raw files; Lambda trung bình 1 giây/lần, 256 MiB; tổng S3 lưu trung bình 0.25 GB-month; 1000 PUT/LIST, 10200 GET; 100 query, mỗi query scan 100 MiB; 2 standard alarms; 0.01 GB log ingest và 0.01 GB-month log storage; 10 catalog objects và 2000 metadata requests. Đây là giả định tải để làm dự toán, **không phải lượng sử dụng thực tế đã đo**.

| Hạng mục | Đơn giá public đã tra |
| --- | --- |
| Athena SQL scan | 5 USD/TB; tối thiểu 10 MB/query |
| S3 Standard, tier đầu | 0.025 USD/GB-month |
| S3 PUT/COPY/POST/LIST | 0.0055 USD/1000 requests |
| S3 GET | 0.0044 USD/10000 requests |
| Lambda x86 duration tier đầu | 0.0000166667 USD/GB-second |
| Lambda request | 0.20 USD/1 triệu requests |
| CloudWatch standard alarm | 0.10 USD/alarm-metric-month |
| Log ingest / storage | 0.67 USD/GB; 0.033 USD/GB-month |
| Glue metadata / request | 1 USD/100000 object-month; 1 USD/1 triệu requests |

Tổng mô hình thận trọng do script tính: **0.273488 USD/tháng**, trước free allowances/credit/thuế. Không bao gồm data transfer out, license Power BI, query phát sinh hoặc monitoring API ngoài mô hình. S3 query outputs/metadata có thể tạo thêm request so với mô hình; kiểm tra hóa đơn thay vì coi số lẻ này là số tiền phải trả. Hai alarm là khoản định kỳ đáng chú ý với lab cực nhỏ.

AWS project hiện được API xác nhận là FREE/ACTIVE với credit còn lại tại thời điểm kiểm tra; không đồng nghĩa mọi dịch vụ/usage miễn phí. Không tự nâng plan hoặc đặt spend limit. Người dùng xem AWS Settings → Billing để kiểm tra plan, credit, spend status; cấu hình budget/notification khi đã quyết định ngưỡng và địa chỉ nhận. Lượt này không tạo budget/email subscription.

## Hoàn thiện bằng AWS Pricing Calculator cho báo cáo

Mở [AWS Pricing Calculator](https://calculator.aws/), tạo estimate Sydney cho S3/Lambda/Athena/CloudWatch/Glue Data Catalog, nhập các giả định trên, ghi rõ 0 Glue ETL jobs/crawlers và dashboard Power BI local. Kiểm tra số liệu, lưu share link hoặc export PDF/CSV vào báo cáo. **Chưa có estimate share link/PDF do Calculator tạo trong lượt này**; CSV hiện tại là mô hình tái hiện từ Price List API. Nếu giao diện không có mục Data Catalog riêng, mô tả khoản này trong ghi chú thay vì thêm ETL job để lấp chỗ.

Tối ưu: chỉ query cleaned, không scan processed tổng; không bật provisioned capacity/crawler/ETL; giới hạn scan mỗi query, dừng query sai, giữ dataset nhỏ, kiểm soát số lượt refresh; dọn artifacts/query results sau khi lưu evidence. Dùng Parquet/partition chỉ khi có nhu cầu đo được, không tăng phức tạp cho bộ mẫu 6 dòng.

Nguồn: [Athena pricing](https://aws.amazon.com/athena/pricing/), [S3 pricing](https://aws.amazon.com/s3/pricing/), [Lambda pricing](https://aws.amazon.com/lambda/pricing/), [CloudWatch pricing](https://aws.amazon.com/cloudwatch/pricing/), [Glue pricing](https://aws.amazon.com/glue/pricing/), cùng JSON giá vùng Sydney.
