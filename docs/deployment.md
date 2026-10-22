# Triển khai và cập nhật

## Phạm vi và các giá trị cố định

- Selected Region: `ap-southeast-2`, kiểm tra tại AWS Settings → View all projects → Overview → Additional Info → Region.
- Profile local: `codex-aws`; project ID phải là `988079434036`.
- Bucket private: `tuan-fcj-sales-pipeline-20261006-a7k9`.
- Lambda: `fcj-sales-processor`, handler `lambda_function.lambda_handler`, Python 3.13, x86_64, 256 MB, timeout 30 giây.
- Role: `fcj-sales-lambda-role`; môi trường `SALES_BUCKET` là đúng tên bucket, không có `s3://`.
- Workgroup: `fcj-sales-workgroup`, output `s3://tuan-fcj-sales-pipeline-20261006-a7k9/athena-results/`, SSE-S3, ngưỡng scan 10 MiB/query.

Các tài nguyên trên đã có/đã được kiểm chứng. Không chạy lại lệnh tạo bucket, tạo Lambda hoặc gán policy mới nếu chỉ cập nhật code.

## 1. Local

```powershell
Set-Location D:\AWS\sales-data-pipeline
python -m unittest discover -s tests -v
python run_local.py
python build_lambda.py
```

Logic nghiệp vụ và test dùng thư viện chuẩn. Bản mới có 30 test. Local output tạo run folder mới nên không dùng các thư mục local output khác lần chạy để cộng chung doanh thu. Bộ mẫu gốc không đổi.

## 2. Xác minh và cập nhật Lambda hiện có

Các lệnh sau để người dùng tái hiện bằng PowerShell. Khi Codex đang có AWS MCP, Codex thực hiện qua MCP thay vì chạy AWS CLI bằng shell.

```powershell
aws sts get-caller-identity --profile codex-aws --region ap-southeast-2
aws lambda get-function-configuration --function-name fcj-sales-processor --profile codex-aws --region ap-southeast-2
aws s3api get-bucket-notification-configuration --bucket tuan-fcj-sales-pipeline-20261006-a7k9 --profile codex-aws --region ap-southeast-2
```

Kiểm tra đúng project, code hiện tại và lưu backup ZIP trước khi cập nhật. Không thay cấu hình role/env bằng một lệnh update ghi đè toàn bộ ngoài ý muốn.

```powershell
$revision = aws lambda get-function-configuration --function-name fcj-sales-processor --query RevisionId --output text --profile codex-aws --region ap-southeast-2
aws lambda update-function-code --function-name fcj-sales-processor --zip-file fileb://dist/fcj-sales-lambda.zip --revision-id $revision --profile codex-aws --region ap-southeast-2
aws lambda wait function-updated-v2 --function-name fcj-sales-processor --profile codex-aws --region ap-southeast-2
```

`RevisionId` giúp dừng nếu có người khác cập nhật hàm sau lần đọc cấu hình. Thư mục ZIP phải có handler ở gốc. Lab tiếp tục dùng boto3 do runtime cung cấp; `requirements-cloud.txt` chỉ phục vụ helper trên máy, không được xem là SDK đã được vendor trong Lambda ZIP. Production cần khóa/đóng gói toàn bộ dependency theo khuyến nghị AWS.

## 3. Trigger và kiểm thử S3

Trong S3 → bucket → Properties → Event notifications: `s3:ObjectCreated:*`, prefix **raw/**, suffix **.csv**, destination là đúng Lambda. Lambda resource policy phải giới hạn SourceAccount và SourceArn của bucket. Configuration đã được kiểm tra, không tạo thêm notification trùng.

```powershell
aws s3 cp data/raw/sales_sample.csv s3://tuan-fcj-sales-pipeline-20261006-a7k9/raw/sales_sample.csv --profile codex-aws --region ap-southeast-2
aws logs tail /aws/lambda/fcj-sales-processor --since 10m --profile codex-aws --region ap-southeast-2
```

Chờ log Processed và kiểm tra summary/S3. Upload trước khi tạo trigger không tự xử lý hồi tố. Không upload bộ mẫu dưới nhiều tên raw khác nhau trong vùng dữ liệu nghiệm thu: các tên khác nhau tạo các bộ output khác nhau và có thể nhân đôi giao dịch.

## 4. Glue Data Catalog và Athena

```powershell
python -m pip install -r requirements-cloud.txt
python scripts/analytics.py setup --profile codex-aws
python scripts/analytics.py validate --profile codex-aws --expect-sample
python scripts/analytics.py export --profile codex-aws --expect-sample
```

Helper dùng session có profile rõ ràng, xác minh project trước khi chạy. requirements-cloud.txt bật boto3[crt] vì profile aws login cần AWS Common Runtime; không thay bằng gói boto3 thiếu CRT. `setup` tạo workgroup nếu chưa có, rồi thực thi 00_database, 01_cleaned_table, 02_typed_view. Các file CREATE DATABASE/TABLE có IF NOT EXISTS; view được replace có chủ đích trong phạm vi dự án. Nếu bảng đã có nhưng schema/location sai, không xóa để tạo lại: đọc GetTable/DESCRIBE và sửa có căn cứ trước khi chạy tiếp.

Console thay thế: chọn Sydney → Athena → workgroup fcj-sales-workgroup → chạy lần lượt SQL 00, 01, 02; tiếp theo 03_quality_gate và 13_profile. Bảng raw chỉ trỏ **processed/cleaned/**; không trỏ toàn bộ processed/. OpenCSVSerde với header skip=1 hỗ trợ trường quote/comma. Cột raw là STRING; view dùng CAST rõ sang DATE, BIGINT, DECIMAL(38,2). Quality gate có TRY_CAST để đếm lỗi, không dùng TRY_CAST âm thầm trong view kinh doanh. Dừng nếu invalid_rows/duplicate_line_keys khác 0.

Chạy SQL 04–12 để phân tích. `--expect-sample` chỉ hợp lệ khi nguồn cleaned chỉ có bộ mẫu. Fixture CSV đặc biệt được tách ở `validation/serde-special/`, table `sales_csv_validation`; nó không thuộc sales_cleaned và không làm thay đổi KPI mẫu. SQL 15/16 phục vụ tái hiện kiểm thử SerDe, không nằm trong setup chính.

Không có Glue ETL job, crawler, database server, capacity reservation hay dịch vụ dashboard cloud mới.

## 5. Rollback

Backup code trước cập nhật ở `docs/evidence/2026-10-22/lambda-before.zip`. Có thể dùng chính quy trình update-function-code với file backup và RevisionId mới. Việc rollback code không rollback nội dung S3; kiểm tra raw/summary/output rồi upload lại raw nếu cần. Không xóa sạch bucket để rollback.

Nguồn: [Lambda ZIP Python](https://docs.aws.amazon.com/lambda/latest/dg/python-package.html), [S3 trigger](https://docs.aws.amazon.com/lambda/latest/dg/with-s3.html), [OpenCSVSerde](https://docs.aws.amazon.com/athena/latest/ug/csv-serde.html).
