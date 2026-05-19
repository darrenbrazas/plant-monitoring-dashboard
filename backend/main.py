#import fastAPI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

#import the main functions from each file
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

#gets all three backend files

@app.get("/data")
def get_data():
    #calls simulator to generate the sensor data
    reading = generate_data()
    #passes the reading to the anomoly detector
    reading.alerts = detect_anomalies(reading)
    #returns a sensorreading object
    return reading
