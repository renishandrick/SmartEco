"""
REN_STARTER_ALL_IN_ONE.py  (SmartEco ML Pack - V2.1 compatible)

What this single script does:
1) Generates 90 days of hourly synthetic campus data (CSV) with realistic patterns + anomalies.
2) Trains RandomForestRegressor models for:
   - energy_kwh
   - water_lpm
   - waste_pct
3) Saves models to ml/models/*.pkl using joblib.
4) Exports:
   - feature_importances.json (optional explainable AI)
   - forecast_backup_energy.json / water / waste (24 points each)
5) Runs sanity checks (load model, predict, ensure non-negative).

Backend integration intent:
- Dev will later add Tier-A forecast by loading these .pkl models.
- If models missing, Dev uses Tier-B curve fallback (already working).

Requirements (save as ml/requirements.txt):
pandas==2.2.3
numpy==2.1.3
scikit-learn==1.5.2
joblib==1.4.2
"""

from __future__ import annotations

import os
import json
import math
import random
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from joblib import dump, load
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split


# ----------------------------
# Config (Ren can tweak)
# ----------------------------
SEED = 42
DAYS = 90                 # minimum 90 days
FREQ_HOURS = 1            # hourly rows
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(OUTPUT_DIR, "data")
MODELS_DIR = os.path.join(OUTPUT_DIR, "models")
ARTIFACTS_DIR = os.path.join(OUTPUT_DIR, "artifacts")

CSV_PATH = os.path.join(DATA_DIR, "campus_data.csv")

ENERGY_MODEL_PATH = os.path.join(MODELS_DIR, "energy_model.pkl")
WATER_MODEL_PATH = os.path.join(MODELS_DIR, "water_model.pkl")
WASTE_MODEL_PATH = os.path.join(MODELS_DIR, "waste_model.pkl")

FEATURE_IMPORTANCES_PATH = os.path.join(ARTIFACTS_DIR, "feature_importances.json")

FORECAST_BACKUP_ENERGY = os.path.join(ARTIFACTS_DIR, "forecast_backup_energy.json")
FORECAST_BACKUP_WATER = os.path.join(ARTIFACTS_DIR, "forecast_backup_water.json")
FORECAST_BACKUP_WASTE = os.path.join(ARTIFACTS_DIR, "forecast_backup_waste.json")

FEATURES = ["hour", "day_of_week", "occupancy"]

# Alert-friendly anomaly injection rates (small)
P_ENERGY_NIGHT_SPIKE = 0.012
P_WATER_LEAK_START = 0.004
P_WASTE_FAST_RISE = 0.006

# Water leak lasts several hours once started
LEAK_MIN_HOURS = 3
LEAK_MAX_HOURS = 8


# ----------------------------
# Helpers
# ----------------------------
def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(MODELS_DIR, exist_ok=True)
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)


def iso(ts: datetime) -> str:
    return ts.replace(tzinfo=timezone.utc).isoformat()


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def activity_curve(hour: int) -> float:
    """
    Smooth daily activity curve: low at night, peak afternoon.
    """
    a = 0.5 + 0.5 * math.sin((hour - 6) / 24 * 2 * math.pi)
    return clamp(a, 0.05, 1.0)


def meal_spike(hour: int) -> float:
    s = 0.0
    if 12 <= hour <= 14:
        s += 20.0
    if 18 <= hour <= 20:
        s += 15.0
    return s


# ----------------------------
# Data generation
# ----------------------------
@dataclass
class LeakState:
    active: bool = False
    remaining_hours: int = 0


