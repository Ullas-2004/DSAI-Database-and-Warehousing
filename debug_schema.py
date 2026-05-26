from sqlalchemy import text
import traceback

from etl.db_config import create_db_engine

engine = create_db_engine()

with open("schema_out.txt", "w") as f:
    try:
        with engine.connect() as conn:
            f.write("Schema for ledger_credit_txn:\n")
            try:
                res = conn.execute(text("DESCRIBE ledger_credit_txn"))
                for row in res:
                    f.write(str(row) + "\n")
            except Exception as e:
                f.write("Error describing txn: " + str(e) + "\n")
                
            f.write("\nSchema for ledger_credit_position:\n")
            try:
                res = conn.execute(text("DESCRIBE ledger_credit_position"))
                for row in res:
                    f.write(str(row) + "\n")
            except Exception as e:
                f.write("Error describing position: " + str(e) + "\n")
                
            f.write("\nRunning ledger pipeline query 1:\n")
            try:
                res = conn.execute(text("""
                    INSERT INTO ledger_credit_txn
                    (credit_id, txn_type, amount, txn_date)
                    VALUES
                    ('CR1001','ISSUE',1000,'2026-01-01'),
                    ('CR1002','ISSUE',500,'2026-01-01'),
                    ('CR1003','ISSUE',300,'2026-01-01')
                """))
                f.write("Success!\n")
            except Exception as e:
                f.write("Error on INSERT: " + str(e) + "\n")
                
    except Exception as e:
        f.write(traceback.format_exc())
