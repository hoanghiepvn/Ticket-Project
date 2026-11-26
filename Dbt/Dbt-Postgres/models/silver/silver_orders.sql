-- Source: bronze.orders (Airbyte Full Refresh Overwrite).
-- Target: silver.orders; grain: one current row per order_id.
-- Incremental MERGE: insert new keys, update changed hashes, retain soft deletions.
-- Run only after a complete successful Airbyte sync; no timestamp watermark.

{{ config(
    materialized='incremental',
    incremental_strategy='merge',
    alias='orders',
    unique_key='order_id',
    indexes=[
        {'columns': ['order_id'], 'unique': true},
        {'columns': ['updated_at']}
    ]
) }}

{% set business_fields = [
    'order_id',
    'event_id',
    'order_code',
    'ordered_at',
    'expires_at',
    'sales_channel',
    'order_status',
    'subtotal_amount',
    'discount_amount',
    'total_amount',
    'currency',
    'created_at',
    'updated_at'
] %}

with source_data as (
    select
        cast("order_id" as bigint) as "order_id",
        cast("event_id" as bigint) as "event_id",
        nullif(btrim(cast("order_code" as text)), '') as "order_code",
        cast("ordered_at" as timestamp without time zone) as "ordered_at",
        cast("expires_at" as timestamp without time zone) as "expires_at",
        upper(nullif(btrim(cast("sales_channel" as text)), '')) as "sales_channel",
        upper(nullif(btrim(cast("order_status" as text)), '')) as "order_status",
        cast("subtotal_amount" as numeric(18,0)) as "subtotal_amount",
        cast("discount_amount" as numeric(18,0)) as "discount_amount",
        cast("total_amount" as numeric(18,0)) as "total_amount",
        upper(nullif(btrim(cast("currency" as text)), '')) as "currency",
        cast("created_at" as timestamp without time zone) as "created_at",
        cast("updated_at" as timestamp without time zone) as "updated_at",
        _airbyte_extracted_at::timestamptz as _source_extracted_at,
        _airbyte_raw_id::text as _source_raw_id
    from {{ source('bronze', 'orders') }}
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
            partition by order_id
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
        order_id,
        event_id,
        order_code,
        ordered_at,
        expires_at,
        sales_channel,
        order_status,
        subtotal_amount,
        discount_amount,
        total_amount,
        currency,
        created_at,
        updated_at,
        _record_hash
    from ranked
    where version_rank = 1
),

final as (
    {{ incremental_changes(
        'deduplicated',
        'order_id',
        business_fields,
        detect_deletes=true
    ) }}
)

select * from final
