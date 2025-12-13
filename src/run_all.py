"""
Master script to run everything
"""
import os
import sys

def main():
    print("=" * 60)
    print("[INFO] AI SMART CAMPUS - COMPLETE SETUP")
    print("=" * 60)
    
    # Add src to path
    sys.path.append('src')
    
    # Step 1: Install requirements
    print("\n[STEP 1] Installing requirements...")
    os.system(f'{sys.executable} -m pip install -r requirements.txt')
    
    # Step 2: Create data
    print("\n[STEP 2] Creating training data...")
    from data_preparation import create_sustainability_data
    create_sustainability_data()
    
    # Step 3: Train forecasting models
    print("\n[STEP 3] Training forecasting models...")
    from train_forecast import train_models
    train_models()
    
    # Step 5: Create delivery packages
    print("\n[STEP 5] Creating delivery packages...")
    create_delivery_packages()
    
    print("\n" + "=" * 60)
    print("[SUCCESS] SETUP COMPLETE!")
    print("=" * 60)
    print("\n[INFO] Delivery packages ready in:")
    print("   - ../delivery/ml_package/ (for backend)")
    print("\n[INFO] Check model_specification.txt for frozen contract")

def create_delivery_packages():
    """Create packages for backend team"""
    import shutil
    
    # ML Package
    ml_files = [
        ('../models/forecast_electricity.pkl', 'forecast_electricity.pkl'),
        ('../models/forecast_water.pkl', 'forecast_water.pkl'),
        ('../models/forecast_waste.pkl', 'forecast_waste.pkl'),
        ('../backups/forecast_backup_electricity.json', 'forecast_backup_electricity.json'),
        ('../backups/forecast_backup_water.json', 'forecast_backup_water.json'),
        ('../backups/forecast_backup_waste.json', 'forecast_backup_waste.json'),
        ('../data/sample_data.csv', 'sample_data.csv'),
        ('../model_specification.txt', 'model_specification.txt'),
        ('predict_api.py', 'predict_api.py')
    ]
    
    # Output to ROOT delivery folder
    os.makedirs('../delivery/ml_package', exist_ok=True)
    
    for src, dst in ml_files:
        if os.path.exists(src):
            shutil.copy(src, f'../delivery/ml_package/{dst}')
            print(f"   - Copied: {dst}")
        else:
            print(f"   [WARN] Missing: {src}")

if __name__ == "__main__":
    main()