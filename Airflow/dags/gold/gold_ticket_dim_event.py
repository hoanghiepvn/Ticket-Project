"""GOLD: dim_event."""
from datetime import timedelta

from airflow import DAG
from airflow.datasets import Dataset

from ticketing.dbt_bash import DbtBashOperator
from ticketing.dbt_defaults import dag_options

# 1. Dataset đầu vào / đầu ra (URI phải khớp với DAG liên quan).
INPUTS = [
    Dataset("transform_bronze_to_silver_ticket_events"),
    Dataset("transform_bronze_to_silver_ticket_ticket_types"),
    Dataset("transform_bronze_to_silver_ticket_orders"),
    Dataset("transform_bronze_to_silver_ticket_order_items"),
    Dataset("transform_bronze_to_silver_ticket_payments"),
]
OUTPUTS = [
    Dataset("transform_silver_to_gold_ticket_dim_event"),
]

# 2. Lịch chạy giữ ngay trong file này; None = chỉ chạy thủ công.
with DAG(
    dag_id="gold_ticket_dim_event",
    schedule=INPUTS,
    tags=["ticket", "gold", "dataset"],
    doc_md="SQL: `Dbt/Dbt-Postgres/models/gold/dimensions/dim_event.sql`",
    **dag_options(),
) as dag:
    # 3. Lệnh dbt: chọn trực tiếp file SQL; đường dẫn tính từ Dbt/Dbt-Postgres.
    run_model = DbtBashOperator(
        task_id="run_dim_event",
        stage="gold",
        bash_command="dbt run --select path:models/gold/dimensions/dim_event.sql",
        outlets=OUTPUTS,
        retries=1,
        retry_delay=timedelta(minutes=1),
    )
