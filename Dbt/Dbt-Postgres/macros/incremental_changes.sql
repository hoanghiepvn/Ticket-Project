{% macro incremental_changes(candidate, primary_key, fields, detect_deletes=true) %}
{% if detect_deletes and var('bronze_mode', 'full_snapshot') != 'full_snapshot' %}
    {{ exceptions.raise_compiler_error(
        'This project requires a complete Bronze snapshot (Airbyte Full Refresh Overwrite).'
    ) }}
{% endif %}
{# Compare every current key, not MAX(updated_at): late updates cannot fall behind a global watermark.
   This saves target writes, but still scans the current source. It is NOT CDC. #}
select
    {% for field in fields %}
    c.{{ adapter.quote(field) }},
    {% endfor %}
    c._record_hash,
    false as _is_deleted,
    current_timestamp as _loaded_at
from {{ candidate }} c
{% if is_incremental() %}
left join {{ this }} t on c.{{ primary_key }} = t.{{ primary_key }}
where t.{{ primary_key }} is null
   or c._record_hash is distinct from t._record_hash
   or t._is_deleted
{% if detect_deletes %}
union all
select
    {% for field in fields %}
    t.{{ adapter.quote(field) }},
    {% endfor %}
    t._record_hash,
    true as _is_deleted,
    current_timestamp as _loaded_at
from {{ this }} t
where not t._is_deleted
  and not exists (select 1 from {{ candidate }} c where c.{{ primary_key }} = t.{{ primary_key }})
{% endif %}
{% endif %}
{% endmacro %}
