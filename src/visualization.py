import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Rectangle, Circle, FancyArrowPatch
from intersection import Intersection, Approach, Car, Road, Turn, WalkState


# Initializing the layout

APPROACH_LAYOUT = {
    "north": {"stop": (25, 35), "dir": (0, -1), "lane_width": 6},
    "south": {"stop": (25, 15), "dir": (0, 1), "lane_width": 6},
    "east": {"stop": (35, 25), "dir": (-1, 0), "lane_width": 6},
    "west": {"stop": (15, 25), "dir": (1, 0), "lane_width": 6}
}

CAR_SIZE = (3, 1.5)
CAR_SPACING = 3

LIGHT_COLORS = {
    "Green": "green",
    "Yellow": "gold",
    "Red": "red",
}

def _determine_road_orientation(stops: list[tuple[float, float]]) -> str:
    """Return 'vertical' or 'horizontal' depending on which coordinate varies more."""
    xs = [s[0] for s in stops]
    ys = [s[1] for s in stops]
    x_range = max(xs) - min(xs) if xs else 0
    y_range = max(ys) - min(ys) if ys else 0
    # small x_range -> vertical (same x, varying y)
    return "vertical" if x_range < y_range else "horizontal"

def _draw_road(ax, stops, lane_widths, xlim, ylim, margin=1.0):
    """Draw the road rectangle based on stops and lane_widths; returns road_width used."""
    if not stops:
        return 0.0, "horizontal"

    orientation = _determine_road_orientation(stops)
    max_lane = max(lane_widths) if lane_widths else 6
    # approximate road width as two directions + small buffer
    road_width = max_lane * 2
    xmin, xmax = xlim
    ymin, ymax = ylim

    if orientation == "vertical":
        # center x from stops, but full height across plot
        center_x = float(np.mean([s[0] for s in stops]))
        x0 = center_x - road_width / 2
        y0 = ymin - margin
        height = (ymax - ymin) + 2 * margin
        rect = Rectangle((x0, y0), road_width, height, color="gray", alpha=0.3, zorder=0)
    else:
        # horizontal road spans full width
        center_y = float(np.mean([s[1] for s in stops]))
        x0 = xmin - margin
        width = (xmax - xmin) + 2 * margin
        y0 = center_y - road_width / 2
        rect = Rectangle((x0, y0), width, road_width, color="gray", alpha=0.3, zorder=0)


    ax.add_patch(rect)
    return road_width, orientation

