import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestRegressor
import joblib
import os
import warnings

# Suppress sklearn warnings for cleaner logs
warnings.filterwarnings("ignore")

class SmartEcoAI:
    def __init__(self):
        self.model_dir = "ml_models_trained"
        self.anomaly_model_path = os.path.join(self.model_dir, "anomaly_detector.pkl")
        self.maintenance_model_path = os.path.join(self.model_dir, "maintenance_predictor.pkl")
        
        self.anomaly_detector = None
        self.maintenance_predictor = None
        self.is_trained = False
        self.model_source = "none"
        
    def load_or_train(self):
        """Load pre-trained models if available, otherwise train on mock data"""
        if self.is_trained:
            return
        
        # Try to load from disk first (auto-trained models)
        if os.path.exists(self.anomaly_model_path) and os.path.exists(self.maintenance_model_path):
            try:
                print("🔄 Loading pre-trained models from disk...")
                self.anomaly_detector = joblib.load(self.anomaly_model_path)
                self.maintenance_predictor = joblib.load(self.maintenance_model_path)
                self.is_trained = True
                self.model_source = "auto_trained"
                print("✅ Loaded auto-trained models successfully!")
                return
            except Exception as e:
                print(f"⚠️  Failed to load models: {e}. Falling back to mock training.")
        
        # Fallback: Train on synthetic data
        self.train_mock()
        
    def train_mock(self):
        """Train models on synthetic baseline data to simulate learning"""
        print("🧠 Training AI Models...")
        
        # Generate normal operating data (Synthetic Baseline)
        # Energy: 300-600 kWh
        # Water: 50-150 LPM
        n_samples = 2000
        
        # Feature 1: Energy (Normal distribution centered at 450)
        energy = np.random.normal(450, 50, n_samples)
        
        # Feature 2: Water (Normal distribution centered at 100)
        water = np.random.normal(100, 20, n_samples)
        
        X_train = np.column_stack((energy, water))
        
        # 1. Train Anomaly Detector (Unsupervised)
        self.anomaly_detector.fit(X_train)
        
        # 2. Train Maintenance Predictor (Supervised Mock)
        # Hypothesis: Higher sustained load = Lower instant health score
        # Normalize inputs roughly 0-1 for health calc
        norm_e = (energy - 300) / 300
        norm_w = (water - 50) / 100
        
        # Health starts at 100, drops based on stress
        stress = (norm_e * 0.6 + norm_w * 0.4) 
        y_health = 100 - (stress * 15) - np.random.normal(0, 2, n_samples)
        y_health = np.clip(y_health, 60, 100) # Health generally stays high
        
        self.maintenance_predictor.fit(X_train, y_health)
        
        self.is_trained = True
        print("✅ SmartEco AI Models Ready (Anomaly Detection + Predictive Maintenance)")

    def check_anomaly(self, energy, water):
        """Returns True if data is anomalous"""
        if not self.is_trained: self.load_or_train()
        
        X = np.array([[energy, water]])
        # predict returns -1 for outlier, 1 for inlier
        pred = self.anomaly_detector.predict(X)[0]
        return pred == -1

    def predict_maintenance_health(self, energy, water):
        """Returns Health Score (0-100%)"""
        if not self.is_trained: self.load_or_train()
        
        X = np.array([[energy, water]])
        return float(self.maintenance_predictor.predict(X)[0])

# Global Singleton
AI_ENGINE = SmartEcoAI()
