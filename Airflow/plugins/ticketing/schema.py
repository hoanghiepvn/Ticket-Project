"""Business columns shared by snapshot ingestion and atomic publication."""
FIELDS = {
    "events": [
        "event_id",
        "event_code",
        "event_name",
        "category",
        "organizer_name",
        "venue_name",
        "province",
        "capacity",
        "starts_at",
        "ends_at",
        "sales_start_at",
        "sales_end_at",
        "event_status",
        "created_at",
        "updated_at"
    ],
    "ticket_types": [
        "ticket_type_id",
        "event_id",
        "ticket_type_code",
        "ticket_type_name",
        "list_price",
        "sale_quota",
        "created_at",
        "updated_at"
    ],
    "orders": [
        "order_id",
        "event_id",
        "order_code",
        "ordered_at",
        "expires_at",
        "sales_channel",
        "order_status",
        "subtotal_amount",
        "discount_amount",
        "total_amount",
        "currency",
        "created_at",
        "updated_at"
    ],
    "order_items": [
        "order_item_id",
        "order_id",
        "event_id",
        "ticket_type_id",
        "quantity",
        "unit_price",
        "discount_amount",
        "line_amount",
        "created_at",
        "updated_at"
    ],
    "payments": [
        "payment_id",
        "order_id",
        "merchant_transaction_id",
        "partner_transaction_id",
        "payment_partner",
        "payment_method",
        "payment_amount",
        "currency",
        "payment_status",
        "failure_reason",
        "initiated_at",
        "completed_at",
        "paid_at",
        "created_at",
        "updated_at"
    ]
}
KEYS = {
    "events": "event_id",
    "ticket_types": "ticket_type_id",
    "orders": "order_id",
    "order_items": "order_item_id",
    "payments": "payment_id"
}
GOLD = {
    "dim_event": [
        "event_id",
        "event_code",
        "event_name",
        "category",
        "organizer_name",
        "venue_name",
        "province",
        "capacity",
        "starts_at"
    ],
    "dim_ticket_type": [
        "ticket_type_id",
        "event_id",
        "ticket_type_code",
        "ticket_type_name",
        "list_price",
        "sale_quota"
    ],
    "dim_channel": [
        "channel_key",
        "sales_channel"
    ],
    "dim_status": [
        "status_key",
        "order_status"
    ],
    "dim_date": [
        "date_key",
        "full_date",
        "year",
        "month",
        "day",
        "weekday",
        "is_weekend"
    ],
    "fact_ticket_sales": [
        "order_item_id",
        "order_id",
        "event_id",
        "ticket_type_id",
        "date_key",
        "channel_key",
        "status_key",
        "quantity",
        "gross_amount",
        "discount_amount",
        "net_amount",
        "sold_quantity",
        "sales_amount"
    ],
    "agg_daily_sales": [
        "date_key",
        "event_id",
        "channel_key",
        "sales_amount",
        "sold_quantity",
        "paid_orders",
        "total_orders"
    ]
}

def require(condition, message):
    if not condition:
        raise RuntimeError(message)
