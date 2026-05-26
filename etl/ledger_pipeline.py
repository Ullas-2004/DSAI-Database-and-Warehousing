from sqlalchemy import text

from db_config import create_db_engine

engine = create_db_engine()

with engine.begin() as conn:
    # Temporarily disable foreign key checks to allow testing without populating all hubs
    conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))

    # Clear ledger tables for clean rerun
    conn.execute(text("DELETE FROM ledger_credit_position"))
    conn.execute(text("DELETE FROM ledger_credit_txn"))

    print("Ledger tables cleared")

    # Example: Issue carbon credits
    conn.execute(text("""
        INSERT INTO ledger_credit_txn
        (txn_id, hk_credit, txn_type, tonnes, txn_ts, load_dts, record_source)
        VALUES
        (UUID(),'CR1001','ISSUE',1000,'2026-01-01', NOW(), 'PHASE_5'),
        (UUID(),'CR1002','ISSUE',500,'2026-01-01', NOW(), 'PHASE_5'),
        (UUID(),'CR1003','ISSUE',300,'2026-01-01', NOW(), 'PHASE_5')
    """))

    # Example: Consume credits to offset emissions
    conn.execute(text("""
        INSERT INTO ledger_credit_txn
        (txn_id, hk_credit, txn_type, tonnes, txn_ts, load_dts, record_source)
        VALUES
        (UUID(),'CR1001','RETIRE',200,'2026-02-01', NOW(), 'PHASE_5'),
        (UUID(),'CR1002','RETIRE',100,'2026-02-01', NOW(), 'PHASE_5')
    """))

    print("Ledger transactions inserted")

    # Compute credit balance
    conn.execute(text("""
        INSERT INTO ledger_credit_position
        (hk_credit, status, current_balance_tonnes, as_of_dts, load_dts, record_source)

        SELECT
        hk_credit,
        'ACTIVE' AS status,
        SUM(
            CASE
                WHEN txn_type='ISSUE' THEN tonnes
                WHEN txn_type='RETIRE' THEN -tonnes
            END
        ) AS current_balance_tonnes,
        NOW() AS as_of_dts,
        NOW() AS load_dts,
        'PHASE_5'  AS record_source

        FROM ledger_credit_txn
        GROUP BY hk_credit
    """))

    print("Ledger balances calculated")
    conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
