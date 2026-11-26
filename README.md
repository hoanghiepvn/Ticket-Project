# Ticket Project — SQL Server / Airbyte / PostgreSQL / dbt / Airflow

Luồng chính: SQL Server → Airbyte → PostgreSQL Bronze → dbt Silver/Gold → Power BI.
Không còn Kafka, Spark, Iceberg, MinIO, Lakekeeper hay Streamlit trong Compose này.

## Thư mục

- `Airflow/dags/`: DAG điều phối; `Airflow/plugins/ticketing/`: API client, sensor, xác nhận Bronze, dbt runner, xuất bản Gold.
- `Dbt/Dbt-Postgres/`: project dbt chỉ có models Silver và Gold (dimensions/facts/marts); nguồn khai báo trong models/sources.yml.
- `Airbyte/tools/`: abctl local; cluster Airbyte do abctl quản lý, không khai báo lại trong Compose.
- `Postgres/sql/`: khởi tạo kho và quyền tài khoản.
- `Source/SqlServer/`: schema, 5 script sinh dữ liệu, dữ liệu đã sinh và hướng dẫn nguồn.
- `PowerBI/`: truy vấn BI và DAX.
- `Docker/`: Dockerfile; `compose.yaml` tại gốc là cấu hình triển khai.
- `Scripts/`: khởi động, trigger DAG, quản lý Airbyte.
- `Runtime/data/`: checkpoint, artifact dbt và dữ liệu lịch sử đã có; phần cũ chưa xóa vì cần xác nhận riêng.
- `Documentation/`: hướng dẫn vận hành và quyết định thiết kế.
- `Reports/`: Word và bản thảo hiện có, chưa cập nhật theo lần refactor này.

Thư mục `individual` nằm ngoài project được giữ nguyên.

## Bắt đầu

Đọc [hướng dẫn vận hành](Documentation/OPERATIONS.md).
Giải thích model, source, ref và bảng đích: [luồng dữ liệu dbt](Documentation/DBT_DATA_FLOW.md).
Mở Airflow tại http://localhost:8080, Airbyte tại http://localhost:8000.
Airflow Home có ba DAG: ticketing_bronze → ticketing_silver → ticketing_gold. Trigger Bronze để chạy cả chuỗi; từng nghiệp vụ vẫn có file/task riêng.
PostgreSQL warehouse: localhost:5433, database ticketing_analytics.
Mật khẩu nằm trong .env, không commit/chia sẻ file này.

Lần chạy DAG đầu sau nâng cấp: bật **full_refresh=true**. Từ lần sau để false.
**run_tests=false mặc định**: không chạy dbt test/build tự động. YAML data tests vẫn được khai báo để bạn chủ động sử dụng.

## Hai thư viện Python

- requests==2.32.3: gọi API Airbyte lấy token, gửi yêu cầu đồng bộ, đọc trạng thái job.
- psycopg2-binary==2.9.10: kết nối PostgreSQL để đóng băng đầu vào, xuất bản Gold và ghi audit.

Chúng không phải framework test. Requirements riêng cho Airflow và dbt giúp tránh xung đột phiên bản.

## Phạm vi

Dữ liệu nguồn được sinh mô phỏng nghiệp vụ, không phải dữ liệu giao dịch thật của Ticketbox.
Incremental hiện tại tối ưu phần ghi đích bằng MERGE; vẫn đọc toàn bộ snapshot để nhận diện thay đổi/xóa.
Chưa triển khai CDC, SCD2, tự động gửi email hay HA. Xem [thiết kế](Documentation/ARCHITECTURE.md).
