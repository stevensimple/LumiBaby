import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_session
from app.middleware.auth import get_current_user
from app.models.event import CalibrationSession
from app.processing.pipeline import set_baseline, get_state

router = APIRouter()

class StartCalibration(BaseModel):
    sensor_id: str
    phase: str

@router.post("/start")
async def start_calibration(body: StartCalibration, db: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    if body.phase not in ("empty", "still", "movement", "breathing"):
        raise HTTPException(status_code=400, detail="Invalid phase")
    session = CalibrationSession(sensor_id=body.sensor_id, phase=body.phase, status="in_progress")
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return {"session_id": session.id, "phase": session.phase, "status": session.status}

@router.get("/{session_id}/status")
async def calibration_status(session_id: str, db: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    result = await db.execute(select(CalibrationSession).where(CalibrationSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"session_id": session.id, "phase": session.phase, "status": session.status,
            "baseline_variance": session.baseline_variance, "signal_quality_score": session.signal_quality_score}

@router.post("/{session_id}/complete")
async def complete_calibration(session_id: str, db: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    result = await db.execute(select(CalibrationSession).where(CalibrationSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    baseline_var = set_baseline(session.sensor_id)
    state = get_state(session.sensor_id)
    quality = min(1.0, (len(state.buffer) / 100)) if state else 0.0
    session.completed_at = datetime.utcnow()
    session.baseline_variance = baseline_var
    session.signal_quality_score = round(quality, 3)
    session.thresholds = {"presence_variance_multiplier": 2.5, "movement_low": 0.08, "movement_medium": 0.3, "movement_high": 1.0}
    session.status = "completed"
    await db.commit()
    return {"session_id": session.id, "status": "completed", "signal_quality_score": session.signal_quality_score, "baseline_variance": baseline_var}

@router.get("/thresholds")
async def get_thresholds(sensor_id: str, db: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    result = await db.execute(
        select(CalibrationSession)
        .where(CalibrationSession.sensor_id == sensor_id, CalibrationSession.status == "completed")
        .order_by(CalibrationSession.completed_at.desc()).limit(1)
    )
    session = result.scalar_one_or_none()
    if not session:
        return {"calibrated": False}
    return {"calibrated": True, "thresholds": session.thresholds, "signal_quality_score": session.signal_quality_score}
