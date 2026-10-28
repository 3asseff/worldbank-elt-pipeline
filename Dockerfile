FROM apache/airflow:2.9.3

USER airflow

# dbt in its own virtualenv so it doesn't clash with Airflow's dependencies
RUN python -m venv /home/airflow/dbt_venv \
 && /home/airflow/dbt_venv/bin/pip install --no-cache-dir "dbt-core==1.12.6" "dbt-bigquery==1.12.1"

# Libraries our extract and load tasks will use
RUN pip install --no-cache-dir requests pandas pyarrow db-dtypes google-cloud-bigquery
