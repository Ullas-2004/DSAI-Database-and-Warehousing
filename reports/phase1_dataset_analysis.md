# Phase 1 - Dataset Analysis and Data Vault 2.0 Mapping

## 1) Dataset File Inventory
Source folder: `datasets/green_trace_export/green_trace_export_20260310_195112`

Total files: **25**
- README.txt
- bv_scope2_emission_event.csv
- bv_scope3_emission_event.csv
- dm_csrds_emissions_summary.csv
- hub_carbon_credit.csv
- hub_facility.csv
- hub_meter.csv
- hub_reporting_period.csv
- hub_shipment.csv
- hub_supplier.csv
- ledger_credit_position.csv
- ledger_credit_txn.csv
- link_facility_meter.csv
- link_facility_period.csv
- link_shipment_supplier_facility.csv
- manifest.json
- meta_lineage_edge.csv
- python
- ref_emission_factor.csv
- sat_carbon_credit_attr.csv
- sat_energy_reading.csv
- sat_facility_attr.csv
- sat_manual_esg_metrics.csv
- sat_shipment_activity.csv
- sat_supplier_attr.csv

CSV datasets: **22**

## 2) Data Vault 2.0 Categorization

### Hub Tables
- `hub_facility` - company facilities
- `hub_supplier` - supply chain partners
- `hub_meter` - energy meters
- `hub_shipment` - logistics shipments
- `hub_carbon_credit` - carbon credit assets
- `hub_reporting_period` - reporting periods

### Link Tables
- `link_facility_meter` - facility <-> meter
- `link_facility_period` - facility <-> reporting period
- `link_shipment_supplier_facility` - shipment <-> supplier <-> facility

### Satellite Tables
- `sat_facility_attr` - facility descriptive attributes
- `sat_supplier_attr` - supplier descriptive attributes
- `sat_energy_reading` - meter reading events
- `sat_shipment_activity` - shipment activity and fuel usage
- `sat_manual_esg_metrics` - manually entered ESG metrics
- `sat_carbon_credit_attr` - carbon credit descriptive attributes

### Reference Table
- `ref_emission_factor` - emission conversion factors

### Business Vault Tables
- `bv_scope2_emission_event` - calculated scope-2 emissions from electricity
- `bv_scope3_emission_event` - calculated scope-3 emissions from transport activity

### Ledger Tables
- `ledger_credit_txn` - carbon credit transactions
- `ledger_credit_position` - carbon credit balance snapshots

### Data Mart
- `dm_csrds_emissions_summary` - reporting-ready emissions summary

### Metadata
- `meta_lineage_edge` - lineage edge tracking across transformations

## 3) Column Structure by Dataset

