from models import Alert, SensorReading


THRESHOLDS = {
    "temperature": {"medium": 280.0, "high": 292.0, "unit": "C"},
    "pressure": {"medium": 1400.0, "high": 1475.0, "unit": "kPa"},
    "flow_rate": {"low": 58.0, "critical_low": 52.0, "unit": "L/s"},
    "vibration": {"medium": 4.0, "high": 4.7, "unit": "Hz"},
}


def _upper_alert(sensor: str, value: float, medium: float, high: float, unit: str):
    if value >= high:
        return Alert(
            sensor=sensor,
            message=f"{sensor.replace('_', ' ').title()} above high limit",
            severity="high",
            value=round(value, 2),
            threshold=high,
        )
    if value >= medium:
        return Alert(
            sensor=sensor,
            message=f"{sensor.replace('_', ' ').title()} requires attention",
            severity="medium",
            value=round(value, 2),
            threshold=medium,
        )
    return None


def detect_anomalies(reading: SensorReading) -> list[Alert]:
    alerts: list[Alert] = []

    for sensor in ("temperature", "pressure", "vibration"):
        threshold = THRESHOLDS[sensor]
        alert = _upper_alert(
            sensor,
            getattr(reading, sensor),
            threshold["medium"],
            threshold["high"],
            threshold["unit"],
        )
        if alert:
            alerts.append(alert)

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
