"""GOLD: manual full-layer rebuild."""
from datetime import timedelta

from airflow import DAG
from airflow.datasets import Dataset

from ticketing.dbt_bash import DbtBashOperator
from ticketing.dbt_defaults import dag_options

# 1. Dataset đầu vào / đầu ra (URI phải khớp với DAG liên quan).
OUTPUTS = [
    Dataset("transform_silver_to_gold_ticket_dim_event"),
    Dataset("transform_silver_to_gold_ticket_dim_ticket_type"),
    Dataset("transform_silver_to_gold_ticket_dim_channel"),
    Dataset("transform_silver_to_gold_ticket_dim_status"),
    Dataset("transform_silver_to_gold_ticket_dim_date"),
    Dataset("transform_gold_dimensions_to_gold_fact_ticket_sales"),
    Dataset("transform_gold_fact_to_gold_agg_daily_sales"),
]

# 2. Lịch chạy giữ ngay trong file này; None = chỉ chạy thủ công.
with DAG(
    dag_id="gold_ticket_all",
    schedule=None,
    tags=["ticket", "gold", "manual"],
    doc_md="SQL: `Dbt/Dbt-Postgres/models/gold/`",
    **dag_options(),
) as dag:
    # 3. Lệnh dbt: chọn trực tiếp file SQL; đường dẫn tính từ Dbt/Dbt-Postgres.
    run_model = DbtBashOperator(
        task_id="run_all_gold",
        stage="gold",
        bash_command="dbt run --select tag:gold",
        outlets=OUTPUTS,
        retries=0,
        retry_delay=timedelta(minutes=1),
    )
