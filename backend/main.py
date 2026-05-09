from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from anomaly import detect_anomalies
from simulator import generate_data

app = FastAPI(title="Smart Power Plant Monitoring API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/data")
def get_data():
    reading = generate_data()
    reading.alerts = detect_anomalies(reading)
    return reading
