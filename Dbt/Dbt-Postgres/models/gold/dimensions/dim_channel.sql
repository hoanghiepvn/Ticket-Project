{{ config(
    materialized='table',
    indexes=[{'columns': ['channel_key'], 'unique': true}]
) }}

select 1::bigint as channel_key, 'WEB'::text as sales_channel
union all select 2::bigint, 'APP'::text
