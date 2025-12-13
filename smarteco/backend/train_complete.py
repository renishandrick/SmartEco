"""
Complete ML Training Pipeline for SmartEco
Supports real datasets (ASHRAE) and synthetic data
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.multioutput import MultiOutputRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
import joblib
import os
import json
from datetime import datetime

from data_loader import DataLoader


class ModelTrainer:
    """Complete training pipeline with validation"""
    
    def __init__(self, model_dir: str = "models", data_dir: str = "data"):
        self.model_dir = model_dir
        self.data_dir = data_dir
        os.makedirs(model_dir, exist_ok=True)
        
        self.metrics = {}
    
    def train_energy_water_model(self, df: pd.DataFrame):
        """
        Train unified energy + water prediction model
        """
        print("\n" + "="*60)
        print("🔋💧 Training Energy & Water Prediction Model")
        print("="*60)
        
        # Features
        feature_cols = ["hour", "day_of_week", "is_weekend", "occupancy"]
        X = df[feature_cols].values
        
        # Targets (multi-output)
        y = df[["energy_kwh", "water_lpm"]].values
        
        # Split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, shuffle=True
        )
        
        print(f"Training set: {len(X_train)} samples")
        print(f"Test set: {len(X_test)} samples")
        
        # Train model
        print("\nTraining RandomForest (this may take 1-2 minutes)...")
        base_model = RandomForestRegressor(
            n_estimators=150,
            max_depth=20,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1,
            verbose=0
        )
        model = MultiOutputRegressor(base_model)
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
        
        # Energy metrics
        energy_train_r2 = r2_score(y_train[:, 0], y_pred_train[:, 0])
        energy_test_r2 = r2_score(y_test[:, 0], y_pred_test[:, 0])
        energy_mae = mean_absolute_error(y_test[:, 0], y_pred_test[:, 0])
        energy_rmse = np.sqrt(mean_squared_error(y_test[:, 0], y_pred_test[:, 0]))
        
        # Water metrics
        water_train_r2 = r2_score(y_train[:, 1], y_pred_train[:, 1])
        water_test_r2 = r2_score(y_test[:, 1], y_pred_test[:, 1])
        water_mae = mean_absolute_error(y_test[:, 1], y_pred_test[:, 1])
        water_rmse = np.sqrt(mean_squared_error(y_test[:, 1], y_pred_test[:, 1]))
        
        print("\n📊 Performance Metrics:")
        print(f"\nEnergy Prediction:")
        print(f"  Train R²: {energy_train_r2:.4f}")
        print(f"  Test R²:  {energy_test_r2:.4f}")
        print(f"  MAE:      {energy_mae:.2f} kWh")
        print(f"  RMSE:     {energy_rmse:.2f} kWh")
        
        print(f"\nWater Prediction:")
        print(f"  Train R²: {water_train_r2:.4f}")
        print(f"  Test R²:  {water_test_r2:.4f}")
        print(f"  MAE:      {water_mae:.2f} LPM")
        print(f"  RMSE:     {water_rmse:.2f} LPM")
        
        # Save metrics
        self.metrics['energy'] = {
            'train_r2': float(energy_train_r2),
            'test_r2': float(energy_test_r2),
            'mae': float(energy_mae),
            'rmse': float(energy_rmse)
        }
        self.metrics['water'] = {
            'train_r2': float(water_train_r2),
            'test_r2': float(water_test_r2),
            'mae': float(water_mae),
            'rmse': float(water_rmse)
        }
        
        # Quality check
        if energy_test_r2 < 0.85:
            print("\n⚠️  WARNING: Energy R² below 0.85 - consider more/better data")
        if water_test_r2 < 0.80:
            print("\n⚠️  WARNING: Water R² below 0.80 - consider more/better data")
        
        # Save model
        model_path = os.path.join(self.model_dir, "smarteco_unified.pkl")
        joblib.dump(model, model_path)
        print(f"\n💾 Model saved: {model_path}")
        
        return model
    
    def train_anomaly_detector(self, df: pd.DataFrame):
        """Train anomaly detection model"""
        print("\n" + "="*60)
        print("⚠️  Training Anomaly Detector")
        print("="*60)
        
        feature_cols = ["energy_kwh", "water_lpm", "waste_pct", "hour", "occupancy"]
        X = df[feature_cols].values
        
        model = IsolationForest(
            contamination=0.05,
            max_samples=256,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X)
        
        # Test detection
        predictions = model.predict(X)
        anomalies_detected = (predictions == -1).sum()
        
        if 'is_anomaly' in df.columns:
            actual_anomalies = df['is_anomaly'].sum()
            print(f"\nDetected: {anomalies_detected} anomalies")
            print(f"Actual:   {actual_anomalies} anomalies")
            print(f"Detection rate: {(anomalies_detected/max(actual_anomalies,1))*100:.1f}%")
        else:
            print(f"\nDetected: {anomalies_detected} anomalies ({(anomalies_detected/len(X))*100:.2f}%)")
        
        # Save
        model_path = os.path.join(self.model_dir, "anomaly_detector.pkl")
        joblib.dump(model, model_path)
        print(f"💾 Model saved: {model_path}")
        
        return model
    
    def save_metadata(self, df: pd.DataFrame):
        """Save training metadata"""
        metadata = {
            "trained_on": datetime.now().isoformat(),
            "data_points": len(df),
            "date_range": {
                "start": str(df['timestamp'].min()),
                "end": str(df['timestamp'].max())
            },
            "features": ["hour", "day_of_week", "is_weekend", "occupancy"],
            "targets": ["energy_kwh", "water_lpm"],
            "metrics": self.metrics
        }
        
        meta_path = os.path.join(self.model_dir, "model_metadata.json")
        with open(meta_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\n📋 Metadata saved: {meta_path}")


def main():
    """Main training orchestrator"""
    print("="*60)
    print("SmartEco Complete ML Training Pipeline")
    print("="*60)
    
    # Step 1: Load data
    loader = DataLoader()
    
    # Check for ASHRAE data
    ashrae_path = "data/ashrae_train.csv"
    if os.path.exists(ashrae_path):
        print("\n✅ Found ASHRAE dataset")
        df = loader.load_ashrae(ashrae_path, building_id=100)
    else:
        print("\n📝 ASHRAE not found, using enhanced synthetic data")
        df = loader.generate_synthetic(days=365, include_seasonality=True, include_holidays=True)
    
    # Save processed data
    loader.save(df)
    
    # Step 2: Train models
    trainer = ModelTrainer()
    
    energy_water_model = trainer.train_energy_water_model(df)
    anomaly_model = trainer.train_anomaly_detector(df)
    
    # Step 3: Save metadata
    trainer.save_metadata(df)
    
    # Final summary
    print("\n" + "="*60)
    print("✅ TRAINING COMPLETE!")
    print("="*60)
    print(f"\n📁 Models saved in: models/")
    print(f"📁 Data saved in: data/")
    print("\nNext steps:")
    print("1. Review metrics above")
    print("2. Restart backend: uvicorn main:app --reload --port 8000")
    print("3. Test: curl http://localhost:8000/api/forecast?resource=energy")
    print("="*60)


if __name__ == "__main__":
    main()
