# LumiBaby

Monitor your baby's sleep and activity using WiFi signals — no cameras, no wearables, no contact.

```
ESP32-S3 → Backend (FastAPI) → PostgreSQL → WebSocket → iPhone app (SwiftUI)
```

> **Not a medical device.** LumiBaby provides activity and sleep pattern indicators for informational purposes only. Always follow safe sleep guidelines.

## Quick Start

### 1. Backend (local dev)

```bash
cd backend
cp ../.env.example .env
# Edit .env — set a strong SECRET_KEY
pip install -r requirements.txt
uvicorn app.main:app --reload
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### 2. Backend (Docker)

```bash
cp .env.example .env
# Edit .env — set SECRET_KEY
docker compose up -d
```

### 3. iOS App (LumiBaby)

1. Open Xcode → New Project → App (SwiftUI, iOS 16+)
2. Name it **LumiBaby**, Bundle ID of your choice
3. Delete the generated `ContentView.swift`
4. Drag all files from `ios/WiFiVision/` into the Xcode project
5. Replace `@main` entry point with `WiFiVisionApp.swift`
6. Build & run on simulator or device

In **Réglages** tab, set your server URL (e.g. `http://192.168.1.100:8000`).

### 4. Firmware (ESP32-S3)

```bash
# Prerequisites: ESP-IDF v5.x
cd firmware/esp32-csi
idf.py set-target esp32s3

# Edit main/main.c — set WIFI_SSID, WIFI_PASSWORD, BACKEND_IP
idf.py build flash monitor
```

The sensor streams CSI packets to `POST /api/v1/ingest` at ~20 Hz.

## Architecture

| Layer | Tech | Role |
|-------|------|------|
| Firmware | ESP32-S3 C | CSI capture → HTTP POST |
| Backend | FastAPI + SQLAlchemy | Processing, REST API, WebSocket |
| Database | PostgreSQL / SQLite | History, events, calibration, sleep |
| iOS App | SwiftUI (French, dark) | Live dashboard, sleep tracking, alerts |

## API Overview

| Endpoint | Description |
|----------|-------------|
| `POST /api/v1/auth/login` | Get JWT token |
| `POST /api/v1/ingest` | Receive CSI packet (no auth) |
| `GET /api/v1/status/live` | Current room status |
| `GET /api/v1/sensors` | List sensors |
| `GET /api/v1/history/presence` | Presence history |
| `GET /api/v1/alerts` | Active alerts |
| `POST /api/v1/calibration/start` | Start calibration |
| `GET /api/v1/sleep/current` | Live sleep session |
| `GET /api/v1/sleep/tonight` | Tonight's sleep summary |
| `GET /api/v1/sleep/history` | Daily sleep history |
| `GET /api/v1/sleep/weekly` | 7-day trend & consistency |
| `WS /ws/live?token=` | Real-time updates |

## Signal Processing

```
Raw CSI → Amplitude extraction → Median filter
                                       ↓
                    Presence: variance vs. baseline
                    Movement: frame-to-frame energy → calm/light/agitated
                    Signal pattern: bandpass 0.1-0.5 Hz + FFT (experimental)
                                       ↓
                          Activity score (0–99, higher = calmer)
                                       ↓
                         WebSocket broadcast → iOS app
```

## Sleep Tracking

LumiBaby automatically detects sleep sessions from movement patterns:

```
awake → drowsy (~5 min calm) → sleeping
sleeping ↔ wake_event (~1.5 min agitation)
```

**Sleep score** (0–100):
- Duration component (up to 30 pts for 11h+)
- Calm ratio component (up to 20 pts)
- Wake event penalty (−4 pts per event)

**Daily summaries**: total sleep, longest streak, session count, avg start time.
**Weekly trends**: avg score, consistency score, avg duration.

## Calibration

4-step guided flow (2 min total):
1. **Pièce vide** — establishes baseline variance
2. **Sans mouvement** — presence threshold
3. **Mouvement lent** — movement calibration
4. **Repos calme** — signal pattern baseline

## iOS App (LumiBaby)

Premium dark UI in French with 5 tabs:
- **Accueil** — animated wave status card, activity score, inactivity alerts
- **Sommeil** — tonight's session, timeline, weekly bar chart, insights
- **Capteur** — sensor health, signal strength, placement tips
- **Alertes** — inactivity and unusual activity notifications
- **Réglages** — server URL, room name, disclaimer

## Security

- JWT auth enabled by default (`ENABLE_AUTH=true`)
- No hardcoded secrets — all via environment variables
- Ingest endpoint (`/api/v1/ingest`) is auth-free (sensors use sensor_id only)

## Hardware

| Option | Hardware | Cost | CSI |
|--------|----------|------|-----|
| Recommended | ESP32-S3 DevKit | ~$9 | Full |
| Research | Intel 5300 NIC | ~$50 | Full |
| Dev/test | Any machine | $0 | Simulated |

> ESP32-C3 and original ESP32 are **not supported** (single-core, insufficient for CSI DSP).
