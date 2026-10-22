# Bàn giao giữa Codex và Kiro

## Mục tiêu hiện tại

Kết nối Kiro với project AWS đang dùng và thiết lập cách phối hợp trên cùng thư mục `D:\AWS\sales-data-pipeline`.

Người dùng chọn mức hướng dẫn **HIGH**: giải thích kỹ từng bước và lý do để có thể hiểu, demo và viết báo cáo thực tập.

## Kết nối

- AWS profile: `codex-aws`.
- Selected Region: `ap-southeast-2` (Sydney).
- AWS MCP: tên `aws-mcp`, dùng cùng project và profile với Codex.
- Kiro chạy proxy `mcp-proxy-for-aws` phiên bản 1.7.0 từ môi trường riêng `C:/Users/ASUS/.kiro/aws-mcp/venv`; cấu hình tại `C:/Users/ASUS/.kiro/settings/mcp.json`.
- Kiro đã được cài 24 bộ hướng dẫn AWS trong thư mục skills của người dùng.
- Codex đã gọi thành công `STS GetCallerIdentity` qua AWS MCP trong lượt thiết lập này.
- Log thực tế của Kiro đã ghi `mcp.connect.ok` và `Connected` cho `aws-mcp` lúc 10:02 ngày 22/10/2026 (Asia/Saigon). Đã xử lý lỗi timeout bằng cách cài sẵn proxy trong môi trường riêng.
- Kiểm tra độc lập với chính cấu hình Kiro đã khởi tạo MCP thành công và liệt kê 8 công cụ.
- Việc Kiro gọi thao tác AWS trong chat cần được Kiro xác nhận; không suy ra chỉ từ việc kết nối transport thành công.

## Trạng thái code đã kiểm tra

- Pipeline local: `run_local.py` gọi logic trong `src/pipeline.py`.
- Adapter Lambda/S3: `lambda_function.py`; cách đóng gói ở `build_lambda.py`.
- Đã đọc `README.md`, `README_LAMBDA.md` và `event_manual.json`.
- Lệnh đã chạy: `python -m unittest discover -s tests -v`.
- Kết quả: **18/18 kiểm thử đạt**. Các kiểm thử này chạy local với S3 giả lập.
- Lượt thiết lập này chưa kiểm tra tài nguyên triển khai, quyền của Lambda hoặc trigger S3 trên AWS.
- Thư mục hiện chưa có Git repository.

## Phân công lượt thiết lập

| Bên | Công việc | File được ghi trong lượt này | Trạng thái |
| --- | --- | --- | --- |
| Codex | Cấu hình AWS MCP, cài skills cho Kiro, kiểm tra local và chuẩn bị bàn giao | `AGENTS.md`, tài liệu này; cấu hình Kiro nằm ngoài dự án | Hoàn tất |
| Kiro | Đọc hướng dẫn chung, xác nhận đã mở đúng dự án, kiểm tra AWS MCP bằng thao tác đọc | Chỉ tạo `docs/kiro-readiness.md` nếu file đó chưa tồn tại | Đã có docs/kiro-readiness.md; STS thành công, Codex đã đọc |

## Kênh phối hợp đã xác minh

- Code và file bàn giao được lưu trong cùng thư mục dự án; hai bên đọc lại file khi nhận việc.
- Lệnh `kiro chat` đã được thử nhưng bản Kiro 1.2.4 hiện tại báo `workbench.action.chat.newChat` không tồn tại trong renderer log. Chưa có bằng chứng yêu cầu được gửi tới Kiro.
- Người dùng gửi yêu cầu đầu tiên trong chat Kiro theo phần bên dưới. Kiro phản hồi qua `docs/kiro-readiness.md`; Codex đọc file đó khi tiếp tục cuộc trò chuyện.
- Chưa thiết lập cầu nối chat tự động hoặc tiến trình theo dõi chạy nền.

## Yêu cầu đầu tiên dành cho Kiro

1. Đọc `AGENTS.md`, tài liệu này và hai file README.
2. Xác nhận hiểu dự án xử lý dữ liệu bán hàng; nêu ngắn gọn phần local và phần Lambda/S3 hiện có.
3. Nếu `aws-mcp` đã nạp, dùng thao tác chỉ đọc `STS GetCallerIdentity` để xác nhận quyền truy cập. Ghi kết quả thật; nếu chưa gọi được, ghi đúng lỗi hoặc bước người dùng cần thực hiện.
4. Chỉ tạo `docs/kiro-readiness.md` để phản hồi. Không sửa code ứng dụng, không triển khai hoặc thay đổi tài nguyên AWS trong lượt kiểm tra kết nối này.
5. Chờ yêu cầu tiếp theo của người dùng sau khi xác nhận.

## Bổ sung bối cảnh báo cáo ngày 22/10/2026

- Người dùng cung cấp thư mục Hugo `D:/AWS/tuan-fcaj-internship-report` và hai nguồn yêu cầu: https://hcm-rules.awsfcaj.com/3-project/ và https://hcm-rules.awsfcaj.com/5-scoring/.
- Dùng hai nguồn này khi lập kế hoạch và rà soát báo cáo. Người dùng phải tự thiết kế, vẽ và giải thích kiến trúc; hỗ trợ AI không thay thế phần đó.
- Báo cáo hiện còn Proposal IoT Weather và Workshop S3/VPC Endpoint của mẫu, chưa khớp pipeline bán hàng. Trang tiếng Anh còn thông tin cá nhân mẫu.
- Người dùng đã xác nhận ngày bắt đầu 26/08/2026. Ngày kết thúc và ngày cần mộc chưa xác định; dòng thời gian VI/EN đã được sửa theo thông tin này. Không tự gán ngày kết thúc hoặc hạn nộp.
- Repo báo cáo có thay đổi staged/unstaged của người dùng. Lượt rà soát chỉ đọc nội dung báo cáo; giữ nguyên các chỉnh sửa đó.
- Khi viết, phân biệt bằng chứng local với bằng chứng AWS; blog, sự kiện và worklog phải dựa trên việc thực tế.
- Bản đối chiếu ban đầu được lưu tại `C:/Users/ASUS/Documents/Codex/2026-10-22/m-x20/outputs/doi-chieu-workshop-fcaj.md`.

