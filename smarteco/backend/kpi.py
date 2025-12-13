from typing import Dict, Any

# Editable assumptions (keep transparent for judges)
CAMPUS_BASELINE = {
    "students": 5000,
    "energy_kwh_per_day": 3500,
    "water_liters_per_day": 12000,
    "waste_collections_per_month": 30,
    "tariff_energy_per_kwh_inr": 8,
    "tariff_water_per_1000l_inr": 50,
    "tariff_waste_collection_inr": 500,
}

SAVINGS_ASSUMPTIONS = {
    "energy_reduction_pct": 0.15,  # 15%
    "water_reduction_pct": 0.30,   # 30%
    "waste_reduction_pct": 0.20,   # 20%
}

ENV_ASSUMPTIONS = {
    # Demo conversion (keep as assumption)
    "co2_kg_per_kwh": 0.82,
}


def calculate_kpis() -> Dict[str, Any]:
    # Annual savings
    energy_saved_kwh = CAMPUS_BASELINE["energy_kwh_per_day"] * SAVINGS_ASSUMPTIONS["energy_reduction_pct"] * 365
    energy_savings_inr = energy_saved_kwh * CAMPUS_BASELINE["tariff_energy_per_kwh_inr"]

    water_saved_liters = CAMPUS_BASELINE["water_liters_per_day"] * SAVINGS_ASSUMPTIONS["water_reduction_pct"] * 365
    water_savings_inr = (water_saved_liters / 1000.0) * CAMPUS_BASELINE["tariff_water_per_1000l_inr"]

    waste_collections_saved = CAMPUS_BASELINE["waste_collections_per_month"] * SAVINGS_ASSUMPTIONS["waste_reduction_pct"] * 12
    waste_savings_inr = waste_collections_saved * CAMPUS_BASELINE["tariff_waste_collection_inr"]

    annual = energy_savings_inr + water_savings_inr + waste_savings_inr
    monthly = annual / 12.0

    # Environmental impact
    co2_tons_avoided = (energy_saved_kwh * ENV_ASSUMPTIONS["co2_kg_per_kwh"]) / 1000.0

    return {
        "monthly_savings_inr": int(round(monthly)),
        "annual_savings_inr": int(round(annual)),
        "co2_tons_avoided": round(co2_tons_avoided, 1),
        "water_liters_saved": int(round(water_saved_liters)),
    }
