import json
from example_intersection import build_four_way_intersection, build_t_junction
from intersection import (
    Approach,
    Road,
    Intersection,
    Car,
    Turn,
)
from simulation import Simulator
from visualization import render_snapshot
from traffic_control import FixedTimeController


def main():
    # Build a 4-way intersection (N, S, E, W)
    approaches, intersection = build_t_junction()
    approach_north, approach_east, approach_south = approaches
    
    # Add some cars
    approach_north.add_car(Car(target_approach="south", clear_time=0.0))
    approach_north.add_car(Car(target_approach="east", clear_time=1.5))
    approach_east.add_car(Car(target_approach="north", clear_time=0.0))

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
    render_snapshot(intersection.snapshot())

    while simulator.time < sim_duration:
        controller.tick(dt, intersection)
        simulator.tick(dt)

        if simulator.time >= next_print:
            print(f"\n=== t = {simulator.time:.1f}s ===")
            print(json.dumps(intersection.snapshot(), indent=2))
            print(f"Total wait time: {simulator.total_wait_time:.1f}")
            next_print += print_interval
            render_snapshot(intersection.snapshot())

    print("\nSimulation finished.")
    print(f"Final total wait time: {simulator.total_wait_time:.1f}")


if __name__ == "__main__":
    main()
