
from collections import deque
from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import StrEnum
import json


class Phase(StrEnum):
    RED = "Red"
    GREEN = "Green"
    YELLOW = "Yellow"

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
    target_approach_index: int
    clear_time: float=0.0  # Time it takes for the vehicle to reach the stop line
    wait_time: float=0.0  # Duration the vehicle has been waiting stopped

    def __post_init__(self):
        # Validate the clear time
        if self.clear_time < 0.0:
            raise ValueError("clear_time must be non-negative")

@dataclass
class Approach:
    name: str | None = None
    cars: deque[Car] = field(default_factory=deque)
    crosswalk: Crosswalk | None = None
    light: TrafficSignal = field(default_factory=TrafficSignal)

    def __init__(self, *, has_crosswalk: bool = False, name: str | None = None):
        self.name = name
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

@dataclass
class Road:
    approaches: Sequence[Approach]
    phase: Phase = Phase.RED

class Intersection:
    def __init__(self, roads: list[Road]):
        self.roads: list[Road] = roads

    @property
    def approaches(self):
        return [approach for road in self.roads for approach in road.approaches]

    def snapshot(self) -> dict:
        return {
            approach.name if approach.name is not None else f"approach_{i}": approach.snapshot()
            for i, approach in enumerate(self.approaches)
        }

def get_clear_time(pos_idx: int) -> float:
    CAR_SPACING_TIME = 1.5  # seconds per car
    return pos_idx * CAR_SPACING_TIME

def main():
    
    # Two approaches
    approach_1 = Approach(has_crosswalk=True)
    approach_2 = Approach(has_crosswalk=False)

    # Build the "intersection"
    road = Road(approaches=[approach_1, approach_2])
    intersection = Intersection(roads=[road])

    # Put a car on approach 1
    fast_car = Car(target_approach_index=1, clear_time=1.0)
    approach_1.add_car(fast_car)

    # Display the intersection
    state = intersection.snapshot()
    print(json.dumps(state, indent=4))


if __name__ == "__main__":
    main()