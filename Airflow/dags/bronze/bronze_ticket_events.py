"""Một file = một DAG Airbyte. Chỉnh tên và lịch ngay trong file này."""
from datetime import timedelta

import pendulum
from airflow import DAG
from airflow.datasets import Dataset
from airflow.operators.python import PythonOperator

from ticketing.sensors import AirbyteJobSensor
from ticketing_workflows.bronze.airbyte_sync import trigger_sync
from ticketing_workflows.bronze.config import CONNECTIONS

CONNECTION_ID = CONNECTIONS["events"]

# Airflow publishes these only after wait_for_complete succeeds.
OUTPUT_DATASETS = [
    Dataset("transform_source_to_bronze_ticket_events"),
]

with DAG(
    dag_id="bronze_ticket_events",
    description="bronze_ticket_events",
    schedule="00 1 * * *",
    start_date=pendulum.datetime(2026, 9, 24, tz="Asia/Ho_Chi_Minh"),
    catchup=False,
    max_active_runs=1,
    max_active_tasks=2,
    is_paused_upon_creation=True,
    dagrun_timeout=timedelta(hours=6),
    default_args={"owner": "ticket", "retries": 0},
    tags=["bronze", "airbyte", "daily", "event", "events"],
) as dag:
    
    # 1. Trigger Airbyte. Không tự retry POST để tránh tạo job trùng.
    run_airbyte = PythonOperator(
        task_id="trigger_airbyte",
        python_callable=trigger_sync,
        op_kwargs={"connection_id": CONNECTION_ID},
        retries=0,
        execution_timeout=timedelta(minutes=2),
    )

    # 2. Chờ đúng Job ID trả về; nhả worker giữa các lần kiểm tra.
    wait_airbyte = AirbyteJobSensor(
        task_id="wait_for_complete",
        job_id=run_airbyte.output,
        outlets=OUTPUT_DATASETS,
        mode="reschedule",
        poke_interval=30,
        timeout=4 * 60 * 60,
        retries=1,
        execution_timeout=timedelta(minutes=2),
    )

    run_airbyte >> wait_airbyte
