{{
    config(
        materialized='incremental',
        unique_key='indicator_key',
        incremental_strategy='merge'
    )
}}

select
    to_hex(md5(concat(i.country_iso3, '|', i.indicator_name, '|', cast(i.year as string)))) as indicator_key,
    i.country_iso3,
    i.indicator_name,
    i.year,
    i.value,
    i.ingested_at
from {{ ref('stg_indicators') }} as i
inner join {{ ref('dim_countries') }} as c
    on i.country_iso3 = c.country_iso3
where i.value is not null

{% if is_incremental() %}
  and i.ingested_at > (select max(ingested_at) from {{ this }})
{% endif %}
