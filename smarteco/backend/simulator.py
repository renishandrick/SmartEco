import math
import random
from datetime import datetime
from state import STATE


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def update_telemetry_from_simulator() -> None:
    """
    Option B simulator: directly updates STATE.telemetry.
    Produces realistic-ish patterns + crisis overrides.
    """
    now = datetime.now()
    hour = now.hour
    dow = now.weekday()

    # Base campus "activity" curve
    # Peak around 14:00, low at night
    activity = 0.5 + 0.5 * math.sin((hour - 6) / 24 * 2 * math.pi)
    activity = _clamp(activity, 0.05, 1.0)

    # Energy baseline (kWh)
    energy = 70 + 140 * activity + random.uniform(-8, 8)
    # Slight weekday effect
    if dow >= 5:  # weekend
        energy *= 0.8

    # Water baseline (LPM) with meal spikes
    meal_spike = 0.0
    if 12 <= hour <= 14:
        meal_spike += 20
    if 18 <= hour <= 20:
        meal_spike += 15
    water = 8 + 25 * activity + meal_spike + random.uniform(-2, 2)

    # Waste baseline (%): gradual increase, reset once per day around 18:00
    waste = STATE.telemetry.get("waste_pct", 30.0)
    # Increase rate depends on activity (Slowed down for ~25 mins fill time)
    # Target: 100% in 1500 ticks => ~0.06 per tick
    increment = (0.04 + 0.04 * activity) + random.uniform(-0.01, 0.02)
    waste += increment
    waste = _clamp(waste, 0, 100)

    # Reset waste once per day at 18:00 (simulate collection)
    if hour == 18 and STATE.last_waste_reset_hour != hour:
        waste = random.uniform(10, 25)
        STATE.last_waste_reset_hour = hour

    # Crisis overrides (WOW demo)
    if STATE.crisis_state["energy_spike"]:
        energy += random.uniform(80, 150)

    if STATE.crisis_state["water_leak"]:
        water += random.uniform(50, 120)

    if STATE.crisis_state["waste_overflow"]:
        waste = max(waste, random.uniform(92, 99))

    # Clamp final
    energy = _clamp(energy, 10, 600)
    water = _clamp(water, 0, 250)
    waste = _clamp(waste, 0, 100)

    STATE.telemetry = {
        "energy_kwh": round(energy, 2),
        "water_lpm": round(water, 2),
        "waste_pct": round(waste, 2),
    }
