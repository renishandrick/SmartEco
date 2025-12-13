"""
Train ML models for sustainability forecasting
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import json
from datetime import datetime

def prepare_features(df, target_col):
    """
    Prepare features for ML model
    FROZEN FEATURES: hour, day_of_week, occupancy
    """
    # Basic features (MUST KEEP THESE 3)
    X = df[['hour', 'day_of_week', 'occupancy']].copy()
    
    # Add cyclical features for better patterns
    X['hour_sin'] = np.sin(2 * np.pi * X['hour'] / 24)
    X['hour_cos'] = np.cos(2 * np.pi * X['hour'] / 24)
    X['day_sin'] = np.sin(2 * np.pi * X['day_of_week'] / 7)
    X['day_cos'] = np.cos(2 * np.pi * X['day_of_week'] / 7)
    
    # Target variable
    y = df[target_col].values
    
    return X, y

def train_model(X, y, model_name):
    """Train RandomForest model"""
    print(f"\n🔄 Training {model_name} model...")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train model
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train_scaled, y_train)
    
    # Evaluate
    train_score = model.score(X_train_scaled, y_train)
    test_score = model.score(X_test_scaled, y_test)
    
    print(f"   Training R²: {train_score:.3f}")
    print(f"   Testing R²:  {test_score:.3f}")
    
    # Get feature importance
    feature_names = X.columns.tolist()
    importances = model.feature_importances_
    
    print(f"\n   Top features:")
    for name, importance in zip(feature_names, importances):
        if importance > 0.05:  # Show only important features
            print(f"      {name}: {importance:.3f}")
    
    # Save model and scaler
    model_data = {
        'model': model,
        'scaler': scaler,
        'feature_names': feature_names,
        'train_score': train_score,
        'test_score': test_score
    }
    
    joblib.dump(model_data, f'{model_name}.pkl')
    print(f"   💾 Saved: {model_name}.pkl")
    
    return model_data

def create_24h_forecast(model_data, current_hour=14, current_day=2, current_occupancy=0.75):
    """
    Create 24-hour forecast
    OUTPUT FORMAT (FROZEN):
    [
        {"h": 0, "y": value},
        {"h": 1, "y": value},
        ...
        {"h": 23, "y": value}
    ]
    """
    model = model_data['model']
    scaler = model_data['scaler']
    feature_names = model_data['feature_names']
    
    forecasts = []
    
    for hour_ahead in range(24):
        # Calculate future timestamp
        future_hour = (current_hour + hour_ahead) % 24
        future_day = (current_day + (current_hour + hour_ahead) // 24) % 7
        
        # Create feature vector (BASIC 3 FEATURES + cyclical)
        features = {
            'hour': future_hour,
            'day_of_week': future_day,
            'occupancy': current_occupancy * 0.9  # Slight decay
        }
        
        # Add cyclical features
        features['hour_sin'] = np.sin(2 * np.pi * features['hour'] / 24)
        features['hour_cos'] = np.cos(2 * np.pi * features['hour'] / 24)
        features['day_sin'] = np.sin(2 * np.pi * features['day_of_week'] / 7)
        features['day_cos'] = np.cos(2 * np.pi * features['day_of_week'] / 7)
        
        # Convert to array in correct order
        X_pred = np.array([[features[col] for col in feature_names]])
        
        # Scale and predict
        X_pred_scaled = scaler.transform(X_pred)
        prediction = model.predict(X_pred_scaled)[0]
        
        # Ensure positive values
        prediction = max(0, round(float(prediction), 2))
        
        forecasts.append({
            "h": hour_ahead,
            "y": prediction
        })
    
    return forecasts

def main():
    print("=" * 60)
    print("🌱 SUSTAINABILITY FORECASTING - MODEL TRAINING")
    print("=" * 60)
    
    # Load data
    print("\n📂 Loading dataset...")
    df = pd.read_csv('sustainability_data.csv')
    print(f"   Loaded {len(df)} rows")
    
    # Train models for each resource
    models = {}
    
    # 1. Electricity model
    X_elec, y_elec = prepare_features(df, 'electricity_usage')
    models['electricity'] = train_model(X_elec, y_elec, 'forecast_electricity')
    
    # 2. Water model
    X_water, y_water = prepare_features(df, 'water_usage')
    models['water'] = train_model(X_water, y_water, 'forecast_water')
    
    # 3. Waste model
    X_waste, y_waste = prepare_features(df, 'waste_generated')
    models['waste'] = train_model(X_waste, y_waste, 'forecast_waste')
    
    # Create backup forecasts
    print("\n📝 Creating backup forecasts...")
    
    # Example current conditions: Wednesday 2 PM, 75% occupancy
    current_conditions = {
        'hour': 14,
        'day_of_week': 2,  # Wednesday
        'occupancy': 0.75
    }
    
    for resource in ['electricity', 'water', 'waste']:
        forecast = create_24h_forecast(
            models[resource],
            current_hour=current_conditions['hour'],
            current_day=current_conditions['day_of_week'],
            current_occupancy=current_conditions['occupancy']
        )
        
        # Save as JSON
        output = {
            "forecast": forecast,
            "confidence": round(float(models[resource]['test_score']), 3),
            "model_version": "v2.1",
            "generated_at": datetime.now().isoformat(),
            "current_conditions": current_conditions
        }
        
        with open(f'forecast_backup_{resource}.json', 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"   💾 Saved: forecast_backup_{resource}.json")
        
        # Show sample
        print(f"   Sample {resource} forecast (first 3 hours):")
        for point in forecast[:3]:
            print(f"      Hour {point['h']}: {point['y']}")
    
    # Create feature importances
    print("\n📊 Creating feature importances...")
    feature_importances = {}
    
    for resource in ['electricity', 'water', 'waste']:
        model = models[resource]['model']
        features = models[resource]['feature_names']
        importances = model.feature_importances_
        
        feature_importances[resource] = {
            feature: round(float(importance), 4)
            for feature, importance in zip(features, importances)
        }
    
    with open('feature_importances.json', 'w') as f:
        json.dump(feature_importances, f, indent=2)
    
    print("   💾 Saved: feature_importances.json")
    
    # Create model specification
    print("\n📄 Creating model specification...")
    spec = {
        "input_features": ["hour", "day_of_week", "occupancy"],
        "output_format": "List of 24 points: {'h': 0-23, 'y': float}",
        "models_trained": ["electricity", "water", "waste"],
        "training_date": datetime.now().isoformat(),
        "note": "BASIC 3 FEATURES ARE FROZEN. Internal features can be extended."
    }
    
    with open('model_specification.txt', 'w') as f:
        f.write("MODEL SPECIFICATION\n")
        f.write("=" * 50 + "\n\n")
        f.write("FROZEN INPUT FEATURES (3 columns):\n")
        f.write("1. hour (0-23)\n")
        f.write("2. day_of_week (0-6, 0=Monday)\n")
        f.write("3. occupancy (0-1, float)\n\n")
        f.write("FROZEN OUTPUT FORMAT:\n")
        f.write("24-point forecast in format: [{'h':0,'y':value}, ...]\n\n")
        f.write("Files delivered:\n")
        f.write("- forecast_electricity.pkl\n")
        f.write("- forecast_water.pkl\n")
        f.write("- forecast_waste.pkl\n")
        f.write("- forecast_backup_*.json (3 files)\n")
        f.write("- sample_data.csv\n")
    
    print("   💾 Saved: model_specification.txt")
    
    print("\n" + "=" * 60)
    print("✅ TRAINING COMPLETE!")
    print("=" * 60)
    
    # Test loading
    print("\n🧪 Testing model loading...")
    try:
        test_model = joblib.load('forecast_electricity.pkl')
        print("   ✅ Joblib loading works!")
        
        # Test prediction
        test_input = [[14, 2, 0.75]]  # Wednesday 2PM, 75% occupancy
        print(f"   Test input: {test_input}")
        
        # Note: Real prediction needs scaling
        print("   📝 Note: Backend will handle scaling automatically")
        
    except Exception as e:
        print(f"   ❌ Loading failed: {e}")

if __name__ == "__main__":
    main()