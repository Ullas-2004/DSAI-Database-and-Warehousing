from sqlalchemy import text

from db_config import create_db_engine

ENGINE = create_db_engine()
TRANSFORM_VERSION = "phase4_calc_v1"
RECORD_SOURCE = "BV_CALC"

SCOPE2_INSERT_SQL = """
INSERT INTO bv_scope2_emission_event
(
    event_id,
    hk_facility,
    hk_meter,
    hk_period,
    factor_id,
    reading_ts,
    kwh_value,
    scope2_kgco2e,
    raw_record_hash,
    transform_ver,
    load_dts,
    record_source
)
SELECT
    (@scope2_event_id := @scope2_event_id + 1) AS event_id,
    src.hk_facility,
    src.hk_meter,
    src.hk_period,
    src.factor_id,
    src.reading_ts,
    src.kwh_value,
    ROUND(src.kwh_value * src.emission_factor, 4) AS scope2_kgco2e,
    MD5(
        CONCAT_WS(
            '|',
            src.hk_meter,
            DATE_FORMAT(src.reading_ts, '%Y-%m-%d %H:%i:%s'),
            CAST(src.kwh_value AS CHAR),
            CAST(src.emission_factor AS CHAR)
        )
    ) AS raw_record_hash,
    :transform_ver AS transform_ver,
    NOW(6) AS load_dts,
    :record_source AS record_source
FROM (
    SELECT
        lfm.hk_facility,
        er.hk_meter,
        lfp.hk_period,
        ef.factor_id,
        er.reading_ts,
        er.kwh_value,
        ef.kgco2e_per_unit AS emission_factor
    FROM sat_energy_reading er
    JOIN (
        SELECT lm.hk_meter, lm.hk_facility
        FROM link_facility_meter lm
        JOIN (
            SELECT hk_meter, MAX(load_dts) AS max_load_dts
            FROM link_facility_meter
            GROUP BY hk_meter
        ) latest_lm
            ON latest_lm.hk_meter = lm.hk_meter
           AND latest_lm.max_load_dts = lm.load_dts
    ) lfm
        ON lfm.hk_meter = er.hk_meter
    JOIN (
        SELECT fa.hk_facility, fa.grid_region
        FROM sat_facility_attr fa
        JOIN (
            SELECT hk_facility, MAX(load_dts) AS max_load_dts
            FROM sat_facility_attr
            GROUP BY hk_facility
        ) latest_fa
            ON latest_fa.hk_facility = fa.hk_facility
           AND latest_fa.max_load_dts = fa.load_dts
    ) sfa
        ON sfa.hk_facility = lfm.hk_facility
    JOIN (
        SELECT hk_facility, hk_period, MAX(load_dts) AS load_dts
        FROM link_facility_period
        GROUP BY hk_facility, hk_period
    ) lfp
        ON lfp.hk_facility = lfm.hk_facility
    JOIN hub_reporting_period hp
        ON hp.hk_period = lfp.hk_period
    JOIN ref_emission_factor ef
        ON ef.activity_type = 'kwh'
       AND ef.region = sfa.grid_region
       AND DATE(er.reading_ts) BETWEEN ef.valid_from AND ef.valid_to
    WHERE CAST(SUBSTRING(hp.period_bk, 1, 4) AS UNSIGNED) = YEAR(er.reading_ts)
      AND CAST(SUBSTRING(hp.period_bk, 6, 1) AS UNSIGNED) = QUARTER(er.reading_ts)
) src
ORDER BY src.hk_meter, src.reading_ts, src.factor_id
"""

