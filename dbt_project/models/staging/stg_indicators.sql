select
    indicator_code,
    indicator_name,
    country_iso3,
    country_name,
    year,
    value,
    ingested_at
from {{ source('worldbank_raw', 'raw_indicators') }}
