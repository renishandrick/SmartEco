from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Any


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class AppState:
    # Latest telemetry snapshot
    telemetry: Dict[str, float] = field(default_factory=lambda: {
        "energy_kwh": 120.0,
        "water_lpm": 18.0,
        "waste_pct": 35.0
    })

    # Crisis flags
    crisis_state: Dict[str, bool] = field(default_factory=lambda: {
        "energy_spike": False,
        "water_leak": False,
        "waste_overflow": False
    })

    # Alert queue (keep last N)
    alerts: List[Dict[str, Any]] = field(default_factory=list)

    # Per-alert cooldown tracking
    last_alert_ts: Dict[str, float] = field(default_factory=dict)

    # Used by simulator
    last_waste_reset_hour: int = -1

    # Control states for hardware and software
    control_states: Dict[str, bool] = field(default_factory=lambda: {
        "pipe": True,
        "lights_hw": True,
        "dustbin": False,
        "water_valve": True,
        "lights_sw": True,
        "ac": True,
        "ventilation": True,
        "heating": False
    })

    # System flags
    started_at: str = field(default_factory=iso_now)
    sim_mode: bool = True  # Option B: simulator always available


STATE = AppState()
