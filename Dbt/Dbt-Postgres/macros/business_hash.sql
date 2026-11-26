{% macro business_hash(fields) -%}
md5(
    jsonb_build_array(
        {% for field in fields %}
        {{ adapter.quote(field) }}{% if not loop.last %},{% endif %}
        {% endfor %}
    )::text
)
{%- endmacro %}
