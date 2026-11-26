{{ config(
    materialized='table',
    indexes=[{'columns': ['event_id'], 'unique': true}]
) }}

select event_id, event_code, event_name, category, organizer_name,
       venue_name, province, capacity, starts_at
from {{ ref('silver_events') }}
where not _is_deleted
