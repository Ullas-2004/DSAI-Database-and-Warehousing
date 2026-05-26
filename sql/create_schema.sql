-- GreenTrace Data Warehouse Schema (Data Vault 2.0)
-- Generated from dataset inspection on 2026-03-11
-- Run with: mysql -u root -p < sql/create_schema.sql

CREATE DATABASE IF NOT EXISTS green_trace_dw;
USE green_trace_dw;

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- Drop in reverse dependency order for idempotent rebuilds
DROP TABLE IF EXISTS dm_csrds_emissions_summary;
DROP TABLE IF EXISTS ledger_credit_position;
DROP TABLE IF EXISTS ledger_credit_txn;
DROP TABLE IF EXISTS bv_scope3_emission_event;
DROP TABLE IF EXISTS bv_scope2_emission_event;
DROP TABLE IF EXISTS sat_manual_esg_metrics;
DROP TABLE IF EXISTS sat_shipment_activity;
DROP TABLE IF EXISTS sat_energy_reading;
DROP TABLE IF EXISTS sat_supplier_attr;
DROP TABLE IF EXISTS sat_facility_attr;
DROP TABLE IF EXISTS sat_carbon_credit_attr;
DROP TABLE IF EXISTS link_shipment_supplier_facility;
DROP TABLE IF EXISTS link_facility_period;
DROP TABLE IF EXISTS link_facility_meter;
DROP TABLE IF EXISTS ref_emission_factor;
DROP TABLE IF EXISTS meta_lineage_edge;
DROP TABLE IF EXISTS hub_carbon_credit;
DROP TABLE IF EXISTS hub_shipment;
DROP TABLE IF EXISTS hub_supplier;
DROP TABLE IF EXISTS hub_meter;
DROP TABLE IF EXISTS hub_reporting_period;
DROP TABLE IF EXISTS hub_facility;

-- Hubs
CREATE TABLE hub_facility (
    hk_facility CHAR(32) PRIMARY KEY,
    facility_bk VARCHAR(50) NOT NULL,
    load_dts DATETIME(6) NOT NULL,
    record_source VARCHAR(50) NOT NULL,
    UNIQUE KEY uq_hub_facility_bk (facility_bk)
) ENGINE=InnoDB;

CREATE TABLE hub_supplier (
    hk_supplier CHAR(32) PRIMARY KEY,
    supplier_bk VARCHAR(50) NOT NULL,
    load_dts DATETIME(6) NOT NULL,
    record_source VARCHAR(50) NOT NULL,
    UNIQUE KEY uq_hub_supplier_bk (supplier_bk)
) ENGINE=InnoDB;

CREATE TABLE hub_meter (
    hk_meter CHAR(32) PRIMARY KEY,
    meter_bk VARCHAR(50) NOT NULL,
    load_dts DATETIME(6) NOT NULL,
    record_source VARCHAR(50) NOT NULL,
    UNIQUE KEY uq_hub_meter_bk (meter_bk)
) ENGINE=InnoDB;

CREATE TABLE hub_shipment (
    hk_shipment CHAR(32) PRIMARY KEY,
    shipment_bk VARCHAR(50) NOT NULL,
    load_dts DATETIME(6) NOT NULL,
    record_source VARCHAR(50) NOT NULL,
    UNIQUE KEY uq_hub_shipment_bk (shipment_bk)
) ENGINE=InnoDB;

CREATE TABLE hub_carbon_credit (
    hk_credit CHAR(32) PRIMARY KEY,
    credit_bk VARCHAR(50) NOT NULL,
    load_dts DATETIME(6) NOT NULL,
    record_source VARCHAR(50) NOT NULL,
    UNIQUE KEY uq_hub_credit_bk (credit_bk)
) ENGINE=InnoDB;

CREATE TABLE hub_reporting_period (
    hk_period CHAR(32) PRIMARY KEY,
    period_bk VARCHAR(50) NOT NULL,
    load_dts DATETIME(6) NOT NULL,
    record_source VARCHAR(50) NOT NULL,
    UNIQUE KEY uq_hub_period_bk (period_bk)
) ENGINE=InnoDB;

