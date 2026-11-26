{{ config(
    materialized='incremental',
    incremental_strategy='merge',
    unique_key='order_item_id',
    on_schema_change='fail',
    post_hook="delete from {{ this }} where _is_deleted",
    indexes=[
        {'columns': ['order_item_id'], 'unique': true},
        {'columns': ['order_id']},
        {'columns': ['date_key', 'event_id']}
    ]
) }}

{% set business_fields = ["order_item_id","order_id","event_id","ticket_type_id","date_key","channel_key","status_key","quantity","gross_amount","discount_amount","net_amount","sold_quantity","sales_amount"] %}

-- Re-evaluate every active order item: an old order changing status must update its fact rows.
-- Payments are not joined here because payment attempts would multiply ticket rows.
with business_rows as (
    select i.order_item_id, i.order_id, i.event_id, i.ticket_type_id,
           to_char(o.ordered_at, 'YYYYMMDD')::bigint as date_key,
           c.channel_key, s.status_key, i.quantity,
           (i.quantity * i.unit_price)::numeric(18,0) as gross_amount,
           i.discount_amount, i.line_amount as net_amount,
           case when o.order_status = 'PAID' then i.quantity else 0 end::bigint as sold_quantity,
           case when o.order_status = 'PAID' then i.line_amount else 0 end::numeric(18,0) as sales_amount
    from {{ ref('silver_order_items') }} i
    join {{ ref('silver_orders') }} o on i.order_id = o.order_id and not o._is_deleted
    left join {{ ref('dim_channel') }} c on o.sales_channel = c.sales_channel
    left join {{ ref('dim_status') }} s on o.order_status = s.order_status
    where not i._is_deleted
),
candidate as (
    select business_rows.*,
           md5(jsonb_build_array(order_item_id, order_id, event_id, ticket_type_id, date_key, channel_key, status_key, quantity, gross_amount, discount_amount, net_amount, sold_quantity, sales_amount)::text) as _record_hash
    from business_rows
)
{{ incremental_changes('candidate', 'order_item_id', business_fields, true) }}
