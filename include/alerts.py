import os

import requests


def notify_failure(context):
    ti = context["task_instance"]
    message = (
        f"Airflow task failed: {ti.dag_id}.{ti.task_id} "
        f"(run {context['run_id']}, try {ti.try_number}). Log: {ti.log_url}"
    )
    print(message)

    url = os.environ.get("ALERT_WEBHOOK_URL")
    if not url:
        return
    try:
        requests.post(url, json={"content": message}, timeout=10)
    except requests.RequestException as exc:
        print(f"Could not send alert: {exc}")