-- Links
CREATE TABLE link_facility_meter (
    hk_facility_meter CHAR(32) PRIMARY KEY,
    hk_facility CHAR(32) NOT NULL,
    hk_meter CHAR(32) NOT NULL,
    load_dts DATETIME(6) NOT NULL,
    record_source VARCHAR(50) NOT NULL,
    KEY ix_lfm_hk_facility (hk_facility),
    KEY ix_lfm_hk_meter (hk_meter),
    CONSTRAINT fk_lfm_facility FOREIGN KEY (hk_facility) REFERENCES hub_facility (hk_facility),
    CONSTRAINT fk_lfm_meter FOREIGN KEY (hk_meter) REFERENCES hub_meter (hk_meter)
) ENGINE=InnoDB;

CREATE TABLE link_facility_period (
    hk_facility_period CHAR(32) PRIMARY KEY,
    hk_facility CHAR(32) NOT NULL,
    hk_period CHAR(32) NOT NULL,
    load_dts DATETIME(6) NOT NULL,
    record_source VARCHAR(50) NOT NULL,
    KEY ix_lfp_hk_facility (hk_facility),
    KEY ix_lfp_hk_period (hk_period),
    CONSTRAINT fk_lfp_facility FOREIGN KEY (hk_facility) REFERENCES hub_facility (hk_facility),
    CONSTRAINT fk_lfp_period FOREIGN KEY (hk_period) REFERENCES hub_reporting_period (hk_period)
) ENGINE=InnoDB;

CREATE TABLE link_shipment_supplier_facility (
    hk_ssf CHAR(32) PRIMARY KEY,
    hk_shipment CHAR(32) NOT NULL,
    hk_supplier CHAR(32) NOT NULL,
    hk_facility CHAR(32) NOT NULL,
    load_dts DATETIME(6) NOT NULL,
    record_source VARCHAR(50) NOT NULL,
    KEY ix_lssf_hk_shipment (hk_shipment),
    KEY ix_lssf_hk_supplier (hk_supplier),
    KEY ix_lssf_hk_facility (hk_facility),
    CONSTRAINT fk_lssf_shipment FOREIGN KEY (hk_shipment) REFERENCES hub_shipment (hk_shipment),
    CONSTRAINT fk_lssf_supplier FOREIGN KEY (hk_supplier) REFERENCES hub_supplier (hk_supplier),
    CONSTRAINT fk_lssf_facility FOREIGN KEY (hk_facility) REFERENCES hub_facility (hk_facility)
) ENGINE=InnoDB;

-- Satellites
CREATE TABLE sat_facility_attr (
    hk_facility CHAR(32) NOT NULL,
    load_dts DATETIME(6) NOT NULL,
    record_source VARCHAR(50) NOT NULL,
    hashdiff CHAR(32) NOT NULL,
    facility_name VARCHAR(100),
    country VARCHAR(10),
    grid_region VARCHAR(50),
    PRIMARY KEY (hk_facility, load_dts),
    KEY ix_sfa_hk_facility (hk_facility),
    CONSTRAINT fk_sfa_facility FOREIGN KEY (hk_facility) REFERENCES hub_facility (hk_facility)
) ENGINE=InnoDB;

CREATE TABLE sat_supplier_attr (
    hk_supplier CHAR(32) NOT NULL,
    load_dts DATETIME(6) NOT NULL,
    record_source VARCHAR(50) NOT NULL,
    hashdiff CHAR(32) NOT NULL,
    supplier_name VARCHAR(100),
    sector VARCHAR(100),
    country VARCHAR(10),
    PRIMARY KEY (hk_supplier, load_dts),
    KEY ix_ssa_hk_supplier (hk_supplier),
    CONSTRAINT fk_ssa_supplier FOREIGN KEY (hk_supplier) REFERENCES hub_supplier (hk_supplier)
) ENGINE=InnoDB;

CREATE TABLE sat_energy_reading (
    hk_meter CHAR(32) NOT NULL,
    reading_ts DATETIME NOT NULL,
    load_dts DATETIME(6) NOT NULL,
    record_source VARCHAR(50) NOT NULL,
    hashdiff CHAR(32) NOT NULL,
    kwh_value DECIMAL(12,4),
    quality_flag VARCHAR(20),
    PRIMARY KEY (hk_meter, reading_ts, load_dts),
    KEY ix_ser_hk_meter (hk_meter),
    CONSTRAINT fk_ser_meter FOREIGN KEY (hk_meter) REFERENCES hub_meter (hk_meter)
) ENGINE=InnoDB;

