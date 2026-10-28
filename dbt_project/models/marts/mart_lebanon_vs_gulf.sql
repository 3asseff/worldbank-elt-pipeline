with fct as (
    select * from {{ ref('fct_indicators') }}
),

lebanon as (
    select year, indicator_name, value as lebanon_value
    from fct
    where country_iso3 = 'LBN'
),

gulf as (
    select
        year,
        indicator_name,
        avg(value) as gulf_avg_value,
        count(*) as gulf_countries_reporting
    from fct
    where country_iso3 in ('SAU', 'ARE', 'QAT', 'KWT', 'BHR', 'OMN')
    group by year, indicator_name
)

select
    l.year,
    l.indicator_name,
    l.lebanon_value,
    g.gulf_avg_value,
    g.gulf_countries_reporting,
    l.lebanon_value - g.gulf_avg_value as gap,
    safe_divide(l.lebanon_value, g.gulf_avg_value) as lebanon_to_gulf_ratio
from lebanon as l
inner join gulf as g
    on l.year = g.year
    and l.indicator_name = g.indicator_name
