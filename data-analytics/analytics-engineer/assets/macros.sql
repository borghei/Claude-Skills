-- 1. Customize Schema Names based on Environments
-- By default, dbt appends custom schemas like `dev_username_custom`.
-- This enforces that Production builds strictly into their raw defined folders.
{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- set default_schema = target.schema -%}
    
    {%- if target.name == 'prod' -%}
        {%- if custom_schema_name is none -%}
            {{ default_schema }}
        {%- else -%}
            {{ custom_schema_name | trim }}
        {%- endif -%}
    {%- else -%}
        {%- if custom_schema_name is none -%}
            {{ default_schema }}
        {%- else -%}
            {{ default_schema }}_{{ custom_schema_name | trim }}
        {%- endif -%}
    {%- endif -%}
{%- endmacro %}

-- 2. Incremental Lookback Filter
-- Enforces a rolling window update to avoid massive full-table scans.
{% macro get_incremental_filter(column_name, default_lookback=3) %}
    {% if is_incremental() %}
        -- Grab from global variables or fallback to default
        {% set lookback = var('incremental_lookback_days', default_lookback) %}
        
        WHERE {{ column_name }} >= (
            SELECT DATEADD(day, -{{ lookback }}, MAX({{ column_name }}))
            FROM {{ this }}
        )
    {% endif %}
{% endmacro %}

-- 3. Dynamic Field Casting
{% macro cents_to_dollars(column_name, decimal_places=2) %}
    ROUND( CAST({{ column_name }} AS FLOAT) / 100.0, {{ decimal_places }} )
{% endmacro %}
