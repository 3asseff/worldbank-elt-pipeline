select
    country_iso3,
    country_iso2,
    country_name,
    region,
    income_level,
    capital_city,
    region = 'Aggregates' as is_aggregate
from {{ source('worldbank_raw', 'raw_countries') }}
