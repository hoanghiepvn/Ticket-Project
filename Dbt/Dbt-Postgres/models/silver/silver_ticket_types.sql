-- Source: bronze.ticket_types (Airbyte Full Refresh Overwrite).
-- Target: silver.ticket_types; grain: one current row per ticket_type_id.
-- Incremental MERGE: insert new keys, update changed hashes, retain soft deletions.
-- Run only after a complete successful Airbyte sync; no timestamp watermark.

{{ config(
    materialized='incremental',
    incremental_strategy='merge',
    alias='ticket_types',
    unique_key='ticket_type_id',
    indexes=[
        {'columns': ['ticket_type_id'], 'unique': true},
        {'columns': ['updated_at']}
    ]
) }}

{% set business_fields = [
    'ticket_type_id',
    'event_id',
    'ticket_type_code',
    'ticket_type_name',
    'list_price',
    'sale_quota',
    'created_at',
    'updated_at'
] %}

with source_data as (
    select
        cast("ticket_type_id" as bigint) as "ticket_type_id",
        cast("event_id" as bigint) as "event_id",
        nullif(btrim(cast("ticket_type_code" as text)), '') as "ticket_type_code",
        nullif(btrim(cast("ticket_type_name" as text)), '') as "ticket_type_name",
        cast("list_price" as numeric(18,0)) as "list_price",
        cast("sale_quota" as bigint) as "sale_quota",
        cast("created_at" as timestamp without time zone) as "created_at",
        cast("updated_at" as timestamp without time zone) as "updated_at",
        _airbyte_extracted_at::timestamptz as _source_extracted_at,
        _airbyte_raw_id::text as _source_raw_id
    from {{ source('bronze', 'ticket_types') }}
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
            partition by ticket_type_id
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
        ticket_type_id,
        event_id,
        ticket_type_code,
        ticket_type_name,
        list_price,
        sale_quota,
        created_at,
        updated_at,
        _record_hash
    from ranked
    where version_rank = 1
),

final as (
    {{ incremental_changes(
        'deduplicated',
        'ticket_type_id',
        business_fields,
        detect_deletes=true
    ) }}
)

select * from final
