from intersection import Intersection, Phase, WalkState


class Controller:
    def tick(self, dt: float, intersection: Intersection):
        raise NotImplementedError

class FixedTimeController:
    # Simple test controller
    def __init__(self, green_duration: float):
        self.green_duration = green_duration
        self.timer = 0.0
        self.active_road = 0

    def tick(self, dt: float, intersection: Intersection):
        self.timer += dt

        # Switch active roads
        if self.timer >= self.green_duration:
            self.timer = 0.0
            self.active_road = (self.active_road + 1) % len(intersection.roads)

        # Update road phases
        for i, road in enumerate(intersection.roads):
            if i == self.active_road:
                road.phase = Phase.GREEN
                # green = vehicles move, pedestrians stop
                for approach in road.approaches:
                    if approach.crosswalk:
                        approach.crosswalk.light.state = WalkState.STOP
            else:
                road.phase = Phase.RED
                # red = vehicles stop, pedestrians can walk (button ignored for now)
                for approach in road.approaches:
                    if approach.crosswalk:
                        approach.crosswalk.light.state = WalkState.WALK