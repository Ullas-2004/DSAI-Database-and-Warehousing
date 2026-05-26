from sqlalchemy import text

from db_config import create_db_engine

engine = create_db_engine()

with engine.begin() as conn:

    # Temporarily disable foreign key checks to allow testing without populating all hubs
    conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))

    # Clear datamart table for clean rerun
    conn.execute(text("DELETE FROM dm_csrds_emissions_summary"))
    print("Datamart table cleared")

    # Insert CSRD emissions summary using Data Vault 2.0 schema relations
    # We aggregate scope2 (from energy readings), scope3 (from shipments), 
    # and offset credits (from ledger) per facility and reporting period
    conn.execute(text("""
        INSERT INTO dm_csrds_emissions_summary
        (hk_facility, hk_period, scope1_kgco2e, scope2_kgco2e, scope3_kgco2e, credits_retired_t, net_emissions_kgco2e, generated_ts)
        
        SELECT 
            f.hk_facility,
            rp.hk_period,
            0 AS scope1_kgco2e, -- To be implemented in future phase if needed
            COALESCE(SUM(s2.scope2_kgco2e), 0) AS scope2_kgco2e,
            COALESCE(SUM(s3.scope3_kgco2e), 0) AS scope3_kgco2e,
            COALESCE(SUM(lct.tonnes), 0) AS credits_retired_t,
            -- Convert scope 2 & 3 from kg to tonnes (divide by 1000) for net emissions comparison, 
            -- then subtract retired credits
            (COALESCE(SUM(s2.scope2_kgco2e), 0) + COALESCE(SUM(s3.scope3_kgco2e), 0)) / 1000.0 - COALESCE(SUM(lct.tonnes), 0) AS net_emissions_kgco2e,
            NOW() AS generated_ts
            
        FROM hub_facility f
        
        CROSS JOIN hub_reporting_period rp
        
        -- Scope 2 Emissions (Facility -> Meter -> Event)
        LEFT JOIN link_facility_meter lfm
            ON f.hk_facility = lfm.hk_facility
        LEFT JOIN bv_scope2_emission_event s2
            ON lfm.hk_meter = s2.hk_meter AND s2.hk_period = rp.hk_period
            
        -- Scope 3 Emissions (Facility -> Shipment -> Event)
        LEFT JOIN link_shipment_supplier_facility lssf
            ON f.hk_facility = lssf.hk_facility
        LEFT JOIN bv_scope3_emission_event s3
            ON lssf.hk_shipment = s3.hk_shipment AND s3.hk_period = rp.hk_period
            
        -- Carbon Credits Retired (Facility -> Ledger)
        LEFT JOIN ledger_credit_txn lct
            ON f.hk_facility = lct.hk_facility AND lct.hk_period = rp.hk_period AND lct.txn_type = 'RETIRE'
            
        GROUP BY 
            f.hk_facility,
            rp.hk_period;
    """))

    print("CSRD Datamart populated successfully")
    conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
