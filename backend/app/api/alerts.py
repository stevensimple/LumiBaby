from datetime import datetime
from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_session
from app.middleware.auth import get_current_user
from app.models.event import Alert

router = APIRouter()

@router.get("")
async def list_alerts(acknowledged: Optional[bool] = Query(None), limit: int = Query(50, le=200),
                       db: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    q = select(Alert).order_by(Alert.created_at.desc()).limit(limit)
    if acknowledged is not None:
        q = q.where(Alert.acknowledged == acknowledged)
    result = await db.execute(q)
    rows = result.scalars().all()
    return [{"id": r.id, "sensor_id": r.sensor_id, "type": r.type, "message": r.message,
             "severity": r.severity, "created_at": r.created_at.isoformat(), "acknowledged": r.acknowledged} for r in rows]

@router.post("/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str, db: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.acknowledged = True
    alert.acknowledged_at = datetime.utcnow()
    await db.commit()
    return {"status": "acknowledged"}
