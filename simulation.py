from intersection import Intersection, LightState, WalkState, get_clear_time


class Simulator:
    # This class manages simulation of an intersection
    def __init__(self, intersection: Intersection):
        self.intersection = intersection
        self.time = 0.0
        self.total_wait_time = 0.0
        self.prev_light_states = [
            street.light.state for street in intersection.streets
        ]

    def tick(self, dt: float):
        # Advance by one simulation step
        self.time += dt
        self._update_cars(dt)
        self._update_pedestrians(dt)

    def _update_cars(self, dt: float):
        for i, street in enumerate(self.intersection.streets):
            prev_state = self.prev_light_states[i]
            curr_state = street.light.state

            # Green: all cars move
            if curr_state == LightState.GREEN:
                for car in street.cars:
                    car.clear_time -= dt

                # Remove cars that made it through
                while street.cars and street.cars[0].clear_time <= 0:
                    street.cars.popleft()

            # Green -> Red: settle the cars' positions
            if prev_state == LightState.GREEN and curr_state == LightState.RED:
                for idx, car in enumerate(street.cars):
                    car.clear_time = get_clear_time(idx)

            # Track wait times
            for car in street.cars:
                car.wait_time += dt
                self.total_wait_time += dt

            # Update previous state
            self.prev_light_states[i] = curr_state

    def _update_pedestrians(self, dt: float):
        for street in self.intersection.streets:
            if (crosswalk := street.crosswalk) is None:
                continue

            # Walk sign on: everyone clears
            if crosswalk.light.state == WalkState.WALK:
                crosswalk.people_waiting = 0
                crosswalk.button_pressed = False

            # Walk sign off: update wait time
            else:
                self.total_wait_time += crosswalk.people_waiting * dt