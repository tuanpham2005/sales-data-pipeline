# Theo dõi và xử lý lỗi

## Log / metric / alarm

Log group: `/aws/lambda/fcj-sales-processor`. Tìm `Processed source=raw/sales_sample.csv valid=6 rejected=4 revenue=670000.00 VND`, RequestId và REPORT tương ứng. Log timestamp UTC; đổi sang Việt Nam +7 giờ khi ghi worklog.

CloudWatch → Metrics → Lambda → By Function Name: Invocations, Errors, Duration, Throttles. Athena workgroup bật PublishCloudWatchMetricsEnabled và chặn query vượt 10 MiB scan; đây là guardrail mỗi query, không phải ngân sách tháng. Với dữ liệu lớn hơn, nâng giới hạn có chủ đích sau dự toán.

Đã tạo hai standard metric alarms, period 300 giây, evaluation 1/1, missing=notBreaching:

- `fcj-sales-lambda-errors`: Sum Errors >= 1.
- `fcj-sales-lambda-duration-high`: Maximum Duration >= 27000 ms, gần timeout 30 giây.

Alarm hiện chỉ xem trong Console, **ActionsEnabled=false, không gửi email/SMS**. Không có kênh liên lạc được tự thêm. Chưa thử phát sinh lỗi cloud để kiểm tra ALARM. Trạng thái và evidence lúc tạo ở cloudwatch_alarms.json; trạng thái ban đầu INSUFFICIENT_DATA là bình thường.

## Lỗi thường gặp

| Triệu chứng | Kiểm tra / xử lý |
| --- | --- |
| Không có log invocation sau upload | Đúng bucket/Region, key raw/*.csv, notification và Lambda resource policy SourceArn/SourceAccount; không add trigger thứ hai để thử |
| AccessDenied | Role Lambda và đúng bucket prefix; nếu quyền trước đây hoạt động bỗng lỗi, kiểm tra spend limit ở AWS Settings → Billing và trạng thái project trước khi mở rộng policy |
| SALES_BUCKET/handler lỗi | Đối chiếu env/handler đã ghi trong deployment.md; không nhập s3:// vào env |
| HIVE_BAD_DATA / lỗi CAST | Chạy raw quality gate, xem source_path và dữ liệu thật; không đặt user.null.for.invalid.data=true để che lỗi |
| Athena output location/permission | Đúng workgroup, output athena-results/, quyền của caller trên Glue/S3; không thêm quyền Athena vào role Lambda |
| Doanh thu nhân đôi | Xem 11_duplicate_line_keys.sql, số source files; cùng nội dung ở hai raw keys không được dedup tự động |
| Input vượt 5 MiB / encoding/header lỗi | Sửa input hoặc dùng kiến trúc khác khi có yêu cầu; lỗi fatal không được coi là xử lý thành công |
| Dashboard không đổi | Chạy export lại từ Athena rồi Refresh PBIX; Refresh PBIX không tự chạy Athena |

Khi input key bị cập nhật nhưng phiên bản mới có lỗi fatal, output cũ của lần thành công trước có thể còn nguyên. Không diễn giải output đó như kết quả của input mới. Kiểm tra raw ETag, summary source_etag và log; sửa input rồi chạy lại. Summary ghi cuối giúp quan sát nhưng không phải transaction hoặc commit marker được Athena tự áp dụng.

## Bảo mật và vận hành

Không có access key trong code; profile dùng phiên browser-login. Không commit cache credentials, URL presigned hay env chứa secret. Bucket đã bật đủ public-access-block và SSE-S3. Không mở public bucket để Power BI đọc: dùng CSV local export. IAM execution role giữ nguyên phạm vi dữ liệu; danh tính người vận hành khác role Lambda.

Chưa bật log retention mới hoặc lifecycle tự xóa vì cần giữ evidence thực tập. Theo dõi dung lượng và dọn kết quả query sau khi lưu bằng chứng theo cleanup.md. Không xóa bucket hoặc tài nguyên nền khác của người dùng khi kết thúc một lần test.


Lượt xác minh cuối: hai alarm đã ở trạng thái OK; metrics quan sát có 2 invocations, 0 errors, maximum duration 3471.92 ms. Xem aws_final_verification.json. Đây không phải kiểm thử gửi notification hoặc fault injection.
