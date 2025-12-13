"""
Enhanced ML Training Pipeline with ONNX Export
Generates synthetic data, trains models, and exports to both PKL and ONNX formats
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType
import joblib
import onnx
import os
from datetime import datetime, timedelta

from config import Config


def generate_synthetic_data(days: int = None) -> pd.DataFrame:
    """
    Generate realistic synthetic campus data for training.
    
    Args:
        days: Number of days to generate (default from Config)
    
    Returns:
        DataFrame with hourly campus telemetry
    """
    if days is None:
        days = Config.TRAINING_DAYS
    
    print(f"📊 Generating {days} days of synthetic campus data...")
    
    records = []
    start_date = datetime.now() - timedelta(days=days)
    
    for day in range(days):
        current_date = start_date + timedelta(days=day)
        is_weekend = current_date.weekday() >= 5
        
        for hour in range(24):
            timestamp = current_date + timedelta(hours=hour)
            
            # Activity curve (peak at 2pm)
            activity = 0.5 + 0.5 * np.sin((hour - 6) / 24 * 2 * np.pi)
            activity = max(0.05, min(activity, 1.0))
            
            # Weekend reduction
            if is_weekend:
                activity *= 0.6
            
            # Occupancy
            base_occupancy = 5000 if not is_weekend else 1500
            occupancy = int(base_occupancy * activity + np.random.normal(0, 200))
            occupancy = max(0, occupancy)
            
            # Energy (kWh)
            energy = 70 + 140 * activity + np.random.normal(0, 8)
            if is_weekend:
                energy *= 0.8
            
            # Water (LPM) with meal spikes
            meal_spike = 0
            if 12 <= hour <= 14:
                meal_spike = 20
            elif 18 <= hour <= 20:
                meal_spike = 15
            water = 8 + 25 * activity + meal_spike + np.random.normal(0, 2)
            
            # Waste (%)
            if hour == 18:
                waste = np.random.uniform(10, 25)
            else:
                prev_waste = records[-1]["waste_pct"] if records else 30
                waste = prev_waste + (0.8 + 1.8 * activity) + np.random.uniform(-0.2, 0.4)
            waste = max(0, min(100, waste))
            
            # Inject anomalies (10%)
            is_anomaly = np.random.random() < 0.1
            if is_anomaly:
                anomaly_type = np.random.choice(["energy", "water", "waste"])
                if anomaly_type == "energy":
                    energy += np.random.uniform(80, 150)
                elif anomaly_type == "water":
                    water += np.random.uniform(50, 120)
                else:
                    waste = max(waste, np.random.uniform(92, 99))
            
            records.append({
                "timestamp": timestamp.isoformat(),
                "hour": hour,
                "day_of_week": current_date.weekday(),
                "is_weekend": int(is_weekend),
                "occupancy": occupancy,
                "energy_kwh": round(energy, 2),
                "water_lpm": round(water, 2),
                "waste_pct": round(waste, 2),
                "is_anomaly": int(is_anomaly)
            })
    
    df = pd.DataFrame(records)
    csv_path = os.path.join(Config.DATA_DIR, "campus_training.csv")
    df.to_csv(csv_path, index=False)
    
    print(f"✅ Generated {len(df)} records → {csv_path}")
    print(f"   Anomalies: {df['is_anomaly'].sum()} ({df['is_anomaly'].mean()*100:.1f}%)")
    
    return df


def export_to_onnx(model, scaler, feature_names, model_name):
    """
    Export sklearn model to ONNX format.
    
    Args:
        model: Trained sklearn model
        scaler: Fitted StandardScaler (if used, else None)
        feature_names: List of feature column names
        model_name: Name for the ONNX file (without extension)
    """
    n_features = len(feature_names)
    initial_type = [('float_input', FloatTensorType([None, n_features]))]
    
    try:
        # Convert model to ONNX
        onnx_model = convert_sklearn(model, initial_types=initial_type)
        
        # Save ONNX model
        onnx_path = os.path.join(Config.ONNX_DIR, f"{model_name}.onnx")
        with open(onnx_path, "wb") as f:
            f.write(onnx_model.SerializeToString())
        
        print(f"   📦 ONNX exported → {onnx_path}")
        
        # Save scaler separately if exists
        if scaler is not None:
            scaler_path = os.path.join(Config.PKL_DIR, f"{model_name}_scaler.pkl")
            joblib.dump(scaler, scaler_path)
            
    except Exception as e:
        print(f"   ⚠️  ONNX export failed: {e}")


def train_energy_model(df: pd.DataFrame):
    """Train and export Energy prediction model"""
    print("\n🔋 Training Energy Predictor...")
    
    feature_cols = ["hour", "day_of_week", "is_weekend", "occupancy"]
    X = df[feature_cols]
    y = df["energy_kwh"]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=Config.TEST_SIZE, random_state=Config.RANDOM_STATE
    )
    
    model = RandomForestRegressor(**Config.ENERGY_MODEL_PARAMS)
    model.fit(X_train, y_train)
    
    # Metrics
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"   MAE: {mae:.2f} kWh")
    print(f"   R²: {r2:.3f}")
    
    # Save PKL
    pkl_path = os.path.join(Config.PKL_DIR, "energy_model.pkl")
    joblib.dump(model, pkl_path)
    print(f"   💾 PKL saved → {pkl_path}")
    
    # Export ONNX
    export_to_onnx(model, None, feature_cols, "energy_model")


def train_water_model(df: pd.DataFrame):
    """Train and export Water prediction model"""
    print("\n💧 Training Water Predictor...")
    
    feature_cols = ["hour", "day_of_week", "is_weekend", "occupancy"]
    X = df[feature_cols]
    y = df["water_lpm"]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=Config.TEST_SIZE, random_state=Config.RANDOM_STATE
    )
    
    model = RandomForestRegressor(**Config.WATER_MODEL_PARAMS)
    model.fit(X_train, y_train)
    
    # Metrics
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"   MAE: {mae:.2f} LPM")
    print(f"   R²: {r2:.3f}")
    
    # Save PKL
    pkl_path = os.path.join(Config.PKL_DIR, "water_model.pkl")
    joblib.dump(model, pkl_path)
    print(f"   💾 PKL saved → {pkl_path}")
    
    # Export ONNX
    export_to_onnx(model, None, feature_cols, "water_model")


def train_anomaly_model(df: pd.DataFrame):
    """Train and export Anomaly detection model"""
    print("\n⚠️  Training Anomaly Detector...")
    
    feature_cols = ["energy_kwh", "water_lpm", "waste_pct", "hour", "occupancy"]
    X = df[feature_cols]
    
    model = IsolationForest(**Config.ANOMALY_MODEL_PARAMS)
    model.fit(X)
    
    # Test detection
    predictions = model.predict(X)
    detected_anomalies = (predictions == -1).sum()
    actual_anomalies = df["is_anomaly"].sum()
    
    print(f"   Detected: {detected_anomalies} anomalies")
    print(f"   Actual: {actual_anomalies} anomalies")
    print(f"   Detection Rate: {(detected_anomalies/actual_anomalies)*100:.1f}%")
    
    # Save PKL
    pkl_path = os.path.join(Config.PKL_DIR, "anomaly_model.pkl")
    joblib.dump(model, pkl_path)
    print(f"   💾 PKL saved → {pkl_path}")
    
    # Export ONNX
    export_to_onnx(model, None, feature_cols, "anomaly_model")


def main():
    """Main training pipeline"""
    print("=" * 60)
    print("SmartEco ML Training Pipeline (Enhanced with ONNX)")
    print("=" * 60)
    
    # Generate data
    df = generate_synthetic_data()
    
    # Train all models
    train_energy_model(df)
    train_water_model(df)
    train_anomaly_model(df)
    
    print("\n" + "=" * 60)
    print("✅ All models trained and exported successfully!")
    print(f"📁 PKL models: {Config.PKL_DIR}")
    print(f"📁 ONNX models: {Config.ONNX_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
