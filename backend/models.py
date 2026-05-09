from pydantic import BaseModel, Field


class Alert(BaseModel):
    sensor: str
    message: str
    severity: str = Field(pattern="^(low|medium|high)$")
    value: float
    threshold: float


class SensorReading(BaseModel):
    plant_id: str
    unit: str
    output_mw: float
    temperature: float
    pressure: float
    flow_rate: float
    vibration: float
    timestamp: float
    alerts: list[Alert] = Field(default_factory=list)
