"""
Forecasting API - Main interface for backend
"""
import joblib
import numpy as np
import json
import os
from typing import Dict, Any

class SustainabilityForecaster:
    def __init__(self, models_dir: str = "../models"):
        self.models = {}
        self.backups = {}
        
        # Load models
        for resource in ['electricity', 'water', 'waste']:
            model_path = f"{models_dir}/forecast_{resource}.pkl"
            backup_path = f"../backups/forecast_backup_{resource}.json"
            
            try:
                self.models[resource] = joblib.load(model_path)
                print(f"✅ Loaded {resource} model")
            except:
                self.models[resource] = None
            
            try:
                with open(backup_path, 'r') as f:
                    self.backups[resource] = json.load(f)
            except:
                self.backups[resource] = None
    
    def predict(self, resource: str, hour: int, day_of_week: int, occupancy: float) -> Dict[str, Any]:
        """Main prediction function"""
        if resource not in self.models or self.models[resource] is None:
            return self._get_backup(resource, hour, day_of_week, occupancy)
        
        try:
            model_data = self.models[resource]
            forecast = self._make_prediction(model_data, hour, day_of_week, occupancy)
            
            return {
                "success": True,
                "resource": resource,
                "forecast": forecast,
                "confidence": model_data['test_score'],
                "model_used": "trained"
            }
            
        except Exception as e:
            return self._get_backup(resource, hour, day_of_week, occupancy, str(e))
    
    def _make_prediction(self, model_data, hour, day_of_week, occupancy):
        """Internal prediction logic"""
        model = model_data['model']
        scaler = model_data['scaler']
        features = model_data['feature_names']
        
        predictions = []
        
        for h_ahead in range(24):
            future_hour = (hour + h_ahead) % 24
            future_day = (day_of_week + (hour + h_ahead) // 24) % 7
            
            # Prepare feature vector
            feat_dict = {
                'hour': future_hour,
                'day_of_week': future_day,
                'occupancy': occupancy * 0.95,  # Slight decay
                'hour_sin': np.sin(2*np.pi*future_hour/24),
                'hour_cos': np.cos(2*np.pi*future_hour/24),
                'day_sin': np.sin(2*np.pi*future_day/7),
                'day_cos': np.cos(2*np.pi*future_day/7)
            }
            
            X = np.array([[feat_dict[f] for f in features]])
            X_scaled = scaler.transform(X)
            pred = model.predict(X_scaled)[0]
            
            predictions.append({
                "h": h_ahead,
                "y": max(0, round(float(pred), 2))
            })
        
        return predictions
    
    def _get_backup(self, resource, hour, day_of_week, occupancy, error=None):
        """Get backup forecast"""
        if resource in self.backups and self.backups[resource]:
            result = self.backups[resource].copy()
            result["success"] = False
            result["using_backup"] = True
            if error:
                result["error"] = error
            return result
        
        # Create simple fallback
        forecast = []
        for h in range(24):
            if resource == 'electricity':
                val = 50 + 20 * np.sin(2*np.pi*(hour+h)/24)
            elif resource == 'water':
                val = 20 + 10 * np.exp(-(((hour+h)%24-8)/4)**2)
            else:
                val = max(0, 5 + ((hour+h)%24)*1.5)
            
            forecast.append({"h": h, "y": round(val, 2)})
        
        return {
            "success": False,
            "resource": resource,
            "forecast": forecast,
            "confidence": 0.5,
            "model_used": "fallback",
            "error": error or "Model unavailable"
        }

# Simple interface
def get_forecast(resource: str, hour: int, day_of_week: int, occupancy: float) -> str:
    """One-line function for backend"""
    if not hasattr(get_forecast, 'forecaster'):
        get_forecast.forecaster = SustainabilityForecaster()
    
    result = get_forecast.forecaster.predict(resource, hour, day_of_week, occupancy)
    return json.dumps(result, indent=2)

if __name__ == "__main__":
    # Test
    print("🧪 Testing forecast API...")
    result = get_forecast("electricity", 14, 2, 0.75)
    data = json.loads(result)
    
    print(f"Success: {data.get('success')}")
    print(f"Forecast points: {len(data.get('forecast', []))}")
    
    # Save sample
    os.makedirs('../backups/sample_outputs', exist_ok=True)
    with open('../backups/sample_outputs/forecast_sample.json', 'w') as f:
        f.write(result)
    print("💾 Saved sample: backups/sample_outputs/forecast_sample.json")