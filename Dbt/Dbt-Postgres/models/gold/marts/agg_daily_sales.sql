{{ config(
    materialized='table',
    indexes=[{'columns': ['date_key', 'event_id', 'channel_key'], 'unique': true}]
) }}

select date_key, event_id, channel_key,
       sum(sales_amount)::numeric(18,0) as sales_amount,
       sum(sold_quantity)::bigint as sold_quantity,
       count(distinct case when status_key = 1 then order_id end)::bigint as paid_orders,
       count(distinct order_id)::bigint as total_orders
from {{ ref('fact_ticket_sales') }}
where not _is_deleted
group by date_key, event_id, channel_key
