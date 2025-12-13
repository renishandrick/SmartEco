import asyncio
from datetime import datetime, timezone
from typing import Dict, Any
from fastapi import FastAPI, WebSocket, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import os


from state import STATE
from ws_manager import MANAGER
from simulator import update_telemetry_from_simulator
from alerts import evaluate_alerts
from kpi import calculate_kpis
from forecast import get_24h_forecast
from database import get_db


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


app = FastAPI(title="SmartEco Backend with MongoDB Atlas", version="2.2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # local demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CrisisRequest(BaseModel):
    type: str


@app.get("/api/health")
def health() -> Dict[str, Any]:
    """Health check endpoint"""
    # Get ML status
    ml_status = {"tier_a_available": False}
    try:
        from predict_api import get_forecaster
        fc = get_forecaster()
        ml_status = fc.get_health_status()
    except Exception as e:
        ml_status["error"] = str(e)
    
    # Get MongoDB status
    db_status = {"connected": False}
    try:
        db = get_db()
        db_status = {"connected": db.connected, "database": "smarteco"}
    except Exception as e:
        db_status["error"] = str(e)
    
    return {
        "status": "ok",
        "mode": "simulator_direct_state",
        "sim_mode": STATE.sim_mode,
        "started_at": STATE.started_at,
        "ml_package": ml_status,
        "database": db_status
    }


@app.get("/api/ml/status")
def ml_status() -> Dict[str, Any]:
    """ML Package status endpoint with auto-training stats"""
    try:
        from predict_api import get_forecaster
        fc = get_forecaster()
        base_status = fc.get_health_status()
    except Exception as e:
        base_status = {
            "tier_a_ready": False,
            "error": str(e)
        }
    
    # Add auto-training stats
    from auto_trainer import AUTO_TRAINER
    training_stats = AUTO_TRAINER.get_stats()
    models_exist = AUTO_TRAINER.models_exist()
    
    from ml_models import AI_ENGINE
    
    return {
        **base_status,
        "auto_training": {
            "enabled": True,
            "models_exist": models_exist,
            "model_source": AI_ENGINE.model_source,
            **training_stats
        }
    }

@app.post("/api/ml/train")
async def trigger_training():
    """Manually trigger model training"""
    from auto_trainer import AUTO_TRAINER
    success = await AUTO_TRAINER.train_models()
    return {
        "status": "success" if success else "failed",
        "stats": AUTO_TRAINER.get_stats()
    }


@app.get("/api/savings")
def savings() -> Dict[str, Any]:
    return calculate_kpis()


@app.get("/api/forecast")
def forecast(resource: str = "energy") -> Dict[str, Any]:
    # Tier B only for now; Tier A (ML) can be plugged later without changing API
    return get_24h_forecast(resource)


@app.post("/api/upload_dataset")
async def upload_dataset(file: UploadFile = File(...)):
    """Handle CSV dataset upload"""
    try:
        # Save uploaded file
        upload_path = os.path.join("data", "uploaded_dataset.csv")
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return {
            "status": "success",
            "message": "Dataset uploaded successfully",
            "filename": file.filename
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/api/reset_graphs")
def reset_graphs():
    """Reset graph data and timestamps"""
    STATE.started_at = datetime.now().isoformat()
    return {"status": "success", "message": "Graphs reset successfully"}


@app.get("/api/telemetry/history")
def get_telemetry_history(hours: int = 24, limit: int = 1000):
    """Get historical telemetry data from MongoDB"""
    db = get_db()
    data = db.get_telemetry_history(hours=hours, limit=limit)
    return {
        "status": "success",
        "count": len(data),
        "data": data
    }


@app.get("/api/alerts/history")
def get_alerts_history(hours: int = 24, limit: int = 100):
    """Get alert history from MongoDB"""
    db = get_db()
    data = db.get_alerts_history(hours=hours, limit=limit)
    return {
        "status": "success",
        "count": len(data),
        "data": data
    }


@app.get("/api/predictions/history")
def get_predictions_history(resource_type: str = None, hours: int = 24, limit: int = 100):
    """Get prediction history from MongoDB"""
    db = get_db()
    data = db.get_predictions_history(resource_type=resource_type, hours=hours, limit=limit)
    return {
        "status": "success",
        "count": len(data),
        "data": data
    }


@app.get("/api/statistics")
def get_statistics(hours: int = 24):
    """Get aggregated statistics from MongoDB"""
    db = get_db()
    stats = db.get_statistics(hours=hours)
    return {
        "status": "success",
        "statistics": stats
    }


@app.get("/api/system/logs")
def get_system_logs(level: str = None, component: str = None, hours: int = 24, limit: int = 100):
    """Get system logs from MongoDB"""
    db = get_db()
    logs = db.get_system_logs(level=level, component=component, hours=hours, limit=limit)
    return {
        "status": "success",
        "count": len(logs),
        "logs": logs
    }


@app.delete("/api/data/cleanup")
def cleanup_old_data(days: int = None):
    """Clean up old data from MongoDB"""
    db = get_db()
    results = db.clear_old_data(days=days)
    return {
        "status": "success",
        "message": "Old data cleaned successfully",
        "results": results
    }



class ResetRequest(BaseModel):
    resource: str

@app.post("/api/resource/reset")
async def reset_resource(body: ResetRequest):
    r = body.resource.strip().lower()
    
    # 1. Reset Telemetry
    if r == 'waste':
        STATE.telemetry["waste_pct"] = 0.0
        STATE.crisis_state["waste_overflow"] = False
    elif r == 'energy':
        # Don't zero energy completely, maybe reset crisis spike
        STATE.crisis_state["energy_spike"] = False
    elif r == 'water':
        # Don't zero water completely
        STATE.crisis_state["water_leak"] = False
    elif r == 'ai':
        STATE.crisis_state["ai_anomaly"] = False

    # 2. Clear from Active Alerts
    # Filter out alerts matching this resource
    STATE.alerts = [a for a in STATE.alerts if a.get('resource') != r]

    # 3. Reset Cooldown (allow new alerts immediately if it recurs)
    keys_to_reset = []
    if r == 'waste': keys_to_reset.append("waste_overflow")
    elif r == 'energy': keys_to_reset.append("energy_spike") 
    elif r == 'water': keys_to_reset.append("water_leak")
    elif r == 'ai': keys_to_reset.append("ai_anomaly")
    
    for k in keys_to_reset:
        if k in STATE.last_alert_ts:
            del STATE.last_alert_ts[k]

    return {"status": "success", "message": f"{r} usage reset and alerts cleared"}

@app.delete("/api/alerts/{alert_id}")
async def delete_alert(alert_id: str):
    # Find alert to check resource/type
    target = next((a for a in STATE.alerts if a["id"] == alert_id), None)
    
    # Remove from list
    STATE.alerts = [a for a in STATE.alerts if a["id"] != alert_id]
    
    if target:
        # If we resolve an AI or Waste alert, also clear the crisis flag to stop recurrence
        r = target.get("resource", "")
        if r == "ai":
             STATE.crisis_state["ai_anomaly"] = False
        elif r == "waste":
             STATE.crisis_state["waste_overflow"] = False
             
    return {"status": "success", "message": "Alert removed"}

@app.post("/api/simulate_crisis")
async def simulate_crisis(body: CrisisRequest) -> Dict[str, Any]:
    t = (body.type or "").strip().lower()

    def reset_all():
        STATE.crisis_state["energy_spike"] = False
        STATE.crisis_state["water_leak"] = False
        STATE.crisis_state["waste_overflow"] = False
        STATE.crisis_state["ai_anomaly"] = False

    if t == "stop_all":
        reset_all()
        return {"ok": True, "crisis_state": STATE.crisis_state}

    if t not in ("energy_spike", "water_leak", "waste_overflow", "ai_anomaly"):
        return {"ok": False, "error": "Invalid crisis type", "allowed": ["energy_spike", "water_leak", "waste_overflow", "ai_anomaly", "stop_all"]}

    # Start selected crisis
    STATE.crisis_state[t] = True
    async def auto_reset():
        await asyncio.sleep(60)
        STATE.crisis_state[t] = False

    asyncio.create_task(auto_reset())

    return {"ok": True, "crisis_state": STATE.crisis_state, "expires_in_seconds": 60}


# Control Endpoints
class ControlAction(BaseModel):
    action: str  # 'on', 'off', 'compress', etc.

@app.get("/api/controls/status")
async def get_control_status() -> Dict[str, Any]:
    """Get current status of all controls"""
    return {
        "status": "success",
        "states": STATE.control_states
    }

@app.post("/api/controls/hardware/{device}")
async def control_hardware(device: str, body: ControlAction) -> Dict[str, Any]:
    """Control hardware device"""
    action = body.action.strip().lower()
    
    if device not in STATE.control_states:
        return {"status": "error", "message": f"Unknown device: {device}"}
    
    # Update state based on action
    if action in ['on', 'compress']:
        STATE.control_states[device] = True
    elif action == 'off':
        STATE.control_states[device] = False
    
    # Broadcast update via WebSocket
    await MANAGER.broadcast_json({
        "type": "control_update",
        "device": device,
        "device_type": "hardware",
        "state": STATE.control_states[device],
        "action": action,
        "ts": iso_now()
    })
    
    return {
        "status": "success",
        "device": device,
        "action": action,
        "new_state": STATE.control_states[device]
    }

@app.post("/api/controls/software/{service}")
async def control_software(service: str, body: ControlAction) -> Dict[str, Any]:
    """Control software service"""
    action = body.action.strip().lower()
    
    if service not in STATE.control_states:
        return {"status": "error", "message": f"Unknown service: {service}"}
    
    # Update state
    if action == 'on':
        STATE.control_states[service] = True
    elif action == 'off':
        STATE.control_states[service] = False
    
    # Broadcast update via WebSocket
    await MANAGER.broadcast_json({
        "type": "control_update",
        "service": service,
        "service_type": "software",
        "state": STATE.control_states[service],
        "action": action,
        "ts": iso_now()
    })
    
    return {
        "status": "success",
        "service": service,
        "action": action,
        "new_state": STATE.control_states[service]
    }


@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await MANAGER.connect(websocket)
    try:
        while True:
            # Keep alive; frontend may send pings or nothing
            await websocket.receive_text()
    except Exception:
        await MANAGER.disconnect(websocket)


async def simulator_loop():
    # Updates telemetry frequently so UI looks smooth
    while True:
        update_telemetry_from_simulator()
        await asyncio.sleep(1)  # 1 second telemetry tick


from ml_models import AI_ENGINE
from digital_twin_service import DT_SERVICE

async def broadcast_loop():
    # Broadcast the unified payload every 1 second, regardless of telemetry arrival.
    db = get_db()
    save_counter = 0
    
    # Ensure AI is ready
    AI_ENGINE.load_or_train()
    
    while True:
        # Rule engine + KPIs computed on every tick
        alerts = evaluate_alerts()
        kpis = calculate_kpis()

        # --- AI ML INFERENCE ---
        tele_energy = STATE.telemetry.get('energy_kwh', 0)
        tele_water = STATE.telemetry.get('water_lpm', 0)
        
        # 1. Anomaly Detection
        if AI_ENGINE.check_anomaly(tele_energy, tele_water):
            alerts.insert(0, {
                "id": f"ai_anom_{int(datetime.now().timestamp())}",
                "message": "⚠️ AI ANOMALY: Unusual resource pattern detected",
                "severity": "critical",
                "resource": "system",
                "ts": iso_now()
            })

        # 2. Predictive Maintenance Score
        health_score = AI_ENGINE.predict_maintenance_health(tele_energy, tele_water)
        kpis['system_health_score'] = round(health_score, 1)
        
        # 3. Digital Twin Update
        dt_data = DT_SERVICE.tick()
        # -----------------------

        payload = {
            "ts": iso_now(),
            "telemetry": STATE.telemetry,
            "alerts": alerts,
            "kpis": kpis,
            "crisis_state": STATE.crisis_state,
            "digital_twin": dt_data
        }
        await MANAGER.broadcast_json(payload)
        
        # Save to MongoDB every 5 seconds (reduce DB load)
        save_counter += 1
        if save_counter >= 5 and db.connected:
            try:
                db.save_telemetry(
                    STATE.telemetry['energy_kwh'],
                    STATE.telemetry['water_lpm'],
                    STATE.telemetry['waste_pct']
                )
                
                # Save new alerts
                for alert in alerts:
                    # Check if this alert was already saved (simple deduplication)
                    if not any(a.get('id') == alert.get('id') for a in STATE.alerts[:-len(alerts)]):
                        db.save_alert(
                            alert_type=alert.get('resource', 'general'),
                            message=alert['message'],
                            severity=alert.get('severity', 'warning'),
                            alert_id=alert.get('id'),
                            estimated_loss_inr=alert.get('estimated_loss_inr', 0)
                        )
                
                save_counter = 0
            except Exception as e:
                print(f"MongoDB save error: {e}")
        
        await asyncio.sleep(1)  # 1Hz broadcast


@app.on_event("startup")
async def on_startup():
    """Startup event handler"""
    print("🚀 SmartEco Backend Starting...")
    
    # Connect to MongoDB
    try:
        db = get_db()
        if db.connect():
            print("✅ MongoDB Atlas connected successfully")
            print(f"   Database: {db.db.name}")
            print(f"   Collections: {db.db.list_collection_names()}")
        else:
            print("⚠️  MongoDB connection failed, running without persistence")
    except Exception as e:
        print(f"⚠️  MongoDB connection error: {e}")
        print("   Server will continue without database persistence")
    
    # Start background tasks
    try:
        asyncio.create_task(simulator_loop())
        asyncio.create_task(broadcast_loop())
        print("✅ Background tasks started")
    except Exception as e:
        print(f"❌ Failed to start background tasks: {e}")
    
    # Start auto-training loop
    try:
        from auto_trainer import auto_training_loop, AUTO_TRAINER
        asyncio.create_task(auto_training_loop())
        print("✅ Auto-training service started (trains every 30 mins)")
        
        # Trigger initial training if we have data
        asyncio.create_task(AUTO_TRAINER.train_models())
        print("🧠 Initial model training triggered...")
    except Exception as e:
        print(f"⚠️  Auto-training setup error: {e}")
    
    print("✅ SmartEco Backend Ready!")


@app.on_event("shutdown")
async def on_shutdown():
    """Shutdown event handler"""
    print("👋 Shutting down SmartEco Backend...")
    try:
        db = get_db()
        db.disconnect()
        print("✅ MongoDB disconnected")
    except Exception as e:
        print(f"⚠️  Shutdown error: {e}")
    print("👋 SmartEco backend shutdown complete")
