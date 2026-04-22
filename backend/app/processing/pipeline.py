import logging
from collections import defaultdict, deque
from datetime import datetime
import numpy as np
from app.processing.preprocessing import preprocess_csi
from app.processing.presence import detect_presence
from app.processing.movement import detect_movement
from app.processing.respiration import detect_signal_pattern
from app.processing.confidence import compute_activity_score
from app.config import settings

logger = logging.getLogger(__name__)
BUFFER_SIZE = 600
SAMPLE_RATE = 20.0

class SensorState:
    def __init__(self):
        self.buffer: deque = deque(maxlen=BUFFER_SIZE)
        self.baseline_variance: float = None
        self.last_presence: bool = None
        self.last_movement_level: str = None
        self.last_pattern_rhythmic: bool = None
        self.packet_count: int = 0
        self.window_start: float = datetime.utcnow().timestamp()
        self.last_movement_time: float = datetime.utcnow().timestamp()
        self.inactivity_alert_sent: bool = False

_sensor_states: dict[str, SensorState] = defaultdict(SensorState)

def get_state(sensor_id: str) -> SensorState:
    return _sensor_states[sensor_id]

def process_packet(sensor_id: str, raw_csi: list, rssi: int) -> dict:
    state = get_state(sensor_id)
    amplitude = preprocess_csi(raw_csi)
    if len(amplitude) == 0:
        return None
    state.buffer.append(amplitude)
    state.packet_count += 1

    buf = np.array(list(state.buffer))
    window = buf[-max(2, int(SAMPLE_RATE)):] if len(buf) >= 2 else buf

    presence_detected, presence_conf = detect_presence(window, state.baseline_variance)
    movement_level, movement_value, movement_conf = detect_movement(window)
    signal_pattern = detect_signal_pattern(buf, SAMPLE_RATE)

    now = datetime.utcnow().timestamp()

    # Track inactivity
    if movement_level != "calm":
        state.last_movement_time = now
        state.inactivity_alert_sent = False

    inactivity_minutes = round((now - state.last_movement_time) / 60.0, 1) if presence_detected else 0.0

    activity_score = compute_activity_score(
        movement_level, presence_conf, presence_detected, inactivity_minutes
    )

    # Build events
    events = []

    if state.last_presence is not None and state.last_presence != presence_detected:
        if not presence_detected:
            events.append({
                "type": "presence_lost",
                "sensor_id": sensor_id,
                "details": {"message": "Baby no longer detected in the crib"}
            })
        # Don't fire "presence detected" as an alert — that's positive, just a status update

    if movement_level in ("agitated", "very_agitated") and state.last_movement_level not in ("agitated", "very_agitated"):
        events.append({
            "type": "unusual_activity",
            "sensor_id": sensor_id,
            "details": {"level": movement_level, "message": "Unusual activity detected"}
        })

    threshold = settings.inactivity_alert_minutes
    if (presence_detected and inactivity_minutes >= threshold and not state.inactivity_alert_sent):
        state.inactivity_alert_sent = True
        events.append({
            "type": "prolonged_inactivity",
            "sensor_id": sensor_id,
            "details": {
                "minutes": inactivity_minutes,
                "message": f"No movement detected for {int(inactivity_minutes)} minutes"
            }
        })

    state.last_presence = presence_detected
    state.last_movement_level = movement_level
    state.last_pattern_rhythmic = signal_pattern["rhythmic"]

    elapsed = now - state.window_start
    packet_rate = state.packet_count / elapsed if elapsed > 0 else 0.0

    return {
        "status": {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "sensor_id": sensor_id,
            "baby": {"detected": presence_detected, "confidence": presence_conf},
            "movement": {"level": movement_level, "value": round(movement_value, 4), "confidence": movement_conf},
            "signal_pattern": signal_pattern,
            "activity_score": activity_score,
            "inactivity_minutes": inactivity_minutes,
        },
        "events": events,
        "packet_rate": packet_rate,
        "rssi": rssi,
    }

def set_baseline(sensor_id: str):
    state = get_state(sensor_id)
    if len(state.buffer) > 10:
        buf = np.array(list(state.buffer))
        state.baseline_variance = float(np.var(buf, axis=0).mean())
        return state.baseline_variance
    return None
