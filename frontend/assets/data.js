const greenTraceData = {
  overview: {
    project: "GreenTrace ESG Data Vault",
    subtitle: "An editorial frontend for auditable carbon intelligence.",
    reportingPeriod: "2026 Q1",
    tables: 22,
    rowsProcessed: 5286,
    facilities: 25,
    meters: 100,
    suppliers: 12,
    shipments: 40,
    credits: 10,
    scope2Kg: 40268.79,
    scope3Kg: 2284.99,
    totalKg: 42553.78,
    energyReadings: 2400,
    captureWindow: "2026-01-01 00:00 to 05:45",
    narrative:
      "GreenTrace turns fragmented emissions data into a calm, auditable command center for modern operations."
  },
  heroHighlights: [
    {
      label: "Total modeled emissions",
      value: 42.55,
      format: "decimal",
      decimals: 2,
      suffix: " tCO2e",
      note: "Modeled footprint across scopes"
    },
    {
      label: "Energy readings",
      value: 2400,
      format: "integer",
      suffix: "+",
      note: "Meter observations in the current model"
    },
    {
      label: "Facilities monitored",
      value: 25,
      format: "integer",
      note: "Facilities in the current operating scope"
    },
    {
      label: "Warehouse tables",
      value: 22,
      format: "integer",
      note: "From vault structures to reporting views"
    }
  ],
  storyPanels: [
    {
      page: "Page 01",
      title: "Capture the source signal.",
      body:
        "Facilities, suppliers, shipments, meters, and credits are preserved in Data Vault form so the system never loses source context."
    },
    {
      page: "Page 02",
      title: "Model emissions without losing lineage.",
      body:
        "Business Vault logic turns raw activity into Scope 2 and Scope 3 events while keeping versions, hashes, and traceability intact."
    },
    {
      page: "Page 03",
      title: "Govern offsets as real assets.",
      body:
        "Carbon credits are modeled as governed assets, ready for issue, retire, and future anti-double-counting workflows."
    },
    {
      page: "Page 04",
      title: "Present the system like a product.",
      body:
        "The frontend reframes the project as a cinematic control room with paced sections, motion, and facility-level intelligence."
    }
  ],
  featureCards: [
    {
      title: "Cinematic motion system",
      body:
        "Every major section is staged as a full-screen reveal, with motion that guides attention instead of distracting from the data."
    },
    {
      title: "Data-backed interface",
      body:
        "Metrics, rankings, intervals, and mix views are grounded in warehouse values so the experience feels credible, not decorative."
    },
    {
      title: "Architecture as narrative",
      body:
        "The model, ETL path, and governance layers are written as a story so technical depth becomes easier to present."
    }
  ],
  architectureLayers: [
    {
      name: "Raw Vault",
      stat: "25 facilities / 100 meters",
      description:
        "Hubs, links, and satellites preserve the operating truth for facilities, suppliers, meters, shipments, reporting periods, and credits."
    },
    {
      name: "Business Vault",
      stat: "2,440 computed events",
      description:
        "Emission logic converts energy and shipment activity into Scope 2 and Scope 3 events with factor references and transform versions."
    },
    {
      name: "Carbon Ledger",
      stat: "10 credit assets",
      description:
        "The credit model is designed for issuance and retirement workflows so offsets can be tracked without double counting."
    },
    {
      name: "Data Mart UX",
      stat: "Executive-ready reporting",
      description:
        "The experience surfaces facility rankings, regional rollups, query cards, and compliance storytelling in one readable layer."
    }
  ],
  kpis: [
    {
      label: "Scope 2 emissions",
      value: 40.27,
      format: "decimal",
      decimals: 2,
      suffix: " tCO2e",
      note: "94.6% of the modeled footprint"
    },
    {
      label: "Scope 3 emissions",
      value: 2.28,
      format: "decimal",
      decimals: 2,
      suffix: " tCO2e",
      note: "Transport-driven emissions layer"
    },
    {
      label: "Meters connected",
      value: 100,
      format: "integer",
      note: "Feeding 2,400 meter observations"
    },
    {
      label: "Supplier entities",
      value: 12,
      format: "integer",
      note: "Distributed across four supplier sectors"
    },
    {
      label: "Processing window",
      value: 345,
      format: "integer",
      suffix: " mins",
      note: "Measured across the current capture window"
    }
  ],
  regionTotals: [
    { region: "IN-NORTH", totalKg: 9638.22 },
    { region: "IN-EAST", totalKg: 9012.64 },
    { region: "IN-WEST", totalKg: 8374.52 },
    { region: "IN-CENTRAL", totalKg: 8077.23 },
    { region: "IN-SOUTH", totalKg: 7451.16 }
  ],
  facilityLeaders: [
    {
      facility: "Facility 00000015",
      region: "IN-NORTH",
      scope2Kg: 1884.8,
      scope3Kg: 121.24,
      totalKg: 2006.05
    },
    {
      facility: "Facility 00000005",
      region: "IN-NORTH",
      scope2Kg: 1885.34,
      scope3Kg: 111.46,
      totalKg: 1996.8
    },
    {
      facility: "Facility 00000025",
      region: "IN-NORTH",
      scope2Kg: 1886.52,
      scope3Kg: 46.98,
      totalKg: 1933.51
    },
    {
      facility: "Facility 00000003",
      region: "IN-EAST",
      scope2Kg: 1756.36,
      scope3Kg: 138.21,
      totalKg: 1894.56
    },
    {
      facility: "Facility 00000008",
      region: "IN-EAST",
      scope2Kg: 1783.17,
      scope3Kg: 107.84,
      totalKg: 1891.02
    },
    {
      facility: "Facility 00000010",
      region: "IN-NORTH",
      scope2Kg: 1736.29,
      scope3Kg: 141.08,
      totalKg: 1877.37
    },
    {
      facility: "Facility 00000004",
      region: "IN-CENTRAL",
      scope2Kg: 1686.73,
      scope3Kg: 154.1,
      totalKg: 1840.83
    },
    {
      facility: "Facility 00000013",
      region: "IN-EAST",
      scope2Kg: 1769.16,
      scope3Kg: 60.86,
      totalKg: 1830.02
    }
  ],
  intervalLoad: [
    { slot: "00:00", totalKg: 1755.14 },
    { slot: "00:15", totalKg: 1548.56 },
    { slot: "00:30", totalKg: 1720.58 },
    { slot: "00:45", totalKg: 1736.77 },
    { slot: "01:00", totalKg: 1746.25 },
    { slot: "01:15", totalKg: 1661.84 },
    { slot: "01:30", totalKg: 1591.95 },
    { slot: "01:45", totalKg: 1563.4 },
    { slot: "02:00", totalKg: 1724.76 },
    { slot: "02:15", totalKg: 1669.68 },
    { slot: "02:30", totalKg: 1666.04 },
    { slot: "02:45", totalKg: 1590.83 },
    { slot: "03:00", totalKg: 1785.31 },
    { slot: "03:15", totalKg: 1768.36 },
    { slot: "03:30", totalKg: 1711.86 },
    { slot: "03:45", totalKg: 1759.27 },
    { slot: "04:00", totalKg: 1685.31 },
    { slot: "04:15", totalKg: 1754.19 },
    { slot: "04:30", totalKg: 1605.7 },
    { slot: "04:45", totalKg: 1578.77 },
    { slot: "05:00", totalKg: 1771.65 },
    { slot: "05:15", totalKg: 1641.71 },
    { slot: "05:30", totalKg: 1531.95 },
    { slot: "05:45", totalKg: 1698.93 }
  ],
  vehicleMix: [
    { label: "Rail", count: 10 },
    { label: "Van", count: 10 },
    { label: "Ship", count: 10 },
    { label: "Truck", count: 10 }
  ],
  supplierSectors: [
    { label: "Packaging", count: 3 },
    { label: "Manufacturing", count: 3 },
    { label: "Logistics", count: 3 },
    { label: "Electronics", count: 3 }
  ],
  schemaCounts: [
    { label: "Hubs", count: 6, detail: "Core entities" },
    { label: "Links", count: 3, detail: "Business relationships" },
    { label: "Satellites", count: 6, detail: "Historical attributes" },
    { label: "Business Vault", count: 2, detail: "Emission event tables" },
    { label: "Ledger", count: 2, detail: "Credit transactions and positions" },
    { label: "Data Mart", count: 1, detail: "CSRD summary layer" },
    { label: "Metadata", count: 1, detail: "Lineage edge table" }
  ],
  phases: [
    {
      phase: "Phase 1",
      title: "Dataset analysis",
      body:
        "Twenty-five source files were profiled and classified into Data Vault structures to frame the warehouse design."
    },
    {
      phase: "Phase 2",
      title: "Schema design",
      body:
        "The MySQL schema was shaped into hubs, links, satellites, business vault tables, a carbon ledger, and the reporting mart."
    },
    {
      phase: "Phase 3",
      title: "ETL pipeline",
      body:
        "Python and SQLAlchemy pipelines load the vault idempotently and prepare the platform for repeatable processing runs."
    },
    {
      phase: "Phase 4",
      title: "Business vault logic",
      body:
        "Scope 2 electricity and Scope 3 transport emissions are computed from source activity and referenced emission factors."
    },
    {
      phase: "Phase 5",
      title: "Carbon credit ledger",
      body:
        "Credit assets, transactions, and positions are modeled to support governed offset accounting."
    },
    {
      phase: "Phase 6",
      title: "Data mart",
      body:
        "A CSRD-oriented reporting layer is prepared for downstream dashboards and compliance rollups."
    },
    {
      phase: "Phase 7",
      title: "Lineage",
      body:
        "Lineage hooks are provisioned so business logic and downstream reporting can be audited end to end."
    },
    {
      phase: "Phase 8",
      title: "Visualization",
      body:
        "The frontend adds the final product layer: animated storytelling, executive dashboards, and architecture communication."
    }
  ],
  queries: [
    {
      label: "Regional load",
      sql:
        "SELECT grid_region, SUM(scope2_kgco2e + scope3_kgco2e) AS total_kg\nFROM emissions_summary\nGROUP BY grid_region\nORDER BY total_kg DESC;",
      result: "IN-NORTH carries the highest modeled regional load at 9,638.22 kgCO2e."
    },
    {
      label: "Facility ranking",
      sql:
        "SELECT facility_name, SUM(scope2_kgco2e + scope3_kgco2e) AS total_kg\nFROM facility_emissions\nGROUP BY facility_name\nORDER BY total_kg DESC\nLIMIT 5;",
      result: "Facility 00000015 is the highest facility footprint at 2,006.05 kgCO2e."
    },
    {
      label: "Capture pulse",
      sql:
        "SELECT reading_slot, SUM(scope2_kgco2e) AS interval_kg\nFROM scope2_events\nGROUP BY reading_slot\nORDER BY reading_slot;",
      result: "The strongest capture interval in the model is 03:00 with 1,785.31 kgCO2e."
    }
  ]
};

window.greenTraceData = greenTraceData;
