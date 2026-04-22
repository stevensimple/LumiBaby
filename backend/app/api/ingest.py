import logging
from datetime import datetime
from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy import select, and_
from app.database import async_session_maker
from app.models.sensor import Sensor, SensorHeartbeat
from app.models.metrics import PresenceEvent, MovementMetric, SignalPatternMetric, InactivityEvent
from app.models.event import Alert
from app.models.sleep import SleepSession, DailySleepSummary
from app.processing.pipeline import process_packet
from app.processing.sleep_tracker import update as sleep_update, quality_label, compute_sleep_score
from app.events.engine import manager

router = APIRouter()
logger = logging.getLogger(__name__)


class CSIPacket(BaseModel):
    sensor_id: str
    timestamp: float
    rssi: int
    noise_floor: int = -95
    raw_csi: list[float]
    num_subcarriers: int
    antenna_count: int = 1


@router.post("")
async def ingest(packet: CSIPacket, background_tasks: BackgroundTasks):
    result = process_packet(packet.sensor_id, packet.raw_csi, packet.rssi)
    if result is None:
        return {"status": "skipped"}
    background_tasks.add_task(_persist_and_broadcast, packet, result)
    return {"status": "ok", "activity_score": result["status"]["activity_score"]}


async def _persist_and_broadcast(packet: CSIPacket, result: dict):
    try:
        now = datetime.utcnow()
        s = result["status"]

        # Sleep tracker update
        sleep_info = sleep_update(
            sensor_id=packet.sensor_id,
            movement_level=s["movement"]["level"],
            baby_detected=s["baby"]["detected"],
            now=now,
        )

        async with async_session_maker() as db:
            # Update sensor
            sensor_res = await db.execute(select(Sensor).where(Sensor.sensor_id == packet.sensor_id))
            sensor = sensor_res.scalar_one_or_none()
            if sensor:
                sensor.last_seen = now
                sensor.is_online = True

            db.add(SensorHeartbeat(sensor_id=packet.sensor_id, rssi=packet.rssi, packet_rate=result["packet_rate"]))
            db.add(PresenceEvent(sensor_id=packet.sensor_id, detected=s["baby"]["detected"], confidence=s["baby"]["confidence"]))
            db.add(MovementMetric(sensor_id=packet.sensor_id, level=s["movement"]["level"], value=s["movement"]["value"], confidence=s["movement"]["confidence"]))
            db.add(SignalPatternMetric(sensor_id=packet.sensor_id, rhythmic=s["signal_pattern"]["rhythmic"], confidence=s["signal_pattern"]["confidence"]))

            # Persist sleep events
            sleep_event = sleep_info.get("event")
            if sleep_event:
                if sleep_event["type"] == "sleep_start":
                    session = SleepSession(
                        id=sleep_event["session_id"],
                        sensor_id=packet.sensor_id,
                        start_time=datetime.fromisoformat(sleep_event["start_time"]),
                        is_active=True,
                        calm_ratio=0.0,
                        wake_events_count=0,
                        sleep_score=0,
                        quality_label="",
                        timeline=[],
                    )
                    db.add(session)

                elif sleep_event["type"] == "sleep_end":
                    res = await db.execute(select(SleepSession).where(SleepSession.id == sleep_event["session_id"]))
                    session = res.scalar_one_or_none()
                    if session:
                        session.end_time = datetime.fromisoformat(sleep_event["end_time"])
                        session.duration_minutes = sleep_event["duration_minutes"]
                        session.calm_ratio = sleep_event["calm_ratio"]
                        session.wake_events_count = sleep_event["wake_events_count"]
                        session.sleep_score = sleep_event["sleep_score"]
                        session.quality_label = sleep_event["quality_label"]
                        session.is_active = False
                        session.timeline = sleep_event["timeline"]
                        # Update daily summary
                        date_str = datetime.fromisoformat(sleep_event["start_time"]).strftime("%Y-%m-%d")
                        await _upsert_daily_summary(db, packet.sensor_id, date_str, sleep_event)

                elif sleep_event["type"] == "wake_event":
                    db.add(Alert(
                        sensor_id=packet.sensor_id,
                        type="wake_event",
                        message="Réveil détecté",
                        severity="info",
                    ))

            # Process regular events (inactivity, presence lost, unusual activity)
            for event in result.get("events", []):
                msg = event["details"].get("message", event["type"])
                severity = "critical" if event["type"] == "presence_lost" else "warning"
                if event["type"] == "prolonged_inactivity":
                    db.add(InactivityEvent(sensor_id=packet.sensor_id, duration_minutes=event["details"].get("minutes", 0)))
                db.add(Alert(sensor_id=packet.sensor_id, type=event["type"], message=msg, severity=severity))

            await db.commit()

        # Broadcast
        broadcast_data = {**s}
        if sleep_info.get("state") in ("sleeping", "wake_event"):
            broadcast_data["sleep"] = {
                "state": sleep_info["state"],
                "session_id": sleep_info.get("session_id"),
                "start_time": sleep_info.get("sleep_start"),
                "duration_minutes": sleep_info.get("duration_minutes", 0),
                "wake_events_count": sleep_info.get("wake_events", 0),
                "calm_ratio": sleep_info.get("calm_ratio", 0),
            }
        else:
            broadcast_data["sleep"] = {"state": sleep_info.get("state", "awake")}

        await manager.broadcast_status(broadcast_data)
        for event in result.get("events", []):
            await manager.broadcast_event(event["type"], event["sensor_id"], event.get("details", {}))
        if sleep_info.get("event"):
            e = sleep_info["event"]
            await manager.broadcast_event(e["type"], packet.sensor_id, e)

    except Exception as e:
        logger.error(f"Persist/broadcast error: {e}", exc_info=True)


async def _upsert_daily_summary(db, sensor_id: str, date_str: str, sleep_event: dict):
    from sqlalchemy import and_
    res = await db.execute(
        select(DailySleepSummary).where(
            and_(DailySleepSummary.sensor_id == sensor_id, DailySleepSummary.date == date_str)
        )
    )
    summary = res.scalar_one_or_none()
    duration = sleep_event.get("duration_minutes", 0)
    start_hour = datetime.fromisoformat(sleep_event["start_time"]).hour + datetime.fromisoformat(sleep_event["start_time"]).minute / 60

    if summary:
        summary.total_sleep_minutes += duration
        summary.wake_count += sleep_event.get("wake_events_count", 0)
        summary.session_count += 1
        summary.longest_streak_minutes = max(summary.longest_streak_minutes, duration)
        summary.sleep_score = compute_sleep_score(summary.total_sleep_minutes, sleep_event["calm_ratio"], summary.wake_count)
        summary.quality_label = quality_label(summary.sleep_score)
        summary.avg_sleep_start_hour = (summary.avg_sleep_start_hour + start_hour) / 2 if summary.avg_sleep_start_hour else start_hour
    else:
        score = sleep_event.get("sleep_score", 0)
        db.add(DailySleepSummary(
            sensor_id=sensor_id,
            date=date_str,
            total_sleep_minutes=duration,
            wake_count=sleep_event.get("wake_events_count", 0),
            longest_streak_minutes=duration,
            sleep_score=score,
            quality_label=sleep_event.get("quality_label", ""),
            session_count=1,
            avg_sleep_start_hour=start_hour,
        ))
