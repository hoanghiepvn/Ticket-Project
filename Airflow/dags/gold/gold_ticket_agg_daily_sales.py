from datetime import timedelta

from airflow import DAG
from airflow.datasets import Dataset

from ticketing.dbt_bash import DbtBashOperator
from ticketing.dbt_defaults import dag_options

INPUTS = [
    Dataset("transform_gold_dimensions_to_gold_fact_ticket_sales"),
]
OUTPUTS = [
    Dataset("transform_gold_fact_to_gold_agg_daily_sales"),
]


with DAG(
    dag_id="gold_ticket_agg_daily_sales",
    schedule=INPUTS,
    tags=["ticket", "gold", "dataset"],
    doc_md="SQL: `Dbt/Dbt-Postgres/models/gold/marts/agg_daily_sales.sql`",
    **dag_options(),
) as dag:
   
    run_model = DbtBashOperator(
        task_id="run_agg_daily_sales",
        stage="gold",
        bash_command="dbt run --select path:models/gold/marts/agg_daily_sales.sql",
        outlets=OUTPUTS,
        retries=1,
        retry_delay=timedelta(minutes=1),
    )
