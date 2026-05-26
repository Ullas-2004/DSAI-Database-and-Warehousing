# Phase 2: Data Warehouse Schema Design

## Objective
To design and implement the Data Vault 2.0 schema in MySQL.

## Approach
- Created hub, link, and satellite tables
- Followed Data Vault modeling principles
- Used hashed keys (hk_*) for relationships

## Tables Created

### Hub Tables
- hub_facility
- hub_supplier
- hub_meter
- hub_shipment
- hub_carbon_credit
- hub_reporting_period

### Link Tables
- link_facility_meter
- link_facility_period
- link_shipment_supplier_facility

### Satellite Tables
- sat_energy_reading
- sat_shipment_activity
- sat_facility_attr
- sat_supplier_attr

## Key Features
- Primary and Foreign Keys implemented
- Indexing for performance
- Idempotent schema creation using SQL script

## Outcome
Successfully created 22 tables representing the Data Vault architecture.
