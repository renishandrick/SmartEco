"""
ML Predictor Module with ONNX Runtime Support
Loads models and provides prediction interface
"""
import os
import joblib
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

try:
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    ONNX_AVAILABLE = False
    print("⚠️  ONNX Runtime not available, using PKL models only")

from config import Config


class SmartEcoPredictor:
    """
    Unified predictor supporting both PKL and ONNX model formats.
    Automatically selects best available format.
    """
    
    def __init__(self, use_onnx: bool = True):
        """
        Initialize predictor and load models.
        
        Args:
            use_onnx: Prefer ONNX models if available
        """
        self.use_onnx = use_onnx and ONNX_AVAILABLE
        self.ready = False
        
        try:
            if self.use_onnx:
                self._load_onnx_models()
            else:
                self._load_pkl_models()
            
            self.ready = True
            print(f"✅ Predictor initialized (Format: {'ONNX' if self.use_onnx else 'PKL'})")
            
        except Exception as e:
            print(f"❌ Failed to load models: {e}")
            self.ready = False
    
    def _load_pkl_models(self):
        """Load PKL format models"""
        self.energy_model = joblib.load(
            os.path.join(Config.PKL_DIR, "energy_model.pkl")
        )
        self.water_model = joblib.load(
            os.path.join(Config.PKL_DIR, "water_model.pkl")
        )
        self.anomaly_model = joblib.load(
            os.path.join(Config.PKL_DIR, "anomaly_model.pkl")
        )
    
    def _load_onnx_models(self):
        """Load ONNX format models"""
        self.energy_session = ort.InferenceSession(
            os.path.join(Config.ONNX_DIR, "energy_model.onnx")
        )
        self.water_session = ort.InferenceSession(
            os.path.join(Config.ONNX_DIR, "water_model.onnx")
        )
        self.anomaly_session = ort.InferenceSession(
            os.path.join(Config.ONNX_DIR, "anomaly_model.onnx")
        )
    
    def predict_energy(
        self, 
        hour: int, 
        day_of_week: int, 
        is_weekend: int, 
        occupancy: float
    ) -> float:
        """
        Predict energy consumption for given conditions.
        
        Args:
            hour: Hour of day (0-23)
            day_of_week: Day of week (0=Mon, 6=Sun)
            is_weekend: 1 if weekend, 0 otherwise
            occupancy: Number of people
        
        Returns:
            Predicted energy in kWh
        """
        if not self.ready:
            return 0.0
        
        X = np.array([[hour, day_of_week, is_weekend, occupancy]], dtype=np.float32)
        
        if self.use_onnx:
            input_name = self.energy_session.get_inputs()[0].name
            result = self.energy_session.run(None, {input_name: X})
            return float(result[0][0])
        else:
            return float(self.energy_model.predict(X)[0])
    
    def predict_water(
        self, 
        hour: int, 
        day_of_week: int, 
        is_weekend: int, 
        occupancy: float
    ) -> float:
        """Predict water consumption"""
        if not self.ready:
            return 0.0
        
        X = np.array([[hour, day_of_week, is_weekend, occupancy]], dtype=np.float32)
        
        if self.use_onnx:
            input_name = self.water_session.get_inputs()[0].name
            result = self.water_session.run(None, {input_name: X})
            return float(result[0][0])
        else:
            return float(self.water_model.predict(X)[0])
    
    def detect_anomaly(
        self,
        energy_kwh: float,
        water_lpm: float,
        waste_pct: float,
        hour: int,
        occupancy: float
    ) -> Dict[str, Any]:
        """
        Detect if current readings are anomalous.
        
        Returns:
            Dict with 'is_anomaly' (bool) and 'score' (float)
        """
        if not self.ready:
            return {"is_anomaly": False, "score": 0.0}
        
        X = np.array([[energy_kwh, water_lpm, waste_pct, hour, occupancy]], dtype=np.float32)
        
        if self.use_onnx:
            input_name = self.anomaly_session.get_inputs()[0].name
            result = self.anomaly_session.run(None, {input_name: X})
            prediction = int(result[0][0])
            is_anomaly = prediction == -1
            score = abs(result[1][0][0]) if len(result) > 1 else 0.5
        else:
            prediction = self.anomaly_model.predict(X)[0]
            is_anomaly = prediction == -1
            score = 0.5  # PKL IsolationForest doesn't provide probability
        
        return {
            "is_anomaly": bool(is_anomaly),
            "score": float(score)
        }
    
    def predict_24h_energy(self, occupancy: float = 3000) -> List[Dict[str, Any]]:
        """Generate 24-hour energy forecast"""
        if not self.ready:
            return []
        
        now = datetime.now()
        forecast = []
        
        for h in range(24):
            future_time = now + timedelta(hours=h)
            hour = future_time.hour
            dow = future_time.weekday()
            is_weekend = int(dow >= 5)
            
            predicted_kwh = self.predict_energy(hour, dow, is_weekend, occupancy)
            
            forecast.append({
                "h": h,
                "timestamp": future_time.isoformat(),
                "y": round(predicted_kwh, 2)
            })
        
        return forecast
    
    def predict_24h_water(self, occupancy: float = 3000) -> List[Dict[str, Any]]:
        """Generate 24-hour water forecast"""
        if not self.ready:
            return []
        
        now = datetime.now()
        forecast = []
        
        for h in range(24):
            future_time = now + timedelta(hours=h)
            hour = future_time.hour
            dow = future_time.weekday()
            is_weekend = int(dow >= 5)
            
            predicted_lpm = self.predict_water(hour, dow, is_weekend, occupancy)
            
            forecast.append({
                "h": h,
                "timestamp": future_time.isoformat(),
                "y": round(predicted_lpm, 2)
            })
        
        return forecast


# Global predictor instance
_predictor: Optional[SmartEcoPredictor] = None


def get_predictor(use_onnx: bool = True) -> SmartEcoPredictor:
    """Get or create global predictor instance"""
    global _predictor
    if _predictor is None:
        _predictor = SmartEcoPredictor(use_onnx=use_onnx)
    return _predictor
