-- Source: bronze.payments (Airbyte Full Refresh Overwrite).
-- Target: silver.payments; grain: one current row per payment_id.
-- Incremental MERGE: insert new keys, update changed hashes, retain soft deletions.
-- Run only after a complete successful Airbyte sync; no timestamp watermark.

{{ config(
    materialized='incremental',
    incremental_strategy='merge',
    alias='payments',
    unique_key='payment_id',
    indexes=[
        {'columns': ['payment_id'], 'unique': true},
        {'columns': ['updated_at']}
    ]
) }}

{% set business_fields = [
    'payment_id',
    'order_id',
    'merchant_transaction_id',
    'partner_transaction_id',
    'payment_partner',
    'payment_method',
    'payment_amount',
    'currency',
    'payment_status',
    'failure_reason',
    'initiated_at',
    'completed_at',
    'paid_at',
    'created_at',
    'updated_at'
] %}

with source_data as (
    select
        cast("payment_id" as bigint) as "payment_id",
        cast("order_id" as bigint) as "order_id",
        nullif(btrim(cast("merchant_transaction_id" as text)), '') as "merchant_transaction_id",
        nullif(btrim(cast("partner_transaction_id" as text)), '') as "partner_transaction_id",
        upper(nullif(btrim(cast("payment_partner" as text)), '')) as "payment_partner",
        upper(nullif(btrim(cast("payment_method" as text)), '')) as "payment_method",
        cast("payment_amount" as numeric(18,0)) as "payment_amount",
        upper(nullif(btrim(cast("currency" as text)), '')) as "currency",
        upper(nullif(btrim(cast("payment_status" as text)), '')) as "payment_status",
        nullif(btrim(cast("failure_reason" as text)), '') as "failure_reason",
        cast("initiated_at" as timestamp without time zone) as "initiated_at",
        cast("completed_at" as timestamp without time zone) as "completed_at",
        cast("paid_at" as timestamp without time zone) as "paid_at",
        cast("created_at" as timestamp without time zone) as "created_at",
        cast("updated_at" as timestamp without time zone) as "updated_at",
        _airbyte_extracted_at::timestamptz as _source_extracted_at,
        _airbyte_raw_id::text as _source_raw_id
    from {{ source('bronze', 'payments') }}
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
            partition by payment_id
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
        payment_id,
        order_id,
        merchant_transaction_id,
        partner_transaction_id,
        payment_partner,
        payment_method,
        payment_amount,
        currency,
        payment_status,
        failure_reason,
        initiated_at,
        completed_at,
        paid_at,
        created_at,
        updated_at,
        _record_hash
    from ranked
    where version_rank = 1
),

final as (
    {{ incremental_changes(
        'deduplicated',
        'payment_id',
        business_fields,
        detect_deletes=true
    ) }}
)

select * from final
