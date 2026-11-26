-- Source: bronze.events (Airbyte Full Refresh Overwrite).
-- Target: silver.events; grain: one current row per event_id.
-- Incremental MERGE: insert new keys, update changed hashes, retain soft deletions.
-- Run only after a complete successful Airbyte sync; no timestamp watermark.

{{ config(
    materialized='incremental',
    incremental_strategy='merge',
    alias='events',
    unique_key='event_id',
    indexes=[
        {'columns': ['event_id'], 'unique': true},
        {'columns': ['updated_at']}
    ]
) }}

{% set business_fields = [
    'event_id',
    'event_code',
    'event_name',
    'category',
    'organizer_name',
    'venue_name',
    'province',
    'capacity',
    'starts_at',
    'ends_at',
    'sales_start_at',
    'sales_end_at',
    'event_status',
    'created_at',
    'updated_at'
] %}

with source_data as (
    select
        cast("event_id" as bigint) as "event_id",
        nullif(btrim(cast("event_code" as text)), '') as "event_code",
        nullif(btrim(cast("event_name" as text)), '') as "event_name",
        nullif(btrim(cast("category" as text)), '') as "category",
        nullif(btrim(cast("organizer_name" as text)), '') as "organizer_name",
        nullif(btrim(cast("venue_name" as text)), '') as "venue_name",
        nullif(btrim(cast("province" as text)), '') as "province",
        cast("capacity" as bigint) as "capacity",
        cast("starts_at" as timestamp without time zone) as "starts_at",
        cast("ends_at" as timestamp without time zone) as "ends_at",
        cast("sales_start_at" as timestamp without time zone) as "sales_start_at",
        cast("sales_end_at" as timestamp without time zone) as "sales_end_at",
        upper(nullif(btrim(cast("event_status" as text)), '')) as "event_status",
        cast("created_at" as timestamp without time zone) as "created_at",
        cast("updated_at" as timestamp without time zone) as "updated_at",
        _airbyte_extracted_at::timestamptz as _source_extracted_at,
        _airbyte_raw_id::text as _source_raw_id
    from {{ source('bronze', 'events') }}
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
            partition by event_id
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
        event_id,
        event_code,
        event_name,
        category,
        organizer_name,
        venue_name,
        province,
        capacity,
        starts_at,
        ends_at,
        sales_start_at,
        sales_end_at,
        event_status,
        created_at,
        updated_at,
        _record_hash
    from ranked
    where version_rank = 1
),

final as (
    {{ incremental_changes(
        'deduplicated',
        'event_id',
        business_fields,
        detect_deletes=true
    ) }}
)

select * from final
