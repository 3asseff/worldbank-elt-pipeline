-- Real countries only: regional aggregates (World, Arab World, ...) are excluded
select
    country_iso3,
    country_iso2,
    country_name,
    region,
    income_level,
    capital_city
from {{ ref('stg_countries') }}
where not is_aggregate
