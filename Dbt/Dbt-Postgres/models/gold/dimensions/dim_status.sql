{{ config(
    materialized='table',
    indexes=[{'columns': ['status_key'], 'unique': true}]
) }}

select 1::bigint as status_key, 'PAID'::text as order_status
union all select 2::bigint, 'EXPIRED'::text
union all select 3::bigint, 'CANCELLED'::text
union all select 4::bigint, 'PENDING'::text
