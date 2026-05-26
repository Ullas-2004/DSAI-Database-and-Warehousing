from __future__ import annotations

import csv
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Engine

from .config import get_snapshot_export_dir

STORY_PANELS = [
    {
        "page": "Page 01",
        "title": "Capture the source signal.",
        "body": (
            "Facilities, suppliers, shipments, meters, and credits are preserved "
            "in Data Vault form so the system never loses source context."
        ),
    },
    {
        "page": "Page 02",
        "title": "Model emissions without losing lineage.",
        "body": (
            "Business Vault logic turns raw activity into Scope 2 and Scope 3 "
            "events while keeping versions, hashes, and traceability intact."
        ),
    },
    {
        "page": "Page 03",
        "title": "Govern offsets as real assets.",
        "body": (
            "Carbon credits are modeled as governed assets, ready for issue, "
            "retire, and future anti-double-counting workflows."
        ),
    },
    {
        "page": "Page 04",
        "title": "Present the system like a product.",
        "body": (
            "The frontend reframes the project as a cinematic control room with "
            "paced sections, motion, and facility-level intelligence."
        ),
    },
]

FEATURE_CARDS = [
    {
        "title": "Cinematic motion system",
        "body": (
            "Every major section is staged as a full-screen reveal, with motion "
            "that guides attention instead of distracting from the data."
        ),
    },
    {
        "title": "Data-backed interface",
        "body": (
            "Metrics, rankings, intervals, and mix views are grounded in warehouse "
            "values so the experience feels credible, not decorative."
        ),
    },
    {
        "title": "Architecture as narrative",
        "body": (
            "The model, ETL path, and governance layers are written as a story "
            "so technical depth becomes easier to present."
        ),
    },
]

PHASES = [
    {
        "phase": "Phase 1",
        "title": "Dataset analysis",
        "body": (
            "Twenty-five source files were profiled and classified into Data Vault "
            "structures to frame the warehouse design."
        ),
    },
    {
        "phase": "Phase 2",
        "title": "Schema design",
        "body": (
            "The MySQL schema was shaped into hubs, links, satellites, business "
            "vault tables, a carbon ledger, and the reporting mart."
        ),
    },
    {
        "phase": "Phase 3",
        "title": "ETL pipeline",
        "body": (
            "Python and SQLAlchemy pipelines load the vault idempotently and prepare "
            "the platform for repeatable processing runs."
        ),
    },
    {
        "phase": "Phase 4",
        "title": "Business vault logic",
        "body": (
            "Scope 2 electricity and Scope 3 transport emissions are computed from source "
            "activity and reference emission factors."
        ),
    },
    {
        "phase": "Phase 5",
        "title": "Carbon credit ledger",
        "body": (
            "Credit assets, transactions, and positions are modeled to support "
            "governed offset accounting."
        ),
    },
    {
        "phase": "Phase 6",
        "title": "Data mart",
        "body": (
            "A CSRD-oriented reporting layer is prepared for downstream dashboards "
            "and compliance rollups."
        ),
    },
    {
        "phase": "Phase 7",
        "title": "Lineage",
        "body": (
            "Lineage hooks are provisioned so business logic and downstream reporting can be "
            "audited end to end."
        ),
    },
    {
        "phase": "Phase 8",
        "title": "Visualization",
        "body": (
            "The frontend adds the final product layer: animated storytelling, live controls, "
            "and architecture communication."
        ),
    },
]


def _timestamp_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _latest_snapshot_path() -> Path:
    return get_snapshot_export_dir()


def _csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
      reader = csv.DictReader(handle)
      return list(reader)


def _to_float(value: Any) -> float:
    if value in (None, "", "NULL"):
        return 0.0
    return float(value)


def _to_int(value: Any) -> int:
    if value in (None, "", "NULL"):
        return 0
    return int(value)


def _format_capture_window(start: str | None, end: str | None) -> str:
    if not start or not end:
        return "No capture window available"

    return f"{start.replace('T', ' ')} to {end.replace('T', ' ')}"


def _hero_highlights(overview: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "label": "Total modeled emissions",
            "value": round(overview["totalKg"] / 1000.0, 2),
            "format": "decimal",
            "decimals": 2,
            "suffix": " tCO2e",
            "note": "Modeled footprint across scopes",
        },
        {
            "label": "Energy readings",
            "value": overview["energyReadings"],
            "format": "integer",
            "suffix": "+",
            "note": "Meter observations in the current model",
        },
        {
            "label": "Facilities monitored",
            "value": overview["facilities"],
            "format": "integer",
            "note": "Facilities in the current operating scope",
        },
        {
            "label": "Warehouse tables",
            "value": overview["tables"],
            "format": "integer",
            "note": "From vault structures to reporting views",
        },
    ]


