# Quyền IAM và ranh giới thực tế

## Lambda: policy đã kiểm tra trên AWS

`lambda-s3-access.observed.json` là bản xuất nguyên nội dung inline policy `fcj-sales-s3-access` đã đọc từ AWS ngày 22/10/2026. Nó cho phép GetObject ở raw/* và PutObject ở processed/*, rejected/* của đúng bucket. Role còn có AWSLambdaBasicExecutionRole để ghi log. Lambda không nhận quyền Athena hoặc Glue; bổ sung category output vẫn nằm trong processed/*, nên không cần mở rộng role.

Lambda resource policy cho S3 InvokeFunction đã kiểm tra có cả SourceAccount `988079434036` và SourceArn của đúng bucket. Trigger chỉ nhận raw/ và .csv.

## Danh tính chạy phân tích

Các DDL/SELECT thực tế trong evidence chạy bằng assumed-role `AccountFullAccessRole` do AWS project hiện tại quản lý; đã có quyền thực hiện. Không tạo danh tính hay gắn thêm policy vào role này. Policy IAM quản lý team member thuộc AWS Settings trong trải nghiệm hiện tại.

Nếu cần danh tính phân tích riêng về sau, tách nó khỏi execution role của Lambda. Quyền phải bao gồm chạy/đọc query của workgroup `fcj-sales-workgroup`, đọc metadata của `fcj_sales_db` và các bảng/view cần dùng, đọc `processed/cleaned/*`, ghi/đọc `athena-results/*`, cùng quyền bucket-level cần cho Athena như liệt kê prefix và xác định Region. Chỉ cho quản trị triển khai quyền tạo metadata; người chỉ xem báo cáo không cần CreateWorkGroup, CREATE TABLE hoặc thay đổi Lambda.

## Sinh và rà soát candidate bằng công cụ AWS

```powershell
python scripts/generate_iam_baseline.py
```

Lệnh được tái hiện trong script:

```powershell
uvx iam-policy-autopilot@latest generate-policies D:\AWS\sales-data-pipeline\lambda_function.py --region ap-southeast-2 --account 988079434036 --service-hints s3 --pretty
uvx iam-policy-autopilot@latest generate-policies D:\AWS\sales-data-pipeline\scripts\analytics.py --region ap-southeast-2 --account 988079434036 --service-hints athena sts --pretty
```

**Các file generated-candidates chỉ dùng audit, chưa phải policy least-privilege để attach.** Chạy thử công cụ cho thấy candidate Lambda bao gồm KMS, Object Lambda, tagging/retention và các ARN wildcard không cần cho demo SSE-S3 này. Candidate analytics có quyền tạo workgroup/PassRole rộng và không tự mô tả hết data-plane S3/Glue do truy vấn SQL gọi gián tiếp. Vì thế không dùng chúng để mở quyền trên AWS. Policy Lambda đã có và đã kiểm thử được giữ nguyên; chính sách một analyst riêng cần một lượt thiết kế/xác minh riêng nếu người dùng muốn cấp quyền đó.

Tham khảo: [IAM Policy Autopilot](https://github.com/awslabs/iam-policy-autopilot), [Athena access to data](https://docs.aws.amazon.com/athena/latest/ug/security-iam-athena.html).