def generate_dataset(days: int = DAYS) -> pd.DataFrame:
    random.seed(SEED)
    np.random.seed(SEED)

    start = datetime.now(timezone.utc) - timedelta(days=days)
    n_rows = days * 24

    rows: List[Dict] = []

    waste_pct = random.uniform(10, 25)
    leak = LeakState()

    for i in range(n_rows):
        ts = start + timedelta(hours=i)
        hour = ts.hour
        dow = ts.weekday()  # 0=Mon

        act = activity_curve(hour)

        # Occupancy: 0-100
        occ_base = 15 + 80 * act + random.uniform(-10, 10)
        # Weekend lower occupancy
        if dow >= 5:
            occ_base *= 0.65
        occupancy = int(clamp(occ_base, 0, 100))

        # ENERGY (kWh)
        energy = 70 + 140 * act + random.uniform(-8, 8)
        if dow >= 5:
            energy *= 0.82

        # Inject night spike anomaly sometimes (AC left ON)
        if hour in (0, 1, 2, 3, 4) and random.random() < P_ENERGY_NIGHT_SPIKE:
            energy += random.uniform(90, 170)

        energy = clamp(energy, 10, 700)

        # WATER (LPM)
        water = 8 + 25 * act + meal_spike(hour) + random.uniform(-2, 2)

        # Leak start (rare) -> lasts a few hours
        if (not leak.active) and random.random() < P_WATER_LEAK_START:
            leak.active = True
            leak.remaining_hours = random.randint(LEAK_MIN_HOURS, LEAK_MAX_HOURS)

        if leak.active:
            water += random.uniform(50, 120)
            leak.remaining_hours -= 1
            if leak.remaining_hours <= 0:
                leak.active = False

        water = clamp(water, 0, 250)

        # WASTE (% full)
        # Gradual increase. Resets daily around 18:00 (collection).
        waste_pct += (0.8 + 1.7 * act) + random.uniform(-0.2, 0.5)

        # Daily collection reset
        if hour == 18:
            waste_pct = random.uniform(8, 25)

        # Sometimes fast rise anomaly (party/event)
        if random.random() < P_WASTE_FAST_RISE:
            waste_pct += random.uniform(20, 45)

        waste_pct = clamp(waste_pct, 0, 100)

        rows.append({
            "timestamp": iso(ts),
            "hour": int(hour),
            "day_of_week": int(dow),
            "occupancy": int(occupancy),
            "energy_kwh": round(float(energy), 2),
            "water_lpm": round(float(water), 2),
            "waste_pct": round(float(waste_pct), 2),
        })

    df = pd.DataFrame(rows)
    return df


# ----------------------------
# Training
# ----------------------------
def train_rf(X: np.ndarray, y: np.ndarray, seed: int = SEED) -> RandomForestRegressor:
    # Fast + stable defaults for hackathon
    model = RandomForestRegressor(
        n_estimators=200,
        random_state=seed,
        n_jobs=-1,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
    )
    model.fit(X, y)
    return model


def train_all_models(df: pd.DataFrame) -> Tuple[RandomForestRegressor, RandomForestRegressor, RandomForestRegressor]:
    X = df[FEATURES].values

    y_energy = df["energy_kwh"].values
    y_water = df["water_lpm"].values
    y_waste = df["waste_pct"].values

    # Simple train split (not time-series strict, but fine for hackathon demo)
    X_train, X_test, yE_train, yE_test = train_test_split(X, y_energy, test_size=0.2, random_state=SEED)
    energy_model = train_rf(X_train, yE_train)

    X_train, X_test, yW_train, yW_test = train_test_split(X, y_water, test_size=0.2, random_state=SEED)
    water_model = train_rf(X_train, yW_train)

    X_train, X_test, yS_train, yS_test = train_test_split(X, y_waste, test_size=0.2, random_state=SEED)
    waste_model = train_rf(X_train, yS_train)

    return energy_model, water_model, waste_model


# ----------------------------
# Artifacts
# ----------------------------
def export_feature_importances(energy_model, water_model, waste_model):
    def pack(model) -> List[Dict]:
        imps = list(model.feature_importances_)
        pairs = sorted(zip(FEATURES, imps), key=lambda x: x[1], reverse=True)
        return [{"factor": f, "impact_pct": round(float(v) * 100, 1)} for f, v in pairs]

    out = {
        "energy": pack(energy_model),
        "water": pack(water_model),
        "waste": pack(waste_model),
    }
    with open(FEATURE_IMPORTANCES_PATH, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)


