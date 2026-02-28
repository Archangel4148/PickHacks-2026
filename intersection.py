
from collections import deque
from dataclasses import dataclass, field
from enum import StrEnum
import json

class LightState(StrEnum):
    RED = "Red"
    YELLOW = "Yellow"
    GREEN = "Green"

class WalkState(StrEnum):
    WALK = "Walk"
    FLASHING = "Flashing"
    STOP = "Stop"

@dataclass
class TrafficSignal:
    state: LightState = LightState.RED

@dataclass
class CrosswalkSignal:
    state: WalkState = WalkState.STOP

@dataclass
class Crosswalk:
    light: CrosswalkSignal = field(default_factory=CrosswalkSignal)
    people_waiting: int = 0
    button_pressed: bool = False

@dataclass
class Car:
    target_street_index: int
    clear_time: float
    wait_time: float=0.0

    def __post_init__(self):
        # Validate the clear time
        if self.clear_time < 0.0:
            raise ValueError("clear_time must be non-negative")

@dataclass
class Street:
    cars: deque[Car] = field(default_factory=deque)
    crosswalk: Crosswalk | None = None
    light: TrafficSignal = field(default_factory=TrafficSignal)

    def __init__(self, *, has_crosswalk: bool = False):
        self.cars = deque()
        self.light = TrafficSignal()
        self.crosswalk = Crosswalk() if has_crosswalk else None
    
    @property
    def num_cars(self) -> int:
        return len(self.cars)

    def add_car(self, car: Car):
        self.cars.append(car)

    def snapshot(self) -> dict:
        return {
            "light": self.light.state.value,
            "num_cars": len(self.cars),
            "crosswalk": None if not self.crosswalk else {
                "light": self.crosswalk.light.state.value,
                "people_waiting": self.crosswalk.people_waiting,
                "button_pressed": self.crosswalk.button_pressed,
            }
        }


class Intersection:
    def __init__(self, streets: list[Street]):
        self.streets: list[Street] = streets

    def snapshot(self) -> dict:
        return {
            f"street_{i}": street.snapshot()
            for i, street in enumerate(self.streets)
        }

def main():
    
    # Two "streets" = a single road with a traffic light
    street_1 = Street(has_crosswalk=True)
    street_2 = Street(has_crosswalk=False)

    # Build the "intersection"
    intersection = Intersection(streets=[street_1, street_2])

    # Put a car on street 1
    fast_car = Car(target_street_index=1, clear_time=1.0)
    street_1.add_car(fast_car)

    # Display the intersection
    state = intersection.snapshot()
    print(json.dumps(state, indent=4))


if __name__ == "__main__":
    main()