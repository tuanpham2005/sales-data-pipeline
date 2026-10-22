# Kiến trúc, dữ liệu và quy tắc

## Luồng cần hiểu để tự vẽ sơ đồ

Người dùng upload CSV vào S3 raw/. S3 phát event ObjectCreated đúng prefix/suffix tới Lambda. Lambda đọc raw, dùng logic Python để kiểm tra và tính tiền, rồi ghi cleaned, rejected, bốn aggregate và summary vào cùng bucket. Summary được ghi sau cùng. CloudWatch nhận log và metric của Lambda.

Athena đọc dữ liệu **trực tiếp từ S3 processed/cleaned/**. Glue Data Catalog chỉ cung cấp schema/location/SerDe; dữ liệu không chạy qua Glue ETL. Raw table lưu các cột kiểu STRING để OpenCSVSerde đọc ISO dates/Decimal an toàn. View chuyển kiểu rõ ràng; quality gate kiểm tra lỗi trước phân tích. Athena ghi query results riêng vào athena-results/. CSV export đã kiểm chứng được tải về máy, rồi Power BI import và refresh thủ công.

Khi tự vẽ trên draw.io: dùng icon AWS chính thức, chia data plane (S3/Lambda/Athena) và metadata (Glue Catalog), vẽ mũi tên metadata khác mũi tên đọc/ghi dữ liệu. Thể hiện IAM execution role cạnh Lambda, CloudWatch ở nhánh log/metric, Power BI bên ngoài AWS. Ghi Sydney ap-southeast-2 cho tài nguyên regional. Tự giải thích vì sao không cần crawler/ETL job với schema CSV cố định và lab nhỏ. Bản hướng dẫn này không phải sơ đồ kiến trúc hoàn toàn do AI tạo để nộp.

## Data dictionary

| Cột | Kiểu raw / kiểu view | Quy tắc |
| --- | --- | --- |
| order_id | STRING / VARCHAR | Mã đơn bắt buộc, giữ nguyên dưới dạng text |
| line_id | STRING / VARCHAR | Mã dòng hàng trong đơn, bắt buộc |
| order_date | STRING / DATE | YYYY-MM-DD và ngày tồn tại |
| product | STRING / VARCHAR | Tên sản phẩm, bắt buộc |
| category | STRING / VARCHAR | Nhóm hàng, bắt buộc |
| quantity | STRING / BIGINT | Số nguyên ASCII từ 1 đến 1000000 |
| unit_price | STRING / DECIMAL(38,2) | Từ 0 đến 1000000000000, tối đa 2 chữ số lẻ |
| city | STRING / VARCHAR | Thành phố, bắt buộc |
| currency | STRING / VARCHAR | Chỉ VND |
| total_amount | STRING / DECIMAL(38,2) | quantity × unit_price; thêm bởi pipeline |
| source_path | Không có trong CSV / VARCHAR | View bổ sung từ Athena "$path" để truy nguồn |

Khóa dòng là (order_id, line_id). Một đơn nhiều dòng là hợp lệ. Trong một file, giữ dòng hợp lệ đầu tiên và loại các dòng hợp lệ trùng khóa phía sau. Khóa của một dòng không hợp lệ không chiếm chỗ của một dòng hợp lệ sau đó. Chỉ bỏ khoảng trắng đầu/cuối; không tự đổi mã đơn hoặc chuẩn hóa tên sản phẩm.

Giới hạn file đầu vào 5 MiB. CSV thiếu/thừa/trùng header, encoding sai hoặc CSV không parse được làm cả file thất bại. Dòng sai số cột/thiếu giá trị/ngày/giá/quantity/currency được đưa vào rejected với source_row, raw_record JSON và error. Comma, quote, Unicode được hỗ trợ. Giá có 3 chữ số lẻ kể cả 1.230 bị loại. Newline nằm trong giá trị sau trim bị loại rõ vì Athena OpenCSVSerde không hỗ trợ multiline record. Đây là ràng buộc tương thích của lab.

Không tính thuế, hoàn hàng, chiết khấu hoặc đổi ngoại tệ. Decimal dùng trong Python; SQL dùng DECIMAL, không float.

## Output

Mỗi source key sinh SHA256 của chính key. Cùng key luôn dùng lại output key:

- processed/cleaned/<id>.csv
- rejected/<id>.csv
- processed/aggregates/date/<id>.csv
- processed/aggregates/product/<id>.csv
- processed/aggregates/category/<id>.csv
- processed/aggregates/city/<id>.csv
- processed/summaries/<id>.json

Số dòng, số đơn phân biệt và tổng quantity là ba chỉ số khác nhau. Với mẫu: 6 dòng, 5 đơn, 17 sản phẩm. Tổng doanh thu từng cách nhóm phải khớp 670000.00 VND; không cộng số đơn của từng nhóm để suy ra tổng số đơn.

## Nguồn và giới hạn

sales_sample.csv là dữ liệu giả lập được cung cấp cùng lab, không phải dữ liệu doanh nghiệp thật. Lượt này không thêm dataset bên ngoài. quoted_unicode.csv cũng do lượt kiểm thử tự tạo, chỉ để kiểm tra định dạng; không có dữ liệu cá nhân/doanh nghiệp. Khi bổ sung dữ liệu bên ngoài, phải ghi URL, license, thời điểm lấy và script chuyển đổi trước khi dùng.

Không có cross-file business dedup. Cùng giao dịch ở hai raw keys sẽ tạo hai output sets; quality gate phát hiện khóa trùng và dừng export. Không có exactly-once, transaction đa object, kiểm soát thứ tự source version hoặc lock. ETag IfMatch chỉ chặn event cũ khi object đã bị thay trước lúc đọc; hai invocation đọc hai phiên bản rồi ghi chồng vẫn có thể xảy ra. Athena cũng có thể đọc file trong lúc một đợt ghi chưa hoàn tất: chạy query sau khi log/summary báo thành công, không query đồng thời khi demo.
