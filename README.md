# Xây dựng pipeline xử lý và phân tích dữ liệu bán hàng trên AWS

## Mốc 1: chạy trên máy bằng Kiro

Phần này hướng dẫn mốc local. Hiện trạng AWS đã được kiểm chứng/cập nhật ngày 22/10/2026; xem [docs/STATUS.md](docs/STATUS.md) và [chỉ mục tài liệu](docs/README.md).
Python 3.10 trở lên; chỉ sử dụng thư viện chuẩn, không cần pip install.

1. Giải nén vào `D:\AWS\sales-data-pipeline`.
2. Kiro: File > Open Folder > chọn thư mục có `run_local.py`.
3. Terminal > New Terminal; chạy `python --version`.
4. Chạy `python run_local.py`.
5. Chạy `python -m unittest discover -s tests -v`.
6. Mở thư mục `data/output/<run_id>/` để xem kết quả.

Nếu Windows không nhận `python` nhưng nhận `py`, thay `python` bằng `py`.
Nếu báo không tìm thấy file, kiểm tra thư mục hiện tại bằng `Get-Location` và `Get-ChildItem`.

## Dữ liệu và quy tắc

`sales_sample.csv` là dữ liệu giả lập do bộ khởi đầu tạo cho kiểm thử, không phải số liệu kinh doanh thật.
Mỗi dòng là một dòng hàng trong đơn. Một đơn có thể có nhiều dòng hàng.
Khóa duy nhất là cặp `(order_id, line_id)`, không chỉ `order_id`.

| Cột | Ý nghĩa |
|---|---|
| order_id | Mã đơn hàng |
| line_id | Mã dòng hàng trong đơn |
| order_date | Ngày YYYY-MM-DD hợp lệ |
| product | Tên sản phẩm |
| category | Nhóm sản phẩm |
| quantity | Số lượng nguyên dương, tối đa 1.000.000 trong demo |
| unit_price | Đơn giá không âm, tối đa 1.000.000.000.000 và tối đa 2 chữ số thập phân |
| city | Thành phố |
| currency | Chỉ nhận VND trong bản đầu |

Tất cả các cột bắt buộc, có thể đổi thứ tự nhưng không thêm/bớt hoặc trùng tên cột.
Bỏ khoảng trắng ở đầu/cuối giá trị. Dòng trống hoàn toàn bị bỏ qua.
Ngày, giá, số lượng sai hoặc khóa trùng được chuyển sang rejected.csv kèm lý do.
Khóa trùng chỉ kiểm tra trong một file; cần bổ sung kiểm soát liên file khi triển khai cloud.
Với khóa trùng, giữ dòng hợp lệ đầu tiên; các dòng sau bị loại, kể cả giá trị khác nhau.
Không xử lý hoàn hàng, chiết khấu, thuế hoặc quy đổi tiền tệ trong bản này.
`total_amount = quantity * unit_price` là doanh thu gộp theo dòng hàng.
Tiền dùng Decimal, không dùng float. Lỗi header, encoding hoặc CSV không đọc được làm cả file thất bại.
Giới hạn input demo là 5 MiB, xử lý trong bộ nhớ; chưa phù hợp dữ liệu lớn.

## Kết quả chuẩn của bộ mẫu

- 10 dòng đầu vào (không tính header); 6 dòng hợp lệ; 4 dòng loại.
- 5 đơn hàng hợp lệ; 17 sản phẩm tính theo tổng quantity.
- Doanh thu: 670.000 VND.
- Ngày 01/09/2026: 150.000; 02/09: 340.000; 03/09: 180.000 VND.
- Các lỗi: số lượng âm, đơn giá chữ, ngày không tồn tại, trùng mã đơn+dòng.

Mỗi lần chạy tạo thư mục kết quả mới theo giờ UTC, không ghi đè kết quả trước.
`cleaned.csv`: dòng hợp lệ; `rejected.csv`: dòng gốc và lý do loại.
`summary.json`: chỉ số chất lượng và doanh thu.
`revenue_by_date.csv`, `revenue_by_product.csv`, `revenue_by_category.csv`, `revenue_by_city.csv`: tổng hợp.
Không cộng dữ liệu của nhiều lần chạy cùng file: sẽ bị đếm trùng.

## Tự kiểm tra thay đổi

Sao chép file mẫu thành `data/raw/sales_changed.csv`, sửa quantity của dòng ORD001/1 đầu tiên từ 2 thành 3.
Chạy `python run_local.py --input data/raw/sales_changed.csv`.
Doanh thu phải tăng thành 720.000 VND; tổng quantity thành 18; vẫn 6 valid và 4 rejected.

## Các mốc tiếp theo

1. S3 private lưu raw, processed, rejected; dùng raw prefix riêng cho trigger.
2. Lambda adapter gọi lại hàm `process_csv`, bổ sung giới hạn kích thước và log.
3. Kiểm soát xử lý lặp khi S3 phát lại sự kiện và tránh đếm trùng giữa các file.
4. Glue Data Catalog + Athena truy vấn dữ liệu trên S3.
5. Dashboard, CloudWatch, dự toán chi phí, kiểm thử và clean-up.

Lưu bằng chứng thực hiện thật để viết Worklog. Tự vẽ và giải thích kiến trúc khi làm báo cáo.
Không hard-code AWS access key. Chưa cần AWS CLI, boto3 hoặc credentials cho mốc local.

## Tham khảo

- https://docs.python.org/3/library/csv.html
- https://docs.python.org/3/library/decimal.html
- https://docs.aws.amazon.com/lambda/latest/dg/with-s3.html
- https://docs.aws.amazon.com/athena/latest/ug/data-sources-glue.html


## Phần phân tích đã bổ sung

SQL trong `sql/`; helper trong `scripts/`; gói Power BI ở `dashboard/`. Hướng dẫn triển khai và cập nhật tại [docs/deployment.md](docs/deployment.md); bằng chứng local/AWS và giới hạn tại [docs/testing.md](docs/testing.md). Chạy `python scripts/analytics.py export --profile codex-aws --expect-sample` để xuất lại sau khi cài requirements-cloud.txt.
