import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Boolean, Float, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class Sensor(Base):
    __tablename__ = "sensors"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    sensor_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    owner_id: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_seen: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_online: Mapped[bool] = mapped_column(Boolean, default=False)

class SensorHeartbeat(Base):
    __tablename__ = "sensor_heartbeats"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    sensor_id: Mapped[str] = mapped_column(String, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    rssi: Mapped[int] = mapped_column(Integer, nullable=False)
    packet_rate: Mapped[float] = mapped_column(Float, default=0.0)
