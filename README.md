# GreenTrace Database and Warehousing Project

GreenTrace is an ESG data warehousing project for carbon-emission tracking, carbon-credit ledger management, data lineage, and dashboard-based reporting. It demonstrates a complete Data Vault 2.0 style warehouse using MySQL, Python ETL scripts, backend APIs, exported datasets, reports, and a frontend dashboard.

## Project Highlights

- Designs a Data Vault 2.0 warehouse with hubs, links, satellites, business vault tables, and data marts.
- Loads ESG and sustainability datasets into MySQL through Python ETL scripts.
- Calculates Scope 2 and Scope 3 emissions.
- Implements a carbon-credit ledger to track issue and retire transactions.
- Maintains lineage from source data to reporting-ready data marts.
- Provides dashboard and architecture pages for presentation and review.

## Tech Stack

| Area | Tools |
| --- | --- |
| Database | MySQL |
| ETL | Python, Pandas, SQLAlchemy, PyMySQL |
| Backend | Flask, Flask-CORS |
| Frontend | HTML, CSS, JavaScript |
| Reporting | PDF report, phase reports, PowerPoint presentation |
| Architecture | Data Vault 2.0, carbon ledger, ESG data mart |

## Repository Structure

```text
.
|-- sql/
|   +-- create_schema.sql
|-- etl/
|   |-- load_csv_to_mysql.py
|   |-- calc_emissions.py
|   |-- ledger_pipeline.py
|   |-- datamart_pipeline.py
|   +-- lineage_pipeline.py
|-- backend/
|   +-- app.py
|-- frontend/
|   |-- index.html
|   |-- dashboard.html
|   +-- architecture.html
|-- datasets/
|-- reports/
|-- Report.pdf
|-- PPT.pptx
|-- .env.example
```

## Implementation Phases

| Phase | Work Completed |
| --- | --- |
| 1 | Dataset analysis and source-file review |
| 2 | Data Vault 2.0 schema design in MySQL |
| 3 | Python ETL pipeline for loading and cleaning data |
| 4 | Scope 2 and Scope 3 emissions calculation |
| 5 | Carbon-credit ledger with issue/retire tracking |
| 6 | Data mart for CSRD-style reporting |
| 7 | Data lineage tracking for auditability |
| 8 | Dashboard and visualization layer |

## Setup

Create a local environment file:

```cmd
copy .env.example .env
```

Update `.env` with your local MySQL credentials.

Install Python dependencies:

```cmd
pip install flask flask-cors pandas sqlalchemy pymysql python-dotenv
```

Create the warehouse schema using:

```text
sql/create_schema.sql
```

## How to Run

Load datasets into MySQL:

```cmd
python etl\load_csv_to_mysql.py
```

Calculate emissions:

```cmd
python etl\calc_emissions.py
```

Build the reporting data mart:

```cmd
python etl\datamart_pipeline.py
```

Run the live frontend flow:

```cmd
run_live_frontend.cmd
```

## Results

The project implements an auditable ESG warehouse that connects raw sustainability data, emissions calculations, carbon-credit accounting, lineage tracking, and dashboard-ready reporting outputs. The final report documents a full eight-phase implementation and shows how structured warehousing improves traceability for carbon reporting.

## Notes

Local `.env` files, logs, command outputs, and Python cache files are intentionally excluded from GitHub.
