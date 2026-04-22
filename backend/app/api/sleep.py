from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.database import get_session
from app.middleware.auth import get_current_user
from app.models.sleep import SleepSession, DailySleepSummary
from app.processing.sleep_tracker import get_current_session_info

router = APIRouter()


@router.get("/current")
async def current_session(
    sensor_id: str = Query(...),
    current_user=Depends(get_current_user)
):
    """Return active sleep session, if any."""
    info = get_current_session_info(sensor_id)
    if not info:
        return {"active": False, "message": "Pas de session de sommeil en cours"}
    return {"active": True, **info}


@router.get("/tonight")
async def tonight_session(
    sensor_id: str = Query(...),
    db: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user)
):
    """Return the most recent completed or active session."""
    # First check in-memory (active session)
    info = get_current_session_info(sensor_id)
    if info:
        return {"active": True, **info}

    # Fallback: latest completed session from DB
    cutoff = datetime.utcnow() - timedelta(hours=16)
    result = await db.execute(
        select(SleepSession)
        .where(and_(SleepSession.sensor_id == sensor_id, SleepSession.start_time >= cutoff))
        .order_by(SleepSession.start_time.desc())
        .limit(1)
    )
    session = result.scalar_one_or_none()
    if not session:
        return {"active": False, "message": "Aucune donnée cette nuit"}
    return {
        "active": False,
        "session_id": session.id,
        "start_time": session.start_time.isoformat() + "Z",
        "end_time": session.end_time.isoformat() + "Z" if session.end_time else None,
        "duration_minutes": session.duration_minutes,
        "calm_ratio": session.calm_ratio,
        "wake_events_count": session.wake_events_count,
        "sleep_score": session.sleep_score,
        "quality_label": session.quality_label,
        "timeline": session.timeline or [],
    }


@router.get("/history")
async def sleep_history(
    sensor_id: str = Query(...),
    days: int = Query(7, le=30),
    db: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user)
):
    """Daily summaries for the last N days."""
    cutoff = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
    result = await db.execute(
        select(DailySleepSummary)
        .where(and_(DailySleepSummary.sensor_id == sensor_id, DailySleepSummary.date >= cutoff))
        .order_by(DailySleepSummary.date.desc())
    )
    rows = result.scalars().all()
    return [
        {
            "id": r.id,
            "date": r.date,
            "total_sleep_minutes": r.total_sleep_minutes,
            "wake_count": r.wake_count,
            "longest_streak_minutes": r.longest_streak_minutes,
            "sleep_score": r.sleep_score,
            "quality_label": r.quality_label,
            "session_count": r.session_count,
            "avg_sleep_start_hour": r.avg_sleep_start_hour,
        }
        for r in rows
    ]


@router.get("/weekly")
async def weekly_trend(
    sensor_id: str = Query(...),
    db: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user)
):
    """7-day trend + consistency score."""
    result = await db.execute(
        select(DailySleepSummary)
        .where(DailySleepSummary.sensor_id == sensor_id)
        .order_by(DailySleepSummary.date.desc())
        .limit(7)
    )
    rows = result.scalars().all()
    if not rows:
        return {"days": [], "avg_score": 0, "consistency_score": 0, "avg_duration_hours": 0}

    scores = [r.sleep_score for r in rows]
    durations = [r.total_sleep_minutes / 60 for r in rows]
    start_hours = [r.avg_sleep_start_hour for r in rows if r.avg_sleep_start_hour is not None]

    avg_score = round(sum(scores) / len(scores))
    avg_duration = round(sum(durations) / len(durations), 1)

    # Consistency: lower std-dev of sleep start hour = more consistent
    consistency = 100
    if len(start_hours) >= 2:
        import statistics
        std = statistics.stdev(start_hours)
        consistency = max(0, min(100, int(100 - std * 20)))

    return {
        "days": [
            {
                "date": r.date,
                "sleep_score": r.sleep_score,
                "quality_label": r.quality_label,
                "total_hours": round(r.total_sleep_minutes / 60, 1),
                "wake_count": r.wake_count,
            }
            for r in rows
        ],
        "avg_score": avg_score,
        "consistency_score": consistency,
        "avg_duration_hours": avg_duration,
    }
