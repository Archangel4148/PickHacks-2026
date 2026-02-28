
from dataclasses import dataclass, field
from enum import StrEnum

class LightState(StrEnum):
    RED = "Red"
    YELLOW = "Yellow"
    GREEN = "Green"

@dataclass
class Car:
    target_street: Street
    clear_time: float
    wait_time: float

@dataclass
class TrafficSignal:
    state: LightState = LightState.RED

@dataclass
class CrosswalkSignal:
    state: LightState = LightState.RED

@dataclass
class Crosswalk:
    light: CrosswalkSignal = CrosswalkSignal()
    people_waiting: int = 0
    button_pressed: bool = False

@dataclass
class Street:
    cars: list[Car] = field(default_factory=list)
    crosswalk: Crosswalk | None = None
    light: TrafficSignal = TrafficSignal()

class Intersection:
    def __init__(self, streets: list[Street]):
        self.streets: list[Street] = streets