CREATE TABLE sat_shipment_activity (
    hk_shipment CHAR(32) NOT NULL,
    load_dts DATETIME(6) NOT NULL,
    record_source VARCHAR(50) NOT NULL,
    hashdiff CHAR(32) NOT NULL,
    route_from VARCHAR(50),
    route_to VARCHAR(50),
    distance_km DECIMAL(12,3),
    vehicle_type VARCHAR(50),
    fuel_type VARCHAR(50),
    fuel_used_l DECIMAL(12,3),
    PRIMARY KEY (hk_shipment, load_dts),
    KEY ix_sship_hk_shipment (hk_shipment),
    CONSTRAINT fk_sship_shipment FOREIGN KEY (hk_shipment) REFERENCES hub_shipment (hk_shipment)
) ENGINE=InnoDB;

CREATE TABLE sat_manual_esg_metrics (
    hk_facility_period CHAR(32) NOT NULL,
    load_dts DATETIME(6) NOT NULL,
    record_source VARCHAR(50) NOT NULL,
    hashdiff CHAR(32) NOT NULL,
    workforce_total INT,
    women_pct DECIMAL(5,2),
    waste_kg DECIMAL(14,3),
    water_m3 DECIMAL(14,3),
    PRIMARY KEY (hk_facility_period, load_dts),
    KEY ix_smem_hk_facility_period (hk_facility_period),
    CONSTRAINT fk_smem_facility_period FOREIGN KEY (hk_facility_period) REFERENCES link_facility_period (hk_facility_period)
) ENGINE=InnoDB;

CREATE TABLE sat_carbon_credit_attr (
    hk_credit CHAR(32) NOT NULL,
    load_dts DATETIME(6) NOT NULL,
    record_source VARCHAR(50) NOT NULL,
    hashdiff CHAR(32) NOT NULL,
    registry_name VARCHAR(50),
    project_id VARCHAR(50),
    vintage_year INT,
    co2e_tonnes DECIMAL(14,3),
    PRIMARY KEY (hk_credit, load_dts),
    KEY ix_scca_hk_credit (hk_credit),
    CONSTRAINT fk_scca_credit FOREIGN KEY (hk_credit) REFERENCES hub_carbon_credit (hk_credit)
) ENGINE=InnoDB;

-- Reference
CREATE TABLE ref_emission_factor (
    factor_id INT PRIMARY KEY,
    activity_type VARCHAR(50) NOT NULL,
    region VARCHAR(50),
    unit VARCHAR(20) NOT NULL,
    kgco2e_per_unit DECIMAL(12,6) NOT NULL,
    valid_from DATE NOT NULL,
    valid_to DATE NOT NULL,
    source VARCHAR(100)
) ENGINE=InnoDB;

-- Business Vault
CREATE TABLE bv_scope2_emission_event (
    event_id BIGINT PRIMARY KEY,
    hk_facility CHAR(32) NOT NULL,
    hk_meter CHAR(32) NOT NULL,
    hk_period CHAR(32) NOT NULL,
    factor_id INT NOT NULL,
    reading_ts DATETIME NOT NULL,
    kwh_value DECIMAL(12,4),
    scope2_kgco2e DECIMAL(14,4),
    raw_record_hash CHAR(32) NOT NULL,
    transform_ver VARCHAR(50) NOT NULL,
    load_dts DATETIME(6) NOT NULL,
    record_source VARCHAR(50) NOT NULL,
    KEY ix_bv2_hk_facility (hk_facility),
    KEY ix_bv2_hk_meter (hk_meter),
    KEY ix_bv2_hk_period (hk_period),
    KEY ix_bv2_factor_id (factor_id),
    CONSTRAINT fk_bv2_facility FOREIGN KEY (hk_facility) REFERENCES hub_facility (hk_facility),
    CONSTRAINT fk_bv2_meter FOREIGN KEY (hk_meter) REFERENCES hub_meter (hk_meter),
    CONSTRAINT fk_bv2_period FOREIGN KEY (hk_period) REFERENCES hub_reporting_period (hk_period),
    CONSTRAINT fk_bv2_factor FOREIGN KEY (factor_id) REFERENCES ref_emission_factor (factor_id)
) ENGINE=InnoDB;

