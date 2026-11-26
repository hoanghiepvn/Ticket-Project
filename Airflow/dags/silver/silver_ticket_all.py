"""SILVER: manual full-layer rebuild."""
from datetime import timedelta

from airflow import DAG
from airflow.datasets import Dataset

from ticketing.dbt_bash import DbtBashOperator
from ticketing.dbt_defaults import dag_options

# 1. Dataset đầu vào / đầu ra (URI phải khớp với DAG liên quan).
OUTPUTS = [
    Dataset("transform_bronze_to_silver_ticket_all"),
    Dataset("transform_bronze_to_silver_ticket_events"),
    Dataset("transform_bronze_to_silver_ticket_ticket_types"),
    Dataset("transform_bronze_to_silver_ticket_orders"),
    Dataset("transform_bronze_to_silver_ticket_order_items"),
    Dataset("transform_bronze_to_silver_ticket_payments"),
]

# 2. Lịch chạy giữ ngay trong file này; None = chỉ chạy thủ công.
with DAG(
    dag_id="silver_ticket_all",
    schedule=None,
    tags=["ticket", "silver", "manual"],
    doc_md="SQL: `Dbt/Dbt-Postgres/models/silver/`",
    **dag_options(),
) as dag:
    # 3. Lệnh dbt: chọn trực tiếp file SQL; đường dẫn tính từ Dbt/Dbt-Postgres.
    run_model = DbtBashOperator(
        task_id="run_all_silver",
        stage="silver",
        bash_command="dbt run --select tag:silver",
        outlets=OUTPUTS,
        retries=0,
        retry_delay=timedelta(minutes=1),
    )
