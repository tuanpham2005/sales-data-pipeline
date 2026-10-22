# Mốc Lambda: Kiro -> ZIP -> kiểm thử trên AWS

Gói này bổ sung adapter S3, không thay đổi quy tắc làm sạch trong src/pipeline.py.
Nếu đang có dự án local, chép lambda_function.py, build_lambda.py,
event_manual.json, README_LAMBDA.md và tests/test_lambda.py vào vị trí tương ứng.
Các file src/ và dữ liệu mẫu được kèm để gói tự chạy độc lập; không ghi đè code
cậu đã tự chỉnh mà chưa xem khác biệt.

## 1. Trong Kiro

Mở thư mục có run_local.py và lambda_function.py. Terminal PowerShell:

```powershell
python -m unittest discover -s tests -v
python build_lambda.py
```

30 kiểm thử phải đạt với phiên bản cập nhật ngày 22/10/2026. Test adapter dùng S3 giả lập,
không gọi AWS hoặc cần credentials. File deploy: dist/fcj-sales-lambda.zip.
ZIP phải chứa lambda_function.py ở gốc và src/ bên cạnh. Không upload ZIP bộ
khởi đầu hay ZIP gói hướng dẫn thay cho file deploy này.

## 2. Cấu hình hàm đã tạo

- Hàm fcj-sales-processor, Sydney ap-southeast-2, Python 3.13, x86_64.
- Role fcj-sales-lambda-role: GetObject ở raw/*, PutObject ở processed/* và
  rejected/* trong bucket tuan-fcj-sales-pipeline-20261006-a7k9, quyền log CloudWatch.
- Memory 256 MB, timeout 30 giây là cấu hình khởi đầu cho lab.
- Configuration > Environment variables > Edit: thêm SALES_BUCKET với giá trị
  tuan-fcj-sales-pipeline-20261006-a7k9. Không nhập s3:// hoặc dấu / vào giá trị.
- Code > Upload from > .zip file: chọn dist/fcj-sales-lambda.zip rồi Save.
- Runtime settings > Edit: handler lambda_function.lambda_handler.

Bản lab dùng boto3 có sẵn trong runtime Python Lambda; không cần cài SDK để
chạy build/test trên máy. Khi chuẩn bị bản triển khai ổn định, đóng gói và khóa
phiên bản boto3 cùng phụ thuộc theo khuyến nghị AWS.

## 3. Test thủ công trước khi thêm trigger

Tạo private test event tên sales-sample-manual; dùng event_manual.json:

```json
{
  "bucket": "tuan-fcj-sales-pipeline-20261006-a7k9",
  "key": "raw/sales_sample.csv"
}
```

Save rồi Test. Expected response results[0]: status processed, input_rows 10,
valid_rows 6, rejected_rows 4, total_quantity 17, total_revenue 670000.00, VND.
Status Succeeded riêng nó chưa chứng minh dữ liệu đúng: xem response và S3.

Output ID là SHA256 của tên key đầu vào, nên tên file là chuỗi dài:

- processed/cleaned/<id>.csv: 6 dòng hợp lệ
- rejected/<id>.csv: 4 dòng lỗi kèm lý do
- processed/summaries/<id>.json: thống kê và đường dẫn outputs
- processed/aggregates/date/<id>.csv
- processed/aggregates/product/<id>.csv
- processed/aggregates/category/<id>.csv
- processed/aggregates/city/<id>.csv

Chỉ trỏ bảng Athena dữ liệu sạch vào processed/cleaned/; không trỏ toàn bộ
processed/ vì chứa nhiều schema và cả JSON.

Test lại cùng file giữ nguyên số object đầu ra; không sinh thêm thư mục run.
Nếu thay nội dung tại cùng input key, kết quả cũ được thay thế. Demo không
gộp/loại trùng giao dịch giữa nhiều input key khác nhau.

## 4. Trigger tự động, sau khi test thủ công đúng

Add trigger > S3 > chọn bucket trên; event All object create events,
prefix raw/, suffix .csv. Xác nhận cảnh báo vòng lặp sau khi kiểm tra chính xác
prefix/suffix. Không chọn trigger cho toàn bộ bucket. Hàm ghi ở processed/ và
rejected/ nên những output này không khớp raw/.

Sau khi thêm trigger, upload lại sales_sample.csv tại cùng key trong raw/;
upload trước khi tạo trigger không được tự xử lý hồi tố. Chờ vài giây rồi
xem CloudWatch và output. Chụp cấu hình trigger, log và summary làm bằng chứng.

## Lỗi thường gặp

- SALES_BUCKET missing: kiểm tra Environment variables.
- Unable to import module: ZIP sai gốc hoặc thiếu src/.
- Handler not found: kiểm tra lambda_function.lambda_handler.
- NoSuchKey: kiểm tra key raw/sales_sample.csv và file đã upload.
- AccessDenied: kiểm tra IAM role, policy, bucket ARN và mã hóa SSE-S3;
  nếu dùng SSE-KMS cần thiết kế thêm quyền KMS.
- CSV header: dữ liệu phải theo 9 cột của bản local.
- Timeout: kiểm tra timeout, log và VPC; lab này không cần gắn Lambda vào VPC.

## Giới hạn cần trình bày đúng

Đây là demo file nhỏ <=5 MiB, không xử lý dữ liệu lớn bằng Spark/Glue ETL.
Kiểm thử local dùng client giả, chưa chứng minh quyền/trigger trên tài khoản thật.
Output key cố định giúp lần phát lại cùng nội dung không tạo thêm object.
Không phải cơ chế exactly-once đầy đủ: ghi nhiều object không có transaction;
cần thêm kiểm soát concurrency, thứ tự phiên bản, trạng thái và khôi phục
khi một source key bị cập nhật liên tục. IfMatch chỉ bỏ qua event cũ khi
object đã bị thay trước lúc đọc, không giải quyết mọi race condition.

Nguồn: AWS Lambda Python ZIP docs; Lambda with S3; S3 notification structure.


Bản cập nhật ghi **7 file output** cho mỗi source key (thêm category). Các kiểm tra AWS thực tế và hướng dẫn rollback/cập nhật ở [docs/testing.md](docs/testing.md) và [docs/deployment.md](docs/deployment.md).
