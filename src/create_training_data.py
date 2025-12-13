"""
Create synthetic time-series data for campus sustainability forecasting
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def create_synthetic_dataset():
    """
    Create realistic campus data with patterns:
    - Daily patterns (peak during day, low at night)
    - Weekly patterns (weekend vs weekday)
    - Seasonal patterns
    """
    
    # Create date range: 90 days of hourly data
    dates = pd.date_range(start='2024-01-01', periods=90*24, freq='H')
    
    data = []
    
    for i, dt in enumerate(dates):
        # Base features (FROZEN - DON'T CHANGE)
        hour = dt.hour
        day_of_week = dt.weekday()  # 0=Monday, 6=Sunday
        day_of_year = dt.dayofyear
        
        # Create realistic patterns
        
        # 1. ELECTRICITY USAGE
        # Base pattern: higher during day, lower at night
        base_electricity = 50 + 30 * np.sin(2*np.pi*hour/24 - np.pi/2)
        
        # Weekend effect: 30% lower on weekends
        weekend_factor = 0.7 if day_of_week >= 5 else 1.0
        
        # Seasonal effect: higher in summer (June-August)
        month = dt.month
        seasonal_factor = 1.0 + 0.3 * np.sin(2*np.pi*(month-6)/12) if 6 <= month <= 8 else 1.0
        
        # Random noise
        noise = np.random.normal(0, 5)
        
        electricity = base_electricity * weekend_factor * seasonal_factor + noise
        
        # 2. WATER USAGE
        # Different pattern: peaks in morning and evening
        morning_peak = 20 * np.exp(-((hour-8)/2)**2)  # 8 AM peak
        evening_peak = 25 * np.exp(-((hour-20)/2)**2)  # 8 PM peak
        base_water = 10 + morning_peak + evening_peak
        
        # Weekend effect: different pattern
        water_weekend_factor = 0.8 if day_of_week >= 5 else 1.0
        
        # Seasonal: higher in summer
        water_seasonal = 1.0 + 0.5 * np.sin(2*np.pi*(month-7)/12)
        
        water = base_water * water_weekend_factor * water_seasonal + np.random.normal(0, 3)
        
        # 3. WASTE GENERATION
        # Builds up during day, collected in evening
        waste_accumulation = hour * 0.5  # accumulates through day
        waste_drop = 30 if hour == 18 else 0  # collection at 6 PM
        
        base_waste = 5 + waste_accumulation - waste_drop
        if base_waste < 0:
            base_waste = 0
            
        # Weekend: more waste on weekends
        waste_factor = 1.3 if day_of_week >= 5 else 1.0
        
        waste = base_waste * waste_factor + np.random.normal(0, 2)
        
        # 4. OCCUPANCY (0-1 scale)
        # Campus occupancy: high during work hours
        if 8 <= hour <= 18 and day_of_week < 5:  # Weekday work hours
            occupancy = 0.7 + 0.2 * np.random.random()
        elif 8 <= hour <= 18 and day_of_week >= 5:  # Weekend daytime
            occupancy = 0.3 + 0.2 * np.random.random()
        else:  # Nights
            occupancy = 0.1 + 0.1 * np.random.random()
        
        # Add to dataset
        data.append({
            'timestamp': dt,
            'hour': hour,
            'day_of_week': day_of_week,
            'day_of_year': day_of_year,
            'month': month,
            'occupancy': round(occupancy, 2),
            'electricity_usage': max(0, round(electricity, 2)),
            'water_usage': max(0, round(water, 2)),
            'waste_generated': max(0, round(waste, 2))
        })
    
    df = pd.DataFrame(data)
    
    # Save to CSV
    df.to_csv('sustainability_data.csv', index=False)
    
    # Create sample data (3 rows for specification)
    sample = df[['hour', 'day_of_week', 'occupancy']].head(3)
    sample.to_csv('sample_data.csv', index=False)
    
    print("✅ Dataset created successfully!")
    print(f"   Total rows: {len(df)}")
    print(f"   Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    print(f"   Features: {list(df.columns)}")
    print(f"\n📁 Files saved:")
    print(f"   - sustainability_data.csv (full dataset)")
    print(f"   - sample_data.csv (3 sample rows)")
    
    return df

if __name__ == "__main__":
    df = create_synthetic_dataset()
    
    # Show statistics
    print("\n📊 Data Statistics:")
    print(df[['electricity_usage', 'water_usage', 'waste_generated']].describe())