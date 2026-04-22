from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_session
from app.models.sensor import Sensor, SensorHeartbeat
from app.middleware.auth import get_current_user
from app.config import settings

router = APIRouter()

class SensorCreate(BaseModel):
    sensor_id: str
    name: str
    location: Optional[str] = None

def auth_dep():
    return Depends(get_current_user) if settings.enable_auth else None

@router.get("")
async def list_sensors(db: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    result = await db.execute(select(Sensor).where(Sensor.owner_id == current_user["id"]))
    sensors = result.scalars().all()
    return [{"sensor_id": s.sensor_id, "name": s.name, "location": s.location,
             "is_online": s.is_online, "last_seen": s.last_seen.isoformat() if s.last_seen else None,
             "created_at": s.created_at.isoformat()} for s in sensors]

@router.post("")
async def create_sensor(body: SensorCreate, db: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    result = await db.execute(select(Sensor).where(Sensor.sensor_id == body.sensor_id))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="sensor_id already registered")
    sensor = Sensor(sensor_id=body.sensor_id, name=body.name, location=body.location, owner_id=current_user["id"])
    db.add(sensor)
    await db.commit()
    return {"sensor_id": sensor.sensor_id, "name": sensor.name, "id": sensor.id}

@router.get("/{sensor_id}")
async def get_sensor(sensor_id: str, db: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    result = await db.execute(select(Sensor).where(Sensor.sensor_id == sensor_id))
    sensor = result.scalar_one_or_none()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    return {"sensor_id": sensor.sensor_id, "name": sensor.name, "location": sensor.location,
            "is_online": sensor.is_online, "last_seen": sensor.last_seen.isoformat() if sensor.last_seen else None}

@router.get("/{sensor_id}/health")
async def sensor_health(sensor_id: str, db: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    result = await db.execute(select(Sensor).where(Sensor.sensor_id == sensor_id))
    sensor = result.scalar_one_or_none()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    hb_result = await db.execute(
        select(SensorHeartbeat).where(SensorHeartbeat.sensor_id == sensor_id)
        .order_by(SensorHeartbeat.timestamp.desc()).limit(10)
    )
    heartbeats = hb_result.scalars().all()
    avg_rssi = sum(h.rssi for h in heartbeats) / len(heartbeats) if heartbeats else -100
    signal_quality = max(0.0, min(1.0, (avg_rssi + 100) / 50))
    avg_rate = sum(h.packet_rate for h in heartbeats) / len(heartbeats) if heartbeats else 0.0
    return {"online": sensor.is_online, "last_seen": sensor.last_seen.isoformat() if sensor.last_seen else None,
            "signal_quality": round(signal_quality, 3), "packet_rate": round(avg_rate, 2), "avg_rssi": avg_rssi}

@router.delete("/{sensor_id}", status_code=204)
async def delete_sensor(sensor_id: str, db: AsyncSession = Depends(get_session), current_user=Depends(get_current_user)):
    result = await db.execute(select(Sensor).where(Sensor.sensor_id == sensor_id, Sensor.owner_id == current_user["id"]))
    sensor = result.scalar_one_or_none()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")
    await db.delete(sensor)
    await db.commit()
