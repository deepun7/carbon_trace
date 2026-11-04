import os
import json
import sqlite3

DATA_DIR = "data"
DB_PATH = os.path.join(DATA_DIR, "enterprise_telemetry.db")
EF_REGISTRY_PATH = os.path.join(DATA_DIR, "emission_factors_registry.json")

OFFICIAL_EMISSION_FACTORS = {
    "metadata": {
        "standard": "GHG Protocol Corporate Accounting and Reporting Standard",
        "version": "2024.3",
        "historical_applicability_note": (
            "Static 2024 reference factors are applied across all historical years for prototype "
            "trend consistency; production accounting requires year-specific historical factors."
        ),
        "included_boundary": (
            "Partial operational inventory covering selected Scope 1 (stationary diesel, natural gas, "
            "diesel fleet), Scope 2 (location-based grid electricity), and Scope 3 (air travel, HGV road freight) categories."
        )
    },
    "scope_1_factors": {
        "diesel_stationary_kg_co2e_per_liter": {
            "value": 2.68787,
            "unit": "kg CO2e / liter",
            "source": "UK DESNZ / DEFRA Greenhouse Gas Conversion Factors 2024",
            "url": "https://www.gov.uk/government/collections/government-conversion-factors-for-company-reporting",
            "geography": "Global default stationary diesel fuel properties",
            "year_published": 2024
        },
        "natural_gas_kg_co2e_per_m3": {
            "value": 2.02135,
            "unit": "kg CO2e / m3",
            "source": "US EPA GHG Emission Factors Hub (2024)",
            "url": "https://www.epa.gov/climateleadership/ghg-emission-factors-hub",
            "geography": "North America / Global standard pipeline natural gas",
            "year_published": 2024
        },
        "fleet_diesel_kg_co2e_per_km": {
            "value": 0.17048,
            "unit": "kg CO2e / km",
            "source": "UK DESNZ 2024 Conversion Factors (Average Diesel Van / LCV)",
            "url": "https://www.gov.uk/government/collections/government-conversion-factors-for-company-reporting",
            "geography": "Assumes diesel commercial fleet average",
            "year_published": 2024
        }
    },
    "scope_2_location_grid_factors_kg_co2e_per_kwh": {
        "India": {
            "value": 0.716,
            "source": "Central Electricity Authority (CEA) India CO2 Baseline Database v19.0 (2023-24)",
            "url": "https://cea.nic.in/cdm-co2-baseline-database/",
            "geography": "India National Grid",
            "methodology": "Location-based weighted average grid operating margin"
        },
        "United States": {
            "value": 0.367,
            "source": "US EPA eGRID 2024 Summary Tables",
            "url": "https://www.epa.gov/egrid",
            "geography": "United States National Average",
            "methodology": "Location-based total output emission rate"
        },
        "China": {
            "value": 0.557,
            "source": "Ministry of Ecology and Environment (MEE) China Grid Factor",
            "url": "https://www.mee.gov.cn/",
            "geography": "China National Grid",
            "methodology": "Location-based national average grid factor"
        },
        "European Union (27)": {
            "value": 0.251,
            "source": "European Environment Agency (EEA) Greenhouse Gas Emission Intensity",
            "url": "https://www.eea.europa.eu/",
            "geography": "EU-27 Member States",
            "methodology": "Location-based EU-27 average"
        },
        "United Kingdom": {
            "value": 0.20707,
            "source": "UK DESNZ 2024 Conversion Factors (UK Electricity)",
            "url": "https://www.gov.uk/government/collections/government-conversion-factors-for-company-reporting",
            "geography": "United Kingdom",
            "methodology": "Location-based grid generation average"
        },
        "Germany": {
            "value": 0.380,
            "source": "Umweltbundesamt (UBA) German Electricity Mix Factor",
            "url": "https://www.umweltbundesamt.de/",
            "geography": "Germany",
            "methodology": "Location-based national grid mix"
        },
        "Japan": {
            "value": 0.457,
            "source": "Ministry of the Environment (MOE) Japan Grid Factors",
            "url": "https://www.env.go.jp/en/",
            "geography": "Japan",
            "methodology": "Location-based national utility average"
        },
        "World": {
            "value": 0.436,
            "source": "IEA Emissions Factors 2023 Global Benchmark",
            "url": "https://www.iea.org/data-and-statistics",
            "geography": "Global Average",
            "methodology": "Global weighted electricity average"
        }
    },
    "scope_3_factors": {
        "business_flight_short_medium_haul_kg_co2e_per_pkm": {
            "value": 0.15102,
            "unit": "kg CO2e / passenger-km",
            "source": "UK DESNZ 2024 Business Travel - Air (without radiative forcing)",
            "url": "https://www.gov.uk/government/collections/government-conversion-factors-for-company-reporting",
            "geography": "Global short/medium-haul economy average",
            "year_published": 2024
        },
        "road_freight_hgv_kg_co2e_per_ton_km": {
            "value": 0.10455,
            "unit": "kg CO2e / ton-km",
            "source": "UK DESNZ 2024 Freighting Goods - All HGV Average",
            "url": "https://www.gov.uk/government/collections/government-conversion-factors-for-company-reporting",
            "geography": "Heavy goods vehicle road freight average",
            "year_published": 2024
        }
    }
}

