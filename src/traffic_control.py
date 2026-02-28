from intersection import Intersection, Phase, WalkState


class Controller:
    def tick(self, dt: float, intersection: Intersection):
        raise NotImplementedError

class FixedTimeController:
    # Simple "standard" controller
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



#######################################
############### AI CODE ###############
#######################################

class AdaptiveController:
    def __init__(
        self,
        min_green: float,
        max_green: float,
        vehicle_weight: float,
        pedestrian_weight: float,
        switch_threshold: float,
    ):
        self.min_green = min_green
        self.max_green = max_green
        self.vehicle_weight = vehicle_weight
        self.pedestrian_weight = pedestrian_weight
        self.switch_threshold = switch_threshold

        self.active_road = 0
        self.timer = 0.0

    def _road_score(self, road):
        vehicle_score = sum(a.num_cars for a in road.approaches)

        ped_score = 0
        for a in road.approaches:
            if a.crosswalk:
                ped_score += a.crosswalk.people_waiting

        return (
            self.vehicle_weight * vehicle_score
            + self.pedestrian_weight * ped_score
        )

    def tick(self, dt, intersection):
        self.timer += dt

        roads = intersection.roads
        current = roads[self.active_road]
        other_index = (self.active_road + 1) % len(roads)
        other = roads[other_index]

        current_score = self._road_score(current)
        other_score = self._road_score(other)

        should_switch = False

        if self.timer >= self.min_green:
            if other_score > current_score + self.switch_threshold:
                should_switch = True
            elif self.timer >= self.max_green:
                should_switch = True

        if should_switch:
            self.active_road = other_index
            self.timer = 0.0

        # Apply phases
        for i, road in enumerate(roads):
            if i == self.active_road:
                road.phase = Phase.GREEN
                for approach in road.approaches:
                    if approach.crosswalk:
                        approach.crosswalk.light.state = WalkState.STOP
            else:
                road.phase = Phase.RED
                for approach in road.approaches:
                    if approach.crosswalk:
                        approach.crosswalk.light.state = WalkState.WALK