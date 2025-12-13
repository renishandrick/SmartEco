"""
Universal Data Loader for SmartEco ML Training
Supports: ASHRAE, UCF, Custom CSV, and Synthetic generation
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import os


class DataLoader:
    """Flexible data loader with validation"""
    
    REQUIRED_COLUMNS = [
        "timestamp", "hour", "day_of_week", "is_weekend",
        "occupancy", "energy_kwh", "water_lpm"
    ]
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def load_ashrae(self, csv_path: str, building_id: int = 100) -> pd.DataFrame:
        """
        Load and preprocess ASHRAE dataset
        
        Args:
            csv_path: Path to ASHRAE train.csv
            building_id: Which building to extract
        
        Returns:
            Preprocessed DataFrame
        """
        print(f"📥 Loading ASHRAE data for building {building_id}...")
        
        # Load raw data
        df = pd.read_csv(csv_path)
        
        # Filter for specific building
        df = df[df['building_id'] == building_id].copy()
        
        # Parse timestamp
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        
        # Separate meter types
        energy_df = df[df['meter'] == 0][['timestamp', 'meter_reading']].rename(
            columns={'meter_reading': 'energy_kwh'}
        )
        water_df = df[df['meter'] == 1][['timestamp', 'meter_reading']].rename(
            columns={'meter_reading': 'water_lpm'}
        )
        
        # Merge
        result = energy_df.merge(water_df, on='timestamp', how='outer')
        
        # Add derived features
        result['hour'] = result['timestamp'].dt.hour
        result['day_of_week'] = result['timestamp'].dt.dayofweek
        result['is_weekend'] = (result['day_of_week'] >= 5).astype(int)
        
        # Estimate occupancy (proxy from square_footage if available)
        result['occupancy'] = 3000  # Default assumption
        
        # Fill missing values
        result = result.fillna(method='ffill').fillna(method='bfill')
        
        print(f"✅ Loaded {len(result)} records from ASHRAE")
        return self._validate_and_clean(result)
    
    def load_custom_csv(self, csv_path: str) -> pd.DataFrame:
        """
        Load user-provided CSV
        
        Expected columns: timestamp, hour, day_of_week, is_weekend,
                         occupancy, energy_kwh, water_lpm
        """
        print(f"📥 Loading custom CSV: {csv_path}")
        
        df = pd.read_csv(csv_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        return self._validate_and_clean(df)
    
    def generate_synthetic(
        self, 
        days: int = 365,
        include_seasonality: bool = True,
        include_holidays: bool = True
    ) -> pd.DataFrame:
        """
        Generate high-quality synthetic data
        
        Args:
            days: Number of days to generate
            include_seasonality: Add seasonal patterns
            include_holidays: Reduce activity on holidays
        """
        print(f"🔧 Generating {days} days of synthetic data...")
        
        records = []
        start_date = datetime.now() - timedelta(days=days)
        
        # Holiday dates (simplified)
        holidays = [
            datetime(2024, 1, 1),  # New Year
            datetime(2024, 12, 25), # Christmas
            # Add more as needed
        ]
        
        for day in range(days):
            current_date = start_date + timedelta(days=day)
            is_weekend = current_date.weekday() >= 5
            is_holiday = current_date.date() in [h.date() for h in holidays]
            
            # Seasonal factor (summer higher cooling, winter higher heating)
            month = current_date.month
            if include_seasonality:
                seasonal_factor = 1.0 + 0.2 * np.sin((month - 1) / 12 * 2 * np.pi)
            else:
                seasonal_factor = 1.0
            
            for hour in range(24):
                timestamp = current_date + timedelta(hours=hour)
                
                # Activity curve
                activity = 0.5 + 0.5 * np.sin((hour - 6) / 24 * 2 * np.pi)
                activity = max(0.05, min(activity, 1.0))
                
                # Reduce on weekends/holidays
                if is_weekend:
                    activity *= 0.6
                if is_holiday:
                    activity *= 0.3
                
                # Occupancy
                base_occ = 5000 if not (is_weekend or is_holiday) else 1500
                occupancy = int(base_occ * activity + np.random.normal(0, 200))
                occupancy = max(0, occupancy)
                
                # Energy (with seasonality)
                energy = (70 + 140 * activity) * seasonal_factor + np.random.normal(0, 8)
                if is_weekend or is_holiday:
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
                
                # Anomaly injection (5% for better quality)
                is_anomaly = np.random.random() < 0.05
                if is_anomaly:
                    choice = np.random.choice(["energy", "water"])
                    if choice == "energy":
                        energy += np.random.uniform(80, 150)
                    else:
                        water += np.random.uniform(50, 120)
                
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
        print(f"✅ Generated {len(df)} records")
        
        return df
    
    def _validate_and_clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate schema and clean data"""
        print("🔍 Validating data quality...")
        
        # Check required columns
        missing_cols = set(self.REQUIRED_COLUMNS) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Remove duplicates
        before = len(df)
        df = df.drop_duplicates(subset=['timestamp'])
        if len(df) < before:
            print(f"   ⚠️  Removed {before - len(df)} duplicate timestamps")
        
        # Sort by timestamp
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        # Check for gaps
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        time_diffs = df['timestamp'].diff()
        gaps = (time_diffs > pd.Timedelta(hours=2)).sum()
        if gaps > 0:
            print(f"   ⚠️  Found {gaps} time gaps > 2 hours")
        
        # Value range checks
        if (df['energy_kwh'] < 0).any() or (df['energy_kwh'] > 1000).any():
            print("   ⚠️  Energy values outside expected range [0, 1000]")
        
        if (df['water_lpm'] < 0).any() or (df['water_lpm'] > 500).any():
            print("   ⚠️  Water values outside expected range [0, 500]")
        
        # Summary stats
        print(f"   ✅ {len(df)} records validated")
        print(f"   📊 Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
        print(f"   📊 Energy mean: {df['energy_kwh'].mean():.2f} kWh")
        print(f"   📊 Water mean: {df['water_lpm'].mean():.2f} LPM")
        
        return df
    
    def save(self, df: pd.DataFrame, filename: str = "campus_training.csv"):
        """Save processed data"""
        path = os.path.join(self.data_dir, filename)
        df.to_csv(path, index=False)
        print(f"💾 Saved to {path}")
        return path


def main():
    """Example usage"""
    loader = DataLoader()
    
    # Try loading ASHRAE (if available)
    ashrae_path = "data/ashrae_train.csv"
    if os.path.exists(ashrae_path):
        df = loader.load_ashrae(ashrae_path, building_id=100)
    else:
        # Fallback to synthetic
        print("ASHRAE data not found, generating synthetic...")
        df = loader.generate_synthetic(days=365, include_seasonality=True)
    
    loader.save(df)
    print("\n✅ Data ready for training!")


if __name__ == "__main__":
    main()
