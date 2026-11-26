# Vận hành Ticket Project

## Lưu ý bản Bronze daily mới

Tên DAG hiện hành: bronze_ticket_events (01:30), bronze_ticket_events_0200 (02:00), silver_ticket_all, gold_ticket_sales. Các hướng dẫn/tên cũ phía dưới là lịch sử; xem Airflow/README.md để vận hành hiện tại.
Hai DAG Bronze hiện cùng connection events: chỉ bật lịch cần dùng. Script run.ps1 gọi bronze_ticket_events.

Bronze hiện chỉ sync Airbyte theo cron, KHÔNG tự trigger Silver/Gold.
Connection IDs nằm ở Airflow/dags/bronze/config.py. Cron, dag_id và mô tả nằm ngay trong hai file Airflow/dags/ticketing_bronze.py và Airflow/dags/airbyte_bronze_cb8a6465.py; hướng dẫn hiện hành ở Airflow/dags/bronze/README.md.
Scripts/run.ps1 hiện chạy thủ công Bronze, không nhận FullRefresh/RunTests.
Các mục chuỗi ba DAG, full_refresh và truyền tham số bên dưới thuộc thiết kế cũ; Silver/Gold sẽ được chỉnh riêng sau.

Mở PowerShell trong thư mục Ticket_Project. Các lệnh dưới đây không chạy test trừ khi bạn chủ động yêu cầu.

## Khởi động

```powershell
.\Scripts\start.ps1
.\Scripts\airbyte.ps1 -Action start
```

Không cần build lại nếu chỉ sửa model dbt/DAG/plugin đã bind mount:
```powershell
.\Scripts\start.ps1
```

Khi thay requirements/Dockerfile, dùng start.ps1 -Build. Build mới cần kết nối PyPI.
Trong lần refactor này, PyPI timeout khi tải python-dateutil; image 4.0 đã dựng bằng thư viện có sẵn từ image 3.0, đã xác nhận đúng các phiên bản requirements.
Docker/Dockerfile.local-cache là phương án build offline trên máy còn image ticketing-elt:3.0-postgres:

```powershell
docker build -f Docker/Dockerfile.local-cache -t ticketing-elt:4.0-postgres .
```

Không dùng phương án cache nếu đã thay phiên bản requirements. Máy mới dùng Docker/Dockerfile mặc định.

- Airflow: http://localhost:8080 — user admin; mật khẩu AIRFLOW_ADMIN_PASSWORD trong .env.
- Airbyte: http://localhost:8000. Xem thông tin đăng nhập bằng:
```powershell
.\Scripts\airbyte.ps1 -Action credentials
```
Không gửi output credentials lên chat/repository.
- PostgreSQL: localhost:5433, database ticketing_analytics.
  - warehouse_admin / WAREHOUSE_PASSWORD: quản trị, dbt.
  - airbyte_loader / AIRBYTE_DB_PASSWORD: Airbyte destination.
  - powerbi_reader / BI_PASSWORD: Power BI chỉ đọc Gold.
- Trong container: PostgreSQL là warehouse-db:5432; trong Airbyte local dùng host.docker.internal:5433.

Đổi .env không tự đổi mật khẩu tài khoản đã tồn tại trong DB/Airflow. Giữ credential hiện hành khi di chuyển thư mục.
Không chạy docker compose down -v: tùy chọn này xóa dữ liệu volume.

## Cấu hình trước khi chạy

Airbyte: 5 stream events, ticket_types, orders, order_items, payments.
Destination schema bronze; full refresh/overwrite, không append bản chụp lặp.
Chỉ Airflow lên lịch đồng bộ; tắt lịch độc lập trong Airbyte. Không bấm sync thủ công trong lúc DAG đang chạy.
.env cần AIRBYTE_API_URL, AIRBYTE_CLIENT_ID, AIRBYTE_CLIENT_SECRET và AIRBYTE_CONNECTION_ID.
Mô hình mặc định full_snapshot yêu cầu từng stream chứa toàn bộ trạng thái nguồn hiện tại, không chỉ dữ liệu của một ngày.
Các cột updated_at dùng giờ nghiệp vụ Việt Nam; không trộn dữ liệu UTC mà chưa chuyển múi giờ.

## Chạy xử lý

