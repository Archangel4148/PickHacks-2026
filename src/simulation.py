from intersection import Intersection, LightState, WalkState, get_clear_time, turn_allowed

class Simulator:
    # This class manages simulation of an intersection
    def __init__(self, intersection: Intersection):
        self.intersection = intersection
        self.time = 0.0
        self.total_wait_time = 0.0
        self.prev_can_move = [False] * len(intersection.approaches)

    def tick(self, dt: float):
        # Advance by one simulation step
        self.time += dt
        self._update_cars(dt)
        self._update_pedestrians(dt)

    def _update_cars(self, dt: float):
        for i, approach in enumerate(self.intersection.approaches):
            road = self.intersection.approach_to_road(approach)
            phase = road.phase

            blocked = False
            any_movement = False

            # Track cars that move
            moved_cars = []

            for car in approach.cars:
                if blocked:
                    break

                # Can this car move?
                intended_turn = self.intersection.get_turn(approach.name, car.target_approach)
                if turn_allowed(phase, intended_turn):
                    car.clear_time -= dt
                    any_movement = True
                    moved_cars.append(car)
                else:
                    blocked = True

            # Remove cars that made it through
            while moved_cars and moved_cars[0].clear_time <= 0:
                approach.cars.popleft()
                moved_cars.pop(0)

            # Settle car positions after everything stops moving
            if self.prev_can_move[i] and not any_movement:
                for idx, car in enumerate(approach.cars):
                    car.clear_time = get_clear_time(idx)

            # Track wait times
            for car in approach.cars:
                car.wait_time += dt
                self.total_wait_time += dt

    def _update_pedestrians(self, dt: float):
        for approach in self.intersection.approaches:
            if (crosswalk := approach.crosswalk) is None:
                continue

            # Walk sign on: everyone clears
            if crosswalk.light.state == WalkState.WALK:
                crosswalk.people_waiting = 0
                crosswalk.button_pressed = False

            # Walk sign off: update wait time
            else:
                if crosswalk.people_waiting > 0:
                    crosswalk.button_pressed = True  # Assume pedestrians push the button on arrival
                self.total_wait_time += crosswalk.people_waiting * dt