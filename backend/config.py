from __future__ import annotations

import os
from pathlib import Path

DEFAULT_DB_URL = "mysql+pymysql://root@localhost/green_trace_dw"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIR = PROJECT_ROOT / "frontend"
DATASET_ROOT = PROJECT_ROOT / "datasets" / "green_trace_export"
ENV_FILE = PROJECT_ROOT / ".env"


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


def get_snapshot_export_dir() -> Path:
    if not DATASET_ROOT.exists():
        raise FileNotFoundError(f"Dataset root not found: {DATASET_ROOT}")

    export_dirs = sorted(
        [path for path in DATASET_ROOT.iterdir() if path.is_dir()],
        key=lambda item: item.name,
        reverse=True,
    )

    if not export_dirs:
        raise FileNotFoundError(f"No dataset export directories found under: {DATASET_ROOT}")

    return export_dirs[0]
