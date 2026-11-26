{{ config(
    materialized='table',
    indexes=[{'columns': ['ticket_type_id'], 'unique': true}]
) }}

select ticket_type_id, event_id, ticket_type_code, ticket_type_name, list_price, sale_quota
from {{ ref('silver_ticket_types') }}
where not _is_deleted
