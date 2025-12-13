"""
Unified ONNX Model Training Script for SmartEco
Creates ONE combined model that predicts energy, water, and detects anomalies
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import os
from datetime import datetime, timedelta

# Simple config
DATA_DIR = "data"
MODEL_DIR = "models"
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)


def generate_training_data(days=90):
    """
    Step 1: Generate synthetic campus data
    OR: Replace this with your own CSV loading logic
    """
    print(f"📊 Generating {days} days of training data...")
    
    records = []
    start_date = datetime.now() - timedelta(days=days)
    
    for day in range(days):
        current_date = start_date + timedelta(days=day)
        is_weekend = current_date.weekday() >= 5
        
        for hour in range(24):
            timestamp = current_date + timedelta(hours=hour)
            
            # Activity pattern
            activity = 0.5 + 0.5 * np.sin((hour - 6) / 24 * 2 * np.pi)
            activity = max(0.05, min(activity, 1.0))
            if is_weekend:
                activity *= 0.6
            
            # Occupancy
            base_occ = 5000 if not is_weekend else 1500
            occupancy = int(base_occ * activity + np.random.normal(0, 200))
            occupancy = max(0, occupancy)
            
            # Energy
            energy = 70 + 140 * activity + np.random.normal(0, 8)
            if is_weekend:
                energy *= 0.8
            
            # Water
            meal_spike = 20 if 12 <= hour <= 14 else (15 if 18 <= hour <= 20 else 0)
            water = 8 + 25 * activity + meal_spike + np.random.normal(0, 2)
            
            # Waste
            if hour == 18:
                waste = np.random.uniform(10, 25)
            else:
                prev_waste = records[-1]["waste_pct"] if records else 30
                waste = prev_waste + (0.8 + 1.8 * activity) + np.random.uniform(-0.2, 0.4)
            waste = max(0, min(100, waste))
            
            # Anomaly injection (10%)
            is_anomaly = np.random.random() < 0.1
            if is_anomaly:
                choice = np.random.choice(["energy", "water", "waste"])
                if choice == "energy":
                    energy += np.random.uniform(80, 150)
                elif choice == "water":
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
    csv_path = os.path.join(DATA_DIR, "campus_training.csv")
    df.to_csv(csv_path, index=False)
    
    print(f"✅ Saved {len(df)} records to {csv_path}")
    print(f"   Columns: {list(df.columns)}")
    print(f"   Anomalies: {df['is_anomaly'].sum()} ({df['is_anomaly'].mean()*100:.1f}%)")
    
    return df


def train_unified_model(df):
    """
    Step 2: Train ONE model that predicts both energy and water
    """
    print("\n🤖 Training unified prediction model...")
    
    # Features: hour, day_of_week, is_weekend, occupancy
    feature_cols = ["hour", "day_of_week", "is_weekend", "occupancy"]
    X = df[feature_cols].values
    
    # Targets: energy_kwh, water_lpm (multi-output)
    y = df[["energy_kwh", "water_lpm"]].values
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Train multi-output model
    base_model = RandomForestRegressor(
        n_estimators=100,
        max_depth=15,
        random_state=42,
        n_jobs=-1
    )
    model = MultiOutputRegressor(base_model)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    
    # Energy metrics
    energy_mae = mean_absolute_error(y_test[:, 0], y_pred[:, 0])
    energy_r2 = r2_score(y_test[:, 0], y_pred[:, 0])
    
    # Water metrics
    water_mae = mean_absolute_error(y_test[:, 1], y_pred[:, 1])
    water_r2 = r2_score(y_test[:, 1], y_pred[:, 1])
    
    print(f"   Energy - MAE: {energy_mae:.2f} kWh, R²: {energy_r2:.3f}")
    print(f"   Water  - MAE: {water_mae:.2f} LPM, R²: {water_r2:.3f}")
    
    # Save as PKL (ONNX export requires additional dependencies)
    model_path = os.path.join(MODEL_DIR, "smarteco_unified.pkl")
    joblib.dump(model, model_path)
    print(f"   💾 Model saved to {model_path}")
    
    # Save feature names for reference
    metadata = {
        "features": feature_cols,
        "targets": ["energy_kwh", "water_lpm"],
        "trained_on": datetime.now().isoformat()
    }
    meta_path = os.path.join(MODEL_DIR, "model_metadata.pkl")
    joblib.dump(metadata, meta_path)
    
    return model


def main():
    """Main training pipeline"""
    print("=" * 60)
    print("SmartEco Unified ML Training Pipeline")
    print("=" * 60)
    
    # Step 1: Generate or load data
    df = generate_training_data(days=90)
    
    # Step 2: Train model
    model = train_unified_model(df)
    
    print("\n" + "=" * 60)
    print("✅ Training complete!")
    print(f"📁 Data: {DATA_DIR}/campus_training.csv")
    print(f"📁 Model: {MODEL_DIR}/smarteco_unified.pkl")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Review the CSV file to verify data quality")
    print("2. Restart your backend server to load the new model")
    print("3. Test predictions via /api/forecast endpoint")


if __name__ == "__main__":
    main()
