import sys
from datetime import datetime, timedelta

sys.path.insert(0, "/opt/airflow")

from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator

from include.bigquery_load import load_all
from include.worldbank_extract import extract_all

DBT = "/home/airflow/dbt_venv/bin/dbt"
DBT_DIR = "/opt/airflow/dbt_project"


@dag(
    dag_id="worldbank_pipeline",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    default_args={"retries": 2, "retry_delay": timedelta(minutes=2)},
    tags=["worldbank"],
)
def worldbank_pipeline():
    @task
    def extract(ds=None):
        return extract_all(ds)

    @task
    def load_to_bigquery(paths):
        counts = load_all(paths)
        print(f"Loaded rows: {counts}")
        return counts

    # dbt build runs models and tests together: a failing test fails the DAG run
    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command=f"cd {DBT_DIR} && {DBT} build --profiles-dir .",
        retries=1,
    )

    load_to_bigquery(extract()) >> dbt_build


worldbank_pipeline()