Lần đầu sau refactor, Silver cũ chưa có metadata incremental:
```powershell
.\Scripts\run.ps1 -FullRefresh
```

Lần sau:
```powershell
.\Scripts\run.ps1
```

Hoặc Airflow → DAG ticketing_bronze → Trigger → full_refresh=true lần đầu.
Home có ba DAG: ticketing_bronze → ticketing_silver → ticketing_gold. Giữ cả ba unpaused; chỉ trigger Bronze để chạy cả chuỗi.
Bronze gọi Silver và Silver gọi Gold sau khi tầng trước thành công, truyền cùng tham số. Cha chờ con bằng sensor reschedule nên không chiếm worker.
Chạy riêng Silver/Gold chỉ khi dữ liệu tầng trước đã sẵn sàng và không có chuỗi khác đang chạy. Silver chạy riêng vẫn gọi Gold.
Không xóa/clear run cũ khi đã có sync mới. Nếu DAG con lỗi, sửa/clear task của đúng run con; sau khi con thành công, clear task wait_for_* bị lỗi ở DAG cha. Không reset DAG con đã chạy bằng một run mới tùy tiện.
run_tests=false mặc định. allow_empty_snapshot=false bảo vệ tránh nguồn rỗng làm xóa logic hàng loạt.
Full refresh xây lại Silver và Gold trực tiếp. Lần đầu chuyển từ Gold cũ thiếu metadata incremental cần full_refresh=true. Gold có thể cập nhật dở nếu một task lỗi; chỉ refresh BI sau toàn bộ DAG thành công.

Chỉ khi bạn muốn chạy YAML tests:
```powershell
.\Scripts\run.ps1 -RunTests
docker compose run --rm dbt-postgres test --stage silver
docker compose run --rm dbt-postgres test --stage gold
```

Không chạy dbt writer thủ công song song DAG. dbt Gold ghi trực tiếp vào schema gold.

## Xem dbt

dbt Core không có trang đăng nhập riêng. Sửa SQL/YAML trong Dbt/Dbt-Postgres.
```powershell
docker compose run --rm dbt-postgres parse
docker compose run --rm dbt-postgres debug
docker compose run --rm dbt-postgres docs
```

Sau khi docs generate thành công, mở Runtime/data/elt/tools/docs/target/static_index.html bằng trình duyệt để xem lineage và mô tả.
Docs generate đọc catalog DB, không thay thế việc chạy models. Parse chỉ kiểm tra cấu trúc, không xác nhận SQL đã chạy đúng.

## Khi lỗi

- Airbyte submit: không retry POST mù. Checkpoint lưu Runtime/data/elt/<run hash>/airbyte.json.
- Có sync_intent.json nhưng chưa có airbyte.json: kết quả POST không chắc chắn; kiểm tra job Airbyte trước khi can thiệp checkpoint.
- Sensor timeout không hủy job Airbyte. Xử lý job còn chạy trước khi trigger lần mới.
- Silver/Gold lỗi: sửa SQL/YAML, clear task lỗi và downstream trong cùng run nếu chưa có run mới.
- Không clear run cũ sau khi run mới bắt đầu. Không đồng bộ Bronze trong lúc Silver/Gold chạy; không còn bản sao cách ly đầu vào.
- Thay đổi schema: on_schema_change=fail cố ý dừng; xem xét migration/full refresh trước khi tiếp tục.
- Airflow lưu log lỗi, audit.runs lưu thời điểm xác nhận Bronze/publish (cột frozen_at giữ tên cũ để tương thích); đây không phải dịch vụ email cảnh báo.
- Không xóa Runtime/data/elt tùy tiện vì có checkpoint chống gửi job trùng.
- Không còn transaction chung cho toàn bộ Gold. Task record_completion chỉ ghi audit và cấp quyền đọc, không rollback các model đã chạy. Nếu DAG lỗi, sửa và hoàn tất toàn bộ Gold trước khi refresh Power BI.

## Sau di chuyển

Giữ compose project name ticketing-elt để dùng lại đúng named volumes.
Project Ticket_Project có ba DAG ticketing_bronze, ticketing_silver, ticketing_gold. DAG ticketing_elt cũ inactive/paused; lịch sử vẫn giữ.
Các volume/database không bị đổi tên hoặc xóa trong lần tổ chức này.
