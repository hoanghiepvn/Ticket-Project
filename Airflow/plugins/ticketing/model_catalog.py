"""Explicit model inventory for per-model Airflow tasks and CLI validation."""
SILVER_MODELS = ('silver_events','silver_ticket_types','silver_orders','silver_order_items','silver_payments')
DIMENSION_MODELS = ('dim_event','dim_ticket_type','dim_channel','dim_status','dim_date')
MODEL_GROUPS = {
    'silver': SILVER_MODELS,
    'gold': DIMENSION_MODELS + ('fact_ticket_sales','agg_daily_sales'),
}
