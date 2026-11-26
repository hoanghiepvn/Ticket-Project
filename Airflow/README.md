# Airflow: DAG chia theo tầng

```text
Airflow/
├── dags/
│   ├── bronze/   6 DAG Bronze + config.py + airbyte_sync.py
│   ├── silver/   5 DAG từng bảng + silver_ticket_all.py (manual)
│   ├── gold/     7 DAG từng model + gold_ticket_all.py (manual)
│   ├── __init__.py
│   └── .airflowignore
└── plugins/ticketing/  API client, sensor, Dataset và dbt runner dùng chung
```

- Sửa dag_id, schedule, params ngay trong file DAG tương ứng.
- Bronze giữ nguyên nội dung người dùng, chỉ chuyển vị trí.
- Bronze/config.py và airbyte_sync.py vẫn ở đây để giữ nguyên import trong Bronze.
- Hai tên file bronze_ticket_order_payments.py và bronze_ticket_order_ticket_types.py
  vẫn giữ theo người dùng; dag_id bên trong lần lượt là bronze_ticket_payments và bronze_ticket_ticket_types.
- .airflowignore chỉ bỏ qua cache và module hỗ trợ, KHÔNG bỏ qua thư mục tầng.
- Giữ hai mount dags và ticketing_workflows trong compose.yaml để import không bị trùng tên module.
- Không thay đổi dag_id, lịch chạy, Dataset hoặc trạng thái pause khi sắp xếp thư mục.

## Luồng chạy

Bronze thành công → Silver tương ứng → đủ 5 Silver → 5 dimension Gold
→ fact_ticket_sales → agg_daily_sales → refresh Power BI.

Silver/Gold tự động theo Dataset, không cần thêm cron.
Hai DAG *_ticket_all có schedule=None, dùng khởi tạo/rebuild thủ công.
Không chạy chúng chồng với các DAG tự động.
Hướng dẫn khởi tạo và full_refresh: ../Documentation/AIRFLOW_DATASET_WORKFLOW.md.

UI: http://localhost:8080
Module cũ silver/gold/common đã bỏ; bản phục hồi:
../Runtime/legacy-dag-modules-20260929.zip.
Không giải nén bản cũ trực tiếp vào dags khi đang vận hành.

