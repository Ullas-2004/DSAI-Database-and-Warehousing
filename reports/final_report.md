# Final Project Report: GreenTrace ESG Data Vault

## 1. Introduction
This report documents the implementation of the GreenTrace project, an ESG Data Vault 2.0 system designed to track, calculate, and report carbon emissions (Scope 2 and Scope 3) alongside a carbon credit ledger to prevent double counting. The system provides a scalable foundation for enterprise-level carbon accounting.

## 2. Problem Statement
Organizations struggle with fragmented ESG data, leading to inaccurate reporting and lack of traceability. There is a critical need for a robust data architecture to handle complex supply chain logistics, energy consumption, and carbon reporting in full compliance with CSRD (Corporate Sustainability Reporting Directive) requirements.

## 3. Architecture
The project utilizes the Data Vault 2.0 methodology. The architecture is split into:
- **Raw Vault**: Hubs (core business entities), Links (relationships), and Satellites (context/attributes).
- **Business Vault**: Applied business logic for calculating emissions (Scope 2 and Scope 3).
- **Carbon Ledger**: A ledger system to securely track the issuance and retirement of carbon credits.
- **Data Mart**: Aggregated data ready for enterprise reporting and analytical dashboards.

## 4. Phase 1 → Phase 8

### Phase 1: Dataset Analysis
Analyzed 25 source files (22 CSV datasets) and categorized them into Data Vault 2.0 components, establishing the structural foundation for the project.

### Phase 2: Data Warehouse Schema Design
Designed and implemented the Data Vault 2.0 schema in MySQL, resulting in 22 tables including hubs, links, satellites, and business vault elements. Primary keys, foreign keys, and indexes were implemented correctly for performance and data integrity.

### Phase 3: ETL Pipeline Implementation
Developed an ETL pipeline using Python, Pandas, and SQLAlchemy to extract, transform, and load data into the MySQL database. Handled duplicates and missing values, successfully processing 5286 rows.

### Phase 4: Business Vault Implementation
Computed Scope 2 (electricity) and Scope 3 (transportation fuel) emissions using raw data and emission factors, outputting results into specialized computational event tables.

### Phase 5: Carbon Credit Ledger
Developed a ledger system to record carbon credit transactions (ISSUE/RETIRE) and maintain accurate balance positions, inherently preventing double counting of carbon offsets.

### Phase 6: Data Mart Creation
Created a reporting layer (`dm_csrds_emissions_summary`) aggregating facility-level emissions and tracked carbon credits per reporting period for streamlined CSRD compliance reporting.

### Phase 7: Data Lineage Tracking
Implemented data lineage tracking (`meta_lineage_edge`) to map data flow from source satellites directly to the final data mart, ensuring end-to-end auditability of data transformations.

### Phase 8: Dashboard and Visualization
Built interactive visual dashboards (utilizing Power BI and Streamlit) to visualize total emissions, compare Scope 2 vs Scope 3, analyze facility performance, and monitor active carbon credit balances.

## 5. Results
The implementation resulted in a fully functional, auditable, and idempotent Data Vault 2.0 architecture processing all target rows perfectly across every vault layer, culminating in an aggregation structure instantly ready for regulatory compliance assessments.

## 6. Conclusion
The GreenTrace project successfully demonstrates how Data Vault 2.0 and a structured Python ETL process solve complex ESG data challenges. By ensuring complete lineage, a scalable schema design, and fully auditable computation logic, the system effectively resolves accuracy and tracking issues in carbon reporting.
