from __future__ import annotations

import hashlib
import json
import re
import secrets
import time
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from flask import Flask, Response, jsonify, request, send_from_directory
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from .config import FRONTEND_DIR, get_database_url
from .live_data import build_facility_editor_rows_from_csv, build_live_payload

app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")
engine: Engine = create_engine(get_database_url(), pool_pre_ping=True, future=True)
app.config["WRITE_TOKEN"] = secrets.token_urlsafe(32)

SAFE_SQL_VERBS = {"select", "insert", "update", "delete"}
DISALLOWED_SQL_KEYWORDS = {"drop", "alter", "truncate", "create", "grant", "revoke"}
SINGLE_STATEMENT_RE = re.compile(r";\s*\S")
HEX_32_RE = re.compile(r"^[0-9a-f]{32}$", re.IGNORECASE)
COUNTRY_RE = re.compile(r"^[A-Z]{2,10}$")
GRID_REGION_RE = re.compile(r"^[A-Z0-9 _-]{2,50}$")
SECURE_HEADERS = {
    "Content-Security-Policy": (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "font-src 'self' https://fonts.gstatic.com data:; "
        "img-src 'self' data:; "
        "connect-src 'self'; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "form-action 'self'; "
        "frame-ancestors 'none'"
    ),
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "X-Frame-Options": "DENY",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
}


def _json_error(message: str, status_code: int = 400):
    return jsonify({"ok": False, "error": message}), status_code


def _request_origin_matches(host_url: str, header_value: str | None) -> bool:
    if not header_value:
        return True

    try:
        parsed = urlparse(header_value)
        request_origin = f"{parsed.scheme}://{parsed.netloc}"
    except Exception:  # noqa: BLE001
        return False

    return request_origin == host_url.rstrip("/")


def _require_write_access():
    token = request.headers.get("X-GreenTrace-Write-Token", "")
    expected = app.config.get("WRITE_TOKEN", "")
    if not expected or not secrets.compare_digest(token, expected):
        return _json_error("Write access token is missing or invalid.", 403)

    host_url = request.host_url
    if not _request_origin_matches(host_url, request.headers.get("Origin")):
        return _json_error("Cross-origin writes are not allowed.", 403)

    if not _request_origin_matches(host_url, request.headers.get("Referer")):
        return _json_error("Cross-origin writes are not allowed.", 403)

    return None


def _ping_database() -> tuple[bool, str | None]:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True, None
    except Exception as exc:  # noqa: BLE001
        return False, str(exc)


