# GreenTrace Database and Warehousing Project

GreenTrace is a database and warehousing project for ESG/carbon emission tracking. The project includes a MySQL warehouse schema, ETL scripts, sample exported datasets, backend APIs, and a frontend dashboard.

## Contents

- `sql/create_schema.sql` - warehouse schema definition
- `etl/` - CSV loading, emissions calculation, ledger, data mart, and lineage pipelines
- `backend/` - backend API and live data modules
- `frontend/` - dashboard and architecture pages
- `datasets/` - sample GreenTrace CSV export
- `reports/` - phase reports and final report notes
- `PPT.pptx` - project presentation
- `Report.pdf` - final project report
- `.env.example` - example database connection configuration

## Setup

Create a local `.env` file from `.env.example` and update the password/database URL for your MySQL setup.

```cmd
copy .env.example .env
```

Install the Python packages used by the backend and ETL scripts:

```cmd
pip install flask flask-cors pandas sqlalchemy pymysql python-dotenv
```

## Run

Create the database schema using `sql/create_schema.sql`, then run the ETL scripts from the project root as needed:

```cmd
python etl\load_csv_to_mysql.py
python etl\calc_emissions.py
python etl\datamart_pipeline.py
```

Start the backend/live frontend flow:

```cmd
run_live_frontend.cmd
```

## Notes

The local `.env`, logs, generated command outputs, and Python cache files are intentionally ignored and not uploaded to GitHub.
