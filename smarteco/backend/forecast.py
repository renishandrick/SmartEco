from datetime import datetime
from typing import Dict, Any, List

# Load Tier-A forecaster from ml_package
try:
    from predict_api import get_forecaster
    forecaster = get_forecaster()
    TIER_A_READY = forecaster.ready
    if TIER_A_READY:
        print("✅ Tier-A Forecaster loaded from ml_package")
except Exception as e:
    print(f"⚠️  Tier-A unavailable: {e}")
    TIER_A_READY = False
    forecaster = None


def get_24h_forecast(resource: str) -> Dict[str, Any]:
    """
    24-hour forecast with Tier-A ML or fallback
    """
    resource = resource.lower().strip()
    
    # Map resource names
    if resource == "energy":
        resource = "electricity"
    
    if resource not in ("electricity", "water", "waste"):
        resource = "electricity"

    # Tier A: Use pre-trained models from ml_package
    if TIER_A_READY and forecaster:
        points = forecaster.get_24h_forecast(resource=resource, occupancy=0.75)
        
        return {
            "resource": resource,
            "points": points,
            "tier": "A (Pre-trained)",
            "source": "ml_package"
        }
    
    # Tier B: Simple fallback (should rarely happen)
    import math
    now_h = datetime.now().hour
    points = []
    
    for h in range(24):
        hour = (now_h + h) % 24
        activity = 0.5 + 0.5 * math.sin((hour - 6) / 24 * 2 * math.pi)
        activity = max(0.05, min(activity, 1.0))
        
        if resource == "electricity":
            y = 80 + 160 * activity
        elif resource == "water":
            meal = 20 if 12 <= hour <= 14 else (15 if 18 <= hour <= 20 else 0)
            y = 10 + 30 * activity + meal
        else:  # waste
            y = min(98.0, 20 + 60 * activity + (h * 1.2))
        
        points.append({"h": h, "y": round(y, 2)})

    return {
        "resource": resource,
        "points": points,
        "tier": "B (Fallback)"
    }
