import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Boolean, Float, DateTime, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class SleepSession(Base):
    __tablename__ = "sleep_sessions"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    sensor_id: Mapped[str] = mapped_column(String, nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_minutes: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    calm_ratio: Mapped[float] = mapped_column(Float, default=0.0)
    wake_events_count: Mapped[int] = mapped_column(Integer, default=0)
    sleep_score: Mapped[int] = mapped_column(Integer, default=0)
    quality_label: Mapped[str] = mapped_column(String, default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    timeline: Mapped[Optional[list]] = mapped_column(JSON, default=list)

class DailySleepSummary(Base):
    __tablename__ = "daily_sleep_summaries"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    sensor_id: Mapped[str] = mapped_column(String, nullable=False)
    date: Mapped[str] = mapped_column(String, nullable=False)
    total_sleep_minutes: Mapped[float] = mapped_column(Float, default=0.0)
    wake_count: Mapped[int] = mapped_column(Integer, default=0)
    longest_streak_minutes: Mapped[float] = mapped_column(Float, default=0.0)
    sleep_score: Mapped[int] = mapped_column(Integer, default=0)
    quality_label: Mapped[str] = mapped_column(String, default="")
    session_count: Mapped[int] = mapped_column(Integer, default=0)
    avg_sleep_start_hour: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