def _kpis(overview: dict[str, Any]) -> list[dict[str, Any]]:
    scope2_pct = (overview["scope2Kg"] / overview["totalKg"] * 100.0) if overview["totalKg"] else 0.0
    scope3_pct = (overview["scope3Kg"] / overview["totalKg"] * 100.0) if overview["totalKg"] else 0.0
    return [
        {
            "label": "Scope 2 emissions",
            "value": round(overview["scope2Kg"] / 1000.0, 2),
            "format": "decimal",
            "decimals": 2,
            "suffix": " tCO2e",
            "note": f"{scope2_pct:.1f}% of the modeled footprint",
        },
        {
            "label": "Scope 3 emissions",
            "value": round(overview["scope3Kg"] / 1000.0, 2),
            "format": "decimal",
            "decimals": 2,
            "suffix": " tCO2e",
            "note": f"{scope3_pct:.1f}% of the modeled footprint",
        },
        {
            "label": "Meters connected",
            "value": overview["meters"],
            "format": "integer",
            "note": f"Feeding {overview['energyReadings']} meter observations",
        },
        {
            "label": "Supplier entities",
            "value": overview["suppliers"],
            "format": "integer",
            "note": "Distributed across the supply network",
        },
        {
            "label": "Shipment records",
            "value": overview["shipments"],
            "format": "integer",
            "note": "Driving the current Scope 3 layer",
        },
    ]


