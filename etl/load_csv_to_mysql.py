import os
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from db_config import create_db_engine

ENGINE = create_db_engine()
DATASET_PATH = Path("../datasets/green_trace_export/green_trace_export_20260310_195112")

LOAD_ORDER = [
    ("ref_emission_factor.csv", "ref_emission_factor"),
    ("hub_facility.csv", "hub_facility"),
    ("hub_supplier.csv", "hub_supplier"),
    ("hub_meter.csv", "hub_meter"),
    ("hub_shipment.csv", "hub_shipment"),
    ("hub_carbon_credit.csv", "hub_carbon_credit"),
    ("hub_reporting_period.csv", "hub_reporting_period"),
    ("link_facility_meter.csv", "link_facility_meter"),
    ("link_facility_period.csv", "link_facility_period"),
    ("link_shipment_supplier_facility.csv", "link_shipment_supplier_facility"),
    ("sat_facility_attr.csv", "sat_facility_attr"),
    ("sat_supplier_attr.csv", "sat_supplier_attr"),
    ("sat_energy_reading.csv", "sat_energy_reading"),
    ("sat_shipment_activity.csv", "sat_shipment_activity"),
    ("sat_manual_esg_metrics.csv", "sat_manual_esg_metrics"),
    ("sat_carbon_credit_attr.csv", "sat_carbon_credit_attr"),
    ("bv_scope2_emission_event.csv", "bv_scope2_emission_event"),
    ("bv_scope3_emission_event.csv", "bv_scope3_emission_event"),
    ("ledger_credit_txn.csv", "ledger_credit_txn"),
    ("ledger_credit_position.csv", "ledger_credit_position"),
    ("dm_csrds_emissions_summary.csv", "dm_csrds_emissions_summary"),
    ("meta_lineage_edge.csv", "meta_lineage_edge"),
]


def table_count(table_name: str) -> int:
    with ENGINE.connect() as conn:
        return conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar_one()


def load_table(csv_name: str, table_name: str) -> tuple[int, int]:
    file_path = DATASET_PATH / csv_name
    if not file_path.exists():
        raise FileNotFoundError(f"Missing file: {file_path}")

    df = pd.read_csv(file_path)
    csv_rows = len(df)

    print(f"\nLoading {table_name} from {csv_name}...")
    print(f"Rows in CSV: {csv_rows}")

    before = table_count(table_name)
    if csv_rows > 0:
        df.to_sql(table_name, ENGINE, if_exists="append", index=False, method="multi", chunksize=1000)
    after = table_count(table_name)

    inserted = after - before
    print(f"Rows inserted: {inserted}")
    print(f"Rows in DB now: {after}")

    if inserted != csv_rows:
        raise RuntimeError(
            f"Row mismatch for {table_name}: csv_rows={csv_rows}, inserted={inserted}, before={before}, after={after}"
        )

    print(f"{table_name} loaded successfully")
    return csv_rows, inserted


def clear_all_tables() -> None:
    with ENGINE.begin() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
        try:
            for _, table_name in reversed(LOAD_ORDER):
                conn.execute(text(f"DELETE FROM {table_name}"))
        finally:
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
    print("All target tables cleared.")


def main() -> None:
    truncate_first = os.environ.get("TRUNCATE_FIRST", "1") == "1"

    total_csv_rows = 0
    total_inserted = 0

    if truncate_first:
        clear_all_tables()

    for csv_name, table_name in LOAD_ORDER:
        csv_rows, inserted = load_table(csv_name, table_name)
        total_csv_rows += csv_rows
        total_inserted += inserted

    print("\n" + "=" * 70)
    print("ETL completed successfully")
    print(f"Total CSV rows processed: {total_csv_rows}")
    print(f"Total DB rows inserted : {total_inserted}")


if __name__ == "__main__":
    main()
