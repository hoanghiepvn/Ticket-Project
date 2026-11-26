{{ config(
    materialized='table',
    indexes=[{'columns': ['date_key'], 'unique': true}]
) }}

with bounds as (
    select min(ordered_at::date) as first_date, max(ordered_at::date) as last_date
    from {{ ref('silver_orders') }} where not _is_deleted
),
calendar as (
    select generate_series(first_date::timestamp, last_date::timestamp, interval '1 day')::date as full_date
    from bounds
)
select to_char(full_date, 'YYYYMMDD')::bigint as date_key, full_date,
       extract(year from full_date)::bigint as "year",
       extract(month from full_date)::bigint as "month",
       extract(day from full_date)::bigint as "day",
       extract(isodow from full_date)::bigint as weekday,
       case when extract(isodow from full_date) in (6,7) then 1 else 0 end::bigint as is_weekend
from calendar
