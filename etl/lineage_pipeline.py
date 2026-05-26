from sqlalchemy import text

from db_config import create_db_engine

engine = create_db_engine()

with engine.begin() as conn:

    print("Starting lineage pipeline...")

    # Clear table for rerun
    conn.execute(text("DELETE FROM meta_lineage_edge"))

    print("Old lineage cleared")

    # Insert lineage relationships
    conn.execute(text("""
    INSERT INTO meta_lineage_edge
    (source_table, target_table, transformation)

    VALUES

    -- Scope 2 lineage
    ('sat_energy_reading','bv_scope2_emission_event','kwh_value × emission_factor'),
    ('bv_scope2_emission_event','dm_csrds_emissions_summary','aggregation by facility'),

    -- Scope 3 lineage
    ('sat_shipment_activity','bv_scope3_emission_event','fuel_used × emission_factor'),
    ('bv_scope3_emission_event','dm_csrds_emissions_summary','aggregation by facility'),

    -- Carbon credit lineage
    ('ledger_credit_txn','ledger_credit_position','credit balance calculation'),
    ('ledger_credit_position','dm_csrds_emissions_summary','credit offset applied')
    """))

    print("Lineage relationships inserted")

print("Lineage pipeline completed successfully")
