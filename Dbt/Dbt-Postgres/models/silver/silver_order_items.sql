-- Source: bronze.order_items (Airbyte Full Refresh Overwrite).
-- Target: silver.order_items; grain: one current row per order_item_id.
-- Incremental MERGE: insert new keys, update changed hashes, retain soft deletions.
-- Run only after a complete successful Airbyte sync; no timestamp watermark.

{{ config(
    materialized='incremental',
    incremental_strategy='merge',
    alias='order_items',
    unique_key='order_item_id',
    indexes=[
        {'columns': ['order_item_id'], 'unique': true},
        {'columns': ['updated_at']}
    ]
) }}

{% set business_fields = [
    'order_item_id',
    'order_id',
    'event_id',
    'ticket_type_id',
    'quantity',
    'unit_price',
    'discount_amount',
    'line_amount',
    'created_at',
    'updated_at'
] %}

with source_data as (
    select
        cast("order_item_id" as bigint) as "order_item_id",
        cast("order_id" as bigint) as "order_id",
        cast("event_id" as bigint) as "event_id",
        cast("ticket_type_id" as bigint) as "ticket_type_id",
        cast("quantity" as bigint) as "quantity",
        cast("unit_price" as numeric(18,0)) as "unit_price",
        cast("discount_amount" as numeric(18,0)) as "discount_amount",
        cast("line_amount" as numeric(18,0)) as "line_amount",
        cast("created_at" as timestamp without time zone) as "created_at",
        cast("updated_at" as timestamp without time zone) as "updated_at",
        _airbyte_extracted_at::timestamptz as _source_extracted_at,
        _airbyte_raw_id::text as _source_raw_id
    from {{ source('bronze', 'order_items') }}
),

hashed as (
    select
        source_data.*,
        {{ business_hash(business_fields) }} as _record_hash
    from source_data
),

ranked as (
    select
        *,
        row_number() over (
            partition by order_item_id
            order by
                updated_at desc nulls last,
                _source_extracted_at desc nulls last,
                _source_raw_id desc nulls last,
                _record_hash desc
        ) as version_rank
    from hashed
),

deduplicated as (
    select
        order_item_id,
        order_id,
        event_id,
        ticket_type_id,
        quantity,
        unit_price,
        discount_amount,
        line_amount,
        created_at,
        updated_at,
        _record_hash
    from ranked
    where version_rank = 1
),

final as (
    {{ incremental_changes(
        'deduplicated',
        'order_item_id',
        business_fields,
        detect_deletes=true
    ) }}
)

select * from final
