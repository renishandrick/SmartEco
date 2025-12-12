"""
Create synthetic training data for sustainability forecasting
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import os

def create_sustainability_data():
    """Create 90 days of hourly sustainability data"""
    print("📊 Creating sustainability dataset...")
    
    dates = pd.date_range(start='2024-01-01', periods=90*24, freq='H')
    data = []
    
    for i, dt in enumerate(dates):
        hour = dt.hour
        day_of_week = dt.weekday()
        month = dt.month
        
        # 1. Occupancy (0-1 scale)
        if 8 <= hour <= 18 and day_of_week < 5:  # Weekday work hours
            occupancy = 0.7 + 0.2 * np.random.random()
        elif 8 <= hour <= 18 and day_of_week >= 5:  # Weekend daytime
            occupancy = 0.3 + 0.2 * np.random.random()
        else:  # Nights
            occupancy = 0.1 + 0.1 * np.random.random()
        
        # 2. Electricity Usage
        base_electricity = 50 + 30 * np.sin(2*np.pi*hour/24 - np.pi/2)
        weekend_factor = 0.7 if day_of_week >= 5 else 1.0
        seasonal_factor = 1.0 + 0.3 * np.sin(2*np.pi*(month-6)/12) if 6 <= month <= 8 else 1.0
        electricity = base_electricity * weekend_factor * seasonal_factor + np.random.normal(0, 5)
        
        # 3. Water Usage
        morning_peak = 20 * np.exp(-((hour-8)/2)**2)
        evening_peak = 25 * np.exp(-((hour-20)/2)**2)
        base_water = 10 + morning_peak + evening_peak
        water_weekend_factor = 0.8 if day_of_week >= 5 else 1.0
        water_seasonal = 1.0 + 0.5 * np.sin(2*np.pi*(month-7)/12)
        water = base_water * water_weekend_factor * water_seasonal + np.random.normal(0, 3)
        
        # 4. Waste Generation
        waste_accumulation = hour * 0.5
        waste_drop = 30 if hour == 18 else 0
        base_waste = 5 + waste_accumulation - waste_drop
        waste_factor = 1.3 if day_of_week >= 5 else 1.0
        waste = base_waste * waste_factor + np.random.normal(0, 2)
        
        data.append({
            'timestamp': dt,
            'hour': hour,
            'day_of_week': day_of_week,
            'occupancy': round(occupancy, 2),
            'electricity_usage': max(0, round(electricity, 2)),
            'water_usage': max(0, round(water, 2)),
            'waste_generated': max(0, round(waste, 2))
        })
    
    df = pd.DataFrame(data)
    
    # Save files
    os.makedirs('../data', exist_ok=True)
    df.to_csv('../data/sustainability_data.csv', index=False)
    
    # Create sample data (3 rows)
    sample = df[['hour', 'day_of_week', 'occupancy']].head(3)
    sample.to_csv('../data/sample_data.csv', index=False)
    
    print(f"✅ Created dataset with {len(df)} rows")
    print(f"📁 Saved: data/sustainability_data.csv")
    print(f"📁 Saved: data/sample_data.csv")
    
    return df

if __name__ == "__main__":
    df = create_sustainability_data()
    print("\n📊 Sample data:")
    print(df.head())