CREATE TABLE bv_scope3_emission_event (
    event_id BIGINT PRIMARY KEY,
    hk_facility CHAR(32) NOT NULL,
    hk_shipment CHAR(32) NOT NULL,
    hk_period CHAR(32) NOT NULL,
    factor_id INT NOT NULL,
    activity_value DECIMAL(12,4),
    scope3_kgco2e DECIMAL(14,4),
    raw_record_hash CHAR(32) NOT NULL,
    transform_ver VARCHAR(50) NOT NULL,
    load_dts DATETIME(6) NOT NULL,
    record_source VARCHAR(50) NOT NULL,
    KEY ix_bv3_hk_facility (hk_facility),
    KEY ix_bv3_hk_shipment (hk_shipment),
    KEY ix_bv3_hk_period (hk_period),
    KEY ix_bv3_factor_id (factor_id),
    CONSTRAINT fk_bv3_facility FOREIGN KEY (hk_facility) REFERENCES hub_facility (hk_facility),
    CONSTRAINT fk_bv3_shipment FOREIGN KEY (hk_shipment) REFERENCES hub_shipment (hk_shipment),
    CONSTRAINT fk_bv3_period FOREIGN KEY (hk_period) REFERENCES hub_reporting_period (hk_period),
    CONSTRAINT fk_bv3_factor FOREIGN KEY (factor_id) REFERENCES ref_emission_factor (factor_id)
) ENGINE=InnoDB;

-- Ledger
CREATE TABLE ledger_credit_txn (
    txn_id VARCHAR(50) PRIMARY KEY,
    hk_credit CHAR(32) NOT NULL,
    txn_type VARCHAR(30) NOT NULL,
    tonnes DECIMAL(14,4) NOT NULL,
    txn_ts DATETIME NOT NULL,
    hk_facility CHAR(32),
    hk_period CHAR(32),
    source_doc_id VARCHAR(100),
    load_dts DATETIME(6) NOT NULL,
    record_source VARCHAR(50) NOT NULL,
    KEY ix_lct_hk_credit (hk_credit),
    KEY ix_lct_hk_facility (hk_facility),
    KEY ix_lct_hk_period (hk_period),
    CONSTRAINT fk_lct_credit FOREIGN KEY (hk_credit) REFERENCES hub_carbon_credit (hk_credit),
    CONSTRAINT fk_lct_facility FOREIGN KEY (hk_facility) REFERENCES hub_facility (hk_facility),
    CONSTRAINT fk_lct_period FOREIGN KEY (hk_period) REFERENCES hub_reporting_period (hk_period)
) ENGINE=InnoDB;

CREATE TABLE ledger_credit_position (
    hk_credit CHAR(32) NOT NULL,
    status VARCHAR(30) NOT NULL,
    owner_entity VARCHAR(100),
    current_balance_tonnes DECIMAL(14,4),
    as_of_dts DATETIME NOT NULL,
    load_dts DATETIME(6) NOT NULL,
    record_source VARCHAR(50) NOT NULL,
    PRIMARY KEY (hk_credit, as_of_dts),
    KEY ix_lcp_hk_credit (hk_credit),
    CONSTRAINT fk_lcp_credit FOREIGN KEY (hk_credit) REFERENCES hub_carbon_credit (hk_credit)
) ENGINE=InnoDB;

-- Data Mart
CREATE TABLE dm_csrds_emissions_summary (
    hk_facility CHAR(32) NOT NULL,
    hk_period CHAR(32) NOT NULL,
    scope1_kgco2e DECIMAL(14,4),
    scope2_kgco2e DECIMAL(14,4),
    scope3_kgco2e DECIMAL(14,4),
    credits_retired_t DECIMAL(14,4),
    net_emissions_kgco2e DECIMAL(14,4),
    generated_ts DATETIME,
    PRIMARY KEY (hk_facility, hk_period),
    KEY ix_dm_hk_facility (hk_facility),
    KEY ix_dm_hk_period (hk_period),
    CONSTRAINT fk_dm_facility FOREIGN KEY (hk_facility) REFERENCES hub_facility (hk_facility),
    CONSTRAINT fk_dm_period FOREIGN KEY (hk_period) REFERENCES hub_reporting_period (hk_period)
) ENGINE=InnoDB;

-- Metadata
CREATE TABLE meta_lineage_edge (
    edge_id VARCHAR(64) PRIMARY KEY,
    from_table VARCHAR(100) NOT NULL,
    from_key VARCHAR(100) NOT NULL,
    to_table VARCHAR(100) NOT NULL,
    to_key VARCHAR(100) NOT NULL,
    transform_name VARCHAR(100) NOT NULL,
    transform_ver VARCHAR(50) NOT NULL,
    executed_ts DATETIME NOT NULL
) ENGINE=InnoDB;

SET FOREIGN_KEY_CHECKS = 1;

-- Validation helpers
SELECT COUNT(*) AS table_count
FROM information_schema.tables
WHERE table_schema = 'green_trace_dw';

SHOW TABLES;

