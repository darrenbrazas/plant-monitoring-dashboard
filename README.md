# Smart Power Plant Monitoring System

A full-stack real-time monitoring dashboard that simulates industrial sensor data for a nuclear generating station, detects operational anomalies using threshold-based logic, and visualizes live plant conditions in a React dashboard. The project is themed around Ontario Power Generation's Darlington Nuclear Generating Station and models the kind of SCADA-adjacent tooling used in real grid operations.

---

## What It Does

The system continuously generates simulated sensor readings — temperature, pressure, flow rate, vibration, and generating unit output — and streams them to a React frontend that updates every second. The backend checks each reading against operating thresholds and raises tiered alerts (medium or high severity) when a sensor goes out of range. The dashboard displays live metric cards, an active alerts panel, and rolling time-series charts for all four sensor types.

The project demonstrates end-to-end full-stack development: a Python REST API with data modeling and business logic on the backend, and a reactive single-page application with real-time charting on the frontend.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend language | Python 3.11+ |
| API framework | FastAPI |
| Data validation | Pydantic v2 |
| ASGI server | Uvicorn |
| Frontend framework | React 18 |
| Build tool | Vite |
| Charting | Chart.js + react-chartjs-2 |
| HTTP client | Axios |
| Icons | lucide-react |

---

## Architecture

```
Sensor Simulator (simulator.py)
        |
        v
  FastAPI Backend (main.py)
        |
        ├── Anomaly Detection (anomaly.py)
        |         |
        |         v
        |     Tiered Alerts (medium / high)
        |
        v
  GET /data  ──polling every 1s──>  React Dashboard (App.jsx)
                                          |
                                    ┌─────┴──────┐
                                 Metric       Rolling
                                 Cards        Charts
```

---

## Project Structure

```
backend/
  main.py          API routes and CORS config
  models.py        Pydantic models: SensorReading, Alert
  simulator.py     Randomized sensor data generation with occasional spikes/drops
  anomaly.py       Threshold-based anomaly detection, returns Alert objects
  requirements.txt Python dependencies

frontend/
  index.html       HTML entry point
  vite.config.js   Vite + React plugin config
  package.json     Node dependencies
  .env             API base URL override (VITE_API_URL)
  src/
    main.jsx       React app entry point
    App.jsx        Main dashboard component, polling logic, state management
    api.js         Axios wrapper for GET /data
    styles.css     Dark theme dashboard styles
```

---

## Sensor Simulation

`simulator.py` generates a new `SensorReading` on every request using realistic operating ranges for a CANDU reactor environment:

| Sensor | Normal Range | Spike/Drop Behavior |
|---|---|---|
| Temperature | 236–274 °C | +14–29 °C spike, 12% chance |
| Pressure | 1110–1368 kPa | +70–150 kPa spike, 10% chance |
| Flow Rate | 63–96 L/s | −8–18 L/s drop, 9% chance |
| Vibration | 0.8–3.5 Hz | +0.8–1.8 Hz spike, 11% chance |
| Output | 640–720 MW | Reduced by 25–70 MW if sensors exceed limits |

Each reading also includes a plant ID (`OPG-DARLINGTON-SIM`), a randomly assigned generating unit (Unit 1–4), and a Unix timestamp.

---

## Anomaly Detection

`anomaly.py` applies two-tier threshold checks on every reading. Alerts are returned as structured objects alongside the sensor data.

**Upper-bound sensors (temperature, pressure, vibration):**

| Sensor | Medium threshold | High threshold |
|---|---|---|
| Temperature | 280 °C | 292 °C |
| Pressure | 1400 kPa | 1475 kPa |
| Vibration | 4.0 Hz | 4.7 Hz |

**Lower-bound sensor (flow rate):**

| Level | Threshold |
|---|---|
| Trending low (medium) | < 58 L/s |
| Critical low (high) | < 52 L/s |

Each `Alert` object contains: `sensor`, `message`, `severity` (`medium` or `high`), `value`, and `threshold`.

---

## API Endpoints

Base URL: `http://localhost:8000` (or `8001` if port 8000 is unavailable)

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Returns `{"status": "ok"}` |
| GET | `/data` | Returns one `SensorReading` with any active alerts |

CORS is enabled for `localhost:3000` and `localhost:5173`.

---

## Setup and Running

### Backend

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser. The backend must be running first.

If you changed the backend port, set it in `frontend/.env`:

```
VITE_API_URL=http://localhost:8001
```

---

## Dashboard Features

- **System status badge** — reflects current state: Normal, Attention, High Alert, Connecting, or Offline
- **Plant strip** — shows plant ID, active generating unit, current output in MW, and timestamp of last reading
- **Metric cards** — live values for temperature, pressure, flow rate, and vibration; cards highlight when a sensor is in alert
- **Active alerts panel** — lists all current anomalies with sensor name, message, measured value, and breach threshold
- **Rolling charts** — Chart.js line charts showing the last 30 readings for each sensor with filled area and smooth curves

---

## Resume Talking Points

- Built a full-stack real-time monitoring dashboard using **FastAPI** and **React**, simulating industrial sensor data for a nuclear generating station modeled on Ontario Power Generation's Darlington facility
- Designed a **Pydantic v2** data model pipeline from sensor simulation through anomaly detection to a typed REST API response
- Implemented **threshold-based anomaly detection** with two severity tiers across four sensor types, returning structured alert objects consumed directly by the frontend
- Built a **React dashboard** with live polling, rolling time-series charts (Chart.js), and conditional UI states (normal / attention / high alert / offline) that update every second
- Applied **CORS configuration**, environment-variable-driven API URLs, and Vite tooling for a production-ready frontend build setup

---

## Future Improvements

- WebSocket stream to replace polling and reduce latency
- Historical logs page with time-range filtering
- CSV export of sensor readings
- Multiple plant views with a plant selector
- Authentication and operator role support
- Persistent alert log with acknowledgement workflow
