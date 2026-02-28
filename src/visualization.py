import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Rectangle, Circle
from matplotlib.text import Text

from intersection import Intersection, Approach, Car, LightState, WalkState, Road, Turn
from simulation import Simulator
from traffic_control import FixedTimeController

# Initializing the layout

APPROACH_LAYOUT = {
    "north": {"stop": (25, 35), "dir": (0, -1), "lane_width": 6},
    "south": {"stop": (25, 15), "dir": (0, 1), "lane_width": 6},
    "east": {"stop": (35, 25), "dir": (1, 0), "lane_width": 6},
    "west": {"stop": (15, 25), "dir": (-1, 0), "lane_width": 6}
}  # ----- Do east and west need to swap dir? ------

CAR_SIZE = (3, 1.5)
CAR_SPACING = 3

LIGHT_COLORS = {
    "Green": "green",
    "Yellow": "gold",
    "Red": "red",
}


def render_snapshot(snapshot: dict, show=True):
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(0, 50)
    ax.set_ylim(0, 50)
    ax.set_aspect('equal')
    ax.axis('off')

    # Roads
    ax.add_patch(Rectangle((20, 0), 10, 50, color="gray", alpha=0.3, fill=True))
    ax.add_patch(Rectangle((0, 20), 50, 10, color="gray", alpha=0.3, fill=True))

    for road_name, road_data in snapshot.items():

        for app_name, data in road_data["approaches"].items():
            print(app_name)
            if app_name not in APPROACH_LAYOUT:
                continue

            layout = APPROACH_LAYOUT[app_name]
            stop_x, stop_y = layout["stop"]
            dx, dy = layout["dir"]

            # ---------------
            #      Cars
            # ---------------
            n_cars = data.get("num_cars", 0)
            for i in range(n_cars):
                offset = i * (CAR_SIZE[0] + CAR_SPACING)
                car_x = stop_x + (-dx) * offset
                car_y = stop_y + (-dy) * offset

                # HORIZONTAL:
                if dx != 0:
                    rect = Rectangle(
                        (car_x - CAR_SIZE[0] / 2, car_y - CAR_SIZE[1] / 2),
                        CAR_SIZE[0],
                        CAR_SIZE[1],
                        facecolor="tab:blue",
                        edgecolor="black"
                    )
                # Vertical:
                else:
                    rect = Rectangle(
                        (car_x - CAR_SIZE[1] / 2, car_y - CAR_SIZE[0] / 2),
                        CAR_SIZE[1],
                        CAR_SIZE[0],
                        facecolor="tab:blue",
                        edgecolor="black"
                    )
                ax.add_patch(rect)

            # ---------------
            # Traffic Lights
            # ---------------

            light_state = data.get("light", "Red")
            light_color = LIGHT_COLORS.get(light_state, "gray")

            light_offset = {
                "north": (0, -5),
                "south": (0, 5),
                "east": (-5, 0),
                "west": (5, 0)
            }[app_name]  # swap west and east?

            lx = stop_x + light_offset[0]
            ly = stop_y + light_offset[1]

            light_circle = Circle((lx, ly), radius=2, color=light_color, ec="Black")
            ax.add_patch(light_circle)

            # ---------------
            #  Pedestrians
            # ---------------

            crosswalk = data.get("crosswalk")
            if crosswalk:
                people = crosswalk.get("people_waiting", 0)
            else:
                people = 0

            if people > 0:
                pedestrian_offset = {
                    "north": (-10, -3),
                    "south": (7, 2),
                    "east": (-2, 7),
                    "west": (2, -7),
                }[app_name]
                pox, poy = pedestrian_offset

                px = stop_x + pox
                py = stop_y + poy

                pedestrian_circle = Circle((px, py), radius=.4 + 0.3 * people, color="purple", )
                ax.add_patch(pedestrian_circle)

                ax.text(px, py + 6, str(people), fontsize=9, va="center")

    if show:
        plt.show()

    return fig, ax


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
    approach_south.add_car(Car(target_approach="north", clear_time=0.0))

    # Add some pedestrians pressing buttons
    approach_north.crosswalk.people_waiting = 3
    approach_east.crosswalk.people_waiting = 1
    approach_west.crosswalk.people_waiting = 1
    approach_south.crosswalk.people_waiting = 1


    render_snapshot(intersection.snapshot())


if __name__ == "__main__":
    main()
