"""Dataset identifiers contain no credentials and do not create database tables."""
from airflow.datasets import Dataset

TABLES = ("events", "ticket_types", "orders", "order_items", "payments")
GOLD_MODELS = (
    "dim_event", "dim_ticket_type", "dim_channel", "dim_status", "dim_date",
    "fact_ticket_sales", "agg_daily_sales",
)

# Logical identifiers only; Airflow does not poll PostgreSQL through these URIs.
BRONZE = {name: Dataset(f"transform_source_to_bronze_ticket_{name}") for name in TABLES}
SILVER = {name: Dataset(f"transform_bronze_to_silver_ticket_{name}") for name in TABLES}
GOLD = {
    name: Dataset(
        "transform_gold_dimensions_to_gold_fact_ticket_sales" if name == "fact_ticket_sales"
        else "transform_gold_fact_to_gold_agg_daily_sales" if name == "agg_daily_sales"
        else f"transform_silver_to_gold_ticket_{name}"
    )
    for name in GOLD_MODELS
}

# Map actual dag_id values, not filenames (two protected filenames differ from IDs).
BRONZE_DAG_TABLES = {
    "bronze_ticket_all": TABLES,
    "bronze_ticket_events": ("events",),
    "bronze_ticket_ticket_types": ("ticket_types",),
    "bronze_ticket_orders": ("orders",),
    "bronze_ticket_order_items": ("order_items",),
    "bronze_ticket_payments": ("payments",),
}
