from models import Alert, SensorReading

#files purpose is to take a reading and return a list of alerts

#different threshold for each reading

THRESHOLDS = {
    "temperature": {"medium": 280.0, "high": 292.0, "unit": "C"},
    "pressure": {"medium": 1400.0, "high": 1475.0, "unit": "kPa"},
    "flow_rate": {"low": 58.0, "critical_low": 52.0, "unit": "L/s"},
    "vibration": {"medium": 4.0, "high": 4.7, "unit": "Hz"},
}

#returns the alerts if the current sensor reading is  above the high or medium limits defined in the object above
# also returns no alerts if the reading lies below both
def _upper_alert(sensor: str, value: float, medium: float, high: float, unit: str):
    #checks in priority order, first checks if the reading is greater than the high threshold
    if value >= high:
        return Alert(
            sensor=sensor,
            message=f"{sensor.replace('_', ' ').title()} above high limit",
            severity="high",
            value=round(value, 2),
            threshold=high,
        )
    #then checks the medium one
    if value >= medium:
        return Alert(
            sensor=sensor,
            message=f"{sensor.replace('_', ' ').title()} requires attention",
            severity="medium",
            value=round(value, 2),
            threshold=medium,
        )
    return None

#starts with an empty list 
def detect_anomalies(reading: SensorReading) -> list[Alert]:
    alerts: list[Alert] = []

    for sensor in ("temperature", "pressure", "vibration"):
        threshold = THRESHOLDS[sensor]
        #call the upper alert function with the parameters for each type of upper bounded sensor (3 times)
        alert = _upper_alert(
            sensor,
            #acceses an attribute using a string name i.e reading.temperature or reading.pressure
            getattr(reading, sensor),
            threshold["medium"],
            threshold["high"],
            threshold["unit"],
        )
        if alert:
            alerts.append(alert)

    #flow rate is checked separately since it's lower bounded, there is no lower alert function since it's only one sensor that has risk at lower values
    #should include a lower alert for scalability
    flow = reading.flow_rate
    flow_limits = THRESHOLDS["flow_rate"]
    if flow <= flow_limits["critical_low"]:
        alerts.append(
            Alert(
                sensor="flow_rate",
                message="Flow rate below critical operating range",
                severity="high",
                value=round(flow, 2),
                threshold=flow_limits["critical_low"],
            )
        )
    elif flow <= flow_limits["low"]:
        alerts.append(
            Alert(
                sensor="flow_rate",
                message="Flow rate trending low",
                severity="medium",
                value=round(flow, 2),
                threshold=flow_limits["low"],
            )
        )

    return alerts
