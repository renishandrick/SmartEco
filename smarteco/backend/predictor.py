"""
Production Predictor Service with Health Checks
"""
import joblib
import numpy as np
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional


class ProductionPredictor:
    """Production-ready ML predictor with error handling"""
    
    def __init__(self, model_dir: str = "models"):
        self.model_dir = model_dir
        self.ready = False
        self.metadata = {}
        self.load_models()
    
    def load_models(self):
        """Load all models and metadata"""
        try:
            # Load main model
            model_path = os.path.join(self.model_dir, "smarteco_unified.pkl")
            if not os.path.exists(model_path):
                print("⚠️  Model not found. Run train_complete.py first.")
                return
            
            self.model = joblib.load(model_path)
            
            # Load anomaly detector
            anomaly_path = os.path.join(self.model_dir, "anomaly_detector.pkl")
            if os.path.exists(anomaly_path):
                self.anomaly_model = joblib.load(anomaly_path)
            else:
                self.anomaly_model = None
            
            # Load metadata
            meta_path = os.path.join(self.model_dir, "model_metadata.json")
            if os.path.exists(meta_path):
                with open(meta_path, 'r') as f:
                    self.metadata = json.load(f)
            
            self.ready = True
            print(f"✅ Models loaded successfully")
            if self.metadata:
                print(f"   Trained: {self.metadata.get('trained_on', 'Unknown')[:10]}")
                print(f"   Data points: {self.metadata.get('data_points', 'Unknown')}")
            
        except Exception as e:
            print(f"❌ Failed to load models: {e}")
            self.ready = False
    
    def predict(
        self, 
        hour: int, 
        day_of_week: int, 
        is_weekend: int, 
        occupancy: float
    ) -> Dict[str, float]:
        """
        Predict energy and water for given conditions
        
        Returns:
            {"energy_kwh": float, "water_lpm": float}
        """
        if not self.ready:
            return {"energy_kwh": 0.0, "water_lpm": 0.0}
        
        try:
            X = np.array([[hour, day_of_week, is_weekend, occupancy]])
            predictions = self.model.predict(X)[0]
            
            return {
                "energy_kwh": round(float(predictions[0]), 2),
                "water_lpm": round(float(predictions[1]), 2)
            }
        except Exception as e:
            print(f"Prediction error: {e}")
            return {"energy_kwh": 0.0, "water_lpm": 0.0}
    
    def detect_anomaly(
        self,
        energy_kwh: float,
        water_lpm: float,
        waste_pct: float,
        hour: int,
        occupancy: float
    ) -> Dict[str, Any]:
        """Detect if readings are anomalous"""
        if not self.ready or self.anomaly_model is None:
            return {"is_anomaly": False, "confidence": 0.0}
        
        try:
            X = np.array([[energy_kwh, water_lpm, waste_pct, hour, occupancy]])
            prediction = self.anomaly_model.predict(X)[0]
            score = self.anomaly_model.score_samples(X)[0]
            
            return {
                "is_anomaly": bool(prediction == -1),
                "confidence": round(float(abs(score)), 3)
            }
        except Exception as e:
            print(f"Anomaly detection error: {e}")
            return {"is_anomaly": False, "confidence": 0.0}
    
    def forecast_24h(self, resource: str = "energy", occupancy: float = 3000) -> List[Dict[str, Any]]:
        """Generate 24-hour forecast"""
        if not self.ready:
            return []
        
        now = datetime.now()
        forecast = []
        
        for h in range(24):
            future_time = now + timedelta(hours=h)
            hour = future_time.hour
            dow = future_time.weekday()
            is_weekend = int(dow >= 5)
            
            pred = self.predict(hour, dow, is_weekend, occupancy)
            
            value = pred["energy_kwh"] if resource == "energy" else pred["water_lpm"]
            
            forecast.append({
                "h": h,
                "timestamp": future_time.isoformat(),
                "y": value
            })
        
        return forecast
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get ML system health status"""
        return {
            "ml_ready": self.ready,
            "model_loaded": self.ready,
            "anomaly_detector_loaded": self.anomaly_model is not None,
            "trained_on": self.metadata.get("trained_on", "Unknown"),
            "data_points": self.metadata.get("data_points", 0),
            "metrics": self.metadata.get("metrics", {})
        }


# Global instance
_predictor: Optional[ProductionPredictor] = None


def get_predictor() -> ProductionPredictor:
    """Get or create global predictor instance"""
    global _predictor
    if _predictor is None:
        _predictor = ProductionPredictor()
    return _predictor
