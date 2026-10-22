# Kiểm thử và bằng chứng

## Local — đã chạy 22/10/2026

`python -m unittest discover -s tests -v`: **30/30 PASS** sau khi bổ sung category và quy tắc tương thích CSV. Không gọi AWS trong unit tests.

| Nhóm | Kết quả đã kiểm tra |
| --- | --- |
| Golden sample | 10 input, 6 valid, 4 rejected, 5 orders, quantity 17, revenue 670000.00 |
| Bốn dimension | date/product/category/city cùng cộng lại 670000.00 |
| Chất lượng | Thiếu từng trường bắt buộc, ngày không tồn tại, giá âm/chữ/NaN/Infinity, quantity sai, duplicate line key bị loại |
| Chính xác tiền | Decimal, zero price, giá/quantity biên, giá có 3 chữ số lẻ bị loại |
| CSV | BOM/reordered header, comma/quote/Unicode; header lỗi hoặc quote không đóng làm file thất bại |
| Giới hạn | File vượt 5 MiB, kể cả ContentLength khai thiếu; body được đóng; encoding lỗi không ghi output |
| Lặp/cập nhật | Cùng key ghi lại 7 output keys; nội dung mới cùng key thay doanh thu; stale ETag được bỏ qua |
| Không che giấu giới hạn | Hai file cùng giao dịch chưa được dedup; lỗi ghi object thứ hai để lại output đầu tiên, chứng minh không atomic |

## AWS — đã chạy 22/10/2026

Evidence nằm ở `evidence/2026-10-22/`, chứa API call status và query ID. Không chỉ dựa trên chữ “Succeeded”.

1. Đọc cấu hình Lambda, role inline/managed policies, Lambda invoke policy và bucket notification. Python 3.13/256 MB/30 giây, handler/env đúng; trigger raw/ + .csv; S3 private/SSE-S3.
2. Download package Lambda trước thay đổi: ba source files khớp local. Download S3 raw: byte-for-byte khớp sample local. Cleaned/rejected/summary trước thay đổi khớp golden sample.
3. Cập nhật ZIP trên chính hàm có sẵn, xác minh CodeSha256 và LastUpdateStatus=Successful. Lưu backup ZIP để rollback.
4. Upload **cùng** raw/sales_sample.csv hai lần. Summary LastModified lần lượt 03:34:09Z và 03:34:49Z; cùng ETag summary. Danh sách key/ETag của 7 output data files giữ nguyên giữa hai lần. Không tính folder marker 0 byte là data file. Log Processed từ invocation thật và summary mới chứng minh S3 trigger chạy.
5. Athena quality gate: 6 rows, 1 source file, 0 invalid rows, 0 duplicate line keys. KPI trước/sau repeat: 5 orders, 17 quantity, 670000.00. Daily: 150000.00 / 340000.00 / 180000.00 theo 01/02/03 tháng 9.
6. SQL reconciliation: difference=0.00 ở date/product/category/city; duplicate query không trả dòng nào.
7. Fixture có comma/quote/Unicode upload vào validation/serde-special/, tách khỏi cleaned. Table sales_csv_validation đọc lại đúng “Bút, \"đỏ\" – Việt Nam” và “Sổ tay \"A\", khổ nhỏ”, tổng từng dòng 20.50 và 15.00. Query 57e300c1-94c5-4e0c-889f-9656dd45ef08.

KPI sau repeat: query **6f11a343-1491-4601-92df-59c37da9a93a**. Quality gate sau repeat: **3651d095-c04a-4176-a05d-47808c3e234a**. Kết quả full trong after_repeat_and_csv_validation.json.

## Chưa chứng minh / cần người dùng thực hiện

- Chưa tạo PBIX trong Power BI Desktop, chụp slicer hay quay video demo. Đã cung cấp CSV SQL thật, Power Query, DAX, theme và bước tái hiện.
- Chưa fault-inject vào AWS, chưa kiểm thử race giữa invocation đồng thời hoặc khôi phục partial write trên cloud. Local test chỉ mô tả giới hạn tương ứng.
- Chưa chứng minh exactly-once, global dedup, tải lớn hoặc dữ liệu vượt 5 MiB; không dùng các cụm này trong báo cáo như kết quả đạt được.
- Alarm đã tạo cấu hình, chưa phát sinh một lỗi Lambda có chủ đích để chứng minh chuyển trạng thái ALARM. Alarm không có kênh gửi thông báo.

## Tái kiểm tra khi chỉnh tiếp

Chạy local tests → build ZIP → kiểm tra revision và backup → cập nhật đúng hàm → upload sample cùng key → chờ summary/log mới → quality gate → SQL acceptance → export. Không chạy test raw key khác vào cleaned chung rồi bỏ quên dữ liệu; fixture parsing phải ở prefix validation riêng. Nếu muốn dọn test data, xem cleanup.md và xác nhận phạm vi trước.
