# ML Forecast Model Integration Guide

**To:** Backend Team
**From:** AI/ML Team
**Date:** 2024-12-12
**Subject:** Tier-A Forecast Models (v2.1)

## 📦 What's in this Package?

This folder contains the fully trained AI Core for the Smart Campus Dashboard. It is designed to be a "drop-in" backend module.

| File | Purpose |
| :--- | :--- |
| `predict_api.py` | **MAIN ENTRY POINT**. The only Python file you need to import. |
| `forecast_*.pkl` | The trained Random Forest brains (Energy, Water, Waste). |
| `forecast_backup_*.json` | Fallback data (Tier-B) automatically used if models fail. |
| `sample_data.csv` | Sample rows showing the data schema used for training. |

## 🚀 How to Integrate (3 Lines of Code)

1.  **Copy** this entire folder into your backend project (e.g., as `src/ml_engine/`).
2.  **Install Dependencies**:
    ```bash
    pip install pandas numpy scikit-learn joblib
    ```
3.  **Call the API** in your route/controller:

```python
# Import the simple wrapper function
from ml_engine.predict_api import get_forecast

# Get a 24-hour forecast
# Inputs: Resource Name, Current Hour (0-23), Day (0=Mon), Occupancy (0.0-1.0)
json_response = get_forecast("electricity", hour=14, day_of_week=2, occupancy=0.75)

# Returns JSON string:
# {
#   "success": true,
#   "forecast": [{"h": 0, "y": 85.2}, {"h": 1, "y": 88.1}, ...],
#   "confidence": 0.97
# }
```

## 🛡️ Reliability Features
*   **Auto-Fallback**: If a `.pkl` file is missing or corrupt, `predict_api.py` automatically returns the data from `forecast_backup_*.json`. The frontend will *never* crash.
*   **Frozen Contract**: Inputs (Hour/Day/Occupancy) and Outputs (List of 24 points) are locked. We won't change them without versioning.

## ❓ Troubleshooting
*   **"Model not found"**: Ensure the `.pkl` files are in the same directory as `predict_api.py`.
*   **"Input Error"**: Ensure occupancy is a float between 0.0 and 1.0.
