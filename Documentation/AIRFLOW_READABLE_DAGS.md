# Sửa DAG Silver/Gold

Mỗi file chia ba phần: INPUTS/OUTPUTS → with DAG → lệnh dbt run.
Không sinh DAG qua factory và không giấu lịch chạy trong file cấu hình.

## Những chỗ thường sửa

- INPUTS: Dataset cần chờ. Danh sách nghĩa là chờ đủ các Dataset cập nhật.
- OUTPUTS: Dataset phát ra khi task thành công.
- dag_id, schedule, tags: định danh và lịch chạy ngay trong file.
- bash_command: ví dụ dbt run --select path:models/silver/silver_events.sql.
  Đường dẫn tính từ Ticket_Project/Dbt/Dbt-Postgres, không từ thư mục DAG.
- DAG *_all dùng --select tag:silver hoặc tag:gold, chỉ chạy thủ công.

Selector trong câu lệnh là nguồn duy nhất xác định model; không còn phải sửa
đồng thời DBT_MODEL và DBT_MODEL_FILES.

## Phần dùng chung

- Airflow/plugins/ticketing/dbt_defaults.py: ngày bắt đầu, timeout, params,
  catchup=False, mặc định paused và giới hạn một lượt chạy.
- Airflow/plugins/ticketing/dbt_bash.py: DbtBashOperator kế thừa BashOperator.
  Chuẩn bị project/profiles và artifacts riêng; ghi đầy đủ lệnh thực thi vào log.
  Chỉ hỗ trợ dbt run --select path:models/<tầng>/...sql hoặc tag:<tầng>.
- Airflow/plugins/ticketing/dataset_dbt.py: giữ khóa ghi cùng model và kiểm tra
  layout incremental. Không cần chỉnh file này khi chỉ đổi SQL của một DAG.

Trong UI, xem Code để đọc lệnh ngắn; Logs để đọc lệnh đầy đủ và lỗi dbt.
full_refresh chỉnh khi Trigger DAG. Artifacts lưu tại Runtime/data/dbt_runs.
Không chạy test mặc định. Dataset URI và thứ tự Bronze → Silver → Gold giữ nguyên.
Các DAG mới vẫn có trạng thái pause hiện tại, không tự bật sau chỉnh code.

## Cơ sở thiết kế

Đây là lựa chọn cho project này, không phải một chuẩn duy nhất áp dụng mọi hệ thống.
Airflow khuyến nghị tái sử dụng cấu hình lặp lại và tránh I/O ở lúc parse DAG:
https://airflow.apache.org/docs/apache-airflow/2.10.5/best-practices.html

dbt hỗ trợ selector path để chọn model trực tiếp theo đường dẫn:
https://docs.getdbt.com/reference/node-selection/methods

Không nâng phiên bản Airflow, không thêm framework hoặc dependency mới.