SCOPE3_INSERT_SQL = """
INSERT INTO bv_scope3_emission_event
(
    event_id,
    hk_facility,
    hk_shipment,
    hk_period,
    factor_id,
    activity_value,
    scope3_kgco2e,
    raw_record_hash,
    transform_ver,
    load_dts,
    record_source
)
SELECT
    (@scope3_event_id := @scope3_event_id + 1) AS event_id,
    src.hk_facility,
    src.hk_shipment,
    src.hk_period,
    src.factor_id,
    src.activity_value,
    ROUND(src.activity_value * src.emission_factor, 4) AS scope3_kgco2e,
    MD5(
        CONCAT_WS(
            '|',
            src.hk_shipment,
            CAST(src.activity_value AS CHAR),
            CAST(src.emission_factor AS CHAR),
            DATE_FORMAT(src.activity_ts, '%Y-%m-%d %H:%i:%s')
        )
    ) AS raw_record_hash,
    :transform_ver AS transform_ver,
    NOW(6) AS load_dts,
    :record_source AS record_source
FROM (
    SELECT
        lssf.hk_facility,
        sa.hk_shipment,
        lfp.hk_period,
        ef.factor_id,
        sa.fuel_used_l AS activity_value,
        sa.load_dts AS activity_ts,
        ef.kgco2e_per_unit AS emission_factor
    FROM sat_shipment_activity sa
    JOIN (
        SELECT ssf.hk_shipment, ssf.hk_facility
        FROM link_shipment_supplier_facility ssf
        JOIN (
            SELECT hk_shipment, MAX(load_dts) AS max_load_dts
            FROM link_shipment_supplier_facility
            GROUP BY hk_shipment
        ) latest_ssf
            ON latest_ssf.hk_shipment = ssf.hk_shipment
           AND latest_ssf.max_load_dts = ssf.load_dts
    ) lssf
        ON lssf.hk_shipment = sa.hk_shipment
    JOIN (
        SELECT hk_facility, hk_period, MAX(load_dts) AS load_dts
        FROM link_facility_period
        GROUP BY hk_facility, hk_period
    ) lfp
        ON lfp.hk_facility = lssf.hk_facility
    JOIN hub_reporting_period hp
        ON hp.hk_period = lfp.hk_period
    JOIN ref_emission_factor ef
        ON ef.activity_type = CONCAT(sa.fuel_type, '_l')
       AND DATE(sa.load_dts) BETWEEN ef.valid_from AND ef.valid_to
    WHERE CAST(SUBSTRING(hp.period_bk, 1, 4) AS UNSIGNED) = YEAR(sa.load_dts)
      AND CAST(SUBSTRING(hp.period_bk, 6, 1) AS UNSIGNED) = QUARTER(sa.load_dts)
) src
ORDER BY src.hk_shipment, src.activity_ts
"""


def table_count(conn, table_name: str) -> int:
    return conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar_one()


def fetch_rows(conn, sql: str):
    return conn.execute(text(sql)).fetchall()


def main() -> None:
    with ENGINE.begin() as conn:
        expected_scope2 = table_count(conn, "sat_energy_reading")
        expected_scope3 = table_count(conn, "sat_shipment_activity")

        conn.execute(text("DELETE FROM bv_scope3_emission_event"))
        conn.execute(text("DELETE FROM bv_scope2_emission_event"))

        conn.execute(text("SET @scope2_event_id := 0"))
        conn.execute(
            text(SCOPE2_INSERT_SQL),
            {"transform_ver": TRANSFORM_VERSION, "record_source": RECORD_SOURCE},
        )

        actual_scope2 = table_count(conn, "bv_scope2_emission_event")
        if actual_scope2 != expected_scope2:
            raise RuntimeError(
                f"Scope 2 row mismatch: expected={expected_scope2}, actual={actual_scope2}"
            )

        conn.execute(
            text(
                "SET @scope3_event_id := (SELECT COALESCE(MAX(event_id), 0) FROM bv_scope2_emission_event)"
            )
        )
        conn.execute(
            text(SCOPE3_INSERT_SQL),
            {"transform_ver": TRANSFORM_VERSION, "record_source": RECORD_SOURCE},
        )

        actual_scope3 = table_count(conn, "bv_scope3_emission_event")
        if actual_scope3 != expected_scope3:
            raise RuntimeError(
                f"Scope 3 row mismatch: expected={expected_scope3}, actual={actual_scope3}"
            )

        scope2_preview = fetch_rows(
            conn,
            """
            SELECT event_id, hk_meter, kwh_value, scope2_kgco2e
            FROM bv_scope2_emission_event
            ORDER BY event_id
            LIMIT 5
            """,
        )
        scope3_preview = fetch_rows(
            conn,
            """
            SELECT event_id, hk_shipment, activity_value, scope3_kgco2e
            FROM bv_scope3_emission_event
            ORDER BY event_id
            LIMIT 5
            """,
        )

    print("Business Vault emission calculations completed.")
    print(f"Scope 2 rows inserted: {actual_scope2}")
    print(f"Scope 3 rows inserted: {actual_scope3}")
    print("\nScope 2 sample:")
    for row in scope2_preview:
        print(row)
    print("\nScope 3 sample:")
    for row in scope3_preview:
        print(row)


if __name__ == "__main__":
    main()
