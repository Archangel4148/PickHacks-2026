import json
from intersection import (
    Approach,
    Road,
    Intersection,
    Car,
    Turn,
)
from simulation import Simulator
from traffic_control import FixedTimeController


def main():
    # Build a 4-way intersection (N, S, E, W)
    approach_north = Approach(name="north", has_crosswalk=True)
    approach_south = Approach(name="south", has_crosswalk=True)
    road_ns = Road(approaches=[approach_north, approach_south])
    approach_east = Approach(name="east", has_crosswalk=True)
    approach_west = Approach(name="west", has_crosswalk=True)
    road_ew = Road(approaches=[approach_east, approach_west])

    topology = {
        "north": {"west": Turn.RIGHT_TURN, "south": Turn.THROUGH, "east": Turn.LEFT_TURN},
        "east": {"north": Turn.RIGHT_TURN, "west": Turn.THROUGH, "south": Turn.LEFT_TURN},
        "south": {"east": Turn.RIGHT_TURN, "north": Turn.THROUGH, "west": Turn.LEFT_TURN},
        "west": {"south": Turn.RIGHT_TURN, "east": Turn.THROUGH, "north": Turn.LEFT_TURN},
    }
    intersection = Intersection(roads=[road_ns, road_ew], topology=topology)

    # Add some cars
    approach_north.add_car(Car(target_approach="south", clear_time=0.0))
    approach_north.add_car(Car(target_approach="east", clear_time=1.5))
    approach_east.add_car(Car(target_approach="west", clear_time=0.0))
    approach_west.add_car(Car(target_approach="south", clear_time=1.5))

    # Add some pedestrians pressing buttons
    approach_north.crosswalk.people_waiting = 3
    approach_east.crosswalk.people_waiting = 1

    # Simulator + controller
    simulator = Simulator(intersection)
    controller = FixedTimeController(green_duration=5.0)

    # Run simulation
    dt = 0.1
    sim_duration = 10.0
    next_print = 0.0
    print_interval = 1.0

    print("=== START STATE ===")
    print(json.dumps(intersection.snapshot(), indent=2))

    while simulator.time < sim_duration:
        controller.tick(dt, intersection)
        simulator.tick(dt)

        if simulator.time >= next_print:
            print(f"\n=== t = {simulator.time:.1f}s ===")
            print(json.dumps(intersection.snapshot(), indent=2))
            print(f"Total wait time: {simulator.total_wait_time:.1f}")
            next_print += print_interval

    print("\nSimulation finished.")
    print(f"Final total wait time: {simulator.total_wait_time:.1f}")


if __name__ == "__main__":
    main()
