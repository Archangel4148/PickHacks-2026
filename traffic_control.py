from intersection import Intersection, LightState, Street, WalkState
from enum import StrEnum
from dataclasses import dataclass
from typing import Sequence

class Phase(StrEnum):
    RED = "Red"
    GREEN = "Green"
    YELLOW = "Yellow"

@dataclass
class Road:
    streets: Sequence[Street]
    phase: Phase = Phase.RED

class Controller:
    def tick(self, dt: float, intersection: Intersection):
        raise NotImplementedError
    

class FixedTimeController:
    # Simple test controller
    def __init__(self, green_duration: float):
        self.green_duration = green_duration
        self.timer = 0.0
        self.active_street = 0

    def tick(self, dt: float, intersection: Intersection):
        self.timer += dt

        if self.timer >= self.green_duration:
            self.timer = 0.0
            self.active_street = (self.active_street + 1) % len(intersection.streets)

        for i, street in enumerate(intersection.streets):
            if i == self.active_street:
                street.light.state = LightState.GREEN
                if street.crosswalk:
                    street.crosswalk.light.state = WalkState.STOP
            else:
                street.light.state = LightState.RED
                if street.crosswalk:
                    street.crosswalk.light.state = WalkState.WALK