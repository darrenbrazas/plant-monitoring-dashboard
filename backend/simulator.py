import random
import time

from models import SensorReading

#this controls the mock sensor reading whether it spikes or not

#private helper funciton 1 (for mock data)
def _occasionally_spike(value: float, chance: float, amount: tuple[float, float]) -> float:
    if random.random() < chance:
        return value + random.uniform(*amount)
    return value

#private helper funciton 2 (for mock data)
def _occasionally_drop(value: float, chance: float, amount: tuple[float, float]) -> float:
    if random.random() < chance:
        return value - random.uniform(*amount)
    return value

#generates data for the SensorReading object
def generate_data() -> SensorReading:
    #temp, pressure, vibration chosen as spike since its a high risk and flow rate chosen as drop since lower is a risk
    temperature = _occasionally_spike(random.uniform(236, 274), 0.12, (14, 29))
    pressure = _occasionally_spike(random.uniform(1110, 1368), 0.1, (70, 150))
    flow_rate = _occasionally_drop(random.uniform(63, 96), 0.09, (8, 18))
    vibration = _occasionally_spike(random.uniform(0.8, 3.5), 0.11, (0.8, 1.8))

    #the output_mw chooses a random megawatt value between 640 and 720m however if plant conditions  are bad
    #then the plant will simply choose less power
    output_mw = random.uniform(640, 720)
    if temperature > 285 or pressure > 1430 or flow_rate < 55:
        output_mw -= random.uniform(25, 70)

    #returns the randomized sensor readings (plant id stays the same as OPG-Darlington)
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
