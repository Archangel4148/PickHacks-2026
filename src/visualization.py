import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
from IPython.display import HTML #For rendering in Colab
from PIL import Image
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Rectangle, Circle
from matplotlib.text import Text

from intersection import Intersection, Approach, Car, LightState, WalkState
from simulation import Simulator
from traffic_control import FixedTimeController

#Initializing the layout

APPROACH_LAYOUT = {
    "north_approach": {"stop": (50, 70), "dir": (0, -1), "lane_width": 6},
    "south_approach": {"stop": (50, 30), "dir": (0, 1), "lane_width": 6},
    "east_approach": {"stop": (70, 50), "dir": (1, 0), "lane_width": 6}, 
    "west_approach": {"stop": (30, 50), "dir": (-1, 0), "lane_width":6}
} #----- Do east and west need to swap dir? ------

CAR_SIZE = (6,3)
CAR_SPACING = 5

LIGHT_COLORS = {
    "Green": "green",
    "Yellow": "gold",
    "Red": "red",
}


def render_snapshot(snapshot:dict, show = True):
  fig, ax = plt.subplots(figsize=(6,6))
  ax.set_xlim(0, 100)
  ax.set_ylim(0, 100)
  ax.set_aspect('equal')
  ax.axis('off')
  
  #Roads
  ax.add_patch(Rectangle((40,20), 20, 60, color="gray", alpha = 0.3, fill=True))
  ax.add_patch(Rectangle((20, 40), 60, 20, color="gray", alpha = 0.3, fill=True))

  for app_name, data in snapshot.items():
        if app_name not in APPROACH_LAYOUT:
            continue
  layout = APPROACH_LAYOUT[app_name]
  stop_x, stop_y = layout["stop"]
  dx, dy = layout["dir"]

  #Cars
  n_cars = data.get("num_cars", 0)
  for i in range(n_cars):
    offset = i * (CAR_SIZE[0] + CAR_SPACING)
    car_x = stop_x + (-dx) * offset
    car_y = stop_y + (-dy) * offset


  #HORIZONTAL:
  if dx != 0:
    rect = Rectangle(
                    (car_x - CAR_SIZE[0] / 2, car_y - CAR_SIZE[1] / 2),
                    CAR_SIZE[0],
                    CAR_SIZE[1],
                    facecolor="tab:blue",
                    edgecolor="black"
                    )
  #Vertical:
  else:
    rect = Rectangle(
                    (car_x - CAR_SIZE[1] / 2, car_y - CAR_SIZE[0] / 2),
                    CAR_SIZE[1],
                    CAR_SIZE[0],
                    facecolor="tab:blue",
                    edgecolor="black"
                    )
  ax.add_patch(rect)
  



  if show:
    plt.show()

  return fig, ax

def main():
  render_snapshot(intersection.snapshot())
if __name__ == "__main__":
  main()


# HTML(ani.to_jshtml())
