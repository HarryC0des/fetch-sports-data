import json
import os
from datetime import datetime, timezone
from pathlib import Path


def build_run_id():
    run_id = os.getenv("RUN_ID")
    if run_id:
        return run_id
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def resolve_run_date():
    run_date = os.getenv("RUN_DATE")
    if run_date:
        return run_date
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def get_env(name, default=None, required=False):
    value = os.getenv(name, default)
    if required and not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


def load_json(path):
    with open(path, "r", encoding="utf-8") as file_handle:
        return json.load(file_handle)


def write_json(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def log_info(message):
    print(f"[INFO] {message}")


def log_warning(message):
    print(f"[WARNING] {message}")


def log_error(message):
    print(f"[ERROR] {message}")


def log_start(script_name, run_id, run_date):
    log_info(f"{script_name} started | run_id={run_id} run_date={run_date}")


def log_end(script_name, summary):
    log_info(f"{script_name} finished | {summary}")
