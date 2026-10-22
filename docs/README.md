# Tài liệu dự án

Đề tài: **Xây dựng pipeline xử lý và phân tích dữ liệu bán hàng trên AWS**.

| Tài liệu | Dùng để |
| --- | --- |
| [STATUS.md](STATUS.md) | Phần đã chạy, phần còn thiếu và bằng chứng |
| [deployment.md](deployment.md) | Chạy local, đóng gói/cập nhật Lambda, tạo catalog và query |
| [architecture-and-data.md](architecture-and-data.md) | Luồng dữ liệu, data dictionary và hướng dẫn tự vẽ kiến trúc |
| [testing.md](testing.md) | Đầu vào, kỳ vọng, kết quả thực tế và giới hạn kiểm thử |
| [operations.md](operations.md) | Log, metric, alarm và xử lý lỗi |
| [costs.md](costs.md) | Giá Sydney đã tra, giả định tải và dự toán |
| [cleanup.md](cleanup.md) | Dọn đúng tài nguyên; chỉ chạy khi muốn kết thúc lab |
| [screenshots.md](screenshots.md) | Các vị trí cần tự chụp/quay để làm báo cáo |
| [workshop.vi.md](workshop.vi.md), [workshop.en.md](workshop.en.md) | Nội dung workshop nháp song ngữ dựa trên việc đã làm |
| [worklog-2026-10-22.md](worklog-2026-10-22.md) | Nhật ký thực tế ngày triển khai |
| [../dashboard/README.md](../dashboard/README.md) | Tái hiện dashboard Power BI |
| [../iam/README.md](../iam/README.md) | Quyền đã xác minh và candidate IAM không được tự attach |

Evidence JSON/query IDs được lưu trong `evidence/2026-10-22/`. Thời điểm trong AWS là UTC; quy đổi sang giờ Việt Nam cộng 7 giờ. Dự án báo cáo Hugo nằm riêng ở `D:/AWS/tuan-fcaj-internship-report`; lượt này không viết đè website báo cáo.