| Dataset | Type | Row Count | Columns |
|---|---|---:|---|
| hub_facility | Hub | 25 | `hk_facility`, `facility_bk`, `load_dts`, `record_source` |
| hub_supplier | Hub | 12 | `hk_supplier`, `supplier_bk`, `load_dts`, `record_source` |
| hub_meter | Hub | 100 | `hk_meter`, `meter_bk`, `load_dts`, `record_source` |
| hub_shipment | Hub | 40 | `hk_shipment`, `shipment_bk`, `load_dts`, `record_source` |
| hub_carbon_credit | Hub | 10 | `hk_credit`, `credit_bk`, `load_dts`, `record_source` |
| hub_reporting_period | Hub | 1 | `hk_period`, `period_bk`, `load_dts`, `record_source` |
| link_facility_meter | Link | 100 | `hk_facility_meter`, `hk_facility`, `hk_meter`, `load_dts`, `record_source` |
| link_facility_period | Link | 25 | `hk_facility_period`, `hk_facility`, `hk_period`, `load_dts`, `record_source` |
| link_shipment_supplier_facility | Link | 40 | `hk_ssf`, `hk_shipment`, `hk_supplier`, `hk_facility`, `load_dts`, `record_source` |
| sat_facility_attr | Satellite | 25 | `hk_facility`, `load_dts`, `record_source`, `hashdiff`, `facility_name`, `country`, `grid_region` |
| sat_supplier_attr | Satellite | 12 | `hk_supplier`, `load_dts`, `record_source`, `hashdiff`, `supplier_name`, `sector`, `country` |
| sat_energy_reading | Satellite | 2400 | `hk_meter`, `reading_ts`, `load_dts`, `record_source`, `hashdiff`, `kwh_value`, `quality_flag` |
| sat_shipment_activity | Satellite | 40 | `hk_shipment`, `load_dts`, `record_source`, `hashdiff`, `route_from`, `route_to`, `distance_km`, `vehicle_type`, `fuel_type`, `fuel_used_l` |
| sat_manual_esg_metrics | Satellite | 0 | `hk_facility_period`, `load_dts`, `record_source`, `hashdiff`, `workforce_total`, `women_pct`, `waste_kg`, `water_m3` |
| sat_carbon_credit_attr | Satellite | 10 | `hk_credit`, `load_dts`, `record_source`, `hashdiff`, `registry_name`, `project_id`, `vintage_year`, `co2e_tonnes` |
| ref_emission_factor | Reference | 6 | `factor_id`, `activity_type`, `region`, `unit`, `kgco2e_per_unit`, `valid_from`, `valid_to`, `source` |
| bv_scope2_emission_event | Business Vault | 2400 | `event_id`, `hk_facility`, `hk_meter`, `hk_period`, `factor_id`, `reading_ts`, `kwh_value`, `scope2_kgco2e`, `raw_record_hash`, `transform_ver`, `load_dts`, `record_source` |
| bv_scope3_emission_event | Business Vault | 40 | `event_id`, `hk_facility`, `hk_shipment`, `hk_period`, `factor_id`, `activity_value`, `scope3_kgco2e`, `raw_record_hash`, `transform_ver`, `load_dts`, `record_source` |
| ledger_credit_txn | Ledger | 0 | `txn_id`, `hk_credit`, `txn_type`, `tonnes`, `txn_ts`, `hk_facility`, `hk_period`, `source_doc_id`, `load_dts`, `record_source` |
| ledger_credit_position | Ledger | 0 | `hk_credit`, `status`, `owner_entity`, `current_balance_tonnes`, `as_of_dts`, `load_dts`, `record_source` |
| dm_csrds_emissions_summary | Data Mart | 0 | `hk_facility`, `hk_period`, `scope1_kgco2e`, `scope2_kgco2e`, `scope3_kgco2e`, `credits_retired_t`, `net_emissions_kgco2e`, `generated_ts` |
| meta_lineage_edge | Metadata | 0 | `edge_id`, `from_table`, `from_key`, `to_table`, `to_key`, `transform_name`, `transform_ver`, `executed_ts` |

## 4) Key Column Validation (Hashed Keys)
Data Vault hashed keys are consistently present via `hk_` fields.

Examples:
- `hk_facility` in `hub_facility`, `link_*`, `sat_facility_attr`, `bv_*`, `ledger_credit_txn`, `dm_csrds_emissions_summary`
- `hk_meter` in `hub_meter`, `link_facility_meter`, `sat_energy_reading`, `bv_scope2_emission_event`
- `hk_shipment` in `hub_shipment`, `link_shipment_supplier_facility`, `sat_shipment_activity`, `bv_scope3_emission_event`
- `hk_supplier` in `hub_supplier`, `link_shipment_supplier_facility`, `sat_supplier_attr`
- `hk_credit` in `hub_carbon_credit`, `sat_carbon_credit_attr`, `ledger_*`
- `hk_period` in `hub_reporting_period`, `link_facility_period`, `bv_*`, `ledger_credit_txn`, `dm_csrds_emissions_summary`
- `hk_facility_period` in `link_facility_period` and `sat_manual_esg_metrics`

Example (energy satellite):
- `hk_meter` - hashed meter key
- `reading_ts` - reading timestamp
- `kwh_value` - energy consumption
- `quality_flag` - reading quality status

## 5) Notes for Report/Viva
- `load_dts` and `record_source` are present across vault layers, supporting auditability and lineage.
- Satellite tables use `hashdiff`, enabling change detection for historization.
- Some downstream/reporting datasets are currently empty (`dm_csrds_emissions_summary`, `ledger_*`, `meta_lineage_edge`, `sat_manual_esg_metrics`), which is acceptable for a staged pipeline and should be mentioned as current load status.

## 6) Scripts Added in ETL
- `etl/list_datasets.py` - prints all files and total count in export folder
- `etl/inspect_datasets.py` - inspects all CSVs: columns, dtypes, shape, sample rows

Phase 1 status: **Completed**
