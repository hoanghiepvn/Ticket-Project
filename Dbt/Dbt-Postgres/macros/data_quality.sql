{% test expression_is_true(model, expression) %}
select * from {{ model }} where not ({{ expression }}) or ({{ expression }}) is null
{% endtest %}

{% test unique_combination(model, combination_of_columns) %}
select {{ combination_of_columns | join(', ') }}, count(*) as duplicate_count
from {{ model }}
group by {{ combination_of_columns | join(', ') }}
having count(*) > 1
{% endtest %}
