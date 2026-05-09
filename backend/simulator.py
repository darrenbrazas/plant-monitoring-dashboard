import random
import time

from models import SensorReading


def _occasionally_spike(value: float, chance: float, amount: tuple[float, float]) -> float:
    if random.random() < chance:
        return value + random.uniform(*amount)
    return value


def _occasionally_drop(value: float, chance: float, amount: tuple[float, float]) -> float:
    if random.random() < chance:
        return value - random.uniform(*amount)
    return value


def generate_data() -> SensorReading:
    temperature = _occasionally_spike(random.uniform(236, 274), 0.12, (14, 29))
    pressure = _occasionally_spike(random.uniform(1110, 1368), 0.1, (70, 150))
    flow_rate = _occasionally_drop(random.uniform(63, 96), 0.09, (8, 18))
    vibration = _occasionally_spike(random.uniform(0.8, 3.5), 0.11, (0.8, 1.8))

    output_mw = random.uniform(640, 720)
    if temperature > 285 or pressure > 1430 or flow_rate < 55:
        output_mw -= random.uniform(25, 70)

    return SensorReading(
        plant_id="OPG-DARLINGTON-SIM",
        unit=random.choice(["Unit 1", "Unit 2", "Unit 3", "Unit 4"]),
        output_mw=round(output_mw, 1),
        temperature=round(temperature, 2),
        pressure=round(pressure, 2),
        flow_rate=round(flow_rate, 2),
        vibration=round(vibration, 2),
        timestamp=time.time(),
    )