BASE_SERIES = [
    (2000, 112000.0, 64000.0, 410000.0, 2150000.0, 520000.0, 1950000.0),
    (2001, 115400.0, 65800.0, 422000.0, 2210000.0, 535000.0, 2010000.0),
    (2002, 118900.0, 67500.0, 435000.0, 2285000.0, 548000.0, 2080000.0),
    (2003, 123100.0, 69900.0, 449000.0, 2360000.0, 565000.0, 2150000.0),
    (2004, 127800.0, 72100.0, 465000.0, 2450000.0, 590000.0, 2240000.0),
    (2005, 132400.0, 74800.0, 481000.0, 2540000.0, 612000.0, 2330000.0),
    (2006, 137900.0, 77600.0, 498000.0, 2635000.0, 638000.0, 2420000.0),
    (2007, 143200.0, 80500.0, 516000.0, 2730000.0, 665000.0, 2515000.0),
    (2008, 124500.0, 71200.0, 448000.0, 2410000.0, 510000.0, 2180000.0),
    (2009, 139800.0, 78900.0, 502000.0, 2680000.0, 615000.0, 2460000.0),
    (2010, 146500.0, 82400.0, 525000.0, 2790000.0, 655000.0, 2580000.0),
    (2011, 152100.0, 85300.0, 544000.0, 2895000.0, 682000.0, 2675000.0),
    (2012, 157800.0, 88100.0, 562000.0, 3005000.0, 710000.0, 2770000.0),
    (2013, 163200.0, 91000.0, 581000.0, 3110000.0, 735000.0, 2865000.0),
    (2014, 168900.0, 94200.0, 601000.0, 3220000.0, 762000.0, 2960000.0),
    (2015, 174100.0, 97100.0, 619000.0, 3325000.0, 788000.0, 3055000.0),
    (2016, 179500.0, 99800.0, 638000.0, 3430000.0, 815000.0, 3150000.0),
    (2017, 184800.0, 102600.0, 656000.0, 3535000.0, 842000.0, 3245000.0),
    (2018, 190200.0, 105400.0, 675000.0, 3645000.0, 870000.0, 3340000.0),
    (2019, 195100.0, 108100.0, 692000.0, 3740000.0, 895000.0, 3430000.0),
    (2020, 151200.0, 86400.0, 512000.0, 3080000.0, 245000.0, 2710000.0),
    (2021, 186400.0, 103800.0, 658000.0, 3590000.0, 620000.0, 3290000.0),
    (2022, 198500.0, 110200.0, 704000.0, 3810000.0, 865000.0, 3495000.0),
    (2023, 203400.0, 112900.0, 721000.0, 3915000.0, 905000.0, 3585000.0),
]

