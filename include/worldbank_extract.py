import json
from datetime import datetime, timezone
from pathlib import Path

import requests

BASE_URL = "https://api.worldbank.org/v2"
RAW_DIR = Path("/opt/airflow/include/data/raw")
DATE_RANGE = "2000:2025"

INDICATORS = {
    "NY.GDP.PCAP.CD": "gdp_per_capita_usd",
    "SP.POP.TOTL": "population",
    "SP.DYN.LE00.IN": "life_expectancy",
    "FP.CPI.TOTL.ZG": "inflation_pct",
    "SL.UEM.TOTL.ZS": "unemployment_pct",
}


def _get_all_pages(url, params=None):
    """Fetch every page of a World Bank API response and return all rows."""
    rows, page = [], 1
    while True:
        resp = requests.get(
            url,
            params={**(params or {}), "format": "json", "per_page": 1000, "page": page},
            timeout=60,
        )
        resp.raise_for_status()
        payload = resp.json()
        if len(payload) < 2 or payload[1] is None:
            raise ValueError(f"Unexpected API response from {url}: {payload}")
        meta, data = payload
        rows.extend(data)
        if page >= meta["pages"]:
            return rows
        page += 1


def _write_jsonl(records, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for rec in records:
            f.write(json.dumps(rec) + "\n")


def extract_indicator(code, name, ds):
    raw = _get_all_pages(f"{BASE_URL}/country/all/indicator/{code}", {"date": DATE_RANGE})
    now = datetime.now(timezone.utc).isoformat()
    records = [
        {
            "indicator_code": code,
            "indicator_name": name,
            "country_iso3": r["countryiso3code"],
            "country_name": r["country"]["value"],
            "year": int(r["date"]),
            "value": r["value"],
            "ingested_at": now,
        }
        for r in raw
    ]
    path = RAW_DIR / f"ds={ds}" / f"{name}.jsonl"
    _write_jsonl(records, path)
    return str(path)


def extract_countries(ds):
    raw = _get_all_pages(f"{BASE_URL}/country")
    now = datetime.now(timezone.utc).isoformat()
    records = [
        {
            "country_iso3": r["id"],
            "country_iso2": r["iso2Code"],
            "country_name": r["name"],
            "region": r["region"]["value"],
            "income_level": r["incomeLevel"]["value"],
            "capital_city": r["capitalCity"],
            "ingested_at": now,
        }
        for r in raw
    ]
    path = RAW_DIR / f"ds={ds}" / "countries.jsonl"
    _write_jsonl(records, path)
    return str(path)


def extract_all(ds):
    paths = [extract_countries(ds)]
    for code, name in INDICATORS.items():
        paths.append(extract_indicator(code, name, ds))
    return paths
