import random
from typing import Dict, Any
from state import STATE

class DigitalTwinService:
    def __init__(self):
        # Initial State of the Digital Twin Campus
        self.locations = {
            "Hostel": {
                "id": "loc_1", "name": "Hostel Block A", "icon": "Building", 
                "metrics": {"energy": 45, "water": 12, "waste": 30}, 
                "status": "normal", "alert": None, "action": None
            },
            "Classroom": {
                "id": "loc_2", "name": "Classroom 4", "icon": "BookOpen", 
                "metrics": {"energy": 120, "water": 5, "waste": 15}, 
                "status": "normal", "alert": None, "action": None
            },
            "Washroom": {
                "id": "loc_3", "name": "Washroom 2", "icon": "Droplets", 
                "metrics": {"energy": 10, "water": 8, "waste": 5}, 
                "status": "normal", "alert": None, "action": None
            },
            "Labs": {
                "id": "loc_4", "name": "Chemistry Lab", "icon": "FlaskConical", 
                "metrics": {"energy": 210, "water": 20, "waste": 45}, 
                "status": "normal", "alert": None, "action": None
            },
            "Canteen": {
                "id": "loc_5", "name": "Main Canteen", "icon": "Coffee", 
                "metrics": {"energy": 150, "water": 80, "waste": 60}, 
                "status": "normal", "alert": None, "action": None
            }
        }
        
        # Cumulative Savings Counter
        self.savings = {"water_l": 1240.5, "energy_w": 4500, "waste_kg": 320}
        self.counter = 0

    def tick(self) -> Dict[str, Any]:
        self.counter += 1
        
        # 1. Simulate Normal Fluctuations
        for key, loc in self.locations.items():
            # If in critical/safe mode, physics are controlled by scenario below
            if loc["status"] == "normal":
                loc["metrics"]["energy"] = max(0, loc["metrics"]["energy"] + random.uniform(-2, 2))
                loc["metrics"]["water"] = max(0, loc["metrics"]["water"] + random.uniform(-1, 1))
                
                # Waste increases slowly over time, resets at 100%
                loc["metrics"]["waste"] = min(100, max(0, loc["metrics"]["waste"] + random.uniform(0, 0.3)))
                
                # Auto-reset waste when full (simulate collection)
                if loc["metrics"]["waste"] >= 99:
                    loc["metrics"]["waste"] = random.uniform(10, 25)
                
                loc["alert"] = None
                loc["action"] = None

        # 2. SCENARIO A: WATER LEAK (Washroom)
        # Triggered by global crisis state or random chance
        if STATE.crisis_state.get("water_leak"):
            loc = self.locations["Washroom"]
            
            # Phase 1: The Leak Starts
            if loc["status"] == "normal":
                loc["status"] = "critical"
                loc["metrics"]["water"] = 145.5 # Massive spike
                loc["alert"] = "⚠ LEAK DETECTED (3.2 L/min)"
            
            # Phase 2: AI Intervention (After 3 seconds)
            elif loc["status"] == "critical":
                if self.counter % 20 < 10: # oscillate slightly
                     loc["metrics"]["water"] += random.uniform(-2, 2)
                
                # Trigger Auto-Action
                loc["status"] = "resolving"
                loc["action"] = "🤖 AI: Solenoid Valve Auto-Closing..."
            
            # Phase 3: Resolution & Savings
            elif loc["status"] == "resolving":
                loc["metrics"]["water"] *= 0.85 # Rapid drop
                self.savings["water_l"] += 0.05 # Tally up
                
                if loc["metrics"]["water"] < 2:
                    loc["metrics"]["water"] = 0
                    loc["status"] = "safe"
                    loc["action"] = "✅ Valve Closed. Leak Stopped."

        # 3. SCENARIO B: ENERGY SPIKE (Classroom)
        if STATE.crisis_state.get("energy_spike"):
            loc = self.locations["Classroom"]
            
            if loc["status"] == "normal":
                loc["status"] = "critical"
                loc["metrics"]["energy"] = 850 # Huge spike
                loc["alert"] = "⚡ DANGEROUS SURGE (>800W)"
            
            elif loc["status"] == "critical":
                loc["status"] = "resolving"
                loc["action"] = "🤖 AI: Isolating Circuit Breaker..."
            
            elif loc["status"] == "resolving":
                loc["metrics"]["energy"] *= 0.6 # Power cut
                self.savings["energy_w"] += 5.0
                
                if loc["metrics"]["energy"] < 50:
                    loc["status"] = "safe"
                    loc["action"] = "✅ Hazard Freed. Circuit Isolated."

        # 4. SCENARIO C: WASTE OVERFLOW (Canteen/Hostel)
        # Let's use Hostel for variety if waste overflow
        if STATE.crisis_state.get("waste_overflow"):
            loc = self.locations["Hostel"] # Mapping "Bin Overflow" to Hostel
            
            if loc["status"] == "normal":
                loc["status"] = "critical"
                loc["metrics"]["waste"] = 98.0
                loc["alert"] = "🗑️ BIN OVERFLOW DETECTED"
            
            elif loc["status"] == "critical":
                loc["status"] = "resolving"
                loc["action"] = "🤖 AI: Pneumatic Compressor Active..."
            
            elif loc["status"] == "resolving":
                loc["metrics"]["waste"] -= 2.0 # Compressing
                self.savings["waste_kg"] += 0.1
                
                if loc["metrics"]["waste"] < 60:
                     loc["status"] = "safe"
                     loc["action"] = "✅ Volume Reduced by 40%"

        # Cleanup if crisis turned off
        if not any(STATE.crisis_state.values()):
            # Reset safes to normal slowly
            for loc in self.locations.values():
                if loc["status"] in ["safe", "critical", "resolving"]:
                   loc["status"] = "normal" 

        return {
            "locations": self.locations,
            "savings": self.savings
        }

DT_SERVICE = DigitalTwinService()
