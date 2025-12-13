"""
Debug script to test all imports and identify the error
"""
import sys
import traceback

print("=" * 60)
print("Testing SmartEco Backend Imports")
print("=" * 60)

modules_to_test = [
    "config",
    "database",
    "state",
    "ws_manager",
    "simulator",
    "alerts",
    "kpi",
    "forecast",
    "predict_api"
]

for module in modules_to_test:
    try:
        print(f"\n[{module}] Importing...", end=" ")
        __import__(module)
        print("✅ OK")
    except Exception as e:
        print(f"❌ FAILED")
        print(f"Error: {e}")
        traceback.print_exc()

print("\n" + "=" * 60)
print("Testing FastAPI App Creation")
print("=" * 60)

try:
    print("\nImporting main module...", end=" ")
    import main
    print("✅ OK")
    print(f"App created: {main.app}")
    print(f"App title: {main.app.title}")
except Exception as e:
    print("❌ FAILED")
    print(f"Error: {e}")
    traceback.print_exc()

print("\n" + "=" * 60)
print("All tests complete!")
print("=" * 60)
