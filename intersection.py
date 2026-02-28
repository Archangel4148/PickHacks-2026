
from dataclasses import dataclass
from enum import StrEnum

@dataclass
class Car:
    target_street: Street
    clear_time: float
    wait_time: float

@dataclass
class Crosswalk:
    people_waiting: int = 0
    light_on: bool = False
    button_pressed: bool = False

@dataclass
class Street:
    cars: list[Car] = None
    crosswalk: Crosswalk | None = None

class Intersection:
    def __init__(self, streets: list[Street]):
        self.streets: list[Street] = streets


