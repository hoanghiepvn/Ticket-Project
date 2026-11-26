# Vận hành Bronze → Silver → Gold bằng Dataset

## Luồng hiện tại

Bronze từng bảng (cron do bạn đặt)
→ Airbyte thành công → Dataset Bronze của bảng
→ Silver tương ứng
→ đủ 5 Dataset Silver được cập nhật
→ 5 DAG dimension Gold
→ đủ 5 dimension thành công
→ fact_ticket_sales → agg_daily_sales → có thể refresh Power BI.

Silver chạy theo bảng, không phải chờ các bảng Bronze khác.
Gold dimension chờ đủ cả 5 bảng Silver để giữ ranh giới tầng.

## File cần sửa khi tùy biến

- Airflow/dags/silver/silver_ticket_*.py: từng model Silver, schedule, dag_id, params.
- Airflow/dags/gold/gold_ticket_*.py: từng model Gold, schedule, dag_id, params.
- Airflow/plugins/ticketing/data_assets.py: định danh Dataset và ánh xạ dag_id Bronze.
- Airflow/plugins/ticketing/sensors.py: tự gắn outlets; chỉ thông báo sau Airbyte succeeded.
- Airflow/plugins/ticketing/dataset_dbt.py: chạy dbt, log, khóa chống ghi đồng thời cùng model.
- Dbt: SQL model không thay đổi trong lần cập nhật này.

Sáu file Bronze của bạn không thay đổi. Nếu đổi dag_id Bronze về sau,
cần sửa BRONZE_DAG_TABLES trong data_assets.py tương ứng.

Ví dụ ở silver_ticket_events.py:

    schedule=[BRONZE["events"]]
    ...
    outlets=[SILVER["events"]]

Không cần cron cho Silver/Gold. schedule là danh sách Dataset đầu vào;
outlets là thông báo đầu ra khi task thành công, không phải câu lệnh ghi dữ liệu.
dbt vẫn đọc source bronze, dùng ref giữa models và ghi bảng Silver/Gold.

## Khởi tạo lần đầu với bảng hiện có

Các bảng Silver/fact hiện tại thiếu metadata incremental mà code dbt đang cần.
Chưa tự chạy full-refresh vì thao tác này xây dựng lại dữ liệu đích.

1. Giữ các DAG riêng lẻ Silver/Gold ở trạng thái Paused.
2. Đảm bảo Airbyte đã đồng bộ đủ 5 bảng Bronze và không có sync đang chạy.
3. Trong http://localhost:8080, Trigger DAG silver_ticket_all:
   full_refresh=true; run_tests=false; bronze_mode khớp chế độ Airbyte.
4. Chờ thành công rồi Trigger gold_ticket_all với full_refresh=true.
5. Sau khi cả hai thành công, bật 5 DAG Silver và 7 DAG Gold riêng lẻ.
6. Hai DAG *_ticket_all là công cụ thủ công, schedule=None.
   Để chúng paused trong vận hành thường ngày; không chạy cùng pipeline tự động.

Nếu UI yêu cầu bật DAG thủ công để chạy bước 3/4, chỉ bật DAG *_all đó,
chờ hoàn thành rồi pause lại. Lần chạy thường ngày full_refresh=false.
Dataset từ bước khởi tạo có thể tạo thêm lượt chạy incremental khi bật DAG riêng lẻ.

bronze_mode=full_snapshot khi Bronze thể hiện toàn bộ trạng thái hiện tại của nguồn.
bronze_mode=append_history khi Bronze giữ lịch sử nhiều phiên bản.
Không chọn full_snapshot cho dữ liệu chỉ chứa phần tăng thêm không đầy đủ.

## Kiểm tra trên Airflow

- DAGs: lọc tag silver/gold; từng bảng/model có một DAG riêng.
- Datasets: xem đường nối producer/consumer và thời điểm cập nhật.
- Bronze: task wait_for_complete phải success (không chỉ trigger_airbyte).
- Silver: xem task run_silver_<bảng> và log dbt.
- Gold: xem dimensions, rồi fact, cuối cùng agg_daily_sales.
- Nếu Bronze thành công trước khi triển khai Dataset thì sự kiện không được phát lại.
  Cần một sync Bronze thành công mới, hoặc dùng luồng khởi tạo thủ công ở trên.
- Nếu một nhánh Silver lỗi/chưa chạy, Gold sẽ tiếp tục chờ đủ đầu vào.
- Không bật bronze_ticket_all và năm DAG Bronze riêng cùng lúc cho cùng đợt sync.

## Giới hạn cần hiểu

Danh sách schedule=[A, B] nghĩa là cả A và B có cập nhật kể từ lượt chạy consumer
trước đó, KHÔNG đảm bảo cùng ngày hoặc cùng batch_id. Đây là luồng daily đơn giản,
không phải cơ chế đồng bộ snapshot toàn bộ database.
Không sync/rebuild thủ công chồng lên pipeline đang xử lý nếu cần báo cáo nhất quán.
Khóa trong runner chỉ chống ghi đồng thời cùng model; không khóa toàn bộ các tầng.
Gold cập nhật từng model, không xuất bản nguyên tầng atomically:
chỉ refresh Power BI sau khi agg_daily_sales thành công.

Data tests mặc định tắt (run_tests=false); không dùng dbt build.
Kiểm tra triển khai chỉ parse/import DAG và cấu hình, không chạy sync/dbt/data tests.

DAG gold_ticket_sales cũ được thay bằng các DAG Gold riêng và gold_ticket_all.
Lịch sử chạy cũ có thể vẫn hiển thị trong metadata Airflow; không xóa lịch sử đó.

Tài liệu Airflow 2.10.5:
https://airflow.apache.org/docs/apache-airflow/2.10.5/authoring-and-scheduling/datasets.html
