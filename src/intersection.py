
from collections import deque
from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import StrEnum
import json
from typing import Self

class Phase(StrEnum):
    ALL_RED = "All Red"
    THROUGH = "Through"
    LEFT_TURN = "Left Turn"

class LightState(StrEnum):
    RED = "Red"
    YELLOW = "Yellow"
    GREEN = "Green"
    LEFT_ARROW = "Left Arrow"

    @classmethod
    def from_phase(cls, phase: Phase) -> Self:
        PHASE_MAP = {
            Phase.ALL_RED: cls.RED,
            Phase.THROUGH: cls.GREEN,
            Phase.LEFT_TURN: cls.LEFT_ARROW,
        }
        return PHASE_MAP[phase]


class WalkState(StrEnum):
    WALK = "Walk"
    FLASHING = "Flashing"
    STOP = "Stop"

class Turn(StrEnum):
    THROUGH = "Through"
    LEFT_TURN = "Left Turn"
    RIGHT_TURN = "Right Turn"

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
    target_approach: str  # Name of the target approach
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

    def snapshot(self, intersection: "Intersection" | None = None) -> dict:
        """Return snapshot of this approach, optionally showing car turn directions."""
        car_turns = None
        if intersection:
            car_turns = [
                intersection.get_turn(self.name, car.target_approach).value
                for car in self.cars
            ]

        return {
            "light": self.light.state.value,
            "num_cars": len(self.cars),
            "car_turns": car_turns,
            "crosswalk": None if not self.crosswalk else {
                "light": self.crosswalk.light.state.value,
                "people_waiting": self.crosswalk.people_waiting,
                "button_pressed": self.crosswalk.button_pressed,
            }
        }

@dataclass
class Road:
    approaches: Sequence[Approach]
    phase: Phase = Phase.ALL_RED

class Intersection:
    def __init__(self, roads: list[Road], topology: dict[str, dict[str, Turn]]):
        self.roads: list[Road] = roads
        self.topology: dict[str, dict[str, Turn]] = topology

    def approach_to_road(self, approach: Approach) -> Road:
        for road in self.roads:
            if approach in road.approaches:
                return road

    @property
    def approaches(self):
        return [a for r in self.roads for a in r.approaches]

    def set_road_phase(self, road: Road, phase: Phase):
        # Set the light phase of the road
        road.phase = phase

        for approach in road.approaches:
            approach.light.state = LightState.from_phase(phase)

    def set_road_crosswalks(self, road: Road, state: WalkState):
        # Set the crosswalk states for the road (assuming crosswalks sharing a road trigger together)
        for approach in road.approaches:
            if approach.crosswalk:
                approach.crosswalk.light.state = state

    def get_turn(self, from_approach: str, to_approach: str) -> Turn:
        try:
            return self.topology[from_approach][to_approach]
        except KeyError:
            raise ValueError(f"No valid turn from {from_approach} to {to_approach}")

    def snapshot(self) -> dict:
        return {
            f"road_{i}": {
                "phase": road.phase.value,
                "approaches": {
                    approach.name if approach.name else f"approach_{j}": approach.snapshot(self)
                    for j, approach in enumerate(road.approaches)
                }
            }
            for i, road in enumerate(self.roads)
        }

def get_clear_time(pos_idx: int) -> float:
    CAR_SPACING_TIME = 1.5  # seconds per car
    return pos_idx * CAR_SPACING_TIME

def turn_allowed(phase: Phase, turn: Turn) -> bool:
    match phase:
        case Phase.THROUGH:
            return turn in (Turn.THROUGH, Turn.RIGHT_TURN)
        case Phase.LEFT_TURN:
            return turn == Turn.LEFT_TURN
        case Phase.ALL_RED:
            return turn == Turn.RIGHT_TURN  # Allow right on red
        case _:
            return False

def main():
    
    # Two approaches
    approach_1 = Approach(name="app1", has_crosswalk=True)
    approach_2 = Approach(name="app2", has_crosswalk=False)

    # Build the "intersection"
    road = Road(approaches=[approach_1, approach_2])
    intersection = Intersection(roads=[road])

    # Put a car on approach 1
    fast_car = Car(target_approach="app2", clear_time=1.0)
    approach_1.add_car(fast_car)

    # Display the intersection
    state = intersection.snapshot()
    print(json.dumps(state, indent=4))


if __name__ == "__main__":
    main()