def _architecture_layers(overview: dict[str, Any], schema_counts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    schema_index = {item["label"]: item["count"] for item in schema_counts}
    return [
        {
            "name": "Raw Vault",
            "stat": f"{overview['facilities']} facilities / {overview['meters']} meters",
            "description": (
                "Hubs, links, and satellites preserve the operating truth for "
                "facilities, suppliers, meters, shipments, reporting periods, and credits."
            ),
        },
        {
            "name": "Business Vault",
            "stat": f"{overview['energyReadings'] + overview['shipments']} computed events",
            "description": (
                "Emission logic converts energy and shipment activity into Scope 2 "
                "and Scope 3 events with factor references and transform versions."
            ),
        },
        {
            "name": "Carbon Ledger",
            "stat": f"{overview['credits']} credit assets",
            "description": (
                "The credit model is designed for issuance and retirement workflows "
                "so offsets can be tracked without double counting."
            ),
        },
        {
            "name": "Data Mart UX",
            "stat": f"{schema_index.get('Data Mart', 0)} reporting layer",
            "description": (
                "The experience surfaces facility rankings, regional rollups, query "
                "cards, and compliance storytelling in one readable layer."
            ),
        },
    ]


def _query_cards(region_totals: list[dict[str, Any]], facility_leaders: list[dict[str, Any]], interval_load: list[dict[str, Any]]) -> list[dict[str, Any]]:
    top_region = region_totals[0] if region_totals else {"region": "N/A", "totalKg": 0}
    top_facility = facility_leaders[0] if facility_leaders else {"facility": "N/A", "totalKg": 0}
    top_slot = max(interval_load, key=lambda item: item["totalKg"], default={"slot": "N/A", "totalKg": 0})
    return [
        {
            "label": "Regional load",
            "sql": (
                "SELECT grid_region, SUM(scope2_kgco2e + scope3_kgco2e) AS total_kg\n"
                "FROM emissions_summary\n"
                "GROUP BY grid_region\n"
                "ORDER BY total_kg DESC;"
            ),
            "result": f"{top_region['region']} carries the highest modeled regional load at {top_region['totalKg']:.2f} kgCO2e.",
        },
        {
            "label": "Facility ranking",
            "sql": (
                "SELECT facility_name, SUM(scope2_kgco2e + scope3_kgco2e) AS total_kg\n"
                "FROM facility_emissions\n"
                "GROUP BY facility_name\n"
                "ORDER BY total_kg DESC\n"
                "LIMIT 5;"
            ),
            "result": f"{top_facility['facility']} is the highest facility footprint at {top_facility['totalKg']:.2f} kgCO2e.",
        },
        {
            "label": "Capture pulse",
            "sql": (
                "SELECT reading_slot, SUM(scope2_kgco2e) AS interval_kg\n"
                "FROM scope2_events\n"
                "GROUP BY reading_slot\n"
                "ORDER BY reading_slot;"
            ),
            "result": f"The strongest capture interval in the model is {top_slot['slot']} with {top_slot['totalKg']:.2f} kgCO2e.",
        },
    ]


def _payload_from_metrics(metrics: dict[str, Any], source: str, db_connected: bool, error: str | None = None) -> dict[str, Any]:
    overview = metrics["overview"]
    schema_counts = metrics["schemaCounts"]
    region_totals = metrics["regionTotals"]
    facility_leaders = metrics["facilityLeaders"]
    interval_load = metrics["intervalLoad"]
    payload = {
        "meta": {
            "source": source,
            "dbConnected": db_connected,
            "live": db_connected,
            "lastUpdated": _timestamp_now(),
            "error": error,
        },
        "overview": overview,
        "heroHighlights": _hero_highlights(overview),
        "storyPanels": STORY_PANELS,
        "featureCards": FEATURE_CARDS,
        "architectureLayers": _architecture_layers(overview, schema_counts),
        "kpis": _kpis(overview),
        "regionTotals": region_totals,
        "facilityLeaders": facility_leaders,
        "intervalLoad": interval_load,
        "vehicleMix": metrics["vehicleMix"],
        "supplierSectors": metrics["supplierSectors"],
        "schemaCounts": schema_counts,
        "phases": PHASES,
        "queries": _query_cards(region_totals, facility_leaders, interval_load),
    }
    return payload


def build_payload_from_database(engine: Engine) -> dict[str, Any]:
    with engine.connect() as conn:
        table_names = [row[0] for row in conn.execute(text("SHOW TABLES")).fetchall()]
        exact_rows = 0
        for table_name in table_names:
            exact_rows += int(conn.execute(text(f"SELECT COUNT(*) FROM `{table_name}`")).scalar_one())

        reporting_period = conn.execute(
            text("SELECT period_bk FROM hub_reporting_period ORDER BY load_dts DESC LIMIT 1")
        ).scalar_one_or_none() or "N/A"

        capture_start, capture_end = conn.execute(
            text("SELECT MIN(reading_ts), MAX(reading_ts) FROM sat_energy_reading")
        ).one()

        facilities = int(conn.execute(text("SELECT COUNT(*) FROM hub_facility")).scalar_one())
        meters = int(conn.execute(text("SELECT COUNT(*) FROM hub_meter")).scalar_one())
        suppliers = int(conn.execute(text("SELECT COUNT(*) FROM hub_supplier")).scalar_one())
        shipments = int(conn.execute(text("SELECT COUNT(*) FROM hub_shipment")).scalar_one())
        credits = int(conn.execute(text("SELECT COUNT(*) FROM hub_carbon_credit")).scalar_one())
        energy_readings = int(conn.execute(text("SELECT COUNT(*) FROM sat_energy_reading")).scalar_one())
        scope2 = float(conn.execute(text("SELECT COALESCE(SUM(scope2_kgco2e), 0) FROM bv_scope2_emission_event")).scalar_one())
        scope3 = float(conn.execute(text("SELECT COALESCE(SUM(scope3_kgco2e), 0) FROM bv_scope3_emission_event")).scalar_one())

        region_totals = [
            {
                "region": row.region,
                "totalKg": round(float(row.total_kg), 2),
            }
            for row in conn.execute(
                text(
                    """
                    SELECT latest.grid_region AS region,
                           ROUND(SUM(COALESCE(s2.total_scope2, 0) + COALESCE(s3.total_scope3, 0)), 2) AS total_kg
                    FROM (
                        SELECT fa.hk_facility, fa.grid_region
                        FROM sat_facility_attr fa
                        JOIN (
                            SELECT hk_facility, MAX(load_dts) AS max_load_dts
                            FROM sat_facility_attr
                            GROUP BY hk_facility
                        ) latest_fa
                          ON latest_fa.hk_facility = fa.hk_facility
                         AND latest_fa.max_load_dts = fa.load_dts
                    ) latest
                    LEFT JOIN (
                        SELECT hk_facility, SUM(scope2_kgco2e) AS total_scope2
                        FROM bv_scope2_emission_event
                        GROUP BY hk_facility
                    ) s2
                      ON s2.hk_facility = latest.hk_facility
                    LEFT JOIN (
                        SELECT hk_facility, SUM(scope3_kgco2e) AS total_scope3
                        FROM bv_scope3_emission_event
                        GROUP BY hk_facility
                    ) s3
                      ON s3.hk_facility = latest.hk_facility
                    GROUP BY latest.grid_region
                    ORDER BY total_kg DESC, latest.grid_region ASC
                    """
                )
            ).fetchall()
        ]

        facility_leaders = [
            {
                "facility": row.facility_name,
                "region": row.grid_region,
                "scope2Kg": round(float(row.scope2_kg), 2),
                "scope3Kg": round(float(row.scope3_kg), 2),
                "totalKg": round(float(row.total_kg), 2),
            }
            for row in conn.execute(
                text(
                    """
                    SELECT latest.facility_name,
                           latest.grid_region,
                           COALESCE(s2.total_scope2, 0) AS scope2_kg,
                           COALESCE(s3.total_scope3, 0) AS scope3_kg,
                           COALESCE(s2.total_scope2, 0) + COALESCE(s3.total_scope3, 0) AS total_kg
                    FROM (
                        SELECT fa.hk_facility, fa.facility_name, fa.grid_region
                        FROM sat_facility_attr fa
                        JOIN (
                            SELECT hk_facility, MAX(load_dts) AS max_load_dts
                            FROM sat_facility_attr
                            GROUP BY hk_facility
                        ) latest_fa
                          ON latest_fa.hk_facility = fa.hk_facility
                         AND latest_fa.max_load_dts = fa.load_dts
                    ) latest
                    LEFT JOIN (
                        SELECT hk_facility, SUM(scope2_kgco2e) AS total_scope2
                        FROM bv_scope2_emission_event
                        GROUP BY hk_facility
                    ) s2
                      ON s2.hk_facility = latest.hk_facility
                    LEFT JOIN (
                        SELECT hk_facility, SUM(scope3_kgco2e) AS total_scope3
                        FROM bv_scope3_emission_event
                        GROUP BY hk_facility
                    ) s3
                      ON s3.hk_facility = latest.hk_facility
                    ORDER BY total_kg DESC, latest.facility_name ASC
                    LIMIT 8
                    """
                )
            ).fetchall()
        ]

        interval_load = [
            {
                "slot": row.slot,
                "totalKg": round(float(row.total_kg), 2),
            }
            for row in conn.execute(
                text(
                    """
                    SELECT DATE_FORMAT(reading_ts, '%H:%i') AS slot,
                           SUM(scope2_kgco2e) AS total_kg
                    FROM bv_scope2_emission_event
                    GROUP BY slot
                    ORDER BY slot
                    """
                )
            ).fetchall()
        ]

        vehicle_mix = [
            {"label": row.vehicle_type or "Unknown", "count": int(row.total_count)}
            for row in conn.execute(
                text(
                    """
                    SELECT vehicle_type, COUNT(*) AS total_count
                    FROM sat_shipment_activity
                    GROUP BY vehicle_type
                    ORDER BY total_count DESC, vehicle_type ASC
                    """
                )
            ).fetchall()
        ]

        supplier_sectors = [
            {"label": row.sector or "Unknown", "count": int(row.total_count)}
            for row in conn.execute(
                text(
                    """
                    SELECT sector, COUNT(*) AS total_count
                    FROM sat_supplier_attr
                    GROUP BY sector
                    ORDER BY total_count DESC, sector ASC
                    """
                )
            ).fetchall()
        ]

        schema_counts = [
            {"label": "Hubs", "count": int(conn.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name LIKE 'hub\\_%' ESCAPE '\\\\'")).scalar_one()), "detail": "Core entities"},
            {"label": "Links", "count": int(conn.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name LIKE 'link\\_%' ESCAPE '\\\\'")).scalar_one()), "detail": "Business relationships"},
            {"label": "Satellites", "count": int(conn.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name LIKE 'sat\\_%' ESCAPE '\\\\'")).scalar_one()), "detail": "Historical attributes"},
            {"label": "Business Vault", "count": int(conn.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name LIKE 'bv\\_%' ESCAPE '\\\\'")).scalar_one()), "detail": "Emission event tables"},
            {"label": "Ledger", "count": int(conn.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name LIKE 'ledger\\_%' ESCAPE '\\\\'")).scalar_one()), "detail": "Credit transactions and positions"},
            {"label": "Data Mart", "count": int(conn.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name LIKE 'dm\\_%' ESCAPE '\\\\'")).scalar_one()), "detail": "CSRD summary layer"},
            {"label": "Metadata", "count": int(conn.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name LIKE 'meta\\_%' ESCAPE '\\\\'")).scalar_one()), "detail": "Lineage and audit metadata"},
        ]

    overview = {
        "project": "GreenTrace ESG Data Vault",
        "subtitle": "An editorial live frontend for auditable carbon intelligence.",
        "reportingPeriod": reporting_period,
        "tables": len(table_names),
        "rowsProcessed": exact_rows,
        "facilities": facilities,
        "meters": meters,
        "suppliers": suppliers,
        "shipments": shipments,
        "credits": credits,
        "scope2Kg": round(scope2, 2),
        "scope3Kg": round(scope3, 2),
        "totalKg": round(scope2 + scope3, 2),
        "energyReadings": energy_readings,
        "captureWindow": _format_capture_window(str(capture_start) if capture_start else None, str(capture_end) if capture_end else None),
        "narrative": "GreenTrace is reading the warehouse live and can redraw the interface as the model changes.",
    }

    return _payload_from_metrics(
        {
            "overview": overview,
            "schemaCounts": schema_counts,
            "regionTotals": region_totals,
            "facilityLeaders": facility_leaders,
            "intervalLoad": interval_load,
            "vehicleMix": vehicle_mix,
            "supplierSectors": supplier_sectors,
        },
        source="database",
        db_connected=True,
    )


def build_payload_from_csv() -> dict[str, Any]:
    snapshot_dir = _latest_snapshot_path()

    facility_rows = _csv_rows(snapshot_dir / "sat_facility_attr.csv")
    supplier_rows = _csv_rows(snapshot_dir / "sat_supplier_attr.csv")
    shipment_rows = _csv_rows(snapshot_dir / "sat_shipment_activity.csv")
    scope2_rows = _csv_rows(snapshot_dir / "bv_scope2_emission_event.csv")
    scope3_rows = _csv_rows(snapshot_dir / "bv_scope3_emission_event.csv")
    period_rows = _csv_rows(snapshot_dir / "hub_reporting_period.csv")
    energy_rows = _csv_rows(snapshot_dir / "sat_energy_reading.csv")

    latest_facilities: dict[str, dict[str, str]] = {}
    for row in facility_rows:
        hk = row["hk_facility"]
        current = latest_facilities.get(hk)
        if current is None or row["load_dts"] >= current["load_dts"]:
            latest_facilities[hk] = row

    facility_totals: dict[str, dict[str, float]] = defaultdict(lambda: {"scope2": 0.0, "scope3": 0.0})
    interval_load: dict[str, float] = defaultdict(float)

    for row in scope2_rows:
        hk = row["hk_facility"]
        facility_totals[hk]["scope2"] += _to_float(row["scope2_kgco2e"])
        slot = row["reading_ts"][11:16]
        interval_load[slot] += _to_float(row["scope2_kgco2e"])

    for row in scope3_rows:
        hk = row["hk_facility"]
        facility_totals[hk]["scope3"] += _to_float(row["scope3_kgco2e"])

    region_totals_map: dict[str, float] = defaultdict(float)
    facility_leaders: list[dict[str, Any]] = []
    for hk, totals in facility_totals.items():
        facility_row = latest_facilities.get(hk, {})
        facility_name = facility_row.get("facility_name", hk)
        grid_region = facility_row.get("grid_region", "Unknown")
        total_kg = totals["scope2"] + totals["scope3"]
        region_totals_map[grid_region] += total_kg
        facility_leaders.append(
            {
                "facility": facility_name,
                "region": grid_region,
                "scope2Kg": round(totals["scope2"], 2),
                "scope3Kg": round(totals["scope3"], 2),
                "totalKg": round(total_kg, 2),
            }
        )

    facility_leaders.sort(key=lambda item: (-item["totalKg"], item["facility"]))
    region_totals = [
        {"region": key, "totalKg": round(value, 2)}
        for key, value in sorted(region_totals_map.items(), key=lambda item: (-item[1], item[0]))
    ]

    vehicle_mix_map: dict[str, int] = defaultdict(int)
    for row in shipment_rows:
        vehicle_mix_map[row.get("vehicle_type") or "Unknown"] += 1
    vehicle_mix = [
        {"label": key, "count": value}
        for key, value in sorted(vehicle_mix_map.items(), key=lambda item: (-item[1], item[0]))
    ]

    supplier_sector_map: dict[str, int] = defaultdict(int)
    for row in supplier_rows:
        supplier_sector_map[row.get("sector") or "Unknown"] += 1
    supplier_sectors = [
        {"label": key, "count": value}
        for key, value in sorted(supplier_sector_map.items(), key=lambda item: (-item[1], item[0]))
    ]

    schema_counts = [
        {"label": "Hubs", "count": 6, "detail": "Core entities"},
        {"label": "Links", "count": 3, "detail": "Business relationships"},
        {"label": "Satellites", "count": 6, "detail": "Historical attributes"},
        {"label": "Business Vault", "count": 2, "detail": "Emission event tables"},
        {"label": "Ledger", "count": 2, "detail": "Credit transactions and positions"},
        {"label": "Data Mart", "count": 1, "detail": "CSRD summary layer"},
        {"label": "Metadata", "count": 1, "detail": "Lineage and audit metadata"},
    ]

    all_csv_paths = list(snapshot_dir.glob("*.csv"))
    rows_processed = 0
    for csv_path in all_csv_paths:
        with csv_path.open("r", encoding="utf-8", newline="") as handle:
            rows_processed += max(sum(1 for _ in handle) - 1, 0)

    scope2_total = round(sum(_to_float(row["scope2_kgco2e"]) for row in scope2_rows), 2)
    scope3_total = round(sum(_to_float(row["scope3_kgco2e"]) for row in scope3_rows), 2)
    capture_times = [row["reading_ts"] for row in energy_rows if row.get("reading_ts")]
    capture_start = min(capture_times) if capture_times else None
    capture_end = max(capture_times) if capture_times else None

    overview = {
        "project": "GreenTrace ESG Data Vault",
        "subtitle": "An editorial live-ready frontend for auditable carbon intelligence.",
        "reportingPeriod": period_rows[0]["period_bk"] if period_rows else "N/A",
        "tables": 22,
        "rowsProcessed": rows_processed,
        "facilities": len({row["hk_facility"] for row in facility_rows}),
        "meters": len(_csv_rows(snapshot_dir / "hub_meter.csv")),
        "suppliers": len({row["hk_supplier"] for row in supplier_rows}),
        "shipments": len({row["hk_shipment"] for row in shipment_rows}),
        "credits": len(_csv_rows(snapshot_dir / "hub_carbon_credit.csv")),
        "scope2Kg": scope2_total,
        "scope3Kg": scope3_total,
        "totalKg": round(scope2_total + scope3_total, 2),
        "energyReadings": len(energy_rows),
        "captureWindow": _format_capture_window(capture_start, capture_end),
        "narrative": "GreenTrace is showing the latest exported snapshot because the live warehouse connection is not available.",
    }

    interval_rows = [
        {"slot": key, "totalKg": round(value, 2)}
        for key, value in sorted(interval_load.items(), key=lambda item: item[0])
    ]

    return _payload_from_metrics(
        {
            "overview": overview,
            "schemaCounts": schema_counts,
            "regionTotals": region_totals,
            "facilityLeaders": facility_leaders[:8],
            "intervalLoad": interval_rows,
            "vehicleMix": vehicle_mix,
            "supplierSectors": supplier_sectors,
        },
        source="snapshot",
        db_connected=False,
    )


def build_live_payload(engine: Engine) -> dict[str, Any]:
    try:
        return build_payload_from_database(engine)
    except Exception as exc:
        payload = build_payload_from_csv()
        payload["meta"]["error"] = str(exc)
        return payload


def build_facility_editor_rows_from_csv() -> list[dict[str, Any]]:
    snapshot_dir = _latest_snapshot_path()
    facility_rows = _csv_rows(snapshot_dir / "sat_facility_attr.csv")
    latest_facilities: dict[str, dict[str, str]] = {}
    for row in facility_rows:
        hk = row["hk_facility"]
        current = latest_facilities.get(hk)
        if current is None or row["load_dts"] >= current["load_dts"]:
            latest_facilities[hk] = row

    rows = [
        {
            "hkFacility": hk,
            "facilityName": row.get("facility_name", hk),
            "country": row.get("country", ""),
            "gridRegion": row.get("grid_region", ""),
            "readOnly": True,
        }
        for hk, row in latest_facilities.items()
    ]
    rows.sort(key=lambda item: item["facilityName"])
    return rows