def _build_seed_rows() -> list[tuple]:
    rows = []
    for yr, d, ng, fl, el, air, fr in BASE_SERIES:
        rows.append((
            "Apex Manufacturing Pvt Ltd", "FAC-IN-01", yr,
            round(d * 0.60, 2), round(ng * 0.60, 2), round(fl * 0.60, 2),
            round(el * 0.60, 2), round(air * 0.60, 2), round(fr * 0.60, 2),
            "SIMULATED_DEMO"
        ))
        rows.append((
            "Apex Manufacturing Pvt Ltd", "FAC-IN-02", yr,
            round(d * 0.40, 2), round(ng * 0.40, 2), round(fl * 0.40, 2),
            round(el * 0.40, 2), round(air * 0.40, 2), round(fr * 0.40, 2),
            "SIMULATED_DEMO"
        ))
    for yr, d, ng, fl, el, air, fr in BASE_SERIES:
        rows.append((
            "GreenGrid Logistics Corp", "FAC-GG-01", yr,
            round(d * 0.35, 2), round(ng * 0.25, 2), round(fl * 0.85, 2),
            round(el * 0.45, 2), round(air * 0.30, 2), round(fr * 0.90, 2),
            "SIMULATED_DEMO"
        ))
        rows.append((
            "GreenGrid Logistics Corp", "FAC-GG-02", yr,
            round(d * 0.25, 2), round(ng * 0.15, 2), round(fl * 0.55, 2),
            round(el * 0.30, 2), round(air * 0.20, 2), round(fr * 0.60, 2),
            "SIMULATED_DEMO"
        ))
    return rows

def initialize_enterprise_data_store(force_reset: bool = False):
    os.makedirs( os.path.dirname(DB_PATH) or ".", exist_ok=True)
    os.makedirs( os.path.dirname(EF_REGISTRY_PATH) or ".", exist_ok=True)

    with open(EF_REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(OFFICIAL_EMISSION_FACTORS, f, indent=2)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(enterprise_activity_logs)")
    cols = [row[1] for row in cur.fetchall()]

    if force_reset:
        cur.execute("DROP TABLE IF EXISTS enterprise_activity_logs")
    elif cols and "org_id" not in cols:
        # Non-destructive migration for legacy single-org tables
        cur.execute("ALTER TABLE enterprise_activity_logs RENAME TO _legacy_activity_logs")
        cur.execute("""
            CREATE TABLE enterprise_activity_logs (
                org_id TEXT NOT NULL,
                facility_id TEXT NOT NULL,
                year INTEGER NOT NULL,
                stationary_diesel_liters REAL NOT NULL,
                natural_gas_m3 REAL NOT NULL,
                fleet_transport_km REAL NOT NULL,
                purchased_electricity_kwh REAL NOT NULL,
                business_air_travel_pkm REAL NOT NULL,
                supply_chain_freight_ton_km REAL NOT NULL,
                data_provenance TEXT NOT NULL DEFAULT 'SIMULATED_DEMO',
                PRIMARY KEY (org_id, facility_id, year)
            )
        """)
        cur.execute("""
            INSERT OR IGNORE INTO enterprise_activity_logs (
                org_id, facility_id, year,
                stationary_diesel_liters, natural_gas_m3, fleet_transport_km,
                purchased_electricity_kwh, business_air_travel_pkm,
                supply_chain_freight_ton_km, data_provenance
            )
            SELECT 'Apex Manufacturing Pvt Ltd', facility_id, year,
                   stationary_diesel_liters, natural_gas_m3, fleet_transport_km,
                   purchased_electricity_kwh, business_air_travel_pkm,
                   supply_chain_freight_ton_km, 'SIMULATED_DEMO'
            FROM _legacy_activity_logs
        """)
        cur.execute("DROP TABLE _legacy_activity_logs")
        conn.commit()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS enterprise_activity_logs (
            org_id TEXT NOT NULL,
            facility_id TEXT NOT NULL,
            year INTEGER NOT NULL,
            stationary_diesel_liters REAL NOT NULL,
            natural_gas_m3 REAL NOT NULL,
            fleet_transport_km REAL NOT NULL,
            purchased_electricity_kwh REAL NOT NULL,
            business_air_travel_pkm REAL NOT NULL,
            supply_chain_freight_ton_km REAL NOT NULL,
            data_provenance TEXT NOT NULL DEFAULT 'SIMULATED_DEMO',
            PRIMARY KEY (org_id, facility_id, year)
        )
    """)
    cur.execute("SELECT COUNT(*) FROM enterprise_activity_logs")
    if cur.fetchone()[0] == 0:
        cur.executemany("""
            INSERT INTO enterprise_activity_logs (
                org_id, facility_id, year,
                stationary_diesel_liters, natural_gas_m3, fleet_transport_km,
                purchased_electricity_kwh, business_air_travel_pkm,
                supply_chain_freight_ton_km, data_provenance
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, _build_seed_rows())
        conn.commit()
    conn.close()

if __name__ == "__main__":
    initialize_enterprise_data_store(force_reset=False)
    print("✅ Seeded simulated demo SQLite database & factor registry initialized safely.")