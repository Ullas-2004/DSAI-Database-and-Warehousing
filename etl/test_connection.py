from db_config import create_db_engine

engine = create_db_engine()

connection = engine.connect()

print("Connected to MySQL successfully!")

connection.close()
