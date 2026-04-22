"""
Sleep estimation based on movement signals.
NOT a medical device. Estimations only — no health claims.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import logging

logger = logging.getLogger(__name__)

DROWSY_THRESHOLD_FRAMES = 100     # ~5 min at 20Hz before considered drowsy
SLEEP_THRESHOLD_FRAMES = 200      # ~10 min before confirmed sleeping
WAKE_AGITATION_FRAMES = 30        # ~1.5 min of agitation = wake event
BACK_ASLEEP_CALM_FRAMES = 40      # ~2 min calm = back to sleeping
TIMELINE_SAMPLE_INTERVAL_S = 300  # Sample timeline every 5 min


def quality_label(score: int) -> str:
    if score >= 75:
        return "Bonne nuit"
    if score >= 50:
        return "Nuit modérée"
    return "Nuit agitée"


def compute_sleep_score(duration_minutes: float, calm_ratio: float, wake_count: int) -> int:
    duration_hours = duration_minutes / 60.0
    base = 50
    duration_score = min(30, int(duration_hours / 11.0 * 30))
    calm_score = int(calm_ratio * 20)
    wake_penalty = min(20, wake_count * 4)
    score = base + duration_score + calm_score - wake_penalty
    return max(0, min(99, score))


@dataclass
class SleepTrackerState:
    state: str = "awake"                   # awake | drowsy | sleeping | wake_event
    session_id: Optional[str] = None
    sleep_start: Optional[datetime] = None
    drowsy_frames: int = 0
    agitation_frames: int = 0
    calm_after_wake_frames: int = 0
    wake_events: int = 0
    total_frames: int = 0
    calm_frames: int = 0
    last_timeline_ts: float = 0.0
    timeline: list = field(default_factory=list)


_states: dict[str, SleepTrackerState] = {}


def get_tracker(sensor_id: str) -> SleepTrackerState:
    if sensor_id not in _states:
        _states[sensor_id] = SleepTrackerState()
    return _states[sensor_id]


def update(sensor_id: str, movement_level: str, baby_detected: bool, now: datetime) -> dict:
    """
    Feed one packet into the sleep state machine.
    Returns a dict describing any state transition that occurred.
    """
    st = get_tracker(sensor_id)
    is_calm = movement_level in ("calm",)
    is_agitated = movement_level in ("agitated", "very_agitated")
    ts = now.timestamp()

    event = None

    if not baby_detected:
        if st.state in ("sleeping", "drowsy", "wake_event"):
            event = _end_session(st, now, "baby_left")
        st.state = "awake"
        st.drowsy_frames = 0
        return {"event": event, "state": st.state}

    st.total_frames += 1
    if is_calm:
        st.calm_frames += 1

    # --- State machine ---
    if st.state == "awake":
        if is_calm:
            st.drowsy_frames += 1
            if st.drowsy_frames >= DROWSY_THRESHOLD_FRAMES:
                st.state = "drowsy"
        else:
            st.drowsy_frames = max(0, st.drowsy_frames - 5)

    elif st.state == "drowsy":
        if is_calm:
            st.drowsy_frames += 1
            if st.drowsy_frames >= SLEEP_THRESHOLD_FRAMES:
                # Estimated sleep start = SLEEP_THRESHOLD_FRAMES ago
                st.state = "sleeping"
                import uuid as _uuid
                st.session_id = str(_uuid.uuid4())
                st.sleep_start = now
                st.wake_events = 0
                st.total_frames = 0
                st.calm_frames = 0
                st.timeline = []
                event = {
                    "type": "sleep_start",
                    "session_id": st.session_id,
                    "start_time": now.isoformat(),
                }
        else:
            st.drowsy_frames = max(0, st.drowsy_frames - 10)
            if st.drowsy_frames < DROWSY_THRESHOLD_FRAMES // 2:
                st.state = "awake"

    elif st.state == "sleeping":
        # Sample timeline every 5 min
        if ts - st.last_timeline_ts >= TIMELINE_SAMPLE_INTERVAL_S:
            st.timeline.append({"t": ts, "level": movement_level})
            st.last_timeline_ts = ts

        if is_agitated:
            st.agitation_frames += 1
            if st.agitation_frames >= WAKE_AGITATION_FRAMES:
                st.state = "wake_event"
                st.wake_events += 1
                st.calm_after_wake_frames = 0
                event = {
                    "type": "wake_event",
                    "session_id": st.session_id,
                    "wake_count": st.wake_events,
                    "timestamp": now.isoformat(),
                }
        else:
            st.agitation_frames = max(0, st.agitation_frames - 3)

    elif st.state == "wake_event":
        if is_calm:
            st.calm_after_wake_frames += 1
            if st.calm_after_wake_frames >= BACK_ASLEEP_CALM_FRAMES:
                st.state = "sleeping"
                st.agitation_frames = 0
        elif is_agitated:
            st.calm_after_wake_frames = 0
            # If agitated for too long, end session
            if st.agitation_frames > WAKE_AGITATION_FRAMES * 3:
                event = _end_session(st, now, "woke_up")
                st.state = "awake"
                st.drowsy_frames = 0

    return {
        "event": event,
        "state": st.state,
        "session_id": st.session_id,
        "sleep_start": st.sleep_start.isoformat() if st.sleep_start else None,
        "wake_events": st.wake_events,
        "calm_ratio": round(st.calm_frames / max(st.total_frames, 1), 3),
        "timeline": st.timeline,
    }


def _end_session(st: SleepTrackerState, now: datetime, reason: str) -> dict:
    if not st.sleep_start or not st.session_id:
        return None
    duration = (now - st.sleep_start).total_seconds() / 60.0
    calm_ratio = round(st.calm_frames / max(st.total_frames, 1), 3)
    score = compute_sleep_score(duration, calm_ratio, st.wake_events)
    result = {
        "type": "sleep_end",
        "session_id": st.session_id,
        "start_time": st.sleep_start.isoformat(),
        "end_time": now.isoformat(),
        "duration_minutes": round(duration, 1),
        "calm_ratio": calm_ratio,
        "wake_events_count": st.wake_events,
        "sleep_score": score,
        "quality_label": quality_label(score),
        "timeline": list(st.timeline),
        "reason": reason,
    }
    st.session_id = None
    st.sleep_start = None
    st.wake_events = 0
    st.total_frames = 0
    st.calm_frames = 0
    st.timeline = []
    return result


def get_current_session_info(sensor_id: str) -> Optional[dict]:
    st = get_tracker(sensor_id)
    if st.state not in ("sleeping", "wake_event") or not st.sleep_start:
        return None
    now = datetime.utcnow()
    duration = (now - st.sleep_start).total_seconds() / 60.0
    calm_ratio = round(st.calm_frames / max(st.total_frames, 1), 3)
    score = compute_sleep_score(duration, calm_ratio, st.wake_events)
    return {
        "session_id": st.session_id,
        "state": st.state,
        "start_time": st.sleep_start.isoformat() + "Z",
        "duration_minutes": round(duration, 1),
        "calm_ratio": calm_ratio,
        "wake_events_count": st.wake_events,
        "sleep_score": score,
        "quality_label": quality_label(score),
        "is_active": True,
        "timeline": list(st.timeline),
    }
