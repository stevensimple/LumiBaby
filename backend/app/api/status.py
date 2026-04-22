from fastapi import APIRouter, Depends
from app.middleware.auth import get_current_user
from app.processing.pipeline import _sensor_states

router = APIRouter()

@router.get("/live")
async def live_status(current_user=Depends(get_current_user)):
    result = {}
    for sensor_id, state in _sensor_states.items():
        if state.last_presence is not None:
            result[sensor_id] = {
                "baby_detected": state.last_presence,
                "movement_level": state.last_movement_level,
                "signal_pattern_rhythmic": state.last_pattern_rhythmic,
                "buffer_size": len(state.buffer),
                "inactivity_alert_sent": state.inactivity_alert_sent,
            }
    return result