def _draw_crosswalk(ax, stop_x, stop_y, dx, dy, road_width,
                    crosswalk_light_state=None, depth=3.0,
                    stripe_gap=0.6, stripe_width=0.4):
    """
       Draw a crosswalk centered on (stop_x, stop_y).
       If crosswalk_light_state indicates Walk/Flashing, stripes are green; otherwise white.
       """
    # Determine stripe color from crosswalk light state
    stripe_color = "green" if (crosswalk_light_state in ("Walk", "Flashing")) else "white"
    base_color = "darkgray"  # background of crosswalk

    if dx == 0:
        # vertical approach -> crosswalk runs horizontally across the road
        cw_length = road_width + 1.5
        cw_height = depth
        x0 = stop_x - cw_length / 2
        y0 = stop_y - cw_height / 2
        base = Rectangle((x0, y0), cw_length, cw_height, color=base_color, alpha=0.6, zorder=1)
        ax.add_patch(base)
        n_stripes = int(max(1, cw_length // (stripe_gap + stripe_width))) + 1
        start = x0 + 0.2
        for i in range(n_stripes):
            sx = start + i * (stripe_width + stripe_gap)
            stripe = Rectangle((sx, y0 + 0.15), stripe_width, cw_height - 0.3, color=stripe_color, zorder=2)
            ax.add_patch(stripe)
    else:
        # horizontal approach -> crosswalk runs vertically across the road
        cw_length = road_width + 1.5
        cw_width = depth
        x0 = stop_x - cw_width / 2
        y0 = stop_y - cw_length / 2
        base = Rectangle((x0, y0), cw_width, cw_length, color=base_color, alpha=0.6, zorder=1)
        ax.add_patch(base)
        n_stripes = int(max(1, cw_length // (stripe_gap + stripe_width))) + 1
        start = y0 + 0.2
        for i in range(n_stripes):
            sy = start + i * (stripe_width + stripe_gap)
            stripe = Rectangle((x0 + 0.15, sy), cw_width - 0.3, stripe_width, color=stripe_color, zorder=2)
            ax.add_patch(stripe)

def _compute_arrow_direction_from_center(px, py, ax, dx, dy):
    """Compute an arrow direction perpendicular to traffic but pointing outward from intersection center."""
    # center of plot
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    cx = 0.5 * (xlim[0] + xlim[1])
    cy = 0.5 * (ylim[0] + ylim[1])
    vec = np.array([px - cx, py - cy])

    # perpendicular to traffic direction:
    if dx == 0:
        perp = np.array([1.0, 0.0])  # horizontal crosswalk

    else:
        perp = np.array([0.0, -1.0])  # vertical crosswalk

    # choose sign to point away from center
    sign = np.sign(np.dot(perp, vec))
    if sign == 0:
        sign = 1.0
    dir_vec = perp * sign

    if dx == 0:  # horizontal crosswalk
        dir_vec = -dir_vec
    if dy == 0:  # horizontal crosswalk
        dir_vec = -dir_vec
    # normalize
    norm = np.linalg.norm(dir_vec)
    if norm == 0:
        return np.array([1.0, 0.0])
    return dir_vec / norm

def render_snapshot(snapshot: dict, show=True):
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(0, 50)
    ax.set_ylim(0, 50)
    ax.set_aspect('equal')
    ax.axis('off')

    # plot bounds used so roads can extend to edges (longer roads)
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()

    for road_name, road_data in snapshot.items():
        approaches = road_data.get("approaches", {})
        stops = []
        lane_widths = []
        for app_name in approaches.keys():
            if app_name in APPROACH_LAYOUT:
                stops.append(tuple(APPROACH_LAYOUT[app_name]["stop"]))
                lane_widths.append(APPROACH_LAYOUT[app_name].get("lane_width", 6))
        # draw the road rectangle computed from approach stops
        road_width, _orientation = _draw_road(ax, stops, lane_widths, xlim, ylim, margin=1.0)
        for app_name, data in approaches.items():
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
                offset = i * (CAR_SIZE[0] + CAR_SPACING) + 4
                car_x = stop_x + (-dx) * offset
                car_y = stop_y + (-dy) * offset

                # HORIZONTAL:
                if dx != 0:
                    rect = Rectangle(
                        (car_x - CAR_SIZE[0] / 2, car_y - CAR_SIZE[1] / 2),
                        CAR_SIZE[0],
                        CAR_SIZE[1],
                        facecolor="tab:blue",
                        edgecolor="black",
                        zorder = 3
                    )
                # Vertical:
                else:
                    rect = Rectangle(
                        (car_x - CAR_SIZE[1] / 2, car_y - CAR_SIZE[0] / 2),
                        CAR_SIZE[1],
                        CAR_SIZE[0],
                        facecolor="tab:blue",
                        edgecolor="black",
                        zorder = 3
                    )
                ax.add_patch(rect)

            # ---------------
            # Traffic Lights
            # ---------------

            light_state = data.get("light", "Red")
            light_color = LIGHT_COLORS.get(light_state, "pink")

            light_offset = {
                "north": (0, -4),
                "south": (0, 4),
                "east": (-4, 0),
                "west": (4, 0)
            }[app_name]  # swap west and east?

            lx = stop_x + light_offset[0]
            ly = stop_y + light_offset[1]

            light_circle = Circle((lx, ly), radius=2, color=light_color, ec="Black", zorder = 4)
            ax.add_patch(light_circle)

            # ---------------
            # Crosswalks and Pedestrians
            # ---------------

            crosswalk = data.get("crosswalk")
            crosswalk_light_state = None

            if crosswalk:
                crosswalk_light_state = crosswalk.get("light")

                # people = crosswalk.get("people_waiting", 0)
                # # draw crosswalk perpendicular to approach direction
                # _draw_crosswalk(ax, stop_x, stop_y, dx, dy, road_width)

                # draw crosswalk perpendicular to approach direction
                _draw_crosswalk(ax, stop_x, stop_y, dx, dy, road_width, crosswalk_light_state=crosswalk_light_state)

                # small pedestrian marker placed just off the stop line towards sidewalk
                if dx == 0:
                    ped_off = (np.sign(dy) * 10, 0)  # push outside the road in x
                else:
                    ped_off = (0, np.sign(dx) * -10)  # push outside the road in y
                px = stop_x + ped_off[0]
                py = stop_y + ped_off[1]

                people = crosswalk.get("people_waiting", 0) if crosswalk else 0
                if people > 0:
                    pedestrian_circle = Circle((px, py), radius=0.4 + 0.25 * people, color="purple", zorder=5)
                    ax.add_patch(pedestrian_circle)
                    ax.text(px, py + 1.0, str(people), fontsize=8, va="center", zorder=6)

                    # draw arrow indicating which crosswalk the pedestrians are using
                    arrow_dir = _compute_arrow_direction_from_center(px, py, ax, dx, dy)
                    arrow_len = 3.8
                    arrow_target = (px + arrow_dir[0] * arrow_len, py + arrow_dir[1] * arrow_len)

                    arrow_color = "green" if (crosswalk_light_state in ("Walk", "Flashing")) else "black"
                    arrow = FancyArrowPatch((px, py), arrow_target,
                                            arrowstyle='-|>', mutation_scale=16,
                                            linewidth=2, color=arrow_color, zorder=6)
                    ax.add_patch(arrow)
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
    approach_east.add_car(Car(target_approach="west", clear_time=0.0))

    # Add some pedestrians pressing buttons
    approach_north.crosswalk.people_waiting = 3
    approach_east.crosswalk.people_waiting = 1
    approach_west.crosswalk.people_waiting = 1
    approach_south.crosswalk.people_waiting = 1

    # Set some crosswalk signals for demonstration
    approach_north.crosswalk.light.state = WalkState.WALK
    approach_east.crosswalk.light.state = WalkState.STOP
    approach_west.crosswalk.light.state = WalkState.FLASHING
    approach_south.crosswalk.light.state = WalkState.STOP

    render_snapshot(intersection.snapshot())


if __name__ == "__main__":
    main()
