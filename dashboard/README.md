# Power BI dashboard: tái hiện từ kết quả Athena

Đây là gói dữ liệu, Power Query và DAX để người dùng dựng trong **Power BI Desktop**. Chưa có file PBIX hoàn tất hoặc dashboard đã publish. Dữ liệu mẫu là **giả lập**. Đây là **batch với refresh thủ công**, không phải realtime.

## 1. Chuẩn bị dữ liệu

`data/sales_from_athena.csv` là kết quả thật của `sql/12_dashboard_export.sql`, không phải tự suy diễn từ kết quả mong đợi. `data/export-metadata.json` ghi query ID, nguồn và thời điểm xuất. Không import toàn bộ thư mục `athena-results/`: ở đó còn kết quả truy vấn cũ và các schema khác nhau.

Xuất lại sau khi nguồn thay đổi, tại thư mục gốc dự án:

```powershell
python -m pip install -r requirements-cloud.txt
python scripts/analytics.py export --profile codex-aws --expect-sample
```

`--expect-sample` chỉ dùng khi vùng cleaned chỉ có bộ mẫu chuẩn. Với dữ liệu mới hợp lệ, bỏ cờ này sau khi kiểm tra phạm vi; quality gate vẫn phải đạt. Nếu duplicate line keys hoặc dữ liệu lỗi kiểu, script dừng trước khi ghi đè CSV dashboard. Không tự xóa dữ liệu để làm test đạt.

## 2. Import và kiểu dữ liệu

1. Mở Power BI Desktop → **Transform data** → **New Source → Blank Query**.
2. Mở **Advanced Editor**, dán nội dung `Sales.pq`; sửa `CsvPath` nếu chuyển thư mục.
3. Đặt tên query là **Sales**, chọn **Close & Apply**.
4. Cột `order_id`, `line_id` phải là Text để giữ mã/leading zeros. `order_date` là Date; `quantity` là Whole Number. Tiền dùng Fixed Decimal Number, định dạng 2 số lẻ và VND.
5. Query không thay lỗi bằng null. Nếu lỗi chuyển kiểu, kiểm tra CSV và SQL trước khi hiển thị KPI.

Giới hạn: Fixed Decimal của Power BI có phạm vi nhỏ hơn DECIMAL(38,2) trong Athena. Bộ mẫu hiện tại nằm trong phạm vi; với doanh thu rất lớn phải đánh giá lại mô hình hiển thị, không chuyển sang float rồi tuyên bố giữ chính xác tuyệt đối.

## 3. Measure và bố cục

Tạo từng measure riêng trong `measures.dax`. Import `theme.json` tại **View → Themes → Browse for themes** nếu muốn.

| Thành phần | Fields |
| --- | --- |
| Card 1 | Revenue VND |
| Card 2 | Distinct Orders |
| Card 3 | Units Sold |
| Card phụ | Valid Line Items |
| Line chart | X: order_date (cột ngày trực tiếp); Y: Revenue VND |
| Bar chart sản phẩm | Y: product; X: Revenue VND; sắp giảm dần |
| Bar chart nhóm hàng | Y: category; X: Revenue VND |
| Bar chart thành phố | Y: city; X: Revenue VND |
| Slicer | order_date kiểu Between; category và city kiểu Dropdown |

Đặt slicer bên trái, KPI trên cùng, biểu đồ bên dưới; chỉnh Edit interactions để các slicer lọc mọi visual. Ghi tiêu đề “Dữ liệu giả lập – làm mới thủ công” và thời điểm export từ metadata. Không cộng `distinct_orders` của từng sản phẩm: một đơn có nhiều sản phẩm.

## 4. Kiểm tra trước khi lưu PBIX

Với tất cả slicer được xóa: **670000.00 VND; 5 đơn; 17 sản phẩm; 6 dòng hàng**.

| Bộ lọc/ngày | Doanh thu VND |
| --- | ---: |
| 2026-09-01 | 150000.00 |
| 2026-09-02 | 340000.00 |
| 2026-09-03 | 180000.00 |
| category = Stationery | 250000.00 |
| city = Ha Noi | 360000.00 |

Đối chiếu với các CSV `data/revenue_by_*.csv` và `data/kpis.csv` cùng đợt export. Lưu PBIX, chụp trang tổng quan và trạng thái sau lọc. Đây là bước Desktop người dùng cần thực hiện; chưa được ghi nhận hoàn tất trong evidence cloud.

## 5. Quy trình cập nhật

Upload raw → chờ Lambda hoàn tất → chạy quality gate/SQL/export → mở PBIX → **Refresh** → đối chiếu KPI → lưu PBIX. Refresh Power BI đơn lẻ chỉ đọc lại CSV local, **không tự chạy Athena**. CSV cũ vẫn là snapshot cũ.

Không trộn dữ liệu rejected/summary vào Sales. Nếu làm trang Data Quality, tạo nguồn và measure riêng, giải thích mẫu số là số dòng đầu vào, không phải số đơn.

Tham khảo: [Csv.Document](https://learn.microsoft.com/en-us/powerquery-m/csv-document).
