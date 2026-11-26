# dbt-postgres: Silver và Gold

## Thiết kế hiện tại

Airbyte dùng Full Refresh Overwrite, nhưng dbt Silver và fact dùng incremental MERGE.
Đây là hai cơ chế độc lập: Bronze thay snapshot; dbt so sánh snapshot với đích.
Không dùng MAX(updated_at), vì có thể bỏ sót dữ liệu đến muộn.
Mỗi lượt vẫn đọc toàn bộ Bronze để dedup và so sánh; incremental giảm số dòng ghi,
không phải CDC và không đồng nghĩa chỉ quét dữ liệu mới.

Silver: source_data → hashed → ranked → deduplicated → final.
Khóa mới được insert; hash đổi được update; khóa vắng trong snapshot được xóa mềm.
Nếu khóa xuất hiện trở lại thì _is_deleted được đặt lại false.
Status, channel, currency và mã phương thức/đối tác thanh toán được chuẩn hóa chữ hoa.
Chỉ chạy sau Airbyte thành công; không chạy trong lúc Bronze đang overwrite.
Snapshot rỗng được xem là nguồn rỗng, nên cần xác nhận nếu việc rỗng là bất thường.

Incremental Silver và fact đã được cấu hình; dimension và mart nhỏ vẫn là table
để không giữ thừa nhóm tổng hợp khi đơn đổi trạng thái/ngày/kênh hoặc bị xóa.
Không tự đổi các bảng tổng hợp sang merge nếu chưa có quy tắc xóa nhóm cũ.
Không đổi grain, schema hay tên model trong lần chuẩn hóa này.

Quy ước:
- SQL giữ source/ref, unique_key và quy tắc nghiệp vụ rõ ràng.
- Mỗi model SQL khai báo `materialized` trong khối `config()` ở đầu file. Model tăng dần khai báo thêm `incremental_strategy='merge'` và `unique_key` theo khóa của bảng.
- dbt_project.yml giữ schema, tag, contract và các cấu hình dùng chung; không đặt materialization hoặc incremental_strategy theo thư mục.
- business_hash.sql tránh lặp danh sách trường khi tạo hash.
- YAML contracts/tests vẫn được giữ; dbt run không tự chạy test.
- on_schema_change=fail: không tự thay cấu trúc bảng ngoài dự kiến.

Sau khi đã khởi tạo đúng cấu trúc, chạy thường ngày với full_refresh=false.
Không cần full-refresh chỉ vì thay cách trình bày SQL hay macro tạo hash.
Đây là các thực hành dbt phổ biến, không có chứng nhận “chuẩn quốc tế” duy nhất.

- models/sources.yml: nguồn Airbyte, schema bronze.
- models/silver/silver_*.sql: đọc Bronze trực tiếp bằng source(), ép kiểu, dedup, incremental MERGE.
- models/gold/dimensions: các chiều phân tích.
- models/gold/facts: fact bán vé incremental, một dòng mỗi order_item_id.
- models/gold/marts: tổng hợp ngày/sự kiện/kênh.
- schema.yml: mô tả, kiểu cột, contracts và YAML tests.
- macros/incremental_changes.sql: cập nhật dòng mới/thay đổi/xóa mềm.
- profiles.yml: kết nối từ biến môi trường, không chứa mật khẩu.

Silver ghi thẳng schema silver; Gold ghi thẳng schema gold. Không dùng gold_build.
Không có models/bronze hay work_bronze trong luồng xử lý.

Tại gốc Ticket_Project:
```powershell
docker compose run --rm dbt-postgres compile
docker compose run --rm dbt-postgres docs
```

Vận hành chính bằng DAG để đồng bộ Airbyte và chạy đúng thứ tự.
Nếu chạy model riêng, chỉ thực hiện khi Bronze đã sẵn sàng và không có DAG/sync khác:
```powershell
docker compose run --rm dbt-postgres run --stage silver --model silver_orders
```

run không tự gọi test. Test chỉ chạy khi bạn yêu cầu test --stage silver/gold.
Full snapshot phải chứa toàn bộ dữ liệu hiện tại, không phải dữ liệu lọc một ngày.
