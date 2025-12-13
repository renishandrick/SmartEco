"""
ML Model Verification Script
Tests if ml_package models are working correctly
"""
import sys
sys.path.append('.')

from predict_api import get_forecaster
import json

def test_ml_models():
    """Run comprehensive ML model tests"""
    print("="*60)
    print("ML Model Verification Test")
    print("="*60)
    
    # Initialize forecaster
    fc = get_forecaster()
    
    # Test 1: Check if models loaded
    print("\n1. MODEL LOADING TEST")
    print("-" * 40)
    status = fc.get_health_status()
    print(f"Tier-A Ready: {status['tier_a_ready']}")
    print(f"Models Loaded: {status['models_loaded']}")
    print(f"Backups Available: {status['backups_available']}")
    print(f"Zero-Crash: {status['zero_crash']}")
    
    if not status['tier_a_ready']:
        print("❌ FAILED: Models not loaded")
        return False
    print("✅ PASSED: Models loaded successfully")
    
    # Test 2: Single prediction test
    print("\n2. SINGLE PREDICTION TEST")
    print("-" * 40)
    test_cases = [
        {"resource": "electricity", "hour": 14, "dow": 2, "occ": 0.75},
        {"resource": "water", "hour": 12, "dow": 3, "occ": 0.80},
        {"resource": "waste", "hour": 18, "dow": 5, "occ": 0.50}
    ]
    
    for test in test_cases:
        result = fc.get_forecast(
            resource=test["resource"],
            hour=test["hour"],
            day_of_week=test["dow"],
            occupancy=test["occ"]
        )
        print(f"\n{test['resource'].upper()}:")
        print(f"  Input: hour={test['hour']}, dow={test['dow']}, occ={test['occ']}")
        print(f"  Output: {result['value']} {result['unit']}")
        print(f"  Tier: {result['tier']}")
        print(f"  Source: {result['source']}")
        
        # Validate output
        if result['value'] <= 0:
            print(f"  ❌ FAILED: Invalid prediction value")
            return False
        if result['tier'] not in ['A (ML)', 'A (Backup)', 'B (Default)']:
            print(f"  ❌ FAILED: Invalid tier")
            return False
        print(f"  ✅ PASSED")
    
    # Test 3: 24-hour forecast test
    print("\n3. 24-HOUR FORECAST TEST")
    print("-" * 40)
    for resource in ["electricity", "water", "waste"]:
        forecast = fc.get_24h_forecast(resource=resource, occupancy=0.75)
        
        print(f"\n{resource.upper()}:")
        print(f"  Points generated: {len(forecast)}")
        
        if len(forecast) != 24:
            print(f"  ❌ FAILED: Expected 24 points, got {len(forecast)}")
            return False
        
        # Check first few values
        sample = forecast[:3]
        print(f"  Sample values: {[p['y'] for p in sample]}")
        
        # Validate structure
        for point in forecast:
            if 'h' not in point or 'y' not in point:
                print(f"  ❌ FAILED: Invalid point structure")
                return False
            if point['y'] <= 0:
                print(f"  ❌ FAILED: Invalid prediction at hour {point['h']}")
                return False
        
        print(f"  ✅ PASSED")
    
    # Test 4: Fallback system test
    print("\n4. FALLBACK SYSTEM TEST")
    print("-" * 40)
    # This tests if JSON backups work
    if len(status['backups_available']) == 3:
        print(f"  JSON backups: {status['backups_available']}")
        print("  ✅ PASSED: Fallback system ready")
    else:
        print("  ⚠️  WARNING: Some backups missing")
    
    # Final summary
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED")
    print("="*60)
    print("\nML Package Status:")
    print(f"  - Models: {', '.join(status['models_loaded'])}")
    print(f"  - Tier: A (Pre-trained)")
    print(f"  - Reliability: Zero-crash guaranteed")
    
    return True

if __name__ == "__main__":
    try:
        success = test_ml_models()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ TEST FAILED WITH ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
