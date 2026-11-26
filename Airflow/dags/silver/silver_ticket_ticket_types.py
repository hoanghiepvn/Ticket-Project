"""SILVER: silver_ticket_types."""
from datetime import timedelta

from airflow import DAG
from airflow.datasets import Dataset

from ticketing.dbt_bash import DbtBashOperator
from ticketing.dbt_defaults import dag_options

# 1. Dataset đầu vào / đầu ra (URI phải khớp với DAG liên quan).
INPUTS = [
    Dataset("transform_source_to_bronze_ticket_ticket_types"),
]
OUTPUTS = [
    Dataset("transform_bronze_to_silver_ticket_ticket_types"),
]

# 2. Lịch chạy giữ ngay trong file này; None = chỉ chạy thủ công.
with DAG(
    dag_id="silver_ticket_ticket_types",
    schedule=INPUTS,
    tags=["ticket", "silver", "dataset"],
    doc_md="SQL: `Dbt/Dbt-Postgres/models/silver/silver_ticket_types.sql`",
    **dag_options(),
) as dag:
    # 3. Lệnh dbt: chọn trực tiếp file SQL; đường dẫn tính từ Dbt/Dbt-Postgres.
    run_model = DbtBashOperator(
        task_id="run_silver_ticket_types",
        stage="silver",
        bash_command="dbt run --select path:models/silver/silver_ticket_types.sql",
        outlets=OUTPUTS,
        retries=1,
        retry_delay=timedelta(minutes=1),
    )
