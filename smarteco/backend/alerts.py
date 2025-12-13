from datetime import datetime, timezone
from typing import Dict, Any, List
import time
from state import STATE


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _cooldown_ok(key: str, cooldown_s: int) -> bool:
    now = time.time()
    last = STATE.last_alert_ts.get(key, 0.0)
    if now - last >= cooldown_s:
        STATE.last_alert_ts[key] = now
        return True
    return False


def _push_alert(alert: Dict[str, Any]) -> None:
    STATE.alerts.append(alert)
    # keep last 20 only
    if len(STATE.alerts) > 20:
        STATE.alerts = STATE.alerts[-20:]


def evaluate_alerts() -> List[Dict[str, Any]]:
    """
    Runs rule engine on latest telemetry + crisis flags.
    Uses cooldown so alerts don't spam every second.
    Returns current alert list (last 20).
    """
    t = STATE.telemetry
    energy = t["energy_kwh"]
    water = t["water_lpm"]
    waste = t["waste_pct"]

    # ENERGY
    if STATE.crisis_state["energy_spike"] or energy > 180:
        if _cooldown_ok("energy_spike", 12):
            _push_alert({
                "id": "ALRT-ENERGY-001",
                "severity": "HIGH",
                "resource": "energy",
                "message": "Energy spike detected (possible AC/lights left ON).",
                "estimated_loss_inr": 850,
                "created_at": iso_now()
            })

    # WATER
    if STATE.crisis_state["water_leak"] or water > 60:
        if _cooldown_ok("water_leak", 12):
            _push_alert({
                "id": "ALRT-WATER-001",
                "severity": "CRITICAL",
                "resource": "water",
                "message": "Water anomaly detected (possible leak / tap left open).",
                "estimated_loss_inr": 600,
                "created_at": iso_now()
            })

    # WASTE
    if STATE.crisis_state["waste_overflow"] or waste > 85:
        if _cooldown_ok("waste_overflow", 1800): # 30 mins cooldown
            _push_alert({
                "id": "ALRT-WASTE-001",
                "severity": "MEDIUM",
                "resource": "waste",
                "message": f"Waste Alert: Almost 85% is filled ({int(waste)}%). Collection required.",
                "estimated_loss_inr": 300,
                "created_at": iso_now()
            })

    return STATE.alerts
