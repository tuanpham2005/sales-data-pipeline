# Dọn tài nguyên đúng phạm vi

**Tài liệu hướng dẫn, chưa thực thi cleanup.** Giữ tài nguyên khi còn dựng Power BI, chụp ảnh hoặc quay demo. Chỉ dọn sau khi người dùng quyết định kết thúc lab và đã lưu evidence/PBIX/mã nguồn.

Project ID: `988079434036`; Region: `ap-southeast-2`; bucket: `tuan-fcj-sales-pipeline-20261006-a7k9`. Trước mỗi bước đối chiếu lại tên/Region và tài nguyên có thuộc dự án hay không.

1. Lưu query IDs, JSON evidence, dữ liệu xuất, ảnh/video, code ZIP và PBIX ra máy. Kiểm tra không còn invocation/query đang chạy.
2. S3 → Properties → Event notifications: xóa **chỉ notification** trỏ tới fcj-sales-processor với raw/ và .csv. Không thay toàn bộ cấu hình notification bằng rỗng nếu có cấu hình khác.
3. CloudWatch → Alarms: xóa `fcj-sales-lambda-errors` và `fcj-sales-lambda-duration-high` khi không cần nữa. Không xóa alarm khác hoặc để lại hai alarm định kỳ vô thời hạn nếu không dùng.
4. Athena, đúng workgroup: thực thi các câu trong `sql/90_cleanup.sql` từng câu. DROP DATABASE không có CASCADE; nếu còn bảng lạ thì dừng, rà soát ownership. External table bị xóa không tự xóa file S3.
5. Athena → Workgroups: chỉ xóa fcj-sales-workgroup sau khi lưu lịch sử/query cần cho báo cáo. Không xóa hoặc sửa primary.
6. Lambda: xóa đúng fcj-sales-processor nếu đang dọn **toàn bộ dự án**. Nếu chỉ dọn phần Athena vừa thêm, giữ Lambda và trigger; bỏ qua bước 2 và bước này.
7. S3: sau khi ngắt trigger và dừng query, kiểm tra các object trong raw/, processed/, rejected/, athena-results/, artifacts/lambda/fcj-sales-processor-20261022.zip và validation/serde-special/. Chỉ xóa dữ liệu thuộc lab đã quyết định dọn. Không có lệnh tự động empty toàn bộ bucket trong gói này. Nếu bật versioning trong tương lai, cần rà soát cả object versions/delete markers và multipart uploads; trạng thái lúc triển khai là chưa bật versioning.
8. Chỉ xóa bucket nếu muốn kết thúc toàn bộ lab, bucket trống và không còn dữ liệu khác. Không dùng force-delete làm tắt bước kiểm tra.
9. CloudWatch log group /aws/lambda/fcj-sales-processor: giữ tới khi hoàn tất bằng chứng, rồi xóa/đặt retention theo quyết định người dùng.
10. IAM role fcj-sales-lambda-role: chỉ dọn khi Lambda đã xóa và role không còn được sử dụng. Gỡ inline policy fcj-sales-s3-access và managed policy AWSLambdaBasicExecutionRole khỏi **role này**, sau đó xóa role. Không xóa managed policy AWSLambdaBasicExecutionRole của AWS, không chạm AccountFullAccessRole hoặc team-member access.

Cuối cùng kiểm tra Console và AWS Settings → Billing trong các ngày sau vì số liệu billing cập nhật trễ. Giữ tài liệu local không phát sinh phí AWS; xóa credentials không phải một bước cleanup tài nguyên dự án.
