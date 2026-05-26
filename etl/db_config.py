from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy import create_engine

DEFAULT_DB_URL = "mysql+pymysql://root@localhost/green_trace_dw"
ENV_FILE = Path(__file__).resolve().parents[1] / ".env"


def _load_env_file() -> dict[str, str]:
    if not ENV_FILE.exists():
        return {}

    values: dict[str, str] = {}
    for raw_line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")

    return values


def get_database_url() -> str:
    file_values = _load_env_file()
    return (
        os.environ.get("GREEN_TRACE_DB_URL")
        or os.environ.get("DATABASE_URL")
        or file_values.get("GREEN_TRACE_DB_URL")
        or file_values.get("DATABASE_URL")
        or DEFAULT_DB_URL
    )


def create_db_engine():
    return create_engine(get_database_url())
