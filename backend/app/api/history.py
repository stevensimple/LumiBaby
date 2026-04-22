from fastapi import APIRouter, Depends, Query
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_session
from app.middleware.auth import get_current_user
from app.models.metrics import PresenceEvent, MovementMetric, SignalPatternMetric, InactivityEvent

router = APIRouter()

@router.get("/presence")
async def presence_history(sensor_id: Optional[str] = Query(None), limit: int = Query(100, le=500),
                            db: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    q = select(PresenceEvent).order_by(PresenceEvent.timestamp.desc()).limit(limit)
    if sensor_id:
        q = q.where(PresenceEvent.sensor_id == sensor_id)
    result = await db.execute(q)
    rows = result.scalars().all()
    return [{"id": r.id, "sensor_id": r.sensor_id, "timestamp": r.timestamp.isoformat(),
             "detected": r.detected, "confidence": r.confidence} for r in rows]

@router.get("/movement")
async def movement_history(sensor_id: Optional[str] = Query(None), limit: int = Query(100, le=500),
                            db: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    q = select(MovementMetric).order_by(MovementMetric.timestamp.desc()).limit(limit)
    if sensor_id:
        q = q.where(MovementMetric.sensor_id == sensor_id)
    result = await db.execute(q)
    rows = result.scalars().all()
    return [{"id": r.id, "sensor_id": r.sensor_id, "timestamp": r.timestamp.isoformat(),
             "level": r.level, "value": r.value, "confidence": r.confidence} for r in rows]

@router.get("/signal_pattern")
async def signal_pattern_history(sensor_id: Optional[str] = Query(None), limit: int = Query(100, le=500),
                                  db: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    q = select(SignalPatternMetric).order_by(SignalPatternMetric.timestamp.desc()).limit(limit)
    if sensor_id:
        q = q.where(SignalPatternMetric.sensor_id == sensor_id)
    result = await db.execute(q)
    rows = result.scalars().all()
    return [{"id": r.id, "sensor_id": r.sensor_id, "timestamp": r.timestamp.isoformat(),
             "rhythmic": r.rhythmic, "confidence": r.confidence,
             "note": "experimental — not a medical indicator"} for r in rows]

@router.get("/inactivity")
async def inactivity_history(sensor_id: Optional[str] = Query(None), limit: int = Query(50, le=200),
                              db: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    q = select(InactivityEvent).order_by(InactivityEvent.timestamp.desc()).limit(limit)
    if sensor_id:
        q = q.where(InactivityEvent.sensor_id == sensor_id)
    result = await db.execute(q)
    rows = result.scalars().all()
    return [{"id": r.id, "sensor_id": r.sensor_id, "timestamp": r.timestamp.isoformat(),
             "duration_minutes": r.duration_minutes} for r in rows]