## Mẫu bàn giao các lượt sau

- Yêu cầu của người dùng:
- Bên thực hiện:
- File đang xử lý:
- Thay đổi đã lưu:
- Kiểm tra đã chạy và kết quả:
- Bằng chứng AWS thực tế (nếu có):
- Vấn đề còn lại:
- Hành động tiếp theo:

Chỉ ghi việc thực sự đã làm. Khi bên kia đang sửa một file, chờ bàn giao trước khi sửa tiếp file đó.

## Cập nhật ngày thực tập theo xác nhận người dùng

- Bên thực hiện: Codex.
- File đang xử lý: `content/_index.vi.md`, `content/_index.md` trong repo báo cáo.
- Ngày bắt đầu đã xác nhận: 26/08/2026. Ngày kết thúc và ngày cần mộc: chưa xác định.
- Trạng thái: hoàn tất. Mỗi trang chỉ đổi một dòng thời gian; đã kiểm tra ngày bắt đầu đúng và phần chưa xác định hiển thị rõ. Các file đã stage được giữ nguyên.


## Triển khai dàn ý người dùng ngày 22/10/2026

- Bên thực hiện: Codex; người dùng đã yêu cầu triển khai các giai đoạn A–F.
- File đang xử lý: src/pipeline.py, lambda_function.py, run_local.py, tests/test_pipeline.py, tests/test_lambda.py; bổ sung sql/, scripts/, dashboard/, docs/ và requirements-cloud.txt.
- Kiro: chờ bàn giao; không sửa đồng thời các file trên.
- Giữ nguyên báo cáo Hugo trong thư mục riêng. Không tạo lại/xóa tài nguyên AWS hiện có.
- Đã xác minh AWS ban đầu: Lambda python3.13/256 MB/30 giây; S3 trigger raw/ + .csv; database fcj_sales_db chưa tồn tại; project đang ở FREE plan.


## Bàn giao sau triển khai A–F ngày 22/10/2026

- Bên thực hiện: Codex. Đã hoàn tất code/SQL/docs thuộc lượt này; giải phóng quyền sửa các file đã ghi ở phần phân công.
- Hiện trạng thật và việc còn thiếu: đọc docs/STATUS.md trước khi sửa tiếp.
- Local: 30/30 tests PASS. Golden sample không thay đổi. Category aggregation và kiểm tra định dạng CSV được bổ sung.
- AWS: cập nhật Lambda hiện có; S3 upload/repeat thành công; 7 output files cùng key/ETag; Athena 6 lines, 5 orders, quantity 17, revenue 670000.00, không invalid/duplicate rows.
- Catalog/workgroup/2 CloudWatch alarms đã tạo và xác minh. Hai alarm hiện OK; không có notification action. Không thêm quyền Athena/Glue vào Lambda role.
- Evidence: docs/evidence/2026-10-22/. Giữ nguyên file phản hồi của Kiro.
- Dashboard: chỉ mới gói Power BI có dữ liệu Athena thật + Power Query/DAX/theme và hướng dẫn, chưa có PBIX. Người dùng cần tạo visual/filter và kiểm tra.
- Báo cáo Hugo nằm riêng, chưa được chép đè. Đã có workshop.vi.md/workshop.en.md và worklog-2026-10-22.md dựa trên việc thật.
- Người dùng đã chọn giữ phần Glue/Athena và hai alarm để tiếp tục demo; không tự cleanup.
- Bước tiếp theo: hỗ trợ người dùng dựng Power BI và tự vẽ kiến trúc/chụp demo/hoàn thiện Calculator estimate. Không làm lại tài nguyên hay chạy test cloud ngoài phạm vi khi chưa có yêu cầu mới.

## Đưa mã nguồn lên GitHub ngày 22/10/2026

- Yêu cầu: người dùng yêu cầu Codex trực tiếp commit/push dự án.
- Bên thực hiện: Codex; file đang xử lý: .gitignore và tài liệu bàn giao này, cùng metadata Git. Không sửa mã ứng dụng hoặc tài nguyên AWS.
- Đã xác minh GitHub CLI đăng nhập tuanpham2005; repo tuanpham2005/sales-data-pipeline tồn tại, đang public và chưa có commit.
- Bổ sung ignore cho credential/caches và ZIP build/backup có thể tạo lại; các file này vẫn giữ trên máy. Không thay đổi visibility của repo.
- Đã kiểm tra 94 staged files bằng pattern scan: không phát hiện access-key IDs, GitHub tokens, private keys, literal AWS secrets hoặc URL presigned. Đây không phải security audit đầy đủ.
- Đã push commit mã nguồn đầu tiên 35d3b045b859a5d7281413a138bec694be670264 lên main; git ls-remote xác nhận đúng SHA và working tree sạch tại thời điểm kiểm tra. Main đã track origin/main.
- Repo: https://github.com/tuanpham2005/sales-data-pipeline (public). Cập nhật AGENTS.md để các lượt sau biết workspace hiện có Git; không thay đổi tài nguyên AWS trong lượt này.
- Tài liệu bàn giao này được lưu bằng commit riêng sau commit mã nguồn; kiểm tra git log/status để lấy HEAD mới nhất. Không ghi secret hoặc credential vào Git.
