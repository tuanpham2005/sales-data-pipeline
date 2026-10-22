# Báo cáo sẵn sàng của Kiro

Ngày tạo: 2026-10-22 (theo giờ hệ thống).

## 1. Xác nhận workspace

- Thư mục mở đúng: `D:\AWS\sales-data-pipeline` (có `run_local.py`, `src/pipeline.py`, `lambda_function.py`, `build_lambda.py`).
- Không phát hiện sai lệch so với cấu trúc dự kiến trong AGENTS.md.

## 2. Tài liệu đã đọc

| Tài liệu | Mục đích |
| --- | --- |
| `AGENTS.md` | Hướng dẫn chung: profile `codex-aws`, Region `ap-southeast-2`, mức hướng dẫn HIGH, quy tắc phối hợp. |
| `docs/codex-kiro-handoff.md` | Bàn giao từ Codex: kết quả chạy test, kết nối MCP, yêu cầu đầu tiên dành cho Kiro. |
| `README.md` | Mô tả pipeline local: quy tắc làm sạch dữ liệu bán hàng, kết quả chuẩn, các mốc tiếp theo. |
| `README_LAMBDA.md` | Mô tả adapter Lambda/S3: đóng gói ZIP, cấu hình hàm, test thủ công, trigger S3, giới hạn. |

## 3. Tóm tắt pipeline local và adapter Lambda/S3

### Pipeline local (Mốc 1)

- Entry point: `run_local.py` gọi logic trong `src/pipeline.py`.
- Input: file CSV trong `data/raw/` (mặc định `sales_sample.csv`).
- Xử lý: dùng thư viện chuẩn Python (csv, decimal), không cần pip install.
- Quy tắc chính: 9 cột bắt buộc, khóa duy nhất là cặp `(order_id, line_id)`, tiền tệ chỉ VND, dùng Decimal không dùng float.
- Output: mỗi lần chạy tạo thư mục `data/output/<run_id>/` chứa `cleaned.csv`, `rejected.csv`, `summary.json` và 3 file tổng hợp (theo ngày, sản phẩm, thành phố).
- Kết quả chuẩn bộ mẫu: 10 dòng đầu vào, 6 hợp lệ, 4 loại, tổng quantity 17, tổng doanh thu 670.000 VND.
- Kiểm thử: `python -m unittest discover -s tests -v` → 18/18 đạt (Codex đã chạy, không lặp lại).

### Adapter Lambda/S3 (Mốc Lambda)

- Entry point: `lambda_function.py` với handler `lambda_function.lambda_handler`.
- Đóng gói: `python build_lambda.py` → `dist/fcj-sales-lambda.zip` (chứa `lambda_function.py` ở gốc và `src/` bên cạnh).
- Adapter gọi lại hàm `process_csv` trong `src/pipeline.py`, không thay đổi quy tắc làm sạch.
- Đọc input từ S3 (prefix `raw/`), ghi output vào `processed/` và `rejected/` trong cùng bucket.
- Output key dùng SHA256 của tên key đầu vào, cố định để lần phát lại cùng nội dung không tạo thêm object.
- Test adapter dùng S3 giả lập (fake client), chưa chứng minh quyền/trigger trên tài khoản thật.
- Theo `README_LAMBDA.md`, hàm `fcj-sales-processor` đã được cấu hình trên AWS; đây là ghi chú cấu hình, chưa được Kiro xác minh trong lượt này.

## 4. Kết quả kiểm tra AWS MCP

- Công cụ: AWS MCP (`aws-mcp`), thao tác `STS GetCallerIdentity`.
- Region: `ap-southeast-2`.
- Trạng thái API call: thành công (`api_calls[0].status = "success"`).
- Kết quả trả về:

```json
{
  "UserId": "AROA6MDQ7VE2AH6DY4RIM:546874e8-20e1-70d9-4677-a0d287158f68",
  "Account": "988079434036",
  "Arn": "arn:aws:sts::988079434036:assumed-role/AccountFullAccessRole/546874e8-20e1-70d9-4677-a0d287158f68"
}
```

- Nhận xét: caller là assumed-role `AccountFullAccessRole` trong project AWS. Đây là bằng chứng AWS thật, xác nhận Kiro có quyền truy cập qua MCP.
- Lưu ý: `GetCallerIdentity` chỉ xác nhận kết nối và định danh; không chứng minh các quyền cụ thể (Lambda, S3, IAM) hay tài nguyên đã tồn tại.

## 5. Giới hạn lượt kiểm tra này

- Chỉ tạo file `docs/kiro-readiness.md`. Không sửa code ứng dụng (`src/pipeline.py`, `lambda_function.py`, `run_local.py`, `build_lambda.py`).
- Không tạo, sửa, xóa hay triển khai tài nguyên AWS nào.
- Không chạy lại kiểm thử local (Codex đã xác nhận 18/18 đạt).
- Chưa xác minh các tài nguyên AWS ghi trong `README_LAMBDA.md` (hàm Lambda, role IAM, bucket S3, trigger) có thực sự tồn tại hay không.

## 6. Bước tiếp theo

- Chờ yêu cầu tiếp theo của người dùng.
- Khi có yêu cầu, đọc lại `docs/codex-kiro-handoff.md` để nắm trạng thái bàn giao mới nhất trước khi thay đổi file.
- Nếu yêu cầu liên quan đến tài nguyên AWS, sẽ dùng AWS MCP (thao tác chỉ đọc trước) để kiểm tra tài nguyên thực tế trước khi đề xuất thay đổi.

## Mẫu bàn giao lượt này

- Yêu cầu của người dùng: kiểm tra sẵn sàng — đọc tài liệu, xác nhận workspace, gọi STS GetCallerIdentity, tạo file phản hồi.
- Bên thực hiện: Kiro.
- File đã tạo: `docs/kiro-readiness.md`.
- Kiểm tra đã chạy: `STS GetCallerIdentity` qua AWS MCP → thành công.
- Bằng chứng AWS thực tế: kết quả GetCallerIdentity ở mục 4.
- Vấn đề còn lại: chưa xác minh tài nguyên AWS thực tế (Lambda, S3, IAM role, trigger).
- Hành động tiếp theo: chờ yêu cầu tiếp theo của người dùng.
