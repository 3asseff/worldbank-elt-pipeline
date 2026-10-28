from pathlib import Path

from google.api_core.exceptions import NotFound
from google.cloud import bigquery

PROJECT_ID = "elias-wb-pipeline-2610"
DATASET = "worldbank_raw"
DATASET_LOCATION = "US"  # only used if the dataset doesn't exist yet

INDICATOR_SCHEMA = [
    bigquery.SchemaField("indicator_code", "STRING"),
    bigquery.SchemaField("indicator_name", "STRING"),
    bigquery.SchemaField("country_iso3", "STRING"),
    bigquery.SchemaField("country_name", "STRING"),
    bigquery.SchemaField("year", "INT64"),
    bigquery.SchemaField("value", "FLOAT64"),
    bigquery.SchemaField("ingested_at", "TIMESTAMP"),
]

COUNTRY_SCHEMA = [
    bigquery.SchemaField("country_iso3", "STRING"),
    bigquery.SchemaField("country_iso2", "STRING"),
    bigquery.SchemaField("country_name", "STRING"),
    bigquery.SchemaField("region", "STRING"),
    bigquery.SchemaField("income_level", "STRING"),
    bigquery.SchemaField("capital_city", "STRING"),
    bigquery.SchemaField("ingested_at", "TIMESTAMP"),
]


def _ensure_dataset(client):
    ref = f"{PROJECT_ID}.{DATASET}"
    try:
        client.get_dataset(ref)
    except NotFound:
        ds = bigquery.Dataset(ref)
        ds.location = DATASET_LOCATION
        client.create_dataset(ds)


def _load_file(client, path, table, schema):
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        schema=schema,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )
    with open(path, "rb") as f:
        job = client.load_table_from_file(
            f, f"{PROJECT_ID}.{DATASET}.{table}", job_config=job_config
        )
    job.result()
    return client.get_table(f"{PROJECT_ID}.{DATASET}.{table}").num_rows


def load_all(paths):
    client = bigquery.Client(project=PROJECT_ID)
    _ensure_dataset(client)

    paths = [Path(p) for p in paths]
    countries_path = next(p for p in paths if p.name == "countries.jsonl")
    indicator_paths = [
        p for p in paths
        if p.name not in ("countries.jsonl", "_all_indicators.jsonl")
    ]

    # Combine the indicator files into a single file for one atomic load
    combined = countries_path.parent / "_all_indicators.jsonl"
    with open(combined, "w") as out:
        for p in sorted(indicator_paths):
            out.write(p.read_text())

    return {
        "raw_indicators": _load_file(client, combined, "raw_indicators", INDICATOR_SCHEMA),
        "raw_countries": _load_file(client, countries_path, "raw_countries", COUNTRY_SCHEMA),
    }
