"""
AI Forecasting Core (Tier-A) Integration
Pre-trained models with zero-crash fallback system
"""
import joblib
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta


class TierAForecaster:
    """
    Production-ready ML forecaster with automatic fallback
    Uses pre-trained models from ml_package/
    """
    
    def __init__(self, package_dir: str = "ml_package"):
        self.package_dir = package_dir
        self.models = {}
        self.backups = {}
        self.ready = False
        
        self._load_models()
    
    def _load_models(self):
        """Load pre-trained models and JSON backups"""
        resources = ["electricity", "water", "waste"]
        
        for resource in resources:
            pkl_path = os.path.join(self.package_dir, f"forecast_{resource}.pkl")
            json_path = os.path.join(self.package_dir, f"forecast_backup_{resource}.json")
            
            # Try loading PKL model
            try:
                if os.path.exists(pkl_path):
                    self.models[resource] = joblib.load(pkl_path)
                    print(f"✅ Loaded {resource} model (.pkl)")
            except Exception as e:
                print(f"⚠️  Failed to load {resource} model: {e}")
            
            # Load JSON backup
            try:
                if os.path.exists(json_path):
                    with open(json_path, 'r') as f:
                        self.backups[resource] = json.load(f)
                    print(f"✅ Loaded {resource} backup (.json)")
            except Exception as e:
                print(f"⚠️  Failed to load {resource} backup: {e}")
        
        self.ready = len(self.models) > 0 or len(self.backups) > 0
        
        if self.ready:
            print(f"🚀 Tier-A Forecaster initialized")
            print(f"   Models loaded: {list(self.models.keys())}")
            print(f"   Backups available: {list(self.backups.keys())}")
    
    def get_forecast(
        self,
        resource: str,
        hour: int,
        day_of_week: int,
        occupancy: float
    ) -> Dict[str, Any]:
        """
        Get single-point forecast
        
        Args:
            resource: "electricity", "water", or "waste"
            hour: Hour of day (0-23)
            day_of_week: Day of week (0=Mon, 6=Sun)
            occupancy: Occupancy ratio (0.0-1.0)
        
        Returns:
            {"value": float, "unit": str, "tier": str}
        """
        # Map resource names
        resource_map = {"energy": "electricity"}
        resource = resource_map.get(resource, resource)
        
        # Try ML model first
        if resource in self.models:
            try:
                import numpy as np
                is_weekend = 1 if day_of_week >= 5 else 0
                
                # Prepare features (adjust based on model training)
                X = np.array([[hour, day_of_week, is_weekend, occupancy]])
                
                prediction = self.models[resource].predict(X)[0]
                
                return {
                    "value": round(float(prediction), 2),
                    "unit": self._get_unit(resource),
                    "tier": "A (ML)",
                    "source": "trained_model"
                }
            except Exception as e:
                print(f"ML prediction failed for {resource}: {e}")
        
        # Fallback to JSON backup
        if resource in self.backups:
            backup_data = self.backups[resource]
            # Use hour-based lookup from backup
            if "hourly_pattern" in backup_data:
                value = backup_data["hourly_pattern"].get(str(hour), 0)
                return {
                    "value": value,
                    "unit": self._get_unit(resource),
                    "tier": "A (Backup)",
                    "source": "json_fallback"
                }
        
        # Final fallback
        return {
            "value": 0.0,
            "unit": self._get_unit(resource),
            "tier": "B (Default)",
            "source": "default"
        }
    
    def get_24h_forecast(
        self,
        resource: str,
        occupancy: float = 0.75
    ) -> List[Dict[str, Any]]:
        """
        Generate 24-hour forecast
        
        Args:
            resource: "electricity", "water", or "waste"
            occupancy: Average occupancy ratio (0.0-1.0)
        
        Returns:
            List of 24 hourly predictions
        """
        now = datetime.now()
        forecast = []
        
        for h in range(24):
            future_time = now + timedelta(hours=h)
            hour = future_time.hour
            dow = future_time.weekday()
            
            pred = self.get_forecast(resource, hour, dow, occupancy)
            
            forecast.append({
                "h": h,
                "timestamp": future_time.isoformat(),
                "y": pred["value"],
                "unit": pred["unit"]
            })
        
        return forecast
    
    def _get_unit(self, resource: str) -> str:
        """Get unit for resource"""
        units = {
            "electricity": "kWh",
            "energy": "kWh",
            "water": "LPM",
            "waste": "%"
        }
        return units.get(resource, "")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get system health status"""
        return {
            "tier_a_ready": self.ready,
            "models_loaded": list(self.models.keys()),
            "backups_available": list(self.backups.keys()),
            "package_dir": self.package_dir,
            "zero_crash": len(self.backups) > 0
        }


# Global instance
_forecaster: Optional[TierAForecaster] = None


def get_forecaster() -> TierAForecaster:
    """Get or create global forecaster instance"""
    global _forecaster
    if _forecaster is None:
        _forecaster = TierAForecaster()
    return _forecaster
