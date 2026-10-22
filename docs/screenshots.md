# Vị trí cần chụp và kịch bản demo

Chụp bằng chứng từ lần thực hiện thật, ghi ngày và query ID/RequestId; không dựng ảnh Console bằng AI. Lượt này chưa chụp/quay các màn hình dưới đây.

1. AWS Settings → project → Additional Info → Region (Sydney); che thông tin cá nhân không cần thiết.
2. S3 → Properties → Event notification: raw/, .csv, Lambda đích.
3. Lambda → Runtime/handler, memory 256 MB, timeout 30 giây, env SALES_BUCKET; không chụp secret.
4. IAM role → đúng hai phạm vi S3 GetObject và PutObject, basic log policy; Lambda resource policy giới hạn nguồn bucket.
5. S3 → raw sample; processed/cleaned; rejected; summary; aggregate/category. Mở nội dung đã làm sạch và lý do lỗi.
6. CloudWatch log invocation mới: valid=6, rejected=4, revenue=670000.00; RequestId/REPORT.
7. Glue Data Catalog → fcj_sales_db → sales_cleaned_raw → location chỉ cleaned và SerDe/header; view sales_cleaned.
8. Athena → workgroup output/scan limit; quality gate 0 lỗi, KPI 6/5/17/670000, ngày và reconciliation difference=0. Lưu query ID.
9. Upload lại raw cùng key; chụp key list không thêm output set và query KPI không đổi.
10. Power BI Desktop: 3 KPI, 4 biểu đồ và 3 slicer; chụp tổng quan + sau lọc. Ghi “giả lập, refresh thủ công”.
11. CloudWatch metric graph và hai alarm; không ghi “đã gửi email” vì không có action.
12. AWS Pricing Calculator estimate của người dùng; trang cleanup sau khi thực sự dọn ở thời điểm kết thúc.

Video demo đề xuất: giải thích bài toán/dữ liệu giả lập → upload mẫu → log/output → Athena quality/KPI/group totals → Power BI refresh/filter → upload lại cùng key và đối chiếu → nêu giới hạn/cost/cleanup. Sơ đồ kiến trúc do người dùng tự vẽ và tự giải thích theo architecture-and-data.md.