def export_24h_backup(resource: str, base_value: float, outfile: str):
    # Simple stable curve backup (same shape as backend expects)
    # points use h=0..23 (relative next hours)
    now_hour = datetime.now().hour
    points = []
    for h in range(24):
        hour = (now_hour + h) % 24
        act = activity_curve(hour)

        if resource == "energy":
            y = 80 + 160 * act
        elif resource == "water":
            y = 10 + 30 * act + meal_spike(hour)
        else:
            y = 25 + 55 * act + (h * 1.2)

        # center around approximate current
        y = 0.6 * y + 0.4 * base_value
        y = float(clamp(y, 0, 9999))
        points.append({"h": h, "y": round(y, 2)})

    out = {"resource": resource, "points": points}
    with open(outfile, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)


def sanity_check_models():
    # Verify saved models load and predict
    e = load(ENERGY_MODEL_PATH)
    w = load(WATER_MODEL_PATH)
    s = load(WASTE_MODEL_PATH)

    test_X = np.array([[12, 3, 80]])  # hour=12, day_of_week=3, occupancy=80
    pe = float(e.predict(test_X)[0])
    pw = float(w.predict(test_X)[0])
    ps = float(s.predict(test_X)[0])

    if pe < 0 or pw < 0 or ps < 0:
        raise ValueError("Sanity check failed: negative prediction detected.")

    print("✅ Sanity OK. Sample predictions:",
          {"energy_kwh": round(pe, 2), "water_lpm": round(pw, 2), "waste_pct": round(ps, 2)})


# ----------------------------
# Main
# ----------------------------
def main():
    ensure_dirs()

    print("1) Generating dataset...")
    df = generate_dataset(days=DAYS)
    df.to_csv(CSV_PATH, index=False)
    print(f"✅ Saved CSV: {CSV_PATH}  rows={len(df)}")

    print("2) Training models (RandomForestRegressor)...")
    energy_model, water_model, waste_model = train_all_models(df)

    print("3) Saving models with joblib...")
    dump(energy_model, ENERGY_MODEL_PATH)
    dump(water_model, WATER_MODEL_PATH)
    dump(waste_model, WASTE_MODEL_PATH)
    print("✅ Saved models:",
          ENERGY_MODEL_PATH, WATER_MODEL_PATH, WASTE_MODEL_PATH)

    print("4) Exporting feature importances...")
    export_feature_importances(energy_model, water_model, waste_model)
    print(f"✅ Saved: {FEATURE_IMPORTANCES_PATH}")

    print("5) Exporting 24h forecast backups...")
    # Use last known values from dataset for better realism
    last = df.iloc[-1]
    export_24h_backup("energy", float(last["energy_kwh"]), FORECAST_BACKUP_ENERGY)
    export_24h_backup("water", float(last["water_lpm"]), FORECAST_BACKUP_WATER)
    export_24h_backup("waste", float(last["waste_pct"]), FORECAST_BACKUP_WASTE)
    print("✅ Saved backups:",
          FORECAST_BACKUP_ENERGY, FORECAST_BACKUP_WATER, FORECAST_BACKUP_WASTE)

    print("6) Running sanity checks...")
    sanity_check_models()

    print("\nHANDOFF TO DEV:")
    print("- Send these folders/files:")
    print(f"  - {CSV_PATH}")
    print(f"  - {ENERGY_MODEL_PATH}")
    print(f"  - {WATER_MODEL_PATH}")
    print(f"  - {WASTE_MODEL_PATH}")
    print(f"  - {FEATURE_IMPORTANCES_PATH}")
    print(f"  - {FORECAST_BACKUP_ENERGY}")
    print(f"  - {FORECAST_BACKUP_WATER}")
    print(f"  - {FORECAST_BACKUP_WASTE}")
    print("\nNOTE: Dev will plug these into forecast Tier-A later without changing API.")


if __name__ == "__main__":
    main()
