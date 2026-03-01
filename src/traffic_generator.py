import random
from intersection import Car, get_clear_time


class TrafficGenerator:
    def __init__(
        self,
        intersection,
        car_arrival_prob=0.3,      # probability per approach per second
        ped_arrival_prob=0.05      # probability per crosswalk per second
    ):
        self.intersection = intersection
        self.car_arrival_prob = car_arrival_prob
        self.ped_arrival_prob = ped_arrival_prob

    def tick(self, dt: float):
        self._spawn_cars(dt)
        self._spawn_pedestrians(dt)

    def _spawn_cars(self, dt: float):
        for approach in self.intersection.approaches:

            # Bernoulli approximation of Poisson process
            if random.random() < self.car_arrival_prob * dt:

                # Pick random valid outgoing direction
                outgoing = list(
                    self.intersection.topology[approach.name].keys()
                )
                target = random.choice(outgoing)

                # Position at back of queue
                pos_idx = len(approach.cars)
                clear_time = get_clear_time(pos_idx)

                approach.add_car(
                    Car(
                        target_approach=target,
                        clear_time=clear_time
                    )
                )

    def _spawn_pedestrians(self, dt: float):
        for approach in self.intersection.approaches:
            if approach.crosswalk is None:
                continue

            if random.random() < self.ped_arrival_prob * dt:
                approach.crosswalk.people_waiting += 1
                