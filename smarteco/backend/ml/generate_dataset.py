import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# Ensure directories exist
os.makedirs("data", exist_ok=True)

def generate_campus_dataset(days=90, output_path="data/campus_training.csv"):
    """
    Generate realistic simulated campus resource usage data for ML training.
    """
    print(f"Generating {days} days of campus data...")
    
    records = []
    start_date = datetime.now() - timedelta(days=days)
    
    for day in range(days):
        current_date = start_date + timedelta(days=day)
        is_weekend = current_date.weekday() >= 5
        
        for hour in range(24):
            timestamp = current_date + timedelta(hours=hour)
            
            # Base activity level (0-1 scale)
            activity = 0.5 + 0.5 * np.sin((hour - 6) / 24 * 2 * np.pi)
            activity = max(0.05, min(activity, 1.0))
            
            # Weekend reduction
            if is_weekend:
                activity *= 0.6
            
            # Occupancy (people on campus)
            base_occupancy = 5000 if not is_weekend else 1500
            occupancy = int(base_occupancy * activity + np.random.normal(0, 200))
            occupancy = max(0, occupancy)
            
            # Energy (kWh)
            energy = 70 + 140 * activity + np.random.normal(0, 8)
            if is_weekend:
                energy *= 0.8
            
            # Water (LPM)
            meal_spike = 0
            if 12 <= hour <= 14:
                meal_spike = 20
            elif 18 <= hour <= 20:
                meal_spike = 15
            water = 8 + 25 * activity + meal_spike + np.random.normal(0, 2)
            
            # Waste (%)
            # Gradual increase through day, reset at 18:00
            if hour == 18:
                waste = np.random.uniform(10, 25)
            else:
                prev_waste = records[-1]["waste_pct"] if records else 30
                waste = prev_waste + (0.8 + 1.8 * activity) + np.random.uniform(-0.2, 0.4)
            waste = max(0, min(100, waste))
            
            # Inject anomalies (10% of data)
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
    df.to_csv(output_path, index=False)
    print(f"✅ Generated {len(df)} records → {output_path}")
    print(f"   Anomalies: {df['is_anomaly'].sum()} ({df['is_anomaly'].mean()*100:.1f}%)")
    return df

if __name__ == "__main__":
    generate_campus_dataset()