def _normalize_value(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat(sep=" ")
    return value


def _latest_facility_rows() -> list[dict[str, Any]]:
    query = text(
        """
        SELECT hf.hk_facility,
               hf.facility_bk,
               fa.facility_name,
               fa.country,
               fa.grid_region
        FROM hub_facility hf
        JOIN sat_facility_attr fa
          ON fa.hk_facility = hf.hk_facility
        JOIN (
            SELECT hk_facility, MAX(load_dts) AS max_load_dts
            FROM sat_facility_attr
            GROUP BY hk_facility
        ) latest
          ON latest.hk_facility = fa.hk_facility
         AND latest.max_load_dts = fa.load_dts
        ORDER BY fa.facility_name ASC
        """
    )
    with engine.connect() as conn:
        return [
            {
                "hkFacility": row.hk_facility,
                "facilityBk": row.facility_bk,
                "facilityName": row.facility_name,
                "country": row.country,
                "gridRegion": row.grid_region,
                "readOnly": False,
            }
            for row in conn.execute(query).fetchall()
        ]


def _insert_facility_attribute_version(hk_facility: str, facility_name: str, country: str, grid_region: str) -> dict[str, Any]:
    hashdiff = hashlib.md5(
        f"{facility_name}|{country}|{grid_region}".encode("utf-8"),
        usedforsecurity=False,
    ).hexdigest()

    with engine.begin() as conn:
        conn.execute(
            text(
                """
                INSERT INTO sat_facility_attr
                (hk_facility, load_dts, record_source, hashdiff, facility_name, country, grid_region)
                VALUES
                (:hk_facility, NOW(6), :record_source, :hashdiff, :facility_name, :country, :grid_region)
                """
            ),
            {
                "hk_facility": hk_facility,
                "record_source": "FRONTEND_LIVE_EDIT",
                "hashdiff": hashdiff,
                "facility_name": facility_name,
                "country": country,
                "grid_region": grid_region,
            },
        )

    return {
        "hkFacility": hk_facility,
        "facilityName": facility_name,
        "country": country,
        "gridRegion": grid_region,
    }


def _validate_sql_statement(sql: str) -> tuple[bool, str | None]:
    trimmed = sql.strip()
    if not trimmed:
        return False, "SQL is empty."

    if len(trimmed) > 2000:
        return False, "SQL is too long for the live console."

    lowered = trimmed.lower()
    first_word = lowered.split(None, 1)[0]
    if first_word not in SAFE_SQL_VERBS:
        return False, "Only SELECT, INSERT, UPDATE, and DELETE statements are allowed."

    if SINGLE_STATEMENT_RE.search(trimmed):
        return False, "Only one SQL statement can be executed at a time."

    for keyword in DISALLOWED_SQL_KEYWORDS:
        if re.search(rf"\b{keyword}\b", lowered):
            return False, f"The keyword '{keyword}' is not allowed in the live SQL console."

    return True, None


@app.after_request
def add_security_headers(response):
    for header, value in SECURE_HEADERS.items():
        response.headers.setdefault(header, value)

    if request.path.startswith("/api/"):
        response.headers.setdefault("Cache-Control", "no-store")

    return response


@app.get("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.get("/dashboard")
def dashboard_alias():
    return send_from_directory(FRONTEND_DIR, "dashboard.html")


@app.get("/architecture")
def architecture_alias():
    return send_from_directory(FRONTEND_DIR, "architecture.html")


@app.get("/api/health")
def health():
    db_connected, error = _ping_database()
    return jsonify(
        {
            "ok": True,
            "dbConnected": db_connected,
            "source": "database" if db_connected else "snapshot",
            "error": error,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    )


@app.get("/api/security/bootstrap")
def security_bootstrap():
    return jsonify({"ok": True, "writeToken": app.config["WRITE_TOKEN"]})


@app.get("/api/live-data")
def live_data():
    payload = build_live_payload(engine)
    return jsonify({"ok": True, "data": payload})


@app.get("/api/live-events")
def live_events():
    def stream():
        while True:
            db_connected, error = _ping_database()
            payload = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "source": "database" if db_connected else "snapshot",
                "dbConnected": db_connected,
                "error": error,
            }
            yield f"data: {json.dumps(payload)}\n\n"
            time.sleep(4)

    return Response(
        stream(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/editor/facilities")
def facility_editor_rows():
    db_connected, error = _ping_database()
    if db_connected:
        rows = _latest_facility_rows()
        return jsonify({"ok": True, "rows": rows, "readOnly": False})

    return jsonify(
        {
            "ok": True,
            "rows": build_facility_editor_rows_from_csv(),
            "readOnly": True,
            "error": error,
        }
    )


@app.patch("/api/editor/facilities/<hk_facility>")
def patch_facility(hk_facility: str):
    write_error = _require_write_access()
    if write_error:
        return write_error

    db_connected, error = _ping_database()
    if not db_connected:
        return _json_error(
            "The live database is not connected, so facility edits are currently disabled.",
            503,
        )

    if not HEX_32_RE.fullmatch(hk_facility):
        return _json_error("Facility identifier is invalid.")

    body = request.get_json(silent=True) or {}
    facility_name = str(body.get("facilityName", "")).strip()
    country = str(body.get("country", "")).strip().upper()
    grid_region = str(body.get("gridRegion", "")).strip().upper()

    if not facility_name:
        return _json_error("Facility name is required.")
    if not country:
        return _json_error("Country is required.")
    if not grid_region:
        return _json_error("Grid region is required.")
    if len(facility_name) > 100:
        return _json_error("Facility name is too long.")
    if not COUNTRY_RE.fullmatch(country):
        return _json_error("Country must be 2 to 10 uppercase letters.")
    if not GRID_REGION_RE.fullmatch(grid_region):
        return _json_error("Grid region contains invalid characters.")

    try:
        record = _insert_facility_attribute_version(hk_facility, facility_name, country, grid_region)
    except SQLAlchemyError as exc:
        return _json_error(f"Unable to save facility changes: {exc}", 500)

    return jsonify({"ok": True, "record": record, "message": "Facility attributes saved as a new satellite version."})


@app.post("/api/sql/execute")
def execute_sql():
    write_error = _require_write_access()
    if write_error:
        return write_error

    db_connected, _ = _ping_database()
    if not db_connected:
        return _json_error(
            "The live database is not connected, so SQL execution is unavailable right now.",
            503,
        )

    body = request.get_json(silent=True) or {}
    sql = str(body.get("sql", ""))
    valid, message = _validate_sql_statement(sql)
    if not valid:
        return _json_error(message or "Invalid SQL.")

    verb = sql.strip().split(None, 1)[0].lower()

    try:
        if verb == "select":
            with engine.connect() as conn:
                result = conn.execute(text(sql))
                rows = result.mappings().fetchmany(200)
                payload_rows = [
                    {key: _normalize_value(value) for key, value in row.items()}
                    for row in rows
                ]
                return jsonify(
                    {
                        "ok": True,
                        "mode": "select",
                        "columns": list(result.keys()),
                        "rows": payload_rows,
                        "rowCount": len(payload_rows),
                        "message": "Select executed successfully.",
                    }
                )

        with engine.begin() as conn:
            result = conn.execute(text(sql))
            return jsonify(
                {
                    "ok": True,
                    "mode": verb,
                    "rowsAffected": int(result.rowcount or 0),
                    "message": f"{verb.upper()} executed successfully.",
                }
            )
    except SQLAlchemyError as exc:
        return _json_error(f"SQL execution failed: {exc}", 500)


@app.get("/<path:path>")
def static_proxy(path: str):
    candidate = Path(FRONTEND_DIR / path)
    if candidate.exists() and candidate.is_file():
        return send_from_directory(FRONTEND_DIR, path)
    return send_from_directory(FRONTEND_DIR, "index.html")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5500, debug=True)
