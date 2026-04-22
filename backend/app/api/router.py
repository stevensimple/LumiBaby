from fastapi import APIRouter
from app.api import auth, sensors, ingest, status, history, calibration, alerts, sleep

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(sensors.router, prefix="/sensors", tags=["sensors"])
api_router.include_router(ingest.router, prefix="/ingest", tags=["ingest"])
api_router.include_router(status.router, prefix="/status", tags=["status"])
api_router.include_router(history.router, prefix="/history", tags=["history"])
api_router.include_router(calibration.router, prefix="/calibration", tags=["calibration"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
api_router.include_router(sleep.router, prefix="/sleep", tags=["sleep"])
