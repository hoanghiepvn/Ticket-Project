# dbt chỉ có Silver và Gold

Luồng: SQL Server → Airbyte → PostgreSQL Bronze → dbt Silver → dbt Gold → Power BI.
Airflow điều phối các bước, không trực tiếp kéo dữ liệu thay Airbyte.

## Một model là gì?

Một model SQL là một file SELECT để dbt tạo/cập nhật bảng đích.
Ví dụ models/silver/silver_orders.sql:
- Đọc source('bronze','orders'), được khai báo trong models/sources.yml với schema: bronze.
- Ép kiểu, trim, tính hash và dedup ngay trong SQL đó.
- MERGE theo order_id vào silver.orders (schema silver, alias orders).
Không có model Bronze, bảng stg_* hoặc bước sao chép work_bronze trong luồng mới.

ref('silver_orders') đọc kết quả model silver_orders, tức silver.orders.
Gold đọc các model Silver bằng ref(), tạo dimension/fact/mart.
Gold ghi trực tiếp vào schema gold, không có gold_build. Chỉ refresh BI sau toàn bộ DAG thành công; không còn vùng cách ly kết quả đang xây.

## Nguồn và đích

| Thành phần | Đầu vào | Đầu ra |
|---|---|---|
| Airbyte | SQL Server dbo.orders | bronze.orders |
| dbt silver_orders | bronze.orders | silver.orders |
| dbt fact_ticket_sales | Silver và dimension | gold.fact_ticket_sales |
| Airflow record_completion | Gold đã xây xong | Audit và quyền đọc BI |

Tất cả schema đích trên nằm trong PostgreSQL ticketing_analytics.

## Thứ tự Airflow

Trigger Airbyte → đợi sync thành công → xác nhận Bronze đã sẵn sàng
→ 5 task Silver riêng → 5 task dimension → fact → mart → ghi nhận hoàn tất.

Bronze không có task dbt; task confirm_loaded chỉ kiểm tra cột/khóa và ghi nhận run, không copy dữ liệu.
Các model độc lập cùng tầng có thể chạy song song; Gold đợi toàn bộ Silver.
Tests mặc định tắt, chỉ bật khi run_tests=true.

## Điều kiện vận hành

Tắt lịch sync riêng của Airbyte; không sync thủ công khi DAG đang chạy.
Không còn bản chụp cách ly nên các model sẽ không nhất quán nếu Bronze bị ghi lại giữa chừng.
Nếu cần sync mới sau một run lỗi, chạy một DAG run mới từ đầu; không chỉ retry các model còn thiếu trên một Bronze đã đổi.
Các bảng work_bronze cũ nếu còn trong DB không được đọc nữa; chưa tự xóa dữ liệu lịch sử đó.
