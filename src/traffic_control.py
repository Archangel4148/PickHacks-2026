from dataclasses import dataclass

from intersection import Intersection, Phase, WalkState


class Controller:
    def tick(self, dt: float, intersection: Intersection):
        raise NotImplementedError

class FixedTimeController(Controller):
    """
    Simple controller
    - One road at a time gets THROUGH
    - All others ALL_RED
    - Crosswalks run only on ALL_RED roads
    """

    def __init__(self, green_duration: float):
        self.green_duration = green_duration
        self.timer = 0.0
        self.active_road = 0

    def tick(self, dt: float, intersection: Intersection):
        self.timer += dt

        if self.timer >= self.green_duration:
            self.timer = 0.0
            self.active_road = (self.active_road + 1) % len(intersection.roads)

        for i, road in enumerate(intersection.roads):
            if i == self.active_road:
                intersection.set_road_phase(road, Phase.THROUGH)
                intersection.set_road_crosswalks(road, WalkState.STOP)
            else:
                intersection.set_road_phase(road, Phase.ALL_RED)
                intersection.set_road_crosswalks(road, WalkState.WALK)


@dataclass(frozen=True)
class PhaseStep:
    road_idx: int
    phase: Phase
    walk_state: WalkState  # Walk state of the OTHER road(s)
    duration: float

class SequenceController(Controller):
    """
    Cycles through a defined sequence of steps.
    """
    def __init__(self, sequence: list[PhaseStep]):
        if not sequence:
            raise ValueError("Sequence must contain at least one step")

        self.sequence = sequence
        self.step_idx = 0
        self.timer = 0.0

    def tick(self, dt: float, intersection: Intersection):
        step = self.sequence[self.step_idx]
        self.timer += dt

        # Apply phases
        for i, road in enumerate(intersection.roads):
            if i == step.road_idx:
                intersection.set_road_phase(road, step.phase)
                intersection.set_road_crosswalks(road, WalkState.STOP)
            else:
                intersection.set_road_phase(road, Phase.ALL_RED)
                intersection.set_road_crosswalks(road, step.walk_state)

        # Advance step
        if self.timer >= step.duration:
            self.timer = 0.0
            self.step_idx = (self.step_idx + 1) % len(self.sequence)